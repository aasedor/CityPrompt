import asyncio
import copy
from types import SimpleNamespace
import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.models.models import Project
from app.services.render_trial import TRIAL_KEY, reserve_trial_slot, reserve_image_trial_slot
from tests.test_render_attempts import isolated  # real PostgreSQL, disposable schema


def project(user="student"):
    return SimpleNamespace(metadata_={"address": "Keep", TRIAL_KEY: {
        "user_id": user, "image_limit": 10, "video_limit": 3,
        "image_requests": {}, "video_requests": {},
    }})


@pytest.mark.parametrize("kind,limit", [("image", 10), ("video", 3)])
def test_finite_slots_keep_failures_counted_and_replay_idempotent(kind, limit):
    p = project()
    for i in range(limit):
        reserve_trial_slot(p, "student", kind, str(i), "same-request")
    saved = copy.deepcopy(p.metadata_)
    reserve_trial_slot(p, "student", kind, "0", "same-request")
    assert p.metadata_ == saved
    assert p.metadata_["address"] == "Keep"
    with pytest.raises(HTTPException) as error:
        reserve_trial_slot(p, "student", kind, "extra", "request")
    assert error.value.status_code == 409
    assert p.metadata_ == saved
    with pytest.raises(HTTPException):
        reserve_trial_slot(p, "student", kind, "0", "different-request")


def test_trial_is_bound_to_account_and_does_not_change_unconfigured_projects():
    p = project()
    with pytest.raises(HTTPException) as error:
        reserve_trial_slot(p, "other", "image", "1", "hash")
    assert error.value.status_code == 403
    ordinary = SimpleNamespace(metadata_={"address": "Keep"})
    reserve_trial_slot(ordinary, "student", "image", "1", "hash")
    assert ordinary.metadata_ == {"address": "Keep"}


@pytest.mark.asyncio
@pytest.mark.parametrize("kind,limit", [("image", 10), ("video", 3)])
async def test_parallel_admission_and_new_sessions_cannot_exceed_trial(isolated, kind, limit):
    f = isolated
    async with f.sessions() as db:
        p = await db.get(Project, f.project.id)
        p.metadata_ = project(str(f.user.id)).metadata_
        await db.commit()
    async def reserve(key):
        async with f.sessions() as db:
            try:
                if kind == "image":
                    await reserve_image_trial_slot(db, f.project.id, f.user.id, key, "hash")
                else:
                    p = await db.scalar(select(Project).where(Project.id == f.project.id).with_for_update())
                    reserve_trial_slot(p, f.user.id, kind, key, "hash")
                await db.commit()
                return True
            except HTTPException:
                await db.rollback()
                return False
    admitted = await asyncio.gather(*(reserve(str(uuid.uuid4())) for _ in range(20)))
    assert sum(admitted) == limit
    async with f.sessions() as db:
        p = await db.get(Project, f.project.id)
        keys = p.metadata_[TRIAL_KEY][kind + "_requests"]
        assert len(keys) == limit
    assert await reserve(next(iter(keys)))
    assert not await reserve(str(uuid.uuid4()))
    f.provider.assert_not_called()
