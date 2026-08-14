"""Deterministic fixed-landmark geometry for the historic iron-and-glass market hall."""
from __future__ import annotations
import hashlib,json,math
from typing import Any

ARCHETYPE_ID="food_hall_market_hall";VARIANT_ID="market_historic_iron_glass"
W=45.;D=60.;X0=-22.5;X1=22.5;Y0=-30.;Y1=30.;SPRING_Z=8.35;CROWN_Z=15.35
FRAME_Y=(-26.0,-18.55,-11.10,-3.65,3.80,11.25,18.70,26.15)
REFS=[f"frontend/public/archetypes/buildings/food_hall_market_hall/variant_0{x}" for x in (".png","_angle_60.jpg","_angle_90.jpg")]
def digest(v:Any):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def mesh(n,v,f,o,d,**m):return {"name":n,"vertices":v,"faces":f,"face_owners":[[o] for _ in f],"sticker_owner_id":o,"material_domain":d,"face_roles":[d]*len(f),**m}
def box(n,b,o,d,**m):
 x0,x1,y0,y1,z0,z1=b;v=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
 return mesh(n,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],o,d,closed=True,outward_winding=True,cap_faces=[2,3,4,5],**m)
def prism_axis(n,poly,a,b,axis,o,d,**m):
 area=sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))
 if area<0:poly=list(reversed(poly))
 if axis=="y":v=[[u,a,w] for u,w in poly]+[[u,b,w] for u,w in poly]
 else:v=[[a,u,w] for u,w in poly]+[[b,u,w] for u,w in poly]
 q=len(poly);f=[list(reversed(range(q))),list(range(q,2*q))]+[[i,(i+1)%q,(i+1)%q+q,i+q] for i in range(q)]
 return mesh(n,v,f,o,d,closed=True,outward_winding=True,cap_faces=list(range(2,len(f))),**m)
def plane(n,v,o,d,**m):return mesh(n,v,[list(range(len(v)))],o,d,**m)
def beam_xz(n,p0,p1,t,y0,y1,o,d,**m):
 x0,z0=p0;x1,z1=p1;dx=x1-x0;dz=z1-z0;l=max(math.hypot(dx,dz),1e-6);nx=-dz/l*t/2;nz=dx/l*t/2
 return prism_axis(n,[(x0+nx,z0+nz),(x1+nx,z1+nz),(x1-nx,z1-nz),(x0-nx,z0-nz)],y0,y1,"y",o,d,**m)
def beam_yz(n,p0,p1,t,x0,x1,o,d,**m):
 y0,z0=p0;y1,z1=p1;dy=y1-y0;dz=z1-z0;l=max(math.hypot(dy,dz),1e-6);ny=-dz/l*t/2;nz=dy/l*t/2
 return prism_axis(n,[(y0+ny,z0+nz),(y1+ny,z1+nz),(y1-ny,z1-nz),(y0-ny,z0-nz)],x0,x1,"x",o,d,**m)
def ellipse_z(x):return SPRING_Z+(CROWN_Z-SPRING_Z)*math.sqrt(max(0.,1-(x/13.5)**2))
def ellipse_x(z):return 13.5*math.sqrt(max(0.,1-((z-SPRING_Z)/(CROWN_Z-SPRING_Z))**2))
def aisle_z(side,x):
 return 7.35+(8.35-7.35)*((x+22.5)/9.0 if side=="left" else (22.5-x)/9.0)
def aisle_poly(side,a,b,raise_z=0.):
 za,zb=aisle_z(side,a)+raise_z,aisle_z(side,b)+raise_z
 return [(a,za),(b,zb),(b,zb-.18),(a,za-.18)]
