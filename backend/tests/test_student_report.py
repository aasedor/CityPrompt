import copy
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from shapely.geometry import Polygon, mapping

from app.api.v1 import student_reports as routes
from app.models.student_report import StudentPlanningReport
from app.schemas.student_report import StudentDecisionRequest
from app.services.student_report import (
    analyze_snapshot,
    build_snapshot,
    digest,
    report_html,
    select_policy_sources,
)
from app.services.policy_intelligence.retrieval import ChunkRecord


def rectangle(x=0, y=0, width=0.001, height=0.001):
    lon, lat = -114.07 + x, 51.04 + y
    return Polygon(
        [
            (lon, lat),
            (lon + width, lat),
            (lon + width, lat + height),
            (lon, lat + height),
            (lon, lat),
        ]
    )


def zone(kind, geom=None, **props):
    return SimpleNamespace(
        id=uuid.uuid4(),
        name=kind.title(),
        zone_type=kind,
        geometry=geom if geom is not None else rectangle(),
        properties=props,
        is_active_boundary=kind == "site_boundary",
        building_id=None,
        building_ids=[],
    )


def snapshot(zones, buildings=None, references=None):
    project = SimpleNamespace(name="Student community", description="Our vision", site_boundary=None)
    return build_snapshot(project, zones, buildings or [], references or [], None)


def values(analysis):
    return {metric["key"]: metric["value"] for metric in analysis["metrics"]}


def test_housing_is_never_invented_for_commercial_or_industrial():
    plan = snapshot(
        [
            zone("site_boundary", rectangle(width=0.01, height=0.01)),
            zone("building", floors=4, development_type="commercial", unit_count=99),
            zone(
                "building",
                rectangle(x=0.002),
                floors=3,
                development_type="industrial",
                unit_count=70,
            ),
        ]
    )
    metrics = values(analyze_snapshot(plan))
    assert metrics["gfa_m2"] > 0
    assert metrics["recorded_units"] is None


def detached_fixture(*, compiled=True, unit_estimate=99):
    from app.services.residual_landscape import community_3d_source_hash

    parcel = zone(
        "building",
        floors=2,
        development_type="residential_single_family",
        development_archetype_id="detached_contemporary_infill",
        unit_count=unit_estimate,
    )
    building = SimpleNamespace(
        id=uuid.uuid4(),
        name="Housing plot",
        footprint=parcel.geometry,
        floor_count=2,
        height_meters=8,
        specifications={},
    )
    parcel.building_id = building.id
    parcel.building_ids = [str(building.id)]
    if compiled:
        building.specifications["legoAssembly"] = {
            "fit": {"placement_mode": "detached_lots", "dwelling_count": 3},
            "instances": [
                {"segment_id": f"dwelling-{i}", "role": role} for i in range(3) for role in ("podium", "floor", "roof")
            ],
        }
        parcel.properties["community_3d"] = {
            "state": "compiled",
            "source_hash": community_3d_source_hash(parcel.zone_type, parcel.geometry, parcel.properties),
        }
    return parcel, building


def test_compiled_detached_units_count_houses_once_and_never_count_yards_as_floor_area():
    parcel, building = detached_fixture()
    report = analyze_snapshot(snapshot([parcel], [building]))
    metrics = values(report)
    assert metrics["compiled_detached_dwellings"] == 3
    assert metrics["detached_plots_pending"] == 0
    assert metrics["recorded_units"] is None  # superseded student estimate, not added twice
    assert metrics["building_footprint_m2"] == 0
    assert metrics["gfa_m2"] == 0
    assert {"floor-area-inputs", "detached-housing-quantities"}.issubset(f["id"] for f in report["findings"])


def test_compiled_detached_recipe_linked_twice_does_not_double_dwellings():
    parcel, building = detached_fixture()
    duplicate = copy.deepcopy(parcel)
    duplicate.id = uuid.uuid4()
    metrics = values(analyze_snapshot(snapshot([parcel, duplicate], [building])))
    assert metrics["compiled_detached_dwellings"] == 3


