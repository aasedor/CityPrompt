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
from typing import Any, Iterable, Mapping, Sequence

import httpx
from PIL import Image

OMNI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
MAX_GUIDE_IMAGE_BYTES = 12 * 1024 * 1024
MAX_ROUTE_IMAGE_BYTES = 36 * 1024 * 1024
MAX_PREVIEW_VIDEO_BYTES = 24 * 1024 * 1024
MIN_GUIDE_IMAGE_EDGE = 640

MOTION_PROMPTS: dict[str, str] = {
    "path_follow": (
        "Use the drawn route to define heading and curve shape, not the amount of distance to cover. Make an extremely "
        "slow constant-altitude drone truck with gentle banking only where the route curves. Do not dolly toward the "
        "site, zoom, descend, or increase the apparent building scale by more than two percent"
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


@dataclass(frozen=True)
class PreviewVideo:
    data: bytes
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


def decode_preview_video(value: str, declared_mime_type: str) -> PreviewVideo:
    """Decode the browser-recorded deterministic route preview safely."""
    encoded = value.split(",", 1)[1] if "," in value else value
    try:
        data = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("The route preview is not valid base64 video data.") from exc
    if len(data) < 1024:
        raise ValueError("The route preview is empty or incomplete.")
    if len(data) > MAX_PREVIEW_VIDEO_BYTES:
        raise ValueError("The route preview exceeds the 24 MB pilot limit.")

    mime_type = declared_mime_type.split(";", 1)[0].strip().lower()
    if mime_type not in {"video/webm", "video/mp4"}:
        raise ValueError("The route preview must be WebM or MP4.")
    is_webm = data.startswith(b"\x1aE\xdf\xa3")
    is_mp4 = len(data) >= 12 and data[4:8] == b"ftyp"
    if mime_type == "video/webm" and not is_webm:
        raise ValueError("The route preview MIME type does not match its WebM content.")
    if mime_type == "video/mp4" and not is_mp4:
        raise ValueError("The route preview MIME type does not match its MP4 content.")
    return PreviewVideo(data=data, mime_type=mime_type)


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
    camera_motion: str,
    scene_brief: str,
    duration_seconds: int,
    control_mode: str = "single_frame",
    keyframe_count: int = 1,
    provider: str = "omni",
) -> str:
    """Build a motion-only prompt used for both preflight and generation."""
    prompt_scene_brief = scene_brief.strip()
    motion_prompt = MOTION_PROMPTS[camera_motion]
    route_description = describe_route(route_points)
    is_street = camera_motion == "street_walkby"
    travel_lock = (
        "Move no more than 4 metres during the full shot."
        if is_street
        else (
            "Translate no more than one sixteenth of the shorter authored building dimension during the full shot; "
            "hold altitude, focal length, and subject scale constant."
            if camera_motion == "path_follow"
            else "Keep total camera travel below one quarter of an authored building length during the full shot."
        )
    )
    shot_kind = "pedestrian-height architectural walk-by" if is_street else "professional architectural drone shot"
    framing_lock = (
        "Keep the authored facade and adjacent public realm in the same clear close-up view for the entire shot. Preserve "
        "every already-visible joint, window frame, railing, entrance, plant, and paving edge at its source level of detail."
        if is_street
        else "Keep every authored building and the complete authored open space clearly legible together for all eight seconds."
    )
    if control_mode == "multi_keyframe":
        references = " ".join(
            f"<IMAGE_REF_{index}>@Image{index + 2}"
            for index in range(max(0, keyframe_count - 1))
        )
        control_prefix = f"[# Sources <FIRST_FRAME>@Image1] [# References {references}]"
        input_authority = (
            f"Images1 through Image{keyframe_count} are deterministic City Prompt renders of the same frozen scene, "
            "sampled in chronological order at equal travelled-distance intervals along the route"
        )
        flight_instruction = (
            "Follow the exact chronological camera progression demonstrated by the ordered route images. "
            "Image1 is the literal first frame; later images are geometric and geographic route checkpoints, not alternate designs."
        )
        final_preservation = "preserve the corresponding City Prompt route image and reduce motion between checkpoints"
    elif control_mode == "preview_video":
        control_prefix = ""
        if provider == "seedance_mini" and keyframe_count > 0:
            input_authority = (
                f"@Video1 is City Prompt's deterministic render of the complete camera path through one frozen 3D scene; "
                f"@Image1 through @Image{keyframe_count} are exact chronological geometry checkpoints sampled from that same route"
            )
            flight_instruction = (
                "Copy @Video1's camera positions, headings, speed, timing, focal length, and single-shot continuity exactly. "
                "Use the ordered images only as immutable geometry anchors for the corresponding moments; they are not alternate designs."
            )
        else:
            input_authority = (
                "The supplied video is City Prompt's deterministic render of the complete camera path through one frozen 3D scene"
            )
            flight_instruction = (
                "Copy the supplied video's camera positions, headings, speed, timing, focal length, and single-shot continuity exactly. "
                "Do not substitute a new camera move or treat the video as a loose stylistic reference."
            )
        final_preservation = "preserve the corresponding source-video frame and reduce generative change"
    else:
        control_prefix = ""
        input_authority = "Image1 is the sole authoritative City Prompt render of one frozen 3D scene"
        flight_instruction = "Use the described screen-space route conservatively and keep the camera move extremely small."
        final_preservation = "preserve Image1 unchanged"

    body = "\n\n".join(
        section
        for section in [
            (
                f"Create one single continuous, unbroken {duration_seconds}-second 16:9 {shot_kind} from the supplied "
                "City Prompt control input. This is one coherent camera take—no cuts, "
                "montage, jump transitions, or time lapse."
            ),
            (
                "FLIGHT PATH: The route is supplied as normalized screen-space coordinates and described below; "
                "there is intentionally no route graphic burned into the first frame. Travel smoothly from the "
                "described start region toward the described finish region at a physically plausible speed. "
                f"{route_description} {motion_prompt}. {flight_instruction}"
            ),
            (
                "STATIC SCENE IDENTITY — HIGHEST PRIORITY: This is a camera animation of one frozen 3D scene, not "
                f"a scene redesign. {input_authority}. Preserve the exact site plan and recognizable spatial identity of the source. "
                f"{prompt_scene_brief} Keep every authored zone at the same location, footprint, height, proportions, "
                "setbacks, roofline, opening pattern, path layout, and street relationship in every frame. Each building "
                "zone is one indivisible persistent object and must never split into wings, merge with another zone, or "
                "duplicate. BUILDING SEPARATION CHECKSUM: count the disconnected building solids in the first frame and "
                "preserve that exact component count. Every open-air gap, alley, park frontage, and setback separating them "
                "must remain open from ground to sky. Never bridge, join, fuse, wrap, or extend one building toward another, "
                "and never turn separate buildings into a perimeter block. COURTYARD TOPOLOGY CHECKSUM: before generating "
                "motion, count every visible courtyard, lightwell, "
                "roof void, and wing in the first frame. Treat each void as immutable three-dimensional negative space. "
                "Preserve its exact count, perimeter, length, width, aspect ratio, separation, alignment, and position inside "
                "its building in all 192 frames. Never lengthen, widen, shrink, merge, split, fill, or invent a courtyard or "
                "roof opening. Architecture and site geometry are immutable. Do not invent a fountain, pool, monument, "
                "gazebo, roof feature, extra path, or landscape centerpiece. Internal prompt identifiers "
                "are organizational metadata only; never render any identifier as a label, callout, leader line, or text."
            ),
            (
                f"APPEARANCE LOCK — {provider.replace('_', ' ').upper()} IS THE ANIMATOR ONLY: {input_authority}. The control input already contains the final approved design and look. "
                "Animate those existing pixels; do not improve, beautify, materialize, regenerate, relight, recolor, sharpen, "
                "restyle, or add detail. Preserve the exact materials, colors, textures, facade rhythm, landscape treatment, "
                "time of day, weather, shadows, exposure, and visual medium from the source. Do not apply a photographic or "
                "artistic style. Newly revealed pixels caused by the small camera move must be conservative continuations of "
                "adjacent source surfaces, never invented architecture or landscape."
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
            (
                "CONTEXT ISOLATION — FINAL OVERRIDE: Authored-zone identity applies only inside each explicitly authored "
                "proposal silhouette; it is not global art direction. Every building, roof, lot, street, tree, and skyline "
                "element outside those authored proposal silhouettes is immutable geographic context from the City Prompt control input. Preserve "
                "each context building's exact count, footprint, height, roof form, facade style, spacing, and location. Do "
                "not propagate, repeat, clone, or extend any authored architectural archetype into the background or replace "
                "the captured neighborhood with a stylistically matching city. Any new background instance of an authored "
                "archetype is a failed result. Do not redesign or enhance any pixel. When motion or visual quality conflicts "
                f"with context fidelity, {final_preservation}."
            ),
        ]
        if section
    ).strip()
    return f"{control_prefix}\n\n{body}".strip()


def build_omni_payload(
    *,
    model: str,
    guide_base64: str,
    guide_mime_type: str,
    prompt: str,
    duration_seconds: int,
    control_mode: str = "single_frame",
    route_keyframes: Sequence[tuple[str, str]] | None = None,
    preview_video_base64: str | None = None,
    preview_video_mime_type: str | None = None,
) -> dict[str, Any]:
    if control_mode == "multi_keyframe":
        if not route_keyframes:
            raise ValueError("Multi-keyframe video generation requires route keyframes.")
        input_items: list[dict[str, Any]] = [
            {
                "type": "image",
                "data": value.split(",", 1)[1] if "," in value else value,
                "mime_type": mime_type,
            }
            for value, mime_type in route_keyframes
        ]
        task = "reference_to_video"
    elif control_mode == "preview_video":
        if not preview_video_base64 or not preview_video_mime_type:
            raise ValueError("Preview-video generation requires a deterministic route preview.")
        input_items = [{
            "type": "video",
            "data": preview_video_base64.split(",", 1)[1] if "," in preview_video_base64 else preview_video_base64,
            "mime_type": preview_video_mime_type,
        }]
        task = "edit"
    else:
        encoded = guide_base64.split(",", 1)[1] if "," in guide_base64 else guide_base64
        input_items = [{"type": "image", "data": encoded, "mime_type": guide_mime_type}]
        task = "image_to_video"
    input_items.append({"type": "text", "text": prompt})
    response_format = (
        {"type": "video"}
        if control_mode == "preview_video"
        else {
            "type": "video",
            "aspect_ratio": "16:9",
            "duration": f"{duration_seconds}s",
            "delivery": "inline",
        }
    )
    return {
        "model": model,
        "input": input_items,
        "generation_config": {"video_config": {"task": task}},
        "response_format": response_format,
        "background": False,
        "store": False,
        "stream": False,
    }


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
