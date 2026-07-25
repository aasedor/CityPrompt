import json
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.models import Building, ModelLibraryEntry
from app.services.community_3d_artifacts import (
    community_3d_buildings_for_zones,
    stale_community_3d_buildings,
)
from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    descriptor_from_library_entry,
    find_family_module_entry,
    lego_metadata_from_manifest,
    manifest_validation_errors,
    plan_vertical_assembly,
)
from app.services.master_planner.lego_catalog import build_lego_planning_catalog
from app.services.residual_landscape import community_3d_source_hash
from tests.conftest import FakeProject


def entry(asset_id: str, name: str, role: str, *, height: float, width: float = 24, depth: float = 18):
    return SimpleNamespace(
        id=asset_id,
        name=name,
        model_url=f"https://example.test/{asset_id}.glb",
        metadata_={
            "lego": {
                "enabled": True,
                "role": role,
                "family": "nordic-midrise",
                "width_m": width,
                "depth_m": depth,
                "height_m": height,
                "repeatable_z": role == "floor",
                "archetype_ids": ["nordic-midrise"],
                "reuse_keys": ["nordic", "mixed-use"],
                "min_floors": 3,
                "max_floors": 12,
            }
        },
    )


def test_descriptor_ignores_unconfigured_library_items():
    raw = SimpleNamespace(id="x", name="X", model_url="x.glb", metadata_={})
    assert descriptor_from_library_entry(raw) is None


def test_vertical_plan_reuses_archetype_metadata_and_stacks_modules():
    modules = [
        descriptor_from_library_entry(entry("podium", "Retail podium", "podium", height=4.5)),
        descriptor_from_library_entry(entry("floor", "Residential floor", "floor", height=3.2)),
        descriptor_from_library_entry(entry("setback", "Setback floor", "setback", height=3.2)),
        descriptor_from_library_entry(entry("roof", "Green roof", "roof", height=1.0)),
    ]

    plan = plan_vertical_assembly(
        [module for module in modules if module],
        AssemblyRequest(
            target_width_m=24,
            target_depth_m=18,
            target_floors=6,
            archetype_id="nordic-midrise",
            reuse_keys=("nordic", "mixed-use"),
        ),
    )

    assert plan["family"] == "nordic-midrise"
    assert [item["role"] for item in plan["instances"]] == [
        "podium",
        "floor",
        "floor",
        "floor",
        "floor",
        "setback",
        "roof",
    ]
    assert plan["instances"][0]["position"] == [0.0, 0.0, 0.0]
    assert plan["assembled_height_m"] == pytest.approx(21.5)
    assert plan["archetype_id"] == "nordic-midrise"
    assert plan["reuse_keys"] == ["nordic", "mixed-use"]


def test_exact_variant_uses_fixed_landmark_at_canonical_size_and_floors():
    raw = entry("assembled", "Tudor quadrangle", "assembled", height=27.6, width=60, depth=25)
    raw.metadata_["lego"].update({
        "archetype_ids": ["collegiate_gothic_education", "collegiate_gothic_tudor"],
        "reuse_keys": ["collegiate_gothic"],
        "native_floors": 4,
        "source_variant_id": "collegiate_gothic_tudor",
    })
    landmark = descriptor_from_library_entry(raw)

    plan = plan_vertical_assembly(
        [landmark] if landmark else [],
        AssemblyRequest(
            target_width_m=60,
            target_depth_m=25,
            target_floors=4,
            archetype_id="collegiate_gothic_tudor",
            reuse_keys=("collegiate_gothic",),
        ),
    )

    assert plan["version"] == 3
    assert plan["fit"]["assembly_mode"] == "fixed_landmark"
    assert plan["assembled_height_m"] == pytest.approx(27.6)
    assert len(plan["instances"]) == 1
    assert plan["instances"][0]["role"] == "assembled"
    assert plan["instances"][0]["scale"] == [1.0, 1.0, 1.0]


def test_generation_archetype_id_resolves_to_exact_fixed_landmark():
    raw = entry("assembled", "Tudor quadrangle", "assembled", height=27.6, width=60, depth=25)
    raw.metadata_["lego"].update({
        "archetype_ids": [
            "collegiate_gothic_education",
            "collegiate_gothic_tudor",
            "collegiate_gothic_education_variant_0",
        ],
        "reuse_keys": ["collegiate_gothic"],
        "native_floors": 4,
        "source_variant_id": "collegiate_gothic_tudor",
        "generation_archetype_id": "collegiate_gothic_education_variant_0",
    })
    landmark = descriptor_from_library_entry(raw)

    plan = plan_vertical_assembly(
        [landmark] if landmark else [],
        AssemblyRequest(
            target_width_m=60,
            target_depth_m=25,
            target_floors=4,
            archetype_id="collegiate_gothic_education_variant_0",
            reuse_keys=("collegiate_gothic",),
        ),
    )

    assert plan["fit"]["assembly_mode"] == "fixed_landmark"
    assert plan["instances"][0]["role"] == "assembled"


def test_exact_variant_landmark_resizes_to_a_small_city_parcel():
    raw = entry("assembled", "Perpendicular chapel", "assembled", height=34.0, width=61.58, depth=42.74)
    raw.metadata_["lego"].update({
        "archetype_ids": ["collegiate_gothic_perpendicular"],
        "reuse_keys": ["collegiate_gothic"],
        "native_floors": 4,
        "source_variant_id": "collegiate_gothic_perpendicular",
    })
    landmark = descriptor_from_library_entry(raw)

    plan = plan_vertical_assembly(
        [landmark] if landmark else [],
        AssemblyRequest(
            target_width_m=35.3,
            target_depth_m=21.5,
            target_floors=4,
            archetype_id="collegiate_gothic_perpendicular",
            reuse_keys=("collegiate_gothic",),
        ),
    )

    assert plan["fit"]["assembly_mode"] == "fixed_landmark"
    assert plan["instances"][0]["scale"] == [pytest.approx(0.57324), pytest.approx(0.50304), 1.0]


def test_rejects_destructive_footprint_scaling():
    modules = [
        descriptor_from_library_entry(entry("podium", "Podium", "podium", height=4.5)),
        descriptor_from_library_entry(entry("floor", "Floor", "floor", height=3.2)),
        descriptor_from_library_entry(entry("roof", "Roof", "roof", height=1.0)),
    ]

    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly(
            [module for module in modules if module],
            AssemblyRequest(target_width_m=40, target_depth_m=18, target_floors=5),
        )


def test_allow_setback_false_suppresses_setback_even_at_six_floors():
    modules = [
        descriptor_from_library_entry(entry("podium", "Podium", "podium", height=4.5)),
        descriptor_from_library_entry(entry("floor", "Floor", "floor", height=3.2)),
        descriptor_from_library_entry(entry("setback", "Setback", "setback", height=3.2)),
        descriptor_from_library_entry(entry("roof", "Roof", "roof", height=1.0)),
    ]

    plan = plan_vertical_assembly(
        [module for module in modules if module],
        AssemblyRequest(
            target_width_m=24,
            target_depth_m=18,
            target_floors=6,
            allow_setback=False,
        ),
    )

    roles = [item["role"] for item in plan["instances"]]
    assert "setback" not in roles
    assert roles == ["podium", "floor", "floor", "floor", "floor", "floor", "roof"]
    assert plan["assembled_height_m"] == pytest.approx(21.5)


def test_variant_specific_rooftop_addition_can_start_at_four_floors():
    setback_entry = entry("setback", "Contemporary rooftop addition", "setback", height=3.2)
    setback_entry.metadata_["lego"]["setback_min_floors"] = 4
    modules = [
        descriptor_from_library_entry(entry("podium", "Podium", "podium", height=4.5)),
        descriptor_from_library_entry(entry("floor", "Floor", "floor", height=3.2)),
        descriptor_from_library_entry(setback_entry),
        descriptor_from_library_entry(entry("roof", "Green roof", "roof", height=1.0)),
    ]

    plan = plan_vertical_assembly(
        [module for module in modules if module],
        AssemblyRequest(target_width_m=24, target_depth_m=18, target_floors=4),
    )

    assert [item["role"] for item in plan["instances"]] == [
        "podium", "floor", "floor", "setback", "roof",
    ]


# ---------------------------------------------------------------------------
# Manifest helpers (service layer)
# ---------------------------------------------------------------------------


def _manifest(**overrides):
    """A minimal but shape-faithful blender_generate.py manifest."""
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/blender_generate.py",
            "version": "0.5.0",
            "blender_version": "5.1.2",
        },
        "family": "nordic-timber-midrise",
        "archetype_id": "nordic_timber_midrise",
        "archetype_label": "Nordic Timber Mid-Rise",
        "variant_id": None,
        "generation_archetype_id": "nordic_timber_midrise_variant_0",
        "aesthetic_category_id": "scandinavian_nordic",
        "development_type": "residential_multifamily",
        "reuse_keys": ["nordic_timber_midrise", "scandinavian_nordic"],
        "generation_tags": ["nordic", "timber", "midrise"],
        "coordinate_contract": {"units": "metres", "origin": "bottom centre"},
        "dimensions": {"width_m": 20.0, "depth_m": 16.0, "floor_height_m": 3.2},
        "min_floors": 2,
        "max_floors": 8,
        "default_floors": 5,
        "modules": [
            {
                "role": "podium",
                "filename": "fam_podium.glb",
                "module_family": "nordic-timber-midrise",
                "width_m": 20.0,
                "depth_m": 16.0,
                "height_m": 4.0,
                "floor_height_m": 3.2,
                "repeatable_z": False,
                "variant_key": "default",
                "lod": 0,
                "triangle_count": 624,
                "material_count": 4,
            },
            {
                "role": "floor",
                "filename": "fam_floor.glb",
                "module_family": "nordic-timber-midrise",
                "width_m": 20.0,
                "depth_m": 16.0,
                "height_m": 3.2,
                "floor_height_m": 3.2,
                "repeatable_z": True,
                "variant_key": "typical_a",
                "lod": 0,
                "triangle_count": 936,
                "material_count": 5,
            },
        ],
        "assembled": {
            "filename": "fam_assembled.glb",
            "floors": 5,
            "uses_setback": False,
            "height_m": 18.0,
            "triangle_count": 4452,
        },
        "thumbnail": "fam_preview.png",
    }
    manifest.update(overrides)
    return manifest


