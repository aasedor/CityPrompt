"""Keep development data services reachable only from the host itself."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA_SERVICES = {"db", "redis", "minio"}


def services(filename):
    return yaml.safe_load((ROOT / filename).read_text(encoding="utf-8"))["services"]


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("docker-compose.yml", {"db": [(5432, 5432)], "redis": [(6379, 6379)], "minio": [(9000, 9000), (9001, 9001)]}),
        (
            "cityprompt-compose.yml",
            {"db": [(5433, 5432)], "redis": [(6380, 6379)], "minio": [(9002, 9000), (9003, 9001)]},
        ),
    ],
)
def test_data_ports_bind_loopback_without_changing_host_or_container_ports(filename, expected):
    selected = services(filename)
    for name, wanted in expected.items():
        published = []
        for binding in selected[name]["ports"]:
            parts = binding.rsplit(":", 2)
            assert len(parts) == 3 and parts[0] == "127.0.0.1", (filename, name, binding)
            published.append((int(parts[1]), int(parts[2])))
        assert published == wanted


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("docker-compose.yml", {"backend": ["8000:8000"], "frontend": ["5175:5174"]}),
        ("cityprompt-compose.yml", {"backend": ["8010:8000", "8000:8000"]}),
    ],
)
def test_application_publications_and_internal_service_connections_are_preserved(filename, expected):
    selected = services(filename)
    actual = {
        name: service["ports"] for name, service in selected.items() if name not in DATA_SERVICES and "ports" in service
    }
    assert actual == expected
    backend_environment = selected["backend"]["environment"]
    assert "REDIS_URL=redis://redis:6379/0" in backend_environment
    assert "S3_ENDPOINT_URL=http://minio:9000" in backend_environment
    assert "DATABASE_URL=postgresql+asyncpg://devuser:devpassword@db:5432/dev_platform" in backend_environment


def test_staging_overlay_does_not_reexpose_data_services():
    selected = services("docker-compose.staging.yml")
    for name in DATA_SERVICES:
        for binding in selected[name].get("ports", []):
            assert binding.startswith("127.0.0.1:"), (name, binding)


@pytest.mark.parametrize(
    "filename",
    [
        "deployment/classroom/compose.yaml",
        "deployment/validation/compose.yaml",
        "deployment/classroom/prefork-probe.compose.yaml",
    ],
)
def test_standalone_profiles_publish_no_data_ports_and_only_loopback_application_ports(filename):
    for name, service in services(filename).items():
        if name in DATA_SERVICES | {"media"}:
            assert not service.get("ports"), (filename, name)
        for binding in service.get("ports", []):
            assert binding.startswith("127.0.0.1:"), (filename, name, binding)
