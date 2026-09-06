"""Stage one reviewed clay building; default is a read-only preflight.

Run from the repository root: python -m tools.catalogue_promotion --help.
This tool never approves a model, contacts a provider, commits, or pushes Git.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import tempfile

from tools.rlasm_clay_library import REPO_ROOT, _glb_counts, _validate_payload

LIBRARY = Path("seed/model-library/rlasm-architectural-clay/library.json")
PICKER = Path("frontend/src/features/pickPlace/publishedBuildingAssets.ts")
TRIAL_CHECKS = (
    "catalogue_card",
    "exact_variant",
    "ground_contact",
    "small_and_large_plot",
    "rotation",
    "save_reload",
    "close_and_occluded_capture",
    "no_console_errors",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def encoded(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def repo_file(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes repository: {value}")
    return path


def validate_review(entry: dict, root: Path) -> None:
    review = entry["review"]
    path = repo_file(root, review["repo_path"])
    if digest(path) != review["sha256"]:
        raise ValueError("Independent review bytes have changed")
    result = read(path)
    reviewed_sources = {item.get("sha256") for item in result.get("inspected_files", [])}
    if (
        result.get("architectural_clay_pass") is not True
        or result.get("holistic_review_performed") is not True
        or result.get("unresolved_p0") != 0
        or result.get("unresolved_p1") != 0
        or result.get("candidate") != entry["candidate"]
        or result.get("model_sha256") != entry["model"]["sha256"]
        or not result.get("reviewer")
        or not {reference["sha256"] for reference in entry["references"]}.issubset(reviewed_sources)
    ):
        raise ValueError("Require an independent holistic pass for this exact candidate and GLB")


def picker_assets(payload: dict) -> list[dict]:
    assets = []
    ids = set()
    for entry in payload["entries"]:
        p = entry["picker"]
        if not re.fullmatch(r"[a-z0-9_]+", p["id"]) or p["id"] in ids:
            raise ValueError("Picker IDs must be unique and stable")
        ids.add(p["id"])
        if p["reshape_mode"] not in ("repeat_native", "fixed_native"):
            raise ValueError("Clay buildings require native placement")
        dims = entry["model"]["native_dimensions_m"]
        width, depth, maximum = (float(p[k]) for k in ("width", "depth", "max_size"))
        if (
            not all(math.isfinite(v) for v in (width, depth, maximum))
            or width < dims["width"] + 3
            or depth < dims["depth"] + 3
            or maximum < max(width, depth)
        ):
            raise ValueError("Plot must contain the native envelope plus 3m total clearance")
        props = {
            "building_archetype_id": entry["archetype_id"],
            "development_archetype_id": entry["archetype_id"],
            "development_selected_variant_id": entry["variant_id"],
            "development_archetype_label": entry["variant_label"],
            "floors": entry["native_floors"],
            "floor_count": entry["native_floors"],
        }
        if p["reshape_mode"] == "repeat_native":
            props["native_home_plot"] = True
        else:
            props["native_plot_axes"] = True
        assets.append(
            {
                "id": p["id"],
                "kind": "object",
                "definitionVersion": 1,
                "readiness": "pilot" if entry.get("local_trial_only") else "ready",
                "label": entry["variant_label"],
                "description": p["description"],
                "thumbnail": next(r["repo_path"] for r in entry["references"] if r["role"] == "front").removeprefix(
                    "frontend/public"
                ),
                "model": {"variantId": entry["variant_id"], "revision": entry["candidate"], "method": "RLASM 6.1"},
                "calgaryGuide": {"groupId": p["group_id"], "basis": "form_reference"},
                "zoneType": "building",
                "reshapeMode": p["reshape_mode"],
                "width": width,
                "depth": depth,
                "minWidth": width,
                "minDepth": depth,
                "maxSize": maximum,
                "nativeDimensions": [dims["width"], dims["depth"], dims["height"]],
                "reshapeDescription": p["reshape_description"],
                "properties": props,
            }
        )
    return assets


def picker_source(payload: dict) -> str:
    return (
        "// Generated by python -m tools.catalogue_promotion sync. Edit library.json.\n"
        "import type { PlaceAsset } from './assetRegistry';\n\n"
        "export const PUBLISHED_BUILDING_ASSETS: PlaceAsset[] = "
        + json.dumps(picker_assets(payload), indent=2, ensure_ascii=False, allow_nan=False)
        + ";\n"
    )


def check(root: Path, *, hydrated: bool = True, allow_trials: bool = False) -> dict:
    payload = read(root / LIBRARY)
    if hydrated:
        _validate_payload(payload, clay_root=(root / LIBRARY).parent, repo_root=root)
    for entry in payload["entries"]:
        if entry.get("local_trial_only") and not allow_trials:
            raise ValueError("Local trial cannot be published: complete trial and record human activation")
        if not entry.get("local_trial_only") and "activation" in entry:
            approval, trial = entry["activation"], entry.get("local_trial", {})
            if (
                approval.get("authorized_by") != "human_user"
                or not approval.get("quote")
                or not approval.get("date")
                or approval.get("model_sha256") != entry["model"]["sha256"]
                or trial.get("model_sha256") != entry["model"]["sha256"]
                or not all(trial.get(k) for k in ("project_url", "tested_by", "tested_at", "evidence"))
                or any(trial.get("checks", {}).get(k) is not True for k in TRIAL_CHECKS)
            ):
                raise ValueError("Published activation or local trial no longer matches the model")
        validate_review(entry, root)
    validate_integration(payload, root)
    if (root / PICKER).read_text(encoding="utf-8") != picker_source(payload):
        raise ValueError("Picker drift: run python -m tools.catalogue_promotion sync")
    return payload


def validate_integration(payload: dict, root: Path) -> None:
    """Catch new-family wiring omissions without importing the running backend."""
    guide = root / "frontend/src/features/calgaryCatalogue/guide.ts"
    backend = root / "backend/app/services/lego_assembly.py"
    groups = set(re.findall(r"group\('([^']+)', 'building'", guide.read_text(encoding="utf-8")))
    detached = set()
    for node in ast.parse(backend.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "DETACHED_ARCHETYPE_IDS" for t in node.targets
        ):
            detached = set(ast.literal_eval(node.value.args[0]))
    for entry in payload["entries"]:
        if entry["picker"]["group_id"] not in groups:
            raise ValueError("Choose an existing Calgary building group")
        if entry["picker"]["reshape_mode"] == "repeat_native" and entry["archetype_id"] not in detached:
            raise ValueError(
                "New repeat-native family needs backend DETACHED_ARCHETYPE_IDS support and a placement test"
            )


def prepare(root: Path, package: Path, *, apply: bool = False, trial_only: bool = False) -> list[str]:
    """Validate all content in scratch space before writing an additive promotion."""
    spec = read(package)
    entry = copy.deepcopy(spec["entry"])
    candidate = entry["candidate"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", candidate):
        raise ValueError("Candidate must be a versioned lowercase slug")
    source = (package.parent / spec["model_file"]).resolve()
    review = (package.parent / spec["review_file"]).resolve()
    model_hash = digest(source)
    approval = spec.get("approval", {})
    if not trial_only and (
        approval.get("authorized_by") != "human_user"
        or not approval.get("quote")
        or not approval.get("date")
        or approval.get("model_sha256") != model_hash
    ):
        raise ValueError("Record existing human approval for these exact model bytes")
    trial = spec.get("trial", {})
    if not trial_only and (
        trial.get("model_sha256") != model_hash
        or not trial.get("project_url")
        or not trial.get("tested_by")
        or not trial.get("tested_at")
        or not trial.get("evidence")
        or any(trial.get("checks", {}).get(k) is not True for k in TRIAL_CHECKS)
    ):
        raise ValueError("Complete the local student trial for these exact model bytes")
    import trimesh

    scene = trimesh.load(source, force="scene", process=False)
    model_rel = LIBRARY.parent / "models" / f"{candidate}.glb"
    review_rel = LIBRARY.parent / "evidence" / f"{candidate}.json"
    entry.update(
        runtime_enabled=True,
        activation=approval if not trial_only else {},
        local_trial=trial,
        local_trial_only=trial_only,
    )
    counts = _glb_counts(source)
    entry["model"] = {
        "path": f"models/{candidate}.glb",
        "bytes": source.stat().st_size,
        "sha256": model_hash,
        "native_dimensions_m": dict(zip(("width", "height", "depth"), map(float, scene.extents))),
        **{
            f"{k}_count": counts[v]
            for k, v in [("mesh", "meshes"), ("material", "materials"), ("texture", "textures"), ("image", "images")]
        },
    }
    entry["review"] = {
        "repo_path": review_rel.as_posix(),
        "sha256": digest(review),
        "status": "PASS_INDEPENDENT_ARCHITECTURAL_CLAY",
        "unresolved_p0": 0,
        "unresolved_p1": 0,
    }
    payload = check(root, allow_trials=True)
    # Never silently replace a published candidate, variant or saved picker ID.
    pending = None
    for old in payload["entries"]:
        if any(old[k] == entry[k] for k in ("candidate", "variant_id", "family")):
            if (
                not trial_only
                and old.get("local_trial_only")
                and old["candidate"] == candidate
                and old["model"]["sha256"] == model_hash
                and old["picker"]["id"] == entry["picker"]["id"]
                and old["variant_id"] == entry["variant_id"]
                and old["family"] == entry["family"]
            ):
                pending = old
            else:
                raise ValueError("Already published identity; revisions require an explicit migration")
    if pending is not None:
        payload["entries"].remove(pending)
    payload["entries"].append(entry)
    if not trial_only:
        payload["updated_at"] = approval["date"]
    output = picker_source(payload)
    validate_integration(payload, root)
    for dest in (model_rel, review_rel):
        if (root / dest).exists() and (
            pending is None or digest(root / dest) != digest(source if dest == model_rel else review)
        ):
            raise ValueError(f"Refusing to overwrite {dest}")
    # Validate only the new GLB/source references here; check() validated existing ones.
    with tempfile.TemporaryDirectory(prefix="cityprompt-promotion-") as temporary:
        scratch = Path(temporary)
        (scratch / model_rel).parent.mkdir(parents=True)
        (scratch / review_rel).parent.mkdir(parents=True)
        shutil.copyfile(source, scratch / model_rel)
        shutil.copyfile(review, scratch / review_rel)
        _validate_payload({**payload, "entries": [entry]}, clay_root=scratch / LIBRARY.parent, repo_root=root)
        validate_review(entry, scratch)
    paths = [model_rel, review_rel, LIBRARY, PICKER]
    if apply:
        # Roll back only our writes if any filesystem operation fails.
        backups = {p: (root / p).read_bytes() if (root / p).exists() else None for p in paths}
        try:
            for dest, src in ((model_rel, source), (review_rel, review)):
                (root / dest).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, root / dest)
            (root / LIBRARY).write_text(encoded(payload), encoding="utf-8", newline="\n")
            (root / PICKER).write_text(output, encoding="utf-8", newline="\n")
        except Exception:
            for path, original in backups.items():
                if original is None:
                    (root / path).unlink(missing_ok=True)
                else:
                    (root / path).write_bytes(original)
            raise
    return [p.as_posix() for p in paths]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("check", help="Verify exact GLBs, references, reviews and picker")
    verify.add_argument("--metadata-only", action="store_true", help="CI drift check; does not prove GLB hydration")
    sub.add_parser("sync", help="Regenerate picker from the canonical manifest")
    template = sub.add_parser(
        "template", help="Create an unapproved package skeleton using an existing entry as a shape example"
    )
    template.add_argument("output", type=Path)
    stage = sub.add_parser("prepare", help="Preflight one package; writes only with --apply")
    stage.add_argument("package", type=Path)
    stage.add_argument("--apply", action="store_true")
    trial = sub.add_parser("trial", help="Stage an independently reviewed local pilot; CI rejects it until promotion")
    trial.add_argument("package", type=Path)
    trial.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.command == "check":
        payload = check(REPO_ROOT, hydrated=not args.metadata_only)
        print(f"PASS: {len(payload['entries'])} buildings ({'metadata only' if args.metadata_only else 'hydrated'})")
    elif args.command == "sync":
        (REPO_ROOT / PICKER).write_text(picker_source(read(REPO_ROOT / LIBRARY)), encoding="utf-8", newline="\n")
        print(PICKER)
    elif args.command == "template":
        entry = copy.deepcopy(read(REPO_ROOT / LIBRARY)["entries"][0])
        for key in ("model", "review", "activation", "local_trial"):
            entry.pop(key, None)
        entry.update(
            candidate="replace-with-versioned-candidate",
            family="replace-with-exact-family",
            archetype_id="replace_with_parent",
            variant_id="replace_with_variant",
            archetype_label="Replace with parent label",
            variant_label="Replace with student label",
            external_evidence="Replace with durable evidence location",
        )
        entry["picker"]["id"] = "replace_with_stable_picker_id"
        spec = {
            "entry": entry,
            "model_file": "reviewed.glb",
            "review_file": "independent-review.json",
            "approval": {"authorized_by": "", "quote": "", "date": "", "model_sha256": ""},
            "trial": {
                "model_sha256": "",
                "project_url": "",
                "tested_by": "",
                "tested_at": "",
                "evidence": [],
                "checks": dict.fromkeys(TRIAL_CHECKS, False),
            },
        }
        with args.output.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded(spec))
        print(
            "Template only: replace identity, references, measurements and picker settings; record real review, trial and approval."
        )
    else:
        for path in prepare(REPO_ROOT, args.package.resolve(), apply=args.apply, trial_only=args.command == "trial"):
            print(path)
        print(
            "Applied. Run checks and local seed."
            if args.apply
            else "Dry run passed; no files changed. Add --apply to stage."
        )


if __name__ == "__main__":
    main()
