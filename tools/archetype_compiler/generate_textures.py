"""Generate the tileable PBR texture library for the archetype compiler.

For every canonical ``texture_key`` in the compiler's material keyword table this
tool asks Gemini (``gemini-3.1-flash-image``) for a straight-on, evenly lit,
seamless material photograph, then post-processes it into a deterministic PBR set:

  tools/archetype_compiler/textures/<texture_key>/
      albedo.jpg     1024x1024, tileable (offset + cross-blend, mirror fallback)
      normal.png     512x512, derived from blurred luminance (Sobel, OpenGL +Y)
      roughness.jpg  512x512, inverted local contrast remapped around the
                     keyword table's flat roughness value

Tileability is measured with a wrap-seam contrast ratio (seam gradient vs mean
interior gradient). Raw generations above the regenerate threshold are retried
(max 2), then fall back to mirror-tiling, which is seamless by construction.
Provenance (prompt, model, seam metrics, method, retries, reference image) is
recorded per texture in ``textures/manifest.json``.

Usage (backend venv has google-genai + Pillow + numpy):

  backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_textures.py --list
  backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_textures.py \
      --materials charred_timber,buff_brick,zinc          # pilot trio
  backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_textures.py  # full sweep
  ... --from-archetype nordic_timber_midrise --materials charred_timber \
      # attach the archetype's card image so the texture matches its look

GEMINI_API_KEY is read from the environment or backend/.env.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
sys.path.insert(0, str(TOOL_DIR))

from compiler import _DEFAULT_TEXTURE_ANCHORS, texture_anchor_table  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL_ID = "gemini-3.1-flash-image"
TEXTURE_SIZE = 1024
DERIVED_SIZE = 512  # normal + roughness resolution
SEAM_NARROW = 1.5   # raw seam ratio at/below this: narrow blend keeps detail
SEAM_REGEN = 2.8    # above this: regenerate; after retries, mirror-tile
MAX_ATTEMPTS = 3    # 1 initial + 2 retries
JPEG_QUALITY = 92

# Coverage note: 1 tile = 2 m of facade (blender_generate box-projects UVs at
# that density), so the prose below describes what fits in a 2 m square.
TEXTURE_PROSE: dict[str, str] = {
    "charred_timber": "charred black shou-sugi-ban timber cladding, vertical board-on-board planks, subtle alligator-skin char",
    "black_metal": "matte charcoal-black architectural metal panels, fine vertical brushed grain, thin recessed panel joints",
    # distinctive wording on purpose: plain "galvanized corrugated steel" hits
    # IMAGE_RECITATION every time (too close to ubiquitous stock textures)
    "corrugated_steel": "industrial ribbed steel siding on a Canadian prairie workshop, vertical corrugations, cool grey zinc coating with faint weathering streaks",
    "corten_steel": "weathered corten steel plates, rust-orange patina with subtle vertical streaking, thin panel seams",
    "zinc": "blue-grey zinc facade cladding, flat-lock rectangular panels with staggered joints",
    "copper": "aged copper facade panels, warm russet brown with soft patina variation",
    "standing_seam": "dark grey standing-seam metal cladding, parallel vertical seams every half metre",
    "mediterranean_roof_tile": "handmade Mediterranean terracotta barrel roof tiles, burnt orange and ochre, overlapping rows with subtle weathering",
    "welsh_slate": "dark blue-grey natural Welsh slate roof tiles in overlapping horizontal courses, subtle cleft edges",
    "metal_panel": "silver-grey aluminium composite facade panels with slim recessed joints",
    "glulam": "glue-laminated timber surface, warm honey tone, visible horizontal lamination lines",
    "clt": "exposed cross-laminated timber panel, pale honey spruce, fine vertical board joints",
    "birch_wood": "pale birch wood cladding boards, smooth fine grain",
    "pine_wood": "golden pine wood cladding boards, occasional small knots, straight grain",
    "larch_wood": "natural larch wood cladding, narrow vertical boards, warm amber tone",
    "scandinavian_larch": "premium Scandinavian larch and glulam facade, honey-amber narrow vertical boards, straight grain and restrained board variation",
    "cedar_wood": "western red cedar cladding boards, warm reddish-brown, fine straight grain",
    "oak_wood": "european oak boards, medium warm brown, straight grain",
    "natural_timber": "warm natural timber cladding boards, medium brown, vertical orientation",
    "red_brick": "red-brown clay brick wall in running bond, slight tonal variation per brick, recessed grey mortar joints",
    "victorian_brick": "late nineteenth-century red-brown pressed clay brick in running bond, warm grey lime mortar, darker fired bricks and subtle soot age",
    "buff_brick": "buff cream-yellow brick wall in running bond, subtle tonal variation, light grey mortar joints",
    "white_plaster": "smooth white lime plaster wall, very subtle trowel texture",
    "stucco": "light beige mineral stucco wall, fine sand-float texture",
    "limestone": "pale limestone ashlar wall, large smooth blocks, thin flush joints",
    "heritage_portland_stone": "warm off-white London Portland limestone ashlar, finely dressed large blocks with restrained joints",
    "brownstone": "historic warm umber-brown sandstone ashlar, sedimentary banding, hand-dressed block faces and fine matching mortar joints",
    "sandstone": "warm buff sandstone ashlar wall, soft tonal banding across blocks",
    "granite": "grey granite wall panels, flame-finished, fine salt-and-pepper speckle",
    "natural_stone": "coursed natural stone wall, mixed warm grey tones, split-face texture",
    "precast_concrete": "smooth precast concrete panels, pale warm grey, slim recessed reveals",
    "concrete": "cast-in-place concrete wall, light warm grey, subtle formwork marks and small pores",
    "curtain_wall": "glass curtain wall, blue-grey reflective glazing panels between slim dark aluminium mullions",
    "fiber_cement": "smooth fibre-cement facade panels, pale grey, matte finish, faint fibre texture",
    "terracotta": "terracotta rainscreen panels, warm orange-brown, horizontal format with fine grooves",
    "art_deco_terracotta": "1920s glazed architectural terracotta blocks, warm ivory and pale sandstone, fine joints with subtle glaze and crazing",
    "roof_membrane": "grey built-up bitumen roof membrane with fine gravel ballast, seen from directly above",
    "sedum_roof": "extensive sedum green roof carpet, mixed green and russet succulents, seen from directly above",
}

# Attempt-indexed variants: recitation blocks (FinishReason.IMAGE_RECITATION)
# happen when the output would match stock texture photos too closely, so each
# retry rewords the request instead of repeating it verbatim.
PROMPT_TEMPLATES = (
    "Seamless tileable texture of {prose}, photographed straight-on, even diffuse "
    "lighting, no shadows, no perspective, covering a 2 by 2 metre area of the "
    "surface. The texture must tile seamlessly in both directions.",
    "Flat frontal close-up photograph of {prose} on a building, slightly weathered "
    "with natural variation, overcast even light, no shadows or perspective, about "
    "2 by 2 metres of the surface. The pattern must repeat seamlessly in both directions.",
    "Architectural material swatch: {prose}, orthographic straight-on view filling "
    "the whole frame, soft uniform illumination, subtle real-world imperfections, "
    "roughly 2 metres of coverage. Edges must wrap so the image tiles perfectly.",
)
REFERENCE_SUFFIX = (
    " Match the colour and character of this material as it appears in the "
    "attached reference photograph of the building."
)


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------

def load_api_key(cli_key: str | None) -> str:
    if cli_key:
        return cli_key
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    env_file = REPO_ROOT / "backend" / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    raise SystemExit("GEMINI_API_KEY not found (env, --api-key, or backend/.env)")


def gemini_generate(client, prose: str, reference: Image.Image | None, variant: int = 0):
    """One generation call; returns (PIL image, prompt used)."""
    from google.genai import types

    prompt = PROMPT_TEMPLATES[variant % len(PROMPT_TEMPLATES)].format(prose=prose)
    contents: list = []
    if reference is not None:
        prompt += REFERENCE_SUFFIX
        contents.append(reference)
    contents.append(prompt)

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="1:1", image_size="1K"),
        ),
    )
    texts: list[str] = []
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else []) or []:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                return Image.open(io.BytesIO(inline.data)).convert("RGB"), prompt
            if getattr(part, "text", None):
                texts.append(part.text.strip())
    finish = ", ".join(str(c.finish_reason) for c in (response.candidates or []))
    detail = f" finish_reason={finish}" if finish else ""
    if texts:
        detail += f" text={' | '.join(texts)[:200]!r}"
    raise RuntimeError(f"Gemini returned no image part.{detail}")


# ---------------------------------------------------------------------------
# Tileability
# ---------------------------------------------------------------------------

def _gray(arr: np.ndarray) -> np.ndarray:
    return arr.astype(np.float64) @ np.array([0.299, 0.587, 0.114])


def seam_ratio(img: Image.Image) -> float:
    """Wrap-seam contrast vs mean interior gradient. ~1.0 tiles as smoothly as
    the interior; large values mean a visible seam when the image repeats."""
    g = _gray(np.asarray(img))
    interior = (np.abs(np.diff(g, axis=0)).mean() + np.abs(np.diff(g, axis=1)).mean()) / 2
    seam_h = np.abs(g[0, :] - g[-1, :]).mean()
    seam_v = np.abs(g[:, 0] - g[:, -1]).mean()
    return float(((seam_h + seam_v) / 2) / max(interior, 1e-6))


def flatten_lighting(img: Image.Image) -> Image.Image:
    """Remove low-frequency lighting gradients (vignettes tile into banding —
    worse than the seam itself). Multiplicative luminance correction so hue is
    untouched: divide by the heavily blurred luminance, restore the mean."""
    arr = np.asarray(img).astype(np.float64)
    lum = Image.fromarray(_gray(arr).astype(np.uint8))
    blurred = np.asarray(lum.filter(ImageFilter.GaussianBlur(radius=arr.shape[0] / 3))).astype(np.float64)
    blurred = np.clip(blurred, 24.0, None)
    gain = (blurred.mean() / blurred)[..., None]
    return Image.fromarray(np.clip(arr * gain, 0, 255).astype(np.uint8))


def cross_blend_tile(img: Image.Image, feather: float) -> Image.Image:
    """Offset by 50% (borders become seamless by construction) and hide the
    resulting interior cross-seam by blending the original back in with a
    weight that is 1 on the centre lines and 0 at the borders. Keep the band
    narrow: wide feathers ghost structured textures like brick courses."""
    arr = np.asarray(img).astype(np.float64)
    h, w = arr.shape[:2]
    rolled = np.roll(arr, (h // 2, w // 2), axis=(0, 1))

    def ramp(n: int) -> np.ndarray:
        idx = np.arange(n)
        t = np.minimum(idx, n - 1 - idx) / max(1.0, feather * n)
        t = np.clip(t, 0.0, 1.0)
        return t * t * (3 - 2 * t)  # smoothstep

    weight = np.minimum.outer(ramp(h), ramp(w))[..., None]
    blended = weight * arr + (1.0 - weight) * rolled
    return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8))


def mirror_tile(img: Image.Image) -> Image.Image:
    """Seamless by construction; features mirror and repeat at half scale."""
    arr = np.asarray(img)
    top = np.concatenate([arr, arr[:, ::-1]], axis=1)
    full = np.concatenate([top, top[::-1, :]], axis=0)
    return Image.fromarray(full).resize(img.size, Image.LANCZOS)


# ---------------------------------------------------------------------------
# Derived maps
# ---------------------------------------------------------------------------

def derive_normal(albedo: Image.Image, strength: float = 2.2) -> Image.Image:
    small = albedo.resize((DERIVED_SIZE, DERIVED_SIZE), Image.LANCZOS)
    height = _gray(np.asarray(small.filter(ImageFilter.GaussianBlur(radius=1.5)))) / 255.0
    # Sobel via wrap-padding so the normal map tiles with the albedo
    padded = np.pad(height, 1, mode="wrap")
    gx = (
        (padded[:-2, 2:] + 2 * padded[1:-1, 2:] + padded[2:, 2:])
        - (padded[:-2, :-2] + 2 * padded[1:-1, :-2] + padded[2:, :-2])
    ) / 8.0
    gy = (
        (padded[2:, :-2] + 2 * padded[2:, 1:-1] + padded[2:, 2:])
        - (padded[:-2, :-2] + 2 * padded[:-2, 1:-1] + padded[:-2, 2:])
    ) / 8.0
    nx, ny, nz = -gx * strength, gy * strength, np.ones_like(gx)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    rgb = np.stack([nx / length, ny / length, nz / length], axis=-1) * 0.5 + 0.5
    return Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8))


def derive_roughness(albedo: Image.Image, base_roughness: float, spread: float = 0.18) -> Image.Image:
    small = albedo.resize((DERIVED_SIZE, DERIVED_SIZE), Image.LANCZOS)
    g = Image.fromarray(_gray(np.asarray(small)).astype(np.uint8))
    mean = np.asarray(g.filter(ImageFilter.BoxBlur(8))).astype(np.float64)
    sq_mean = np.asarray(
        Image.fromarray((np.asarray(g).astype(np.float64) ** 2 / 255.0).astype(np.uint8)).filter(ImageFilter.BoxBlur(8))
    ).astype(np.float64) * 255.0
    variance = np.clip(sq_mean - mean**2, 0, None)
    contrast = np.sqrt(variance)
    lo, hi = np.percentile(contrast, 5), np.percentile(contrast, 95)
    norm = np.clip((contrast - lo) / max(hi - lo, 1e-6), 0, 1)
    # inverted local contrast: contrasty spots (sheen, highlights) read glossier
    rough = base_roughness + (0.5 - norm) * 2 * spread
    return Image.fromarray(np.clip(rough * 255, 13, 250).astype(np.uint8), mode="L")


# ---------------------------------------------------------------------------
# Reference image lookup (--from-archetype)
# ---------------------------------------------------------------------------

def load_archetype_reference(archetype_id: str) -> tuple[Image.Image, str]:
    source_file = REPO_ROOT / "build" / "archetypes" / archetype_id / "archetype-source.json"
    if not source_file.exists():
        raise SystemExit(
            f"--from-archetype: {source_file} not found. Run generate_family.py "
            f"--archetype-id {archetype_id} first so the catalogue export exists."
        )
    payload = json.loads(source_file.read_text(encoding="utf-8"))
    thumbnail = str(payload.get("thumbnailUrl") or "")
    candidate = REPO_ROOT / "frontend" / "public" / thumbnail.lstrip("/")
    if not thumbnail or not candidate.exists():
        raise SystemExit(f"--from-archetype: card image not found for {archetype_id} (thumbnailUrl={thumbnail!r})")
    image = Image.open(candidate).convert("RGB")
    image.thumbnail((1024, 1024))
    return image, str(candidate.relative_to(REPO_ROOT))


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def process_raw(key: str, raw: Image.Image, anchor: tuple[str, float], out_dir: Path) -> dict:
    """Deterministic post-processing: flatten lighting, make tileable, derive
    normal + roughness, write the texture set. Returns provenance fields."""
    base_color, base_roughness = anchor
    flattened = flatten_lighting(raw)
    ratio_flat = seam_ratio(flattened)

    if ratio_flat <= SEAM_REGEN:
        method, feather = "cross_blend", 0.09
        albedo = cross_blend_tile(flattened, feather)
    else:
        method, feather = "mirror_tile", None
        albedo = mirror_tile(flattened)
    final_ratio = seam_ratio(albedo)

    normal = derive_normal(albedo)
    roughness = derive_roughness(albedo, base_roughness)

    tex_dir = out_dir / key
    tex_dir.mkdir(parents=True, exist_ok=True)
    raw.save(tex_dir / "raw.jpg", quality=JPEG_QUALITY)  # enables --reprocess without API calls
    albedo.save(tex_dir / "albedo.jpg", quality=JPEG_QUALITY)
    normal.save(tex_dir / "normal.png", optimize=True)
    roughness.save(tex_dir / "roughness.jpg", quality=90)

    mean_rgb = np.asarray(albedo).reshape(-1, 3).mean(axis=0)
    size_kb = sum((tex_dir / f).stat().st_size for f in ("albedo.jpg", "normal.png", "roughness.jpg")) // 1024
    print(f"  [{key}] {method} (feather={feather}) -> final seam ratio {final_ratio:.2f}, {size_kb} KB")
    return {
        "target_base_color": base_color,
        "target_roughness": base_roughness,
        "seam_ratio_flattened": round(ratio_flat, 3),
        "seam_method": method,
        "seam_feather": feather,
        "seam_ratio_final": round(final_ratio, 3),
        "mean_rgb": [int(c) for c in mean_rgb],
        "files": {"albedo": "albedo.jpg", "normal": "normal.png", "roughness": "roughness.jpg", "raw": "raw.jpg"},
        "size_kb": size_kb,
    }


def generate_one(client, key: str, anchor: tuple[str, float], out_dir: Path,
                 reference: Image.Image | None, reference_path: str | None) -> dict:
    prose = TEXTURE_PROSE[key]
    attempts: list[dict] = []
    best_img, best_ratio, prompt_used = None, float("inf"), ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            image, prompt_used = gemini_generate(client, prose, reference, variant=attempt - 1)
        except RuntimeError as exc:
            # Recitation blocks and empty responses burn the attempt; the next
            # attempt uses a reworded prompt variant.
            attempts.append({"attempt": attempt, "error": str(exc)[:160]})
            print(f"  [{key}] attempt {attempt}: {exc}")
            time.sleep(0.5)
            continue
        if image.size != (TEXTURE_SIZE, TEXTURE_SIZE):
            image = image.resize((TEXTURE_SIZE, TEXTURE_SIZE), Image.LANCZOS)
        ratio = seam_ratio(flatten_lighting(image))
        attempts.append({"attempt": attempt, "seam_ratio_flattened": round(ratio, 3)})
        print(f"  [{key}] attempt {attempt}: flattened seam ratio {ratio:.2f}")
        if ratio < best_ratio:
            best_img, best_ratio = image, ratio
        if ratio <= SEAM_REGEN:
            break
        time.sleep(0.5)

    if best_img is None:
        raise RuntimeError(f"all {MAX_ATTEMPTS} generation attempts failed (see manifest attempts)")

    return {
        "prompt": prompt_used,
        "model": MODEL_ID,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reference_image": reference_path,
        "attempts": attempts,
        **process_raw(key, best_img, anchor, out_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the tileable PBR texture library")
    parser.add_argument("--materials", default=None,
                        help="comma-separated texture keys (default: every key in the compiler table)")
    parser.add_argument("--out", type=Path, default=TOOL_DIR / "textures")
    parser.add_argument("--from-archetype", default=None,
                        help="attach this archetype's card image as a style reference")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--force", action="store_true", help="regenerate even if files exist")
    parser.add_argument("--list", action="store_true", help="list texture keys and exit")
    parser.add_argument("--dry-run", action="store_true", help="show planned generations, no API calls")
    parser.add_argument("--reprocess", action="store_true",
                        help="re-run post-processing from the saved raw.jpg files (no API calls)")
    args = parser.parse_args()

    anchors = texture_anchor_table()
    unknown_prose = sorted(set(anchors) - set(TEXTURE_PROSE))
    if unknown_prose:
        raise SystemExit(f"texture keys missing prose in TEXTURE_PROSE: {unknown_prose}")

    if args.list:
        for key, (color, rough) in sorted(anchors.items()):
            print(f"{key:22s} {color}  rough={rough:.2f}  {TEXTURE_PROSE[key][:70]}")
        return

    keys = list(anchors) if not args.materials else [k.strip() for k in args.materials.split(",") if k.strip()]
    bad = sorted(set(keys) - set(anchors))
    if bad:
        raise SystemExit(f"unknown texture keys: {bad} (see --list)")

    manifest_path = args.out / "manifest.json"
    manifest: dict = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if args.reprocess:
        targets = [k for k in keys if (args.out / k / "raw.jpg").exists()]
        missing = sorted(set(keys) - set(targets))
        if missing:
            print(f"no raw.jpg for: {', '.join(missing)} (skipped)")
        for key in targets:
            print(f"[reprocess] {key}")
            raw = Image.open(args.out / key / "raw.jpg").convert("RGB")
            manifest.setdefault(key, {})
            manifest[key].update(process_raw(key, raw, anchors[key], args.out))
            manifest[key]["reprocessed_at"] = datetime.now(timezone.utc).isoformat()
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"\nwrote {manifest_path} ({len(targets)} reprocessed)")
        return

    todo = [k for k in keys if args.force or not (args.out / k / "albedo.jpg").exists()]
    skipped = [k for k in keys if k not in todo]
    if skipped:
        print(f"skipping {len(skipped)} existing (use --force to regenerate): {', '.join(skipped)}")
    if args.dry_run:
        for key in todo:
            print(f"would generate {key}: {PROMPT_TEMPLATES[0].format(prose=TEXTURE_PROSE[key])[:110]}...")
        print(f"dry-run: {len(todo)} generation(s), 0 API calls made")
        return
    if not todo:
        print("nothing to do")
        return

    reference, reference_path = (None, None)
    if args.from_archetype:
        reference, reference_path = load_archetype_reference(args.from_archetype)
        print(f"reference image: {reference_path}")

    from google import genai
    client = genai.Client(api_key=load_api_key(args.api_key))

    failures: list[str] = []
    for i, key in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {key}")
        try:
            manifest[key] = generate_one(client, key, anchors[key], args.out, reference, reference_path)
        except Exception as exc:  # keep sweeping; report at the end
            failures.append(key)
            print(f"  [{key}] FAILED: {exc}")
        args.out.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        time.sleep(0.4)

    print(f"\nwrote {manifest_path} ({len(manifest)} textures)")
    if failures:
        raise SystemExit(f"{len(failures)} texture(s) failed: {', '.join(failures)}")


if __name__ == "__main__":
    main()