@pytest.mark.parametrize("stale_recipe", [False, True])
def test_detached_missing_or_stale_recipe_requires_compile_and_labels_recorded_estimate(stale_recipe):
    parcel, building = detached_fixture(compiled=stale_recipe, unit_estimate=6)
    if stale_recipe:
        parcel.geometry = rectangle(width=0.003)
    report = analyze_snapshot(snapshot([parcel], [building]))
    metrics = values(report)
    assert metrics["compiled_detached_dwellings"] is None
    assert metrics["detached_plots_pending"] == 1
    assert metrics["recorded_units"] == 6
    assert metrics["gfa_m2"] == 0
    recorded = next(metric for metric in report["metrics"] if metric["key"] == "recorded_units")
    assert "estimates" in recorded["label"]


def test_detached_recipe_inconsistent_count_is_not_reported_as_compiled_housing():
    parcel, building = detached_fixture()
    building.specifications["legoAssembly"]["fit"]["dwelling_count"] = 999
    metrics = values(analyze_snapshot(snapshot([parcel], [building])))
    assert metrics["compiled_detached_dwellings"] is None
    assert metrics["detached_plots_pending"] == 1


@pytest.mark.parametrize("bad_field", ["legoAssembly", "fit", "instances", "segment_id", "community_3d"])
def test_malformed_detached_metadata_is_reported_as_unknown(bad_field):
    parcel, building = detached_fixture()
    if bad_field == "community_3d":
        parcel.properties[bad_field] = "invalid"
    elif bad_field == "legoAssembly":
        building.specifications[bad_field] = "invalid"
    elif bad_field == "segment_id":
        building.specifications["legoAssembly"]["instances"][0][bad_field] = ["invalid"]
    else:
        building.specifications["legoAssembly"][bad_field] = "invalid"
    metrics = values(analyze_snapshot(snapshot([parcel], [building])))
    assert metrics["compiled_detached_dwellings"] is None
    assert metrics["detached_plots_pending"] == 1


def test_development_parcel_is_not_a_building_footprint_and_zero_parks_are_reported():
    plan = snapshot(
        [
            zone("site_boundary", rectangle(width=0.01, height=0.01)),
            zone("development_area", floors=20),
        ]
    )
    report = analyze_snapshot(plan)
    metrics = values(report)
    assert metrics["development_land_m2"] > 0
    assert metrics["building_footprint_m2"] == 0
    assert metrics["gfa_m2"] == 0
    assert "floor-area-inputs" in {f["id"] for f in report["findings"]}
    assert "open-space" in {f["id"] for f in report["findings"]}


def test_linked_footprint_not_counted_twice_and_unknown_floors_are_not_guessed():
    building = SimpleNamespace(
        id=uuid.uuid4(),
        name="Office",
        footprint=rectangle(width=0.0002),
        floor_count=3,
        height_meters=10,
        specifications={},
    )
    parcel = zone("development_area", floors=20)
    parcel.building_id = building.id
    plan = snapshot([zone("site_boundary", rectangle(width=0.01, height=0.01)), parcel], [building])
    metrics = values(analyze_snapshot(plan))
    assert metrics["gfa_m2"] == pytest.approx(metrics["building_footprint_m2"] * 3, abs=0.02)
    building.floor_count = None
    report = analyze_snapshot(snapshot([parcel], [building]))
    assert values(report)["gfa_m2"] == 0
    assert "floor-area-inputs" in {f["id"] for f in report["findings"]}


def test_park_union_preserves_holes_and_excludes_reference_layers():
    outer = rectangle()
    hole = rectangle(x=0.0002, y=0.0002, width=0.0002, height=0.0002)
    park = Polygon(outer.exterior.coords, [hole.exterior.coords])
    ref = SimpleNamespace(
        id=uuid.uuid4(),
        name="Zoning",
        kind="zoning",
        source_url=None,
        source_filename="zoning.geojson",
        source_crs="EPSG:4326",
        feature_count=1,
        feature_collection={
            "type": "FeatureCollection",
            "features": [{"geometry": mapping(rectangle(width=0.1))}],
        },
    )
    report = analyze_snapshot(snapshot([zone("green_space", park), zone("green_space", park)], references=[ref]))
    single = analyze_snapshot(snapshot([zone("green_space", park)]))
    full = analyze_snapshot(snapshot([zone("green_space", outer)]))
    assert values(report)["park_area_m2"] == values(single)["park_area_m2"]
    assert values(single)["park_area_m2"] < values(full)["park_area_m2"]
    assert values(report)["building_footprint_m2"] == 0


