"""Closed legacy relay; shared project access uses authenticated HTTP APIs.

Live presence/edit broadcasting must not be enabled until connection identity,
project membership, edit permissions, and recipient revocation are enforced.
"""

from fastapi import APIRouter, WebSocket

router = APIRouter()

COLLABORATION_UNAVAILABLE_REASON = (
    "Live collaboration is paused; use authenticated project APIs."
)


@router.websocket("/ws/projects/{project_id}")
async def project_collaboration(websocket: WebSocket, project_id: str):
    """Reject before accepting or receiving any private project messages."""
    await websocket.close(code=1008, reason=COLLABORATION_UNAVAILABLE_REASON)
