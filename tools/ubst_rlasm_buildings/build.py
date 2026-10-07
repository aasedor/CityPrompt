"""Source-locked three-bay live/work pilot. No existing family composition reused."""
import argparse
import math
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / 'catalogue_services_batch'))
sys.path.append(str(HERE.parent / 'catalogue_affordable_five'))
import clay_core as C
from references import source_entry, SLUG
from assemblies import hole, faces, sofa, bed, desk, bathroom, vertical_cladding, seated_guard, shrub, garden_chair
from geometry import kitchen

PALETTE = dict(wall=(.66,.57,.40), brick=(.66,.57,.40), timber=(.46,.265,.12),
    trim=(.065,.075,.08), roof=(.10,.115,.13), foundation=(.39,.40,.38),
    glass=(.34,.40,.40), hardware=(.065,.075,.08), interior=(.79,.76,.68),
    floor=(.56,.43,.29), pale=(.67,.65,.57), planting=(.24,.31,.14),
    blue=(.16,.25,.28), joint=(.45,.41,.32))
GROUND, FIRST, SECOND, EAVE, RIDGE = .15, 3.93, 6.78, 9.48, 11.75


def cameras():
    whole = [('front',(0,-43,5.8)), ('front_corner',(30,-39,20)),
        ('aerial',(28,-32,45)), ('top',(0,0,55)), ('left_side',(-38,0,8)),
        ('right_side',(38,0,8)), ('rear',(0,40,8)), ('rear_side',(-30,36,20))]
    result = [dict(name=n,location=p,target=(0,.001 if n=='top' else 0,0 if n=='top' else 5),
                   **({'ortho_scale':24} if n=='top' else {})) for n,p in whole]
    details = [
        ('facade_close',(1,-18,7),(0,-5,5.9),52),
        ('architecture_close',(4,-10,2.3),(1.7,-4.8,1.9),42),
        ('glass_close',(-.5,-8,1.9),(-.8,-3.3,1.6),42),
        ('roof_contact',(5,-12,15),(3,-4.7,9.6),52),
        ('side_projection',(15,-9,6),(9,-1.6,5),42),
        ('interior',(.0,-4.55,1.8),(-1,1.5,1.4),24),
        ('stairs',(1.85,-4.5,1.75),(1.85,.8,3.4),20),
        ('upper_landing',(1,3.8,5.5),(1.8,-1,4.5),24),
        ('upper_stairs',(1.9,-4.45,5.5),(1.9,.8,6.1),20),
        ('bedroom',(.15,-3.9,8.3),(-1.35,-1.8,7.6),22),
        ('rear_entry',(3.8,9,2.4),(1.75,5,1.5),42),
        ('living',(.05,-3.8,5.5),(-1.25,.6,4.65),22),
        ('bathroom',(.35,3.0,8.35),(-1.5,4.0,7.55),20)]
    result += [dict(name=n,location=p,target=t,lens=l,whole=False) for n,p,t,l in details]
    return result


def open_door(face,h):
    """Recessed frame, glazed transom and inward-open leaf: clear access at grade."""
    u,z,w,height=h['u'],h['z'],h['w'],h['h']
    name=h['id']; leaf_h=min(2.45,height-.12)
    for sign in (-1,1):
        face.part(name+' jamb',u+sign*(w/2-.035),.15,z+height/2,.07,.12,height)
    face.part(name+' header',u,.15,z+height-.035,w,.12,.07)
    face.part(name+' transom rail',u,.15,z+leaf_h,w,.12,.065)
    if height>leaf_h+.12:
        face.part(name+' transom pane',u,.185,z+(leaf_h+height)/2,w-.14,.009,height-leaf_h-.08,'glass',soft=0)
    # Open 90 degrees inward from right hinge. Leaf sits alongside passage, not across it.
    hinge=u+w/2-.07; depth=.15+(w-.14)/2
    for du in (.15,.15+w-.14):
        face.part(name+' leaf stile',hinge,du,z+leaf_h/2,.055,.065,leaf_h)
    for zz in (z+.035,z+leaf_h-.035):
        face.part(name+' leaf rail',hinge,depth,zz,.055,w-.14,.07)
    face.part(name+' open optical leaf',hinge,depth,z+leaf_h/2,.009,w-.25,leaf_h-.14,'glass',soft=0)
    C.OPENINGS.append(dict(id=name,face=face.label,u=u,z=z,width=w,height=height,
        kind='inward-open glazed door',clear_wall_cut=True,carrier_depth_m=.26,
        frame_inset_m=.15,pane_inset_m=.185,face_origin=list(face.o),
        face_tangent=list(face.t),face_inward=list(face.n),
        occupied_space='physically open doorway into occupied continuous interior'))


