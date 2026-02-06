import pytest

from wallet.core.domain import User, Wallet
from wallet.core.errors import ConflictError, NotFoundError
from wallet.infra.sqlite.storage import SqliteStorage


def test_create_and_read_wallet(storage: SqliteStorage) -> None:
    users = storage.users()
    wallets = storage.wallets()

    users.create(User(id="u1", api_key="k1"))

    wallet = Wallet(address="addr1", user_id="u1", balance_sat=1000)
    wallets.create(wallet)

    loaded = wallets.read("addr1")
    assert loaded == wallet


def test_read_all_and_count_wallet(storage: SqliteStorage) -> None:
    users = storage.users()
    wallets = storage.wallets()

    users.create(User(id="u1", api_key="k1"))
    users.create(User(id="u2", api_key="k2"))
    wallets.create(Wallet(address="w1", user_id="u1", balance_sat=100))
    wallets.create(Wallet(address="w2", user_id="u1", balance_sat=200))
    wallets.create(Wallet(address="w3", user_id="u2", balance_sat=300))

    assert wallets.count() == 3

    loaded = wallets.read_all()

    addresses = {w.address for w in loaded}
    assert addresses == {"w1", "w2", "w3"}

    balances = {w.address: w.balance_sat for w in loaded}
    assert balances["w1"] == 100
    assert balances["w2"] == 200
    assert balances["w3"] == 300


def test_update_wallet_balance(storage: SqliteStorage) -> None:
    users = storage.users()
    wallets = storage.wallets()

    users.create(User(id="u1", api_key="k1"))
    wallets.create(Wallet("addr1", "u1", 1000))

    wallets.update(Wallet("addr1", "u1", 500))

    updated = wallets.read("addr1")
    assert updated.balance_sat == 500


def test_delete_wallet(storage: SqliteStorage) -> None:
    users = storage.users()
    wallets = storage.wallets()

    users.create(User(id="u1", api_key="k1"))
    wallets.create(Wallet("addr1", "u1", 1000))

    wallets.delete("addr1")

    with pytest.raises(NotFoundError):
        wallets.read("addr1")


def test_wallet_conflict(storage: SqliteStorage) -> None:
    users = storage.users()
    wallets = storage.wallets()

    users.create(User(id="u1", api_key="key1"))
    wallet = Wallet(address="w1", user_id="u1", balance_sat=100)
    wallets.create(wallet)

    with pytest.raises(ConflictError):
        wallets.create(wallet)
