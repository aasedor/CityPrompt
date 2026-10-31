"""Independent checks on reimported court GLB geometry; no trusted bounds metadata."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def verify(package):
    package = Path(package)
    r = json.loads((package/'recipe.json').read_text())
    model = package/'assembly-preview.glb'
    sha = hashlib.sha256(model.read_bytes()).hexdigest()
    assert sha == r['assembly']['sha256']
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(model))
    objects = [o for o in bpy.context.scene.objects if o.type=='MESH']
    points = [o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
    lo = [min(p[i] for p in points) for i in range(3)]
    hi = [max(p[i] for p in points) for i in range(3)]
    w, d = r['module_m']
    assert all(abs(v-e)<.003 for v,e in zip(lo[:2]+hi[:2], [-w/2,-d/2,w/2,d/2])), (lo,hi)
    names = {m.name.split('.')[0] for o in objects for m in o.data.materials}
    assert names <= {'court','runoff','paint','key','padding','rim','board','metal','net','sand','sand_grain','kitchen'}, names
    assert len(objects) <= 10, len(objects)
    trees = []
    for o in objects:
        vertices = [o.matrix_world@v.co for v in o.data.vertices]
        trees.append(BVHTree.FromPolygons(vertices, [list(p.vertices) for p in o.data.polygons]))

    def height(x,y):
        hits = [tree.ray_cast(Vector((x,y,10)), Vector((0,0,-1)), 12)[0] for tree in trees]
        return max((hit.z for hit in hits if hit is not None), default=-100)

    # A perimeter fence would obstruct these probes above the flat clear reserve.
    perimeter = [(s*(w/2-.01), y*d) for s in (-1,1) for y in (-.4,-.2,.2,.4)]
    perimeter += [(x*w, s*(d/2-.01)) for s in (-1,1) for x in (-.4,-.2,.2,.4)]
    assert all(-.02 <= height(x,y) <= .02 for x,y in perimeter)
    if r['sport'] == 'basketball':
        equipment = [height(.225, sign*(14-1.575)) for sign in (-1,1)]
        assert all(3.035 < h < 3.07 for h in equipment), equipment
    else:
        equipment = [height(0,0)]
        assert abs(equipment[0]-r['net_center_m']) < .012, equipment
    # Court and corner reserve remain real continuous ground after GLB conversion.
    samples = [height(0,-r['playing_m'][1]/4), height(-w/2+.3,-d/4)]
    assert all(-.02 <= h <= .03 for h in samples), samples
    for o in objects: o.data.calc_loop_triangles()
    report = dict(status='PASS_OFFLINE_GEOMETRY', model_sha256=sha, bounds_m=[lo,hi],
                  mesh_instances=len(objects), triangles=sum(len(o.data.loop_triangles) for o in objects),
                  materials=sorted(names), equipment_top_samples_m=equipment,
                  perimeter_probes=len(perimeter), surface_samples_m=samples,
                  checks=['exact GLB hash', 'measured native reserve', 'court-only material allowlist',
                          'open perimeter', 'equipment height', 'continuous ground'])
    (package/'geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('COURT_ONLY_VERIFIED', r['id'], json.dumps(report), flush=True)
    return report
