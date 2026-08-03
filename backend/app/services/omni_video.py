"""Gemini Omni video helpers for the bounded City Prompt pilot.

This module deliberately makes one HTTP POST per generation request.  It does
not use an SDK retry layer: the caller owns idempotency and the bounded pilot
ledger before reaching this boundary.
"""

from __future__ import annotations

import base64
import binascii
import io
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import httpx
from PIL import Image

OMNI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
MAX_GUIDE_IMAGE_BYTES = 12 * 1024 * 1024
MIN_GUIDE_IMAGE_EDGE = 640

STYLE_PROMPTS: dict[str, str] = {
    "golden_hour": (
        "Late golden-hour sunlight with long soft shadows, warm limestone and brick, "
        "subtle atmospheric haze, restrained lens bloom, and premium architectural-film color grading"
    ),
    "crisp_daylight": (
        "Bright soft daylight after a clearing storm, crisp material definition, realistic neutral color, "
        "soft cloud shadows, and polished architectural-film color grading"
    ),
    "after_rain": (
        "A refined after-rain atmosphere with damp paving, subtle physically plausible reflections, "
        "soft overcast-to-sun light, rich planting, and cinematic contrast"
    ),
    "blue_hour": (
        "Early blue hour with a luminous sky, warm interior window light, realistic street and park lighting, "
        "and sophisticated low-noise cinematic exposure"
    ),
    "warm_overcast": (
        "Warm bright overcast daylight, exceptionally soft shadows, natural material color, lush but plausible "
        "landscape detail, and calm high-end architectural photography"
    ),
}

MOTION_PROMPTS: dict[str, str] = {
    "path_follow": (
        "Use the drawn route to define heading and curve shape, not the amount of distance to cover. Make an extremely "
        "slow constant-altitude drone truck with gentle banking only where the route curves. Do not dolly toward the "
        "site, zoom, descend, or increase the apparent building scale by more than five percent"
    ),
    "forward_descent": (
        "Track forward along the route while descending very gradually toward the central park; keep a dignified, "
        "slow real-estate-film pace"
    ),
    "reveal_ascent": (
        "Track forward along the route while rising gradually to reveal the full two-building composition and its "
        "surrounding urban context"
    ),
    "orbit_left": (
        "Use the route as a counter-clockwise orbital arc around the central park, maintaining stable altitude, "
        "distance, horizon, and subject scale"
    ),
    "orbit_right": (
        "Use the route as a clockwise orbital arc around the central park, maintaining stable altitude, distance, "
        "horizon, and subject scale"
    ),
    "street_walkby": (
        "Create a stabilized pedestrian-height walk-by parallel to the visible site frontage at an unhurried walking "
        "pace. Hold the lens at 1.7 metres above the sidewalk with a natural 35 mm perspective, level verticals, "
        "no drone rise, and no orbit. Travel no more than 4 metres during the entire shot"
    ),
}


@dataclass(frozen=True)
class GuideImage:
    data: bytes
    mime_type: str
    width: int
    height: int


@dataclass(frozen=True)
class OmniVideoResult:
    interaction_id: str
    video_bytes: bytes
    mime_type: str


@dataclass(frozen=True)
class OmniVideoContent:
    data: str | None
    uri: str | None
    mime_type: str


def decode_guide_image(value: str) -> GuideImage:
    """Decode and inspect a base64 PNG/JPEG without trusting the data-URL label."""
    encoded = value.split(",", 1)[1] if "," in value else value
    try:
        data = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("The captured guide frame is not valid base64 image data.") from exc
    if not data:
        raise ValueError("The captured guide frame is empty.")
    if len(data) > MAX_GUIDE_IMAGE_BYTES:
        raise ValueError("The captured guide frame exceeds the 12 MB pilot limit.")

    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            image_format = (image.format or "").upper()
    except Exception as exc:  # Pillow raises several format-specific exceptions.
        raise ValueError("The captured guide frame is not a readable PNG or JPEG.") from exc

    if image_format not in {"PNG", "JPEG"}:
        raise ValueError("The captured guide frame must be PNG or JPEG.")
    if min(width, height) < MIN_GUIDE_IMAGE_EDGE:
        raise ValueError(
            f"The captured guide frame is only {width}×{height}; keep the globe visible and capture at least 640 px."
        )
    mime_type = "image/png" if image_format == "PNG" else "image/jpeg"
    return GuideImage(data=data, mime_type=mime_type, width=width, height=height)


