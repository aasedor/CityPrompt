"""Two original, bounded park concepts. Shared runtime terrain remains authoritative."""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import scene as S

def module(out, name, build):
    before=set(S.bpy.context.scene.objects);build()
    objects=list(set(S.bpy.context.scene.objects)-before)
    asset=S.export(out/(name+'.glb'),objects)
    return objects,asset

def place(objects,x,y,z=0):
    for original in objects:
        o=original.copy();o.data=original.data;S.bpy.context.collection.objects.link(o)
        o.location.x+=x;o.location.y+=y;o.location.z+=z

def picnic_table():
    for j in range(7):S.box('Table top slat',(0,-.35+j*.115,.78),(2,.10,.055),'timber')
    for x in (-.7,.7):
        for y in (-.65,.65):S.beam('Splayed table leg',(x,y,.04),(x,y*.45,.75),.06,'metal')
        S.box('Seat cross support',(x,0,.38),(.10,1.7,.08),'metal')
    for y in (-.75,.75):
        for dy in (-.1,.1):S.box('Picnic seat',(0,y+dy,.46),(2.1,.18,.06),'timber')
    # Foot pads sit at native grade rather than leaving diagonal leg tips unsupported.
    for x in (-.7,.7):
        for y in (-.65,.65):S.box('Table foot',(x,y,.025),(.22,.20,.05),'metal')

def pergola():
    for x in (-3.8,3.8):
        for y in (-2.8,2.8):
            S.box('Pergola foot',(x,y,.06),(.36,.36,.12),'stone')
            S.box('Pergola post',(x,y,1.4),(.18,.18,2.8),'timber')
    for y in (-2.8,2.8):S.box('Main timber beam',(0,y,2.78),(8.2,.20,.28),'timber')
    for x in (-3.8,3.8):S.box('Side timber beam',(x,0,2.78),(.20,5.6,.28),'timber')
    for i in range(15):S.box('Shade rafter',(-3.85+i*.55,0,2.99),(.10,6.3,.14),'timber')
    for x in (-3.8,3.8):
        for y in (-2.8,2.8):
            S.beam('Pergola knee brace',(x,y,2.15),(x-math.copysign(.6,x),y,2.64),.045,'timber')

def path(rect):
    x0,y0,x1,y1=rect;S.box('Preview walking surface',((x0+x1)/2,(y0+y1)/2,-.04),(x1-x0,y1-y0,.08),'pale')

def ground(bounds,paths,hole=None):
    rects=[bounds,*paths]+([hole] if hole else [])
    xs=sorted(set(v for r in rects for v in (r[0],r[2])))
    ys=sorted(set(v for r in rects for v in (r[1],r[3])))
    def inside(x,y,r):return r[0]<x<r[2] and r[1]<y<r[3]
    for x0,x1 in zip(xs,xs[1:]):
        for y0,y1 in zip(ys,ys[1:]):
            x,y=(x0+x1)/2,(y0+y1)/2
            if not inside(x,y,bounds) or (hole and inside(x,y,hole)):continue
            mat='pale' if any(inside(x,y,r) for r in paths) else 'grass'
            S.box('Single-owner ground cell',(x,y,-.04),(x1-x0,y1-y0,.08),mat)

def picnic(out):
    r=dict(id='student_picnic_garden_v1',dimensions_m=[28,24],programme=dict(pergolas=1,picnic_tables=4,benches=2,lights=2),
        entrances=[dict(x=-14,y=-6,width=3),dict(x=14,y=-6,width=3)],
        clear_routes=[[-14,-7.5,14,-4.5],[-1,-4.5,1,2.5]],
        surface_recipe=dict(lawn_rect=[-14,-12,14,12],paving_rects=[[-14,-7.5,14,-4.5],[-1,-4.5,1,-3.3],[-4.2,-3.3,4.2,3.3],[-8.5,1.5,-5.5,4.5],[5.5,1.5,8.5,4.5],[-8,-4.5,-6,1.5],[6,-4.5,8,1.5]]),
        tree_policy='Optional shared trees only after full crown, pergola and route clearance checks; none baked into assets.')
    defs={'picnic-table':picnic_table,'timber-pergola':pergola,'garden-bench':lambda:S.bench(0,0),'garden-light':lambda:S.lamp(0,0)}
    positions={'picnic-table':[(-2.2,0),(2.2,0),(-7,3),(7,3)],'timber-pergola':[(0,0)],'garden-bench':[(-6,-9),(6,-9)],'garden-light':[(-11,-9),(11,-9)]}
    ground([-14,-12,14,12],r['surface_recipe']['paving_rects'])
    return r,defs,positions

