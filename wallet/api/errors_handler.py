from __future__ import annotations

from urllib.request import Request

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
    def _not_found(
        request: Request,  # noqa: ARG001
        exc: NotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(ConflictError)
    def _conflict(
        request: Request,  # noqa: ARG001
        exc: ConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(ValidationError)
    def _bad_request(
        request: Request,  # noqa: ARG001
        exc: ValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )

    @app.exception_handler(InsufficientFundsError)
    def _insufficient(
        request: Request,  # noqa: ARG001
        exc: InsufficientFundsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )
