"""Compile the Scottish Baronial v77 material-continuity and passage pilot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from architectural_evidence import compile_interpretation
from compiler import compile_archetype
from generate_family import export_archetype
from generation_quality_contract import assess_generation_quality_contract
from pipeline_preflight import assess_generation_preflight
from signature_profiles import inject_signature


TOOL_DIR = Path(__file__).resolve().parent
REPO = TOOL_DIR.parents[1]
ARCHETYPE_ID = "chateauesque_grand_railway_hotel"
VARIANT_ID = "scottish_baronial_granite_tower"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--geometry-evidence", type=Path,
        default=REPO / "artifacts/architectural-evidence-v76/evidence/architectural-geometry-evidence.json",
    )
    parser.add_argument("--output", type=Path, default=REPO / "artifacts/material-void-v77")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    source_path = output / "archetype-source.json"
    source = export_archetype(ARCHETYPE_ID, VARIANT_ID, source_path)
    grammar = compile_archetype(source, floors=5, width_m=55.0, depth_m=36.0).to_dict()
    inject_signature(grammar, ARCHETYPE_ID, variant_id=VARIANT_ID)
    profiles = json.loads((TOOL_DIR / "architectural_evidence_profiles.json").read_text(encoding="utf-8"))
    geometry = json.loads(args.geometry_evidence.resolve().read_text(encoding="utf-8"))
    memory = json.loads((TOOL_DIR / "high_quality_building_memory.json").read_text(encoding="utf-8"))
    interpretation, patched = compile_interpretation(
        grammar, geometry, profiles["profiles"]["scottish_baronial_v76"], memory,
    )
    if interpretation["decision"] != "apply_reviewed_constraints":
        raise SystemExit("Architectural evidence gates withheld the v77 graph")

    patched["family_id"] = "scottish-baronial-material-void-v77"
    patched["massing_graph"]["profile"] = "scottish_baronial_material_void_v77"
    quality = assess_generation_quality_contract(patched, source=source)
    preflight = assess_generation_preflight(source, patched)
    if quality["status"] != "pass" or preflight["status"] != "pass":
        raise SystemExit("Material/void quality contract or production preflight failed")

    (output / "grammar.json").write_text(json.dumps(patched, indent=2) + "\n", encoding="utf-8")
    (output / "generation-quality.json").write_text(json.dumps(quality, indent=2) + "\n", encoding="utf-8")
    (output / "production-preflight.json").write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "quality": quality["status"], "preflight": preflight["status"],
        "grammar": str(output / "grammar.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
