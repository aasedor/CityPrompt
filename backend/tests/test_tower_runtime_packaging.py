from pathlib import Path

from app.services import building_flex_contract as contracts


def test_render_image_contains_the_tower_contract_at_its_runtime_path():
    docker = (Path(__file__).resolve().parents[1] / "Dockerfile.render").read_text()
    assert (
        "COPY frontend/src/data/localTowerStoreyPrograms.json /app/frontend/src/data/localTowerStoreyPrograms.json"
        in docker
    )
    ignored = (Path(__file__).resolve().parents[2] / ".dockerignore").read_text().splitlines()
    assert all(
        path in ignored
        for path in [
            "!frontend/",
            "!frontend/src/",
            "!frontend/src/data/",
            "!frontend/src/data/localTowerStoreyPrograms.json",
        ]
    )


def test_ordinary_buildings_do_not_depend_on_a_local_tower_manifest(monkeypatch):
    def unavailable():
        raise FileNotFoundError("Local tower manifest unavailable")

    monkeypatch.setattr(contracts, "_tower_contracts", unavailable)
    assert contracts.trusted_building_footprint_target({}) is None
    assert contracts.trusted_building_footprint_target({"building_footprint_program_id": {"invalid": "object"}}) is None
