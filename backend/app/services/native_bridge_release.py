"""Exact scoped bridge publication receipts, separate from executable candidates."""

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.services.native_street_registry import load_native_street_rows

MANIFEST = Path(__file__).resolve().parents[1] / "data/nativeBridgeRelease.json"
SHA = re.compile(r"[a-f0-9]{64}\Z")


def released_bridge_profiles(manifest=None):
    payload = json.loads(Path(manifest or MANIFEST).read_text(encoding="utf-8"))
    if (
        payload.get("schema") != "cityprompt.native-bridge-release@1"
        or payload.get("authorization", {}).get("approvedBy") != "human_user"
    ):
        raise ValueError("Native bridge production release authorization is invalid.")
    sources = {row["id"]: row for row in load_native_street_rows()}
    profiles = {}
    for entry in payload.get("entries", []):
        profile = entry.get("profile", {})
        canonical = entry.get("profileCanonical", "")
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        runtime, visual = entry.get("runtimeReview", {}), entry.get("sourceVisualReview", {})
        if (
            entry.get("status") != "ready_for_production_pilot"
            or profile.get("status") != "candidate"
            or profile != sources.get(profile.get("id"))
            or json.loads(canonical) != profile
            or entry.get("profileSha256") != digest
            or runtime.get("status") != "prepared_level_scoped_pass"
            or runtime.get("profileSha256") != digest
            or visual.get("status") != "architectural_clay_pass"
            or visual.get("sourceAssemblySha256") != profile.get("sourceAssemblySha256")
            or any(
                not SHA.fullmatch(str(record.get("sha256", "")))
                for record in (runtime, visual, entry.get("provenance", {}))
            )
            or profile.get("id") in profiles
        ):
            raise ValueError("Native bridge production release disagrees with its exact source or review locks.")
        profiles[profile["id"]] = profile
    return profiles


@lru_cache(maxsize=1)
def _released_bridge_ids():
    return frozenset(released_bridge_profiles())


def native_bridge_available(variant):
    return get_settings().app_env.lower() == "development" or variant in _released_bridge_ids()
