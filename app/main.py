"""CoWork API application entrypoint."""
from fastapi import FastAPI, Request

from .auth import get_current_user, token_payload_from_header
from .database import Base, SessionLocal, engine
from .errors import AppError, app_error_handler, unhandled_exception_handler
from .routers import admin, auth, bookings, health, rooms
from .services import ratelimit

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CoWork API", version="1.0.0")

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.middleware("http")
async def rate_limit_booking_create(request: Request, call_next):
    if request.method == "POST" and request.url.path == "/bookings":
        db = SessionLocal()
        try:
            payload = token_payload_from_header(request.headers.get("Authorization"), db)
            user = get_current_user(payload, db)
            ratelimit.record_and_check(user.id, db)
        except AppError as exc:
            return await app_error_handler(request, exc)
        finally:
            db.close()
    return await call_next(request)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(admin.router)
