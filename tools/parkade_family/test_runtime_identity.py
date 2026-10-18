import json
from pathlib import Path
from .specs import DESIGNS
ROOT=Path(__file__).resolve().parents[2]


def test_each_original_design_has_one_trusted_backend_variant():
    table=json.loads((ROOT/'backend/app/data/parkade_trial_dims.json').read_text())['archetypes']
    for key,brief in DESIGNS.items():
        found=[row for row in table if row['id']==brief['slug']]
        assert len(found)==1,key
        row=found[0]
        assert row['variant_ids']==['classic-concrete-v1' if key=='classic' else key+'-v1']
        assert row['min_floors']==row['max_floors']==brief['levels']
        assert row['suggested_w_m']>=brief['dimensions'][0]+3
        assert row['suggested_d_m']>=brief['dimensions'][1]+3
