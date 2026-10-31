"""Exact retained runtime bounds; immutable GLB/library metadata stays untouched."""

from functools import lru_cache
import json
from pathlib import Path
from urllib.parse import urlsplit


@lru_cache(maxsize=1)
def building_only_envelopes():
    return json.loads((Path(__file__).resolve().parents[1] / "data/buildingOnlyEnvelopes.json").read_text())


def building_only_dimensions(revision, model_url, delivery_format, role):
    if delivery_format != "architectural_clay" or role != "assembled":
        return None
    if urlsplit(model_url).path != f"/api/v1/files/library/rlasm-architectural-clay/{revision}.glb":
        return None
    return retained_building_dimensions(revision)


def retained_building_dimensions(revision):
    row = building_only_envelopes().get(revision)
    if not row:
        return None
    lo, hi = row["bounds"]["min"], row["bounds"]["max"]
    return hi[0] - lo[0], hi[2] - lo[2], hi[1] - lo[1]
