from types import SimpleNamespace

from app.api.v1 import oauth


def _settings(*, production: bool):
    return SimpleNamespace(
        frontend_url="https://cityprompt.example" if production else "http://localhost:5175",
        cors_origins=(
            ["https://cityprompt.example"] if production else ["http://localhost:5174", "http://localhost:5175"]
        ),
        is_production=production,
    )


def test_development_preserves_ipv4_loopback_worktree_origin(monkeypatch):
    monkeypatch.setattr(oauth, "settings", _settings(production=False))
    origin = "http://127.0.0.1:5174"

    state = oauth._build_oauth_state(origin)

    assert oauth._resolve_frontend_redirect_origin(state) == origin


def test_development_rejects_loopback_url_that_is_not_an_origin(monkeypatch):
    monkeypatch.setattr(oauth, "settings", _settings(production=False))

    state = oauth._build_oauth_state("http://127.0.0.1:5174/oauth/callback")

    assert oauth._resolve_frontend_redirect_origin(state) == "http://localhost:5175"


def test_production_does_not_implicitly_allow_loopback_origin(monkeypatch):
    monkeypatch.setattr(oauth, "settings", _settings(production=True))

    state = oauth._build_oauth_state("http://127.0.0.1:5174")

    assert oauth._resolve_frontend_redirect_origin(state) == "https://cityprompt.example"
