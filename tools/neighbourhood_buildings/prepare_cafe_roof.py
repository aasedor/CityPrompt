"""Prepare exact planar roof faces with py_straight_skeleton 0.1.0.

Run outside Blender; the checked-in JSON is the deterministic build input.
Upstream: https://github.com/iconbuild/py_straight_skeleton (BSD-3-Clause).
"""
import argparse, ast, json, math, sys
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--deps',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.deps:sys.path.insert(0,str(a.deps))
    from py_straight_skeleton import compute_skeleton
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    source=ast.parse(Path(__file__).with_name('cafe_build.py').read_text())
    constants={n.targets[0].id:ast.literal_eval(n.value) for n in source.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('PLAN','UPPER_RING_DEPTH')}
    plan=constants['PLAN'];d=constants['UPPER_RING_DEPTH'];ring=[]
    for i,b in enumerate(plan):
        a0=plan[i-1];c=plan[(i+1)%len(plan)];v=(b[0]-a0[0],b[1]-a0[1]);w=(c[0]-b[0],c[1]-b[1]);lv=math.hypot(*v);lw=math.hypot(*w);v=(v[0]/lv,v[1]/lv);w=(w[0]/lw,w[1]/lw);n=(-v[1]*d,v[0]*d);m=(-w[1]*d,w[0]*d);den=v[0]*w[1]-v[1]*w[0];t=((m[0]-n[0])*w[1]-(m[1]-n[1])*w[0])/den;ring.append((b[0]+n[0]+v[0]*t,b[1]+n[1]+v[1]*t))
    polygon=Polygon(ring);assert polygon.is_valid
    skeleton=compute_skeleton(exterior=ring,holes=[])
    nodes=[[n.position.x,n.position.y,n.time] for n in skeleton.nodes]
    faces=skeleton.get_faces();polys=[Polygon([nodes[i][:2] for i in f]) for f in faces]
    assert all(p.is_valid for p in polys)
    union=unary_union(polys)
    assert union.symmetric_difference(polygon).area<1e-6
    assert abs(sum(p.area for p in polys)-polygon.area)<1e-6
    report=dict(generator='py_straight_skeleton==0.1.0',upstream='https://github.com/iconbuild/py_straight_skeleton',plan=plan,depth=d,ring=ring,nodes=nodes,faces=faces,checks=dict(simple_boundary=True,complete_coverage=True,no_overlap=True,area_m2=polygon.area))
    with a.output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(nodes=len(nodes),faces=len(faces),max_time=max(n[2] for n in nodes),checks=report['checks'])))


if __name__=='__main__':main()
