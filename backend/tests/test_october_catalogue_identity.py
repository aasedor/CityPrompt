"""A frontend selection must survive the backend's exact identity guard."""
import json
from pathlib import Path

from app.services.lego_assembly import catalog_parent_archetype_id
from app.services.lego_assembly import AssemblyRequest, AssemblyPlanningError, descriptor_from_library_entry, plan_vertical_assembly
from app.api.v1.lego_assembly import _strict_locked_building_plan
from types import SimpleNamespace
from dataclasses import replace
import pytest


def test_installed_october_models_have_trusted_exact_identities():
    root = Path(__file__).resolve().parents[2]
    roster = json.loads((root/'frontend/src/data/catalogueOctober2026.json').read_text())['entries']
    installed = json.loads((root/'seed/model-library/rlasm-architectural-clay/library.json').read_text())['entries']
    active = {(e['archetype_id'], e['variant_id']) for e in installed}
    for item in roster:
        parent, variant = item['archetype_id'], item['variant_id']
        if (parent, variant) in active:
            assert catalog_parent_archetype_id(variant) == parent
    assert catalog_parent_archetype_id('not_a_catalogue_building') is None


def test_revised_model_cannot_compile_to_older_bytes_of_the_same_variant(monkeypatch):
    root = Path(__file__).resolve().parents[2]
    monkeypatch.syspath_prepend(str(root))
    from tools.rlasm_clay_library import clay_seed_rows
    library = json.loads((root/'seed/model-library/rlasm-architectural-clay/library.json').read_text())
    library['entries'] = [e for e in library['entries'] if e['variant_id'] == 'corten_timber_equipment_yard']
    row = next(clay_seed_rows(library))
    row['metadata_'] = row.pop('metadata')
    current = descriptor_from_library_entry(SimpleNamespace(**row))
    assert current.model_revision == 'contractor-storage-yard-clay-v003'
    old = replace(current, id='old', model_revision='contractor-storage-yard-clay-v002', model_url='/old.glb')
    request = AssemblyRequest(42,34,1,archetype_id=current.source_variant_id,model_revision=current.model_revision)
    for modules in ([old,current],[current,old]):
        plan = plan_vertical_assembly(modules,request)
        assert plan['instances'][0]['model_url'] == current.model_url
        locked = _strict_locked_building_plan(modules,current.source_variant_id,(42,34,1,'rectangle',None),{'pick_place_model_revision':current.model_revision})
        assert locked['instances'][0]['model_url'] == current.model_url
    with pytest.raises(AssemblyPlanningError,match='revision is not installed'):
        plan_vertical_assembly([old],request)
