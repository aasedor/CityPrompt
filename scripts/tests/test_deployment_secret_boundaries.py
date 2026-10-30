"""Exercise public deployment inputs without discovering desktop credentials."""

import importlib.util
from io import BytesIO
import os
from pathlib import Path
import sys
import tarfile

import pathspec
import pytest

ROOT = Path(__file__).resolve().parents[2]
STRONG_TEST_SECRET = "f5b632e9cf61a7840b3e98521a649c7d4e817f308a596b2cd064e37f8c912a65"


@pytest.fixture
def isolated_settings(tmp_path, monkeypatch):
    # Import the actual source from an empty project, so its dotenv discovery
    # cannot touch the developer checkout or its shared Git directory.
    target = tmp_path / "project/backend/app/core/config.py"
    target.parent.mkdir(parents=True)
    target.write_bytes((ROOT / "backend/app/core/config.py").read_bytes())
    monkeypatch.setattr(os, "environ", {})
    name = "isolated_deployment_config"
    spec = importlib.util.spec_from_file_location(name, target)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module.Settings


def production_settings(settings_class, secret):
    return settings_class(
        _env_file=None,
        app_env="production",
        app_debug=False,
        jwt_secret_key=secret,
        allowed_origins="https://company.example",
    )


def test_public_classroom_jwt_placeholder_cannot_start_production(isolated_settings):
    template = ROOT / "deployment/classroom/backend.env.example"
    secret = next(
        line.split("=", 1)[1] for line in template.read_text().splitlines() if line.startswith("JWT_SECRET_KEY=")
    )
    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        production_settings(isolated_settings, secret)


@pytest.mark.parametrize(
    "secret",
    [
        "x",
        "secret",
        "CHANGE-THIS-IN-PRODUCTION",
        "replace_with_a_unique_random_secret",
        "your-production-jwt-secret-goes-here",
        "a" * 64,
        "0123456789abcdef" * 4,
        "correct horse battery staple",
    ],
)
def test_production_refuses_obvious_or_too_short_keys(isolated_settings, secret):
    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        production_settings(isolated_settings, secret)


def test_production_accepts_a_strong_operator_key(isolated_settings):
    assert production_settings(isolated_settings, STRONG_TEST_SECRET).is_production


def test_development_retains_its_inert_default(isolated_settings):
    settings = isolated_settings(_env_file=None, app_env="development")
    assert settings.jwt_secret_key == "change-this-in-production"


@pytest.mark.parametrize("context", [".", "backend"])
def test_synthetic_docker_context_omits_vertex_credentials_and_keeps_runtime_json(tmp_path, context):
    root_context = context == "."
    rules = (ROOT / context / ".dockerignore").read_text().splitlines()
    # These contexts use ordinary ordered wildcard/**/negation rules, shared
    # with pathspec. This tests our delivery selection, not a live Docker daemon.
    selected = pathspec.GitIgnoreSpec.from_lines(rules)
    prefix = "backend/" if root_context else ""
    credential_paths = [prefix + "vertex-key.json", prefix + "private/vertex-key.json"]
    runtime_paths = [prefix + "app/main.py", prefix + "app/data/runtime.json"]
    if root_context:
        runtime_paths += [
            "seed/model-library/rlasm-architectural-clay/house-flex-pilot-v001.json",
            "frontend/src/data/localTowerStoreyPrograms.json",
        ]
    for relative in credential_paths + runtime_paths:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("synthetic marker only", encoding="utf-8")
    archive = BytesIO()
    with tarfile.open(fileobj=archive, mode="w") as output:
        for target in tmp_path.rglob("*"):
            if target.is_file():
                relative = target.relative_to(tmp_path).as_posix()
                if not selected.match_file(relative):
                    output.add(target, arcname=relative)
    archive.seek(0)
    with tarfile.open(fileobj=archive) as output:
        delivered = set(output.getnames())
    assert delivered.isdisjoint(credential_paths)
    assert delivered.issuperset(runtime_paths)
