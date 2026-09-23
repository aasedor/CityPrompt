"""Original summer-market concept. Does not relabel the mismatched reference cards."""
import argparse
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import scene as S

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    recipe=dict(id='student_summer_market_plaza_v1',version=1,domain='open_space',authorship='original concept',
        dimensions_m=[32,28],axes='X east, Y north, Z up; metres',base_datum='walking plane Z=0',
        plot_policy='Fixed 32 x 28 m first pilot; translation and rotation only. No stretching or cropping.',
        surface_owner='shared terrain-following runtime mesh; preview substrate is NOT a rigid runtime park slab',
        programme=dict(stalls=6,benches=4,raised_planters=4,lights=4,open_event_square_m=[12,14]),
        entrances=[dict(x=0,y=-14,width=4),dict(x=0,y=14,width=4),dict(x=-16,y=3.5,width=3),dict(x=16,y=3.5,width=3)],
        tree_policy='No baked trees. Runtime may add shared GlobeLandscapeTreeStand only in reviewed planting footprints.',
        limitations=['No fountain or retail buildings advertised.','Level/prepared-ground visual pilot only; natural-ground component seating untested.',
        'Not an exact-source reconstruction: existing summer-market and market-square cards fail identity audit.',
        'No runtime adapter, picker activation, save/reload or exact export tested.'],placements=[])
    if a.dry_run:
        assert 6*3.2*2.8<32*28;print('DRY_RUN_PASS',recipe);return
    a.output.mkdir(parents=True,exist_ok=False)
    for f in ('build.py','scene.py'):shutil.copy2(Path(__file__).with_name(f),a.output/f)
    S.init();modules={}
    # Furniture authored at module origin, exported once, then copied for the fixture.
    before=set(S.bpy.context.scene.objects)
    for x in (-1.45,1.45):
        for y in (-1.15,1.15):S.box('Stall post',(x,y,1.2),(.12,.12,2.4),'timber')
    S.box('Vendor counter',(0,-.88,.95),(2.8,.56,.10),'timber')
    for x in (-1.2,1.2):S.box('Counter leg',(x,-.88,.46),(.09,.42,.92),'timber')
    for y in (-1.15,1.15):S.box('Canopy beam',(0,y,2.35),(3.12,.12,.16),'timber')
    S.mesh('Ochre canvas canopy',[(-1.65,-1.4,2.4),(1.65,-1.4,2.4),(1.65,0,2.9),(-1.65,0,2.9),(-1.65,1.4,2.4),(1.65,1.4,2.4)],[(0,1,2,3),(3,2,5,4)],'ochre')
    stall=list(set(S.bpy.context.scene.objects)-before);modules['market-stall']=stall
    before=set(S.bpy.context.scene.objects);S.bench(0,0);modules['timber-bench']=list(set(S.bpy.context.scene.objects)-before)
    before=set(S.bpy.context.scene.objects)
    for x in (-1.5,1.5):S.box('Planter short wall',(x,0,.28),(.12,2,.56),'stone')
    for y in (-1,1):S.box('Planter long wall',(0,y,.28),(3.12,.12,.56),'stone')
    S.box('Planter soil',(0,0,.45),(2.88,1.88,.12),'soil')
    for x in (-1,-.5,0,.5,1):
        for y in (-.6,0,.6):S.grass(x,y,.51,int((x+2)*7+y*3))
    modules['prairie-planter']=list(set(S.bpy.context.scene.objects)-before)
    before=set(S.bpy.context.scene.objects);S.lamp(0,0);modules['plaza-light']=list(set(S.bpy.context.scene.objects)-before)
    # Save native origin modules before placing each copy. Hidden prototypes are removed afterwards.
    assets={k:S.export(a.output/(k+'.glb'),v) for k,v in modules.items()}
    placements={'market-stall':[(x,y) for x in (-10,10) for y in (-7,0,7)],
        'timber-bench':[(-5,-10),(5,-10),(-5,10),(5,10)],
        'prairie-planter':[(-11,-11),(11,-11),(-11,11),(11,11)],
        'plaza-light':[(-14,-10),(14,-10),(-14,10),(14,10)]}
    for key,positions in placements.items():
        for x,y in positions:
            import math
            angle=(math.pi/2 if x<0 else -math.pi/2) if key=='market-stall' else 0
            recipe['placements'].append(dict(module=key,x=x,y=y,z=0,rotation=angle))
            for original in modules[key]:
                obj=original.copy();obj.data=original.data;S.bpy.context.collection.objects.link(obj)
                ox,oy=obj.location.x,obj.location.y
                obj.location.x=x+ox*math.cos(angle)-oy*math.sin(angle)
                obj.location.y=y+ox*math.sin(angle)+oy*math.cos(angle);obj.rotation_euler.z+=angle
    for obs in modules.values():
        for obj in obs:S.bpy.data.objects.remove(obj,do_unlink=True)
    S.box('Preview paving only',(0,0,-.06),(32,28,.12),'pale')
    for x in range(-16,17,2):S.box('Paving joint',(x,0,.001),(.015,28,.002),'stone')
    for y in range(-14,15,2):S.box('Paving joint',(0,y,.001),(32,.015,.002),'stone')
    recipe['assets']=assets
    cameras=[('aerial',(34,-40,42),(0,0,0),49),('top',(0,0,60),(0,.001,0),44),
             ('entrance',(0,-32,9),(0,0,1),35),('market_close',(18,-19,12),(9,-7,1),15)]
    S.deliver(a.output,recipe,cameras,{})
    # Preserve the already exported origin modules in the final machine recipe.
    import json
    r=json.loads((a.output/'recipe.json').read_text());r['assets']=assets;S.save_json(a.output/'recipe.json',r)

if __name__=='__main__':main()
