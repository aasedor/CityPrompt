"""Budget admission uses committed reservations before mocked provider work."""

import asyncio
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.api.v1 import render


def user(credits=13):
    return SimpleNamespace(
        id=uuid.UUID(int=7),
        email="student@example.com",
        role="editor",
        render_credits=credits,
        credits_reset_at=datetime.now(timezone.utc),
    )


def request():
    return render.RenderRequest(prompt="A complete neighborhood", model="gpt-image-2", post_process=False)


@pytest.mark.asyncio
async def test_two_sessions_with_last_render_credit_admit_only_one_provider_call(
    monkeypatch,
):
    shared = SimpleNamespace(balance=13, lock=asyncio.Lock())

    class Session:
        def __init__(self, account):
            self.account = account
            self.locked = False

        async def refresh(self, obj, with_for_update=False):
            assert obj is self.account and with_for_update is True
            await shared.lock.acquire()
            self.locked = True
            obj.render_credits = shared.balance

        def add(self, obj):
            pass

        async def commit(self):
            if self.locked:
                shared.balance = self.account.render_credits
                self.locked = False
                shared.lock.release()

        async def rollback(self):
            if self.locked:
                self.locked = False
                shared.lock.release()

    calls = []

    async def provider(*args):
        # Even if the second request arrives while generation is pending,
        # committed funds have already been removed.
        assert shared.balance == 0
        assert not shared.lock.locked()
        calls.append(1)
        await asyncio.sleep(0)
        return "provider-image"

    monkeypatch.setattr(render, "get_settings", lambda: SimpleNamespace(render_global_daily_token_cap=0))
    monkeypatch.setattr(render, "_generate_render_image", provider)
    monkeypatch.setattr(render, "_save_render_audit", AsyncMock())
    accounts = [user(), user()]
    outcomes = await asyncio.gather(
        *(render.generate_render(request(), account, Session(account)) for account in accounts),
        return_exceptions=True,
    )
    assert len(calls) == 1
    assert sum(isinstance(outcome, render.RenderResponse) for outcome in outcomes) == 1
    failures = [outcome for outcome in outcomes if isinstance(outcome, HTTPException)]
    assert len(failures) == 1 and failures[0].status_code == 403
    assert shared.balance == 0


@pytest.mark.asyncio
async def test_classic_and_direct_render_use_same_daily_cap_lock(mock_db):
    from app.api.v1.direct_3d_render import _DIRECT_RENDER_CAP_LOCK

    scalar = MagicMock()
    scalar.scalar.return_value = 0
    mock_db.execute.return_value = scalar
    await render._reserve_render(mock_db, user(), request(), "gpt-image-2", 13, 100)
    first_call = mock_db.execute.call_args_list[0]
    assert first_call.args[1]["lock_key"] == _DIRECT_RENDER_CAP_LOCK
    mock_db.refresh.assert_awaited_once()
    assert mock_db.refresh.call_args.kwargs["with_for_update"] is True
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_provider_failure_refunds_once(monkeypatch, mock_db):
    account = user()
    monkeypatch.setattr(render, "get_settings", lambda: SimpleNamespace(render_global_daily_token_cap=0))
    monkeypatch.setattr(
        render,
        "_generate_render_image",
        AsyncMock(side_effect=HTTPException(502, "provider failed")),
    )
    with pytest.raises(HTTPException) as exc:
        await render.generate_render(request(), account, mock_db)
    assert exc.value.status_code == 502
    assert account.render_credits == 13
    reservation = next(
        call.args[0] for call in mock_db.add.call_args_list if isinstance(call.args[0], render.RenderAuditLog)
    )
    assert reservation.tokens_spent == 0
    await render._refund_render(mock_db, account, reservation)
    assert account.render_credits == 13


@pytest.mark.asyncio
async def test_audit_storage_failure_keeps_image_and_single_charge(monkeypatch, mock_db):
    account = user()
    monkeypatch.setattr(render, "get_settings", lambda: SimpleNamespace(render_global_daily_token_cap=0))
    monkeypatch.setattr(render, "_generate_render_image", AsyncMock(return_value="paid-image"))
    monkeypatch.setattr(
        render,
        "_save_render_audit",
        AsyncMock(side_effect=RuntimeError("storage unavailable")),
    )
    response = await render.generate_render(request(), account, mock_db)
    assert response.image_base64 == "paid-image"
    assert account.render_credits == 0
    reservations = {
        id(call.args[0]) for call in mock_db.add.call_args_list if isinstance(call.args[0], render.RenderAuditLog)
    }
    assert len(reservations) == 1
