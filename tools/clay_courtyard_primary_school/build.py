"""Pilot RLASM runner for Linux hosts; reuses clay_core, geometry and assemblies unchanged.

Writes heavyweight artefacts outside the repository, mirroring prepare_candidate()
without its Windows artefact-root assertion. Sources are copied from the lock
manifest and re-hashed; the build refuses to start if any locked pixel changed.
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
for rel in ('final_five_buildings', 'catalogue_affordable_five', 'catalogue_services_batch'):
    sys.path.append(str(HERE.parent / rel))
import clay_core as C          # noqa: E402
import geometry as G           # noqa: E402  (final_five_buildings/geometry.py)
import assemblies as A         # noqa: E402  (catalogue_affordable_five/assemblies.py)
import family_school as family  # noqa: E402
from lock_sources import verify     # noqa: E402

SCRIPTS = [Path(C.__file__), Path(G.__file__), HERE.parent / 'final_five_buildings/contract.py', Path(A.__file__),
           Path(family.__file__), Path(__file__), HERE / 'lock_sources.py']


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prepare(a, manifest, lock):
    out = Path(a.output).resolve()
    if a.dry_run:
        print(json.dumps(dict(dry_run=True, no_geometry_written=True, sources=len(lock['records']),
                              cameras=len(manifest['camera_roster']), candidate=manifest['candidate'])), flush=True)
        return None
    out.mkdir(parents=True, exist_ok=False)
    for name in ('sources', 'scripts', 'renders', 'review', 'evidence', 'boards'):
        (out / name).mkdir()
    sources = []
    for r in lock['records']:
        src = ROOT / r['path']; dest = out / 'sources' / (r['role'] + Path(r['file']).suffix)
        shutil.copy2(src, dest)
        assert dest.stat().st_size == r['bytes'] and digest(dest) == r['sha256']
        sources.append(dict(role=r['role'], original_path=str(src), path='sources/' + dest.name, bytes=r['bytes'], sha256=r['sha256']))
    for p in SCRIPTS:
        shutil.copy2(p, out / 'scripts' / p.name)
    entry = dict(archetype_id=manifest['archetype_id'], variant_id=manifest['variant_id'],
                 source_origin=lock['source_origin'], source_archetype=lock['archetype_id'] + '/' + lock['variant_id'], sources=sources)
    C.write_json(out / 'source-entry.json', entry)
    manifest['source_contract'] = dict(sources=sources, exact_variant_only=True, no_generated_substitute_references=True,
                                       sibling_variants_excluded=lock['excluded_sibling_files'])
    manifest['provenance'] = dict(scripts=[dict(path='scripts/' + p.name, sha256=digest(out / 'scripts' / p.name)) for p in SCRIPTS],
                                  blender_version=C.bpy.app.version_string, python_version=sys.version, generation_api_calls=0,
                                  build_started_utc=C.utc(), render_source='actual optimized GLB reimport only', host='linux container, Cycles CPU')
    C.write_json(out / 'prework-manifest.json', manifest)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--version', type=int, required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--resolution', type=int, default=1440)
    p.add_argument('--samples', type=int, default=32)
    p.add_argument('--cameras', default='', help='comma list to render a subset (iteration only)')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    lock = verify()
    m = family.manifest(a.version)
    if a.cameras:
        keep = set(a.cameras.split(','))
        m['camera_roster'] = [c for c in m['camera_roster'] if c['name'] in keep]
        m['state'] = 'iteration_subset_render'
    out = prepare(a, m, lock)
    if out is None:
        return
    cameras = C.setup(family.PALETTE, m['camera_roster'], a.resolution)
    C.bpy.context.scene.cycles.samples = a.samples
    rig = getattr(family, 'LIGHT_RIG', dict(key=(-14, -20, 20), fill=(18, -8, 16), rear=(-8, 20, 18), target=(0, 0, 4.5), gain=2.5))
    for name in ('key', 'fill', 'rear'):
        light = C.bpy.data.objects['QA ' + name]
        light.location = rig[name]; light.data.energy *= rig['gain']
        C.look_at(light, rig['target'])
    C.bevel = lambda *args, **kwargs: None
    print('AUTHORING_START ' + m['candidate'], flush=True)
    family.build()
    print('AUTHORING_COMPLETE ' + m['candidate'], flush=True)
    for obj in C.objects():
        bm = C.bmesh.new(); bm.from_mesh(obj.data)
        C.bmesh.ops.triangulate(bm, faces=list(bm.faces))
        C.bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_area() <= 1e-10], context='FACES_ONLY')
        bm.to_mesh(obj.data); bm.free(); obj.data.update()
    C.deliver(out, m, cameras)


if __name__ == '__main__':
    main()
