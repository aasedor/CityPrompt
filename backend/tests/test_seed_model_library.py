from __future__ import annotations

import json

from tools.seed_model_library import _prepare_row_for_restore, _seed_owner_ids


COLUMNS = [
    "id",
    "owner_id",
    "source_building_id",
    "source_project_id",
    "tags",
    "metadata",
    "is_public",
]


def test_seed_owner_ids_are_unique_and_deterministic() -> None:
    rows = [
        {"owner_id": "owner-b"},
        {"owner_id": "owner-a"},
        {"owner_id": "owner-b"},
    ]

    assert _seed_owner_ids(rows) == ["owner-a", "owner-b"]


def test_lego_restore_clears_missing_provenance_and_becomes_shared() -> None:
    row = {
        "id": "module-1",
        "owner_id": "owner-1",
        "source_building_id": "missing-building",
        "source_project_id": "missing-project",
        "tags": ["machiya"],
        "metadata": {"lego": {"asset_kind": "lego_module", "family": "restored-kyoto-machiya"}},
        "is_public": False,
    }

    restored = _prepare_row_for_restore(row, COLUMNS)

    assert restored["source_building_id"] is None
    assert restored["source_project_id"] is None
    assert restored["is_public"] is True
    assert json.loads(restored["tags"]) == ["machiya"]
    assert json.loads(restored["metadata"])["lego"]["family"] == "restored-kyoto-machiya"


def test_non_lego_restore_preserves_visibility() -> None:
    row = {
        "id": "legacy-1",
        "owner_id": "owner-1",
        "source_building_id": "missing-building",
        "source_project_id": "missing-project",
        "tags": [],
        "metadata": None,
        "is_public": False,
    }

    restored = _prepare_row_for_restore(row, COLUMNS)

    assert restored["is_public"] is False
    assert restored["source_building_id"] is None
    assert restored["source_project_id"] is None
