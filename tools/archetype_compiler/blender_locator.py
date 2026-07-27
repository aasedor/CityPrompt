"""Cross-platform Blender discovery for the archetype compiler."""
from __future__ import annotations

import glob
import os
import re
import shutil
import sys
from pathlib import Path


class BlenderNotFoundError(RuntimeError):
    pass


def _windows_candidates() -> list[str]:
    patterns = [
        r"C:\Program Files\Blender Foundation\Blender *\blender.exe",
        r"C:\Program Files (x86)\Blender Foundation\Blender *\blender.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Blender Foundation\Blender *\blender.exe"),
    ]
    found: list[str] = []
    for pattern in patterns:
        found.extend(glob.glob(pattern))
    return found


def _version_key(path: str) -> tuple[int, int]:
    match = re.search(r"Blender (\d+)\.(\d+)", path)
    return (int(match.group(1)), int(match.group(2))) if match else (0, 0)


def find_blender(explicit: str | None = None) -> str:
    """Resolve the Blender executable. Precedence: --blender-path > BLENDER_PATH > well-known installs > PATH."""
    checked: list[str] = []

    for source, candidate in (("--blender-path", explicit), ("BLENDER_PATH", os.environ.get("BLENDER_PATH"))):
        if candidate:
            if Path(candidate).is_file():
                return candidate
            checked.append(f"{candidate} (from {source} — not found)")

    if sys.platform == "win32":
        installs = sorted(_windows_candidates(), key=_version_key, reverse=True)
        if installs:
            return installs[0]
        checked.append(r"C:\Program Files\Blender Foundation\Blender *\blender.exe")
    elif sys.platform == "darwin":
        mac_path = "/Applications/Blender.app/Contents/MacOS/Blender"
        if Path(mac_path).is_file():
            return mac_path
        checked.append(mac_path)

    on_path = shutil.which("blender")
    if on_path:
        return on_path
    checked.append("'blender' on PATH")

    raise BlenderNotFoundError(
        "Blender was not found. Paths checked:\n"
        + "\n".join(f"  - {c}" for c in checked)
        + "\n\nTo fix this:\n"
        "  1. Install Blender 4.x or newer from https://www.blender.org/download/\n"
        "  2. Or point the tool at an existing install:\n"
        "       set BLENDER_PATH=C:\\path\\to\\blender.exe   (Windows)\n"
        "       export BLENDER_PATH=/path/to/blender        (macOS/Linux)\n"
        "     or pass --blender-path <path>\n"
        "  3. Retry:  python tools/archetype_compiler/generate_family.py --archetype-id <id>\n"
    )


if __name__ == "__main__":
    print(find_blender())
