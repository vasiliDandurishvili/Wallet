from unittest.mock import patch

import pytest

from wallet.core.domain import SATOSHIS_PER_BTC
from wallet.core.errors import (
    ConflictError,
    InsufficientFundsError,
    NotFoundError,
    ValidationError,
)
from wallet.core.services.transactions import TransactionService, external_fee_sat
from wallet.core.services.users import UserService
from wallet.core.services.wallets import WalletService


def test_register_user_collision(user_service: UserService) -> None:
    with patch("secrets.token_urlsafe", return_value="fixed_api_key"):
        user1 = user_service.register()
        assert user1.api_key == "fixed_api_key"

        with pytest.raises(ConflictError):
            user_service.register()


def test_create_wallet(
    user_service: UserService, wallet_service: WalletService
) -> None:
    user = user_service.register()
    user_id = user.id

    w1 = wallet_service.create_wallet(user_id)
    w2 = wallet_service.create_wallet(user_id)
    w3 = wallet_service.create_wallet(user_id)
    assert all(w.user_id == user_id for w in [w1, w2, w3])

    with pytest.raises(ConflictError):
        wallet_service.create_wallet(user_id)


def test_get_wallet_owned(
    user_service: UserService, wallet_service: WalletService
) -> None:
    user = user_service.register()
    user_id = user.id
    wallet = wallet_service.create_wallet(user_id)

    w = wallet_service.get_wallet_owned(user_id, wallet.address)
    assert w.address == wallet.address

    with pytest.raises(NotFoundError):
        wallet_service.get_wallet_owned("other_user", wallet.address)


def test_wallet_view(user_service: UserService, wallet_service: WalletService) -> None:
    user = user_service.register()
    user_id = user.id
    wallet = wallet_service.create_wallet(user_id)
    view = wallet_service.wallet_view(wallet)

    assert view["balance_sat"] == SATOSHIS_PER_BTC
    assert float(view["balance_usd"]) > 0
    assert view["address"] == wallet.address


def test_transfer_between_wallets(
    user_service: UserService,
    wallet_service: WalletService,
    tx_service: TransactionService,
) -> None:
    user1 = user_service.register().id
    user2 = user_service.register().id
    w1 = wallet_service.create_wallet(user1)
    w2 = wallet_service.create_wallet(user2)

    amount = 50_000_000
    tx = tx_service.transfer(user1, w1.address, w2.address, amount)

    expected_fee = external_fee_sat(amount)
    assert tx.fee_sat == expected_fee

    assert (
        tx_service.storage.wallets().read(w1.address).balance_sat
        == SATOSHIS_PER_BTC - amount
    )

    assert tx_service.storage.wallets().read(
        w2.address
    ).balance_sat == SATOSHIS_PER_BTC + (amount - expected_fee)

    with pytest.raises(InsufficientFundsError):
        tx_service.transfer(user1, w1.address, w2.address, SATOSHIS_PER_BTC * 10)

    with pytest.raises(ValidationError):
        tx_service.transfer(user1, w1.address, w1.address, 1000)


def test_transfer_fee_is_zero_for_same_user(
    user_service: UserService,
    wallet_service: WalletService,
    tx_service: TransactionService,
) -> None:
    user = user_service.register().id
    w1 = wallet_service.create_wallet(user)
    w2 = wallet_service.create_wallet(user)

    amount = 10_000_000
    tx = tx_service.transfer(user, w1.address, w2.address, amount)

    assert tx.fee_sat == 0
    assert (
        tx_service.storage.wallets().read(w1.address).balance_sat
        == SATOSHIS_PER_BTC - amount
    )
    assert (
        tx_service.storage.wallets().read(w2.address).balance_sat
        == SATOSHIS_PER_BTC + amount
    )


def test_list_user_transactions(
    user_service: UserService,
    wallet_service: WalletService,
    tx_service: TransactionService,
) -> None:
    user1 = user_service.register().id
    user2 = user_service.register().id
    w1 = wallet_service.create_wallet(user1)
    w2 = wallet_service.create_wallet(user2)

    txs = tx_service.list_user_transactions(user1)
    assert txs == []

    tx_service.transfer(user1, w1.address, w2.address, 10_000_000)
    txs = tx_service.list_user_transactions(user1)
    assert len(txs) == 1


def test_tx_view(
    user_service: UserService,
    wallet_service: WalletService,
    tx_service: TransactionService,
) -> None:
    user1 = user_service.register().id
    user2 = user_service.register().id
    w1 = wallet_service.create_wallet(user1)
    w2 = wallet_service.create_wallet(user2)

    tx = tx_service.transfer(user1, w1.address, w2.address, 10_000_000)
    view = tx_service.tx_view(tx)

    assert view["id"] == tx.id
    assert view["amount_sat"] == 10_000_000
    assert float(view["amount_usd"]) > 0
    assert float(view["fee_usd"]) > 0
