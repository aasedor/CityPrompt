"""Finite, source-locked bridge modules using the native street recipe contract."""

import hashlib
import json
import math
import re
from functools import lru_cache
from pathlib import Path
from app.services.native_street_registry import load_native_street_rows
from app.services.native_source_bridge import SOURCE_BRIDGE_SOURCES, validate_source_bridge_profile


MANIFEST = Path(__file__).resolve().parents[1] / "data/nativeStreetPilots.json"
MODULAR_BRIDGE_IDENTITIES = {
    "timber_covered_bridge_route_v1": ("urban_pedestrian_footbridge", 6),
    **{key: (value[0], None) for key, value in SOURCE_BRIDGE_SOURCES.items()},
}
MODULE_KINDS = {"bridge_left_stair", "bridge_left_end", "bridge_bay", "bridge_right_end", "bridge_right_stair"}
BRIDGE_FIELDS = {"approachM", "endM", "bayM", "deckHeightM", "clearWidthM"}
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def is_modular_bridge(properties):
    return (properties or {}).get("road_selected_variant_id") in MODULAR_BRIDGE_IDENTITIES


def modular_bridge_route_length(route):
    """Use the authored route datum rather than a second projected length."""
    sx = 111320 * math.cos(math.radians(route[0][1]))
    return math.hypot((route[-1][0] - route[0][0]) * sx, (route[-1][1] - route[0][1]) * 111320)


def validate_modular_bridge_profile(row):
    """Reject incomplete or unsupported source-module adapters before execution."""
    program = row.get("program")
    variant = row.get("id")
    if (
        variant in SOURCE_BRIDGE_SOURCES
        or isinstance(program, dict)
        and program.get("adapter") == "source-span-bridge-v1"
    ):
        validate_source_bridge_profile(row)
        return
    if variant not in MODULAR_BRIDGE_IDENTITIES and (
        not isinstance(program, dict) or program.get("adapter") != "modular-bridge-v1"
    ):
        return
    expected = MODULAR_BRIDGE_IDENTITIES.get(variant)
    if (
        expected is None
        or row.get("sourceArchetypeId") != expected[0]
        or row.get("widthM") != expected[1]
        or not isinstance(program, dict)
        or program.get("adapter") != "modular-bridge-v1"
        or row.get("routeAxis") != "local_y"
        or row.get("placements") != []
        or program.get("surfaceRegions") not in (None, [])
    ):
        raise ValueError("Modular bridge needs its trusted catalogue identity and native module-only program.")
    bridge = program.get("bridge")
    if not isinstance(bridge, dict) or set(bridge) != BRIDGE_FIELDS:
        raise ValueError("Modular bridge needs its complete measured structural dimensions.")
    values = [*bridge.values(), program.get("minLengthM"), program.get("maxLengthM")]
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for value in values
    ):
        raise ValueError("Modular bridge dimensions must be finite metres.")
    if (
        any(value <= 0 for value in values)
        or bridge["clearWidthM"] > row["widthM"]
        or program["minLengthM"] <= 2 * (bridge["approachM"] + bridge["endM"])
        or program["minLengthM"] > program["maxLengthM"]
    ):
        raise ValueError("Modular bridge dimensions must retain complete approaches, ends and a positive main span.")
    modules = row.get("modules")
    if not isinstance(modules, dict) or set(modules) != MODULE_KINDS:
        raise ValueError("Modular bridge needs exactly its five locked native structural modules.")
    locks = [
        row.get(name) for name in ("sourceRecipeSha256", "sourceAssemblySha256", "referenceSha256", "programSha256")
    ]
    for kind, module in modules.items():
        if not isinstance(module, dict) or module.get("url") != f"/street-kits/pilots/{variant}/{kind}.glb":
            raise ValueError("Modular bridge module identity is invalid.")
        locks.append(module.get("sha256"))
    digest = hashlib.sha256(json.dumps(program, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if (
        any(not isinstance(value, str) or not _SHA256.fullmatch(value) for value in locks)
        or row["programSha256"] != digest
    ):
        raise ValueError("Modular bridge source, program or module hash is invalid.")


@lru_cache(maxsize=1)
def modular_bridge_profiles():
    profiles = {}
    for row in load_native_street_rows(MANIFEST):
        program = row.get("program")
        if row.get("id") in MODULAR_BRIDGE_IDENTITIES or (
            isinstance(program, dict) and program.get("adapter") in {"modular-bridge-v1", "source-span-bridge-v1"}
        ):
            validate_modular_bridge_profile(row)
            if row["id"] in profiles or row.get("status") != "candidate":
                raise ValueError("Modular bridge source manifest identity or status is invalid.")
            profiles[row["id"]] = row
    return profiles


def modular_bridge_profile(variant_id):
    profile = modular_bridge_profiles().get(variant_id)
    if profile is None:
        raise ValueError("This modular bridge has no trusted executable source profile.")
    return profile
