"""Source-locked blue curtain-wall tower: architectural clay pilot."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'catalogue_foursquare_pilot'))
import support as S
C=S.C
_original_mesh=C.mesh
def _square_mesh(name,vs,fs,role='wall',module='envelope',soft=0):
 return _original_mesh(name,vs,fs,role,module,0)
C.mesh=_square_mesh
SLUG='glass_tower_podium_modern';PARENT=SLUG;VARIANT='glass_tower_blue_reflective';INDEX=0
TITLE='Blue glass office tower';WIDTH=32.;DEPTH=30.;HEIGHT=99.;STOREYS=25
PALETTE=dict(wall=(.64,.64,.60),foundation=(.45,.46,.44),trim=(.49,.55,.58),roof=(.40,.43,.44),glass=(.12,.27,.37),interior=(.38,.39,.37),floor=(.48,.48,.45),timber=(.30,.23,.16),hardware=(.18,.21,.23))

def manifest(version):
 return S.prework(sys.modules[__name__],version,dict(width=WIDTH,depth=DEPTH,height=HEIGHT),
  dict(plan='Rectangular curtain-wall tower, slightly projecting central front glass bay; low stone-clad glazed podium and projecting entrance canopy.',roof='Flat roof with perimeter glass crown, central mechanical room, offset smaller plant enclosure and roof equipment; slender right front mast.',programme='Office tower with glazed lobby, repeated occupied office floors and enclosed lift core.',facade='Approximately 24 repeated upper floor bands plus tall lobby; silver mullion grid over blue glass. Front central bay projects; corner strips step back.'),
  ['Native dimensions and 25 occupied levels are conceptual estimates from source floor bands, not surveyed.', 'Front source and oblique differ at the podium: front is authoritative for asymmetric stone portal heights; top is authoritative for projecting canopy; rear and side lobby entrances inferred.', 'Rear curtain wall continues the visible grid; unseen office fitout and core are inferred.', 'Mast capped at 99 m; light strips represented as pale solid trim, not emissive textures.'],
  ['Continuous floor slabs support facade mullions.','Podium walls reach ground; entry is level with grade.','Canopy beams return into the podium structure.','Mechanical enclosures and mast bear on roof slab.'],[
   dict(name='facade_close',location=(-29,-58,52),target=(0,-12,49),whole=False),
   dict(name='architecture_close',location=(28,-49,15),target=(0,-13,5),whole=False),
   dict(name='glass_close',location=(9,-29,45),target=(4,-12,43),whole=False,lens=60),
   dict(name='roof_contact',location=(39,-44,112),target=(0,0,92),whole=False),
   dict(name='lobby_contact',location=(-21,-42,9),target=(0,-12,3),whole=False)])

def facade(face,length,z0,floors,bays,step=3.5):
 bay=length/bays
 for level in range(floors):
  z=z0+level*step
  face.part('Floor edge',length/2,.15,z+.19,length,.30,.38,'trim','floor edges',0)
  for i in range(bays):
   u=bay*(i+.5)
   # The carrier consists of actual mullions and floor-edge bands; no solid backing across apertures.
   face.part('Facade mullion',i*bay,.15,z+step/2,.12,.30,step,'trim','curtain wall',0)
   if face.label=='lobby' and i in (4,5):
    face.door(f'Lobby entrance {i}',u,z,bay-.14,2.7,role='trim',glazed=True)
    face.window(f'Lobby entrance transom {i}',u,z+2.75,bay-.14,step-2.8,cols=1,rows=1,sill=False)
   else:
    face.window(f'{face.label} level {level+1} bay {i+1}',u,z+.42,bay-.14,step-.47,cols=1,rows=1,inset=.14,sill=False,bar=.04)
  face.part('End mullion',length,.15,z+step/2,.12,.30,step,'trim','curtain wall',0)

def build():
 C.box('Ground slab',(0,0,.10),(32,30,.2),'foundation','base',0)
 C.box('Podium roof',(0,1,7.9),(32,25,.3),'wall','podium',0)
 for x,top in [(-14.5,10.5),(14.5,14)]:C.box('Asymmetric stone portal pier',(x,-11,(top+.2)/2),(3,3,top-.2),'wall','podium',0)
 C.box('Stone portal head',(0,-11,7.3),(32,3,1.1),'wall','podium',0)
 facade(C.Face((-13,-12.5,0),(1,0,0),(0,1,0),'lobby'),26,.2,1,10,6.5)
 for name,origin,tangent,inward,length in [('right',(16,-11,0),(0,1,0),(-1,0,0),24),('left',(-16,13,0),(0,-1,0),(1,0,0),24),('rear',(16,13,0),(-1,0,0),(0,-1,0),32)]:
  facade(C.Face(origin,tangent,inward,name+' lobby'),length,.2,1,8,7.5)
 # Transparent canopy is bounded and structurally connected, not a floating plate.
 C.box('Canopy glass',(0,-12.7,6.5),(27,4.6,.10),'glass','entry canopy',0)
 for x in range(-13,14,2):C.box('Canopy beam',(x,-12.7,6.37),(.12,4.6,.20),'trim','entry canopy',0)
 C.box('Canopy fascia',(0,-15,6.38),(27,.15,.25),'trim','entry canopy',0)
 for level in range(25):
  z=8+level*3.5
  C.box('Occupied floor slab',(0,1,z),(28,24,.23),'floor','office slabs',0)
  C.box('Projecting central bay floor',(0,-11.5,z),(20,1,.23),'floor','front bay',0)
  if level<24:
   C.box('Enclosed lift core',(0,3,z+1.65),(7,7,3.3),'interior','core',0)
   for x in (-9,-3,3,9):
    C.box('Office desk',(x,-7,z+.85),(1.6,.75,.10),'timber','office occupation',0)
    C.box('Desk pedestal',(x,-7,z+.42),(.45,.6,.74),'interior','office occupation',0)
    C.box('Office partition',(x,-5,z+1.1),(.12,2,2),'interior','office occupation',0)
 for name,origin,tangent,inward,length,bays in [('front centre',(-10,-12,0),(1,0,0),(0,1,0),20,8),('front left',(-14,-11,0),(1,0,0),(0,1,0),4,2),('front right',(10,-11,0),(1,0,0),(0,1,0),4,2),('bay left return',(-10,-11,0),(0,-1,0),(1,0,0),1,1),('bay right return',(10,-12,0),(0,1,0),(-1,0,0),1,1)]:
  facade(C.Face(origin,tangent,inward,name),length,8,24,bays)
 facade(C.Face((14,-11,0),(0,1,0),(-1,0,0),'right'),24,8,24,8)
 facade(C.Face((-14,13,0),(0,-1,0),(1,0,0),'left'),24,8,24,8)
 facade(C.Face((14,13,0),(-1,0,0),(0,-1,0),'rear'),28,8,24,10)
 C.box('Mechanical room',(0,2,93.6),(13,12,3.3),'wall','roof plant',0)
 C.box('Secondary mechanical room',(8,5,93.1),(3,5,2.3),'wall','roof plant',0)
 for x,y in [(-10,-3),(-10,5),(9,-5)]:C.box('Roof equipment',(x,y,92.8),(2.5,3,1.5),'roof','roof plant',0)
 for name,origin,tangent,inward,length,bays in [('front',(-14,-11,0),(1,0,0),(0,1,0),28,10),('rear',(14,13,0),(-1,0,0),(0,-1,0),28,10),('right',(14,-11,0),(0,1,0),(-1,0,0),24,8),('left',(-14,13,0),(0,-1,0),(1,0,0),24,8)]:
  face=C.Face(origin,tangent,inward,name+' crown')
  facade(face,length,92,1,bays,4)
  face.part('Crown horizontal rail',length/2,.1,94,length,.15,.08,'trim','crown',0)
 C.box('Mast',(13.5,-11.25,53.5),(.16,.16,91),'trim','mast',0)
 C.box('Lobby reception',(0,-6,1.1),(4,1,1.8),'wall','lobby programme',0)
 C.box('Lobby core',(0,3,4),(7,7,7.6),'interior','lobby programme',0)

if __name__=='__main__': S.run(sys.modules[__name__])
