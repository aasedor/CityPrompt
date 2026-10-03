"""The three reviewed buildings must compile as exact intact native models."""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from scripts.showcase_buildings import selection
from scripts.classroom_buildings import catalogue_records
from tools.rlasm_clay_library import clay_seed_rows
from app.services.lego_assembly import descriptor_from_library_entry,plan_vertical_assembly,AssemblyRequest,AssemblyPlanningError


@pytest.fixture(scope='module')
def package():
    payload=selection(hydrated=False)
    rows=list(clay_seed_rows(payload))
    descriptors=[descriptor_from_library_entry(SimpleNamespace(id=r['id'],name=r['name'],model_url=r['model_url'],metadata_=r['metadata'])) for r in rows]
    _,assets=catalogue_records(payload)
    return payload,rows,descriptors,assets


@pytest.mark.parametrize('index',range(3))
@pytest.mark.parametrize('margin',[0,20])
def test_showcase_model_keeps_exact_identity_and_scale(package,index,margin):
    payload,rows,descriptors,assets=package;entry=payload['entries'][index];asset=assets[index]
    plan=plan_vertical_assembly(descriptors,AssemblyRequest(target_width_m=asset['width']+margin,
        target_depth_m=asset['depth']+margin,target_floors=entry['native_floors'],archetype_id=entry['variant_id']),allow_forced_fit=False)
    assert plan['family']==entry['family']
    assert len(plan['instances'])==1
    assert plan['instances'][0]['model_url']==rows[index]['model_url']
    assert plan['instances'][0]['scale']==[1,1,1]


@pytest.mark.parametrize('index',range(3))
def test_insufficient_plot_never_squashes_or_substitutes_showcase(package,index):
    payload,_,descriptors,_=package;entry=payload['entries'][index]
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly(descriptors,AssemblyRequest(target_width_m=2,target_depth_m=2,
            target_floors=entry['native_floors'],archetype_id=entry['variant_id']),allow_forced_fit=False)
