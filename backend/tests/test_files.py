import pytest
from io import BytesIO
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.api.v1 import files
from tests.file_response_support import response_bytes


def test_safe_download_name_rejects_header_control_characters() -> None:
    assert files._safe_download_name("City Prompt\r\nunsafe: yes.mp4", "video/omni.mp4") == "City-Prompt-unsafe-yes.mp4"


@pytest.mark.asyncio
async def test_head_file_checks_metadata_without_downloading(monkeypatch, mock_db) -> None:
    calls: list[dict[str, str]] = []

    class FakeS3:
        def close(self):
            pass

        def head_object(self, **kwargs):
            calls.append(kwargs)
            return {"ContentLength": 42, "ContentType": "model/gltf-binary"}

    monkeypatch.setattr(files, "_s3_client", lambda: FakeS3())
    response = await files.head_file("archetype-cache/example.glb", user=None, db=mock_db)

    assert response.status_code == 200
    assert response.headers["content-length"] == "42"
    assert response.headers["content-type"] == "model/gltf-binary"
    assert calls == [
        {
            "Bucket": files.settings.s3_bucket_name,
            "Key": "archetype-cache/example.glb",
        }
    ]


@pytest.mark.asyncio
async def test_head_file_returns_404_for_stale_storage_key(monkeypatch, mock_db) -> None:
    class MissingS3:
        def close(self):
            pass

        def head_object(self, **_kwargs):
            raise KeyError("missing")

    monkeypatch.setattr(files, "_s3_client", lambda: MissingS3())

    with pytest.raises(HTTPException) as exc_info:
        await files.head_file("archetype-cache/missing.glb", user=None, db=mock_db)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_file_can_force_a_named_download(monkeypatch, mock_db) -> None:
    class FakeS3:
        def close(self):
            pass

        def get_object(self, **_kwargs):
            return {"Body": BytesIO(b"video"), "ContentType": "video/mp4", "ContentLength": 5}

    monkeypatch.setattr(files, "_s3_client", lambda: FakeS3())
    monkeypatch.setattr(files, "_authorize_file", AsyncMock(return_value=False))
    response = await files.get_file(
        "projects/example/video-render/attempt/omni.mp4",
        download=True,
        filename="city-prompt-golden-hour.mp4",
        user=None,
        db=mock_db,
    )

    assert await response_bytes(response) == b"video"
    assert response.headers["content-type"] == "video/mp4"
    assert response.headers["content-disposition"] == 'attachment; filename="city-prompt-golden-hour.mp4"'
