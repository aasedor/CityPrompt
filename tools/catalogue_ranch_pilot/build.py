"""Exact post-war Calgary bungalow; adjacent modern house is source context."""
import sys
import math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import support as S
C=S.C
SLUG='calgary-inner-city-bungalow';PARENT='calgary_inner_city_bungalow';VARIANT='bungalow_postwar_ranch';INDEX=2
TITLE='Calgary post-war bungalow';WIDTH=10.6;DEPTH=15.0;HEIGHT=6.0;STOREYS=1
PALETTE=dict(wall=(.49,.205,.12),mortar=(.48,.43,.34),trim=(.67,.65,.55),coping=(.55,.53,.45),roof=(.19,.20,.185),foundation=(.47,.46,.40),glass=(.31,.39,.37),hardware=(.08,.08,.065),timber=(.41,.25,.12),interior=(.68,.63,.53),floor=(.35,.28,.20),siding=(.56,.56,.47))
GF=.62;EAVE=3.55

def manifest(v):
    return S.prework(sys.modules[__name__],v,dict(width=WIDTH,depth=DEPTH,height=HEIGHT),
        dict(front='One-storey bungalow left of unrelated modern infill; low hipped roof, small white front-right gable, left porch and centre door.',
             oblique='Brick facade, pale horizontal side siding, narrow left chimney; porch stair at right edge of timber rail.',
             top='Single long rectangular hipped roof and one shallow front-right gable. The neighbouring flat-roof house is excluded.',
             roof='Closed four-plane hip unioned with a smaller forward gable; no dormer.',programme='One dwelling, porch and rear secondary entry.'),
        ['Metric sizes inferred from door/window proportions, not surveyed.','Back and partly hidden side openings and room partitions inferred.','Neighbouring modern infill, garages, garden and public sidewalk excluded.'],
        ['Foundation at zero.','Porch posts support eave; stair meets porch.','Gable and main hip form a closed Boolean union.'],[
          dict(name='facade_close',location=(-10,-19,6),target=(-1,-6.4,2),whole=False),
          dict(name='architecture_close',location=(6,-14,5),target=(-.5,-7,1.6),whole=False),
          dict(name='glass_close',location=(-4,-13,3.2),target=(-2.6,-6.2,2),whole=False,lens=62),
          dict(name='roof_contact',location=(13,-16,12),target=(2,-4,4),whole=False),
          dict(name='porch_contact',location=(-7,-14,4),target=(-1.7,-7,1.8),whole=False)])

def brickwork(f,length,holes):
    S.courses(f,length,GF,EAVE,holes,pitch=.085)
    for row in range(35):
        z=GF+(row+.5)*.085
        for i in range(math.ceil(length/.245)):
            u=(i+.5*(row%2))*.245
            if not .01<u<length-.01 or z>EAVE-.01:continue
            if any(h['u']-h['w']/2-.02<u<h['u']+h['w']/2+.02 and h['z']-.03<z<h['z']+h['h']+.03 for h in holes):continue
            f.part('Staggered brick perp joint',u,-.003,z,.006,.004,.077,'mortar','brick bonding',0)

