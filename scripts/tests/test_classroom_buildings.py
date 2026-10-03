import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'backend'))
from scripts.classroom_buildings import load_selection, catalogue_records
from tools.rlasm_clay_library import clay_seed_rows
from app.services.lego_assembly import descriptor_from_library_entry, plan_vertical_assembly, AssemblyRequest, AssemblyPlanningError

PAYLOAD=load_selection(hydrated=False)
ROWS=list(clay_seed_rows(PAYLOAD))
DESCRIPTORS=[descriptor_from_library_entry(SimpleNamespace(id=r['id'],name=r['name'],model_url=r['model_url'],metadata_=r['metadata'])) for r in ROWS]


@pytest.mark.parametrize('index',range(8))
@pytest.mark.parametrize('larger',[False,True])
def test_exact_classroom_model_compiles_once_at_native_scale(index,larger):
    entry=PAYLOAD['entries'][index]
    _,assets=catalogue_records(PAYLOAD)
    asset=assets[index]
    plan=plan_vertical_assembly(DESCRIPTORS,AssemblyRequest(target_width_m=asset['width']+(20 if larger else 0),
        target_depth_m=asset['depth']+(20 if larger else 0),target_floors=entry['native_floors'],archetype_id=entry['variant_id']),allow_forced_fit=False)
    assert plan['family']==entry['family']
    assert len(plan['instances'])==1
    assert plan['instances'][0]['scale']==[1,1,1]
    assert plan['instances'][0]['model_url']==ROWS[index]['model_url']


@pytest.mark.parametrize('index',range(8))
def test_undersized_plot_does_not_shrink_or_substitute(index):
    entry=PAYLOAD['entries'][index]
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly(DESCRIPTORS,AssemblyRequest(target_width_m=2,target_depth_m=2,
            target_floors=entry['native_floors'],archetype_id=entry['variant_id']),allow_forced_fit=False)
