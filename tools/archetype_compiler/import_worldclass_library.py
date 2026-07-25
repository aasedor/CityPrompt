"""Import every validated v7 family into City Prompt's LEGO model library."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--index",
        type=Path,
        default=REPO_ROOT / "build" / "worldclass-v7" / "worldclass-library-index.json",
    )
    parser.add_argument("--api-base", default="http://localhost:8000")
    parser.add_argument("--token", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    payload = json.loads(args.index.resolve().read_text(encoding="utf-8"))
    families = [item for item in payload.get("families", []) if item.get("city_prompt_ready")]
    failures = 0
    for item in families:
        command = [
            sys.executable,
            str(TOOL_DIR / "import_manifest.py"),
            str(REPO_ROOT / item["output_directory"]),
            "--api-base", args.api_base,
        ]
        for flag in ("token", "email", "password"):
            value = getattr(args, flag)
            if value:
                command += [f"--{flag}", value]
        if args.force:
            command.append("--force")
        if subprocess.run(command, cwd=str(REPO_ROOT)).returncode:
            failures += 1
    print(f"Imported {len(families) - failures}/{len(families)} validated families")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
