"""Four timber homes with a shared five-post veranda; exact measured source cadence."""
import clay_core as C
from assemblies import hole, faces, bed, sofa, bathroom, shrub, garden_chair, vertical_cladding, flat_roof
from geometry import kitchen
from common import wall, stair, stair_hole, base_manifest, camera_set
from build import PALETTE as BASE

SLUG='ubst-timber-cohousing'
PALETTE=dict(BASE,wall=(.57,.355,.18),timber=(.57,.355,.18),roof=(.15,.16,.17))
GROUND=.15
FIRST=4.15
ROOF=7.85


def cameras():
    roster=camera_set(24,10,8.05,[
      ('facade_close',(-3,-20,5),(-3,-5,4.5),52),
      ('architecture_close',(-3,-12,2.4),(-1,-5,2),35),
      ('glass_close',(-4,-7.7,1.9),(-4.6,-3,1.5),35),
      ('roof_contact',(15,-10,13),(10,-5,7.8),42),
      ('side_projection',(22,-5,5),(12,0,4),42),
      ('interior',(-2.7,-4.5,1.8),(-4.1,1.5,1.4),24),
      ('stairs',(-1.1,2.7,5.8),(-1.1,-2,1.5),24),
      ('upper_landing',(-1.9,3.7,5.8),(-1.1,-1,4.9),24),
      ('bedroom',(-2.9,-3.6,5.8),(-4.4,-1.8,4.9),22),
      ('bathroom',(-2.7,3.0,5.8),(-4.5,4,4.9),20),
      ('rear_entry',(-1.2,10,2.5),(-1.2,5,1.5),42),
      ('veranda',(9,-8.6,2),(0,-5.8,2),28),
      ('shared_garden',(0,15,5),(0,6.8,1.2),35)])
    matched={
      'front':dict(location=(0,-40,2.4),target=(0,0,2.4),lens=42,shift_y=.08),
      'front_corner':dict(location=(23,-42,2.4),target=(0,0,2.4),lens=42,shift_y=.08),
      'aerial':dict(location=(23,-46,27),target=(0,0,4),lens=42)}
    for view in roster:
        view.update(matched.get(view['name'],{}))
    return roster


