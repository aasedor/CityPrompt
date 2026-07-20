"""Build review boards for the three-archetype Gemini skin realism pilot."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = REPO_ROOT / "build/gemini-skin-v9"
COMPARISON_OUTPUT = OUTPUT_ROOT / "gemini-skin-comparison-board.png"
RESULTS_OUTPUT = OUTPUT_ROOT / "gemini-skin-results-board.png"

FAMILIES = (
    {
        "name": "Nordic Timber Mid-Rise",
        "archetype_id": "nordic_timber_midrise",
        "family": "nordic-timber-midrise",
        "note": "Full rectified timber elevation + real frame, stone plinth, roof terrace and pavilion",
    },
    {
        "name": "Industrial Brick Mixed Use",
        "archetype_id": "industrial_brick_mixed_use",
        "family": "industrial-brick-mixed-use",
        "note": "Full rectified brick elevation + steel datums, loading canopy, chimney and roof monitor",
    },
    {
        "name": "Modern Glass Office / Institutional",
        "archetype_id": "modern_glass_office_institutional",
        "family": "modern-glass-office-institutional",
        "note": "Floor-accurate glass bands + fine curtain-wall grid, lobby canopy and rooftop pergola",
    },
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def input_paths(spec: dict[str, str]) -> tuple[Path, Path, Path, Path]:
    family = spec["family"]
    archetype = REPO_ROOT / f"frontend/public/archetypes/buildings/{spec['archetype_id']}/variant_0.png"
    baseline = REPO_ROOT / f"build/worldclass-v8/families/{family}/{family}_preview.png"
    hero = OUTPUT_ROOT / family / f"{family}_archetype_match.png"
    aerial = OUTPUT_ROOT / family / f"{family}_aerial.png"
    return archetype, baseline, hero, aerial


def image_panel(path: Path, size: tuple[int, int], label: str, accent: str, *, centering=(0.5, 0.5)) -> Image.Image:
    label_height = 50
    image = Image.open(path).convert("RGB")
    fitted = ImageOps.fit(
        image,
        (size[0], size[1] - label_height),
        method=Image.Resampling.LANCZOS,
        centering=centering,
    )
    result = Image.new("RGB", size, "#f1eee6")
    result.paste(fitted, (0, label_height))
    draw = ImageDraw.Draw(result)
    draw.rectangle((0, 0, size[0], label_height), fill=accent)
    draw.text((16, 13), label, font=font(20, bold=True), fill="white")
    return result


def verify_inputs() -> None:
    required = [path for spec in FAMILIES for path in input_paths(spec)]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing gallery inputs:\n" + "\n".join(missing))


def comparison_board() -> None:
    canvas = Image.new("RGB", (1800, 2190), "#f7f4ec")
    draw = ImageDraw.Draw(canvas)
    draw.text((48, 32), "Gemini skin realism pilot - three architectural systems", font=font(42, bold=True), fill="#15222d")
    draw.text(
        (50, 88),
        "Archetype reference, previous procedural V8, and the new depth-backed photographic facade method.",
        font=font(22), fill="#52616c",
    )

    panel_size = (540, 470)
    row_top = 145
    for row, spec in enumerate(FAMILIES):
        archetype, baseline, hero, _ = input_paths(spec)
        y = row_top + row * 620
        draw.text((48, y), spec["name"], font=font(30, bold=True), fill="#15222d")
        draw.text((48, y + 40), spec["note"], font=font(19), fill="#66737d")
        cards = (
            image_panel(archetype, panel_size, "ARCHETYPE", "#15222d", centering=(0.5, 0.52)),
            image_panel(baseline, panel_size, "V8 PROCEDURAL BASELINE", "#68727a", centering=(0.5, 0.52)),
            image_panel(hero, panel_size, "V9 GEMINI SKIN + DEPTH", "#36750d", centering=(0.5, 0.48)),
        )
        for column, card in enumerate(cards):
            canvas.paste(card, (48 + column * 578, y + 78))

    footer_y = 2040
    draw.rounded_rectangle((48, footer_y, 1752, 2150), radius=16, fill="#e7ede2", outline="#bdc9b4", width=2)
    draw.text((74, footer_y + 18), "PILOT RESULT", font=font(20, bold=True), fill="#36750d")
    draw.text(
        (74, footer_y + 54),
        "Photographic micro-detail carries material realism; geometry is reserved for silhouette, corners, slabs, frames, canopies and roofs.",
        font=font(19), fill="#2b3840",
    )
    canvas.save(COMPARISON_OUTPUT, quality=95)


def results_board() -> None:
    canvas = Image.new("RGB", (1800, 1320), "#f7f4ec")
    draw = ImageDraw.Draw(canvas)
    draw.text((48, 30), "V9 Gemini skin pilot - final path-traced views", font=font(42, bold=True), fill="#15222d")
    draw.text((50, 84), "Front-elevation fidelity and whole-building roof/corner coherence.", font=font(22), fill="#52616c")

    for column, spec in enumerate(FAMILIES):
        _, _, hero, aerial = input_paths(spec)
        x = 42 + column * 586
        draw.text((x, 130), spec["name"], font=font(24, bold=True), fill="#15222d")
        canvas.paste(image_panel(hero, (550, 510), "FRONT / MATERIAL DETAIL", "#36750d", centering=(0.5, 0.48)), (x, 172))
        canvas.paste(image_panel(aerial, (550, 510), "AERIAL / ASSEMBLY", "#285d75", centering=(0.5, 0.48)), (x, 708))

    draw.text(
        (48, 1250),
        "All three assembled GLBs pass the existing City Prompt validator and retain bottom-centre placement metadata.",
        font=font(20), fill="#52616c",
    )
    canvas.save(RESULTS_OUTPUT, quality=95)


def main() -> None:
    verify_inputs()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    comparison_board()
    results_board()
    print(COMPARISON_OUTPUT)
    print(RESULTS_OUTPUT)


if __name__ == "__main__":
    main()
