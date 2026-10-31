from types import SimpleNamespace
import pytest
from app.services.plan_geometry.archetypes import load_dims_table


@pytest.mark.parametrize(
    "flag,app_env,db",
    [
        ("", "development", "postgresql://localhost/local"),
        ("true", "production", "postgresql://localhost/local"),
        ("true", "development", "postgresql://remote.example/production"),
        ("true", "development", "postgresql://127.0.0.1/local"),
    ],
)
def test_published_parkades_resolve_without_local_flags_or_duplicate_overlays(monkeypatch, flag, app_env, db):
    monkeypatch.setenv("CITYPROMPT_LOCAL_PARKADE_TRIAL", flag)
    monkeypatch.setattr("app.core.config.get_settings", lambda: SimpleNamespace(app_env=app_env, database_url=db))
    load_dims_table.cache_clear()
    try:
        parkades = [entry for entry in load_dims_table() if entry["id"].startswith("parkade-")]
        assert len(parkades) == 5
        assert len({entry["id"] for entry in parkades}) == 5
        for entry in parkades:
            assert entry["min_floors"] == entry["max_floors"]
            assert len(entry["variant_ids"]) == 1
    finally:
        load_dims_table.cache_clear()