def test_snapshot_staleness_tracks_design_and_reference_data_but_not_visibility():
    building = zone("building", floors=3, visible=True)
    first = snapshot([building])
    building.properties["visible"] = False
    assert digest(first) == digest(snapshot([building]))
    building.properties["floors"] = 4
    assert digest(first) != digest(snapshot([building]))
    assert first["zones"][0]["properties"]["floors"] == 3
    changed = copy.deepcopy(first)
    changed["references"] = [{"data_version": "new"}]
    assert digest(first) != digest(changed)


def test_reference_attributes_are_site_scoped_and_do_not_change_proposal_metrics():
    boundary = zone("site_boundary")
    layer = SimpleNamespace(
        id=uuid.uuid4(),
        name="Zoning",
        kind="zoning",
        source_url="https://city.example/zoning",
        source_filename="zoning.geojson",
        source_crs="EPSG:4326",
        feature_count=2,
        feature_collection={
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "inside",
                    "geometry": mapping(rectangle()),
                    "properties": {"district": "RECORDED-CODE"},
                },
                {
                    "id": "outside",
                    "geometry": mapping(rectangle(x=0.1)),
                    "properties": {"district": "UNRELATED"},
                },
            ],
        },
    )
    plan = snapshot([boundary], references=[layer])
    examples = plan["references"][0]["site_attribute_examples"]
    assert len(examples) == 1 and examples[0]["attributes"]["district"] == "RECORDED-CODE"
    analysis = analyze_snapshot(plan)
    source = next(f for f in analysis["findings"] if f["id"] == "reference-evidence")["sources"][0]
    assert "RECORDED-CODE" in source["excerpt"] and "UNRELATED" not in source["excerpt"]
    assert values(analysis)["proposal_zones"] == 0


def test_findings_locate_outside_geometry_without_claiming_legal_conformance():
    outside = zone("building", rectangle(x=0.0009), floors=4)
    report = analyze_snapshot(snapshot([zone("site_boundary"), outside]))
    finding = next(f for f in report["findings"] if f["id"] == "outside-boundary")
    assert finding["location"]["zone_ids"] == [str(outside.id)]
    assert all(f["kind"] != "conformance" for f in report["findings"])
    assert (
        "No replacement district" in next(f for f in report["findings"] if f["id"] == "implementation")["uncertainty"]
    )


def test_policy_leads_preserve_passage_page_and_document_source():
    records = [
        ChunkRecord(
            "chunk1",
            "local-plan",
            "Local area plan",
            "Walking",
            12,
            12,
            "Pedestrian pathways should connect housing to public spaces.",
            "https://city.example/plan.pdf",
        )
    ]
    sources = select_policy_sources(records, {})
    assert sources[0]["page"] == 12
    assert sources[0]["excerpt"] == records[0].text
    finding = next(f for f in analyze_snapshot(snapshot([]), sources)["findings"] if f["id"] == "city-documents")
    assert "does not establish" in finding["uncertainty"]


def test_export_preserves_authors_reasoning_snapshot_and_staleness_without_executing_markup():
    plan = snapshot([zone("residential", floors=3, unit_count=12)])
    plan["project_name"] = "<script>alert(1)</script>"
    analysis = analyze_snapshot(plan)
    decision = {
        "choice": "decline",
        "rationale": "Our reason <script>attack()</script>",
        "follow_through": "Discuss access.",
        "author_name": "Student A",
        "author_id": "u1",
        "updated_at": "2026-09-04",
    }
    report = {
        "id": "report-id",
        "project_name": plan["project_name"],
        "plan_version": digest(plan),
        "created_at": "2026-09-04",
        "requested_by_name": "Student B",
        "is_stale": True,
        "analysis": analysis,
        "decisions": {analysis["findings"][0]["id"]: decision},
        "response_revision": 1,
    }
    output = report_html(report, plan, [{"finding_id": analysis["findings"][0]["id"], **decision}])
    assert "Student A" in output and "Student B" in output
    assert "The proposal has changed" in output
    assert "<script>alert(1)</script>" not in output
    assert "<script>attack()</script>" not in output
    assert 'id="plan-snapshot"' in output and 'aria-label="Saved proposal plan"' in output
    assert "Our reason &lt;script&gt;" in output


