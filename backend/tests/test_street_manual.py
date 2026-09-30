import json
from pathlib import Path
import pytest
from app.services.public_realm_lego import (PublicRealmPlanRequest, StreetSegmentTarget,
    plan_public_realm_recipe, public_realm_recipe_identity, PublicRealmPlanningError)

MANIFEST = Path(__file__).resolve().parents[1] / 'app/data/streetManual.json'
ROWS = json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manual_mirror_and_thirteen_distinct_sections():
    assert MANIFEST.read_bytes() == (MANIFEST.parents[3] / 'frontend/src/data/streetManual.json').read_bytes()
    assert len(ROWS) == 13
    assert {int(r['figure']) for r in ROWS} == set(range(1, 14))


@pytest.mark.parametrize('row', ROWS, ids=lambda r:r['archetypeId'])
def test_manual_compiles_and_reopens_exact_section(row):
    request = PublicRealmPlanRequest(archetype_id=row['archetypeId'], variant_id=row['variantId'],
        target=StreetSegmentTarget(row_width_m=row['widthM'], length_m=180))
    recipe = plan_public_realm_recipe(request)
    assert recipe.family_id == row['familyId']
    assert recipe.component_set_ids == (f"manual_section:{row['sourceSectionSha256']}", 'manual_streets_v1')
    saved = json.loads(recipe.model_dump_json())
    assert public_realm_recipe_identity(saved) is not None
    saved['component_set_ids'][0] = 'manual_section:' + '0'*64
    assert public_realm_recipe_identity(saved) is None
    with pytest.raises(PublicRealmPlanningError):
        plan_public_realm_recipe(request.model_copy(update={'target':StreetSegmentTarget(row_width_m=row['widthM']+1, length_m=180)}))
