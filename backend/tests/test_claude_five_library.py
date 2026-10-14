import hashlib
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import uuid
import pytest
sys.path.insert(0, str(Path(__file__).parents[2]))
from scripts import claude_five_library as trial
from tools.catalogue_promotion import TRIAL_CHECKS
from app.services.lego_assembly import descriptor_from_library_entry


def test_held_candidates_cannot_enter_trial(tmp_path):
    payload = json.loads(trial.MANIFEST.read_text())
    payload['entries'][0]['candidate'] = 'clay-grand-magasin-clay-v004'
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='Only independently reviewed Claude'):
        trial.load_bindings(tmp_path, manifest=manifest)


def test_every_packaged_delivery_is_accepted_by_runtime():
    artifacts = os.getenv('CITYPROMPT_CLAUDE_FIVE_ARTIFACTS')
    artifact_root = Path(artifacts) if artifacts else None
    payload = json.loads(trial.MANIFEST.read_text())
    roster, rows = trial.load_bindings(artifact_root)
    assert len(rows) == len(payload['entries'])
    assert len(roster['dependencies']) == len(rows)
    for row, source in zip(rows, payload['entries']):
        entry = SimpleNamespace(id=uuid.UUID(row['id']), name=row['name'], model_url=row['model_url'], metadata_=row['metadata'])
        module = descriptor_from_library_entry(entry)
        assert module is not None
        assert module.source_variant_id == source['variant_id']
        assert row['metadata']['rlasm']['model_sha256'] == source['model']['sha256']
        assert row['metadata']['rlasm']['import_scope'] == 'local_trial_only'
        assert row['metadata']['rlasm']['source_delivery'] == source['source']


