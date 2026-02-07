from collections.abc import Generator
from decimal import Decimal
from pathlib import Path
from sqlite3 import Connection

import pytest

from wallet.core.services.pricing import PriceProvider, BtcUsdQuote
from wallet.core.services.transactions import TransactionService
from wallet.core.services.users import UserService
from wallet.core.services.wallets import WalletService
from wallet.infra.sqlite.connection import connect
from wallet.infra.sqlite.setup import setup
from wallet.infra.sqlite.storage import SqliteStorage


@pytest.fixture
def connection(tmp_path: Path) -> Generator[Connection]:
    db_path = tmp_path / "test.db"
    conn = connect(db_path)
    setup(conn)
    yield conn
    conn.close()


@pytest.fixture
def storage(connection) -> SqliteStorage:
    return SqliteStorage(connection)


class FakePriceProvider(PriceProvider):
    def btc_usd(self) -> BtcUsdQuote:
        return BtcUsdQuote(usd_per_btc=Decimal("50000.00"))


@pytest.fixture
def wallet_service(storage: SqliteStorage) -> WalletService:
    return WalletService(storage=storage, price_provider=FakePriceProvider())

@pytest.fixture
def user_service(storage: SqliteStorage) -> UserService:
    return UserService(storage=storage)

@pytest.fixture
def tx_service(storage: SqliteStorage) -> TransactionService:
    return TransactionService(storage=storage, price_provider=FakePriceProvider())
