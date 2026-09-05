"""URL credentials are exact-object reads with live ownership checks."""

import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Response
from jose import jwt

from app.api.v1 import files
from app.core import security


FILE_PATH = "library/private-model/model.glb"


def scalar(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def library_result(owner_id):
    result = MagicMock()
    result.scalars.return_value.all.return_value = [
        SimpleNamespace(
            model_url=f"/api/v1/files/{FILE_PATH}",
            thumbnail_url=None,
            lod_urls={},
            is_public=False,
            owner_id=owner_id,
        )
    ]
    return result


@pytest.mark.asyncio
async def test_private_library_owner_gets_expiring_exact_file_ticket(mock_db, test_user):
    mock_db.execute.return_value = library_result(test_user.id)
    response = Response()
    result = await files.issue_file_read_ticket(
        files.FileReadTicketRequest(file_path=FILE_PATH), response, test_user, mock_db
    )
    payload = security.decode_token(result["file_ticket"])
    assert payload["type"] == "file_asset"
    assert payload["file_path"] == FILE_PATH
    assert payload["sub"] == str(test_user.id)
    assert 0 < payload["exp"] - datetime.now(timezone.utc).timestamp() <= 900
    assert result["expires_in"] == 900
    assert response.headers["cache-control"] == "private, no-store"
    with pytest.raises(HTTPException) as exc:
        await security.get_current_user(result["file_ticket"], mock_db)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_unrelated_account_cannot_issue_private_library_ticket(mock_db, test_user, monkeypatch):
    mock_db.execute.return_value = library_result(uuid.uuid4())
    mint = MagicMock()
    monkeypatch.setattr(files, "create_file_asset_ticket", mint)
    with pytest.raises(HTTPException) as exc:
        await files.issue_file_read_ticket(
            files.FileReadTicketRequest(file_path=FILE_PATH), Response(), test_user, mock_db
        )
    assert exc.value.status_code == 403
    mint.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", [files.get_file, files.head_file])
async def test_file_ticket_cannot_read_different_object(endpoint, mock_db, test_user, monkeypatch):
    token = security.create_file_asset_ticket(FILE_PATH, test_user.id)
    storage = MagicMock()
    monkeypatch.setattr(files, "_s3_client", storage)
    with pytest.raises(HTTPException) as exc:
        await endpoint("library/private-model/another.glb", user=None, db=mock_db, file_ticket=token)
    assert exc.value.status_code == 403
    mock_db.execute.assert_not_called()
    storage.assert_not_called()


@pytest.mark.asyncio
async def test_file_ticket_rechecks_revoked_ownership_before_storage(mock_db, test_user, monkeypatch):
    token = security.create_file_asset_ticket(FILE_PATH, test_user.id)
    mock_db.execute.side_effect = [scalar(test_user), library_result(uuid.uuid4())]
    storage = MagicMock()
    monkeypatch.setattr(files, "_s3_client", storage)
    with pytest.raises(HTTPException) as exc:
        await files.get_file(FILE_PATH, user=None, db=mock_db, file_ticket=token)
    assert exc.value.status_code == 403
    storage.assert_not_called()


@pytest.mark.asyncio
async def test_file_ticket_rejects_inactive_account(mock_db, test_user):
    token = security.create_file_asset_ticket(FILE_PATH, test_user.id)
    test_user.is_active = False
    mock_db.execute.return_value = scalar(test_user)
    with pytest.raises(HTTPException) as exc:
        await files._file_ticket_user(FILE_PATH, token, mock_db)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_file_ticket_expiry_and_login_token_are_rejected(mock_db, test_user):
    expired = jwt.encode(
        {
            "type": "file_asset",
            "sub": str(test_user.id),
            "file_path": FILE_PATH,
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        security.settings.jwt_secret_key,
        algorithm=security.settings.jwt_algorithm,
    )
    for token, expected_status in (
        (expired, 401),
        (security.create_access_token(str(test_user.id)), 403),
    ):
        with pytest.raises(HTTPException) as exc:
            await files._file_ticket_user(FILE_PATH, token, mock_db)
        assert exc.value.status_code == expected_status
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_authorized_file_ticket_reads_object_and_disables_caching(mock_db, test_user, monkeypatch):
    token = security.create_file_asset_ticket(FILE_PATH, test_user.id)
    mock_db.execute.side_effect = [scalar(test_user), library_result(test_user.id)]
    storage = MagicMock()
    storage.get_object.return_value = {"Body": SimpleNamespace(read=lambda: b"glTF")}
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    response = await files.get_file(FILE_PATH, user=None, db=mock_db, file_ticket=token)
    assert response.body == b"glTF"
    assert response.headers["cache-control"] == "private, no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    storage.get_object.assert_called_once_with(Bucket=files.settings.s3_bucket_name, Key=FILE_PATH)


@pytest.mark.asyncio
async def test_render_audit_ticket_rechecks_current_audit_owner(mock_db, test_user):
    path = f"render-audit/{uuid.uuid4()}/output.png"
    mock_db.execute.return_value = scalar(SimpleNamespace(user_id=test_user.id))
    result = await files.issue_file_read_ticket(
        files.FileReadTicketRequest(file_path=path), Response(), test_user, mock_db
    )
    assert security.decode_token(result["file_ticket"])["file_path"] == path
    mock_db.execute.return_value = scalar(SimpleNamespace(user_id=uuid.uuid4()))
    with pytest.raises(HTTPException) as exc:
        await files._authorize_file(path, test_user, mock_db, None, None)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", ["/library/model.glb", "library/../model.glb", "library//model.glb", "library/model.glb?x=y"]
)
async def test_ticket_issuance_requires_canonical_key(path, mock_db, test_user):
    with pytest.raises(HTTPException) as exc:
        await files.issue_file_read_ticket(files.FileReadTicketRequest(file_path=path), Response(), test_user, mock_db)
    assert exc.value.status_code == 400
    mock_db.execute.assert_not_called()
