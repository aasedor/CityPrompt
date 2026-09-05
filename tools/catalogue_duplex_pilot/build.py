"""One exact-source RLASM 6.1 clay duplex. No provider calls or runtime promotion.

Run with Blender --background --python build.py -- --source-root <checkout>
--output <external-new-candidate> [--dry-run]. Source pixels govern two storeys.
"""
from pathlib import Path
import argparse
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clay_core as C

PARENT = 'calgary_modern_infill_house'
VARIANT = 'infill_duplex'
PALETTE = {
    'wall': (.225, .215, .190), 'mortar': (.30, .285, .25),
    'timber': (.39, .245, .12), 'timber_joint': (.24, .145, .072),
    'trim': (.105, .115, .112), 'coping': (.32, .315, .285),
    'roof': (.61, .59, .53), 'foundation': (.42, .425, .40),
    'glass': (.36, .42, .40), 'hardware': (.075, .083, .080),
    'interior': (.61, .57, .47), 'floor': (.48, .39, .27),
}
GF, UP, SOFFIT, DECK, TOP = .90, 4.22, 8.30, 8.55, 8.84
# Model-native XY: front is -Y. The right half projects 0.35 m in front.
UNITS = [dict(label='west', x=-3.05, front=-7.75, side=-6.10, sign=-1),
         dict(label='east', x=3.05, front=-8.10, side=6.10, sign=1)]
CAMERAS = [
    dict(name='front', location=(0,-34,4.5),target=(0,-.8,4.5),ortho_scale=22),
    dict(name='front_corner',location=(19,-31,3.2),target=(0,-.6,4.0)),
    dict(name='aerial',location=(19,-28,31),target=(0,-.3,3.8)),
    dict(name='top',location=(0,-.7,40),target=(0,-.69,0),ortho_scale=27),
    dict(name='left_side',location=(-38,-.7,4.5),target=(0,-.7,4.5),ortho_scale=27),
    dict(name='right_side',location=(38,-.7,4.5),target=(0,-.7,4.5),ortho_scale=27),
    dict(name='rear',location=(0,36,4.5),target=(0,0,4.5),ortho_scale=23),
    dict(name='rear_side',location=(-26,30,18),target=(0,-.4,3.8)),
    dict(name='facade_close',location=(11,-21,11),target=(2,-7.9,5.2),whole=False,lens=62),
    dict(name='architecture_close',location=(9,-19,5.0),target=(1.6,-8.0,1.8),whole=False,lens=63),
    dict(name='glass_close',location=(8,-16,7.4),target=(4.1,-7.9,5.9),whole=False,lens=72),
    dict(name='roof_contact',location=(13,-17,17),target=(2,-4.3,8.5),whole=False,lens=55),
    dict(name='side_projection',location=(20,4,13),target=(6,3.8,5.7),whole=False,lens=56),
]


def source_entry(root):
    directory = root / 'frontend/public/archetypes/buildings/calgary-modern-infill-house'
    if (root / 'source-entry.json').is_file():
        entry = C.read_json(root / 'source-entry.json')
        entry['_reference_root'] = str(root / 'sources')
        return entry
    files = [('front','variant_2.png'),('oblique','variant_2_angle_60.jpg'),('top','variant_2_angle_90.jpg')]
    return dict(archetype_id=PARENT, variant_id=VARIANT, directory='.',
        _reference_root=str(directory), sources=[dict(role=role,
        original_path=str(directory/name),path='sources/'+name,
        bytes=(directory/name).stat().st_size,sha256=C.digest(directory/name)) for role,name in files])


