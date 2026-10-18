"""Classic Concrete pilot: authored structure, open decks and continuous ramps.

Run with Blender --background --python <this file> -- --sources ... --output ...
Sources and every candidate are immutable. No network, seed or publication.
"""
import argparse
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'catalogue_services_batch'),str(HERE.parent/'final_five_buildings')]
import clay_core as C
import geometry as G
import specs as S

PALETTE=dict(concrete=(.52,.51,.46),deck=(.40,.405,.38),steel=(.08,.105,.115),
    glass=(.46,.59,.62),marking=(.82,.81,.72),yellow=(.86,.61,.06),sign=(.07,.10,.12))


def plate(name,rect,z,thick=.25,role='deck'):
    a,b,c,d=rect
    return C.box(name,((a+b)/2,(c+d)/2,z-thick/2),(b-a,d-c,thick),role,'floor structure',0)


def guard(name,a,b,height=1.10):
    for h in (.32,.68,height):
        C.beam(name+' horizontal rail',(a[0],a[1],a[2]+h),(b[0],b[1],b[2]+h),.045,.045,'steel','guards')
    n=math.ceil(math.dist(a,b)/1.5)
    for i in range(n+1):
        p=tuple(a[j]+(b[j]-a[j])*i/n for j in range(3))
        C.beam(name+' seated post',p,(p[0],p[1],p[2]+height),.055,.055,'steel','guards')


def text(name,value,loc,size,role='marking',rotation=(math.pi/2,0,0)):
    curve=C.bpy.data.curves.new(name,'FONT');curve.body=value;curve.size=size
    curve.align_x='CENTER';curve.extrude=.006;curve.resolution_u=2
    obj=C.bpy.data.objects.new(name,curve);C.bpy.context.collection.objects.link(obj)
    obj.location=loc;obj.rotation_euler=rotation
    C.bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    C.bpy.ops.object.convert(target='MESH');obj=C.bpy.context.object
    obj.data.materials.append(C.MATS[role]);C.tag(obj,role,'wayfinding')
    obj.select_set(False)


def flight(name,x,start_y,end_y,z0,z1,width=1.35):
    count=10;dy=(end_y-start_y)/count;dz=(z1-z0)/count
    outline=[(start_y,max(0,z0-.15)),(start_y,z0)]
    for i in range(count):
        outline.extend([(start_y+i*dy,z0+(i+1)*dz),(start_y+(i+1)*dy,z0+(i+1)*dz)])
    outline.append((end_y,z1-.15))
    C.prism(name,outline,'x',x-width/2,x+width/2,'concrete','pedestrian stairs')
    for xx in (x-width/2+.04,x+width/2-.04):
        C.beam(name+' continuous handrail',(xx,start_y,z0+1),(xx,end_y,z1+1),.04,.04,'steel','pedestrian stairs')
        for i in range(0,count+1,2):
            yy=start_y+i*dy;zz=z0+i*dz
            C.box(name+' supported baluster',(xx,yy,zz+.5),(.03,.03,1),'steel','pedestrian stairs',0)


