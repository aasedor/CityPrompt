"""Server placement contract for immutable canal and fixed-span bridge programs."""
import json
import math
import re

CONTRACTS = {
    'student_elevated_garden_rail_v1': ('elevated_garden_rail', 26, 48, 288),
    'skytrain_elevated_corridor_v0': ('skytrain_elevated_corridor', 26, 48, 288),
    'elevated_rail_transit_corridor_v0': ('elevated_rail_transit_corridor', 26, 48, 288),
    'amsterdam_gracht_v1': ('amsterdam_gracht', 36, 80, 320),
    'landmark_signature_bridge_v2': ('landmark_signature_bridge', 36, 260, 480),
}


def is_native_specialist(properties):
    props = properties or {}
    return props.get('road_selected_variant_id') in CONTRACTS and not props.get('validation_fixed_fixture')


def validate_specialist_ground(properties, boundary_properties):
    if not is_native_specialist(properties):
        return
    boundary = boundary_properties or {}
    if boundary.get('terrain_strategy') == 'landscape' or boundary.get('community_3d_mask_existing_tiles') is not True:
        raise ValueError('Keep this specialist street on a prepared level site with existing surfaces cleared.')


def validate_specialist_properties(properties):
    props = properties or {}
    if not is_native_specialist(props):
        return
    parent, width, minimum, maximum = CONTRACTS[props['road_selected_variant_id']]
    if props['road_selected_variant_id'] in ('student_elevated_garden_rail_v1','skytrain_elevated_corridor_v0','elevated_rail_transit_corridor_v0') and props.get('connect_to_public_road'):
        raise ValueError('Elevated rail cannot connect directly to an ordinary public road.')
    if props.get('road_archetype_id') != parent or props.get('width') != width:
        raise ValueError('Keep this specialist street’s original section and catalogue identity.')
    route = props.get('plan_centerline')
    if isinstance(route, str):
        try:
            route = json.loads(route)
        except ValueError:
            route = None
    if not isinstance(route, list) or len(route) < 2:
        raise ValueError('Draw two endpoints for this straight specialist street.')
    if any(not isinstance(p, list) or len(p) != 2 or any(isinstance(n, bool) or not isinstance(n, (int,float)) or not math.isfinite(n) for n in p) for p in route):
        raise ValueError('Specialist street route coordinates are invalid.')
    sx = 111320*math.cos(math.radians(route[0][1]))
    local = [((p[0]-route[0][0])*sx, (p[1]-route[0][1])*111320) for p in route]
    dx,dy = local[-1]
    length = math.hypot(dx,dy)
    if not minimum-.01 <= length <= maximum+.01:
        raise ValueError(f'Keep this route {minimum}–{maximum} m long for its complete crossing and approaches.')
    previous = -1
    for x,y in local:
        station = (x*dx+y*dy)/length
        if abs(x*dy-y*dx)/length > .05 or station < previous-.01:
            raise ValueError('Keep this specialist route straight; its structure cannot bend.')
        previous = station
    if props['road_selected_variant_id'] in ('skytrain_elevated_corridor_v0','elevated_rail_transit_corridor_v0'):
        stops = props.get('road_native_stops', [])
        if not isinstance(stops,list) or len(stops)>4:
            raise ValueError('Choose at most four elevated rail stations.')
        ids,positions=set(),[]
        for stop in stops:
            if not isinstance(stop,dict) or set(stop)!={'id','stationM'}:
                raise ValueError('A rail station must contain only its identity and position.')
            identity,position=stop['id'],stop['stationM']
            if not isinstance(identity,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',identity) or identity in ids:
                raise ValueError('A rail station needs a unique identity.')
            if isinstance(position,bool) or not isinstance(position,(int,float)) or not math.isfinite(position):
                raise ValueError('A rail station needs a valid position.')
            if position<24 or position>length-24+.001:
                raise ValueError('Leave 24 m at each route end for the complete station and stairs.')
            if any(abs(position-old)<52 for old in positions):
                raise ValueError('Place rail stations at least 52 m apart.')
            ids.add(identity);positions.append(position)
