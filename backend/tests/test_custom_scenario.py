"""Custom master-plan scenario — brief expansion, rule hints, API, task reconstruction.

Expansion tests patch the Anthropic client (same pattern as test_planning_agents);
API tests use the mock-DB conftest pattern; the task test uses a fake sync session.
"""

import json
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import app.services.planning_agents.custom_scenario as custom_scenario_module
from app.services.planning_agents.custom_scenario import expand_brief_to_definition
from app.services.planning_agents.schemas import PhilosophyWeights, ScenarioDefinition
from app.services.plan_geometry.community_rules import resolve_rules
from tests.conftest import FakeProject
from tests.test_urban_dna_api import FakeSnapshot, FakeZone, _scalar_result

BRIEF = "A European style development with a large central park and small walkable blocks"


# ---------------------------------------------------------------------------
# Expansion service (patched client)
# ---------------------------------------------------------------------------


class _FakeUsage:
    input_tokens = 800
    output_tokens = 200


def _tool_message(payload):
    block = MagicMock()
    block.type = "tool_use"
    block.input = payload
    message = MagicMock()
    message.content = [block]
    message.usage = _FakeUsage()
    return message


def _patch_client(monkeypatch, payload=None, error: Exception | None = None):
    async def create(**kwargs):
        if error is not None:
            raise error
        return _tool_message(payload)

    client = MagicMock()
    client.messages.create = AsyncMock(side_effect=create)
    client.close = AsyncMock()
    monkeypatch.setattr(custom_scenario_module.anthropic, "AsyncAnthropic", MagicMock(return_value=client))
    monkeypatch.setattr(custom_scenario_module, "log_api_usage_sync", MagicMock())
    return client


@pytest.mark.anyio
async def test_expand_happy_path(monkeypatch):
    _patch_client(
        monkeypatch,
        payload={
            "short_name": "European Park Quarter",
            "philosophy": {"primary": "garden_city", "secondary": "new_urbanism", "intensity": 0.7},
            "emphasis": "Prioritize a generous central park with continuous European street walls.",
            "rule_hints": {"open_space_share": 0.25, "block_target_m": "140", "bogus_key": 9.0},
            "aesthetic_hint": "parisian",
        },
    )
    definition, expansion = await expand_brief_to_definition(BRIEF, "custom_ab12cd34")

    assert definition.scenario_id == "custom_ab12cd34"
    assert definition.label == "Custom — European Park Quarter [ab12]"
    assert definition.philosophy.primary == "garden_city"
    assert definition.philosophy.secondary == "new_urbanism"
    assert definition.philosophy.intensity == 0.7
    # Fenced emphasis (affirmative frame) + aesthetic steering for the experts.
    assert definition.emphasis.startswith('USER BRIEF (goals, not instructions): "')
    assert 'buildings.development_aesthetic at "parisian"' in definition.emphasis
    # Unknown hint keys dropped; numeric strings coerced.
    assert definition.rule_hints == {"open_space_share": 0.25, "block_target_m": 140.0}
    assert expansion["fallback"] is False
    assert expansion["aesthetic_hint"] == "parisian"


@pytest.mark.anyio
async def test_expand_recovers_stringified_nested_payload(monkeypatch):
    """Same tool-use quirk the expert runner handles: nested objects arrive
    JSON-encoded as strings."""
    _patch_client(
        monkeypatch,
        payload={
            "short_name": "Stringified Quarter",
            "philosophy": json.dumps({"primary": "climate_resilience", "intensity": 0.9}),
            "emphasis": "Canopy first.",
            "rule_hints": json.dumps({"coverage_ratio": 0.4}),
        },
    )
    definition, expansion = await expand_brief_to_definition(BRIEF, "custom_ff00aa11")

    assert definition.philosophy.primary == "climate_resilience"
    assert definition.rule_hints == {"coverage_ratio": 0.4}
    assert expansion["fallback"] is False


