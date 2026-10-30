import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.backend_test_assets import fixture_assets, verify


def test_finite_inventory_covers_the_real_binary_fixture_families():
    assets = fixture_assets()
    assert 30 < len(assets) <= 80
    assert "seed/classroom-release/models/calgary-infill-flat-roof-minimal-clay-v006.glb" in assets
    assert sum(p.startswith("seed/model-library/objects/claude-five/models/") for p in assets) == 5
    assert sum(p.startswith("seed/model-library/rlasm-architectural-clay/models/") for p in assets) == 7
    assert len(assets) == len(set(assets))
    assert all(len(sha) == 64 for sha in assets.values())


def test_finite_inventory_covers_all_five_locked_native_bridge_modules():
    root = Path(__file__).resolve().parents[2]
    pilots = json.loads((root / "backend/app/data/nativeBridgePilots.json").read_text(encoding="utf-8"))
    assert len(pilots) == 1
    pilot = pilots[0]
    expected_kinds = {"bridge_left_stair", "bridge_left_end", "bridge_bay", "bridge_right_end", "bridge_right_stair"}
    assert set(pilot["modules"]) == expected_kinds
    prefix = "frontend/public/street-kits/pilots/timber_covered_bridge_route_v1/"
    expected = {f"{prefix}{kind}.glb": pilot["modules"][kind]["sha256"] for kind in expected_kinds}
    assets = fixture_assets()
    assert {path: sha for path, sha in assets.items() if path.startswith(prefix)} == expected
    assert len(assets) == 43


def test_verification_rejects_pointer_and_wrong_bytes(tmp_path):
    path = tmp_path / "model.glb"
    wanted = hashlib.sha256(b"glTF approved fixture").hexdigest()
    path.write_bytes(b"version https://git-lfs.github.com/spec/v1\noid sha256:example")
    with pytest.raises(ValueError, match="Unhydrated"):
        verify(tmp_path, {path.name: wanted})
    path.write_bytes(b"glTF different fixture")
    with pytest.raises(ValueError, match="Changed"):
        verify(tmp_path, {path.name: wanted})
    path.write_bytes(b"glTF approved fixture")
    verify(tmp_path, {path.name: wanted})
