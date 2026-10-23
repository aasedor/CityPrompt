"""Exact, fixed public-realm review scenes; never a production capability."""
from __future__ import annotations

import json
import math
from pathlib import Path

from app.core.config import get_settings

MANIFEST = Path(__file__).resolve().parents[3] / 'frontend/src/data/claudeAssetLocalTrial.json'


def validate_local_claude_public_realm(zone_type, geometry, properties) -> bool:
    claimed = any(str(properties.get(key, '')).startswith('claude_trial_')
                  for key in ('pick_place_asset', 'public_realm_trial_asset'))
    if not claimed:
        return False
    if get_settings().app_env.lower() != 'development':
        raise ValueError('Claude fixed-model trials are available only in local development.')
    try:
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ValueError('Local fixed-model trial manifest is unavailable.') from error
    if manifest.get('local_trial_only') is not True or manifest.get('schema') != 'cityprompt.claude-local-trial@1':
        raise ValueError('Local fixed-model trial manifest has an invalid scope.')
    rows = [row for row in manifest['models'] if row['asset']['id'] == properties.get('pick_place_asset')
            and row.get('fixture') is not None]
    if len(rows) != 1:
        raise ValueError('The exact local fixed-model trial is unavailable.')
    row = rows[0]
    asset, fixture = row['asset'], row['fixture']
    expected = asset['properties']
    keys = ('validation_fixed_fixture', 'validation_native_url', 'public_realm_trial_asset',
            'road_archetype_id', 'road_selected_variant_id',
            'green_space_archetype_id', 'green_space_selected_variant_id')
    if (zone_type != asset['zoneType'] or properties.get('pick_place_model_revision') != asset['model']['revision']
            or fixture['sha256'] != row.get('runtime_sha256', row['source_sha256'])
            or any(properties.get(key) != expected.get(key) for key in keys)):
        raise ValueError('The local fixed-model trial identity or revision does not match.')
    if geometry.geom_type != 'Polygon' or geometry.interiors:
        raise ValueError('Keep the complete fixed scene in its native rectangle.')
    ring = list(geometry.exterior.coords)[:-1]
    if len(ring) != 4 or any(not math.isfinite(v) for point in ring for v in point):
        raise ValueError('Keep the complete fixed scene in its native rectangle.')
    lng, lat = (sum(point[i] for point in ring)/4 for i in (0, 1))
    east = 111320*math.cos(math.radians(lat))
    points = [((point[0]-lng)*east, (point[1]-lat)*111320) for point in ring]
    yaw = math.atan2(points[1][1]-points[0][1], points[1][0]-points[0][0])
    c, s = math.cos(yaw), math.sin(yaw)
    width, depth = fixture['dimensions']
    corners = [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]
    if any(math.hypot(p[0]-(x*c-y*s), p[1]-(x*s+y*c)) > .04
           for p, (x, y) in zip(points, corners)):
        raise ValueError('Keep the complete fixed scene at native size; move and rotate only.')
    return True