def stair_tower(cx):
    # Exterior core bounds x=cx+-2.3, y=-17.9..-11.4; inside main envelope.
    for x in (cx-2.3,cx+2.3):
        for y in (-17.85,-11.45):
            C.box('Stair tower structural corner',(x,y,6.45),(.14,.14,12.6),'steel','stair tower frame',0)
    for level,z in enumerate(S.LEVELS):
        plate('Tower recessed full-level landing',(cx-2.25,cx+2.25,-17.75,-16.35),z,.15,'concrete')
        bridge=(25,25.35,-17.75,-16.35) if cx>0 else (-25.35,-25,-17.75,-16.35)
        plate('Inner doorway landing bridge',bridge,z,.15,'concrete')
        if level<3:
            mid=z+S.LEVEL_PITCH/2
            plate('Stair intermediate landing',(cx-2.25,cx+2.25,-13.05,-11.5),mid,.18,'concrete')
            flight('Stair ascending flight',cx-.95,-16.35,-13.05,z,mid)
            flight('Stair return flight',cx+.95,-13.05,-16.35,mid,S.LEVELS[level+1])
            guard('Stair landing edge',(cx-2.15,-11.58,mid),(cx+2.15,-11.58,mid))
        # A door-sized side opening links each full landing to the main deck.
        # There is no pane across the ground-level street entrance.
        for y in (-17.85,-11.45):
            for x0,x1 in [(cx-2.3,cx-.8),(cx-.8,cx+.8),(cx+.8,cx+2.3)]:
                bottom=z+.12
                if level==0 and y==-17.85 and x0==cx-.8:bottom=z+2.4
                top=z+S.LEVEL_PITCH-.10 if level<3 else 12.6
                if top>bottom:
                    C.box('Stair optical pane',((x0+x1)/2,y,(bottom+top)/2),(x1-x0-.08,.012,top-bottom),'glass','stair glazing',0)
            C.box('Stair curtain transom',(cx,y,z+.04),(4.6,.14,.08),'steel','stair tower frame',0)
        for x in (cx-2.3,cx+2.3):
            inward=x==cx+2.3 if cx<0 else x==cx-2.3
            for ya,yb in [(-17.85,-16.4),(-16.4,-14.75),(-14.75,-13.1),(-13.1,-11.45)]:
                bottom=z+.12
                if inward and ya==-17.85:bottom=z+2.4
                top=z+3.20 if level<3 else 12.6
                if top>bottom:C.box('Side optical stair pane',(x,(ya+yb)/2,(bottom+top)/2),(.012,yb-ya-.08,top-bottom),'glass','stair glazing',0)
            C.box('Side tower transom',(x,-14.65,z+.04),(.14,6.4,.08),'steel','stair tower frame',0)
    for x in (cx-2.3,cx-.8,cx+.8,cx+2.3):
        C.box('Front stair glazing mullion',(x,-17.85,6.45),(.06,.12,12.6),'steel','stair tower frame',0)
    for x in (cx-2.3,cx+2.3):
        for y in (-16.4,-14.75,-13.1):C.box('Side stair glazing mullion',(x,y,6.45),(.12,.06,12.6),'steel','stair tower frame',0)
    plate('Tower seated roof cap',(cx-2.4,cx+2.4,-17.95,-11.35),12.8,.18,'steel')
    text('Parking tower letter','P',(cx,-17.94,11.6),.65,'marking')


