from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass

from wallet.core.domain import Wallet
from wallet.core.errors import ConflictError, NotFoundError
from wallet.core.repository.repository import Repository


@dataclass
class SqliteWalletRepository(Repository[Wallet]):
    conn: sqlite3.Connection

    def create(self, item: Wallet) -> None:
        try:
            self.conn.execute(
                "INSERT INTO wallets(address, user_id, balance_sat) VALUES(?, ?, ?);",
                (item.address, item.user_id, item.balance_sat),
            )
        except sqlite3.IntegrityError as e:
            raise ConflictError("Wallet conflict") from e

    def read(self, item_id: str) -> Wallet:
        row = self.conn.execute(
            "SELECT address, user_id, balance_sat FROM wallets WHERE address = ?;",
            (item_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("Wallet not found")
        return Wallet(
            address=str(row["address"]),
            user_id=str(row["user_id"]),
            balance_sat=int(row["balance_sat"]),
        )

    def update(self, item: Wallet) -> None:
        cur = self.conn.execute(
            "UPDATE wallets SET user_id = ?, balance_sat = ? WHERE address = ?;",
            (item.user_id, item.balance_sat, item.address),
        )
        if cur.rowcount == 0:
            raise NotFoundError("Wallet not found")

    def delete(self, item_id: str) -> None:
        cur = self.conn.execute("DELETE FROM wallets WHERE address = ?;", (item_id,))
        if cur.rowcount == 0:
            raise NotFoundError("Wallet not found")

    def read_all(self) -> Iterable[Wallet]:
        rows = self.conn.execute(
            "SELECT address, user_id, balance_sat FROM wallets;"
        ).fetchall()
        return [
            Wallet(
                address=str(r["address"]),
                user_id=str(r["user_id"]),
                balance_sat=int(r["balance_sat"]),
            )
            for r in rows
        ]

    def count(self) -> int:
        (cnt,) = self.conn.execute("SELECT COUNT(*) FROM wallets;").fetchone()
        return int(cnt)
