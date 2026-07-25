"""Generate rectified, repeatable facade sheets for one compiled family.

The geometry generator remains responsible for massing, roofs, setbacks and
shadow-casting attachments.  This tool moves the small facade detail that is
expensive to model (window assemblies, reveals, masonry variation, shopfronts)
into a compact photographic elevation, following the same texture-atlas
strategy used by the Chicago and Kinnaird reference models.

Run after ``generate_family.py`` has produced ``grammar.json``::

    backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_facade_sheets.py \
        --family build/worldclass-v7/rndsqr

The raw provider elevation is cached. ``--provider openai`` selects GPT Image
while preserving Gemini as the default. ``--reprocess`` re-runs deterministic
band detection and texture processing without making another API call.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
sys.path.insert(0, str(TOOL_DIR))

from generate_textures import derive_roughness, flatten_lighting, load_api_key  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GEMINI_MODEL_ID = "gemini-3.1-flash-image"
OPENAI_MODEL_ID = "gpt-image-2"
OPENAI_IMAGES_EDIT_URL = "https://api.openai.com/v1/images/edits"
SHEET_BAYS = 4
ELEVATION_FLOORS = 3
PARAPET_M = 0.9
ALBEDO_WIDTH = 1024
ROUGHNESS_WIDTH = 512
EMISSIVE_WIDTH = 512
GLASS_MASK_WIDTH = 512
JPEG_QUALITY = 91
MAX_ATTEMPTS = 3

PROMPT_TEMPLATES = (
    "Architectural facade TEXTURE MAP for a professional real-time 3D model. "
    "Create a strict rectified orthographic front elevation; the flat wall surface "
    "fills 100 percent of the image. Bottom to top: one {podium_m:.1f} metre {ground}; "
    "exactly {floors} coordinated {floor_m:.1f} metre upper storeys; then a thin parapet. "
    "COUNTING CHECK: show exactly {floors} and only {floors} horizontal rows of upper-storey "
    "windows; do not add, subdivide or imply any extra storey rows. "
    "Exactly {bays} structural bays across, but preserve intentional asymmetry and signature bays. "
    "Architectural identity: {look}. NON-NEGOTIABLE identity cues: {identity}. "
    "Material zoning: {material_zones}. Do not genericize, regularize away, or substitute these cues. "
    "Preserve the reference's actual opening shapes: segmental, round or pointed arches must "
    "remain arches rather than being regularized into rectangles. Physically believable "
    "construction, precise window frames, deep reveals, lintels, "
    "sills, material joints and subtle weathering. A few windows may show softly lit, "
    "unoccupied interiors. Flat even overcast capture light. The wall reaches every edge: "
    "no sky, no pavement, no perspective, no whole-building scene, no people, no signs, "
    "no legible text, no trees and no cars.",
    "Rectified edge-to-edge facade atlas for texturing a rectangular game building. "
    "Shift-lens straight-on elevation, zero perspective. At the bottom edge place one "
    "{podium_m:.1f} metre {ground}; above it exactly {floors} coordinated {floor_m:.1f} "
    "metre floors; slim coping at the top. The upper window grid must have exactly {floors} "
    "horizontal rows, never more. {bays} structural bays wide. Style and construction: "
    "{look}. Required building-specific identity: {identity}. Material zoning: {material_zones}. "
    "Retain distinctive feature bays, deliberate asymmetry and every reference-specific curved "
    "or arched opening. Photoreal architectural materials, accurate joinery, windows, shadowed reveals, "
    "sills and restrained age variation. Uniform diffuse overcast light. Texture surface "
    "only: no sky, no ground plane, no perspective, no massing setback, no people, no writing or scenery.",
    "Seamless architectural elevation texture, wall surface edge to edge, for a modular GLB. "
    "Exactly {bays} structural bays across. Vertical arrangement: {podium_m:.1f} metre {ground} "
    "at the bottom, then {floors} coordinated {floor_m:.1f} metre typical floors, then a narrow "
    "roofline band. Count exactly {floors} upper window rows and no extras. "
    "Visual brief: {look}. Required unique composition: {identity}. "
    "Material zones: {material_zones}. Professional archviz realism, buildable details, "
    "fine window assemblies and natural material variation. Orthographic, evenly de-lit, "
    "no sky, no street, no perspective, no objects, no people and no text.",
)

GLASS_MASK_PROMPT = (
    "Create a SEMANTIC GLASS MASK for the attached rectified architectural facade elevation. "
    "This is a pixel-aligned material-selection map, not a redesigned facade. Preserve the exact "
    "camera, crop, proportions, floor lines, bays, openings and edge positions of the source image. "
    "Output pure WHITE only for transparent or translucent vision glazing: windows, glazed doors, "
    "storefront panes and curtain-wall vision glass. Output pure BLACK for every opaque material, "
    "including frames, mullions, spandrel panels, metal backpans, masonry, timber, concrete, roofs, "
    "shadows and interiors. Do not include reflections outside the physical pane boundaries. "
    "No grey shading, no labels, no legend, no border, no perspective and no artistic reinterpretation. "
    "The result must be one edge-to-edge black-and-white mask registered to the source elevation."
)

REFERENCE_SUFFIX = (
    " The attached catalogue image is a HARD DESIGN REFERENCE, not loose inspiration. "
    "Match its silhouette logic, architectural language, bay proportions, material zones, "
    "opening rhythm, signature asymmetry and colour palette. Preserve the cues that make it "
    "recognizable while converting it into the rectified texture map specified above."
)


def load_grammar(family_dir: Path) -> dict:
    path = family_dir / "grammar.json"
    if not path.exists():
        raise SystemExit(f"grammar.json not found in {family_dir}; generate the family first")
    return json.loads(path.read_text(encoding="utf-8"))


def facade_look_prose(grammar: dict) -> str:
    source = grammar.get("source") or {}
    materials = grammar.get("materials") or {}
    details = []
    for slot in ("primary", "secondary", "accent"):
        text = str((materials.get(slot) or {}).get("source_text") or "").strip().rstrip(".")
        if text and text.lower() not in {item.lower() for item in details}:
            details.append(text)
    identity = source.get("variant_label") or source.get("archetype_label") or grammar["family_id"]
    category = source.get("aesthetic_category_label") or source.get("aesthetic_category_id") or ""
    system = str((grammar.get("facade") or {}).get("system") or "").replace("_", " ")
    roof = str((grammar.get("roof") or {}).get("type") or "").replace("_", " ")
    sentence = f"{identity}; {category}; {system} facade; {roof} roof"
    if details:
        sentence += "; " + "; ".join(details)
    return sentence[:650]


def signature_prose(grammar: dict) -> tuple[str, str]:
    signature = grammar.get("architectural_signature") or {}
    identity = str(signature.get("identity") or "preserve the reference's distinctive composition and proportions")
    material_zones = str(signature.get("material_zones") or "faithful archetype-specific material hierarchy")
    return identity[:700], material_zones[:420]


def band_layout(grammar: dict) -> dict:
    dims = grammar["dimensions"]
    podium = float(dims["podium_height_m"])
    floor = float(dims["floor_height_m"])
    total = PARAPET_M + ELEVATION_FLOORS * floor + podium
    return {
        "podium_m": podium,
        "floor_m": floor,
        "parapet_f": PARAPET_M / total,
        "floor_f": floor / total,
        "podium_f": podium / total,
        "requested_span_m": SHEET_BAYS * float(grammar["facade"]["bay_width_m"]),
    }


def reference_image_path(grammar: dict) -> Path | None:
    """Resolve the exact runtime archetype card before the generic hero image.

    The catalogue exports ``generation_archetype_id`` (for example
    ``industrial_brick_mixed_use_variant_0``), while ``thumbnail_url`` points
    at the family hero. Using the hero silently trained facade sheets toward a
    different building than the comparison card shown to the user.
    """
    source = grammar.get("source") or {}
    archetype_id = str(source.get("archetype_id") or "")
    generation_id = str(source.get("generation_archetype_id") or "")
    prefix = f"{archetype_id}_"
    if archetype_id and generation_id.startswith(prefix):
        image_id = generation_id[len(prefix):]
        candidate = (
            REPO_ROOT / "frontend" / "public" / "archetypes" / "buildings"
            / archetype_id / f"{image_id}.png"
        )
        if candidate.exists():
            return candidate
    thumb = str(source.get("thumbnail_url") or "")
    candidate = REPO_ROOT / "frontend" / "public" / thumb.lstrip("/")
    return candidate if thumb and candidate.exists() else None


def reference_image(grammar: dict) -> Image.Image | None:
    candidate = reference_image_path(grammar)
    if candidate is None:
        return None
    image = Image.open(candidate).convert("RGB")
    image.thumbnail((1024, 1024))
    print(f"[facade_sheets] reference={candidate.relative_to(REPO_ROOT)}")
    return image


def _append_reference_instruction(prompt: str, reference: Image.Image | None) -> str:
    return prompt + REFERENCE_SUFFIX if reference is not None else prompt


def generate_elevation_gemini(
    client,
    prompt: str,
    reference: Image.Image | None,
    *,
    model: str = GEMINI_MODEL_ID,
) -> Image.Image:
    from google.genai import types

    contents: list = []
    if reference is not None:
        contents.append(reference)
    contents.append(_append_reference_instruction(prompt, reference))
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="9:16", image_size="2K"),
        ),
    )
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else []) or []:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                return Image.open(io.BytesIO(inline.data)).convert("RGB")
    reasons = ", ".join(str(candidate.finish_reason) for candidate in (response.candidates or []))
    raise RuntimeError(f"Gemini returned no image ({reasons})")


def generate_semantic_glass_mask_gemini(
    client,
    elevation: Image.Image,
    *,
    model: str = GEMINI_MODEL_ID,
) -> Image.Image:
    """Ask Gemini for a material-selection image registered to ``elevation``."""
    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=[elevation, GLASS_MASK_PROMPT],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="9:16", image_size="2K"),
        ),
    )
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else []) or []:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                generated = Image.open(io.BytesIO(inline.data)).convert("L")
                return normalize_semantic_glass_mask(generated, elevation.size)
    reasons = ", ".join(str(candidate.finish_reason) for candidate in (response.candidates or []))
    raise RuntimeError(f"Gemini returned no semantic glass mask ({reasons})")


def load_openai_api_key(cli_key: str | None) -> str:
    """Load an OpenAI key without ever logging it or committing it to the pilot."""
    if cli_key:
        return cli_key
    for name in ("OPENAI_API_KEY", "OPENAI"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    for env_file in (REPO_ROOT / ".env", REPO_ROOT / "backend" / ".env"):
        if not env_file.exists():
            continue
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            for name in ("OPENAI_API_KEY", "OPENAI"):
                if stripped.startswith(f"{name}="):
                    value = stripped.split("=", 1)[1].strip().strip('"').strip("'")
                    if value:
                        return value
    raise SystemExit(
        "OPENAI_API_KEY not found (environment, --api-key, .env, or backend/.env)"
    )


def _png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _openai_image_edit(
    api_key: str,
    prompt: str,
    image: Image.Image,
    *,
    model: str = OPENAI_MODEL_ID,
    size: str = "1024x1536",
) -> Image.Image:
    """Call the GPT Image edit endpoint using the compiler's existing HTTP stack."""
    import requests

    response = requests.post(
        OPENAI_IMAGES_EDIT_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        data={
            "model": model,
            "prompt": prompt,
            "n": "1",
            "size": size,
            "quality": "high",
            "output_format": "png",
        },
        files=[("image[]", ("architectural-reference.png", _png_bytes(image), "image/png"))],
        timeout=300,
    )
    if response.status_code != 200:
        detail = response.text[:500].replace(api_key, "[redacted]")
        raise RuntimeError(f"OpenAI image edit returned {response.status_code}: {detail}")
    payload = response.json()
    data = payload.get("data") or []
    encoded = data[0].get("b64_json") if data else None
    if not encoded:
        raise RuntimeError("OpenAI image edit returned no b64_json image")
    return Image.open(io.BytesIO(base64.b64decode(encoded))).convert("RGB")


