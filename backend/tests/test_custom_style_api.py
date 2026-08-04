"""
Tests for the Custom Style prompt-expansion API and the document metadata endpoint.

Uses mock DB (per conftest) and a mocked Anthropic client — no network calls.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

import app.api.v1.custom_style as custom_style_module
from tests.conftest import FakeProject


class FakeDocument:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.project_id = kwargs.get("project_id", uuid.uuid4())
        self.filename = kwargs.get("filename", "brief.pdf")
        self.file_type = kwargs.get("file_type", "pdf")
        self.file_size_bytes = kwargs.get("file_size_bytes", 1234)
        self.storage_url = kwargs.get("storage_url", "http://minio:9000/bucket/key.pdf")
        self.processing_status = kwargs.get("processing_status", "completed")
        self.extracted_data = kwargs.get("extracted_data", None)
        self.uploaded_at = kwargs.get("uploaded_at", datetime.now(timezone.utc))
        self.processed_at = kwargs.get("processed_at", None)


def _scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def _scalars_result(values):
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


class FakeUsage:
    input_tokens = 100
    output_tokens = 120


class FakeTextBlock:
    type = "text"
    text = "A cluster of low timber lodges with green roofs surrounds a small pond."


class FakeMessage:
    usage = FakeUsage()
    content = [FakeTextBlock()]


def _mock_anthropic(monkeypatch, message=None, error=None):
    """Replace anthropic.AsyncAnthropic with a stub returning `message`."""
    create_mock = AsyncMock(return_value=message or FakeMessage())
    if error is not None:
        create_mock.side_effect = error

    fake_client = MagicMock()
    fake_client.messages.create = create_mock
    monkeypatch.setattr(custom_style_module.anthropic, "AsyncAnthropic", MagicMock(return_value=fake_client))
    return create_mock


@pytest.mark.anyio
async def test_expand_requires_auth(client):
    response = await client.post(
        "/api/v1/custom-style/expand",
        json={
            "project_id": str(uuid.uuid4()),
            "user_prompt": "timber eco lodges",
        },
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_expand_forbidden_for_non_editor(client, mock_db, test_user, auth_headers):
    project = FakeProject()  # owned by someone else
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # require_auth user lookup
            _scalar_result(project),  # check_project_permission project load
            _scalar_result(None),  # no project share
        ]
    )

    response = await client.post(
        "/api/v1/custom-style/expand",
        json={
            "project_id": str(project.id),
            "user_prompt": "timber eco lodges",
        },
        headers=auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_expand_success_without_documents(client, mock_db, test_user, auth_headers, monkeypatch):
    project = FakeProject(owner_id=test_user.id)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(project),
        ]
    )
    create_mock = _mock_anthropic(monkeypatch)
    monkeypatch.setattr(custom_style_module, "log_api_usage_sync", MagicMock())

    response = await client.post(
        "/api/v1/custom-style/expand",
        json={
            "project_id": str(project.id),
            "user_prompt": "timber eco lodges around a pond",
            "zone_context": {"area_sqm": 4500, "floors": 2, "zone_type": "building"},
            "domain": "building",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "timber lodges" in data["expanded_prompt"]
    assert data["used_documents"] == []
    assert data["truncated"] is False
    # Zone facts and the user's idea should both be in the LLM user message
    sent = create_mock.call_args.kwargs["messages"][0]["content"]
    assert "timber eco lodges around a pond" in sent
    assert "4500" in sent


@pytest.mark.anyio
async def test_expand_foreign_document_404(client, mock_db, test_user, auth_headers, monkeypatch):
    project = FakeProject(owner_id=test_user.id)
    foreign_doc = FakeDocument(project_id=uuid.uuid4())  # belongs to another project
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(project),
            _scalars_result([foreign_doc]),
        ]
    )
    _mock_anthropic(monkeypatch)

    response = await client.post(
        "/api/v1/custom-style/expand",
        json={
            "project_id": str(project.id),
            "user_prompt": "timber eco lodges",
            "document_ids": [str(foreign_doc.id)],
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_expand_with_document_truncates_long_text(client, mock_db, test_user, auth_headers, monkeypatch):
    project = FakeProject(owner_id=test_user.id)
    doc = FakeDocument(
        project_id=project.id,
        processing_status="completed",
        extracted_data={"extraction": {"text_content": "cedar cladding " * 1000}},  # ~15k chars
    )
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(project),
            _scalars_result([doc]),
        ]
    )
    _mock_anthropic(monkeypatch)
    monkeypatch.setattr(custom_style_module, "log_api_usage_sync", MagicMock())

    response = await client.post(
        "/api/v1/custom-style/expand",
        json={
            "project_id": str(project.id),
            "user_prompt": "timber eco lodges",
            "document_ids": [str(doc.id)],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["truncated"] is True
    assert data["used_documents"][0]["chars_used"] == custom_style_module.MAX_CHARS_PER_DOCUMENT
    assert data["used_documents"][0]["status"] == "completed"


@pytest.mark.anyio
async def test_expand_pending_document_contributes_nothing(client, mock_db, test_user, auth_headers, monkeypatch):
    project = FakeProject(owner_id=test_user.id)
    doc = FakeDocument(project_id=project.id, processing_status="pending", extracted_data=None)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(project),
            _scalars_result([doc]),
        ]
    )
    _mock_anthropic(monkeypatch)
    monkeypatch.setattr(custom_style_module, "log_api_usage_sync", MagicMock())

    response = await client.post(
        "/api/v1/custom-style/expand",
        json={
            "project_id": str(project.id),
            "user_prompt": "timber eco lodges",
            "document_ids": [str(doc.id)],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["used_documents"][0]["status"] == "pending"
    assert data["used_documents"][0]["chars_used"] == 0


@pytest.mark.anyio
async def test_expand_returns_502_on_llm_failure(client, mock_db, test_user, auth_headers, monkeypatch):
    project = FakeProject(owner_id=test_user.id)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(project),
        ]
    )
    _mock_anthropic(monkeypatch, error=RuntimeError("api down"))

    response = await client.post(
        "/api/v1/custom-style/expand",
        json={
            "project_id": str(project.id),
            "user_prompt": "timber eco lodges",
        },
        headers=auth_headers,
    )
    assert response.status_code == 502


@pytest.mark.anyio
async def test_expand_validates_prompt_length(client, mock_db, test_user, auth_headers):
    mock_db.execute = AsyncMock(return_value=_scalar_result(test_user))  # auth lookup
    response = await client.post(
        "/api/v1/custom-style/expand",
        json={
            "project_id": str(uuid.uuid4()),
            "user_prompt": "ab",  # below min_length=3
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_document_metadata(client, mock_db, test_user, auth_headers):
    project = FakeProject(owner_id=test_user.id)
    doc = FakeDocument(project_id=project.id, processing_status="processing")
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # get_current_user lookup
            _scalar_result(doc),  # document load
            _scalar_result(project),  # project load for permission
        ]
    )

    response = await client.get(f"/api/v1/documents/{doc.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(doc.id)
    assert data["processing_status"] == "processing"


@pytest.mark.anyio
async def test_get_document_metadata_requires_auth(client):
    response = await client.get(f"/api/v1/documents/{uuid.uuid4()}")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_document_metadata_not_found(client, mock_db, test_user, auth_headers):
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(None),
        ]
    )
    response = await client.get(f"/api/v1/documents/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404
