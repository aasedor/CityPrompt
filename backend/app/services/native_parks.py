"""Immutable, server-resolved native park layouts. V1 parks remain untouched."""
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from shapely.geometry import Polygon
from shapely.ops import transform


@lru_cache(maxsize=1)
def registry() -> dict:
    return json.loads((Path(__file__).resolve().parents[1] / 'data/nativeParks.json').read_text(encoding='utf-8'))


def layout_for(layout_id: str, revision: str) -> dict:
    layout = next((p for p in registry()['layouts'] if p['id'] == layout_id and p['contentRevision'] == revision), None)
    if layout is None:
        raise ValueError('This park layout revision is unavailable. Keep the previous layout.')
    return layout


class ParkFrame(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(gt=-85, lt=85)
    yaw: float


class ParkSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    layout_id: str
    content_revision: str
    frame: ParkFrame


class NativeParkRecipe(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    schema_version: Literal[2] = 2
    kind: Literal['park'] = 'park'
    generator: Literal['park_kit'] = 'park_kit'
    family_id: Literal['native_park'] = 'native_park'
    family_version: Literal[1] = 1
    archetype_id: str
    variant_id: str
    layout_id: str
    content_revision: str
    frame: ParkFrame
    mode: Literal['native_assembly', 'module_assembly']
    terrain_policy: Literal['prepared_level'] = 'prepared_level'
    asset_hashes: dict[str, str]
    recipe_hash: str


def _hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


def recipe_for(selection: ParkSelection) -> NativeParkRecipe:
    layout = layout_for(selection.layout_id, selection.content_revision)
    payload = dict(schema_version=2, kind='park', generator='park_kit', family_id='native_park', family_version=1,
                   archetype_id=layout['archetypeId'], variant_id=layout['variantId'],
                   **selection.model_dump(mode='json'), mode=layout['mode'], terrain_policy='prepared_level',
                   asset_hashes={key: asset['sha256'] for key, asset in layout['assets'].items()})
    return NativeParkRecipe(**payload, recipe_hash=_hash(payload))


def native_park_ground(selection_value: dict) -> Polygon:
    """The assembly owns its native ground, not the student's larger parcel."""
    selection = ParkSelection.model_validate(selection_value)
    layout = layout_for(selection.layout_id, selection.content_revision)
    f = selection.frame
    c, s = math.cos(f.yaw), math.sin(f.yaw)
    east = 111320 * math.cos(math.radians(f.latitude))
    w, d = layout['widthM'] / 2, layout['depthM'] / 2
    return Polygon([(f.longitude + (x*c-y*s)/east, f.latitude + (x*s+y*c)/111320)
                    for x,y in [(-w,-d),(w,-d),(w,d),(-w,d)]])


def plan_native_park(geometry, properties: dict) -> NativeParkRecipe:
    if properties.get('park_terrain') is not None:
        raise ValueError('This native layout needs prepared level ground. Clear the custom park terrain before upgrading.')
    selection = ParkSelection.model_validate(properties['green_space_native_layout'])
    layout = layout_for(selection.layout_id, selection.content_revision)
    if properties.get('green_space_archetype_id') != layout['archetypeId'] or properties.get('green_space_selected_variant_id') != layout['variantId']:
        raise ValueError('The park selection does not match its saved layout.')
    f = selection.frame
    east = 111320 * math.cos(math.radians(f.latitude))
    local = transform(lambda x, y, z=None: ((x - f.longitude) * east, (y - f.latitude) * 111320), geometry)
    c, s = math.cos(f.yaw), math.sin(f.yaw)
    w, d = layout['occupiedWidthM'] / 2, layout['occupiedDepthM'] / 2
    footprint = Polygon([(x*c-y*s, x*s+y*c) for x,y in [(-w,-d),(w,-d),(w,d),(-w,d)]])
    excluded = []
    rings = properties.get('park_exclusion_rings', [])
    if not isinstance(rings, list):
        raise ValueError('The park exclusion areas are invalid. Repair their outlines before changing the layout.')
    for ring in rings:
        if (not isinstance(ring, list) or len(ring) < 3
                or any(not isinstance(point, (list, tuple)) or len(point) != 2
                       or any(not isinstance(n, (int, float)) or not math.isfinite(n) for n in point)
                       for point in ring)):
            raise ValueError('The park exclusion areas are invalid. Repair their outlines before changing the layout.')
        hole = Polygon(ring)
        if not hole.is_valid or hole.is_empty or hole.area == 0:
            raise ValueError('The park exclusion areas are invalid. Repair their outlines before changing the layout.')
        excluded.append(transform(lambda x, y, z=None: ((x-f.longitude)*east,(y-f.latitude)*111320), hole))
    if not local.is_valid or not local.buffer(.025).covers(footprint) or any(footprint.intersects(hole) for hole in excluded):
        raise ValueError(f"Keep the complete {layout['widthM']} × {layout['depthM']} m {layout['label']} layout inside the park. Its objects cannot be stretched.")
    return recipe_for(selection)


def native_park_identity(value) -> dict | None:
    try:
        recipe = NativeParkRecipe.model_validate(value)
        canonical = recipe_for(ParkSelection(layout_id=recipe.layout_id, content_revision=recipe.content_revision, frame=recipe.frame))
        if recipe != canonical:
            return None
        return {'capability_fingerprint': recipe.content_revision, 'recipe_hash': recipe.recipe_hash,
                'recipe': recipe.model_dump(mode='json')}
    except (ValueError, TypeError):
        return None
