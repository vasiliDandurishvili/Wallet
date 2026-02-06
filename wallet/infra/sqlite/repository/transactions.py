from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from wallet.core.domain import Transaction
from wallet.core.errors import ConflictError, NotFoundError
from wallet.core.repository.repository import Repository


@dataclass
class SqliteTransactionRepository(Repository[Transaction]):
    conn: sqlite3.Connection

    def create(self, item: Transaction) -> None:
        try:
            self.conn.execute(
                "INSERT INTO transactions(id, from_address, to_address, "
                "amount_sat, fee_sat, created_at) VALUES(?, ?, ?, ?, ?, ?);",
                (
                    item.id,
                    item.from_address,
                    item.to_address,
                    item.amount_sat,
                    item.fee_sat,
                    item.created_at.isoformat(),
                ),
            )
        except sqlite3.IntegrityError as e:
            raise ConflictError("Transaction conflict") from e

    def read(self, item_id: str) -> Transaction:
        row = self.conn.execute(
            "SELECT id, from_address, to_address, amount_sat, "
            "fee_sat, created_at FROM transactions WHERE id = ?;",
            (item_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("Transaction not found")
        return Transaction(
            id=str(row["id"]),
            from_address=str(row["from_address"]),
            to_address=str(row["to_address"]),
            amount_sat=int(row["amount_sat"]),
            fee_sat=int(row["fee_sat"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
        )

    def update(self, item: Transaction) -> None:
        cur = self.conn.execute(
            "UPDATE transactions SET from_address=?, to_address=?, amount_sat=?, "
            "fee_sat=?, created_at=? WHERE id=?;",
            (
                item.from_address,
                item.to_address,
                item.amount_sat,
                item.fee_sat,
                item.created_at.isoformat(),
                item.id,
            ),
        )
        if cur.rowcount == 0:
            raise NotFoundError("Transaction not found")

    def delete(self, item_id: str) -> None:
        cur = self.conn.execute("DELETE FROM transactions WHERE id = ?;", (item_id,))
        if cur.rowcount == 0:
            raise NotFoundError("Transaction not found")

    def read_all(self) -> Iterable[Transaction]:
        rows = self.conn.execute(
            "SELECT id, from_address, to_address, amount_sat, "
            "fee_sat, created_at FROM transactions;"
        ).fetchall()
        return [
            Transaction(
                id=str(r["id"]),
                from_address=str(r["from_address"]),
                to_address=str(r["to_address"]),
                amount_sat=int(r["amount_sat"]),
                fee_sat=int(r["fee_sat"]),
                created_at=datetime.fromisoformat(str(r["created_at"])),
            )
            for r in rows
        ]

    def count(self) -> int:
        (cnt,) = self.conn.execute("SELECT COUNT(*) FROM transactions;").fetchone()
        return int(cnt)
