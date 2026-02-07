from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal

from wallet.core.domain import SATOSHIS_PER_BTC, Wallet
from wallet.core.errors import ConflictError, NotFoundError
from wallet.core.repository.storage import Storage
from wallet.core.services.pricing import PriceProvider, quantize_usd

MAX_WALLETS_PER_USER = 3
INITIAL_WALLET_BALANCE_SAT = SATOSHIS_PER_BTC


def sat_to_btc(sat: int) -> Decimal:
    return (Decimal(sat) / Decimal(SATOSHIS_PER_BTC)).quantize(Decimal("0.00000001"))


@dataclass
class WalletService:
    storage: Storage
    price_provider: PriceProvider

    def create_wallet(self, user_id: str) -> Wallet:
        with self.storage.uow():
            wallets_repo = self.storage.wallets()
            user_wallets = [w for w in wallets_repo.read_all() if w.user_id == user_id]
            if len(user_wallets) >= MAX_WALLETS_PER_USER:
                raise ConflictError(f"User already has {MAX_WALLETS_PER_USER} wallets")

            wallet = Wallet(
                address=self._new_address(),
                user_id=user_id,
                balance_sat=INITIAL_WALLET_BALANCE_SAT,
            )
            wallets_repo.create(wallet)
            return wallet

    def get_wallet_owned(self, user_id: str, address: str) -> Wallet:
        wallet = self.storage.wallets().read(address)
        if wallet.user_id != user_id:
            raise NotFoundError("Wallet not found")
        return wallet

    def wallet_view(self, wallet: Wallet) -> dict[str, str | int]:
        quote = self.price_provider.btc_usd()
        btc = sat_to_btc(wallet.balance_sat)
        usd = quantize_usd(btc * quote.usd_per_btc)
        return {
            "address": wallet.address,
            "balance_sat": wallet.balance_sat,
            "balance_btc": format(btc, "f"),
            "balance_usd": format(usd, "f"),
        }

    def _new_address(self) -> str:
        return "w_" + uuid.uuid4().hex
