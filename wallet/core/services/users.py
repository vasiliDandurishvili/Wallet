from __future__ import annotations

import secrets
import uuid
from dataclasses import dataclass

from wallet.core.domain import User
from wallet.core.errors import ConflictError
from wallet.core.repository.storage import Storage


@dataclass
class UserService:
    storage: Storage

    def register(self) -> User:
        api_key = secrets.token_urlsafe(32)
        user = User(id=str(uuid.uuid4()), api_key=api_key)

        if any(u.api_key == api_key for u in self.storage.users().read_all()):
            raise ConflictError("API key collision; retry")

        with self.storage.uow():
            self.storage.users().create(user)
        return user
