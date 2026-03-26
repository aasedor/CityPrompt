from types import SimpleNamespace

from google.auth.exceptions import DefaultCredentialsError, TransportError

from app.api.v1.render import _describe_google_auth_failure


def _settings(**overrides):
    base = {
        "app_debug": False,
        "app_env": "development",
        "google_application_credentials": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


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
