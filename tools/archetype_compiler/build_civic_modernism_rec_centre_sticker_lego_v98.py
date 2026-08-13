"""Deterministic clay geometry for the exact Brick-and-Glass Rec Centre refs."""
from __future__ import annotations
import hashlib, json
from typing import Any

ARCHETYPE_ID="civic_modernism_rec_centre"; VARIANT_ID="rec_brick_glass_box"
DEPTH_M=35.0; POOL_WING_M=30.0; GYM_BAY_M=6.25
LOW_TOP_M=9.0; GYM_TOP_M=13.5
SIZE_MATRIX={
 "canonical":{"width_m":55.0,"depth_m":35.0,"gym_bays":4},
 "extended":{"width_m":61.25,"depth_m":35.0,"gym_bays":5},
}
REFERENCE_EVIDENCE=(
 "frontend/public/archetypes/buildings/civic_modernism_rec_centre/variant_0.png",
 "frontend/public/archetypes/buildings/civic_modernism_rec_centre/variant_0_angle_60.jpg",
 "frontend/public/archetypes/buildings/civic_modernism_rec_centre/variant_0_angle_90.jpg",
)

def _hash(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _mesh(name,vertices,faces,owner,domain,**meta):
 roles=meta.pop("face_roles",[domain]*len(faces));assert len(roles)==len(faces)
 return {"name":name,"vertices":vertices,"faces":faces,"face_owners":[[owner] for _ in faces],"sticker_owner_id":owner,"material_domain":domain,"face_roles":roles,**meta}
def _box(name,b,owner,domain,**meta):
 x0,x1,y0,y1,z0,z1=b;v=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
 return _mesh(name,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],owner,domain,closed_box=True,consistent_outward_winding=True,cap_face_indices=[2,3,4,5],**meta)
def _point(side,u,inset,z,w,d):
 if side=="front":return [u,-d/2+inset,z]
 if side=="rear":return [-u,d/2-inset,z]
 if side=="left":return [-w/2+inset,-u,z]
 if side=="right":return [w/2-inset,u,z]
 raise KeyError(side)
def _obox(name,orientation,u0,u1,z0,z1,i0,i1,w,d,owner,domain,**meta):
 v=[_point(orientation,u0,i0,z0,w,d),_point(orientation,u1,i0,z0,w,d),_point(orientation,u1,i1,z0,w,d),_point(orientation,u0,i1,z0,w,d),_point(orientation,u0,i0,z1,w,d),_point(orientation,u1,i0,z1,w,d),_point(orientation,u1,i1,z1,w,d),_point(orientation,u0,i1,z1,w,d)]
 return _mesh(name,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],owner,domain,closed_box=True,consistent_outward_winding=True,cap_face_indices=[2,3,4,5],**meta)

