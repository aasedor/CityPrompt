import json
from pathlib import Path
from .specs import DESIGNS
ROOT=Path(__file__).resolve().parents[2]


def test_each_original_design_has_one_trusted_backend_variant():
    table=json.loads((ROOT/'backend/app/data/archetype_plan_dims.json').read_text())['archetypes']
    for key,brief in DESIGNS.items():
        found=[row for row in table if row['id']==brief['slug']]
        assert len(found)==1,key
        row=found[0]
        assert row['variant_ids']==['classic-concrete-v1' if key=='classic' else key+'-v1']
        assert row['min_floors']==row['max_floors']==brief['levels']
        assert row['suggested_w_m']>=brief['dimensions'][0]+3
        assert row['suggested_d_m']>=brief['dimensions'][1]+3


def test_finite_release_is_the_exact_canonical_five_with_real_activation():
    base=ROOT/'seed/model-library/rlasm-architectural-clay'
    published=json.loads((base/'library.json').read_text(encoding='utf-8'))
    finite=json.loads((base/'parkades-release-v001.json').read_text(encoding='utf-8'))
    trial=json.loads((ROOT/'seed/parkade-family-trial/library.json').read_text(encoding='utf-8'))
    expected=[entry for entry in published['entries'] if entry['archetype_id'] in {b['slug'] for b in DESIGNS.values()}]
    assert len(expected)==5
    assert finite['entries']==expected
    for entry in expected:
        original=next(e for e in trial['entries'] if e['candidate']==entry['candidate'])
        assert entry['model']['sha256']==original['model']['sha256']
        assert entry['review']==original['review']
        assert entry['picker']['id']==original['picker']['id']
        assert entry['native_floors']==original['native_floors']
        assert entry['runtime_enabled'] and not entry['local_trial_only']
        assert entry['activation']['authorized_by']=='human_user'
        assert entry['activation']['model_sha256']==entry['model']['sha256']
