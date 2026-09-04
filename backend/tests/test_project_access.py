"""Cross-account and public-link regressions, with all external systems stubbed."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.api.v1 import annotations, buildings, files, shares
from app.core.security import (
    check_project_asset_access,
    check_project_permission,
    check_project_read_access,
    create_project_asset_ticket,
    decode_token,
)
from app.schemas.schemas import ProjectResponse
from tests.conftest import FakeProject


def result(value):
    response = MagicMock()
    response.scalar_one_or_none.return_value = value
    return response


@pytest.mark.anyio
@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/buildings/projects/{id}/buildings",
        "/api/v1/site-zones/projects/{id}/zones",
        "/api/v1/activity/projects/{id}/activity",
        "/api/v1/annotations/projects/{id}/annotations",
        "/api/v1/reports/projects/{id}/report",
        "/api/v1/model-library/archetype-previews",
    ],
)
async def test_project_lists_reject_anonymous_requests(client, path):
    response = await client.get(path.format(id=uuid.uuid4()))
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_email_alone_does_not_claim_pending_membership(mock_db, test_user):
    project = FakeProject()
    mock_db.execute.side_effect = [result(project), result(None)]
    with pytest.raises(HTTPException) as exc:
        await check_project_permission(project.id, test_user, mock_db)
    assert exc.value.status_code == 403
    query = mock_db.execute.call_args.args[0]
    assert "project_shares.email" not in str(query.whereclause)
    assert "project_shares.user_id" in str(query.whereclause)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "permission,required,allowed",
    [
        ("viewer", "viewer", True),
        ("viewer", "editor", False),
        ("editor", "viewer", True),
        ("editor", "editor", True),
    ],
)
async def test_accepted_member_permission_matrix(mock_db, test_user, permission, required, allowed):
    project = FakeProject()
    mock_db.execute.side_effect = [
        result(project),
        result(SimpleNamespace(permission=permission)),
    ]
    if allowed:
        assert await check_project_permission(project.id, test_user, mock_db, required) == permission
    else:
        with pytest.raises(HTTPException) as exc:
            await check_project_permission(project.id, test_user, mock_db, required)
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_public_read_requires_matching_project_and_public_token(mock_db):
    project_id = uuid.uuid4()
    mock_db.execute.return_value = result(None)
    with pytest.raises(HTTPException) as exc:
        await check_project_read_access(project_id, None, mock_db, "wrong-or-revoked")
    assert exc.value.status_code == 403
    query = mock_db.execute.call_args.args[0]
    assert project_id in query.compile().params.values()
    assert "project_shares.is_public_link IS true" in str(query)


@pytest.mark.asyncio
async def test_unrelated_user_cannot_cancel_generation(mock_db, test_user, monkeypatch):
    project = FakeProject()
    building = SimpleNamespace(project_id=project.id, generation_status="generating", specifications={})
    mock_db.execute.side_effect = [result(building), result(project), result(None)]
    revoke = MagicMock()
    monkeypatch.setattr(buildings.celery_app.control, "revoke", revoke)
    with pytest.raises(HTTPException) as exc:
        await buildings.cancel_generation(uuid.uuid4(), user=test_user, db=mock_db)
    assert exc.value.status_code == 403
    assert building.generation_status == "generating"
    revoke.assert_not_called()
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_batch_authorizes_every_project_before_revoking(mock_db, test_user, monkeypatch):
    first_project = FakeProject(owner_id=test_user.id)
    second_project = FakeProject()
    first = SimpleNamespace(
        project_id=first_project.id,
        generation_status="generating",
        specifications={"celery_task_id": "one"},
    )
    second = SimpleNamespace(
        project_id=second_project.id,
        generation_status="generating",
        specifications={"celery_task_id": "two"},
    )
    mock_db.execute.side_effect = [
        result(first),
        result(first_project),
        result(second),
        result(second_project),
        result(None),
    ]
    revoke = MagicMock()
    monkeypatch.setattr(buildings.celery_app.control, "revoke", revoke)
    with pytest.raises(HTTPException):
        await buildings.batch_cancel_generation(
            {"building_ids": [str(uuid.uuid4()), str(uuid.uuid4())]}, test_user, mock_db
        )
    revoke.assert_not_called()
    assert first.generation_status == "generating"


@pytest.mark.asyncio
async def test_unrelated_user_cannot_delete_annotation(mock_db, test_user):
    project = FakeProject()
    annotation = SimpleNamespace(project_id=project.id)
    mock_db.execute.side_effect = [result(annotation), result(project), result(None)]
    with pytest.raises(HTTPException) as exc:
        await annotations.delete_annotation(uuid.uuid4(), test_user, mock_db)
    assert exc.value.status_code == 403
    mock_db.delete.assert_not_called()


@pytest.mark.asyncio
async def test_invitation_requires_token_and_intended_account(mock_db, test_user):
    share = SimpleNamespace(email="somebody-else@example.com", user_id=None)
    mock_db.execute.return_value = result(share)
    with pytest.raises(HTTPException) as exc:
        await shares.accept_invitation("secret", test_user, mock_db)
    assert exc.value.status_code == 403
    assert share.user_id is None
    share.email = test_user.email
    assert await shares.accept_invitation("secret", test_user, mock_db) is share
    assert share.user_id == test_user.id
    assert "FOR UPDATE" in str(mock_db.execute.call_args.args[0])


@pytest.mark.asyncio
async def test_redeemed_invitation_cannot_bind_second_account(mock_db, test_user):
    share = SimpleNamespace(email=test_user.email, user_id=uuid.uuid4())
    mock_db.execute.return_value = result(share)
    with pytest.raises(HTTPException) as exc:
        await shares.accept_invitation("secret", test_user, mock_db)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
@pytest.mark.parametrize("public_link", [True, False])
async def test_delete_public_link_and_uuid_invitation_match_their_actual_routes(
    client, mock_db, test_user, auth_headers, public_link
):
    project = FakeProject(owner_id=test_user.id)
    share = SimpleNamespace(id=uuid.uuid4(), project_id=project.id, is_public_link=public_link)
    mock_db.execute.side_effect = [result(test_user), result(project), result(share)]
    suffix = "public-link" if public_link else str(share.id)
    response = await client.delete(f"/api/v1/shares/projects/{project.id}/shares/{suffix}", headers=auth_headers)
    assert response.status_code == 204
    mock_db.delete.assert_awaited_once_with(share)
    statement = str(mock_db.execute.call_args_list[-1].args[0])
    if public_link:
        assert "project_shares.is_public_link IS true" in statement
    else:
        assert "project_shares.id =" in statement


@pytest.mark.asyncio
async def test_public_project_serializes_postgis_and_omits_documents(mock_db):
    project = FakeProject()
    project.location = from_shape(Point(-114, 51), srid=4326)
    project.metadata_ = {}
    project.documents = [SimpleNamespace(filename="private-source.pdf")]
    mock_db.execute.side_effect = [
        result(SimpleNamespace(project_id=project.id)),
        result(project),
    ]
    payload = await shares.get_shared_project("public-token", mock_db)
    response = ProjectResponse.model_validate(payload)
    assert response.location.latitude == 51
    assert response.location.longitude == -114
    assert response.documents == []
    assert "project_shares.is_public_link IS true" in str(mock_db.execute.call_args_list[0].args[0])


@pytest.mark.asyncio
async def test_asset_ticket_is_read_only_and_rechecks_revocation(mock_db, test_user):
    project = FakeProject()
    token = create_project_asset_ticket(project.id, test_user.id)
    assert decode_token(token)["type"] == "project_asset"
    mock_db.execute.side_effect = [result(test_user), result(project), result(None)]
    with pytest.raises(HTTPException) as exc:
        await check_project_asset_access(project.id, None, mock_db, asset_ticket=token)
    assert exc.value.status_code == 403
    mock_db.execute.reset_mock()
    with pytest.raises(HTTPException) as exc:
        await check_project_asset_access(uuid.uuid4(), None, mock_db, asset_ticket=token)
    assert exc.value.status_code == 403
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_public_video_ticket_cannot_fetch_capture_inputs(mock_db, monkeypatch):
    pid = uuid.uuid4()
    monkeypatch.setattr(files, "check_project_asset_access", AsyncMock())
    mock_db.get.return_value = SimpleNamespace(
        metadata_={
            "video_pilot_attempts": [
                {
                    "status": "complete",
                    "video_url": f"/api/v1/files/projects/{pid}/video-render/attempt/final.mp4",
                }
            ]
        }
    )
    with pytest.raises(HTTPException) as exc:
        await files._authorize_file(
            f"projects/{pid}/video-render/attempt/route-guide.png",
            None,
            mock_db,
            "public",
            None,
        )
    assert exc.value.status_code == 403
    assert (
        await files._authorize_file(
            f"projects/{pid}/video-render/attempt/final.mp4",
            None,
            mock_db,
            "public",
            None,
        )
        is False
    )


@pytest.mark.asyncio
async def test_project_download_denied_before_object_storage(mock_db, monkeypatch):
    s3 = MagicMock()
    monkeypatch.setattr(files, "_s3_client", s3)
    with pytest.raises(HTTPException) as exc:
        await files.get_file(f"projects/{uuid.uuid4()}/renders/image.png", user=None, db=mock_db)
    assert exc.value.status_code == 401
    s3.assert_not_called()
