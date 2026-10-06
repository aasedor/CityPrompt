"""Reference mutation and inferred-use metadata must fail safely."""
import json
from pathlib import Path
import shutil

import pytest

from tools.catalogue_original_five.plan import SPECS, source_entry


ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def home_sources(tmp_path):
    relative = Path('frontend/public/archetypes/buildings') / SPECS['home']['slug']
    shutil.copytree(ROOT / relative, tmp_path / relative)
    return tmp_path, tmp_path / relative


def test_original_reference_chain_is_distinct_and_complete(home_sources):
    root, _ = home_sources
    entry = source_entry('home', root)
    assert entry['source_origin'] == 'original_generated_design'
    assert {s['role'] for s in entry['sources']} == {'front', 'oblique', 'top'}
    assert len({s['sha256'] for s in entry['sources']}) == 3


def test_changed_reference_cannot_inherit_source_approval(home_sources):
    root, folder = home_sources
    path = folder / 'variant_0.png'
    path.write_bytes(path.read_bytes() + b'changed')
    with pytest.raises(ValueError, match='reference changed'):
        source_entry('home', root)


def test_relative_source_root_resolves_for_blender_image_loader(home_sources, monkeypatch):
    root, _ = home_sources
    monkeypatch.chdir(root)
    entry = source_entry('home', Path('.'))
    assert all(Path(s['original_path']).is_absolute() for s in entry['sources'])
    assert all(Path(s['original_path']).is_file() for s in entry['sources'])


def test_unhydrated_reference_fails(home_sources):
    root, folder = home_sources
    (folder / 'variant_0.png').write_text('version https://git-lfs.github.com/spec/v1\n')
    with pytest.raises(ValueError, match='Unhydrated'):
        source_entry('home', root)


def test_missing_role_or_unreviewed_extra_fails(home_sources):
    root, folder = home_sources
    shutil.copy2(folder / 'variant_0.png', folder / 'variant_0_rear.png')
    with pytest.raises(ValueError, match='Additional reference'):
        source_entry('home', root)


def test_new_programmes_do_not_claim_zoning_or_runtime_approval():
    assert len(SPECS) == 5
    catalogue = json.loads((ROOT / 'frontend/src/data/buildingArchetypes.json').read_text(encoding='utf-8'))
    existing = {a['id'] for a in catalogue['archetypes']}
    for spec in SPECS.values():
        assert spec['id'] not in existing
        assert spec['zoning_research']['approval'] is False
        assert spec['lifecycle']['runtime_enabled'] is False
        assert spec['storey_program']['minimum'] == spec['storey_program']['maximum']
        for route in spec['zoning_research']['district_candidates']:
            assert route['url'].startswith('https://www.calgary.ca/')


def test_operating_conditions_are_not_lost():
    assert 'chassis' in SPECS['home']['program']
    assert 'Municipally operated' in SPECS['depot']['program']
    assert 'all operations indoors' in SPECS['recovery']['program']
    assert 'ancillary' in SPECS['yard']['program']
    assert SPECS['childcare']['capacity_assumption']['children'] == 30