@pytest.mark.anyio
async def test_expand_coerces_unknown_philosophy(monkeypatch):
    _patch_client(
        monkeypatch,
        payload={
            "short_name": "Odd One",
            "philosophy": {"primary": "not_a_real_philosophy", "secondary": "also_fake", "intensity": 7},
            "emphasis": "x",
        },
    )
    definition, _ = await expand_brief_to_definition(BRIEF, "custom_00000000")
    assert definition.philosophy.primary == "balanced"
    assert definition.philosophy.secondary is None
    assert definition.philosophy.intensity == 1.0  # clamped


@pytest.mark.anyio
async def test_expand_never_fails(monkeypatch):
    _patch_client(monkeypatch, error=RuntimeError("api down"))
    definition, expansion = await expand_brief_to_definition(BRIEF, "custom_deadbeef")

    assert expansion["fallback"] is True
    assert definition.philosophy.primary == "balanced"
    assert definition.philosophy.intensity == 0.5
    assert definition.rule_hints == {}
    # Brief lands verbatim (fenced) so the experts still see the user's goals.
    assert BRIEF in definition.emphasis
    assert definition.label.startswith("Custom — ")
    assert definition.label.endswith("[dead]")


@pytest.mark.anyio
async def test_expand_strips_control_chars_from_label(monkeypatch):
    """Label drives layer identity (`Plan — {label}`) — must be one clean line."""
    _patch_client(
        monkeypatch,
        payload={
            "short_name": "Two\nLine\tName",
            "philosophy": {"primary": "balanced"},
            "emphasis": "x",
        },
    )
    definition, _ = await expand_brief_to_definition(BRIEF, "custom_12345678")
    assert definition.label == "Custom — Two Line Name [1234]"


# ---------------------------------------------------------------------------
# resolve_rules rule-hint clamps
# ---------------------------------------------------------------------------


def test_resolve_rules_applies_and_clamps_hints():
    profile, notes = resolve_rules(
        "custom_ab12cd34",
        {},
        rule_hints={"open_space_share": 0.5, "coverage_ratio": 0.2, "block_target_m": 140.0},
    )
    # open clamped to the evaluator's own revision ceiling; coverage floored.
    assert profile.open_space_share == 0.30
    assert profile.coverage_ratio == 0.30
    assert profile.block_target_m == 140.0
    hint_notes = [n for n in notes if n["code"] == "RULE_HINT_APPLIED"]
    assert len(hint_notes) == 3
    assert any("clamped" in n["message"] for n in hint_notes)


def test_resolve_rules_presets_unaffected_without_hints():
    profile, notes = resolve_rules("as_of_right", {})
    assert profile.open_space_share == 0.10
    assert profile.coverage_ratio == 0.50
    assert not [n for n in notes if n["code"] == "RULE_HINT_APPLIED"]


def test_resolve_rules_ignores_non_numeric_hints():
    profile, notes = resolve_rules(
        "custom_x",
        {},
        rule_hints={"open_space_share": "lots", "coverage_ratio": True},
    )
    assert profile.open_space_share == 0.10  # fallback defaults
    assert profile.coverage_ratio == 0.50
    assert not [n for n in notes if n["code"] == "RULE_HINT_APPLIED"]


# ---------------------------------------------------------------------------
# Task: definition reconstruction + payload carry-forward
# ---------------------------------------------------------------------------


class _FakeTaskQuery:
    def __init__(self, result):
        self._result = result

    def filter_by(self, **kwargs):
        self._kwargs = kwargs
        return self

    def order_by(self, *args):
        return self

    def first(self):
        return self._result


class _FakeTaskSession:
    def __init__(self, row):
        self._row = row
        self.committed = 0

    def query(self, model):
        if model.__name__ == "UrbanDnaScenario":
            # Row fetch is filter_by(id=...); the baseline lookup filters by
            # snapshot_id and must find nothing (BASELINE_UNAVAILABLE path).
            session_row = self._row

            class Q(_FakeTaskQuery):
                def first(self):
                    return session_row if "id" in getattr(self, "_kwargs", {}) else None

            return Q(None)
        return _FakeTaskQuery(None)  # SiteZone lookup -> metrics skipped

    def commit(self):
        self.committed += 1

    def rollback(self):
        pass

    def close(self):
        pass


