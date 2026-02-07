from __future__ import annotations

from fastapi import APIRouter, Depends

from wallet.api.dependencies import get_price_provider, get_storage, require_admin
from wallet.api.models import StatisticsResponse
from wallet.core.services.pricing import quantize_usd
from wallet.core.services.transactions import TransactionService
from wallet.core.services.wallets import sat_to_btc

router = APIRouter()


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    dependencies=[Depends(require_admin)],
)
def statistics(
    storage=Depends(get_storage), price_provider=Depends(get_price_provider)
):
    service = TransactionService(storage=storage, price_provider=price_provider)

    total = storage.transactions().count()
    profit_sat = service.platform_profit_sat()

    quote = price_provider.btc_usd()
    profit_btc = sat_to_btc(profit_sat)
    profit_usd = quantize_usd(profit_btc * quote.usd_per_btc)

    return StatisticsResponse(
        total_transactions=total,
        platform_profit_sat=profit_sat,
        platform_profit_btc=format(profit_btc, "f"),
        platform_profit_usd=format(profit_usd, "f"),
    )