def _glazed_bay(side,bay,u0,u1,z0,z1,w,d,*,entrance=False,evidence="exact"):
 p=f"{side}_{'entrance' if entrance else 'pool_glass'}_{bay:02d}"; inset=.72 if entrance else .56
 meshes=[]; frame=[]
 # Deep concrete reveals own the aperture tunnel.
 for label,a,b,c,e in (("left",u0,u0+.18,z0,z1),("right",u1-.18,u1,z0,z1),("sill",u0+.18,u1-.18,z0,z0+.18),("head",u0+.18,u1-.18,z1-.22,z1)):
  n=f"{p}_{label}_reveal";meshes.append(_obox(n,side,a,b,c,e,0,inset,w,d,f"sticker_{p}_concrete","pale_exposed_concrete",side=side,bay=bay,carrier_kind="deep_opening_reveal",endpoint_role=f"{label}_aperture_boundary"))
 # Exterior terminal caps own the image-visible outer reveal strips.  Pane and
 # card start strictly inside these bounds, so no black backing can leak out.
 terminal_caps=[]
 for label,a,b in (("left",u0,u0+.18),("right",u1-.18,u1)):
  n=f"{p}_{label}_exterior_terminal_cap";terminal_caps.append(n)
  meshes.append(_obox(n,side,a,b,z0,z1,-.045,0,w,d,f"sticker_{p}_terminal_caps","pale_exposed_concrete",side=side,bay=bay,carrier_kind="curtain_wall_exterior_terminal_cap",cap_role=f"outward_{label}_reveal_terminal",fixed_identity=True))
 contour=[(u0+.18,z0+.18),(u1-.18,z0+.18),(u1-.18,z1-.22),(u0+.18,z1-.22)]
 glass=f"{p}_recessed_glass";card=f"{p}_interior_card"
 meshes.append(_mesh(glass,[_point(side,u,inset,z,w,d) for u,z in contour],[list(range(4))],f"sticker_{p}_glass","recessed_glazing",side=side,bay=bay,carrier_kind="recessed_glass"))
 meshes.append(_mesh(card,[_point(side,u,inset+.40,z,w,d) for u,z in contour],[list(range(4))],f"sticker_{p}_interior","interior_card",face_roles=["interior_card"],side=side,bay=bay,occupied=True,behind_glass_m=.40,carrier_kind="recessed_interior_card"))
 for i,ratio in enumerate((.25,.5,.75)):
  u=contour[0][0]+(contour[1][0]-contour[0][0])*ratio;n=f"{p}_mullion_{i}";frame.append(n)
  meshes.append(_obox(n,side,u-.035,u+.035,contour[0][1],contour[2][1],inset-.05,inset-.01,w,d,f"sticker_{p}_aluminum","silver_aluminum",side=side,bay=bay,carrier_kind="physical_mullion"))
 for i,ratio in enumerate((.34,.67)):
  z=contour[0][1]+(contour[2][1]-contour[0][1])*ratio;n=f"{p}_transom_{i}";frame.append(n)
  meshes.append(_obox(n,side,contour[0][0],contour[1][0],z-.035,z+.035,inset-.05,inset-.01,w,d,f"sticker_{p}_aluminum","silver_aluminum",side=side,bay=bay,carrier_kind="physical_mullion"))
 doors=[]
 if entrance:
  c=(u0+u1)/2
  for i,(a,b) in enumerate(((c-1.45,c-.06),(c+.06,c+1.45))):
   assembly=f"{p}_glazed_door_{i}";parts=[]
   for label,du0,du1,dz0,dz1 in (("left_stile",a,a+.065,.22,3.35),("right_stile",b-.065,b,.22,3.35),("bottom_rail",a,b,.22,.36),("top_rail",a,b,3.21,3.35),("door_transom",a+.065,b-.065,2.48,2.57)):
    n=f"{assembly}_{label}";parts.append(n);meshes.append(_obox(n,side,du0,du1,dz0,dz1,inset-.075,inset-.02,w,d,f"sticker_{p}_door_aluminum","silver_aluminum",side=side,bay=bay,carrier_kind="glazed_door_frame",fixed_identity=True,door_leaf=i))
   pane=f"{assembly}_recessed_glass";pane_card=f"{assembly}_lobby_card"
   contour_d=[(a+.075,.37),(b-.075,.37),(b-.075,3.20),(a+.075,3.20)]
   meshes.append(_mesh(pane,[_point(side,u,inset-.01,z,w,d) for u,z in contour_d],[list(range(4))],f"sticker_{p}_door_glass","recessed_glazing",side=side,bay=bay,carrier_kind="glazed_door_pane",fixed_identity=True,door_leaf=i))
   meshes.append(_mesh(pane_card,[_point(side,u,inset+.24,z,w,d) for u,z in contour_d],[list(range(4))],f"sticker_{p}_door_lobby_card","interior_card",face_roles=["interior_card"],side=side,bay=bay,carrier_kind="glazed_door_lobby_card",fixed_identity=True,occupied=True,behind_glass_m=.25,door_leaf=i))
   doors.append({"assembly_id":assembly,"frame_meshes":parts,"glass_mesh":pane,"lobby_card_mesh":pane_card})
 return meshes,{"aperture_id":p,"side":side,"bay":bay,"kind":"entrance" if entrance else "pool_glazing","u_bounds_m":[u0,u1],"glass_u_bounds_m":[contour[0][0],contour[1][0]],"recess_depth_m":inset,"recessed_glass_mesh":glass,"interior_card_mesh":card,"terminal_cap_meshes":terminal_caps,"mullion_meshes":frame,"door_assemblies":doors,"completion_evidence":evidence,"flat_printed_void":False}

