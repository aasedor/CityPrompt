"""Source-locked Toronto red-brick Foursquare architectural clay."""
import sys, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import support as S
C=S.C
SLUG='toronto-edwardian-foursquare';PARENT='toronto_edwardian_foursquare';VARIANT='toronto_foursquare_red_brick';INDEX=0
TITLE='Edwardian Foursquare';WIDTH=11.2;DEPTH=16.2;HEIGHT=11.1;STOREYS=2
PALETTE=dict(wall=(.40,.19,.12),mortar=(.29,.265,.22),trim=(.61,.59,.49),coping=(.52,.50,.42),roof=(.15,.17,.17),foundation=(.43,.41,.34),glass=(.31,.39,.37),hardware=(.07,.065,.05),timber=(.28,.18,.095),interior=(.65,.60,.50),floor=(.34,.26,.18),siding=(.35,.31,.23))
GF=.85;UP=3.95;EAVE=7.10

def brickwork(face,length,z0,z1,holes):
    S.courses(face,length,z0,z1,holes,pitch=.085)
    vs=[];fs=[]
    for row in range(math.ceil((z1-z0)/.085)):
        z=z0+(row+.5)*.085
        for i in range(math.ceil(length/.245)):
            u=(i+.5*(row%2))*.245
            if not .01<u<length-.01 or z>z1-.01:continue
            if any(h['u']-h['w']/2-.02<u<h['u']+h['w']/2+.02 and h['z']-.03<z<h['z']+h['h']+.03 for h in holes):continue
            n=len(vs)
            vs.extend(face.p(uu,dd,zz) for uu,dd,zz in [(u-.003,-.004,z-.038),(u+.003,-.004,z-.038),(u+.003,.001,z-.038),(u-.003,.001,z-.038),(u-.003,-.004,z+.038),(u+.003,-.004,z+.038),(u+.003,.001,z+.038),(u-.003,.001,z+.038)])
            fs.extend(tuple(n+j for j in f) for f in C.BOX_FACES)
    if vs:C.mesh('Source brick staggered perp joints',vs,fs,'mortar','brick bonding')

def manifest(v):
    return S.prework(sys.modules[__name__],v,dict(width=WIDTH,depth=DEPTH,height=HEIGHT),
        dict(front='Two-storey red brick Foursquare, paired upper windows, full-width porch and centred hipped dormer.',
             oblique='Long rectangular hipped roof, front dormer, chimney on right slope, brick porch piers and pale railing.',
             top='Single main hip; shorter ridge; one front hipped dormer and long shallow porch shed roof.',
             roof='Main hip with full-depth dormer opening, constructed dormer cheeks and unioned hip cap; separate porch shed.',programme='One family house; two occupied storeys and an inferred attic room.'),
        ['Dimensions are conceptual, inferred from doors and floors.','Rear and left openings, attic interior and partitions inferred.','Front hero has two main porch piers; oblique adds pale secondary columns. Main corner piers retained as stable source identity.','Gardens, neighbours and public sidewalk excluded.'],
        ['Foundation meets grade; stairs reach porch.','Brick porch piers and rear ledger support shed roof.','Dormer cheeks penetrate actual roof plane; carrier aperture cut before glazing.'],[
          dict(name='facade_close',location=(-13,-23,10),target=(0,-6.3,4.8),whole=False),
          dict(name='architecture_close',location=(9,-17,6),target=(0,-8,2.7),whole=False),
          dict(name='glass_close',location=(-6,-14,6.2),target=(-2.5,-6.2,5.3),whole=False,lens=62),
          dict(name='roof_contact',location=(11,-16,15),target=(0,-3.8,8.8),whole=False),
          dict(name='dormer_section',location=(-7,-12,10.4),target=(0,-4.65,8.45),whole=False,lens=64)])

