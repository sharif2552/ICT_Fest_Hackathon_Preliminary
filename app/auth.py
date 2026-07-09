"""Authentication: password hashing, JWT issue/verify, request dependencies."""
import hashlib
import hmac
import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Request
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

# Access tokens presented to /auth/logout are recorded here so they can no
# longer be used.
_revoked_tokens: set[str] = set()

# Refresh tokens are single-use: once presented to /auth/refresh, their jti
# is recorded here so a replay of the same token is rejected.
_used_refresh_tokens: set[str] = set()

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


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise AppError(401, "UNAUTHORIZED", "Invalid or expired token")


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
        db.commit()


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
    _revoked_tokens.add(payload["jti"])
    _persist_invalidation(db, payload)


def consume_refresh_token(payload: dict, db: Session) -> None:
    """Mark a refresh token's jti as used; raise 401 if it was already used."""
    if payload["jti"] in _used_refresh_tokens or _is_invalidated(db, payload):
        raise AppError(401, "UNAUTHORIZED", "Refresh token already used")
    _used_refresh_tokens.add(payload["jti"])
    _persist_invalidation(db, payload)


def get_token_payload(request: Request, db: Session = Depends(get_db)) -> dict:
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Bearer "):
        raise AppError(401, "UNAUTHORIZED", "Missing bearer token")
    token = header[len("Bearer "):].strip()
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AppError(401, "UNAUTHORIZED", "Wrong token type")
    if payload.get("jti") in _revoked_tokens or _is_invalidated(db, payload):
        raise AppError(401, "UNAUTHORIZED", "Token has been revoked")
    return payload


def get_current_user(
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db),
) -> User:
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise AppError(401, "UNAUTHORIZED", "Unknown user")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise AppError(403, "FORBIDDEN", "Admin privileges required")
    return user
