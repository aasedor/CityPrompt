"""Prepare the bounded free-geometry Titanium Museum v75 grammar."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from compiler import compile_archetype
from generate_family import export_archetype
from signature_profiles import inject_signature, signature_for


TOOL_DIR = Path(__file__).resolve().parent
REPO = TOOL_DIR.parents[1]
OUTPUT = REPO / "artifacts" / "archetype-geometry-pass-v75"
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
        raise KeyError(f"Geometry patches reference missing ids: {sorted(missing)}")
    return resolved


def apply_patch(graph: dict, patch: dict) -> None:
    graph["profile"] = patch["profile"]
    graph["description"] = patch["description"]
    removed = set(patch.get("remove_nodes", []))
    graph["nodes"] = [node for node in graph.get("nodes", []) if node.get("id") not in removed]
    graph["nodes"] = patch_named(graph.get("nodes", []), patch.get("node_overrides", {}))
    graph["assemblies"] = patch_named(
        graph.get("assemblies", []), patch.get("assembly_overrides", {})
    )
    graph["assemblies"].extend(deepcopy(patch.get("assemblies_add", [])))


def prepare() -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source_path = OUTPUT / "archetype-source.json"
    payload = export_archetype(ARCHETYPE_ID, VARIANT_ID, source_path)
    grammar = compile_archetype(payload, floors=4, width_m=80.0, depth_m=60.0).to_dict()
    inject_signature(grammar, ARCHETYPE_ID, variant_id=VARIANT_ID)

    profile = signature_for(VARIANT_ID)
    sam_patch = deepcopy(profile["sam_evidence_patches"])
    geometry_patch = deepcopy(profile["free_geometry_evidence_patches"])
    signature = grammar.get("architectural_signature") or {}
    signature.pop("sam_evidence_patches", None)
    signature.pop("free_geometry_evidence_patches", None)

    graph = grammar["massing_graph"]
    apply_patch(graph, sam_patch)
    apply_patch(graph, geometry_patch)
    signature["signature_material_overrides"] = merge(
        signature.get("signature_material_overrides", {}),
        geometry_patch.get("signature_material_overrides", {}),
    )

    grammar["family_id"] = "titanium-museum-free-geometry-v75"
    grammar["evidence_pass"] = {
        "mode": "free_moge_da3_reviewed_constraints",
        "models": ["Ruicheng/moge-2-vits-normal", "depth-anything/DA3-BASE"],
        "evidence_contract": geometry_patch["evidence_contract"],
        "automatic_status": "review",
        "human_review_decision": "apply_shared_visible_constraints_only",
        "accepted_findings": [
            "continuous curved front envelope and real layer separation",
            "deep left-biased cantilever with a visible underside",
            "multi-level curvilinear roof with several dominant elevation peaks",
            "non-boxy inner volumes retained from the seven-pod evidence base",
        ],
        "withheld_findings": [
            "reflective perforated-metal depth",
            "glazing depth",
            "occluded rear and side construction",
        ],
    }

    output_path = OUTPUT / "free-geometry-grammar.json"
    output_path.write_text(json.dumps(grammar, indent=2) + "\n", encoding="utf-8")
    return output_path


if __name__ == "__main__":
    print(prepare())
