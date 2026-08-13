"""Deterministic five-storey collegiate brick courtyard block geometry."""
from __future__ import annotations
import hashlib,json
from typing import Any
ARCHETYPE_ID="graduate_family_housing";VARIANT_ID="collegiate_brick_corner_block"
SIZES={"canonical":42.,"extended":49.};D=38.;DATUMS=(0.,3.8,7.15,10.50,13.85,17.20);MODULE=7.
REFS=[f"frontend/public/archetypes/buildings/graduate-family-housing/variant_0{x}" for x in (".png","_angle_60.jpg","_angle_90.jpg")]
def digest(v:Any):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def mesh(n,v,f,o,d,**m):return {"name":n,"vertices":v,"faces":f,"face_owners":[[o] for _ in f],"sticker_owner_id":o,"material_domain":d,"face_roles":[d]*len(f),**m}
def box(n,b,o,d,**m):
 x0,x1,y0,y1,z0,z1=b;v=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
 return mesh(n,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],o,d,closed=True,outward_winding=True,cap_faces=[2,3,4,5],**m)
def footprint_prism(n,points,z0,z1,o,d,**m):
 # Closed concave-capable extrusion. CCW footprint gives outward side faces.
 area=sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))
 if area<0:points=list(reversed(points))
 count=len(points);v=[[x,y,z0] for x,y in points]+[[x,y,z1] for x,y in points]
 faces=[list(reversed(range(count))),list(range(count,count*2))]+[[i,(i+1)%count,(i+1)%count+count,i+count] for i in range(count)]
 return mesh(n,v,faces,o,d,closed=True,outward_winding=True,cap_faces=list(range(2,len(faces))),**m)
def plane(n,v,o,d,**m):return mesh(n,v,[list(range(len(v)))],o,d,**m)
def aperture(ms,name,side,u0,u1,z0,z1,wall,**meta):
 # wall is exterior/recess coordinate pair. Separate optical planes and backing.
 a,b=wall;reveal=[]
 if side in {"front","rear","court_front","court_rear"}:
  y0,y1=(a,b) if a<b else (b,a);gy=b if side in {"front","court_front"} else a;sgn={"front":1,"rear":-1,"court_front":-1,"court_rear":1}[side]
  for label,bb in (("left",(u0,u0+.13,y0,y1,z0,z1)),("right",(u1-.13,u1,y0,y1,z0,z1)),("sill",(u0+.13,u1-.13,y0,y1,z0,z0+.13)),("head",(u0+.13,u1-.13,y0,y1,z1-.13,z1))):reveal.append(box(name+"_"+label,bb,"sticker_opening_return","precast_return",carrier_kind="opening_return",side=side,**meta))
  cy=gy+sgn*.09;by=gy+sgn*.32;verts=lambda y,dx,dz:[[u0+dx,y,z0+dz],[u1-dx,y,z0+dz],[u1-dx,y,z1-dz],[u0+dx,y,z1-dz]]
 else:
  x0,x1=(a,b) if a<b else (b,a);gx=b if side in {"left","court_left"} else a;sgn={"left":1,"right":-1,"court_left":-1,"court_right":1}[side]
  for label,bb in (("front",(x0,x1,u0,u0+.13,z0,z1)),("rear",(x0,x1,u1-.13,u1,z0,z1)),("sill",(x0,x1,u0+.13,u1-.13,z0,z0+.13)),("head",(x0,x1,u0+.13,u1-.13,z1-.13,z1))):reveal.append(box(name+"_"+label,bb,"sticker_opening_return","precast_return",carrier_kind="opening_return",side=side,**meta))
  cx=gx+sgn*.09;bx=gx+sgn*.32;verts=lambda x,dx,dz:[[x,u0+dx,z0+dz],[x,u1-dx,z0+dz],[x,u1-dx,z1-dz],[x,u0+dx,z1-dz]]
 if side in {"front","rear","court_front","court_rear"}:gv,cv,bv=verts(gy,.13,.13),verts(cy,.15,.15),verts(by,.08,.08)
 else:gv,cv,bv=verts(gx,.13,.13),verts(cx,.15,.15),verts(bx,.08,.08)
 normals={"front":[0,-1,0],"rear":[0,1,0],"left":[-1,0,0],"right":[1,0,0],"court_front":[0,1,0],"court_rear":[0,-1,0],"court_left":[1,0,0],"court_right":[-1,0,0]}
 if side in {"rear","court_front","left","court_right"}:gv,cv,bv=list(reversed(gv)),list(reversed(cv)),list(reversed(bv))
 glass=plane(name+"_glass",gv,"sticker_"+name+"_glass","recessed_glazing",carrier_kind="recessed_glass",side=side,exterior_normal=normals[side],optical_depth_m=0.,**meta);card=plane(name+"_card",cv,"sticker_"+name+"_card","interior_card",carrier_kind="recessed_interior_card",side=side,exterior_normal=normals[side],optical_depth_m=.09,immediately_behind_pane=True,**meta);back=plane(name+"_backing",bv,"sticker_"+name+"_backing","interior_backing",carrier_kind="opaque_aperture_backing",side=side,opaque=True,exterior_normal=normals[side],optical_depth_m=.32,farther_inward=True,contains_card_with_margin_m=.07,**meta);ms+=reveal+[glass,card,back]
 # Shallow occupied-room cues sit behind the card/backing stack. They never
 # intercept the primary sightline and remain aperture bounded.
 cues=[];depth0=.34;depth1=.58
 if side in {"front","rear","court_front","court_rear"}:
  q0=gy+sgn*depth0;q1=gy+sgn*depth1;ya,yb=sorted((q0,q1));
  cues += [box(name+"_room_floor",(u0+.20,u1-.20,ya,yb,z0+.13,z0+.18),"sticker_room_cue","interior_architecture",carrier_kind="interior_room_floor",side=side,**meta),box(name+"_room_ceiling",(u0+.20,u1-.20,ya,yb,z1-.18,z1-.13),"sticker_room_cue","interior_architecture",carrier_kind="interior_room_ceiling",side=side,**meta)]
  for lab,x in (("left",u0+.20),("right",u1-.25)):cues.append(box(name+f"_room_{lab}_wall",(x,x+.05,ya,yb,z0+.18,z1-.18),"sticker_room_cue","interior_architecture",carrier_kind="interior_room_sidewall",side=side,**meta))
 else:
  q0=gx+sgn*depth0;q1=gx+sgn*depth1;xa,xb=sorted((q0,q1));
  cues += [box(name+"_room_floor",(xa,xb,u0+.20,u1-.20,z0+.13,z0+.18),"sticker_room_cue","interior_architecture",carrier_kind="interior_room_floor",side=side,**meta),box(name+"_room_ceiling",(xa,xb,u0+.20,u1-.20,z1-.18,z1-.13),"sticker_room_cue","interior_architecture",carrier_kind="interior_room_ceiling",side=side,**meta)]
  for lab,y in (("front",u0+.20),("rear",u1-.25)):cues.append(box(name+f"_room_{lab}_wall",(xa,xb,y,y+.05,z0+.18,z1-.18),"sticker_room_cue","interior_architecture",carrier_kind="interior_room_sidewall",side=side,**meta))
 ms+=cues
 # Ordinary outer/courtyard windows cut only the approved aperture. Explicit
 # opaque sill/head fabric owns the remainder of the storey across its width.
 zones=[]
 if "level" in meta and not meta.get("fixed_oriel") and not meta.get("stair_slot"):
  level=meta["level"];sb,st=DATUMS[level]+.20,DATUMS[level+1]-.10
  domain="precast" if level==0 else "warm_brick";owner="sticker_aperture_wall_zone"
  if side in {"front","rear","court_front","court_rear"}:
   wall_bounds=(u0,u1,min(a,b),max(a,b))
   for zone,za,zb in (("sill",sb,z0),("head",z1,st)):
    if zb>za:zones.append(box(f"{name}_{zone}_wall",wall_bounds+(za,zb),owner,domain,carrier_kind=f"aperture_{zone}_wall",side=side,level=level,aperture=name,opaque_zone=True))
  else:
   wall_bounds=(min(a,b),max(a,b),u0,u1)
   for zone,za,zb in (("sill",sb,z0),("head",z1,st)):
    if zb>za:zones.append(box(f"{name}_{zone}_wall",wall_bounds+(za,zb),owner,domain,carrier_kind=f"aperture_{zone}_wall",side=side,level=level,aperture=name,opaque_zone=True))
  ms+=zones
 return {"name":name,"side":side,"returns":[x["name"] for x in reveal],"glass":glass["name"],"card":card["name"],"backing":back["name"],"interior_cues":[x["name"] for x in cues],"wall_zones":[x["name"] for x in zones],"opening_u":[u0,u1],"opening_z":[z0,z1],**meta}