def build_geometry():
    plate('Ground slab',(-30,30,-18,18),S.GROUND_TOP,.15)
    # Upper decks have full cut-through core wells and rear ramp wells.
    for z in S.LEVELS[1:]:
        for rect in S.main_deck_panels():plate('Open-well parking deck',rect,z)
        for rect in [(-30,-23,11.5,18),(23,30,11.5,18)]:plate('Ramp end landing',rect,z)
    for x in [-29.75,-24,-18,-12,-6,0,6,12,18,24,29.75]:
        for y in (-17.75,-5.75,5.75):
            # Corner tower owns its own supports, no opaque column through glass.
            if abs(x)>25 and y<-11:continue
            C.box('Continuous load-bearing concrete column',(x,y,5.65),(.5,.5,11),'concrete','concrete frame',0)
    for x in (-29.75,29.75):C.box('Rear landing column',(x,17.75,5.65),(.5,.5,11),'concrete','concrete frame',0)
    for z in S.LEVELS[1:]:
        for y in (-17.75,-5.75,5.75):
            # Main front beam terminates against the two glass towers.
            span=50.4 if y<-11 else 60
            C.box('Continuous deck-edge beam',(0,y,z-.32),(span,.48,.5),'concrete','concrete frame',0)
        for x in (-29.75,29.75):
            C.box('Side beam seated at rear core frame',(x,3.3,z-.32),(.5,29.4,.5),'concrete','concrete frame',0)
    for level in range(3):
        za,zb=S.LEVELS[level:level+2]
        C.solid_surface('Continuous rear vehicle ramp',[(S.RAMP_X[0],S.RAMP_Y[0],za),(S.RAMP_X[1],S.RAMP_Y[0],zb),
            (S.RAMP_X[1],S.RAMP_Y[1],zb),(S.RAMP_X[0],S.RAMP_Y[1],za)],S.RAMP_THICKNESS,'deck','vehicle ramps')
        for y in (S.RAMP_Y[0]+.06,S.RAMP_Y[1]-.06):
            guard('Sloping ramp protection',(S.RAMP_X[0],y,za),(S.RAMP_X[1],y,zb))
        for y in (11.65,17.85):
            # Edge girders lie outside the six-metre vehicle clearance. The
            # lowest girder tapers into the ground slab rather than below grade.
            top0,top1=za-S.RAMP_THICKNESS,zb-S.RAMP_THICKNESS
            if top0<.45:
                section=[(-23,top0),(23,top1),(23,top1-.45),(-23+(.45-top0)/S.LEVEL_PITCH*46,0),(-23,0)]
            else:section=[(-23,top0),(23,top1),(23,top1-.45),(-23,top0-.45)]
            if section[0]==section[-1]:section.pop()
            C.prism('Ramp continuous edge girder',section,'y',y-.09,y+.09,'concrete','ramp supports')
        # Contrast strips follow the ramp plane, avoiding coplanar paint.
        for y in (12.0,17.5):
            C.solid_surface('Ramp edge marking',[(-23,y-.04,za+.006),(23,y-.04,zb+.006),(23,y+.04,zb+.006),(-23,y+.04,za+.006)],.003,'yellow','road markings')
    for x in (-23,-12,0,12,23):
        top=S.ramp_height(2,x)-S.RAMP_THICKNESS
        for y in (11.65,17.85):C.box('Ramp edge ground-bearing pier',(x,y,top/2),(.18,.18,top),'concrete','ramp supports',0)
    for z in S.LEVELS[1:]:
        guard('Front open guard',(-25,-17.8,z),(25,-17.8,z))
        for xa,xb in [(-29.8,-23),(23,29.8)]:
            guard('Rear landing guard',(xa,17.85,z),(xb,17.85,z))
        guard('Main deck rear-well edge',(-23,11.43,z),(23,11.43,z))
        for x in (-29.8,29.8):guard('Side open guard',(x,-11.3,z),(x,17.85,z))
    # Bays have fixed 2.7 x 5.5m dimensions and no filled backing sheets.
    for level,z in enumerate(S.LEVELS):
        for ya,yb in [(-17,-11.5),(-5.5,0),(0,5.5)]:
            lo=-16.2 if ya==-17 else -21.6
            for i in range(round((21.6-lo)/2.7)+1):
                x=lo+i*2.7
                C.box('Parking stall stripe',(x,(ya+yb)/2,z+.006),(.075,yb-ya,.006),'marking','road markings',0)
            C.box('Parking row head line',((lo+21.6)/2,ya,z+.006),(21.6-lo,.075,.006),'marking','road markings',0)
        for x,y,rotation in [(0,-8.5,0),(0,8.5,math.pi)]:
            pts=[(x-2,y-.10,z+.01),(x+1,y-.10,z+.01),(x+1,y-.45,z+.01),(x+2,y,z+.01),(x+1,y+.45,z+.01),(x+1,y+.10,z+.01),(x-2,y+.10,z+.01)]
            if rotation:pts=[(2*x-a,2*y-b,c) for a,b,c in pts]
            C.solid_surface('Directional aisle arrow',pts,.004,'yellow','road markings')
    for cx in (-27.5,27.5):stair_tower(cx)
    # Vehicle portal spans one clear structural bay. Beam is above it.
    C.box('Vehicle entrance sign',(-21,-17.88,2.95),(5.45,.20,.65),'sign','wayfinding',0)
    text('Vehicle entrance lettering','ENTRANCE',(-21,-17.985,2.77),.40)
    for x in (-23.55,-18.45):C.box('Yellow vehicle entry jamb',(x,-17.82,1.3875),(.12,.12,2.475),'yellow','wayfinding',0)
    C.box('Yellow vehicle entry lintel',(-21,-17.82,2.625),(5.22,.12,.12),'yellow','wayfinding',0)
    for x in (-23.5,-18.5,-28.5,-26.5,26.5,28.5):
        C.rod('Seated yellow protective bollard',(x,-17.7,.15),(x,-17.7,1.2),.085,'yellow','bollards',10)
    for x,y in [(-15,0),(15,0),(-15,9.5),(15,9.5)]:
        C.rod('Roof light mast',(x,y,10.05),(x,y,12.5),.045,'steel','roof equipment',8)
        C.box('Roof light head',(x,y,12.5),(.65,.2,.07),'steel','roof equipment',0)


