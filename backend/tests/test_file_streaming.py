"""Independent server-loop responsiveness and S3 streaming resource ownership."""

import asyncio
from io import BytesIO
import threading
import time
from unittest.mock import AsyncMock

from fastapi import HTTPException
import pytest
from starlette.requests import ClientDisconnect

from app.api.v1 import files
from tests.file_response_support import response_bytes

PATH = "archetype-cache/streaming-fixture.glb"
DATA = bytes(range(256)) * 1024


class Body:
    def __init__(self, data=DATA, gate=None, fail=False):
        self.data = BytesIO(data)
        self.gate = gate
        self.fail = fail
        self.sizes = []
        self.close_count = 0
        self.closed = threading.Event()

    def read(self, size=None):
        self.sizes.append(size)
        if self.gate:
            gate, self.gate = self.gate, None
            gate()
        if self.fail:
            raise RuntimeError("synthetic storage read failure")
        return self.data.read(size)

    def close(self):
        self.close_count += 1
        self.data.close()
        self.closed.set()


class Storage:
    def __init__(self, body=None, gate=None, fail=False):
        self.body = body or Body()
        self.gate = gate
        self.fail = fail
        self.close_count = 0
        self.thread_ids = []

    def get_object(self, **_kwargs):
        self.thread_ids.append(threading.get_ident())
        if self.gate:
            self.gate()
        if self.fail:
            raise RuntimeError("synthetic storage open failure")
        return {"Body": self.body, "ContentLength": len(DATA), "ContentType": "model/gltf-binary"}

    def head_object(self, **_kwargs):
        self.thread_ids.append(threading.get_ident())
        if self.gate:
            self.gate()
        return {"ContentLength": len(DATA), "ContentType": "model/gltf-binary"}

    def close(self):
        self.close_count += 1


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["construct", "open", "read", "head"])
async def test_blocking_storage_does_not_stop_an_independent_event_loop_heartbeat(monkeypatch, mock_db, phase):
    ticks = []
    held = []

    def block():
        started = time.monotonic()
        release = threading.Event()
        timer = threading.Timer(0.2, release.set)
        timer.start()
        try:
            assert release.wait(2)
        finally:
            timer.join()
        held.append((started, time.monotonic()))

    storage = Storage(
        body=Body(gate=block if phase == "read" else None), gate=block if phase in {"open", "head"} else None
    )

    def construct():
        if phase == "construct":
            block()
        return storage

    monkeypatch.setattr(files, "_s3_client", construct)
    running = True

    async def heartbeat():
        while running:
            ticks.append(time.monotonic())
            await asyncio.sleep(0.002)

    ticker = asyncio.create_task(heartbeat())
    await asyncio.sleep(0)
    try:
        if phase == "head":
            await files.head_file(PATH, user=None, db=mock_db)
        else:
            response = await files.get_file(PATH, user=None, db=mock_db)
            assert await response_bytes(response) == DATA
    finally:
        running = False
        await ticker
    assert held
    assert all(
        any(start < tick < end for tick in ticks) for start, end in held
    ), "Synchronous S3 I/O blocked the API event loop"
    assert all(thread_id != threading.get_ident() for thread_id in storage.thread_ids)


@pytest.mark.asyncio
async def test_original_is_lazy_exact_and_uses_bounded_reads_with_metadata(monkeypatch, mock_db):
    storage = Storage()
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    response = await files.get_file(PATH, user=None, db=mock_db, download=True, filename="review-model.glb")
    assert storage.body.sizes == [], "Creating the response must not buffer the original"
    assert response.headers["content-length"] == str(len(DATA))
    assert response.headers["content-type"] == "model/gltf-binary"
    assert response.headers["content-disposition"] == 'attachment; filename="review-model.glb"'
    assert response.headers["cache-control"] == "public, max-age=31536000, immutable"
    assert await response_bytes(response) == DATA
    assert storage.body.sizes and all(isinstance(size, int) and 0 < size <= 65536 for size in storage.body.sizes)
    assert storage.body.close_count == 1 and storage.close_count == 1