def test_manifest_validation_accepts_real_shape():
    assert manifest_validation_errors(_manifest()) == []


def test_manifest_validation_reports_actionable_errors():
    errors = manifest_validation_errors(
        _manifest(manifest_schema=1, family="", reuse_keys=[], modules=[])
    )
    joined = "; ".join(errors)
    assert "manifest_schema" in joined
    assert "family" in joined
    assert "reuse_keys" in joined
    assert "modules" in joined


def test_manifest_validation_rejects_path_syntax_in_family_and_role():
    """family/role become storage-key segments — path syntax must never pass."""
    for bad_family in ("../evil", "a/b", "a\\b", "UPPER", "dots.dots"):
        errors = manifest_validation_errors(_manifest(family=bad_family))
        assert any("family" in e and "slug" in e for e in errors), bad_family

    manifest = _manifest()
    manifest["modules"][0]["role"] = "podium/../../x"
    errors = manifest_validation_errors(manifest)
    assert any("role" in e for e in errors)


def test_lego_metadata_from_manifest_builds_planner_shape():
    manifest = _manifest(
        archetype_aliases=[
            "nordic_timber_midrise_variant_1",
            "nordic_timber_midrise_variant_2",
            "nordic_timber_midrise_variant_1",
            "",
        ]
    )
    metadata = lego_metadata_from_manifest(
        manifest, manifest["modules"][1], validation_status="pass"
    )
    assert metadata["enabled"] is True
    assert metadata["role"] == "floor"
    assert metadata["family"] == "nordic-timber-midrise"
    assert metadata["repeatable_z"] is True
    assert metadata["variant_key"] == "typical_a"
    assert metadata["lod"] == 0
    assert metadata["archetype_ids"] == [
        "nordic_timber_midrise",
        "nordic_timber_midrise_variant_0",
        "nordic_timber_midrise_variant_1",
        "nordic_timber_midrise_variant_2",
    ]
    assert metadata["min_floors"] == 2 and metadata["max_floors"] == 8
    assert metadata["validation_status"] == "pass"
    assert metadata["asset_kind"] == "lego_module"

    assembled_meta = lego_metadata_from_manifest(
        manifest,
        {"role": "assembled", "filename": "fam_assembled.glb", "height_m": 18.0},
    )
    assert assembled_meta["enabled"] is False
    assert assembled_meta["role"] == "assembled"

    landmark_manifest = _manifest(
        variant_id="collegiate_gothic_tudor",
        massing_graph={"schema": "massing-graph@1", "profile": "gothic_gatehouse_hero"},
    )
    landmark_meta = lego_metadata_from_manifest(
        landmark_manifest,
        {
            "role": "assembled",
            "filename": "tudor_assembled.glb",
            "width_m": 60.0,
            "depth_m": 25.0,
            "height_m": 27.6,
            "native_floors": 4,
        },
    )
    assert landmark_meta["enabled"] is True
    assert landmark_meta["native_floors"] == 4
    assert landmark_meta["source_variant_id"] == "collegiate_gothic_tudor"
    assert landmark_meta["generation_archetype_id"] == "nordic_timber_midrise_variant_0"


def test_find_family_module_entry_dedupes_on_family_and_role():
    match = SimpleNamespace(metadata_={"lego": {"family": "fam-a", "role": "floor"}})
    entries = [
        SimpleNamespace(metadata_=None),
        SimpleNamespace(metadata_={"lego": {"family": "fam-b", "role": "floor"}}),
        SimpleNamespace(metadata_={"lego": {"family": "fam-a", "role": "roof"}}),
        match,
    ]
    assert find_family_module_entry(entries, "fam-a", "floor") is match
    assert find_family_module_entry(entries, "fam-a", "podium") is None


def test_requested_archetype_never_substitutes_unrelated_family():
    modules = [
        descriptor_from_library_entry(entry("podium", "Podium", "podium", height=4.5)),
        descriptor_from_library_entry(entry("floor", "Floor", "floor", height=3.2)),
        descriptor_from_library_entry(entry("roof", "Roof", "roof", height=1.0)),
    ]
    with pytest.raises(AssemblyPlanningError, match="explicitly matches archetype") as error:
        plan_vertical_assembly(
            [module for module in modules if module],
            AssemblyRequest(
                target_width_m=24,
                target_depth_m=18,
                target_floors=5,
                archetype_id="contemporary_midrise",
            ),
        )
    assert error.value.code == "family_not_found"
    assert error.value.requested == {
        "width_m": 24.0,
        "depth_m": 18.0,
        "floors": 5,
        "footprint_profile": "rectangle",
    }
    assert error.value.supported_families is None


def test_rectangle_plan_quarter_turns_an_exact_narrow_module():
    modules = [
        descriptor_from_library_entry(
            entry("narrow-podium", "Narrow podium", "podium", height=4.5, width=8, depth=15)
        ),
        descriptor_from_library_entry(
            entry("narrow-floor", "Narrow floor", "floor", height=3.2, width=8, depth=15)
        ),
        descriptor_from_library_entry(
            entry("narrow-roof", "Narrow roof", "roof", height=1.0, width=8, depth=15)
        ),
    ]

    plan = plan_vertical_assembly(
        [module for module in modules if module],
        AssemblyRequest(
            target_width_m=15,
            target_depth_m=8,
            target_floors=5,
            archetype_id="nordic-midrise",
        ),
    )

    assert plan["family"] == "nordic-midrise"
    assert plan["fit"]["scale_x"] == 1.0
    assert plan["fit"]["scale_y"] == 1.0
    assert {instance["rotation_degrees"] for instance in plan["instances"]} == {90.0}
    assert {tuple(instance["scale"]) for instance in plan["instances"]} == {
        (1.0, 1.0, 1.0)
    }
    assert plan["footprint_segments"] == [{
        "id": "main",
        "centre_x_m": 0.0,
        "centre_y_m": 0.0,
        "length_m": 8,
        "thickness_m": 15,
        "rotation_degrees": 90.0,
    }]


def test_matching_family_reports_incompatible_target_and_supported_ranges():
    modules = [
        descriptor_from_library_entry(entry("podium", "Podium", "podium", height=4.5)),
        descriptor_from_library_entry(entry("floor", "Floor", "floor", height=3.2)),
        descriptor_from_library_entry(entry("roof", "Roof", "roof", height=1.0)),
    ]

    with pytest.raises(AssemblyPlanningError, match="No compatible module family") as error:
        plan_vertical_assembly(
            [module for module in modules if module],
            AssemblyRequest(
                target_width_m=60,
                target_depth_m=40,
                target_floors=6,
                archetype_id="nordic-midrise",
            ),
        )

    assert error.value.code == "family_incompatible"
    assert error.value.requested == {
        "width_m": 60.0,
        "depth_m": 40.0,
        "floors": 6,
        "footprint_profile": "rectangle",
    }
    assert error.value.supported_families == [{
        "family": "nordic-midrise",
        "widths_m": [24.0],
        "depths_m": [18.0],
        "min_floors": 3,
        "max_floors": 12,
    }]


def test_industrial_brick_parent_selects_original_mill_for_30x20_six_floors():
    def industrial_module(
        asset_id: str,
        family: str,
        role: str,
        *,
        width: float,
        depth: float,
        min_floors: int,
        max_floors: int,
    ):
        raw = entry(asset_id, asset_id, role, height=1.0 if role == "roof" else 3.5,
                    width=width, depth=depth)
        raw.metadata_["lego"].update({
            "family": family,
            "archetype_ids": ["industrial_brick_mixed_use"],
            "min_floors": min_floors,
            "max_floors": max_floors,
        })
        return descriptor_from_library_entry(raw)

    modules = [
        industrial_module(
            f"original-{role}",
            "industrial-brick-original-mill-v1-renderlocked",
            role,
            width=30,
            depth=20,
            min_floors=4,
            max_floors=8,
        )
        for role in ("podium", "floor", "roof")
    ] + [
        industrial_module(
            f"brewery-{role}",
            "industrial-brick-brewery-v1-renderlocked",
            role,
            width=40,
            depth=26,
            min_floors=2,
            max_floors=5,
        )
        for role in ("podium", "floor", "roof")
    ]

    plan = plan_vertical_assembly(
        [module for module in modules if module],
        AssemblyRequest(
            target_width_m=30,
            target_depth_m=20,
            target_floors=6,
            archetype_id="industrial_brick_mixed_use",
        ),
    )

    assert plan["family"] == "industrial-brick-original-mill-v1-renderlocked"
    assert plan["target"] == {
        "width_m": 30,
        "depth_m": 20,
        "floors": 6,
        "footprint_profile": "rectangle",
        "wing_depth_m": 20.0,
    }


def test_l_shape_plan_places_two_rotated_streetwall_segments():
    modules = [
        descriptor_from_library_entry(entry("podium", "Podium", "podium", height=4.5, width=30, depth=10)),
        descriptor_from_library_entry(entry("floor", "Floor", "floor", height=3.2, width=30, depth=10)),
        descriptor_from_library_entry(entry("roof", "Roof", "roof", height=1.0, width=30, depth=10)),
    ]
    plan = plan_vertical_assembly(
        [module for module in modules if module],
        AssemblyRequest(
            target_width_m=36,
            target_depth_m=28,
            target_floors=5,
            footprint_profile="l_shape",
            wing_depth_m=10,
        ),
    )

    assert plan["target"]["footprint_profile"] == "l_shape"
    assert plan["fit"]["segment_count"] == 2
    assert {instance["segment_id"] for instance in plan["instances"]} == {"front", "left_return"}
    assert {instance["rotation_degrees"] for instance in plan["instances"]} == {0.0, 90.0}
    assert len(plan["instances"]) == 12


