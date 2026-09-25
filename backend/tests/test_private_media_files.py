"""Shared saved pixels must not expose private request/recovery evidence."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest
from fastapi import HTTPException, Response

from app.api.v1 import files
from app.core.security import create_project_asset_ticket, create_file_asset_ticket


@pytest.fixture
def media(mock_db, test_user, monkeypatch):
    project_id = uuid.uuid4()
    requester = uuid.uuid4()
    root = f"projects/{project_id}/video-render/attempt"
    project = SimpleNamespace(id=project_id, owner_id=test_user.id, metadata_={
        "video_pilot_attempts": [{"id": "attempt", "requested_by": str(requester),
            "status": "interrupted", "video_url": f"/api/v1/files/{root}/final.mp4"}]
    })
    mock_db.get.return_value = project
    monkeypatch.setattr(files, "check_project_asset_access", AsyncMock())
    return SimpleNamespace(project=project, requester=requester, root=root)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["get", "head", "ticket"])
@pytest.mark.parametrize("private_path", ["image-request", "video-guide", "video-checkpoint"])
async def test_owner_cannot_bypass_private_recovery_via_file_proxy(media, mock_db, test_user, monkeypatch, operation, private_path):
    paths = {
        "image-request": f"projects/{media.project.id}/render-attempts/attempt/request.json",
        "video-guide": f"{media.root}/route-guide.png",
        "video-checkpoint": f"{media.root}/controls/geometry-00-depth.png",
    }
    path = paths[private_path]
    storage = MagicMock()
    monkeypatch.setattr(files, "_s3_client", storage)
    with pytest.raises(HTTPException) as exc:
        if operation == "ticket":
            await files.issue_file_read_ticket(files.FileReadTicketRequest(file_path=path), Response(), test_user, mock_db)
        else:
            await getattr(files, operation + "_file")(path, user=test_user, db=mock_db)
    assert exc.value.status_code == 403
    storage.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("ticket_owner", ["requester", "owner"])
async def test_project_ticket_preserves_video_requester_identity(media, mock_db, test_user, ticket_owner):
    uid = media.requester if ticket_owner == "requester" else test_user.id
    ticket = create_project_asset_ticket(media.project.id, uid)
    path = f"{media.root}/controls/route-preview.webm"
    if ticket_owner == "requester":
        assert await files._authorize_file(path, None, mock_db, None, ticket) is False
    else:
        with pytest.raises(HTTPException) as exc:
            await files._authorize_file(path, None, mock_db, None, ticket)
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_saved_video_survives_interrupted_completion_and_is_shared(media, mock_db, test_user):
    assert await files._authorize_file(f"{media.root}/final.mp4", test_user, mock_db, None, None) is False
    requester = SimpleNamespace(id=media.requester)
    assert await files._authorize_file(f"{media.root}/route-guide.png", requester, mock_db, None, None) is False
    with pytest.raises(HTTPException):
        await files._authorize_file(f"{media.root}/route-guide.png", requester, mock_db, "public", None)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["get", "head"])
async def test_old_exact_file_ticket_cannot_bypass_new_private_policy(media, mock_db, test_user, monkeypatch, operation):
    path = f"{media.root}/route-guide.png"
    ticket = create_file_asset_ticket(path, test_user.id)
    monkeypatch.setattr(files, "_file_ticket_user", AsyncMock(return_value=test_user))
    storage = MagicMock()
    monkeypatch.setattr(files, "_s3_client", storage)
    with pytest.raises(HTTPException) as exc:
        await getattr(files, operation + "_file")(path, user=None, db=mock_db, file_ticket=ticket)
    assert exc.value.status_code == 403
    storage.assert_not_called()
