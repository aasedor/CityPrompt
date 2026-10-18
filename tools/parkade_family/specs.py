"""Approved finite original-design brief and metric Classic Concrete contract.

Blender authoring uses Z-up; GLB export uses Y-up. Fixed assemblies only.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

DESIGNS = {
    'classic': dict(label='Classic Concrete Parkade', slug='parkade-classic-concrete',
        dimensions=[60, 36], levels=4, style='conventional',
        identity='Open concrete decks, horizontal steel guards, two front glazed stair towers.'),
    'brick': dict(label='Urban Brick Parkade', slug='parkade-urban-brick',
        dimensions=[54, 36], levels=5, style='conventional',
        identity='Brick piers, recessed metal ventilation screens, sheltered pedestrian entrance.'),
    'green': dict(label='Green Terraces Parkade', slug='parkade-green-terraces',
        dimensions=[60, 40], levels=4, style='innovative',
        identity='Stepped planted edges, climbing screens and a separate rooftop garden.'),
    'solar': dict(label='Solar Ribbon Parkade', slug='parkade-solar-ribbon',
        dimensions=[66, 36], levels=5, style='innovative',
        identity='Sculptural metal fins, solar roof canopy and marked EV bays.'),
    'courtyard': dict(label='Mobility Courtyard Parkade', slug='parkade-mobility-courtyard',
        dimensions=[64, 48], levels=4, style='innovative',
        identity='Open central court, colourful screens, bicycle hub and street-facing cafe.'),
}
LEVEL_PITCH = 3.3
GROUND_TOP = .15
LEVELS = tuple(GROUND_TOP + i * LEVEL_PITCH for i in range(4))
RAMP_X = (-23., 23.)
RAMP_Y = (11.55, 17.95)
RAMP_CLEAR_WIDTH = 6.0
RAMP_THICKNESS = .15
CORE_HOLES = [(-30, -25.1, -18, -11.4), (25.1, 30, -18, -11.4)]


def ramp_height(level: int, x: float) -> float:
    if level not in range(3) or not RAMP_X[0] <= x <= RAMP_X[1]:
        raise ValueError('Outside the authored three-ramp programme')
    return LEVELS[level] + LEVEL_PITCH * (x - RAMP_X[0]) / (RAMP_X[1] - RAMP_X[0])


def main_deck_panels() -> list[tuple[float, float, float, float]]:
    """Rectangular partition with actual stair wells, not an opaque cover slab."""
    return [(-25.1, 25.1, -18, -11.4), (-30, 30, -11.4, 11.5)]


def source_entry(directory: Path) -> dict:
    directory = Path(directory)
    provenance = json.loads((directory / 'generation-provenance.json').read_text(encoding='utf-8'))
    if provenance.get('origin') not in {'original_generated_design','original_authored_design'}:
        raise ValueError('Original-design provenance required')
    records = provenance['records']
    roles = [r['role'] for r in records]
    if len(roles) != len(set(roles)) or not {'front', 'oblique', 'top', 'ramp_section'} <= set(roles):
        raise ValueError('Distinct front, oblique, top and ramp_section source roles required')
    sources = []
    for record in records:
        path = (directory / record['file']).resolve()
        if not path.is_relative_to(directory.resolve()):
            raise ValueError('Source escapes its package')
        raw = path.read_bytes()
        if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Locked source changed: ' + record['role'])
        sources.append(dict(role=record['role'], original_path=str(path),
            path='sources/' + path.name, bytes=len(raw), sha256=record['sha256']))
    return dict(archetype_id=DESIGNS['classic']['slug'], variant_id='classic-concrete-v1',
        source_origin=provenance['origin'], sources=sources, _reference_root=str(directory.resolve()))