def manifest(version):
    return dict(candidate=f'calgary-side-by-side-duplex-clay-v{version:03d}',method=C.METHOD,
        representation_kind='architectural_clay',archetype_id=PARENT,variant_id=VARIANT,
        state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        supersedes=f'calgary-side-by-side-duplex-clay-v{version-1:03d}' if version>1 else None,
        finite_corrections=['Separate the paired stairs, canopies and walks; remove overlapping tread/landing top faces.',
            'Cut both occupied slabs back at the entry recess and keep the foundation below the floor slab.',
            'Align canopy tops with the upper-floor datum and close internal stair-to-floor endpoints.',
            'Inset occupied slab edges inside exterior carriers and terminate the concrete plinth at the brick base; no coplanar floor/foundation stripe.',
            'Match the front-corner reference with a street-height camera; retain the full aerial roof view.',
            'Use three clearly observed small white roof pipes and continue front railing grammar at inferred rear stairs.',
            'Restore both source-visible near-grade glazing bands with real carrier cuts, recessed frames and two panes.',
            'Extend the shared wall into its coping underside; remove the unsupported 40 mm daylight slot.'] if version>1 else [],
        measurement_contract=dict(dimensions_m=dict(wall_width=12.20,wall_depth=15.60,
            ground_floor=GF,upper_floor=UP,roof_deck=DECK,coping_top=TOP),
            observed_storeys=2,dwelling_units=2,
            source_discrepancies=['Catalogue prose describes three storeys and two-tone stucco; all three locked views instead show two visible storeys, dark brick, cedar entry recesses and flat paired roofs. Pixels govern this exact model.'],
            source_measurements={
                'front':'Two outer tall glazing stacks and near-grade basement glazing bands; paired central recessed doors and separate straight entrance stairs. Upper cedar slit above each entry. Continuous brick piers; thin bronze-grey spandrels and eave fascia. Central dark party-wall divider.',
                'oblique':'Right half front edge projects slightly. Side brick wall continues behind tall front volume; a cedar-clad upper rear-side projection carries two small openings. Main upper glazing is approximately 1.5 times lower glazing height.',
                'top':'Two distinct flat membrane decks divided by a raised shared centre strip; stepped outer side edges, rear parapets, small roof penetrations. No pitched roof or invented third floor.',
                'scale':'Conceptual metres inferred from 2.2 m doors, 0.18 m steps and reference people. Not a measured survey. Relative facade/deck/entry geometry governs.'},
            hidden_assumptions=['Rear fenestration and internal partitions are inferred consistently from two separate homes; not claimed as photographed.',
                'Left upper side projection repeats the stepped outline visible in top view; its windows are inferred.',
                'Two separate residential circulation routes and modest furniture are inferred behind visible glazing.',
                'Only the above-grade basement glazing bands are visible; below-grade rooms and excavations are outside this asset. The bands open into the enclosed shallow volume below the ground-floor slab.',
                'Neighbouring buildings, alley garages, public street and mature contextual trees are excluded from this building asset.']),
        roof_contract=dict(type='two continuous flat decks with capped shared party wall',
            drainage='conceptual rear outlets with sealed roof penetrations; not engineering approval'),
        material_contract=dict(profile='texture-free semantic architectural clay',
            authority='exact locked brick/cedar/metal/concrete palette with geometric joints; no bitmap surfaces',
            limitations='No photorealistic weathering or textured-keeper claim.'),
        identity_contract=dict(owner='constructed facade, bay cadence, recesses and roof topology',
            bitmap_stickers='none in clay delivery; geometry owns every visible feature'),
        contact_contract=['Solid foundations reach Z=0; entry walks and six 0.15 m risers meet GF=.90.',
            'Canopies intersect the entry returns; full-depth door and window openings are cut in every carrier.',
            'Roof decks intersect wall heads; parapets and coping form continuous weathering edges.',
            'Upper side bays extend the occupied floor and bear on their authored exterior wall returns.'],
        camera_roster=CAMERAS,mandatory_review_views=[c['name'] for c in CAMERAS],
        programme_contract=dict(dwellings=2,independent_entries=2,party_wall=True,
            rooms='living/dining below, bedrooms/study above; independent internal stairs',
            excluded='Detached-home repetition and arbitrary dimensional scaling are not authorized.'))


def clear_segments(lo, hi, z0, z1, holes):
    segments=[(lo,hi)]
    for h in holes:
        if h['z'] < z1 and h['z']+h['h'] > z0:
            a,b=h['u']-h['w']/2-.025,h['u']+h['w']/2+.025
            segments=[part for l,r in segments for part in [(l,min(r,a)),(max(l,b),r)] if part[1]-part[0]>.0001]
    return segments


def skin(face, lo, hi, z0, z1, holes, timber=False):
    """Metric joints clipped around every physical opening; one surface owner."""
    if timber:
        for i in range(math.floor((hi-lo)/.145)):
            u=lo+(i+1)*.145
            zs=[(z0,z1)]
            for h in holes:
                if h['u']-h['w']/2-.025 < u < h['u']+h['w']/2+.025:
                    zs=[p for a,b in zs for p in [(a,min(b,h['z']-.025)),(max(a,h['z']+h['h']+.025),b)] if p[1]-p[0]>.01]
            for a,b in zs:face.part('Cedar vertical board joint',u,-.001,(a+b)/2,.004,.004,b-a,'timber_joint','source cedar joints',0)
    else:
        for row in range(math.ceil((z1-z0)/.083)):
            z=z0+row*.083
            for a,b in clear_segments(lo,hi,z-.002,z+.002,holes):
                face.part('Brick bed joint',(a+b)/2,-.001,z,b-a,.004,.004,'mortar','source brick joints',0)
            # Restrained brick head joints only on principal elevations.
            if face.label.endswith('front'):
                for col in range(math.ceil((hi-lo)/.25)):
                    u=lo+col*.25+(row%2)*.125
                    if u>=hi:continue
                    if clear_segments(u-.002,u+.002,z+.002,min(z+.08,z1),holes):
                        face.part('Brick staggered head joint',u,-.001,z+.04,.004,.004,min(.077,z1-z),'mortar','source brick joints',0)


