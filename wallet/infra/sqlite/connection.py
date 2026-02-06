from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@dataclass
class SqliteUnitOfWork:
    conn: sqlite3.Connection

    def __enter__(self) -> SqliteUnitOfWork:
        self.conn.execute("BEGIN IMMEDIATE;")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        if exc_type is None:
            self.conn.commit()
            return None
        self.conn.rollback()
        return None
