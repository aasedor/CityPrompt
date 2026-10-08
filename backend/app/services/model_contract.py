"""Exact authored dimensions; placement plots are not measured floor plates.

Read the same immutable catalogue/revision records as the frontend. An optional
local-trial manifest supplies local-only records without publishing prototypes.
"""
from __future__ import annotations

import json
import math
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parents[1] / 'data'


@lru_cache(maxsize=1)
def _records() -> tuple[dict, ...]:
    result = json.loads((DATA / 'native_model_contract.json').read_text(encoding='utf-8'))['records']
    rows = []
    local_manifest = os.environ.get('CITYPROMPT_LOCAL_MODEL_BINDINGS')
    if local_manifest:
        local = json.loads(Path(local_manifest).read_text(encoding='utf-8'))
        if local.get('local_trial_only') is not True:
            raise ValueError('Local model bindings must retain local trial status')
        rows.extend(row['asset'] for row in local['models'])
    result.extend({
        'asset_id': row['id'], 'variant_id': row['model']['variantId'], 'revision': row['model']['revision'],
        'dimensions_m': row.get('nativeDimensions'),
        'storeys': row['properties'].get('floor_count', row['properties'].get('floors')),
        'fixed': row.get('storeyProgram', {}).get('mode', 'fixed_authored_assembly') == 'fixed_authored_assembly', 'current': True,
    } for row in rows)
    return tuple(result)


def native_model_facts(properties: dict[str, Any]) -> dict | None:
    if not properties.get('pick_place_asset'):
        return None
    revision = properties.get('pick_place_model_revision')
    variant = properties.get('development_selected_variant_id')
    matches = [row for row in _records() if row['asset_id'] == properties.get('pick_place_asset')
               and (not variant or row['variant_id'] == variant)
               and (row['revision'] == revision if revision else row['current'])]
    if len(matches) != 1:
        return None
    row = matches[0]
    dimensions = row.get('dimensions_m')
    if not isinstance(dimensions, list) or len(dimensions) != 3 or any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0
        for value in dimensions
    ):
        return None
    override = properties.get('development_height_override_m')
    if override is not None and (isinstance(override, bool) or not isinstance(override, (int, float))
                                 or not math.isfinite(override) or abs(override - dimensions[2]) > 0.05):
        return None
    return row


def uses_placement_plot(properties: dict[str, Any]) -> bool:
    return bool(properties.get('building_geometry_basis') == 'placement_plot'
                or properties.get('native_home_plot') is True
                or properties.get('validation_fixed_fixture') is True
                or properties.get('validation_native_url')
                or (properties.get('native_plot_axes') is True and properties.get('pick_place_asset'))
                or native_model_facts(properties))


@lru_cache(maxsize=1)
def _dwelling_programmes() -> tuple[dict, ...]:
    return tuple(json.loads((DATA / 'catalogue_dwelling_programmes.json').read_text(encoding='utf-8'))['records'])


def catalogue_dwellings(properties: dict[str, Any]) -> int | None:
    """Only an exact, unchanged authored assembly supplies a catalogue estimate."""
    facts = native_model_facts(properties)
    if not facts or not facts.get('fixed'):
        return None
    if properties.get('floor_count', properties.get('floors', facts['storeys'])) != facts['storeys']:
        return None
    return next((row['dwellings'] for row in _dwelling_programmes()
                 if row['variant_id'] == facts['variant_id'] and row['revision'] == facts['revision']), None)