def glazed(face, holes):
    for h in holes:
        if h.get('door'):
            face.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='trim',panels=1)
        else:
            face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=h.get('cols',1),rows=1,curtain=h.get('curtain',False))
            # Reference: narrow outer sash and short upper/lower transoms.
            if h.get('large'):
                sign=h.get('sign',1)
                face.part(h['id']+' asymmetric vertical mullion',h['u']+sign*h['w']*.27,.13,h['z']+h['h']/2,.045,.09,h['h']-.13,'trim','source opening cadence',.002)
                for fraction in (.17,.85):
                    face.part(h['id']+' reference transom',h['u'],.13,h['z']+h['h']*fraction,h['w']-.13,.09,.045,'trim','source opening cadence',.002)


def furniture(cx, front, sign):
    for level in (GF,UP):
        # Stairs occupy the inner half, with a genuine opening in the upper slab.
        sx=cx-sign*1.7
        for i in range(19):
            y=front+4.3+i*.25; z=GF+(i+1)*(UP-GF)/19
            if level==GF:C.box('Independent internal stair',(sx,y,(GF+z)/2),(1.0,.25,z-GF),'floor','residential circulation',0)
    for z in (GF,UP):
        C.box('Sofa or bedroom seat',(cx+sign*.7,front+2.45,z+.32),(1.65,.80,.64),'interior','residential room',.025)
        C.box('Sofa or bed back',(cx+sign*.7,front+2.80,z+.70),(1.65,.12,.8),'floor','residential room',.01)
        C.box('Table supported pedestal',(cx+sign*.4,front+1.2,z+.26),(.25,.4,.52),'floor','residential room',.005)
        C.box('Table top',(cx+sign*.4,front+1.2,z+.55),(1.1,.70,.08),'interior','residential room',.015)
    C.box('Kitchen base',(cx,6.85,GF+.45),(3.0,.6,.90),'interior','inferred rear kitchen',.01)
    C.box('Kitchen worktop',(cx,6.83,GF+.94),(3.08,.65,.08),'coping','inferred rear kitchen',.008)


