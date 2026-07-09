"""Authentication: password hashing, JWT issue/verify, request dependencies."""
import hashlib
import hmac
import os
import threading
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from .database import get_db
from .errors import AppError
from .models import TokenInvalidation, User

_REQUIRED_CLAIMS = ["sub", "org", "role", "jti", "iat", "exp", "type"]

# Access tokens presented to /auth/logout are recorded here so they can no
# longer be used.
_revoked_tokens: set[str] = set()

# Refresh tokens are single-use: once presented to /auth/refresh, their jti
# is recorded here so a replay of the same token is rejected.
_used_refresh_tokens: set[str] = set()

# Serializes the check-then-record critical section in revoke_access_token
# and consume_refresh_token so two concurrent requests presenting the same
# token can't both pass the "not yet invalidated" check before either
# records it (and so both sets stay consistent with the persisted table).
_invalidation_lock = threading.Lock()

_PBKDF2_ROUNDS = 100_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ROUNDS)
    return f"{salt.hex()}:{dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split(":")
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), _PBKDF2_ROUNDS)
    return hmac.compare_digest(dk.hex(), dk_hex)


def _now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def create_access_token(user: User) -> str:
    iat = _now_ts()
    lifetime = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id),
        "org": user.org_id,
        "role": user.role,
        "jti": uuid.uuid4().hex,
        "iat": iat,
        "exp": iat + int(lifetime.total_seconds()),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user: User) -> str:
    iat = _now_ts()
    lifetime = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user.id),
        "org": user.org_id,
        "role": user.role,
        "jti": uuid.uuid4().hex,
        "iat": iat,
        "exp": iat + int(lifetime.total_seconds()),
        "type": "refresh",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _invalid_token() -> AppError:
    return AppError(401, "UNAUTHORIZED", "Invalid or expired token")


def _validate_token_claims(payload: dict) -> None:
    try:
        int(payload["sub"])
        int(payload["org"])
    except (TypeError, ValueError):
        raise _invalid_token()

    if not isinstance(payload["jti"], str) or not payload["jti"]:
        raise _invalid_token()
    if payload["role"] not in {"admin", "member"}:
        raise _invalid_token()
    if payload["type"] not in {"access", "refresh"}:
        raise _invalid_token()
    if not isinstance(payload["iat"], int) or not isinstance(payload["exp"], int):
        raise _invalid_token()

    expected_lifetime = (
        ACCESS_TOKEN_EXPIRE_MINUTES * 60
        if payload["type"] == "access"
        else REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    if payload["exp"] - payload["iat"] != expected_lifetime:
        raise _invalid_token()


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": _REQUIRED_CLAIMS},
        )
    except jwt.PyJWTError:
        raise _invalid_token()
    _validate_token_claims(payload)
    return payload


def _expires_at(payload: dict) -> datetime:
    return datetime.fromtimestamp(int(payload["exp"]), timezone.utc).replace(tzinfo=None)


def _persist_invalidation(db: Session, payload: dict) -> None:
    jti = payload["jti"]
    token_type = payload["type"]
    exists = (
        db.query(TokenInvalidation)
        .filter(TokenInvalidation.jti == jti, TokenInvalidation.token_type == token_type)
        .first()
    )
    if exists is None:
        db.add(TokenInvalidation(jti=jti, token_type=token_type, expires_at=_expires_at(payload)))
        try:
            db.commit()
        except IntegrityError:
            # Another concurrent request already recorded the same jti; the
            # end state (invalidated) is identical, so treat this as a no-op.
            db.rollback()


def _is_invalidated(db: Session, payload: dict) -> bool:
    return (
        db.query(TokenInvalidation)
        .filter(
            TokenInvalidation.jti == payload["jti"],
            TokenInvalidation.token_type == payload["type"],
        )
        .first()
        is not None
    )


def revoke_access_token(payload: dict, db: Session) -> None:
    with _invalidation_lock:
        _revoked_tokens.add(payload["jti"])
        _persist_invalidation(db, payload)


def consume_refresh_token(payload: dict, db: Session) -> None:
    """Mark a refresh token's jti as used; raise 401 if it was already used."""
    with _invalidation_lock:
        if payload["jti"] in _used_refresh_tokens or _is_invalidated(db, payload):
            raise AppError(401, "UNAUTHORIZED", "Refresh token already used")
        _used_refresh_tokens.add(payload["jti"])
        _persist_invalidation(db, payload)


def token_payload_from_header(header: str | None, db: Session) -> dict:
    if not header or not header.startswith("Bearer "):
        raise AppError(401, "UNAUTHORIZED", "Missing bearer token")
    token = header[len("Bearer "):].strip()
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AppError(401, "UNAUTHORIZED", "Wrong token type")
    if payload.get("jti") in _revoked_tokens or _is_invalidated(db, payload):
        raise AppError(401, "UNAUTHORIZED", "Token has been revoked")
    return payload


def get_token_payload(request: Request, db: Session = Depends(get_db)) -> dict:
    return token_payload_from_header(request.headers.get("Authorization"), db)


def get_current_user(
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db),
) -> User:
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise AppError(401, "UNAUTHORIZED", "Unknown user")
    if user.org_id != int(payload["org"]) or user.role != payload["role"]:
        raise _invalid_token()
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise AppError(403, "FORBIDDEN", "Admin privileges required")
    return user
