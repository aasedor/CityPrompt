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

SOURCES = ('kensington-2026.svg', 'inglewood-2026-horizontal.jpg', 'fourth-street-header.png', 'fourth-favicon.ico', '4th-street-logo.png')


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
    """Filled area of every path in an SVG, as geometry in its own units with y up.
    Subpaths are combined by the even-odd rule, which suits a logo whose only overlaps
    are counters cut out of letters."""
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
    return affinity.scale(shape, 1, -1, origin=(0, 0))


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


def hexcolour(rgb) -> str:
    return '#' + ''.join(f'{round(float(v)):02x}' for v in rgb[:3])


# --- the three districts -----------------------------------------------------

def kensington(sources: Path):
    """Burgundy roundel and wordmark on the off-white of the district's website."""
    logo = fit(outline((sources / 'kensington-2026.svg').read_text(encoding='utf-8')), 2.56, (LENGTH / 2, HEIGHT / 2))
    return {'field': '#f8f8f8', 'top': '#42031a', 'layers': [('#42031a', logo)]}


def inglewood(sources: Path):
    """Yellow wordmark on red: the district's 2026 horizontal logo."""
    image = np.array(Image.open(sources / 'inglewood-2026-horizontal.jpg').convert('RGB')).astype(int)
    wordmark = fit(trace(image[:, :, 1] > 128), 2.62, (LENGTH / 2, HEIGHT / 2))
    return {'field': '#d84d2c', 'top': '#d84d2c', 'layers': [('#fec93c', wordmark)]}


def fourth_street(sources: Path, colourway: str):
    """The rounded 4 and the wordmark. The 4 is rebuilt from its geometry: an upright
    bar and a level bar with round ends, and the wedge that joins their tips. Its
    gradients become bands whose colours are sampled from the district's own artwork."""
    lockup = np.array(Image.open(sources / 'fourth-street-header.png').convert('RGBA'))[:, :, 3]
    radius, size = 129.0, 954.0  # pixels of the lockup file, rows running down

    def disc(x, y):
        return Point(x, size - y).buffer(radius, 12)

    upright = box(433, radius, 691, size - radius).union(disc(562, radius)).union(disc(562, size - radius))
    level = box(radius, size - 691, 953 - radius, size - 433).union(disc(radius, 562)).union(disc(953 - radius, 562))
    wedge = disc(562, radius).union(disc(radius, 562)).convex_hull

    if colourway == 'green':
        art = np.array(Image.open(sources / 'fourth-favicon.ico').convert('RGBA')).astype(float)
        inked = art[:, :, 3] > 200
    else:
        art = np.array(Image.open(sources / '4th-street-logo.png').convert('RGBA')).astype(float)
        inked = (art[:, :, :3].sum(axis=2) < 600)
        inked[100:, :] = False  # the wordmark sits below the 4 in this file
    rows, cols = np.nonzero(inked.any(axis=1))[0], np.nonzero(inked.any(axis=0))[0]
    left, right, top, bottom = cols.min(), cols.max() + 1, rows.min(), rows.max() + 1

    def sample(x: float, y: float) -> str:
        """Colour of the artwork at a point of the 4, in lockup pixels with rows running down."""
        px, py = left + (right - left) * x / 953, top + (bottom - top) * y / size
        span = max(1, round((right - left) / 80))
        patch = art[int(py) - span:int(py) + span + 1, int(px) - span:int(px) + span + 1, :3]
        keep = inked[int(py) - span:int(py) + span + 1, int(px) - span:int(px) + span + 1]
        return hexcolour(np.median(patch[keep], axis=0))

    def bands(shape, axis: int, count: int, probe, reach=None):
        """Slice a shape into strips along x or y, each in the colour found at its probe
        point. reach stops the slicing early; the last strip then takes the rest."""
        x0, y0, x1, y1 = shape.bounds
        far = reach if reach is not None else (x1 if axis == 0 else y1)
        out = []
        for k in range(count):
            a, b = k / count, (k + 1) / count
            lo, hi = (x0, far) if axis == 0 else (y0, far)
            start, stop = lo + (hi - lo) * a, lo + (hi - lo) * b if k < count - 1 else (x1 if axis == 0 else y1)
            strip = box(start, y0, stop, y1) if axis == 0 else box(x0, start, x1, stop)
            out.append((sample(*probe((a + b) / 2)), shape.intersection(strip)))
        return out

    def clear_of_level(t: float) -> float:
        """The level bar hides the middle of the upright; sample a band it partly covers just clear of it."""
        return t if not .43 < t < .745 else .42 if t < .59 else .755

    # Top to bottom: the level bar, then the upright, then the wedge. Lower layers are cut
    # by the ones above when the face is tiled, so the parts share their edges exactly.
    parts = bands(level, 0, 7, lambda t: (40 + 873 * t, 562))
    parts += bands(upright, 1, 8, lambda t: (562, 30 + 894 * clear_of_level(1 - t)))
    # the wedge shows only above the level bar, so each band is sampled midway up that visible part
    parts += bands(wedge, 0, 4, lambda t: (140 + 270 * t, (508.6 - (140 + 270 * t) + 433) / 2), reach=433)
    x0, y0, _, y1 = unary_union([upright, level, wedge]).bounds
    scale, origin_u, origin_v = .62 / (y1 - y0), .385, HEIGHT / 2 - .31

    def place(shape):
        return affinity.translate(affinity.scale(shape, scale, scale, origin=(0, 0)), origin_u - x0 * scale, origin_v - y0 * scale)

    word = np.pad(lockup[745:835, 750:1200], ((0, 0), (0, 6)))
    wordmark = fit(trace(upscaled(word, 8)), 1.45, (origin_u + .62 + .16 + .725, HEIGHT / 2 - .045))
    return {'field': '#fbfafc', 'top': sample(562, 200), 'layers': [(tone, place(shape)) for tone, shape in parts] + [('#1c1c1e', wordmark)]}


DISTRICTS = {
    'kensington': kensington,
    'inglewood': inglewood,
    'fourth-street-purple': lambda sources: fourth_street(sources, 'purple'),
    'fourth-street-green': lambda sources: fourth_street(sources, 'green'),
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
