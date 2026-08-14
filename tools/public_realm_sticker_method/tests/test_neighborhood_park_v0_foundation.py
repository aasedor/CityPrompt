from __future__ import annotations

import importlib.util
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "tools/public_realm_sticker_method/park/neighborhood_park_v0"
AUDIT_PATH = PILOT / "audit.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("neighborhood_park_v0_audit", AUDIT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_evidence_and_contract_lock_the_exact_rustic_variant() -> None:
    evidence = json.loads((PILOT / "evidence-lock.json").read_text(encoding="utf-8"))
    contract = json.loads((PILOT / "contract.json").read_text(encoding="utf-8"))

    assert evidence["variant_id"] == "neighborhood_park_v0"
    assert evidence["references"] == [
        {
            "path": "frontend/public/archetypes/openspaces/neighborhood-park/variant_0.png",
            "sha256": "38c1079127126017edb7945f77f47d73c4d0dde1fe5a566ac5dc0e791473d5c3",
            "width_px": 1024,
            "height_px": 768,
            "mode": "RGB",
            "role": "primary_identity",
        }
    ]
    assert contract["representation"] == "site_adaptive_whole_program"
    assert contract["canonical_test_site_m"] == {"width": 100.0, "depth": 80.0}
    assert contract["adaptation_rule"]["nonuniform_object_scaling_allowed"] is False
    assert contract["adaptation_rule"]["whole_element_fit_required"] is True
    assert len(contract["fixed_identity_kit"]) == 5


def test_compiled_manifest_owns_five_metric_glb_families() -> None:
    compiled = json.loads((PILOT / "compiled-kit.json").read_text(encoding="utf-8"))
    assert compiled["method"] == "sticker_method_site_adaptive_whole_program"
    assert compiled["fixedProgramEnvelopeM"] == [50.0, 38.0]
    assert compiled["adaptation"] == {
        "cropFixedObjectsAllowed": False,
        "nonuniformObjectScalingAllowed": False,
        "siteAdaptiveGround": True,
        "wholeFixedKit": True,
    }
    assert set(compiled["assets"]) == {
        "timber_pavilion",
        "timber_climbing_tower_with_slide",
        "timber_swing_frame",
        "split_rail_fence",
        "natural_boulder_group",
    }
    assert compiled["skin"]["roles"] == [
        "asphalt", "lawn", "metal", "paver", "planting", "rope", "safety", "stone", "timber"
    ]
    kit_root = ROOT / "frontend/public/park-kits/neighborhood-park-rustic-v0"
    for asset in compiled["assets"].values():
        path = kit_root / asset["file"]
        assert path.exists()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"]
        assert asset["metricScale"] == 1.0
        assert asset["nonuniformScalingAllowed"] is False
    assert compiled["surfaceOwnership"] == {
        "assetOwners": compiled["surfaceOwnership"]["assetOwners"],
        "exactOne": True,
        "fallbackAllowed": False,
    }


def test_assessment_is_integrity_clean_and_runtime_ready() -> None:
    module = load_audit_module()
    result = module.audit(ROOT)

    assert result["evidence_integrity"] is True
    assert result["source_integrity"] is True
    assert result["runtime_ready"] is True
    assert result["status"] == "ready"
    failed = {item["id"] for item in result["runtime_checks"] if not item["passed"]}
    assert failed == set()


def test_require_ready_passes_after_the_geometry_wave() -> None:
    completed = subprocess.run(
        [sys.executable, str(AUDIT_PATH), "--repo", str(ROOT), "--require-ready"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert '"status": "ready"' in completed.stdout
