from types import SimpleNamespace
import pytest
from app.services.plan_geometry.archetypes import load_dims_table


@pytest.mark.parametrize('flag,app_env,db,enabled',[
    ('','development','postgresql://localhost/local',False),
    ('true','production','postgresql://localhost/local',False),
    ('true','development','postgresql://remote.example/production',False),
    ('true','development','postgresql://127.0.0.1/local',True),
])
def test_parkade_metadata_is_opt_in_and_local_only(monkeypatch,flag,app_env,db,enabled):
    monkeypatch.setenv('CITYPROMPT_LOCAL_PARKADE_TRIAL',flag)
    monkeypatch.setattr('app.core.config.get_settings',lambda:SimpleNamespace(app_env=app_env,database_url=db))
    load_dims_table.cache_clear()
    try:
        parkades=[entry for entry in load_dims_table() if entry['id'].startswith('parkade-')]
        assert len(parkades)==(5 if enabled else 0)
    finally:load_dims_table.cache_clear()
