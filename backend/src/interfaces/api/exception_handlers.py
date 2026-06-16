from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.seedwork.exceptions import DomainException
from src.domain.user.exceptions import (
    EmailAlreadyExists,
    InvalidEmail,
    InvalidHashedPassword,
)

EXCEPTION_STATUS_MAP = {
    InvalidEmail: 422,
    InvalidHashedPassword: 422,
    EmailAlreadyExists: 409,
}


def auth_exception_handler(app: FastAPI) -> None:
    """Common auth exception handler."""

    @app.exception_handler(Exception)
    async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Domain exception handler."""
        if isinstance(exc, DomainException):
            status_code = EXCEPTION_STATUS_MAP.get(type(exc), 400)
            content = {
                "detail": exc.detail,
                "code": exc.code,
            }
        else:
            status_code = 500
            content = {
                "detail": "Internal server error",
                "code": "internal_error",
            }

        return JSONResponse(
            status_code=status_code,
            content=content,
        )
