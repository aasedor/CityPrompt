"""Create one isolated local review project; reuses its checkpoint on reruns."""
import argparse
import json
import math
from pathlib import Path
import httpx

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
checkpoint = args.output_dir / 'local-project.json'
if checkpoint.exists():
    previous = json.loads(checkpoint.read_text())
    if len(previous.get('zones', [])) != 7:
        raise SystemExit(f'Incomplete pilot checkpoint: {checkpoint}. Inspect the saved project before resuming; no duplicate project was created.')
    print(json.dumps({'existing': previous['project']['id'], 'zones': 7}))
    raise SystemExit(0)
client = httpx.Client(base_url='http://127.0.0.1:8001/api/v1', timeout=60)
login = client.post('/auth/login', json={'email': 'studio-smoke@example.com', 'password': 'Studio-local-2027!'})
login.raise_for_status()
client.headers['Authorization'] = 'Bearer ' + login.json()['access_token']
def request(method, url, data=None):
    response = client.request(method, url, json=data)
    response.raise_for_status()
    return response.json()
lat, lng = 51.04542, -114.04677
east = 111320 * math.cos(math.radians(lat))
def ll(x, y): return [lng + x / east, lat + y / 111320]
def box(x, y, w, h): return [ll(x-w/2, y-h/2), ll(x+w/2, y-h/2), ll(x+w/2, y+h/2), ll(x-w/2, y+h/2)]
project = request('POST', '/projects/', {'name': 'Neighbourhood park — adaptive rustic pilot', 'description': 'One reference-locked park pilot on the open Fort Calgary field. Local visual review only.', 'location': {'latitude': lat, 'longitude': lng}})
record = {'project': project, 'zones': []}
checkpoint.parent.mkdir(parents=True, exist_ok=True)
checkpoint.write_text(json.dumps(record, indent=2))
def zone(name, kind, coordinates, props):
    result = request('POST', f"/site-zones/projects/{project['id']}/zones", {'name': name, 'zone_type': kind, 'coordinates': coordinates, 'properties': props, 'color': '#76a557' if kind == 'green_space' else '#909090', 'sort_order': len(record['zones'])})
    record['zones'].append(result)
    checkpoint.write_text(json.dumps(record, indent=2))
zone('Open field — shared ground', 'site_boundary', box(0, 9.5, 90, 93), {'community_3d_mask_existing_tiles': False})
zone('Rustic neighbourhood park — 70 × 55 m', 'green_space', box(0, -8, 70, 55), {'green_space_archetype_id': 'neighborhood_park', 'green_space_selected_variant_id': 'neighborhood_park_v0', 'neighborhood_park_layout': 'adaptive_rustic_v1'})
zone('Neighbourhood street with sidewalks', 'road', box(0, 26, 86, 10), {'road_archetype_id': 'narrow_residential_street', 'width': 10, 'road_width': 10, 'plan_centerline': [ll(-43, 26), ll(43, 26)]})
zone('Park-side walkway', 'road', box(39, -8, 3, 55), {'road_archetype_id': 'multi_use_trail', 'width': 3, 'road_width': 3, 'plan_centerline': [ll(39, -35.5), ll(39, 19.5)]})
for name, x, archetype, variant, w, h, floors in [
    ('Vancouver Special', -27, 'vancouver_special', 'special_original_1970s', 18, 16, 2),
    ('Corner cafe', 0, 'amsterdam_brown_cafe', 'brown_cafe_corner', 18, 16, 1),
    ('Calgary infill', 27, 'calgary_modern_infill_house', 'infill_flat_roof_minimal', 15, 17, 2),
]:
    zone(name, 'building', box(x, 43, w, h), {'development_archetype_id': archetype, 'development_selected_variant_id': variant, 'height': floors * 3.5, 'floors': floors, 'target_w_m': w, 'target_d_m': h})
print(json.dumps({'project': project['id'], 'zones': len(record['zones']), 'url': f"http://127.0.0.1:5174/projects/{project['id']}"}))
