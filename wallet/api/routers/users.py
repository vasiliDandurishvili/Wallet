from __future__ import annotations

from fastapi import APIRouter, Depends

from wallet.api.dependencies import get_storage
from wallet.api.models import UserCreateResponse
from wallet.core.services.users import UserService
from wallet.infra.sqlite.storage import SqliteStorage

router = APIRouter()


@router.post("/users", response_model=UserCreateResponse)
def create_user(storage: SqliteStorage = Depends(get_storage)) -> UserCreateResponse:  # noqa: B008
    user = UserService(storage).register()
    return UserCreateResponse(user_id=user.id, api_key=user.api_key)
