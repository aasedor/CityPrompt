"""Meshy client pure-logic tests — prompt capping and 4xx classification.

These guard the fix for the 2026-07-08 outage: every "real" building failed
because compose_zone_prompt output (~2,300 chars) exceeded Meshy's 800-char
prompt limit, and the failures were being retried instead of failing fast.
"""

import httpx
import pytest

from app.generation.meshy_client import (
    MESHY_PROMPT_MAX,
    MeshyClient,
    MeshyClientError,
    _cap_prompt,
)


def test_cap_prompt_leaves_short_text_untouched():
    text = "A modern 6-storey mixed-use residential building."
    assert _cap_prompt(text) == text


def test_cap_prompt_trims_over_limit_to_word_boundary():
    text = "word " * 400  # 2000 chars
    capped = _cap_prompt(text)
    assert len(capped) <= MESHY_PROMPT_MAX
    assert not capped.endswith("wor")  # cut at a space, not mid-word


def test_cap_prompt_handles_empty():
    assert _cap_prompt("") == ""
    assert _cap_prompt(None) == ""


def test_cap_prompt_hard_cut_when_no_space():
    text = "x" * 2000  # no spaces
    assert len(_cap_prompt(text)) == MESHY_PROMPT_MAX


def _resp(status: int, body: str = "err") -> httpx.Response:
    return httpx.Response(status_code=status, text=body, request=httpx.Request("POST", "http://x"))


def test_check_raises_permanent_error_on_400():
    with pytest.raises(MeshyClientError):
        MeshyClient._check(_resp(400, '{"message":"Prompt must be a maximum of 800 characters"}'), "preview")


def test_check_retryable_on_429_and_5xx():
    # 429 rate-limit and 5xx are transient — plain RuntimeError, NOT MeshyClientError.
    for status in (429, 500, 503):
        with pytest.raises(RuntimeError) as exc:
            MeshyClient._check(_resp(status), "preview")
        assert not isinstance(exc.value, MeshyClientError)


def test_check_passes_on_2xx():
    MeshyClient._check(_resp(200), "preview")
    MeshyClient._check(_resp(202), "preview")


# --- image-to-3D endpoint version -------------------------------------------
# Meshy's image-to-3D API exists only under /openapi/v1/ — the v2 path 404s
# (verified live 2026-07-10). These pin the paths so a "helpful" v2 upgrade
# can't silently break image mode again.


def _mock_client(recorded: list[httpx.Request], response_json: dict) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        recorded.append(request)
        return httpx.Response(200, json=response_json)

    return httpx.AsyncClient(
        base_url="https://api.meshy.ai",
        transport=httpx.MockTransport(handler),
    )


async def test_image_to_3d_posts_v1_endpoint_with_pbr(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "task-123"}))

    task_id = await client.image_to_3d("data:image/png;base64,abc", target_polycount=30000)

    assert task_id == "task-123"
    assert recorded[0].url.path == "/openapi/v1/image-to-3d"
    import json

    payload = json.loads(recorded[0].content)
    assert payload["image_url"] == "data:image/png;base64,abc"
    assert payload["enable_pbr"] is True
    assert payload["target_polycount"] == 30000
    # meshy-6 defaults should_remesh to false and then IGNORES
    # target_polycount — the client must always send it explicitly.
    assert payload["should_remesh"] is True


async def test_image_to_3d_omits_polycount_when_disabled(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "task-1"}))

    await client.image_to_3d("https://example.com/card.png", target_polycount=None)

    import json

    payload = json.loads(recorded[0].content)
    assert "target_polycount" not in payload
    assert payload["should_remesh"] is True


async def test_text_preview_sends_polycount_cap(monkeypatch):
    # Without an explicit cap the raw text-to-3D mesh arrives at 1M+ tris
    # (41MB refine GLB observed 2026-07-11).
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "task-p"}))

    await client.text_to_3d_preview("a building")

    import json

    payload = json.loads(recorded[0].content)
    assert payload["target_polycount"] == 30000
    assert payload["topology"] == "triangle"


async def test_get_image_task_polls_v1_endpoint(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(
        client, "_client", lambda: _mock_client(recorded, {"status": "SUCCEEDED"})
    )

    result = await client.get_image_task("task-9")

    assert result["status"] == "SUCCEEDED"
    assert recorded[0].url.path == "/openapi/v1/image-to-3d/task-9"