def build():
    for unit in UNITS:
        label,cx,fy,side,sign=[unit[k] for k in ('label','x','front','side','sign')]
        lo,hi=cx-3.05,cx+3.05
        wx=cx+sign*.8; ex=cx-sign*2.2
        front=C.Face((0,fy,0),(1,0,0),(0,1,0),label+'_front')
        holes=[dict(id=label+' near-grade basement glazing',u=wx,z=.30,w=2.55,h=.40,cols=2),
               dict(id=label+' lower living glazing',u=wx,z=1.18,w=2.55,h=2.47,large=True,sign=sign,curtain=True),
               dict(id=label+' upper tall glazing',u=wx,z=4.45,w=2.55,h=3.35,large=True,sign=sign,curtain=True)]
        # Entry zone is a 0.60 m recess, not a door pasted onto the front plane.
        recess_lo,recess_hi=(lo,lo+1.60) if sign==1 else (hi-1.60,hi)
        solid_lo,solid_hi=(lo+1.60,hi) if sign==1 else (lo,hi-1.60)
        front.wall(label+' front brick carrier',solid_lo,solid_hi,.18,SOFFIT,holes=holes)
        skin(front,solid_lo,solid_hi,.18,SOFFIT,holes);glazed(front,holes)
        C.box(label+' facade floor spandrel',(wx,fy-.025,3.95),(2.68,.10,.51),'coping','front spandrel',.006)
        entry=C.Face((0,fy+.60,0),(1,0,0),(0,1,0),label+'_entry')
        eh=[dict(id=label+' independent front door',u=ex,z=GF,w=1.03,h=2.25,door=True),
            dict(id=label+' entry transom',u=ex,z=3.21,w=1.03,h=.37),
            dict(id=label+' upper cedar slit',u=ex,z=5.17,w=.63,h=1.85)]
        entry.wall(label+' cedar entry carrier',recess_lo,recess_hi,.18,SOFFIT,role='timber',holes=eh)
        skin(entry,recess_lo,recess_hi,.18,SOFFIT,eh,True);glazed(entry,eh)
        for x in (recess_lo,recess_hi):
            C.box(label+' solid cedar entry return',(x,fy+.3,(SOFFIT+.18)/2),(.08,.61,SOFFIT-.18),'timber','recess return',0)
        C.box(label+' supported entry canopy',(ex,fy+.05,UP-.12),(1.60,1.10,.24),'coping','entry canopy',.01)
        # Discrete grounded steps; landing reaches the actual threshold.
        for i in range(6):
            height=(i+1)*.15;y=fy-1.65+i*.30
            C.box(label+' entry riser '+str(i),(ex,y,height/2),(1.50,.30,height),'foundation','entry circulation',.005)
        C.box(label+' entrance landing',(ex,fy+.30,.45),(1.50,.60,.90),'foundation','entry circulation',.004)
        C.box(label+' entry walk',(ex,fy-2.50,.035),(1.50,1.40,.07),'foundation','entry circulation',.005)
        for edge in (-.73,.73):
            x=ex+edge
            C.rod(label+' stair handrail',(x,fy-1.80,1.0),(x,fy-.06,1.85),.025,'hardware','entry guard')
            for t in (0,.5,1):
                y=fy-1.8+t*1.74;z=1.0+t*.85
                C.rod(label+' seated stair post',(x,y,max(.02,t*.85)),(x,y,z),.022,'hardware','entry guard')
        # Foundation and occupied slabs. Upper stairwell is cut through its floor.
        C.box(label+' grounded full foundation',(cx,(fy+7.5)/2,.09),(6.10,7.5-fy,.18),'foundation','foundation',0)
        for level in (GF,UP):
            slab=C.box(label+' occupied slab',(cx-sign*.075,(fy+7.5)/2,level-.08),(5.95,7.5-fy-.30,.16),'floor','floor system',0)
            C.cut_box(slab,'Recess removes exposed slab shelf',((recess_lo+recess_hi)/2,fy+.25,level),(recess_hi-recess_lo+.002,.70,.70))
            if level==UP:
                C.cut_box(slab,'Actual upper stairwell',(cx-sign*1.7,fy+6.55,UP),(1.10,4.75,.7))
        # Outer side: brick at ground level, tall front slit, upper cedar bay.
        outer=C.Face((side,0,0),(0,1,0),(-sign,0,0),label+'_side')
        sh=[dict(id=label+' side tall slit',u=fy+2.05,z=4.68,w=.62,h=2.55),
            dict(id=label+' lower side slit',u=fy+2.05,z=1.46,w=.62,h=1.85),
            dict(id=label+' rear side ground window',u=5.65,z=1.75,w=1.00,h=1.20)]
        # The cedar projection replaces the upper brick carrier in its span.
        outer.wall(label+' lower side brick',fy,7.5,.18,UP,holes=sh)
        outer.wall(label+' upper front brick',fy,.35,UP,SOFFIT,holes=sh)
        outer.wall(label+' upper rear brick',5.7,7.5,UP,SOFFIT,holes=sh)
        skin(outer,fy,7.5,.18,UP,sh);skin(outer,fy,.35,UP,SOFFIT,sh);skin(outer,5.7,7.5,UP,SOFFIT,sh);glazed(outer,sh)
        projected=C.Face((side+sign*.38,0,0),(0,1,0),(-sign,0,0),label+'_cedar_bay')
        ph=[dict(id=label+' cedar side upper window A',u=1.50,z=5.91,w=.84,h=1.10),
            dict(id=label+' cedar side upper window B',u=3.40,z=5.91,w=.84,h=1.10)]
        projected.wall(label+' upper cedar bay',.35,5.7,UP,SOFFIT,role='timber',holes=ph)
        skin(projected,.35,5.7,UP,SOFFIT,ph,True);glazed(projected,ph)
        for y in (.35,5.7):C.box(label+' bay end return',(side+sign*.19,y,(UP+SOFFIT)/2),(.54,.20,SOFFIT-UP),'timber','cedar bay return',0)
        C.box(label+' bay occupied floor',(side+sign*.06,3.025,UP-.08),(.64,5.35,.16),'floor','cedar bay load path',0)
        rear=C.Face((0,7.5,0),(1,0,0),(0,-1,0),label+'_rear')
        rh=[dict(id=label+' rear dining window',u=wx,z=1.50,w=2.30,h=1.85,curtain=True),
            dict(id=label+' rear bedroom window',u=wx,z=4.70,w=2.30,h=2.15,curtain=True),
            dict(id=label+' rear door',u=ex,z=GF,w=1.03,h=2.25,door=True),
            dict(id=label+' rear upper study',u=ex,z=5.10,w=.80,h=1.40)]
        rear.wall(label+' enclosed rear',lo,hi,.18,SOFFIT,holes=rh);skin(rear,lo,hi,.18,SOFFIT,rh);glazed(rear,rh)
        C.box(label+' rear grounded landing',(ex,7.95,.45),(1.45,.8,.9),'foundation','rear circulation',.005)
        for i in range(6):
            height=.9-i*.15;C.box(label+' rear stair',(ex,8.50+i*.30,height/2),(1.45,.30,height),'foundation','rear circulation',.005)
        for dx in (-.70,.70):
            C.rod(label+' rear stair handrail',(ex+dx,8.35,1.85),(ex+dx,10.15,1.0),.025,'hardware','rear guard')
            for t in (0,.5,1):
                y=8.35+t*1.8;z=1.85-t*.85
                C.rod(label+' rear seated post',(ex+dx,y,max(.02,.90-t*.90)),(ex+dx,y,z),.022,'hardware','rear guard')
        # Single polygon deck per home, including the source side-bay step.
        outer_x=side+sign*.45;inner_x=0
        outline=[(inner_x,fy-.25),(side+sign*.2,fy-.25),(side+sign*.2,.15),
                 (outer_x,.15),(outer_x,5.85),(side+sign*.2,5.85),(side+sign*.2,7.7),(inner_x,7.7)]
        if sign==-1:outline.reverse()
        C.prism(label+' continuous roof deck',outline,'z',SOFFIT,DECK,'roof','roof deck')
        for a,b in zip(outline,outline[1:]+outline[:1]):
            if a[0]==b[0]==0:continue
            x,y=(a[0]+b[0])/2,(a[1]+b[1])/2
            length=math.dist(a,b)
            size=(length,.17,TOP-DECK) if a[1]==b[1] else (.17,length,TOP-DECK)
            C.box(label+' roof parapet',(x,y,(TOP+DECK)/2),size,'roof','weathering parapet',0)
            size=(length+.035,.24,.07) if a[1]==b[1] else (.24,length+.035,.07)
            C.box(label+' continuous coping',(x,y,TOP+.035),size,'coping','weathering cap',.003)
        C.box(label+' thin front fascia',(cx,fy-.30,SOFFIT+.14),(6.12,.10,.45),'coping','front roof edge',.005)
        # One west and two east pipes, seated through visible flashing bases.
        for x,y in ([(cx,0.20)] if sign==-1 else [(cx,0.20),(cx+sign*1.4,.55)]):
            C.box(label+' pipe flashing',(x,y,DECK+.018),(.25,.25,.045),'coping','roof fitting',.003)
            C.rod(label+' short roof penetration',(x,y,DECK-.10),(x,y,DECK+.32),.046,'roof','roof fitting')
        furniture(cx,fy,sign)
    party_top=TOP+.02  # 20 mm overlap into the cap: no floating coping.
    C.box('Shared party wall',(0,-.125,party_top/2),(.20,15.95,party_top),'wall','party wall',0)
    C.box('Shared capped centre weathering upstand',(0,-.25,TOP+.08),(.24,16.10,.16),'coping','party wall cap',.003)
    C.box('Front centre dark divider',(0,-8.03,4.38),(.16,.20,8.76),'trim','source centre divider',.005)
    C.CONTACTS.extend([dict(name='Independent entries',status='constructed',count=2,grounded_risers=12),
        dict(name='Party wall',status='continuous ground to capped roof'),
        dict(name='Roof bodies',status='one sealed deck per home with seated parapets and penetrations')])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-root',type=Path,required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--version',type=int,default=1)
    parser.add_argument('--resolution',type=int,default=1440)
    parser.add_argument('--dry-run',action='store_true')
    a=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    entry=source_entry(a.source_root);m=manifest(a.version)
    out=C.prepare_candidate(a,entry,m,__file__)
    if out is None:return
    cameras=C.setup(PALETTE,CAMERAS,a.resolution)
    build();C.deliver(out,m,cameras)


if __name__=='__main__':main()
