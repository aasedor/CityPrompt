"""Build only the finite, exact-source RLASM 6.1 housing candidates."""
import argparse
import importlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE), str(REPO / 'tools/catalogue_duplex_pilot')]
import bpy
import clay_core as C
from tools.housing_teaching.contracts import candidate_path, load_cards, lock_family_sources
from tools.teaching_style_pilot.contracts import verify_evidence
from tools.teaching_style_wave2.build import cameras

BATCH = Path('C:/dev-artifacts/CityPrompt/housing-teaching-20261025')
SOURCES = REPO / 'frontend/public/archetypes/buildings/housing-teaching'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--family', choices=['victory', 'split'], required=True)
    p.add_argument('--version', type=int, default=1)
    p.add_argument('--output', required=True)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--resolution', type=int, default=1600)
    a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if a.version < 1:
        p.error('Version must be positive')
    card = load_cards()[a.family]
    family = importlib.import_module('family_' + a.family)
    spec = family.specification(cameras)
    output = candidate_path(a.output, BATCH)
    root = SOURCES / a.family
    expected = json.loads((HERE / 'source-lock.json').read_text(encoding='utf-8'))[a.family]
    sources = lock_family_sources(card['archetypeId'], card['variantId'],
        {r['role']: root / Path(r['path']).name for r in expected},
        REPO / 'frontend/public/archetypes/buildings', expected=expected)
    verify_evidence(sources, root)
    if a.dry_run:
        print(json.dumps(dict(status='DRY_RUN_PASS', family=a.family,
            sources=len(sources), cameras=len(spec['cameras']), output=str(output))))
        return
    output.mkdir(parents=True)
    for name in ('sources', 'scripts', 'renders', 'review', 'evidence', 'boards'):
        (output / name).mkdir()
    for source in sources:
        shutil.copy2(source['original_path'], output / source['path'])
    for name in ('original-board.png', 'source-provenance.json', 'generation-prompt.txt'):
        shutil.copy2(root / name, output / 'sources' / name)
    for path in [*root.glob('correction-*.txt'), *root.glob('prior-board-*.png')]:
        shutil.copy2(path, output / 'sources' / path.name)
    scripts = [Path(__file__), Path(family.__file__), HERE / 'construction.py',
        HERE / 'contracts.py', Path(C.__file__), REPO / 'tools/teaching_style_wave2/build.py']
    # Preserve nested dependencies with their repository paths, avoiding the two
    # different build.py files overwriting one another in a flat replay bundle.
    for path in scripts:
        target = output / 'scripts' / path.relative_to(REPO)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    shutil.copy2(REPO / 'docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md',
                 output / 'review/runtime-integration-NOT-TESTED.md')
    base = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO,
                          capture_output=True, text=True, check=True).stdout.strip()
    manifest = dict(candidate=spec['candidate'] + f'-v{a.version:03d}',
        method='RLASM v6.1', representation_kind='architectural_clay',
        archetype_id=card['archetypeId'], variant_id=card['variantId'],
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=spec['dimensions_m'], floors=spec['floors'],
            observations=spec['measurement_notes']),
        source_contract=dict(sources=sources, source_origin='Original generated teaching design; not a named historic building'),
        identity_contract=dict(owner='Source-locked geometry, no bitmap identity in clay profile'),
        material_contract=dict(profile='Source-palette architectural clay; texture-free, no PBR keeper claim'),
        roof_contract=spec['roof_contract'], programme_contract=spec['programme_contract'],
        contact_contract=spec['contact_contract'], camera_roster=spec['cameras'],
        runtime_contract=dict(scale='fixed_native_only', resizing=False,
            installation='not installed', review='NOT TESTED'),
        teaching=card, entrance_measurements=spec['entrances'],
        provenance=dict(builder='Codex', base_commit=base,
            scripts=[dict(path=str((Path('scripts') / path.relative_to(REPO))).replace('\\', '/'), sha256=C.digest(path)) for path in scripts],
            working_scripts_archived=True, render_source='exact GLB reimport'))
    C.write_json(output / 'prework-manifest.json', manifest)
    roster = C.setup(spec['palette'], spec['cameras'], a.resolution)
    bpy.context.scene.view_settings.exposure = .7
    ground = bpy.data.objects['QA ground - excluded']
    ground.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.27, .34, .19, 1)
    family.construct()
    # Family specifications keep each inspection emitter fully inside its room.
    # A large disc intersecting a sloped roof becomes an exterior bright patch.
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.name.startswith('QA interior'):
            obj.visible_camera = obj.visible_glossy = obj.visible_transmission = False
            obj.data.specular_factor = obj.data.transmission_factor = 0
    C.deliver(output, manifest, roster)
    verify_evidence(sources, output, require_renders=True)


if __name__ == '__main__':
    main()
