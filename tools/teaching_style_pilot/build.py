"""Finite exact-source RLASM 6.1 teaching pilots; architectural-clay profile.

Run with Blender --background --python this_file -- --family prairie --output ...
The only reused geometry is audited low-level construction/evidence machinery.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'catalogue_duplex_pilot'))
sys.path.insert(0, str(HERE))
import clay_core as C
from contracts import lock_sources, verify_evidence, unobstructed_spans
import bpy
import family_library

ROOT = Path('C:/dev-artifacts/CityPrompt/teaching-gaps-20261025')


def cameras(width, depth, height, details):
    r = max(width, depth) * 2.2
    specs = []
    for name, loc in [('front', (0, -r, height*.65)),
                      ('front_corner', (r*.8, -r, height*2.1)),
                      ('aerial', (r*.6, -r*.7, height*4.7)),
                      ('top', (0, 0, r*1.5)),
                      ('left_side', (-r, 0, height*.7)),
                      ('right_side', (r, 0, height*.7)),
                      ('rear', (0, r, height*.65)),
                      ('rear_side', (r*.8, r, height*2))]:
        specs.append(dict(name=name, location=loc, target=(0, .001 if name=='top' else 0, 0 if name=='top' else height*.43),
                          **({'ortho_scale': max(width, depth)*1.4} if name=='top' else {})))
    specs.extend(dict(name=n, location=p, target=t, lens=l, whole=False) for n,p,t,l in details)
    return specs


def face_wall(face, name, u0, u1, z0, z1, holes, role='wall'):
    face.wall(name,u0,u1,z0,z1,depth=.30,role=role,holes=holes)
    for h in holes:
        if h.get('door'):
            face.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',glazed=h.get('glazed',False))
        else:
            face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=h.get('cols',1),frame='trim',depth=.30)


def hole(ident,u,z,w,h,**extra):
    return dict(id=ident,u=u,z=z,w=w,h=h,**extra)


def table(name,x,y,z=.17,width=1.5,depth=.8):
    C.box(name+' top',(x,y,z+.74),(width,depth,.065),'timber','interior')
    for xx in (-width*.4,width*.4):
        for yy in (-depth*.37,depth*.37):
            C.box(name+' leg',(x+xx,y+yy,z+.35),(.05,.05,.7),'timber','interior')


def chair(name,x,y,z=.17):
    C.box(name+' seat',(x,y,z+.43),(.45,.45,.055),'timber','interior')
    C.box(name+' back',(x,y+.20,z+.72),(.45,.045,.55),'timber','interior')
    for xx in (-.17,.17):
        for yy in (-.17,.17):
            C.box(name+' leg',(x+xx,y+yy,z+.21),(.035,.035,.42),'timber','interior',0)


def prairie_spec():
    details=[('facade_close',(0,-12,3.1),(0,-4.6,1.6),46),
             ('architecture_close',(11,-10,5.2),(6,-4,3.15),48),
             ('glass_close',(4.6,-7.6,2.0),(4.6,-4.2,1.7),48),
             ('chimney_contact',(-8.5,9.5,7.6),(-5.3,5.0,4.8),48),
             ('living_programme',(4.4,-4.5,1.8),(3,0,1.25),38),
             ('entrance_low',(2,-8,1.25),(0,-4.6,1.1),40)]
    return dict(archetype_id='prairie_school_house',variant_id='roman_brick_hip_roof',
        candidate='prairie-school-house-clay',title='Prairie School house',style='Prairie School',
        reference='prairie-school-house-original-reference-board.png',
        references={r:'prairie-'+r+'.png' for r in ('front','oblique','top')},
        dimensions_m=dict(width=16,depth=10,height=5.8),floors=1,
        teaching=dict(description='Prairie School houses use low roofs, broad eaves and bands of windows to emphasize the horizon. Rooms often connect more openly to one another and to the landscape.',
            features=['Low hipped roof with broad eaves','Horizontal window and stone bands','Broad chimney and restrained asymmetry'],
            main_idea='Connect domestic space to the horizontal landscape.',
            source='https://www.flwright.org/explore/prairie-style'),
        cameras=cameras(18.3,12.3,4.8,details),
        palette=dict(wall=(.36,.16,.095),trim=(.13,.085,.045),stone=(.65,.57,.42),roof=(.12,.105,.085),
                     timber=(.26,.13,.052),interior=(.73,.70,.61),glass=(.58,.68,.65),hardware=(.15,.16,.14),
                     floor=(.39,.29,.18),artglass=(.62,.46,.18)),
        measurement_notes=['Four casements in each front band, centred entrance with two sidelights.',
            'The visible right side has three casements, not the four requested in the generation prompt; model follows pixels.',
            'Original rear quadrant has mirrored handedness and is rejected. Additional rear generation has chimney-position drift and is also rejected. Rear and left are explicit architectural inferences; only compatible front/oblique/top govern identity.',
            'Top-source chimney cap centre is approximately x=-5.3m,y=5.0m, about 9 percent of roof depth from rear eave.',
            'Single closed hip; broad chimney on rear-left quarter; no invented roof wings.',
            'Front source roof rise/width is approximately80/748=.10695. Read-only camera calibration gives ridge5.75m, cap5.8m; requested prompt heights were not reliable pixel measurements.',
            '16 x 10m walls; complete roof envelope 18.3 x 12.3m. Native plot must contain eaves and entrance apron.'])


def prairie():
    C.box('Native house floor and foundation',(0,0,.085),(16,10,.17),'floor','foundation',0)
    front=C.Face((0,-5,0),(1,0,0),(0,1,0),'front')
    recessed=C.Face((0,-4.6,0),(1,0,0),(0,1,0),'entrance recess')
    left=C.Face((-8,0,0),(0,1,0),(1,0,0),'left')
    right=C.Face((8,0,0),(0,1,0),(-1,0,0),'right')
    rear=C.Face((0,5,0),(1,0,0),(0,-1,0),'rear')
    for u0,u1,u in [(-8,-1.4,-4.55),(1.4,8,4.55)]:
        face_wall(front,'Front Roman brick wing',u0,u1,.17,3.3,[hole('four-casement band '+str(u),u,.90,4.40,1.66,cols=4)])
        for z,h in [(.77,.15),(2.72,.17)]:
            front.part('Continuous limestone horizontal belt',(u0+u1)/2,-.025,z,u1-u0,.085,h,'stone','horizontal datums')
    face_wall(recessed,'Recessed entry brick',-1.4,1.4,.17,3.3,[hole('Main entrance',0,.17,.98,2.35,door=True),
        hole('Left entry sidelight',-.88,.24,.38,2.29),hole('Right entry sidelight',.88,.24,.38,2.29)])
    for x in (-1.4,1.4): C.box('Entry recessed masonry return',(x,-4.78,1.735),(.12,.44,3.13),'wall','entry')
    C.box('Entry lintel',(0,-4.8,2.95),(2.8,.4,.30),'timber','entry')
    face_wall(right,'Right complete wall',-4.7,4.7,.17,3.3,[hole('Right three-casement band',0,.9,3.3,1.66,cols=3)])
    face_wall(left,'Left complete wall',-4.7,4.7,.17,3.3,[hole('Left paired casements A',-2.2,.9,2.2,1.66,cols=2),hole('Left paired casements B',2.2,.9,2.2,1.66,cols=2)])
    face_wall(rear,'Rear complete wall',-8,8,.17,3.3,[hole('Rear right three casements',4.5,.9,3.3,1.66,cols=3),
        hole('Rear middle three casements',.0,.9,3.3,1.66,cols=3),hole('Garden door',-3.2,.17,1.04,2.39,door=True,glazed=True)])
    for f,span in [(left,10),(right,10),(rear,16)]:
        for z,h in [(.77,.15),(2.72,.17)]:
            segments=unobstructed_spans(-span/2,span/2,[(-3.72,-2.68)] if f is rear and z<2.5 else [])
            for lo,hi in segments:f.part('Unobstructed limestone belt',(lo+hi)/2,-.025,z,hi-lo,.085,h,'stone','horizontal datums')
    # One closed four-plane weathering roof, with a supported deep eave.
    w=9.15;d=6.15;e=3.38;b=3.23;r=5.75;k=3.0
    vs=[(-w,-d,e),(w,-d,e),(w,d,e),(-w,d,e),(-w,-d,b),(w,-d,b),(w,d,b),(-w,d,b),(-k,0,r),(k,0,r)]
    fs=[(0,1,9,8),(1,2,9),(2,3,8,9),(3,0,8),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    C.mesh('Single closed low hipped roof',vs,fs,'roof','weathering roof')
    C.box('Deep front eave fascia',(0,-d,3.25),(2*w,.10,.19),'timber','roof edge')
    C.box('Deep rear eave fascia',(0,d,3.25),(2*w,.10,.19),'timber','roof edge')
    for x in (-w,w):C.box('Deep side eave fascia',(x,0,3.25),(.10,2*d,.19),'timber','roof edge')
    C.box('Broad continuous chimney',(-5.3,5.0,2.87),(1.8,1.0,5.74),'wall','chimney')
    C.box('Chimney stone cap',(-5.3,5.0,5.75),(1.98,1.18,.10),'stone','chimney')
    # Bounded saddle/flashing over the actual roof plane, not a floating collar.
    roofz=lambda x,y: e+(r-e)*min((w-abs(x))/(w-k),(d-abs(y))/d)
    corners=[(-6.26,4.44),(-4.34,4.44),(-4.34,5.56),(-6.26,5.56)]
    C.solid_surface('Chimney seated flashing',[(x,y,roofz(x,y)+.025) for x,y in corners],.045,'hardware','chimney contact')
    C.box('Front small entrance landing',(0,-5.18,.07),(2.45,1.2,.14),'stone','entry')
    C.box('Garden threshold',(-3.2,5.25,.07),(1.3,.65,.14),'stone','entry')
    # Actual bounded leaded art-glass border geometry, one owner per feature.
    for center in (-4.55,4.55):
        for i in range(4):
            u=center-2.2+1.1*(i+.5)
            for off in (-.35,.35): front.part('Art-glass border lead',u+off,.151,1.73,.018,.015,1.27,'artglass','art glass',0)
            for z in (1.13,2.34):front.part('Art-glass horizontal lead',u,.151,z,.73,.015,.018,'artglass','art glass',0)
    # Enclosed occupied plan; hidden partitions are explicit inferences.
    C.box('Plaster ceiling below roof',(0,0,3.10),(15.4,9.4,.10),'interior','interior',0)
    C.box('Rear bedroom division',(-1.9,2.95,1.60),(.12,3.5,2.86),'interior','interior')
    partition=C.Face((0,1.2,0),(1,0,0),(0,1,0),'bedroom partition')
    partition.wall('Rear bedroom partition A',-7.7,-1.9,.17,3.03,depth=.12,role='interior',
                   holes=[hole('Open bedroom passage',-2.65,.17,1.0,2.1)])
    table('Dining table',-4,-1.4,width=1.9,depth=.95)
    for x in (-4.6,-3.4):chair('Dining chair',x,-.6);chair('Dining chair',x,-2.2)
    C.box('Living sofa',(4.8,-1.4,.55),(2.7,.9,.75),'interior','interior')
    C.box('Sofa back',(4.8,-1.0,.85),(2.7,.18,.9),'timber','interior')
    table('Coffee table',4.4,-2.8,width=1.1,depth=.6)
    for x in (-3.3,.7):
        C.box('Bed base',(x,3,.35),(2.0,1.8,.36),'timber','interior')
        C.box('Bed mattress',(x,3,.60),(1.95,1.75,.20),'interior','interior')
    for loc in [(-4,-1,2.8),(4,-1,2.8),(-5,3,2.8),(1,3,2.8)]:C.qa_room_light('House room',loc,80,2.8)
    C.CONTACTS.extend([dict(name='Deep eave',supported_by='continuous masonry walls and timber soffit',overhang_m=1.15),
        dict(name='Chimney',base_m=0,top_m=5.8,penetrates_closed_roof=True),
        dict(name='Main threshold',landing_top_m=.14,door_base_m=.17,concept_step_m=.03)])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--family',choices=['prairie','library'],required=True)
    parser.add_argument('--output',required=True);parser.add_argument('--version',type=int,default=1)
    parser.add_argument('--resolution',type=int,default=1600);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    spec=prairie_spec() if args.family=='prairie' else family_library.specification(cameras)
    out=Path(args.output).resolve()
    if ROOT.resolve() not in out.parents:raise ValueError('Output must be in the named external batch')
    refs=spec.get('references',{r:spec['reference'] for r in ('front','oblique','top')})
    sources=lock_sources(spec['archetype_id'],spec['variant_id'],{r:ROOT/'references'/p for r,p in refs.items()})
    verify_evidence(sources,ROOT)
    if out.exists():raise ValueError('Candidate exists; preserve it and use a new version')
    if args.dry_run:
        print(json.dumps(dict(status='DRY_RUN_PASS',sources=len(sources),cameras=len(spec['cameras']),family=args.family)));return
    out.mkdir(parents=True)
    for name in ('sources','scripts','renders','review','evidence','boards'): (out/name).mkdir()
    for p in {Path(s['original_path']) for s in sources}:shutil.copy2(p,out/'sources'/p.name)
    provenance=ROOT/'references'/spec.get('provenance_file','source-provenance.json')
    if provenance.exists():shutil.copy2(provenance,out/'sources/source-provenance.json')
    for p in (Path(__file__),HERE/'contracts.py',HERE/'family_library.py',Path(C.__file__)):shutil.copy2(p,out/'scripts'/p.name)
    shutil.copy2(HERE.parents[1]/'docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md',out/'review/runtime-integration-NOT-TESTED.md')
    manifest=dict(candidate=spec['candidate']+f'-v{args.version:03d}',method='RLASM v6.1',representation_kind='architectural_clay',
        archetype_id=spec['archetype_id'],variant_id=spec['variant_id'],state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=spec['dimensions_m'],floors=spec['floors'],observations=spec['measurement_notes']),
        source_contract=dict(sources=sources,source_origin='Original generated design; not an existing historic building'),
        identity_contract=dict(owner='Exact-source physical geometry; no bitmap identity in architectural-clay profile'),
        material_contract=dict(profile='Source palette architectural clay; no textures or PBR keeper claim'),
        roof_contract=spec['measurement_notes'],programme_contract='Occupied rooms and usable entry, explicit hidden-view inferences',
        contact_contract=['Complete foundation','Through-carrier apertures','Supported roof','Seated weathering connections'],
        runtime_contract=dict(scale='fixed_native_only',resizing=False,installation='not installed',review='NOT TESTED'),
        camera_roster=spec['cameras'],teaching=spec['teaching'],
        provenance=dict(builder='Codex',base_commit='c622c7575',working_scripts_archived=True,render_source='exact GLB reimport'))
    C.write_json(out/'prework-manifest.json',manifest)
    cams=C.setup(spec['palette'],spec['cameras'],args.resolution)
    bpy.context.scene.view_settings.exposure=.7
    # Green neutral context is QA-only; never export a full rectangular site pad.
    ground=bpy.data.objects.get('QA ground - excluded')
    ground.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.27,.34,.19,1)
    if args.family=='prairie':prairie()
    else:family_library.construct(face_wall,hole,table,chair)
    C.deliver(out,manifest,cams)
    verify_evidence(sources,out,require_renders=True)


if __name__=='__main__':main()
