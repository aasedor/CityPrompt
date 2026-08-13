"""Deterministic clay geometry for the industrial tilt-up concrete family."""
from __future__ import annotations
import hashlib,json
from typing import Any

ARCHETYPE_ID="industrial_park_modernism";VARIANT_ID="industrial_tilt_up_concrete"
W=60.;FRONT_Y=-21.;SIZES={"canonical":42.,"extended":48.}
REFS=[f"frontend/public/archetypes/buildings/industrial_park_modernism/variant_0{x}" for x in (".png","_angle_60.jpg","_angle_90.jpg")]
def digest(v:Any):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def mesh(n,v,f,o,d,**m):return {"name":n,"vertices":v,"faces":f,"face_owners":[[o] for _ in f],"sticker_owner_id":o,"material_domain":d,"face_roles":[d]*len(f),**m}
def box(n,b,o,d,**m):
 x0,x1,y0,y1,z0,z1=b;v=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
 return mesh(n,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],o,d,closed=True,outward_winding=True,cap_faces=[2,3,4,5],**m)
def plane(n,verts,o,d,**m):return mesh(n,verts,[list(range(len(verts)))],o,d,**m)
def opaque_door(ms,name,bounds,side,kind,**meta):
 x0,x1,y0,y1,z0,z1=bounds
 if side=="right":
  reveals=[box(name+"_reveal_front",(x0,x1,y0,y0+.16,z0,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_rear",(x0,x1,y1-.16,y1,z0,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_head",(x0,x1,y0+.16,y1-.16,z1-.16,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta)]
  d=plane(name+"_ribbed_door",[[x0,y0+.16,z0],[x0,y1-.16,z0],[x0,y1-.16,z1-.16],[x0,y0+.16,z1-.16]],"sticker_"+name+"_door","ribbed_overhead_door",carrier_kind="opaque_ribbed_door_plane",side=side,recessed_inward=True,**meta)
 else:
  reveals=[box(name+"_reveal_left",(x0,x0+.16,y0,y1,z0,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_right",(x1-.16,x1,y0,y1,z0,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_head",(x0+.16,x1-.16,y0,y1,z1-.16,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta)]
  # Clockwise in X/Z when viewed from outside produces a +Y exterior normal.
  d=plane(name+"_ribbed_door",[[x0+.16,y0,z0],[x0+.16,y0,z1-.16],[x1-.16,y0,z1-.16],[x1-.16,y0,z0]],"sticker_"+name+"_door","ribbed_overhead_door",carrier_kind="opaque_ribbed_door_plane",side=side,recessed_inward=True,exterior_normal=[0,1,0],**meta)
 ms+=reveals+[d];return {"name":name,"kind":kind,"side":side,"reveals":[m["name"] for m in reveals],"door_plane":d["name"],**meta}
def aperture(ms,name,bounds,side,kind,**meta):
 x0,x1,y0,y1,z0,z1=bounds
 if side in {"front","rear"}:
  exterior=y0;glass_y=y1;card_y=y1+(.30 if side=="front" else -.30)
  reveal=[box(name+"_reveal_left",(x0,x0+.16,y0,y1,z0,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_right",(x1-.16,x1,y0,y1,z0,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_head",(x0+.16,x1-.16,y0,y1,z1-.16,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_sill",(x0+.16,x1-.16,y0,y1,z0,z0+.16),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta)]
  gl=plane(name+"_glass",[[x0+.16,glass_y,z0+.16],[x1-.16,glass_y,z0+.16],[x1-.16,glass_y,z1-.16],[x0+.16,glass_y,z1-.16]],"sticker_"+name+"_glass","recessed_glazing",carrier_kind="recessed_glass",side=side,**meta)
  card=plane(name+"_card",[[x0+.16,card_y,z0+.16],[x1-.16,card_y,z0+.16],[x1-.16,card_y,z1-.16],[x0+.16,card_y,z1-.16]],"sticker_"+name+"_card","interior_card",carrier_kind="recessed_interior_card",side=side,**meta)
 else:
  exterior=x1;glass_x=x0;card_x=x0-.30
  reveal=[box(name+"_reveal_front",(x0,x1,y0,y0+.16,z0,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_rear",(x0,x1,y1-.16,y1,z0,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_head",(x0,x1,y0+.16,y1-.16,z1-.16,z1),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta),box(name+"_reveal_sill",(x0,x1,y0+.16,y1-.16,z0,z0+.16),"sticker_reveal","concrete_return",carrier_kind="opening_reveal",side=side,**meta)]
  gl=plane(name+"_glass",[[glass_x,y0+.16,z0+.16],[glass_x,y1-.16,z0+.16],[glass_x,y1-.16,z1-.16],[glass_x,y0+.16,z1-.16]],"sticker_"+name+"_glass","recessed_glazing",carrier_kind="recessed_glass",side=side,**meta)
  card=plane(name+"_card",[[card_x,y0+.16,z0+.16],[card_x,y1-.16,z0+.16],[card_x,y1-.16,z1-.16],[card_x,y0+.16,z1-.16]],"sticker_"+name+"_card","interior_card",carrier_kind="recessed_interior_card",side=side,**meta)
 ms += reveal+[gl,card];return {"name":name,"kind":kind,"side":side,"reveals":[m["name"] for m in reveal],"glass":gl["name"],"card":card["name"],**meta}

def build_geometry(size="canonical"):
 if size not in SIZES:raise KeyError(size)
 depth=SIZES[size];rear=FRONT_Y+depth;ms=[];aps=[]
 # Continuous high-bay shell: slab/roof plus panelized elevations around real openings.
 ms += [box("floor_slab_fixed",(-30,30,FRONT_Y,21.,0,.20),"sticker_floor","industrial_slab",carrier_kind="fixed_floor_slab",uv_scale_m=1.)]
 if size=="extended":ms.append(box("floor_slab_rear_depth_module",(-30,30,21.,27.,0,.20),"sticker_floor_module","industrial_slab",carrier_kind="rear_depth_module",module_depth_m=6.,uv_scale_m=1.))
 # Two continuous office ribbons, not isolated punched bays. The lower ribbon
 # is split only by the singular entry; the upper is one uninterrupted band.
 office=[]
 ribbon_schedule=((0,-28.5,-5.0,1.15,4.25,"left_of_entry"),(0,1.4,4.0,1.15,4.25,"right_of_entry"),(1,-28.5,4.0,5.25,8.20,"continuous_upper"))
 for index,(level,x0,x1,z0,z1,role) in enumerate(ribbon_schedule):
  office.append(aperture(ms,f"front_office_ribbon_{index}",(x0,x1,FRONT_Y,FRONT_Y+.38,z0,z1),"front","office_window_ribbon",level=level,ribbon_role=role,continuous_ribbon=True))
  spacing=3.25;count=int((x1-x0)/spacing)
  for j in range(1,count+1):
   xx=x0+(x1-x0)*j/(count+1);ms.append(box(f"front_office_ribbon_{index}_mullion_{j}",(xx-.025,xx+.025,FRONT_Y+.36,FRONT_Y+.42,z0+.16,z1-.16),"sticker_office_mullion","dark_metal",carrier_kind="office_window_mullion",level=level,ribbon=index,mullion=j))
 # Singular recessed entrance, paired doors and interior card.
 entry=aperture(ms,"fixed_recessed_entrance",(-4.6,1.0,FRONT_Y,FRONT_Y+.90,.2,4.45),"front","entrance",fixed=True)
 for j,(a,b) in enumerate(((-3.95,-1.95),(-1.65,.35))):
  for label,bb in (("left",(a,a+.07,FRONT_Y+.86,FRONT_Y+.96,.35,3.75)),("right",(b-.07,b,FRONT_Y+.86,FRONT_Y+.96,.35,3.75)),("bottom",(a+.07,b-.07,FRONT_Y+.86,FRONT_Y+.96,.35,.45)),("top",(a+.07,b-.07,FRONT_Y+.86,FRONT_Y+.96,3.65,3.75)),("transom",(a+.07,b-.07,FRONT_Y+.86,FRONT_Y+.96,2.95,3.04))):ms.append(box(f"entrance_door_{j}_{label}",bb,"sticker_entry_frame","dark_metal",carrier_kind="slim_entry_frame_member",door=j,member=label))
  ms.append(plane(f"entrance_door_{j}_pane",[[a+.07,FRONT_Y+.98,.45],[b-.07,FRONT_Y+.98,.45],[b-.07,FRONT_Y+.98,3.65],[a+.07,FRONT_Y+.98,3.65]],"sticker_entry_door_glass","recessed_glazing",carrier_kind="entry_door_pane",door=j))
 # Front concrete panels fill every opaque field, never behind a pane/entry.
 front_panels=[]
 def add_front(name,a,b,z0,z1,kind="tilt_up_panel",**meta):
  if b-a<=1e-6:return
  q="front_panel_"+name;front_panels.append(q);ms.append(box(q,(a,b,FRONT_Y,FRONT_Y+.30,z0,z1),"sticker_front_concrete","tilt_up_concrete",carrier_kind=kind,side="front",**meta))
 def gaps(lo,hi,voids):
  out=[];cursor=lo
  for a,b in sorted(voids):
   if a>cursor:out.append((cursor,a))
   cursor=max(cursor,b)
  if cursor<hi:out.append((cursor,hi))
  return out
 level0=[(-28.5,-5.0),(-4.6,1.),(1.4,4.0)]
 level1=[(-28.5,4.0)]
 for i,(a,b) in enumerate(gaps(-30,17.8,[(-4.6,1.)])):add_front(f"base_{i}",a,b,.2,1.15)
 for i,(a,b) in enumerate(gaps(-30,17.8,level0)):add_front(f"office_l0_pier_{i}",a,b,1.15,4.25,"office_opaque_pier_field",level=0,pier=i)
 for i,(a,b) in enumerate(gaps(-30,17.8,[(-4.6,1.)])):add_front(f"entry_head_{i}",a,b,4.25,4.45)
 add_front("middle_band",-30,17.8,4.45,5.25)
 for i,(a,b) in enumerate(gaps(-30,17.8,level1)):add_front(f"office_l1_pier_{i}",a,b,5.25,8.2,"office_opaque_pier_field",level=1,pier=i)
 add_front("head",-30,17.8,8.2,11.1);add_front("blind_right",28.2,30,.2,11.1)
 # 7m supported canopy: slab meets posts only at z boundary; dedicated end caps.
 canopy=[]
 canopy.append(box("entrance_canopy_slab",(-5.22,1.62,FRONT_Y-3.5,FRONT_Y-.08,4.50,4.68),"sticker_canopy","metal_canopy",carrier_kind="supported_canopy_slab",fixed=True))
 for j,x in enumerate((-4.9,1.3)):canopy.append(box(f"entrance_canopy_post_{j}",(x-.09,x+.09,FRONT_Y-3.18,FRONT_Y-3.00,.2,4.50),"sticker_canopy_post","dark_metal",carrier_kind="canopy_post",fixed=True))
 for side,a,b in (("left",-5.3,-5.22),("right",1.62,1.7)):canopy.append(box(f"entrance_canopy_{side}_cap",(a,b,FRONT_Y-3.5,FRONT_Y-.08,4.50,4.68),"sticker_canopy_cap","metal_canopy",carrier_kind="adjacent_finish_endpoint_cap",assembly="canopy",outward_terminal_faces=True))
 ms+=canopy
 # Singular raised blind pylon and long, physically open roofline screen.
 pylon=box("fixed_front_right_pylon",(17.8,28.2,FRONT_Y-.20,FRONT_Y+.42,.2,13.35),"sticker_pylon","tilt_up_concrete",carrier_kind="raised_blind_pylon",fixed=True,raise_above_shell_m=2.25);ms.append(pylon)
 slots=[]
 backing=plane("roofline_openwork_dark_backing",[[-29.3,FRONT_Y-.055,9.05],[17.55,FRONT_Y-.055,9.05],[17.55,FRONT_Y-.055,11.58],[-29.3,FRONT_Y-.055,11.58]],"sticker_openwork_backing","dark_recess",carrier_kind="openwork_screen_backing",bounded_before_pylon=True);ms.append(backing)
 fin_count=85
 for i in range(fin_count):
  x=-29.25+i*(46.7/(fin_count-1));q=f"roofline_openwork_fin_{i}";slots.append(q);ms.append(box(q,(x-.025,x+.025,FRONT_Y-.18,FRONT_Y-.08,9.05,11.58),"sticker_openwork_fin","dark_metal",carrier_kind="vertical_openwork_fin",fin=i,bounded_before_pylon=True,visible_above_shell_m=.48))
 coping=box("roofline_openwork_top_coping",(-29.3,17.55,FRONT_Y-.18,FRONT_Y-.08,11.58,11.70),"sticker_openwork_coping","dark_metal",carrier_kind="openwork_top_coping",bounded_before_pylon=True,outward_terminal_faces=True);ms.append(coping)
 # Left wall is constrained panel construction; right return owns exactly six loading doors.
 ms.append(box("left_wall_fixed",(-30,-29.70,FRONT_Y+.30,20.7,.2,11.1),"sticker_left_concrete","tilt_up_concrete",carrier_kind="fixed_side_wall",side="left",uv_scale_m=1.))
 if size=="extended":ms.append(box("left_wall_rear_depth_module",(-30,-29.70,20.7,26.7,.2,11.1),"sticker_left_module","tilt_up_concrete",carrier_kind="rear_depth_module",side="left",module_depth_m=6.,uv_scale_m=1.))
 loading=[];door_centres=(-14,-8,-2,4,10,16)
 for i,cy in enumerate(door_centres):
  loading.append(opaque_door(ms,f"right_loading_door_{i}",(29.55,30.,cy-2.05,cy+2.05,.2,4.75),"right","overhead_door",door=i,fixed=True))
  for j,y in enumerate((cy-2.35,cy+2.35)):ms.append(box(f"right_loading_door_{i}_bollard_{j}",(30.02,30.20,y-.09,y+.09,.2,1.35),"sticker_safety_yellow","safety_yellow",carrier_kind="loading_bollard",door=i,pair=j,exterior_clearance_m=.02))
 # Right wall panels occupy door gaps only; no shell exists behind apertures.
 edges=[FRONT_Y+.3]+[v for c in door_centres for v in (c-2.05,c+2.05)]+[20.7]
 edges=sorted(set(max(FRONT_Y+.3,min(20.7,v)) for v in edges))
 for i,(a,b) in enumerate(zip(edges,edges[1:])):
  if b-a>.20 and not any(a>=c-2.05-.01 and b<=c+2.05+.01 for c in door_centres):ms.append(box(f"right_wall_panel_{i}",(29.70,30.,a,b,.2,11.1),"sticker_right_concrete","tilt_up_concrete",carrier_kind="tilt_up_panel",side="right"))
 for i,cy in enumerate(door_centres):ms.append(box(f"right_loading_door_{i}_concrete_head",(29.70,30.,cy-2.05,cy+2.05,4.75,11.1),"sticker_right_concrete","tilt_up_concrete",carrier_kind="loading_door_concrete_head",side="right",door=i))
 if size=="extended":ms.append(box("right_wall_rear_depth_module",(29.70,30.,20.7,26.7,.2,11.1),"sticker_right_module","tilt_up_concrete",carrier_kind="rear_depth_module",side="right",module_depth_m=6.,uv_scale_m=1.))
 # Three constrained rear receiving positions, translated with the rear wall.
 receiving=[]
 for i,cx in enumerate((-18,0,18)):receiving.append(opaque_door(ms,f"rear_receiving_{i}",(cx-3,cx+3,rear-.50,rear,.2,4.45),"rear","receiving_door",position=i,fixed_count=True,terminal_translated_m=depth-42))
 for i,(a,b) in enumerate(((-30,-21),(-15,-3),(3,15),(21,30))):ms.append(box(f"rear_panel_{i}",(a,b,rear-.30,rear,.2,11.1),"sticker_rear_concrete","tilt_up_concrete",carrier_kind="tilt_up_panel",side="rear"))
 for i,cx in enumerate((-18,0,18)):ms.append(box(f"rear_receiving_{i}_concrete_head",(cx-3,cx+3,rear-.30,rear,4.45,11.1),"sticker_rear_concrete","tilt_up_concrete",carrier_kind="receiving_door_concrete_head",side="rear",position=i,terminal_translated_m=depth-42))
 # Roof parapet runs use dedicated closed corner caps; no run overlaps a corner.
 parapets=[]
 for n,b in (("front_left",(-29.75,17.72,FRONT_Y,FRONT_Y+.22,11.1,11.75)),("front_right",(28.28,29.75,FRONT_Y,FRONT_Y+.22,11.1,11.75)),("rear",(-29.75,29.75,rear-.22,rear,11.1,11.75)),("left_fixed",(-30,-29.78,FRONT_Y+.25,20.75,11.1,11.75)),("right_fixed",(29.78,30,FRONT_Y+.25,20.75,11.1,11.75))):
  q=f"roof_parapet_{n}_run";parapets.append(q);ms.append(box(q,b,"sticker_parapet","tilt_up_concrete",carrier_kind="parapet_run",side=n,shortened_for_caps=True))
 if size=="extended":
  for side,x0,x1 in (("left",-30,-29.78),("right",29.78,30)):
   q=f"roof_parapet_{side}_rear_depth_module";parapets.append(q);ms.append(box(q,(x0,x1,20.75,26.75,11.1,11.75),"sticker_parapet_module","tilt_up_concrete",carrier_kind="rear_depth_module",module_depth_m=6.,uv_scale_m=1.,assembly="parapet"))
 for sx,x in (("left",-30),("right",29.75)):
  for sy,y in (("front",FRONT_Y),("rear",rear-.25)):
   q=f"roof_parapet_{sx}_{sy}_corner_cap";parapets.append(q);ms.append(box(q,(x,x+.25,y,y+.25,11.1,11.75),"sticker_parapet_cap","tilt_up_concrete",carrier_kind="adjacent_finish_endpoint_cap",assembly="parapet",outward_terminal_faces=True))
 # Pylon gap in front parapet/TPO has its own terminal caps.
 for side,a,b in (("left",17.72,17.80),("right",28.20,28.28)):
  q=f"front_parapet_pylon_{side}_cap";parapets.append(q);ms.append(box(q,(a,b,FRONT_Y,FRONT_Y+.22,11.1,11.75),"sticker_parapet_cap","tilt_up_concrete",carrier_kind="adjacent_finish_endpoint_cap",assembly="pylon_parapet",outward_terminal_faces=True))
 # Fixed roof field plus a discrete 6m module and translated terminal strip.
 ms.append(box("tpo_roof_fixed_main",(-29.7,29.7,FRONT_Y+.42,20.7,11.10,11.28),"sticker_tpo_roof","tpo_roof",carrier_kind="fixed_tpo_roof",uv_scale_m=1.))
 ms.append(box("tpo_roof_fixed_front_left",(-29.7,17.8,FRONT_Y+.3,FRONT_Y+.42,11.10,11.28),"sticker_tpo_roof","tpo_roof",carrier_kind="fixed_tpo_roof",uv_scale_m=1.,pylon_gap=True))
 ms.append(box("tpo_roof_fixed_front_right",(28.2,29.7,FRONT_Y+.3,FRONT_Y+.42,11.10,11.28),"sticker_tpo_roof","tpo_roof",carrier_kind="fixed_tpo_roof",uv_scale_m=1.,pylon_gap=True))
 if size=="extended":ms.append(box("tpo_roof_rear_depth_module",(-29.7,29.7,20.7,26.7,11.10,11.28),"sticker_tpo_module","tpo_roof",carrier_kind="rear_depth_module",module_depth_m=6.,uv_scale_m=1.))
 # Fixed bounded roof kit: exactly 2 RTUs, 3 low rooflights and sparse vents.
 roofkit=[]
 for i,(x,y) in enumerate(((-12,-2),(10,8))):q=f"roof_rtu_{i}";roofkit.append(q);ms.append(box(q,(x-2,x+2,y-1.5,y+1.5,11.28,12.75),"sticker_rtu","roof_equipment",carrier_kind="roof_rtu",fixed=True))
 for i,(x,y) in enumerate(((-14,8),(0,-4),(14,-8))):
  q=f"low_rooflight_{i}";parts=[]
  for label,b in (("front",(x-1.9,x+1.9,y-.75,y-.65,11.28,11.48)),("rear",(x-1.9,x+1.9,y+.65,y+.75,11.28,11.48)),("left",(x-1.9,x-1.8,y-.65,y+.65,11.28,11.48)),("right",(x+1.8,x+1.9,y-.65,y+.65,11.28,11.48))):
   n=f"{q}_curb_{label}";parts.append(n);ms.append(box(n,b,"sticker_rooflight_curb","roof_curb",carrier_kind="rooflight_curb",rooflight=i,side=label))
  top=plane(q+"_top_glass",[[x-1.8,y-.65,11.43],[x+1.8,y-.65,11.43],[x+1.8,y+.65,11.43],[x-1.8,y+.65,11.43]],"sticker_rooflight_glass","rooflight_glass",carrier_kind="recessed_rooflight_top_glass",rooflight=i,fixed=True);ms.append(top);roofkit += parts+[top["name"]]
 for i,(x,y) in enumerate(((-22,2),(22,3),(3,14))):q=f"sparse_roof_vent_{i}";roofkit.append(q);ms.append(box(q,(x-.18,x+.18,y-.18,y+.18,11.28,11.92),"sticker_roof_vent","galvanized_metal",carrier_kind="sparse_roof_vent",fixed=True))
 # Physical recessed panel joints are clipped to opaque front/rear fields only.
 joints=[]
 # Front joints exist only in opaque head/band zones, never through office/entry.
 for i,x in enumerate(range(-20,21,10)):
  for segment,z0,z1 in (("middle",4.45,5.25),("head",8.2,11.1)):
   q=f"front_panel_joint_{i}_{segment}";joints.append(q);ms.append(plane(q,[[x-.025,FRONT_Y-.011,z0],[x+.025,FRONT_Y-.011,z0],[x+.025,FRONT_Y-.011,z1],[x-.025,FRONT_Y-.011,z1]],"sticker_panel_joint","joint_recess",carrier_kind="physical_panel_joint_recess",side="front",opaque_segment=segment))
 # Rear joints stop at door heads and resume only above them.
 for i,x in enumerate(range(-20,21,10)):
  q=f"rear_panel_joint_{i}_head";joints.append(q);ms.append(plane(q,[[x-.025,rear+.011,4.45],[x+.025,rear+.011,4.45],[x+.025,rear+.011,11.1],[x-.025,rear+.011,11.1]],"sticker_panel_joint","joint_recess",carrier_kind="physical_panel_joint_recess",side="rear",opaque_segment="head"))
 g={"archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,"size":size,"reference_evidence":REFS,"dimensions":{"width_m":W,"depth_m":depth,"shell_height_m":11.1,"office_storeys":2},"scale_contract":{"canonical":"60x42","extended":"60x48","extension":"one complete 6m rear operational depth bay","front_fixed":True,"loading_count_fixed":6,"roof_kit_fixed":True},"office_frontage_ratio":34/60,"office_windows":office,"entrance":entry,"canopy":[m["name"] for m in canopy],"pylon":pylon["name"],"vertical_slots":slots,"loading_doors":loading,"rear_receiving":receiving,"parapets":parapets,"roof_kit":roofkit,"panel_joints":joints,"meshes":ms,"hard_stops":["one_high_bay_shell","exactly_two_front_office_bands","singular_recessed_entrance_and_supported_canopy","singular_raised_blind_pylon","six_fixed_right_loading_doors_with_bollards","three_rear_receiving_positions","fixed_two_rtu_three_rooflight_kit","no_positive_overlap_at_thin_assembly_terminals"]};g["geometry_sha256"]=digest({k:v for k,v in g.items() if k!="geometry_sha256"});return g
if __name__=="__main__":
 for s in SIZES:
  g=build_geometry(s);print(s,len(g["meshes"]),g["geometry_sha256"])
