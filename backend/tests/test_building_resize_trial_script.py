"""The pilot's verification script reads repository files and installs nothing."""

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts import building_resize_trial as trial  # noqa: E402

from app.services import building_flex_contract as contracts  # noqa: E402


def copy_contract(tmp_path, *, model: bytes | None = None):
    """A minimal repository copy holding only what offline verification reads."""
    for relative in (trial.TUNING_FILE, trial.SERVER_COPY, trial.CLAY_ROOT / "library.json"):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    families = json.loads((ROOT / trial.TUNING_FILE).read_text(encoding="utf-8"))["families"]
    # Every trial model as a Git LFS pointer; `model` replaces the first one's bytes.
    for index, row in reversed(list(enumerate(families))):
        target = tmp_path / trial.CLAY_ROOT / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        pointer = f"version https://git-lfs.github.com/spec/v1\noid sha256:{row['sha256']}\nsize {row['bytes']}\n"
        target.write_bytes(pointer.encode() if model is None or index else model)
    return families[0], target


def edit_tuning(tmp_path, change):
    path = tmp_path / trial.TUNING_FILE
    payload = json.loads(path.read_text(encoding="utf-8"))
    change(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(path, tmp_path / trial.SERVER_COPY)


def test_the_repository_contract_verifies_offline():
    manifest, rows = trial.load_trial()
    assert manifest["id"] == trial.PROGRAM_ID == contracts.RESIZE_TRIAL_PROGRAM_ID
    assert (trial.SCALE_FLOOR, trial.SCALE_CEILING) == (
        contracts.RESIZE_TRIAL_SCALE_FLOOR,
        contracts.RESIZE_TRIAL_SCALE_CEILING,
    )
    by_id = {row["asset_id"]: row for row in rows}
    assert len(rows) == len(by_id) == len(manifest["families"]) >= 70
    assert all(row["model"] in {"verified", "lfs_pointer"} and row["height_scale"] == 1.0 for row in rows)
    # The two piloted buildings keep the widest range and their facade kits.
    seniors, courtyard = by_id["final_seniors_apartments"], by_id["final_courtyard_block"]
    assert (seniors["band"], seniors["massing_kit"]) == ("wide", "aspen_terrace")
    assert (seniors["stretch_width_m"], seniors["stretch_depth_m"]) == ([22.65, 45.3], [12.59, 25.17])
    assert (courtyard["band"], courtyard["massing_kit"]) == ("wide", "brick_garden_courtyard")
    assert (courtyard["stretch_width_m"], courtyard["stretch_depth_m"]) == ([21.27, 42.53], [18.41, 36.82])
    # Every other building takes a narrower range by type and has no free draw.
    office, house = by_id["clay_admin_faculty_brick_bronze_fins"], by_id["clay_rammed_earth_infill"]
    assert (office["band"], office["stretch_width_m"], office["massing_kit"]) == ("regular", [29.25, 41.29], None)
    assert (house["band"], house["stretch_width_m"], house["massing_kit"]) == ("careful", [12.04, 14.71], None)
    assert {row["band"] for row in rows} == set(manifest["stretch"]["bands"])


def test_the_committed_building_list_matches_the_library_and_the_rollout_rules():
    manifest = json.loads((ROOT / trial.TUNING_FILE).read_text(encoding="utf-8"))
    library = json.loads((ROOT / trial.CLAY_ROOT / "library.json").read_text(encoding="utf-8"))
    families, skipped = trial.expected_families(manifest, library)
    assert families == manifest["families"]
    assert len(families) + len(skipped) == len(library["entries"])
    left_out = {row["asset_id"]: row["reason"] for row in skipped}
    # Buildings with rules of their own are left out, each with its reason.
    assert left_out == manifest["rollout"]["exclude"]
    assert "its own storey programme" in left_out["clay_vancouver_balcony_podium_tower"]
    assert "house resize programme" in left_out["trial_postwar_bungalow"]
    # Anything nine storeys or taller is held to the careful range whatever its group.
    tall = [row for row in families if row["native_storeys"] >= 9]
    assert tall and all(row["band"] == "careful" for row in tall)


def test_syncing_rebuilds_the_list_from_the_rules_and_keeps_the_server_copy_identical(tmp_path):
    copy_contract(tmp_path)
    before = (tmp_path / trial.TUNING_FILE).read_bytes()
    trial.sync_families(tmp_path)
    # Already in sync: nothing changes, byte for byte.
    assert (tmp_path / trial.TUNING_FILE).read_bytes() == before == (tmp_path / trial.SERVER_COPY).read_bytes()

    def retune(payload):
        payload["rollout"]["band_by_group"]["civic"] = "regular"
        payload["rollout"]["exclude"]["autumn_timber"] = "left out for this test"

    path = tmp_path / trial.TUNING_FILE
    payload = json.loads(path.read_text(encoding="utf-8"))
    retune(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="--sync-families"):
        trial.load_trial(tmp_path, require_mirror=False)
    families, skipped = trial.sync_families(tmp_path)
    assert "autumn_timber" not in {row["asset_id"] for row in families}
    assert {
        "asset_id": "autumn_timber",
        "label": "Nordic Roof-Garden Apartments",
        "reason": "left out for this test",
    } in skipped
    civic = [row for row in families if row["asset_id"] == "final_health_centre"]
    assert civic and civic[0]["band"] == "regular"
    # Facade kits survive a rebuild, and the result verifies with its mirror.
    assert {row["asset_id"]: row["massing_kit"] for row in families if row["massing_kit"]} == {
        "final_seniors_apartments": "aspen_terrace",
        "final_courtyard_block": "brick_garden_courtyard",
    }
    assert (tmp_path / trial.TUNING_FILE).read_bytes() == (tmp_path / trial.SERVER_COPY).read_bytes()
    trial.load_trial(tmp_path)


def test_the_default_run_is_a_dry_run_that_never_reaches_a_database(monkeypatch, capsys):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("The default run must not open a database")

    monkeypatch.setattr(trial, "check_database", forbidden)
    assert trial.main([]) == 0
    output = capsys.readouterr().out
    assert output.startswith("Dry run.")
    assert "nothing was installed or changed" in output


def test_the_script_offers_no_install_or_apply_mode():
    for flag in ("--install", "--apply", "--owner-id"):
        with pytest.raises(SystemExit):
            trial.main([flag])


def test_a_matching_lfs_pointer_or_the_exact_bytes_verify(tmp_path):
    family, model = copy_contract(tmp_path)
    assert trial.load_trial(tmp_path)[1][0]["model"] == "lfs_pointer"
    copy_contract(tmp_path, model=b"glTF" + b"\0" * 2048)
    with pytest.raises(ValueError, match="Changed trial model bytes"):
        trial.load_trial(tmp_path)
    # The same file verifies once the pin names its real bytes and size.
    assert trial.model_state(model, hashlib.sha256(model.read_bytes()).hexdigest(), model.stat().st_size) == "verified"
    other = f"version https://git-lfs.github.com/spec/v1\noid sha256:{'0' * 64}\nsize {family['bytes']}\n"
    model.write_bytes(other.encode())
    with pytest.raises(ValueError, match="names different bytes"):
        trial.load_trial(tmp_path)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda p: p["stretch"].update(maximum_scale=1.7), "bounded runtime range"),
        (lambda p: p["stretch"].update(minimum_scale=0.4), "bounded runtime range"),
        (lambda p: p["stretch"].update(vertical_scale=1.1), "unit vertical scale"),
        (lambda p: p.update(status="PUBLISHED"), "local trial"),
        (lambda p: p["families"][0].update(sha256="0" * 64), "drifted from the reviewed library"),
        (lambda p: p["families"][0].update(native_storeys=6), "drifted from the reviewed library"),
        (lambda p: p["families"][0].update(candidate="unreviewed-clay-v001"), "not in the reviewed clay library"),
        (lambda p: p["families"].append(dict(p["families"][0])), "more than once"),
        (lambda p: p["families"].clear(), "at least one building"),
        (lambda p: p["families"][1].update(massing_kit="unknown_kit"), "no known facade kit"),
        (lambda p: p["families"][0].update(band="elastic"), "no known stretch range"),
        (lambda p: p["families"][0].update(band="wide"), "--sync-families"),
        (lambda p: p["families"].pop(), "--sync-families"),
        (lambda p: p["stretch"]["bands"]["regular"].update(maximum_scale=1.5), "stretch ranges are invalid"),
        (lambda p: p["stretch"]["bands"]["careful"].update(minimum_scale=1.05), "stretch ranges are invalid"),
        (lambda p: p["stretch"].update(bands={}), "stretch ranges are invalid"),
        (lambda p: p["rollout"]["exclude"].update(not_a_building="a reason"), "not in the reviewed library"),
        (lambda p: p["rollout"]["band_by_group"].pop("civic"), "no stretch range for the group"),
        (lambda p: p["rollout"].update(tall_band="elastic"), "rollout rules are invalid"),
        (lambda p: p["rollout"]["exclude"].update(autumn_timber=""), "rollout rules are invalid"),
        (lambda p: p["rollout"]["band_overrides"].update(autumn_timber="careful"), "rollout rules are invalid"),
        (lambda p: p["rollout"]["band_override_reasons"].pop("showcase_market"), "rollout rules are invalid"),
        (lambda p: p["families"][1].update(sha256="0" * 64), "drifted from the reviewed library"),
        (lambda p: p["massing"].update(window_width_m=4.0), "massing dressing"),
        (lambda p: p["stretch"].update(squeeze_on_plot_resize="yes"), "squeeze_on_plot_resize"),
        (lambda p: p["stretch"].update(rigid_prop_materials="CLAY_PLANTING"), "rigid prop"),
        (lambda p: p["stretch"].update(rigid_prop_max_size_m=0), "rigid prop"),
        (lambda p: p["massing"].update(style="photoreal"), "Unknown massing style"),
        (lambda p: p["massing"]["kits"]["aspen_terrace"].update(window_width_m=3.5), "facade kit"),
        (lambda p: p["massing"]["kits"]["aspen_terrace"].update(loggia_height_m=3.2), "facade kit"),
        (lambda p: p["massing"]["kits"]["aspen_terrace"]["colors"].update(wall="tan"), "facade kit"),
        (lambda p: p["massing"]["kits"]["aspen_terrace"].update(upper_floor_height_m=-1), "facade kit"),
        (lambda p: p["massing"]["kits"]["aspen_terrace"].update(type="glass_tower"), "facade kit"),
        (lambda p: p["massing"].update(kits={}), "facade kit"),
        (lambda p: p["massing"]["kits"]["brick_garden_courtyard"].update(window_width_m=4.3), "facade kit"),
        (lambda p: p["massing"]["kits"]["brick_garden_courtyard"].update(shop_front_height_m=4.2), "facade kit"),
        (lambda p: p["massing"]["kits"]["brick_garden_courtyard"].update(wing_depth_m=0), "facade kit"),
        (lambda p: p["massing"]["kits"]["brick_garden_courtyard"].pop("passage_width_m"), "facade kit"),
        (lambda p: p["massing"]["kits"]["brick_garden_courtyard"]["colors"].pop("shopfront"), "facade kit"),
        (lambda p: p["massing"]["kits"]["brick_garden_courtyard"]["colors"].update(joint="#a8937c"), "facade kit"),
        (lambda p: p["shape_freely"].update(minimum_width_m=500), "Shape freely limits"),
    ],
)
def test_unsafe_tuning_is_refused(tmp_path, change, message):
    copy_contract(tmp_path)
    edit_tuning(tmp_path, change)
    with pytest.raises(ValueError, match=message):
        trial.load_trial(tmp_path)


def test_write_mirror_only_rewrites_the_server_copy(tmp_path):
    copy_contract(tmp_path)
    path = tmp_path / trial.TUNING_FILE
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["massing"]["bay_module_m"] = 4.2
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="server copy differs"):
        trial.load_trial(tmp_path)
    before = {item: item.read_bytes() for item in tmp_path.rglob("*") if item.is_file()}
    assert trial.write_mirror(tmp_path) is True
    assert trial.write_mirror(tmp_path) is False
    after = {item: item.read_bytes() for item in tmp_path.rglob("*") if item.is_file()}
    assert {item for item in after if after[item] != before.get(item)} == {tmp_path / trial.SERVER_COPY}
    assert trial.load_trial(tmp_path)[0]["massing"]["bay_module_m"] == 4.2
