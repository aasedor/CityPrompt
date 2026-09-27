"""Server placement contract for immutable canal and fixed-span bridge programs."""
import json
import math

CONTRACTS = {
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
        raise ValueError('Keep the canal or bridge on a prepared level site with existing surfaces cleared.')


def validate_specialist_properties(properties):
    props = properties or {}
    if not is_native_specialist(props):
        return
    parent, width, minimum, maximum = CONTRACTS[props['road_selected_variant_id']]
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
