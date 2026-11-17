#!/usr/bin/env python3
"""Bake business-district logos into flat-colour triangles for the 3 m road barrier.

The detail kits carry no textures, so a logo is painted the way the murals are:
as coloured shapes that tile the barrier's long face without overlapping. This
tool traces each logo, lays it out on the face, cuts the background around it,
splits everything along the bend in the barrier's profile and triangulates. It
writes district_logo_shapes.json, which build_calgary_details.py reads; the
builder itself needs none of this tool's dependencies.

The logos are the property of their business improvement areas. The source
files are not kept in the repository. Download them into an empty directory and
pass it with --sources; docs/DISTRICT_LOGO_BARRIERS_2026-11-17.md lists each
file, where it came from and its SHA-256.

    python tools/detail_catalogue/bake_district_logos.py --sources <dir>

Needs numpy, opencv, shapely, mapbox-earcut, fonttools and Pillow. Run it with
python -I, since the sources are downloaded files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import cv2
import mapbox_earcut
import numpy as np
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
from PIL import Image
from shapely import affinity
from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

OUTPUT = Path(__file__).with_name('district_logo_shapes.json')

# The painted face of the 3 m road barrier, as in build_calgary_details.py:
# u runs 0 to 3 m along it, v runs up the face, and the profile bends at LOWER.
LENGTH = 3.0
LOWER = math.hypot(.305 - .2, .33 - .08)
HEIGHT = LOWER + math.hypot(.2 - .125, .81 - .33)
DETAIL = .0012  # metres: outlines are simplified to this tolerance

SOURCES = ('kensington-2026.svg', 'inglewood-2026-horizontal.jpg', 'fourth-street-header.png', 'seventeenth-ave-2022.svg')


def trace(mask: np.ndarray) -> Polygon | MultiPolygon:
    """Outline of a boolean image as geometry in pixel units, y up, holes kept."""
    height = mask.shape[0]
    contours, hierarchy = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    shapes = []
    for index, contour in enumerate(contours):
        if hierarchy[0][index][3] != -1 or len(contour) < 3:
            continue
        holes, child = [], hierarchy[0][index][2]
        while child != -1:
            if len(contours[child]) >= 3:
                holes.append([(float(x), float(height - y)) for x, y in contours[child][:, 0, :]])
            child = hierarchy[0][child][0]
        shapes.append(Polygon([(float(x), float(height - y)) for x, y in contour[:, 0, :]], holes).buffer(0))
    return unary_union(shapes)


def outline(svg: str):
    """Filled area of every path and polygon in an SVG, as geometry in its own units
    with y up. Subpaths are combined by the even-odd rule, which suits a logo whose only
    overlaps are counters cut out of letters."""
    def flatten(p0, p1, p2, p3, steps=14):
        return [tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))
                for t in (k / steps for k in range(1, steps + 1))]

    shape = Polygon()
    for data in re.findall(r'<path[^>]*\sd="([^"]+)"', svg):
        pen = RecordingPen()
        parse_path(data, pen)
        ring = []
        for command, points in pen.value:
            if command == 'moveTo':
                ring = [points[0]]
            elif command == 'lineTo':
                ring.append(points[0])
            elif command == 'curveTo':
                ring.extend(flatten(ring[-1], *points))
            elif command == 'qCurveTo':
                start, control, finish = ring[-1], *points
                ring.extend(flatten(start, tuple(s + 2 / 3 * (c - s) for s, c in zip(start, control)), tuple(f + 2 / 3 * (c - f) for f, c in zip(finish, control)), finish))
            elif command in ('closePath', 'endPath') and len(ring) >= 3:
                shape = shape.symmetric_difference(Polygon(ring).buffer(0))
                ring = []
    for points in re.findall(r'<polygon[^>]*\spoints="([^"]+)"', svg):
        numbers = [float(value) for value in re.split(r'[\s,]+', points.strip())]
        if len(numbers) >= 6:
            shape = shape.symmetric_difference(Polygon(list(zip(numbers[0::2], numbers[1::2]))).buffer(0))
    return affinity.scale(shape, 1, -1, origin=(0, 0))


def solid(shape, smallest: float):
    """A shape without its specks: drops every piece and every hole smaller than an area.
    A logo drawn with a worn, stamped texture has to lose it to be cut as a stencil."""
    kept = []
    for part in polygons(shape):
        if part.area >= smallest:
            kept.append(Polygon(part.exterior, [ring for ring in part.interiors if Polygon(ring).area >= smallest]))
    return unary_union(kept)


def fit(shape, width: float, centre: tuple[float, float]):
    """Scale a traced shape to a width in metres and centre it at (u, v)."""
    x0, y0, x1, y1 = shape.bounds
    scale = width / (x1 - x0)
    shape = affinity.scale(shape, scale, scale, origin=(0, 0))
    x0, y0, x1, y1 = shape.bounds
    return affinity.translate(shape, centre[0] - (x0 + x1) / 2, centre[1] - (y0 + y1) / 2).simplify(DETAIL)


def upscaled(alpha: np.ndarray, factor: int) -> np.ndarray:
    image = Image.fromarray(alpha).resize((alpha.shape[1] * factor, alpha.shape[0] * factor), Image.LANCZOS)
    return np.array(image) > 127


# Each barrier is meant to be painted for real: a ground coat, then one or two more
# flat colours through stencils. So no design here uses a gradient or more than three
# colours, and each is sized to leave little bare ground for anyone else to write on.

def kensington(sources: Path):
    """Burgundy ground, the wordmark in off-white and the roundel in the district's
    orange. The K is a hole in the roundel, so the ground shows through it."""
    logo = fit(outline((sources / 'kensington-2026.svg').read_text(encoding='utf-8')), 2.86, (LENGTH / 2, HEIGHT / 2))
    x0, y0, _, y1 = logo.bounds
    edge = x0 + (y1 - y0) + .01  # the roundel is as wide as the logo is tall
    roundel = unary_union([part for part in polygons(logo) if part.bounds[2] < edge])
    wordmark = unary_union([part for part in polygons(logo) if part.bounds[2] >= edge])
    return {'field': '#42031a', 'top': '#42031a', 'layers': [('#ff5010', roundel), ('#f8f8f8', wordmark)]}


def inglewood(sources: Path):
    """Yellow wordmark on red: the district's 2026 horizontal logo."""
    image = np.array(Image.open(sources / 'inglewood-2026-horizontal.jpg').convert('RGB')).astype(int)
    wordmark = fit(trace(image[:, :, 1] > 128), 2.62, (LENGTH / 2, HEIGHT / 2))
    return {'field': '#d84d2c', 'top': '#d84d2c', 'layers': [('#fec93c', wordmark)]}


