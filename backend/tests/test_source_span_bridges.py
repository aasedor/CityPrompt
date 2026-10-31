"""Source-only spans use trusted finite programmes, not generic at-grade streets."""

import copy
import hashlib
import json
import pytest
from pathlib import Path

from app.services.native_modular_bridge import validate_modular_bridge_profile
from app.services.native_source_bridge import SOURCE_BRIDGE_SOURCES
from app.services.native_specialist_streets import validate_specialist_properties
from app.services.native_modular_bridge import modular_bridge_profile


def row():
    variant = "planted_green_bridge_route_v1"
    program = {
        "adapter": "source-span-bridge-v1",
        "minLengthM": 101,
        "maxLengthM": 277,
        "bridge": {
            "approachM": 10.5,
            "endM": 6,
            "deckHeightM": 6,
            "clearWidthM": 4.6,
            "trafficKind": "walk",
            "parts": [
                {"kind": "end", "lengthM": 20, "mode": "fixed"},
                {
                    "kind": "span",
                    "lengthM": 81,
                    "mode": "span",
                    "companions": [{"kind": "plants", "pitchM": 22, "lengthM": 22}],
                },
            ],
        },
        "surfaceRegions": [],
    }
    result = {
        "id": variant,
        "sourceArchetypeId": "landscape_park_pedestrian_bridge",
        "widthM": 36.971,
        "routeAxis": "local_y",
        "placements": [],
        "program": program,
        "sourceAssemblySha256": "d7dddc9371b5cf554bcb372b6d46c8fc0e6256d7335bd47ff542420463f20066",
        "sourceRecipeSha256": "1" * 64,
        "referenceSha256": "2" * 64,
        "modules": {
            kind: {"url": f"/street-kits/pilots/{variant}/{kind}.glb", "sha256": "3" * 64}
            for kind in ("end", "span", "plants")
        },
    }
    seal(result)
    return result


def seal(value):
    value["programSha256"] = hashlib.sha256(
        json.dumps(value["program"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def test_accepts_a_complete_trusted_source_span():
    validate_modular_bridge_profile(row())


def test_all_nine_deliveries_close_the_exact_source_and_module_bytes():
    root = Path(__file__).resolve().parents[2]
    rows = json.loads((root / "backend/app/data/nativeBridgePilots.json").read_text(encoding="utf-8"))
    delivered = [item for item in rows if item["id"] in SOURCE_BRIDGE_SOURCES]
    assert {item["id"] for item in delivered} == SOURCE_BRIDGE_SOURCES.keys()
    assert len(delivered) == 9
    for item in delivered:
        validate_modular_bridge_profile(item)
        source = root / f"frontend/public/street-kits/claude-20261023/{item['sourceAssemblySha256']}.glb"
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item["sourceAssemblySha256"]
        for module in item["modules"].values():
            data = (root / "frontend/public" / module["url"].lstrip("/")).read_bytes()
            assert data[:4] == b"glTF"
            assert len(data) == module["bytes"]
            assert hashlib.sha256(data).hexdigest() == module["sha256"]


@pytest.mark.parametrize(
    "variant,lanes", [("stone_arch_road_bridge_route_v1", 4), ("steel_truss_road_bridge_route_v1", 2)]
)
def test_road_lane_counts_follow_source_programmes_not_carriageway_width(variant, lanes):
    profile = modular_bridge_profile(variant)
    props = {
        "road_selected_variant_id": variant,
        "road_archetype_id": profile["sourceArchetypeId"],
        "width": profile["widthM"],
        "lane_count": lanes,
        "plan_centerline": [[0, 0], [profile["fixtureLengthM"] / 111320, 0]],
    }
    validate_specialist_properties(props)
    with pytest.raises(ValueError):
        validate_specialist_properties({**props, "lane_count": 6 - lanes})


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r["program"]["bridge"]["parts"][1].update(lengthM=0),
        lambda r: r["program"]["bridge"]["parts"][1].update(mode="any_scale"),
        lambda r: r["program"]["bridge"]["parts"][1]["companions"][0].update(pitchM=0),
        lambda r: r["modules"].pop("plants"),
        lambda r: r.update(sourceAssemblySha256="f" * 64),
        lambda r: r["program"]["bridge"].update(trafficKind="motor_race"),
        lambda r: r["program"].update(minLengthM=10),
        lambda r: r["program"]["bridge"]["parts"][1].update(deformation={"mode": "unknown", "nativeLengthM": 81}),
    ],
)
def test_rejects_untrusted_or_incomplete_structure_even_with_rehashed_program(change):
    value = copy.deepcopy(row())
    change(value)
    seal(value)
    with pytest.raises(ValueError):
        validate_modular_bridge_profile(value)
