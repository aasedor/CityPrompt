from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.services.master_planner.lego_catalog import (
    build_lego_planning_catalog,
    select_lego_archetype,
)
from app.tasks.urban_dna import (
    LegoInventoryChangedDuringPlan,
    _refresh_project_lego_inventory,
)


INDUSTRIAL_PARENT = "industrial_brick_mixed_use"
INDUSTRIAL_VARIANT = "industrial_brick_original_mill"
PARISIAN_PARENT = "parisian_boulevard_corner"
MARKET_PARENT = "food_hall_market_hall"
MARKET_VARIANT = "market_historic_iron_glass"


def _entry(
    entry_id: str,
    *,
    family: str,
    role: str,
    width_m: float,
    depth_m: float,
    height_m: float,
    archetype_ids: list[str],
    repeatable_z: bool = False,
    min_floors: int | None = None,
    max_floors: int | None = None,
    native_floors: int | None = None,
    source_variant_id: str | None = None,
    generation_archetype_id: str | None = None,
    enabled: bool = True,
):
    return SimpleNamespace(
        id=entry_id,
        name=entry_id,
        model_url=f"/models/{entry_id}.glb",
        metadata_={
            "lego": {
                "enabled": enabled,
                "family": family,
                "role": role,
                "width_m": width_m,
                "depth_m": depth_m,
                "height_m": height_m,
                "archetype_ids": archetype_ids,
                "reuse_keys": [],
                "repeatable_z": repeatable_z,
                "min_floors": min_floors,
                "max_floors": max_floors,
                "native_floors": native_floors,
                "source_variant_id": source_variant_id,
                "generation_archetype_id": generation_archetype_id,
                "variant_key": "default",
                "lod": 0,
            }
        },
    )


def _modular_family(
    *,
    family: str = "industrial-family",
    archetype_ids: list[str] | None = None,
    min_floors: int | None = 2,
    max_floors: int | None = 5,
    include_floor: bool = True,
    include_roof: bool = True,
) -> list[SimpleNamespace]:
    ids = archetype_ids or [INDUSTRIAL_PARENT, INDUSTRIAL_VARIANT]
    entries = [
        _entry(
            f"{family}-podium",
            family=family,
            role="podium",
            width_m=30,
            depth_m=20,
            height_m=3.2,
            archetype_ids=ids,
            min_floors=min_floors,
            max_floors=max_floors,
        ),
    ]
    if include_floor:
        entries.append(
            _entry(
                f"{family}-floor",
                family=family,
                role="floor",
                width_m=30,
                depth_m=20,
                height_m=3.2,
                archetype_ids=ids,
                repeatable_z=True,
                min_floors=min_floors,
                max_floors=max_floors,
            )
        )
    if include_roof:
        entries.append(
            _entry(
                f"{family}-roof",
                family=family,
                role="roof",
                width_m=30,
                depth_m=20,
                height_m=1,
                archetype_ids=ids,
                min_floors=min_floors,
                max_floors=max_floors,
            )
        )
    return entries


def test_modular_catalog_proves_parent_variant_and_supported_floors():
    catalog = build_lego_planning_catalog(_modular_family())

    assert catalog.parent_ids == (INDUSTRIAL_PARENT,)
    assert catalog.variants_by_parent == {
        INDUSTRIAL_PARENT: (INDUSTRIAL_VARIANT,),
    }
    assert catalog.supported_floors_by_parent == {
        INDUSTRIAL_PARENT: (2, 3, 4, 5),
    }
    assert catalog.supported_floors_by_selectable_id == {
        INDUSTRIAL_PARENT: (2, 3, 4, 5),
        INDUSTRIAL_VARIANT: (2, 3, 4, 5),
    }
    assert catalog.parent_by_selectable_id == {
        INDUSTRIAL_PARENT: INDUSTRIAL_PARENT,
        INDUSTRIAL_VARIANT: INDUSTRIAL_PARENT,
    }
    assert catalog.target_dimensions_by_selectable_id == {
        INDUSTRIAL_PARENT: (30.0, 20.0),
        INDUSTRIAL_VARIANT: (30.0, 20.0),
    }
    capability = catalog.capabilities[0]
    assert capability.selectable_ids == (INDUSTRIAL_PARENT, INDUSTRIAL_VARIANT)
    assert capability.families == ("industrial-family",)
    assert capability.target_width_m == 30
    assert capability.target_depth_m == 20
    assert "supported_floors=2-5" in catalog.prompt_vocabulary
    assert f"selectable_ids={INDUSTRIAL_PARENT}, {INDUSTRIAL_VARIANT}" in catalog.prompt_vocabulary


