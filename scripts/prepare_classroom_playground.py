"""Partition the finite playground's ground without overlapping surfaces.

Run with the backend Python environment (Shapely), then pass the resulting JSON
to tools/public_realm_assets/build_classroom_playground.py in Blender.
"""
import argparse
import json
from pathlib import Path
from shapely.geometry import Point, LineString, box
from shapely.affinity import scale
from shapely.ops import triangulate, unary_union


def ellipse(x, y, rx, ry):
    return scale(Point(x,y).buffer(1,resolution=32),rx,ry)


def covered_triangles(shape, depth=0):
    """Clip Delaunay triangles to concave boundaries, then triangulate pieces."""
    if shape.is_empty or shape.area<1e-10:return []
    if shape.geom_type!='Polygon':
        return [t for part in shape.geoms if part.geom_type in ('Polygon','MultiPolygon')
                for t in covered_triangles(part,depth)]
    result=[];coverage=shape.buffer(1e-8)
    for triangle in triangulate(shape):
        if coverage.covers(triangle):result.append(triangle)
        elif triangle.intersection(shape).area>1e-10:
            if depth>=3:raise ValueError('Ground triangulation did not converge.')
            result.extend(covered_triangles(triangle.intersection(shape),depth+1))
    return result


def prepare():
    site=box(-19,-18,19,18)
    interior=box(-16,-15,16,14).buffer(1.6,join_style=1).buffer(-1.6,join_style=1)
    soil=unary_union([site.difference(interior),Point(-15.7,-2).buffer(1.15),Point(15.7,-2).buffer(1.15)]).difference(box(-1.5,-18,1.5,-14))
    paved=unary_union([box(-1.5,-18,1.5,-10),box(-13,9,13,13.5)])
    regions=[('soil',soil),('paving',paved),
             ('paving.green',ellipse(-10,-10,5.6,5.4)),
             ('paving.orange',ellipse(10,-10,5.6,5.4)),
             ('paving.green',ellipse(1,3,5,5)),
             ('paving.blue',site)]
    remaining=site;result=[]
    for name,shape in regions+[('grass',site)]:
        owned=remaining.intersection(shape);remaining=remaining.difference(owned)
        triangles=covered_triangles(owned)
        if abs(sum(t.area for t in triangles)-owned.area)>1e-5:
            raise ValueError(f'Incomplete triangulation: {name}')
        result.append(dict(material=name,area_m2=owned.area,
                           triangles=[list(t.exterior.coords)[:3] for t in triangles]))
    assert abs(sum(r['area_m2'] for r in result)-1368)<1e-5
    return dict(dimensions_m=[38,36],ground_regions=result,
                equipment=[dict(name='inclusive-spinner',x=10,y=-10)],
                clear_routes=[dict(a=[0,-17.8],b=[0,-10],width=1.8),
                              dict(a=[0,-10],b=[3,-10],width=1.8),
                              dict(a=[3,-10],b=[3,0],width=1.8),
                              dict(a=[0,-10],b=[-3,-10],width=1.8),
                              dict(a=[-3,-10],b=[-3,-7],width=1.8),
                              dict(a=[-3,-7],b=[-5,-7],width=1.8)])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();data=prepare()
    if a.output.exists():raise ValueError('Use a fresh preparation path.')
    a.output.write_text(json.dumps(data,indent=2)+'\n')
    print('PASS: 1368 square metres, one ground owner per point; equipment unscaled.')
