"""No-provider tests for saved actor directions shared by stills and video."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

import pytest
from fastapi import HTTPException

from app.services.people_actions import (
    PEOPLE_ACTIONS,
    append_people_action_direction,
    people_action_direction,
)


INCLUSIVE_POSES = {
    "white-cane": ("standing", 1, "white cane"),
    "guide-dog": ("standing", 1, "guide dog"),
    "manual-wheelchair": ("sitting", 1, "manual wheelchair"),
    "power-wheelchair": ("sitting", 1, "powered wheelchair"),
    "older-woman": ("standing", 1, "older woman"),
    "older-man-rollator": ("standing", 1, "rollator"),
    "family-parent-child": ("standing", 2, "child"),
    "family-stroller": ("standing", 2, "infant"),
}


@pytest.fixture
def registered_inclusive_people(monkeypatch):
    """Exercise the contract before the measured assets enter the registry."""
    from app.services import people_actions

    variants = {f"people-inclusive-{slug}" for slug in INCLUSIVE_POSES}
    monkeypatch.setattr(people_actions, "_PEOPLE_MODELS", people_actions._PEOPLE_MODELS | variants)
    return variants


@pytest.mark.parametrize("slug,pose", INCLUSIVE_POSES.items())
def test_fixed_people_default_to_their_captured_pose_and_preserve_representation(
    registered_inclusive_people, slug, pose
):
    action, count, description = pose
    direction = people_action_direction({"props": [{"variant": f"people-inclusive-{slug}"}]})
    assert f"1 {action}" in direction
    assert f"People represented by saved models: {count}" in direction
    assert description in direction.lower()
    assert "fixed pose" in direction.lower() and "not animated" in direction.lower()
    assert "offscreen" in direction and "Do not add" in direction
    if "wheelchair" in slug:
        assert "walking" not in direction and "heel-to-toe" not in direction
        assert "seated" in direction
    if slug == "guide-dog":
        assert "harness" in direction


def test_group_counts_are_people_and_guide_dog_is_not_a_second_person(registered_inclusive_people):
    direction = people_action_direction(
        {
            "props": [
                {"variant": "people-inclusive-family-parent-child"},
                {"variant": "people-inclusive-family-stroller"},
                {"variant": "people-inclusive-guide-dog"},
                {"variant": "people-inclusive-manual-wheelchair"},
            ]
        }
    )
    assert "3 standing; 1 sitting" in direction
    assert "People represented by saved models: 6" in direction
    assert "group arrangement" in direction and "mobility aids" in direction
    assert "adult and child" in direction and "adult and infant" in direction


@pytest.mark.parametrize("slug,pose", INCLUSIVE_POSES.items())
def test_render_directions_reject_forged_unsupported_fixed_pose_actions(registered_inclusive_people, slug, pose):
    supported, _, _ = pose
    for action in PEOPLE_ACTIONS:
        if action == supported:
            continue
        with pytest.raises(ValueError, match="Unsupported people action"):
            people_action_direction(
                {
                    "props": [
                        {
                            "variant": f"people-inclusive-{slug}",
                            "people_action": action,
                        }
                    ]
                }
            )


def details(*actions):
    return {
        "revision": 3,
        "props": [
            {
                "id": f"person-{index}",
                "variant": "people-pilot-commuter",
                **({"people_action": action} if action is not None else {}),
            }
            for index, action in enumerate(actions)
        ],
    }


def test_all_actions_are_natural_and_legacy_people_stand():
    direction = people_action_direction(details(*PEOPLE_ACTIONS, None))
    for phrase in (
        "standing",
        "walking",
        "running",
        "sitting",
        "talking",
        "lying down",
        "waving",
        "using a phone",
        "reading",
        "waiting",
        "looking around",
        "pointing",
        "stretching",
        "dancing",
        "cheering",
    ):
        assert phrase in direction
    assert "2 standing" in direction
    assert "visible" in direction and "offscreen" in direction
    assert "do not add" in direction.lower()
    assert "buildings" in direction and "furniture" in direction
    assert "lying_down" not in direction


def test_furniture_and_unknown_models_do_not_become_people():
    assert (
        people_action_direction(
            {
                "props": [
                    {"variant": "dual-stream-bin"},
                    {"variant": "people-forged", "people_action": "walking"},
                ]
            }
        )
        == ""
    )
    assert people_action_direction(None) == ""
    for action in ("flying", ""):
        with pytest.raises(ValueError, match="people action"):
            people_action_direction(details(action))


def test_walking_direction_improves_biomechanics_without_changing_routes_or_other_actions():
    direction = people_action_direction(details("walking", "sitting"))
    assert "heel-to-toe" in direction and "weight transfer" in direction
    assert "retain their captured route and speed" in direction
    assert "low-polygon joint stiffness" in direction
    assert "heel-to-toe" not in people_action_direction(details("sitting", "standing"))


def test_authoritative_direction_fits_after_long_custom_text_and_is_idempotent():
    direction = people_action_direction(details("reading", "walking"))
    prompt = append_people_action_direction("x" * 32000, direction)
    assert prompt.endswith(direction) and len(prompt) <= 32000
    assert append_people_action_direction(prompt, direction) == prompt
    assert append_people_action_direction("Scene", "") == "Scene"
    assert len(people_action_direction(details(*(["walking"] * 256)))) < 2000
    assert len(append_people_action_direction("x" * 32000 + direction, direction)) <= 32000


def test_image_inventory_conditions_actions_on_visible_saved_details():
    from app.services.direct_3d_render import _visible_people_action_direction

    inventory = [{"instance_id": "project-details", "people_action_direction": "saved reading"}]
    assert _visible_people_action_direction(inventory, {"project-details"}) == "saved reading"
    assert _visible_people_action_direction(inventory, {"other"}) == ""


def test_image_saved_actions_are_derived_from_current_revision_bound_details():
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones
    from app.schemas.direct_3d_render import Direct3DInstanceDescriptor
    from tests.test_direct_3d_render import _request

    req = _request().model_copy(
        update={
            "details_revision": 3,
            "community_3d_claims": [],
            "instance_id_manifest": {
                "#010001": Direct3DInstanceDescriptor(instance_id="project-details", semantic_class="landscape")
            },
        }
    )
    inventory = _validate_direct_3d_project_zones(req, [], {}, project_details=details("sitting"))
    assert inventory[0]["people_action_direction"] == people_action_direction(details("sitting"))
    with pytest.raises(HTTPException) as error:
        _validate_direct_3d_project_zones(req, [], {}, project_details={**details("walking"), "revision": 4})
    assert error.value.status_code == 409


def test_video_uses_saved_actions_even_with_only_custom_prompt():
    from app.api.v1.video import _saved_people_prompt, _preflight_values
    from tests.test_people_video import _preview_request

    req = _preview_request(details_revision=3, custom_prompt="Warm sunset.", use_custom_prompt_only=True)
    project = SimpleNamespace(metadata_={"scene_details": details("reading")})
    *_, prompt, _ = _preflight_values(req)
    assert prompt == "Warm sunset."
    result = _saved_people_prompt(req, project, prompt)
    assert result.startswith("Warm sunset.") and "reading" in result
    assert "offscreen" in result
    assert (
        _saved_people_prompt(req.model_copy(update={"details_revision": None}), SimpleNamespace(metadata_={}), prompt)
        == prompt
    )
    with pytest.raises(HTTPException) as error:
        _saved_people_prompt(req.model_copy(update={"details_revision": None}), project, prompt)
    assert error.value.status_code == 409
    with pytest.raises(HTTPException) as error:
        _saved_people_prompt(req.model_copy(update={"details_revision": 2}), project, prompt)
    assert error.value.status_code == 409


@pytest.mark.asyncio
async def test_free_video_preflight_uses_current_saved_actions_without_provider_contact(monkeypatch):
    from app.api.v1 import video
    from tests.test_people_video import _preview_request

    req = _preview_request(details_revision=3, custom_prompt="Warm sunset.", use_custom_prompt_only=True)
    project = SimpleNamespace(metadata_={"scene_details": details("reading")})
    db = AsyncMock()
    db.get.return_value = project
    user = SimpleNamespace(id=uuid.uuid4(), role="admin", render_credits=1000)
    settings = video.get_settings().model_copy(update={"gemini_api_key": "mock-only"})
    monkeypatch.setattr(video, "get_settings", lambda: settings)
    monkeypatch.setattr(video, "check_project_permission", AsyncMock(return_value="editor"))
    monkeypatch.setattr(video, "_inspect_omni_source", AsyncMock())
    monkeypatch.setattr(video, "_validate_video_scene_revision", AsyncMock(return_value="a" * 64))
    provider = AsyncMock(side_effect=AssertionError("Preflight must not submit"))
    monkeypatch.setattr(video, "request_omni_video_once", provider)
    result = await video.preflight_video(req, user, db)
    assert result.ready and result.prompt_preview.startswith("Warm sunset.")
    assert "reading" in result.prompt_preview and "offscreen" in result.prompt_preview
    provider.assert_not_awaited()
    db.commit.assert_not_awaited()
    assert project.metadata_ == {"scene_details": details("reading")}


@pytest.mark.asyncio
async def test_photographic_guide_uses_validated_source_actions_before_mock_image_call(monkeypatch):
    from app.api.v1 import direct_3d_render as direct
    from app.schemas.video_appearance import VideoAppearanceRequest
    from app.services import video_appearance as appearance
    from tests.test_people_video import _preview_request

    source_req = _preview_request(details_revision=3)
    req = VideoAppearanceRequest(
        project_id=source_req.project_id,
        beauty_image_base64=source_req.guide_frame_base64,
        source_video_sha256="a" * 64,
        source_request=source_req.model_dump(mode="json"),
        details_revision=3,
        prompt="Warm sunset.",
    )
    settings = appearance.get_settings().model_copy(
        update={"classroom_release": False, "direct_3d_images_enabled": True, "openai_api_key": "mock-only"}
    )
    monkeypatch.setattr(appearance, "get_settings", lambda: settings)
    monkeypatch.setattr(appearance, "validate_scene", AsyncMock(return_value="b" * 64))
    monkeypatch.setattr(appearance, "check_project_permission", AsyncMock())
    monkeypatch.setattr(appearance, "write_evidence", AsyncMock())
    reserve = AsyncMock()
    monkeypatch.setattr(direct, "_reserve_direct_render", reserve)
    response = SimpleNamespace(
        status_code=200, json=lambda: {"data": [{"b64_json": source_req.guide_frame_base64.split(",")[-1]}]}
    )
    provider = AsyncMock(return_value=response)
    monkeypatch.setattr(appearance, "call_image_edit", provider)
    db = AsyncMock()
    db.get.return_value = SimpleNamespace(metadata_={"scene_details": details("reading")})
    await appearance.run_appearance_render(req, SimpleNamespace(), db, attempt=SimpleNamespace(id=uuid.uuid4()))
    prompt = provider.await_args.args[0].prompt
    assert "Warm sunset." in prompt and "reading" in prompt and "offscreen" in prompt
    assert reserve.await_args.kwargs["prompt"] == prompt
    db.get.return_value = SimpleNamespace(metadata_={"scene_details": {**details("walking"), "revision": 4}})
    with pytest.raises(HTTPException) as error:
        await appearance.run_appearance_render(req, SimpleNamespace(), db, attempt=SimpleNamespace(id=uuid.uuid4()))
    assert error.value.status_code == 409
    reserve.assert_awaited_once()
    provider.assert_awaited_once()
    with pytest.raises(HTTPException) as error:
        missing_revision_source = source_req.model_copy(update={"details_revision": None})
        await appearance.run_appearance_render(
            req.model_copy(
                update={"details_revision": None, "source_request": missing_revision_source.model_dump(mode="json")}
            ),
            SimpleNamespace(),
            db,
            attempt=SimpleNamespace(id=uuid.uuid4()),
        )
    assert error.value.status_code == 409
    reserve.assert_awaited_once()
    provider.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("visible", [True, False])
@pytest.mark.parametrize("long_prompt", [False, True])
async def test_image_provider_receives_saved_actions_only_for_visible_details(monkeypatch, visible, long_prompt):
    from app.schemas.direct_3d_render import Direct3DRenderRequest
    from app.services import direct_3d_render as service
    from app.services.render_fidelity import RENDER_PRESERVATION_LOCK
    from tests.test_direct_3d_presentation_first import _scene_request
    from tests.test_direct_3d_render import _RecordingClient, _FakeResponse, _png_b64

    payload = _scene_request(presentation_mode="scene").model_dump()
    payload["add_people"] = False
    if long_prompt:
        payload["prompt"] = "Warm light. " * 1600
    # Use a real capture pixel region, or an unrepresented manifest color.
    payload["object_id_manifest"]["#00FF00"] = "landscape"
    payload["instance_id_manifest"]["#010002"]["semantic_class"] = "landscape"
    if visible:
        payload["instance_id_manifest"]["#010002"].update(instance_id="project-details", zone_id=None)
    else:
        payload["instance_id_manifest"]["#020002"] = {"instance_id": "project-details", "semantic_class": "landscape"}
    req = Direct3DRenderRequest(**payload)
    capture = service.prepare_direct_3d_capture(req)
    _RecordingClient.calls = []
    _RecordingClient.response = _FakeResponse(200, {"data": [{"b64_json": _png_b64(capture.normalized_beauty)}]})
    monkeypatch.setattr(service.httpx, "AsyncClient", _RecordingClient)
    direction = people_action_direction(details("reading"))
    await service.Direct3DRenderService("mock-only")._call_openai(
        req,
        capture,
        server_inventory=[
            {"instance_id": "project-details", "semantic_class": "landscape", "people_action_direction": direction}
        ],
    )
    prompt = _RecordingClient.calls[0]["data"]["prompt"]
    assert ("SAVED PEOPLE ACTIONS:" in prompt) is visible
    assert len(prompt) <= 32000
    if visible:
        assert direction in prompt
    assert "Do not add people" in prompt
    assert "Preserve any people or vehicles already captured" in prompt
    assert prompt.endswith(RENDER_PRESERVATION_LOCK)
