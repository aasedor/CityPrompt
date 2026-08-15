"""Canonical identity for a compiled City Prompt scene revision."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable


def _json_value(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    raise TypeError("Scene revision claims must be mappings or Pydantic models")


def compiled_scene_revision_sha256(
    community_3d_claims: Iterable[Any],
    residual_landscape_claim: Any | None,
) -> str:
    """Hash exact zone/model claims and the optional residual parcel recipe.

    Claim ordering is deliberately ignored so image and video outputs created
    from the same compiled scene share one durable revision identifier.
    """

    claims = sorted(
        (_json_value(claim) for claim in community_3d_claims),
        key=lambda claim: str(claim.get("zone_id", "")),
    )
    if not claims:
        raise ValueError("A compiled scene revision requires zone claims")
    identity = {
        "community_3d": claims,
        "residual_landscape": (_json_value(residual_landscape_claim) if residual_landscape_claim is not None else None),
    }
    return hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
