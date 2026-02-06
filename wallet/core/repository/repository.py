from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, TypeVar

T = TypeVar("T")


class Repository(Protocol[T]):
    def create(self, item: T) -> None:
        pass

    def read(self, item_id: str) -> T:
        pass

    def update(self, item: T) -> None:
        pass

    def delete(self, item_id: str) -> None:
        pass

    def read_all(self) -> Iterable[T]:
        pass

    def count(self) -> int:
        pass