FOURTH_COLOURS = {
    # ground, and the colour of the 4's level bar, from the gradients of the district's artwork
    'purple': ('#5a3491', '#d08ab4'),
    'green': ('#0f6166', '#3cc494'),
}


def fourth_street(sources: Path, colourway: str):
    """A 4 at each end and the name stacked in two lines between them, so the artwork
    runs the length and height of the face. The 4 is rebuilt from its geometry: an
    upright bar and a level bar with round ends, and the wedge that joins their tips.
    The district's artwork shades these with gradients; here the upright and wedge are
    white and the level bar, which lies over them, takes the second colour."""
    lockup = np.array(Image.open(sources / 'fourth-street-header.png').convert('RGBA'))[:, :, 3]
    ground, accent = FOURTH_COLOURS[colourway]
    radius, size = 129.0, 954.0  # pixels of the lockup file, rows running down

    def disc(x, y):
        return Point(x, size - y).buffer(radius, 12)

    upright = box(433, radius, 691, size - radius).union(disc(562, radius)).union(disc(562, size - radius))
    level = box(radius, size - 691, 953 - radius, size - 433).union(disc(radius, 562)).union(disc(953 - radius, 562))
    wedge = disc(562, radius).union(disc(radius, 562)).convex_hull
    body = upright.union(wedge)
    x0, y0, x1, y1 = body.union(level).bounds
    tall, gap = .68, .13
    scale = tall / (y1 - y0)
    wide = (x1 - x0) * scale

    # the name, traced from the lockup and split into its two words
    word = np.pad(lockup[745:835, 750:1200], ((0, 0), (0, 6)))
    letters = polygons(trace(upscaled(word, 8)))
    split = 240 * 8  # pixels: the space between the words
    lines = [unary_union([letter for letter in letters if (letter.bounds[0] < split) == first]) for first in (True, False)]
    unit = .66 / (2 * 56 + 12) / 8  # two lines 56 lockup pixels tall with 12 between, on a block 0.66 m tall
    block = max(line.bounds[2] - line.bounds[0] for line in lines) * unit
    start = (LENGTH - (2 * wide + 2 * gap + block)) / 2

    def place(shape, u):
        return affinity.translate(affinity.scale(shape, scale, scale, origin=(0, 0)), u - x0 * scale, (HEIGHT - tall) / 2 - y0 * scale)

    layers = []
    for u in (start, start + wide + gap + block + gap):
        layers += [(accent, place(level, u)), ('#fbfafc', place(body, u))]
    for line, centre_v in zip(lines, (HEIGHT / 2 + (56 + 12) / 2 * 8 * unit, HEIGHT / 2 - (56 + 12) / 2 * 8 * unit)):
        lx0, _, lx1, _ = line.bounds
        layers.append(('#fbfafc', fit(line, (lx1 - lx0) * unit, (LENGTH / 2, centre_v))))
    return {'field': ground, 'top': ground, 'layers': layers}