def generate_elevation_openai(
    api_key: str,
    prompt: str,
    reference: Image.Image | None,
    *,
    model: str = OPENAI_MODEL_ID,
) -> Image.Image:
    has_reference = reference is not None
    if reference is None:
        # The edit endpoint is deliberately used so GPT Image receives the same
        # archetype goalpost as Gemini. A neutral canvas keeps the API contract
        # usable for catalogue entries that do not yet have a card image.
        reference = Image.new("RGB", (1024, 1536), (224, 224, 220))
    return _openai_image_edit(
        api_key,
        _append_reference_instruction(prompt, reference if has_reference else None),
        reference,
        model=model,
    )


def generate_semantic_glass_mask_openai(
    api_key: str,
    elevation: Image.Image,
    *,
    model: str = OPENAI_MODEL_ID,
) -> Image.Image:
    generated = _openai_image_edit(
        api_key,
        GLASS_MASK_PROMPT,
        elevation,
        model=model,
        size=f"{elevation.width}x{elevation.height}",
    )
    return normalize_semantic_glass_mask(generated.convert("L"), elevation.size)


def _otsu_threshold(array: np.ndarray) -> int:
    histogram = np.bincount(array.reshape(-1), minlength=256).astype(np.float64)
    total = array.size
    weighted_total = float(np.dot(np.arange(256), histogram))
    background_weight = 0.0
    background_sum = 0.0
    best_variance = -1.0
    best_threshold = 127
    for threshold in range(256):
        background_weight += histogram[threshold]
        if background_weight <= 0:
            continue
        foreground_weight = total - background_weight
        if foreground_weight <= 0:
            break
        background_sum += threshold * histogram[threshold]
        background_mean = background_sum / background_weight
        foreground_mean = (weighted_total - background_sum) / foreground_weight
        variance = background_weight * foreground_weight * (background_mean - foreground_mean) ** 2
        if variance > best_variance:
            best_variance = variance
            best_threshold = threshold
    return best_threshold


