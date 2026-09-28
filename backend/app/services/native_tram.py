"""Exact grass tram section and deliberately positioned whole stop assemblies."""
import json
import math
import re

VARIANT = 'student_grass_tram_avenue_v1'


def is_native_tram(properties):
    return (properties or {}).get('road_selected_variant_id') == VARIANT and not (properties or {}).get('validation_fixed_fixture')


def validate_tram_ground(properties, boundary_properties):
    if not is_native_tram(properties):
        return
    boundary = boundary_properties or {}
    if boundary.get('terrain_strategy') == 'landscape' or boundary.get('community_3d_mask_existing_tiles') is not True:
        raise ValueError('Keep this tram avenue on a prepared level site with existing surfaces cleared.')


def validate_tram_properties(properties):
    props = properties or {}
    if not is_native_tram(props):
        return
    if props.get('road_archetype_id') != 'light_rail_tram_avenue' or props.get('width') != 22:
        raise ValueError('Garden Tram Avenue requires its original 22 m section and catalogue identity.')
    points = props.get('plan_centerline')
    if isinstance(points, str):
        try:
            points = json.loads(points)
        except ValueError:
            points = None
    if not isinstance(points, list) or len(points) < 2 or any(not isinstance(p, list) or len(p) != 2 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in p) for p in points):
        raise ValueError('Draw the tram route with two valid endpoints.')
    sx = 111320 * math.cos(math.radians(points[0][1]))
    local = [((p[0]-points[0][0])*sx,(p[1]-points[0][1])*111320) for p in points]
    dx,dy = local[-1]; length = math.hypot(dx,dy)
    if not 47.99 <= length <= 480.01:
        raise ValueError('Garden Tram Avenue needs a straight route 48–480 m long.')
    previous = -1
    for x,y in local:
        along = (x*dx+y*dy)/length
        if abs(x*dy-y*dx)/length > .05 or along < previous-.01:
            raise ValueError('Keep this tram avenue straight so tracks, wires and platforms remain aligned.')
        previous = along
    stops = props.get('road_native_stops', [])
    if not isinstance(stops,list) or len(stops)>8:
        raise ValueError('Choose at most eight tram stops.')
    ids,positions = set(),[]
    for stop in stops:
        if not isinstance(stop,dict) or set(stop)!={'id','stationM'}:
            raise ValueError('A tram stop must contain only its identity and position.')
        identity,station = stop['id'],stop['stationM']
        if not isinstance(identity,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',identity) or identity in ids:
            raise ValueError('A tram stop needs a unique identity.')
        if isinstance(station,bool) or not isinstance(station,(int,float)) or not math.isfinite(station):
            raise ValueError('A tram stop needs a valid position.')
        if station<15 or station>length-15+.001:
            raise ValueError('Leave 15 m at each end for the complete tram platform and ramps.')
        if any(abs(p-station)<32 for p in positions):
            raise ValueError('Place tram stops at least 32 m apart.')
        ids.add(identity);positions.append(station)
