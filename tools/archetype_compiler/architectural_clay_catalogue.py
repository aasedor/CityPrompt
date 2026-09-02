"""Validation helpers for the saved, pre-runtime architectural-clay catalogue."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOGUE = Path(__file__).with_name("architectural_clay_catalogue.json")
SCHEMA = "cityprompt.rlasm.architectural-clay-catalogue@1"
STATUS = "BUILDER_VERIFIED_FOR_USER_VISUAL_REVIEW"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SEMANTIC_ROLES = {"masonry", "wall", "trim", "roof", "glass", "timber", "interior", "hardware"}


def load_catalogue(path: Path = DEFAULT_CATALOGUE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalogue(catalogue: dict, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if catalogue.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")

    assets = catalogue.get("assets")
    if not isinstance(assets, list) or not assets:
        return errors + ["assets must be a non-empty list"]

    seen: set[str] = set()
    for index, asset in enumerate(assets):
        label = f"assets[{index}]"
        candidate = asset.get("candidate")
        if not isinstance(candidate, str) or not candidate:
            errors.append(f"{label}.candidate must be a non-empty string")
            continue
        label = candidate
        if candidate in seen:
            errors.append(f"duplicate candidate: {candidate}")
        seen.add(candidate)

        if asset.get("status") != STATUS:
            errors.append(f"{label}.status must remain builder-review status")
        if asset.get("runtime_seed_allowed") is not False:
            errors.append(f"{label}.runtime_seed_allowed must be false before approval")
        if asset.get("independent_keeper_review") != "pending":
            errors.append(f"{label}.independent_keeper_review must be pending")
        if not str(asset.get("method", "")).startswith("RLASM v6.1"):
            errors.append(f"{label}.method must use RLASM v6.1")

        documentation = asset.get("documentation")
        if not isinstance(documentation, str) or not (root / documentation).is_file():
            errors.append(f"{label}.documentation does not exist: {documentation}")

        roles = asset.get("semantic_roles")
        if not isinstance(roles, list) or not roles or not set(roles).issubset(SEMANTIC_ROLES):
            errors.append(f"{label}.semantic_roles contains unknown or missing roles")

        runtime = asset.get("runtime")
        if not isinstance(runtime, dict):
            errors.append(f"{label}.runtime must be an object")
        else:
            if runtime.get("images") != 0 or runtime.get("textures") != 0:
                errors.append(f"{label}.runtime must remain image- and texture-free")
            if "sha256" in runtime and not SHA256.fullmatch(str(runtime["sha256"])):
                errors.append(f"{label}.runtime.sha256 must be lowercase SHA-256")

        runtime_trial = asset.get("runtime_trial")
        if runtime_trial is not None:
            if not isinstance(runtime_trial, dict):
                errors.append(f"{label}.runtime_trial must be an object")
            else:
                source_variant = asset.get("source_variant")
                if runtime_trial.get("scope") != "private_local":
                    errors.append(f"{label}.runtime_trial.scope must remain private_local")
                if runtime_trial.get("planner_selectable") is not True:
                    errors.append(f"{label}.runtime_trial.planner_selectable must be true")
                if runtime_trial.get("generated_only_after_compile") is not True:
                    errors.append(f"{label}.runtime_trial must remain compile-gated")
                if not source_variant or runtime_trial.get("exact_variant_id") != source_variant:
                    errors.append(f"{label}.runtime_trial must bind the exact source_variant")

            source_lock = asset.get("source_lock")
            if not isinstance(source_lock, list) or len(source_lock) < 3:
                errors.append(f"{label}.runtime_trial requires front, oblique, and top source locks")
            else:
                for item in source_lock:
                    if not SHA256.fullmatch(str(item.get("sha256", ""))):
                        errors.append(f"{label}.runtime_trial source_lock contains an invalid SHA-256")

        if asset.get("generation_mode") == "clay_first":
            source_lock = asset.get("source_lock")
            if not isinstance(source_lock, list) or len(source_lock) < 3:
                errors.append(f"{label}.source_lock requires front, oblique, and top evidence")
            else:
                views = {item.get("view") for item in source_lock}
                if views != {"front", "oblique_aerial", "near_true_top"}:
                    errors.append(f"{label}.source_lock has an unexpected view roster")
                for item in source_lock:
                    if not SHA256.fullmatch(str(item.get("sha256", ""))):
                        errors.append(f"{label}.source_lock contains an invalid SHA-256")
            build_script = asset.get("build_script")
            if not isinstance(build_script, str) or not (root / build_script).is_file():
                errors.append(f"{label}.build_script does not exist: {build_script}")
            grammar = asset.get("semantic_size_grammar")
            if not isinstance(grammar, dict) or grammar.get("stretching_allowed") is not False:
                errors.append(f"{label}.semantic_size_grammar must prohibit stretching")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    args = parser.parse_args()
    errors = validate_catalogue(load_catalogue(args.catalogue))
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"ARCHITECTURAL_CLAY_CATALOGUE_OK assets={len(load_catalogue(args.catalogue)['assets'])}")


if __name__ == "__main__":
    main()
