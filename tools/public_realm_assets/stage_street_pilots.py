"""Stage reviewed street modules and a small, hash-locked runtime pilot manifest.

The straight assembly is deliberately excluded: student routes must reconstruct
the metric bands and place independent rigid modules, never stretch the preview.
This command stages candidates; it does not activate a student catalogue entry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


FINISHES = {"stone": "pavers", "brick": "brick", "cobble": "cobble", "deck": "timber"}
MATERIALS = {"paving", "asphalt", "cycle", "soil", "grass"}
PILOT_ID = re.compile(r"^student_[a-z0-9_]+_v[1-9][0-9]*$")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _checked_file(path: Path, expected: dict) -> bytes:
    if path.name != expected.get("path") or not path.is_file():
        raise ValueError(f"Missing exact module: {path}")
    data = path.read_bytes()
    if len(data) != expected.get("bytes") or _sha256(data) != expected.get("sha256"):
        raise ValueError(f"Module bytes or SHA-256 changed: {path}")
    return data


def _finite(*values: object) -> bool:
    return all(isinstance(value, (int, float)) and math.isfinite(value) for value in values)


def inspect_pilot(package: Path) -> tuple[dict, dict[str, bytes]]:
    recipe_path = package / "recipe.json"
    recipe_bytes = recipe_path.read_bytes()
    recipe = json.loads(recipe_bytes)
    street_id = recipe.get("id")
    if not isinstance(street_id, str) or not PILOT_ID.fullmatch(street_id) or recipe.get("runtime_approved") is not False:
        raise ValueError("Only explicitly staged, unapproved student street pilot packages are accepted")
    width, length = recipe["dimensions_m"]
    if not _finite(width, length) or not 5 <= width <= 40 or not 20 <= length <= 100:
        raise ValueError("Invalid metric street envelope")
    if width != recipe.get("fixed_width_m") or length != recipe.get("fixture_length_m"):
        raise ValueError("Fixture and metric dimensions disagree")
    _checked_file(package / recipe["assembly"]["path"], recipe["assembly"])
    sections = recipe["sections"]
    if not sections or len({section["name"] for section in sections}) != len(sections):
        raise ValueError("Missing or duplicate ordered bands")
    cursor = -width / 2
    for section in sections:
        if not _finite(section["x"], section["width"]) or section["width"] <= 0:
            raise ValueError("Invalid metric band")
        if section["material"] not in MATERIALS or abs(section["x"] - cursor - section["width"] / 2) > 1e-5:
            raise ValueError("Bands must tile the exact width without overlap or gap")
        cursor += section["width"]
    if abs(cursor - width / 2) > 1e-5:
        raise ValueError("Bands do not cover the whole right of way")
    finish = FINISHES.get(recipe.get("pattern"))
    if finish is None:
        raise ValueError("The pilot needs an explicit supported junction finish")
    module_names = {item["kind"] for item in recipe["placements"]}
    wells = recipe["tree_wells"]
    if wells:
        module_names.update({"grove_tree", "tree_well_grate"})
    if module_names - set(recipe["modules"]):
        raise ValueError("A placed component has no native module")
    modules = {
        name: _checked_file(package / "modules" / recipe["modules"][name]["path"], recipe["modules"][name])
        for name in sorted(module_names)
    }
    placements = []
    for item in recipe["placements"]:
        pose = {"kind": item["kind"], "x": item["x"], "y": item["y"],
                "z": item.get("z", 0), "yaw": item.get("yaw", 0), "scale": item.get("scale", 1)}
        if not _finite(*(pose[key] for key in ("x", "y", "z", "yaw", "scale"))):
            raise ValueError("A module pose is not finite")
        if pose["scale"] <= 0 or abs(pose["x"]) >= width / 2 or abs(pose["y"]) >= length / 2:
            raise ValueError("A module pose leaves the native section")
        placements.append(pose)
    tree_wells = []
    for item in wells:
        if item.get("style") != "grate" or item.get("tree_kind") != "grove_tree":
            raise ValueError("Unrecognized hardscape tree/well pair")
        if not _finite(*(item.get(key) for key in ("x", "y", "width", "depth"))):
            raise ValueError("Invalid tree well")
        if item["width"] <= 0 or item["depth"] <= 0 or abs(item["x"]) + item["width"] / 2 > width / 2:
            raise ValueError("A tree well leaves the section")
        for kind in ("grove_tree", "tree_well_grate"):
            if not any(pose["kind"] == kind and abs(pose["x"] - item["x"]) < 1e-5
                       and abs(pose["y"] - item["y"]) < 1e-5 for pose in placements):
                raise ValueError("Every hardscape tree needs its exact tree/well pair")
        tree_wells.append({key: item[key] for key in ("x", "y", "width", "depth", "style", "tree_kind")})
    reference = recipe["image_references"][0]
    reference_parent = Path(recipe["reference"]).parts[0].replace("-", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", reference_parent):
        raise ValueError("Source reference must identify one catalogue street")
    relative_reference = Path(reference["path"])
    if relative_reference.is_absolute() or ".." in relative_reference.parts or relative_reference.suffix.lower() != ".png":
        raise ValueError("Reference image must be a package-local PNG")
    reference_path = package / relative_reference
    reference_data = reference_path.read_bytes()
    if len(reference_data) != reference["bytes"] or _sha256(reference_data) != reference["sha256"]:
        raise ValueError("Source reference image changed")
    manifest = {
        "id": street_id,
        "sourceArchetypeId": reference_parent,
        "title": recipe["title"],
        "status": "candidate",
        "sourceRecipeSha256": _sha256(recipe_bytes),
        "sourceAssemblySha256": recipe["assembly"]["sha256"],
        "referenceSha256": reference["sha256"],
        "widthM": width,
        "fixtureLengthM": length,
        "routeAxis": "local_y",
        "junctionSurface": finish,
        "sections": [{key: item[key] for key in ("name", "x", "width", "material")} for item in sections],
        "placements": placements,
        "treeWells": tree_wells,
        "modules": {name: {"sha256": recipe["modules"][name]["sha256"], "bytes": len(data),
                           "url": f"/street-kits/pilots/{street_id}/{name}.glb"}
                    for name, data in modules.items()},
        "thumbnailUrl": f"/street-kits/pilots/{street_id}/reference.png",
    }
    return manifest, {**{f"{name}.glb": data for name, data in modules.items()}, "reference.png": reference_data}


def stage(pilots: list[Path], public_root: Path, manifest_path: Path, *, dry_run: bool,
          replace: bool = False) -> list[dict]:
    inspected = [inspect_pilot(package) for package in pilots]
    ids = [manifest["id"] for manifest, _ in inspected]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate pilot identity")
    existing_rows = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    existing = {row["id"]: row for row in existing_rows}
    if len(existing) != len(existing_rows):
        raise ValueError("Existing pilot registry contains duplicate identities")
    for manifest, files in inspected:
        if not replace and manifest["id"] in existing and existing[manifest["id"]] != manifest:
            raise ValueError(f"Refusing to silently replace a staged pilot: {manifest['id']}")
        destination = public_root / "street-kits" / "pilots" / manifest["id"]
        for name, data in files.items():
            existing_file = destination / name
            if existing_file.exists() and existing_file.read_bytes() != data:
                raise ValueError(f"Refusing to overwrite changed deliverable: {existing_file}")
    if not dry_run:
        for manifest, files in inspected:
            destination = public_root / "street-kits" / "pilots" / manifest["id"]
            destination.mkdir(parents=True, exist_ok=True)
            for name, data in files.items():
                target = destination / name
                if not target.exists():
                    target.write_bytes(data)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        replacements = {item["id"]: item for item, _ in inspected}
        merged = [replacements.get(row["id"], row) for row in existing_rows]
        merged += [item for item, _ in inspected if item["id"] not in existing]
        manifest_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return [item for item, _ in inspected]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="append", type=Path, required=True)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replace", action="store_true", help="Explicitly revise previously staged metadata")
    args = parser.parse_args()
    result = stage(args.pilot, args.public_root, args.manifest, dry_run=args.dry_run, replace=args.replace)
    print(("DRY_RUN_PASS" if args.dry_run else "STAGED_CANDIDATES"), ", ".join(row["id"] for row in result))


if __name__ == "__main__":
    main()
