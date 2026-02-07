from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import requests

from wallet.core.services.pricing import BtcUsdQuote, PriceProvider


@dataclass
class CoinbasePriceProvider(PriceProvider):
    def btc_usd(self) -> BtcUsdQuote:
        url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        amount = Decimal(str(data["data"]["amount"]))
        return BtcUsdQuote(usd_per_btc=amount)