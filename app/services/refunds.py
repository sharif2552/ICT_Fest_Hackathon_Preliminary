"""Refund bookkeeping.

When a booking is cancelled a refund is calculated from its price and the
applicable notice tier, then written to the refund ledger with a processed
status. Amounts are stored in whole cents.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Booking, RefundLog


def log_refund(db: Session, booking: Booking, percent: int) -> RefundLog:
    # Exact integer round-half-up: adding half the divisor before floor
    # division rounds .5 cents up instead of using float math or Python's
    # round()  (which rounds half-to-even), matching the documented policy.
    amount_cents = (booking.price_cents * percent + 50) // 100
    entry = RefundLog(
        booking_id=booking.id,
        amount_cents=amount_cents,
        status="processed",
        processed_at=datetime.utcnow(),
    )
    db.add(entry)
    # Intentionally not committed here: the caller commits this insert in
    # the same transaction as the booking status update so the two writes
    # land atomically (see cancel_booking in routers/bookings.py). Committing
    # independently would let a crash between the two commits leave a
    # durable refund against a booking still marked "confirmed", so a retry
    # would log a second, duplicate refund.
    db.flush()
    return entry
