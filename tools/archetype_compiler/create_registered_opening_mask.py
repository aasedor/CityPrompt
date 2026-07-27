"""Create a pixel-registered semantic glazing mask from an opening schedule.

Image models are useful for facade identity but can turn masonry, reflections,
or roof bands white when asked for a semantic glass mask.  This small utility
keeps the reliable part of the workflow deterministic: an architecturally
audited opening schedule is stored in normalized coordinates and rasterized at
the exact source-elevation resolution.

Supported shapes:

``rect``
    A rectangular opening.
``segmental_arch``
    A rectangular opening with a shallow curved head.  ``rise`` is normalized
    to the image height and defaults to one quarter of the opening height.
``pointed_arch``
    A Gothic lancet with a cusped apex and curved shoulders. ``rise`` defaults
    to thirty percent of the opening height.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def _px(value: float, extent: int) -> int:
    return int(round(float(value) * extent))


def _segmental_arch_polygon(
    bbox: list[float], rise: float, width: int, height: int,
) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = bbox
    left, top, right, bottom = (
        _px(x0, width), _px(y0, height), _px(x1, width), _px(y1, height)
    )
    rise_px = max(1, _px(rise, height))
    half = max(1.0, (right - left) / 2.0)
    centre = (left + right) / 2.0
    curve: list[tuple[int, int]] = []
    steps = max(16, right - left)
    for index in range(steps + 1):
        x = left + (right - left) * index / steps
        unit = max(-1.0, min(1.0, (x - centre) / half))
        y = top + rise_px * (1.0 - math.sqrt(max(0.0, 1.0 - unit * unit)))
        curve.append((int(round(x)), int(round(y))))
    return curve + [(right, bottom), (left, bottom)]


def _quadratic_point(
    start: tuple[float, float], control: tuple[float, float], end: tuple[float, float], t: float,
) -> tuple[int, int]:
    inverse = 1.0 - t
    x = inverse * inverse * start[0] + 2.0 * inverse * t * control[0] + t * t * end[0]
    y = inverse * inverse * start[1] + 2.0 * inverse * t * control[1] + t * t * end[1]
    return int(round(x)), int(round(y))


def _pointed_arch_polygon(
    bbox: list[float], rise: float, width: int, height: int,
) -> list[tuple[int, int]]:
    """A two-centred lancet approximation that preserves a crisp apex."""
    x0, y0, x1, y1 = bbox
    left, top, right, bottom = (
        _px(x0, width), _px(y0, height), _px(x1, width), _px(y1, height)
    )
    spring = min(bottom - 1, top + max(2, _px(rise, height)))
    apex = ((left + right) / 2.0, float(top))
    steps = max(12, (right - left) // 2)
    left_curve = [
        _quadratic_point(apex, (float(left), float(top)), (float(left), float(spring)), index / steps)
        for index in range(steps + 1)
    ]
    right_curve = [
        _quadratic_point((float(right), float(spring)), (float(right), float(top)), apex, index / steps)
        for index in range(steps + 1)
    ]
    return left_curve + [(left, bottom), (right, bottom)] + right_curve


def build_mask(source: Path, schedule: dict) -> Image.Image:
    with Image.open(source) as image:
        width, height = image.size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    shape_override = schedule.get("shape_override")
    for opening in schedule.get("openings", []):
        bbox = [float(value) for value in opening["bbox"]]
        shape = str(shape_override or opening.get("shape") or "rect")
        if shape == "rect":
            draw.rectangle(
                [_px(bbox[0], width), _px(bbox[1], height),
                 _px(bbox[2], width), _px(bbox[3], height)],
                fill=255,
            )
        elif shape == "segmental_arch":
            rise = float(opening.get("rise") or ((bbox[3] - bbox[1]) * 0.25))
            draw.polygon(_segmental_arch_polygon(bbox, rise, width, height), fill=255)
        elif shape == "pointed_arch":
            rise = float(opening.get("rise") or ((bbox[3] - bbox[1]) * 0.30))
            draw.polygon(_pointed_arch_polygon(bbox, rise, width, height), fill=255)
        else:
            raise ValueError(f"unsupported opening shape: {shape}")
    return mask


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--glass-output", type=Path, required=True)
    parser.add_argument("--opaque-output", type=Path)
    args = parser.parse_args()

    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    mask = build_mask(args.source, schedule)
    args.glass_output.parent.mkdir(parents=True, exist_ok=True)
    mask.save(args.glass_output, optimize=True)
    if args.opaque_output:
        args.opaque_output.parent.mkdir(parents=True, exist_ok=True)
        ImageOps.invert(mask).save(args.opaque_output, optimize=True)
    histogram = mask.histogram()
    coverage = sum(index * count for index, count in enumerate(histogram)) / (
        255.0 * mask.width * mask.height
    )
    print(f"registered {len(schedule.get('openings', []))} openings; glass coverage={coverage:.1%}")


if __name__ == "__main__":
    main()
