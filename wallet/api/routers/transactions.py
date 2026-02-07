from __future__ import annotations

from fastapi import APIRouter, Depends

from wallet.api.dependencies import get_price_provider, get_storage, require_user
from wallet.api.models import TransactionCreateRequest, TransactionResponse
from wallet.core.services.transactions import TransactionService

router = APIRouter()


@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(
    payload: TransactionCreateRequest,
    user=Depends(require_user),
    storage=Depends(get_storage),
    price_provider=Depends(get_price_provider),
):
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
    user=Depends(require_user),
    storage=Depends(get_storage),
    price_provider=Depends(get_price_provider),
):
    service = TransactionService(storage=storage, price_provider=price_provider)
    out: list[TransactionResponse] = []
    for tx in service.list_user_transactions(user.id):
        out.append(TransactionResponse(**service.tx_view(tx)))
    return out


@router.get("/wallets/{address}/transactions", response_model=list[TransactionResponse])
def list_wallet_transactions(
    address: str,
    user=Depends(require_user),
    storage=Depends(get_storage),
    price_provider=Depends(get_price_provider),
):
    service = TransactionService(storage=storage, price_provider=price_provider)
    out: list[TransactionResponse] = []
    for tx in service.list_wallet_transactions(user.id, address):
        out.append(TransactionResponse(**service.tx_view(tx)))
    return out