def seventeenth_logo(sources: Path):
    """The 17th Ave logo in the units of its file, about a millimetre each on a barrier,
    without the worn texture it is drawn with: no specks, and its rough edges evened out
    to within 3 units."""
    return solid(outline((sources / 'seventeenth-ave-2022.svg').read_text(encoding='utf-8')), 200.0).simplify(3.0)


def seventeenth(sources: Path, count: int = 4):
    """Red ground and the logo in white, as the district's own barriers are painted, but
    with the logo at the full height of the face. Four fill the face, from one stencil
    used four times; one stands alone at the centre, from the same stencil."""
    logo = seventeenth_logo(sources)
    x0, y0, x1, y1 = logo.bounds
    tall = .68
    wide = tall * (x1 - x0) / (y1 - y0)
    gap = (LENGTH - count * wide) / (count + 1)
    return {'field': '#e21a2d', 'top': '#e21a2d', 'layers': [('#ffffff', fit(logo, wide, (gap + wide / 2 + k * (wide + gap), HEIGHT / 2))) for k in range(count)]}


DISTRICTS = {
    'kensington': kensington,
    'inglewood': inglewood,
    'fourth-street-purple': lambda sources: fourth_street(sources, 'purple'),
    'fourth-street-green': lambda sources: fourth_street(sources, 'green'),
    'seventeenth-ave': seventeenth,
    'seventeenth-ave-single': lambda sources: seventeenth(sources, 1),
}


# --- tiling the face ----------------------------------------------------------

def polygons(shape):
    if shape.is_empty:
        return []
    if isinstance(shape, Polygon):
        return [shape]
    return [part for part in getattr(shape, 'geoms', []) for part in polygons(part)]