def test_courtyard_plan_places_four_perimeter_segments():
    modules = [
        descriptor_from_library_entry(entry("podium", "Podium", "podium", height=4.5, width=30, depth=10)),
        descriptor_from_library_entry(entry("floor", "Floor", "floor", height=3.2, width=30, depth=10)),
        descriptor_from_library_entry(entry("roof", "Roof", "roof", height=1.0, width=30, depth=10)),
    ]
    plan = plan_vertical_assembly(
        [module for module in modules if module],
        AssemblyRequest(
            target_width_m=36,
            target_depth_m=30,
            target_floors=4,
            footprint_profile="courtyard",
            wing_depth_m=10,
        ),
    )
    assert plan["fit"]["segment_count"] == 4
    assert len(plan["footprint_segments"]) == 4
    assert {segment["id"] for segment in plan["footprint_segments"]} == {
        "front", "rear", "left_return", "right_return",
    }


# ---------------------------------------------------------------------------
# API: shared mock-db helpers (same pattern as test_site_zones_generate_all_api)
# ---------------------------------------------------------------------------


def _scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def _scalars_result(values):
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = values
    result.scalars.return_value = scalars
    return result


@pytest.mark.anyio
async def test_plan_api_returns_structured_family_not_found_error(
    client, mock_db, test_user, auth_headers
):
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/plan",
        headers=auth_headers,
        json={
            "target_width_m": 24,
            "target_depth_m": 18,
            "target_floors": 5,
            "archetype_id": "missing_family",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "code": "family_not_found",
        "message": (
            "No module family explicitly matches archetype 'missing_family'. "
            "Import that archetype/variant instead of substituting an unrelated family."
        ),
        "requested": {
            "width_m": 24.0,
            "depth_m": 18.0,
            "floors": 5,
            "footprint_profile": "rectangle",
        },
    }


@pytest.mark.anyio
async def test_plan_api_returns_structured_family_incompatible_error(
    client, mock_db, test_user, auth_headers
):
    library_entries = [
        entry("podium", "Podium", "podium", height=4.5),
        entry("floor", "Floor", "floor", height=3.2),
        entry("roof", "Roof", "roof", height=1.0),
    ]
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalars_result(library_entries),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/plan",
        headers=auth_headers,
        json={
            "target_width_m": 60,
            "target_depth_m": 40,
            "target_floors": 6,
            "archetype_id": "nordic-midrise",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "code": "family_incompatible",
        "message": (
            "No compatible module family found. Add podium, repeatable floor, and roof modules "
            "whose native footprint is within 20% of the target."
        ),
        "requested": {
            "width_m": 60.0,
            "depth_m": 40.0,
            "floors": 6,
            "footprint_profile": "rectangle",
        },
        "supported_families": [{
            "family": "nordic-midrise",
            "widths_m": [24.0],
            "depths_m": [18.0],
            "min_floors": 3,
            "max_floors": 12,
        }],
    }


@pytest.mark.anyio
async def test_plan_api_uses_only_project_owner_modules_for_an_authorized_editor(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=uuid.uuid4())
    share = SimpleNamespace(permission="editor")
    library_entries = [
        entry("podium", "Podium", "podium", height=4.5),
        entry("floor", "Floor", "floor", height=3.2),
        entry("roof", "Roof", "roof", height=1.0),
    ]
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(project),
        _scalar_result(share),
        _scalars_result(library_entries),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/plan",
        headers=auth_headers,
        json={
            "project_id": str(project.id),
            "target_width_m": 24,
            "target_depth_m": 18,
            "target_floors": 5,
            "archetype_id": "nordic-midrise",
        },
    )

    assert response.status_code == 200
    library_query = mock_db.execute.await_args_list[-1].args[0]
    owner_values = [
        value
        for value in library_query.compile().params.values()
        if isinstance(value, (list, set, tuple))
    ]
    assert any(
        project.owner_id in values and test_user.id not in values
        for values in owner_values
    )


def _multipart(manifest_dict, glb_names, *, thumbnail=False, report=None):
    parts = [
        ("manifest", ("manifest.json", json.dumps(manifest_dict).encode(), "application/json"))
    ]
    for name in glb_names:
        parts.append(("files", (name, f"glb-bytes-{name}".encode(), "model/gltf-binary")))
    if thumbnail:
        parts.append(("thumbnail", ("fam_preview.png", b"png-bytes", "image/png")))
    if report is not None:
        parts.append(
            (
                "validation_report",
                ("validation_report.json", json.dumps(report).encode(), "application/json"),
            )
        )
    return parts


@pytest.fixture
def fake_storage(monkeypatch):
    """Capture _upload_to_storage calls instead of hitting MinIO."""
    uploaded = {}

    def fake_upload(key, data, content_type):
        uploaded[key] = (bytes(data), content_type)
        return f"http://minio:9000/test-bucket/{key}"

    monkeypatch.setattr("app.tasks.processing._upload_to_storage", fake_upload)
    return uploaded


# ---------------------------------------------------------------------------
# API: import-manifest
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_import_manifest_creates_entries_with_deterministic_keys(
    client, mock_db, test_user, auth_headers, fake_storage
):
    created = []
    mock_db.add.side_effect = created.append
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # require_auth user lookup
            _scalars_result([]),        # owner's existing library entries
        ]
    )

    response = await client.post(
        "/api/v1/lego-assembly/import-manifest",
        headers=auth_headers,
        files=_multipart(
            _manifest(),
            ["fam_podium.glb", "fam_floor.glb", "fam_assembled.glb"],
            thumbnail=True,
            report={"status": "pass"},
        ),
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["family"] == "nordic-timber-midrise"
    assert payload["archetype_id"] == "nordic_timber_midrise"
    assert payload["skipped"] == []
    assert {item["role"]: item["action"] for item in payload["imported"]} == {
        "podium": "created",
        "floor": "created",
        "assembled": "created",
    }

    prefix = f"library/lego/{test_user.id}/nordic-timber-midrise"
    assert set(fake_storage) == {
        f"{prefix}/preview.png",
        f"{prefix}/podium--default--lod0.glb",
        f"{prefix}/floor--typical_a--lod0.glb",
        f"{prefix}/assembled--default--lod0.glb",
    }
    assert fake_storage[f"{prefix}/floor--typical_a--lod0.glb"][1] == "model/gltf-binary"
    assert fake_storage[f"{prefix}/preview.png"][1] == "image/png"

    assert len(created) == 3
    floor = next(e for e in created if e.metadata_["lego"]["role"] == "floor")
    assert isinstance(floor, ModelLibraryEntry)
    assert floor.name == "Nordic Timber Mid-Rise — floor / typical_a"
    assert floor.category == "lego_module"
    assert floor.generation_engine == "compiler" and len(floor.generation_engine) <= 20
    assert floor.architectural_style == "scandinavian_nordic"
    assert floor.is_public is False
    assert floor.tags[:2] == ["nordic-timber-midrise", "floor"]
    # model_url must be the browser-reachable proxy URL, not the raw MinIO URL
    assert floor.model_url.startswith(f"/api/v1/files/{prefix}/floor--typical_a--lod0.glb?v=")
    assert floor.thumbnail_url.startswith(f"/api/v1/files/{prefix}/preview.png?v=")
    assert "archetype_compiler/blender_generate.py v0.5.0" in floor.generation_prompt

    lego = floor.metadata_["lego"]
    assert lego["enabled"] is True
    assert lego["repeatable_z"] is True
    assert lego["validation_status"] == "pass"
    assert lego["schema_version"] == 3
    assert lego["variant_key"] == "typical_a"
    assert lego["archetype_ids"] == ["nordic_timber_midrise", "nordic_timber_midrise_variant_0"]
    assert lego["min_floors"] == 2 and lego["max_floors"] == 8
    assert lego["coordinate_contract"]["units"] == "metres"
    assert len(lego["content_hash"]) == 64

    assembled = next(e for e in created if e.metadata_["lego"]["role"] == "assembled")
    assert assembled.metadata_["lego"]["enabled"] is False
    assert assembled.metadata_["lego"]["height_m"] == pytest.approx(18.0)


@pytest.mark.anyio
async def test_import_manifest_rejects_oversized_files(
    client, mock_db, test_user, auth_headers, fake_storage, monkeypatch
):
    monkeypatch.setattr("app.api.v1.lego_assembly._MAX_UPLOAD_BYTES", 8)
    mock_db.execute = AsyncMock(side_effect=[_scalar_result(test_user)])

    response = await client.post(
        "/api/v1/lego-assembly/import-manifest",
        headers=auth_headers,
        files=_multipart(_manifest(), ["fam_podium.glb"]),  # body exceeds 8 bytes
    )

    assert response.status_code == 413
    assert "capped" in response.json()["detail"]
    assert fake_storage == {}  # nothing was uploaded before the rejection


@pytest.mark.anyio
async def test_reimport_updates_existing_entries_instead_of_duplicating(
    client, mock_db, test_user, auth_headers, fake_storage
):
    existing = ModelLibraryEntry(
        id=uuid.uuid4(),
        owner_id=test_user.id,
        name="Old name",
        category="lego_module",
        model_url="/api/v1/files/old/floor.glb",
        metadata_={"lego": {
            "family": "nordic-timber-midrise", "role": "floor", "enabled": True,
            "variant_key": "typical_a", "lod": 0,
        }},
    )
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalars_result([existing]),
        ]
    )

    response = await client.post(
        "/api/v1/lego-assembly/import-manifest",
        headers=auth_headers,
        files=_multipart(_manifest(assembled={}), ["fam_floor.glb"]),
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload["imported"]) == 1
    assert payload["imported"][0]["id"] == str(existing.id)
    assert payload["imported"][0]["role"] == "floor"
    assert payload["imported"][0]["action"] == "updated"
    assert payload["imported"][0]["model_url"].startswith(
        f"/api/v1/files/library/lego/{test_user.id}/nordic-timber-midrise/floor--typical_a--lod0.glb?v="
    )
    mock_db.add.assert_not_called()
    assert existing.name == "Nordic Timber Mid-Rise — floor / typical_a"
    assert "/nordic-timber-midrise/floor--typical_a--lod0.glb?v=" in existing.model_url
    assert existing.metadata_["lego"]["height_m"] == pytest.approx(3.2)
    assert existing.metadata_["lego"]["validation_status"] == "unknown"


