"""New cards must also be trusted by the compile endpoint's identity resolver."""
import json
from pathlib import Path

from app.services.lego_assembly import catalog_parent_archetype_id
from app.services.plan_geometry.archetypes import dims_by_id


def test_enrolled_final_five_have_trusted_parent_and_exact_variant():
    root=Path(__file__).resolve().parents[2]
    roster=json.loads((root/'frontend/src/data/finalFiveBuildingBatch.json').read_text(encoding='utf-8'))['entries']
    assert len(roster)==5
    for row in roster:
        assert catalog_parent_archetype_id(row['variant_id'])==row['archetype_id']
        parent=dims_by_id()[row['archetype_id']]
        assert parent['variant_ids']==[row['variant_id']]
        assert parent['min_floors']==parent['max_floors']