def _screen_region(point: Mapping[str, float]) -> str:
    horizontal = "left" if point["x"] < 0.34 else "right" if point["x"] > 0.66 else "center"
    vertical = "upper" if point["y"] < 0.34 else "lower" if point["y"] > 0.66 else "middle"
    return f"{vertical} {horizontal}"


def describe_route(points: Iterable[Mapping[str, float]]) -> str:
    route = list(points)
    start = _screen_region(route[0])
    finish = _screen_region(route[-1])
    dx = route[-1]["x"] - route[0]["x"]
    bends = max(0, len(route) - 2)
    turn = "with a gentle rightward arc" if dx > 0.12 else "with a gentle leftward arc" if dx < -0.12 else "nearly straight"
    return f"The route begins in the {start} of frame and finishes in the {finish}, {turn}, using {bends} guide bends."


def build_cinematic_prompt(
    *,
    route_points: Iterable[Mapping[str, float]],
    style: str,
    camera_motion: str,
    scene_brief: str,
    duration_seconds: int,
) -> str:
    """Build the immutable-geometry prompt used for both preflight and generation."""
    style_prompt = STYLE_PROMPTS[style]
    motion_prompt = MOTION_PROMPTS[camera_motion]
    route_description = describe_route(route_points)
    is_street = camera_motion == "street_walkby"
    travel_lock = (
        "Move no more than 4 metres during the full shot."
        if is_street
        else (
            "Translate no more than one eighth of the shorter authored building dimension during the full shot; "
            "hold altitude, focal length, and subject scale constant."
            if camera_motion == "path_follow"
            else "Keep total camera travel below one quarter of an authored building length during the full shot."
        )
    )
    shot_kind = "pedestrian-height architectural walk-by" if is_street else "professional architectural drone shot"
    framing_lock = (
        "Keep the authored facade and adjacent public realm in clear close-up view for the entire shot. Resolve fine "
        "stone joints, window frames, balcony railings, entrances, planting, and paving consistently without changing "
        "their design or position."
        if is_street
        else "Keep every authored building and the complete authored open space clearly legible together for all eight seconds."
    )
    return "\n\n".join(
        [
            (
                f"Create one single continuous, unbroken {duration_seconds}-second 16:9 {shot_kind} from the supplied "
                "City Prompt planning image. This is one coherent camera take—no cuts, "
                "montage, jump transitions, or time lapse."
            ),
            (
                "FLIGHT PATH: The route is supplied as normalized screen-space coordinates and described below; "
                "there is intentionally no route graphic burned into the first frame. Travel smoothly from the "
                "described start region toward the described finish region at a physically plausible speed. "
                f"{route_description} {motion_prompt}."
            ),
            (
                "STATIC SCENE IDENTITY — HIGHEST PRIORITY: This is a camera animation of one frozen 3D scene, not "
                "a scene redesign. Preserve the exact site plan and recognizable spatial identity of the source. "
                f"{scene_brief.strip()} Keep every authored zone at the same location, footprint, height, proportions, "
                "setbacks, roofline, opening pattern, path layout, and street relationship in every frame. Each building "
                "zone is one indivisible persistent object and must never split into wings, merge with another zone, or "
                "duplicate. COURTYARD TOPOLOGY CHECKSUM: before generating motion, count every visible courtyard, lightwell, "
                "roof void, and wing in the first frame. Treat each void as immutable three-dimensional negative space. "
                "Preserve its exact count, perimeter, length, width, aspect ratio, separation, alignment, and position inside "
                "its building in all 192 frames. Never lengthen, widen, shrink, merge, split, fill, or invent a courtyard or "
                "roof opening. Architecture and site geometry are immutable. Do not invent a fountain, pool, monument, "
                "gazebo, roof feature, extra path, or "
                "landscape centerpiece unless the archetype contract explicitly requires it. B1, B2, P1, and all similar "
                "zone tokens are internal prompt identifiers only; never render them as labels, callouts, leader lines, or text."
            ),
            (
                "VISUAL FINISH: Apply texture, material, lighting, and atmospheric enhancement to the existing geometry "
                "only; do not remodel, reinterpret, or regenerate the architecture or landscape. "
                f"{style_prompt}. Use realistic PBR materials, coherent reflections, the same planted areas, "
                "and razor-sharp facade detail. This must read as premium cinema-camera footage, not a game capture or map model."
            ),
            (
                "ACTOR AND TRAFFIC LOCK: Before the first visible frame, remove every car and pedestrian baked into the "
                "source map tiles. This pre-frame actor cleanup is explicitly allowed and does not alter the locked site "
                "geometry. Keep every street and sidewalk empty for this pilot: no replacement cars, bicycles, buses, "
                "motorcycles, pedestrians, or animals in any frame. Do not preserve, invent, spawn, fade, dissolve, "
                "teleport, duplicate, or move any actor or vehicle."
            ),
            (
                "CONTINUITY LOCKS: Maintain one stable world coordinate system and physically realistic parallax. "
                "Every physical object has persistent identity and fixed world coordinates across all 192 frames. Every "
                "wall, roof, courtyard edge, tree mass, path, and park surface visible at the start remains the same object "
                "through the end; normal camera occlusion is the only reason an object may leave the frame. "
                "Do not add, remove, duplicate, repeat, resize, bend, melt, or redesign any building, road, park, path, "
                "tree mass, or landmark. No facade warping, sliding textures, floating objects, fisheye distortion, "
                "excessive motion blur, visible red route, pins, labels, captions, logos, borders, or split screens. "
                f"Move slowly. {travel_lock} Courtyard perimeter drift or changing roof negative space is a failed result. Keep all "
                f"buildings spatially coherent. {framing_lock} Keep the "
                "horizon level, motion fluid, exposure stable, and the final composition calm and sharp. "
                "Output polished 720p 24 fps cinematic footage."
            ),
        ]
    )


