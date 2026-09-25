"""First-release paid feature boundary; deterministic authoring stays available."""

import re

from fastapi import HTTPException, Request

from app.core.config import get_settings

_DEFERRED = tuple(re.compile(pattern) for pattern in (
    r"/api/v1/video/.*",
    r"/api/v1/render/(generate|generate-direct-3d)",
    r"/api/v1/buildings/[^/]+/(generate|generate-from-image|render-preview)",
    r"/api/v1/model-cache/prewarm",
    r"/api/v1/custom-style/expand",
    r"/api/v1/urban-dna/.*",
    r"/api/v1/master-plan-2d/.*",
    r"/api/v1/site-zones/[^/]+/(render-layout-preview|render-site-preview)",
    r"/api/v1/site-zones/projects/[^/]+/generate-all",
    r"/api/v1/documents/[^/]+/process",
))


def deferred_classroom_request(method: str, path: str, process_mode: str | None = None):
    if method != "POST":
        return False
    if re.fullmatch(r"/api/v1/documents/projects/[^/]+/upload", path):
        return process_mode != "reference"
    return any(pattern.fullmatch(path) for pattern in _DEFERRED)


async def require_classroom_scope(request: Request):
    if get_settings().classroom_release and deferred_classroom_request(
        request.method, request.url.path.rstrip("/"), request.query_params.get("process_mode"),
    ):
        raise HTTPException(403, detail={
            "code": "outside_classroom_release", "billed": False,
            "message": "This feature is outside the classroom starter release. Use the catalogue, 3D site landscape or current-view image tools. No credits were charged.",
        })
