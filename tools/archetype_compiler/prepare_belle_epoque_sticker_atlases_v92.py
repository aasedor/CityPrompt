"""Prepare seam-matched elevation stickers and polar dome atlases for V92."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image


REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs/reviews/catalogue-rollout-v91/three-all-surface-sticker-pilot/belle-epoque-grand-magasin"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "sticker_assets/belle_epoque_v92"


def _edge_strip(image: Image.Image, side: str, width: int) -> Image.Image:
    if side == "left":
        return image.crop((0, 0, width, image.height))
    return image.crop((image.width - width, 0, image.width, image.height))


def _paste_edge(image: Image.Image, strip: Image.Image, side: str, width: int) -> None:
    strip = strip.resize((width, image.height), Image.Resampling.LANCZOS)
    # Full correction at the seam, tapering to zero at the inner edge.
    alpha = Image.new("L", (width, image.height))
    pixels = alpha.load()
    for x in range(width):
        distance = x if side == "left" else width - 1 - x
        value = round(255 * max(0.0, 1.0 - distance / max(width - 1, 1)))
        for y in range(image.height):
            pixels[x, y] = value
    box = (0, 0) if side == "left" else (image.width - width, 0)
    image.paste(strip, box, alpha)


def blend_pair(a: Image.Image, side_a: str, b: Image.Image, side_b: str, width: int = 72) -> None:
    common_height = max(a.height, b.height)
    edge_a = _edge_strip(a, side_a, min(width, a.width)).resize((width, common_height), Image.Resampling.LANCZOS)
    edge_b = _edge_strip(b, side_b, min(width, b.width)).resize((width, common_height), Image.Resampling.LANCZOS)
    shared = Image.blend(edge_a, edge_b, 0.5)
    _paste_edge(a, shared, side_a, min(width, a.width))
    _paste_edge(b, shared, side_b, min(width, b.width))


def polar_unwrap(source: Image.Image, centre: tuple[float, float], radius: float, size: tuple[int, int]) -> Image.Image:
    """Convert a plan-view circular dome into base-to-apex equirectangular UVs."""
    width, height = size
    source = source.convert("RGB")
    output = Image.new("RGB", size)
    src = source.load()
    dst = output.load()
    for y in range(height):
        v = y / max(height - 1, 1)
        # PIL rows run top-to-bottom while Blender UV v runs bottom-to-top:
        # the output top is the dome apex (source centre), bottom is its spring.
        r = radius * v
        for x in range(width):
            angle = math.tau * x / max(width - 1, 1)
            sx = max(0.0, min(source.width - 1.001, centre[0] + r * math.cos(angle)))
            sy = max(0.0, min(source.height - 1.001, centre[1] + r * math.sin(angle)))
            x0, y0 = int(sx), int(sy)
            x1, y1 = min(x0 + 1, source.width - 1), min(y0 + 1, source.height - 1)
            fx, fy = sx - x0, sy - y0
            p00, p10, p01, p11 = src[x0, y0], src[x1, y0], src[x0, y1], src[x1, y1]
            dst[x, y] = tuple(round(
                p00[c] * (1-fx) * (1-fy) + p10[c] * fx * (1-fy)
                + p01[c] * (1-fx) * fy + p11[c] * fx * fy
            ) for c in range(3))
    return output


def prepare(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    front = Image.open(SOURCE / "sticker-front.png").convert("RGB")
    left = Image.open(SOURCE / "sticker-left.png").convert("RGB")
    corner = Image.open(SOURCE / "sticker-front-left.png").convert("RGB")
    # Corner u=0 meets the left elevation; corner u=1 meets the front.
    blend_pair(left, "right", corner, "left")
    blend_pair(front, "left", corner, "right")
    front.save(output / "front_seam_matched.jpg", quality=94, subsampling=0)
    left.save(output / "left_seam_matched.jpg", quality=94, subsampling=0)
    corner.save(output / "corner_seam_matched.jpg", quality=94, subsampling=0)

    roof = Image.open(SOURCE / "sticker-roof.png").convert("RGB")
    roof.crop((90, 0, roof.width - 90, 135)).resize((1536, 192), Image.Resampling.LANCZOS).save(
        output / "cornice_zinc.jpg", quality=95, subsampling=0,
    )
    polar_unwrap(roof, (620.0, 620.0), 245.0, (1536, 768)).save(
        output / "central_dome_polar.jpg", quality=95, subsampling=0,
    )
    polar_unwrap(roof, (113.0, 1070.0), 98.0, (1024, 512)).save(
        output / "corner_dome_polar.jpg", quality=95, subsampling=0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    prepare(args.output.resolve())


if __name__ == "__main__":
    main()
