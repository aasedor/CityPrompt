"""Changed sources and unsupported coverage claims cannot silently pass."""
import json
from pathlib import Path
import shutil
import pytest
from tools.catalogue_coverage_five.plan import SPECS,source_entry

ROOT=Path(__file__).resolve().parents[3]

@pytest.fixture
def locked(tmp_path):
    rel=Path('frontend/public/archetypes/buildings')/SPECS['maple']['slug']
    shutil.copytree(ROOT/rel,tmp_path/rel)
    return tmp_path,tmp_path/rel

def test_exact_sources_and_distinct_roles(locked):
    root,_=locked
    entry=source_entry('maple',root)
    assert {s['role'] for s in entry['sources']}=={'front','oblique','top'}
    assert len({s['sha256'] for s in entry['sources']})==3

def test_changed_source_is_rejected(locked):
    root,folder=locked;p=folder/'variant_0.png';p.write_bytes(p.read_bytes()+b'changed')
    with pytest.raises(ValueError,match='reference changed'):source_entry('maple',root)

def test_lfs_pointer_is_rejected(locked):
    root,folder=locked;(folder/'variant_0.png').write_text('version https://git-lfs.github.com/spec/v1\n')
    with pytest.raises(ValueError,match='Unhydrated'):source_entry('maple',root)

def test_unenrolled_view_cannot_inherit_review(locked):
    root,folder=locked;shutil.copy2(folder/'variant_0.png',folder/'variant_0_rear.png')
    with pytest.raises(ValueError,match='Additional reference'):source_entry('maple',root)

def test_missing_role_fails(locked):
    root,folder=locked;p=folder/'generation-provenance.json';j=json.loads(p.read_text());j['records']=j['records'][:2];p.write_text(json.dumps(j))
    with pytest.raises(ValueError,match='Three compatible'):source_entry('maple',root)

def test_delivery_remains_bounded_and_not_approved():
    assert len(SPECS)==5
    for s in SPECS.values():
        assert not s['zoning_research']['approval']
        assert not s['lifecycle']['runtime_enabled']
        assert s['storey_program']['minimum']==s['storey_program']['maximum']==s['storeys']
    for key in ('maple','horizon'):
        assert 'chassis' in SPECS[key]['program']
        assert SPECS[key]['dimensions_m']['height']<5

def test_office_does_not_lose_small_use_area_design():
    s=SPECS['office'];d=s['dimensions_m']
    assert d['width']==14 and d['depth']==12
    assert 2*(2*3.5*12+7*4)<300

def test_distinct_fixed_ids_do_not_overwrite_catalogue():
    a=json.loads((ROOT/'frontend/src/data/buildingArchetypes.json').read_text(encoding='utf-8'))
    existing={x['id'] for x in a['archetypes']}
    assert len({s['id'] for s in SPECS.values()})==5
    assert not existing.intersection(s['id'] for s in SPECS.values())
