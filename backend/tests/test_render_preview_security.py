"""Preview inputs are private uploaded images, never worker HTTP destinations."""

from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from PIL import Image
import pytest

from app.api.v1 import buildings
from app.core.database import get_db
from app.core.security import require_auth
from app.generation import stability_client
from app.models.models import Building, Document, Project, ProjectShare, User
from app.services import render_preview_source
from app.tasks import render_preview
from tests.conftest import FakeProject


def row(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def image_bytes():
    image = BytesIO()
    Image.new("RGB", (24, 18), "white").save(image, format="PNG")
    return image.getvalue()


@pytest.fixture
def preview_data(test_user):
    project = FakeProject(owner_id=test_user.id)
    building = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=project.id,
        preview_status="idle",
        architectural_style=None,
        created_at=datetime.now(timezone.utc),
    )
    document = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=project.id,
        file_type="png",
        file_size_bytes=100,
        storage_url=f"{buildings.settings.s3_endpoint_url}/{buildings.settings.s3_bucket_name}/projects/{project.id}/documents/{uuid.uuid4()}.png",
    )
    return project, building, document


@pytest.fixture
async def preview_api(mock_db, test_user, monkeypatch, preview_data):
    app = FastAPI()
    app.include_router(buildings.router, prefix="/buildings")
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[require_auth] = lambda: test_user
    monkeypatch.setattr(buildings, "settings", buildings.settings.model_copy(update={"stability_api_key": "mock-only"}))
    monkeypatch.setattr(render_preview.generate_render_preview, "delay", MagicMock())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/image.png",
        "http://127.0.0.1/image.png",
        "http://10.0.0.1/image.png",
        "http://169.254.169.254/image.png",
        "http://[::1]/image.png",
        "https://attacker.invalid/redirect-to-private",
        "file:///tmp/input.png",
    ],
)
async def test_client_urls_rejected_before_preview_dispatch(preview_api, preview_data, mock_db, url):
    project, building, _ = preview_data
    mock_db.execute.side_effect = [row(building), row(project)]
    response = await preview_api.post(
        f"/buildings/{building.id}/render-preview",
        json={
            "prompt": "Brick apartments",
            "source_type": "sketch",
            "source_image_url": url,
        },
    )
    assert response.status_code == 422
    assert building.preview_status == "idle"
    render_preview.generate_render_preview.delay.assert_not_called()


@pytest.mark.asyncio
async def test_same_project_uploaded_image_can_queue_sketch(preview_api, preview_data, mock_db, test_user):
    project, building, document = preview_data
    mock_db.execute.side_effect = [row(building), row(project), row(document)]
    response = await preview_api.post(
        f"/buildings/{building.id}/render-preview",
        json={
            "prompt": "Brick apartments",
            "source_type": "sketch",
            "source_document_id": str(document.id),
        },
    )
    assert response.status_code == 200
    assert response.json()["source_image_url"] == f"/api/v1/documents/{document.id}/file"
    queued = render_preview.generate_render_preview.delay.call_args
    assert queued.kwargs["source_document_id"] == str(document.id)
    assert queued.kwargs["requested_by"] == str(test_user.id)
    assert document.storage_url not in str(queued)


@pytest.mark.asyncio
async def test_foreign_project_document_cannot_be_used_as_a_preview(preview_api, preview_data, mock_db):
    project, building, document = preview_data
    document.project_id = uuid.uuid4()
    mock_db.execute.side_effect = [row(building), row(project), row(document)]
    response = await preview_api.post(
        f"/buildings/{building.id}/render-preview",
        json={
            "prompt": "Brick apartments",
            "source_type": "floor_plan",
            "source_document_id": str(document.id),
        },
    )
    assert response.status_code == 404
    render_preview.generate_render_preview.delay.assert_not_called()


@pytest.mark.asyncio
async def test_document_file_path_alias_preserves_uploaded_sketch_workflow(preview_api, preview_data, mock_db):
    project, building, document = preview_data
    mock_db.execute.side_effect = [row(building), row(project), row(document)]
    response = await preview_api.post(
        f"/buildings/{building.id}/render-preview",
        json={
            "prompt": "Brick apartments",
            "source_type": "floor_plan",
            "source_image_url": f"/api/v1/documents/{document.id}/file",
        },
    )
    assert response.status_code == 200
    assert render_preview.generate_render_preview.delay.call_args.kwargs["source_document_id"] == str(document.id)


@pytest.mark.asyncio
async def test_text_preview_preserves_source_free_workflow(preview_api, preview_data, mock_db):
    project, building, _ = preview_data
    mock_db.execute.side_effect = [row(building), row(project)]
    response = await preview_api.post(f"/buildings/{building.id}/render-preview", json={"prompt": "Brick apartments"})
    assert response.status_code == 200
    assert response.json()["source_image_url"] is None
    assert render_preview.generate_render_preview.delay.call_args.kwargs["source_document_id"] is None


