"""Finite RLASM 6.1 teaching Wave 2; source-specific architectural clay."""
from pathlib import Path
import argparse
import importlib
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / 'tools/catalogue_duplex_pilot'))
import bpy
import clay_core as C
from tools.teaching_style_pilot.contracts import verify_evidence
from tools.teaching_style_wave2.contracts import candidate_path, source_lock

BATCH = Path('C:/dev-artifacts/CityPrompt/teaching-wave2-20261025')
SOURCES = REPO / 'frontend/public/archetypes/buildings/teaching-wave2'


def cameras(width, depth, height, details):
    r = max(width, depth) * 2.2
    whole = [
        ('front', (0, -r, height*.5)),
        ('front_corner', (-r*.45, -r, height*1.7)),
        ('aerial', (-r*.6, -r*.7, height*4.8)),
        ('top', (0, 0, r*1.5)),
        ('left_side', (-r, 0, height*.65)),
        ('right_side', (r, 0, height*.65)),
        ('rear', (0, r, height*.6)),
        ('rear_side', (r*.8, r, height*1.8)),
    ]
    roster = []
    for name, location in whole:
        spec = dict(name=name, location=location,
            target=(0, .001 if name == 'top' else 0, 0 if name == 'top' else height*.5))
        if name in ('front', 'top'):
            spec['ortho_scale'] = max(width, depth)*1.35
        roster.append(spec)
    roster.extend(dict(name=n, location=location, target=target, lens=lens, whole=False)
                  for n, location, target, lens in details)
    return roster


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--family', choices=['workshop', 'destijl', 'pavilion'], required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--version', type=int, default=1)
    parser.add_argument('--resolution', type=int, default=1600)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    family = importlib.import_module('family_' + args.family)
    spec = family.specification(cameras)
    output = candidate_path(args.output, BATCH)
    root = SOURCES / args.family
    roles = {role: root / f'{role}.png' for role in spec['source_roles']}
    sources = source_lock(spec['archetype_id'], spec['variant_id'], roles,
                          REPO / 'frontend/public/archetypes/buildings')
    verify_evidence(sources, root)
    if args.dry_run:
        print(json.dumps(dict(status='DRY_RUN_PASS', family=args.family,
            sources=len(sources), cameras=len(spec['cameras']), output=str(output))))
        return
    output.mkdir(parents=True)
    for name in ('sources', 'scripts', 'renders', 'review', 'evidence', 'boards'):
        (output / name).mkdir()
    for source in sources:
        shutil.copy2(source['original_path'], output / source['path'])
    for name in ('original-board.png', 'source-provenance.json', 'generation-prompt.txt'):
        shutil.copy2(root / name, output / 'sources' / name)
    script_paths = [Path(__file__), HERE/'contracts.py', Path(family.__file__), Path(C.__file__)]
    script_paths.extend(HERE / name for name in getattr(family, 'SUPPORT_FILES', ()))
    for path in script_paths:
        shutil.copy2(path, output / 'scripts' / path.name)
    shutil.copy2(REPO/'docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md',
                 output/'review/runtime-integration-NOT-TESTED.md')
    manifest = dict(candidate=spec['candidate']+f'-v{args.version:03d}',
        method='RLASM v6.1', representation_kind='architectural_clay',
        archetype_id=spec['archetype_id'], variant_id=spec['variant_id'], state='prework',
        keeper_claimed=False, runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=spec['dimensions_m'], floors=spec['floors'],
                                  observations=spec['measurement_notes']),
        source_contract=dict(sources=sources,
            source_origin='Original generated teaching design; not a named historic building'),
        identity_contract=dict(owner='Exact-source geometry; no bitmap identity in architectural-clay profile'),
        material_contract=dict(profile='Source palette architectural clay, no textures/PBR keeper claim'),
        roof_contract=spec['roof_contract'], programme_contract=spec['programme_contract'],
        contact_contract=spec['contact_contract'],
        runtime_contract=dict(scale='fixed_native_only', resizing=False,
                              installation='not installed', review='NOT TESTED'),
        camera_roster=spec['cameras'], teaching=spec['teaching'],
        provenance=dict(builder='Codex', base_commit='fd90fed3b',
            scripts=[dict(path='scripts/'+path.name,sha256=C.digest(path)) for path in script_paths],
            working_scripts_archived=True, render_source='exact GLB reimport'))
    C.write_json(output/'prework-manifest.json',manifest)
    roster = C.setup(spec['palette'],spec['cameras'],args.resolution)
    bpy.context.scene.view_settings.exposure = .7
    ground = bpy.data.objects.get('QA ground - excluded')
    ground.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.27,.34,.19,1)
    family.construct()
    # Interior inspection emitters illuminate rooms without appearing as
    # floating luminous discs in the delivered glazing's reflections.
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.name.startswith('QA interior'):
            obj.visible_camera = False
            obj.visible_glossy = False
            obj.visible_transmission = False
            obj.data.specular_factor = 0
            obj.data.transmission_factor = 0
    C.deliver(output,manifest,roster)
    verify_evidence(sources,output,require_renders=True)


if __name__ == '__main__':
    main()
