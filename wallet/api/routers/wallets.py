from __future__ import annotations

from fastapi import APIRouter, Depends

from wallet.api.dependencies import (
    AuthenticatedUser,
    get_price_provider,
    get_storage,
    require_user,
)
from wallet.api.models import WalletCreateResponse, WalletGetResponse
from wallet.core.services.pricing import PriceProvider
from wallet.core.services.wallets import WalletService
from wallet.infra.sqlite.storage import SqliteStorage

router = APIRouter()


@router.post("/wallets", response_model=WalletCreateResponse)
def create_wallet(
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
    storage: SqliteStorage = Depends(get_storage),  # noqa: B008
    price_provider: PriceProvider = Depends(get_price_provider),  # noqa: B008
) -> WalletCreateResponse:
    service = WalletService(storage=storage, price_provider=price_provider)
    wallet = service.create_wallet(user.id)
    return WalletCreateResponse(**service.wallet_view(wallet))


@router.get("/wallets/{address}", response_model=WalletGetResponse)
def get_wallet(
    address: str,
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
    storage: SqliteStorage = Depends(get_storage),  # noqa: B008
    price_provider: PriceProvider = Depends(get_price_provider),  # noqa: B008
) -> WalletGetResponse:
    service = WalletService(storage=storage, price_provider=price_provider)
    wallet = service.get_wallet_owned(user.id, address)
    return WalletGetResponse(**service.wallet_view(wallet))