def tile(design):
    """Cut the layers into regions that do not overlap, add the background around them,
    split everything at the bend, and triangulate. Returns vertices, triangles, colours."""
    face = box(0, 0, LENGTH, HEIGHT)
    regions, covered = [], Polygon()
    for tone, shape in design['layers']:
        shape = shape.buffer(0).intersection(face)
        regions.append((tone, shape.difference(covered)))
        covered = covered.union(shape)
    regions.append((design['field'], face.difference(covered)))
    halves = (box(0, 0, LENGTH, LOWER), box(0, LOWER, LENGTH, HEIGHT))
    pieces = [(tone, part) for tone, shape in regions for half in halves for part in polygons(shape.intersection(half)) if part.area > 1e-8]

    # Give every ring the vertices its neighbours have along a shared edge, so that the
    # separate triangulations meet point for point and leave no hairline gaps.
    def key(p):
        return (round(p[0], 5), round(p[1], 5))

    points = np.array(sorted({key(p) for _, part in pieces for ring in (part.exterior, *part.interiors) for p in ring.coords}))

    def densify(ring):
        coords = [key(p) for p in ring.coords[:-1]]
        out = []
        for a, b in zip(coords, coords[1:] + coords[:1]):
            out.append(a)
            ax, ay, bx, by = *a, *b
            length = math.hypot(bx - ax, by - ay)
            if length < 1e-6:
                continue
            t = ((points[:, 0] - ax) * (bx - ax) + (points[:, 1] - ay) * (by - ay)) / length ** 2
            off = np.abs((points[:, 0] - ax) * (by - ay) - (points[:, 1] - ay) * (bx - ax)) / length
            inside = (off < 2e-5) & (t > 1e-6) & (t < 1 - 1e-6)
            out.extend(key(p) for p in points[inside][np.argsort(t[inside])])
        return out

    colours, vertices, index, triangles = [], [], {}, []
    for tone, part in pieces:
        if tone not in colours:
            colours.append(tone)
        rings = [densify(part.exterior)] + [densify(ring) for ring in part.interiors]
        flat = np.array([p for ring in rings for p in ring], dtype=np.float64)
        ends = np.cumsum([len(ring) for ring in rings]).astype(np.uint32)
        for a, b, c in mapbox_earcut.triangulate_float64(flat, ends).reshape(-1, 3):
            corners = [tuple(flat[i]) for i in (a, b, c)]
            area = abs((corners[1][0] - corners[0][0]) * (corners[2][1] - corners[0][1]) - (corners[2][0] - corners[0][0]) * (corners[1][1] - corners[0][1])) / 2
            if area < 1e-9:
                continue
            ids = []
            for corner in corners:
                if corner not in index:
                    index[corner] = len(vertices)
                    vertices.append([round(corner[0], 5), round(corner[1], 5)])
                ids.append(index[corner])
            triangles.append([*ids, colours.index(tone)])
    area = sum(abs((vertices[b][0] - vertices[a][0]) * (vertices[c][1] - vertices[a][1]) - (vertices[c][0] - vertices[a][0]) * (vertices[b][1] - vertices[a][1])) / 2 for a, b, c, _ in triangles)
    assert abs(area - LENGTH * HEIGHT) < 2e-4, f'the tiling does not cover the face exactly: {area} of {LENGTH * HEIGHT}'
    return {'top': design['top'], 'colours': colours, 'vertices': vertices, 'triangles': triangles}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--sources', type=Path, required=True, help='directory holding the downloaded logo files')
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    baked = {'face': {'length': LENGTH, 'bend': round(LOWER, 6), 'height': round(HEIGHT, 6)}, 'sources': {}, 'districts': {}}
    for name in sorted(SOURCES):
        baked['sources'][name] = hashlib.sha256((args.sources / name).read_bytes()).hexdigest()
    for name, design in DISTRICTS.items():
        baked['districts'][name] = tile(design(args.sources))
        print(name, len(baked['districts'][name]['vertices']), 'vertices', len(baked['districts'][name]['triangles']), 'triangles', baked['districts'][name]['colours'])
    args.output.write_text(json.dumps(baked, separators=(',', ':')) + '\n', encoding='utf-8')
    print(args.output, args.output.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
