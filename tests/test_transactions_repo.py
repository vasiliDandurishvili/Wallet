from dataclasses import replace
from datetime import UTC, datetime

import pytest

from wallet.core.domain import Transaction, User, Wallet
from wallet.core.errors import ConflictError, NotFoundError
from wallet.infra.sqlite.storage import SqliteStorage

FIXED_DATETIME = datetime(2026, 2, 6, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def populated_storage(storage: SqliteStorage) -> SqliteStorage:
    storage.users().create(User(id="u1", api_key="k1"))
    storage.users().create(User(id="u2", api_key="k2"))
    storage.wallets().create(Wallet(address="w1", user_id="u1", balance_sat=1000))
    storage.wallets().create(Wallet(address="w2", user_id="u2", balance_sat=500))
    return storage


def test_create_and_read_transaction(populated_storage: SqliteStorage) -> None:
    tx = Transaction(
        id="t1",
        from_address="w1",
        to_address="w2",
        amount_sat=100,
        fee_sat=1,
        created_at=FIXED_DATETIME,
    )
    populated_storage.transactions().create(tx)
    fetched = populated_storage.transactions().read("t1")
    assert fetched.amount_sat == 100
    assert fetched.from_address == "w1"
    assert fetched.to_address == "w2"
    assert fetched.created_at == FIXED_DATETIME


def test_transaction_read_all(populated_storage: SqliteStorage) -> None:
    tx1 = Transaction(
        id="t1",
        from_address="w1",
        to_address="w2",
        amount_sat=100,
        fee_sat=1,
        created_at=FIXED_DATETIME,
    )
    tx2 = Transaction(
        id="t2",
        from_address="w2",
        to_address="w1",
        amount_sat=50,
        fee_sat=1,
        created_at=FIXED_DATETIME,
    )

    populated_storage.transactions().create(tx1)
    populated_storage.transactions().create(tx2)

    all_tx = populated_storage.transactions().read_all()
    assert populated_storage.transactions().count() == 2

    ids = {tx.id for tx in all_tx}
    assert ids == {"t1", "t2"}


def test_transaction_update(populated_storage: SqliteStorage) -> None:
    tx = Transaction(
        id="t1",
        from_address="w1",
        to_address="w2",
        amount_sat=100,
        fee_sat=1,
        created_at=FIXED_DATETIME,
    )
    populated_storage.transactions().create(tx)

    updated_tx = replace(tx, amount_sat=200, fee_sat=2)

    populated_storage.transactions().update(updated_tx)

    fetched = populated_storage.transactions().read("t1")
    assert fetched.amount_sat == 200
    assert fetched.fee_sat == 2
    assert fetched.from_address == "w1"
    assert fetched.to_address == "w2"


def test_transaction_delete(populated_storage: SqliteStorage) -> None:
    tx = Transaction(
        id="t1",
        from_address="w1",
        to_address="w2",
        amount_sat=100,
        fee_sat=1,
        created_at=FIXED_DATETIME,
    )
    populated_storage.transactions().create(tx)

    populated_storage.transactions().delete("t1")

    with pytest.raises(NotFoundError):
        populated_storage.transactions().read("t1")


def test_transaction_delete_not_found(populated_storage: SqliteStorage) -> None:
    with pytest.raises(NotFoundError):
        populated_storage.transactions().delete("nonexistent")


def test_transaction_conflict(populated_storage: SqliteStorage) -> None:
    tx = Transaction(
        id="t1",
        from_address="w1",
        to_address="w2",
        amount_sat=100,
        fee_sat=1,
        created_at=FIXED_DATETIME,
    )
    populated_storage.transactions().create(tx)
    with pytest.raises(ConflictError):
        populated_storage.transactions().create(tx)


def test_transaction_count(populated_storage: SqliteStorage) -> None:
    assert populated_storage.transactions().count() == 0

    tx1 = Transaction(
        id="t1",
        from_address="w1",
        to_address="w2",
        amount_sat=100,
        fee_sat=1,
        created_at=FIXED_DATETIME,
    )
    tx2 = Transaction(
        id="t2",
        from_address="w2",
        to_address="w1",
        amount_sat=50,
        fee_sat=1,
        created_at=FIXED_DATETIME,
    )

    populated_storage.transactions().create(tx1)
    populated_storage.transactions().create(tx2)

    assert populated_storage.transactions().count() == 2

    populated_storage.transactions().delete("t1")
    assert populated_storage.transactions().count() == 1
