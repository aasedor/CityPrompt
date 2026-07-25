"""Validate the physical-glass / baked-facade contract in one or more GLBs."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


REQUIRED_LOD_TAGS = {"far", "near", "physical", "interior"}


def glb_json(path: Path) -> dict:
    with path.open("rb") as stream:
        magic, version, _length = struct.unpack("<4sII", stream.read(12))
        if magic != b"glTF" or version != 2:
            raise ValueError(f"{path} is not a glTF 2 GLB")
        chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
        if chunk_type != 0x4E4F534A:
            raise ValueError(f"{path} does not start with a JSON chunk")
        return json.loads(stream.read(chunk_length))


def validate(path: Path) -> list[str]:
    payload = glb_json(path)
    materials = payload.get("materials") or []
    errors: list[str] = []
    lod_tags = {
        material.get("extras", {}).get("glazing_lod")
        for material in materials
        if material.get("extras", {}).get("glazing_lod")
    }
    missing = REQUIRED_LOD_TAGS - lod_tags
    if missing:
        errors.append(f"missing LOD tags: {sorted(missing)}")

    transmitted = [
        material for material in materials
        if "KHR_materials_transmission" in (material.get("extensions") or {})
    ]
    if not transmitted:
        errors.append("no KHR_materials_transmission materials")
    for material in transmitted:
        name = material.get("name", "(unnamed)")
        if material.get("alphaMode", "OPAQUE") == "BLEND":
            errors.append(f"{name}: physical transmission must not use alpha BLEND")
        if "GlassOverlay" in name and material.get("alphaMode", "OPAQUE") != "MASK":
            errors.append(f"{name}: semantic overlay must use alpha MASK")
        if name == "MAT_Glass" and material.get("alphaMode", "OPAQUE") != "OPAQUE":
            errors.append("MAT_Glass must use alpha OPAQUE")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("glb", type=Path, nargs="+")
    args = parser.parse_args()
    failed = False
    for path in args.glb:
        errors = validate(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  {error}")
        else:
            print(f"PASS {path}")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
