"""Compile the bounded Scottish Baronial v76 architectural-evidence pilot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from architectural_evidence import compile_interpretation
from compiler import compile_archetype
from generate_family import export_archetype
from signature_profiles import inject_signature


TOOL_DIR = Path(__file__).resolve().parent
REPO = TOOL_DIR.parents[1]
ARCHETYPE_ID = "chateauesque_grand_railway_hotel"
VARIANT_ID = "scottish_baronial_granite_tower"
PROFILE_ID = "scottish_baronial_v76"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--geometry-evidence",
        type=Path,
        default=REPO / "artifacts/architectural-evidence-v76/evidence/architectural-geometry-evidence.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "artifacts/architectural-evidence-v76",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    source_path = output / "archetype-source.json"
    payload = export_archetype(ARCHETYPE_ID, VARIANT_ID, source_path)
    grammar = compile_archetype(payload, floors=5, width_m=55.0, depth_m=36.0).to_dict()
    inject_signature(grammar, ARCHETYPE_ID, variant_id=VARIANT_ID)

    profiles = json.loads((TOOL_DIR / "architectural_evidence_profiles.json").read_text(encoding="utf-8"))
    profile = profiles["profiles"][PROFILE_ID]
    geometry = json.loads(args.geometry_evidence.resolve().read_text(encoding="utf-8"))
    memory = json.loads((TOOL_DIR / "high_quality_building_memory.json").read_text(encoding="utf-8"))
    interpretation, patched = compile_interpretation(grammar, geometry, profile, memory)
    if interpretation["decision"] != "apply_reviewed_constraints":
        raise SystemExit("Architectural evidence gates withheld the v76 graph patch")

    patched["family_id"] = "scottish-baronial-architectural-evidence-v76"
    patched["architectural_interpretation"] = {
        "schema": interpretation["schema"],
        "id": interpretation["id"],
        "status": interpretation["status"],
        "decision": interpretation["decision"],
        "identity_mode": interpretation["identity_mode"],
        "learned_mesh_delivery": "prohibited",
    }
    interpretation_path = output / "architectural-interpretation.json"
    grammar_path = output / "grammar.json"
    interpretation_path.write_text(json.dumps(interpretation, indent=2) + "\n", encoding="utf-8")
    grammar_path.write_text(json.dumps(patched, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision": interpretation["decision"],
        "interpretation": str(interpretation_path),
        "grammar": str(grammar_path),
    }, indent=2))


if __name__ == "__main__":
    main()
