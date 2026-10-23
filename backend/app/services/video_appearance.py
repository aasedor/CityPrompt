"""Photographic guides share the image outbox, credits and private recovery.

One image edit only; no provider retry, video dispatch or schema migration.
The original route bytes and saved scene must still match before video spend.
"""

import hashlib

from fastapi import HTTPException
from app.core.config import get_settings
from app.core.security import check_project_permission
from app.schemas.video_appearance import VideoAppearanceRequest
from app.services.omni_video import decode_guide_image
from app.services.render_attempt_storage import write_evidence
from app.api.v1.render import RenderRequest, _call_openai_image_edit as call_image_edit

GUIDE_CREDIT_COST = 26
PHOTOGRAPHIC_DIRECTION = (
    "Turn this exact 3D scene into a convincing live-action architectural film still. "
    "Use realistic materials, natural human skin and clothing, and physically plausible planting. "
    "Clear blue sky, a few soft white clouds and neutral sunshine. "
    "Keep the camera, every building, street, opening, person and skyline in the same position and scale. "
    "No new buildings or people. No captions. "
)


async def validate_scene(req, db):
    from app.api.v1.video import (
        VideoPilotRequest,
        _locked_project,
        _validate_video_scene_revision,
        _preflight_values,
        _inspect_omni_source,
    )

    if req.source_request is None:
        raise HTTPException(400, "The original route capture is required for guide recovery.")
    source = VideoPilotRequest.model_validate(req.source_request)
    if (
        source.project_id != req.project_id
        or source.provider != "omni"
        or source.control_mode != "preview_video"
        or source.omni_reference_mode != "video_only"
    ):
        raise HTTPException(400, "Photographic guides require an original Omni route recording.")
    guide, _, preview, _, _, _ = _preflight_values(source)
    if (
        preview is None
        or hashlib.sha256(preview.data).hexdigest() != req.source_video_sha256
        or guide.data != decode_guide_image(req.beauty_image_base64).data
    ):
        raise HTTPException(400, "The guide frame and original route recording do not match.")
    await _inspect_omni_source(source, preview)
    await _locked_project(db, req.project_id)
    return await _validate_video_scene_revision(source, db)


async def run_appearance_render(req: VideoAppearanceRequest, user, db, *, attempt):
    from app.api.v1.direct_3d_render import _reserve_direct_render

    settings = get_settings()
    if settings.classroom_release or not settings.direct_3d_images_enabled or not settings.openai_api_key:
        raise HTTPException(503, "Photographic video guides are unavailable.")
    await check_project_permission(req.project_id, user, db, required="editor")
    try:
        source = decode_guide_image(req.beauty_image_base64)
        if source.width > 2048 or source.height > 2048:
            raise ValueError("The guide source must be no larger than 2048 px per edge.")
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    scene_sha = await validate_scene(req, db)
    prompt = PHOTOGRAPHIC_DIRECTION + req.prompt.strip()
    if req.source_request is not None:
        from app.api.v1.video import VideoPilotRequest, _saved_people_prompt
        from app.models.models import Project

        # validate_scene bound this exact source request, not the guide's
        # client-authored prose or optional duplicate scene claims.
        source_request = VideoPilotRequest.model_validate(req.source_request)
        project = await db.get(Project, source_request.project_id)
        prompt = _saved_people_prompt(source_request, project, prompt)
    await write_evidence(
        attempt,
        "source",
        {
            "scene_revision_sha256": scene_sha,
            "source_video_sha256": req.source_video_sha256,
            "source_image_sha256": hashlib.sha256(source.data).hexdigest(),
        },
    )
    await _reserve_direct_render(
        db,
        user,
        token_cost=GUIDE_CREDIT_COST,
        daily_cap=settings.render_global_daily_token_cap,
        prompt=prompt,
        project_id=req.project_id,
        model=req.model,
        attempt=attempt,
    )
    # The outbox reconciler refunds known-unproduced/unknown failures exactly once.
    # Saving provider-result before the final response makes paid bytes recoverable.
    try:
        response = await call_image_edit(
            RenderRequest(
                image_base64=req.beauty_image_base64,
                prompt=prompt,
                model=req.model,
                image_quality="high",
                aspect_ratio="16:9",
                post_process=False,
                project_id=req.project_id,
                guide_image_kind="model_3d",
            ),
            settings,
            req.model,
            include_mask=False,
        )
        if response.status_code != 200:
            billing = (
                "unproduced" if response.status_code in {400, 401, 403, 404, 409, 413, 415, 422, 429} else "unknown"
            )
            await write_evidence(
                attempt, "provider-error", {"billing_status": billing, "status_code": response.status_code}
            )
            raise HTTPException(502, "The photographic guide did not finish. Recover this attempt before trying again.")
        body = response.json()
        pixels = (body.get("data") or [{}])[0].get("b64_json")
        if not pixels:
            raise ValueError("The provider returned no image bytes.")
        image = decode_guide_image(pixels)
        result = {
            "purpose": "video_appearance",
            "attempt_id": str(attempt.id),
            "image_base64": pixels,
            "model": req.model,
            "source_video_sha256": req.source_video_sha256,
            "scene_revision_sha256": scene_sha,
            "output_fingerprint": hashlib.sha256(image.data).hexdigest(),
            "tokens_spent": GUIDE_CREDIT_COST,
            "provider_usage": body.get("usage"),
            "warning": "Appearance guide only. Review against the source; architecture and people remain approximate.",
        }
        await write_evidence(attempt, "provider-result", result)
        return result
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            502, "The photographic guide response could not be verified. This attempt will not retry."
        ) from exc


async def validate_binding(db, user, project_id, attempt_id, *, source_sha256, scene_sha256, images):
    from app.services.render_attempts import authorized_attempt, recover_result

    attempt = await authorized_attempt(db, user, attempt_id)
    if attempt.project_id != project_id or attempt.style != "video-appearance" or attempt.status != "completed":
        raise HTTPException(409, "Recover a completed photographic guide for this project first.")
    result = await recover_result(attempt)
    if (
        not isinstance(result, dict)
        or result.get("source_video_sha256") != source_sha256
        or result.get("scene_revision_sha256") != scene_sha256
        or len(images) != 1
        or result.get("output_fingerprint") != hashlib.sha256(images[0]).hexdigest()
    ):
        raise HTTPException(409, "The scene, route or photographic guide changed. Prepare and review a matching guide.")