@pytest.mark.anyio
async def test_failed_validation_report_rejected_unless_forced(
    client, mock_db, test_user, auth_headers, fake_storage
):
    mock_db.execute = AsyncMock(side_effect=[_scalar_result(test_user)])
    response = await client.post(
        "/api/v1/lego-assembly/import-manifest",
        headers=auth_headers,
        files=_multipart(_manifest(), ["fam_floor.glb"], report={"status": "fail"}),
    )
    assert response.status_code == 422
    assert "force=true" in response.json()["detail"]
    assert fake_storage == {}  # nothing hit storage

    # Same payload with ?force=true goes through.
    mock_db.execute = AsyncMock(
        side_effect=[_scalar_result(test_user), _scalars_result([])]
    )
    response = await client.post(
        "/api/v1/lego-assembly/import-manifest",
        headers=auth_headers,
        params={"force": "true"},
        files=_multipart(_manifest(), ["fam_floor.glb"], report={"status": "fail"}),
    )
    assert response.status_code == 200, response.text
    imported = response.json()["imported"]
    assert [item["role"] for item in imported] == ["floor"]


@pytest.mark.anyio
async def test_malformed_manifest_returns_400(client, mock_db, test_user, auth_headers, fake_storage):
    mock_db.execute = AsyncMock(side_effect=[_scalar_result(test_user)])
    response = await client.post(
        "/api/v1/lego-assembly/import-manifest",
        headers=auth_headers,
        files=_multipart(
            _manifest(manifest_schema=1, family="", modules=[]),
            ["fam_floor.glb"],
        ),
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "manifest_schema" in detail and "family" in detail and "modules" in detail

    # Non-JSON manifest is also a 400, not a 500.
    mock_db.execute = AsyncMock(side_effect=[_scalar_result(test_user)])
    response = await client.post(
        "/api/v1/lego-assembly/import-manifest",
        headers=auth_headers,
        files=[
            ("manifest", ("manifest.json", b"not-json{", "application/json")),
            ("files", ("fam_floor.glb", b"glb", "model/gltf-binary")),
        ],
    )
    assert response.status_code == 400
    assert "not valid JSON" in response.json()["detail"]


# ---------------------------------------------------------------------------
# API: recipe persistence
# ---------------------------------------------------------------------------


def _recipe_body():
    return {
        "schema_version": 1,
        "module_family": "nordic-timber-midrise",
        "archetype_id": "nordic_timber_midrise",
        "reuse_keys": ["nordic"],
        "target": {"width_m": 20.0, "depth_m": 16.0, "floors": 6},
        "instances": [
            {"role": "podium", "model_url": "/api/v1/files/a.glb", "repeat": 1},
            {"role": "floor", "model_url": "/api/v1/files/b.glb", "repeat": 4},
            {"role": "roof", "model_url": "/api/v1/files/c.glb", "repeat": 1},
        ],
        "assembled_height_m": 18.0,
        "fit": {"scale_x": 1.0, "scale_y": 1.0},
        "assembled_preview_url": None,
    }


@pytest.mark.anyio
async def test_recipe_save_get_roundtrip_preserves_instances(client, mock_db, test_user, auth_headers):
    project = FakeProject(owner_id=test_user.id)
    building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        specifications={
            "modelUrlWorkflow": {"model_url": "/api/v1/files/original.glb"},
            "plannedMassing": {
                "schema_version": 1,
                "source": "community_3d",
                "source_zone_id": "old-zone",
                "height_meters": 12,
            },
        },
    )
    linked_zone = _make_zone(
        project,
        building_id=building.id,
        building_ids=[str(building.id)],
        properties={
            "_plan_role": "building",
            "community_3d": {
                "state": "compiled",
                "kind": "building",
                "generator": "lego_assembly",
            },
        },
    )
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # POST: require_auth
            _scalar_result(building),   # POST: building lookup
            _scalar_result(project),    # POST: project lookup (owner -> no share query)
            _scalar_result(project.id), # POST: project mutation lock
            _scalars_result([linked_zone]), # POST: linked Community 3D zones
            _scalar_result(test_user),  # GET: require_auth
            _scalar_result(building),   # GET: building lookup
            _scalar_result(project),    # GET: project lookup
        ]
    )

    body = _recipe_body()
    response = await client.post(
        f"/api/v1/lego-assembly/recipes/{building.id}", headers=auth_headers, json=body
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "saved"
    assert linked_zone.properties["community_3d"]["state"] == "stale"

    # Untouched workflow fields survive the copy-update-reassign.
    assert building.specifications["modelUrlWorkflow"]["model_url"] == "/api/v1/files/original.glb"

    response = await client.get(
        f"/api/v1/lego-assembly/recipes/{building.id}", headers=auth_headers
    )
    assert response.status_code == 200
    saved = response.json()["legoAssembly"]
    assert saved["instances"] == body["instances"]
    assert saved["instances"][1]["repeat"] == 4
    assert saved["target"] == body["target"]
    assert saved["module_family"] == "nordic-timber-midrise"


@pytest.mark.anyio
async def test_recipe_delete_clears_only_lego_key(client, mock_db, test_user, auth_headers):
    project = FakeProject(owner_id=test_user.id)
    building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        specifications={
            "legoAssembly": {"module_family": "x", "instances": []},
            "modelUrlWorkflow": {"model_url": "/api/v1/files/original.glb"},
        },
    )
    linked_zone = _make_zone(
        project,
        building_id=building.id,
        building_ids=[str(building.id)],
        properties={
            "_plan_role": "building",
            "community_3d": {
                "state": "compiled",
                "kind": "building",
                "generator": "lego_assembly",
            },
        },
    )
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(building),
            _scalar_result(project),
            _scalar_result(project.id),
            _scalars_result([linked_zone]),
        ]
    )

    response = await client.delete(
        f"/api/v1/lego-assembly/recipes/{building.id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "removed"
    assert "legoAssembly" not in building.specifications
    assert building.specifications["modelUrlWorkflow"]["model_url"] == "/api/v1/files/original.glb"
    assert linked_zone.properties["community_3d"]["state"] == "stale"


@pytest.mark.anyio
async def test_recipe_save_denied_for_non_member(client, mock_db, test_user, auth_headers):
    project = FakeProject(owner_id=uuid.uuid4())  # someone else's project
    building = Building(id=uuid.uuid4(), project_id=project.id, specifications=None)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(building),
            _scalar_result(project),
            _scalar_result(None),  # no editor share for this user
        ]
    )

    response = await client.post(
        f"/api/v1/lego-assembly/recipes/{building.id}", headers=auth_headers, json=_recipe_body()
    )
    assert response.status_code == 403
    assert building.specifications is None


@pytest.mark.anyio
async def test_recipe_404_when_building_missing(client, mock_db, test_user, auth_headers):
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(None),  # building lookup misses
        ]
    )
    response = await client.get(
        f"/api/v1/lego-assembly/recipes/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# API: place (zone-addressed recipe save + building ensure)
# ---------------------------------------------------------------------------


def _make_zone(
    project,
    *,
    building_id=None,
    building_ids=None,
    zone_type="building",
    properties=None,
    geometry="SRID=4326;POLYGON((0 0,1 0,1 1,0 1,0 0))",
):
    from app.models.models import SiteZone

    return SiteZone(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Hotel Site",
        zone_type=zone_type,
        geometry=geometry,
        properties=properties,
        building_id=building_id,
        building_ids=building_ids,
        updated_at=datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc),
    )


def _community_item(zone, *, recipe=None):
    item = {
        "zone_id": str(zone.id),
        "source_updated_at": zone.updated_at.isoformat(),
    }
    if recipe is not None:
        item["recipe"] = recipe
    return item


def _calgary_rectangle_ewkt(width_m: float, depth_m: float) -> str:
    """Small WGS84 rectangle suitable for metric Public Realm LEGO tests."""

    origin_lon = -114.08
    origin_lat = 51.04
    longitude_span = width_m / 70_000.0
    latitude_span = depth_m / 111_000.0
    return (
        "SRID=4326;POLYGON(("
        f"{origin_lon} {origin_lat},"
        f"{origin_lon + longitude_span} {origin_lat},"
        f"{origin_lon + longitude_span} {origin_lat + latitude_span},"
        f"{origin_lon} {origin_lat + latitude_span},"
        f"{origin_lon} {origin_lat}"
        "))"
    )


def _recipe_from_plan(plan, catalog_fingerprint: str):
    return {
        "schema_version": 1,
        "module_family": plan["family"],
        "archetype_id": plan["archetype_id"],
        "reuse_keys": plan["reuse_keys"],
        "target": plan["target"],
        "instances": plan["instances"],
        "assembled_height_m": plan["assembled_height_m"],
        "fit": plan["fit"],
        "assembled_preview_url": None,
        "catalog_fingerprint": catalog_fingerprint,
    }