def test_modular_catalog_uses_imported_podium_dimensions_not_card_suggestion():
    entries = _modular_family()
    for module in entries:
        module.metadata_["lego"]["width_m"] = 26
        module.metadata_["lego"]["depth_m"] = 17

    catalog = build_lego_planning_catalog(entries)

    assert catalog.target_dimensions_by_selectable_id == {
        INDUSTRIAL_PARENT: (26.0, 17.0),
        INDUSTRIAL_VARIANT: (26.0, 17.0),
    }
    capability = catalog.capabilities[0]
    assert (capability.target_width_m, capability.target_depth_m) == (26.0, 17.0)
    assert "catalog_target=26x17m" in catalog.prompt_vocabulary


def test_catalog_keeps_one_newest_native_revision_and_its_floor_set():
    older = _modular_family(
        family="industrial-revision-old",
        min_floors=2,
        max_floors=5,
    )
    newer = _modular_family(
        family="industrial-revision-new",
        min_floors=4,
        max_floors=6,
    )
    imported_at = datetime(2026, 7, 21, tzinfo=timezone.utc)
    for module in older:
        module.created_at = imported_at
        module.metadata_["lego"]["source_variant_id"] = INDUSTRIAL_VARIANT
    for module in newer:
        module.created_at = imported_at + timedelta(minutes=1)
        module.metadata_["lego"]["width_m"] = 34
        module.metadata_["lego"]["depth_m"] = 22
        module.metadata_["lego"]["source_variant_id"] = INDUSTRIAL_VARIANT

    first = build_lego_planning_catalog([*older, *newer])
    second = build_lego_planning_catalog(reversed([*older, *newer]))

    assert first == second
    assert first.capabilities[0].selectable_ids == (INDUSTRIAL_VARIANT,)
    assert first.target_dimensions_by_selectable_id == {
        INDUSTRIAL_VARIANT: (34.0, 22.0),
    }
    assert first.supported_floors_by_selectable_id == {
        INDUSTRIAL_VARIANT: (4, 5, 6),
    }
    assert first.capabilities[0].families == ("industrial-revision-new",)


def test_catalog_rejects_inconsistent_podium_dimensions_within_one_family():
    entries = _modular_family()
    entries.append(
        _entry(
            "industrial-family-podium-conflict",
            family="industrial-family",
            role="podium",
            width_m=31,
            depth_m=20,
            height_m=3.2,
            archetype_ids=[INDUSTRIAL_PARENT, INDUSTRIAL_VARIANT],
            min_floors=2,
            max_floors=5,
        )
    )

    assert build_lego_planning_catalog(entries).parent_ids == ()


def test_modular_family_without_floor_is_capable_only_at_one_floor():
    catalog = build_lego_planning_catalog(
        _modular_family(
            include_floor=False,
            min_floors=None,
            max_floors=None,
            archetype_ids=[INDUSTRIAL_PARENT],
        )
    )

    assert catalog.parent_ids == (INDUSTRIAL_PARENT,)
    assert catalog.supported_floors_by_parent[INDUSTRIAL_PARENT] == (1,)


def test_selection_prefers_parent_alias_and_respects_policy_ceiling():
    catalog = build_lego_planning_catalog(_modular_family())

    nearest = select_lego_archetype(catalog, INDUSTRIAL_PARENT, 4.4)
    below = select_lego_archetype(
        catalog,
        INDUSTRIAL_PARENT,
        3.8,
        at_or_below=True,
    )

    assert nearest is not None
    assert nearest.selectable_id == INDUSTRIAL_PARENT
    assert nearest.variant_id is None
    assert nearest.floors == 4
    assert below is not None
    assert below.floors == 3


