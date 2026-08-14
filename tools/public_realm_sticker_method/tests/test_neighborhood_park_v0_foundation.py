from __future__ import annotations

import importlib.util
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


def test_assessment_is_integrity_clean_and_honestly_holds_runtime() -> None:
    module = load_audit_module()
    result = module.audit(ROOT)

    assert result["evidence_integrity"] is True
    assert result["source_integrity"] is True
    assert result["runtime_ready"] is False
    assert result["status"] == "hold"
    failed = {item["id"] for item in result["runtime_checks"] if not item["passed"]}
    assert failed == {
        "profile_owns_exact_rustic_identity",
        "recipe_binds_observed_fixed_kit",
        "generic_contemporary_path_is_absent",
    }


def test_require_ready_fails_closed_until_the_geometry_wave() -> None:
    completed = subprocess.run(
        [sys.executable, str(AUDIT_PATH), "--repo", str(ROOT), "--require-ready"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    assert '"status": "hold"' in completed.stdout
