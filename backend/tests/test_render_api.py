from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from google.auth.exceptions import DefaultCredentialsError, TransportError

from app.api.v1.render import (
    _describe_google_auth_failure,
    _enforce_global_daily_render_cap,
    _utc_day_start,
)


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class _DbWithTokenTotal:
    def __init__(self, tokens_spent_today):
        self.tokens_spent_today = tokens_spent_today

    async def execute(self, _statement):
        return _ScalarResult(self.tokens_spent_today)


def _settings(**overrides):
    base = {
        "app_debug": False,
        "app_env": "development",
        "google_application_credentials": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_utc_day_start_normalizes_to_midnight_utc():
    now = datetime(2026, 5, 28, 18, 30, tzinfo=timezone.utc)

    assert _utc_day_start(now) == datetime(2026, 5, 28, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_global_daily_render_cap_allows_disabled_cap():
    await _enforce_global_daily_render_cap(
        _DbWithTokenTotal(tokens_spent_today=9999),
        token_cost=13,
        daily_cap=0,
    )


@pytest.mark.asyncio
async def test_global_daily_render_cap_allows_render_under_cap():
    await _enforce_global_daily_render_cap(
        _DbWithTokenTotal(tokens_spent_today=37),
        token_cost=13,
        daily_cap=50,
    )


@pytest.mark.asyncio
async def test_global_daily_render_cap_blocks_render_over_cap():
    with pytest.raises(HTTPException) as exc_info:
        await _enforce_global_daily_render_cap(
            _DbWithTokenTotal(tokens_spent_today=38),
            token_cost=13,
            daily_cap=50,
        )

    assert exc_info.value.status_code == 429
    assert "Daily render token cap reached" in exc_info.value.detail


def test_describe_google_auth_failure_when_credentials_not_configured(monkeypatch):
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)

    detail = _describe_google_auth_failure(
        DefaultCredentialsError("missing credentials"),
        _settings(app_env="production"),
    )

    assert "not configured" in detail
    assert "GOOGLE_APPLICATION_CREDENTIALS" in detail


def test_describe_google_auth_failure_when_credentials_file_missing(monkeypatch):
    missing_path = "C:/missing/vertex-key.json"
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", missing_path)

    detail = _describe_google_auth_failure(
        DefaultCredentialsError("file missing"),
        _settings(app_env="production"),
    )

    assert "was not found" in detail
    assert missing_path in detail


def test_describe_google_auth_failure_for_bad_adc_file(monkeypatch, tmp_path):
    credentials_path = tmp_path / "vertex-key.json"
    credentials_path.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(credentials_path))

    detail = _describe_google_auth_failure(
        DefaultCredentialsError("not a valid service account"),
        _settings(app_env="production"),
    )

    assert "could not be loaded" in detail
    assert "service-account JSON" in detail


def test_describe_google_auth_failure_for_transport_error(monkeypatch, tmp_path):
    credentials_path = tmp_path / "vertex-key.json"
    credentials_path.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(credentials_path))

    detail = _describe_google_auth_failure(
        TransportError("connection blocked"),
        _settings(app_env="production"),
    )

    assert "could not reach Google's token service" in detail
    assert "oauth2.googleapis.com" in detail


def test_describe_google_auth_failure_for_permission_error(monkeypatch, tmp_path):
    credentials_path = tmp_path / "vertex-key.json"
    credentials_path.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(credentials_path))

    detail = _describe_google_auth_failure(
        RuntimeError("403 permission denied"),
        _settings(app_env="production"),
    )

    assert "Google rejected the token request" in detail
    assert "Vertex AI" in detail


def test_describe_google_auth_failure_includes_debug_suffix(monkeypatch, tmp_path):
    credentials_path = tmp_path / "vertex-key.json"
    credentials_path.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(credentials_path))

    detail = _describe_google_auth_failure(
        TransportError("connection blocked"),
        _settings(app_debug=True, app_env="development"),
    )

    assert "[TransportError: connection blocked]" in detail
