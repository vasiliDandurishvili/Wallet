import pytest

from wallet.core.domain import User
from wallet.infra.sqlite.storage import SqliteStorage


def test_uow_commit(storage: SqliteStorage) -> None:
    with storage.uow():
        storage.users().create(User("u1", "k1"))

    user = storage.users().read("u1")
    assert user.id == "u1"


def test_uow_rollback_on_error(storage: SqliteStorage) -> None:
    def failing_transaction() -> None:
        with storage.uow():
            storage.users().create(User("u1", "k1"))
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        failing_transaction()

    assert storage.users().count() == 0