def supported_stair(name,x,lower,upper,count):
    start=-3.55; length=5.46; run=length/count; rise=(upper-lower)/count
    # A single closed sawtooth slab, not solid blocks filling the lower flight's headroom.
    points=[(start,lower)]
    for i in range(count):
        points.extend([(start+i*run,lower+(i+1)*rise),
                       (start+(i+1)*run,lower+(i+1)*rise)])
    points.extend([(start+length,upper-.17),(start+.30,lower)])
    C.prism(name+' continuous supported flight',points,'x',x-.55,x+.55,'timber','stairs')
    for dx in (-.50,.50):
        C.beam(name+' handrail',(x+dx,start+.1,lower+1.1),(x+dx,start+length-.1,upper+1.0),.045,.045,'hardware','stairs')
        for i in range(count):
            C.box(name+' seated baluster',(x+dx,start+(i+.5)*run,lower+(i+1)*rise+.50),(.025,.025,1.0),'hardware','stairs',0)
    C.CONTACTS.append(dict(name=name,lower=lower,upper=upper,treads=count,
                          rise_m=rise,run_m=run,headroom='Stacked sloped flights; no solid under-stair fill.'))


def roof(x):
    """Three parallel roofs, shared uninterrupted valleys, source-derived 37 degree pitch."""
    for sign in (-1,1):
        edge=x+sign*3
        C.solid_surface('Closed standing seam roof',[(x,-5.12,RIDGE),(x,5.12,RIDGE),
            (edge,5.12,EAVE),(edge,-5.12,EAVE)],.14,'roof','roof weathering')
        for i in range(26):
            y=-5.08+i*10.16/25
            C.beam('Standing seam',(x,y,RIDGE+.014),(edge,y,EAVE+.014),.024,.022,'roof','roof morphology')
    C.beam('Continuous ridge cap',(x,-5.15,RIDGE+.012),(x,5.15,RIDGE+.012),.10,.06,'roof','roof weathering')
    for y in (-5,5):
        # Full gable and boards belong to the facade carrier below, avoiding a coplanar eave band.
        for sign in (-1,1):
            C.beam('Rake trim',(x,y*1.024,RIDGE-.065),(x+sign*3,y*1.024,EAVE-.065),.11,.11,'trim','roof edges')