def arched_side_aperture(ms,name,side,cy,level=0):
 ext=22.5 if side=="right" else -22.5;sgn=-1 if side=="right" else 1;glass_x=ext+sgn*.28;card_x=ext+sgn*.34;back_x=ext+sgn*.62
 y0,y1=cy-1.75,cy+1.75;z0,spring,crown=1.25,4.45,5.65;segments=10
 arc=[(cy+1.75*math.cos(math.pi*i/segments),spring+1.20*math.sin(math.pi*i/segments)) for i in range(segments+1)]
 outline=[(y0,z0),(y1,z0),(y1,spring)]+arc[1:-1]+[(y0,spring)]
 def verts(x,inset):return [[x,y,z] for y,z in [(y0+inset,z0+inset),(y1-inset,z0+inset),(y1-inset,spring)]+[(cy+(1.75-inset)*math.cos(math.pi*i/segments),spring+(1.20-inset)*math.sin(math.pi*i/segments)) for i in range(1,segments)]+[(y0+inset,spring)]]
 normal=[1,0,0] if side=="right" else [-1,0,0]
 gv,cv,bv=verts(glass_x,.10),verts(card_x,.15),verts(back_x,.04)
 if side=="left":gv,cv,bv=list(reversed(gv)),list(reversed(cv)),list(reversed(bv))
 glass=plane(name+"_glass",gv,"sticker_arch_glass","physical_glass",carrier_kind="recessed_arch_glass",side=side,exterior_normal=normal)
 card=plane(name+"_card",cv,"sticker_market_interior","interior_card",carrier_kind="recessed_interior_card",side=side,exterior_normal=normal)
 back=plane(name+"_backing",bv,"sticker_market_backing","interior_backing",carrier_kind="opaque_interior_backing",side=side,exterior_normal=normal)
 # The opaque optical backing faces the exterior card.  Give its nave side a
 # separate warm occupied-bay face and low timber counter, so an interior
 # camera never sees the black back of the exterior-only carrier.
 inner_x=ext+sgn*.70;iv=verts(inner_x,.08)
 if side=="right":iv=list(reversed(iv))
 interior_normal=[-1,0,0] if side=="right" else [1,0,0]
 warm=plane(name+"_interior_warm_plane",iv,"sticker_front_side_bay","warm_plaster",carrier_kind="gallery_bay_warm_backplane",side=side,exterior_normal=interior_normal,nave_facing=True,bounded_to_arch=True)
 inner2=inner_x+sgn*.10
 counter=box(name+"_interior_counter",(min(inner_x,inner2),max(inner_x,inner2),y0+.18,y1-.18,z0,z0+.30),"sticker_timber_stall","timber_stall",carrier_kind="gallery_bay_counter_front",side=side,nave_facing=True)
 ms += [glass,card,back,warm,counter,box(name+"_sill",(min(ext,glass_x),max(ext,glass_x),y0,y1,z0-.16,z0),"sticker_stone_return","pale_stone",carrier_kind="arch_sill_return",side=side)]
 for label,y in (("left",y0),("right",y1-.14)):ms.append(box(name+"_"+label,(min(ext,glass_x),max(ext,glass_x),y,y+.14,z0,spring),"sticker_stone_return","pale_stone",carrier_kind="arch_jamb_return",side=side))
 for i in range(segments):ms.append(beam_yz(f"{name}_arch_ring_{i}",arc[i],arc[i+1],.16,min(ext,glass_x),max(ext,glass_x),"sticker_stone_arch","pale_stone",carrier_kind="physical_arch_ring",side=side,segment=i))
 return {"name":name,"side":side,"glass":glass["name"],"card":card["name"],"backing":back["name"],"opening_y":[y0,y1],"opening_z":[z0,crown]}