@pytest.mark.asyncio
async def test_revoked_project_editor_cannot_submit_preview(preview_api, preview_data, mock_db):
    project, building, _ = preview_data
    project.owner_id = uuid.uuid4()
    mock_db.execute.side_effect = [row(building), row(project), row(None)]
    response = await preview_api.post(f"/buildings/{building.id}/render-preview", json={"prompt": "Brick apartments"})
    assert response.status_code == 403
    assert building.preview_status == "idle"
    render_preview.generate_render_preview.delay.assert_not_called()


class PreviewSession:
    def __init__(self, values):
        self.values = values
        self.added = []

    def query(self, model):
        session = self

        class Query:
            def filter_by(self, **filters):
                self.filters = filters
                return self

            def first(self):
                value = session.values.get(model)
                return (
                    value if value and all(getattr(value, key) == item for key, item in self.filters.items()) else None
                )

        return Query()

    def add(self, value):
        value.id = uuid.uuid4()
        self.added.append(value)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


@pytest.fixture
def worker(preview_data, test_user, monkeypatch):
    project, building, document = preview_data
    session = PreviewSession({Building: building, Project: project, Document: document, User: test_user})
    monkeypatch.setattr(render_preview, "_get_sync_session", lambda: session)
    monkeypatch.setattr(render_preview, "_upload_to_storage", lambda *_: "/api/v1/files/synthetic-preview.png")
    monkeypatch.setattr(render_preview.generate_render_preview, "update_state", MagicMock())

    def fail(exc, **_):
        raise exc

    monkeypatch.setattr(render_preview.generate_render_preview, "retry", fail)
    provider = SimpleNamespace(
        image_to_image=AsyncMock(return_value=b"synthetic-output"),
        text_to_image=AsyncMock(return_value=b"synthetic-output"),
    )
    monkeypatch.setattr(stability_client, "StabilityClient", lambda: provider)
    # A regression cannot contact any source URL, including before the fix.
    import httpx

    http = MagicMock(return_value=SimpleNamespace(content=image_bytes()))
    monkeypatch.setattr(httpx, "get", http)
    return session, provider, http


def test_worker_rejects_legacy_arbitrary_source_url_before_network_or_provider(worker, preview_data):
    _, provider, http = worker
    _, building, _ = preview_data
    with pytest.raises(ValueError):
        render_preview.generate_render_preview.run(
            str(building.id), "Brick apartments", "sketch", "http://127.0.0.1/input.png"
        )
    http.assert_not_called()
    provider.image_to_image.assert_not_awaited()
    provider.text_to_image.assert_not_awaited()


@pytest.mark.parametrize("access", ["revoked", "viewer", "inactive", "foreign_document"])
def test_queued_worker_rechecks_access_before_reading_source(worker, preview_data, test_user, monkeypatch, access):
    session, provider, _ = worker
    project, building, document = preview_data
    if access in {"revoked", "viewer"}:
        project.owner_id = uuid.uuid4()
        if access == "viewer":
            session.values[ProjectShare] = SimpleNamespace(
                project_id=project.id, user_id=test_user.id, permission="viewer"
            )
    elif access == "inactive":
        test_user.is_active = False
    else:
        document.project_id = uuid.uuid4()
    read = MagicMock(side_effect=AssertionError("unauthorized source must not be read"))
    monkeypatch.setattr(render_preview_source, "read_source_image", read)
    with pytest.raises(ValueError):
        render_preview.generate_render_preview.run(
            str(building.id),
            "Brick apartments",
            "sketch",
            source_document_id=str(document.id),
            requested_by=str(test_user.id),
        )
    read.assert_not_called()
    provider.image_to_image.assert_not_awaited()
    provider.text_to_image.assert_not_awaited()


@pytest.mark.parametrize("role", ["owner", "editor"])
def test_authorized_worker_reads_storage_and_sends_validated_png(worker, preview_data, test_user, monkeypatch, role):
    session, provider, http = worker
    project, building, document = preview_data
    if role == "editor":
        project.owner_id = uuid.uuid4()
        session.values[ProjectShare] = SimpleNamespace(project_id=project.id, user_id=test_user.id, permission="editor")
    source = BytesIO(image_bytes())
    storage = MagicMock()
    storage.get_object.return_value = {"Body": source, "ContentLength": len(source.getvalue())}
    monkeypatch.setattr(render_preview_source.boto3, "client", lambda *_args, **_kwargs: storage)
    result = render_preview.generate_render_preview.run(
        str(building.id),
        "Brick apartments",
        "floor_plan",
        source_document_id=str(document.id),
        requested_by=str(test_user.id),
    )
    assert result["status"] == "completed" and building.preview_status == "completed"
    assert session.added[0].source_image_url == f"/api/v1/documents/{document.id}/file"
    assert source.closed
    http.assert_not_called()
    data = provider.image_to_image.call_args.args[0]
    with Image.open(BytesIO(data)) as image:
        assert image.format == "PNG" and image.size == (24, 18) and image.getpixel((0, 0)) == (255, 255, 255)
    provider.text_to_image.assert_not_awaited()
    assert storage.get_object.call_args.kwargs["Key"].startswith(f"projects/{project.id}/documents/")


