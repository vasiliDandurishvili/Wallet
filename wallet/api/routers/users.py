from __future__ import annotations

from fastapi import APIRouter, Depends

from wallet.api.dependencies import get_storage
from wallet.api.models import UserCreateResponse
from wallet.core.services.users import UserService

router = APIRouter()


@router.post("/users", response_model=UserCreateResponse)
def create_user(storage=Depends(get_storage)) -> UserCreateResponse:
    user = UserService(storage).register()
    return UserCreateResponse(user_id=user.id, api_key=user.api_key)
