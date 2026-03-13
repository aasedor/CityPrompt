import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.master_plan_2d import MasterPlan2DService
from tests.conftest import FakeProject


def _scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def _scalars_result(values):
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = values
    result.scalars.return_value = scalars
    return result


@pytest.mark.anyio
async def test_generate_to_3d_returns_422_on_unexpected_service_failure(client, mock_db, test_user, auth_headers, monkeypatch):
    project_id = uuid.uuid4()
    option_id = uuid.uuid4()

    option = SimpleNamespace(id=option_id, project_id=project_id)
    project = FakeProject(id=project_id, owner_id=test_user.id)

    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # require_auth user lookup
            _scalar_result(option),     # option lookup
            _scalar_result(project),    # project lookup
            _scalars_result([]),        # zones lookup
            _scalars_result([]),        # buildings lookup
        ]
    )

    monkeypatch.setattr(
        MasterPlan2DService,
        'generate_3d_render_packages',
        AsyncMock(side_effect=RuntimeError('simulated transform failure')),
    )

    response = await client.post(
        f'/api/v1/master-plan-2d/options/{option_id}/generate-3d',
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 422
    assert 'Failed to prepare 3D render packages' in response.json()['detail']


@pytest.mark.anyio
async def test_generate_to_3d_returns_400_for_service_validation_errors(client, mock_db, test_user, auth_headers, monkeypatch):
    project_id = uuid.uuid4()
    option_id = uuid.uuid4()

    option = SimpleNamespace(id=option_id, project_id=project_id)
    project = FakeProject(id=project_id, owner_id=test_user.id)

    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # require_auth user lookup
            _scalar_result(option),     # option lookup
            _scalar_result(project),    # project lookup
            _scalars_result([]),        # zones lookup
            _scalars_result([]),        # buildings lookup
        ]
    )

    monkeypatch.setattr(
        MasterPlan2DService,
        'generate_3d_render_packages',
        AsyncMock(side_effect=ValueError('No eligible zones with valid geometry were available to generate 3D render packages.')),
    )

    response = await client.post(
        f'/api/v1/master-plan-2d/options/{option_id}/generate-3d',
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 400
    assert 'No eligible zones with valid geometry were available' in response.json()['detail']


@pytest.mark.anyio
async def test_generate_to_3d_rejects_selected_scope_without_zone_ids(client, mock_db, test_user, auth_headers):
    mock_db.execute = AsyncMock(return_value=_scalar_result(test_user))
    response = await client.post(
        f'/api/v1/master-plan-2d/options/{uuid.uuid4()}/generate-3d',
        headers=auth_headers,
        json={
            'scope': 'selected_zones',
            'selected_zone_ids': [],
        },
    )

    assert response.status_code == 422
    assert 'selected_zone_ids must include at least one zone' in str(response.json())

