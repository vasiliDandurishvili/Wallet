from __future__ import annotations

from fastapi import FastAPI

from wallet.api.errors_handler import install_error_handlers
from wallet.api.routers.statistics import router as statistics_router
from wallet.api.routers.transactions import router as transactions_router
from wallet.api.routers.users import router as users_router
from wallet.api.routers.wallets import router as wallets_router
from wallet.settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Bitcoin Wallet API")
    app.state.settings = settings
    install_error_handlers(app)

    app.include_router(users_router)
    app.include_router(wallets_router)
    app.include_router(transactions_router)
    app.include_router(statistics_router)
    return app
