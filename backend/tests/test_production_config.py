import pytest

from app.core.config import Settings


def test_production_rejects_default_jwt_secret():
    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        Settings(
            app_env="production",
            app_debug=False,
            jwt_secret_key="change-this-in-production",
            allowed_origins="https://cityprompt.example",
        )


def test_production_rejects_localhost_cors_origin():
    with pytest.raises(ValueError, match="ALLOWED_ORIGINS"):
        Settings(
            app_env="production",
            app_debug=False,
            jwt_secret_key="safe-production-secret",
            allowed_origins="https://cityprompt.example,http://localhost:5175",
        )


def test_production_rejects_debug_mode():
    with pytest.raises(ValueError, match="APP_DEBUG"):
        Settings(
            app_env="production",
            app_debug=True,
            jwt_secret_key="safe-production-secret",
            allowed_origins="https://cityprompt.example",
        )


def test_production_accepts_explicit_safe_origin():
    settings = Settings(
        app_env="production",
        app_debug=False,
        jwt_secret_key="safe-production-secret",
        allowed_origins="https://cityprompt.example",
    )

    assert settings.is_production is True
    assert settings.cors_origins == ["https://cityprompt.example"]
    assert settings.cors_allow_origin_regex is None


def test_production_accepts_render_worker_env_contract():
    settings = Settings(
        app_env="production",
        app_debug=False,
        jwt_secret_key="safe-production-secret",
        allowed_origins="https://cityprompt.ca,https://www.cityprompt.ca,https://threed-platform-frontend.onrender.com",
        frontend_url="https://cityprompt.ca",
        google_redirect_uri="https://threed-platform-api.onrender.com/api/v1/auth/oauth/google/callback",
        microsoft_redirect_uri="https://threed-platform-api.onrender.com/api/v1/auth/oauth/microsoft/callback",
        render_global_daily_token_cap=5000,
    )

    assert settings.is_production is True
    assert settings.cors_origins == [
        "https://cityprompt.ca",
        "https://www.cityprompt.ca",
        "https://threed-platform-frontend.onrender.com",
    ]
    assert settings.frontend_url == "https://cityprompt.ca"
    assert settings.google_redirect_uri.startswith("https://threed-platform-api.onrender.com/")
    assert settings.render_global_daily_token_cap == 5000


def test_development_keeps_localhost_cors_regex():
    settings = Settings(app_env="development")

    assert settings.is_production is False
    assert settings.cors_allow_origin_regex is not None