@pytest.mark.asyncio
async def test_database_connection_is_released_after_authorization_before_storage(monkeypatch, mock_db):
    events = []
    monkeypatch.setattr(
        files, "_authorize_file", AsyncMock(side_effect=lambda *_args: events.append("authorized") or False)
    )
    mock_db.close.side_effect = lambda: events.append("db-closed")
    storage = Storage()

    def construct():
        events.append("storage-open")
        return storage

    monkeypatch.setattr(files, "_s3_client", construct)
    response = await files.get_file("library/private/model.glb", user=None, db=mock_db)
    assert events == ["authorized", "db-closed", "storage-open"]
    assert response.headers["cache-control"] == "private, no-store"
    assert await response_bytes(response) == DATA


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["before-first-chunk", "sending-chunk", "reading"])
async def test_body_and_client_close_on_stream_failures(monkeypatch, mock_db, phase):
    storage = Storage(body=Body(fail=phase == "reading"))
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    response = await files.get_file(PATH, user=None, db=mock_db)

    async def send(message):
        if phase == "before-first-chunk" and message["type"] == "http.response.start":
            raise OSError("synthetic disconnect")
        if phase == "sending-chunk" and message.get("body"):
            raise OSError("synthetic disconnect")

    async def receive():
        return {"type": "http.disconnect"}

    with pytest.raises((RuntimeError, ClientDisconnect)):
        await response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send)
    assert storage.body.close_count == 1 and storage.close_count == 1


@pytest.mark.asyncio
async def test_disconnect_event_closes_stream_without_prefetching_the_whole_file(monkeypatch, mock_db):
    storage = Storage()
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    response = await files.get_file(PATH, user=None, db=mock_db)
    first_chunk = asyncio.Event()
    received = []

    async def send(message):
        if message.get("body"):
            received.append(message["body"])
            first_chunk.set()

    async def receive():
        await first_chunk.wait()
        return {"type": "http.disconnect"}

    await response({"type": "http", "asgi": {"spec_version": "2.3"}}, receive, send)
    assert 0 < len(b"".join(received)) < len(DATA)
    assert storage.body.close_count == 1 and storage.close_count == 1


@pytest.mark.asyncio
async def test_open_failure_closes_client_and_keeps_safe_404(monkeypatch, mock_db):
    storage = Storage(fail=True)
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    with pytest.raises(HTTPException) as rejected:
        await files.get_file(PATH, user=None, db=mock_db)
    assert rejected.value.status_code == 404
    assert rejected.value.detail == "File not found in storage"
    assert storage.close_count == 1


@pytest.mark.asyncio
async def test_cancelled_open_closes_the_body_when_blocking_sdk_call_returns(monkeypatch, mock_db):
    entered, release = threading.Event(), threading.Event()

    def block():
        entered.set()
        assert release.wait(2)

    storage = Storage(gate=block)
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    request = asyncio.create_task(files.get_file(PATH, user=None, db=mock_db))
    try:
        while not entered.is_set():
            await asyncio.sleep(0.001)
        request.cancel()
        with pytest.raises(asyncio.CancelledError):
            await request
    finally:
        release.set()
    for _ in range(100):
        if storage.body.closed.is_set():
            break
        await asyncio.sleep(0.005)
    assert storage.body.close_count == 1 and storage.close_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("spec", ["2.0", "2.3"])
async def test_disconnect_before_iterator_starts_closes_open_resources(monkeypatch, mock_db, spec):
    storage = Storage()
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    response = await files.get_file(PATH, user=None, db=mock_db)

    async def send(_message):
        await asyncio.Event().wait()

    async def receive():
        return {"type": "http.disconnect"}

    await response({"type": "http", "asgi": {"spec_version": spec}}, receive, send)
    assert storage.body.sizes == []
    assert storage.body.close_count == 1 and storage.close_count == 1


@pytest.mark.asyncio
async def test_raw_task_cancellation_during_blocking_read_closes_resources(monkeypatch, mock_db):
    entered, release = threading.Event(), threading.Event()

    class WaitingBody(Body):
        def read(self, size=None):
            self.sizes.append(size)
            entered.set()
            assert release.wait(2)
            return b""

        def close(self):
            super().close()
            release.set()

    storage = Storage(body=WaitingBody())
    monkeypatch.setattr(files, "_s3_client", lambda: storage)
    response = await files.get_file(PATH, user=None, db=mock_db)

    async def send(_message):
        pass

    async def receive():
        return {"type": "http.disconnect"}

    request = asyncio.create_task(response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send))
    try:
        while not entered.is_set():
            await asyncio.sleep(0.001)
        request.cancel()
        with pytest.raises(asyncio.CancelledError):
            await request
    finally:
        release.set()
    assert storage.body.close_count == 1 and storage.close_count == 1
