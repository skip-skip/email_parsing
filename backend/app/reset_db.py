"""Reset the database by dropping all tables and re-running migrations.

Usage:
    python -m backend.app.reset_db
    python -m backend.app.reset_db --confirm
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from alembic.config import Config

from alembic import command


async def reset_database() -> None:
    """Drop all tables and recreate via Alembic migrations."""
    alembic_cfg = Config("alembic.ini")
    await asyncio.get_event_loop().run_in_executor(
        None, command.downgrade, alembic_cfg, "base"
    )
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
