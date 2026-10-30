"""Shared source rows; the bounded bridge pilot has a separate delivery file."""

import json
from functools import lru_cache
from pathlib import Path


NATIVE_STREET_MANIFEST = Path(__file__).resolve().parents[1] / "data/nativeStreetPilots.json"


def _manifest_rows(path):
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Native street manifest must contain a list of source rows")
    return tuple(rows)


def _load_rows(manifest_path):
    """Combine canonical siblings; standalone review manifests remain isolated."""
    manifest_path = Path(manifest_path)
    paths = [manifest_path]
    if manifest_path.name == "nativeStreetPilots.json":
        supplement = manifest_path.with_name("nativeBridgePilots.json")
        if supplement.exists():
            paths.append(supplement)
    rows = []
    for path in paths:
        rows.extend(_manifest_rows(path))
    return rows


@lru_cache(maxsize=1)
def _runtime_rows():
    return _load_rows(NATIVE_STREET_MANIFEST)


def load_native_street_rows(manifest_path=NATIVE_STREET_MANIFEST):
    # Runtime registries are immutable for this process. Explicit review files
    # must read fresh bytes, including same-size edits made within one tick.
    if Path(manifest_path).resolve() == NATIVE_STREET_MANIFEST.resolve():
        return list(_runtime_rows())
    return _load_rows(manifest_path)


@lru_cache(maxsize=1)
def native_street_roster():
    return json.loads(NATIVE_STREET_MANIFEST.with_name("classroomStarter.json").read_text(encoding="utf-8"))
