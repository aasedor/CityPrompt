"""Fail-closed startup migrations, serialized across API replicas."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

from app.core.config import get_settings

MIGRATION_LOCK = 23_140_785_570_741


def migration_config():
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    return config


def expected_schema_heads():
    return set(ScriptDirectory.from_config(migration_config()).get_heads())


def prepare_database():
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    try:
        with engine.connect() as lock:
            lock.execute(text("SELECT pg_advisory_lock(:key)"), {"key": MIGRATION_LOCK})
            lock.commit()
            try:
                with engine.begin() as db:
                    db.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
                    db.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                command.upgrade(migration_config(), "head")
                with engine.connect() as db:
                    heads = set(db.execute(text("SELECT version_num FROM alembic_version")).scalars())
                    if heads != expected_schema_heads():
                        raise RuntimeError("Database schema does not match this release")
            finally:
                lock.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": MIGRATION_LOCK})
                lock.commit()
    finally:
        engine.dispose()


if __name__ == "__main__":
    prepare_database()