def test_student_cannot_submit_blank_or_automatically_invented_reasoning():
    with pytest.raises(ValidationError):
        StudentDecisionRequest(choice="decline", rationale="  ", expected_revision=0)
    with pytest.raises(ValidationError):
        StudentDecisionRequest(choice="approve", rationale="Yes", expected_revision=0)


def make_row():
    plan = snapshot([zone("building", floors=3)])
    return StudentPlanningReport(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        requested_by=uuid.uuid4(),
        requested_by_name="Student",
        snapshot=plan,
        plan_version=digest(plan),
        analysis=analyze_snapshot(plan),
        decisions={},
        decision_history=[],
        response_revision=0,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_decision_route_persists_decline_with_author_and_rejects_lost_update(
    monkeypatch,
):
    row = make_row()
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = row
    db.execute.return_value = result
    user = SimpleNamespace(id=uuid.uuid4(), full_name="Student Chen", email="chen@example.com")
    permission = AsyncMock()
    monkeypatch.setattr(routes, "check_project_permission", permission)
    monkeypatch.setattr(routes, "_snapshot", AsyncMock(return_value=row.snapshot))
    finding_id = row.analysis["findings"][0]["id"]
    request = StudentDecisionRequest(
        choice="decline",
        rationale="We retain this space for a community garden.",
        expected_revision=0,
    )
    response = await routes.respond_to_finding(row.id, finding_id, request, db, user)
    assert response["decisions"][finding_id]["author_name"] == "Student Chen"
    assert response["response_revision"] == 1
    assert len(row.decision_history) == 1
    assert row.decision_history[0]["choice"] == "decline"
    permission.assert_awaited_with(row.project_id, user, db, required="editor")
    with pytest.raises(HTTPException) as exc:
        await routes.respond_to_finding(row.id, finding_id, request, db, user)
    assert exc.value.status_code == 409
    assert len(row.decision_history) == 1


@pytest.mark.asyncio
async def test_new_report_preserves_old_decisions_and_staleness_is_live(monkeypatch):
    original = make_row()
    original.decisions = {"access": {"rationale": "Original reasoning"}}
    user = SimpleNamespace(id=uuid.uuid4(), full_name="Student", email="s@example.com")
    db = AsyncMock()
    db.add = MagicMock()
    monkeypatch.setattr(routes, "check_project_permission", AsyncMock())
    current = copy.deepcopy(original.snapshot)
    current["zones"][0]["properties"]["floors"] = 9
    monkeypatch.setattr(routes, "_snapshot", AsyncMock(return_value=current))
    monkeypatch.setattr(routes, "_policy_sources", AsyncMock(return_value=[]))
    response = await routes.create_report(original.project_id, routes.StudentReportRequest(), db, user)
    assert response["id"] != str(original.id)
    assert response["decisions"] == {}
    assert original.decisions["access"]["rationale"] == "Original reasoning"
    assert routes._view(original, current)["is_stale"] is True


@pytest.mark.asyncio
async def test_http_routes_require_auth_and_editor_permission(monkeypatch):
    app = FastAPI()
    app.include_router(routes.router, prefix="/api/v1")
    db = AsyncMock()
    app.dependency_overrides[routes.get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/student-reports/project/{uuid.uuid4()}")
        assert response.status_code in {401, 403}
        user = SimpleNamespace(id=uuid.uuid4(), full_name="Viewer", email="v@example.com")
        app.dependency_overrides[routes.require_auth] = lambda: user
        permission = AsyncMock(side_effect=HTTPException(403, "Requires editor permission"))
        monkeypatch.setattr(routes, "check_project_permission", permission)
        response = await client.post(f"/api/v1/student-reports/project/{uuid.uuid4()}", json={})
        assert response.status_code == 403
        assert permission.await_args.kwargs["required"] == "editor"
        db.add.assert_not_called()
