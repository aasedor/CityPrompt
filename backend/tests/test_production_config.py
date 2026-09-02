import pytest

import app.core.config as config_module
from app.core.config import Settings, _git_common_dir, _settings_env_files


def test_primary_checkout_resolves_one_shared_and_two_local_env_files(tmp_path):
    project_root = tmp_path / "city-prompt"
    backend_root = project_root / "backend"
    common_dir = project_root / ".git"
    backend_root.mkdir(parents=True)
    common_dir.mkdir()

    assert _git_common_dir(project_root) == common_dir.resolve()
    assert _settings_env_files(backend_root) == (
        str(common_dir / ".env"),
        str(project_root / ".env"),
        str(backend_root / ".env"),
    )


def test_linked_worktree_resolves_primary_checkout_shared_env(tmp_path):
    common_dir = tmp_path / "primary" / ".git"
    admin_dir = common_dir / "worktrees" / "workflow"
    project_root = tmp_path / "workflow"
    backend_root = project_root / "backend"
    admin_dir.mkdir(parents=True)
    backend_root.mkdir(parents=True)
    (project_root / ".git").write_text(f"gitdir: {admin_dir}\n", encoding="utf-8")
    (admin_dir / "commondir").write_text("../..\n", encoding="utf-8")

    assert _git_common_dir(project_root) == common_dir.resolve()
    assert _settings_env_files(backend_root) == (
        str(common_dir / ".env"),
        str(common_dir.parent / ".env"),
        str(project_root / ".env"),
        str(backend_root / ".env"),
    )


def test_linked_worktree_reads_rotated_maps_key_from_primary_checkout(tmp_path, monkeypatch):
    primary_root = tmp_path / "primary"
    common_dir = primary_root / ".git"
    admin_dir = common_dir / "worktrees" / "workflow"
    project_root = tmp_path / "workflow"
    admin_dir.mkdir(parents=True)
    project_root.mkdir(parents=True)
    (project_root / ".git").write_text(f"gitdir: {admin_dir}\n", encoding="utf-8")
    (admin_dir / "commondir").write_text("../..\n", encoding="utf-8")
    (primary_root / ".env").write_text("VITE_GOOGLE_MAPS_API_KEY=rotated-local-key\n", encoding="utf-8")
    monkeypatch.setattr(config_module, "_PROJECT_ROOT", project_root)

    assert config_module._primary_checkout_env_value("VITE_GOOGLE_MAPS_API_KEY") == "rotated-local-key"


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
