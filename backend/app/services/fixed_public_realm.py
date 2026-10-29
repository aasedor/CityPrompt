"""Hash-bound fixed native public-realm scenes, separate from DEV fixtures.

No publication authority is inferred from the source review or context-removal
review. Exact visual/runtime approval is mandatory outside local rehearsal.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import re

from app.core.config import get_settings

MANIFEST = Path(__file__).resolve().parents[1] / 'data/public_realm_release_20261023.json'
OWNERSHIP_MANIFEST = MANIFEST.with_name('public_realm_ownership_contracts.json')


def _ownership_identity_valid(fixture, properties):
    try:
        contracts = json.loads(OWNERSHIP_MANIFEST.read_text(encoding='utf-8')).values()
    except (OSError, ValueError):
        return False
    expected = [contract for contract in contracts if contract['sourceSha256'] == fixture['sha256']
                or contract['assetId'] == fixture['id']]
    if not expected:
        return fixture.get('ownershipSha256') is None and properties.get('public_realm_ownership_sha256') is None
    return any(contract['sourceSha256'] == fixture['sha256'] and contract['assetId'] == fixture['id']
               and contract['ownershipSha256'] == fixture.get('ownershipSha256')
               and contract['ownershipSha256'] == properties.get('public_realm_ownership_sha256')
               and fixture['url'] == '/street-kits/claude-20261023/'+contract['sourceSha256']+'.glb'
               for contract in expected)


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r'[a-f0-9]{64}', value) is not None


def release_gate_errors(row):
    asset, fixture = row['asset'], row['fixture']
    props, digest = asset['properties'], row['runtime_sha256']
    prefix = '/park-kits/claude-20261023/' if row['category'] == 'park' else '/street-kits/claude-20261023/'
    variant = props.get('green_space_selected_variant_id') if asset['zoneType'] == 'green_space' else props.get('road_selected_variant_id')
    dimensions = asset.get('nativeDimensions', [])
    errors = []
    if (not all(_sha(row.get(key)) for key in ('source_sha256', 'review_sha256', 'runtime_sha256', 'thumbnail_sha256'))
            or not asset['id'].startswith('claude_public_realm:') or not asset['id'].endswith(':'+digest[:12])
            or asset['kind'] != 'object' or asset['reshapeMode'] != 'fixed_native' or asset['model']['method'] != 'fixed_public_realm_v1'
            or row['category'] not in ('park', 'street') or asset['zoneType'] != ('green_space' if row['category'] == 'park' else 'road')
            or asset['model']['revision'] != digest or variant != asset['model']['variantId']
            or props.get('public_realm_release_asset') != asset['id'] or props.get('native_public_realm_url') != fixture['url']
            or any(props.get(key) is not None for key in ('validation_fixed_fixture', 'validation_native_url', 'public_realm_trial_asset'))
            or fixture['id'] != asset['id'] or fixture['sha256'] != digest or fixture['kind'] != row['category']
            or fixture['url'] != prefix+digest+'.glb'
            or asset['thumbnail'] not in (prefix+row['thumbnail_sha256']+'.jpg', prefix+row['thumbnail_sha256']+'.png')
            or fixture['dimensions'] != [asset['width'], asset['depth']]
            or asset['minWidth'] != asset['width'] or asset['minDepth'] != asset['depth']
            or asset.get('maxWidth') != asset['width'] or asset.get('maxDepth') != asset['depth']
            or len(dimensions) != 3 or any(isinstance(value, bool) or not isinstance(value, (int, float))
                                         or not math.isfinite(value) or value <= 0 for value in [asset['width'], asset['depth'], *dimensions])
            or dimensions[0] > asset['width'] or dimensions[1] > asset['depth']
            or fixture.get('preserveNativeGround') is not True or fixture.get('centerNativeClay') is not True
            or not _ownership_identity_valid(fixture, props)):
        errors.append('identity_mismatch')
    visual = row['visual_review']
    if (visual.get('status') != 'passed' or visual.get('scope') != 'complete_runtime_derivative'
            or visual.get('runtime_sha256') != digest or not _sha(visual.get('evidence_sha256'))
            or visual.get('unresolved_p0') != 0 or visual.get('unresolved_p1') != 0):
        errors.append('visual_review_pending')
    runtime = row['runtime_review']
    if runtime.get('status') != 'passed' or runtime.get('runtime_sha256') != digest or not _sha(runtime.get('evidence_sha256')):
        errors.append('runtime_review_pending')
    return errors


def validate_fixed_public_realm(zone_type, geometry, properties, *, manifest=None) -> bool:
    claimed = bool(properties.get('public_realm_release_asset')) or str(properties.get('pick_place_asset', '')).startswith('claude_public_realm:')
    if not claimed:
        return False
    if manifest is None:
        try:
            manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        except (OSError, ValueError) as error:
            raise ValueError('Fixed public-realm release registry is unavailable.') from error
    if manifest.get('schema') != 'cityprompt.fixed-public-realm-release@1':
        raise ValueError('Fixed public-realm release registry is invalid.')
    rows = [row for row in manifest['models'] if row['asset']['id'] == properties.get('pick_place_asset')]
    if len(rows) != 1:
        raise ValueError('The exact fixed public-realm model is unavailable.')
    row = rows[0]
    errors = release_gate_errors(row)
    rehearsal = get_settings().app_env.lower() == 'development' and row['status'] == 'runtime_trial'
    if 'identity_mismatch' in errors or (not rehearsal and (row['status'] not in ('ready', 'retired') or errors)):
        raise ValueError('The exact fixed public-realm model still requires visual/runtime review.')
    asset, fixture = row['asset'], row['fixture']
    if (zone_type != asset['zoneType'] or properties.get('pick_place_model_revision') != row['runtime_sha256']
            or properties.get('pick_place_definition_version') != asset['definitionVersion']
            or any(properties.get(key) != value for key, value in asset['properties'].items())
            or any(properties.get(key) is not None for key in ('validation_fixed_fixture', 'validation_native_url', 'public_realm_trial_asset'))
            or properties.get('_plan_scenario')):
        raise ValueError('The fixed public-realm identity or revision does not match; AI route generation is unsupported.')
    if geometry.geom_type != 'Polygon' or geometry.interiors:
        raise ValueError('Keep the fixed native scene in its complete native rectangle.')
    ring = list(geometry.exterior.coords)[:-1]
    if len(ring) != 4 or any(not math.isfinite(v) for point in ring for v in point):
        raise ValueError('Keep the fixed native scene in its complete native rectangle.')
    lng, lat = (sum(point[i] for point in ring)/4 for i in (0, 1))
    east = 111320*math.cos(math.radians(lat))
    points = [((point[0]-lng)*east, (point[1]-lat)*111320) for point in ring]
    yaw = math.atan2(points[1][1]-points[0][1], points[1][0]-points[0][0])
    c, s = math.cos(yaw), math.sin(yaw)
    width, depth = fixture['dimensions']
    corners = [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]
    if any(math.hypot(p[0]-(x*c-y*s), p[1]-(x*s+y*c)) > .04 for p, (x, y) in zip(points, corners)):
        raise ValueError('Keep the fixed scene at native size; move and rotate only.')
    return True
