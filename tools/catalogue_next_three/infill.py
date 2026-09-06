"""Exact rammed-earth/timber three-storey infill, authored as native clay."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import support as S
C = S.C
SLUG='detached_contemporary_infill';PARENT='detached_contemporary_infill'
VARIANT='detached_infill_rammed_earth';INDEX=3
TITLE='Rammed-earth timber infill';WIDTH=13;DEPTH=20;HEIGHT=10.2;STOREYS=3
PALETTE=dict(wall=(.52,.35,.20),earthlight=(.57,.40,.24),earthdark=(.48,.32,.19),
 trim=(.20,.19,.16),coping=(.27,.29,.28),roof=(.38,.39,.36),foundation=(.46,.43,.36),
 glass=(.29,.34,.32),hardware=(.10,.10,.09),timber=(.47,.31,.17),interior=(.63,.58,.48),floor=(.41,.33,.24))
LEVELS=[.12,3.30,6.48]

def manifest(v):
    m = S.prework(sys.modules[__name__],v,dict(width=WIDTH,depth=DEPTH,height=HEIGHT),
        dict(front='Three occupied storeys; two open front loggia bays divided by a full-height earth pier. Timber posts and exposed beams carry shallow projecting roof.',
             oblique='Deep rectangular earth volume; rear-right stacked timber balcony and screen. Front rooms are recessed behind solid layered-earth balcony guards.',
             top='One rectangular shallow metal roof with central longitudinal spine and closely spaced exposed battens; no gables or skylights.',
             roof='Closed near-flat membrane slab, perimeter metal cap and central longitudinal spine; timber battens over the membrane are retained from top reference.',
             programme='Three-storey residential infill with front loggias and stacked rear-side balconies.'),
        ['Dimensions are inferred, not surveyed.','Rear openings and interior partitions are inferred from visible residential grammar.',
         'Road, neighbouring houses, street trees and grass belong to site context and are excluded.','Earth stratification is constructed palette relief, not textured keeper material.'],
        ['Posts contact grade and roof beams.','Balcony guards seat on floor slabs and have return ends.','Roof slab closes envelope; battens do not substitute for weathering.'],[
        dict(name='facade_close',location=(-12,-23,8),target=(-1,-8,4.8),whole=False),
        dict(name='architecture_close',location=(12,-19,10),target=(2,-8,6.1),whole=False),
        dict(name='glass_close',location=(2.8,-11,2),target=(2.5,-6.8,1.5),whole=False,lens=46),
        dict(name='roof_contact',location=(13,-16,15),target=(2,-5,9.5),whole=False),
        dict(name='balcony_contact',location=(15,12,8),target=(6,5.5,5.0),whole=False)])
    for camera in m['camera_roster']:
        if camera['name'] in ('front_corner','aerial'):
            camera['location']=(abs(camera['location'][0]), *camera['location'][1:])
    return m

def earth(face,length,z0,z1,holes=(),depth=.34):
    # Continuous physical lifts; every carrier independently terminates at openings.
    pitch=.16
    n=0;z=z0
    while z<z1-.001:
        end=min(z+(.09,.20,.13,.23,.15,.16)[n%6],z1)
        role=('wall','earthlight','wall','earthdark','earthlight','wall')[n%6]
        face.wall('Compacted earth lift',0,length,z,end,depth=depth,role=role,holes=holes)
        z=end;n+=1

def build():
    C.box('Continuous foundation',(0,0,.06),(11.6,18,.12),'foundation','base',0)
    # Earth carrier fronts start behind open loggias.
    front=C.Face((-5.7,-7,0),(1,0,0),(0,1,0),'recessed front rooms')
    holes=[]
    for level,z in enumerate(LEVELS):
        for u,w in ((2.1,3.4),(8.8,4.0)):holes.append(dict(id=f'front {level}-{u}',u=u,z=z+.04,w=w,h=2.68))
    earth(front,11.4,.12,9.66,holes)
    for h in holes:
        if h['id']=='front 0-2.1':continue
        front.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,rows=1,frame='trim',curtain=True,depth=.34,sill=False,kind='sliding loggia door')
    flush=C.Face((-5.7,-9,0),(1,0,0),(0,1,0),'flush ground left frontage')
    entry=dict(id='flush front entrance',u=2.1,z=.16,w=3.4,h=2.68)
    earth(flush,4.2,.12,3.3,[entry])
    flush.window(entry['id'],2.1,.16,3.4,2.68,cols=2,frame='trim',depth=.34,sill=False,kind='glazed entrance')
    earth(C.Face((-5.7,-9,0),(0,1,0),(1,0,0),'ground left forward return'),2,.12,3.3)
    C.box('Front left occupied extension floor',(-3.6,-8,.18),(4.2,2,.12),'floor','room depth',0)
    for name,o,t,n in [('right',(5.7,-7,0),(0,1,0),(-1,0,0)),('left',(-5.7,9,0),(0,-1,0),(1,0,0))]:
        face=C.Face(o,t,n,name);hs=[]
        for floor,z in enumerate(LEVELS):
            locations=(10.8,14.5) if name=='right' else (3.8,9.5,13.8)
            for u in locations:hs.append(dict(id=f'{name} {floor}-{u}',u=u,z=z+.1 if name=='right' else z+.9,w=1.7,h=2.5 if name=='right' else 1.7))
        earth(face,16,.12,9.66,hs)
        for h in hs:face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=1,frame='trim',depth=.34,curtain=True)
    rear=C.Face((5.7,9,0),(-1,0,0),(0,-1,0),'inferred rear');hs=[]
    for floor,z in enumerate(LEVELS):
        for u in (2.4,8.7):hs.append(dict(id=f'rear {floor}-{u}',u=u,z=z+.85,w=2.4,h=1.85))
    earth(rear,11.4,.12,9.66,hs)
    for h in hs:rear.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,curtain=True,depth=.34)
    pier=C.Face((-1.5,-9,0),(1,0,0),(0,1,0),'front solid pier')
    earth(pier,2.1,.12,9.66,depth=2.0)
    for z in LEVELS:
        C.box('Complete occupied floor',(0,1,z+.06),(11.1,15.6,.12),'floor','floor',0)
        C.box('Residential spine partition',(-.3,2,z+1.50),(.16,13.5,2.86),'interior','room depth',0)
        for x in (-3,2.8):S.room(x,.3,z,5,12,2.98)
        if z>.2:
            C.box('Front loggia slab',(0,-8,z-.08),(11.4,2.2,.20),'timber','loggia',0)
            for x0,length in [(-5.7,4.2),(.6,5.1)]:
                earth(C.Face((x0,-9,0),(1,0,0),(0,1,0),'front balcony guard'),length,z,z+1.08)
            for x,sign in [(-5.7,1),(5.7,-1)]:earth(C.Face((x,-9,0),(0,1,0),(sign,0,0),'guard return'),2,z,z+1.08)
            # Side balcony's timber enclosure is open pickets, not an opaque cube.
            C.box('Side balcony slab',(6.3,6,z-.08),(1.55,5.8,.20),'timber','side balcony',0)
            for y in (3.1,8.9):C.railing('Side balcony return',(5.65,y,z),(7.02,y,z),1.12,.11,'timber')
    for i in range(49):
        C.box('Continuous two-level timber privacy batten',(7.02,3.1+i*5.8/48,5.46),(.075,.055,4.52),'timber','side screen',.002)
    for z in (3.25,6.42,7.69):C.box('Side screen carrier rail',(7.015,6,z),(.10,5.9,.10),'timber','screen support',0)
    for x in (-5.6,.6,5.6):
        C.box('Front full-height timber post',(x,-9,4.91),(.20,.23,9.82),'timber','load path',.005)
    for x in (-5.6,5.6):
        for y in (-4,1,8.9):C.box('Side full-height post',(x,y,4.88),(.19,.19,9.76),'timber','load path',.004)
    C.box('Closed shallow roof',(0,.0,9.88),(12.6,19.6,.18),'roof','weathering',0)
    for x in (-6.2,0,6.2):C.box('Longitudinal metal roof edge or spine',(x,0,10.06),(.18,19.6,.18),'coping','roof spine',0)
    for y in (-9.7,9.7):C.box('Cross roof edge',(0,y,10.0),(12.6,.16,.22),'coping','roof perimeter',0)
    for i in range(29):
        y=-9.4+i*18.8/28
        for x in (-3.1,3.1):C.box('Source top timber batten',(x,y,10.025),(5.95,.10,.09),'timber','roof battens',0)
        C.box('Exposed underside roof rafter',(0,y,9.69),(12.3,.11,.20),'timber','roof support',0)
    for x in (-5.6,.6,5.6):C.box('Roof bearing beam',(x,0,9.62),(.20,19.3,.27),'timber','load path',0)

if __name__=='__main__':S.run(sys.modules[__name__])