def _blind_grid(side,u_min,u_max,bays,z_top,w,d,evidence,*,suppress_first_pier=False,suppress_end_pier=False,trim_start=0.0,trim_end=0.0,name_prefix=None):
 meshes=[]
 prefix=name_prefix or side
 extent=u_max-u_min
 for i in range(bays):
  u0=u_min+i*extent/bays;u1=u_min+(i+1)*extent/bays
  mid=z_top*.48
  for panel,(pz0,pz1) in enumerate(((.35,mid),(mid+.35,z_top-.38))):
   meshes.append(_obox(f"{prefix}_blind_brick_infill_{i:02d}_panel_{panel}",side,u0+.22,u1-.22,pz0,pz1,.28,.48,w,d,f"sticker_{prefix}_blind_brick_{i:02d}","warm_red_brick",side=side,bay=i,panel=panel,carrier_kind="blind_gym_brick_infill",completion_evidence=evidence,grid_zone=prefix))
  if not (i==0 and suppress_first_pier):
   meshes.append(_obox(f"{prefix}_concrete_pier_{i:02d}",side,u0-.13,u0+.22,0,z_top,0,.31,w,d,f"sticker_{prefix}_concrete_grid","pale_exposed_concrete",side=side,bay=i,carrier_kind="exposed_concrete_grid_pier",completion_evidence=evidence,grid_zone=prefix))
 if not suppress_end_pier:
  meshes.append(_obox(f"{prefix}_concrete_end_pier",side,u_max-.22,u_max+.13,0,z_top,0,.31,w,d,f"sticker_{prefix}_concrete_grid","pale_exposed_concrete",side=side,bay=bays,carrier_kind="exposed_concrete_grid_pier",completion_evidence=evidence,grid_zone=prefix))
 for beam,z in enumerate((0.0,z_top*.48,z_top-.38)):
  for bay in range(bays):
   bu0=u_min+bay*extent/bays+.22;bu1=u_min+(bay+1)*extent/bays-.22
   if bay==0:bu0=max(bu0,u_min+trim_start)
   if bay==bays-1:bu1=min(bu1,u_max-trim_end)
   meshes.append(_obox(f"{prefix}_concrete_beam_{beam}_bay_{bay:02d}",side,bu0,bu1,z,z+.35,-.04,.34,w,d,f"sticker_{prefix}_concrete_grid","pale_exposed_concrete",side=side,bay=bay,carrier_kind="exposed_concrete_grid_beam",completion_evidence=evidence,grid_zone=prefix,end_caps_outward=True))
 return meshes

def _opaque_field(side,name,u0,u1,z0,z1,w,d,evidence="exact"):
 return _obox(name,side,u0,u1,z0,z1,0,.44,w,d,f"sticker_{name}","warm_red_brick",side=side,carrier_kind="opaque_envelope_field",completion_evidence=evidence)

def _canopy(w,d,pool_end):
 x0=pool_end-10.0;x1=pool_end+.2;y0=-d/2-5.3;y1=-d/2-.55;z0=4.18;meshes=[]
 top="fixed_entrance_canopy_top";soffit="fixed_entrance_canopy_soffit"
 meshes += [_box(top,(x0,x1,y0,y1,z0+0.28,z0+.42),"sticker_canopy_top","white_painted_steel",carrier_kind="canopy_top",fixed_identity=True),_box(soffit,(x0,x1,y0,y1,z0,z0+.12),"sticker_canopy_soffit","white_painted_steel",carrier_kind="canopy_soffit",fixed_identity=True)]
 fascias=[]
 for label,b in (("front",(x0,x1,y0-.08,y0+.12,z0,z0+.42)),("rear",(x0,x1,y1-.12,y1+.08,z0,z0+.42)),("left",(x0-.08,x0+.12,y0,y1,z0,z0+.42)),("right",(x1-.12,x1+.08,y0,y1,z0,z0+.42))):
  n=f"fixed_entrance_canopy_{label}_fascia";fascias.append(n);meshes.append(_box(n,b,"sticker_canopy_fascia","white_painted_steel",carrier_kind="canopy_fascia",fixed_identity=True))
 ribs=[]
 for i in range(18):
  x=x0+(i+.5)*(x1-x0)/18;n=f"canopy_rib_{i:02d}";ribs.append(n);meshes.append(_box(n,(x-.045,x+.045,y0+.08,y1-.08,z0+.12,z0+.28),"sticker_canopy_ribs","white_painted_steel",carrier_kind="canopy_rib",fixed_identity=True))
 posts=[]
 for i,x in enumerate((x0+.35,x1-.35)):
  n=f"canopy_post_{i}";posts.append(n);meshes.append(_box(n,(x-.07,x+.07,y0+.22,y0+.36,0,z0),"sticker_canopy_posts","white_painted_steel",carrier_kind="canopy_post",fixed_identity=True))
 return meshes,{"top":top,"soffit":soffit,"fascias":fascias,"ribs":ribs,"posts":posts}

