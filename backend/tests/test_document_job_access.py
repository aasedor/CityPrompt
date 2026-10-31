"""Document job polling requires a persisted binding and current project access."""

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from app.api.v1 import documents
from app.core.database import get_db
from app.core.security import require_auth
from app.models.models import Document
from app.tasks import processing
from tests.conftest import FakeProject


def row(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


@pytest.fixture
async def polling(mock_db, test_user):
    app = FastAPI()
    app.include_router(documents.router, prefix="/documents")
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[require_auth] = lambda: test_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
def task_result(monkeypatch):
    result = SimpleNamespace(state="SUCCESS", info={}, result={"secret": "private provider payload"})
    lookup = MagicMock(return_value=result)
    monkeypatch.setattr(documents.celery_app, "AsyncResult", lookup)
    return result, lookup


@pytest.mark.asyncio
async def test_anonymous_status_never_looks_up_celery(client, task_result):
    response = await client.get(f"/api/v1/documents/status/{uuid.uuid4()}")
    assert response.status_code == 401
    task_result[1].assert_not_called()


@pytest.mark.asyncio
async def test_unknown_or_non_document_task_denied_before_result_lookup(polling, mock_db, task_result):
    mock_db.execute.return_value = row(None)
    response = await polling.get(f"/documents/status/{uuid.uuid4()}")
    assert response.status_code == 404
    task_result[1].assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("permission", [None, "viewer", "editor"])
async def test_current_membership_rechecked_for_known_task(polling, mock_db, test_user, task_result, permission):
    project = FakeProject()
    job_id = str(uuid.uuid4())
    document = SimpleNamespace(id=uuid.uuid4(), project_id=project.id, processing_task_id=job_id)
    share = SimpleNamespace(permission=permission) if permission else None
    mock_db.execute.side_effect = [row(document), row(project), row(share)]
    response = await polling.get(f"/documents/status/{job_id}")
    assert response.status_code == (200 if permission else 403)
    if permission is None:
        task_result[1].assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state,info", [("FAILURE", RuntimeError("private key and path")), ("RETRY", {"step": "secret"})]
)
async def test_owner_polling_sanitizes_failure_and_unknown_steps(polling, mock_db, test_user, task_result, state, info):
    project = FakeProject(owner_id=test_user.id)
    document = SimpleNamespace(id=uuid.uuid4(), project_id=project.id, processing_task_id=str(uuid.uuid4()))
    mock_db.execute.side_effect = [row(document), row(project)]
    task_result[0].state, task_result[0].info = state, info
    response = await polling.get(f"/documents/status/{document.processing_task_id}")
    assert response.status_code == 200
    assert response.json()["status"] in {"failed", "queued"}
    assert "private key" not in response.text and "secret" not in response.text


@pytest.mark.asyncio
async def test_owner_completion_returns_only_public_document_summary(polling, mock_db, test_user, task_result):
    project = FakeProject(owner_id=test_user.id)
    document = SimpleNamespace(id=uuid.uuid4(), project_id=project.id, processing_task_id=str(uuid.uuid4()))
    mock_db.execute.side_effect = [row(document), row(project)]
    response = await polling.get(f"/documents/status/{document.processing_task_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["result"] == {"document_id": str(document.id)}
    assert "private provider" not in response.text
    query = mock_db.execute.call_args_list[0].args[0]
    assert query.column_descriptions[0]["entity"] is Document
    assert "documents.processing_task_id =" in str(query)
    assert document.processing_task_id in query.compile().params.values()


@pytest.mark.asyncio
async def test_worker_success_cannot_hide_persisted_extraction_failure(polling, mock_db, test_user, task_result):
    project = FakeProject(owner_id=test_user.id)
    document = SimpleNamespace(
        id=uuid.uuid4(), project_id=project.id, processing_task_id=str(uuid.uuid4()), processing_status="failed"
    )
    mock_db.execute.side_effect = [row(document), row(project)]
    task_result[0].state = "SUCCESS"
    task_result[0].result = {"status": "failed", "error": "sensitive path"}
    response = await polling.get(f"/documents/status/{document.processing_task_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert "sensitive" not in response.text


@pytest.mark.asyncio
async def test_revoked_share_cannot_poll_previously_authorized_job(polling, mock_db, task_result):
    project = FakeProject()
    document = SimpleNamespace(id=uuid.uuid4(), project_id=project.id, processing_task_id=str(uuid.uuid4()))
    mock_db.execute.side_effect = [
        row(document),
        row(project),
        row(SimpleNamespace(permission="viewer")),
        row(document),
        row(project),
        row(None),
    ]
    first = await polling.get(f"/documents/status/{document.processing_task_id}")
    assert first.status_code == 200
    task_result[1].reset_mock()
    second = await polling.get(f"/documents/status/{document.processing_task_id}")
    assert second.status_code == 403
    task_result[1].assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "progress,expected",
    [(float("nan"), 0), (float("inf"), 0), (-0.5, 0), (2, 1), ("private payload", 0), (10**400, 0)],
)
async def test_status_progress_is_bounded_public_number(polling, mock_db, test_user, task_result, progress, expected):
    project = FakeProject(owner_id=test_user.id)
    document = SimpleNamespace(id=uuid.uuid4(), project_id=project.id, processing_task_id=str(uuid.uuid4()))
    mock_db.execute.side_effect = [row(document), row(project)]
    task_result[0].state = "PROCESSING"
    task_result[0].info = {"progress": progress, "step": "private payload"}
    response = await polling.get(f"/documents/status/{document.processing_task_id}")
    assert response.status_code == 200
    assert response.json()["progress"] == expected
    assert "private payload" not in response.text


@pytest.mark.asyncio
async def test_reprocessing_persists_binding_before_dispatch(polling, mock_db, test_user, monkeypatch):
    project = FakeProject(owner_id=test_user.id)
    document = SimpleNamespace(id=uuid.uuid4(), project_id=project.id, filename="source.pdf", processing_task_id=None)
    mock_db.execute.side_effect = [row(document), row(project)]

    def dispatch(*, args, kwargs, task_id):
        assert mock_db.commit.await_count == 1
        assert document.processing_task_id == task_id
        assert args == [str(document.id)] and kwargs == {"extract_only": False}
        return SimpleNamespace(id=task_id)

    monkeypatch.setattr(processing.process_document, "apply_async", dispatch)
    # A real broker is never contacted even before the fix.
    monkeypatch.setattr(processing.process_document, "delay", lambda *_: SimpleNamespace(id="unbound-task"))
    response = await polling.post(f"/documents/{document.id}/process")
    assert response.status_code == 200
    assert response.json()["job_id"] == document.processing_task_id
    assert document.processing_task_id is not None