@pytest.mark.anyio
async def test_place_creates_and_links_building_when_zone_has_none(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    zone = _make_zone(project)
    added: list = []
    mock_db.add.side_effect = added.append
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # require_auth
            _scalar_result(zone),       # zone lookup
            _scalar_result(project),    # project lookup (owner -> no share query)
            _scalar_result(project.id), # project mutation lock
        ]
    )

    body = {**_recipe_body(), "building_name": "Hotel Particulier"}
    response = await client.post(
        f"/api/v1/lego-assembly/place/{zone.id}", headers=auth_headers, json=body
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "placed"
    assert payload["building_created"] is True
    assert payload["zone_id"] == str(zone.id)

    assert len(added) == 1
    building = added[0]
    assert str(building.id) == payload["building_id"]
    assert building.project_id == project.id
    assert building.name == "Hotel Particulier"
    # footprint comes from the zone polygon so the globe stack has a ring
    assert building.footprint == zone.geometry
    assert building.floor_count == body["target"]["floors"]
    assert building.rotation_degrees == 0.0
    assert zone.building_id == building.id
    assert zone.building_ids == [str(building.id)]

    saved = building.specifications["legoAssembly"]
    assert saved["module_family"] == body["module_family"]
    assert saved["instances"] == body["instances"]
    assert "building_name" not in saved
    assert building.specifications["lego_placed"] is True
    assert zone.properties["community_3d"]["kind"] == "building"
    assert zone.properties["community_3d"]["generator"] == "lego_assembly"


@pytest.mark.anyio
async def test_place_reuses_existing_building_and_preserves_specifications(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        floor_count=4,
        footprint="SRID=4326;POLYGON((0 0,2 0,2 2,0 2,0 0))",
        specifications={"modelUrlWorkflow": {"model_url": "/api/v1/files/original.glb"}},
    )
    zone = _make_zone(project, building_id=building.id, building_ids=[str(building.id)])
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # require_auth
            _scalar_result(zone),       # zone lookup
            _scalar_result(project),    # project lookup
            _scalar_result(project.id), # project mutation lock
            _scalar_result(building),   # existing building lookup
        ]
    )

    response = await client.post(
        f"/api/v1/lego-assembly/place/{zone.id}", headers=auth_headers, json=_recipe_body()
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["building_created"] is False
    assert payload["building_id"] == str(building.id)

    mock_db.add.assert_not_called()
    # The zone ring is the orientation source of truth: every re-place syncs
    # the building footprint from the CURRENT zone geometry so rotating or
    # reshaping the zone rotates the compiled building (2026-07-24 fix).
    # Floor count, when already set, remains authoritative.
    assert building.footprint == zone.geometry
    assert building.floor_count == 4
    # copy-update-reassign: the untouched workflow fields survive
    assert building.specifications["modelUrlWorkflow"]["model_url"] == "/api/v1/files/original.glb"
    assert building.specifications["legoAssembly"]["module_family"] == "nordic-timber-midrise"
    assert building.specifications["lego_placed"] is True
    assert "plannedMassing" not in building.specifications
    assert zone.properties["community_3d"]["state"] == "compiled"


def test_community_artifact_selection_requires_complete_ownership_marker():
    project_id = uuid.uuid4()
    current_zone_id = uuid.uuid4()
    replaced_zone_id = uuid.uuid4()

    def _building(specifications):
        return Building(
            id=uuid.uuid4(),
            project_id=project_id,
            name="selection fixture",
            specifications=specifications,
        )

    current = _building({
        "community3DRepresentation": {
            "schema_version": 1,
            "zone_id": str(current_zone_id),
            "generator": "lego_assembly",
            "representation_hash": "a" * 64,
            "compiled_at": "2026-07-21T12:00:00+00:00",
        },
    })
    replaced = _building({
        "community3DRepresentation": {
            "schema_version": 1,
            "zone_id": str(replaced_zone_id),
            "generator": "planned_massing",
            "representation_hash": "b" * 64,
            "compiled_at": "2026-07-21T12:00:00+00:00",
        },
    })
    unmarked = _building({"legoAssembly": {"module_family": "preserve-me"}})
    malformed = _building({
        "community3DRepresentation": {
            "schema_version": 1,
            "zone_id": str(replaced_zone_id),
            "generator": "unknown_generator",
            "representation_hash": "c" * 64,
            "compiled_at": "2026-07-21T12:00:00+00:00",
        },
    })

    buildings = [current, replaced, unmarked, malformed]
    assert community_3d_buildings_for_zones(buildings, {replaced_zone_id}) == [replaced]
    assert stale_community_3d_buildings(buildings, {current_zone_id}) == [replaced]


@pytest.mark.anyio
async def test_place_community_compiles_mixed_plan_with_one_server_timestamp(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    building_zone = _make_zone(project, properties={"_plan_role": "building"})
    park_zone = _make_zone(
        project,
        zone_type="green_space",
        properties={"_plan_role": "open_space", "green_space_archetype_id": "neighborhood_park"},
    )
    street_zone = _make_zone(
        project,
        zone_type="road",
        properties={"_plan_role": "street", "road_archetype_id": "main_street_complete"},
    )
    added: list = []
    mock_db.add.side_effect = added.append
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(building_zone), _scalar_result(project),
        _scalar_result(park_zone), _scalar_result(project),
        _scalar_result(street_zone), _scalar_result(project),
        _scalar_result(project.id),  # serialize project-wide compilation
        _scalars_result([building_zone, park_zone, street_zone]),
        _scalars_result([]),  # project buildings: no stale derived artifacts
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [
            _community_item(building_zone, recipe=_recipe_body()),
            _community_item(park_zone),
            _community_item(street_zone),
        ]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "compiled"
    assert payload["counts"] == {"building": 1, "park": 1, "street": 1}
    assert len(payload["items"]) == 3
    assert len(added) == 1
    assert added[0].specifications["legoAssembly"]["module_family"] == "nordic-timber-midrise"
    stamps = {
        zone.properties["community_3d"]["compiled_at"]
        for zone in (building_zone, park_zone, street_zone)
    }
    assert stamps == {payload["compiled_at"]}
    assert park_zone.properties["green_space_archetype_id"] == "neighborhood_park"
    assert street_zone.properties["road_archetype_id"] == "main_street_complete"
    assert park_zone.properties["community_3d"]["generator"] == "park_kit"
    assert street_zone.properties["community_3d"]["generator"] == "street_section"
    mock_db.commit.assert_not_awaited()


@pytest.mark.anyio
async def test_place_community_persists_and_hashes_strict_ai_public_realm_recipe(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    street_zone = _make_zone(
        project,
        zone_type="road",
        geometry=_calgary_rectangle_ewkt(200, 22),
        properties={
            "_plan_scenario": "community_wellbeing",
            "_plan_role": "street",
            "street_role": "spine",
            "road_archetype_id": "main_street_complete",
            "road_selected_variant_id": "main_street_complete_v2",
            "width": 22,
        },
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(street_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([street_zone]),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(street_zone)]},
    )

    assert response.status_code == 200, response.text
    recipe = street_zone.properties["public_realm_lego"]
    assert recipe["family_id"] == "street_complete_main_22m"
    assert recipe["family_version"] == 1
    assert recipe["variant_id"] == "main_street_complete_v2"
    assert recipe["appearance_kit_id"] == "european_cobblestone_v1"
    assert recipe["target"]["row_width_m"] == 22
    assert len(recipe["catalog_fingerprint"]) == 64
    assert len(recipe["capability_fingerprint"]) == 64
    assert len(recipe["recipe_hash"]) == 64
    assert len(street_zone.properties["plan_centerline"]) == 2
    assert street_zone.properties["community_3d"]["representation_hash"]
    assert response.json()["items"][0]["generator"] == "street_section"


@pytest.mark.parametrize(
    "existing_centerline",
    [
        pytest.param(
            {"coordinates": [[-114.08, 51.04], [-114.079, 51.04]]},
            id="malformed-object",
        ),
        pytest.param(
            [[-113.5, 51.5], [-113.49, 51.5]],
            id="stale-outside-current-zone",
        ),
        pytest.param(
            [
                [-114.08 + 100 / 70_000, 51.04],
                [-114.08 + 100 / 70_000, 51.04 + 18 / 111_000],
            ],
            id="contained-but-crosswise",
        ),
    ],
)
@pytest.mark.anyio
async def test_place_community_recovers_invalid_existing_street_centerline(
    client,
    mock_db,
    test_user,
    auth_headers,
    existing_centerline,
):
    from app.api.v1.lego_assembly import _community_source_geometry
    from app.services.plan_geometry.generator import (
        validate_street_plan_centerline_wgs84,
    )

    project = FakeProject(owner_id=test_user.id)
    street_zone = _make_zone(
        project,
        zone_type="road",
        geometry=_calgary_rectangle_ewkt(200, 18),
        properties={
            "_plan_scenario": "city_policy",
            "_plan_role": "street",
            "street_role": "spine",
            "road_archetype_id": "main_street_complete",
            "road_selected_variant_id": "main_street_complete_v0",
            "width": 18,
            "plan_centerline": existing_centerline,
            "community_3d": {
                "state": "compiled",
                "source_hash": "a" * 64,
            },
        },
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(street_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([street_zone]),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(street_zone)]},
    )

    assert response.status_code == 200, response.text
    recovered = street_zone.properties["plan_centerline"]
    assert recovered != existing_centerline
    assert validate_street_plan_centerline_wgs84(
        _community_source_geometry(street_zone),
        recovered,
    )
    assert street_zone.properties["public_realm_lego"]["family_id"] == (
        "street_complete_main_18m"
    )
    assert street_zone.properties["community_3d"]["state"] == "compiled"


@pytest.mark.anyio
async def test_place_community_rejects_invalid_centerline_when_recovery_is_unsafe(
    client,
    mock_db,
    test_user,
    auth_headers,
):
    project = FakeProject(owner_id=test_user.id)
    malformed = {"coordinates": [[-114.08, 51.04], [-114.079, 51.04]]}
    street_zone = _make_zone(
        project,
        zone_type="road",
        geometry=_calgary_rectangle_ewkt(18, 18),
        properties={
            "_plan_scenario": "city_policy",
            "_plan_role": "street",
            "street_role": "spine",
            "road_archetype_id": "main_street_complete",
            "road_selected_variant_id": "main_street_complete_v0",
            "width": 18,
            "plan_centerline": malformed,
        },
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(street_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([street_zone]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(street_zone)]},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "invalid_plan_centerline"
    assert detail["zone_id"] == str(street_zone.id)
    assert street_zone.properties["plan_centerline"] == malformed
    assert "public_realm_lego" not in street_zone.properties


@pytest.mark.parametrize(
    (
        "archetype_id",
        "legacy_variant_id",
        "canonical_variant_id",
        "row_width_m",
        "appearance_kit_id",
    ),
    [
        (
            "yield_street",
            "yield_street_v2",
            "yield_street_v0",
            10,
            "dutch_woonerf_v1",
        ),
        (
            "woonerf_shared_street",
            "woonerf_shared_street_v3",
            "woonerf_shared_street_v0",
            10,
            "dutch_woonerf_v1",
        ),
        (
            "calgary_local",
            "calgary_local_v1",
            "calgary_local_v0",
            16,
            "calgary_contemporary_native",
        ),
        (
            "green_alley",
            "green_alley_v3",
            "green_alley_v0",
            5,
            "green_corridor_v1",
        ),
        (
            "toronto_laneway",
            "toronto_laneway_v2",
            "toronto_laneway_v0",
            5,
            "calgary_contemporary_native",
        ),
    ],
)
@pytest.mark.anyio
async def test_place_community_migrates_known_ai_street_variants_and_backfills_line(
    client,
    mock_db,
    test_user,
    auth_headers,
    archetype_id,
    legacy_variant_id,
    canonical_variant_id,
    row_width_m,
    appearance_kit_id,
):
    from app.api.v1.lego_assembly import _community_source_geometry

    project = FakeProject(owner_id=test_user.id)
    street_zone = _make_zone(
        project,
        zone_type="road",
        geometry=_calgary_rectangle_ewkt(200, row_width_m),
        properties={
            "_plan_scenario": "city_policy",
            "_plan_role": "street",
            "street_role": "local",
            "road_archetype_id": archetype_id,
            "road_selected_variant_id": legacy_variant_id,
            "width": row_width_m,
            "community_3d": {
                "state": "compiled",
                "source_hash": "a" * 64,
            },
        },
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(street_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([street_zone]),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(street_zone)]},
    )

    assert response.status_code == 200, response.text
    assert street_zone.properties["road_selected_variant_id"] == canonical_variant_id
    assert len(street_zone.properties["plan_centerline"]) == 2
    recipe = street_zone.properties["public_realm_lego"]
    assert recipe["variant_id"] == canonical_variant_id
    assert recipe["appearance_kit_id"] == appearance_kit_id
    compiled = street_zone.properties["community_3d"]
    assert compiled["state"] == "compiled"
    assert compiled["source_hash"] == community_3d_source_hash(
        street_zone.zone_type,
        _community_source_geometry(street_zone),
        street_zone.properties,
    )
    assert compiled["representation_hash"]


@pytest.mark.anyio
async def test_place_community_rejects_unsupported_ai_public_realm_structurally(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    park_zone = _make_zone(
        project,
        zone_type="green_space",
        geometry=_calgary_rectangle_ewkt(30, 30),
        properties={
            "_plan_scenario": "community_wellbeing",
            "_plan_role": "open_space",
            "green_space_archetype_id": "invented_magic_park",
        },
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(park_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([park_zone]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(park_zone)]},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "family_not_found"
    assert detail["kind"] == "park"
    assert detail["zone_id"] == str(park_zone.id)
    assert detail["requested"]["archetype_id"] == "invented_magic_park"
    assert detail["supported_families"]
    assert "public_realm_lego" not in park_zone.properties
    assert "community_3d" not in park_zone.properties
    mock_db.add.assert_not_called()


@pytest.mark.anyio
async def test_place_community_removes_only_stale_marked_buildings(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    current_zone = _make_zone(project, properties={"_plan_role": "building"})
    deleted_zone_id = uuid.uuid4()
    stale_building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        name="old generated building",
        specifications={
            "community3DRepresentation": {
                "schema_version": 1,
                "zone_id": str(deleted_zone_id),
                "generator": "lego_assembly",
                "representation_hash": "d" * 64,
                "compiled_at": "2026-07-21T12:00:00+00:00",
            },
        },
    )
    user_building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        name="unmarked user building",
        specifications={"legoAssembly": {"module_family": "preserve-me"}},
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(current_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([current_zone]),
        _scalars_result([stale_building, user_building]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(current_zone, recipe=_recipe_body())]},
    )

    assert response.status_code == 200, response.text
    assert response.json()["stale_buildings_removed"] == 1
    mock_db.delete.assert_awaited_once_with(stale_building)
    assert mock_db.delete.await_args.args[0] is not user_building


@pytest.mark.parametrize(
    ("zone_type", "properties", "expected_kind", "expected_generator"),
    [
        (
            "green_space",
            {
                "_plan_role": "open_space",
                "green_space_archetype_id": "neighborhood_park",
            },
            "park",
            "park_kit",
        ),
        (
            "road",
            {
                "_plan_role": "street",
                "road_archetype_id": "main_street_complete",
            },
            "street",
            "street_section",
        ),
    ],
)
@pytest.mark.anyio
async def test_place_community_removes_owned_building_when_source_becomes_public_realm(
    client,
    mock_db,
    test_user,
    auth_headers,
    zone_type,
    properties,
    expected_kind,
    expected_generator,
):
    project = FakeProject(owner_id=test_user.id)
    derived_building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        name="formerly compiled building",
        specifications={},
    )
    user_building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        name="linked user building",
        specifications={"legoAssembly": {"module_family": "preserve-me"}},
    )
    public_realm_zone = _make_zone(
        project,
        building_id=derived_building.id,
        building_ids=[str(derived_building.id), str(user_building.id)],
        zone_type=zone_type,
        properties=properties,
    )
    derived_building.specifications = {
        "community3DRepresentation": {
            "schema_version": 1,
            "zone_id": str(public_realm_zone.id),
            "generator": "lego_assembly",
            "representation_hash": "e" * 64,
            "compiled_at": "2026-07-21T12:00:00+00:00",
        },
    }
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(public_realm_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([public_realm_zone]),
        _scalars_result([derived_building, user_building]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(public_realm_zone)]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["stale_buildings_removed"] == 1
    assert payload["items"][0]["kind"] == expected_kind
    assert payload["items"][0]["generator"] == expected_generator
    mock_db.delete.assert_awaited_once_with(derived_building)
    assert public_realm_zone.building_id is None
    assert public_realm_zone.building_ids == [str(user_building.id)]


@pytest.mark.anyio
async def test_place_community_rejects_recipe_planned_from_stale_same_kind_revision(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    browser_zone = _make_zone(
        project,
        properties={"_plan_role": "building", "floors": 5},
    )
    current_zone = _make_zone(
        project,
        properties={"_plan_role": "building", "floors": 12},
    )
    current_zone.id = browser_zone.id
    current_zone.updated_at = datetime(2026, 7, 20, 12, 5, tzinfo=timezone.utc)
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(current_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([current_zone]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(browser_zone, recipe=_recipe_body())]},
    )

    assert response.status_code == 409
    assert "changed while its 3D recipe was being prepared" in response.json()["detail"]
    assert current_zone.properties.get("community_3d") is None
    mock_db.add.assert_not_called()


def _ai_recipe_inventory():
    return [
        entry("ai-podium", "AI podium", "podium", height=4.5),
        entry("ai-floor", "AI floor", "floor", height=3.2),
        entry("ai-setback", "AI setback", "setback", height=3.2),
        entry("ai-roof", "AI roof", "roof", height=1.0),
    ]


def _plan_for_ai_recipe(entries):
    descriptors = [
        descriptor
        for item in entries
        if (descriptor := descriptor_from_library_entry(item)) is not None
    ]
    return plan_vertical_assembly(
        descriptors,
        AssemblyRequest(
            target_width_m=24,
            target_depth_m=18,
            target_floors=6,
            archetype_id="nordic-midrise",
            allow_setback=False,
        ),
    )


@pytest.mark.anyio
async def test_place_community_rejects_stale_ai_catalog_under_locked_inventory(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    stale_fingerprint = "a" * 64
    zone = _make_zone(
        project,
        properties={
            "_plan_role": "building",
            "_plan_scenario": "community_wellbeing",
            "_lego_catalog_fingerprint": stale_fingerprint,
        },
    )
    recipe = _recipe_body()
    recipe["catalog_fingerprint"] = stale_fingerprint
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([zone]),
        _scalar_result(project),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(zone, recipe=recipe)]},
    )

    assert response.status_code == 409
    assert "catalogue changed" in response.json()["detail"]
    library_query = mock_db.execute.await_args_list[-1].args[0]
    assert library_query._for_update_arg is not None
    assert zone.properties.get("community_3d") is None
    mock_db.add.assert_not_called()
    mock_db.delete.assert_not_awaited()


