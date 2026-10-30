"""Read-only URL credentials must expire with their issuing user's session epoch."""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from fastapi import HTTPException, Response
from jose import jwt
import pytest

from app.api.v1 import files, shares
from app.core import security
from tests.conftest import FakeProject
from tests.test_file_read_tickets import FILE_PATH, library_result, scalar


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["project", "file"])
async def test_asset_ticket_issuer_binds_current_session_version(mock_db, test_user, kind):
    test_user.session_version = 7
    if kind == "project":
        project = FakeProject(owner_id=test_user.id)
        mock_db.execute.return_value = scalar(project)
        result = await shares.issue_asset_ticket(project.id, test_user, mock_db)
        token = result["asset_ticket"]
    else:
        mock_db.execute.return_value = library_result(test_user.id)
        result = await files.issue_file_read_ticket(
            files.FileReadTicketRequest(file_path=FILE_PATH),
            Response(),
            test_user,
            mock_db,
        )
        token = result["file_ticket"]
    assert security.decode_token(token)["ver"] == 7


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["project", "file"])
@pytest.mark.parametrize("version", [None, 6, 7, 8])
async def test_asset_ticket_requires_exact_current_session_epoch(mock_db, test_user, kind, version):
    test_user.session_version = 7
    project = FakeProject(owner_id=test_user.id)
    payload = {
        "type": "project_asset" if kind == "project" else "file_asset",
        "sub": str(test_user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "project_id": str(project.id),
        "file_path": FILE_PATH,
    }
    if version is not None:
        payload["ver"] = version
    token = jwt.encode(
        payload,
        security.settings.jwt_secret_key,
        algorithm=security.settings.jwt_algorithm,
    )
    mock_db.execute.side_effect = [scalar(test_user), scalar(project)]

    async def consume():
        if kind == "project":
            await security.check_project_asset_access(project.id, None, mock_db, asset_ticket=token)
        else:
            assert (await files._file_ticket_user(FILE_PATH, token, mock_db)).id == test_user.id

    if version == 7:
        await consume()
    else:
        with pytest.raises(HTTPException) as rejected:
            await consume()
        assert rejected.value.status_code == 401
        assert mock_db.execute.await_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", [files.get_file, files.head_file])
@pytest.mark.parametrize("kind", ["project", "file"])
async def test_password_epoch_change_stops_asset_download_before_storage(
    endpoint, kind, mock_db, test_user, monkeypatch
):
    project_id = uuid.uuid4()
    path = f"projects/{project_id}/models/private.glb" if kind == "project" else FILE_PATH
    test_user.session_version = 0
    token = (
        security.create_project_asset_ticket(project_id, test_user.id)
        if kind == "project"
        else security.create_file_asset_ticket(path, test_user.id)
    )
    security.revoke_user_sessions(test_user)
    # Without epoch validation, membership/ownership permits the old URL.
    mock_db.execute.side_effect = [
        scalar(test_user),
        (
            scalar(FakeProject(id=project_id, owner_id=test_user.id))
            if kind == "project"
            else library_result(test_user.id)
        ),
    ]
    storage = MagicMock()
    storage.get_object.return_value = {"Body": MagicMock(read=lambda: b"private")}
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    with pytest.raises(HTTPException) as rejected:
        await endpoint(
            path,
            user=None,
            db=mock_db,
            **({"asset_ticket": token} if kind == "project" else {"file_ticket": token}),
        )
    assert rejected.value.status_code == 401
    storage.get_object.assert_not_called()
    storage.head_object.assert_not_called()
