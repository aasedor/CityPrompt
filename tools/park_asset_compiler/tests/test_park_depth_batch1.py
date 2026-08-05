from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SPEC_PATH = REPOSITORY_ROOT / "tools/park_asset_compiler/park_depth_batch1_reference_spec.json"
ASSET_ROOT = REPOSITORY_ROOT / "assets/park-depth-kits/staging"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_batch_references_have_three_catalogue_angles() -> None:
    spec = load_json(SPEC_PATH)
    assert spec["status"] == "staging_not_integrated"
    assert [kit["archetype_id"] for kit in spec["kits"]] == [
        "tennis_court_cluster",
        "skate_park",
        "dog_park",
    ]
    for kit in spec["kits"]:
        assert len(kit["views"]) >= 3
        catalogue_root = REPOSITORY_ROOT / kit["catalogue_root"]
        assert all((catalogue_root / view).is_file() for view in kit["views"])


def test_staged_glbs_match_manifest_hashes_and_contract() -> None:
    manifest = load_json(ASSET_ROOT / "manifest.json")
    assert manifest["status"] == "staging_not_integrated"
    assert len(manifest["assets"]) == 3
    for record in manifest["assets"]:
        path = ASSET_ROOT / record["file"]
        payload = path.read_bytes()
        assert payload[:4] == b"glTF"
        assert len(payload) == record["bytes"]
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]
        assert record["metric_scale"] == 1.0
        assert record["ground_contact_origin_z_m"] == 0.0
        assert record["status"] == "staging_not_integrated"
        assert record["triangles"] > 0