@pytest.mark.anyio
async def test_place_community_rejects_changed_ai_module_even_when_catalog_shape_matches(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    planned_entries = _ai_recipe_inventory()
    current_entries = _ai_recipe_inventory()
    current_entries[1].model_url = "https://example.test/ai-floor.glb?v=reimported"
    planned_catalog = build_lego_planning_catalog(planned_entries)
    current_catalog = build_lego_planning_catalog(current_entries)
    # Catalogue capabilities are intentionally unchanged; exact module
    # validation must still catch the re-imported renderer asset.
    assert planned_catalog.fingerprint == current_catalog.fingerprint

    zone = _make_zone(
        project,
        properties={
            "_plan_role": "building",
            "_plan_scenario": "community_wellbeing",
            "_lego_catalog_fingerprint": current_catalog.fingerprint,
        },
    )
    recipe = _recipe_from_plan(
        _plan_for_ai_recipe(planned_entries),
        planned_catalog.fingerprint,
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([zone]),
        _scalar_result(project),
        _scalars_result(current_entries),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(zone, recipe=recipe)]},
    )

    assert response.status_code == 409
    assert "modules used" in response.json()["detail"]
    assert zone.properties.get("community_3d") is None
    mock_db.add.assert_not_called()
    mock_db.delete.assert_not_awaited()


@pytest.mark.anyio
async def test_place_community_accepts_current_ai_recipe_before_persisting(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    entries = _ai_recipe_inventory()
    catalog = build_lego_planning_catalog(entries)
    zone = _make_zone(
        project,
        properties={
            "_plan_role": "building",
            "_plan_scenario": "community_wellbeing",
            "_lego_catalog_fingerprint": catalog.fingerprint,
        },
    )
    recipe = _recipe_from_plan(_plan_for_ai_recipe(entries), catalog.fingerprint)
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([zone]),
        _scalar_result(project),
        _scalars_result(entries),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(zone, recipe=recipe)]},
    )

    assert response.status_code == 200, response.text
    assert response.json()["items"][0]["generator"] == "lego_assembly"
    assert zone.properties["community_3d"]["state"] == "compiled"
    assert mock_db.add.call_count == 1


@pytest.mark.anyio
async def test_place_one_rejects_stale_ai_catalog_before_mutation(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    entries = _ai_recipe_inventory()
    stale_fingerprint = "a" * 64
    zone = _make_zone(
        project,
        properties={
            "_plan_role": "building",
            "_plan_scenario": "community_wellbeing",
            "_lego_catalog_fingerprint": stale_fingerprint,
        },
    )
    recipe = _recipe_from_plan(_plan_for_ai_recipe(entries), stale_fingerprint)
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone),
        _scalar_result(project),
        _scalar_result(project.id),
        _scalar_result(project),
        _scalars_result(entries),
    ])

    response = await client.post(
        f"/api/v1/lego-assembly/place/{zone.id}",
        headers=auth_headers,
        json=recipe,
    )

    assert response.status_code == 409
    assert "catalogue changed" in response.json()["detail"]
    assert zone.building_id is None
    assert zone.properties.get("community_3d") is None
    mock_db.add.assert_not_called()


