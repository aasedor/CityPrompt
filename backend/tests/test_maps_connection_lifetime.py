"""Slow read-only Maps work must not occupy the database pool after auth."""

import asyncio
import uuid
from types import SimpleNamespace

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.v1 import elevation
from app.core import provider_limits
from app.core.database import get_db
from app.core.security import create_access_token, require_auth


class OneConnectionPool:
    """Model checkout/return without touching any development or production DB."""

    def __init__(self, user):
        self.available = asyncio.Semaphore(1)
        self.user = user

    def session(self):
        pool = self

        class Session:
            checked_out = False

            async def execute(self, _query):
                if not self.checked_out:
                    await asyncio.wait_for(pool.available.acquire(), timeout=0.25)
                    self.checked_out = True
                return SimpleNamespace(scalar_one_or_none=lambda: pool.user)

            async def close(self):
                if self.checked_out:
                    self.checked_out = False
                    pool.available.release()

        return Session()


def application(pool, external_provider):
    api = FastAPI()

    async def session():
        db = pool.session()
        try:
            yield db
        finally:
            await db.close()

    api.dependency_overrides[get_db] = session
    api.include_router(elevation.router, prefix="/elevation")

    # The real geocoding router uses this same authenticated admission boundary.
    api.add_api_route(
        "/geocoding", external_provider, methods=["GET"], dependencies=[Depends(provider_limits.require_maps_admission)]
    )

    @api.get("/saved-work")
    async def saved_work(_user=Depends(require_auth), db=Depends(get_db)):
        await db.execute("short unrelated database read")
        return {"saved_work_available": True}

    return api


@pytest.mark.parametrize("route", ["single", "batch", "geocoding"])
@pytest.mark.parametrize("stage", ["admission", "provider"])
@pytest.mark.asyncio
async def test_slow_maps_request_does_not_starve_authenticated_database_reads(route, stage, monkeypatch):
    user = SimpleNamespace(id=uuid.uuid4(), role="editor", is_active=True, session_version=0)
    pool = OneConnectionPool(user)
    entered, finish = asyncio.Event(), asyncio.Event()

    async def wait_for_external_work():
        entered.set()
        await finish.wait()

    async def admission(*_args, **_kwargs):
        if stage == "admission":
            await wait_for_external_work()

    async def provider(*_args, **_kwargs):
        if stage == "provider":
            await wait_for_external_work()
        return elevation._unavailable(51, -114, "network_error")

    async def batch_provider(*_args, **_kwargs):
        if stage == "provider":
            await wait_for_external_work()
        return elevation.BatchElevationResponse(
            elevations=[-25], statuses=["unavailable"], sources=["renderer_fallback"]
        )

    async def geocoding_provider():
        if stage == "provider":
            await wait_for_external_work()
        return {"suggestions": []}

    monkeypatch.setattr(elevation, "admit_maps_request", admission)
    monkeypatch.setattr(provider_limits, "admit_maps_request", admission)
    monkeypatch.setattr(elevation, "get_elevation", provider)
    monkeypatch.setattr(elevation, "get_elevation_batch", batch_provider)
    api = application(pool, geocoding_provider)
    headers = {"Authorization": f"Bearer {create_access_token(str(user.id), user.role)}"}
    async with AsyncClient(
        transport=ASGITransport(app=api, raise_app_exceptions=False), base_url="http://test"
    ) as client:
        if route == "single":
            pending = asyncio.create_task(client.get("/elevation?lat=51&lng=-114", headers=headers))
        elif route == "batch":
            pending = asyncio.create_task(
                client.post("/elevation/batch", json={"points": [[-114, 51]]}, headers=headers)
            )
        else:
            pending = asyncio.create_task(client.get("/geocoding", headers=headers))
        try:
            await asyncio.wait_for(entered.wait(), timeout=1)
            response = await asyncio.wait_for(client.get("/saved-work", headers=headers), timeout=1)
            assert response.status_code == 200
            assert response.json() == {"saved_work_available": True}
        finally:
            finish.set()
            completed = await asyncio.wait_for(pending, timeout=1)
        assert completed.status_code == 200


@pytest.mark.parametrize("route", ["single", "batch", "geocoding"])
@pytest.mark.asyncio
async def test_revoked_maps_credentials_still_fail_before_external_work(route, monkeypatch):
    user = SimpleNamespace(id=uuid.uuid4(), role="editor", is_active=True, session_version=1)
    pool = OneConnectionPool(user)

    async def forbidden(*_args, **_kwargs):
        raise AssertionError("Revoked credentials must not reach admission or provider work")

    monkeypatch.setattr(elevation, "admit_maps_request", forbidden)
    monkeypatch.setattr(provider_limits, "admit_maps_request", forbidden)
    monkeypatch.setattr(elevation, "get_elevation", forbidden)
    monkeypatch.setattr(elevation, "get_elevation_batch", forbidden)
    api = application(pool, forbidden)
    headers = {"Authorization": f"Bearer {create_access_token(str(user.id), user.role, session_version=0)}"}
    async with AsyncClient(
        transport=ASGITransport(app=api, raise_app_exceptions=False), base_url="http://test"
    ) as client:
        if route == "single":
            response = await client.get("/elevation?lat=51&lng=-114", headers=headers)
        elif route == "batch":
            response = await client.post("/elevation/batch", json={"points": [[-114, 51]]}, headers=headers)
        else:
            response = await client.get("/geocoding", headers=headers)
        assert response.status_code == 401
