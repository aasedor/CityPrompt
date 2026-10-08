"""Fetch a bounded, dated official transport snapshot; never georeference PDF pixels.

python tools/policy_maps/fetch_transport_vectors.py --output <review-directory>
Review before promoting the two GeoJSON files into frontend/public/policy-maps/transport-vectors-v1.
"""
import argparse
import datetime
import json
import math
from pathlib import Path
import requests

BASE = 'https://services1.arcgis.com/AVP60cs0Q9PEA8rH/arcgis/rest/services/'
FIVE_A = ['Recommended_Pathway_Priority', 'Existing_Pathway_Priority',
          'Recommended_On_Street_Bikeway_Priority', 'Existing_On_Street_Bikeway_Priority',
          'Recommended_Pathway_Secondary', 'Recommended_On_Street_Bikeway_Secondary']
TRANSIT = ['Municipal_Development_Plan_Primary_Transit_Network_Lines',
           'Municipal_Development_Plan_Primary_Transit_Network_Points']
CATEGORIES = {'PROPOSED PATHWAY': 'proposed-pathway', 'EXISTING PATHWAY': 'existing-pathway',
              'PROPOSED ONSTREETBIKEWAY': 'proposed-bikeway', 'EXISTING ONSTREETBIKEWAY': 'existing-bikeway',
              'Primary Transit Network': 'primary-transit', 'Primary Transit Network to be determined': 'transit-undetermined',
              'Skeletal Light Rail Transit': 'lrt', 'Skeletal Light Rail Transit Future': 'future-lrt',
              'Primary Transit Hub': 'hub', 'Transit Centre': 'transit-centre',
              'Regional/ Inter City Gateway Hub': 'regional-hub'}


def normalize_feature(row, network, source):
    p = row['properties']
    designation = p.get('CLASS_5A') if network == '5a' else p.get('DESCRIPTION', p.get('description'))
    if designation not in CATEGORIES: raise ValueError(f'Unreviewed designation: {designation}')
    g = row.get('geometry')
    if not g or g.get('type') not in ('Point', 'LineString', 'MultiLineString'): raise ValueError('Invalid geometry')
    def coordinates(value):
        if not isinstance(value, list) or not value: raise ValueError('Empty coordinates')
        if isinstance(value[0], (int, float)):
            if len(value) < 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in value[:2]): raise ValueError('Invalid position')
            if not (-115.5 < value[0] < -112.5 and 49.5 < value[1] < 52.5): raise ValueError('Outside Calgary region')
            return [round(value[0], 6), round(value[1], 6)]
        return [coordinates(v) for v in value]
    identity = p.get('GLOBALID') or p.get('GLOBALID_GUID') or p.get('globalid') or p.get('GLOABID') or p.get('gloabid')
    if not identity: raise ValueError('Missing stable feature ID')
    return {'type': 'Feature', 'id': identity, 'properties': {'category': CATEGORIES[designation],
            'designation': designation, 'priority': p.get('PRIORITY_5A'), 'source': source},
            'geometry': {'type': g['type'], 'coordinates': coordinates(g['coordinates'])}}


def group_routes(features):
    """Compress repeated cartographic attributes without moving any vertices."""
    groups = {}
    for feature in sorted(features.values(), key=lambda f: f['id']):
        p = feature['properties']
        key = f"{p['category']}:{p['priority'] or 'unspecified'}:{p['source']}"
        group = groups.setdefault(key, {'type': 'Feature', 'id': key, 'properties': p,
                                       'geometry': {'type': 'MultiLineString', 'coordinates': []}})
        g = feature['geometry']
        if g['type'] not in ('LineString', 'MultiLineString'):
            raise ValueError('5A routes must be lines')
        group['geometry']['coordinates'].extend([g['coordinates']] if g['type'] == 'LineString' else g['coordinates'])
    return groups


def fetch_network(network, services):
    features, sources = {}, {}
    for service in services:
        url = BASE + service + '/FeatureServer/0'
        def query(**params):
            response = requests.post(url + '/query', data={'f': 'json', 'where': '1=1', **params}, timeout=60)
            response.raise_for_status()
            data = response.json()
            if 'error' in data: raise ValueError(data['error'])
            return data
        ids = sorted(query(returnIdsOnly='true')['objectIds'])
        sources[service] = {'url': url, 'featureCount': len(ids)}
        found = 0
        for start in range(0, len(ids), 500):
            part = ids[start:start + 500]
            data = query(f='geojson', objectIds=','.join(map(str, part)), outFields='*', outSR=4326)
            rows = data.get('features', [])
            if len(rows) != len(part) or data.get('exceededTransferLimit'): raise ValueError('Incomplete source response')
            found += len(rows)
            for row in rows:
                feature = normalize_feature(row, network, service)
                # Several published views overlap. Render the official feature only once.
                old = features.get(feature['id'])
                if old and (old['geometry'] != feature['geometry'] or any(old['properties'][key] != feature['properties'][key] for key in ('category', 'priority'))):
                    raise ValueError('Conflicting official feature IDs')
                features.setdefault(feature['id'], feature)
        print(service, found, flush=True)
    # Cartographic route inspection needs designation/priority, not an individual
    # database segment row. Group identical attributes without simplifying or
    # snapping any coordinates; this removes repeated metadata from the payload.
    raw_count = len(features)
    if network == '5a':
        features = group_routes(features)
    return {'type': 'FeatureCollection', 'network': network, 'retrieved': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'sources': sources, 'sourceFeatureCount': raw_count, 'featureCount': len(features),
            'features': sorted(features.values(), key=lambda f: f['id'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, services in [('transit', TRANSIT), ('5a', FIVE_A)]:
        data = fetch_network(name, services)
        target = args.output / (name + '.geojson')
        target.write_text(json.dumps(data, separators=(',', ':')) + '\n', encoding='utf-8')
        print(name, data['featureCount'], target.stat().st_size, 'bytes', flush=True)