@pytest.mark.anyio
async def test_place_one_accepts_current_ai_recipe_with_setbacks_disabled(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    entries = _ai_recipe_inventory()
    catalog = build_lego_planning_catalog(entries)
    zone = _make_zone(
        project,
        properties={
            "_plan_role": "building",
            "_plan_scenario": "community_wellbeing",
            "_lego_catalog_fingerprint": catalog.fingerprint,
        },
    )
    planned = _plan_for_ai_recipe(entries)
    assert all(instance["role"] != "setback" for instance in planned["instances"])
    recipe = _recipe_from_plan(planned, catalog.fingerprint)
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone),
        _scalar_result(project),
        _scalar_result(project.id),
        _scalar_result(project),
        _scalars_result(entries),
    ])

    response = await client.post(
        f"/api/v1/lego-assembly/place/{zone.id}",
        headers=auth_headers,
        json=recipe,
    )

    assert response.status_code == 200, response.text
    assert response.json()["building_created"] is True
    assert zone.properties["community_3d"]["generator"] == "lego_assembly"
    assert mock_db.add.call_count == 1


@pytest.mark.anyio
async def test_place_community_preserves_all_six_public_realm_archetype_contracts(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    archetype_specs = [
        ("green_space", "green_space_archetype_id", "neighborhood_park"),
        ("green_space", "green_space_archetype_id", "urban_pocket_park"),
        ("green_space", "green_space_archetype_id", "linear_park_greenway"),
        ("plaza", "plaza_archetype_id", "formal_civic_plaza"),
        ("plaza", "plaza_archetype_id", "fountain_water_feature"),
        ("green_space", "green_space_archetype_id", "stormwater_retention_pond"),
    ]
    zones = [
        _make_zone(
            project,
            zone_type=zone_type,
            properties={"_plan_role": "open_space", property_name: archetype_id},
        )
        for zone_type, property_name, archetype_id in archetype_specs
    ]
    db_results = [_scalar_result(test_user)]
    for zone in zones:
        db_results.extend([_scalar_result(zone), _scalar_result(project)])
    db_results.append(_scalar_result(project.id))
    db_results.append(_scalars_result(zones))
    db_results.append(_scalars_result([]))
    mock_db.execute = AsyncMock(side_effect=db_results)

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(zone) for zone in zones]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["counts"] == {"building": 0, "park": 6, "street": 0}
    assert [item["generator"] for item in payload["items"]] == ["park_kit"] * 6
    assert {item["kind"] for item in payload["items"]} == {"park"}
    assert {
        zone.properties["community_3d"]["compiled_at"] for zone in zones
    } == {payload["compiled_at"]}
    for zone, (_, property_name, archetype_id) in zip(zones, archetype_specs):
        assert zone.properties[property_name] == archetype_id
        assert zone.properties["community_3d"]["state"] == "compiled"
        assert zone.properties["community_3d"]["generator"] == "park_kit"
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_awaited()


@pytest.mark.anyio
async def test_place_community_persists_exact_footprint_massing_without_family_recipe(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    zone = _make_zone(
        project,
        properties={
            "_plan_role": "building",
            "development_archetype_id": "new_york_corner_bodega",
            "floors": 3,
            "floor_height": 3.5,
        },
    )
    added: list = []
    mock_db.add.side_effect = added.append
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([zone]),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(zone)]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["counts"] == {"building": 1, "park": 0, "street": 0}
    assert payload["items"][0]["generator"] == "planned_massing"
    assert len(added) == 1
    building = added[0]
    assert building.footprint == zone.geometry
    assert building.floor_count == 3
    assert building.height_meters == 10.5
    assert zone.building_id == building.id
    assert zone.properties["community_3d"]["generator"] == "planned_massing"
    fallback = building.specifications["plannedMassing"]
    assert fallback["archetype_id"] == "new_york_corner_bodega"
    assert fallback["height_meters"] == 10.5
    assert "legoAssembly" not in building.specifications
    mock_db.commit.assert_not_awaited()


@pytest.mark.anyio
async def test_place_community_stamps_lod_only_generated_model_as_visible_meshy_representation(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        name="LOD model",
        footprint="SRID=4326;POLYGON((0 0,2 0,2 2,0 2,0 0))",
        height_meters=24,
        floor_count=7,
        model_url=None,
        lod_urls={"0": "/api/v1/files/lod-zero.glb"},
        specifications={
            "legoAssembly": {
                "schema_version": 1,
                "instances": [{"model_url": "/old.glb"}],
            },
            "lego_placed": True,
        },
    )
    zone = _make_zone(
        project,
        building_id=building.id,
        building_ids=[str(building.id)],
        properties={
            "_plan_role": "building",
            "development_archetype_id": "family_pending",
        },
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([zone]),
        _scalars_result([]),
        _scalar_result(building),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(zone)]},
    )

    assert response.status_code == 200, response.text
    assert zone.properties["community_3d"]["generator"] == "meshy"
    assert len(zone.properties["community_3d"]["representation_hash"]) == 64
    assert "legoAssembly" not in building.specifications
    assert "lego_placed" not in building.specifications
    assert building.specifications["plannedMassing"]["source_zone_id"] == str(zone.id)


