"""Application-level error type and JSON representation.

Every business-rule violation raises :class:`AppError`, which is rendered as
``{"detail": <string>, "code": <CODE>}`` with the appropriate HTTP status.
"""
from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, status_code: int, code: str, detail: str):
        self.status_code = status_code
        self.code = code
        self.detail = detail
        super().__init__(detail)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Last-resort safety net: any exception that isn't an AppError (a bug we
    # haven't found and wrapped yet) still has to honor the documented
    # {"detail","code"} error contract instead of falling through to
    # Starlette's default plain-text 500.
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
    )
