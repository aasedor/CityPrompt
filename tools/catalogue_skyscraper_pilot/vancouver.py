"""Vancouver classic: curved balconies, ribbon frame and mixed-use podium."""
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'catalogue_foursquare_pilot'))
import support as S
C=S.C
_mesh=C.mesh
C.mesh=lambda name,vs,fs,role='wall',module='envelope',soft=0:_mesh(name,vs,fs,role,module,0)
SLUG='vancouverism-tower-podium';PARENT='vancouverism_tower_podium';VARIANT='vancouverism_classic';INDEX=0
TITLE='Vancouver balcony and podium tower';WIDTH=48.;DEPTH=40.;HEIGHT=58.8;STOREYS=16
PALETTE=dict(wall=(.64,.63,.57),foundation=(.40,.41,.39),trim=(.59,.62,.62),roof=(.40,.42,.39),glass=(.12,.26,.29),interior=(.40,.39,.34),floor=(.51,.51,.46),timber=(.34,.24,.16),hardware=(.19,.23,.24),brick=(.40,.22,.15),plant=(.18,.25,.09))

def manifest(version):
 m=S.prework(sys.modules[__name__],version,dict(width=WIDTH,depth=DEPTH,height=HEIGHT),dict(plan='Rounded-corner tower over a wider three-level mixed-use podium with an offset brick wing.',roof='Planted podium terraces and roof terrace with rounded perimeter guard, central mechanical penthouse, equipment and planters.',programme='Retail lobby at ground, podium rooms and thirteen occupied residential levels above.',facade='Front left vertical fins; front right rounded projecting balconies; right face recessed balconies inside tall rounded ribbon frame.'),['Dimensions and sixteen occupied storeys inferred from oblique floor bands; front image is cropped.','Oblique governs complete elevation and podium; top governs central plant and rooftop garden. Rear repeats compatible glazing and fins; apartment fitout inferred.','Planting is bounded low-detail clay foliage, not textured trees.'],['Podium piers meet ground.','Balconies extend floor slabs and have glass guards.','Ribbon meets roof and lower tower slab.','Roof planting and equipment sit on carrier slabs.'],[
 dict(name='facade_close',location=(26,-48,38),target=(9,-12,34),whole=False),dict(name='architecture_close',location=(50,-54,20),target=(10,-15,9),whole=False),dict(name='glass_close',location=(8,-26,34),target=(7,-12,32),whole=False,lens=60),dict(name='roof_contact',location=(40,-44,77),target=(0,1,55),whole=False),dict(name='lobby_contact',location=(34,-43,7),target=(10,-18,3),whole=False),dict(name='ribbon_contact',location=(55,-15,45),target=(17,1,36),whole=False),dict(name='front_right',location=(123,-147,67),target=(0,0,27),whole=True)])
 for c in m['camera_roster']:
  if c['name']=='top':c['ortho_scale']=65
 return m

def rounded(x0,x1,y0,y1,r=2,steps=8):
 pts=[]
 for cx,cy,start in [(x1-r,y0+r,-90),(x1-r,y1-r,0),(x0+r,y1-r,90),(x0+r,y0+r,180)]:
  pts.extend((cx+r*math.cos(math.radians(start+90*i/steps)),cy+r*math.sin(math.radians(start+90*i/steps))) for i in range(steps+1))
 return pts

def edge_faces(poly):
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy)
  if l>.02:yield C.Face((*a,0),(dx/l,dy/l,0),(-dy/l,dx/l,0),f'perimeter {i}'),l

