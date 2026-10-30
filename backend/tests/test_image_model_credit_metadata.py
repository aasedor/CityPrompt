"""Model discovery exposes read-only affordability floors, never exact quotes."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.image_models import PAID_IMAGE_CREDIT_MULTIPLIERS
from app.services import image_model_availability
from app.services.direct_3d_render import (
    _MIN_PROVIDER_PIXELS,
    _normalized_dimensions,
    estimate_direct_3d_token_cost,
)


@pytest.fixture
def discovery(monkeypatch):
    result = {
        "default_model": "gpt-image-2",
        "models": [{"id": model, "available": True} for model in PAID_IMAGE_CREDIT_MULTIPLIERS],
    }
    fetch = AsyncMock(return_value=result)
    monkeypatch.setattr(image_model_availability, "get_image_model_availability", fetch)
    return fetch, result


@pytest.mark.asyncio
async def test_discovery_requires_authentication(client, discovery):
    response = await client.get("/api/v1/render/image-models")
    assert response.status_code == 401
    discovery[0].assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role,age,expected,exempt",
    [
        ("editor", 1, 0, False),
        ("editor", 6, 0, False),
        ("editor", 7, 1000, False),
        ("editor", None, 1000, False),
        ("admin", 1, 0, True),
        ("cofounder", 1, 0, True),
    ],
)
async def test_authenticated_discovery_reports_effective_balance_without_mutation(
    client,
    mock_db,
    test_user,
    auth_headers,
    discovery,
    role,
    age,
    expected,
    exempt,
):
    test_user.role, test_user.render_credits = role, 0
    reset = None if age is None else datetime.now(timezone.utc) - timedelta(days=age)
    test_user.credits_reset_at = reset
    result = MagicMock()
    result.scalar_one_or_none.return_value = test_user
    mock_db.execute.return_value = result
    response = await client.get("/api/v1/render/image-models", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["credit_balance"] == expected and data["credit_exempt"] is exempt
    # 1024 x 640 is an actually supported, exactly minimum-area capture.
    width, height = _normalized_dimensions(1024, 640)
    assert width * height == _MIN_PROVIDER_PIXELS
    for model in data["models"]:
        assert model["minimum_credit_cost"] == estimate_direct_3d_token_cost(
            width, height, object_id_attached=False, model=model["id"]
        )
    assert test_user.render_credits == 0 and test_user.credits_reset_at == reset
    mock_db.commit.assert_not_awaited()
    mock_db.add.assert_not_called()
    assert "credit_balance" not in discovery[1]  # Never mutate provider discovery's shared cache.
    assert all("minimum_credit_cost" not in item for item in discovery[1]["models"])
