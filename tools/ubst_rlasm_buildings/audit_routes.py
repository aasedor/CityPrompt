"""Probe floor support and headroom on the delivered GLB, independent of authored objects.

This is an offline centreline audit. It does not replace CityPrompt browser walking,
body-radius collision, accessibility, egress or code-compliance testing.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def routes(family='ubst-live-work-row'):
    if family!='ubst-live-work-row':
        yield from batch_routes(family)
        return
    for index in range(3):
        cx=(index-1)*6
        points=[(cx+1.94,-5.3,.15),(cx+1.94,-4.8,.15),(cx+1.9,-4.0,.15)]
        for lower,upper,count in ((.15,3.93,21),(3.93,6.78,16)):
            for i in range(count):
                points.append((cx+1.9,-3.55+(i+.5)*5.46/count,lower+(i+1)*(upper-lower)/count))
            points += [(cx+1.9,2.25,upper),(cx+.85,2.25,upper)]
            if upper==3.93:
                points += [(cx+.85,yy,upper) for yy in (1.5,0,-1.5,-3,-4.2)]
                points.append((cx+1.9,-4.2,upper))
        yield f'home-{index+1}-entry-and-two-stairs',points
        yield f'home-{index+1}-public-studio-entry',[
            (cx+.075,-5.3,.15),(cx+.075,-4.75,.15),(cx+.075,-4.0,.15),
            (cx+.40,-3.0,.15),(cx+.40,-1.2,.15),(cx+.40,1.0,.15),(cx+.40,2.8,.15)]


def batch_routes(family):
    if family=='ubst-timber-cohousing':
        flights=[(f'home-{i+1}',x+1.9,-3.55,.15,4.15,5.46) for i,x in enumerate((-9,-3,3,9))]
        for i,x in enumerate((-9,-3,3,9)):
            yield f'home-{i+1}-entry',[(x+1.94,y,.15) for y in (-5.4,-4.9,-4.4,-3.8)]
    elif family=='ubst-student-courtyard':
        flights=[('lower',6.8,5.7,.15,4.05,5.46),('upper',6.8,5.7,4.05,7.95,5.46)]
        yield 'lounge-entry',[(0,y,.15) for y in (4.5,5,5.5,6)]
    elif family=='ubst-garden-hotel':
        flights=[('lower',9,-.2,.15,4.90,7.2),('upper',9,-.2,4.90,8.70,7.2)]
        yield 'lobby-entry',[(.60,y,.15) for y in (-8.5,-8,-7.5,-7)]
    else:
        raise ValueError('No prescribed route for '+family)
    for name,x,y,lower,upper,length in flights:
        count=math.ceil((upper-lower)/.18)
        points=[(x,y-.12,lower)]
        points += [(x,y+(i+.5)*length/count,lower+(i+1)*(upper-lower)/count) for i in range(count)]
        points += [(x,y+length+.23,upper)]
        yield name+'-stair',points


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('candidate',type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    root=args.candidate.resolve()
    report=json.loads((root/'build-report.json').read_text())
    manifest=json.loads((root/'prework-manifest.json').read_text())
    glb=root/report['runtime']['path']
    if hashlib.sha256(glb.read_bytes()).hexdigest()!=report['runtime']['sha256']:
        raise ValueError('Delivered model hash mismatch')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    # Exclude optical panes from support and headroom. Real frames remain.
    for obj in list(bpy.data.objects):
        if obj.type=='MESH' and obj.get('cityprompt_semantic_role')=='glass':
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.view_layer.update()
    scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
    checks=[]
    for name,points in routes(manifest['archetype_id']):
        for i,(x,y,z) in enumerate(points):
            hit,where,_,_,obj,_=scene.ray_cast(deps,Vector((x,y,z+.10)),Vector((0,0,-1)),distance=.20)
            support=bool(hit and abs(where.z-z)<.025)
            obstruction=scene.ray_cast(deps,Vector((x,y,z+.035)),Vector((0,0,1)),distance=1.815)
            checks.append(dict(route=name,index=i,point=[x,y,z],support=support,
                measured_floor_z=float(where.z) if hit else None,
                clear_headroom_1_85m=not obstruction[0],
                obstruction=obstruction[4].name if obstruction[0] else None))
    result=dict(status='PASS_OFFLINE_ROUTE_PROBES' if all(c['support'] and c['clear_headroom_1_85m'] for c in checks)
                else 'FAIL_OFFLINE_ROUTE_PROBES',model_sha256=report['runtime']['sha256'],
                scope='Family-specific prescribed centrelines, floor support and 1.85m vertical clearance only; not continuous body collision, runtime or code approval.',
                samples=len(checks),checks=checks)
    with (root/'evidence/offline-route-probes.json').open('x') as handle:
        json.dump(result,handle,indent=2)
    failures=[c for c in checks if not c['support'] or not c['clear_headroom_1_85m']]
    print(json.dumps(dict(status=result['status'],samples=len(checks),failures=failures)))
    if failures:
        raise RuntimeError('Offline route probes failed')


if __name__=='__main__':
    main()
