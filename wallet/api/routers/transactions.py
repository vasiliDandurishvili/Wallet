from __future__ import annotations

from fastapi import APIRouter, Depends

from wallet.api.dependencies import (
    AuthenticatedUser,
    get_price_provider,
    get_storage,
    require_user,
)
from wallet.api.models import TransactionCreateRequest, TransactionResponse
from wallet.core.services.pricing import PriceProvider
from wallet.core.services.transactions import TransactionService
from wallet.infra.sqlite.storage import SqliteStorage

router = APIRouter()


@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(
    payload: TransactionCreateRequest,
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
    storage: SqliteStorage = Depends(get_storage),  # noqa: B008
    price_provider: PriceProvider = Depends(get_price_provider),  # noqa: B008
) -> TransactionResponse:
    service = TransactionService(storage=storage, price_provider=price_provider)
    tx = service.transfer(
        user_id=user.id,
        from_address=payload.from_address,
        to_address=payload.to_address,
        amount_sat=payload.amount_sat,
    )
    return TransactionResponse(**service.tx_view(tx))


@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
    storage: SqliteStorage = Depends(get_storage),  # noqa: B008
    price_provider: PriceProvider = Depends(get_price_provider),  # noqa: B008
) -> list[TransactionResponse]:
    service = TransactionService(storage=storage, price_provider=price_provider)
    out: list[TransactionResponse] = []
    for tx in service.list_user_transactions(user.id):
        out.append(TransactionResponse(**service.tx_view(tx)))
    return out


@router.get("/wallets/{address}/transactions", response_model=list[TransactionResponse])
def list_wallet_transactions(
    address: str,
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
    storage: SqliteStorage = Depends(get_storage),  # noqa: B008
    price_provider: PriceProvider = Depends(get_price_provider),  # noqa: B008
) -> list[TransactionResponse]:
    service = TransactionService(storage=storage, price_provider=price_provider)
    out: list[TransactionResponse] = []
    for tx in service.list_wallet_transactions(user.id, address):
        out.append(TransactionResponse(**service.tx_view(tx)))
    return out
