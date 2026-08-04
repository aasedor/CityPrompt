"""Real-world site context pack for street-level renders.

Validated 2026-06-10 (artifacts/sv-context-pilot/): Street View panos + a
top-down satellite tile + a Places tenant layout make renders reproduce the
REAL surroundings (businesses, signage, lane counts) instead of hallucinated
ones. This module fetches that pack server-side using GOOGLE_MAPS_API_KEY.

Cost per uncached site: 4 Street View images (~$0.028) + 1 static satellite
tile (~$0.002) + 1 Places nearby search (~$0.032). Metadata gate is free.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_CACHE: dict[tuple, tuple[float, dict | None]] = {}
_CACHE_TTL_S = 600

# NOTE: Places/tenant TEXT grounding was removed 2026-06-10 — it forced business
# names ("Happy Cake", "1bridge Marketing") into residential scenes where they
# don't belong and confused the model. The Street View PHOTOS still carry real
# businesses VISUALLY for commercial scenes, so we keep the visual grounding and
# drop the textual one. (Re-add later behind a commercial-vs-residential heuristic.)


async def fetch_streetview_plate(
    lat: float,
    lng: float,
    heading: float,
    fov: float,
    width: int,
    height: int,
) -> dict | None:
    """Fetch ONE real Street View photo aligned to a given camera, for use as the
    composite background plate in SV-snap photomontage mode.

    Snaps to the nearest pano and returns its true position + the offset from the
    requested point (the accuracy cost). Returns None when there's no coverage so
    the caller can fall back to the 3D-tiles capture. Never raises.
    """
    key = getattr(get_settings(), "google_maps_api_key", "") or ""
    if not key:
        return None
    # SV Static caps each dimension at 640 and fov at 120.
    w = max(16, min(640, int(width)))
    h = max(16, min(640, int(height)))
    fov = max(10.0, min(120.0, float(fov)))
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            meta = (
                await client.get(
                    "https://maps.googleapis.com/maps/api/streetview/metadata",
                    params={"location": f"{lat},{lng}", "key": key},
                )
            ).json()
            if meta.get("status") != "OK":
                logger.info("sv-plate: no coverage at %.5f,%.5f", lat, lng)
                return None
            pano = meta["pano_id"]
            ploc = meta.get("location", {})
            r = await client.get(
                "https://maps.googleapis.com/maps/api/streetview",
                params={
                    "pano": pano,
                    "size": f"{w}x{h}",
                    "heading": round(heading),
                    "fov": round(fov),
                    "pitch": 0,
                    "key": key,
                },
            )
            if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/"):
                logger.warning("sv-plate: image fetch HTTP %s", r.status_code)
                return None
    except Exception as exc:  # noqa: BLE001
        logger.warning("sv-plate fetch failed: %s", exc)
        return None

    offset_m = None
    if ploc.get("lat") is not None:
        import math

        dlat = math.radians(ploc["lat"] - lat)
        dlng = math.radians(ploc["lng"] - lng)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat)) * math.cos(math.radians(ploc["lat"])) * math.sin(dlng / 2) ** 2
        )
        offset_m = round(2 * 6_371_000 * math.asin(math.sqrt(a)), 1)
    return {
        "photo_base64": base64.b64encode(r.content).decode(),
        "pano_offset_m": offset_m,
        "pano_date": meta.get("date"),
        "width": w,
        "height": h,
    }


async def build_site_context_pack(lat: float, lng: float, heading: float | None = None) -> dict | None:
    """Returns {"images": [(label, mime, b64), ...], "prompt_block": str} or None.

    Never raises — context is an enhancer, not a dependency; any failure
    degrades to None and the render proceeds without it.
    """
    key = getattr(get_settings(), "google_maps_api_key", "") or ""
    if not key:
        return None
    cache_key = (round(lat, 4), round(lng, 4), round(heading) % 360 if heading is not None else None)
    hit = _CACHE.get(cache_key)
    if hit and (time.monotonic() - hit[0]) < _CACHE_TTL_S:
        return hit[1]

    pack: dict | None = None
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            meta = (
                await client.get(
                    "https://maps.googleapis.com/maps/api/streetview/metadata",
                    params={"location": f"{lat},{lng}", "key": key},
                )
            ).json()
            if meta.get("status") != "OK":
                logger.info("site-context: no Street View coverage at %.5f,%.5f", lat, lng)
                _CACHE[cache_key] = (time.monotonic(), None)
                return None
            pano = meta["pano_id"]

            # If the nearest Street View pano is more than 20 m from the site, its imagery
            # is too offset to be a trustworthy reference — skip grounding entirely and
            # degrade to clay/tiles + prompt, exactly like no coverage.
            ploc = meta.get("location", {})
            if ploc.get("lat") is not None and ploc.get("lng") is not None:
                import math

                dlat = math.radians(ploc["lat"] - lat)
                dlng = math.radians(ploc["lng"] - lng)
                a = (
                    math.sin(dlat / 2) ** 2
                    + math.cos(math.radians(lat)) * math.cos(math.radians(ploc["lat"])) * math.sin(dlng / 2) ** 2
                )
                offset_m = 2 * 6_371_000 * math.asin(math.sqrt(a))
                if offset_m > 20:
                    logger.info(
                        "site-context: nearest Street View is %.0f m away (>20 m) at " "%.5f,%.5f — skipping grounding",
                        offset_m,
                        lat,
                        lng,
                    )
                    _CACHE[cache_key] = (time.monotonic(), None)
                    return None

            async def sv(heading: int) -> bytes | None:
                r = await client.get(
                    "https://maps.googleapis.com/maps/api/streetview",
                    params={"pano": pano, "size": "640x640", "heading": heading, "fov": 90, "pitch": 0, "key": key},
                )
                ok = r.status_code == 200 and r.headers.get("content-type", "").startswith("image/")
                return r.content if ok else None

            async def satellite() -> bytes | None:
                r = await client.get(
                    "https://maps.googleapis.com/maps/api/staticmap",
                    params={
                        "center": f"{lat},{lng}",
                        "zoom": 19,
                        "size": "640x640",
                        "maptype": "satellite",
                        "key": key,
                    },
                )
                ok = r.status_code == 200 and r.headers.get("content-type", "").startswith("image/")
                return r.content if ok else None

            tasks = [sv(0), sv(90), sv(180), sv(270), satellite()]
            if heading is not None:
                tasks.append(sv(round(heading) % 360))
            results = await asyncio.gather(*tasks)
            n, e, s, w, sat = results[:5]
            fwd = results[5] if heading is not None else None

        images: list[tuple[str, str, str]] = []
        for img, direction in ((n, "NORTH"), (e, "EAST"), (s, "SOUTH"), (w, "WEST")):
            if img:
                images.append(
                    (
                        f"CONTEXT PHOTO (REAL Street View photo of this exact site, looking "
                        f"{direction}) — use it to confirm the true MATERIALS, colours and facade "
                        f"details of the EXISTING buildings on that side (e.g. brick vs stucco, "
                        f"roof, windows, fences), not their geometry.",
                        "image/jpeg",
                        base64.b64encode(img).decode(),
                    )
                )
        if sat:
            images.append(
                (
                    "CONTEXT AERIAL (REAL top-down satellite photo of this site) — a secondary "
                    "reference for the real layout (roadway width, lanes, parking, footprints) "
                    "where it helps; the base massing image (Image 1) remains the authority for "
                    "geometry.",
                    "image/jpeg",
                    base64.b64encode(sat).decode(),
                )
            )
        # Forward-facing plate at the EXACT camera heading — appended LAST so it is the most
        # heavily-weighted reference ("read last"). Grounds the distant background in the real
        # scene instead of letting the model invent it.
        if fwd:
            images.append(
                (
                    "FORWARD STREET VIEW (REAL photo looking in the camera's EXACT view direction) "
                    "- the GROUND TRUTH for the DISTANT BACKGROUND and existing surroundings. "
                    "Reconstruct the real far buildings, trees, fields, fences and horizon as they "
                    "appear here instead of inventing them; where this photo shows open ground, "
                    "fields or sky in the distance, keep it open and do NOT add buildings that are "
                    "not in it. IGNORE whatever currently occupies the design zone in this photo - "
                    "that area is replaced by the new building in Image 1.",
                    "image/jpeg",
                    base64.b64encode(fwd).decode(),
                )
            )
        if not images:
            _CACHE[cache_key] = (time.monotonic(), None)
            return None

        prompt_block = (
            "REAL-WORLD DETAIL REFERENCE - read last, weight heavily for MATERIALS and "
            "DETAIL. Image 1 (the 3D massing / tiles capture) is the AUTHORITATIVE source for "
            "LAYOUT ONLY - the position, footprint, height and massing of every building, "
            "street and tree, and the camera angle. Do not move, add, or remove anything from "
            "it. Treat it as a low-detail blockout: it tells you WHAT is where, but it is NOT "
            "a guide to surface quality. RENDER THE ENTIRE FRAME as crisp, sharp, "
            "photorealistic architecture - every building, existing and new, plus the ground "
            "and street. Do NOT reproduce the blur, melting, smearing, warping or "
            "low-resolution artifacts of the tiles capture; reconstruct clean, well-defined "
            "facades, edges, rooflines and pavement everywhere in the image, not only inside "
            "the design zone. The other attached CONTEXT photos are REAL photographs of this "
            "exact site - use them to read the true MATERIALS, colours and facade details of "
            "the EXISTING surroundings (brick vs stucco, roof colour, window and fence style) "
            "and render those buildings crisply with those real materials, keeping their "
            "position and massing as in Image 1. Do not invent storefronts, signage, or shops "
            "not visible in the photos. If a FORWARD STREET VIEW photo is attached, treat it as "
            "the authority for the DISTANT BACKGROUND and existing surroundings: reconstruct what "
            "it really shows, and keep open ground, fields or sky open - never invent extra "
            "buildings to fill the distance."
        )
        pack = {"images": images, "prompt_block": prompt_block}
    except Exception as exc:  # noqa: BLE001 — context must never break a render
        logger.warning("site-context fetch failed: %s", exc)
        pack = None

    _CACHE[cache_key] = (time.monotonic(), pack)
    return pack
