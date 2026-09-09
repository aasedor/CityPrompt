"""Finite, offline visual QA batch. Run with the backend Python environment."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.road_network import Road, build_network
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import shape


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/road-network")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    main_road = Road("main", ((-80, 0), (80, 0)))
    cases = [
        ("Four-way / 10 m", (main_road, Road("branch", ((0, -80), (0, 80))))),
        ("T / 20 m meets 6 m", (Road("main", ((-80, 0), (80, 0)), 20), Road("branch", ((0, 0), (0, 80)), 6))),
        ("Angled T", (main_road, Road("branch", ((0, 0), (65, 75))))),
        ("Angled four-way", (main_road, Road("branch", ((-60, -80), (60, 80))))),
        ("Two close nodes / 12 m", (main_road, Road("a", ((0, -80), (0, 80))), Road("b", ((12, -80), (12, 80))))),
        (
            "Curved crossing",
            (
                Road("a", ((-80, -10), (-30, 5), (20, 0), (80, 15))),
                Road("b", ((-10, -80), (0, -20), (10, 20), (-5, 80))),
            ),
        ),
    ]
    image = Image.new("RGB", (1800, 1280), "#101826")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 23)
        small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
    except OSError:
        font = small = ImageFont.load_default()
    draw.text((30, 20), "CITY PROMPT / PROCEDURAL ROAD NETWORK / deterministic kernel output", font=font, fill="white")
    draw.text(
        (30, 60),
        "Grey: trimmed roads    Teal: resolved junction    Gold: nodes    Pink: ordered approach vectors    Blue: centrelines",
        font=small,
        fill="#c5d3e6",
    )
    for i, (title, roads) in enumerate(cases):
        graph = build_network(roads)
        (output / f"case-{i+1}.json").write_text(json.dumps(graph, indent=2))
        ox, oy = (i % 3) * 600 + 300, (i // 3) * 570 + 390

        def xy(point):
            return (ox + point[0] * 2.6, oy - point[1] * 2.6)

        def polygon(geometry, fill):
            geom = shape(geometry)
            for part in [geom] if geom.geom_type == "Polygon" else getattr(geom, "geoms", []):
                if part.is_empty:
                    continue
                draw.polygon([xy(p) for p in part.exterior.coords], fill=fill)
                for ring in part.interiors:
                    draw.polygon([xy(p) for p in ring.coords], fill="#101826")

        draw.text((ox - 260, oy - 255), title, font=font, fill="white")
        for edge in graph["edges"]:
            polygon(edge["geometry"], "#667385")
        for junction in graph["intersections"]:
            polygon(junction["generatedGeometry"], "#239e99")
        for edge in graph["edges"]:
            draw.line([xy(p) for p in edge["centerline"]["coordinates"]], fill="#83b6ed", width=2)
        for node in graph["nodes"]:
            x, y = xy(node["location"])
            r = 5 if node["intersectionId"] else 3
            draw.ellipse((x - r, y - r, x + r, y + r), fill="#ffc857")
        for junction in graph["intersections"]:
            node = next(n for n in graph["nodes"] if n["id"] == junction["nodeId"])
            x, y = node["location"]
            for a in junction["approaches"]:
                dx, dy = a["direction"]
                draw.line([xy((x, y)), xy((x + dx * 13, y + dy * 13))], fill="#ff80ad", width=3)
        draw.text(
            (ox - 260, oy + 240),
            f'{len(graph["nodes"])} nodes / {len(graph["edges"])} edges / {len(graph["intersections"])} intersections',
            font=small,
            fill="#c5d3e6",
        )
    image.save(output / "road-network-debug.png")
    print(output / "road-network-debug.png")


if __name__ == "__main__":
    main()
