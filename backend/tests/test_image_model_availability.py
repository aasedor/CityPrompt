import asyncio

import httpx
import pytest

from app.api.v1 import render
from app.services import image_model_availability as availability
from app.services.direct_3d_render import estimate_direct_3d_token_cost


@pytest.fixture(autouse=True)
def clear_cache(monkeypatch):
    monkeypatch.setattr(availability, "_cache", None)
    monkeypatch.setattr(availability, "_lock", asyncio.Lock())


def mock_models(monkeypatch, ids, status=200):
    calls = []

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            calls.append(url)
            return httpx.Response(
                status, json={"data": [{"id": model} for model in ids]}, request=httpx.Request("GET", url)
            )

    monkeypatch.setattr(availability.httpx, "AsyncClient", Client)
    return calls


@pytest.mark.asyncio
async def test_rollout_account_keeps_working_legacy_model(monkeypatch):
    calls = mock_models(monkeypatch, ["gpt-image-2"])
    result = await availability.get_image_model_availability("test")
    assert result["default_model"] == "gpt-image-2"
    assert {entry["id"] for entry in result["models"] if entry["available"]} == {"gpt-image-2"}
    assert await availability.get_image_model_availability("test") == result
    assert len(calls) == 1
    # Cache identity changes with the credential, without storing the key.
    await availability.get_image_model_availability("another-test")
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_new_model_account_prefers_flare(monkeypatch):
    mock_models(monkeypatch, ["gpt-image-2", "gpt-image-2.5-flare", "gpt-image-2.5-sunburst"])
    result = await availability.get_image_model_availability("test")
    assert result["default_model"] == "gpt-image-2.5-flare"
    assert all(entry["available"] for entry in result["models"] if entry["id"].startswith("gpt-image-2.5"))


@pytest.mark.asyncio
async def test_listing_failure_does_not_claim_generation_is_unavailable(monkeypatch):
    mock_models(monkeypatch, [], status=403)
    result = await availability.get_image_model_availability("test")
    assert result["default_model"] == "gpt-image-2"
    assert all(entry["available"] is None for entry in result["models"])


@pytest.mark.parametrize(
    "model,multiplier", [("gpt-image-2", 1), ("gpt-image-2.5-flare", 2), ("gpt-image-2.5-sunburst", 2)]
)
def test_selected_engine_has_explicit_routing_and_credit_reservation(model, multiplier):
    assert model in render._ALLOWED_MODELS
    assert render._is_openai_model(model)
    assert render._MODEL_TOKEN_COST[model] == 13 * multiplier
    assert estimate_direct_3d_token_cost(1024, 1024, object_id_attached=True, model=model) == 51 * multiplier
