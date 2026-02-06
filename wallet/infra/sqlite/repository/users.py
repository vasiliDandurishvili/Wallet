from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass

from wallet.core.domain import User
from wallet.core.errors import ConflictError, NotFoundError
from wallet.core.repository.repository import Repository


@dataclass
class SqliteUserRepository(Repository[User]):
    conn: sqlite3.Connection

    def create(self, item: User) -> None:
        try:
            self.conn.execute(
                "INSERT INTO users(id, api_key) VALUES(?, ?);", (item.id, item.api_key)
            )
        except sqlite3.IntegrityError as e:
            raise ConflictError("User Conflict") from e

    def read(self, item_id: str) -> User:
        row = self.conn.execute(
            "SELECT id, api_key FROM users WHERE id = ?;", (item_id,)
        ).fetchone()
        if row is None:
            raise NotFoundError("User not found")
        return User(id=str(row["id"]), api_key=str(row["api_key"]))

    def read_by_api_key(self, api_key: str) -> User:
        row = self.conn.execute(
            "SELECT id, api_key FROM users WHERE api_key = ?;", (api_key,)
        ).fetchone()
        if row is None:
            raise NotFoundError("User not found")
        return User(id=str(row["id"]), api_key=str(row["api_key"]))

    def update(self, item: User) -> None:
        cur = self.conn.execute(
            "UPDATE users SET api_key = ? WHERE id = ?;", (item.api_key, item.id)
        )
        if cur.rowcount == 0:
            raise NotFoundError("User not found")

    def delete(self, item_id: str) -> None:
        cur = self.conn.execute("DELETE FROM users WHERE id = ?;", (item_id,))
        if cur.rowcount == 0:
            raise NotFoundError("User not found")

    def read_all(self) -> Iterable[User]:
        rows = self.conn.execute("SELECT id, api_key FROM users;").fetchall()
        return [User(id=str(r["id"]), api_key=str(r["api_key"])) for r in rows]

    def count(self) -> int:
        (cnt,) = self.conn.execute("SELECT COUNT(*) FROM users;").fetchone()
        return int(cnt)
