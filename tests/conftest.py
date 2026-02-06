from collections.abc import Generator
from pathlib import Path
from sqlite3 import Connection

import pytest

from wallet.infra.sqlite.connection import connect
from wallet.infra.sqlite.setup import setup
from wallet.infra.sqlite.storage import SqliteStorage


@pytest.fixture
def connection(tmp_path: Path) -> Generator[Connection]:
    db_path = tmp_path / "test.db"
    conn = connect(db_path)
    setup(conn)
    yield conn
    conn.close()


@pytest.fixture
def storage(connection: Connection) -> SqliteStorage:
    return SqliteStorage(connection)
