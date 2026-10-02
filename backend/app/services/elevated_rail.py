"""Protect the complete landscaped viaduct from unsupported street overlaps."""
import math
from shapely.geometry import Polygon

VARIANTS = {'student_elevated_garden_rail_v1','skytrain_elevated_corridor_v0','elevated_rail_transit_corridor_v0'}
VARIANT = 'student_elevated_garden_rail_v1'  # preserved review/test identity


def validate_rail_overlap(candidate_coordinates, candidate_properties, neighbours):
    rail = candidate_properties.get('road_selected_variant_id') in VARIANTS
    origin = candidate_coordinates[0]
    sx = 111320 * math.cos(math.radians(origin[1]))
    def local(coords):
        return Polygon([((p[0]-origin[0])*sx, (p[1]-origin[1])*111320) for p in coords])
    candidate = local(candidate_coordinates)
    for coordinates, properties in neighbours:
        if not rail and properties.get('road_selected_variant_id') not in VARIANTS:
            continue
        if candidate.intersection(local(coordinates)).area > .01:
            raise ValueError('Keep other streets outside the elevated rail corridor; crossings and rail junctions are not supported.')