def test_selection_uses_exact_variant_for_assembled_only_family():
    assembled = _entry(
        "mill-assembled",
        family="mill-landmark",
        role="assembled",
        width_m=30,
        depth_m=20,
        height_m=14,
        archetype_ids=[INDUSTRIAL_PARENT, INDUSTRIAL_VARIANT],
        native_floors=4,
        source_variant_id=INDUSTRIAL_VARIANT,
        generation_archetype_id=INDUSTRIAL_VARIANT,
    )
    catalog = build_lego_planning_catalog([assembled])

    selection = select_lego_archetype(catalog, INDUSTRIAL_PARENT, 9)

    assert selection is not None
    assert selection.parent_id == INDUSTRIAL_PARENT
    assert selection.variant_id == INDUSTRIAL_VARIANT
    assert selection.floors == 4


def test_historic_market_catalog_advertises_only_native_two_floor_landmark():
    assembled = _entry(
        "historic-market-assembled",
        family="market-historic-iron-glass-v98-canonical",
        role="assembled",
        width_m=45,
        depth_m=60,
        height_m=24.8,
        archetype_ids=[MARKET_PARENT, MARKET_VARIANT],
        native_floors=2,
        source_variant_id=MARKET_VARIANT,
        generation_archetype_id="food_hall_market_hall_variant_0",
    )

    catalog = build_lego_planning_catalog([assembled])

    assert catalog.parent_ids == (MARKET_PARENT,)
    assert catalog.capabilities[0].selectable_ids == (MARKET_VARIANT,)
    assert catalog.supported_floors_by_parent[MARKET_PARENT] == (2,)
    assert catalog.supported_floors_by_selectable_id[MARKET_VARIANT] == (2,)
    assert catalog.target_dimensions_by_selectable_id[MARKET_VARIANT] == (45.0, 60.0)


def test_hybrid_exact_variant_uses_assembled_native_dimensions():
    entries = _modular_family()
    entries.append(
        _entry(
            "mill-renderlocked",
            family="industrial-family",
            role="assembled",
            width_m=45,
            depth_m=27,
            height_m=14,
            archetype_ids=[INDUSTRIAL_PARENT, INDUSTRIAL_VARIANT],
            native_floors=4,
            source_variant_id=INDUSTRIAL_VARIANT,
            generation_archetype_id=INDUSTRIAL_VARIANT,
        )
    )

    catalog = build_lego_planning_catalog(entries)

    # A source-variant package owns the concrete variant, not its broad parent
    # grouping alias. This prevents the hero asset from silently redefining a
    # generic parent's dimensions.
    assert catalog.capabilities[0].selectable_ids == (INDUSTRIAL_VARIANT,)
    assert catalog.target_dimensions_by_selectable_id == {
        INDUSTRIAL_VARIANT: (45.0, 27.0),
    }
    assert (catalog.capabilities[0].target_width_m, catalog.capabilities[0].target_depth_m) == (
        45.0,
        27.0,
    )
    assert catalog.supported_floors_by_selectable_id[INDUSTRIAL_VARIANT] == (4,)


def test_incomplete_or_disabled_modular_families_are_excluded():
    missing_roof = _modular_family(include_roof=False)
    disabled_roof = _modular_family()
    disabled_roof[-1].metadata_["lego"]["enabled"] = False

    assert build_lego_planning_catalog(missing_roof).parent_ids == ()
    assert build_lego_planning_catalog(disabled_roof).parent_ids == ()