@pytest.mark.anyio
async def test_place_community_rebuild_upgrades_massing_without_losing_public_realm(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        footprint="SRID=4326;POLYGON((0 0,2 0,2 2,0 2,0 0))",
        floor_count=3,
        height_meters=10.5,
        specifications={
            "plannedMassing": {
                "schema_version": 1,
                "source": "community_3d",
                "archetype_id": "new_york_corner_bodega",
            },
            "modelUrlWorkflow": {"status": "preserve-me"},
        },
    )
    building_zone = _make_zone(
        project,
        building_id=building.id,
        building_ids=[str(building.id)],
        properties={
            "_plan_role": "building",
            "development_archetype_id": "new_york_corner_bodega",
        },
    )
    park_zone = _make_zone(
        project,
        zone_type="green_space",
        properties={
            "_plan_role": "open_space",
            "green_space_archetype_id": "neighborhood_park",
            "park_access_points": [[-114.08, 51.04], [-114.079, 51.041]],
            "community_3d": {
                "schema_version": 1,
                "state": "compiled",
                "kind": "park",
                "generator": "park_kit",
                "compiled_at": "2026-07-17T00:00:00Z",
            },
        },
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(building_zone), _scalar_result(project),
        _scalar_result(park_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([building_zone, park_zone]),
        _scalars_result([building]),
        _scalar_result(building),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [
            _community_item(building_zone, recipe=_recipe_body()),
            _community_item(park_zone),
        ]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["counts"] == {"building": 1, "park": 1, "street": 0}
    assert payload["items"][0]["building_created"] is False
    assert payload["items"][0]["generator"] == "lego_assembly"
    assert "plannedMassing" not in building.specifications
    assert building.specifications["legoAssembly"]["module_family"] == "nordic-timber-midrise"
    assert building.specifications["modelUrlWorkflow"] == {"status": "preserve-me"}
    assert building_zone.properties["community_3d"]["generator"] == "lego_assembly"
    assert park_zone.properties["green_space_archetype_id"] == "neighborhood_park"
    assert park_zone.properties["park_access_points"] == [
        [-114.08, 51.04], [-114.079, 51.041],
    ]
    assert park_zone.properties["community_3d"]["generator"] == "park_kit"
    assert {
        building_zone.properties["community_3d"]["compiled_at"],
        park_zone.properties["community_3d"]["compiled_at"],
    } == {payload["compiled_at"]}
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_awaited()


@pytest.mark.anyio
async def test_place_community_rejects_framework_overlay_without_mutating_it(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    framework = _make_zone(
        project,
        zone_type="development_area",
        properties={"_plan_role": "framework_height", "floors": 12},
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(framework), _scalar_result(project),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(framework)]},
    )

    assert response.status_code == 422
    assert framework.properties == {"_plan_role": "framework_height", "floors": 12}
    mock_db.add.assert_not_called()


@pytest.mark.anyio
async def test_place_community_derives_residual_from_all_project_zones(
    client, mock_db, test_user, auth_headers
):
    from geoalchemy2.shape import from_shape, to_shape
    from shapely.geometry import box
    from shapely.ops import unary_union
    from app.services.site_engine import (
        WGS84_CRS,
        build_transformer,
        local_metric_crs_for_polygon,
        project_geometry,
    )

    project = FakeProject(owner_id=test_user.id)
    boundary = _make_zone(
        project,
        zone_type="site_boundary",
        geometry=from_shape(box(-114.0800, 51.0400, -114.0780, 51.0415), srid=4326),
        properties={"site_name": "Residual landscape test"},
    )
    building_zone = _make_zone(
        project,
        geometry=from_shape(box(-114.0798, 51.0402, -114.0793, 51.0407), srid=4326),
        properties={"_plan_role": "building", "floors": 4},
    )
    # This already-compiled park is intentionally absent from request.items.
    # Incremental Complete must still subtract it from residual land.
    park_zone = _make_zone(
        project,
        zone_type="green_space",
        geometry=from_shape(box(-114.0791, 51.0404, -114.0784, 51.0411), srid=4326),
        properties={
            "_plan_role": "open_space",
            "community_3d": {
                "schema_version": 1,
                "state": "compiled",
                "kind": "park",
                "generator": "park_kit",
                "compiled_at": "2026-07-19T00:00:00Z",
            },
        },
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(building_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([boundary, building_zone, park_zone]),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(building_zone)]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["residual_landscape"]["boundary_count"] == 1
    assert payload["residual_landscape"]["area_sqm"] > 0
    recipe = boundary.properties["community_3d_landscape"]
    assert recipe["state"] == "compiled"
    assert recipe["compiled_at"] == payload["compiled_at"]
    assert recipe["boundary_id"] == str(boundary.id)
    boundary_shape = to_shape(boundary.geometry)
    metric_crs = local_metric_crs_for_polygon(boundary_shape)
    to_metric = build_transformer(WGS84_CRS, metric_crs)
    expected_occupied = unary_union([
        project_geometry(to_shape(building_zone.geometry), to_metric),
        project_geometry(to_shape(park_zone.geometry), to_metric),
    ]).area
    assert recipe["occupied_area_sqm"] == pytest.approx(expected_occupied, abs=0.2)
    assert recipe["regions"]


@pytest.mark.anyio
async def test_place_community_residual_uses_visible_complete_imported_scope(
    client, mock_db, test_user, auth_headers
):
    from geoalchemy2.shape import from_shape, to_shape
    from shapely.geometry import box
    from app.services.site_engine import (
        WGS84_CRS,
        build_transformer,
        local_metric_crs_for_polygon,
        project_geometry,
    )

    project = FakeProject(owner_id=test_user.id)
    boundary = _make_zone(
        project,
        zone_type="site_boundary",
        geometry=from_shape(box(-114.0800, 51.0400, -114.0780, 51.0415), srid=4326),
    )
    selected_building = _make_zone(
        project,
        geometry=from_shape(box(-114.0798, 51.0402, -114.0793, 51.0407), srid=4326),
        properties={
            "_plan_role": "building",
            "_imported_from": "Plan — City Policy",
            "floors": 4,
        },
    )
    hidden_alternative = _make_zone(
        project,
        zone_type="green_space",
        geometry=from_shape(box(-114.0791, 51.0404, -114.0784, 51.0411), srid=4326),
        properties={
            "_plan_role": "open_space",
            "_imported_from": "Plan — Economic",
        },
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(selected_building), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([boundary, selected_building, hidden_alternative]),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={
            "items": [_community_item(selected_building)],
            "scope_zone_ids": [str(selected_building.id)],
        },
    )

    assert response.status_code == 200, response.text
    recipe = boundary.properties["community_3d_landscape"]
    boundary_shape = to_shape(boundary.geometry)
    metric_crs = local_metric_crs_for_polygon(boundary_shape)
    to_metric = build_transformer(WGS84_CRS, metric_crs)
    selected_area = project_geometry(
        to_shape(selected_building.geometry),
        to_metric,
    ).area
    hidden_area = project_geometry(
        to_shape(hidden_alternative.geometry),
        to_metric,
    ).area
    assert recipe["occupied_area_sqm"] == pytest.approx(selected_area, abs=0.2)
    assert recipe["occupied_area_sqm"] < selected_area + hidden_area - 1


@pytest.mark.anyio
async def test_place_community_accepts_exact_boundary_subset_and_excludes_outside(
    client, mock_db, test_user, auth_headers
):
    from geoalchemy2.shape import from_shape, to_shape
    from shapely.geometry import box
    from app.services.site_engine import (
        WGS84_CRS,
        build_transformer,
        local_metric_crs_for_polygon,
        project_geometry,
    )

    project = FakeProject(owner_id=test_user.id)
    boundary = _make_zone(
        project,
        zone_type="site_boundary",
        geometry=from_shape(box(-114.0800, 51.0400, -114.0780, 51.0415), srid=4326),
    )
    inside = _make_zone(
        project,
        geometry=from_shape(box(-114.0798, 51.0402, -114.0793, 51.0407), srid=4326),
        properties={"_plan_role": "building", "floors": 4},
    )
    outside = _make_zone(
        project,
        geometry=from_shape(box(-114.0700, 51.0500, -114.0690, 51.0510), srid=4326),
        properties={"_plan_role": "building", "floors": 4},
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(inside), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([boundary, inside, outside]),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={
            "items": [_community_item(inside)],
            "scope_zone_ids": [str(inside.id)],
            "scope_boundary_id": str(boundary.id),
        },
    )

    assert response.status_code == 200, response.text
    recipe = boundary.properties["community_3d_landscape"]
    boundary_shape = to_shape(boundary.geometry)
    metric_crs = local_metric_crs_for_polygon(boundary_shape)
    to_metric = build_transformer(WGS84_CRS, metric_crs)
    inside_area = project_geometry(to_shape(inside.geometry), to_metric).area
    outside_area = project_geometry(to_shape(outside.geometry), to_metric).area
    assert recipe["occupied_area_sqm"] == pytest.approx(inside_area, abs=0.2)
    assert recipe["occupied_area_sqm"] < inside_area + outside_area - 1


@pytest.mark.anyio
async def test_place_community_infers_and_persists_boundary_for_legacy_plan(
    client, mock_db, test_user, auth_headers
):
    from geoalchemy2.shape import from_shape, to_shape
    from shapely.geometry import box

    project = FakeProject(owner_id=test_user.id)
    park_zone = _make_zone(
        project,
        zone_type="green_space",
        geometry=from_shape(box(-114.0800, 51.0400, -114.0795, 51.0405), srid=4326),
        properties={"_plan_role": "open_space"},
    )
    street_zone = _make_zone(
        project,
        zone_type="road",
        geometry=from_shape(box(-114.0788, 51.0410, -114.0780, 51.0412), srid=4326),
        properties={"_plan_role": "street"},
    )
    added: list = []
    mock_db.add.side_effect = added.append
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(park_zone), _scalar_result(project),
        _scalar_result(street_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([park_zone, street_zone]),
        _scalars_result([]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [
            _community_item(park_zone),
            _community_item(street_zone),
        ]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["residual_landscape"]["boundary_count"] == 1
    assert payload["residual_landscape"]["derived_boundary_count"] == 1
    assert len(added) == 1
    boundary = added[0]
    assert boundary.zone_type == "site_boundary"
    assert to_shape(boundary.geometry).is_valid
    assert boundary.properties["_derived_site_boundary"] is True
    assert boundary.properties["community_3d_landscape"]["boundary_id"] == str(boundary.id)
    assert boundary.properties["community_3d_landscape"]["area_sqm"] > 0


@pytest.mark.anyio
async def test_place_community_rejects_ambiguous_multiple_site_boundaries(
    client, mock_db, test_user, auth_headers
):
    from geoalchemy2.shape import from_shape
    from shapely.geometry import box

    project = FakeProject(owner_id=test_user.id)
    building_zone = _make_zone(
        project,
        geometry=from_shape(box(-114.0798, 51.0402, -114.0793, 51.0407), srid=4326),
        properties={"_plan_role": "building", "floors": 4},
    )
    first_boundary = _make_zone(
        project,
        zone_type="site_boundary",
        geometry=from_shape(box(-114.0800, 51.0400, -114.0780, 51.0415), srid=4326),
    )
    second_boundary = _make_zone(
        project,
        zone_type="site_boundary",
        geometry=from_shape(box(-114.0810, 51.0395, -114.0775, 51.0420), srid=4326),
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(building_zone), _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([first_boundary, building_zone, second_boundary]),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [_community_item(building_zone)]},
    )

    assert response.status_code == 422
    assert "one authoritative site boundary" in response.json()["detail"]
    assert building_zone.properties.get("community_3d") is None
    mock_db.add.assert_not_called()


@pytest.mark.anyio
async def test_place_community_rejects_cross_project_batches_before_mutation(
    client, mock_db, test_user, auth_headers
):
    first_project = FakeProject(owner_id=test_user.id)
    second_project = FakeProject(owner_id=test_user.id)
    first_zone = _make_zone(first_project, properties={"_plan_role": "building"})
    second_zone = _make_zone(second_project, properties={"_plan_role": "building"})
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(first_zone), _scalar_result(first_project),
        _scalar_result(second_zone), _scalar_result(second_project),
    ])

    response = await client.post(
        "/api/v1/lego-assembly/place-community",
        headers=auth_headers,
        json={"items": [
            _community_item(first_zone),
            _community_item(second_zone),
        ]},
    )

    assert response.status_code == 422
    assert "one project" in response.json()["detail"]
    assert first_zone.building_id is None
    assert second_zone.building_id is None
    mock_db.add.assert_not_called()


@pytest.mark.anyio
async def test_place_backfills_missing_footprint_from_zone(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    building = Building(
        id=uuid.uuid4(), project_id=project.id, footprint=None, floor_count=None,
        specifications=None,
    )
    zone = _make_zone(project, building_id=building.id, building_ids=[str(building.id)])
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(zone),
            _scalar_result(project),
            _scalar_result(project.id),
            _scalar_result(building),
        ]
    )

    response = await client.post(
        f"/api/v1/lego-assembly/place/{zone.id}", headers=auth_headers, json=_recipe_body()
    )
    assert response.status_code == 200, response.text
    assert building.footprint == zone.geometry
    assert building.floor_count == _recipe_body()["target"]["floors"]


@pytest.mark.anyio
async def test_place_denied_for_non_member(client, mock_db, test_user, auth_headers):
    project = FakeProject(owner_id=uuid.uuid4())  # someone else's project
    zone = _make_zone(project)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(zone),
            _scalar_result(project),
            _scalar_result(None),  # no editor share
        ]
    )

    response = await client.post(
        f"/api/v1/lego-assembly/place/{zone.id}", headers=auth_headers, json=_recipe_body()
    )
    assert response.status_code == 403
    assert zone.building_id is None
    mock_db.add.assert_not_called()


@pytest.mark.anyio
async def test_place_404_when_zone_missing(client, mock_db, test_user, auth_headers):
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(None),  # zone lookup misses
        ]
    )
    response = await client.post(
        f"/api/v1/lego-assembly/place/{uuid.uuid4()}", headers=auth_headers, json=_recipe_body()
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_recipe_delete_also_clears_placed_stamp(client, mock_db, test_user, auth_headers):
    project = FakeProject(owner_id=test_user.id)
    building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        specifications={
            "legoAssembly": {"module_family": "x", "instances": []},
            "lego_placed": True,
            "modelUrlWorkflow": {"model_url": "/api/v1/files/original.glb"},
        },
    )
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(building),
            _scalar_result(project),
            _scalar_result(project.id),
            _scalars_result([]),
        ]
    )

    response = await client.delete(
        f"/api/v1/lego-assembly/recipes/{building.id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert "legoAssembly" not in building.specifications
    assert "lego_placed" not in building.specifications
    assert building.specifications["modelUrlWorkflow"]["model_url"] == "/api/v1/files/original.glb"
