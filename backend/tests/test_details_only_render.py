from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones
from app.services.scene_revision import compiled_scene_revision_sha256
from app.schemas.direct_3d_render import Direct3DInstanceDescriptor
from app.schemas.direct_3d_render import Direct3DRenderRequest
from pydantic import ValidationError

DETAILS = {"revision": 3, "benches": [], "props": [{"id": "one", "variant": "rrfb"}]}

def test_request_schema_accepts_details_without_zone_claims_but_not_empty_scenes():
    payload = {"project_id": "00000000-0000-0000-0000-000000000001", "community_3d_claims": [],
               "beauty_image_base64": "a" * 32, "proposal_mask_base64": "a" * 32, "prompt": "Preserve the crossing"}
    assert Direct3DRenderRequest(**payload, details_revision=3).details_revision == 3
    with pytest.raises(ValidationError):
        Direct3DRenderRequest(**payload)
def request(revision=3):
    return SimpleNamespace(details_revision=revision, community_3d_claims=[], residual_landscape_claim=None, instance_id_manifest={})

def test_details_only_requires_current_saved_content():
    assert _validate_direct_3d_project_zones(request(), [], {}, bind_capture_instances=False, project_details=DETAILS) == []
    for details in [None, {**DETAILS, "revision": 4}, {"revision": 3, "benches": []}]:
        with pytest.raises(HTTPException) as exc:
            _validate_direct_3d_project_zones(request(), [], {}, bind_capture_instances=False, project_details=details)
        assert exc.value.status_code == 409
        assert exc.value.detail["billed"] is False

def test_empty_scene_stays_rejected():
    with pytest.raises(HTTPException):
        _validate_direct_3d_project_zones(request(None), [], {}, bind_capture_instances=False)

def test_details_revision_changes_output_identity():
    assert compiled_scene_revision_sha256([], None, 3) != compiled_scene_revision_sha256([], None, 4)

def test_image_capture_binds_details_to_saved_project():
    req = request()
    req.instance_id_manifest = {"#010203": Direct3DInstanceDescriptor(instance_id="project-details", semantic_class="landscape")}
    inventory = _validate_direct_3d_project_zones(req, [], {}, project_details=DETAILS)
    assert inventory[0]["instance_id"] == "project-details"
    assert inventory[0]["zone_id"] is None

def test_details_only_image_needs_visible_authored_details():
    with pytest.raises(HTTPException) as exc:
        _validate_direct_3d_project_zones(request(), [], {}, project_details=DETAILS)
    assert exc.value.detail["billed"] is False

@pytest.mark.parametrize("patch", [{"semantic_class": "building"}, {"zone_id": "00000000-0000-0000-0000-000000000001"}])
def test_details_cannot_impersonate_buildings_or_zone_ownership(patch):
    req = request()
    req.instance_id_manifest = {"#010203": Direct3DInstanceDescriptor(**{"instance_id": "project-details", "semantic_class": "landscape", **patch})}
    with pytest.raises(HTTPException):
        _validate_direct_3d_project_zones(req, [], {}, project_details=DETAILS)