def _roofs(w,d,pool_end):
 meshes=[]
 low=_box("low_wing_membrane_roof",(-w/2+.4,pool_end-.4,-d/2+.4,d/2-.4,8.92,9.02),"sticker_low_roof","light_membrane_roof",carrier_kind="low_roof_deck",fixed_identity=True);meshes.append(low)
 gym=_box("high_gym_membrane_roof",(pool_end+.35,w/2-.4,-d/2+.4,d/2-.4,13.42,13.52),"sticker_high_roof","light_membrane_roof",carrier_kind="high_roof_deck",fixed_identity=True);meshes.append(gym)
 parapets=[]
 parapet_corner_caps=[]; endpoint_caps=[]
 for level,z,x0,x1 in (("low",9.0,-w/2,pool_end),("high",13.5,pool_end,w/2)):
  sx0=x0+.34 if level=="low" else x0+.34;sx1=x1-.34 if level=="low" else x1-.34
  runs=[("front",(sx0,sx1,-d/2,-d/2+.34,z,z+.55)),("rear",(sx0,sx1,d/2-.34,d/2,z,z+.55))]
  if level=="low":runs.append(("left",(x0,x0+.34,-d/2+.34,d/2-.34,z,z+.55)))
  else:runs.append(("right",(x1-.34,x1,-d/2+.34,d/2-.34,z,z+.55)))
  for side,b in runs:
   n=f"{level}_{side}_nested_parapet";parapets.append(n);meshes.append(_box(n,b,f"sticker_{n}","pale_exposed_concrete",carrier_kind="nested_roof_parapet",fixed_identity=True))
  outer_x=x0 if level=="low" else x1-.34
  for end,y0,y1 in (("front",-d/2,-d/2+.34),("rear",d/2-.34,d/2)):
   n=f"{level}_{end}_closed_parapet_corner_cap";parapet_corner_caps.append(n)
   meshes.append(_box(n,(outer_x,outer_x+.34,y0,y1,z,z+.55),f"sticker_{n}","pale_exposed_concrete",carrier_kind="closed_parapet_corner_cap",fixed_identity=True,cap_role="outward_parapet_corner"))
  # Inner step ends at the pool/gym junction require their own concrete cap;
  # neither the low nor high straight run crosses this bounded zone.
  inner_x=pool_end-.24 if level=="low" else pool_end+.24
  for end,y0,y1 in (("front",-d/2,-d/2+.34),("rear",d/2-.34,d/2)):
   n=f"{level}_{end}_junction_endpoint_cap";endpoint_caps.append(n)
   meshes.append(_box(n,(inner_x-.10,inner_x+.10,y0,y1,z,z+.55),f"sticker_{n}","pale_exposed_concrete",carrier_kind="roof_junction_endpoint_cap",fixed_identity=True,cap_role=f"outward_{level}_{end}_roof_endpoint"))
 rooflights=[]
 for i,(x,y) in enumerate(((pool_end-8.0,-1.2),(pool_end-3.0,-1.2))):
  curb=f"rooflight_{i}_curb";pane=f"rooflight_{i}_glass";rooflights.append({"curb":curb,"glass":pane})
  meshes.append(_box(curb,(x-1.45,x+1.45,y-.68,y+.68,9.02,9.35),f"sticker_{curb}","silver_aluminum",carrier_kind="rooflight_curb",fixed_identity=True))
  meshes.append(_box(pane,(x-1.30,x+1.30,y-.54,y+.54,9.35,9.43),f"sticker_{pane}","rooflight_glass",carrier_kind="rooflight_glass",fixed_identity=True))
 px,py=pool_end-13.0,2.0;curb="small_pyramidal_rooflight_curb";glass="small_pyramidal_rooflight_glass"
 meshes.append(_box(curb,(px-.72,px+.72,py-.72,py+.72,9.02,9.28),f"sticker_{curb}","silver_aluminum",carrier_kind="pyramidal_rooflight_curb",fixed_identity=True))
 pv=[[px-.62,py-.62,9.28],[px+.62,py-.62,9.28],[px+.62,py+.62,9.28],[px-.62,py+.62,9.28],[px,py,10.12]];pf=[[0,1,4],[1,2,4],[2,3,4],[3,0,4],[0,3,2,1]]
 meshes.append(_mesh(glass,pv,pf,f"sticker_{glass}","rooflight_glass",carrier_kind="closed_pyramidal_rooflight_glass",fixed_identity=True,watertight=True,outward_winding=True))
 ladder=[];lx=pool_end+.32;ly=7.0
 for i,y in enumerate((ly-.38,ly+.38)):
  n=f"gym_access_ladder_rail_{i}";ladder.append(n);meshes.append(_box(n,(lx-.12,lx+.12,y-.035,y+.035,9.20,13.22),f"sticker_{n}","galvanized_metal",carrier_kind="access_ladder_rail",fixed_identity=True))
 for i in range(9):
  z=9.50+i*.40;n=f"gym_access_ladder_rung_{i:02d}";ladder.append(n);meshes.append(_box(n,(lx-.14,lx+.14,ly-.38,ly+.38,z-.035,z+.035),f"sticker_{n}","galvanized_metal",carrier_kind="access_ladder_rung",fixed_identity=True))
 # Bounded open mechanical well on low rear roof with walls, visible equipment and open sky.
 mx0,mx1=-w/2+8.0,pool_end-7.0;my0,my1=4.0,12.5;well=[]
 for label,b in (("front",(mx0+.28,mx1-.28,my0,my0+.28,9.02,10.55)),("rear",(mx0+.28,mx1-.28,my1-.28,my1,9.02,10.55)),("left",(mx0,mx0+.28,my0+.28,my1-.28,9.02,10.55)),("right",(mx1-.28,mx1,my0+.28,my1-.28,9.02,10.55))):
  n=f"mechanical_well_{label}_wall";well.append(n);meshes.append(_box(n,b,f"sticker_{n}","warm_red_brick",carrier_kind="open_mechanical_well_wall",fixed_identity=True))
 well_caps=[]
 for corner,x0,x1,y0,y1 in (("front_left",mx0,mx0+.28,my0,my0+.28),("front_right",mx1-.28,mx1,my0,my0+.28),("rear_left",mx0,mx0+.28,my1-.28,my1),("rear_right",mx1-.28,mx1,my1-.28,my1)):
  n=f"mechanical_well_{corner}_closed_corner_cap";well_caps.append(n);meshes.append(_box(n,(x0,x1,y0,y1,9.02,10.55),f"sticker_{n}","warm_red_brick",carrier_kind="closed_mechanical_well_corner_cap",fixed_identity=True,cap_role="outward_mechanical_corner"))
 equip=[]
 for i,(x,y,sx,sy,h) in enumerate(((mx0+2.0,my0+2.0,1.4,1.0,.9),(mx0+5.2,my0+2.2,1.8,1.2,1.2),(mx0+3.5,my0+5.4,1.2,1.4,.75))):
  n=f"mechanical_equipment_{i}";equip.append(n);meshes.append(_box(n,(x-sx/2,x+sx/2,y-sy/2,y+sy/2,9.06,9.06+h),f"sticker_{n}","galvanized_mechanical",carrier_kind="mechanical_equipment",fixed_identity=True))
 return meshes,{"low_deck":"low_wing_membrane_roof","high_deck":"high_gym_membrane_roof","parapets":parapets,"parapet_corner_caps":parapet_corner_caps,"junction_endpoint_caps":endpoint_caps,"rooflights":rooflights,"small_pyramidal_rooflight":{"curb":curb,"glass":glass},"gym_access_ladder_meshes":ladder,"mechanical_well_walls":well,"mechanical_well_corner_caps":well_caps,"mechanical_equipment":equip,"mechanical_well_open_to_sky":True,"mechanical_bounds_xy_m":[mx0,mx1,my0,my1]}

