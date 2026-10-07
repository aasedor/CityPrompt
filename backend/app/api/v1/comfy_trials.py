"""Local saved-image trials with durable admission and recoverable GPU jobs."""

import asyncio
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
import httpx
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import User
from app.services import comfy_trials as comfy
from app.api.v1.render_animation import _source_render, _load_source
from app.api.v1.video import _locked_project, _now, _public_attempt
from app.api.v1.render import SaveRenderRequest, persist_render_to_gallery

router = APIRouter()
JOBS_KEY = "local_comfy_trials"
TERMINAL = {"complete", "failed"}


class TrialRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: uuid.UUID
    source_render_id: uuid.UUID
    request_id: uuid.UUID
    preset: Literal["flux-klein", "qwen-image", "wan-video"]
    prompt: str = Field(min_length=1, max_length=1500)


def configured(settings):
    if settings.is_production or not settings.comfy_trials_enabled:
        raise HTTPException(503, "Local model trials are disabled on this server.")


def public(entry):
    return {
        k: entry.get(k)
        for k in (
            "id",
            "request_id",
            "source_render_id",
            "preset",
            "kind",
            "status",
            "prompt",
            "generation_settings",
            "created_at",
            "error",
            "result",
        )
    }


def jobs(project):
    return [dict(item) for item in (project.metadata_ or {}).get(JOBS_KEY, [])]


def store(project, entries):
    project.metadata_ = {**(project.metadata_ or {}), JOBS_KEY: entries}


async def update_job(db, project_id, job_id, **changes):
    project = await _locked_project(db, project_id)
    entries = jobs(project)
    entry = next((item for item in entries if item["id"] == job_id), None)
    if not entry:
        raise HTTPException(404, "Local trial not found.")
    entry.update(changes)
    store(project, entries)
    await db.commit()
    return entry


@router.get("/presets")
async def presets(user: User = Depends(require_auth)):
    return {"presets": await comfy.available_presets(get_settings()), "credit_cost": 0}


