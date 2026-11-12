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
    family = json.loads((ROOT / trial.TUNING_FILE).read_text(encoding="utf-8"))["families"][0]
    target = tmp_path / trial.CLAY_ROOT / family["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    pointer = f"version https://git-lfs.github.com/spec/v1\noid sha256:{family['sha256']}\nsize {family['bytes']}\n"
    target.write_bytes(pointer.encode() if model is None else model)
    return family, target


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
    assert [row["asset_id"] for row in rows] == ["final_seniors_apartments"]
    assert rows[0]["model"] in {"verified", "lfs_pointer"}
    assert rows[0]["height_scale"] == 1.0
    assert rows[0]["stretch_width_m"] == [22.65, 45.3]
    assert rows[0]["stretch_depth_m"] == [12.59, 25.17]


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
        (lambda p: p["families"].append(dict(p["families"][0])), "exactly one building"),
        (lambda p: p["massing"].update(window_width_m=4.0), "massing dressing"),
        (lambda p: p["stretch"].update(squeeze_on_plot_resize="yes"), "squeeze_on_plot_resize"),
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
