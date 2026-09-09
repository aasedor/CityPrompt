"""Two-stack twisting tower, locked to the glass_tower_twisted references."""
import math
import sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'catalogue_foursquare_pilot'))
import support as S
C=S.C
_mesh=C.mesh
C.mesh=lambda name,vs,fs,role='wall',module='envelope',soft=0:_mesh(name,vs,fs,role,module,0)
SLUG='glass_tower_podium_modern';PARENT=SLUG;VARIANT='glass_tower_twisted';INDEX=1
TITLE='Twisting glass tower with sky garden';WIDTH=46.;DEPTH=46.;HEIGHT=147.7;STOREYS=40
PALETTE=dict(wall=(.66,.65,.60),foundation=(.43,.44,.42),trim=(.66,.66,.61),roof=(.47,.48,.46),glass=(.30,.36,.39),interior=(.42,.40,.35),floor=(.51,.50,.46),timber=(.35,.27,.17),hardware=(.24,.25,.24),plant=(.16,.24,.08))

def manifest(version):
 m=S.prework(sys.modules[__name__],version,dict(width=WIDTH,depth=DEPTH,height=HEIGHT),dict(plan='Five-sided footprint, two gently rotating glazed stacks separated by a recessed planted sky garden; trussed glazed lobby.',roof='Angular perimeter glass crown surrounds chamfered mechanical penthouse, roof equipment and front planted terrace.',programme='Tall occupied lobby, twenty lower and eighteen upper office levels, plus shared sky-garden level: forty occupied levels including lobby and garden.',facade='Pale continuous floor bands and fine silver mullions follow each twisted stack; clearly recessed planted horizontal break.'),['Native size, twist angles and forty occupied levels are conceptual estimates from the source bands, not surveyed dimensions.','Front governs two-stack proportions, lobby trusses and garden opening; top governs five-sided crown and plant room. Rear uses the same glazing grammar.','Upper stack transfer structure and occupied office fitout are inferred; complete load paths are represented but are not structural engineering.'],['Lobby trusses connect ground to first occupied slab.','Lift core and garden columns connect both tower stacks.','Each glazing panel is bounded by its actual twisted floor edges.','Roof equipment and garden planters sit on slabs.'],[
 dict(name='facade_close',location=(40,-63,48),target=(0,-19,43),whole=False),dict(name='architecture_close',location=(38,-51,16),target=(0,-16,6),whole=False),dict(name='glass_close',location=(11,-35,46),target=(3,-19,44),whole=False,lens=60),dict(name='roof_contact',location=(47,-60,170),target=(0,0,143),whole=False),dict(name='lobby_contact',location=(-27,-40,7),target=(0,-18,3),whole=False),dict(name='garden_contact',location=(44,-54,88),target=(0,-16,80),whole=False),dict(name='garden_structure',location=(0,-16,80.2),target=(0,2,80.2),whole=False,lens=22)])
 m['candidate']=f'glass-tower-twisted-clay-v{version:03}'
 for c in m['camera_roster']:
  if c['name']=='top':c['ortho_scale']=66
 return m

BASE=[(-18,-17),(0,-22),(18,-17),(18,18),(-18,18)]
def plan(angle):
 a=math.radians(angle)
 return [(x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a)) for x,y in BASE]

def slab(poly,z,thick=.25,role='floor'):
 return C.prism('Occupied polygon floor',poly,'z',z,z+thick,role,'floor slabs')

def panel(name,points,role='glass'):
 n=(Vector(points[1])-Vector(points[0])).cross(Vector(points[3])-Vector(points[0])).normalized()
 front=[Vector(p) for p in points];back=[p-n*.018 for p in front]
 C.mesh(name,[tuple(p) for p in front+back],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],role,'twisted glazing')

