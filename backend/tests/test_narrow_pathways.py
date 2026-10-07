"""Small pathways must compile without weakening existing street contracts."""
import copy
import json
from pathlib import Path
import pytest
from app.services.native_street_candidate_contract import build_native_street_candidate_catalog
from app.services.public_realm_lego import (
    PublicRealmPlanRequest, StreetSegmentTarget, plan_public_realm_recipe,
    public_realm_recipe_identity, PublicRealmPlanningError,
)

DATA = Path(__file__).resolve().parents[1] / 'app/data/nativeStreetPilots.json'
PATHS = [row for row in json.loads(DATA.read_text(encoding='utf-8'))
         if row.get('program', {}).get('adapter') == 'narrow-pathway-v1']

@pytest.mark.parametrize('row', PATHS, ids=lambda row: row['id'])
def test_pathway_recipe_roundtrip_and_width_lock(row):
    for length in [2, 35, 300]:
        recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id=row['sourceArchetypeId'], variant_id=row['id'],
            target=StreetSegmentTarget(row_width_m=row['widthM'], length_m=length)))
        assert public_realm_recipe_identity(recipe) is not None
        assert recipe.variant_id == row['id']
        assert recipe.target.row_width_m == row['widthM']
        assert f"program:{row['programSha256']}" in recipe.component_set_ids
    for width,length in [(5,35),(row['widthM'],1),(row['widthM'],301)]:
        with pytest.raises(PublicRealmPlanningError):
            plan_public_realm_recipe(PublicRealmPlanRequest(
                archetype_id=row['sourceArchetypeId'],variant_id=row['id'],
                target=StreetSegmentTarget(row_width_m=width,length_m=length)))

@pytest.mark.parametrize('mutation', ['unknown_id','wrong_width','missing_module','changed_program'])
def test_surface_only_exception_is_finite_and_hash_locked(tmp_path, mutation):
    rows=json.loads(DATA.read_text(encoding='utf-8'))
    row=copy.deepcopy(PATHS[0])
    if mutation=='unknown_id': row['id']='invented_path_v1'
    elif mutation=='wrong_width': row['widthM']=1.2
    elif mutation=='changed_program': row['program']['baseLiftM']=3
    else:
        row=copy.deepcopy(rows[0]);row['modules']={}
    manifest=tmp_path/'manifest.json'
    manifest.write_text(json.dumps([row]),encoding='utf-8')
    with pytest.raises(ValueError): build_native_street_candidate_catalog(manifest)

def test_five_exact_pathway_choices():
    assert len(PATHS)==5
    assert sorted(p['widthM'] for p in PATHS)==[1.5,1.8,2,2,3]
