import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest
from fastapi import HTTPException

from app.api.v1.site_zones import get_road_network


@pytest.mark.asyncio
async def test_network_endpoint_reads_sources_without_writing():
    db = AsyncMock()
    rows = MagicMock()
    rows.scalars.return_value.all.return_value = [
        SimpleNamespace(
            id=uuid.uuid4(),
            properties={
                "procedural_road": 1,
                "plan_centerline": [[-114, 51], [-113.999, 51]],
                "width": 10,
            },
        )
    ]
    db.execute.return_value = rows
    project_id, user = uuid.uuid4(), SimpleNamespace()
    with patch("app.api.v1.site_zones._ensure_project_access", new_callable=AsyncMock) as access:
        result = await get_road_network(project_id, user, db)
    access.assert_awaited_once_with(db, project_id, user)
    assert len(result["edges"]) == 1
    assert result["features"]["type"] == "FeatureCollection"
    json.dumps(result, allow_nan=False)
    db.flush.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_network_requires_project_access():
    with patch(
        "app.api.v1.site_zones._ensure_project_access",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=403),
    ):
        db = AsyncMock()
        with pytest.raises(HTTPException) as error:
            await get_road_network(uuid.uuid4(), SimpleNamespace(), db)
        assert error.value.status_code == 403
        db.execute.assert_not_awaited()
