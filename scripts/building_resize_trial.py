#!/usr/bin/env python3
"""Verify the building resize pilot. Dry-run by default; installs nothing.

The pilot stretches one exact, reviewed mid-rise model. Its contract is a
hash-pinned repository file, so there is no database row to create or change:

    frontend/src/data/buildingResizeTrial.json   (the single tuning file)
    backend/app/data/buildingResizeTrial.json    (byte-identical server copy)

Default run (no flags) reads repository files only. It checks the tuning file,
the server copy, the pin against the reviewed clay library, and the model
bytes (or their Git LFS pointer). It opens no network or database connection.

    python scripts/building_resize_trial.py
    python scripts/building_resize_trial.py --write-mirror
    python scripts/building_resize_trial.py --check-database

``--write-mirror`` rewrites the server copy from the tuning file. It touches
one repository file and nothing else.

``--check-database`` is a read-only readback of the already-installed library
row and its stored object, for a local session to confirm that the pinned
model is the one the planner will see. It never writes. Run it only against
your own local database.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUNING_FILE = Path("frontend/src/data/buildingResizeTrial.json")
SERVER_COPY = Path("backend/app/data/buildingResizeTrial.json")
CLAY_ROOT = Path("seed/model-library/rlasm-architectural-clay")
SCHEMA = "cityprompt.building-resize-trial@1"
PROGRAM_ID = "building-resize-trial-v001"
# Mirrors backend/app/services/building_flex_contract.py; a test keeps them equal.
SCALE_FLOOR = 0.5
SCALE_CEILING = 1.6
APPROVED_REVIEW = "PASS_INDEPENDENT_ARCHITECTURAL_CLAY"
_LFS_POINTER = re.compile(rb"^version https://git-lfs\.github\.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize (\d+)\n?$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def model_state(path: Path, sha256: str, size: int) -> str:
    """``verified`` for exact bytes, ``lfs_pointer`` for the matching pointer.

    A pointer proves which bytes Git LFS will deliver without downloading them.
    Anything else is a changed or missing model and fails verification.
    """

    if not path.is_file():
        raise ValueError(f"Missing trial model: {path}")
    if path.stat().st_size < 1024:
        pointer = _LFS_POINTER.match(path.read_bytes())
        if pointer:
            if pointer.group(1).decode() != sha256 or int(pointer.group(2)) != size:
                raise ValueError(f"Git LFS pointer names different bytes: {path}")
            return "lfs_pointer"
    if path.stat().st_size != size or _sha256(path) != sha256:
        raise ValueError(f"Changed trial model bytes: {path}")
    return "verified"


def load_trial(root: Path = ROOT, *, require_mirror: bool = True) -> tuple[dict, list[dict]]:
    """Validate the pilot contract offline and return it with one row per model."""

    tuning_path = root / TUNING_FILE
    manifest = json.loads(tuning_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA or manifest.get("id") != PROGRAM_ID:
        raise ValueError("Unknown building resize trial manifest")
    if manifest.get("status") != "LOCAL_TRIAL_ONLY":
        raise ValueError("The resize trial must stay a local trial; it publishes nothing")
    if require_mirror and (root / SERVER_COPY).read_bytes() != tuning_path.read_bytes():
        raise ValueError("The server copy differs from the tuning file. Run with --write-mirror.")

    stretch = manifest["stretch"]
    if stretch.get("mode") != "independent_horizontal_scale" or stretch.get("vertical_scale") != 1.0:
        raise ValueError("The resize trial must keep unit vertical scale")
    minimum, maximum = float(stretch["minimum_scale"]), float(stretch["maximum_scale"])
    if not (SCALE_FLOOR <= minimum <= 1.0 <= maximum <= SCALE_CEILING) or stretch.get("default_scale") != 1.0:
        raise ValueError("The resize trial band is outside the bounded runtime range")
    step = float(stretch["step"])
    if not 0 < step <= 0.25:
        raise ValueError("The resize trial step is invalid")
    margin = stretch.get("fit_plot_margin_m")
    if margin is not None and not 0 <= float(margin) <= 10:
        raise ValueError("The fit margin is invalid")
    if not isinstance(stretch.get("squeeze_on_plot_resize"), bool):
        raise ValueError("squeeze_on_plot_resize must be true or false")
    rigid = stretch.get("rigid_prop_materials")
    if (
        not isinstance(rigid, list)
        or any(not isinstance(name, str) or not name for name in rigid)
        or not 0 < float(stretch["rigid_prop_max_size_m"]) <= 10
    ):
        raise ValueError("The rigid prop settings are invalid")

    shape = manifest["shape_freely"]
    if not (
        0 < float(shape["minimum_width_m"]) <= float(shape["maximum_size_m"])
        and 0 < float(shape["minimum_depth_m"]) <= float(shape["maximum_size_m"])
        and float(shape["minimum_area_m2"]) > 0
        and 4 <= int(shape["maximum_outline_points"]) <= 128
    ):
        raise ValueError("The Shape freely limits are invalid")

    massing = manifest["massing"]
    if not (
        0 < float(massing["window_width_m"]) < float(massing["bay_module_m"])
        and float(massing["window_height_m"]) > 0
        and float(massing["window_sill_m"]) >= 0
        and float(massing["wall_end_margin_m"]) >= 0
        and float(massing["floor_line_height_m"]) > 0
        and float(massing["surface_offset_m"]) > 0
    ):
        raise ValueError("The massing dressing settings are invalid")
    spacing = massing.get("floor_line_spacing_m")
    if spacing is not None and not float(spacing) > 0:
        raise ValueError("The floor line spacing is invalid")
    if massing.get("style") not in {"archetype_kit", "floor_lines_and_windows"}:
        raise ValueError("Unknown massing style")
    kit = massing["kit"]
    lengths = [value for key, value in kit.items() if key.endswith("_m")]
    colors = kit["colors"]
    if (
        len(lengths) < 18
        or any(isinstance(value, bool) or not float(value) > 0 for value in lengths)
        or not float(kit["window_width_m"]) < float(kit["window_bay_module_m"])
        or not float(kit["loggia_width_m"]) < float(kit["loggia_bay_module_m"])
        or not float(kit["loggia_height_m"]) < float(kit["upper_floor_height_m"])
        or not float(kit["window_sill_m"]) + float(kit["window_height_m"]) < float(kit["upper_floor_height_m"])
        or len(colors) != 12
        or any(not re.fullmatch(r"#[0-9a-f]{6}", str(color)) for color in colors.values())
    ):
        raise ValueError("The facade kit settings are invalid")

    library = json.loads((root / CLAY_ROOT / "library.json").read_text(encoding="utf-8"))
    entries = {entry["candidate"]: entry for entry in library["entries"]}
    rows: list[dict] = []
    for family in manifest["families"]:
        entry = entries.get(family["candidate"])
        if entry is None:
            raise ValueError(f"The trial model is not in the reviewed clay library: {family['candidate']}")
        native = entry["model"]["native_dimensions_m"]
        review = entry["review"]
        if (
            entry.get("runtime_enabled") is not True
            or review.get("status") != APPROVED_REVIEW
            or review.get("unresolved_p0") != 0
            or review.get("unresolved_p1") != 0
        ):
            raise ValueError(f"The trial model has no clean independent review: {family['candidate']}")
        if (
            entry["variant_id"] != family["variant_id"]
            or entry["archetype_id"] != family["archetype_id"]
            or entry["family"] != family["family"]
            or entry["picker"]["id"] != family["asset_id"]
            or entry["model"]["path"] != family["path"]
            or entry["model"]["sha256"] != family["sha256"]
            or entry["model"]["bytes"] != family["bytes"]
            or int(entry["native_floors"]) != family["native_storeys"]
            or [native["width"], native["depth"], native["height"]] != family["native_dimensions_m"]
            or [entry["picker"]["width"], entry["picker"]["depth"]] != family["placement_plot_m"]
        ):
            raise ValueError(f"The trial pin drifted from the reviewed library: {family['candidate']}")
        width, depth, height = family["native_dimensions_m"]
        plot_width, plot_depth = family["placement_plot_m"]
        if plot_width < width or plot_depth < depth:
            raise ValueError(f"The placement plot is smaller than the model: {family['candidate']}")
        state = model_state(root / CLAY_ROOT / family["path"], family["sha256"], family["bytes"])
        rows.append(
            {
                "asset_id": family["asset_id"],
                "variant_id": family["variant_id"],
                "candidate": family["candidate"],
                "sha256": family["sha256"],
                "model": state,
                "native_m": [round(width, 3), round(depth, 3), round(height, 3)],
                "stretch_width_m": [round(width * minimum, 2), round(width * maximum, 2)],
                "stretch_depth_m": [round(depth * minimum, 2), round(depth * maximum, 2)],
                "storeys": family["native_storeys"],
                "height_scale": 1.0,
            }
        )
    if len(rows) != 1:
        raise ValueError("The pilot covers exactly one building")
    return manifest, rows


def write_mirror(root: Path = ROOT) -> bool:
    """Copy the tuning file over the server copy. Returns True when it changed."""

    load_trial(root, require_mirror=False)
    source = (root / TUNING_FILE).read_bytes()
    target = root / SERVER_COPY
    if target.is_file() and target.read_bytes() == source:
        return False
    target.write_bytes(source)
    return True


def check_database() -> list[dict]:
    """Read-only readback of the installed library rows. Never writes."""

    _, rows = load_trial()
    sys.path.insert(0, str(ROOT / "backend"))
    from app.core.config import get_settings
    from app.models.models import ModelLibraryEntry
    from app.services.building_flex_contract import _resize_trial_manifest
    from app.services.lego_assembly import descriptor_from_library_entry
    from app.services.render_attempt_storage import _client
    from botocore.exceptions import ClientError
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    settings = get_settings()
    contract = _resize_trial_manifest()
    client, bucket = _client()
    engine = create_engine(settings.database_url_sync)
    report: list[dict] = []
    try:
        with Session(engine) as database:
            entries = list(database.scalars(select(ModelLibraryEntry).where(ModelLibraryEntry.is_public.is_(True))))
            for row in rows:
                matches = [
                    entry
                    for entry in entries
                    if (descriptor := descriptor_from_library_entry(entry)) is not None
                    and contract.family_for_module(descriptor) is not None
                    and descriptor.source_variant_id == row["variant_id"]
                ]
                objects = []
                for entry in matches:
                    key = entry.model_url.removeprefix("/api/v1/files/")
                    try:
                        body = client.get_object(Bucket=bucket, Key=key)["Body"]
                    except ClientError as exc:
                        if exc.response["Error"]["Code"] in {"NoSuchKey", "404", "NotFound"}:
                            objects.append("missing")
                            continue
                        raise
                    try:
                        digest = hashlib.sha256()
                        for block in iter(lambda: body.read(1024 * 1024), b""):
                            digest.update(block)
                    finally:
                        body.close()
                    objects.append("verified" if digest.hexdigest() == row["sha256"] else "conflict")
                report.append(
                    {
                        "variant": row["variant_id"],
                        "candidate": row["candidate"],
                        "matching_rows": len(matches),
                        "binding": "verified" if matches else "missing",
                        "object": (
                            "missing"
                            if not objects or "missing" in objects
                            else "conflict" if "conflict" in objects else "verified"
                        ),
                        "server_flag": bool(settings.enable_building_resize_trial),
                    }
                )
            database.rollback()
    finally:
        engine.dispose()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write-mirror", action="store_true", help="rewrite the server copy from the tuning file")
    mode.add_argument("--check-database", action="store_true", help="read-only readback of the installed row")
    args = parser.parse_args(argv)
    if args.write_mirror:
        changed = write_mirror()
        print("Server copy updated." if changed else "Server copy already matches the tuning file.")
        return 0
    if args.check_database:
        report = check_database()
        print(json.dumps(report, indent=2))
        return int(any(row["binding"] != "verified" or row["object"] != "verified" for row in report))
    manifest, rows = load_trial()
    print(f"Dry run. Verified {manifest['id']} offline; nothing was installed or changed.")
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
