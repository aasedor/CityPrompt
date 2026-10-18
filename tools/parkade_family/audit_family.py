"""Sparse measurements on delivered Y-up GLBs (imported back into Z-up Blender)."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from layout import frame_plan


def main():
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    m=json.loads((a.candidate/'prework-manifest.json').read_text());s=m['native_design'];f=frame_plan(s['width'],s.get('frameDepth',s['depth']),s['levels'])
    glb=next(a.candidate.glob('*.glb'));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));bpy.context.view_layer.update()
    vertices=[];faces=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or not any(mat and mat.name.startswith(('CLAY_DECK','CLAY_CONCRETE')) for mat in obj.data.materials):continue
        offset=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in face.vertices) for face in obj.data.polygons)
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=False);checks=[];clearances=[]
    def ray(name,point,direction,length,expect=None,absent=False):
        hit=tree.ray_cast(Vector(point),Vector(direction),length)[0]
        ok=hit is None if absent else hit is not None and (expect is None or abs(hit.z-expect)<.001)
        checks.append(dict(name=name,point=point,hit=list(hit) if hit is not None else None,passed=ok))
        return hit
    h=f['width']/2;front=f['frontY'];ax,bx=f['rampX'];ay,by=f['rampY']
    for z in f['datums'][1:]:
        for sign in (-1,1):
            for d in (4.75,4.85,4.95):ray('Stair bridge continuity',(sign*(h-d),front+1,z+.05),(0,0,-1),.08,z)
            ray('Glazed side core without opaque beam',(sign*(h+.2),front+3,z-.32),(-sign,0,0),.8,absent=True)
    for i in range(f['levels']-1):
        for ratio in (.02,.25,.5,.75,.98):
            x=ax+(bx-ax)*ratio;z=f['datums'][i]+3.3*ratio
            for y in (ay+.21,(ay+by)/2,by-.21):
                ray('Ramp surface',(x,y,z+.05),(0,0,-1),.08,z)
                if i<f['levels']-2:
                    hit=ray('Stacked ramp headroom',(x,y,z+.05),(0,0,1),4)
                    clearance=hit.z-z if hit is not None else 0;clearances.append(clearance)
                    checks[-1]['clearance_m']=clearance;checks[-1]['passed']=clearance>=3.1
        for x in (-h+3.5,h-3.5):
            for z in f['datums'][i:i+2]:ray('Ramp end landing',(x,(ay+by)/2,z+.05),(0,0,-1),.08,z)
    if s.get('courtyard'):
        ray('Cafe open doorway through opaque structure',(-1.4,-24.1,1.5),(0,1,0),.9,absent=True)
        # Rooted trees occupy corners; central cross remains fully open sky.
        for x,y in ((0,0),(0,4),(4,0)):
            ray('Open courtyard sky',(x,y,1),(0,0,1),20,absent=True)
    result=dict(status='PASS' if all(c['passed'] for c in checks) else 'FAIL',model_sha256=hashlib.sha256(glb.read_bytes()).hexdigest(),checks=checks,minimum_measured_ramp_headroom_m=min(clearances),limitation='Sparse reimported-GLB geometry probes, not certified circulation, engineering or terrain review.')
    with (a.candidate/'evidence/actual-glb-audit.json').open('x') as output:json.dump(result,output,indent=2)
    print(json.dumps(dict(status=result['status'],checks=len(checks),failed=sum(not c['passed'] for c in checks))))
    if result['status']!='PASS':raise RuntimeError('Actual GLB audit failed')


if __name__=='__main__':main()
