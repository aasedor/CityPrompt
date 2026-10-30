"""Authenticated admission for server-funded Maps calls, shared across endpoints."""

from fastapi import Depends, HTTPException, Request

from app.core.config import get_settings
from app.core.rate_limit import enforce_rate_limit
from app.core.security import require_auth


async def admit_maps_request(request: Request, user, units: int = 1) -> None:
    if user is None:
        raise HTTPException(401, "Authentication required")
    await enforce_rate_limit(request, 120, bucket="maps-account-minute", identity=str(user.id))
    await enforce_rate_limit(request, 1200, bucket="maps-peer-minute")
    # Reserve the full batch before making any provider calls. Rejected requests
    # may consume admissions but can never exceed either shared hard bound.
    for _ in range(units):
        await enforce_rate_limit(request, 600, 3600, bucket="maps-account-hour", identity=str(user.id))
        await enforce_rate_limit(
            request, get_settings().maps_requests_per_hour, 3600, bucket="maps-global-hour", identity="provider"
        )


async def require_maps_admission(request: Request, user=Depends(require_auth)) -> None:
    await admit_maps_request(request, user)
