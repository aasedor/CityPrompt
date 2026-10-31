from io import BytesIO
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from PIL import Image

from app.api.v1 import files
from tests.file_response_support import response_bytes


def saved_image(monkeypatch, data=None):
    if data is None:
        out = BytesIO()
        Image.new("RGB", (1952, 704), "#587944").save(out, format="PNG")
        data = out.getvalue()
    storage = Mock()
    storage.get_object.side_effect = lambda **_: {"Body": BytesIO(data), "ContentType": "image/png"}
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    monkeypatch.setattr(files, "_authorize_file", AsyncMock(return_value=False))
    return storage, data


@pytest.mark.asyncio
async def test_small_preview_preserves_aspect_ratio_and_private_access(monkeypatch, mock_db):
    storage, original = saved_image(monkeypatch)
    response = await files.get_file("projects/p/renders/a.png", thumbnail=True, user=None, db=mock_db)
    assert response.media_type == "image/webp"
    assert response.headers["cache-control"] == "private, no-store"
    with Image.open(BytesIO(response.body)) as preview:
        assert preview.size == (384, 138)
    assert len(response.body) < len(original)
    storage.close.assert_called_once()
    storage.put_object.assert_not_called()
    full = await files.get_file("projects/p/renders/a.png", user=None, db=mock_db)
    assert await response_bytes(full) == original


@pytest.mark.asyncio
async def test_download_keeps_original_even_when_preview_parameter_is_present(monkeypatch, mock_db):
    _, original = saved_image(monkeypatch)
    response = await files.get_file("projects/p/renders/a.png", download=True, thumbnail=True, user=None, db=mock_db)
    assert await response_bytes(response) == original
    assert response.media_type == "image/png"


@pytest.mark.asyncio
async def test_thumbnail_cannot_bypass_project_access(monkeypatch, mock_db):
    storage, _ = saved_image(monkeypatch)
    monkeypatch.setattr(files, "_authorize_file", AsyncMock(side_effect=HTTPException(status_code=403)))
    with pytest.raises(HTTPException) as exc:
        await files.get_file("projects/p/renders/a.png", thumbnail=True, user=None, db=mock_db)
    assert exc.value.status_code == 403
    storage.get_object.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["projects/p/render-attempts/a/request.json", "archetype-cache/model.glb"])
async def test_preview_is_limited_to_saved_render_images(monkeypatch, mock_db, path):
    storage, _ = saved_image(monkeypatch)
    with pytest.raises(HTTPException) as exc:
        await files.get_file(path, thumbnail=True, user=None, db=mock_db)
    assert exc.value.status_code == 400
    storage.get_object.assert_not_called()


@pytest.mark.asyncio
async def test_corrupt_preview_fails_without_modifying_original(monkeypatch, mock_db):
    storage, data = saved_image(monkeypatch, b"not image data")
    with pytest.raises(HTTPException) as exc:
        await files.get_file("projects/p/renders/a.png", thumbnail=True, user=None, db=mock_db)
    assert exc.value.status_code == 422
    storage.close.assert_called_once()
    storage.put_object.assert_not_called()
    assert await response_bytes(await files.get_file("projects/p/renders/a.png", user=None, db=mock_db)) == data
