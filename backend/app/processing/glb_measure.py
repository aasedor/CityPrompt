"""
Measure a GLB's native bounding box for the archetype model cache.

The stored values let the plan generator carve parcels matching the model's
real proportions: extents are in the GLB's NATIVE units (Meshy output is not
metric), so the useful quantities are the aspect ratio and the per-height
ratios — absolute metres are derived per placement as
`height_m * long_per_height`, mirroring the frontend height-anchoring in
buildingPlacement.ts (heightFit = height_meters / modelSize.y).

Axis convention: glTF is Y-up, so footprint = X x Z plane — the same
max/min(modelSize.x, modelSize.z) the globe placement uses.
"""

import io
import logging

logger = logging.getLogger(__name__)


def measure_glb(glb_bytes: bytes) -> dict | None:
    """Return native dimension metadata for a GLB, or None if unmeasurable.

    Fail-open contract like optimize_glb: callers treat None as "no dims
    available" — never raise for a malformed model.
    """
    try:
        import trimesh

        scene = trimesh.load(io.BytesIO(glb_bytes), file_type="glb")
        bounds = scene.bounds  # [[minx,miny,minz],[maxx,maxy,maxz]]
        if bounds is None:
            return None
        extents = bounds[1] - bounds[0]
        x, y, z = (float(extents[0]), float(extents[1]), float(extents[2]))
        if y <= 1e-6 or x <= 1e-6 or z <= 1e-6:
            logger.warning("GLB has degenerate extents (%s, %s, %s); skipping measurement", x, y, z)
            return None
        footprint_long = max(x, z)
        footprint_short = min(x, z)
        return {
            "native_x": round(x, 4),
            "native_y": round(y, 4),
            "native_z": round(z, 4),
            "footprint_long": round(footprint_long, 4),
            "footprint_short": round(footprint_short, 4),
            "aspect": round(footprint_long / footprint_short, 4),
            "long_per_height": round(footprint_long / y, 4),
            "short_per_height": round(footprint_short / y, 4),
        }
    except Exception as exc:
        logger.warning("GLB measurement failed (non-fatal): %s", exc)
        return None
