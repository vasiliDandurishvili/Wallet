from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from wallet.core.domain import Transaction, Wallet, utcnow
from wallet.core.errors import InsufficientFundsError, NotFoundError, ValidationError
from wallet.core.repository.storage import Storage
from wallet.core.services.pricing import PriceProvider, quantize_usd
from wallet.core.services.wallets import sat_to_btc

EXTERNAL_FEE_NUM = 15
EXTERNAL_FEE_DEN = 1000

def ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b

def external_fee_sat(amount_sat: int) -> int:
    return ceil_div(amount_sat * EXTERNAL_FEE_NUM, EXTERNAL_FEE_DEN)

@dataclass
class TransactionService:
    storage: Storage
    price_provider: PriceProvider

    def transfer(
        self, user_id: str, from_address: str, to_address: str, amount_sat: int
    ) -> Transaction:
        if from_address == to_address:
            raise ValidationError("from_address and to_address must be different")
        if amount_sat <= 0:
            raise ValidationError("amount_sat must be > 0")

        with self.storage.uow():
            from_wallet = self.storage.wallets().read(from_address)
            if from_wallet.user_id != user_id:
                raise NotFoundError("Source wallet not found")

            to_wallet = self.storage.wallets().read(to_address)

            fee = 0 if to_wallet.user_id == user_id else external_fee_sat(amount_sat)
            total_transaction = amount_sat - fee
            if from_wallet.balance_sat < amount_sat:
                raise InsufficientFundsError("Insufficient funds")

            self.storage.wallets().update(
                Wallet(
                    address=from_wallet.address,
                    user_id=from_wallet.user_id,
                    balance_sat=from_wallet.balance_sat - amount_sat,
                )
            )
            self.storage.wallets().update(
                Wallet(
                    address=to_wallet.address,
                    user_id=to_wallet.user_id,
                    balance_sat=to_wallet.balance_sat + total_transaction,
                )
            )

            tx = Transaction(
                id=str(uuid.uuid4()),
                from_address=from_address,
                to_address=to_address,
                amount_sat=amount_sat,
                fee_sat=fee,
                created_at=utcnow(),
            )
            self.storage.transactions().create(tx)
            return tx

    def list_user_transactions(self, user_id: str) -> list[Transaction]:
        owned = {
            w.address for w in self.storage.wallets().read_all() if w.user_id == user_id
        }
        txs = [
            t
            for t in self.storage.transactions().read_all()
            if t.from_address in owned or t.to_address in owned
        ]
        return sorted(txs, key=lambda t: t.created_at)

    def list_wallet_transactions(self, user_id: str, address: str) -> list[Transaction]:
        wallet = self.storage.wallets().read(address)
        if wallet.user_id != user_id:
            raise NotFoundError("Wallet not found")

        txs = [
            t
            for t in self.storage.transactions().read_all()
            if t.from_address == address or t.to_address == address
        ]
        return sorted(txs, key=lambda t: t.created_at)

    def tx_view(self, tx: Transaction) -> dict[str, str | int]:
        quote = self.price_provider.btc_usd()
        amount_btc = sat_to_btc(tx.amount_sat)
        fee_btc = sat_to_btc(tx.fee_sat)

        amount_usd = quantize_usd(amount_btc * quote.usd_per_btc)

        fee_usd = quantize_usd(fee_btc * quote.usd_per_btc)

        return {
            "id": tx.id,
            "from_address": tx.from_address,
            "to_address": tx.to_address,
            "amount_sat": tx.amount_sat,
            "amount_btc": format(amount_btc, "f"),
            "amount_usd": format(amount_usd, "f"),
            "fee_sat": tx.fee_sat,
            "fee_btc": format(fee_btc, "f"),
            "fee_usd": format(fee_usd, "f"),
            "created_at": tx.created_at.isoformat(),
        }

    def platform_profit_sat(self) -> int:
        return sum(t.fee_sat for t in self.storage.transactions().read_all())
