"""The legacy project relay must reject every handshake before receiving data."""

from unittest.mock import AsyncMock

import pytest
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

from app.api.v1.collaboration import (
    COLLABORATION_UNAVAILABLE_REASON,
    project_collaboration,
)
from app.main import app


@pytest.mark.parametrize("project_id", ["00000000-0000-0000-0000-000000000001", "not-a-project"])
@pytest.mark.parametrize("credential_mode", ["anonymous", "bearer", "query"])
def test_registered_relay_rejects_all_handshakes(project_id, credential_mode, auth_headers):
    # Exercise the real application route without invoking its startup services.
    client = TestClient(app)
    path = f"/ws/projects/{project_id}"
    headers = auth_headers if credential_mode == "bearer" else {}
    if credential_mode == "query":
        token = auth_headers["Authorization"].removeprefix("Bearer ")
        path += f"?token={token}&name=Owner&email=owner@example.com"

    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(path, headers=headers):
            pytest.fail("The unavailable relay accepted a handshake")
    assert exc.value.code == 1008
    assert exc.value.reason == COLLABORATION_UNAVAILABLE_REASON


@pytest.mark.asyncio
async def test_relay_never_accepts_receives_or_broadcasts():
    receive = AsyncMock()
    send = AsyncMock()
    websocket = WebSocket({"type": "websocket"}, receive=receive, send=send)

    await project_collaboration(websocket, "private-project")

    receive.assert_not_awaited()
    send.assert_awaited_once_with(
        {
            "type": "websocket.close",
            "code": 1008,
            "reason": COLLABORATION_UNAVAILABLE_REASON,
        }
    )