def build():
    C.box('Whole foundation',(0,0,GF/2),(10,12.4,GF),'foundation','base',0)
    front=C.Face((-5,-6.2,0),(1,0,0),(0,1,0),'brick front')
    holes=[dict(id='living room',u=2.4,z=1.18,w=2.6,h=1.75,cols=3)]
    door=dict(id='front entry',u=4.85,z=GF,w=.94,h=2.18)
    fw=front.wall('Recessed porch brick facade',0,5.55,GF,EAVE,holes=holes+[door])
    front.window('living room',2.4,1.18,2.6,1.75,cols=1,curtain=True)
    for u in (1.55,3.25):front.part('Living room narrow side sash',u,.132,2.055,.055,.09,1.62,'trim','living room sash',0)
    front.window('Pale framed glazed entry',4.85,GF,.94,2.18,cols=1,rows=2,frame='trim',kind='glazed door')
    front.part('Entry leaf lower kick panel',4.85,.13,GF+.21,.80,.075,.34,'trim','operable entry leaf',0)
    front.part('Entry threshold',4.85,.08,GF-.015,1.0,.36,.06,'trim','operable entry leaf',0)
    for u in (4.85-.36,4.85+.36):front.part('Entry door leaf stile',u,.12,GF+1.09,.055,.075,2.05,'trim','operable entry leaf',0)
    C.rod('Entry pull handle',front.p(5.16,.04,GF+.93),front.p(5.16,.04,GF+1.14),.019,'hardware','operable entry leaf',10)
    brickwork(front,5.55,holes+[door])
    bay=C.Face((.55,-7.25,0),(1,0,0),(0,1,0),'projecting bedroom')
    bh=[dict(id='right room',u=2.45,z=1.15,w=1.86,h=1.80,cols=1)]
    S.openings(bay,4.45,GF,EAVE,bh,joints=False);brickwork(bay,4.45,bh)
    C.box('Bedroom projection foundation',(2.775,-6.725,GF/2),(4.45,1.05,GF),'foundation','base',0)
    C.box('Bedroom projection floor',(2.775,-6.72,GF+.05),(4.2,1.05,.1),'floor','occupied room',0)
    for x in (.55,5):C.box('Bedroom projection return',(x,-6.70,2.085),(.27,1.1,2.93),'wall','envelope',0)
    for label,origin,tangent,inward in [('right',(5,-6.2,0),(0,1,0),(-1,0,0)),('left',(-5,6.2,0),(0,-1,0),(1,0,0))]:
        f=C.Face(origin,tangent,inward,label);hs=[dict(id=label+str(i),u=u,z=1.25,w=w,h=1.5) for i,(u,w) in enumerate([(2.7,1.6),(6.4,1.6),(9.8,1)])]
        S.openings(f,12.4,GF,3.55,hs,role='siding',joints=False)
        S.courses(f,12.4,GF,3.55,hs,role='trim',pitch=.18)
    rear=C.Face((5,6.2,0),(-1,0,0),(0,-1,0),'rear');hs=[dict(id='rear door',u=3,z=GF,w=.94,h=2.15,door=True),dict(id='rear room',u=7,z=1.25,w=1.7,h=1.5)]
    S.openings(rear,10,GF,3.55,hs,role='siding',joints=False);S.stairs(2,6.22,GF,direction=1)
    C.box('Continuous porch and entry landing',(-2.225,-6.85,GF/2),(5.55,1.3,GF),'foundation','porch',0)
    S.stairs(-.15,-7.5,GF,width=1.4)
    for x in (-4.7,):C.box('Porch supporting post',(x,-7.12,1.99),(.15,.15,2.75),'trim','porch',.004)
    C.railing('Timber porch rail',(-4.7,-7.18,GF),(-.95,-7.18,GF),.92,.105,'timber')
    C.railing('Left porch return',(-4.7,-6.22,GF),(-4.7,-7.18,GF),.92,.105,'timber')
    roof=S.hip('Hipped main roof',-5.35,5.35,-7.4,6.55,3.62,2.0)
    # The rear cap sinks beneath the hip carrier instead of ending in a visible cliff.
    gable=C.mesh('Intersecting front gable roof',[(.38,-7.5,3.55),(5.45,-7.5,3.55),(2.915,-7.5,5.05),(.55,-2.4,3.55),(5.1,-2.4,3.55),(2.915,-2.4,3.60)],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'roof','roof')
    S.union(roof,gable)
    # White gable infill is seated above the brick front; solid triangular face.
    C.prism('White front gable',[(.55,3.53),(5.16,3.53),(2.855,4.86)],'y',-7.52,-7.38,'siding','gable')
    for i in range(1,20):
        x=.55+i*4.61/20;top=3.53+1.33*(1-abs(x-2.855)/2.305)
        C.box('Vertical gable board joint',(x,-7.525,(3.54+top)/2),(.011,.012,top-3.54),'trim','gable boarding',0)
    for a,b in [((.42,-7.51,3.6),(2.915,-7.51,5.08)),((2.915,-7.51,5.08),(5.42,-7.51,3.6))]:C.beam('Gable fascia',a,b,.16,.19,'trim','roof edge')
    for a,b in [((-5.36,-7.4,3.56),(.45,-7.4,3.56)),((-5.36,-7.4,3.56),(-5.36,6.56,3.56)),((5.36,-7.4,3.56),(5.36,6.56,3.56)),((-5.36,6.56,3.56),(5.36,6.56,3.56))]:C.beam('Eave fascia',a,b,.14,.18,'trim','roof edge')
    C.box('Brick chimney',(-4.55,-2.8,3.6),(.54,.67,4.9),'wall','chimney',0)
    C.box('Chimney cap',(-4.55,-2.8,6.08),(.65,.78,.11),'coping','chimney',.005)
    for dy in (-.15,.15):C.rod('Chimney pot',(-4.55,-2.8+dy,6.1),(-4.55,-2.8+dy,6.36),.09,'coping','chimney')
    for y in (1.1,3.1):
        roof_z=3.62+2.0*min(5.35-.2,y+7.4,6.55-y)/5.35
        C.rod('Roof vent',(.2,y,roof_z-.08),(.2,y,roof_z+.35),.055,'hardware','roof fittings')
    S.room(0,-3,GF,9.4,5.6,2.74);S.room(0,3,GF,9.4,5.6,2.74)

if __name__=='__main__':S.run(sys.modules[__name__])
