import pytest

from wallet.core.domain import User
from wallet.core.errors import ConflictError, NotFoundError
from wallet.infra.sqlite.storage import SqliteStorage


def test_create_and_read_user(storage: SqliteStorage) -> None:
    repo = storage.users()

    user = User(id="u1", api_key="key-123")
    repo.create(user)

    loaded = repo.read("u1")

    assert loaded == user


def test_read_all_users(storage: SqliteStorage) -> None:
    repo = storage.users()

    repo.create(User(id="u1", api_key="k1"))
    repo.create(User(id="u2", api_key="k2"))

    users = list(repo.read_all())

    assert len(users) == 2
    assert {u.id for u in users} == {"u1", "u2"}


def test_read_by_api_key(storage: SqliteStorage) -> None:
    repo = storage.users()

    repo.create(User(id="u123", api_key="key-123"))

    loaded = repo.read_by_api_key("key-123")
    assert loaded.id == "u123"
    assert loaded.api_key == "key-123"

    with pytest.raises(NotFoundError):
        repo.read_by_api_key("non-existent-key")


def test_update_user(storage: SqliteStorage) -> None:
    repo = storage.users()

    repo.create(User(id="u1", api_key="k1"))
    repo.update(User(id="u1", api_key="k2"))

    updated = repo.read("u1")
    assert updated.api_key == "k2"


def test_delete_user(storage: SqliteStorage) -> None:
    repo = storage.users()

    repo.create(User(id="u1", api_key="k1"))
    repo.delete("u1")

    with pytest.raises(NotFoundError):
        repo.read("u1")


def test_user_count(storage: SqliteStorage) -> None:
    repo = storage.users()

    assert repo.count() == 0
    repo.create(User(id="u1", api_key="k1"))
    assert repo.count() == 1


def test_duplicate_user_id_raises(storage: SqliteStorage) -> None:
    repo = storage.users()

    repo.create(User(id="u1", api_key="k1"))

    with pytest.raises(ConflictError):
        repo.create(User(id="u1", api_key="k2"))
