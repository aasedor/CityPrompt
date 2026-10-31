"""The finite production cohort requires an exact receipt for every route."""

import hashlib
import copy
import json
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.services.native_source_bridge import SOURCE_BRIDGE_LANES
from app.services.native_specialist_streets import validate_specialist_properties

ROOT = Path(__file__).resolve().parents[2]
ROWS = json.loads((ROOT / "backend/app/data/nativeBridgePilots.json").read_text(encoding="utf-8"))


def properties(row):
    return {
        "road_selected_variant_id": row["id"],
        "road_archetype_id": row["sourceArchetypeId"],
        "width": row["widthM"],
        "lane_count": SOURCE_BRIDGE_LANES.get(row["id"], 0),
        "plan_centerline": [[0, 0], [0, row["fixtureLengthM"] / 111320]],
    }


@pytest.fixture
def hold_bridge(monkeypatch, tmp_path):
    from app.services import native_bridge_release as release

    def hold(variant):
        payload = json.loads(release.MANIFEST.read_text(encoding="utf-8"))
        payload["entries"] = [entry for entry in payload["entries"] if entry["profile"]["id"] != variant]
        receipt = tmp_path / "held-release.json"
        receipt.write_text(json.dumps(payload), encoding="utf-8")
        monkeypatch.setattr(release, "MANIFEST", receipt)
        release._released_bridge_ids.cache_clear()

    yield hold
    release._released_bridge_ids.cache_clear()


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["id"])
def test_production_cannot_place_a_held_bridge_through_a_direct_api_claim(monkeypatch, row, hold_bridge):
    hold_bridge(row["id"])
    monkeypatch.setattr(get_settings(), "app_env", "production")
    with pytest.raises(ValueError, match="production release"):
        validate_specialist_properties(properties(row))


def test_production_accepts_exact_ten_route_cohort_and_retains_local_rehearsal(monkeypatch):
    monkeypatch.setattr(get_settings(), "app_env", "production")
    from app.services.native_bridge_release import released_bridge_profiles, native_bridge_available

    assert set(released_bridge_profiles()) == {row["id"] for row in ROWS}
    assert not native_bridge_available("unreviewed_bridge_route_v1")
    for row in ROWS:
        validate_specialist_properties(properties(row))
    monkeypatch.setattr(get_settings(), "app_env", "development")
    for row in ROWS:
        validate_specialist_properties(properties(row))


def test_release_profile_and_durable_evidence_match_original_exact_bytes():
    source = ROOT / "backend/app/data/nativeBridgeRelease.json"
    assert source.read_bytes() == (ROOT / "frontend/src/data/nativeBridgeRelease.json").read_bytes()
    manifest = json.loads(source.read_text(encoding="utf-8"))
    assert [entry["profile"]["id"] for entry in manifest["entries"]] == [row["id"] for row in ROWS]
    for entry in manifest["entries"]:
        assert entry["profile"] == next(row for row in ROWS if row["id"] == entry["profile"]["id"])
        assert hashlib.sha256(entry["profileCanonical"].encode()).hexdigest() == entry["profileSha256"]
        assert json.loads(entry["profileCanonical"]) == entry["profile"]
        for evidence in (entry["sourceVisualReview"], entry["runtimeReview"], entry["provenance"]):
            assert evidence["sha256Encoding"] == "utf8-lf"
            text = (ROOT / evidence["path"]).read_bytes().replace(b"\r\n", b"\n")
            assert hashlib.sha256(text).hexdigest() == evidence["sha256"]
        for module in entry["profile"]["modules"].values():
            data = (ROOT / "frontend/public" / module["url"].lstrip("/")).read_bytes()
            assert len(data) == module["bytes"]
            assert hashlib.sha256(data).hexdigest() == module["sha256"]


def test_production_registry_does_not_advertise_a_held_executable_bridge_kit(monkeypatch, hold_bridge):
    from app.services.native_street_candidate_contract import native_street_runtime_capabilities

    monkeypatch.setattr(get_settings(), "app_env", "production")
    held = "cable_stayed_cycle_ring_route_v1"
    hold_bridge(held)
    native_street_runtime_capabilities.cache_clear()
    try:
        variants = {
            selection.variant_id
            for capability in native_street_runtime_capabilities()
            for selection in capability.selections
        }
        assert variants & {row["id"] for row in ROWS} == {row["id"] for row in ROWS if row["id"] != held}
    finally:
        native_street_runtime_capabilities.cache_clear()


@pytest.mark.parametrize(
    "mutation",
    [
        lambda entry: entry["profile"]["program"].update(maxLengthM=241),
        lambda entry: entry["profile"]["modules"]["bridge_bay"].update(sha256="f" * 64),
        lambda entry: entry["profile"].update(sourceAssemblySha256="f" * 64),
        lambda entry: entry["runtimeReview"].update(status="pending"),
        lambda entry: entry.update(status="local-pilot-runtime-pending"),
    ],
)
def test_stale_or_unreviewed_release_profile_cannot_gain_production_admission(tmp_path, mutation):
    from app.services.native_bridge_release import released_bridge_profiles

    payload = copy.deepcopy(
        json.loads((ROOT / "backend/app/data/nativeBridgeRelease.json").read_text(encoding="utf-8"))
    )
    mutation(payload["entries"][0])
    receipt = tmp_path / "release.json"
    receipt.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="production release"):
        released_bridge_profiles(receipt)
