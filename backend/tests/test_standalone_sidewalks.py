"""Standalone sidewalks retain fixed pedestrian widths and exact recipe locks."""

import json
import importlib.util
from pathlib import Path
import pytest
from app.services.public_realm_lego import (
    PublicRealmPlanRequest,
    StreetSegmentTarget,
    plan_public_realm_recipe,
    PublicRealmPlanningError,
    public_realm_recipe_identity,
)

DATA = Path(__file__).resolve().parents[1] / "app/data/nativeStreetPilots.json"
EXPECTED = {
    "standalone_narrow_sidewalk_v1": 1.5,
    "standalone_neighbourhood_sidewalk_v1": 2.0,
    "standalone_urban_sidewalk_v1": 3.0,
}


def test_three_exact_standalone_sidewalks_are_installed():
    rows = {r["id"]: r for r in json.loads(DATA.read_text(encoding="utf-8"))}
    assert EXPECTED.keys() <= rows.keys()


@pytest.mark.parametrize("key,width", EXPECTED.items())
def test_sidewalk_recipe_roundtrip_and_bounds(key, width):
    rows = {r["id"]: r for r in json.loads(DATA.read_text(encoding="utf-8"))}
    assert key in rows
    row = rows[key]
    assert row["widthM"] == width
    assert row["placements"] == [] and row["modules"] == {} and row["treeWells"] == []
    assert row["program"]["adapter"] == "narrow-pathway-v1"
    assert row["program"]["preparedLevelOnly"] is True
    assert row["program"]["minLengthM"] == max(2, width)
    for length in [max(2, width), 35, 300, 2000]:
        recipe = plan_public_realm_recipe(
            PublicRealmPlanRequest(
                archetype_id=row["sourceArchetypeId"],
                variant_id=key,
                target=StreetSegmentTarget(row_width_m=width, length_m=length),
            )
        )
        assert public_realm_recipe_identity(recipe) is not None
        assert recipe.variant_id == key
        assert f"program:{row['programSha256']}" in recipe.component_set_ids
    for wrong_width, length in [(width + 0.1, 35), (width, max(2, width) - 0.1), (width, 2001)]:
        with pytest.raises(PublicRealmPlanningError):
            plan_public_realm_recipe(
                PublicRealmPlanRequest(
                    archetype_id=row["sourceArchetypeId"],
                    variant_id=key,
                    target=StreetSegmentTarget(row_width_m=wrong_width, length_m=length),
                )
            )


def test_generator_splices_without_reserializing_old_entries():
    generator_path = DATA.parents[3] / "tools/public_realm_assets/build_standalone_sidewalks.py"
    spec = importlib.util.spec_from_file_location("sidewalk_generator", generator_path)
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    original = '[\n  {"id":"kept", "hash" : "old", "thumbnailUrl":"under_score.png"}\n]\n'
    updated = generator.append_json(original, [{"id": "added"}])
    assert original[:-2] in updated
    assert json.loads(updated) == [json.loads(original)[0], {"id": "added"}]
    assert generator.append_json(original, []) == original
    roster = '{"entries": [{"id":"kept"}], "metadata":{"future":true}}'
    updated_roster = generator.append_json(roster, [{"id": "added"}], "entries")
    assert '{"id":"kept"}' in updated_roster
    assert json.loads(updated_roster)["metadata"] == {"future": True}


def test_generator_install_is_idempotent_and_rejects_changed_revisions(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "sidewalk_generator", DATA.parents[3] / "tools/public_realm_assets/build_standalone_sidewalks.py"
    )
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    monkeypatch.setattr(generator, "FRONT", tmp_path / "frontend/src/data")
    monkeypatch.setattr(generator, "BACK", tmp_path / "backend/app/data")
    row = next(r for r in json.loads(DATA.read_text(encoding="utf-8")) if r["id"] in EXPECTED)
    for root in (generator.FRONT, generator.BACK):
        generator.write(root / "nativeStreetPilots.json", [{"id": "old", "programSha256": "unchanged"}])
        generator.write(root / "classroomStarter.json", {"entries": []})
    generator.write(
        generator.BACK / "publicRealmCatalogHistory.json", {"catalogs": {"historic": {"old@1": "unchanged"}}}
    )
    generator.install([row], tmp_path / "output")
    paths = [
        root / name
        for root in (generator.FRONT, generator.BACK)
        for name in ("nativeStreetPilots.json", "classroomStarter.json")
    ]
    paths.append(generator.BACK / "publicRealmCatalogHistory.json")
    first = {p: p.read_bytes() for p in paths}
    generator.install([row], tmp_path / "output")
    assert {p: p.read_bytes() for p in paths} == first
    assert json.loads(paths[-1].read_text())["catalogs"]["historic"] == {"old@1": "unchanged"}
    changed = {**row, "sourceRecipeSha256": "0" * 64}
    with pytest.raises(ValueError, match="cannot be overwritten"):
        generator.install([changed], tmp_path / "output")
    assert {p: p.read_bytes() for p in paths} == first
