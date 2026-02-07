from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from typing import cast

from fastapi import Depends, Header, HTTPException, Request, status

from wallet.core.errors import NotFoundError
from wallet.core.services.pricing import PriceProvider
from wallet.infra.pricing.coinbase import CoinbasePriceProvider
from wallet.infra.sqlite.connection import connect
from wallet.infra.sqlite.setup import setup
from wallet.infra.sqlite.storage import SqliteStorage
from wallet.settings import Settings


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def get_storage(settings: Settings = Depends(get_settings)) -> Generator[SqliteStorage]:  # noqa: B008
    conn = connect(settings.database_path)
    try:
        setup(conn)
        yield SqliteStorage(conn)
    finally:
        conn.close()


def get_price_provider() -> PriceProvider:
    return CoinbasePriceProvider()


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    api_key: str


def require_user(
    x_api_key: str | None = Header(default=None, alias="X-API-KEY"),
    storage: SqliteStorage = Depends(get_storage),  # noqa: B008
) -> AuthenticatedUser:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-KEY"
        )

    try:
        user = storage.users().read_by_api_key(x_api_key)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        ) from e

    return AuthenticatedUser(id=user.id, api_key=user.api_key)


def require_admin(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-KEY"),
) -> None:
    settings: Settings = request.app.state.settings
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
