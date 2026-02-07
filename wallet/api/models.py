from __future__ import annotations

from pydantic import BaseModel, Field


class UserCreateResponse(BaseModel):
    user_id: str
    api_key: str


class WalletCreateResponse(BaseModel):
    address: str
    balance_sat: int
    balance_btc: str
    balance_usd: str


class WalletGetResponse(WalletCreateResponse):
    pass


class TransactionCreateRequest(BaseModel):
    from_address: str
    to_address: str
    amount_sat: int


class TransactionResponse(BaseModel):
    id: str
    from_address: str
    to_address: str
    amount_sat: int
    amount_btc: str
    amount_usd: str
    fee_sat: int
    fee_btc: str
    fee_usd: str
    created_at: str


class StatisticsResponse(BaseModel):
    total_transactions: int
    platform_profit_sat: int
    platform_profit_btc: str
    platform_profit_usd: str
