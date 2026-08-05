"""Validate and checkpoint the bounded five-archetype LEGO + depth batch."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .compile_neighborhood_park_skins import REPO_ROOT
except ImportError:
    from compile_neighborhood_park_skins import REPO_ROOT


CONTRACT_PATH = REPO_ROOT / "tools/park_skin_compiler/park_archetype_batch.json"
DEFAULT_OUT = REPO_ROOT / "artifacts/neighborhood-park-lego-depth-pilot/five-archetype-batch"


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def validate_contract(contract: dict) -> list[str]:
    errors: list[str] = []
    archetypes = contract.get("archetypes", [])
    if len(archetypes) != 5:
        errors.append(f"expected 5 archetypes, found {len(archetypes)}")
    ids = [item.get("id") for item in archetypes]
    if len(ids) != len(set(ids)):
        errors.append("archetype ids must be unique")
    policy = contract.get("renderPolicy", {})
    if policy.get("people") is not False:
        errors.append("people must remain disabled")
    if policy.get("largeBuildings") is not False:
        errors.append("large buildings must remain in the separate render layer")
    if policy.get("referenceViews") != ["base", "angle_60", "angle_90"]:
        errors.append("every archetype requires base, 60-degree and 90-degree references")
    for item in archetypes:
        width, depth = item.get("envelopeM", [0, 0])
        if width <= 0 or depth <= 0:
            errors.append(f"{item.get('id')}: invalid envelope")
        if not item.get("depthAssets"):
            errors.append(f"{item.get('id')}: no depth assets")
        source = REPO_ROOT / "frontend/public/archetypes/openspaces" / item.get("slug", "")
        for filename in ("variant_0.png", "variant_0_angle_60.jpg", "variant_0_angle_90.jpg"):
            if not (source / filename).exists():
                errors.append(f"{item.get('id')}: missing {filename}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract = load_contract()
    errors = validate_contract(contract)
    if errors:
        raise SystemExit("\n".join(errors))
    summary = {
        "batchId": contract["batchId"],
        "method": contract["method"],
        "apiCalls": contract["apiCalls"],
        "archetypeCount": len(contract["archetypes"]),
        "people": contract["renderPolicy"]["people"],
        "largeBuildings": contract["renderPolicy"]["largeBuildings"],
        "assetCount": sum(len(item["depthAssets"]) for item in contract["archetypes"]),
        "archetypes": [item["id"] for item in contract["archetypes"]],
    }
    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "batch_checkpoint.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"wrote {args.out / 'batch_checkpoint.json'}")


if __name__ == "__main__":
    main()