def build_omni_payload(
    *,
    model: str,
    guide_base64: str,
    guide_mime_type: str,
    prompt: str,
    duration_seconds: int,
    reference_images: Iterable[GuideImage] = (),
) -> dict[str, Any]:
    encoded = guide_base64.split(",", 1)[1] if "," in guide_base64 else guide_base64
    references = list(reference_images)
    input_items: list[dict[str, Any]] = [
        {"type": "image", "data": encoded, "mime_type": guide_mime_type},
    ]
    input_items.extend(
        {
            "type": "image",
            "data": base64.b64encode(reference.data).decode("ascii"),
            "mime_type": reference.mime_type,
        }
        for reference in references
    )
    input_items.append({"type": "text", "text": prompt})
    return {
        "model": model,
        "input": input_items,
        "generation_config": {"video_config": {"task": "reference_to_video" if references else "image_to_video"}},
        "response_format": {
            "type": "video",
            "aspect_ratio": "16:9",
            "duration": f"{duration_seconds}s",
            "delivery": "inline",
        },
        "background": False,
        "store": False,
        "stream": False,
    }


def bind_reference_roles(prompt: str, reference_count: int) -> str:
    """Bind ordered images to Omni's documented first-frame/reference tags."""
    if reference_count <= 0:
        return prompt
    reference_tags = " ".join(
        f"<IMAGE_REF_{index}>@Image{index + 2}" for index in range(reference_count)
    )
    return (
        f"[# Sources <FIRST_FRAME>@Image1] [# References {reference_tags}]\n\n{prompt}\n\n"
        "Use Image1 as the exact geometric starting view and camera composition. The first visible frame must be its "
        "clean architectural version after removing only baked-in cars, pedestrians, pins, labels, and route markup. "
        f"Use Images 2 through {reference_count + 1} only as references for video generation; those images must "
        "not be used as literal initial frames or appear as shots in the video. Use each reference only for its "
        "explicitly mapped authored archetype's facade, roof, material, or landscape identity. Never copy a "
        "reference image's people, vehicles, camera angle, background, footprint, massing, or site layout into Image1."
    )


