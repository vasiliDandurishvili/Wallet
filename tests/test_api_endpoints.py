from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from wallet.api.app import create_app
from wallet.api.dependencies import get_price_provider
from wallet.core.services.pricing import BtcUsdQuote, PriceProvider
from wallet.settings import Settings


class FakePriceProvider(PriceProvider):
    def btc_usd(self) -> BtcUsdQuote:
        return BtcUsdQuote(usd_per_btc=Decimal("50000.00"))


def test_full_api_flow(tmp_path: Path) -> None:
    settings = Settings(database_path=tmp_path / "api.db", admin_api_key="ADMIN")
    app = create_app(settings)
    app.dependency_overrides[get_price_provider] = lambda: FakePriceProvider()

    client = TestClient(app)

    r = client.post("/users")
    assert r.status_code == 200
    user_id = r.json()["user_id"]
    api_key = r.json()["api_key"]
    assert user_id
    assert api_key

    headers = {"X-API-KEY": api_key}

    r = client.post("/wallets", headers=headers)
    assert r.status_code == 200
    w1 = r.json()
    assert w1["address"]
    assert int(w1["balance_sat"]) > 0

    r = client.post("/wallets", headers=headers)
    assert r.status_code == 200
    w2 = r.json()

    r = client.get(f"/wallets/{w1['address']}", headers=headers)
    assert r.status_code == 200
    assert r.json()["address"] == w1["address"]

    r = client.post(
        "/transactions",
        headers=headers,
        json={
            "from_address": w1["address"],
            "to_address": w2["address"],
            "amount_sat": 1000,
        },
    )
    assert r.status_code == 200
    tx = r.json()
    assert tx["from_address"] == w1["address"]
    assert tx["to_address"] == w2["address"]
    assert tx["amount_sat"] == 1000
    assert tx["fee_sat"] == 0

    r = client.get("/transactions", headers=headers)
    assert r.status_code == 200
    txs = r.json()
    assert len(txs) == 1

    r = client.get(f"/wallets/{w1['address']}/transactions", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get("/statistics", headers={"X-API-KEY": "NOT_ADMIN"})
    assert r.status_code == 403

    r = client.get("/statistics", headers={"X-API-KEY": "ADMIN"})
    assert r.status_code == 200
    stats = r.json()
    assert stats["total_transactions"] == 1
    assert stats["platform_profit_sat"] == 0