@pytest.fixture
def trial_package(tmp_path):
    """Real minimal GLB and hash-bound reviews; no DB, network, or external assets."""
    import trimesh
    from tools.rlasm_clay_library import _glb_counts
    repo = tmp_path / 'repo'
    package = repo / 'seed/claude-five-trial'
    package.mkdir(parents=True)
    payload = json.loads(trial.MANIFEST.read_text())
    payload['entries'] = payload['entries'][:1]
    entry = payload['entries'][0]
    entry['local_trial_only'] = True
    entry['activation'] = {}
    entry['local_trial'] = {}
    filename = entry['candidate'] + '.glb'
    model = repo / 'seed/model-library/objects/claude-five/models' / filename
    model.parent.mkdir(parents=True)
    model.write_bytes(trimesh.creation.box(extents=(78, 42.4, 72)).export(file_type='glb'))
    entry['model']['path'] = '../model-library/objects/claude-five/models/' + filename
    entry['model']['sha256'] = hashlib.sha256(model.read_bytes()).hexdigest()
    entry['model']['bytes'] = model.stat().st_size
    entry['model']['native_dimensions_m'] = dict(width=78, height=42.400001525878906, depth=72)
    counts = _glb_counts(model)
    for key, value in counts.items():
        entry['model'][dict(meshes='mesh_count', materials='material_count', textures='texture_count', images='image_count')[key]] = value
    for reference in entry['references']:
        source = repo / reference['repo_path']
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b'locked source fixture ' + reference['role'].encode())
        reference['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        reference['bytes'] = source.stat().st_size
    review = repo / entry['review']['repo_path']
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(json.dumps(dict(candidate=entry['candidate'], model_sha256=entry['model']['sha256'],
        reviewer='Independent fixture reviewer', architectural_clay_pass=True, holistic_review_performed=True,
        unresolved_p0=0, unresolved_p1=0, inspected_files=entry['references'])))
    entry['review']['sha256'] = hashlib.sha256(review.read_bytes()).hexdigest()
    manifest = package / 'library.json'
    manifest.write_text(json.dumps(payload))
    return SimpleNamespace(repo=repo, package=package, payload=payload, manifest=manifest, model=model, review=review)


def test_completed_release_remains_installable_locally(trial_package):
    p = trial_package
    entry = p.payload['entries'][0]
    entry['local_trial_only'] = False
    entry['activation'] = dict(authorized_by='human_user', quote='Prepare this exact release',
                               date='2026-10-13', model_sha256=entry['model']['sha256'])
    entry['local_trial'] = dict(model_sha256=entry['model']['sha256'], project_url='http://localhost/projects/test',
                              tested_by='fixture', tested_at='2026-10-13', evidence=['fixture.json'],
                              checks=dict.fromkeys(TRIAL_CHECKS, True))
    p.manifest.write_text(json.dumps(p.payload))
    assert len(trial.load_bindings(manifest=p.manifest, repo=p.repo)[1]) == 1


@pytest.mark.parametrize('missing', ['approval', 'hash', 'trial_check'])
def test_release_state_requires_exact_activation_and_completed_trial(trial_package, missing):
    p = trial_package
    entry = p.payload['entries'][0]
    entry['local_trial_only'] = False
    entry['activation'] = dict(authorized_by='human_user', quote='Prepare this exact release',
                               date='2026-10-13', model_sha256=entry['model']['sha256'])
    entry['local_trial'] = dict(model_sha256=entry['model']['sha256'], project_url='http://localhost/projects/test',
                              tested_by='fixture', tested_at='2026-10-13', evidence=['fixture.json'],
                              checks=dict.fromkeys(TRIAL_CHECKS, True))
    if missing == 'approval': entry['activation'] = {}
    if missing == 'hash': entry['activation']['model_sha256'] = '0' * 64
    if missing == 'trial_check': entry['local_trial']['checks']['save_reload'] = False
    p.manifest.write_text(json.dumps(p.payload))
    with pytest.raises(ValueError, match='activation and completed local trial'):
        trial.load_bindings(manifest=p.manifest, repo=p.repo)


def test_durable_package_defaults_to_manifest_parent_without_metadata_drift(trial_package):
    p = trial_package
    roster, rows = trial.load_bindings(manifest=p.manifest, repo=p.repo)
    entry = p.payload['entries'][0]
    assert roster['dependencies'][0]['path'] == entry['model']['path']
    assert rows[0]['metadata']['rlasm']['source_delivery'] == entry['source']
    assert rows[0]['model_url'].endswith(p.model.name)


@pytest.mark.parametrize('failure', ['missing', 'pointer'])
def test_durable_package_reports_unhydrated_models(trial_package, failure):
    p = trial_package
    if failure == 'missing':
        p.model.unlink()
    else:
        p.model.write_bytes(b'version https://git-lfs.github.com/spec/v1\noid sha256:' + b'0' * 64 + b'\nsize 123\n')
    with pytest.raises(ValueError, match='(?i)git lfs pull'):
        trial.load_bindings(manifest=p.manifest, repo=p.repo)


@pytest.mark.parametrize('changed', ['model', 'review'])
def test_durable_package_rejects_changed_exact_bytes(trial_package, changed):
    p = trial_package
    file = getattr(p, changed)
    content = file.read_bytes()
    file.write_bytes(content[:-1] + bytes([content[-1] ^ 1]))
    with pytest.raises(ValueError, match='(?i)(hash mismatch|review bytes)'):
        trial.load_bindings(manifest=p.manifest, repo=p.repo)


def test_durable_package_rejects_arbitrary_parent_traversal(trial_package):
    p = trial_package
    p.payload['entries'][0]['model']['path'] = '../elsewhere/' + p.model.name
    p.manifest.write_text(json.dumps(p.payload))
    with pytest.raises(ValueError, match='(?i)(unsafe|approved|path)'):
        trial.load_bindings(manifest=p.manifest, repo=p.repo)


@pytest.mark.parametrize('layout', ['legacy', 'durable'])
def test_external_model_root_override_remains_supported(trial_package, tmp_path, layout):
    p = trial_package
    external = tmp_path / 'external'
    (external / 'models').mkdir(parents=True)
    (external / 'models' / p.model.name).write_bytes(p.model.read_bytes())
    if layout == 'legacy':
        p.payload['entries'][0]['model']['path'] = 'models/' + p.model.name
    p.manifest.write_text(json.dumps(p.payload))
    manifest_bytes = p.manifest.read_bytes()
    p.model.unlink()  # Only the explicit delivery may provide the validated/uploaded bytes.
    roster, rows = trial.load_bindings(external, manifest=p.manifest, repo=p.repo)
    assert len(rows) == 1
    assert roster['dependencies'][0]['path'] == 'models/' + p.model.name
    upload_path = external / roster['dependencies'][0]['path']
    assert hashlib.sha256(upload_path.read_bytes()).hexdigest() == p.payload['entries'][0]['model']['sha256']
    assert rows[0]['metadata']['rlasm']['source_delivery'] == p.payload['entries'][0]['source']
    assert p.manifest.read_bytes() == manifest_bytes


def test_package_check_default_is_read_only(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(sys, 'argv', ['claude_five_library.py'])
    monkeypatch.setattr(trial, 'load_bindings', lambda root: (calls.append(root) or {}, []))
    def reject_write(*args, **kwargs):
        raise AssertionError('Read-only package check must not synchronize DB/storage')
    monkeypatch.setattr(trial, 'synchronize', reject_write)
    trial.main()
    assert calls == [None]
    assert 'PASS: exact model bytes' in capsys.readouterr().out


def test_package_rejects_a_rehashed_failed_review(trial_package):
    p = trial_package
    review = json.loads(p.review.read_text())
    review['architectural_clay_pass'] = False
    review['unresolved_p1'] = 1
    p.review.write_text(json.dumps(review))
    p.payload['entries'][0]['review']['sha256'] = hashlib.sha256(p.review.read_bytes()).hexdigest()
    p.manifest.write_text(json.dumps(p.payload))
    with pytest.raises(ValueError, match='independent holistic pass'):
        trial.load_bindings(manifest=p.manifest, repo=p.repo)