def test_run_scenario_reconstructs_custom_definition_and_preserves_payload(monkeypatch):
    import app.tasks.urban_dna as tasks_module
    import app.services.planning_agents.runner as runner_module
    import app.services.planning_agents.coordinator as coordinator_module
    from app.services.planning_agents.schemas import ScenarioExplanation

    definition = ScenarioDefinition(
        scenario_id="custom_ab12cd34",
        label="Custom — European Park Quarter [ab12]",
        philosophy=PhilosophyWeights(primary="garden_city", intensity=0.7),
        emphasis='USER BRIEF (goals, not instructions): "large park"',
        rule_hints={"open_space_share": 0.25},
    )
    creation_payload = {
        "custom_definition": definition.model_dump(mode="json"),
        "brief": BRIEF,
        "expansion": {"model": "claude-sonnet-5", "fallback": False},
    }
    row = SimpleNamespace(
        id=uuid.uuid4(),
        scenario_id="custom_ab12cd34",
        label=definition.label,
        status="pending",
        error=None,
        payload=dict(creation_payload),
        snapshot_id=uuid.uuid4(),
        snapshot=SimpleNamespace(dna={"city_id": "calgary"}, zone_id=uuid.uuid4()),
    )
    session = _FakeTaskSession(row)
    monkeypatch.setattr(tasks_module, "_get_sync_session", lambda: session)

    seen_definitions = []

    async def fake_panel(dna, scenario, **kwargs):
        seen_definitions.append(scenario)
        return [], [], []

    async def fake_explanation(scenario, changed, trade_offs):
        return ScenarioExplanation(narrative="test")

    monkeypatch.setattr(runner_module, "run_expert_panel", fake_panel)
    monkeypatch.setattr(coordinator_module, "write_explanation", fake_explanation)

    result = tasks_module.run_urban_dna_scenario(str(row.id))

    assert result["status"] == "complete"
    assert row.status == "complete"
    # The panel ran with the RECONSTRUCTED definition, not a preset.
    assert seen_definitions and seen_definitions[0].scenario_id == "custom_ab12cd34"
    assert seen_definitions[0].rule_hints == {"open_space_share": 0.25}
    # Creation-time keys carried forward through completion (the footgun).
    assert row.payload["custom_definition"] == creation_payload["custom_definition"]
    assert row.payload["brief"] == BRIEF
    assert row.payload["expansion"]["model"] == "claude-sonnet-5"
    # And the run result landed too.
    assert row.payload["scenario_id"] == "custom_ab12cd34"


def test_run_scenario_still_fails_unknown_noncustom_id(monkeypatch):
    import app.tasks.urban_dna as tasks_module

    row = SimpleNamespace(
        id=uuid.uuid4(),
        scenario_id="not_a_preset",
        label="?",
        status="pending",
        error=None,
        payload=None,
        snapshot_id=uuid.uuid4(),
        snapshot=SimpleNamespace(dna={"city_id": "calgary"}, zone_id=uuid.uuid4()),
    )
    session = _FakeTaskSession(row)
    monkeypatch.setattr(tasks_module, "_get_sync_session", lambda: session)

    result = tasks_module.run_urban_dna_scenario(str(row.id))
    assert result["status"] == "failed"
    assert "unknown scenario preset" in row.error


# ---------------------------------------------------------------------------
# API: creation with a brief, spend cap, delete
# ---------------------------------------------------------------------------


def _count_result(value):
    result = MagicMock()
    result.scalar.return_value = value
    return result


def _zones_result(zones):
    result = MagicMock()
    result.scalars.return_value.all.return_value = zones
    return result


def _fake_definition(scenario_id: str) -> ScenarioDefinition:
    return ScenarioDefinition(
        scenario_id=scenario_id,
        label=f"Custom — Test [{scenario_id.rsplit('_', 1)[-1][:4]}]",
        philosophy=PhilosophyWeights(primary="balanced", intensity=0.5),
        emphasis='USER BRIEF (goals, not instructions): "test"',
        rule_hints={"open_space_share": 0.25},
    )


