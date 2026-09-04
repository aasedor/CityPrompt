"""Server-owned plan snapshots for a validated render request.

The camera is captured by the client renderer, validated by the request schema
and bound to the control-image fingerprint. It is not independently measured
by the server. Persist that distinction rather than calling a client hash proof.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any, Iterable

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
        allow_nan=False,
    )


def revision_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _geometry(value: Any) -> dict | None:
    return (
        mapping(value if hasattr(value, "geom_type") else to_shape(value))
        if value is not None
        else None
    )


def build_render_source_snapshot(
    req: Any, zones: Iterable[Any], buildings: Iterable[Any], *, captured_at: str
) -> dict:
    """Call only after project scope and compiled claims pass server validation."""
    zone_ids = {str(claim.zone_id) for claim in req.community_3d_claims}
    if req.residual_landscape_claim:
        zone_ids.add(str(req.residual_landscape_claim.boundary_id))
    for descriptor in (req.instance_id_manifest or {}).values():
        if descriptor.zone_id:
            zone_ids.add(str(descriptor.zone_id))
        zone_ids.update(str(value) for value in descriptor.source_zone_ids)
    source_zones = []
    building_ids = set()
    for zone in sorted(zones, key=lambda item: str(item.id)):
        if str(zone.id) not in zone_ids:
            continue
        linked_ids = list(getattr(zone, "building_ids", None) or [])
        if getattr(zone, "building_id", None):
            linked_ids.append(str(zone.building_id))
        building_ids.update(str(value) for value in linked_ids)
        source_zones.append(
            {
                "id": str(zone.id),
                "name": getattr(zone, "name", None),
                "zone_type": zone.zone_type,
                "geometry": _geometry(zone.geometry),
                "properties": dict(zone.properties or {}),
                "is_active_boundary": bool(getattr(zone, "is_active_boundary", False)),
                "building_ids": sorted(set(str(value) for value in linked_ids)),
            }
        )
    missing = zone_ids - {zone["id"] for zone in source_zones}
    if missing:
        raise ValueError("Validated render snapshot references missing project zones")
    source_buildings = []
    for building in sorted(buildings, key=lambda item: str(item.id)):
        if str(building.id) not in building_ids:
            continue
        source_buildings.append(
            {
                "id": str(building.id),
                "footprint": _geometry(getattr(building, "footprint", None)),
                **{
                    key: getattr(building, key, None)
                    for key in (
                        "name",
                        "height_meters",
                        "floor_count",
                        "floor_height_meters",
                        "roof_type",
                        "rotation_degrees",
                        "generation_engine",
                        "model_url",
                        "lod_urls",
                        "specifications",
                    )
                },
            }
        )
    if building_ids - {building["id"] for building in source_buildings}:
        raise ValueError(
            "Validated render snapshot references missing linked buildings"
        )
    plan = json.loads(
        canonical_json(
            {
                "project_id": str(req.project_id),
                "zones": source_zones,
                "buildings": source_buildings,
            }
        )
    )
    camera = req.camera.model_dump(mode="json") if req.camera is not None else None
    capture = {
        "camera": camera,
        "view_mode": req.view_mode,
        "control_bundle_version": req.control_bundle_version,
    }
    return {
        "schema_version": 1,
        "captured_at": captured_at,
        "plan_revision_sha256": revision_sha256(plan),
        "camera_revision_sha256": revision_sha256(capture)
        if camera is not None
        else None,
        "plan": plan,
        "capture": capture,
        "camera_evidence": "validated_client_capture_manifest"
        if camera is not None
        else "not_supplied",
        "plan_evidence": "server_project_state_after_claim_validation",
        "scope": "rendered_zones_and_linked_buildings",
    }