def build_geometry(size="canonical"):
 if size!="canonical":raise KeyError(size)
 ms=[];aps=[]
 # Ground hall and two independent mezzanine bars leave the central nave open.
 ms.append(box("market_hall_floor",(X0+.35,X1-.35,Y0+.35,Y1-.35,0,.18),"sticker_market_floor","brick_floor",carrier_kind="open_market_floor",nave_open=True))
 for side,a,b in (("left",X0+.55,-13.50),("right",13.50,X1-.55)):
  # The street end lands exactly on the inner face of the terminal stone pier.
  deck_a,deck_b=(-21.45,b-.18) if side=="left" else (a+.18,21.45)
  ms += [box(f"{side}_gallery_deck",(deck_a,deck_b,-29.66,27.0,4.12,4.34),"sticker_gallery_deck","timber_gallery",carrier_kind="gallery_deck",side=side,extended_to_entrance=True),box(f"{side}_gallery_soffit",(deck_a,deck_b,-29.66,27.0,3.96,4.12),"sticker_gallery_soffit","painted_soffit",carrier_kind="gallery_soffit",side=side,extended_to_entrance=True),box(f"{side}_gallery_edge_girder",((b-.18,b) if side=="left" else (a,a+.18))+(-29.66,27.0,3.82,4.42),"sticker_iron","painted_iron",carrier_kind="gallery_edge_girder",side=side,extended_to_entrance=True)]
  inner=b if side=="left" else a
  for j,y in enumerate([-29.60,*FRAME_Y,27.0]):ms.append(box(f"{side}_gallery_rail_post_{j}",(inner-.055,inner+.055,y-.055,y+.055,4.42,5.48),"sticker_iron","painted_iron",carrier_kind="gallery_rail_post",side=side))
  ms += [box(f"{side}_gallery_rail_top",(inner-.055,inner+.055,-29.66,27.0,5.40,5.50),"sticker_iron","painted_iron",carrier_kind="gallery_rail_top",side=side,extended_to_entrance=True),box(f"{side}_gallery_rail_mid",(inner-.04,inner+.04,-29.66,27.0,4.82,4.90),"sticker_iron","painted_iron",carrier_kind="gallery_rail_mid",side=side,extended_to_entrance=True)]
 # Eight complete structural frame lines / seven equal longitudinal bays.
 for fi,y in enumerate(FRAME_Y):
  for side,x in (("left",-13.5),("right",13.5)):
   ms += [box(f"frame{fi}_{side}_column_base",(x-.34,x+.34,y-.34,y+.34,.18,.48),"sticker_iron","painted_iron",carrier_kind="cast_iron_column_base",frame=fi,side=side),box(f"frame{fi}_{side}_column_shaft",(x-.22,x+.22,y-.22,y+.22,.48,3.82),"sticker_iron","painted_iron",carrier_kind="cast_iron_column_shaft",frame=fi,side=side),box(f"frame{fi}_{side}_column_capital",(x-.42,x+.42,y-.38,y+.38,3.82,4.12),"sticker_iron","painted_iron",carrier_kind="cast_iron_column_capital",frame=fi,side=side),box(f"frame{fi}_{side}_upper_post",(x-.18,x+.18,y-.18,y+.18,4.42,8.30),"sticker_iron","painted_iron",carrier_kind="gallery_upper_iron_post",frame=fi,side=side,supports_eave_clerestory=True,seated_on_edge_girder=True)]
  # Barrel truss rib and gallery cross tie at every line.
  xs=[-13.5+i*1.125 for i in range(25)]
  for i in range(24):
   if xs[i+1]<=-2.25 or xs[i]>=2.25:
    # Stop the haunch ribs short of the lantern cheek frames.  The explicit
    # 0.10 m clearance prevents the thick rib prism from spearing the closed
    # lantern side in Cycles while keeping the structural spring continuous.
    a,b=xs[i],xs[i+1]
    if b==-2.25:b=-2.35
    if a==2.25:a=2.35
    ms.append(beam_xz(f"frame{fi}_barrel_rib_{i}",(a,ellipse_z(a)),(b,ellipse_z(b)),.18,y-.10,y+.10,"sticker_iron","painted_iron",carrier_kind="barrel_truss_rib",frame=fi,segment=i,split_for_lantern=True,lantern_clearance_m=.10))
  ms.append(box(f"frame{fi}_gallery_cross_tie",(-13.5,13.5,y-.09,y+.09,7.72,7.90),"sticker_iron","painted_iron",carrier_kind="iron_cross_tie",frame=fi,lands_at_spring=True))
 # Long side walls: seven actual arched apertures each, panelized around voids.
 centers=[-22.5+i*7.5 for i in range(7)]
 for side in ("left","right"):
  ext0,ext1=(-22.5,-21.9) if side=="left" else (21.9,22.5);cursor=Y0+.72
  for i,cy in enumerate(centers):
   y0,y1=cy-1.75,cy+1.75
   if y0>cursor:ms.append(box(f"{side}_brick_pier_{i}",(ext0,ext1,cursor,y0,.18,7.85),"sticker_side_brick","red_brick",carrier_kind="side_brick_pier",side=side,bay=i))
   ms += [box(f"{side}_bay{i}_sill_wall",(ext0,ext1,y0,y1,.18,1.25),"sticker_side_brick","red_brick",carrier_kind="aperture_sill_wall",side=side,bay=i),box(f"{side}_bay{i}_head_wall",(ext0,ext1,y0,y1,5.65,7.85),"sticker_side_brick","red_brick",carrier_kind="aperture_head_wall",side=side,bay=i)]
   # Stepped brick spandrels above the curved glass shoulders.
   for j in range(8):
    ya=y0+j*(3.5/8);yb=y0+(j+1)*(3.5/8);mid=(ya+yb)/2;curve=4.45+1.20*math.sqrt(max(0,1-((mid-cy)/1.75)**2))
    if curve+.10<5.65:ms.append(box(f"{side}_bay{i}_arch_spandrel_{j}",(ext0,ext1,ya,yb,curve+.10,5.65),"sticker_side_brick","red_brick",carrier_kind="arch_spandrel_wall",side=side,bay=i,segment=j))
   aps.append(arched_side_aperture(ms,f"{side}_arched_bay_{i}",side,cy));cursor=y1
  if cursor<Y1-.62:ms.append(box(f"{side}_brick_terminal",(ext0,ext1,cursor,Y1-.62,.18,7.85),"sticker_side_brick","red_brick",carrier_kind="side_brick_pier",side=side,terminal=True))
  for y in (Y0+.72,Y1-1.12):ms.append(box(f"{side}_stone_end_quoin_{int(y)}",(ext0-.08,ext1+.08,y,y+.50,.18,8.10),"sticker_stone","pale_stone",carrier_kind="stone_end_quoin",side=side,outward_terminal_faces=True))
  ms += [box(f"{side}_stone_coping",(ext0-.08,ext1+.08,Y0+.72,Y1-.62,7.85,8.10),"sticker_stone","pale_stone",carrier_kind="side_wall_coping",side=side)]
 # Exact front: 27m central cavern plus two closed, occupied 9m side bays.
 for side,x in (("left",-22.5),("right",21.45)):ms.append(box(f"front_{side}_stone_pier",(x,x+1.05,Y0,Y0+.72,.18,8.25),"sticker_stone","pale_stone",carrier_kind="front_terminal_stone_pier",side=side,outward_terminal_faces=True))
 for side,a,b in (("left",-21.45,-13.78),("right",13.78,21.45)):
  # The side aisle remains a real entrance volume.  Its occupied shopfront is
  # recessed 4.5 m behind the frontage and panelized around transparent
  # joinery; nothing closes the street plane between pier and column.
  xa,xb=a+.62,b-.62;back_y=-25.18
  upper_poly=[(a,4.34),(b,4.34),(b,aisle_z(side,b)-.22),(a,aisle_z(side,a)-.22)]
  ms += [box(f"front_{side}_shop_back_left",(a,xa,back_y,back_y+.34,.18,3.96),"sticker_front_side_bay","warm_plaster",carrier_kind="recessed_shop_back_wall",side=side,part="left"),box(f"front_{side}_shop_back_right",(xb,b,back_y,back_y+.34,.18,3.96),"sticker_front_side_bay","warm_plaster",carrier_kind="recessed_shop_back_wall",side=side,part="right"),box(f"front_{side}_shop_back_sill",(xa,xb,back_y,back_y+.34,.18,.84),"sticker_front_side_bay","warm_plaster",carrier_kind="recessed_shop_back_wall",side=side,part="sill"),box(f"front_{side}_shop_back_lower_head",(xa,xb,back_y,back_y+.34,3.76,3.96),"sticker_front_side_bay","warm_plaster",carrier_kind="recessed_shop_back_wall",side=side,part="lower_head"),prism_axis(f"front_{side}_shop_back_upper",upper_poly,back_y,back_y+.34,"y","sticker_front_side_bay","warm_plaster",carrier_kind="recessed_shop_back_wall",side=side,part="upper",split_for_gallery=True,slope_capped=True,roof_clearance_m=.22,clear_of_roof_underside_m=.04)]
  door_a,door_b=((xb-1.42,xb-.12) if side=="left" else (xa+.12,xa+1.42));display_a,display_b=((xa+.12,door_a-.12) if side=="left" else (door_b+.12,xb-.12))
  for part,x0,x1 in (("left_jamb",xa,xa+.12),("right_jamb",xb-.12,xb),("door_divide",door_a-.06,door_a+.06) if side=="left" else ("door_divide",door_b-.06,door_b+.06)):
   for tier,z0,z1 in (("lower",.98,3.00),("upper",3.10,3.62)):
    ms.append(box(f"front_{side}_shop_joinery_{part}_{tier}",(x0,x1,back_y-.12,back_y-.02,z0,z1),"sticker_timber_stall","timber_stall",carrier_kind="recessed_shopfront_joinery",side=side,part=part,tier=tier,split_around_rails=True))
  for part,z0,z1 in (("sill",.84,.98),("transom",3.00,3.10),("head",3.62,3.76)):
   ms.append(box(f"front_{side}_shop_joinery_{part}",(xa,xb,back_y-.12,back_y-.02,z0,z1),"sticker_timber_stall","timber_stall",carrier_kind="recessed_shopfront_joinery",side=side,part=part))
  for part,x0,x1 in (("display",display_a,display_b),("door",door_a,door_b)):
   ms += [plane(f"front_{side}_shop_{part}_glass",[[x0,back_y-.01,.99],[x1,back_y-.01,.99],[x1,back_y-.01,3.61],[x0,back_y-.01,3.61]],"sticker_shop_glass","physical_glass",carrier_kind="recessed_shopfront_glass",side=side,part=part,exterior_normal=[0,-1,0]),plane(f"front_{side}_shop_{part}_card",[[x0+.03,back_y+.025,1.02],[x1-.03,back_y+.025,1.02],[x1-.03,back_y+.025,3.58],[x0+.03,back_y+.025,3.58]],"sticker_market_interior","interior_card",carrier_kind="recessed_shopfront_card",side=side,part=part,exterior_normal=[0,-1,0],brought_forward_for_cycles=True),plane(f"front_{side}_shop_{part}_backing",[[x0-.02,back_y+.24,.96],[x1+.02,back_y+.24,.96],[x1+.02,back_y+.24,3.64],[x0-.02,back_y+.24,3.64]],"sticker_market_backing","interior_backing",carrier_kind="recessed_shopfront_backing",side=side,part=part,exterior_normal=[0,-1,0])]
  # The old full display-width "cavity" sat between glass and card and was the
  # actual Cycles occluder.  Keep only bounded warm side/ceiling cues behind the
  # card plus the existing timber counter front.
  ms.append(box(f"front_{side}_shop_counter",(display_a,display_b,back_y-.48,back_y-.14,.78,1.02),"sticker_timber_stall","timber_stall",carrier_kind="recessed_shop_counter",side=side,warm_counter_front=True))
  for edge,x0,x1 in (("left",display_a,display_a+.12),("right",display_b-.12,display_b)):
   ms.append(box(f"front_{side}_shop_bay_side_{edge}",(x0,x1,back_y+.04,back_y+.20,1.04,3.56),"sticker_front_side_bay","warm_plaster",carrier_kind="recessed_shop_bay_side_cue",side=side,edge=edge,behind_card=True))
  ms.append(box(f"front_{side}_shop_bay_ceiling",(display_a+.12,display_b-.12,back_y+.04,back_y+.20,3.44,3.58),"sticker_front_side_bay","warm_plaster",carrier_kind="recessed_shop_bay_ceiling_cue",side=side,behind_card=True))
  outer=-21.45 if side=="left" else 21.45;inner=-13.5 if side=="left" else 13.5
  ms.append(beam_xz(f"front_{side}_iron_half_gable",(outer,7.55),(inner,8.35),.22,Y0-.18,Y0+.18,"sticker_iron","painted_iron",carrier_kind="front_iron_half_gable",side=side))
  c=(a+b)/2;spandrel=[(c-1.25,7.32),(c-.85,7.18),(c-.30,7.28),(c,7.12),(c+.30,7.28),(c+.85,7.18),(c+1.25,7.32),(c+1.25,7.48),(c-1.25,7.48)]
  ms.append(prism_axis(f"front_{side}_shaped_spandrel",spandrel,Y0-.34,Y0-.18,"y","sticker_iron","painted_iron",carrier_kind="historic_shaped_spandrel",side=side,physical_relief=True,open_bay_fraction=.67))
  # Four endpoint-shaped panes follow the actual half-gable, avoiding the
  # rectangular overshoot that previously protruded through the sloped head.
  pa,pb=a+.18,b-.18;step=(pb-pa)/4
  def side_fan_top(x):return 7.55+(8.35-7.55)*((x-a)/(b-a) if side=="left" else (b-x)/(b-a))
  for j in range(4):
   x0,x1=pa+j*step,pa+(j+1)*step
   q0,q1=x0+.025,x1-.025;t0,t1=side_fan_top(q0)-.03,side_fan_top(q1)-.03
   # At the two outer eaves the pane tapers to a small triangle instead of
   # inverting below the common fan sill.
   b0,b1=min(7.60,t0-.03),min(7.60,t1-.03)
   ms.append(plane(f"front_{side}_fan_glass_{j}",[[q0,Y0+.19,b0],[q1,Y0+.19,b1],[q1,Y0+.19,t1],[q0,Y0+.19,t0]],"sticker_roof_glass","physical_glass",carrier_kind="front_side_fan_glass",side=side,panel=j,exterior_normal=[0,-1,0],endpoint_clipped=True,triangular_outer_taper=(j==0 if side=="left" else j==3)))
 for side,x in (("left",-13.5),("right",13.5)):
  capital=[(x-.50,7.88),(x-.38,8.10),(x-.62,8.24),(x-.42,8.35),(x+.42,8.35),(x+.62,8.24),(x+.38,8.10),(x+.50,7.88)]
  ms += [box(f"front_{side}_principal_column",(x-.28,x+.28,Y0-.30,Y0+.30,.18,7.88),"sticker_iron","painted_iron",carrier_kind="front_principal_column",side=side,lands_at_spring=True),prism_axis(f"front_{side}_principal_capital",capital,Y0-.34,Y0+.34,"y","sticker_iron","painted_iron",carrier_kind="front_principal_capital",side=side,lands_at_spring=True,shaped_historic_capital=True)]
  for direction in (-1,1):
   end_x=x+direction*1.65;sideward=direction==(-1 if side=="left" else 1)
   if sideward:
    outer_x=-21.45 if side=="left" else 21.45;inner_x=x;target_z=7.55+.80*((end_x-outer_x)/(inner_x-outer_x))
   else:target_z=7.72
   points=[(x+direction*.16,6.42),(x+direction*.42,6.78),(x+direction*.92,7.20),(end_x,target_z)]
   for j in range(3):ms.append(beam_xz(f"front_{side}_knee_{direction}_{j}",points[j],points[j+1],.11,Y0-.36,Y0-.30,"sticker_iron","painted_iron",carrier_kind="historic_curved_knee_brace",side=side,direction=direction,segment=j,physical_relief=True))
   ms.append(box(f"front_{side}_knee_{direction}_terminal",(end_x-.075,end_x+.075,Y0-.30,Y0-.18,target_z-.075,target_z+.075),"sticker_iron","painted_iron",carrier_kind="historic_brace_terminal_connector",side=side,direction=direction,target="half_gable" if sideward else "lattice",boundary_contact_only=True))
  rosette=[(x+.24*math.cos(2*math.pi*i/10),8.10+.24*math.sin(2*math.pi*i/10)) for i in range(10)]
  ms.append(prism_axis(f"front_{side}_capital_rosette",rosette,Y0-.44,Y0-.34,"y","sticker_iron","painted_iron",carrier_kind="historic_capital_rosette",side=side,physical_relief=True))
 # Fine iron filigree is supported only by the two physical side galleries;
 # the existing high lattice remains the sole central ornamental bridge.
 for zone,a,b in (("left",-21.28,-13.94),("right",13.94,21.28)):
  ms += [box(f"front_filigree_{zone}_bottom",(a,b,Y0+.22,Y0+.34,4.30,4.42),"sticker_iron","painted_iron",carrier_kind="front_gallery_filigree_rail",zone=zone,part="bottom",seated_on_gallery=True),box(f"front_filigree_{zone}_top",(a,b,Y0+.22,Y0+.34,5.34,5.43),"sticker_iron","painted_iron",carrier_kind="front_gallery_filigree_rail",zone=zone,part="top",seated_on_gallery=True)]
  n=max(2,int((b-a)/1.15));step=(b-a)/n
  for j in range(n):
   x0=a+j*step;x1=x0+step
   ms += [beam_xz(f"front_filigree_{zone}_diag_a_{j}",(x0+.10,4.43),(x1-.10,5.31),.055,Y0+.22,Y0+.34,"sticker_iron","painted_iron",carrier_kind="front_gallery_filigree",zone=zone,panel=j,seated_on_gallery=True),beam_xz(f"front_filigree_{zone}_diag_b_{j}",(x0+.10,5.31),(x1-.10,4.43),.055,Y0+.22,Y0+.34,"sticker_iron","painted_iron",carrier_kind="front_gallery_filigree",zone=zone,panel=j,seated_on_gallery=True)]
  for j in range(n+1):
   cx=a+j*step;motif=[(cx+.10*math.cos(2*math.pi*i/8),4.95+.10*math.sin(2*math.pi*i/8)) for i in range(8)];ms.append(prism_axis(f"front_filigree_{zone}_rosette_{j}",motif,Y0+.20,Y0+.22,"y","sticker_iron","painted_iron",carrier_kind="front_gallery_filigree_rosette",zone=zone,panel=j,physical_relief=True,seated_on_gallery=True))
 xs=[-13.5+i*1.125 for i in range(25)]
 for i in range(24):ms.append(beam_xz(f"front_gable_arch_ring_{i}",(xs[i],ellipse_z(xs[i])),(xs[i+1],ellipse_z(xs[i+1])),.34,Y0-.18,Y0,"sticker_iron","painted_iron",carrier_kind="front_gable_arch_ring",segment=i,outward_terminal_faces=True))
 ms.append(box("front_lattice_gallery_girder",(-13.0,13.0,Y0-.18,Y0+.18,7.55,7.90),"sticker_iron","painted_iron",carrier_kind="front_iron_lattice_girder"))
 for i in range(12):
  a=-13.5+i*2.25;b=a+2.25;ms.append(beam_xz(f"front_lattice_diag_a_{i}",(a,7.58),(b,7.88),.09,Y0-.20,Y0-.10,"sticker_iron","painted_iron",carrier_kind="iron_lattice_diagonal",segment=i));ms.append(beam_xz(f"front_lattice_diag_b_{i}",(a,7.88),(b,7.58),.09,Y0-.20,Y0-.10,"sticker_iron","painted_iron",carrier_kind="iron_lattice_diagonal",segment=i))
 fan_x=[-13.5+i*1.5 for i in range(19)]
 for i,x in enumerate(fan_x):ms.append(box(f"front_gable_mullion_{i}",(x-.035,x+.035,Y0+.18,Y0+.30,7.90,ellipse_z(x)-.20),"sticker_iron","painted_iron",carrier_kind="front_gable_mullion",member=i))
 for i in range(18):
  a,b=fan_x[i],fan_x[i+1];ms.append(plane(f"front_gable_glass_{i}",[[a+.05,Y0+.29,7.95],[b-.05,Y0+.29,7.95],[b-.05,Y0+.29,ellipse_z(b-.05)-.25],[a+.05,Y0+.29,ellipse_z(a+.05)-.25]],"sticker_roof_glass","physical_glass",carrier_kind="front_gable_glass",panel=i,exterior_normal=[0,-1,0],endpoint_clipped=True))
 for i,z in enumerate((9.45,11.25,13.05)):
  lim=ellipse_x(z)-.18;ms.append(box(f"front_gable_horizontal_rail_{i}",(-lim,lim,Y0+.16,Y0+.30,z-.045,z+.045),"sticker_iron","painted_iron",carrier_kind="front_gable_horizontal_rail",rail=i,ellipse_clipped=True))
 # Barrel glass/rails now close fully to both gable/verge planes.
 xs=[-13.5+i*.75 for i in range(37)]
 for i in range(36):
  a,b=xs[i]+.06,xs[i+1]-.06;poly=[(a,ellipse_z(a)),(b,ellipse_z(b)),(b,ellipse_z(b)-.10),(a,ellipse_z(a)-.10)]
  if b<=-2.25 or a>=2.25:ms.append(prism_axis(f"barrel_glass_strip_{i}",poly,Y0,Y1,"y","sticker_roof_glass","physical_glass",carrier_kind="barrel_glass_panel",strip=i,watertight=True,closed_to_gables=True))
 for i,x in enumerate(xs):
  if abs(x)>=2.35:ms.append(beam_xz(f"barrel_longitudinal_rail_{i}",(x,ellipse_z(x)-.13),(x,ellipse_z(x)+.13),.12,Y0,Y1,"sticker_iron","painted_iron",carrier_kind="barrel_longitudinal_rail",rail=i,closed_to_gables=True,split_for_lantern=True))
 # The lantern stops 2.8 m short of each gable.  Close those two central ridge
 # bands with the same glass-and-rail grammar so no 4.6 m-wide roof slot is
 # left open between the lantern end and the gable arch.
 ridge_x=[-2.25+i*.75 for i in range(7)]
 for end,ya,yb in (("front",Y0,-27.20),("rear",27.20,Y1)):
  for i in range(6):
   a,b=ridge_x[i]+.06,ridge_x[i+1]-.06;poly=[(a,ellipse_z(a)),(b,ellipse_z(b)),(b,ellipse_z(b)-.10),(a,ellipse_z(a)-.10)]
   ms.append(prism_axis(f"barrel_{end}_ridge_end_glass_{i}",poly,ya,yb,"y","sticker_roof_glass","physical_glass",carrier_kind="barrel_ridge_end_glass_panel",end=end,strip=i,watertight=True,closed_to_gable=True))
  for i,x in enumerate(ridge_x):ms.append(beam_xz(f"barrel_{end}_ridge_end_rail_{i}",(x,ellipse_z(x)-.13),(x,ellipse_z(x)+.13),.12,ya,yb,"sticker_iron","painted_iron",carrier_kind="barrel_ridge_end_rail",end=end,rail=i,closed_to_gable=True))
 # Bay-split eave clerestories close the long spring-line strips.  Existing
 # upper frame posts own the eight structural seams; rails stop at their faces
 # and the terminal spans meet the front/rear ironwork without overlap.
 clerestory_spans=[(-29.66,FRAME_Y[0]-.18)]+[(FRAME_Y[i]+.18,FRAME_Y[i+1]-.18) for i in range(7)]+[(FRAME_Y[-1]+.18,29.62)]
 for side,x,norm in (("left",-13.44,[1,0,0]),("right",13.44,[-1,0,0])):
  for i,(ya,yb) in enumerate(clerestory_spans):
   ms += [box(f"{side}_eave_clerestory_sill_{i}",(x-.06,x+.06,ya,yb,7.90,8.00),"sticker_iron","painted_iron",carrier_kind="eave_clerestory_rail",side=side,bay=i,part="sill"),box(f"{side}_eave_clerestory_head_{i}",(x-.06,x+.06,ya,yb,8.27,8.35),"sticker_iron","painted_iron",carrier_kind="eave_clerestory_rail",side=side,bay=i,part="head")]
   v=[[x,ya+.04,8.01],[x,yb-.04,8.01],[x,yb-.04,8.26],[x,ya+.04,8.26]]
   if side=="right":v=list(reversed(v))
   ms.append(plane(f"{side}_eave_clerestory_glass_{i}",v,"sticker_roof_glass","physical_glass",carrier_kind="eave_clerestory_glass",side=side,bay=i,exterior_normal=norm,bay_split=True))
 # Roof fields are physically cut around 8 rooflights and one zinc dormer.
 light_centers=(-15.,-5.,5.,15.)
 for side,domain,owner,ox0,ox1 in (("left","slate_roof","sticker_slate_roof",-17.85,-15.15),("right","standing_seam_zinc","sticker_zinc_roof",15.15,17.85)):
  rows=[(Y0,-16.,None),(-16.,-14.,"light0"),(-14.,-6.,None),(-6.,-4.,"light1"),(-4.,4.,None),(4.,6.,"light2"),(6.,14.,None),(14.,16.,"light3"),(16.,20.,None)]
  if side=="right":rows += [(20.,24.,"dormer"),(24.,Y1,None)]
  else:rows += [(20.,Y1,None)]
  xa,xb=(-22.5,-13.5) if side=="left" else (13.5,22.5)
  for ri,(ya,yb,hole) in enumerate(rows):
   # The dormer has a wider, separately bounded footprint than a rooflight.
   spans=[(xa,xb)] if hole is None else ([(xa,15.15),(19.50,xb)] if hole=="dormer" else [(xa,ox0),(ox1,xb)])
   for si,(a,b) in enumerate(spans):ms.append(prism_axis(f"{side}_aisle_roof_r{ri}_s{si}",aisle_poly(side,a,b),ya,yb,"y",owner,domain,carrier_kind="closed_aisle_roof_panel",side=side,row=ri,segment=si,asymmetric_finish=True,cut_around_apertures=True))
  for li,y in enumerate(light_centers):
   # Four slope-aligned curbs and a thin closed glass panel sit in each cutout.
   for part,a,b,ya,yb in (("outer",ox0,ox0+.12,y-.88,y+.88),("inner",ox1-.12,ox1,y-.88,y+.88),("front",ox0+.12,ox1-.12,y-1.,y-.88),("rear",ox0+.12,ox1-.12,y+.88,y+1.)):
    ms.append(prism_axis(f"{side}_rooflight_{li}_curb_{part}",aisle_poly(side,a,b,.08),ya,yb,"y","sticker_rooflight_curb","painted_iron",carrier_kind="rooflight_curb",side=side,index=li,part=part,slope_aligned=True))
   ms.append(prism_axis(f"{side}_rooflight_{li}_glass",aisle_poly(side,ox0+.16,ox1-.16,.18),y-.84,y+.84,"y","sticker_roof_glass","physical_glass",carrier_kind="rooflight_glass",side=side,index=li,slope_aligned=True))
 # One watertight dormer shell occupies the exact cutout.  Its bottom edge
 # follows the aisle plane at both endpoints, so the end caps and longitudinal
 # cheeks neither float above nor penetrate the standing-seam roof.
 dormer_section=[(15.15,aisle_z("right",15.15)+.02),(19.50,aisle_z("right",19.50)+.02),(19.50,9.08),(17.30,10.10),(15.15,9.08)]
 ms.append(prism_axis("right_zinc_dormer_shell",dormer_section,20.,24.,"y","sticker_zinc_dormer","standing_seam_zinc",carrier_kind="zinc_roof_dormer",side="right",actual_footprint_cut=True,slope_following_base=True,closed_side_cheeks=True,closed_end_caps=True))
 # True open lantern side frames: continuous sill/head rails and posts at each
 # six-metre seam expose the glass rather than hiding it behind an opaque slab.
 ms += [box("ridge_lantern_front_end",(-2.25,2.25,-27.20,-27.,15.00,16.50),"sticker_iron","painted_iron",carrier_kind="ridge_lantern_end",side="front",outward_terminal_faces=True),box("ridge_lantern_rear_end",(-2.25,2.25,27.,27.20,15.00,16.50),"sticker_iron","painted_iron",carrier_kind="ridge_lantern_end",side="rear",outward_terminal_faces=True),box("ridge_lantern_cap",(-2.30,2.30,-27.20,27.20,16.50,16.72),"sticker_zinc_roof","standing_seam_zinc",carrier_kind="ridge_lantern_cap")]
 for side,x0,x1,x,norm in (("left",-2.25,-2.05,-2.15,[-1,0,0]),("right",2.05,2.25,2.15,[1,0,0])):
  ms += [box(f"ridge_lantern_{side}_sill",(x0,x1,-27.,27.,15.00,15.12),"sticker_iron","painted_iron",carrier_kind="ridge_lantern_sill_head_rail",side=side,part="sill"),box(f"ridge_lantern_{side}_head",(x0,x1,-27.,27.,16.38,16.50),"sticker_iron","painted_iron",carrier_kind="ridge_lantern_sill_head_rail",side=side,part="head")]
  for j,y in enumerate([-27.+i*6. for i in range(10)]):ms.append(box(f"ridge_lantern_{side}_post_{j}",(x0,x1,y-.06,y+.06,15.12,16.38),"sticker_iron","painted_iron",carrier_kind="ridge_lantern_frame_post",side=side,seam=j))
  for i in range(9):
   ya=-27+i*6.;yb=ya+6.;v=[[x,ya+.08,15.14],[x,yb-.08,15.14],[x,yb-.08,16.36],[x,ya+.08,16.36]]
   if side=="left":v=list(reversed(v))
   ms.append(plane(f"ridge_lantern_{side}_glass_{i}",v,"sticker_roof_glass","physical_glass",carrier_kind="ridge_lantern_glass",side=side,panel=i,exterior_normal=norm,exposed_between_frames=True))
 # Constrained rear lower wall plus complete upper iron/glass fan and roof closure.
 ms += [box("rear_wall_left",(X0+.35,-3.0,Y1-.62,Y1,.18,8.0),"sticker_rear_brick","red_brick",carrier_kind="constrained_rear_wall",side="rear"),box("rear_wall_right",(3.0,X1-.35,Y1-.62,Y1,.18,8.0),"sticker_rear_brick","red_brick",carrier_kind="constrained_rear_wall",side="rear"),box("rear_service_head",(-3.,3.,Y1-.62,Y1,3.35,8.0),"sticker_rear_brick","red_brick",carrier_kind="constrained_rear_wall",side="rear"),box("rear_service_door",(-2.75,2.75,Y1-.64,Y1-.58,.25,3.25),"sticker_service_door","dark_bronze",carrier_kind="rear_service_door",side="rear")]
 for side,x in (("left",-13.5),("right",13.5)):
  ms += [box(f"rear_{side}_spring_pier",(x-.28,x+.28,Y1-.82,Y1-.62,.18,7.90),"sticker_iron","painted_iron",carrier_kind="rear_spring_pier",side=side,outward_terminal_faces=True),box(f"rear_{side}_spring_capital",(x-.50,x+.50,Y1-.38,Y1,8.00,8.38),"sticker_iron","painted_iron",carrier_kind="rear_spring_capital",side=side,outward_terminal_faces=True,reaches_rear_terminal=True)]
 ms.append(box("rear_fan_spring_sill",(-13.0,13.0,Y1-.38,Y1,8.00,8.38),"sticker_iron","painted_iron",carrier_kind="rear_fan_spring_sill",outward_terminal_faces=True,reaches_rear_terminal=True))
 for i in range(36):ms.append(beam_xz(f"rear_gable_arch_ring_{i}",(xs[i],ellipse_z(xs[i])),(xs[i+1],ellipse_z(xs[i+1])),.30,Y1,Y1+.18,"sticker_iron","painted_iron",carrier_kind="rear_gable_arch_ring",segment=i,outward_terminal_faces=True))
 for i in range(18):
  a,b=fan_x[i],fan_x[i+1];ms.append(plane(f"rear_gable_glass_{i}",[[b-.05,Y1-.29,8.38],[a+.05,Y1-.29,8.38],[a+.05,Y1-.29,ellipse_z(a+.05)-.25],[b-.05,Y1-.29,ellipse_z(b-.05)-.25]],"sticker_roof_glass","physical_glass",carrier_kind="rear_gable_glass",panel=i,exterior_normal=[0,1,0],endpoint_clipped=True))
 # The rear fan is a structural iron-and-glass closure, not a printed upper
 # wall: its mullions and rails sit toward the exterior of the recessed glass.
 for i,x in enumerate(fan_x):ms.append(box(f"rear_gable_mullion_{i}",(x-.035,x+.035,Y1-.24,Y1-.12,8.38,ellipse_z(x)-.20),"sticker_iron","painted_iron",carrier_kind="rear_gable_mullion",member=i,outward_terminal_faces=True))
 for i,z in enumerate((9.45,11.25,13.05)):
  lim=ellipse_x(z)-.18;ms.append(box(f"rear_gable_horizontal_rail_{i}",(-lim,lim,Y1-.24,Y1-.12,z-.045,z+.045),"sticker_iron","painted_iron",carrier_kind="rear_gable_horizontal_rail",rail=i,outward_terminal_faces=True,ellipse_clipped=True))
 g={"archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,"size":"canonical","representation":"fixed_landmark","reference_evidence":REFS,"dimensions":{"width_m":W,"depth_m":D,"occupied_hall_levels":1,"partial_mezzanines":2,"nave_width_m":27.,"aisle_width_m":9.,"spring_m":SPRING_Z,"barrel_crown_m":CROWN_Z,"lantern_crown_m":16.72},"scale_contract":{"canonical":"45x60","fixed_landmark":True,"extended_tier":None,"nonuniform_scale_forbidden":True},"frame_lines":list(FRAME_Y),"apertures":aps,"meshes":ms,"hard_stops":["one_hall_plus_side_mezzanines","binding_27m_nave_9m_aisles","central_nave_open","eight_frame_lines_seven_bays","open_front_cavern_and_open_side_aisle_entries","recessed_panelized_side_shops","three_zone_physical_historic_iron_motif_kit","bay_split_long_eave_clerestories","complete_front_and_rear_iron_glass_fans","physical_iron_structure_lands_at_spring","panelized_real_side_arches","barrel_and_aisle_roofs_close_to_gables","eight_slope_aligned_cut_rooflights","split_closed_ridge_lantern","asymmetric_slate_zinc_aisles","constrained_rear","one_owner_closed_outward"]};g["geometry_sha256"]=digest({k:v for k,v in g.items() if k!="geometry_sha256"});return g
if __name__=="__main__":
 g=build_geometry();print(g["size"],len(g["meshes"]),g["geometry_sha256"])