def build_geometry(size="canonical"):
 if size not in SIZE_MATRIX:raise KeyError(size)
 s=SIZE_MATRIX[size];w=float(s["width_m"]);d=float(s["depth_m"]);gym_bays=int(s["gym_bays"]);pool_end=-w/2+POOL_WING_M
 meshes=[];apertures=[]
 # One dominant pool curtain wall plus a separate recessed junction entrance.
 gm,a=_glazed_bay("front",0,-w/2,-w/2+12.5,.15,8.72,w,d);meshes+=gm;apertures.append(a)
 meshes.append(_opaque_field("front","front_pool_brick_field",-w/2+12.5,pool_end-10,.15,8.72,w,d))
 gm,a=_glazed_bay("front",4,pool_end-10,pool_end,.15,8.72,w,d,entrance=True);meshes+=gm;apertures.append(a)
 gm,a=_glazed_bay("left",0,-d/2,-d/2+7,.15,8.72,w,d);meshes+=gm;apertures.append(a)
 gm,a=_glazed_bay("left",1,-d/2+7,-d/2+14,.15,4.25,w,d);meshes+=gm;apertures.append(a)
 meshes.append(_opaque_field("left","left_return_upper_brick_field",-d/2+7,-d/2+14,4.25,8.72,w,d))
 meshes.append(_opaque_field("left","left_return_rear_brick_field",-d/2+14,d/2,.15,8.72,w,d,"constrained"))
 # Blind gym occupies right-hand stepped mass; rear is intentionally constrained.
 gym_width=w/2-pool_end
 meshes+=_blind_grid("front",pool_end,w/2,gym_bays,GYM_TOP_M,w,d,"exact",suppress_first_pier=True,trim_start=.24)
 meshes+=_blind_grid("right",-d/2,d/2,7,GYM_TOP_M,w,d,"exact")
 # Rear u is negated world x: gym is u=-w/2..-pool_end; low wing is
 # u=-pool_end..w/2.  The seam alone owns their structural junction.
 meshes+=_blind_grid("rear",-w/2,-pool_end,gym_bays,GYM_TOP_M,w,d,"constrained",suppress_end_pier=True,trim_end=.24)
 meshes+=_blind_grid("rear",-pool_end,w/2,6,LOW_TOP_M,w,d,"constrained",suppress_first_pier=True,trim_start=.24,name_prefix="rear_low")
 # Localized front/rear junction frame, not a full-depth occluding slab.
 junction=[]
 for side,y0,y1 in (("front",-d/2,-d/2+.55),("rear",d/2-.55,d/2)):
  pier=f"pool_gym_{side}_junction_pier";beam=f"pool_gym_{side}_junction_beam"
  junction.extend([pier,beam])
  meshes.append(_box(pier,(pool_end-.24,pool_end+.24,y0,y1,0,GYM_TOP_M),f"sticker_{pier}","pale_exposed_concrete",carrier_kind="localized_massing_junction_pier",fixed_identity=True,junction_side=side))
  meshes.append(_box(beam,(pool_end-.24,pool_end+.52,y0,y1,LOW_TOP_M-.22,LOW_TOP_M+.22),f"sticker_{beam}","pale_exposed_concrete",carrier_kind="localized_massing_junction_beam",fixed_identity=True,junction_side=side))
  cap=f"pool_gym_{side}_junction_beam_outward_cap";junction.append(cap)
  # Cap is just outside the beam end and owns the previously black terminal.
  cap_y0,cap_y1=(y0-.08,y0) if side=="front" else (y1,y1+.08)
  meshes.append(_box(cap,(pool_end-.24,pool_end+.52,cap_y0,cap_y1,LOW_TOP_M-.22,LOW_TOP_M+.22),f"sticker_{cap}","pale_exposed_concrete",carrier_kind="junction_beam_outward_terminal_cap",fixed_identity=True,cap_role=f"outward_{side}_junction_beam"))
 # The raised gym wall exposed above the low wing is warm brick with a pale
 # coping. It begins behind the front junction and ends before the rear one.
 stepped_wall="exposed_inner_gym_stepped_brick_wall";stepped_coping="exposed_inner_gym_wall_pale_coping"
 meshes.append(_box(stepped_wall,(pool_end+.24,pool_end+.58,-d/2+.55,d/2-.55,LOW_TOP_M,GYM_TOP_M),f"sticker_{stepped_wall}","warm_red_brick",carrier_kind="exposed_stepped_inner_gym_wall",fixed_identity=True))
 meshes.append(_box(stepped_coping,(pool_end+.18,pool_end+.64,-d/2+.55,d/2-.55,GYM_TOP_M,GYM_TOP_M+.16),f"sticker_{stepped_coping}","pale_exposed_concrete",carrier_kind="inner_gym_wall_coping",fixed_identity=True))
 step_wedge="central_low_high_roof_step_closed_wedge";step_cap="central_low_high_roof_step_pale_terminal_cap"
 meshes.append(_box(step_wedge,(pool_end-.24,pool_end+.24,-.42,.42,LOW_TOP_M+.55,GYM_TOP_M),f"sticker_{step_wedge}","warm_red_brick",carrier_kind="closed_roof_step_wedge",fixed_identity=True))
 meshes.append(_box(step_cap,(pool_end-.29,pool_end+.29,-.47,.47,GYM_TOP_M,GYM_TOP_M+.16),f"sticker_{step_cap}","pale_exposed_concrete",carrier_kind="roof_step_terminal_cap",fixed_identity=True,cap_role="outward_central_roof_step"))
 cm,canopy=_canopy(w,d,pool_end);meshes+=cm
 rm,roof=_roofs(w,d,pool_end);meshes+=rm
 g={"archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,"size":size,"reference_evidence":list(REFERENCE_EVIDENCE),"identity_mode":"massing_graph",
    "dimensions":{"width_m":w,"depth_m":d,"low_wing_top_m":LOW_TOP_M,"gym_hall_top_m":GYM_TOP_M},
    "massing":{"pool_public_wing":{"width_m":POOL_WING_M,"height_m":LOW_TOP_M,"fixed":True},"blind_gym_hall":{"width_m":gym_width,"height_m":GYM_TOP_M,"whole_bays":gym_bays}},
    "structural_grid":{"gym_bay_m":GYM_BAY_M,"gym_bays":gym_bays,"gym_front_u_range_m":[pool_end,w/2],"dominant_pool_curtain_walls":1,"fixed_entrance_bays":1},
    "fixed_modules":{"entrances":1,"pool_wings":1,"canopies":1,"roof_kits":1,"long_rooflights":2,"small_pyramidal_rooflights":1,"gym_access_ladders":1,"mechanical_wells":1},
    "apertures":apertures,"canopy":canopy,"roof":roof,"massing_junction":{"pier_beam_meshes":junction,"stepped_brick_wall_mesh":stepped_wall,"coping_mesh":stepped_coping,"central_step_wedge_mesh":step_wedge,"central_step_cap_mesh":step_cap},"meshes":meshes,
    "completion_policy":{"rear":"constrained_fully_covered_no_invented_public_entrance"},
    "geometry_hard_stops":["canonical_footprint_must_equal_55x35","depth_must_equal_35","low_pool_wing_and_tall_blind_gym_must_remain_stepped","extended_tier_adds_exactly_one_complete_6_25m_blind_gym_bay","pool_wing_entrance_canopy_and_roof_kit_are_fixed","entrance_count_must_equal_1","all_glazing_requires_deep_reveals_physical_mullions_recessed_glass_and_interior_cards","canopy_requires_top_fascias_soffit_ribs_and_posts","roof_schedule_requires_exactly_2_long_plus_1_pyramidal_rooflights","mechanical_well_must_remain_bounded_and_open_to_sky","rear_completion_must_not_invent_public_entry","pool_gym_seam_must_be_single_non_overlapping_structural_owner","every_visible_face_requires_exactly_one_sticker_owner"]}
 g["geometry_sha256"]=_hash({k:v for k,v in g.items() if k!="geometry_sha256"});return g

if __name__=="__main__":
 for t in SIZE_MATRIX:
  g=build_geometry(t);print(t,len(g["meshes"]),g["geometry_sha256"])
