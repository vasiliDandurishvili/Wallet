from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

SATOSHIS_PER_BTC = 100_000_000


def utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class User:
    id: str
    api_key: str


@dataclass(frozen=True)
class Wallet:
    address: str
    user_id: str
    balance_sat: int


@dataclass(frozen=True)
class Transaction:
    id: str
    from_address: str
    to_address: str
    amount_sat: int
    fee_sat: int
    created_at: datetime
