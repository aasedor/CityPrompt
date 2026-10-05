"""Extract a reviewed Riley Urban Form PDF snapshot; no OCR or invented geometry.

Usage: python tools/policy_maps/extract_riley.py approved.pdf --output map.json
Requires PyMuPDF, shapely, numpy, pyproj. Calibration is pinned to this PDF hash.
See docs/RILEY_POLICY_MAP_PILOT.md for the independent street checks and limits.
"""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np
from pyproj import Transformer
from shapely import make_valid, set_precision
from shapely.geometry import LineString, Polygon, mapping
from shapely.ops import transform, unary_union

HERE = Path(__file__).resolve().parent
CATEGORIES = {
    '#e4002b': 'Neighbourhood Commercial', '#ed9d4d': 'Neighbourhood Flex',
    '#fedb00': 'Neighbourhood Connector', '#fff4b2': 'Neighbourhood Local',
    '#a5192e': 'Commercial Centre', '#a9c23f': 'Natural Areas',
    '#70a355': 'Parks and Open Space', '#4db69f': 'City Civic and Recreation',
    '#b2e0d5': 'Private Institutional and Recreation',
}


def path_parts(drawing):
    """Preserve disconnected subpaths; sample Beziers at <=0.25 PDF pt intervals."""
    parts, current = [], []
    for item in drawing['items']:
        op = item[0]
        if op == 're':
            if current:
                parts.append(current)
                current = []
            rect = item[1]
            parts.append([(rect.x0, rect.y0), (rect.x1, rect.y0),
                          (rect.x1, rect.y1), (rect.x0, rect.y1), (rect.x0, rect.y0)])
            continue
        if op not in ('l', 'c'):
            raise ValueError(f'Unsupported PDF path operator: {op}')
        start = tuple(item[1])
        if current and np.linalg.norm(np.array(current[-1]) - start) > .002:
            parts.append(current)
            current = []
        if not current:
            current.append(start)
        if op == 'l':
            current.append(tuple(item[2]))
        else:
            a, b, c, end = (np.array(p) for p in item[1:])
            length = np.linalg.norm(b-a) + np.linalg.norm(c-b) + np.linalg.norm(end-c)
            count = max(4, int(np.ceil(length / .25)))
            for t in np.linspace(0, 1, count + 1)[1:]:
                current.append(tuple((1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*end))
    if current:
        parts.append(current)
    return parts


def path_geometry(drawing):
    rings = [make_valid(Polygon(part)) for part in path_parts(drawing) if len(part) >= 3]
    if not rings:
        return Polygon()
    if len(rings) > 1 and not drawing['even_odd']:
        raise ValueError('Multiple non-even-odd subpaths require a reviewed winding implementation')
    result = rings[0]
    for ring in rings[1:]:
        result = result.symmetric_difference(ring)
    return make_valid(result)


def polygons(geometry):
    if geometry.geom_type == 'Polygon':
        yield geometry
    elif hasattr(geometry, 'geoms'):
        for part in geometry.geoms:
            yield from polygons(part)


def extract(pdf, calibration):
    digest = hashlib.sha256(Path(pdf).read_bytes()).hexdigest()
    if digest != calibration['source_sha256']:
        raise ValueError('PDF changed. Recheck the map page, paths, colours and alignment before extraction.')
    with fitz.open(pdf) as document:
        drawings = document[23].get_drawings()
    boundary = path_geometry(drawings[2])
    assert np.allclose(boundary.bounds, calibration['pdf_bounds'], atol=.002)
    areas = {color: Polygon() for color in CATEGORIES}
    for index, drawing in enumerate(drawings):
        if index < 3 or not drawing['fill'] or drawing['rect'].x0 >= 1000:
            continue  # Background and legend are not geographical features.
        color = '#' + ''.join(f'{round(v * 255):02x}' for v in drawing['fill'])
        if color == '#0085ad':
            continue  # Active frontage is a separate policy symbol, not urban form.
        geometry = path_geometry(drawing).intersection(boundary)
        if geometry.is_empty:
            continue
        for key in areas:
            areas[key] = areas[key].difference(geometry)
        if color in areas:
            areas[color] = unary_union([areas[color], geometry])

    # In the published map, road strokes mask colour fills. Preserve their
    # cartographic gaps; these are NOT cadastral road/parcel boundaries.
    roads = []
    for drawing in drawings:
        if drawing['fill'] is None and drawing['color'] and all(abs(c-.6) < .001 for c in drawing['color']):
            for part in path_parts(drawing):
                if len(part) >= 2:
                    roads.append(LineString(part).buffer(drawing['width'] / 2, quad_segs=4))
    road_mask = unary_union(roads)
    matrix = np.array(calibration['matrix'])
    offset = np.array(calibration['translation'])
    inverse = Transformer.from_crs(calibration['crs'], 4326, always_xy=True)

    def world(x, y, z=None):
        east = matrix[0, 0]*np.array(x) + matrix[0, 1]*np.array(y) + offset[0]
        north = matrix[1, 0]*np.array(x) + matrix[1, 1]*np.array(y) + offset[1]
        lon, lat = inverse.transform(east, north)
        return lon, lat

    features = []
    for color, geometry in areas.items():
        # Preserve shared edges: simplifying categories independently can create
        # thin overlaps, which would darken a transparent overlay.
        for piece in polygons(geometry.difference(road_mask)):
            if piece.area < .01:
                continue  # <0.31 m² PDF intersection slivers.
            # Topology-aware precision reduction removes collapsed micro-edges.
            geographic = set_precision(transform(world, piece), 1e-7)
            for polygon in polygons(geographic):
                if polygon.is_empty:
                    continue
                features.append({'type': 'Feature', 'id': f'riley-urban-form-{len(features)+1}',
                                 'properties': {'category': CATEGORIES[color], 'color': color},
                                 'geometry': mapping(polygon)})
    return {'type': 'FeatureCollection', 'snapshot': 'riley-urban-form-38P2025-v1',
            'source': calibration['source_url'], 'sourcePage': 24,
            'boundary': mapping(set_precision(transform(world, boundary), 1e-7)),
            'bounds': list(transform(world, boundary).bounds), 'features': features}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = extract(args.pdf, json.loads((HERE / 'riley_calibration.json').read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, separators=(',', ':')) + '\n', encoding='utf8')
    print(f"Extracted {len(data['features'])} polygons to {args.output}")
