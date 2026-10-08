"""Fetch a bounded Calgary Transit service snapshot for review before promotion.

python tools/policy_maps/fetch_transit_service.py --output <review-directory>
Routes and active stops are separate layers. Stop-route associations are published
separately and may have a different source update date. These are not live arrivals.
"""
import argparse
import datetime
import json
import math
from pathlib import Path
import requests

SOURCES = {'routes': 'hpnd-riq4', 'stops': 'muzh-c9qc', 'stop-routes': 'pm3p-838w'}
CATEGORIES = {name: 'service-' + name.lower() for name in ['BRT', 'EXPRESS', 'LRT', 'MAX', 'REGULAR', 'SCHOOL', 'SPECIAL']}


def checked_geometry(g, kind):
    if not g or g.get('type') != kind:
        raise ValueError('Missing or unexpected service geometry')
    def position(p):
        if len(p) < 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in p[:2]):
            raise ValueError('Invalid coordinates')
        if not (-115.5 < p[0] < -112.5 and 49.5 < p[1] < 52.5):
            raise ValueError('Outside Calgary region')
        return [round(v, 6) for v in p[:2]]
    if kind == 'Point':
        coords = position(g['coordinates'])
    else:
        if not g['coordinates'] or any(len(line) < 2 for line in g['coordinates']):
            raise ValueError('Empty route geometry')
        coords = [[position(p) for p in line] for line in g['coordinates']]
    return {'type': kind, 'coordinates': coords}


def build_snapshots(route_rows, stop_rows, associations, sources):
    routes, stops, stop_routes = [], [], {}
    for row in associations:
        number = str(row.get('route_short_name', '')).strip()
        if number:
            stop_routes.setdefault(str(row['teleride_number']), {})[number] = row.get('route_long_name', '')
    for row in route_rows:
        category = CATEGORIES.get(row.get('route_category'))
        if not category: raise ValueError('Unreviewed route category')
        routes.append({'type': 'Feature', 'id': row['globalid'], 'properties': {
            'category': category, 'source': 'routes', 'routeNumber': str(row['route_short_name']),
            'name': row['route_long_name'], 'designation': row['route_category']},
            'geometry': checked_geometry(row.get('multilinestring'), 'MultiLineString')})
    for row in stop_rows:
        if row.get('status') == 'INACTIVE': continue
        if row.get('status') != 'ACTIVE': raise ValueError('Unreviewed stop status')
        number = str(row['teleride_number'])
        stops.append({'type': 'Feature', 'id': row['globalid'], 'properties': {
            'category': 'service-stop', 'source': 'stops', 'stopNumber': number,
            'name': row['stop_name'], 'designation': 'ACTIVE',
            'routes': [{'number': n, 'name': name} for n, name in sorted(stop_routes.get(number, {}).items(), key=lambda pair: pair[0].zfill(8))]},
            'geometry': checked_geometry(row.get('point'), 'Point')})
    def snapshot(network, features):
        if len({f['id'] for f in features}) != len(features): raise ValueError('Duplicate service identity')
        return {'type': 'FeatureCollection', 'network': network,
                'retrieved': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'sources': sources,
                'featureCount': len(features), 'features': sorted(features, key=lambda f: f['id'])}
    return snapshot('service-routes', routes), snapshot('service-stops', stops)


def fetch_source(identity):
    url = f'https://data.calgary.ca/resource/{identity}.json'
    def get(params):
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    meta_response = requests.get(f'https://data.calgary.ca/api/views/{identity}.json', timeout=30)
    meta_response.raise_for_status()
    meta = meta_response.json()
    count = int(get({'$select': 'count(*)'})[0]['count'])
    rows = []
    for offset in range(0, count, 1000):
        part = get({'$limit': 1000, '$offset': offset, '$order': ':id'})
        if len(part) != min(1000, count - offset): raise ValueError('Incomplete service snapshot')
        rows.extend(part)
    # Reject a changing source so a refresh cannot quietly publish mixed pages.
    after = requests.get(f'https://data.calgary.ca/api/views/{identity}.json', timeout=30)
    after.raise_for_status()
    if after.json().get('rowsUpdatedAt') != meta.get('rowsUpdatedAt'): raise ValueError('Source changed while downloading')
    return rows, {'url': f'https://data.calgary.ca/d/{identity}', 'featureCount': count,
                  'updated': datetime.datetime.fromtimestamp(meta['rowsUpdatedAt'], datetime.timezone.utc).isoformat()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    rows, sources = {}, {}
    for name, identity in SOURCES.items():
        rows[name], sources[name] = fetch_source(identity)
        print(name, len(rows[name]), flush=True)
    args.output.mkdir(parents=True, exist_ok=True)
    for snapshot in build_snapshots(rows['routes'], rows['stops'], rows['stop-routes'], sources):
        path = args.output / (snapshot['network'] + '.geojson')
        path.write_text(json.dumps(snapshot, separators=(',', ':')) + '\n', encoding='utf-8')
        print(path.name, snapshot['featureCount'], path.stat().st_size, flush=True)
