import pytest
from fastapi import HTTPException

from app.api.v1 import files


def test_safe_download_name_rejects_header_control_characters() -> None:
    assert files._safe_download_name("City Prompt\r\nunsafe: yes.mp4", "video/omni.mp4") == "City-Prompt-unsafe-yes.mp4"


@pytest.mark.asyncio
async def test_head_file_checks_metadata_without_downloading(monkeypatch) -> None:
    calls: list[dict[str, str]] = []

    class FakeS3:
        def head_object(self, **kwargs):
            calls.append(kwargs)
            return {"ContentLength": 42, "ContentType": "model/gltf-binary"}

    monkeypatch.setattr(files, "_s3_client", lambda: FakeS3())
    response = await files.head_file("archetype-cache/example.glb")

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
async def test_head_file_returns_404_for_stale_storage_key(monkeypatch) -> None:
    class MissingS3:
        def head_object(self, **_kwargs):
            raise KeyError("missing")

    monkeypatch.setattr(files, "_s3_client", lambda: MissingS3())

    with pytest.raises(HTTPException) as exc_info:
        await files.head_file("archetype-cache/missing.glb")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_file_can_force_a_named_download(monkeypatch) -> None:
    class FakeBody:
        def read(self):
            return b"video"

    class FakeS3:
        def get_object(self, **_kwargs):
            return {"Body": FakeBody(), "ContentType": "video/mp4"}

    monkeypatch.setattr(files, "_s3_client", lambda: FakeS3())
    response = await files.get_file(
        "projects/example/video-render/attempt/omni.mp4",
        download=True,
        filename="city-prompt-golden-hour.mp4",
    )

    assert response.body == b"video"
    assert response.headers["content-type"] == "video/mp4"
    assert response.headers["content-disposition"] == 'attachment; filename="city-prompt-golden-hour.mp4"'
