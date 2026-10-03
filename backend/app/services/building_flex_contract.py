"""Trusted finite low-rise footprint contracts.

Client properties identify a selected programme and scale, but do not define
native dimensions or limits.  Those values come only from the repository's
hash-pinned manifest so a saved zone cannot enlarge an arbitrary model by
supplying its own claimed approval band.
"""

from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "seed/model-library/rlasm-architectural-clay/house-flex-pilot-v001.json"


@lru_cache(maxsize=1)
def _contracts() -> tuple[str, float, float, dict[str, tuple[float, float]]]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if payload.get("schema") != "cityprompt.authored-lowrise-storey-program@1":
        raise ValueError("Unknown low-rise building programme schema")
    footprint = payload["footprint_contract"]
    if footprint.get("mode") != "uniform_horizontal_scale" or footprint.get("vertical_scale") != 1.0:
        raise ValueError("Low-rise programme must retain unit vertical scale")
    minimum = float(footprint["minimum_scale"])
    maximum = float(footprint["maximum_scale"])
    if not (0.75 <= minimum <= 1.0 <= maximum <= 1.25):
        raise ValueError("Low-rise footprint band is outside the bounded runtime range")
    families: dict[str, tuple[float, float]] = {}
    for family in payload["families"]:
        assemblies = family["assemblies"]
        widths = {round(float(row["native_dimensions_m"][0]), 6) for row in assemblies}
        depths = {round(float(row["native_dimensions_m"][1]), 6) for row in assemblies}
        if len(widths) != 1 or len(depths) != 1:
            raise ValueError(f"Storey assemblies changed footprint for {family['variant_id']}")
        families[str(family["variant_id"])] = (float(assemblies[0]["native_dimensions_m"][0]), float(assemblies[0]["native_dimensions_m"][1]))
    return str(payload["id"]), minimum, maximum, families


def trusted_house_footprint_target(properties: dict[str, Any]) -> tuple[float, float] | None:
    """Return trusted model dimensions for a declared pilot scale.

    A missing or unrelated programme remains on the ordinary drawn-footprint
    path.  A known programme with an invalid variant or scale fails closed.
    """

    program_id, minimum, maximum, families = _contracts()
    declared = properties.get("building_footprint_program_id")
    if declared != program_id:
        return None
    variant = properties.get("development_selected_variant_id")
    if not isinstance(variant, str) or variant not in families:
        raise ValueError("The selected building is not part of this footprint programme")
    try:
        scale = float(properties["building_footprint_scale"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("The building footprint scale is missing or invalid") from exc
    if not math.isfinite(scale) or not minimum <= scale <= maximum:
        raise ValueError("The building footprint scale is outside the reviewed range")
    width, depth = families[variant]
    # Retain the hash-pinned GLB dimensions at full precision. Rounding a
    # target on the edge of the approved band (for example 115%) can move the
    # recomputed ratio a few millionths above the limit and make a freshly
    # planned recipe look different during the server's final lock check.
    return width * scale, depth * scale
