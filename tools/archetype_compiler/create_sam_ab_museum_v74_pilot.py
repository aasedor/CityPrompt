"""Prepare controlled baseline and SAM-informed museum grammars for v74."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from compiler import compile_archetype
from generate_family import export_archetype
from signature_profiles import inject_signature, signature_for


TOOL_DIR = Path(__file__).resolve().parent
REPO = TOOL_DIR.parents[1]
OUTPUT = REPO / "artifacts" / "sam3d-museum-ab-pilot"
ARCHETYPE_ID = "large_art_museum_gallery"
VARIANT_ID = "deconstructivist_titanium_pavilion"


def merge(base: dict, override: dict) -> dict:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def patch_named(items: list[dict], patches: dict[str, dict]) -> list[dict]:
    resolved = []
    found = set()
    for item in items:
        item_id = str(item.get("id", ""))
        if item_id in patches:
            item = merge(item, patches[item_id])
            found.add(item_id)
        resolved.append(item)
    missing = set(patches) - found
    if missing:
        raise KeyError(f"SAM evidence patches reference missing ids: {sorted(missing)}")
    return resolved


def prepare() -> tuple[Path, Path]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source_path = OUTPUT / "archetype-source.json"
    payload = export_archetype(ARCHETYPE_ID, VARIANT_ID, source_path)
    grammar = compile_archetype(
        payload,
        floors=4,
        width_m=80.0,
        depth_m=60.0,
    ).to_dict()
    inject_signature(grammar, ARCHETYPE_ID, variant_id=VARIANT_ID)

    profile = signature_for(VARIANT_ID)
    patches = deepcopy(profile["sam_evidence_patches"])
    signature = grammar.get("architectural_signature") or {}
    signature.pop("sam_evidence_patches", None)

    baseline = deepcopy(grammar)
    baseline["family_id"] = "titanium-museum-baseline-v74"
    baseline["evidence_pass"] = {
        "mode": "catalogue_images_only",
        "reference_roles": ["street_identity", "oblique_massing", "roof_plan"],
    }

    informed = deepcopy(grammar)
    informed["family_id"] = "titanium-museum-sam-informed-v74"
    informed_graph = informed["massing_graph"]
    informed_graph["profile"] = patches["profile"]
    informed_graph["description"] = patches["description"]
    informed_graph["nodes"] = patch_named(
        informed_graph.get("nodes", []), patches.get("node_overrides", {})
    )
    informed_graph["assemblies"] = patch_named(
        informed_graph.get("assemblies", []), patches.get("assembly_overrides", {})
    )
    informed["evidence_pass"] = {
        "mode": "sam3d_depth_and_section",
        "model": "facebook/sam-3d-objects",
        "seed": 42,
        "source_image": "variant_0.png",
        "audited_mask": "artifacts/sam3d-museum-ab-pilot/museum-audited-mask.png",
        "result_metadata": "artifacts/sam3d-museum-ab-pilot/sam-results/pilot-01/metadata.json",
        "applied_findings": [
            "seven-lobed radial inner pod cluster",
            "greater pod lean, twist and height differentiation",
            "deeper left-biased gallery cantilever",
            "stronger vertical drape and plan-wave variation in perimeter ribbon",
        ],
    }

    baseline_path = OUTPUT / "baseline-grammar.json"
    informed_path = OUTPUT / "sam-informed-grammar.json"
    baseline_path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    informed_path.write_text(json.dumps(informed, indent=2) + "\n", encoding="utf-8")
    return baseline_path, informed_path


if __name__ == "__main__":
    for path in prepare():
        print(path)