def find_omni_video_content(payload: Mapping[str, Any]) -> OmniVideoContent:
    """Locate video data/URI in both flat and nested Interactions responses."""
    preferred = payload.get("output_video") or payload.get("outputVideo")
    # Current Interactions responses place generated media inside ``steps``;
    # older SDK shapes expose ``outputs``/``output_video``. Traverse the whole
    # completion envelope so both remain readable.
    queue: list[Any] = [preferred, payload]
    visited = 0
    while queue and visited < 200:
        visited += 1
        candidate = queue.pop(0)
        if isinstance(candidate, Mapping):
            mime_type = str(candidate.get("mime_type") or candidate.get("mimeType") or "")
            looks_like_video = candidate.get("type") == "video" or mime_type.startswith("video/")
            if looks_like_video and (candidate.get("data") or candidate.get("uri")):
                return OmniVideoContent(
                    data=str(candidate.get("data")) if candidate.get("data") else None,
                    uri=str(candidate.get("uri")) if candidate.get("uri") else None,
                    mime_type=mime_type or "video/mp4",
                )
            queue.extend(candidate.values())
        elif isinstance(candidate, list):
            queue.extend(candidate)
    status = payload.get("status", "unknown")
    top_level = ", ".join(sorted(str(key) for key in payload.keys()))
    raise ValueError(
        f"Gemini Omni returned status '{status}' without video data or a video URI (response keys: {top_level})."
    )


def parse_omni_video(payload: Mapping[str, Any]) -> OmniVideoResult:
    """Extract inline MP4 output across current Interactions response shapes."""
    output = find_omni_video_content(payload)
    if not output.data:
        raise ValueError("Gemini Omni returned a video URI; download is required before parsing bytes.")
    try:
        video_bytes = base64.b64decode(output.data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Gemini Omni returned invalid base64 video data.") from exc
    if not video_bytes:
        raise ValueError("Gemini Omni returned an empty video.")
    return OmniVideoResult(
        interaction_id=str(payload.get("id") or ""),
        video_bytes=video_bytes,
        mime_type=output.mime_type,
    )


def _download_url(uri: str) -> str:
    """Turn a Gemini Files metadata URI into its media download endpoint."""
    if "generativelanguage.googleapis.com/v1beta/files/" in uri and "/download/v1beta/" not in uri:
        uri = uri.replace(
            "generativelanguage.googleapis.com/v1beta/files/",
            "generativelanguage.googleapis.com/download/v1beta/files/",
        )
        if ":download" not in uri:
            uri = f"{uri}:download"
        return f"{uri}{'&' if '?' in uri else '?'}alt=media"
    return uri


async def request_omni_video_once(
    *,
    api_key: str,
    payload: Mapping[str, Any],
    timeout_seconds: int,
) -> OmniVideoResult:
    """Issue exactly one provider POST. Transport retries are explicitly disabled."""
    timeout = httpx.Timeout(timeout_seconds, connect=20.0)
    transport = httpx.AsyncHTTPTransport(retries=0)
    async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
        response = await client.post(
            OMNI_INTERACTIONS_URL,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=dict(payload),
        )
        if response.status_code >= 400:
            detail = response.text.replace(api_key, "[redacted]")[:800]
            raise RuntimeError(f"Gemini Omni HTTP {response.status_code}: {detail}")
        interaction_payload = response.json()
        output = find_omni_video_content(interaction_payload)
        if output.data:
            return parse_omni_video(interaction_payload)
        if not output.uri or not output.uri.startswith("https://"):
            raise ValueError("Gemini Omni returned an unsupported non-HTTPS video URI.")

        # This GET retrieves the already-created media; it is not a second
        # generation submission and uses the same no-retry transport.
        download = await client.get(
            _download_url(output.uri),
            headers={"x-goog-api-key": api_key},
        )
        if download.status_code >= 400:
            detail = download.text.replace(api_key, "[redacted]")[:500]
            raise RuntimeError(f"Gemini video download HTTP {download.status_code}: {detail}")
        if not download.content:
            raise ValueError("Gemini returned an empty video download.")
        return OmniVideoResult(
            interaction_id=str(interaction_payload.get("id") or ""),
            video_bytes=download.content,
            mime_type=download.headers.get("content-type", output.mime_type).split(";", 1)[0],
        )