def test_authorized_text_worker_preserves_text_to_image(worker, preview_data, test_user):
    _, provider, http = worker
    _, building, _ = preview_data
    result = render_preview.generate_render_preview.run(
        str(building.id), "Brick apartments", requested_by=str(test_user.id)
    )
    assert result["status"] == "completed"
    provider.text_to_image.assert_awaited_once()
    provider.image_to_image.assert_not_awaited()
    http.assert_not_called()


def test_worker_rejects_deferred_classroom_preview_before_loading_data(monkeypatch, preview_data, test_user):
    monkeypatch.setattr(render_preview, "settings", SimpleNamespace(classroom_release=True))
    get_session = MagicMock()
    monkeypatch.setattr(render_preview, "_get_sync_session", get_session)
    _, building, _ = preview_data
    with pytest.raises(ValueError, match="classroom"):
        render_preview.generate_render_preview.run(str(building.id), "Brick apartments", requested_by=str(test_user.id))
    get_session.assert_not_called()


@pytest.mark.parametrize("corruption", ["foreign_key", "bad_origin", "oversize", "corrupt_image", "pixel_bomb"])
def test_untrusted_stored_images_fail_before_paid_dispatch(worker, preview_data, test_user, monkeypatch, corruption):
    _, provider, http = worker
    project, building, document = preview_data
    data = image_bytes()
    if corruption == "foreign_key":
        document.storage_url = document.storage_url.replace(str(project.id), str(uuid.uuid4()))
    elif corruption == "bad_origin":
        document.storage_url = "http://127.0.0.1/" + document.storage_url.split("/", 3)[-1]
    elif corruption == "corrupt_image":
        data = b"this is not an image"
    elif corruption == "pixel_bomb":
        # A tiny header claims too many pixels. No large image is allocated.
        import struct
        import zlib

        header = data[12:16] + struct.pack(">II", 5000, 4000) + data[24:29]
        data = data[:16] + header[4:] + struct.pack(">I", zlib.crc32(header)) + data[33:]
    source = BytesIO(data)
    storage = MagicMock()
    storage.get_object.return_value = {
        "Body": source,
        "ContentLength": render_preview_source.MAX_SOURCE_BYTES + 1 if corruption == "oversize" else len(data),
    }
    monkeypatch.setattr(render_preview_source.boto3, "client", lambda *_args, **_kwargs: storage)
    with pytest.raises(ValueError):
        render_preview.generate_render_preview.run(
            str(building.id),
            "Brick apartments",
            "sketch",
            source_document_id=str(document.id),
            requested_by=str(test_user.id),
        )
    http.assert_not_called()
    provider.image_to_image.assert_not_awaited()
    provider.text_to_image.assert_not_awaited()
    if corruption in {"foreign_key", "bad_origin"}:
        storage.get_object.assert_not_called()
    else:
        assert source.closed


def test_storage_read_is_bounded_even_when_content_length_is_wrong(preview_data, monkeypatch):
    project, _, document = preview_data
    body = MagicMock()
    body.read.return_value = b"x" * (render_preview_source.MAX_SOURCE_BYTES + 1)
    storage = MagicMock()
    storage.get_object.return_value = {"Body": body, "ContentLength": 1}
    monkeypatch.setattr(render_preview_source.boto3, "client", lambda *_args, **_kwargs: storage)
    with pytest.raises(ValueError, match="size limit"):
        render_preview_source.read_source_image(document, project.id)
    body.read.assert_called_once_with(5 * 1024 * 1024 + 1)
    body.close.assert_called_once()


def test_prepared_preview_source_excludes_private_image_metadata():
    source = BytesIO()
    image = Image.new("RGB", (24, 18), "white")
    metadata = Image.Exif()
    metadata[315] = "private source metadata"
    image.save(source, format="PNG", exif=metadata)
    prepared = render_preview_source.prepare_source_image(source.getvalue())
    with Image.open(BytesIO(prepared)) as output:
        assert not output.getexif()
    assert b"private source metadata" not in prepared
