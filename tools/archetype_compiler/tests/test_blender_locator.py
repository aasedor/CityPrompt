from __future__ import annotations

from pathlib import Path

from blender_locator import find_blender, main


def test_find_blender_prefers_an_explicit_executable(tmp_path: Path):
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"fixture")

    assert find_blender(str(blender)) == str(blender)


def test_cli_accepts_the_positional_path_used_by_the_powershell_wrapper(
    tmp_path: Path,
    capsys,
):
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"fixture")

    assert main([str(blender)]) == 0
    assert capsys.readouterr().out.strip() == str(blender)


def test_cli_accepts_the_documented_blender_path_option(tmp_path: Path, capsys):
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"fixture")

    assert main(["--blender-path", str(blender)]) == 0
    assert capsys.readouterr().out.strip() == str(blender)
