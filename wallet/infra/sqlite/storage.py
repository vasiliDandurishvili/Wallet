from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from wallet.core.repository.storage import Storage, UnitOfWork
from wallet.infra.sqlite.connection import SqliteUnitOfWork
from wallet.infra.sqlite.repository.transactions import SqliteTransactionRepository
from wallet.infra.sqlite.repository.users import SqliteUserRepository
from wallet.infra.sqlite.repository.wallets import SqliteWalletRepository


@dataclass
class SqliteStorage(Storage):
    conn: sqlite3.Connection

    def users(self) -> SqliteUserRepository:
        return SqliteUserRepository(self.conn)

    def wallets(self) -> SqliteWalletRepository:
        return SqliteWalletRepository(self.conn)

    def transactions(self) -> SqliteTransactionRepository:
        return SqliteTransactionRepository(self.conn)

    def uow(self) -> UnitOfWork:
        return SqliteUnitOfWork(self.conn)
