"""Finite brt-v004 route/stop placement validation; no client asset identities."""
import json
import math
import re

VARIANT = 'brt_bus_rapid_transit_corridor_v0'


def is_native_brt(properties):
    props = properties or {}
    return props.get('road_selected_variant_id') == VARIANT and not props.get('validation_fixed_fixture')


def validate_brt_ground(properties, boundary_properties):
    if not is_native_brt(properties):
        return
    boundary = boundary_properties or {}
    if boundary.get('terrain_strategy') == 'landscape' or boundary.get('community_3d_mask_existing_tiles') is not True:
        raise ValueError('Keep this BRT corridor on a prepared level site with existing surfaces cleared.')


def validate_brt_properties(properties):
    props = properties or {}
    if not is_native_brt(props):
        return
    if props.get('road_archetype_id') != 'brt_bus_rapid_transit_corridor' or props.get('width') != 40:
        raise ValueError('This BRT program requires its original 40 m section and catalogue identity.')
    points = props.get('plan_centerline')
    if isinstance(points, str):
        try:
            points = json.loads(points)
        except ValueError:
            points = None
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError('BRT needs an explicit saved route with two endpoints.')
    if any(not isinstance(p, list) or len(p) != 2 or any(isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) for v in p) for p in points):
        raise ValueError('BRT route coordinates are invalid.')
    sx = 111320 * math.cos(math.radians(points[0][1]))
    local = [((p[0]-points[0][0])*sx,(p[1]-points[0][1])*111320) for p in points]
    dx,dy = local[-1]; length = math.hypot(dx,dy)
    if not 99.99 <= length <= 480.01:
        raise ValueError('BRT needs a straight route 100–480 m long.')
    previous = -1
    for x,y in local:
        along = (x*dx+y*dy)/length
        if abs(x*dy-y*dx)/length > .05 or along < previous-.01:
            raise ValueError('Keep this BRT corridor straight; its platform and crossing remain full size.')
        previous = along
    stops = props.get('road_native_stops', [])
    if not isinstance(stops,list) or len(stops)>8:
        raise ValueError('BRT supports at most eight manually selected stops.')
    ids,positions = set(),[]
    for stop in stops:
        if not isinstance(stop,dict) or set(stop)!={'id','stationM'}:
            raise ValueError('A BRT stop must contain only its identity and position.')
        identity,station = stop['id'],stop['stationM']
        if not isinstance(identity,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',identity) or identity in ids:
            raise ValueError('A BRT stop has an invalid or duplicate identity.')
        if isinstance(station,bool) or not isinstance(station,(int,float)) or not math.isfinite(station):
            raise ValueError('A BRT stop has an invalid position.')
        if station<21 or station+33.5>length+.001:
            raise ValueError('Leave 21 m before a stop and 33.5 m after it for the full platform, ramps and crossing.')
        if any(abs(p-station)<56.5 for p in positions):
            raise ValueError('Separate BRT stops by at least 56.5 m.')
        ids.add(identity);positions.append(station)
