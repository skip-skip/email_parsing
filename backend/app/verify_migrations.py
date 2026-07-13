"""Verify all Alembic migrations apply and rollback cleanly.

Usage:
    python -m backend.app.verify_migrations
    python -m backend.app.verify_migrations --db-url sqlite+aiosqlite:///./verify_test.db
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import tempfile
from pathlib import Path

from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import command


def _get_alembic_config(db_url: str) -> Config:
    alembic_ini = Path(__file__).resolve().parent.parent.parent / "alembic.ini"
    cfg = Config(str(alembic_ini))
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


async def _get_table_names(db_url: str) -> set[str]:
    engine = create_async_engine(db_url)
    async with engine.connect() as conn:
        result = await conn.run_sync(
            lambda sync_conn: set(inspect(sync_conn).get_table_names())
        )
    await engine.dispose()
    return result


async def _get_index_names(db_url: str, table: str) -> set[str]:
    engine = create_async_engine(db_url)
    async with engine.connect() as conn:
        result = await conn.run_sync(
            lambda sync_conn: {
                idx["name"]
                for idx in inspect(sync_conn).get_indexes(table)
                if idx["name"]
            }
        )
    await engine.dispose()
    return result


async def _count_records(db_url: str, table: str) -> int:
    engine = create_async_engine(db_url)
    async with engine.connect() as conn:
        result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count: int = result.scalar_one()
    await engine.dispose()
    return count


def verify_migrations(db_url: str | None = None) -> bool:
    use_temp = db_url is None
    tmp_name = ""
    if use_temp:
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db_url = f"sqlite+aiosqlite:///{tmp.name}"
        tmp_name = tmp.name
        tmp.close()

    assert db_url is not None

    alembic_cfg = _get_alembic_config(db_url)
    all_passed = True
    results: list[str] = []

    try:
        # Step 1: Apply all migrations (upgrade to head)
        print("Step 1: Applying all migrations to head...")
        try:
            command.upgrade(alembic_cfg, "head")
            results.append("[PASS] All migrations applied successfully")
        except Exception as e:
            results.append(f"[FAIL] Migration upgrade failed: {e}")
            all_passed = False

        if not all_passed:
            for r in results:
                print(r)
            return False

        # Step 2: Verify expected tables exist
        print("Step 2: Verifying tables exist...")
        expected_tables = {
            "tickets", "emails", "calendar_events", "ai_logs", "alembic_version",
        }
        actual_tables = asyncio.run(_get_table_names(db_url))

        if expected_tables.issubset(actual_tables):
            results.append(
                f"[PASS] All expected tables exist: {sorted(expected_tables)}"
            )
        else:
            missing = expected_tables - actual_tables
            results.append(f"[FAIL] Missing tables: {sorted(missing)}")
            all_passed = False

        # Step 3: Verify indexes exist
        print("Step 3: Verifying indexes...")
        expected_indexes: dict[str, list[str]] = {
            "tickets": [
                "ix_tickets_status", "ix_tickets_conversation_id",
                "ix_tickets_client", "ix_tickets_deadline", "ix_tickets_priority",
            ],
            "emails": [
                "ix_emails_conversation_id", "ix_emails_ticket_id",
                "ix_emails_sender", "ix_emails_received_time",
            ],
            "calendar_events": [
                "ix_calendar_events_ticket_id", "ix_calendar_events_status",
                "ix_calendar_events_start_time",
            ],
            "ai_logs": [
                "ix_ai_logs_ticket_id", "ix_ai_logs_created_at",
                "ix_ai_logs_success", "ix_ai_logs_model", "ix_ai_logs_confidence",
            ],
        }

        for table, indexes in expected_indexes.items():
            actual = asyncio.run(_get_index_names(db_url, table))
            missing_indexes = [idx for idx in indexes if idx not in actual]
            if not missing_indexes:
                results.append(f"[PASS] {table}: all {len(indexes)} indexes present")
            else:
                results.append(f"[FAIL] {table}: missing indexes {missing_indexes}")
                all_passed = False

        # Step 4: Test rollback and re-apply
        print("Step 4: Testing rollback capability...")
        command.downgrade(alembic_cfg, "base")
        results.append("[PASS] Rolled back to base successfully")

        command.upgrade(alembic_cfg, "head")
        results.append("[PASS] Re-applied all migrations successfully")

        # Step 5: Verify alembic_version table
        print("Step 5: Verifying alembic_version...")
        alembic_tables = asyncio.run(_get_table_names(db_url))
        if "alembic_version" in alembic_tables:
            results.append("[PASS] alembic_version table exists")
        else:
            results.append("[FAIL] alembic_version table missing")
            all_passed = False

    finally:
        if use_temp and tmp_name:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass

    # Print results
    print("\n" + "=" * 60)
    print("MIGRATION VERIFICATION RESULTS")
    print("=" * 60)
    for r in results:
        print(f"  {r}")
    print("=" * 60)

    if all_passed:
        print("All migration checks passed!")
    else:
        print("Some checks failed. Review the output above.")

    return all_passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Alembic migrations")
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Database URL to use for verification (default: temporary SQLite DB)",
    )
    args = parser.parse_args()

    success = verify_migrations(args.db_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
