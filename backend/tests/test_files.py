import pytest
from fastapi import HTTPException

from app.api.v1 import files


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
    assert calls == [{
        "Bucket": files.settings.s3_bucket_name,
        "Key": "archetype-cache/example.glb",
    }]


@pytest.mark.asyncio
async def test_head_file_returns_404_for_stale_storage_key(monkeypatch) -> None:
    class MissingS3:
        def head_object(self, **_kwargs):
            raise KeyError("missing")

    monkeypatch.setattr(files, "_s3_client", lambda: MissingS3())

    with pytest.raises(HTTPException) as exc_info:
        await files.head_file("archetype-cache/missing.glb")

    assert exc_info.value.status_code == 404
