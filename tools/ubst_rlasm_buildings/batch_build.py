"""Finite source-locked family runner; every build uses a fresh external candidate."""
import argparse
import importlib
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent/'catalogue_services_batch'))
sys.path.append(str(HERE.parent/'catalogue_affordable_five'))
import clay_core as C
from references import source_entry


def main():
    p = argparse.ArgumentParser()
    p.add_argument('family', choices=['student', 'timber', 'hotel'])
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--version', type=int, required=True)
    p.add_argument('--resolution', type=int, default=1440)
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args(sys.argv[sys.argv.index('--')+1:])
    family = importlib.import_module('family_'+args.family)
    entry = source_entry(ROOT, family.SLUG)
    m = family.manifest(args.version)
    out = args.output.resolve()
    if not out.is_relative_to(Path('C:/dev-artifacts/CityPrompt').resolve()):
        raise ValueError('External output required')
    if args.dry_run:
        print('DRY_RUN_PASS', m['candidate'], len(m['mandatory_review_views']), 'views; exact source hashes verified')
        return
    out.mkdir(parents=True, exist_ok=False)
    for name in ('sources','scripts','renders','review','evidence','boards'):
        (out/name).mkdir()
    for source in entry['sources']:
        shutil.copy2(source['original_path'], out/source['path'])
        assert C.digest(out/source['path']) == source['sha256']
    shutil.copy2(Path(entry['_reference_root'])/'generation-provenance.json',out/'sources/generation-provenance.json')
    scripts=[Path(__file__), Path(family.__file__), HERE/'common.py', HERE/'build.py', HERE/'references.py', Path(C.__file__),
             HERE.parent/'catalogue_affordable_five/assemblies.py', HERE.parent/'catalogue_affordable_five/geometry.py']
    for script in scripts:
        shutil.copy2(script,out/'scripts'/script.name)
    C.write_json(out/'source-entry.json',{k:v for k,v in entry.items() if not k.startswith('_')})
    m['source_contract']=dict(sources=entry['sources'],exact_variant_only=True,origin='original_generated_design',
                             generated_references_explicitly_requested=True,not_surveyed=True)
    m['provenance']=dict(scripts=[dict(path='scripts/'+s.name,sha256=C.digest(out/'scripts'/s.name)) for s in scripts],
        blender_version=C.bpy.app.version_string,python_version=sys.version,build_started_utc=C.utc(),
        generation_api_calls_during_build=0,reference_generation='built-in image_gen; prompts in source provenance',
        render_source='actual optimized GLB reimport only')
    C.write_json(out/'prework-manifest.json',m)
    cams=C.setup(family.PALETTE,m['camera_roster'],args.resolution)
    for spec in m['camera_roster']:
        cams[spec['name']].data.shift_y=spec.get('shift_y',0)
    C.bevel=lambda *args,**kwargs:None
    for obj in C.bpy.context.scene.objects:
        if obj.type=='LIGHT':
            obj.location*=3;obj.data.energy*=9;obj.data.size*=3
    family.construct()
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data)
        C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.deliver(out,m,cams)


if __name__=='__main__': main()
