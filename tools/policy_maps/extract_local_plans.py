"""Extract reviewed Urban Form PDF vectors using pinned, per-plan calibrations.

PDFs stay outside Git. Run with a plan ID, source PDF and explicit output path.
Hatching/frontage are additional policy guidance, not urban-form designations.
"""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np
from pyproj import Transformer
from shapely import set_precision
from shapely.geometry import LineString, Polygon, mapping
from shapely.ops import transform, unary_union

from extract_riley import path_geometry, path_parts, polygons


def hex_color(value):
    return '#' + ''.join(f'{round(v * 255):02x}' for v in value) if value else None


def extract(pdf, calibration):
    if hashlib.sha256(Path(pdf).read_bytes()).hexdigest() != calibration['source_sha256']:
        raise ValueError('PDF changed. Review its page, legend and alignment before extraction.')
    with fitz.open(pdf) as document:
        drawings = document[calibration['pdf_page'] - 1].get_drawings()
    # A common sub-millimetre grid prevents coincident PDF segments producing
    # non-noded intersections; all categories share the same precision model.
    boundary = set_precision(path_geometry(drawings[calibration['boundary_index']]), 1e-5)
    if not np.allclose(boundary.bounds, calibration['pdf_bounds'], atol=.002):
        raise ValueError('The reviewed PDF boundary no longer matches.')
    categories = calibration['categories']
    areas = {color: Polygon() for color in categories}
    # Only base-map fills occlude designations. Tiny dark filled dots and line
    # hatching are Special Policy Area / Comprehensive Planning Site symbols;
    # subtracting these would punch thousands of false holes into the areas.
    masks = set(calibration['mask_colors'])
    for index, drawing in enumerate(drawings):
        color = hex_color(drawing['fill'])
        if index < calibration['boundary_index'] or drawing['fill_opacity'] == 0 or color not in categories and color not in masks:
            continue
        geometry = set_precision(path_geometry(drawing), 1e-5).intersection(boundary)
        if geometry.is_empty:
            continue
        for key in areas:
            areas[key] = areas[key].difference(geometry)
        if color in areas:
            areas[color] = unary_union([areas[color], geometry])
    # Preserve the source's cartographic road gaps, including paired grey/white
    # strokes. These generalized map edges must not be represented as parcels.
    roads = []
    for drawing in drawings:
        if drawing['fill'] is None and drawing['stroke_opacity'] != 0 and hex_color(drawing['color']) == calibration['road_color']:
            for part in path_parts(drawing):
                if len(part) >= 2:
                    roads.append(LineString(part).buffer(drawing['width'] / 2, quad_segs=4))
    road_mask = unary_union(roads)
    matrix, offset = np.array(calibration['matrix']), np.array(calibration['translation'])
    inverse = Transformer.from_crs(calibration['crs'], 4326, always_xy=True)

    def world(x, y, z=None):
        east = matrix[0, 0]*np.array(x) + matrix[0, 1]*np.array(y) + offset[0]
        north = matrix[1, 0]*np.array(x) + matrix[1, 1]*np.array(y) + offset[1]
        return inverse.transform(east, north)

    geographic_boundary = set_precision(set_precision(transform(world, boundary), 1e-7), 0)
    features = []
    occupied = Polygon()
    for color, geometry in areas.items():
        pieces = [piece for piece in polygons(geometry.difference(road_mask)) if piece.area >= .01]
        geographic = unary_union([set_precision(set_precision(transform(world, piece), 1e-7), 0) for piece in pieces])
        # Rounding a shared edge with unequal vertex spacing can introduce a
        # centimetre-wide sliver. Resolve it once across the entire collection
        # so transparency never paints that area twice. Clear GEOS's inherited
        # fixed-precision model before these geographic booleans: repeatedly
        # snapping a large collection can collapse small road gaps and holes.
        geographic = geographic.intersection(geographic_boundary).difference(occupied)
        occupied = unary_union([occupied, geographic])
        for polygon in polygons(geographic):
            if not polygon.is_empty:
                features.append({'type': 'Feature', 'id': f"{calibration['id']}-urban-form-{len(features)+1}",
                                 'properties': {'category': categories[color], 'color': color},
                                 'geometry': mapping(polygon)})
    return {'type': 'FeatureCollection', 'snapshot': f"{calibration['id']}-urban-form-{calibration['source_sha256'][:12]}",
            'source': calibration['source_url'], 'sourcePage': calibration['pdf_page'],
            'boundary': mapping(geographic_boundary),
            'bounds': list(transform(world, boundary).bounds), 'features': features}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan')
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    calibration = json.loads((Path(__file__).parent / 'local_plan_calibrations.json').read_text())[args.plan]
    data = extract(args.pdf, calibration)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, separators=(',', ':')) + '\n', encoding='utf8')
    print(f"Extracted {len(data['features'])} polygons to {args.output}")