def build():
    C.box('Foundation',(0,0,GF/2),(10,12.4,GF),'foundation','base',0)
    front=C.Face((-5,-6.2,0),(1,0,0),(0,1,0),'front')
    holes=[dict(id='upper left pair',u=2.2,z=4.7,w=1.65,h=1.9,cols=2,rows=2),dict(id='upper right pair',u=7.55,z=4.7,w=1.65,h=1.9,cols=2,rows=2),
      dict(id='entry',u=5,z=GF,w=1.05,h=2.35,door=True),dict(id='porch left window',u=2.1,z=1.55,w=1.05,h=1.65,rows=2),dict(id='porch right window',u=7.7,z=1.5,w=1.6,h=1.7,rows=2)]
    S.openings(front,10,GF,EAVE,holes,joints=False);brickwork(front,10,GF,EAVE,holes)
    for u in (2.2,7.55):
        for side in (-1,1):
            for offset in (-.13,.13):front.part('Upper sash fine muntin',u+side*.4125+offset,.115,6.125,.023,.06,.89,'trim','paired upper sash',0)
        front.part('Upper sash fine transom',u,.115,6.08,1.51,.06,.023,'trim','paired upper sash',0)
    for label,origin,tangent,inward in [('right',(5,-6.2,0),(0,1,0),(-1,0,0)),('left',(-5,6.2,0),(0,-1,0),(1,0,0)),('rear',(5,6.2,0),(-1,0,0),(0,-1,0))]:
        length=10 if label=='rear' else 12.4
        hs=[]
        for level,z in enumerate([1.5,4.6]):
            for i,u in enumerate([2.2,5.8,9.7] if length>10 else [2.2,5,7.8]):
                if label=='rear' and level==0 and i==1:hs.append(dict(id='rear entry',u=u,z=GF,w=1,h=2.25,door=True))
                else:hs.append(dict(id=f'{label} {level} {i}',u=u,z=z,w=.9 if i==0 and level==0 else 1.15,h=1.65,cols=2,rows=2))
        f=C.Face(origin,tangent,inward,label)
        S.openings(f,length,GF,EAVE,hs,joints=False);brickwork(f,length,GF,EAVE,hs)
    S.stairs(0,6.22,GF,direction=1,count=5)
    C.box('Porch base',(0,-7.5,GF/2),(10.1,2.6,GF),'foundation','porch',0)
    S.stairs(0,-8.8,GF,width=1.65,count=5)
    for x in (-4.8,4.8):
        C.box('Brick porch pier',(x,-8.48,2.18),(.55,.55,2.66),'wall','porch piers',0)
        C.box('Pier cap',(x,-8.48,3.51),(.68,.69,.14),'trim','porch piers',.006)
        f=C.Face((x-.275,-8.76,0),(1,0,0),(0,1,0),'pier');brickwork(f,.55,GF,3.46,[])
    for xa,xb in [(-4.8,-.95),(.95,4.8)]:
        C.railing('Porch front guard',(xa,-8.5,GF),(xb,-8.5,GF),.98,.10,'trim')
    for x in (-4.8,4.8):C.railing('Porch side guard',(x,-8.5,GF),(x,-6.24,GF),.98,.10,'trim')
    for xa,xb in [(-4.8,-.95),(.95,4.8)]:
        C.box('Pale porch skirt',((xa+xb)/2,-8.815,GF/2),(xb-xa,.045,GF-.08),'trim','porch skirting',0)
        C.beam('Substantial porch handrail',(xa,-8.5,GF+.98),(xb,-8.5,GF+.98),.095,.075,'trim','porch railing',0)
        for i in range(int((xb-xa)/.12)):
            C.box('Skirting board seam',(xa+(i+.5)*.12,-8.844,GF/2),(.008,.015,GF-.10),'siding','porch skirting',0)
    for x in (-4.8,4.8):
        for side,origin,tangent,inward in [('outside',(x+.275,-8.755,0),(0,1,0),(-1,0,0)),('inside',(x-.275,-8.205,0),(0,-1,0),(1,0,0))]:brickwork(C.Face(origin,tangent,inward,'pier '+side),.55,GF,3.46,[])
    for x in (-1.0,1.0):C.box('Stair cheek',(x,-9.12,.40),(.30,.85,.80),'wall','porch steps',0)
    # Closed shed roof, carried by brick piers and wall ledger.
    C.solid_surface('Porch roof',[(-5.35,-8.92,3.67),(5.35,-8.92,3.67),(5.35,-6.12,4.32),(-5.35,-6.12,4.32)],.16,'roof','porch roof')
    for a,b in [((-5.35,-8.92,3.56),(5.35,-8.92,3.56)),((-5.35,-8.92,3.56),(-5.35,-6.12,4.2)),((5.35,-8.92,3.56),(5.35,-6.12,4.2))]:C.beam('Porch fascia',a,b,.19,.22,'trim','porch roof')
    roof=S.hip('Main hipped roof',-5.45,5.45,-6.65,6.65,7.13,2.9)
    C.cut_box(roof,'Dormer interior aperture',(0,-3.55,8.5),(2.46,2.30,4))
    dormer=C.Face((-1.4,-4.76,0),(1,0,0),(0,1,0),'dormer front')
    hs=[dict(id='attic double window',u=1.4,z=8.12,w=2.26,h=.94,cols=2)]
    S.openings(dormer,2.8,7.6,9.22,hs,role='siding',joints=False)
    for x in (-1.4,1.4):C.box('Dormer cheek',(x,-3.37,8.41),(.18,2.76,1.62),'siding','dormer cheeks',0)
    cap=S.hip('Dormer hip cap',-1.66,1.66,-5.00,-1.83,9.24,.58)
    S.union(roof,cap)
    for x in (-1.66,1.66):C.beam('Dormer hip eave return',(x,-5,9.18),(x,-1.83,9.18),.16,.20,'trim','dormer hip eave',0)
    C.beam('Dormer rear eave',(-1.66,-1.83,9.18),(1.66,-1.83,9.18),.16,.20,'trim','dormer hip eave',0)
    for x in (-1.50,1.50):
        for row in range(7):
            z=8.18+row*.155;end=min(-2.7,(z-7.13)*5.45/2.9-6.65)
            if end> -4.74:
                C.box('Dormer shingle course',(x,(-4.74+end)/2,z),(.02,end+4.74,.013),'timber','dormer shingles',0)
                for i in range(math.floor((end+4.74)/.25)):
                    y=-4.70+i*.25+(.12 if row%2 else 0)
                    if y<end-.03:C.box('Dormer shingle joint',(x,y,z+.065),(.02,.01,.13),'timber','dormer shingles',0)
    C.box('Dormer room floor',(0,-3.5,7.92),(2.42,2.2,.1),'floor','attic room',0)
    C.box('Dormer rear room wall',(0,-2.18,8.53),(2.42,.12,1.32),'interior','attic room',0)
    C.qa_room_light('attic',(0,-3.6,9.03),30,1.2)
    for x in (-1.3,1.3):C.box('Dormer corner trim',(x,-4.79,8.45),(.13,.15,1.58),'trim','dormer',.002)
    for a,b in [((-1.66,-5,9.18),(1.66,-5,9.18)),((-5.45,-6.65,7.08),(5.45,-6.65,7.08)),((-5.45,6.65,7.08),(5.45,6.65,7.08)),((-5.45,-6.65,7.08),(-5.45,6.65,7.08)),((5.45,-6.65,7.08),(5.45,6.65,7.08))]:C.beam('Roof fascia',a,b,.17,.20,'trim','roof edges')
    C.box('Right brick chimney',(4.28,-1.4,8.38),(.65,.79,4.0),'wall','chimney',0)
    for label,o,t,n,L in [('front',(3.955,-1.795,0),(1,0,0),(0,1,0),.65),('right',(4.605,-1.795,0),(0,1,0),(-1,0,0),.79),('rear',(4.605,-1.005,0),(-1,0,0),(0,-1,0),.65),('left',(3.955,-1.005,0),(0,-1,0),(1,0,0),.79)]:brickwork(C.Face(o,t,n,'chimney '+label),L,8.15,10.33,[])
    C.box('Chimney crown',(4.28,-1.4,10.4),(.81,.93,.14),'coping','chimney',.005)
    for y in (-1.59,-1.21):C.rod('Clay chimney pot',(4.28,y,10.45),(4.28,y,10.81),.11,'timber','chimney')
    for z in (GF,UP):S.room(0,-3,z,9.35,5.45,2.87);S.room(0,3,z,9.35,5.45,2.87)

if __name__=='__main__':S.run(sys.modules[__name__])
