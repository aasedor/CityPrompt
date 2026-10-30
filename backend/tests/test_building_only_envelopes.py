"""A snug plot must compile the unchanged GLB at unit scale, never miniature it."""
import json
import math
from dataclasses import replace
from pathlib import Path

import pytest
from app.services.lego_assembly import AssemblyPlanningError, AssemblyRequest, ModuleDescriptor, plan_vertical_assembly
from app.services.model_contract import native_model_facts
from app.services.lego_assembly import catalog_parent_archetype_id

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = json.loads((ROOT/'frontend/src/features/legoAssembly/buildingOnlyContracts.json').read_text())


@pytest.mark.parametrize('member', json.loads((ROOT/'frontend/src/data/claudeBuildingRelease.json').read_text())['entries'])
def test_exact_claude_variant_is_trusted_for_community_compilation(member):
    assert catalog_parent_archetype_id(member['variant_id']) == member['archetype_id']


def test_packaged_backend_matches_exact_renderer_envelopes():
    packaged=json.loads((ROOT/'backend/app/data/buildingOnlyEnvelopes.json').read_text())
    assert packaged=={key:{'sourceSha256':v['sourceSha256'],'bounds':v['bounds']} for key,v in CONTRACTS.items()}


@pytest.mark.parametrize('revision,contract', CONTRACTS.items())
def test_report_native_facts_use_retained_architecture_not_removed_context(revision,contract):
    rows=json.loads((ROOT/'backend/app/data/native_model_contract.json').read_text())['records']
    row=next(x for x in rows if x['revision']==revision)
    props={'pick_place_asset':row['asset_id'],'development_selected_variant_id':row['variant_id'],
           'pick_place_model_revision':revision}
    lo,hi=contract['bounds']['min'],contract['bounds']['max']
    assert native_model_facts(props)['dimensions_m']==pytest.approx([hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]])


def fixture(revision, contract):
    lo, hi = contract['bounds']['min'], contract['bounds']['max']
    return ModuleDescriptor(id='exact-model', name=revision,
        model_url=f'/api/v1/files/library/rlasm-architectural-clay/{revision}.glb',
        family='building-only-test', role='assembled', width_m=hi[0]-lo[0]+20,
        depth_m=hi[2]-lo[2]+20, height_m=hi[1]-lo[1],
        archetype_ids=('registered_variant',), reuse_keys=(), native_floors=3,
        min_floors=3, max_floors=3, source_variant_id='registered_variant',
        delivery_format='architectural_clay', model_revision=revision)


@pytest.mark.parametrize('revision,contract', CONTRACTS.items())
def test_exact_building_fits_snug_plot_at_native_scale(revision, contract):
    module=fixture(revision,contract)
    lo,hi=contract['bounds']['min'],contract['bounds']['max']
    width,depth=hi[0]-lo[0],hi[2]-lo[2]
    request=AssemblyRequest(math.ceil((width+.02)*10)/10,math.ceil((depth+.02)*10)/10,3,
        archetype_id='registered_variant',model_revision=revision)
    result=plan_vertical_assembly([module],request,allow_forced_fit=False)
    instance=result['instances'][0]
    assert instance['scale']==[1.0,1.0,1.0]
    assert instance['model_url']==module.model_url
    assert instance['native_dimensions_m']==pytest.approx([width,depth,hi[1]-lo[1]])
    assert module.width_m==width+20  # Library descriptor remains immutable.
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly([module],replace(request,target_width_m=width/2,target_depth_m=depth/2))


def test_similarly_named_import_or_unknown_revision_keeps_full_original_envelope():
    revision,contract=next(iter(CONTRACTS.items()))
    module=fixture(revision,contract)
    request=AssemblyRequest(43.4,40.7,3,archetype_id='registered_variant')
    for other in (replace(module,model_url=f'/api/v1/files/imports/{revision}.glb'),
                  replace(module,model_revision='unknown-source'),
                  replace(module,role='podium')):
        with pytest.raises(AssemblyPlanningError):
            plan_vertical_assembly([other],request,allow_forced_fit=False)
