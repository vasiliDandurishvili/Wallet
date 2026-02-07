from __future__ import annotations

from pathlib import Path

import uvicorn

from wallet.api.app import create_app
from wallet.settings import Settings


def run() -> None:
    settings = Settings(database_path=Path("wallet.sqlite3"))
    app = create_app(settings)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    run()