def skin(low,high,z0,z1,label,crown=False):
 for j,a in enumerate(low):
  b=low[(j+1)%len(low)];ah=high[j];bh=high[(j+1)%len(high)]
  a=Vector((*a,z0));b=Vector((*b,z0));ah=Vector((*ah,z1));bh=Vector((*bh,z1))
  n=max(2,round((b-a).length/2.5))
  C.beam('Continuous pale floor edge',a,b,.30,.28,'trim','floor bands',0)
  for i in range(n):
   t0=(i+.035)/n;t1=(i+.965)/n
   p=a.lerp(b,t0);q=a.lerp(b,t1);r=ah.lerp(bh,t1);s=ah.lerp(bh,t0)
   p.z+=.28;q.z+=.28;r.z-=.07;s.z-=.07
   normal=(q-p).cross(s-p).normalized()
   pts=[v-normal*.15 for v in (p,q,r,s)]
   panel(label+f' pane {j}-{i}',pts)
   for u,v in [(pts[0],pts[1]),(pts[1],pts[2]),(pts[2],pts[3]),(pts[3],pts[0])]:
    C.beam('Recessed panel frame',u,v,.055,.09,'trim','window frames',0)
   C.beam('Twisting mullion',a.lerp(b,i/n),ah.lerp(bh,i/n),.10,.20,'trim','curtain wall',0)
   C.OPENINGS.append(dict(id=label+f' {j}-{i}',face=f'polygon edge {j}',u=0,z=z0+.28,face_origin=[(p.x+q.x+r.x+s.x)/4,(p.y+q.y+r.y+s.y)/4,0],face_tangent=list((q-p).normalized()),face_inward=list(-normal),width=(q-p).length,height=z1-z0-.35,kind='glazed crown' if crown else 'curtain wall',clear_wall_cut=True,carrier_depth_m=.30,frame_inset_m=.15,pane_inset_m=.15,occupied_space='enclosed furnished floor behind perimeter; roof plant behind crown' if crown else 'enclosed furnished office with lift core',cols=1,rows=1))
  C.beam('Twisted corner structural column',a,ah,.35,.35,'trim','primary frame',0)

def garden(poly,z,scale=.82):
 for i,(x,y) in enumerate(poly):
  xn,yn=poly[(i+1)%len(poly)]
  for t in (.2,.4,.6,.8):
   px=(x+(xn-x)*t)*scale;py=(y+(yn-y)*t)*scale
   C.box('Garden planter',(px,py,z+.4),(2,1.8,.8),'wall','sky garden',0)
   C.rod('Tree trunk',(px,py,z+.8),(px,py,z+2.5),.10,'timber','sky garden',8)
   ring=[(px+1.1*math.cos(k*math.tau/8),py+1.1*math.sin(k*math.tau/8)) for k in range(8)]
   C.prism('Bounded garden canopy',ring,'z',z+1.4,z+2.8,'plant','sky garden')

