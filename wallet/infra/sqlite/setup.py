from __future__ import annotations

import sqlite3


def setup(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            api_key TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS wallets (
            address TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            balance_sat INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            from_address TEXT NOT NULL,
            to_address TEXT NOT NULL,
            amount_sat INTEGER NOT NULL,
            fee_sat INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(from_address) REFERENCES wallets(address),
            FOREIGN KEY(to_address) REFERENCES wallets(address)
        );

        CREATE INDEX IF NOT EXISTS idx_wallets_user_id ON wallets(user_id);
        CREATE INDEX IF NOT EXISTS idx_tx_from ON transactions(from_address);
        CREATE INDEX IF NOT EXISTS idx_tx_to ON transactions(to_address);
        CREATE INDEX IF NOT EXISTS idx_tx_created_at ON transactions(created_at);
        """
    )
    connection.commit()