def normalize_semantic_glass_mask(mask: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Resize, binarize and remove image-model speckle while keeping pane edges crisp."""
    resized = ImageOps.fit(mask.convert("L"), target_size, method=Image.Resampling.LANCZOS)
    array = np.asarray(resized, dtype=np.uint8)
    threshold = _otsu_threshold(array)
    binary = (array > threshold).astype(np.uint8) * 255
    # A mask covering most of the elevation usually means the model inverted
    # the requested convention. Vision glass is rarely >65% of these pilots.
    if float(binary.mean()) / 255.0 > 0.65:
        binary = 255 - binary
    result = Image.fromarray(binary, mode="L")
    result = result.filter(ImageFilter.MedianFilter(5))
    result = result.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    return result.point(lambda value: 255 if value >= 128 else 0, mode="L")


def _component_boxes(binary: np.ndarray) -> list[tuple[int, int, int, int, int]]:
    """Connected-component boxes using scanline runs (no OpenCV dependency)."""
    height, width = binary.shape
    parent: list[int] = []
    runs: list[tuple[int, int, int, int]] = []
    previous: list[tuple[int, int, int]] = []

    def make_label() -> int:
        label = len(parent)
        parent.append(label)
        return label

    def find(label: int) -> int:
        while parent[label] != label:
            parent[label] = parent[parent[label]]
            label = parent[label]
        return label

    def union(first: int, second: int) -> int:
        a, b = find(first), find(second)
        if a != b:
            parent[b] = a
        return a

    for y in range(height):
        row = binary[y]
        padded = np.pad(row.astype(np.int8), (1, 1))
        transitions = np.diff(padded)
        starts = np.flatnonzero(transitions == 1)
        stops = np.flatnonzero(transitions == -1) - 1
        current: list[tuple[int, int, int]] = []
        previous_index = 0
        for x0, x1 in zip(starts.tolist(), stops.tolist()):
            while previous_index < len(previous) and previous[previous_index][1] < x0 - 1:
                previous_index += 1
            overlaps: list[int] = []
            cursor = previous_index
            while cursor < len(previous) and previous[cursor][0] <= x1 + 1:
                overlaps.append(previous[cursor][2])
                cursor += 1
            label = find(overlaps[0]) if overlaps else make_label()
            for other in overlaps[1:]:
                label = union(label, other)
            current.append((x0, x1, label))
            runs.append((y, x0, x1, label))
        previous = current

    stats: dict[int, list[int]] = {}
    for y, x0, x1, label in runs:
        root = find(label)
        if root not in stats:
            stats[root] = [x0, y, x1 + 1, y + 1, x1 - x0 + 1]
        else:
            box = stats[root]
            box[0] = min(box[0], x0)
            box[1] = min(box[1], y)
            box[2] = max(box[2], x1 + 1)
            box[3] = max(box[3], y + 1)
            box[4] += x1 - x0 + 1
    return [tuple(box) for box in stats.values()]


def _merge_opening_boxes(boxes: list[list[float]]) -> list[list[float]]:
    """Merge pane components into architectural window/opening groups."""
    merged = [box[:] for box in boxes]
    changed = True
    while changed:
        changed = False
        output: list[list[float]] = []
        while merged:
            current = merged.pop()
            index = 0
            while index < len(merged):
                other = merged[index]
                x_overlap = max(0.0, min(current[2], other[2]) - max(current[0], other[0]))
                y_overlap = max(0.0, min(current[3], other[3]) - max(current[1], other[1]))
                min_width = min(current[2] - current[0], other[2] - other[0])
                min_height = min(current[3] - current[1], other[3] - other[1])
                x_gap = max(0.0, max(current[0], other[0]) - min(current[2], other[2]))
                y_gap = max(0.0, max(current[1], other[1]) - min(current[3], other[3]))
                same_row = y_overlap >= min_height * 0.62 and x_gap <= 0.016
                # Steel sash and residential windows often have a thicker
                # horizontal meeting rail than their vertical glazing bars.
                # The former 1.6% cutoff split one architectural opening into
                # upper/lower boxes, which then produced two projecting 3D
                # surrounds over a single window in City Prompt.  Merge pane
                # rows across a bounded, height-relative rail gap while still
                # keeping genuinely separate storeys apart.
                column_gap_limit = min(0.030, max(0.016, min_height * 0.22))
                same_column = x_overlap >= min_width * 0.62 and y_gap <= column_gap_limit
                if same_row or same_column:
                    current = [
                        min(current[0], other[0]), min(current[1], other[1]),
                        max(current[2], other[2]), max(current[3], other[3]),
                    ]
                    merged.pop(index)
                    changed = True
                else:
                    index += 1
            output.append(current)
        merged = output
    return sorted(merged, key=lambda box: (box[1], box[0]))


def extract_glass_regions(mask: Image.Image, *, max_regions: int = 96) -> list[list[float]]:
    """Return normalized window-group bounds for aligned 3D frame generation."""
    sample_width = min(384, mask.width)
    sample_height = max(32, round(mask.height * sample_width / mask.width))
    sample = mask.convert("L").resize((sample_width, sample_height), Image.Resampling.NEAREST)
    binary = np.asarray(sample, dtype=np.uint8) >= 128
    boxes: list[list[float]] = []
    for x0, y0, x1, y1, area in _component_boxes(binary):
        width, height = x1 - x0, y1 - y0
        bbox_area = width * height
        if area < sample_width * sample_height * 0.00018:
            continue
        if width < max(2, sample_width * 0.006) or height < max(2, sample_height * 0.006):
            continue
        if area / max(1, bbox_area) < 0.28:
            continue
        boxes.append([x0 / sample_width, y0 / sample_height, x1 / sample_width, y1 / sample_height])
    merged = _merge_opening_boxes(boxes)
    merged.sort(key=lambda box: (box[2] - box[0]) * (box[3] - box[1]), reverse=True)
    selected = merged[:max_regions]
    selected.sort(key=lambda box: (box[1], box[0]))
    return [[round(value, 5) for value in box] for box in selected]


def derive_glass_mask_fallback(albedo: Image.Image) -> Image.Image:
    """Conservative deterministic fallback when a semantic API call is unavailable."""
    rgb = np.asarray(albedo.convert("RGB"), dtype=np.float32) / 255.0
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    saturation = maximum - minimum
    # Curtain-wall elevations can be almost entirely cool blue-grey glass. A
    # broad neutral test mistakes the similarly bright aluminium frame for
    # glass and is then inverted by mask normalization. Detect that family
    # first through blue/cyan dominance, keeping neutral mullions out.
    cool_score = (rgb[:, :, 2] - rgb[:, :, 0]) + 0.35 * (rgb[:, :, 1] - rgb[:, :, 0])
    curtain_glass = (
        (cool_score > 0.05)
        & (maximum > 0.08)
        & (maximum < 0.90)
        & (saturation > 0.018)
        & (saturation < 0.38)
    )
    cool_or_neutral = (rgb[:, :, 2] >= rgb[:, :, 0] * 0.90) & (rgb[:, :, 1] >= rgb[:, :, 0] * 0.82)
    plausible_value = (maximum > 0.10) & (maximum < 0.84)
    restrained_colour = saturation < 0.34
    general_glass = cool_or_neutral & plausible_value & restrained_colour
    # GPT Image frequently authors clear, warm-neutral loft/residential glazing
    # with visible lit interiors instead of blue reflections. Those panes are
    # deliberately low-chroma; thin similarly neutral mortar lines disappear
    # in the median/open-close cleanup below.
    warm_clear_glass = (
        (maximum > 0.16)
        & (maximum < 0.86)
        & (saturation < 0.18)
        & (rgb[:, :, 0] <= rgb[:, :, 2] + 0.14)
    )
    if float(curtain_glass.mean()) > 0.40:
        binary_source = curtain_glass
    elif float(warm_clear_glass.mean()) > 0.08:
        binary_source = general_glass | warm_clear_glass
    else:
        binary_source = general_glass
    binary = binary_source.astype(np.uint8) * 255
    result = Image.fromarray(binary, mode="L").filter(ImageFilter.MedianFilter(7))
    result = result.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(5))
    return result.point(lambda value: 255 if value >= 128 else 0, mode="L")


def _row_variance_profile(image: Image.Image) -> np.ndarray:
    grey = np.asarray(image.convert("L"), dtype=np.float64)
    profile = grey.var(axis=1)
    width = max(3, image.height // 200)
    return np.convolve(profile, np.ones(width) / width, mode="same")


def detect_floor_band(
    elevation: Image.Image,
    fallback_top: float,
    fallback_bottom: float,
    expected_fraction: float,
) -> tuple[float, float, str]:
    height = elevation.height
    profile = _row_variance_profile(elevation)
    body = profile[int(0.07 * height): int(0.76 * height)]
    body = body - body.mean()
    if body.std() < 1e-6:
        return fallback_top, fallback_bottom, "fallback-flat"
    autocorrelation = np.correlate(body, body, mode="full")[body.size - 1:]
    low = max(8, int(0.5 * expected_fraction * height))
    high = min(body.size - 1, int(1.85 * expected_fraction * height))
    if high <= low + 4:
        return fallback_top, fallback_bottom, "fallback-range"
    lag = low + int(np.argmax(autocorrelation[low:high]))
    confidence = float(autocorrelation[lag] / (autocorrelation[0] + 1e-9))
    if confidence < 0.24:
        return fallback_top, fallback_bottom, f"fallback-confidence-{confidence:.2f}"
    midpoint = int(0.40 * height)
    start = max(0, midpoint - lag // 2)
    stop = min(height, midpoint + lag // 2)
    anchor = start + int(np.argmin(profile[start:stop]))
    top, bottom = anchor / height, (anchor + lag) / height
    if bottom > 0.88:
        top, bottom = top - lag / height, top
    return top, bottom, f"autocorrelation-{lag}px-{confidence:.2f}"


def detect_podium_band(
    elevation: Image.Image,
    lowest_floor_bottom: float,
    fallback_top: float,
) -> tuple[float, float, str]:
    height = elevation.height
    grey = np.asarray(elevation.convert("L"), dtype=np.float64)
    luminance = grey.mean(axis=1)
    median = float(np.median(luminance[int(0.15 * height): int(0.75 * height)]))
    bottom = height - 1
    for y in range(height - 1, int(0.80 * height), -1):
        if luminance[y] <= median * 1.35:
            bottom = y
            break
    top = max(int(lowest_floor_bottom * height), int(fallback_top * height))
    if bottom - top < height * 0.05:
        return fallback_top, 1.0, "fallback-thin"
    return top / height, bottom / height, f"pavement-cut-{bottom}px"


def select_crown_bottom(
    grammar: dict,
    *,
    floor_top: float,
    floor_bottom: float,
    period: float,
    podium_top: float,
    layout: dict,
) -> float:
    """Choose a semantic crown crop for conventional crowns and pavilions."""
    if bool((grammar.get("massing") or {}).get("rooftop_pavilion")):
        # The first complete masonry floor begins one detected period above
        # floor_top. Everything above that datum is zinc/glass/terrace and must
        # remain a single pavilion band rather than a compressed brick stack.
        return min(podium_top, max(0.12, floor_top - period))
    # Autocorrelation often locks onto the middle storey of a three-storey
    # industrial elevation.  In that case one complete period still exists
    # above ``floor_top`` and the crown must stop at that datum; using
    # ``floor_bottom`` would bake both the top and middle storeys into a single
    # crown module and squash its windows when the LEGO stack scales it to one
    # floor.  Two-storey elevations have no complete period above, so their
    # upper storey correctly remains part of the fixed crown.
    has_complete_storey_above = (
        floor_top - period >= max(0.04, layout["parapet_f"] * 0.72)
    )
    storey_bottom = floor_top if has_complete_storey_above else floor_bottom
    return min(
        podium_top,
        max(storey_bottom, layout["parapet_f"] + layout["floor_f"] * 1.08),
    )


def slice_band(elevation: Image.Image, top: float, bottom: float) -> Image.Image:
    trim = 0.012 * (bottom - top)
    y0 = max(0, int(round((top + trim) * elevation.height)))
    y1 = min(elevation.height, int(round((bottom - trim) * elevation.height)))
    return elevation.crop((0, y0, elevation.width, max(y0 + 8, y1)))


def select_repeatable_side_bay(
    band: Image.Image,
    glass_mask_band: Image.Image,
) -> tuple[Image.Image, Image.Image, tuple[float, float]]:
    """Extract one clean glazed bay for secondary elevations.

    Front elevations often contain fixed identity objects—signs, entrances,
    fire escapes and pavilions—that must not wrap around every side. The
    rightmost actual glazing region is a dependable clean-bay anchor: signs are
    opaque, centre entrances sit away from it, and fire escapes normally occupy
    a middle circulation bay. The crop includes adjacent masonry returns and is
    made tileable later by ``process_band``.
    """
    regions = extract_glass_regions(glass_mask_band)
    usable = [region for region in regions if region[2] - region[0] >= 0.035]
    if usable:
        ordered = sorted(usable, key=lambda region: (region[0] + region[2]) / 2)
        target = ordered[-1]
        centre = (target[0] + target[2]) / 2
        opening_width = target[2] - target[0]
        centres = [(region[0] + region[2]) / 2 for region in ordered]
        spacings = [b - a for a, b in zip(centres, centres[1:]) if b - a > 0.04]
        typical_spacing = float(np.median(spacings)) if spacings else opening_width * 1.45
        crop_width = min(0.34, max(0.15, opening_width * 1.30, typical_spacing * 0.90))
    else:
        centre, crop_width = 0.25, 0.24
    left = max(0.0, min(1.0 - crop_width, centre - crop_width / 2))
    right = min(1.0, left + crop_width)
    x0 = int(round(left * band.width))
    x1 = max(x0 + 8, int(round(right * band.width)))
    return (
        band.crop((x0, 0, min(band.width, x1), band.height)),
        glass_mask_band.crop((x0, 0, min(glass_mask_band.width, x1), glass_mask_band.height)),
        (left, right),
    )


def accent_roll_offset(band: Image.Image) -> int:
    array = np.asarray(band.convert("RGB"), dtype=np.int16)
    saturation = (array.max(axis=2) - array.min(axis=2)).mean(axis=0)
    kernel_width = max(8, band.width // 16)
    smooth = np.convolve(saturation, np.ones(kernel_width) / kernel_width, mode="same")
    peak = int(np.argmax(smooth))
    if smooth[peak] < smooth.mean() * 1.45:
        return 0
    return int(0.61 * band.width) - peak


def roll_image(image: Image.Image, offset: int) -> Image.Image:
    if not offset:
        return image
    return Image.fromarray(np.roll(np.asarray(image), offset, axis=1))


def roll_accent_off_seam(band: Image.Image) -> Image.Image:
    return roll_image(band, accent_roll_offset(band))


def make_horizontally_tileable(image: Image.Image, feather: float = 0.07) -> Image.Image:
    array = np.asarray(image, dtype=np.float64)
    rolled = np.roll(array, image.width // 2, axis=1)
    index = np.arange(image.width)
    distance = np.minimum(index, image.width - 1 - index) / max(1.0, feather * image.width)
    weight = np.clip(distance, 0.0, 1.0)
    weight = (weight * weight * (3 - 2 * weight))[None, :, None]
    return Image.fromarray(np.clip(weight * array + (1 - weight) * rolled, 0, 255).astype(np.uint8))


def derive_emissive_mask(albedo: Image.Image) -> Image.Image:
    """Conservative warm-window mask; black everywhere except plausible lit glass."""
    rgb = np.asarray(albedo.convert("RGB"), dtype=np.float32) / 255.0
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    warm = (rgb[:, :, 0] > rgb[:, :, 2] * 1.14) & (rgb[:, :, 1] > rgb[:, :, 2] * 1.04)
    saturated = (maximum - minimum) > 0.07
    midbright = (maximum > 0.34) & (maximum < 0.93)
    mask = (warm & saturated & midbright).astype(np.uint8) * 255
    result = Image.fromarray(mask, mode="L").filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.1))
    return ImageEnhance.Contrast(result).enhance(1.35)


def _prepare_binary_mask(mask: Image.Image, offset: int) -> Image.Image:
    rolled = roll_image(mask.convert("L"), offset)
    tileable = make_horizontally_tileable(rolled.convert("RGB")).convert("L")
    return tileable.point(lambda value: 255 if value >= 128 else 0, mode="L")


def process_band(
    name: str,
    band: Image.Image,
    glass_mask_band: Image.Image,
    out_dir: Path,
    roughness_anchor: float,
) -> dict:
    offset = accent_roll_offset(band)
    prepared = make_horizontally_tileable(flatten_lighting(roll_image(band, offset)))
    prepared_glass = _prepare_binary_mask(glass_mask_band, offset)
    target_height = max(64, round(ALBEDO_WIDTH * prepared.height / prepared.width))
    albedo = prepared.resize((ALBEDO_WIDTH, target_height), Image.Resampling.LANCZOS)
    roughness = derive_roughness(albedo, roughness_anchor).resize(
        (ROUGHNESS_WIDTH, max(32, round(ROUGHNESS_WIDTH * target_height / ALBEDO_WIDTH))),
        Image.Resampling.LANCZOS,
    )
    emissive = derive_emissive_mask(albedo).resize(
        (EMISSIVE_WIDTH, max(32, round(EMISSIVE_WIDTH * target_height / ALBEDO_WIDTH))),
        Image.Resampling.LANCZOS,
    )
    glass_height = max(32, round(GLASS_MASK_WIDTH * target_height / ALBEDO_WIDTH))
    glass_mask = prepared_glass.resize(
        (GLASS_MASK_WIDTH, glass_height), Image.Resampling.NEAREST,
    ).point(lambda value: 255 if value >= 128 else 0, mode="L")
    opaque_mask = ImageOps.invert(glass_mask)
    albedo_file = f"{name}_albedo.jpg"
    roughness_file = f"{name}_roughness.jpg"
    emissive_file = f"{name}_emissive.png"
    glass_mask_file = f"{name}_glass.png"
    opaque_mask_file = f"{name}_opaque.png"
    albedo.save(out_dir / albedo_file, quality=JPEG_QUALITY, subsampling=0)
    roughness.convert("L").save(out_dir / roughness_file, quality=88)
    emissive.save(out_dir / emissive_file, optimize=True)
    glass_mask.save(out_dir / glass_mask_file, optimize=True)
    opaque_mask.save(out_dir / opaque_mask_file, optimize=True)
    return {
        "albedo": albedo_file,
        "roughness": roughness_file,
        "emissive": emissive_file,
        "glass_mask": glass_mask_file,
        "opaque_mask": opaque_mask_file,
        "glass_regions": extract_glass_regions(glass_mask),
        "px": [albedo.width, albedo.height],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate facade sheets for one modular family")
    parser.add_argument("--family", required=True, type=Path, help="directory containing grammar.json")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--provider", choices=("gemini", "openai"), default="gemini",
                        help="image provider; OpenAI uses GPT Image with the same archetype reference")
    parser.add_argument("--model", default=None,
                        help="provider model override (defaults to Gemini 3.1 Flash Image or GPT Image 2)")
    parser.add_argument("--api-key", default=None,
                        help="temporary provider key override; prefer GEMINI_API_KEY/OPENAI_API_KEY")
    parser.add_argument(
        "--mask-provider",
        choices=("same", "gemini", "openai", "deterministic"),
        default="same",
        help="semantic glazing provider; 'same' follows --provider",
    )
    parser.add_argument("--force", action="store_true", help="regenerate the cached raw elevation")
    parser.add_argument("--force-mask", action="store_true", help="regenerate only the cached semantic glass mask")
    parser.add_argument("--skip-semantic-glass", action="store_true",
                        help="derive a conservative local mask instead of calling an image provider")
    parser.add_argument(
        "--registered-opening-schedule",
        type=Path,
        help=(
            "normalized audited opening schedule; rasterizes an exact semantic glass mask "
            "instead of asking an image model to reinterpret the elevation"
        ),
    )
    parser.add_argument(
        "--registered-band-schedule",
        type=Path,
        help=(
            "audited normalized vertical crops for floor, floor_alt, crown and podium, "
            "plus an optional horizontal side-bay crop"
        ),
    )
    parser.add_argument("--reprocess", action="store_true", help="reuse cached elevation; no API call")
    args = parser.parse_args()

    family_dir = args.family.resolve()
    grammar = load_grammar(family_dir)
    family = grammar["family_id"]
    default_root = "facade_sheets" if args.provider == "gemini" else "facade_sheets_openai"
    out_dir = (args.out or TOOL_DIR / default_root / family).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "elevation_raw.jpg"
    raw_glass_mask_path = out_dir / "glass_mask_raw.png"
    raw_opaque_mask_path = out_dir / "opaque_mask_raw.png"
    layout = band_layout(grammar)
    look = facade_look_prose(grammar)
    identity, material_zones = signature_prose(grammar)
    prompt_used = "(cached raw)"
    gemini = None
    openai_key = None
    elevation_model = args.model or (
        GEMINI_MODEL_ID if args.provider == "gemini" else OPENAI_MODEL_ID
    )
    mask_provider = args.provider if args.mask_provider == "same" else args.mask_provider
    semantic_model = (
        (args.model if args.provider == "openai" and args.model else OPENAI_MODEL_ID)
        if mask_provider == "openai"
        else (args.model if args.provider == "gemini" and args.model else GEMINI_MODEL_ID)
        if mask_provider == "gemini"
        else None
    )

    def gemini_client():
        nonlocal gemini
        if gemini is None:
            from google import genai
            key_override = args.api_key if args.provider == "gemini" else None
            gemini = genai.Client(api_key=load_api_key(key_override))
        return gemini

    def openai_api_key():
        nonlocal openai_key
        if openai_key is None:
            key_override = args.api_key if args.provider == "openai" else None
            openai_key = load_openai_api_key(key_override)
        return openai_key

    print(f"[facade_sheets] family={family} look={look[:110]!r}")

    if args.reprocess:
        if not raw_path.exists():
            raise SystemExit(f"--reprocess requested but {raw_path} is missing")
        elevation = Image.open(raw_path).convert("RGB")
        prompt_used = "(reprocess)"
    elif raw_path.exists() and not args.force:
        elevation = Image.open(raw_path).convert("RGB")
        print(f"[facade_sheets] reusing {raw_path.name}; pass --force to regenerate")
    else:
        reference = reference_image(grammar)
        elevation = None
        last_error: Exception | None = None
        retail = bool((grammar.get("massing") or {}).get("has_podium_retail"))
        ground = (
            "commercial ground floor with detailed glazed storefronts and a main entrance"
            if retail else
            "taller ground floor with a clearly detailed main entrance and larger windows"
        )
        for attempt in range(MAX_ATTEMPTS):
            prompt_used = PROMPT_TEMPLATES[attempt % len(PROMPT_TEMPLATES)].format(
                podium_m=layout["podium_m"],
                ground=ground,
                floors=ELEVATION_FLOORS,
                floor_m=layout["floor_m"],
                bays=SHEET_BAYS,
                look=look,
                identity=identity,
                material_zones=material_zones,
            )
            try:
                if args.provider == "openai":
                    elevation = generate_elevation_openai(
                        openai_api_key(), prompt_used, reference, model=elevation_model,
                    )
                else:
                    elevation = generate_elevation_gemini(
                        gemini_client(), prompt_used, reference, model=elevation_model,
                    )
                break
            except Exception as exc:
                last_error = exc
                print(f"[facade_sheets] attempt {attempt + 1} failed: {exc}")
                time.sleep(0.8)
        if elevation is None:
            raise SystemExit(f"all {args.provider} attempts failed: {last_error}")
        elevation.save(raw_path, quality=93, subsampling=0)
        print(f"[facade_sheets] saved {raw_path.name} {elevation.width}x{elevation.height}")

    glass_mask_source = f"{mask_provider}-semantic"
    should_reuse_mask = raw_glass_mask_path.exists() and not args.force and not args.force_mask
    if args.registered_opening_schedule:
        from create_registered_opening_mask import build_mask

        schedule_path = args.registered_opening_schedule.resolve()
        schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
        glass_mask = build_mask(raw_path, schedule)
        glass_mask_source = "registered-opening-schedule"
        print(
            f"[facade_sheets] semantic glass from {schedule_path.name}; "
            f"openings={len(schedule.get('openings', []))}"
        )
    elif should_reuse_mask:
        glass_mask = normalize_semantic_glass_mask(Image.open(raw_glass_mask_path), elevation.size)
        print(f"[facade_sheets] reusing {raw_glass_mask_path.name}")
    elif args.reprocess or args.skip_semantic_glass or mask_provider == "deterministic":
        glass_mask = derive_glass_mask_fallback(elevation)
        glass_mask_source = "deterministic-fallback"
        print("[facade_sheets] semantic glass API skipped; using deterministic fallback")
    else:
        try:
            if mask_provider == "openai":
                glass_mask = generate_semantic_glass_mask_openai(
                    openai_api_key(), elevation, model=semantic_model or OPENAI_MODEL_ID,
                )
            else:
                glass_mask = generate_semantic_glass_mask_gemini(
                    gemini_client(), elevation, model=semantic_model or GEMINI_MODEL_ID,
                )
        except Exception as exc:
            print(f"[facade_sheets] semantic glass mask failed ({exc}); using deterministic fallback")
            glass_mask = derive_glass_mask_fallback(elevation)
            glass_mask_source = "deterministic-fallback"
    glass_mask = normalize_semantic_glass_mask(glass_mask, elevation.size)
    opaque_mask = ImageOps.invert(glass_mask)
    glass_mask.save(raw_glass_mask_path, optimize=True)
    opaque_mask.save(raw_opaque_mask_path, optimize=True)
    coverage = float(np.asarray(glass_mask, dtype=np.float32).mean() / 255.0)
    full_glass_regions = extract_glass_regions(glass_mask)
    print(
        f"[facade_sheets] glass mask={glass_mask_source}; coverage={coverage:.1%}; "
        f"opening groups={len(full_glass_regions)}"
    )

    band_schedule = None
    if args.registered_band_schedule:
        schedule_path = args.registered_band_schedule.resolve()
        band_schedule = json.loads(schedule_path.read_text(encoding="utf-8"))

        def scheduled_y(name: str, fallback: str | None = None) -> tuple[float, float]:
            payload = band_schedule.get(name)
            if payload is None and fallback:
                payload = band_schedule[fallback]
            values = payload.get("y") if isinstance(payload, dict) else payload
            return tuple(float(value) for value in values)

        floor_top, floor_bottom = scheduled_y("floor")
        alt_top, alt_bottom = scheduled_y("floor_alt", "floor")
        crown_top, crown_bottom = scheduled_y("crown")
        podium_top, podium_bottom = scheduled_y("podium")
        floor_method = f"registered:{schedule_path.name}"
        podium_method = floor_method
        period = floor_bottom - floor_top
    else:
        first_floor_top = layout["parapet_f"] + layout["floor_f"]
        first_floor_bottom = first_floor_top + layout["floor_f"]
        requested_podium_top = layout["parapet_f"] + ELEVATION_FLOORS * layout["floor_f"]
        floor_top, floor_bottom, floor_method = detect_floor_band(
            elevation, first_floor_top, first_floor_bottom, layout["floor_f"]
        )
        period = floor_bottom - floor_top
        lowest_top = floor_top
        while lowest_top + 2 * period < 0.86:
            lowest_top += period
        podium_top, podium_bottom, podium_method = detect_podium_band(
            elevation, lowest_top + period, requested_podium_top
        )
        alt_top = floor_top - period
        if alt_top < layout["parapet_f"] * 0.72:
            alt_top = floor_top + period
        alt_bottom = min(podium_top, alt_top + period)
        if alt_bottom - alt_top < period * 0.72:
            alt_top, alt_bottom = floor_top, floor_bottom
        crown_top = 0.0
        crown_bottom = select_crown_bottom(
            grammar,
            floor_top=floor_top,
            floor_bottom=floor_bottom,
            period=period,
            podium_top=podium_top,
            layout=layout,
        )
    print(f"[facade_sheets] floor={floor_top:.3f}:{floor_bottom:.3f} ({floor_method})")
    print(f"[facade_sheets] podium={podium_top:.3f}:{podium_bottom:.3f} ({podium_method})")

    floor_band = slice_band(elevation, floor_top, floor_bottom)
    floor_glass = slice_band(glass_mask, floor_top, floor_bottom)
    floor_alt_band = slice_band(elevation, alt_top, alt_bottom)
    floor_alt_glass = slice_band(glass_mask, alt_top, alt_bottom)
    crown_band = slice_band(elevation, crown_top, crown_bottom)
    crown_glass = slice_band(glass_mask, crown_top, crown_bottom)
    podium_band = slice_band(elevation, podium_top, podium_bottom)
    podium_glass = slice_band(glass_mask, podium_top, podium_bottom)

    def registered_x_crop(image: Image.Image, name: str) -> Image.Image:
        if not band_schedule:
            return image
        payload = band_schedule.get(name)
        if not isinstance(payload, dict) or not payload.get("x"):
            return image
        x0, x1 = [float(value) for value in payload["x"]]
        left = max(0, min(image.width - 1, round(x0 * image.width)))
        right = max(left + 1, min(image.width, round(x1 * image.width)))
        return image.crop((left, 0, right, image.height))

    floor_band = registered_x_crop(floor_band, "floor")
    floor_glass = registered_x_crop(floor_glass, "floor")
    floor_alt_band = registered_x_crop(floor_alt_band, "floor_alt")
    floor_alt_glass = registered_x_crop(floor_alt_glass, "floor_alt")
    crown_band = registered_x_crop(crown_band, "crown")
    crown_glass = registered_x_crop(crown_glass, "crown")
    podium_band = registered_x_crop(podium_band, "podium")
    podium_glass = registered_x_crop(podium_glass, "podium")

    # Landmark elevations often contain one fixed identity object (a gate
    # tower, civic portico, corner pavilion, etc.) surrounded by repeatable
    # wings.  The floor bands still need the complete source image, while the
    # massing graph's fixed facade skin needs only that identity object.  An
    # optional ``elevation`` crop in the registered band schedule preserves
    # both uses without asking the image model for two inconsistent renders.
    identity_elevation = elevation
    identity_glass = glass_mask
    identity_crop = None
    if band_schedule and isinstance(band_schedule.get("elevation"), dict):
        identity_spec = band_schedule["elevation"]
        x0, x1 = [float(value) for value in identity_spec.get("x", (0.0, 1.0))]
        y0, y1 = [float(value) for value in identity_spec.get("y", (0.0, 1.0))]
        left = max(0, min(elevation.width - 1, round(x0 * elevation.width)))
        right = max(left + 1, min(elevation.width, round(x1 * elevation.width)))
        top = max(0, min(elevation.height - 1, round(y0 * elevation.height)))
        bottom = max(top + 1, min(elevation.height, round(y1 * elevation.height)))
        identity_elevation = elevation.crop((left, top, right, bottom))
        identity_glass = glass_mask.crop((left, top, right, bottom))
        identity_crop = [x0, y0, x1, y1]
        identity_elevation.save(out_dir / "elevation_identity.jpg", quality=93, subsampling=0)
        identity_glass.save(out_dir / "semantic_glass_identity.png", compress_level=7)
        ImageOps.invert(identity_glass).save(
            out_dir / "semantic_opaque_identity.png", compress_level=7,
        )
    if band_schedule and isinstance(band_schedule.get("side"), dict):
        side_spec = band_schedule["side"]
        side_source_band = floor_alt_band if side_spec.get("source") == "floor_alt" else floor_band
        side_source_glass = floor_alt_glass if side_spec.get("source") == "floor_alt" else floor_glass
        side_x0, side_x1 = [float(value) for value in side_spec["x"]]
        crop_left = max(0, min(side_source_band.width - 1, round(side_x0 * side_source_band.width)))
        crop_right = max(crop_left + 1, min(side_source_band.width, round(side_x1 * side_source_band.width)))
        side_band = side_source_band.crop((crop_left, 0, crop_right, side_source_band.height))
        side_glass = side_source_glass.crop((crop_left, 0, crop_right, side_source_glass.height))
        side_crop = (side_x0, side_x1)
    else:
        side_band, side_glass, side_crop = select_repeatable_side_bay(floor_band, floor_glass)
    bands = {
        "floor": process_band("floor", floor_band, floor_glass, out_dir, 0.52),
        "floor_alt": process_band("floor_alt", floor_alt_band, floor_alt_glass, out_dir, 0.52),
        "side": process_band("side", side_band, side_glass, out_dir, 0.54),
        "crown": process_band("crown", crown_band, crown_glass, out_dir, 0.50),
        "podium": process_band("podium", podium_band, podium_glass, out_dir, 0.40),
    }
    span_m = layout["floor_m"] * floor_band.width / max(1, floor_band.height)
    manifest = {
        "schema": "facade-sheet@4",
        "family": family,
        "archetype_id": (grammar.get("source") or {}).get("archetype_id"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider,
        "model": elevation_model,
        "prompt": prompt_used,
        "style_reference": (grammar.get("source") or {}).get("thumbnail_url"),
        "architectural_signature": grammar.get("architectural_signature"),
        "span_m": round(span_m, 2),
        "requested_span_m": round(layout["requested_span_m"], 2),
        "sheet_bays": SHEET_BAYS,
        "elevation_source": (
            "elevation_identity.jpg" if identity_crop else raw_path.name
        ),
        "semantic_glass": {
            "source": glass_mask_source,
            "provider": "deterministic" if args.registered_opening_schedule else mask_provider,
            "model": None if args.registered_opening_schedule else semantic_model,
            "prompt": None if args.registered_opening_schedule else GLASS_MASK_PROMPT,
            "opening_schedule": (
                args.registered_opening_schedule.name if args.registered_opening_schedule else None
            ),
            "glass_mask": (
                "semantic_glass_identity.png" if identity_crop else raw_glass_mask_path.name
            ),
            "opaque_mask": (
                "semantic_opaque_identity.png" if identity_crop else raw_opaque_mask_path.name
            ),
            "coverage": round(
                float(np.asarray(identity_glass, dtype=np.float32).mean() / 255.0), 5,
            ),
            "glass_regions": extract_glass_regions(identity_glass),
            "full_source_glass_mask": raw_glass_mask_path.name if identity_crop else None,
            "full_source_opaque_mask": raw_opaque_mask_path.name if identity_crop else None,
            "identity_crop_normalized": identity_crop,
        },
        "registered_band_schedule": (
            args.registered_band_schedule.name if args.registered_band_schedule else None
        ),
        "bands": {
            "floor": {**bands["floor"], "height_m": layout["floor_m"]},
            "floor_alt": {**bands["floor_alt"], "height_m": layout["floor_m"]},
            "side": {
                **bands["side"],
                "height_m": layout["floor_m"],
                "span_m": round(layout["floor_m"] * side_band.width / max(1, side_band.height), 2),
            },
            "crown": {**bands["crown"], "height_m": layout["floor_m"]},
            "podium": {**bands["podium"], "height_m": layout["podium_m"]},
        },
        "detection": {
            "floor": floor_method,
            "floor_alt": [round(alt_top, 4), round(alt_bottom, 4)],
            "side": [round(side_crop[0], 4), round(side_crop[1], 4)],
            "crown": [0.0, round(crown_bottom, 4)],
            "podium": podium_method,
        },
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[facade_sheets] span={span_m:.2f}m; wrote {manifest_path}")
    print(str(out_dir))


if __name__ == "__main__":
    main()
