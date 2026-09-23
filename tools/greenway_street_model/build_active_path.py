"""Original separated walking/cycling corridor; no runtime writes."""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import scene as S

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    bands=[dict(type='footpath',width_m=2.5),dict(type='planted_separator',width_m=.5),dict(type='two_way_cycle_track',width_m=3),dict(type='furniture_verge',width_m=2)]
    assert sum(b['width_m'] for b in bands)==8
    if a.dry_run:print('DRY_RUN_PASS: original 8 m active-travel concept; finite 36 m fixture');return
    a.output.mkdir(parents=True,exist_ok=False)
    for f in ('build_active_path.py','scene.py'):shutil.copy2(Path(__file__).with_name(f),a.output/f)
    S.init();r=dict(id='student_separated_active_path_v1',version=1,domain='path',authorship='original student concept',dimensions_m=[8,36],
        bands=bands,fixed_width_m=8,axes='X across, Y along, Z up; metres',base_datum='all travel surfaces Z=0',
        transport_modes=['walking','bicycle'],programme=dict(benches=2,bike_racks=2,lights=2,crossings=1),
        crossing=dict(y=0,width_m=3,separator_gap=True),
        route_policy='Shared street/path sweep at fixed width; reverse band ordering explicitly. Never bend assembled preview GLB.',
        tree_policy='No baked trees; shared stand only after full envelope/clearance checks.',
        limitations=['Offline straight, level fixture only. Runtime adapter, bent routes, slopes, edit recovery and export not tested.',
                    'Crossing is a concept treatment, not traffic or accessibility certification.','No motor vehicles or public-road junction supplied.'])
    S.box('Pedestrian paving',(-2.75,0,-.06),(2.5,36,.12),'pale')
    S.box('Two-way red cycle track',(.5,0,-.06),(3,36,.12),'red')
    S.box('Furniture verge',(3,0,-.06),(2,36,.12),'grass')
    for y in (-9.75,9.75):S.box('Planted separator',(-1.25,y,.04),(.5,16.5,.08),'grass')
    S.box('Flush separator opening',(-1.25,0,-.06),(.5,3,.12),'pale')
    # A through connection from footpath to the far side of the corridor.
    S.box('Verge crossing',(3,0,.001),(2,3,.002),'pale')
    for y in range(-16,18,3):
        if abs(y)>2:S.box('Cycle centre dash',(.5,y,.003),(.07,1.2,.004),'marking')
    for x in (-.25,1.25):
        direction=-1 if x<.5 else 1
        for y in (-11,11):
            S.box('Cycle direction shaft',(x,y,.003),(.075,.9,.004),'marking')
            for sign in (-1,1):
                o=S.box('Cycle arrow head',(x+sign*.14,y+direction*.38,.003),(.075,.46,.004),'marking');o.rotation_euler.z=sign*direction*math.pi/4
    for y in (-1,-.5,0,.5,1):S.box('Pedestrian crossing stripe',(.5,y,.003),(3,.22,.004),'marking')
    def rack():
        for y in (-.35,.35):S.beam('Cycle stand leg',(0,y,0),(0,y,.85),.035,'metal')
        S.beam('Cycle stand top',(0,-.35,.85),(0,.35,.85),.035,'metal')
    assets={};r['placements']=[]
    for name,build,positions in [('path-bench',lambda:S.bench(0,0),[(3,-9),(3,9)]),('cycle-stand',rack,[(3,-13),(3,13)]),('path-light',lambda:S.lamp(0,0),[(3,-16),(3,16)])]:
        before=set(S.bpy.context.scene.objects);build();objects=list(set(S.bpy.context.scene.objects)-before)
        assets[name]=S.export(a.output/(name+'.glb'),objects)
        for x,y in positions:
            angle=-math.pi/2 if name=='path-bench' else 0
            r['placements'].append(dict(module=name,x=x,y=y,z=0,rotation=angle))
            for orig in objects:
                o=orig.copy();o.data=orig.data;S.bpy.context.collection.objects.link(o)
                ox,oy=o.location.x,o.location.y;o.location.x=x+ox*math.cos(angle)-oy*math.sin(angle);o.location.y=y+ox*math.sin(angle)+oy*math.cos(angle);o.rotation_euler.z+=angle
        for o in objects:S.bpy.data.objects.remove(o,do_unlink=True)
    cams=[('aerial',(24,-29,27),(0,0,0),48),('top',(0,0,55),(0,.001,0),53),
        ('pedestrian',(-13,-24,7),(0,0,0),35),('crossing',(10,-7,10),(0,0,0),17)]
    S.deliver(a.output,r,cams,{})
    r=json.loads((a.output/'recipe.json').read_text());r['assets']=assets;S.save_json(a.output/'recipe.json',r)

if __name__=='__main__':main()
