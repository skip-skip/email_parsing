"""Reset the database by dropping all tables and re-running migrations.

Usage:
    python -m backend.app.reset_db
    python -m backend.app.reset_db --confirm
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sqlite3
import sys
from pathlib import Path

from alembic.config import Config

from alembic import command


async def reset_database() -> None:
    """Drop all tables and recreate via Alembic migrations.

    Handles three database states:
    - Clean (no data.db): skips downgrade, runs upgrade directly
    - Corrupt (tables exist but no alembic_version): deletes file, runs upgrade
    - Normal (alembic_version present): downgrade base, then upgrade head
    """
    alembic_cfg = Config("alembic.ini")
    db_url = alembic_cfg.get_main_option("sqlalchemy.url")
    db_path = Path(db_url.split("///")[-1])

    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        has_version_table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
        ).fetchone() is not None
        conn.close()

        if has_version_table:
            await asyncio.get_event_loop().run_in_executor(
                None, command.downgrade, alembic_cfg, "base"
            )
        else:
            os.remove(db_path)

    await asyncio.get_event_loop().run_in_executor(
        None, command.upgrade, alembic_cfg, "head"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset the database")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt",
    )
    args = parser.parse_args()

    if not args.confirm:
        response = input("WARNING: This will delete all data. Are you sure? [y/N] ")
        if response.lower() != "y":
            print("Cancelled.")
            sys.exit(1)

    asyncio.run(reset_database())
    print("Database reset complete.")


if __name__ == "__main__":
    main()
