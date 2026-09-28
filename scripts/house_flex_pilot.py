#!/usr/bin/env python3
"""Verify or install the finite three-house flexibility pilot.

The two existing approved native assemblies remain byte-for-byte unchanged.
Installation adds a bounded placement-contract overlay to their database rows,
then adds the alternate complete assemblies. Halifax is installed as a new
two-assembly family because its reviewed source previously lived only in the
local validation catalogue.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "seed/model-library/rlasm-architectural-clay/house-flex-pilot-v001.json"
EXACT_FORMAT = "architectural_clay"
MODULE_FORMAT = "architectural_clay_module_v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_program(root: Path = ROOT) -> tuple[dict, list[dict]]:
    manifest_path = root / MANIFEST.relative_to(ROOT)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "cityprompt.authored-lowrise-storey-program@1":
        raise ValueError("Unknown low-rise storey programme schema")
    if manifest.get("supported_storeys") != {"minimum": 1, "maximum": 2}:
        raise ValueError("The pilot must remain a finite one-to-two-storey programme")

    footprint = manifest["footprint_contract"]
    if footprint != {
        "mode": "uniform_horizontal_scale",
        "minimum_scale": 0.85,
        "maximum_scale": 1.15,
        "default_scale": 1.0,
        "vertical_scale": 1.0,
        "max_axis_ratio": 1.0,
    }:
        raise ValueError("The reviewed uniform footprint band changed")

    rows: list[dict] = []
    for family in manifest["families"]:
        assemblies = family["assemblies"]
        if {assembly["storeys"] for assembly in assemblies} != {1, 2}:
            raise ValueError(f"{family['variant_id']} must provide complete one- and two-storey assemblies")
        heights = family["height_contract"]
        for assembly in assemblies:
            path = manifest_path.parent / assembly["path"]
            if path.stat().st_size != assembly["bytes"] or _sha256(path) != assembly["sha256"]:
                raise ValueError(f"Changed assembly bytes: {assembly['path']}")
            expected_height = heights["base_height_m"] + (
                assembly["storeys"] - heights["base_storeys"]
            ) * heights["additional_storey_height_m"]
            if abs(assembly["native_dimensions_m"][2] - expected_height) > 0.01:
                raise ValueError(f"Height contract drift: {assembly['path']}")

            native = assembly["status"] == "PASS_INDEPENDENT_ARCHITECTURAL_CLAY"
            filename = Path(assembly["path"]).name
            model_url = f"/api/v1/files/library/rlasm-house-flex/{filename}"
            scale_band = {
                "scaleMin": footprint["minimum_scale"],
                "scaleMax": footprint["maximum_scale"],
                "maxAxisRatio": footprint["max_axis_ratio"],
            }
            placement_contract = {
                "mode": "authored_storey_program",
                "continuous_resize_allowed": False,
                "storey_program_id": manifest["id"],
                "uniform_horizontal_scale_only": True,
                "vertical_scale": 1.0,
            }
            rlasm = {
                "method": "RLASM",
                "method_version": "6.1",
                "delivery_format": EXACT_FORMAT if native else MODULE_FORMAT,
                "runtime_enabled": True,
                "source_locked": True,
                "continuous_resize_allowed": False,
                "bounded_uniform_scale": True,
                "candidate": filename.removesuffix(".glb"),
                "variant_id": family["variant_id"],
                "archetype_id": family["archetype_id"],
                "model_sha256": assembly["sha256"],
                "storey_program_id": manifest["id"],
                "review_status": assembly["status"],
            }
            lego = {
                "enabled": True,
                "family": family["family"],
                "role": "assembled",
                "width_m": assembly["native_dimensions_m"][0],
                "depth_m": assembly["native_dimensions_m"][1],
                "height_m": assembly["native_dimensions_m"][2],
                "archetype_ids": [family["archetype_id"], family["variant_id"]],
                "reuse_keys": [family["variant_id"]],
                "min_floors": assembly["storeys"],
                "max_floors": assembly["storeys"],
                "native_floors": assembly["storeys"],
                "allowed_levels": [assembly["storeys"]],
                "repeatable_z": False,
                "variant_key": family["variant_id"],
                "lod": 0,
                "source_variant_id": family["variant_id"],
                "generation_archetype_id": family["variant_id"],
                "allow_inset_footprint": True,
                "placement_contract": placement_contract,
                "footprint_compatibility": {
                    "placementMode": "authored_storey_program",
                    "polygonFit": True,
                    "continuous_resize_allowed": False,
                    "fixedLandmarkScaleBand": scale_band,
                },
            }
            rows.append({
                "id": str(uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"https://cityprompt.ai/model-library/{manifest['id']}/{family['variant_id']}/{assembly['storeys']}",
                )),
                "variantId": family["variant_id"],
                "name": f"{family['variant_id']} — {assembly['storeys']} storey authored assembly",
                "model_url": model_url,
                "path": str(path),
                "native": native,
                "storeys": assembly["storeys"],
                "metadata": {"rlasm": rlasm, "lego": lego},
            })
    if len(rows) != 6:
        raise ValueError("Expected exactly six complete assemblies")
    return manifest, rows


def _object_status(client, bucket: str, row: dict) -> str:
    from botocore.exceptions import ClientError

    key = row["model_url"].removeprefix("/api/v1/files/")
    try:
        response = client.get_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in {"NoSuchKey", "404", "NotFound"}:
            return "missing"
        raise
    try:
        digest = hashlib.sha256()
        for block in iter(lambda: response["Body"].read(1024 * 1024), b""):
            digest.update(block)
    finally:
        response["Body"].close()
    return "verified" if digest.hexdigest() == row["metadata"]["rlasm"]["model_sha256"] else "conflict"


def synchronize(*, apply: bool, owner_id: uuid.UUID | None) -> list[dict]:
    _, rows = load_program()
    sys.path.insert(0, str(ROOT / "backend"))
    from app.core.config import get_settings
    from app.models.models import ModelLibraryEntry, User
    from app.services.render_attempt_storage import _client
    from sqlalchemy import create_engine, select, text
    from sqlalchemy.orm import Session

    settings = get_settings()
    client, bucket = _client()
    engine = create_engine(settings.database_url_sync)
    report: list[dict] = []
    try:
        with Session(engine) as database:
            if apply:
                if owner_id is None:
                    raise ValueError("Installation requires an existing owner")
                database.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": 23_140_785_570_743})
                owner = database.get(User, owner_id)
                if owner is None or not owner.is_active:
                    raise ValueError("Seed owner must be an existing active account")
            entries = list(database.scalars(select(ModelLibraryEntry)))
            for row in rows:
                matches = [entry for entry in entries if (
                    (entry.metadata_ or {}).get("lego", {}).get("source_variant_id") == row["variantId"]
                    and (entry.metadata_ or {}).get("lego", {}).get("role") == "assembled"
                    and (entry.metadata_ or {}).get("lego", {}).get("native_floors") == row["storeys"]
                    and entry.is_public
                )]
                if len(matches) > 1:
                    raise ValueError(f"Multiple active assemblies claim {row['variantId']} at {row['storeys']} storeys")
                existing = matches[0] if matches else None
                if existing is not None:
                    existing_sha = (existing.metadata_ or {}).get("rlasm", {}).get("model_sha256")
                    if existing_sha != row["metadata"]["rlasm"]["model_sha256"]:
                        raise ValueError(f"Existing assembly bytes differ for {row['variantId']} at {row['storeys']} storeys")
                    object_state = _object_status(client, bucket, {
                        **row,
                        "model_url": existing.model_url,
                    })
                    if object_state != "verified":
                        raise ValueError(f"Existing object is unavailable or changed for {row['variantId']}")
                    binding_state = "verified" if all(
                        (existing.metadata_ or {}).get("lego", {}).get(key) == row["metadata"]["lego"][key]
                        for key in ("family", "placement_contract", "footprint_compatibility")
                    ) else "needs_overlay"
                    if apply and binding_state == "needs_overlay":
                        metadata = dict(existing.metadata_ or {})
                        metadata["rlasm"] = {**metadata.get("rlasm", {}), **row["metadata"]["rlasm"]}
                        # Preserve the exact-source delivery type for native rows.
                        if row["native"]:
                            metadata["rlasm"]["delivery_format"] = EXACT_FORMAT
                        metadata["lego"] = {**metadata.get("lego", {}), **row["metadata"]["lego"]}
                        existing.metadata_ = metadata
                        binding_state = "installed"
                    report.append({
                        "variant": row["variantId"], "storeys": row["storeys"],
                        "binding": binding_state, "object": object_state,
                    })
                    continue

                object_state = _object_status(client, bucket, row)
                if object_state == "conflict":
                    raise ValueError(f"Stored object has different bytes for {row['variantId']}")
                binding_state = "missing"
                if apply:
                    if object_state == "missing":
                        key = row["model_url"].removeprefix("/api/v1/files/")
                        with Path(row["path"]).open("rb") as body:
                            client.put_object(
                                Bucket=bucket, Key=key, Body=body,
                                ContentType="model/gltf-binary", IfNoneMatch="*",
                            )
                        if _object_status(client, bucket, row) != "verified":
                            raise ValueError(f"Installed object failed readback for {row['variantId']}")
                        object_state = "installed"
                    entry = ModelLibraryEntry(
                        id=uuid.UUID(row["id"]), owner_id=owner_id, name=row["name"],
                        category="building", model_url=row["model_url"], lod_urls={"0": row["model_url"]},
                        generation_engine="rlasm", is_public=True,
                        tags=["rlasm", "architectural-clay", "house-flex", row["variantId"]],
                        metadata_=row["metadata"],
                    )
                    database.add(entry)
                    entries.append(entry)
                    binding_state = "installed"
                report.append({
                    "variant": row["variantId"], "storeys": row["storeys"],
                    "binding": binding_state, "object": object_state,
                })
            if apply:
                database.commit()
    finally:
        engine.dispose()
    return report


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
        print(f"Verified {manifest['id']} with {len(rows)} immutable complete assemblies")
        return 0
    report = synchronize(apply=args.install, owner_id=args.owner_id)
    print(json.dumps(report, indent=2))
    good_bindings = {"verified", "installed"}
    good_objects = {"verified", "installed"}
    return int(any(row["binding"] not in good_bindings or row["object"] not in good_objects for row in report))


if __name__ == "__main__":
    raise SystemExit(main())
