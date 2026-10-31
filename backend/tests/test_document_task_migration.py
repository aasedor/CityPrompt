"""Repair legacy stamped schemas without replacing any document data."""

import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
import sqlalchemy as sa


@pytest.mark.parametrize("already_present", [False, True])
def test_document_task_binding_repair_preserves_rows_and_is_repeatable(already_present):
    path = Path(__file__).parents[1] / "migrations/versions/033_repair_document_task_binding.py"
    spec = importlib.util.spec_from_file_location("document_task_repair", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        suffix = ", processing_task_id VARCHAR(100)" if already_present else ""
        connection.execute(sa.text(f"CREATE TABLE documents(id INTEGER PRIMARY KEY, filename TEXT{suffix})"))
        connection.execute(sa.text("INSERT INTO documents(id,filename) VALUES(1,'preserved.pdf')"))
        module.op = Operations(MigrationContext.configure(connection))
        module.upgrade()
        module.upgrade()
        assert connection.scalar(sa.text("SELECT filename FROM documents WHERE id=1")) == "preserved.pdf"
        assert "processing_task_id" in {value["name"] for value in sa.inspect(connection).get_columns("documents")}
        assert "ix_documents_processing_task_id" in {
            value["name"] for value in sa.inspect(connection).get_indexes("documents")
        }
    engine.dispose()
