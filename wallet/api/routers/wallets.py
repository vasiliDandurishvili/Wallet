from __future__ import annotations

from fastapi import APIRouter, Depends

from wallet.api.dependencies import get_price_provider, get_storage, require_user
from wallet.api.models import WalletCreateResponse, WalletGetResponse
from wallet.core.services.wallets import WalletService

router = APIRouter()


@router.post("/wallets", response_model=WalletCreateResponse)
def create_wallet(
    user=Depends(require_user),
    storage=Depends(get_storage),
    price_provider=Depends(get_price_provider),
):
    service = WalletService(storage=storage, price_provider=price_provider)
    wallet = service.create_wallet(user.id)
    return WalletCreateResponse(**service.wallet_view(wallet))


@router.get("/wallets/{address}", response_model=WalletGetResponse)
def get_wallet(
    address: str,
    user=Depends(require_user),
    storage=Depends(get_storage),
    price_provider=Depends(get_price_provider),
):
    service = WalletService(storage=storage, price_provider=price_provider)
    wallet = service.get_wallet_owned(user.id, address)
    return WalletGetResponse(**service.wallet_view(wallet))
