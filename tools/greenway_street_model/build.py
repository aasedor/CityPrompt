"""Metric greenway segment study; route surfaces remain procedural at runtime."""
import argparse
import hashlib
import math
import shutil
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import scene as S

BANDS=[('setback',.3),('sidewalk',1.6),('boulevard',1),('shared_lane',2.6),
       ('shared_lane',2.6),('boulevard',1),('sidewalk',1.6),('setback',.3)]

def line(a,b,width=.055):
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    o=S.box('Sharrow paint',((a[0]+b[0])/2,(a[1]+b[1])/2,.005),(length,width,.004),'marking')
    o.rotation_euler.z=math.atan2(dy,dx)

def sharrow(x,y,direction):
    def p(a,b):return (x+a*direction,y+b*direction)
    # Wheel loops and frame, all flat geometry with no image dependency.
    for cx in (-.36,.36):
        for j in range(16):
            a=j*math.tau/16;b=(j+1)*math.tau/16
            line(p(cx+.25*math.cos(a),-.4+.25*math.sin(a)),p(cx+.25*math.cos(b),-.4+.25*math.sin(b)),.045)
    for a,b in [((-.36,-.4),(-.14,.04)),((-.14,.04),(.08,-.4)),((.08,-.4),(-.36,-.4)),
        ((-.14,.04),(.25,.05)),((.25,.05),(.08,-.4)),((.25,.05),(.36,-.4)),
        ((.25,.05),(.21,.23)),((.21,.23),(.38,.23)),((-.22,.08),(-.07,.08))]:line(p(*a),p(*b))
    for dy in (.65,.97):
        line(p(-.5,dy),p(0,dy+.26),.085);line(p(0,dy+.26),p(.5,dy),.085)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--source-root',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert abs(sum(w for _,w in BANDS)-11)<1e-8
    root=a.source_root/'frontend/public/archetypes/streets/neighborhood-greenway'
    sources=[root/f'variant_0{s}' for s in ('.png','_angle_60.jpg','_angle_90.jpg')]
    assert all(p.is_file() for p in sources)
    recipe=dict(id='student_greenway_segment_v1',version=1,domain='street',
        source_reference=dict(archetype='neighborhood_greenway',variant='neighborhood_greenway_v0',
        fidelity='Sectional concept based on the catalogue. NOT full exact-variant reconstruction; islands/junctions omitted.'),
        dimensions_m=[11,48],axes='X across, Y along, Z up; metres',base_datum='carriageway Z=0; sidewalks Z=0.15',
        fixed_width_m=11,bands=[dict(type=n,width_m=w) for n,w in BANDS],
        transport_modes=['walking','bicycle','automobile'],centre_line=False,
        programme=dict(speed_tables=1,sharrows=4,lights=4,parking_lanes=0),
        runtime_surface_owner='streetSectionProfiles/streetMesh3D and shared terrain; never repeat assembled preview GLB along bends',
        terrain_policy='Only offline level fixture built. Runtime must sample band edges and seat fixtures on shared terrain.',
        tree_policy='Use shared GlobeLandscapeTreeStand at reserved positions; no tree GLB or crown substitute baked here.',
        tree_positions=[dict(x=x,y=y,max_crown_radius_m=2.4,clear_trunk_height_m=2.4) for x in (-3.1,3.1) for y in (-17,17)],
        crossings=[dict(y=0,width=3,kind='flush pedestrian connection through boulevard with sidewalk ramps')],
        limitations=['No island, mini-circle or public-road junction is supplied by this straight-segment pilot.',
        'Do not inherit the existing reference variant runtime approval or overwrite its saved identity.',
        'No engineering, speed-control, accessibility or winter-maintenance certification.',
        'Bent routes, slope, approach connection, edit recovery and capture NOT TESTED.'])
    if a.dry_run:print('DRY_RUN_PASS: 11 m section, source triplet present, finite straight pilot');return
    a.output.mkdir(parents=True,exist_ok=False);(a.output/'sources').mkdir()
    for f in ('build.py','scene.py'):shutil.copy2(Path(__file__).with_name(f),a.output/f)
    recipe['sources']=[]
    for f in sources:
        shutil.copy2(f,a.output/'sources'/f.name)
        recipe['sources'].append(dict(path='sources/'+f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
    S.init();x=-5.5
    for kind,width in BANDS:
        center=x+width/2;z=0 if kind=='shared_lane' else .15
        mat='asphalt' if kind=='shared_lane' else 'grass' if kind in ('setback','boulevard') else 'pale'
        if kind in ('sidewalk','boulevard'):
            # Leave actual geometric holes for flush access, rather than burying a path below a slab.
            for sign in (-1,1):S.box(kind,(center,sign*13.75,z-.06),(width,20.5,.12),mat)
            if kind=='sidewalk':
                # Ramp from raised walk at +/-3.5 to flush crossing at +/-1.5.
                for sign in (-1,1):
                    y0,y1=sign*1.5,sign*3.5
                    S.mesh('Sidewalk access ramp',[(x,y0,0),(x+width,y0,0),(x+width,y1,.15),(x,y1,.15)],[(0,1,2,3)] if sign>0 else [(3,2,1,0)],'pale')
            else:
                for sign in (-1,1):S.box('Boulevard beside crossing',(center,sign*2.5,.09),(width,2,.12),'grass')
            S.box('Flush pedestrian access',(center,0,-.06),(width,3,.12),'pale')
        else:S.box(kind,(center,0,z-.06),(width,48,.12),mat)
        x+=width
    # Curb belongs to boulevard; crossing remains open.
    for x in (-2.67,2.67):
        for y in (-12.75,12.75):S.box('Curb with access gap',(x,y,.075),(.14,22.5,.15),'pale')
    for x,y,d in [(-1.3,-13,-1),(-1.3,17,-1),(1.3,-17,1),(1.3,13,1)]:
        S.box('Green sharrow field',(x,y+.3*d,.001),(1.5,2.5,.002),'green');sharrow(x,y,d)
    # One full-width speed table; no gap between table and ramps.
    S.mesh('Concept speed table',[(-2.6,5,0),(2.6,5,0),(-2.6,6,.075),(2.6,6,.075),
        (-2.6,8,.075),(2.6,8,.075),(-2.6,9,0),(2.6,9,0)],[(0,1,3,2),(2,3,5,4),(4,5,7,6)],'asphalt')
    for x in (-1.3,1.3):
        for y in (6.3,7.7):S.box('Table visibility marking',(x,y,.078),(.7,.12,.004),'marking')
    # Fixtures at the outer edge of the boulevard, clear of the 1.6 m sidewalk and crossing.
    before=set(S.bpy.context.scene.objects);S.lamp(0,0);prototype=list(set(S.bpy.context.scene.objects)-before)
    asset=S.export(a.output/'greenway-light.glb',prototype)
    for x in (-3.32,3.32):
        for y in (-9,21):
            for orig in prototype:
                o=orig.copy();o.data=orig.data;S.bpy.context.collection.objects.link(o);o.location.x+=x;o.location.y+=y;o.location.z+=.15
    for o in prototype:S.bpy.data.objects.remove(o,do_unlink=True)
    recipe['fixture_positions']=[dict(module='greenway-light',x=x,y=y,z=.15) for x in (-3.32,3.32) for y in (-9,21)]
    cameras=[('aerial',(26,-39,35),(0,0,0),60),('top',(0,0,70),(0,.001,0),66),
        ('pedestrian',(10,-27,7),(0,-4,.5),36),('access_close',(10,-8,8),(0,0,0),17),('table_close',(9,-1,7),(0,7,0),15)]
    S.deliver(a.output,recipe,cameras,{})
    import json
    r=json.loads((a.output/'recipe.json').read_text());r['assets']={'greenway-light':asset};S.save_json(a.output/'recipe.json',r)

if __name__=='__main__':main()
