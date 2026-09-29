#!/usr/bin/env python3
"""Verify or install the finite Vancouver tower authored-storey modules.

The default command is offline and only verifies the immutable source/module
hashes.  ``--verify`` reads the configured loopback database and object store;
``--install`` adds missing rows and objects without overwriting conflicts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "seed/model-library/rlasm-architectural-clay/vancouverism-classic-storey-program-v001.json"
FAMILY = "vancouver-balcony-podium-tower"
VARIANT = "vancouverism_classic"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_program(root: Path = ROOT) -> tuple[dict, list[dict]]:
    manifest = json.loads((root / MANIFEST.relative_to(ROOT)).read_text(encoding="utf-8"))
    if manifest.get("schema") != "cityprompt.authored-building-storey-program@1":
        raise ValueError("Unknown authored-storey programme schema")
    source = manifest["source"]
    if source["variant_id"] != VARIANT or source["native_storeys"] != 16:
        raise ValueError("The programme no longer identifies the reviewed Vancouver source")
    source_path = MANIFEST.parent / source["path"]
    if _sha256(source_path) != source["sha256"]:
        raise ValueError("Reviewed Vancouver source bytes changed")
    roles = {module["role"] for module in manifest["modules"]}
    if roles != {"podium", "floor", "roof"}:
        raise ValueError("Expected exactly podium, floor and roof modules")

    rows: list[dict] = []
    for module in manifest["modules"]:
        path = MANIFEST.parent / module["path"]
        if path.stat().st_size != module["bytes"] or _sha256(path) != module["sha256"]:
            raise ValueError(f"Changed authored module: {module['role']}")
        width, depth, height = module["native_dimensions_m"]
        model_url = f"/api/v1/files/library/rlasm-vertical-modules/{path.name}"
        role = module["role"]
        rlasm = {
            "method": "RLASM",
            "method_version": "6.1",
            "delivery_format": "architectural_clay_module_v1",
            "runtime_enabled": True,
            "source_locked": True,
            "continuous_resize_allowed": False,
            "candidate": source["candidate"],
            "variant_id": VARIANT,
            "source_model_sha256": source["sha256"],
            "model_sha256": module["sha256"],
            "storey_program_id": manifest["id"],
            "source_vertical_band_m": module["source_vertical_band_m"],
        }
        lego = {
            "enabled": True,
            "family": FAMILY,
            "role": role,
            "width_m": width,
            "depth_m": depth,
            "height_m": height,
            "archetype_ids": ["vancouverism_tower_podium", VARIANT],
            "reuse_keys": [VARIANT],
            "min_floors": manifest["supported_storeys"]["minimum"],
            "max_floors": manifest["supported_storeys"]["maximum"],
            "repeatable_z": role == "floor",
            "variant_key": VARIANT,
            "lod": 0,
            "occupied_storeys": module["occupied_storeys"],
            "source_variant_id": VARIANT,
            "generation_archetype_id": VARIANT,
            "allow_inset_footprint": True,
            "placement_contract": {
                "mode": "authored_storey_program",
                "continuous_resize_allowed": False,
                "storey_program_id": manifest["id"],
            },
        }
        rows.append({
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://cityprompt.ai/model-library/{manifest['id']}/{role}")),
            "variantId": VARIANT,
            "name": f"Vancouver balcony and podium tower — {role.title()} module",
            "model_url": model_url,
            "metadata": {"rlasm": rlasm, "lego": lego},
            "modelDependency": f"vancouver-module:{role}",
        })
    return manifest, rows


def synchronize(*, apply: bool, owner_id: uuid.UUID | None) -> list[dict]:
    manifest, rows = load_program()
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "backend"))
    from app.core.config import get_settings
    from app.services.render_attempt_storage import _client
    from scripts.classroom_model_library import object_matches, synchronize as sync_rows, validate_target
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    settings = get_settings()
    validate_target(settings, {}, local_trial=True)
    dependencies = []
    for module in manifest["modules"]:
        dependencies.append({
            "id": f"vancouver-module:{module['role']}",
            "path": str(MANIFEST.parent.relative_to(ROOT) / module["path"]),
        })
    client, bucket = _client()
    engine = create_engine(settings.database_url_sync)
    try:
        with Session(engine) as database:
            # The picker and the native 16-storey layout still load the reviewed
            # source assembly directly. Verify and restore those immutable bytes
            # alongside the three authored modules so a successful install cannot
            # leave placement previews or the native layout invisible.
            source = manifest["source"]
            source_path = MANIFEST.parent / source["path"]
            source_row = {
                "model_url": f"/api/v1/files/library/rlasm-architectural-clay/{source_path.name}",
                "metadata": {"rlasm": {"model_sha256": source["sha256"]}},
            }
            source_status = object_matches(client, bucket, source_row)
            if source_status == "conflict":
                raise ValueError("Stored Vancouver source has different bytes; it was not overwritten")

            preflight = sync_rows(
                database,
                client,
                bucket,
                {"dependencies": dependencies},
                rows,
                apply=False,
                owner_id=owner_id,
                root=ROOT,
            )
            if not apply:
                return [{
                    "variant": VARIANT,
                    "role": "source",
                    "binding": "verified",
                    "object": source_status,
                }, *preflight]

            if source_status == "missing":
                key = source_row["model_url"].removeprefix("/api/v1/files/")
                with source_path.open("rb") as body:
                    client.put_object(
                        Bucket=bucket,
                        Key=key,
                        Body=body,
                        ContentType="model/gltf-binary",
                        IfNoneMatch="*",
                    )
                if object_matches(client, bucket, source_row) != "verified":
                    raise ValueError("Installed Vancouver source failed exact byte readback")

            installed = sync_rows(
                database,
                client,
                bucket,
                {"dependencies": dependencies},
                rows,
                apply=True,
                owner_id=owner_id,
                root=ROOT,
            )
            return [{
                "variant": VARIANT,
                "role": "source",
                "binding": "verified",
                "object": object_matches(client, bucket, source_row),
            }, *installed]
    finally:
        engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--install", action="store_true")
    parser.add_argument("--owner-id", type=uuid.UUID)
    args = parser.parse_args()
    if args.install and args.owner_id is None:
        parser.error("--install requires an existing local --owner-id")
    manifest, rows = load_program()
    if not args.verify and not args.install:
        print(f"Verified {manifest['id']} with {len(rows)} immutable modules")
        return 0
    report = synchronize(apply=args.install, owner_id=args.owner_id)
    print(json.dumps(report, indent=2))
    return int(any(row["binding"] != "verified" or row["object"] != "verified" for row in report))


if __name__ == "__main__":
    raise SystemExit(main())
