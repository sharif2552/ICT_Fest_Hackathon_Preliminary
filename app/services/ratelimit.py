"""Per-user rolling-window rate limiting for booking creation."""
import threading
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..errors import AppError
from ..models import RateLimitEvent

_WINDOW_SECONDS = 60
_MAX_REQUESTS = 20

_lock = threading.Lock()


def record_and_check(user_id: int, db: Session) -> None:
    with _lock:
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=_WINDOW_SECONDS)

        # Prune this user's events that have already fallen out of the
        # rolling window, then persist the current attempt. Events are
        # stored in the database (not process memory) so the window
        # survives an API restart instead of silently resetting.
        db.query(RateLimitEvent).filter(
            RateLimitEvent.user_id == user_id,
            RateLimitEvent.created_at <= window_start,
        ).delete(synchronize_session=False)
        db.add(RateLimitEvent(user_id=user_id, created_at=now))
        db.commit()

        count = (
            db.query(RateLimitEvent)
            .filter(RateLimitEvent.user_id == user_id, RateLimitEvent.created_at > window_start)
            .count()
        )
        if count > _MAX_REQUESTS:
            raise AppError(429, "RATE_LIMITED", "Too many booking requests")