@router.get("/projects/{project_id}/jobs")
async def list_jobs(
    project_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    await check_project_permission(project_id, user, db, required="viewer")
    project = await _locked_project(db, project_id)
    result = [public(item) for item in jobs(project)]
    await db.commit()
    return {"jobs": result}


@router.post("/jobs", status_code=202)
async def generate(
    req: TrialRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    configured(settings)
    await check_project_permission(req.project_id, user, db, required="editor")
    fingerprint = hashlib.sha256(
        req.model_dump_json(exclude={"request_id"}).encode()
    ).hexdigest()
    project = await _locked_project(db, req.project_id)
    previous = next(
        (j for j in jobs(project) if j["request_id"] == str(req.request_id)), None
    )
    if previous:
        if previous["fingerprint"] != fingerprint:
            raise HTTPException(
                409, "This request ID already belongs to a different local trial."
            )
        await db.commit()
        return public(previous)
    preset = comfy.PRESETS[req.preset]
    _, key = _source_render(
        project, req.source_render_id, require_finished=preset.kind == "video"
    )
    await db.commit()
    capabilities = await comfy.available_presets(settings)
    capability = next(item for item in capabilities if item["id"] == preset.id)
    if not capability["available"]:
        raise HTTPException(503, capability["message"])
    source = await _load_source(key)
    data, w, h = await asyncio.to_thread(comfy.prepare_source, source.data, preset)
    project = await _locked_project(db, req.project_id)
    entries = jobs(project)
    previous = next(
        (j for j in entries if j["request_id"] == str(req.request_id)), None
    )
    if previous:
        if previous["fingerprint"] != fingerprint:
            raise HTTPException(
                409, "This request ID already belongs to a different local trial."
            )
        await db.commit()
        return public(previous)
    _source_render(
        project, req.source_render_id, require_finished=preset.kind == "video"
    )
    if any(j["status"] not in TERMINAL for j in entries):
        raise HTTPException(
            409, "Finish or resolve the existing local trial in this project first."
        )
    job_id = str(uuid.uuid4())
    seed = secrets.randbits(48)
    entry = {
        "id": job_id,
        "request_id": str(req.request_id),
        "fingerprint": fingerprint,
        "requested_by": str(user.id),
        "project_id": str(req.project_id),
        "source_render_id": str(req.source_render_id),
        "source_sha256": hashlib.sha256(source.data).hexdigest(),
        "preset": preset.id,
        "kind": preset.kind,
        "status": "submitting",
        "prompt": req.prompt,
        "created_at": _now(),
        "interaction_id": job_id,
        "generation_settings": {
            "workflow_version": 1,
            "width": w,
            "height": h,
            "steps": preset.steps,
            "seed": seed,
            "frames": 49 if preset.kind == "video" else None,
            "fps": 24 if preset.kind == "video" else None,
            "diffusion_model": preset.diffusion,
            "text_encoder": preset.encoder,
            "vae": preset.vae,
            "source_width": source.width,
            "source_height": source.height,
        },
        "error": None,
        "result": None,
    }
    entries.insert(0, entry)
    store(project, entries)
    await db.commit()  # Native Comfy UUID is durable BEFORE POST /prompt.
    try:
        await comfy.submit(settings, preset, data, req.prompt, seed, w, h, job_id)
        entry = await update_job(db, req.project_id, job_id, status="queued")
    except comfy.ComfyFailure as exc:
        entry = await update_job(
            db, req.project_id, job_id, status="failed", error=str(exc)
        )
    except (httpx.HTTPError, ValueError, KeyError):
        entry = await update_job(
            db,
            req.project_id,
            job_id,
            status="submission_unknown",
            error="Connection interrupted. Check this saved job; no new generation will be submitted.",
        )
    return public(entry)


@router.post("/projects/{project_id}/jobs/{job_id}/recover")
async def recover(
    project_id: uuid.UUID,
    job_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    await check_project_permission(project_id, user, db, required="editor")
    settings = get_settings()
    configured(settings)
    project = await _locked_project(db, project_id)
    entries = jobs(project)
    entry = next((j for j in entries if j["id"] == str(job_id)), None)
    if not entry:
        raise HTTPException(404, "Local trial not found.")
    if entry["status"] in TERMINAL:
        await db.commit()
        return public(entry)
    now = datetime.now(timezone.utc)
    if entry.get("lease_until") and datetime.fromisoformat(entry["lease_until"]) > now:
        await db.commit()
        return public(entry)
    lease = str(uuid.uuid4())
    entry.update(lease_id=lease, lease_until=(now + timedelta(seconds=120)).isoformat())
    store(project, entries)
    await db.commit()
    changes = {}
    try:
        status, output = await comfy.poll(settings, entry["interaction_id"])
        changes.update(status=status, error=None)
        if status == "submission_unknown":
            changes["error"] = (
                "ComfyUI has no queue or history record for this job. It may have restarted. No automatic resubmission."
            )
        if output is not None:
            if entry["kind"] == "image":
                await asyncio.to_thread(
                    comfy.prepare_source, output, comfy.PRESETS[entry["preset"]]
                )
                result = await persist_render_to_gallery(
                    db,
                    project_id,
                    SaveRenderRequest(
                        image_base64=base64.b64encode(output).decode(),
                        prompt=entry["prompt"],
                        style="Local architectural trial",
                        seed=entry["generation_settings"]["seed"],
                        model=entry["preset"],
                    ),
                    variant="final",
                    outcome="review_required",
                    presentation_strategy="local_model_trial",
                    source_snapshot={
                        "source_render_id": entry["source_render_id"],
                        "local_job_id": entry["id"],
                        "source_sha256": entry["source_sha256"],
                        "generation_settings": entry["generation_settings"],
                    },
                    capture_fingerprint=entry["source_sha256"],
                    output_fingerprint=hashlib.sha256(output).hexdigest(),
                    render_warnings=[
                        "Local AI illustration. Geometry preservation has not been verified."
                    ],
                )
                changes["result"] = result.model_dump(mode="json")
            else:
                if output[4:8] != b"ftyp":
                    raise comfy.ComfyFailure("ComfyUI did not return an MP4 video.")
                from app.api.v1.documents import _upload_to_storage

                key = f"projects/{project_id}/video-render/{job_id}/comfy-animation.mp4"
                await _upload_to_storage(key, output, "video/mp4")
                video = {
                    "id": entry["id"],
                    "request_id": entry["request_id"],
                    "provider": "comfyui",
                    "mode": "saved_render_animation",
                    "source_render_id": entry["source_render_id"],
                    "requested_by": entry["requested_by"],
                    "model": entry["preset"],
                    "status": "complete",
                    "style": "architectural_film",
                    "camera_motion": "slow_push_in",
                    "control_mode": "single_frame",
                    "duration_seconds": 2,
                    "created_at": entry["created_at"],
                    "video_url": f"/api/v1/files/{key}",
                    "estimated_cost_usd": 0,
                    "prompt": entry["prompt"],
                    "generation_settings": entry["generation_settings"],
                    "fidelity_status": None,
                    "enhancement_warning": "Local AI animation; no prescribed camera route or verified geometry.",
                }
                project = await _locked_project(db, project_id)
                videos = list((project.metadata_ or {}).get("video_pilot_attempts", []))
                if not any(v["id"] == entry["id"] for v in videos):
                    project.metadata_ = {
                        **(project.metadata_ or {}),
                        "video_pilot_attempts": [video, *videos],
                    }
                    await db.commit()
                changes["result"] = _public_attempt(video).model_dump(mode="json")
            changes["status"] = "complete"
    except comfy.ComfyFailure as exc:
        changes.update(status="failed", error=str(exc))
    except (httpx.HTTPError, OSError, ValueError, KeyError, HTTPException):
        await db.rollback()
        changes["error"] = (
            "Could not retrieve or save this job. Check again to recover its original output."
        )
    finally:
        project = await _locked_project(db, project_id)
        entries = jobs(project)
        latest = next(j for j in entries if j["id"] == str(job_id))
        if latest.get("lease_id") == lease:
            latest.update(changes, lease_id=None, lease_until=None)
            store(project, entries)
        await db.commit()
    return public(latest)


@router.post("/projects/{project_id}/jobs/{job_id}/resolve-missing")
async def resolve_missing(
    project_id: uuid.UUID,
    job_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Explicitly release a lost job only after ComfyUI confirms it is absent.

    Does not cancel other GPU jobs, delete output/history or submit anything.
    """
    await check_project_permission(project_id, user, db, required="editor")
    configured(get_settings())
    project = await _locked_project(db, project_id)
    entry = next((j for j in jobs(project) if j["id"] == str(job_id)), None)
    if not entry or entry["status"] != "submission_unknown":
        raise HTTPException(
            409, "Check the original job before resolving a missing request."
        )
    if (
        datetime.now(timezone.utc) - datetime.fromisoformat(entry["created_at"])
    ).total_seconds() < 120:
        raise HTTPException(
            409, "Wait two minutes after submission, then check the original job again."
        )
    await db.commit()
    try:
        state, _ = await comfy.poll(get_settings(), entry["interaction_id"])
    except (httpx.HTTPError, comfy.ComfyFailure):
        raise HTTPException(
            503, "ComfyUI must be online to confirm this request is missing."
        )
    if state != "submission_unknown":
        raise HTTPException(
            409, "The original job still exists. Check it to recover its output."
        )
    project = await _locked_project(db, project_id)
    entries = jobs(project)
    latest = next(j for j in entries if j["id"] == str(job_id))
    if latest["status"] == "submission_unknown" and not latest.get("lease_id"):
        latest.update(
            status="failed",
            error="Marked as failed after ComfyUI confirmed no queue or history record. No generation was retried.",
        )
        store(project, entries)
    await db.commit()
    return public(latest)