def unit(index):
    x=(index-1)*6
    ff=faces(6,10,cx=x,label=f'Home {index+1} ')
    front=[hole('Studio shopfront',-.95,GROUND,3.15,3.47),hole('Residential entrance',1.94,GROUND,1.15,3.48)]
    for level,z in enumerate((4.22,7.10)):
        front += [hole(f'Front level {level+2} window {j+1}',u,z,1.60,2.20) for j,u in enumerate((-.95,1.25))]
    rear=[hole('Rear workroom window',1.10,.70,2.20,2.20),hole('Rear garden entrance',-1.9,GROUND,1.15,2.6)]
    for level,z in enumerate((4.40,7.25)):
        rear += [hole(f'Rear level {level+2} window {j+1}',u,z,1.45,1.80) for j,u in enumerate((-1.4,1.4))]
    for side,(f,span) in enumerate(zip(ff,(6,10,6,10))):
        if side==3 and index>0:
            continue # Exactly one shared party-wall carrier.
        external=side in (0,2) or (side==1 and index==2) or (side==3 and index==0)
        hs=front if side==0 else rear if side==2 else []
        if external and side in (1,3):
            hs=[hole('Side service entrance',0,GROUND,1.0,2.4)]
            hs += [hole(f'Side upper window {level}-{j}',u,z,1.5,1.8)
                   for level,z in enumerate((4.45,7.30)) for j,u in enumerate((-2.4,2.4))]
        half=span/2 if side in (0,2) else span/2-.26
        f.wall('Buff brick base' if external else 'Shared party wall',-half,half,GROUND,FIRST,
               depth=.26,role='brick' if external else 'interior',holes=hs)
        if side in (0,2):
            carrier=f.panel('Continuous cedar gabled facade',[(-half,FIRST),(half,FIRST),
                (half,EAVE-.14),(0,RIDGE-.14),(-half,EAVE-.14)],0,.26,'timber')
            carrier['rlasm_wall_carrier']=True
            for h in hs:
                if h['z']+h['h']>FIRST:
                    f.cut(carrier,h['id']+' full upper cut',h['u'],h['z'],h['w'],h['h'],.26)
            for j in range(40):
                u=-2.925+j*.15
                top=RIDGE-.15-abs(u)*(RIDGE-EAVE)/3
                spans=[(FIRST,top)]
                for h in hs:
                    if h['u']-h['w']/2-.01<u<h['u']+h['w']/2+.01:
                        spans=[s for a,b in spans for s in ((a,min(b,h['z'])),
                               (max(a,h['z']+h['h']),b)) if s[1]-s[0]>.001]
                for a,b in spans:
                    f.part('Continuous cedar board seam',u,-.012,(a+b)/2,.014,.028,b-a,'timber','cladding',0)
        else:
            f.wall('Cedar upper carrier' if external else 'Shared upper wall',-half,half,FIRST,EAVE,
                   depth=.26,role='timber' if external else 'interior',holes=hs)
        if external and side in (1,3):
            vertical_cladding(f,half*2,FIRST,EAVE,hs,spacing=.15,role='timber')
        for h in hs:
            if 'entrance' in h['id'].lower():
                open_door(f,h)
            elif h['id']=='Studio shopfront':
                # The wide source opening contains both a shop window and its own entry.
                # Keep a full-depth carrier hole, then give the two components one owner each.
                display_w=h['w']-1.10
                f.window('Studio display glazing',h['u']-.55,h['z'],display_w,h['h'],
                         cols=1,depth=.26,frame='trim',inset=.12)
                open_door(f,hole('Public studio entrance',h['u']+display_w/2,
                                GROUND,1.10,h['h']+h['z']-GROUND))
            else:
                f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2 if 'shopfront' in h['id'] else 1,
                         depth=.26,frame='trim',inset=.12)
    # Separate public studio and residential entrance corridor; connected through an open doorway.
    hall=C.Face((x+.83,0,0),(0,1,0),(-1,0,0),'Private stair passage')
    hall.wall('Studio and stair separation',-4.74,4.74,GROUND,FIRST-.20,depth=.12,
              role='interior',holes=[hole('Studio internal doorway',2.9,GROUND,1.0,2.3)])
    for z,below,count in ((FIRST,GROUND,21),(SECOND,FIRST,16)):
        slab=C.box('Occupied floor with stairwell',(x,0,z-.11),(5.48,9.48,.22),'floor','floors')
        C.cut_box(slab,'Open stairwell',(x+1.90,-.82,z-.11),(1.34,5.68,.6))
        supported_stair('Residential stair',x+1.90,below,z,count)
        for sx in (x+1.18,x+2.62):
            seated_guard('Seated stairwell guard',(sx,-3.66,z),(sx,1.96,z))
        seated_guard('Stairwell front guard',(x+1.18,-3.66,z),(x+2.62,-3.66,z))
    C.box('Top floor enclosed ceiling',(x,0,EAVE-.20),(5.48,9.48,.12),'interior','ceilings')
    # Studio furniture leaves the entrance corridor unobstructed.
    desk(x-1.0,-1.2,GROUND);desk(x-1.0,2.0,GROUND)
    sofa(x-1.1,-1,FIRST);kitchen(x-.7,4.2,FIRST,2.4)
    # Bedroom floor: two enclosed rooms with an open central passage alongside stairs.
    bedroom_hall=C.Face((x+.70,0,0),(0,1,0),(-1,0,0),'Bedroom hallway')
    bedroom_hall.wall('Bedroom enclosure',-4.74,4.74,SECOND,EAVE-.26,depth=.12,role='interior',
        holes=[hole('Front bedroom doorway',-1.0,SECOND,.90,2.1),hole('Rear bedroom doorway',1.6,SECOND,.90,2.1)])
    C.box('Bedroom cross wall',(x-1.0,0,(SECOND+EAVE-.26)/2),(3.48,.12,EAVE-.26-SECOND),'interior','partitions')
    bed(x-1.3,-2.0,SECOND);bed(x-1.3,1.4,SECOND)
    bath=C.Face((x,2.65,0),(1,0,0),(0,1,0),'Sanitary room')
    bath.wall('Sanitary room enclosure',-2.74,.70,SECOND,EAVE-.26,depth=.12,role='interior',
              holes=[hole('Bathroom doorway',.10,SECOND,.85,2.1)])
    bathroom(x-1.4,4.05,SECOND)
    roof(x)
    C.box('Rear grounded patio',(x,6,.06),(5.6,2,.12),'pale','garden')
    garden_chair(x-1.0,5.9,.12)
    C.box('Rear garden entrance pad',(x+1.9,5.3,.075),(1.2,.6,.15),'foundation','entry')
    for z in (3.5,6.4,9.05):
        for yy in (-2.6,2.6):
            C.qa_room_light('Occupied room',(x-1.1,yy,z),100,1.7)
        C.qa_room_light('Stair passage',(x+1.9,0,z),90,1.3)


