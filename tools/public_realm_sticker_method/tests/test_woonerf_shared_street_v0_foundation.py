from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "tools/public_realm_sticker_method/street/woonerf_shared_street_v0"
AUDIT_PATH = PILOT / "audit.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("woonerf_v0_audit", AUDIT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_evidence_and_contract_lock_the_pergola_promenade() -> None:
    evidence = json.loads((PILOT / "evidence-lock.json").read_text(encoding="utf-8"))
    contract = json.loads((PILOT / "contract.json").read_text(encoding="utf-8"))

    assert evidence["variant_id"] == "woonerf_shared_street_v0"
    assert [item["sha256"] for item in evidence["references"]] == [
        "620ea49bdc3589b4d1fd6ce7a6b586af75075951c8260c2d56e88270ab3c0999",
        "b330e8ada40f3bd5bfb1cde41fdfe49b3ed3c22b592e5f0bb1c5128543bf9320",
        "5bcd037316f90a9510ea1f9275fa147bd9f99fc78a3be77b7b6815e98f0f6a88",
    ]
    assert contract["representation"] == "connected_corridor_lego"
    assert contract["canonical_diagnostic_segment_m"] == {"width": 10.0, "length": 96.0}
    assert contract["corridor_rule"]["graph_owned_endpoints"] is True
    assert contract["module_schedule"]["whole_module_only"] is True
    assert contract["module_schedule"]["partial_terminal_module_allowed"] is False


def test_assessment_is_integrity_clean_and_honestly_holds_runtime() -> None:
    module = load_audit_module()
    result = module.audit(ROOT)

    assert result["evidence_integrity"] is True
    assert result["source_integrity"] is True
    assert result["runtime_ready"] is False
    assert result["status"] == "hold"
    failed = {item["id"] for item in result["runtime_checks"] if not item["passed"]}
    assert failed == {
        "exact_authority_overrides_dutch_vehicle_chicane",
        "complete_pergola_module_is_bound",
        "full_width_pedestrian_paving_is_bound",
        "botanical_furnishing_kit_is_bound",
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
