"""Promote the bounded V95 render and build its exact-reference review board."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
V94 = REPO / "docs/reviews/catalogue-rollout-v94/belle-epoque-continuous-sticker-pilot"
V95 = Path(r"C:\dev-artifacts\3D-Maps\belle-epoque-v95-run1")
OUT = REPO / "docs/reviews/catalogue-rollout-v95/belle-epoque-geometry-conditioned-sticker-pilot"
FAMILY = "belle-epoque-grand-magasin-v95-conditioned-5"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path(r"C:\Windows\Fonts\segoeuib.ttf") if bold else Path(r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf") if bold else Path(r"C:\Windows\Fonts\arial.ttf"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _panel(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.fit(source.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    references = {
        "reference-street.png": V94 / "reference-street.png",
        "reference-oblique.jpg": V94 / "reference-oblique.jpg",
        "reference-aerial.jpg": V94 / "reference-aerial.jpg",
    }
    renders = {
        "archetype-match.png": V95 / f"{FAMILY}_archetype_match.png",
        "street.png": V95 / f"{FAMILY}_street.png",
        "front-corner.png": V95 / f"{FAMILY}_front_corner_oblique.png",
        "rear-corner.png": V95 / f"{FAMILY}_rear_corner_oblique.png",
        "facade-close.png": V95 / f"{FAMILY}_facade_close.png",
        "roof-audit.png": V95 / f"{FAMILY}_roof_audit.png",
        "aerial.png": V95 / f"{FAMILY}_aerial.png",
        "context.png": V95 / f"{FAMILY}_context.png",
    }
    for name, source in {**references, **renders}.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, OUT / name)

    manifest = json.loads((V95 / f"{FAMILY}_manifest.json").read_text(encoding="utf-8"))
    grammar = json.loads((V95 / "grammar.json").read_text(encoding="utf-8"))
    validation = json.loads((V95 / "validation_report.json").read_text(encoding="utf-8"))
    package = json.loads(
        (REPO / "tools/archetype_compiler/belle_epoque_geometry_conditioned_v95_carrier_package.json")
        .read_text(encoding="utf-8")
    )
    audit = {
        "schema": "sticker-method-v95-surface-audit@1",
        "run": FAMILY,
        "carrier_package_status": package["status"],
        "carrier_count": package["carrier_count"],
        "locked_geometry_sha256": package["locked_geometry_sha256"],
        "final_surface_contract": grammar["massing_graph"]["final_surface_audit"],
        # Blender emits these counts after binding every carrier and before
        # export. Keep them beside the declarative contract so review evidence
        # does not mistake the contract itself for the executed audit result.
        "final_surface_audit": {
            "status": manifest["assembled"]["final_surface_audit_status"],
            "checked_faces": manifest["assembled"]["final_surface_audit_checked_faces"],
            "failure_count": manifest["assembled"]["final_surface_audit_failure_count"],
        },
        "triangles": manifest.get("assembled", {}).get("triangle_count"),
        "glb_bytes": (V95 / f"{FAMILY}_assembled.glb").stat().st_size,
        "validation_status": validation["status"],
        "material_warning": "delivery optimization deferred until visual lock",
    }
    (OUT / "surface-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(V95 / "validation_report.json", OUT / "validation-report.json")

    cell = (600, 410)
    header = 72
    row_label = 42
    board = Image.new("RGB", (cell[0] * 3, header + (cell[1] + row_label) * 3), "#171a1d")
    draw = ImageDraw.Draw(board)
    columns = ("EXACT ARCHETYPE", "V94 — 91/100", "V95 — 95/100 APPROVED")
    for column, title in enumerate(columns):
        box = draw.textbbox((0, 0), title, font=_font(24, True))
        draw.text((column * cell[0] + (cell[0] - (box[2] - box[0])) / 2, 22), title, font=_font(24, True), fill="#f2efe8")
    rows = (
        ("STREET / ARCHETYPE MATCH", references["reference-street.png"], V94 / "archetype-match.png", renders["archetype-match.png"]),
        ("FRONT CORNER / OBLIQUE", references["reference-oblique.jpg"], V94 / "front-corner.png", renders["front-corner.png"]),
        ("ROOF / AERIAL", references["reference-aerial.jpg"], V94 / "aerial.png", renders["aerial.png"]),
    )
    for row, (label, reference, old, new) in enumerate(rows):
        y = header + row * (cell[1] + row_label)
        draw.rectangle((0, y, board.width, y + row_label), fill="#252b30")
        draw.text((18, y + 9), label, font=_font(18, True), fill="#d6b36a")
        for column, source in enumerate((reference, old, new)):
            board.paste(_panel(source, cell), (column * cell[0], y + row_label))
    board.save(OUT / "v94-v95-geometry-conditioned-comparison-board.jpg", quality=94, subsampling=0)
    print(json.dumps({"output": str(OUT), "files": len(references) + len(renders) + 3}, indent=2))


if __name__ == "__main__":
    main()
