"""Local authored programmes stay private and repeatable for each account."""
import copy
import importlib
from pathlib import Path
from types import SimpleNamespace
import sys
import uuid

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
LEGACY_ID = uuid.UUID('c0ad2705-d532-52f5-9540-bc91bd5be152')
LEGACY_OWNER = uuid.UUID('e57f4f05-21e2-44d3-b467-cf8462f34824')
QA_OWNER = uuid.UUID('c40773d4-7771-4f8d-9535-b8cb364f87c3')
QA_PRIVATE_ID = uuid.UUID('9a4e2ec8-a7c6-5830-b511-83da5497507a')


@pytest.fixture(params=['brick', 'regular', 'landmark'])
def local_installer(request, monkeypatch, tmp_path):
    """Exercise each real synchronizer against in-memory local service boundaries."""
    from app.core import config
    from app.models.models import User
    from app.services import render_attempt_storage
    from scripts import classroom_model_library
    import sqlalchemy
    import sqlalchemy.orm

    row = dict(id=str(LEGACY_ID), name='private authored tower', variantId='test_tower',
        model_url='/api/v1/files/library/immutable-tower.glb', source_sha256='a' * 64,
        metadata={'lego': {'native_floors': 25}, 'rlasm': {'model_sha256': 'a' * 64}})
    module = dict(role='floor', sha256='a' * 64)
    entries = {}

    class LocalDatabase:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def get(self, model, key):
            return SimpleNamespace(is_active=True) if model is User else entries.get(key)
        def execute(self, statement):
            return SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: []))
        def commit(self): raise AssertionError('Dry-run must not commit')
        def add(self, entry): raise AssertionError('Dry-run must not insert')

    settings = SimpleNamespace(database_url='postgresql://localhost/test',
        database_url_sync='postgresql://localhost/test', s3_endpoint_url='http://127.0.0.1:9000')
    monkeypatch.setattr(config, 'get_settings', lambda: settings)
    monkeypatch.setattr(sqlalchemy, 'create_engine', lambda value: SimpleNamespace(dispose=lambda: None))
    monkeypatch.setattr(sqlalchemy.orm, 'Session', lambda engine: LocalDatabase())
    monkeypatch.setattr(render_attempt_storage, '_client', lambda: (object(), 'test'))
    monkeypatch.setattr(classroom_model_library, 'object_matches', lambda *args: 'verified')

    if request.param == 'landmark':
        installer = importlib.import_module('scripts.landmark_tower_storeys')
        monkeypatch.setattr(installer, 'load_completed_programme', lambda *args: ([], [copy.deepcopy(row)]))
        run = lambda owner: installer.synchronize_private('twisted', tmp_path, owner_id=owner)
    else:
        name = 'brick_podium_storeys' if request.param == 'brick' else 'regular_tower_storeys'
        installer = importlib.import_module('scripts.' + name)
        monkeypatch.setattr(installer, 'load_program', lambda *args: ({'modules': [module]}, [copy.deepcopy(row)]))
        run = (lambda owner: installer.synchronize(tmp_path, owner_id=owner)) if request.param == 'brick' else (
            lambda owner: installer.synchronize('blue', tmp_path, owner_id=owner))

    def existing(owner, entry_id=LEGACY_ID, **changes):
        entry = SimpleNamespace(id=entry_id, owner_id=owner, is_public=False, name=row['name'],
            category='building', generation_engine='rlasm', model_url=row['model_url'],
            lod_urls={'0': row['model_url']}, tags=['local-student-review', row['variantId']],
            metadata_=copy.deepcopy(row['metadata']))
        for key, value in changes.items(): setattr(entry, key, value)
        entries[entry_id] = entry
        return entry

    return SimpleNamespace(run=run, existing=existing, entries=entries, row=row, settings=settings)


def test_another_accounts_legacy_row_gets_a_distinct_private_id(local_installer):
    state = local_installer
    legacy = state.existing(LEGACY_OWNER)
    before = copy.deepcopy(vars(legacy))
    report = state.run(QA_OWNER)
    assert report[0]['id'] == str(QA_PRIVATE_ID)
    assert report[0]['binding'] == 'missing'
    assert report[0]['object'] == 'verified'
    assert vars(legacy) == before
    assert list(state.entries) == [LEGACY_ID]


def test_existing_owner_retains_the_legacy_id(local_installer):
    state = local_installer
    state.existing(LEGACY_OWNER)
    report = state.run(LEGACY_OWNER)
    assert report[0]['id'] == str(LEGACY_ID)
    assert report[0]['binding'] == 'verified'


def test_fresh_account_uses_stable_id_with_or_without_legacy_collision(local_installer):
    state = local_installer
    assert state.run(QA_OWNER)[0]['id'] == str(QA_PRIVATE_ID)
    state.existing(LEGACY_OWNER)
    state.existing(QA_OWNER, QA_PRIVATE_ID)
    report = state.run(QA_OWNER)
    assert report[0]['id'] == str(QA_PRIVATE_ID)
    assert report[0]['binding'] == 'verified'


@pytest.mark.parametrize('changes', [
    {'is_public': True}, {'metadata_': {}}, {'model_url': '/other.glb'}, {'owner_id': LEGACY_OWNER},
])
def test_selected_private_identity_still_refuses_binding_drift(local_installer, changes):
    state = local_installer
    state.existing(LEGACY_OWNER)
    selected = state.existing(QA_OWNER, QA_PRIVATE_ID, **changes)
    before = copy.deepcopy(vars(selected))
    with pytest.raises(ValueError, match='differs'):
        state.run(QA_OWNER)
    assert vars(selected) == before


@pytest.mark.parametrize('changes', [{'is_public': True}, {'metadata_': {}}, {'model_url': '/other.glb'}])
def test_owned_legacy_identity_still_refuses_binding_drift(local_installer, changes):
    state = local_installer
    selected = state.existing(LEGACY_OWNER, **changes)
    before = copy.deepcopy(vars(selected))
    with pytest.raises(ValueError, match='differs'):
        state.run(LEGACY_OWNER)
    assert vars(selected) == before


def test_owner_uuid_normalization_and_different_module_namespaces():
    from scripts.private_local_pilot_ids import private_local_pilot_id
    assert private_local_pilot_id(str(LEGACY_ID).upper(), str(QA_OWNER).upper()) == QA_PRIVATE_ID
    assert private_local_pilot_id(LEGACY_ID, QA_OWNER, str(QA_OWNER).upper()) == LEGACY_ID
    assert private_local_pilot_id(LEGACY_ID, LEGACY_OWNER) == uuid.UUID('eb38302b-a3fc-5a24-abb2-bf8ed8121d99')
    assert private_local_pilot_id(uuid.UUID('66c52f37-5ce2-5cd8-a635-623a36eb4e88'), QA_OWNER) != QA_PRIVATE_ID


@pytest.mark.parametrize('target', ['database_url', 's3_endpoint_url'])
def test_private_account_ids_do_not_relax_loopback_gate(local_installer, target):
    state = local_installer
    setattr(state.settings, target, 'https://example.com/remote')
    with pytest.raises(ValueError, match='loopback'):
        state.run(QA_OWNER)
    assert state.entries == {}
