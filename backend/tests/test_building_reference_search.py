import hashlib
import io
import json
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import HTTPException
from PIL import Image

from app.api.v1 import buildings as api
from app.services import building_reference_search as search
from app.services.photo_building import photo_state


def page(**overrides):
    info = {
        "mime": "image/jpeg",
        "width": 1000,
        "height": 700,
        "sha1": "a" * 40,
        "thumburl": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Hall.jpg",
        "descriptionurl": "https://commons.wikimedia.org/wiki/File:Hall.jpg",
        "extmetadata": {
            "LicenseShortName": {"value": "CC BY-SA 4.0"},
            "Artist": {"value": '<a href="x">Photographer &amp; Co.</a>'},
        },
        **overrides,
    }
    return {"pageid": 1, "title": "File:Hall.jpg", "imageinfo": [info]}


def photo():
    out = io.BytesIO()
    Image.new("RGB", (100, 100), "white").save(out, "JPEG")
    data = out.getvalue()
    return data, hashlib.sha256(data).hexdigest()


def test_candidates_require_image_license_and_trusted_host():
    candidate = search.commons_candidate(page())
    assert candidate["author"] == "Photographer & Co."
    assert candidate["id"] == search.commons_candidate(page())["id"]
    assert search.commons_candidate(page(thumburl="https://thumb.wikimedia.org/wikipedia/commons/thumb/a/Hall.jpg"))
    for override in (
        {"mime": "image/svg+xml"},
        {"extmetadata": {}},
        {"thumburl": "http://127.0.0.1/private"},
        {"thumburl": "https://upload.wikimedia.org.evil.test/a.jpg"},
        {"thumburl": "https://evil@upload.wikimedia.org/wikipedia/commons/a.jpg"},
        {"descriptionurl": "javascript:alert(1)"},
        {"width": 10},
    ):
        assert search.commons_candidate(page(**override)) is None


def test_signed_candidates_reject_changed_metadata_and_other_buildings():
    candidate = search.sign_candidate(search.commons_candidate(page()), "building-a")
    assert search.verified_candidate(candidate, "building-a")
    assert not search.verified_candidate(candidate, "building-b")
    assert not search.verified_candidate(
        {**candidate, "image_url": "https://upload.wikimedia.org/another.jpg"}, "building-a"
    )


@pytest.mark.anyio
async def test_search_deduplicates_and_preserves_attribution(monkeypatch):
    client = AsyncMock()
    response = httpx.Response(
        200,
        json={"query": {"pages": {"1": page(), "2": {**page(), "pageid": 2}}}},
        request=httpx.Request("GET", search.COMMONS_API),
    )
    client.get.return_value = response
    manager = AsyncMock()
    manager.__aenter__.return_value = client
    monkeypatch.setattr(search.httpx, "AsyncClient", lambda **kwargs: manager)
    result = await search.search_building_views("Famous Hall", "aerial")
    assert len(result) == 1
    assert result[0]["source_url"].endswith("File:Hall.jpg")
    assert '"Famous Hall" aerial' in client.get.call_args.kwargs["params"]["gsrsearch"]


@pytest.mark.anyio
async def test_download_rejects_arbitrary_hosts_and_redirects(monkeypatch):
    with pytest.raises(ValueError, match="not supported"):
        await search.download_building_view({"image_url": "https://127.0.0.1/private"})

    def handler(request):
        return httpx.Response(302, headers={"location": "http://localhost/private"})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        search.httpx, "AsyncClient", lambda **kw: real_client(transport=httpx.MockTransport(handler), **kw)
    )
    with pytest.raises(httpx.HTTPStatusError):
        await search.download_building_view(search.commons_candidate(page()))


@pytest.mark.anyio
async def test_search_retains_selected_candidates_across_view_queries(monkeypatch):
    building = SimpleNamespace(
        specifications={"other": "preserved", "photo_reference_search": {"candidates": [{"id": "old"}]}}
    )
    db = AsyncMock()
    monkeypatch.setattr(api, "_editable_building", AsyncMock(return_value=building))
    monkeypatch.setattr(api, "search_building_views", AsyncMock(return_value=[{"id": "new"}]))
    result = await api.find_photo_references(uuid.uuid4(), "Concert Hall", "all", None, db)
    assert [item["id"] for item in result["candidates"]] == ["new"]
    assert building.specifications["other"] == "preserved"
    assert [item["id"] for item in building.specifications["photo_reference_search"]["candidates"]] == ["new", "old"]


@pytest.mark.anyio
async def test_web_sources_import_before_charge_and_preserve_provenance(monkeypatch):
    from app.tasks import processing

    building_id = uuid.uuid4()
    candidate = search.sign_candidate(search.commons_candidate(page()), str(building_id))
    building = SimpleNamespace(
        id=building_id,
        project_id=uuid.uuid4(),
        generation_status="idle",
        specifications={"photo_reference_search": {"candidates": [candidate]}},
    )
    db = AsyncMock()
    monkeypatch.setattr(api, "_editable_building", AsyncMock(return_value=building))
    monkeypatch.setattr(api, "_check_engine_available", lambda _: None)
    charge = AsyncMock(return_value=uuid.uuid4())
    monkeypatch.setattr(api, "reserve_photo_tokens", charge)
    download = AsyncMock(return_value=photo())
    monkeypatch.setattr(api, "download_building_view", download)
    monkeypatch.setattr(processing, "_upload_to_storage", MagicMock())
    monkeypatch.setattr(processing.synthesize_building_photo_references, "apply_async", MagicMock())
    for ids in (["https://evil/image.jpg"], [candidate["id"]] * 2, ["a", "b", "c", "d", "e"]):
        with pytest.raises(HTTPException):
            await api.create_photo_references(building.id, [], "Hall", None, db, json.dumps(ids))
    download.assert_not_awaited()
    charge.assert_not_awaited()
    download.side_effect = ValueError("unavailable")
    with pytest.raises(HTTPException, match="no tokens were charged"):
        await api.create_photo_references(building.id, [], "Hall", None, db, json.dumps([candidate["id"]]))
    charge.assert_not_awaited()
    download.side_effect = None
    result = await api.create_photo_references(building.id, [], "Hall", None, db, json.dumps([candidate["id"]]))
    assert result["status"] == "synthesizing"
    state = photo_state(building.specifications)
    assert state["source_hashes"] == [photo()[1]]
    assert state["source_provenance"][0]["license"] == "CC BY-SA 4.0"
    assert state["source_provenance"][0]["sha256"] == photo()[1]
    charge.assert_awaited_once()