def construct():
    C.box('Grounded building slab',(0,0,.075),(18,10,.15),'foundation','foundation')
    C.box('Continuous front threshold',(0,-5.25,.075),(18,.5,.15),'foundation','entry')
    C.box('Front pavement',(0,-5.9,.025),(18.6,.8,.05),'pale','pavement')
    for i in range(3):
        unit(i)
    for x in (-3,3):
        C.box('Shared valley weathering gutter',(x,0,EAVE+.01),(.18,10.3,.055),'roof','valleys')
        for y in (-5.17,5.17):
            C.rod('Valley downpipe',(x,y,.15),(x,y,EAVE),.048,'trim','drainage')
    for x in (-9.04,9.04):
        C.box('Outer eave fascia',(x,0,EAVE-.06),(.12,10.3,.15),'trim','eaves')
    for x in (-9,-3,3,9):
        C.box('Rear garden divider',(x,6.1,.6),(.08,2.2,1.2),'timber','garden')
    for x in (-8.5,-2.5,3.5,8.5):
        C.box('Planted front trough',(x,-5.95,.21),(.55,.6,.32),'foundation','planting')
        shrub(x,-5.95,.37,.30)


def manifest(version):
    cams=cameras()
    return dict(candidate=f'{SLUG}-clay-v{version:03d}',method=C.METHOD,
        representation_kind='architectural_clay',archetype_id=SLUG,variant_id=SLUG+'-v0',
        state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=18,depth=10,height=RIDGE),
            observed_storeys=3,source_measurements=['3 equal attached 6m bays; 12 upper front windows.',
            'Front pixels x147-1393, grade y850, eave y204, ridges y47-50, brick datum y588.',
            'At width18: eave9.33m above grade, ridge11.60m, brick3.78m; placed on .15m plinth.'],
            hidden_assumptions=['18x10m footprint authored, not surveyed.','Rear, left side and internal layouts inferred.',
            'High oblique reference is not a nadir orthophoto.']),
        roof_contract=dict(ridges=3,valleys=2,pitch_degrees=37.1,authority='Locked generated pixels'),
        identity_contract=dict(owner='Source-specific physical geometry',bitmap_stickers='None in clay review stage'),
        material_contract=dict(profile='Source-palette architectural clay',limitation='Textured keeper finish remains separate'),
        programme_contract=dict(storeys=3,dwellings=3,ground_workspaces=3,uses=['Live/work','Townhouse','Small studio'],
            legal_approval=False,description='Three independently entered homes over workspaces; stair-connected occupied floors.'),
        contact_contract=['Grade zero support','Through-carrier apertures','Open entrance leaves','Stacked continuous stairs',
                          'Occupied floors with open stairwells','Closed gable roof with continuous valley drainage'],
        runtime_contract=dict(scale='fixed_native_only',resizing=False,installation='not installed',review='NOT TESTED'),
        camera_roster=cams,mandatory_review_views=[v['name'] for v in cams])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--version',type=int,default=1)
    parser.add_argument('--resolution',type=int,default=1440)
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    entry=source_entry(ROOT);m=manifest(args.version);out=args.output.resolve()
    if not out.is_relative_to(Path('C:/dev-artifacts/CityPrompt').resolve()):
        raise ValueError('Generated output must be external')
    if args.dry_run:
        print('DRY_RUN_PASS: 3 locked sources; 21 predeclared views; no geometry or API calls');return
    out.mkdir(parents=True,exist_ok=False)
    for name in ('sources','scripts','renders','review','evidence','boards'):
        (out/name).mkdir()
    for source in entry['sources']:
        shutil.copy2(source['original_path'],out/source['path'])
        assert C.digest(out/source['path'])==source['sha256']
    shutil.copy2(Path(entry['_reference_root'])/'generation-provenance.json',out/'sources/generation-provenance.json')
    scripts=[Path(__file__),HERE/'references.py',Path(C.__file__),
             HERE.parent/'catalogue_affordable_five/assemblies.py',HERE.parent/'catalogue_affordable_five/geometry.py']
    for script in scripts:
        shutil.copy2(script,out/'scripts'/script.name)
    C.write_json(out/'source-entry.json',{k:v for k,v in entry.items() if not k.startswith('_')})
    m['source_contract']=dict(sources=entry['sources'],exact_variant_only=True,origin='original_generated_design',
                             generated_references_explicitly_requested=True,not_surveyed=True)
    m['provenance']=dict(scripts=[dict(path='scripts/'+p.name,sha256=C.digest(out/'scripts'/p.name)) for p in scripts],
        blender_version=C.bpy.app.version_string,python_version=sys.version,build_started_utc=C.utc(),
        generation_api_calls_during_build=0,reference_generation='built-in image_gen; exact prompts in source provenance',
        render_source='actual optimized GLB reimport only')
    C.write_json(out/'prework-manifest.json',m)
    cams=C.setup(PALETTE,m['camera_roster'],args.resolution)
    C.bevel=lambda *args,**kwargs: None
    for obj in C.bpy.context.scene.objects:
        if obj.type=='LIGHT':
            obj.location*=2;obj.data.energy*=4;obj.data.size*=2
    construct()
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data)
        C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.deliver(out,m,cams)


if __name__=='__main__':
    main()
