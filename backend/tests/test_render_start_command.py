"""Exercise startup ordering without opening sockets or touching a database."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest


def run_start(**environment):
    bash = shutil.which("bash")
    if os.name == "nt" and Path("C:/Program Files/Git/bin/bash.exe").is_file():
        bash = "C:/Program Files/Git/bin/bash.exe"
    if not bash:
        pytest.skip("Bash is required to exercise the Linux container entrypoint")
    script = Path(__file__).parents[1] / "scripts/start.sh"
    env = {key: value for key, value in os.environ.items()
           if key not in {"RUN_DATABASE_MIGRATIONS", "BOOTSTRAP_ADMIN_EMAIL", "BOOTSTRAP_ADMIN_PASSWORD"}}
    env.update(environment)
    # Both commands are shell stubs; no Python module or API server executes.
    command = '''
python() { printf 'python:%s\\n' "$*"; return "${TEST_MIGRATION_EXIT:-0}"; }
exec() { printf 'exec:%s\\n' "$*"; }
source "$1"
'''
    return subprocess.run([bash, "-c", command, "startup-test", script.as_posix()],
                          env=env, capture_output=True, text=True, timeout=15)


def test_default_start_migrates_before_api():
    result = run_start()
    assert result.returncode == 0, result.stderr
    assert result.stdout.index("python:-m scripts.prepare_database") < result.stdout.index("exec:uvicorn")


def test_predeploy_mode_skips_inline_migrations():
    result = run_start(RUN_DATABASE_MIGRATIONS="false")
    assert result.returncode == 0, result.stderr
    assert "scripts.prepare_database" not in result.stdout
    assert "exec:uvicorn" in result.stdout


def test_migration_failure_prevents_api_start():
    result = run_start(TEST_MIGRATION_EXIT="7")
    assert result.returncode == 7
    assert "exec:uvicorn" not in result.stdout


def test_invalid_migration_setting_fails_closed():
    result = run_start(RUN_DATABASE_MIGRATIONS="fasle")
    assert result.returncode != 0
    assert "exec:uvicorn" not in result.stdout