def rain(out):
    r=dict(id='student_rain_garden_v1',dimensions_m=[24,20],programme=dict(planted_basins=1,benches=4,interpretation_signs=1,lights=2),
        entrances=[dict(x=-12,y=0,width=2.5),dict(x=12,y=0,width=2.5)],
        clear_routes=[[-12,-1.25,-7.5,1.25],[7.5,-1.25,12,1.25],[-9.5,-7,-7.5,7],[7.5,-7,9.5,7],[-7.5,-7,7.5,-5],[-7.5,5,7.5,7]],
        basin=dict(rim_rect=[-6,-3.5,6,3.5],bottom_rect=[-4.5,-2,4.5,2],depth_m=.35,water='dry planted concept; no permanent water'),
        surface_recipe=dict(grass_rect=[-12,-10,12,10],exclude_basin=True),
        tree_policy='Basin planting is low prairie vegetation. No baked trees.',
        special_limitations=['Basin requires actual terrain depression; never overlay a negative bowl on intact Google tiles. Prepared-ground masking/excavation integration required.',
                            'Stormwater inlets, overflow, soil, infiltration and flood performance are not designed or certified.'])
    # Ground has one owner at every cell and a true hole for the basin.
    ground([-12,-10,12,10],r['clear_routes'],[-6,-3.5,6,3.5])
    outer=[(-6,-3.5,0),(6,-3.5,0),(6,3.5,0),(-6,3.5,0)]
    inner=[(-4.5,-2,-.35),(4.5,-2,-.35),(4.5,2,-.35),(-4.5,2,-.35)]
    S.mesh('Planted basin slopes',outer+inner,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'soil')
    S.mesh('Basin bottom',inner,[(0,1,2,3)],'soil')
    for x in range(-4,5):
        for y in (-1.5,-.5,.5,1.5):S.grass(x,y,-.35,int(x*7+y*3))
    def sign():
        for x in (-.45,.45):S.box('Interpretation post',(x,0,.52),(.07,.07,1.04),'metal')
        S.box('Interpretation panel',(0,0,1.08),(1.25,.50,.06),'stone')
    defs={'rain-garden-bench':lambda:S.bench(0,0),'interpretation-sign':sign,'rain-garden-light':lambda:S.lamp(0,0)}
    positions={'rain-garden-bench':[(-4,-8.3),(4,-8.3),(-4,8.3),(4,8.3)],'interpretation-sign':[(10,3)],'rain-garden-light':[(-10,-8),(10,8)]}
    return r,defs,positions

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['picnic','rain'],required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.dry_run:
        print('DRY_RUN_PASS',a.kind,'original concept, finite fixed footprint, no provider calls');return
    a.output.mkdir(parents=True,exist_ok=False)
    for f in ('build_gardens.py','scene.py'):shutil.copy2(Path(__file__).with_name(f),a.output/f)
    S.init();r,defs,positions=(picnic if a.kind=='picnic' else rain)(a.output)
    r.update(version=1,domain='open_space',authorship='original student concept',axes='X/Y plan, Z up; metres',
        plot_policy='Fixed footprint first pilot; translate/rotate only. No automatic scaling, clipping or irregular-plot claim.',
        terrain_policy='Shared measured runtime surfaces plus rigid furniture support; assembly-preview.glb is inspection only.',
        limitations=['Offline model only; runtime adapter, terrain, placement, persistence and capture untested.','No catalogue activation or independent review.'],placements=[])
    assets={}
    for name,build in defs.items():
        objects,assets[name]=module(a.output,name,build)
        for x,y in positions[name]:
            place(objects,x,y);r['placements'].append(dict(module=name,x=x,y=y,z=0,rotation=0))
        for o in objects:S.bpy.data.objects.remove(o,do_unlink=True)
    cams=[('aerial',(31,-35,33),(0,0,0),43),('top',(0,0,50),(0,.001,0),40),
          ('entrance',(25,-24,8),(0,0,.5),37),('detail',(12,-13,10),(0,0,.5),22)]
    S.deliver(a.output,r,cams,{})
    r=json.loads((a.output/'recipe.json').read_text());r['assets']=assets;S.save_json(a.output/'recipe.json',r)

if __name__=='__main__':main()