def manifest(version):
    cameras=G.camera_roster(60,36,12.8,[
        ('facade_close',(0,-40,6.8),(0,-17.75,5.5),48),
        ('architecture_close',(0,-10,1.8),(6,0,2.0),26),
        ('glass_close',(35,-26,7),(27.5,-14.5,6),40),
        ('ramp_headroom',(-30,8,5),(0,14.75,5),28),
        ('stair_contact',(33,-20,2.7),(27.5,-15,2.0),35),
        ('landing_seam',(23,-14,4.8),(25.2,-17,3.45),40),
        ('ramp_supports',(-18,22,3.5),(-12,17.85,3),32)])
    next(c for c in cameras if c['name']=='front_corner')['location']=(80,-90,42)
    return dict(candidate=f'parkade-classic-concrete-clay-v{version:03d}',method=C.METHOD,
        archetype_id='parkade-classic-concrete',variant_id='classic-concrete-v1',representation_kind='architectural_clay',
        state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=60,depth=36,height=12.8),observed_storeys=4,
            floor_top_datums_m=S.LEVELS,ground_datum_m=0,axes='Author Z-up; exported GLB Y-up; frontage -Y author / +Z GLB'),
        programme_contract=dict(parking_levels=4,stair_towers=2,vehicle_ramps=3,ramp_clear_width_m=6,
            ramp_run_m=46,ramp_rise_m=3.3,ramp_clear_height_m=3.1,bay_dimensions_m=[2.7,5.5],main_aisle_width_m=6,
            no_operational_animation=True,engineering_approval=False,capacity_claimed=False),
        material_contract=dict(profile='texture-free source-palette architectural clay',textured_keeper=False),
        inference_contract=['Supplemental ramp_section.png supersedes original rear-strip internal topology, arrows and transverse divisions. No full-width barriers across the ramp lane.',
            'Rear/side cadence and stair internals completed as original design.',
            'No accessibility, fire-egress, structural or swept-path certification.'],
        runtime_contract=dict(scale='fixed_native_only',storeys='fixed_authored_assembly',review='NOT TESTED'),
        camera_roster=cameras,mandatory_review_views=[c['name'] for c in cameras])


def main():
    p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True)
    p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1)
    p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);entry=S.source_entry(a.sources)
    review=json.loads((a.sources/'source-review.json').read_text(encoding='utf-8'))
    reviewed={item['sha256'] for item in review.get('inspected_files',[])}
    if (not (review.get('compatible') is True or review.get('source_coherence') == 'compatible_with_explicit_supplemental_original_design_authority')
        or review.get('unresolved_p0_p1_in_source_review_scope') != []
        or not {s['sha256'] for s in entry['sources']} <= reviewed):
        raise ValueError('Independent compatible source review required for exact four-source package')
    m=manifest(a.version)
    out=C.prepare_candidate(a,entry,m,__file__,extra_scripts=[HERE/'specs.py',a.sources/'generation-provenance.json',a.sources/'source-review.json'])
    if out is None:return
    cameras=C.setup(PALETTE,m['camera_roster'],a.resolution)
    C.bevel=lambda *args,**kwargs:None
    for name,position in [('key',(-55,-65,60)),('fill',(60,-35,45)),('rear',(-45,60,50))]:
        light=C.bpy.data.objects['QA '+name];light.location=position;light.data.energy*=18;light.data.size=35;C.look_at(light,(0,0,4))
    build_geometry()
    # Neutral QA luminaires reveal the delivered interior without overriding
    # exported materials. These inspection lights are explicitly not exported.
    for z in S.LEVELS[:3]:
        for x in (-18,0,18):
            for y in (-8,6):C.qa_room_light('parking deck',(x,y,z+2.65),power=500,size=8)
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data);C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.deliver(out,m,cameras)


if __name__=='__main__':main()