def build():
 # Tall QA cameras can sit beyond the core utility's 500 m clip distance.
 for obj in S.bpy.context.scene.objects:
  if obj.type=='CAMERA':obj.data.clip_end=2000
 bottom=plan(-12)
 slab(bottom,0,.2,'foundation')
 for x,y in bottom:C.box('Truss bearing plinth',(x,y,.3),(1,1,.6),'foundation','lobby structure',0)
 # Lobby shell has an actual door pair on its front-left edge; glazing avoids that bay.
 for j,a in enumerate(bottom):
  b=bottom[(j+1)%5];dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy)
  f=C.Face((*a,0),(dx/l,dy/l,0),(-dy/l,dx/l,0),'lobby')
  n=max(2,round(l/3));bay=l/n
  for i in range(n):
   u=(i+.5)*bay
   f.part('Lobby mullion',i*bay,.12,5,.15,.24,10,'trim','lobby',0)
   if j==0 and i==n//2:
    f.door('Lobby door',u,.2,bay-.16,3.1,role='trim',glazed=True)
    f.window('Door transom',u,3.35,bay-.16,6.6,cols=1,sill=False)
   else:f.window('Tall lobby glazing',u,.2,bay-.16,9.75,cols=1,rows=2,sill=False)
  C.beam('Lobby diagonal truss',(*a,.55),(*b,10),.55,.55,'trim','lobby structure',0)
  C.beam('Lobby diagonal truss',(*b,.55),(*a,10),.55,.55,'trim','lobby structure',0)
 corefront=C.Face((-4.5,-3.5,0),(1,0,0),(0,1,0),'lift core front')
 holes=[dict(id='Lobby core access',u=4.5,z=.2,w=2.2,h=3),dict(id='Sky garden access',u=4.5,z=78.35,w=2.2,h=3)]
 corefront.wall('Lift core with access',0,9,0,143.2,depth=.35,role='interior',holes=holes)
 for h in holes:corefront.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='hardware')
 for x in (-4.35,4.35):C.box('Lift core side',(x,1,71.6),(.3,9,143.2),'interior','vertical circulation',0)
 C.box('Lift core rear',(0,5.35,71.6),(9,.3,143.2),'interior','vertical circulation',0)
 C.box('Lobby reception',(0,-10,1.1),(5,1.5,1.8),'wall','lobby programme',0)
 for zbase,count in [(10,20),(82,18)]:
  for k in range(count+1):
   p=plan(-12+24*k/count);z=zbase+k*3.4
   slab(p,z)
   if k<count:
    skin(p,plan(-12+24*(k+1)/count),z,z+3.4,f'Stack {zbase} floor {k+1}')
    for x in (-9,-3,3,9):
     C.box('Occupied desk',(x,-9,z+.95),(1.6,.8,.12),'timber','office fitout',0)
     C.box('Desk support',(x,-9,z+.55),(.6,.6,.85),'interior','office fitout',0)
     C.box('Office partition',(x,-5,z+1.4),(.12,4,2.3),'interior','office fitout',0)
 # Transfer garden sits on lower stack roof and supports the upper floor.
 terrace=plan(12)
 slab(terrace,78,.35,'wall');garden(terrace,78.35)
 for x,y in [(-11,-9),(11,-9),(-11,10),(11,10)]:C.box('Garden support column',(x,y,80),(1,1,4),'wall','transfer structure',0)
 for j,a in enumerate(terrace):
  b=terrace[(j+1)%5]
  panel('Sky garden guard',[(*a,78.4),(*b,78.4),(*b,79.5),(*a,79.5)])
 # Roof enclosure and crown inherit the uppermost floor rotation.
 roof=plan(12);skin(roof,roof,143.2,147.7,'Roof crown',crown=True)
 core=[(-10,-8),(6,-8),(11,-3),(11,9),(-10,9)]
 for j,a in enumerate(core):
  b=core[(j+1)%len(core)];dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy)
  f=C.Face((*a,0),(dx/l,dy/l,0),(-dy/l,dx/l,0),'roof plant room')
  holes=[dict(id='Roof garden access',u=8,z=143.45,w=2,h=2.4)] if j==0 else []
  f.wall('Plant room carrier',0,l,143.45,146,depth=.3,holes=holes)
  if j==0:f.door('Roof garden access',8,143.45,2,2.4,role='hardware')
 C.prism('Plant enclosure cap',core,'z',146,146.2,'roof','roof plant')
 for x,y in [(-13,1),(-13,5),(-13,9),(0,12),(5,12)]:C.box('Roof HVAC',(x,y,144.2),(1.6,1.6,1.5),'hardware','roof plant',0)
 # Crescent planter encloses a lower paved roof court in front of the plant room.
 outer=[(8*math.cos(math.pi+i*math.pi/24),-9+8*math.sin(math.pi+i*math.pi/24)) for i in range(25)]
 inner=[(6*math.cos(math.pi+i*math.pi/24),-9+6*math.sin(math.pi+i*math.pi/24)) for i in range(24,-1,-1)]
 C.prism('Recessed court crescent rim',outer+inner,'z',143.45,144.1,'wall','roof court')
 C.prism('Crescent planting',outer+inner,'z',144.1,144.35,'plant','roof court')
 for x in (-10,10):
  C.box('Roof garden planter',(x,-11,143.85),(2,4,.8),'wall','roof court',0)
  C.box('Roof garden shrubs',(x,-11,144.6),(1.8,3.8,.7),'plant','roof court',0)

if __name__=='__main__':S.run(sys.modules[__name__])
