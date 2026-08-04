"""Meshy client pure-logic tests — prompt capping and 4xx classification.

These guard the fix for the 2026-07-08 outage: every "real" building failed
because compose_zone_prompt output (~2,300 chars) exceeded Meshy's 800-char
prompt limit, and the failures were being retried instead of failing fast.
"""

import httpx
import pytest

from app.generation.meshy_client import (
    MESHY_PROMPT_MAX,
    MESHY_TEXTURE_PROMPT_MAX,
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
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"status": "SUCCEEDED"}))

    result = await client.get_image_task("task-9")

    assert result["status"] == "SUCCEEDED"
    assert recorded[0].url.path == "/openapi/v1/image-to-3d/task-9"


# --- multi-image-to-3D --------------------------------------------------------
# Multi-image also lives under /openapi/v1/ only. should_remesh MUST be sent:
# meshy-6 defaults it off and then ignores target_polycount — an un-remeshed
# multi-image run came back at 1.17M tris / 68MB (verified 2026-07-11).


async def test_multi_image_posts_v1_endpoint_with_remesh(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "task-m1"}))

    urls = [
        "data:image/png;base64,street",
        "data:image/jpeg;base64,oblique60",
        "data:image/jpeg;base64,nadir90",
    ]
    task_id = await client.multi_image_to_3d(urls, texture_prompt="brick and glass")

    assert task_id == "task-m1"
    assert recorded[0].url.path == "/openapi/v1/multi-image-to-3d"
    import json

    payload = json.loads(recorded[0].content)
    assert payload["image_urls"] == urls  # order preserved: street card is primary
    assert payload["ai_model"] == "meshy-6"
    assert payload["should_remesh"] is True
    assert payload["target_polycount"] == 30000
    assert payload["topology"] == "triangle"
    assert payload["enable_pbr"] is True
    assert payload["target_formats"] == ["glb"]
    assert payload["multi_view_thumbnails"] is True
    assert payload["texture_prompt"] == "brick and glass"


async def test_multi_image_texture_prompt_capped_at_600(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "task-m2"}))

    await client.multi_image_to_3d(["data:image/png;base64,a"], texture_prompt="word " * 400)

    import json

    payload = json.loads(recorded[0].content)
    assert len(payload["texture_prompt"]) <= MESHY_TEXTURE_PROMPT_MAX


async def test_multi_image_rejects_bad_image_count(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "task-m3"}))

    with pytest.raises(MeshyClientError):
        await client.multi_image_to_3d([])
    with pytest.raises(MeshyClientError):
        await client.multi_image_to_3d(["u1", "u2", "u3", "u4", "u5"])
    assert recorded == []  # rejected before any request went out


async def test_multi_image_omits_polycount_without_remesh(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "task-m4"}))

    await client.multi_image_to_3d(["u1"], should_remesh=False)

    import json

    payload = json.loads(recorded[0].content)
    assert "target_polycount" not in payload
    assert payload["should_remesh"] is False


async def test_get_multi_image_task_and_poll_dispatch(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"status": "SUCCEEDED"}))

    result = await client.get_multi_image_task("task-9")
    assert result["status"] == "SUCCEEDED"
    assert recorded[0].url.path == "/openapi/v1/multi-image-to-3d/task-9"

    # poll_until_done must route the new task_type to the multi-image endpoint
    # (the old binary dispatch would have silently polled image-to-3d).
    result = await client.poll_until_done("task-9", timeout=5, task_type="multi_image")
    assert result["status"] == "SUCCEEDED"
    assert recorded[1].url.path == "/openapi/v1/multi-image-to-3d/task-9"


async def test_poll_until_done_rejects_unknown_task_type():
    client = MeshyClient(api_key="test-key")
    with pytest.raises(ValueError):
        await client.poll_until_done("task-x", timeout=5, task_type="video")


# --- two-stage chain: Image-to-Image multi-view -> multi-image-to-3d ---------
# Stage 1 synthesizes mutually-consistent, auto-isolated views; stage 2 feeds
# them in via input_task_id. Root-cause fix for warped windows (2026-07-12).


async def test_image_to_image_multiview_posts_v1_with_multi_view_flag(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "i2i-1"}))

    task_id = await client.image_to_image_multiview(["data:image/png;base64,card"], "flush facade tower")

    assert task_id == "i2i-1"
    assert recorded[0].url.path == "/openapi/v1/image-to-image"
    import json

    payload = json.loads(recorded[0].content)
    assert payload["generate_multi_view"] is True
    assert payload["reference_image_urls"] == ["data:image/png;base64,card"]
    assert payload["ai_model"] == "nano-banana-pro"
    assert payload["prompt"] == "flush facade tower"


async def test_image_to_image_multiview_rejects_bad_ref_count(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "x"}))

    with pytest.raises(MeshyClientError):
        await client.image_to_image_multiview([], "p")
    with pytest.raises(MeshyClientError):
        await client.image_to_image_multiview(["a", "b", "c", "d", "e", "f"], "p")
    assert recorded == []


async def test_multi_image_to_3d_chains_input_task_id(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"result": "mi3d-1"}))

    task_id = await client.multi_image_to_3d(input_task_id="i2i-1", texture_prompt="brick", target_polycount=30000)

    assert task_id == "mi3d-1"
    import json

    payload = json.loads(recorded[0].content)
    # input_task_id chains the synthesized views; image_urls must be absent.
    assert payload["input_task_id"] == "i2i-1"
    assert "image_urls" not in payload
    assert payload["should_remesh"] is True
    assert payload["target_polycount"] == 30000


async def test_get_image_to_image_task_and_poll_dispatch(monkeypatch):
    recorded: list[httpx.Request] = []
    client = MeshyClient(api_key="test-key")
    monkeypatch.setattr(client, "_client", lambda: _mock_client(recorded, {"status": "SUCCEEDED"}))

    result = await client.get_image_to_image_task("i2i-9")
    assert result["status"] == "SUCCEEDED"
    assert recorded[0].url.path == "/openapi/v1/image-to-image/i2i-9"

    await client.poll_until_done("i2i-9", timeout=5, task_type="image_to_image")
    assert recorded[1].url.path == "/openapi/v1/image-to-image/i2i-9"
