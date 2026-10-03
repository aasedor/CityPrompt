import uuid
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile
from app.api.v1 import documents, activity
from app.tasks import processing


def test_classroom_worker_refuses_paid_document_pipeline_before_loading_data(monkeypatch):
    monkeypatch.setattr(processing, "settings", SimpleNamespace(classroom_release=True))
    session = MagicMock()
    monkeypatch.setattr(processing, "_get_sync_session", session)
    with pytest.raises(ValueError, match="extraction-only"):
        processing.process_document.run(str(uuid.uuid4()))
    session.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("broker_available", [True, False])
async def test_reference_document_is_committed_before_dispatch_and_survives_broker_failure(monkeypatch, broker_available):
    user = SimpleNamespace(id=uuid.uuid4())
    project = SimpleNamespace(id=uuid.uuid4(), owner_id=user.id)
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = project
    db.execute.return_value = result
    def add(document):
        document.id = uuid.uuid4()
    db.add = MagicMock(side_effect=add)
    monkeypatch.setattr(documents, "_upload_to_storage", AsyncMock(return_value="/api/v1/files/test.pdf"))
    monkeypatch.setattr(activity, "log_activity", AsyncMock())
    def dispatch(document_id, *, extract_only):
        assert db.commit.await_count == 1 and extract_only is True
        if not broker_available:
            raise RuntimeError("simulated broker failure")
    monkeypatch.setattr(processing.process_document, "delay", dispatch)
    result = await documents.upload_document(project.id, UploadFile(filename="reference.pdf", file=BytesIO(b"test fixture")), "reference", user, db)
    assert result.storage_url == "/api/v1/files/test.pdf"
    assert result.processing_status == ("pending" if broker_available else "failed")
    if not broker_available:
        assert "file is saved" in result.extracted_data["error"]
        assert db.commit.await_count == 2
