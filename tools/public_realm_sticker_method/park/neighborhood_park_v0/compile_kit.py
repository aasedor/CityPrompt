"""Compile Neighborhood Park v0 objects into the live public-realm workflow.

This is the park analogue of exact-one Sticker Method carrier compilation. It
fails when an expected GLB, skin, semantic owner or fixed placement is absent,
then emits one deterministic JSON manifest consumed by the Three.js runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
KIT_ROOT = REPO_ROOT / "frontend" / "public" / "park-kits" / "neighborhood-park-rustic-v0"
SKIN_ROOT = REPO_ROOT / "frontend" / "public" / "park-skins" / "neighborhood-park-rustic-v0" / "adaptive-v1"
RUNTIME_OUTPUT = REPO_ROOT / "frontend" / "src" / "data" / "neighborhoodParkV0StickerKit.json"
LOCAL_OUTPUT = HERE / "compiled-kit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def glb_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if data[:4] != b"glTF" or len(data) < 20:
        raise ValueError(f"invalid GLB header: {path}")
    version, declared_length = struct.unpack_from("<II", data, 4)
    if version != 2 or declared_length != len(data):
        raise ValueError(f"invalid GLB version/length: {path}")
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        raise ValueError(f"first GLB chunk is not JSON: {path}")
    return json.loads(data[20 : 20 + chunk_length].rstrip(b" \x00").decode("utf-8"))


def validate_asset(asset_id: str, spec: dict[str, Any]) -> dict[str, Any]:
    path = KIT_ROOT / spec["file"]
    if not path.exists():
        raise ValueError(f"{asset_id}: missing {path}")
    actual_hash = sha256(path)
    if actual_hash != spec["sha256"]:
        raise ValueError(f"{asset_id}: stale hash {actual_hash}")
    gltf = glb_json(path)
    mesh_nodes = [node for node in gltf.get("nodes", []) if "mesh" in node]
    if len(mesh_nodes) != spec["meshObjectCount"]:
        raise ValueError(f"{asset_id}: mesh count mismatch")
    owners: set[str] = set()
    roles: set[str] = set()
    for node in mesh_nodes:
        extras = node.get("extras", {})
        owner = extras.get("sticker_owner")
        role = extras.get("material_role")
        semantic = extras.get("semantic_role")
        if owner != "neighborhood_park_v0" or not role or not semantic:
            raise ValueError(f"{asset_id}: unowned mesh node {node.get('name')}")
        if extras.get("nonuniform_scaling_allowed") is not False:
            raise ValueError(f"{asset_id}: nonuniform scaling not forbidden")
        owners.add(owner)
        roles.add(role)
    return {
        "file": spec["file"],
        "url": f"/park-kits/neighborhood-park-rustic-v0/{spec['file']}",
        "sha256": actual_hash,
        "bytes": path.stat().st_size,
        "meshObjectCount": len(mesh_nodes),
        "dimensionsM": spec["dimensionsM"],
        "semantic": spec["semantic"],
        "owners": sorted(owners),
        "materialRoles": sorted(roles),
        "metricScale": 1.0,
        "nonuniformScalingAllowed": False,
    }


def placements() -> list[dict[str, Any]]:
    placed: list[dict[str, Any]] = [
        {"id": "fixed_timber_pavilion", "assetId": "timber_pavilion", "positionM": [-15.0, 4.5, 0.0], "yawDeg": 0.0},
        {"id": "fixed_climbing_tower_slide", "assetId": "timber_climbing_tower_with_slide", "positionM": [7.0, -1.5, 0.0], "yawDeg": -8.0},
        {"id": "fixed_timber_swing", "assetId": "timber_swing_frame", "positionM": [-3.0, 5.5, 0.0], "yawDeg": 0.0},
        {"id": "boulders_west", "assetId": "natural_boulder_group", "positionM": [-10.0, -5.8, 0.0], "yawDeg": 18.0},
        {"id": "boulders_south", "assetId": "natural_boulder_group", "positionM": [2.0, -8.0, 0.0], "yawDeg": -12.0},
        {"id": "boulders_east", "assetId": "natural_boulder_group", "positionM": [15.0, 5.8, 0.0], "yawDeg": 73.0},
    ]
    # A deliberate open gateway faces the park path at the south-west corner.
    fence_specs = [
        (-5.8, -9.0, 0.0), (-1.5, -9.0, 2.0), (2.8, -9.0, -1.0), (7.1, -9.0, 2.0), (11.4, -8.3, 16.0),
        (15.3, -6.2, 72.0), (16.0, -2.0, 92.0), (15.8, 2.2, 86.0), (14.2, 6.3, 60.0),
        (10.5, 8.2, 8.0), (6.2, 8.7, -2.0), (1.9, 8.8, 1.0), (-7.2, 8.3, -8.0),
        (-11.2, 7.2, -24.0), (-13.6, 4.0, -78.0), (-13.8, -0.3, -92.0), (-12.5, -4.4, -64.0),
    ]
    for index, (x, y, yaw) in enumerate(fence_specs):
        placed.append({
            "id": f"split_rail_fence_{index:02d}",
            "assetId": "split_rail_fence",
            "positionM": [x, y, 0.0],
            "yawDeg": yaw,
        })
    return placed


def compile_kit() -> dict[str, Any]:
    kit = load_json(KIT_ROOT / "kit_manifest.json")
    skin = load_json(SKIN_ROOT / "manifest.json")
    if kit["reference"]["sha256"] != "38c1079127126017edb7945f77f47d73c4d0dde1fe5a566ac5dc0e791473d5c3":
        raise ValueError("wrong exact reference")
    if skin.get("sourcePixelsProjected") is not False:
        raise ValueError("perspective source pixels may not be projected")
    required_roles = {
        "paver", "lawn", "asphalt", "planting", "safety", "timber",
        "stone", "metal", "rope",
    }
    if set(skin.get("materials", {})) != required_roles:
        raise ValueError("incomplete intrinsic skin roles")
    assets = {asset_id: validate_asset(asset_id, spec) for asset_id, spec in kit["assets"].items()}
    required_assets = {
        "timber_pavilion",
        "timber_climbing_tower_with_slide",
        "timber_swing_frame",
        "split_rail_fence",
        "natural_boulder_group",
    }
    if set(assets) != required_assets:
        raise ValueError("fixed identity kit is incomplete")
    object_placements = placements()
    placement_ids = [item["id"] for item in object_placements]
    if len(placement_ids) != len(set(placement_ids)):
        raise ValueError("duplicate placement ids")
    if any(item["assetId"] not in assets for item in object_placements):
        raise ValueError("placement references unknown asset")

    asset_face_owners = {
        asset_id: {
            "owner": "neighborhood_park_v0",
            "semantic": asset["semantic"],
            "materialRoles": asset["materialRoles"],
            "coverage": "all_exported_mesh_nodes_exactly_once",
        }
        for asset_id, asset in assets.items()
    }
    return {
        "schemaVersion": 1,
        "method": "sticker_method_site_adaptive_whole_program",
        "archetypeId": "neighborhood_park",
        "variantId": "neighborhood_park_v0",
        "profileId": "neighborhood-park-v4",
        "reference": kit["reference"],
        "canonicalSiteM": [100.0, 80.0],
        "fixedProgramEnvelopeM": [50.0, 38.0],
        "wholeElementClearanceM": 1.5,
        "adaptation": {
            "siteAdaptiveGround": True,
            "wholeFixedKit": True,
            "nonuniformObjectScalingAllowed": False,
            "cropFixedObjectsAllowed": False,
        },
        "skin": {
            "baseUrl": "/park-skins/neighborhood-park-rustic-v0/adaptive-v1",
            "manifestSha256": sha256(SKIN_ROOT / "manifest.json"),
            "roles": sorted(required_roles),
            "sourcePixelsProjected": False,
        },
        "groundPatches": [
            {"id": "rustic_play_gravel", "kind": "ellipse", "role": "safety", "centerM": [3.0, -0.5], "sizeM": [31.0, 20.0], "zM": 0.028},
            {"id": "rustic_pavilion_pad", "kind": "rectangle", "role": "paver", "centerM": [-15.0, 4.5], "sizeM": [10.0, 8.0], "zM": 0.035},
            {"id": "rustic_connector", "kind": "rectangle", "role": "asphalt", "centerM": [-8.8, 1.8], "sizeM": [8.0, 3.2], "zM": 0.031, "yawDeg": -18.0}
        ],
        "assets": assets,
        "placements": object_placements,
        "surfaceOwnership": {
            "exactOne": True,
            "fallbackAllowed": False,
            "assetOwners": asset_face_owners,
        },
        "compilerInputs": {
            "kitManifestSha256": sha256(KIT_ROOT / "kit_manifest.json"),
            "skinManifestSha256": sha256(SKIN_ROOT / "manifest.json"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = compile_kit()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        for output in (LOCAL_OUTPUT, RUNTIME_OUTPUT):
            if not output.exists() or output.read_text(encoding="utf-8") != payload:
                raise SystemExit(f"stale compiled output: {output}")
        print("compiled kit is current")
        return 0
    for output in (LOCAL_OUTPUT, RUNTIME_OUTPUT):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
