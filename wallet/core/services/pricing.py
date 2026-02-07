from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

USD_QUANT = Decimal("0.01")


def quantize_usd(x: Decimal) -> Decimal:
    return x.quantize(USD_QUANT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class BtcUsdQuote:
    usd_per_btc: Decimal


class PriceProvider(Protocol):
    def btc_usd(self) -> BtcUsdQuote: ...