def test_assembled_only_family_requires_exact_source_identity_and_native_floor():
    assembled = _entry(
        "mill-assembled",
        family="mill-landmark",
        role="assembled",
        width_m=30,
        depth_m=20,
        height_m=14,
        archetype_ids=[INDUSTRIAL_PARENT, INDUSTRIAL_VARIANT],
        native_floors=4,
        source_variant_id=INDUSTRIAL_VARIANT,
        generation_archetype_id=INDUSTRIAL_VARIANT,
    )

    catalog = build_lego_planning_catalog([assembled])

    assert catalog.parent_ids == (INDUSTRIAL_PARENT,)
    assert catalog.capabilities[0].selectable_ids == (INDUSTRIAL_VARIANT,)
    assert catalog.variants_by_parent[INDUSTRIAL_PARENT] == (INDUSTRIAL_VARIANT,)
    assert catalog.supported_floors_by_parent[INDUSTRIAL_PARENT] == (4,)

    broad_alias_only = _entry(
        "anonymous-assembled",
        family="anonymous-landmark",
        role="assembled",
        width_m=30,
        depth_m=20,
        height_m=14,
        archetype_ids=[INDUSTRIAL_PARENT],
        native_floors=4,
    )
    assert build_lego_planning_catalog([broad_alias_only]).parent_ids == ()


def test_unknown_archetype_aliases_are_not_exposed():
    catalog = build_lego_planning_catalog(
        _modular_family(
            archetype_ids=["invented_lego_city", INDUSTRIAL_PARENT],
        )
    )

    assert catalog.parent_ids == (INDUSTRIAL_PARENT,)
    assert "invented_lego_city" not in catalog.prompt_vocabulary


def test_catalog_order_and_fingerprint_are_stable():
    industrial = _modular_family(archetype_ids=[INDUSTRIAL_PARENT])
    parisian = [
        _entry(
            "parisian-podium",
            family="parisian-family",
            role="podium",
            width_m=18,
            depth_m=18,
            height_m=3.2,
            archetype_ids=[PARISIAN_PARENT],
        ),
        _entry(
            "parisian-floor",
            family="parisian-family",
            role="floor",
            width_m=18,
            depth_m=18,
            height_m=3.2,
            archetype_ids=[PARISIAN_PARENT],
            repeatable_z=True,
        ),
        _entry(
            "parisian-roof",
            family="parisian-family",
            role="roof",
            width_m=18,
            depth_m=18,
            height_m=2,
            archetype_ids=[PARISIAN_PARENT],
        ),
    ]
    entries = [*parisian, *industrial]

    first = build_lego_planning_catalog(entries)
    second = build_lego_planning_catalog(reversed(entries))

    assert first.parent_ids == (INDUSTRIAL_PARENT, PARISIAN_PARENT)
    assert first == second
    assert len(first.fingerprint) == 64
    int(first.fingerprint, 16)


def test_final_inventory_refresh_detects_a_mid_draw_catalog_mutation():
    initial = build_lego_planning_catalog(_modular_family())
    mutated_entries = _modular_family(include_roof=False)

    class FakeQuery:
        def __init__(self, rows):
            self.rows = rows
            self.populate_existing = False

        def filter(self, *_criteria):
            return self

        def order_by(self, *_columns):
            return self

        def execution_options(self, **options):
            self.populate_existing = options.get("populate_existing") is True
            return self

        def all(self):
            return self.rows

    class FakeSession:
        def __init__(self, rows):
            self.query_result = FakeQuery(rows)

        def query(self, _model):
            return self.query_result

    session = FakeSession(mutated_entries)

    with pytest.raises(
        LegoInventoryChangedDuringPlan,
        match="inventory changed while the AI plan was drawing",
    ):
        _refresh_project_lego_inventory(
            session,
            "project-owner",
            initial.fingerprint,
        )

    assert session.query_result.populate_existing is True


def test_empty_catalog_has_stable_actionable_vocabulary():
    first = build_lego_planning_catalog([])
    second = build_lego_planning_catalog([])

    assert first == second
    assert first.parent_ids == ()
    assert first.variants_by_parent == {}
    assert first.supported_floors_by_parent == {}
    assert first.supported_floors_by_selectable_id == {}
    assert first.parent_by_selectable_id == {}
    assert "No executable LEGO building families" in first.prompt_vocabulary
