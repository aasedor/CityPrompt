"""Kit-showcase RLASM runner for Linux hosts; reuses clay_core, geometry and assemblies unchanged.

Adapted from tools/clay_halifax_public_gardens/build.py. A kit showcase has no locked sources, so prepare() copies
scripts only. keep_instances() is the family-local shim that keeps the planting kit's linked instances out of
clay_core.deliver()'s per-role join (which would turn every shared mesh back into real geometry); everything else
(bounds, aperture audit, GLB export and reimport, renders, build report) runs through deliver() untouched.
"""
import argparse
import hashlib
import json
import os
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
import family_plantkit as family  # noqa: E402

SCRIPTS = [Path(C.__file__), Path(G.__file__), HERE.parent / 'final_five_buildings/contract.py', Path(A.__file__),
           Path(family.__file__), Path(__file__)]


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prepare(a, manifest):
    out = Path(a.output).resolve()
    if a.dry_run:
        print(json.dumps(dict(dry_run=True, no_geometry_written=True, sources=0, cameras=len(manifest['camera_roster']),
                              candidate=manifest['candidate'])), flush=True)
        return None
    out.mkdir(parents=True, exist_ok=False)
    for name in ('scripts', 'renders', 'review', 'evidence', 'boards'):
        (out / name).mkdir()
    for p in SCRIPTS:
        shutil.copy2(p, out / 'scripts' / p.name)
    manifest['source_contract'] = dict(sources=[], kit_showcase=True, note='no locked sources: kit showcase, not a catalogue candidate')
    manifest['provenance'] = dict(scripts=[dict(path='scripts/' + p.name, sha256=digest(out / 'scripts' / p.name)) for p in SCRIPTS],
                                  blender_version=C.bpy.app.version_string, python_version=sys.version, generation_api_calls=0,
                                  build_started_utc=C.utc(), render_source='actual optimized GLB reimport only', host='linux container, Cycles CPU')
    C.write_json(out / 'prework-manifest.json', manifest)
    return out


def keep_instances():
    """Give every kit instance a role that is not in C.MATS, so deliver()'s `for role in MATS` join skips it; the true
    role is kept in cityprompt_base_role (and on the shared material). Returns the number of instance nodes."""
    n = 0
    for o in C.objects():
        if o.get('rlasm_instance'):
            o['cityprompt_base_role'] = o['cityprompt_semantic_role']
            o['cityprompt_semantic_role'] = o['cityprompt_semantic_role'] + '_instanced'
            n += 1
    return n


def glb_size(path):
    """Unique (stored) triangles, meshes and nodes in the delivered GLB."""
    js = C.glb_json(path); acc = js.get('accessors', [])
    tris = sum(acc[p['indices']]['count'] // 3 for m in js.get('meshes', []) for p in m['primitives'] if 'indices' in p)
    return dict(bytes=Path(path).stat().st_size, stored_triangles=tris, meshes=len(js.get('meshes', [])), nodes=len(js.get('nodes', [])))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--version', type=int, required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--resolution', type=int, default=1440)
    p.add_argument('--samples', type=int, default=32)
    p.add_argument('--cameras', default='', help='comma list to render a subset (iteration only)')
    p.add_argument('--no-instancing', action='store_true', help='merge every plant into real geometry (size comparison only)')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    if a.no_instancing:
        family.INSTANCING = False
    m = family.manifest(a.version)
    if a.cameras:
        keep = set(a.cameras.split(','))
        m['camera_roster'] = [c for c in m['camera_roster'] if c['name'] in keep or c['name'] == 'front_corner']
        m['state'] = 'iteration_subset_render'
    out = prepare(a, m)
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
    seen = set()
    for obj in C.objects():
        if obj.data.name in seen:                # shared kit meshes are triangulated once
            continue
        seen.add(obj.data.name)
        bm = C.bmesh.new(); bm.from_mesh(obj.data)
        C.bmesh.ops.triangulate(bm, faces=list(bm.faces))
        C.bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_area() <= 1e-10], context='FACES_ONLY')
        bm.to_mesh(obj.data); bm.free(); obj.data.update()
    nodes = keep_instances()
    kit = family.KIT.stats() if getattr(family, 'KIT', None) else {}
    report = C.deliver(out, m, cameras)
    size = dict(glb_size(out / (m['candidate'] + '.glb')), kit=kit, instance_nodes=nodes,
                scene_triangles=report['runtime']['triangles'])
    if kit.get('plants'):
        size['glb_bytes_per_plant'] = size['bytes'] / kit['plants']
    C.write_json(out / 'evidence/planting-kit-size.json', size)
    print('KIT_SIZE ' + json.dumps(size), flush=True)


if __name__ == '__main__':
    main()