@pytest.mark.anyio
async def test_create_scenarios_brief_only_queues_single_custom_run(
    client, mock_db, test_user, auth_headers, monkeypatch
):
    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    snapshot = FakeSnapshot(zone_id=zone.id, project_id=zone.project_id)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # auth
            _scalar_result(zone),  # zone
            _scalar_result(project),  # permission
            _scalar_result(snapshot),  # latest snapshot
            _count_result(0),  # spend guard: no custom rows in flight
            _count_result(0),  # baseline not in flight -> no blind 75s wait
        ]
    )

    async def fake_expand(brief, scenario_id):
        return _fake_definition(scenario_id), {"model": "m", "fallback": False}

    import app.services.planning_agents.custom_scenario as cs_module

    monkeypatch.setattr(cs_module, "expand_brief_to_definition", fake_expand)

    # server_default timestamps only exist after a real flush — stamp on add
    # so the response model can serialize the fresh row.
    def add_with_timestamps(obj):
        obj.created_at = datetime.now(timezone.utc)
        obj.updated_at = datetime.now(timezone.utc)

    mock_db.add = MagicMock(side_effect=add_with_timestamps)

    import app.tasks.urban_dna as tasks_module

    apply_mock = MagicMock()
    monkeypatch.setattr(tasks_module.run_urban_dna_scenario, "apply_async", apply_mock)

    response = await client.post(
        f"/api/v1/urban-dna/zones/{zone.id}/scenarios",
        headers=auth_headers,
        json={"custom_brief": BRIEF},  # NO scenario_ids -> presets must NOT run
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["scenarios"]) == 1
    row = data["scenarios"][0]
    assert row["scenario_id"].startswith("custom_")
    assert row["label"].startswith("Custom — Test [")
    assert row["payload"]["brief"] == BRIEF
    assert row["payload"]["custom_definition"]["rule_hints"] == {"open_space_share": 0.25}
    # One dispatch, and no baseline in flight -> countdown 0 (no blind 75 s).
    apply_mock.assert_called_once()
    assert apply_mock.call_args.kwargs["countdown"] == 0


@pytest.mark.anyio
async def test_create_scenarios_spend_cap_rejects(client, mock_db, test_user, auth_headers):
    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    snapshot = FakeSnapshot(zone_id=zone.id, project_id=zone.project_id)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(zone),
            _scalar_result(project),
            _scalar_result(snapshot),
            _count_result(4),  # >3 custom rows pending/running
        ]
    )
    response = await client.post(
        f"/api/v1/urban-dna/zones/{zone.id}/scenarios",
        headers=auth_headers,
        json={"custom_brief": BRIEF},
    )
    assert response.status_code == 429


@pytest.mark.anyio
async def test_create_scenarios_rejects_empty_request(client, mock_db, test_user, auth_headers):
    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    snapshot = FakeSnapshot(zone_id=zone.id, project_id=zone.project_id)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(zone),
            _scalar_result(project),
            _scalar_result(snapshot),
        ]
    )
    response = await client.post(
        f"/api/v1/urban-dna/zones/{zone.id}/scenarios",
        headers=auth_headers,
        json={"scenario_ids": []},  # explicit empty, no brief
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_scenarios_rejects_whitespace_brief(client, mock_db, test_user, auth_headers):
    """A whitespace-only brief must 422, not silently queue all three presets."""
    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    snapshot = FakeSnapshot(zone_id=zone.id, project_id=zone.project_id)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(zone),
            _scalar_result(project),
            _scalar_result(snapshot),
        ]
    )
    response = await client.post(
        f"/api/v1/urban-dna/zones/{zone.id}/scenarios",
        headers=auth_headers,
        json={"custom_brief": "   "},
    )
    assert response.status_code == 422
    mock_db.add.assert_not_called()