def glazing(poly,z,h,label,doors=False):
 for j,(f,length) in enumerate(edge_faces(poly)):
  if label.startswith('Podium') and not doors and j in (17,26):continue
  if label=='Wing level 2' and j==8:continue
  n=max(1,round(length/2.4));bay=length/n
  for i in range(n):
   u=(i+.5)*bay
   f.part(label+' pier',i*bay,.15,z+h/2,.13,.3,h,'trim','facade',0)
   if label.startswith('Apartment') and ((j==35 and i==n-2) or (j==8 and i==n//2 and label!='Apartment floor 1')):
    f.door(label+' balcony door',u,z,bay-.16,2.6,role='trim',glazed=True)
    f.window(label+' door transom',u,z+2.65,bay-.16,h-2.7,cols=1,sill=False)
   elif doors and j==len(poly)-1 and i in (n-3,n-2):
    f.door(label+' entrance',u,z,bay-.16,2.8,role='trim',glazed=True)
    f.window(label+' transom',u,z+2.85,bay-.16,h-2.9,cols=1,sill=False)
   else:f.window(label+f' {j}-{i}',u,z+.12,bay-.16,h-.18,cols=1,sill=False)

def guard(poly,z,exclude_tower=False):
 for f,l in edge_faces(poly):
  spans=[(0,l)]
  if exclude_tower:
   def exposed(u):
    q=f.p(u,0,0)
    return math.hypot(max(abs(q[0])-13.5,0),max(abs(q[1])-10.5,0))>2.500001
   count=max(2,math.ceil(l/.2));cuts=[0]
   for i in range(count):
    a=l*i/count;b=l*(i+1)/count
    if exposed(a)!=exposed(b):
     state=exposed(a)
     for _ in range(35):
      m=(a+b)/2
      if exposed(m)==state:a=m
      else:b=m
     cuts.append((a+b)/2)
   cuts.append(l)
   spans=[(a,b) for a,b in zip(cuts,cuts[1:]) if b-a>.001 and exposed((a+b)/2)]
  for a,b in spans:
   if exclude_tower:
    # Meet the recessed glazing, not only its nominal facade plane.
    if a>0 or not exposed(a):a-=.18
    if b<l or not exposed(b):b+=.18
   f.part('Glass guard',(a+b)/2,0,z+.57,b-a,.025,1.1,'glass','balcony guards',0)
   f.part('Guard top rail',(a+b)/2,0,z+1.13,b-a,.055,.055,'trim','balcony guards',0)

def planter(x,y,z,w,d):
 C.box('Terrace planter',(x,y,z+.3),(w,d,.6),'wall','landscape',0)
 C.box('Bounded shrubs',(x,y,z+.78),(w-.15,d-.15,.4),'plant','landscape',0)
 for dx in (-w*.3,0,w*.3):
  C.rod('Shrub stems',(x+dx,y,z+.6),(x+dx,y,z+1.7),.07,'timber','landscape',6)
  # Low polygon crown sits around its supporting trunk.
  p=[(x+dx+.6*math.cos(i*math.tau/8),y+.6*math.sin(i*math.tau/8)) for i in range(8)]
  C.prism('Shrub crown',p,'z',z+1.1,z+1.9,'plant','landscape')

def build():
 podium=rounded(-24,16,-20,20,3)
 C.prism('Ground slab',podium,'z',0,.18,'foundation','base')
 for k in range(4):
  z=.2+k*4.2
  C.prism('Podium floor',podium,'z',z,z+.28,'wall','podium')
  if k<3:
   glazing(rounded(-23,15,-19,19,2),z+.28,3.9,f'Podium level {k+1}',doors=k==0)
   C.box('Podium occupied core',(0,3,z+2),(14,16,3.8),'interior','podium rooms',0)
   for x in (-17,-11,-5,1,7,13):
    C.box('Podium table',(x,-15,z+1),(1.7,.8,.12),'timber','retail programme',0)
   if k in (1,2):guard(podium,z+.28)
 # Brick side and rear bays are assembled around real window holes.
 for f,l in [(C.Face((-23,17,0),(0,-1,0),(1,0,0),'brick left'),34),(C.Face((13,19,0),(-1,0,0),(0,-1,0),'brick rear'),34)]:
  n=round(l/4);bay=l/n
  for i in range(n):
   u=(i+.5)*bay
   for k in (1,2):
    z=.2+k*4.2
    f.part('Brick pier',u-bay/2+.3,.18,z+2.1,.6,.5,4.2,'brick','podium brick',0)
    f.part('Brick spandrel',u,.18,z+.65,bay-.6,.5,1.3,'brick','podium brick',0)
    f.window('Brick wing window',u,z+1.3,bay-.6,2.65,sill=True)
 # Attached two-storey side wing sits below the main three-storey terrace.
 wing=rounded(15,24,-12,18,1)
 C.prism('Wing foundation',wing,'z',0,.2,'foundation','side wing')
 for k in range(3):
  z=.2+k*4.2
  C.prism('Side wing slab',wing,'z',z,z+.28,'wall','side wing')
  if k<2:
   glazing(wing,z+.28,3.9,f'Wing level {k+1}')
   C.box('Wing occupied rooms',(20,5,z+2),(4,16,3.8),'interior','wing',0)
 wf=C.Face((24,-11,0),(0,1,0),(-1,0,0),'brick side wing')
 for i in range(7):
  u=(i+.5)*4
  wf.part('Wing brick pier',i*4+.3,.18,6.5,.6,.4,4.2,'brick','side wing',0)
  wf.part('Wing brick spandrel',u,.18,4.95,3.4,.4,1.1,'brick','side wing',0)
  wf.window('Wing window',u,5.5,3.4,3.05,sill=False)
 guard(wing,8.88)
 guard(podium,13.08,exclude_tower=True)
 for y in (-14,-6,2,10):planter(-21,y,13.08,2.4,5)
 for x in (-14,-6,2,10):planter(x,-17,13.08,5,1.7)
 for y in (-8,1,10):planter(21,y,8.88,2,5)
 # Rounded main tower: 13 floors at 3.2 m over podium.
 tower=rounded(-16,16,-13,13,2.5)
 for k in range(14):
  z=13+k*3.2
  C.prism('Tower floor',tower,'z',z,z+.23,'floor','tower slabs')
  if k<13:
   glazing(tower,z+.23,2.94,f'Apartment floor {k+1}')
   C.box('Apartment core',(0,3,z+1.6),(9,8,3),'interior','residential programme',0)
   for x in (-10,-3,7):
    C.box('Apartment partition',(x,-5,z+1.6),(.13,8,3),'interior','residential programme',0)
    C.box('Living room sofa',(x+1.3,-9,z+.6),(2,.8,.7),'timber','residential programme',0)
   if k>0:
    balcony=[(7,-13),(7,-15),(15.5,-15)]+[(15.5+2.5*math.cos(math.radians(-90+i*90/12)),-12.5+2.5*math.sin(math.radians(-90+i*90/12))) for i in range(1,13)]+[(18,-6),(16,-6),(16,-10.5)]+[(13.5+2.5*math.cos(math.radians(-i*90/12)),-10.5+2.5*math.sin(math.radians(-i*90/12))) for i in range(1,13)]
    C.prism('Rounded corner balcony',balcony,'z',z,z+.22,'wall','balconies');guard(balcony,z+.22,exclude_tower=True)
    C.box('Side recessed balcony',(17.05,3.25,z+.1),(2.1,14.5,.2),'wall','side balconies',0)
    guard([(18.1,-4),(18.1,10.5),(16,10.5),(16,-4)],z+.2,exclude_tower=True)
 # Tall fins dominate the left part of the front, continuous over floor bands.
 for x in range(-15,6,2):C.box('Vertical facade fin',(x,-13.35,32.2),(.23,.6,38.4),'wall','vertical fins',0)
 # Ribbon follows rounded rectangle in right-face y/z plane; thickness physically connects into slabs.
 outline=rounded(-5,13,17,54.6,3.5,12)
 for i,(y,z) in enumerate(outline):
  yn,zn=outline[(i+1)%len(outline)]
  C.beam('Continuous curved ribbon',(18.3,y,z),(18.3,yn,zn),.85,.65,'trim','ribbon frame',0)
 C.prism('Roof terrace',rounded(-17,18,-15,14,3),'z',54.6,54.9,'wall','roof')
 guard(rounded(-17,18,-15,14,3),54.9)
 rf=C.Face((-7.5,-3.5,0),(1,0,0),(0,1,0),'roof access')
 rf.wall('Penthouse front',0,15,54.9,58.5,holes=[dict(id='Roof access',u=7.5,z=54.9,w=1.5,h=2.6)])
 rf.door('Roof access',7.5,54.9,1.5,2.6,role='hardware')
 C.box('Penthouse rear',(0,7.35,56.7),(15,.3,3.6),'wall','roof plant',0)
 for x in (-7.35,7.35):C.box('Penthouse side',(x,2,56.7),(.3,11,3.6),'wall','roof plant',0)
 C.box('Penthouse cap',(0,2,58.65),(15.3,11.3,.3),'roof','roof plant',0)
 for x in (-5,0,5):C.box('HVAC',(x,9,55.6),(2,2,1.4),'hardware','roof plant',0)
 for x,y,w,d in [(-13,0,2,12),(14,0,2,12),(-7,-12,9,2),(7,-12,9,2),(-7,11,9,2),(7,11,9,2)]:planter(x,y,54.9,w,d)
 # Explicit street doors, canopy and level entry on the front.
 C.box('Entry canopy',(8,-19.4,3.5),(6,1.2,.16),'trim','entry',0)

if __name__=='__main__':S.run(sys.modules[__name__])
