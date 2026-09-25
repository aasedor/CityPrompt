"""Optional operator-installed, persistent allowance for one bounded local trial.

The caller holds the Project row lock and commits this metadata in the same
transaction as its durable image/video attempt. No allowance is created by a
student request. Admission consumes a slot, including failures; reads and
preflight never consume one. This conservative rule cannot replay paid calls.
"""

from copy import deepcopy
from types import SimpleNamespace
import uuid
from fastapi import HTTPException
from sqlalchemy import select

from app.models.models import Project

TRIAL_KEY = "render_trial_allowance"


def check_trial_available(project, user_id, kind):
    """Run the admission rule on a detached copy: free preflight reserves nothing."""
    if project is not None:
        reserve_trial_slot(SimpleNamespace(metadata_=deepcopy(project.metadata_)), user_id,
                           kind, "preflight:" + uuid.uuid4().hex, "preflight")


def reserve_trial_slot(project, user_id, kind: str, request_id: str, fingerprint: str):
    metadata = dict(project.metadata_ or {})
    original = metadata.get(TRIAL_KEY)
    if original is None:
        return
    trial = deepcopy(original)
    if trial.get("user_id") != str(user_id):
        raise HTTPException(403, "This rendering trial is assigned to a different account.")
    if kind not in {"image", "video"}:
        raise ValueError("Unknown trial media kind")
    limit = trial.get(kind + "_limit")
    reservations = trial.get(kind + "_requests", {})
    if type(limit) is not int or not 0 <= limit <= {"image": 10, "video": 3}[kind] or not isinstance(reservations, dict):
        raise HTTPException(503, "The rendering trial allowance needs operator review.")
    if request_id in reservations:
        if reservations[request_id] != fingerprint:
            raise HTTPException(409, "This trial request ID already belongs to different media.")
        return
    if len(reservations) >= limit:
        raise HTTPException(409, f"The authorized {limit}-{kind} trial allowance is exhausted. No new provider call was made.")
    reservations[request_id] = fingerprint
    trial[kind + "_requests"] = reservations
    metadata[TRIAL_KEY] = trial
    project.metadata_ = metadata


async def reserve_image_trial_slot(db, project_id, user_id, request_id, fingerprint):
    project = await db.scalar(select(Project).where(Project.id == project_id).with_for_update()
                              .execution_options(populate_existing=True))
    if project is None:
        raise HTTPException(404, "Project not found")
    reserve_trial_slot(project, user_id, "image", request_id, fingerprint)
