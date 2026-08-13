"""Publish the approved Industrial Tilt-up Concrete V98 evidence package."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "frontend/public/archetypes/buildings/industrial_park_modernism"
ARTIFACT = ROOT / "artifacts/sticker-method-batch-01/industrial-tilt-up-concrete"
CANONICAL = ARTIFACT / "formal-canonical-v1"
EXTENDED = ARTIFACT / "formal-extended-v1"
OUTPUT = ROOT / "docs/reviews/catalogue-rollout-v98/sticker-method-batch-01/industrial-tilt-up-concrete"

GEOMETRY_HASHES = {
    "canonical": "9c51f0b075aa1379409377ce3ad9d15887be2a1f29dc18d4aadc91564ca74243",
    "extended": "f7ffcae4a795b48b4598050bfd79e6be6f083b24dd035168779b841023bbb891",
}


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ("arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("arial.ttf", "DejaVuSans.ttf")
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _panel(path: Path, size: tuple[int, int], *, contain: bool = False) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if contain:
        image.thumbnail(size, Image.Resampling.LANCZOS)
        panel = Image.new("RGB", size, "#20262b")
        panel.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
        return panel
    scale = max(size[0] / image.width, size[1] / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left, top = (image.width - size[0]) // 2, (image.height - size[1]) // 2
    return image.crop((left, top, left + size[0], top + size[1]))


def _board(filename: str, title: str, items: list[tuple[Path, str]], *, contain: bool = False) -> None:
    panel_w, panel_h = 700, 540
    board = Image.new("RGB", (panel_w * len(items), panel_h + 112), "#e7e4dd")
    draw = ImageDraw.Draw(board)
    draw.text((32, 22), title, fill="#182026", font=_font(30, True))
    for index, (path, label) in enumerate(items):
        x = index * panel_w
        board.paste(_panel(path, (panel_w, panel_h), contain=contain), (x, 112))
        draw.rectangle((x, 76, x + panel_w, 112), fill="#182026")
        draw.text((x + 18, 82), label, fill="#ffffff", font=_font(20, True))
    board.save(OUTPUT / filename, optimize=True)


def _publish_tier(tier: str, folder: Path) -> dict:
    family = f"industrial-tilt-up-concrete-v98-{tier}"
    for view in ("archetype_match", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit", "aerial"):
        shutil.copy2(folder / f"{family}_{view}.png", OUTPUT / f"render-{tier}-{view}.png")
    shutil.copy2(folder / "validation_report.json", OUTPUT / f"validation-{tier}.json")
    manifest = json.loads((folder / f"{family}_manifest.json").read_text(encoding="utf-8"))
    assembled = manifest["assembled"]
    return {
        "dimensions": manifest["dimensions"],
        "geometry_sha256": GEOMETRY_HASHES[tier],
        "assembled": {
            "height_m": assembled["height_m"],
            "triangle_count": assembled["triangle_count"],
            "assembly_count": assembled["massing_graph"]["assembly_count"],
        },
        "final_surface_audit": {
            "status": assembled["final_surface_audit_status"],
            "checked_faces": assembled["final_surface_audit_checked_faces"],
            "failure_count": assembled["final_surface_audit_failure_count"],
        },
        "validation": json.loads((folder / "validation_report.json").read_text(encoding="utf-8"))["status"],
        "production_preflight": json.loads((folder / "production_preflight.json").read_text(encoding="utf-8"))["status"],
        "render_count": len(manifest["renders"]),
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    tiers = {
        "canonical": _publish_tier("canonical", CANONICAL),
        "extended": _publish_tier("extended", EXTENDED),
    }
    evidence = {
        "schema": "siteforge.sticker-method-machine-evidence@1",
        "architect_scores": {"canonical": 95.15, "extended": 95.10, "mean": 95.125, "hard_stops": 0},
        "tiers": tiers,
        "tier_contract": {
            "representation": "discrete_panel_lego",
            "canonical_to_extended": "one complete 6 m rear operational module",
            "width_scaling": False,
            "vertical_scaling": False,
            "nonuniform_scaling": False,
            "metric_uv_scale_preserved": True,
            "fixed_front_identity_kit_preserved": True,
        },
        "non_blocking_optimization_follow_up": {"material_consolidation": True},
    }
    (OUTPUT / "machine-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    _board("01-exact-reference-comparison.png", "Industrial Tilt-up Concrete V98 - exact identity", [
        (REFERENCE / "variant_0.png", "EXACT ARCHETYPE"),
        (CANONICAL / "industrial-tilt-up-concrete-v98-canonical_archetype_match.png", "CANONICAL - 60 x 42 m"),
        (EXTENDED / "industrial-tilt-up-concrete-v98-extended_archetype_match.png", "EXTENDED - 60 x 48 m"),
    ])
    _board("02-loading-reference-comparison.png", "Office ribbons, fin screen, pylon and operational elevation", [
        (REFERENCE / "variant_0_angle_60.jpg", "EXACT OBLIQUE"),
        (CANONICAL / "industrial-tilt-up-concrete-v98-canonical_front_corner_oblique.png", "CANONICAL"),
        (EXTENDED / "industrial-tilt-up-concrete-v98-extended_front_corner_oblique.png", "EXTENDED"),
    ])
    _board("03-roof-reference-comparison.png", "TPO roof, sparse plant and discrete rear-depth extension", [
        (REFERENCE / "variant_0_angle_90.jpg", "EXACT AERIAL"),
        (CANONICAL / "industrial-tilt-up-concrete-v98-canonical_aerial.png", "CANONICAL AERIAL"),
        (EXTENDED / "industrial-tilt-up-concrete-v98-extended_aerial.png", "EXTENDED AERIAL"),
    ], contain=True)
    _board("04-sticker-and-size-comparison.png", "Sectional doors, glass, panels and constant metric scale", [
        (CANONICAL / "industrial-tilt-up-concrete-v98-canonical_facade_close.png", "CANONICAL CLOSE"),
        (EXTENDED / "industrial-tilt-up-concrete-v98-extended_facade_close.png", "EXTENDED CLOSE"),
    ])


if __name__ == "__main__":
    main()