def build_geometry(size="canonical"):
 if size not in SIZES:raise KeyError(size)
 w=SIZES[size];extra=w-42.;x1=21.;x0=x1-w;y0=-19.;y1=19.;cx1=7.;cx0=cx1-(14.+extra);cy0=-6.;cy1=6.;ms=[];aps=[]
 # Ring floor/roof carriers: four disjoint bars around a true open courtyard.
 ring=[];modules=[]
 # Slabs at all occupied datums are four disjoint bars clipped around both the
 # open courtyard and the fixed entry/stair zone. Extended insertion is a real
 # negative-X slab segment replacing, never overlaying, the canonical terminal.
 for floor,z in enumerate(DATUMS[:-1]):
  z0,z1z=z+.02,z+.16
  front_segments=[(x0,-21.,True)] if size=="extended" else []
  front_segments += [(-21.,9.9,False),(14.35,x1,False)]
  rear_segments=([ (x0,-21.,True) ] if size=="extended" else [])+[(-21.,x1,False)]
  for idx,(a,b,is_module) in enumerate(front_segments):
   n=f"ring_slab_floor{floor}_front_{idx}";ring.append(n);ms.append(box(n,(a+.35,b-.35,y0+.45,cy0-.45,z0,z1z),"sticker_floor_module" if is_module else "sticker_floor","residential_slab",carrier_kind="whole_7m_module" if is_module else "ring_floor",bar="front",floor=floor,module_width_m=7. if is_module else None,uv_scale_m=1.,module_role="inserted_negative_x" if is_module else "fixed"));modules += [n] if is_module else []
  for idx,(a,b,is_module) in enumerate(rear_segments):
   n=f"ring_slab_floor{floor}_rear_{idx}";ring.append(n);ms.append(box(n,(a+.35,b-.35,cy1+.45,y1-.45,z0,z1z),"sticker_floor_module" if is_module else "sticker_floor","residential_slab",carrier_kind="whole_7m_module" if is_module else "ring_floor",bar="rear",floor=floor,module_width_m=7. if is_module else None,uv_scale_m=1.,module_role="inserted_negative_x" if is_module else "fixed"));modules += [n] if is_module else []
  for label,b in (("left",(x0+.45,cx0-.45,cy0+.45,cy1-.45,z0,z1z)),("right",(cx1+.45,x1-.45,cy0+.45,cy1-.45,z0,z1z))):
   n=f"ring_slab_floor{floor}_{label}";ring.append(n);ms.append(box(n,b,"sticker_floor","residential_slab",carrier_kind="ring_floor",bar=label,floor=floor,uv_scale_m=1.))
  # The landmark slot is only a shallow facade recess: an occupied slab/roof
  # continues behind it to the courtyard instead of forming a full-depth canyon.
  n=f"ring_slab_floor{floor}_entry_back";ring.append(n);ms.append(box(n,(9.55,14.70,y0+1.05,cy0-.45,z0,z1z),"sticker_floor","residential_slab",carrier_kind="ring_floor",bar="entry_back",floor=floor,uv_scale_m=1.,behind_shallow_entry=True))
 # Five fixed floor datums. Outer walls are panelized around real apertures.
 # Front excludes fixed corner/entry zone x>=9.5.
 canonical_bays=[-17.8,-12.6,-7.4,-2.2,3.0,8.2]
 bay_centres=([-24.8]+canonical_bays) if size=="extended" else canonical_bays
 bay_centres=[x for x in bay_centres if x<8.5]
 for level,(za,zb) in enumerate(zip(DATUMS,DATUMS[1:])):
  if level==0:winz=(za+.65,zb-.45)
  elif level==4:winz=(za+.50,zb-.50)
  else:winz=(za+.55,zb-.50)
  voids=[]
  for bay,c in enumerate(bay_centres):
   inserted=size=="extended" and c==-24.8;width=3.35 if (0 if inserted else canonical_bays.index(c))%2==0 else 1.75;role="inserted_negative_x" if inserted else f"canonical_{c:.1f}"
   if width>3:
    group0=c-width/2;light=.91;gap=.18
    for light_i in range(3):
     a=group0+.13+light_i*(light+gap);b=a+light;voids.append((a,b));aps.append(aperture(ms,f"front_l{level}_b{bay}_light{light_i}","front",a,b,*winz,(y0,y0+.40),level=level,bay=bay,light=light_i,center_m=c,width_m=width,bay_role=role,inserted_module=inserted,grammar="mega_frame",grouped_lights=3))
    # Pale physical mullions and a shallow owned spandrel make the group read
    # as architecture rather than one oversized black rectangular void.
    for j,x in enumerate((group0+.13+light,group0+.13+2*light+gap)):ms.append(box(f"front_l{level}_b{bay}_mega_mullion_{j}",(x,x+gap,y0-.06,y0,winz[0],winz[1]),"sticker_mega_mullion","precast",carrier_kind="mega_light_mullion",level=level,bay=bay))
    ms.append(box(f"front_l{level}_b{bay}_mega_spandrel",(group0+.16,group0+width-.16,y0-.055,y0,za+.20,winz[0]-.10),"sticker_mega_spandrel","precast",carrier_kind="mega_masonry_spandrel",level=level,bay=bay,shortened_for_outer_frame=True))
    # A projected pale sill closure owns the narrow strip immediately below
    # every grouped triple. It sits ahead of the optical backing and bridges to
    # the vertical mega frame without exposing a black recess.
    ms.append(box(f"front_l{level}_b{bay}_mega_sill_closure",(group0+.16,group0+width-.16,y0-.12,y0-.055,winz[0]-.10,winz[0]+.02),"sticker_mega_sill_closure","precast",carrier_kind="mega_sill_slot_closure",level=level,bay=bay,terminal_source_map="pale_precast",explicit_underside_role="pale_precast_underside",closed_against_frame=True))
   else:
    voids.append((c-width/2,c+width/2));aps.append(aperture(ms,f"front_l{level}_b{bay}","front",c-width/2,c+width/2,*winz,(y0,y0+.40),level=level,bay=bay,center_m=c,width_m=width,bay_role=role,inserted_module=inserted,grammar="punched"))
  cursor=x0
  for i,(a,b) in enumerate(voids+[(9.5,9.5)]):
   if a>cursor:ms.append(box(f"front_brick_l{level}_panel_{i}",(cursor,a,y0,y0+.30,za+.20,zb-.10),"sticker_front_brick","warm_brick",carrier_kind="outer_brick_panel",level=level,side="front"))
   cursor=b
 # Two selected grouped stacks receive bounded multi-storey pale mega-frames.
 for stack,c in enumerate((-17.8,3.0)):
  if c<x0+.5:continue
  a,b=c-1.80,c+1.80
  for side,x in (("left",a),("right",b-.16)):ms.append(box(f"front_mega_stack_{stack}_{side}",(x,x+.16,y0-.22,y0-.06,3.90,17.10),"sticker_mega_outer_frame","precast",carrier_kind="multi_storey_mega_frame",stack=stack,side=side,projection_depth_m=.22,terminal_source_map="pale_precast",adjacent_finish_terminal=True))
  for j,z in enumerate((3.70,7.02,10.37,13.72,16.96)):ms.append(box(f"front_mega_stack_{stack}_bridge_{j}",(a+.16,b-.16,y0-.22,y0-.06,z,z+.14),"sticker_mega_outer_frame","precast",carrier_kind="multi_storey_mega_frame_bridge",stack=stack,bridge=j,projection_depth_m=.22,terminal_source_map="pale_precast",adjacent_finish_terminal=True))
 # Rear and both sides use subordinate real punched openings and panels.
 for level,(za,zb) in enumerate(zip(DATUMS,DATUMS[1:])):
  zz=(za+.65,zb-.55)
  for side in ("rear","left","right"):
   centres=([-24.5,-14,-7,0,7,14] if size=="extended" and side=="rear" else list(range(-14,15,7)));voids=[]
   for bay,u in enumerate(centres):
    if side=="rear":a,b=u-1.15,u+1.15;aps.append(aperture(ms,f"rear_l{level}_b{bay}",side,a,b,*zz,(y1-.40,y1),level=level,bay=bay,center_m=u,width_m=2.3,bay_role="inserted_negative_x" if u==-24.5 else f"canonical_{u}",inserted_module=u==-24.5,grammar="punched"));voids.append((a,b))
    else:a,b=u-1.05,u+1.05;wall=(x0,x0+.40) if side=="left" else (x1-.40,x1);aps.append(aperture(ms,f"{side}_l{level}_b{bay}",side,a,b,*zz,wall,level=level,bay=bay,grammar="punched"));voids.append((a,b))
   lo,hi=(x0,x1) if side=="rear" else (y0,y1);cursor=lo
   for i,(a,b) in enumerate(voids+[(hi,hi)]):
    if a>cursor:
     bounds=(cursor,a,y1-.30,y1,za+.20,zb) if side=="rear" else ((x0,x0+.30,max(cursor,y0+.30),min(a,y1-.30),za+.20,zb) if side=="left" else (x1-.30,x1,max(cursor,y0+.30),min(a,y1-.30),za+.20,zb))
     bb=list(bounds);bb[5]=zb-.10;ms.append(box(f"{side}_brick_l{level}_panel_{i}",tuple(bb),"sticker_secondary_brick","warm_brick",carrier_kind="outer_brick_panel",level=level,side=side))
    cursor=b
 for level,z in enumerate(DATUMS[1:-1],1):
  for side,b in (("rear",(x0+.34,x1-.34,y1-.34,y1,z-.10,z+.10)),("left",(x0,x0+.34,y0+.34,y1-.34,z-.10,z+.10)),("right",(x1-.34,x1,y0+.34,y1-.34,z-.10,z+.10))):ms.append(box(f"{side}_precast_level_band_{level}",b,"sticker_precast_band","precast",carrier_kind="outer_level_seam_band",side=side,level=level,seam_closed=True,shortened_for_corner_caps=True,terminal_source_map="pale_precast",adjacent_finish_terminal=True))
  for corner,x,y in (("rear_left",x0,y1-.34),("rear_right",x1-.34,y1-.34),("front_left",x0,y0),("front_right",x1-.34,y0)):
   ms.append(box(f"outer_{corner}_level_cap_{level}",(x,x+.34,y,y+.34,z-.10,z+.10),"sticker_outer_corner_cap","precast",carrier_kind="outer_level_corner_cap",corner=corner,level=level,outward_terminal_faces=True,terminal_source_map="pale_precast",adjacent_finish_terminal=True))
  # Exact 100mm closure between the band head and the next masonry course.
  for side,b in (("front",(x0+.34,9.55,y0,y0+.30,z+.10,z+.20)),("rear",(x0+.34,x1-.34,y1-.30,y1,z+.10,z+.20)),("left",(x0,x0+.30,y0+.34,y1-.34,z+.10,z+.20)),("right",(x1-.30,x1,y0+.34,y1-.34,z+.10,z+.20))):ms.append(box(f"outer_{side}_datum_slot_closure_{level}",b,"sticker_datum_slot_closure","warm_brick",carrier_kind="datum_slot_closure",scope="outer",side=side,level=level,touches_band=True,no_overlap=True))
 # Four fully occupied courtyard elevations around the true 14(+7)x12 void.
 court=[]
 for level,(za,zb) in enumerate(zip(DATUMS,DATUMS[1:])):
  for side in ("court_front","court_rear"):
   y=cy0 if side=="court_front" else cy1;wall=(y-.30,y) if side=="court_front" else (y,y+.30);centres=([-11.8]+[-4.8,0.0,4.8] if size=="extended" else [-4.8,0.0,4.8])
   voids=[]
   for bay,c in enumerate(centres):voids.append((c-1,c+1));court.append(aperture(ms,f"{side}_l{level}_b{bay}",side,c-1,c+1,za+.60,zb-.60,wall,level=level,bay=bay,center_m=c,width_m=2.,bay_role="inserted_negative_x" if c==-11.8 else f"canonical_{c:.1f}",inserted_module=c==-11.8,courtyard=True))
   cursor=cx0
   for i,(a,b) in enumerate(voids+[(cx1,cx1)]):
    if a>cursor:ms.append(box(f"{side}_brick_l{level}_panel_{i}",(max(cursor,cx0+.30),min(a,cx1-.30),min(wall),max(wall),za+.20,zb-.10),"sticker_court_brick","warm_brick",carrier_kind="courtyard_brick_panel",side=side,level=level))
    cursor=b
  for side,x,wall in (("court_left",cx0,(cx0-.30,cx0)),("court_right",cx1,(cx1,cx1+.30))):
   voids=[]
   for bay,c in enumerate((-3.,2.)):voids.append((c-.85,c+.85));court.append(aperture(ms,f"{side}_l{level}_b{bay}",side,c-.85,c+.85,za+.60,zb-.60,wall,level=level,bay=bay,courtyard=True))
   cursor=cy0
   for i,(a,b) in enumerate(voids+[(cy1,cy1)]):
    if a>cursor:ms.append(box(f"{side}_brick_l{level}_panel_{i}",(min(wall),max(wall),max(cursor,cy0+.30),min(a,cy1-.30),za+.20,zb-.10),"sticker_court_brick","warm_brick",carrier_kind="courtyard_brick_panel",side=side,level=level))
    cursor=b
 for level,z in enumerate(DATUMS[1:-1],1):
  for side,b in (("front",(cx0+.30,cx1-.30,cy0-.34,cy0,z-.08,z+.08)),("rear",(cx0+.30,cx1-.30,cy1,cy1+.34,z-.08,z+.08)),("left",(cx0-.34,cx0,cy0+.30,cy1-.30,z-.08,z+.08)),("right",(cx1,cx1+.34,cy0+.30,cy1-.30,z-.08,z+.08))):ms.append(box(f"court_{side}_level_band_{level}",b,"sticker_court_band","precast",carrier_kind="courtyard_level_band",side=side,level=level,seam_closed=True,shortened_for_corner_caps=True,terminal_source_map="pale_precast",adjacent_finish_terminal=True))
  for side,b in (("front",(cx0+.30,cx1-.30,cy0-.30,cy0,z+.08,z+.20)),("rear",(cx0+.30,cx1-.30,cy1,cy1+.30,z+.08,z+.20)),("left",(cx0-.30,cx0,cy0+.30,cy1-.30,z+.08,z+.20)),("right",(cx1,cx1+.30,cy0+.30,cy1-.30,z+.08,z+.20))):ms.append(box(f"court_{side}_datum_slot_closure_{level}",b,"sticker_datum_slot_closure","warm_brick",carrier_kind="datum_slot_closure",scope="court",side=side,level=level,touches_band=True,no_overlap=True))
 # A single watertight L at each inner corner replaces the former stack of
 # per-band/crown/parapet end blocks. It owns the courtyard-facing brick seam
 # continuously from the ground wall through the parapet base.
 corner_shapes={
  "front_left":[(cx0-.30,cy0-.30),(cx0+.30,cy0-.30),(cx0+.30,cy0),(cx0,cy0),(cx0,cy0+.30),(cx0-.30,cy0+.30)],
  "front_right":[(cx1-.30,cy0-.30),(cx1+.30,cy0-.30),(cx1+.30,cy0+.30),(cx1,cy0+.30),(cx1,cy0),(cx1-.30,cy0)],
  "rear_left":[(cx0-.30,cy1-.30),(cx0,cy1-.30),(cx0,cy1),(cx0+.30,cy1),(cx0+.30,cy1+.30),(cx0-.30,cy1+.30)],
  "rear_right":[(cx1-.30,cy1),(cx1,cy1),(cx1,cy1-.30),(cx1+.30,cy1-.30),(cx1+.30,cy1+.30),(cx1-.30,cy1+.30)]}
 for corner,points in corner_shapes.items():ms.append(footprint_prism(f"court_{corner}_continuous_brick_L",points,.20,17.34,"sticker_court_corner_brick_L","warm_brick",carrier_kind="court_continuous_corner_L",corner=corner,terminal_source_map="court_brick",courtyard_facing_normals=True,render_risk_closure=True))
 # Fixed projecting bronze corner oriel over four upper levels, 3-light on both turns.
 oriel=[]
 oriel_box=(14.55,20.55,y0-1.55,y0+.40,3.8,17.2)
 for level in range(1,5):
  za,zb=DATUMS[level],DATUMS[level+1]
  for light in range(3):
   a=14.78+light*1.80;b=a+1.64;oriel.append(aperture(ms,f"corner_oriel_front_l{level}_light{light}","front",a,b,za+.25,zb-.35,(y0-1.55,y0-1.20),level=level,light=light,fixed_oriel=True,broad_corner_pavilion=True))
   a=y0-1.18+light*.48;b=a+.38;oriel.append(aperture(ms,f"corner_oriel_turn_l{level}_light{light}","right",a,b,za+.25,zb-.35,(20.25,20.55),level=level,light=light,fixed_oriel=True,broad_corner_pavilion=True))
  ms.append(box(f"corner_oriel_spandrel_l{level}",(14.55,20.55,y0-1.60,y0-1.20,zb-.35,zb-.18),"sticker_bronze_spandrel","bronze",carrier_kind="oriel_spandrel_band",level=level,broad_corner_pavilion=True))
 ms += [box("corner_oriel_soffit",oriel_box[:4]+(3.62,3.8),"sticker_oriel_soffit","precast",carrier_kind="oriel_soffit",fixed=True,broad_corner_pavilion=True),box("corner_oriel_cap",oriel_box[:4]+(17.2,17.34),"sticker_oriel_cap","bronze",carrier_kind="oriel_cap",fixed=True,broad_corner_pavilion=True),box("corner_oriel_thin_crown",(14.50,20.60,y0-1.60,y0+.41,17.34,17.82),"sticker_corner_crown","bronze",carrier_kind="corner_crown",fixed=True,slender_crown=True,broad_corner_pavilion=True)]
 for level in range(1,5):
  za,zb=DATUMS[level]+.25,DATUMS[level+1]-.35
  for j,x in enumerate((14.72,16.58,18.38,20.28)):ms.append(box(f"oriel_front_l{level}_vertical_{j}",(x-.035,x+.035,y0-1.61,y0-1.17,za,zb),"sticker_bronze_grid","bronze",carrier_kind="oriel_bronze_mullion",level=level,face="front",member=j))
  for j,z in enumerate((za,(za+zb)/2,zb)):ms.append(box(f"oriel_front_l{level}_transom_{j}",(14.72,20.28,y0-1.61,y0-1.17,z-.035,z+.035),"sticker_bronze_grid","bronze",carrier_kind="oriel_bronze_transom",level=level,face="front",member=j))
  for j,y in enumerate((y0-1.20,y0-.72,y0-.24,y0+.34)):ms.append(box(f"oriel_return_l{level}_vertical_{j}",(20.22,20.57,y-.035,y+.035,za,zb),"sticker_bronze_grid","bronze",carrier_kind="oriel_return_mullion",level=level,face="return",member=j))
  for j,z in enumerate((za,(za+zb)/2,zb)):ms.append(box(f"oriel_return_l{level}_transom_{j}",(20.22,20.57,y0-1.20,y0+.34,z-.035,z+.035),"sticker_bronze_grid","bronze",carrier_kind="oriel_return_transom",level=level,face="return",member=j))
 lobby=[]
 for light in range(3):
  a=15.0+light*1.72;b=a+1.52;lobby.append(aperture(ms,f"corner_lobby_light_{light}","front",a,b,.25,3.45,(y0-1.15,y0-.88),light=light,ground_corner_lobby=True))
 ms += [box("corner_lobby_soffit",(14.7,20.4,y0-1.25,y0-.88,3.45,3.62),"sticker_lobby_soffit","precast",carrier_kind="corner_lobby_soffit",fixed=True),box("corner_lobby_right_return",(20.15,20.4,y0-1.25,y0+.35,.20,3.62),"sticker_lobby_return","warm_brick",carrier_kind="corner_lobby_closed_return",fixed=True)]
 lobby.append(aperture(ms,"corner_lobby_glazed_return","right",y0-.90,y0+.20,.25,3.45,(20.05,20.15),ground_corner_lobby=True,return_glazing=True))
 for j,x in enumerate((14.92,16.72,18.52,20.32)):ms.append(box(f"lobby_front_vertical_{j}",(x-.035,x+.035,y0-1.20,y0-.85,.25,3.45),"sticker_bronze_grid","bronze",carrier_kind="lobby_bronze_mullion",member=j))
 for j,z in enumerate((.25,1.85,3.45)):ms.append(box(f"lobby_front_transom_{j}",(14.92,20.32,y0-1.20,y0-.85,z-.035,z+.035),"sticker_bronze_grid","bronze",carrier_kind="lobby_bronze_transom",member=j))
 for j,y in enumerate((y0-.90,y0-.53,y0-.16,y0+.20)):ms.append(box(f"lobby_return_vertical_{j}",(20.04,20.16,y-.03,y+.03,.25,3.45),"sticker_bronze_grid","bronze",carrier_kind="lobby_return_mullion",member=j))
 for j,z in enumerate((.25,1.85,3.45)):ms.append(box(f"lobby_return_transom_{j}",(20.04,20.16,y0-.90,y0+.20,z-.03,z+.03),"sticker_bronze_grid","bronze",carrier_kind="lobby_return_transom",member=j))
 # Pale civic base and piers ground the glazed corner lobby.
 ms.append(box("corner_lobby_pale_plinth",(14.55,20.55,y0-1.61,y0-1.45,0,.25),"sticker_lobby_plinth","precast",carrier_kind="corner_lobby_pale_plinth",fixed=True,broad_corner_pavilion=True))
 for j,(a,b) in enumerate(((14.7,14.92),(16.52,16.70),(18.24,18.42),(20.22,20.4))):ms.append(box(f"corner_lobby_pale_pier_{j}",(a,b,y0-1.31,y0-1.15,.25,3.62),"sticker_lobby_pier","precast",carrier_kind="corner_lobby_pale_pier",pier=j,fixed=True))
 ms += [box("front_ground_corner_pier",(x0,x0+.42,y0-.08,y0+.30,.20,3.70),"sticker_ground_pier","precast",carrier_kind="pale_ground_pier",fixed=True),box("front_ground_entry_pier",(9.20,9.55,y0-.08,y0+.30,.20,3.70),"sticker_ground_pier","precast",carrier_kind="pale_ground_pier",fixed=True)]
 # Close plinth and crown bands without crossing the fixed entry/oriel.
 for label,a,b in (("left",x0+.30,9.55),("between",14.35,14.55),("right",20.55,x1-.30)):ms.append(box(f"front_ground_plinth_{label}",(a,b,y0,y0+.30,0,.20),"sticker_ground_plinth","precast",carrier_kind="segmented_ground_plinth",side="front",segment=label,split_for_entry_oriel=True))
 for label,a,b in (("left",x0+.30,9.55),("between",14.35,14.55),("right",20.55,x1-.30)):ms.append(box(f"front_top_crown_closure_{label}",(a,b,y0,y0+.30,17.10,17.20),"sticker_top_closure","warm_brick",carrier_kind="top_crown_gap_closure",side="front",segment=label,split_for_entry_oriel=True))
 # Ground/crown closure on the other seven elevation lines. Runs are shortened
 # 300mm from corners; one-owner caps below close each corner exactly once.
 for z0c,z1c,kind,owner in ((0,.20,"segmented_ground_plinth","sticker_ground_plinth"),(17.10,17.20,"top_crown_gap_closure","sticker_top_closure")):
  for side,b in (("rear",(x0+.30,x1-.30,y1-.30,y1,z0c,z1c)),("left",(x0,x0+.30,y0+.30,y1-.30,z0c,z1c)),("right",(x1-.30,x1,y0+.30,y1-.30,z0c,z1c)),("court_front",(cx0+.30,cx1-.30,cy0-.30,cy0,z0c,z1c)),("court_rear",(cx0+.30,cx1-.30,cy1,cy1+.30,z0c,z1c)),("court_left",(cx0-.30,cx0,cy0+.30,cy1-.30,z0c,z1c)),("court_right",(cx1,cx1+.30,cy0+.30,cy1-.30,z0c,z1c))):ms.append(box(f"{side}_{kind}",b,owner,"precast" if z0c==0 else "warm_brick",carrier_kind=kind,side=side,segment="continuous_shortened",shortened_for_corner_caps=True))
 for z0c,z1c,kind in ((0,.20,"ground_closure_corner_cap"),(17.10,17.20,"top_closure_corner_cap")):
  for scope,points in (("outer",((x0,y0),(x1-.30,y0),(x0,y1-.30),(x1-.30,y1-.30))),("court",((cx0-.30,cy0-.30),(cx1,cy0-.30),(cx0-.30,cy1),(cx1,cy1)))):
   if scope=="court" and kind=="top_closure_corner_cap":continue
   for i,(x,y) in enumerate(points):ms.append(box(f"{scope}_{kind}_{i}",(x,x+.30,y,y+.30,z0c,z1c),"sticker_closure_corner_cap","precast",carrier_kind=kind,scope=scope,corner=i,outward_terminal_faces=True))
 # Adjacent recessed entry/stair slot bounded by precast blades.
 entry=aperture(ms,"fixed_recessed_entry","front",9.9,14.0,.25,3.55,(y0,y0+.95),fixed=True,entry=True)
 ms += [box("entry_left_precast_blade",(9.55,9.9,y0-.20,y0+.50,.20,17.65),"sticker_precast_blade","precast",carrier_kind="entry_precast_blade",fixed=True),box("entry_right_precast_blade",(14.,14.35,y0-.20,y0+.50,.20,17.65),"sticker_precast_blade","precast",carrier_kind="entry_precast_blade",fixed=True),box("entry_canopy",(9.55,14.35,y0-1.05,y0+.05,3.55,3.78),"sticker_entry_canopy","precast",carrier_kind="entry_canopy",fixed=True),box("corner_continuous_canopy",(14.35,14.55,y0-1.60,y0-1.05,3.62,3.78),"sticker_entry_canopy","precast",carrier_kind="continuous_corner_canopy",fixed=True,touches_entry_canopy=True,touches_oriel_soffit=True),box("corner_continuous_plinth",(9.55,14.55,y0-1.45,y0-1.05,0,.25),"sticker_lobby_plinth","precast",carrier_kind="continuous_corner_plinth",fixed=True,touches_lobby_plinth=True)]
 for level in range(1,5):aps.append(aperture(ms,f"entry_stair_slot_l{level}","front",10.25,13.65,DATUMS[level]+.25,DATUMS[level+1]-.25,(y0,y0+.55),fixed=True,stair_slot=True,level=level))
 for level in range(1,5):
  z=DATUMS[level]+.30;ms += [box(f"stair_landing_{level}",(10.40,13.50,y0+.60,y0+1.45,z,z+.16),"sticker_stair_landing","pale_interior",carrier_kind="stair_landing",level=level,visible_through_stair_slot=True),box(f"stair_landing_guard_{level}",(10.40,13.50,y0+.58,y0+.66,z+.16,z+.68),"sticker_stair_guard","bronze",carrier_kind="stair_landing_guard",level=level,visible_through_stair_slot=True)]
 # Brighter shallow lobby floor/ceiling and rear light panel, all behind glazing.
 ms += [box("ground_lobby_bright_floor",(15.0,20.0,y0-1.05,y0+.75,.22,.30),"sticker_bright_lobby","pale_interior",carrier_kind="bright_lobby_floor",fixed=True),box("ground_lobby_bright_ceiling",(15.0,20.0,y0-1.05,y0+.75,3.35,3.45),"sticker_bright_lobby","pale_interior",carrier_kind="bright_lobby_ceiling",fixed=True),box("ground_lobby_light_back",(15.15,19.85,y0+.70,y0+.76,.40,3.25),"sticker_lobby_light","bright_interior_card",carrier_kind="bright_lobby_backing",fixed=True,farther_inward=True)]
 # Concrete floor datums, crown/coping. Runs stop at oriel and use caps.
 for level,z in enumerate(DATUMS[1:-1],1):
  # Projected mega-frames own their complete frontage. Datum runs terminate
  # 100mm before each frame and dedicated pale caps close the exposed ends.
  datum_runs=(("far_left",x0+.34,-19.70),("between_mega0",-15.90,1.10),("between_mega1",4.90,9.55))
  for segment,a,b in datum_runs:
   if b>a:ms.append(box(f"front_precast_datum_{level}_{segment}",(a,b,y0-.08,y0+.05,z-.10,z+.10),"sticker_precast_band","precast",carrier_kind="precast_floor_datum",level=level,segment=segment,split_for_entry_blades=True,shortened_for_oriel=True,shortened_for_corner_caps=True,shortened_for_projected_frame=True,explicit_underside_role="pale_precast_underside",terminal_source_map="pale_precast"))
  for terminal,a,b in (("mega0_left",-19.70,-19.60),("mega0_right",-16.00,-15.90),("mega1_left",1.10,1.20),("mega1_right",4.80,4.90)):
   ms.append(box(f"front_datum_{level}_{terminal}_cap",(a,b,y0-.08,y0+.05,z-.10,z+.10),"sticker_precast_datum_cap","precast",carrier_kind="precast_datum_endpoint_cap",level=level,terminal=terminal,outward_terminal_faces=True,terminal_source_map="pale_precast",explicit_underside_role="pale_precast_underside",closed_against_projected_frame=True))
  # At the stair/oriel junction the band turns inward as one deep pale closure,
  # meeting the full-height binding cheek at a boundary rather than exposing a
  # thin cap to Cycles.
  ms.append(box(f"front_oriel_junction_datum_cap_{level}",(14.35,14.55,y0-.08,y0+.40,z-.10,z+.10),"sticker_precast_datum_cap","precast",carrier_kind="precast_datum_endpoint_cap",level=level,terminal="oriel_junction",outward_terminal_faces=True,terminal_source_map="pale_precast",explicit_underside_role="pale_precast_underside",closed_against_oriel=True))
  # Dedicated pale cap at the left outer facade corner; datum does not end on a
  # raw/coplanar brick corner face.
  # The existing one-owner outer level corner cap is the physical endpoint;
  # declare its pale datum underside/terminal contract rather than overlaying it.
  outer_cap=next(m for m in ms if m["name"]==f"outer_front_left_level_cap_{level}");outer_cap.update(datum_corner_endpoint=True,terminal_source_map="pale_precast",explicit_underside_role="pale_precast_underside",closed_against_datum=True)
 ms += [box("main_coping_front",(x0,14.55,y0-.12,y0+.12,17.85,18.10),"sticker_coping","precast",carrier_kind="main_coping",outward_terminal_faces=True)]
 # Brick/precast cheeks and datum bridges integrate the slot/oriel with the wing.
 ms += [box("entry_recess_left_cheek",(9.55,9.9,y0+.50,y0+1.05,.20,17.10),"sticker_entry_cheek","precast",carrier_kind="entry_recess_cheek",side="left"),box("entry_recess_right_cheek",(14.,14.35,y0+.50,y0+1.05,.20,17.10),"sticker_entry_cheek","warm_brick",carrier_kind="entry_recess_cheek",side="right"),box("stair_oriel_full_height_binding_cheek",(14.35,14.55,y0+.40,y0+1.05,.20,17.20),"sticker_corner_binding_cheek","precast",carrier_kind="stair_oriel_binding_cheek",side="junction",full_height=True),box("oriel_left_junction_cheek",(14.55,14.70,y0,y0+.40,.20,17.20),"sticker_oriel_cheek","precast",carrier_kind="oriel_terminal_cheek",side="left"),box("oriel_right_terminal_cheek",(20.55,20.70,y0,y0+.40,.20,17.20),"sticker_oriel_cheek","precast",carrier_kind="oriel_terminal_cheek",side="right"),box("entry_ground_head_bridge",(9.9,14.,y0+.50,y0+1.05,3.55,3.80),"sticker_slot_bridge","precast",carrier_kind="entry_slot_bridge",level=0),box("stair_oriel_full_height_bridge",(14.35,14.55,y0,y0+.40,17.20,17.34),"sticker_corner_binding_bridge","precast",carrier_kind="stair_oriel_binding_bridge",full_height_seam_closed=True)]
 for level,z in enumerate(DATUMS[1:-1],1):ms.append(box(f"entry_slot_bridge_{level}",(9.9,14.,y0+.55,y0+1.05,z-.10,z+.10),"sticker_slot_bridge","precast",carrier_kind="entry_slot_bridge",level=level,back_of_recess=True))
 # Transition and far-terminal fabric are vertically panelized between every
 # datum.  The datum bands, crown closure and parapet therefore own their
 # complete volumes; no concealed coplanar/positive-volume strips remain.
 transition_z=((.20,3.70),(3.90,7.05),(7.25,10.40),(10.60,13.75),(13.95,17.10))
 for role,a,b,owner,domain in (("transition",14.35,14.55,"sticker_transition","precast"),("terminal",20.55,21.,"sticker_terminal_brick","warm_brick")):
  for i,(za,zb) in enumerate(transition_z):ms.append(box(f"front_{role}_fabric_{i}",(a,b,y0,y0+.30,za,zb),owner,domain,carrier_kind="corner_transition_fabric",segment=i,datum_disjoint=True,top_closure_disjoint=True,parapet_disjoint=True))
 # Roof ring, parapet/courtyard coping and essential bounded mechanical court.
 # Roof finish is a true disjoint schedule: a light outer gravel maintenance
 # band and a broad dark membrane/service ring toward the courtyard. Both are
 # closed upward-wound solids; no coplanar overlay is used.
 gravel_fields=(("front_left_outer",(x0+.3,9.45,y0+.5,y0+3.0,17.2,17.38)),("front_left_a_cap",(9.45,9.55,y0+.5,y0+3.0,17.2,17.38)),("landmark_outer",(9.55,20.55,y0+1.05,y0+3.0,17.2,17.38)),("front_left_b_cap",(14.35,14.45,y0+.5,y0+1.05,17.2,17.38)),("front_left_b",(14.45,14.55,y0+.5,y0+1.05,17.2,17.38)),("front_right_outer",(20.55,x1-.3,y0+.3,y0+3.0,17.2,17.38)),("rear_outer",(x0+.3,x1-.3,y1-3.0,y1-.3,17.2,17.38)),("left_outer",(x0+.3,x0+3.0,cy0-.3,cy1+.3,17.2,17.38)),("right_outer",(x1-3.0,x1-.3,cy0-.3,cy1+.3,17.2,17.38)))
 membrane_fields=(("front_left_inner",(x0+.3,9.45,y0+3.0,cy0-.3,17.2,17.38)),("landmark_inner",(9.55,20.55,y0+3.0,cy0-.3,17.2,17.38)),("front_right_inner",(20.55,x1-.3,y0+3.0,cy0-.3,17.2,17.38)),("rear_inner",(x0+.3,x1-.3,cy1+.3,y1-3.0,17.2,17.38)),("left_inner",(x0+3.0,cx0-.3,cy0-.3,cy1+.3,17.2,17.38)),("right_inner",(cx1+.3,x1-3.0,cy0-.3,cy1+.3,17.2,17.38)))
 for label,b in gravel_fields:ms.append(box(f"gravel_roof_{label}",b,"sticker_gravel_roof_cap" if label.endswith("cap") else "sticker_gravel_roof","gravel_roof",carrier_kind="gravel_roof_endpoint_cap" if label.endswith("cap") else "gravel_roof_field",bar=label,uv_scale_m=1.,trimmed_for_oriel_crown=True,split_for_entry_blades=True,outward_terminal_faces=label.endswith("cap"),behind_shallow_entry=label=="landmark_outer",upward_roof_finish=True))
 for label,b in membrane_fields:ms.append(box(f"membrane_roof_{label}",b,"sticker_dark_roof_membrane","dark_roof_membrane",carrier_kind="dark_inner_membrane_field",bar=label,uv_scale_m=1.,trimmed_for_oriel_crown=True,behind_shallow_entry=label=="landmark_inner",upward_roof_finish=True,service_zone=True))
 for side,b in (("front_left_a",(x0+.22,9.45,y0,y0+.22,17.2,17.85)),("front_left_b",(14.45,14.55,y0,y0+.22,17.2,17.85)),("front_right",(20.55,x1-.22,y0,y0+.22,17.2,17.85)),("rear",(x0+.22,x1-.22,y1-.22,y1,17.2,17.85)),("left",(x0,x0+.22,y0+.22,y1-.22,17.2,17.85)),("right",(x1-.22,x1,y0+.22,y1-.22,17.2,17.85)),("court_front",(cx0+.22,cx1-.22,cy0-.22,cy0,17.34,17.85)),("court_rear",(cx0+.22,cx1-.22,cy1,cy1+.22,17.34,17.85)),("court_left",(cx0-.22,cx0,cy0+.22,cy1-.22,17.34,17.85)),("court_right",(cx1,cx1+.22,cy0+.22,cy1-.22,17.34,17.85))):ms.append(box(f"parapet_{side}",b,"sticker_parapet","precast",carrier_kind="closed_parapet_run",side=side,shortened_for_corner_caps=True,split_for_entry_blades=side.startswith("front"),terminal_source_map="pale_precast" if side.startswith("court") else None))
 for side,b in (("front",(cx0+.30,cx1-.30,cy0-.30,cy0,17.20,17.34)),("rear",(cx0+.30,cx1-.30,cy1,cy1+.30,17.20,17.34)),("left",(cx0-.30,cx0,cy0+.30,cy1-.30,17.20,17.34)),("right",(cx1,cx1+.30,cy0+.30,cy1-.30,17.20,17.34))):ms.append(box(f"court_parapet_brick_base_{side}",b,"sticker_court_parapet_brick","warm_brick",carrier_kind="court_parapet_brick_base",side=side,shortened_for_corner_caps=True,terminal_source_map="court_brick",outward_terminal_faces=True))
 for a,b,side in ((9.45,9.55,"entry_left"),(14.35,14.45,"entry_right")):ms.append(box(f"front_parapet_{side}_endpoint_cap",(a,b,y0,y0+.22,17.2,17.85),"sticker_parapet_endpoint_cap","precast",carrier_kind="parapet_entry_endpoint_cap",side=side,outward_terminal_faces=True))
 for scope,points,height in (("outer",((x0,y0),(x1-.22,y0),(x0,y1-.22),(x1-.22,y1-.22)),(17.2,17.85)),("court",((cx0-.22,cy0-.22),(cx1,cy0-.22),(cx0-.22,cy1),(cx1,cy1)),(17.34,17.85))):
  for i,(x,y) in enumerate(points):ms.append(box(f"{scope}_parapet_corner_cap_{i}",(x,x+.22,y,y+.22,*height),"sticker_parapet_corner_cap","precast",carrier_kind="parapet_corner_cap",scope=scope,corner=i,outward_terminal_faces=True,terminal_source_map="pale_precast" if scope=="outer" else "court_coping",adjacent_finish_terminal=True))
 # Independent court coping ring hides no open ends: each run stops at the
 # 220mm corner cap and every terminal is explicitly owned in court coping.
 for side,b in (("front",(cx0,cx1,cy0-.22,cy0,17.85,18.02)),("rear",(cx0,cx1,cy1,cy1+.22,17.85,18.02)),("left",(cx0-.22,cx0,cy0,cy1,17.85,18.02)),("right",(cx1,cx1+.22,cy0,cy1,17.85,18.02))):ms.append(box(f"court_coping_{side}",b,"sticker_court_coping","precast",carrier_kind="court_coping_run",side=side,shortened_for_corner_caps=True,terminal_source_map="court_coping",adjacent_finish_terminal=True))
 for i,(x,y) in enumerate(((cx0-.22,cy0-.22),(cx1,cy0-.22),(cx0-.22,cy1),(cx1,cy1))):ms.append(box(f"court_coping_corner_cap_{i}",(x,x+.22,y,y+.22,17.85,18.02),"sticker_court_coping_cap","precast",carrier_kind="court_coping_corner_cap",corner=i,outward_terminal_faces=True,terminal_source_map="court_coping",adjacent_finish_terminal=True))
 for side,a,b in (("left",14.55,14.65),("right",20.45,20.55)):ms.append(box(f"front_parapet_crown_{side}_cap",(a,b,y0,y0+.22,17.2,18.1),"sticker_parapet_cap","precast",carrier_kind="parapet_crown_endpoint_cap",side=side,outward_terminal_faces=True))
 # ~20x18 central screen, clear of courtyard; four walls with owned ends.
 mech=[]
 # One continuous screen envelope offset 3m around the courtyard. Every wall
 # sits on a roof bar; none crosses the court. Extended tier lengthens only its
 # negative-X wall spans and records the contiguous added segment.
 sx0,sx1=(-17. if size=="extended" else -10.),10.;sy0,sy1=-9.,9.
 horizontal=[(-10.,10.,"fixed")]+([(-17.,-10.,"inserted_negative_x")] if size=="extended" else [])
 for side,y in (("front",sy0),("rear",sy1-.15)):
  for index,(a,b,role) in enumerate(horizontal):
   n=f"mechanical_screen_{side}_{index}";mech.append(n);ms.append(box(n,(a,b,y,y+.15,17.38,18.78),"sticker_mechanical_screen","bronze_screen",carrier_kind="mechanical_screen",side=side,screen_role=role,roof_supported=True,outward_terminal_faces=True,screen_envelope=[sx0,sx1,sy0,sy1],module_width_m=7. if role!="fixed" else None,subordinate_height=True))
 for side,bb in (("left",(sx0,sx0+.15,sy0+.15,sy1-.15,17.38,19.45)),("right",(sx1-.15,sx1,sy0+.15,sy1-.15,17.38,19.45))):
  bb=bb[:4]+(17.38,18.78);n=f"mechanical_screen_{side}";mech.append(n);ms.append(box(n,bb,"sticker_mechanical_screen","bronze_screen",carrier_kind="mechanical_screen",side=side,screen_role="inserted_negative_x_terminal" if side=="left" and size=="extended" else "fixed",roof_supported=True,outward_terminal_faces=True,screen_envelope=[sx0,sx1,sy0,sy1],subordinate_height=True))
 equipment=[]
 for i,(x,y,dx,dy,h) in enumerate(((x0+5,-12,2,1.5,1.3),(x0+11,-12,2,1.5,1.5),(x1-6,-12,2,1.5,1.2),(x0+6,12,2,1.5,1.1),(x1-6,12,2,1.5,1.4))):n=f"roof_hvac_{i}";equipment.append(n);ms.append(box(n,(x-dx/2,x+dx/2,y-dy/2,y+dy/2,17.38,17.38+h),"sticker_hvac","roof_equipment",carrier_kind="bounded_hvac",equipment=i,outside_courtyard=True,court_clearance_m=.45,equipment_clearance_m=.5))
 skylight=box("square_roof_skylight",(16,17.5,3,4.5,17.38,17.70),"sticker_skylight","rooflight_glass",carrier_kind="square_skylight",fixed=True,equipment_clearance_m=.5);ms.append(skylight)
 for i,(x,y) in enumerate(((x0+2,-15),(19,-8),(x0+2,15),(19,8))):ms.append(box(f"roof_vent_{i}",(x-.10,x+.10,y-.10,y+.10,17.38,18.05),"sticker_vent","galvanized_metal",carrier_kind="sparse_roof_vent",vent=i,equipment_clearance_m=.5))
 g={"archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,"size":size,"reference_evidence":REFS,"dimensions":{"width_m":w,"depth_m":D,"occupied_storeys":5,"datums_m":list(DATUMS),"main_coping_m":18.1,"corner_crown_m":18.78},"courtyard":{"width_m":14.+extra,"depth_m":12.,"open_to_sky":True,"bounds":[cx0,cx1,cy0,cy1]},"scale_contract":{"canonical":"42x38","extended":"49x38","module_width_m":7.,"insertion_zone_x_m":[-28.,-21.] if size=="extended" else None,"fixed_positive_x_terminal_m":21.,"depth_fixed":True,"storeys_fixed":True,"fixed_oriel_entry_roof_kit":True},"whole_modules":modules,"apertures":aps,"courtyard_apertures":court,"oriel_apertures":oriel,"corner_lobby_apertures":lobby,"entry":entry,"ring_floors":ring,"mechanical_screen":mech,"roof_equipment":equipment,"skylight":skylight["name"],"meshes":ms,"hard_stops":["exactly_five_storeys","true_open_14x12_courtyard","fixed_three_light_four_upper_corner_oriel","adjacent_recessed_entry_and_stair_slot","alternating_punched_mega_frame_grammar","full_inner_elevations","bounded_20x18_mechanical_screen","seven_metre_whole_module_only","no_balconies_solar_or_full_retail","one_owner_closed_nonoverlapping_assemblies"]};g["geometry_sha256"]=digest({k:v for k,v in g.items() if k!="geometry_sha256"});return g
if __name__=="__main__":
 for s in SIZES:
  g=build_geometry(s);print(s,len(g["meshes"]),g["geometry_sha256"])
