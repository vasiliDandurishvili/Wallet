from __future__ import annotations

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from wallet.core.errors import (
    ConflictError,
    InsufficientFundsError,
    NotFoundError,
    ValidationError,
)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    def _not_found(_, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(ConflictError)
    def _conflict(_, exc: ConflictError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(ValidationError)
    def _bad_request(_, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )

    @app.exception_handler(InsufficientFundsError)
    def _insufficient(_, exc: InsufficientFundsError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )
