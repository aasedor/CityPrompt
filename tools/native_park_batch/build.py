"""Build one native park from the batch as a self-contained assembly GLB and recipe.

    python3 tools/native_park_batch/build.py --park skate --output <new directory>
    python3 tools/native_park_batch/build.py --park skate --dry-run

Pure Python with numpy, shapely and earcut; no Blender and no paid calls. The output
directory must not exist: a candidate is never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import parkkit as kit  # noqa: E402

PARKS = {'skate': 'skate_park', 'fitness': 'fitness_circuit', 'memorial': 'memorial_garden'}


def load(park):
    return importlib.import_module(PARKS[park])


def build(park):
    module = load(park)
    meshes, nodes, meta = module.build()
    payload, rendered, instances = kit.write_glb(meshes, nodes, meta['generator'], meta['id'])
    lo, hi = kit.bounds(meshes, nodes)
    source = (HERE / f'{PARKS[park]}.py').read_bytes() + (HERE / 'parkkit.py').read_bytes()
    recipe = {
        'id': meta['id'], 'title': meta['title'], 'archetype_id': meta['archetype'], 'dimensions_m': list(meta['site']),
        'programme': meta['programme'], 'design_basis': meta['design_basis'], 'reference_views': meta['reference'],
        'generator': meta['generator'], 'generator_sha256': hashlib.sha256(source).hexdigest(),
        'terrain_policy': 'prepared_level', 'native_scale_only': True, 'limitations': meta['limitations'],
        'clear_routes': meta['routes'], 'entrance': meta['entrance'], 'walk_surface_materials': meta['walk_surface_materials'],
        'tree_wells': [], 'placements': [], 'surface_regions': [],
        'surface_priority': 'Assembly owns its ground: every surface inside the site is one tiled assembly.',
        'assembly': {'path': 'assembly-preview.glb', 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()},
        'modules': {}, 'bounds_m': [[round(float(v), 4) for v in lo], [round(float(v), 4) for v in hi]],
        'triangles': rendered, 'mesh_instances': instances, 'render_source': 'reimported GLB', 'runtime_approved': False,
        'axes': 'X east/across; Y north/along; Z up; metres (GLB standard Y-up conversion)',
        'runtime_contract': f"Native assembly at true size on prepared level ground. Walk on {', '.join(meta['walk_surface_materials'])}. "
                            'Never stretch the assembly to fit.',
        'card': {'group': meta['group'], 'description': meta['description']},
    }
    return payload, recipe


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--park', required=True, choices=sorted(PARKS))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    if args.dry_run:
        module = load(args.park)
        print(json.dumps({'id': module.PARK_ID, 'site_m': [module.SITE_W, module.SITE_D], 'paid_calls': 0, 'blender': False}))
        return
    if not args.output:
        parser.error('--output is required')
    if args.output.exists():
        raise SystemExit(f'{args.output} exists; a candidate is never overwritten')
    payload, recipe = build(args.park)
    args.output.mkdir(parents=True)
    (args.output / 'assembly-preview.glb').write_bytes(payload)
    (args.output / 'recipe.json').write_text(json.dumps(recipe, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'id': recipe['id'], 'bytes': len(payload), 'sha256': recipe['assembly']['sha256'], 'triangles': recipe['triangles'],
                      'instances': recipe['mesh_instances'], 'bounds_m': recipe['bounds_m'], 'routes': len(recipe['clear_routes'])}))


if __name__ == '__main__':
    main(sys.argv[1:])