class _FakeScenarioRow:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.snapshot_id = kwargs.get("snapshot_id", uuid.uuid4())
        self.scenario_id = kwargs.get("scenario_id", "custom_ab12cd34")
        self.label = kwargs.get("label", "Custom — Test [ab12]")
        self.status = kwargs.get("status", "complete")
        self.payload = kwargs.get("payload", None)
        self.error = None
        self.created_at = FakeSnapshot().created_at
        self.updated_at = FakeSnapshot().updated_at


@pytest.mark.anyio
async def test_delete_scenario_rejects_presets(client, mock_db, test_user, auth_headers):
    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    row = _FakeScenarioRow(scenario_id="as_of_right", label="As-of-Right")
    snapshot = FakeSnapshot(zone_id=zone.id, project_id=zone.project_id, id=row.snapshot_id)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(row),
            _scalar_result(snapshot),
            _scalar_result(zone),
            _scalar_result(project),
        ]
    )
    response = await client.delete(f"/api/v1/urban-dna/scenarios/{row.id}", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_delete_scenario_removes_row_and_plan_zones(client, mock_db, test_user, auth_headers, monkeypatch):
    zone = FakeZone()
    zone.properties = {
        "community_3d_landscape": {
            "schema_version": 1,
            "state": "compiled",
            "source_hash": "compiled-before-delete",
        },
    }
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    row = _FakeScenarioRow()
    snapshot = FakeSnapshot(zone_id=zone.id, project_id=zone.project_id, id=row.snapshot_id)
    plan_zone_a = SimpleNamespace(id=uuid.uuid4())
    plan_zone_b = SimpleNamespace(id=uuid.uuid4())
    monkeypatch.setattr("app.api.v1.urban_dna.flag_modified", lambda *_args: None)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(row),
            _scalar_result(snapshot),
            _scalar_result(zone),
            _scalar_result(project),
            _scalar_result(project.id),  # project row lock before source mutation
            _zones_result([plan_zone_a, plan_zone_b]),
        ]
    )
    response = await client.delete(f"/api/v1/urban-dna/scenarios/{row.id}", headers=auth_headers)
    assert response.status_code == 204
    deleted = [call.args[0] for call in mock_db.delete.call_args_list]
    assert plan_zone_a in deleted and plan_zone_b in deleted and row in deleted
    residual = zone.properties["community_3d_landscape"]
    assert residual["state"] == "stale"
    assert residual["source_hash"] == "compiled-before-delete"
    assert residual["changed_zone_id"] == str(plan_zone_a.id)
    assert "Scenario plan zones deleted" in residual["stale_reason"]
    mock_db.refresh.assert_awaited_once_with(zone)
    mock_db.commit.assert_awaited()


@pytest.mark.anyio
async def test_delete_scenario_409_while_plan_is_drawing(client, mock_db, test_user, auth_headers):
    from datetime import datetime, timezone as tz

    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    row = _FakeScenarioRow(
        payload={
            "plan": {"status": "drawing", "queued_at": datetime.now(tz.utc).isoformat()},
        }
    )
    snapshot = FakeSnapshot(zone_id=zone.id, project_id=zone.project_id, id=row.snapshot_id)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(row),
            _scalar_result(snapshot),
            _scalar_result(zone),
            _scalar_result(project),
        ]
    )
    response = await client.delete(f"/api/v1/urban-dna/scenarios/{row.id}", headers=auth_headers)
    assert response.status_code == 409
    mock_db.delete.assert_not_called()


@pytest.mark.anyio
async def test_delete_scenario_404_for_non_member(client, mock_db, test_user, auth_headers):
    zone = FakeZone()
    project = FakeProject()  # owned by someone else
    row = _FakeScenarioRow()
    snapshot = FakeSnapshot(zone_id=zone.id, project_id=zone.project_id, id=row.snapshot_id)
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),
            _scalar_result(row),
            _scalar_result(snapshot),
            _scalar_result(zone),
            _scalar_result(project),
            _scalar_result(None),  # no share -> 403 -> masked as 404
        ]
    )
    response = await client.delete(f"/api/v1/urban-dna/scenarios/{row.id}", headers=auth_headers)
    assert response.status_code == 404