def construct():
    C.box('Continuous grounded slab',(0,0,.075),(24,10,.15),'foundation','foundation')
    C.box('Veranda ground slab',(0,-5.9,.075),(24.4,1.8,.15),'pale','entry')
    C.box('Street walk',(0,-9,.025),(25,1.2,.05),'foundation','landscape')
    for i,x in enumerate((-9,-3,3,9)):
        ff=faces(6,10,cx=x,label=f'Home {i+1} ')
        front=[hole('Living window',-.7,.95,3.23,1.95),hole('Front entrance',1.94,GROUND,1.03,2.74)]
        front += [hole('Tall upper bedroom window',u,4.85,1.14,2.38) for u in (-1.0,1.2)]
        rear=[hole('Rear entrance',-1.9,GROUND,1.03,2.74),hole('Kitchen window',1.0,.95,2.2,1.95)]
        rear += [hole('Rear bedroom window',u,4.85,1.14,2.38) for u in (-1.2,1.2)]
        for side,f in enumerate(ff):
            if side==3 and i>0:continue
            external=side in (0,2) or (side==3 and i==0) or (side==1 and i==3)
            hs=front if side==0 else rear if side==2 else []
            if external and side in (1,3):
                hs=[hole('Side service entrance',2.6,GROUND,1.03,2.74),hole('Small side window',-.4,1.60,.9,.95)]
                hs += [hole('Side bedroom window',u,4.85,1.14,2.38) for u in (-2.2,2.2)]
            span=6 if side in (0,2) else 9.46
            wall(f,'Timber wall' if external else 'Shared party wall',span,GROUND,ROOF if external else ROOF-.20,hs,'timber' if external else 'interior')
            if external:
                # Clear the complete sill/trim envelope, not just the optical aperture.
                cladding_cuts=[dict(h,w=h['w']+.18,z=h['z']-.08,h=h['h']+.10) for h in hs]
                vertical_cladding(f,span,GROUND,ROOF,cladding_cuts,spacing=.15,role='timber')
            if side==0:
                # Three panes belong only to the wide living opening.
                for u in (-.7-3.23/6,-.7+3.23/6):f.part('Living mullion',u,.14,1.925,.045,.09,1.95,'trim','openings')
        slab=C.box('Occupied upper floor',(x,0,FIRST-.11),(5.46,9.46,.22),'floor','floors')
        stair_hole(slab,x+1.9,-3.55,FIRST,width=1.1)
        stair('Dwelling stair',x+1.9,-3.55,GROUND,FIRST,width=1.1)
        hall=C.Face((x+.70,0,0),(0,1,0),(-1,0,0),'Upper room corridor')
        hall.wall('Upper bedroom enclosure',-4.73,4.73,FIRST,ROOF-.2,.12,'interior',
                  [hole('Front bedroom doorway',-1.3,FIRST,.95,2.3),hole('Rear bedroom doorway',1.5,FIRST,.95,2.3)])
        C.box('Bedroom divider',(x-1,0,(FIRST+ROOF-.2)/2),(3.46,.12,ROOF-.2-FIRST),'interior','rooms')
        bath=C.Face((x,2.7,0),(1,0,0),(0,1,0),'Bathroom')
        bath.wall('Bathroom front',-2.73,.7,FIRST,ROOF-.2,.12,'interior',[hole('Bathroom entry',.10,FIRST,.85,2.3)])
        bed(x-1.3,-2,FIRST);bed(x-1.3,1.35,FIRST);bathroom(x-1.4,4.05,FIRST)
        sofa(x-.9,-1,GROUND);kitchen(x-.5,4.15,GROUND,2.6)
        C.box('Rear patio',(x,6.3,.06),(5.7,2.6,.12),'pale','shared garden')
        garden_chair(x-1.5,6.1,.12)
        C.box('Front patio',(x,-7.7,.04),(5.9,1.8,.08),'pale','entry')
        garden_chair(x-1.3,-7.4,.08)
        for z in (3.6,7.25):
            for y in (-2.5,2.5):C.qa_room_light('Occupied home',(x-.9,y,z),160,2)
            C.qa_room_light('Stair light',(x+1.9,0,z),100,1.4)
    # One unified canopy; five load-bearing posts at exact bay boundaries.
    C.box('Continuous veranda canopy',(0,-5.8,4.07),(24.4,1.65,.26),'timber','canopy')
    C.box('Canopy membrane',(0,-5.8,4.21),(24.5,1.73,.035),'roof','canopy')
    C.box('Canopy front fascia',(0,-6.64,4.12),(24.5,.10,.24),'trim','canopy')
    for x in (-12,-6,0,6,12):
        C.box('Seated timber canopy post',(x,-6.50,2.045),(.18,.18,3.79),'timber','supports')
        C.box('Post ground shoe',(x,-6.50,.19),(.24,.24,.08),'hardware','supports')
    C.box('Closed inset membrane roof',(0,0,ROOF-.10),(23.46,9.46,.20),'roof','roof')
    for a,b in [((-12,-5),(12,-5)),((12,-5),(12,5)),((12,5),(-12,5)),((-12,5),(-12,-5))]:
        C.beam('Seated roof parapet',(*a,ROOF+.075),(*b,ROOF+.075),.18,.15,'wall','roof')
        C.beam('Continuous coping',(*a,ROOF+.175),(*b,ROOF+.175),.26,.05,'trim','roof')
    for y in (-3,-1,1,3):C.box('Fine membrane seam',(0,y,ROOF+.002),(23.46,.012,.004),'joint','roof')
    # Reference doors are timber. Keep leaves open for walking but preserve their material authority.
    for obj in C.objects():
        if 'open optical leaf' in obj.name:
            obj.data.materials[0]=C.MATS['timber']
            obj['cityprompt_semantic_role']='timber'
            obj.name=obj.name.replace('open optical leaf','open timber leaf')
    for opening in C.OPENINGS:
        if opening.get('kind')=='inward-open glazed door':opening['kind']='inward-open timber leaf with glazed transom'
    for x in (-8,8):
        C.rod('Roof vent',(x,2,ROOF-.05),(x,2,ROOF+.35),.08,'trim','roof services')
        C.box('Vent flashing',(x,2,ROOF+.015),(.35,.35,.03),'roof','roof services')
    for x in (-6,0,6):
        C.box('Grounded front divider planter',(x,-7.4,.30),(.65,2.3,.44),'timber','landscape')
        for y in (-8,-7,-6.6):shrub(x,y,.52,.30)
    for x in (-10,-5,0,5,10):
        C.box('Shared garden planter',(x,8,.22),(3.5,.8,.32),'timber','shared garden')
        shrub(x,8,.38,.45)


def manifest(version):
    return base_manifest(SLUG,version,cameras(),dict(dimensions_m=dict(width=24,depth=10,height=8.05),observed_storeys=2,
       source_measurements=['Front1627pxwide536pxhigh: height7.9m abovegrade at24m frontage.',
         'Four6m bays; eight1.14x2.38m upperwindows; ground3.23x1.95m windows and1.03x2.74m doors.',
         'Five canopy posts; canopy top4.1m abovegrade; two sideupperwindows,smalllowerwindow,rearwarddoor.'],
       hidden_assumptions=['Depth10m authored.','Rear, left side, co-housing garden and internal programme inferred.']),
       dict(storeys=2,dwellings=4,uses=['Townhouse','Co-housing'],legal_approval=False,
            description='Four independently entered homes with connected upper bedrooms, shared veranda and rear garden.'),
       dict(topology='Single continuous flat main roof plus attached shallow veranda canopy',authority='Three compatible locked views'))
