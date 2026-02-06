from __future__ import annotations

from types import TracebackType
from typing import Protocol

from wallet.core.domain import Transaction, User, Wallet
from wallet.core.repository.repository import Repository


class UnitOfWork(Protocol):
    def __enter__(self) -> UnitOfWork:
        pass

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        pass


class Storage(Protocol):
    def users(self) -> Repository[User]:
        pass

    def wallets(self) -> Repository[Wallet]:
        pass

    def transactions(self) -> Repository[Transaction]:
        pass

    def uow(self) -> UnitOfWork:
        pass
