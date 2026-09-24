"""Startup must fail closed without leaking secrets or changing account roles."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import readiness
from app.main import readiness_check
from scripts import ensure_admins


@pytest.mark.asyncio
async def test_readiness_reports_missing_dependencies_without_exception_secrets(monkeypatch):
    for name in ("database_ready", "redis_ready", "storage_ready", "images_ready", "assets_ready"):
        monkeypatch.setattr(readiness, name, AsyncMock())
    monkeypatch.setattr(readiness, "database_ready", AsyncMock(side_effect=RuntimeError("secret-database-url")))
    response = await readiness_check()
    assert response.status_code == 503
    assert response.headers["cache-control"] == "no-store"
    report = json.loads(response.body)
    assert report["checks"]["database"] == "unavailable"
    assert "secret-database-url" not in response.body.decode()


@pytest.mark.asyncio
async def test_readiness_distinguishes_optional_checks_from_passed_checks(monkeypatch):
    for name in ("database_ready", "redis_ready", "storage_ready"):
        monkeypatch.setattr(readiness, name, AsyncMock())
    for name in ("images_ready", "assets_ready"):
        monkeypatch.setattr(readiness, name, AsyncMock(return_value="not_enabled"))
    response = await readiness_check()
    assert response.status_code == 200
    assert json.loads(response.body)["checks"]["starter_assets"] == "not_enabled"


@pytest.mark.asyncio
async def test_schema_mismatch_is_not_ready(monkeypatch):
    session = AsyncMock()
    session.__aenter__.return_value = session
    rows = MagicMock()
    rows.scalars.return_value = ["old_schema"]
    session.execute.return_value = rows
    monkeypatch.setattr(readiness, "async_session_factory", lambda: session)
    with pytest.raises(RuntimeError, match="schema"):
        await readiness.database_ready()


@pytest.mark.asyncio
async def test_unreviewed_starter_receipt_cannot_qualify_classroom_release(monkeypatch, tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"command": "preflight", "errors": [], "dependencies": [], "runtime_reviews_required": True, "roster_sha256": "wrong"}))
    monkeypatch.setattr(readiness, "get_settings", lambda: SimpleNamespace(classroom_release=True, direct_3d_jobs_enabled=True, classroom_asset_receipt=str(receipt)))
    with pytest.raises(RuntimeError, match="does not qualify"):
        await readiness.assets_ready()


@pytest.mark.asyncio
async def test_no_default_admin_or_hardcoded_promotion(monkeypatch):
    monkeypatch.delenv("BOOTSTRAP_ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("BOOTSTRAP_ADMIN_PASSWORD", raising=False)
    db = MagicMock()
    monkeypatch.setattr(ensure_admins, "async_session_factory", db)
    await ensure_admins.ensure_admins()
    db.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["editor", "viewer", "admin", "cofounder"])
async def test_bootstrap_never_promotes_or_changes_existing_account(monkeypatch, role):
    monkeypatch.setenv("BOOTSTRAP_ADMIN_EMAIL", "bootstrap@test.invalid")
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "only-a-test-password")
    user = SimpleNamespace(role=role, hashed_password="original-hash")
    db = AsyncMock()
    db.__aenter__.return_value = db
    db.scalar.return_value = user
    monkeypatch.setattr(ensure_admins, "async_session_factory", lambda: db)
    if role in {"editor", "viewer"}:
        with pytest.raises(RuntimeError, match="non-administrator"):
            await ensure_admins.ensure_admins()
    else:
        await ensure_admins.ensure_admins()
    assert user.role == role and user.hashed_password == "original-hash"
    db.commit.assert_not_awaited()


def test_bootstrap_rejects_partial_or_default_password(monkeypatch):
    monkeypatch.setenv("BOOTSTRAP_ADMIN_EMAIL", "bootstrap@test.invalid")
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123!")
    with pytest.raises(ValueError, match="at least 16"):
        ensure_admins.bootstrap_credentials()
