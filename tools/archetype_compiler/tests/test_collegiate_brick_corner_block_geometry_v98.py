import importlib.util
from pathlib import Path
import pytest
P=Path(__file__).parents[1]/"build_collegiate_brick_corner_block_sticker_lego_v98.py";S=importlib.util.spec_from_file_location("cb",P);M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
@pytest.fixture(scope="module")
def c():return M.build_geometry("canonical")
@pytest.fixture(scope="module")
def e():return M.build_geometry("extended")
def bounds(m):return tuple(f(v[i] for v in m["vertices"]) for i in range(3) for f in(min,max))
def overlap(a,b):
 x,y=bounds(a),bounds(b);return all(min(x[i+1],y[i+1])-max(x[i],y[i])>1e-8 for i in(0,2,4))
def test_locked_dimensions_datums_and_crown(c,e):
 assert c["dimensions"]=={"width_m":42.,"depth_m":38.,"occupied_storeys":5,"datums_m":[0.,3.8,7.15,10.5,13.85,17.2],"main_coping_m":18.1,"corner_crown_m":18.78}
 assert e["dimensions"]["width_m"]==49. and e["dimensions"]["depth_m"]==38.
 assert e["dimensions"]["occupied_storeys"]==5 and e["dimensions"]["corner_crown_m"]<=18.8
def test_true_open_courtyard_and_full_inner_elevations(c,e):
 for g,width in ((c,14.),(e,21.)):
  assert g["courtyard"]=={"width_m":width,"depth_m":12.,"open_to_sky":True,"bounds":g["courtyard"]["bounds"]}
  assert {a["side"] for a in g["courtyard_apertures"]}=={"court_front","court_rear","court_left","court_right"}
  assert {a["level"] for a in g["courtyard_apertures"]}==set(range(5))
  court=g["courtyard"]["bounds"]
  assert not [m for m in g["meshes"] if m.get("carrier_kind") in {"ring_floor","gravel_roof_field"} and bounds(m)[0]<court[1] and bounds(m)[1]>court[0] and bounds(m)[2]<court[3] and bounds(m)[3]>court[2]]
def test_true_aperture_layers(c,e):
 for g in(c,e):
  all_ap=g["apertures"]+g["courtyard_apertures"]+g["oriel_apertures"]+[g["entry"]]
  named={m["name"]:m for m in g["meshes"]}
  assert all(len(a["returns"])==4 and a["glass"] and a["card"] and a["backing"] for a in all_ap)
  assert all(named[a["glass"]]["material_domain"]=="recessed_glazing" and named[a["card"]]["material_domain"]=="interior_card" and named[a["backing"]]["material_domain"]=="interior_backing" for a in all_ap)
  assert all(len(a["interior_cues"])==4 for a in all_ap)
def test_fixed_corner_oriel_entry_and_no_balconies(c,e):
 for g in(c,e):
  assert len(g["oriel_apertures"])==4*3*2 and {a["level"] for a in g["oriel_apertures"]}=={1,2,3,4}
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="oriel_spandrel_band"])==4
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="corner_crown"])==1
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="entry_precast_blade"])==2
  assert len([a for a in g["apertures"] if a.get("stair_slot")])==4
  assert not [m for m in g["meshes"] if "balcony" in str(m.get("carrier_kind","")) or "solar" in str(m.get("carrier_kind",""))]
def test_alternating_front_bay_grammar(c,e):
 for g in(c,e):
  front=[a for a in g["apertures"] if a.get("side")=="front" and "grammar" in a]
  assert {a["grammar"] for a in front}=={"punched","mega_frame"}
  assert {a["level"] for a in front}==set(range(5))
  mega=[a for a in front if a["grammar"]=="mega_frame"]
  groups={(a["level"],a["bay"]):[] for a in mega}
  for a in mega:groups[(a["level"],a["bay"])].append(a)
  assert all(len(v)==3 and {a["light"] for a in v}=={0,1,2} for v in groups.values())
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="mega_light_mullion"])==2*len(groups)
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="mega_masonry_spandrel"])==len(groups)
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="multi_storey_mega_frame"])==4
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="multi_storey_mega_frame_bridge"])==10
  mega_parts=[m for m in g["meshes"] if m.get("carrier_kind") in {"mega_light_mullion","mega_masonry_spandrel","multi_storey_mega_frame","multi_storey_mega_frame_bridge"}]
  assert all(not overlap(a,b) for i,a in enumerate(mega_parts) for b in mega_parts[i+1:])
  assert all(m["projection_depth_m"]==pytest.approx(.22) for m in mega_parts if m.get("carrier_kind") in {"multi_storey_mega_frame","multi_storey_mega_frame_bridge"})
def test_roof_mechanical_contract(c,e):
 for g in(c,e):
  expected_count=4 if g["size"]=="canonical" else 6
  assert len(g["mechanical_screen"])==expected_count and len(g["roof_equipment"])==5
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="sparse_roof_vent"])==4
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="square_skylight"])==1
  screens=[m for m in g["meshes"] if m.get("carrier_kind")=="mechanical_screen"]
  court=g["courtyard"]["bounds"]
  assert all(m["roof_supported"] for m in screens)
  assert {m["side"] for m in screens}=={"front","rear","left","right"}
  if g["size"]=="extended":
   inserted=[m for m in screens if m["screen_role"]=="inserted_negative_x"]
   assert len(inserted)==2 and all((bounds(m)[0],bounds(m)[1])==pytest.approx((-17.,-10.)) for m in inserted)
   fixed=[m for m in screens if m["screen_role"]=="fixed" and m["side"] in {"front","rear"}]
   assert len(fixed)==2 and all((bounds(m)[0],bounds(m)[1])==pytest.approx((-10.,10.)) for m in fixed)
  env={tuple(m["screen_envelope"]) for m in screens};assert len(env)==1
  sx0,sx1,sy0,sy1=next(iter(env));assert (sx1-sx0,sy1-sy0)==pytest.approx((g["courtyard"]["width_m"]+6,18.))
  hvac=[m for m in g["meshes"] if m.get("carrier_kind")=="bounded_hvac"]
  assert all(m["outside_courtyard"] and not (bounds(m)[0]<court[1] and bounds(m)[1]>court[0] and bounds(m)[2]<court[3] and bounds(m)[3]>court[2]) for m in hvac)
def test_exact_whole_module_audit(c,e):
 assert not c["whole_modules"] and len(e["whole_modules"])==10
 modules=[m for m in e["meshes"] if m.get("carrier_kind")=="whole_7m_module"]
 assert len(modules)==10 and all(m["module_width_m"]==pytest.approx(7.) and m["uv_scale_m"]==pytest.approx(1.) for m in modules)
 assert e["scale_contract"]["insertion_zone_x_m"]==[-28.,-21.] and c["scale_contract"]["insertion_zone_x_m"] is None
 assert e["scale_contract"]["fixed_positive_x_terminal_m"]==c["scale_contract"]["fixed_positive_x_terminal_m"]==21.
 assert e["courtyard"]["width_m"]-c["courtyard"]["width_m"]==pytest.approx(7.)
def test_courtyard_masonry_lobby_orientation_and_seam_coverage(c,e):
 for g in(c,e):
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="courtyard_brick_panel"])>0
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="courtyard_level_band"])==16
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="outer_level_seam_band"])==12
  assert len(g["corner_lobby_apertures"])==4 and len([m for m in g["meshes"] if m.get("carrier_kind")=="corner_lobby_soffit"])==1
  assert len([a for a in g["corner_lobby_apertures"] if a.get("return_glazing")])==1
  expected={"front":[0,-1,0],"rear":[0,1,0],"left":[-1,0,0],"right":[1,0,0],"court_front":[0,1,0],"court_rear":[0,-1,0],"court_left":[1,0,0],"court_right":[-1,0,0]}
  for m in g["meshes"]:
   if m.get("carrier_kind") in {"recessed_glass","opaque_aperture_backing"}:assert m["exterior_normal"]==expected[m["side"]]
  named={m["name"]:m for m in g["meshes"]}
  for a in g["apertures"]+g["courtyard_apertures"]+g["oriel_apertures"]+g["corner_lobby_apertures"]+[g["entry"]]:
   glass,card,back=named[a["glass"]],named[a["card"]],named[a["backing"]]
   axis=1 if a["side"] in {"front","rear","court_front","court_rear"} else 0
   gv=glass["vertices"][0][axis];cv=card["vertices"][0][axis];bv=back["vertices"][0][axis]
   if a["side"] in {"front","left","court_rear","court_right"}:assert gv<cv<bv
   else:assert gv>cv>bv
  # Five occupied slab datums, four non-overlapping bars per datum plus modules.
  slabs=[m for m in g["meshes"] if m.get("carrier_kind") in {"ring_floor","whole_7m_module"} and "slab_floor" in m["name"]]
  assert {m["floor"] for m in slabs}==set(range(5))
  assert all(not overlap(a,b) for i,a in enumerate(slabs) for b in slabs[i+1:] if a["floor"]==b["floor"])
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="oriel_bronze_mullion"])==16
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="oriel_bronze_transom"])==12
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="parapet_crown_endpoint_cap"])==2
  # Positive-X landmark anchor is invariant; extended prepends one bay only.
  if g["size"]=="extended":
   front=[a for a in g["apertures"] if a.get("side")=="front" and "grammar" in a]
   assert any(abs((next(v[0] for v in next(m for m in g["meshes"] if m["name"]==a["glass"])["vertices"]))+24.8)<2 for a in front)
def test_unique_owned_closed_and_terminal_overlap(c,e):
 for g in(c,e):
  names=[m["name"] for m in g["meshes"]];assert len(names)==len(set(names))
  assert all(len(m["faces"])==len(m["face_owners"]) and all(o==[m["sticker_owner_id"]] for o in m["face_owners"]) for m in g["meshes"])
  assert all(m["closed"] and m["outward_winding"] for m in g["meshes"] if len(m["faces"])>1)
  caps=[m for m in g["meshes"] if m.get("outward_terminal_faces")]
  assert all(not overlap(a,b) for i,a in enumerate(caps) for b in caps[i+1:])
def test_stable_bay_roles_equipment_clearance_and_forbidden_overlaps(c,e):
 canonical=lambda g:{(a["level"],a["center_m"],a["width_m"],a["grammar"],a["bay_role"]) for a in g["apertures"] if a.get("side")=="front" and a.get("bay_role","").startswith("canonical_")}
 assert canonical(c)==canonical(e)
 inserted=[a for a in e["apertures"]+e["courtyard_apertures"] if a.get("inserted_module")]
 assert inserted and {a["bay_role"] for a in inserted}=={"inserted_negative_x"}
 for g in(c,e):
  # Roof objects keep at least 0.45m XY clearance from each other.
  eq=[m for m in g["meshes"] if m.get("carrier_kind") in {"bounded_hvac","square_skylight","sparse_roof_vent"}]
  def clearance(a,b):
   x,y=bounds(a),bounds(b);return max(max(x[0]-y[1],y[0]-x[1]),max(x[2]-y[3],y[2]-x[3]))
  assert all(clearance(a,b)>=.45 for i,a in enumerate(eq) for b in eq[i+1:])
  # Wall fabric and seam bands/slabs must never share positive volume.
  fabric=[m for m in g["meshes"] if m.get("carrier_kind") in {"outer_brick_panel","courtyard_brick_panel"}]
  bands=[m for m in g["meshes"] if m.get("carrier_kind") in {"outer_level_seam_band","courtyard_level_band","precast_floor_datum"}]
  slabs=[m for m in g["meshes"] if m.get("carrier_kind") in {"ring_floor","whole_7m_module"} and "slab_floor" in m["name"]]
  assert all(not overlap(a,b) for a in fabric for b in bands)
  assert all(not overlap(a,b) for a in slabs for b in bands+fabric)
def test_top_ground_corner_entry_and_bronze_grid_closures(c,e):
 for g in(c,e):
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="segmented_ground_plinth"])==10
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="top_crown_gap_closure"])==10
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="ground_closure_corner_cap"])==8
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="top_closure_corner_cap"])==4
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="court_continuous_corner_L"])==4
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="parapet_corner_cap"])==8
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="parapet_entry_endpoint_cap"])==2
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="gravel_roof_endpoint_cap"])==2
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="outer_level_corner_cap"])==16
  assert not [m for m in g["meshes"] if m.get("carrier_kind")=="courtyard_level_corner_cap"]
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="precast_floor_datum"])==12
  assert all(m["split_for_entry_blades"] for m in g["meshes"] if m.get("carrier_kind")=="precast_floor_datum")
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="oriel_return_mullion"])==16
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="oriel_return_transom"])==12
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="lobby_return_mullion"])==4
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="lobby_return_transom"])==3
  roofs=[m for m in g["meshes"] if m.get("carrier_kind")=="gravel_roof_field"]
  assert all(m["trimmed_for_oriel_crown"] for m in roofs)
  assert not any(bounds(m)[0]<20.45 and bounds(m)[1]>14.65 and bounds(m)[2]<-18.6 for m in roofs)
  blades=[m for m in g["meshes"] if m.get("carrier_kind")=="entry_precast_blade"]
  roof_edge=[m for m in g["meshes"] if m.get("carrier_kind") in {"gravel_roof_field","gravel_roof_endpoint_cap","closed_parapet_run","parapet_entry_endpoint_cap"} and m.get("side","front").startswith("front") or m.get("bar","").startswith("front")]
  assert all(not overlap(a,b) for a in blades for b in roof_edge)

def test_datum_slot_closure_occupied_entry_wing_and_landmark_hierarchy(c,e):
 for g in(c,e):
  closures=[m for m in g["meshes"] if m.get("carrier_kind")=="datum_slot_closure"]
  assert len(closures)==32
  assert {(m["scope"],m["side"],m["level"]) for m in closures}=={(scope,side,level) for scope,sides in (("outer",("front","rear","left","right")),("court",("front","rear","left","right"))) for side in sides for level in range(1,5)}
  for m in closures:
   b=bounds(m);z=M.DATUMS[m["level"]]
   assert b[4]==pytest.approx(z+(.10 if m["scope"]=="outer" else .08)) and b[5]==pytest.approx(z+.20)
   assert m["touches_band"] and m["no_overlap"]
  backs=[m for m in g["meshes"] if m.get("bar")=="entry_back" and m.get("carrier_kind")=="ring_floor"]
  assert len(backs)==5 and {m["floor"] for m in backs}==set(range(5))
  roof=next(m for m in g["meshes"] if m.get("bar")=="landmark_inner" and m.get("carrier_kind")=="dark_inner_membrane_field")
  assert roof["behind_shallow_entry"] and bounds(roof)[3]<=g["courtyard"]["bounds"][2]
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="entry_recess_cheek"])==2
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="entry_slot_bridge"])==5
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="oriel_terminal_cheek"])==2
  crown=next(m for m in g["meshes"] if m.get("carrier_kind")=="corner_crown")
  assert crown["slender_crown"] and bounds(crown)[5]-bounds(crown)[4]==pytest.approx(.48)
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="corner_lobby_pale_plinth"])==1
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="corner_lobby_pale_pier"])==4
  assert all(bounds(m)[5]<=18.78 for m in g["meshes"] if m.get("carrier_kind")=="mechanical_screen")

def test_every_ordinary_aperture_has_opaque_sill_head_and_landmark_roof_closure(c,e):
 for g in(c,e):
  named={m["name"]:m for m in g["meshes"]}
  ordinary=[a for a in g["apertures"]+g["courtyard_apertures"] if "level" in a and not a.get("stair_slot")]
  assert ordinary and all(len(a["wall_zones"])==2 for a in ordinary)
  for a in ordinary:
   zones=[named[n] for n in a["wall_zones"]];kinds={m["carrier_kind"] for m in zones}
   assert kinds=={"aperture_sill_wall","aperture_head_wall"}
   u=sum(a["opening_u"])/2;z0,z1=a["opening_z"]
   for zone,z in (("sill",z0-.05),("head",z1+.05)):
    m=next(x for x in zones if x["carrier_kind"]==f"aperture_{zone}_wall");bb=bounds(m)
    axis=(0,1) if a["side"] in {"front","rear","court_front","court_rear"} else (2,3)
    assert bb[axis[0]]<=u<=bb[axis[1]] and bb[4]<=z<=bb[5]
  # At every occupied datum, the landmark wing is continuous from immediately
  # behind the shallow entry recess to the courtyard boundary.
  slabs=[m for m in g["meshes"] if m.get("bar")=="entry_back"]
  assert all(bounds(m)[0]==pytest.approx(9.55) and bounds(m)[1]==pytest.approx(14.70) and bounds(m)[2]==pytest.approx(-17.95) for m in slabs)
  outer=next(m for m in g["meshes"] if m.get("bar")=="landmark_outer")
  inner=next(m for m in g["meshes"] if m.get("bar")=="landmark_inner")
  ob,ib=bounds(outer),bounds(inner);assert ob[0]==ib[0]==pytest.approx(9.55) and ob[1]==ib[1]==pytest.approx(20.55) and ob[2]==pytest.approx(-17.95) and ob[3]==ib[2] and ib[3]==pytest.approx(g["courtyard"]["bounds"][2]-.30)

def test_signature_corner_is_bound_broad_and_continuous(c,e):
 for g in(c,e):
  cheek=next(m for m in g["meshes"] if m.get("carrier_kind")=="stair_oriel_binding_cheek")
  bridge=next(m for m in g["meshes"] if m.get("carrier_kind")=="stair_oriel_binding_bridge")
  cb,bb=bounds(cheek),bounds(bridge)
  assert cheek["full_height"] and cb==pytest.approx((14.35,14.55,-18.60,-17.95,.20,17.20))
  assert bridge["full_height_seam_closed"] and bb==pytest.approx((14.35,14.55,-19.,-18.60,17.20,17.34))
  pavilion=[a for a in g["oriel_apertures"] if a.get("broad_corner_pavilion")]
  assert len(pavilion)==24 and {a["side"] for a in pavilion}=={"front","right"}
  front=[a for a in pavilion if a["side"]=="front"]
  assert min(a["opening_u"][0] for a in front)==pytest.approx(14.78) and max(a["opening_u"][1] for a in front)==pytest.approx(20.02)
  soffit=next(m for m in g["meshes"] if m.get("carrier_kind")=="oriel_soffit")
  sb=bounds(soffit);assert sb[0]==pytest.approx(14.55) and sb[1]==pytest.approx(20.55) and sb[2]==pytest.approx(-20.55)
  canopy=next(m for m in g["meshes"] if m.get("carrier_kind")=="continuous_corner_canopy")
  plinth=next(m for m in g["meshes"] if m.get("carrier_kind")=="continuous_corner_plinth")
  lobby=next(m for m in g["meshes"] if m.get("carrier_kind")=="corner_lobby_pale_plinth")
  assert bounds(canopy)[0]==pytest.approx(14.35) and bounds(canopy)[1]==pytest.approx(bounds(soffit)[0])
  assert bounds(plinth)[1]==pytest.approx(bounds(lobby)[0])
  signature=[cheek,bridge,canopy,plinth,lobby,soffit]
  assert all(not overlap(a,b) for i,a in enumerate(signature) for b in signature[i+1:])

def test_adjacent_finish_terminal_caps_are_pale_closed_and_nonoverlapping(c,e):
 for g in(c,e):
  terminal=[m for m in g["meshes"] if m.get("adjacent_finish_terminal")]
  assert terminal and all(m.get("terminal_source_map") in {"pale_precast","court_coping"} for m in terminal)
  assert all("dark" not in m["terminal_source_map"] and "joint" not in m["terminal_source_map"] for m in terminal)
  assert all(m["material_domain"]=="precast" for m in terminal)
  assert all(not overlap(a,b) for i,a in enumerate(terminal) for b in terminal[i+1:])
  # Court parapet and its new coping have four shortened runs plus exactly four
  # one-owner corner caps; no stacked/open terminal teeth remain.
  coping=[m for m in g["meshes"] if m.get("carrier_kind") in {"court_coping_run","court_coping_corner_cap"}]
  assert len([m for m in coping if m.get("carrier_kind")=="court_coping_run"])==4
  assert len([m for m in coping if m.get("carrier_kind")=="court_coping_corner_cap"])==4
  assert all(not overlap(a,b) for i,a in enumerate(coping) for b in coping[i+1:])
  assert all(m["closed"] and m["outward_winding"] for m in coping)

def test_court_brick_parapet_base_and_disjoint_roof_finish_schedule(c,e):
 for g in(c,e):
  base=[m for m in g["meshes"] if m.get("carrier_kind") in {"court_parapet_brick_base","court_continuous_corner_L"}]
  assert len([m for m in base if m.get("carrier_kind")=="court_parapet_brick_base"])==4
  assert len([m for m in base if m.get("carrier_kind")=="court_continuous_corner_L"])==4
  assert all(m["terminal_source_map"]=="court_brick" and m["material_domain"]=="warm_brick" and m["closed"] and m["outward_winding"] for m in base)
  assert all(not overlap(a,b) for i,a in enumerate(base) for b in base[i+1:])
  pale=[m for m in g["meshes"] if m.get("carrier_kind") in {"closed_parapet_run","parapet_corner_cap"} and (m.get("side","").startswith("court") or m.get("scope")=="court")]
  assert all(bounds(a)[5]<=bounds(b)[4] or not overlap(a,b) for a in base for b in pale)
  gravel=[m for m in g["meshes"] if m.get("carrier_kind") in {"gravel_roof_field","gravel_roof_endpoint_cap"}]
  membrane=[m for m in g["meshes"] if m.get("carrier_kind")=="dark_inner_membrane_field"]
  assert gravel and len(membrane)==6
  assert all(m["material_domain"]=="dark_roof_membrane" and m["upward_roof_finish"] and m["service_zone"] for m in membrane)
  assert all(m["upward_roof_finish"] for m in gravel)
  assert all(not overlap(a,b) for a in gravel for b in membrane)
  assert all(not overlap(a,b) for i,a in enumerate(membrane) for b in membrane[i+1:])

def test_continuous_court_corner_L_render_risk_contract(c,e):
 for g in(c,e):
  corners=[m for m in g["meshes"] if m.get("carrier_kind")=="court_continuous_corner_L"]
  assert len(corners)==4 and {m["corner"] for m in corners}=={"front_left","front_right","rear_left","rear_right"}
  assert all(m["render_risk_closure"] and m["courtyard_facing_normals"] and m["terminal_source_map"]=="court_brick" for m in corners)
  assert all(m["closed"] and m["outward_winding"] and len(m["vertices"])==12 and len(m["faces"])==8 for m in corners)
  assert all(bounds(m)[4]==pytest.approx(.20) and bounds(m)[5]==pytest.approx(17.34) for m in corners)
  assert all(not overlap(a,b) for i,a in enumerate(corners) for b in corners[i+1:])
  # No obsolete stacked constituent cap is allowed below the court coping.
  assert not [m for m in g["meshes"] if m.get("scope")=="court" and m.get("carrier_kind")=="top_closure_corner_cap"]
  assert not [m for m in g["meshes"] if m.get("carrier_kind") in {"courtyard_level_corner_cap","court_parapet_brick_corner_cap"}]
  runs=[m for m in g["meshes"] if m.get("carrier_kind") in {"courtyard_level_band","datum_slot_closure","court_parapet_brick_base"} and (m.get("scope")=="court" or m["name"].startswith("court_"))]
  assert all(not overlap(a,b) for a in corners for b in runs)

def test_optical_depth_order_containment_and_interior_depth_cues(c,e):
 for g in(c,e):
  named={m["name"]:m for m in g["meshes"]}
  apertures=g["apertures"]+g["courtyard_apertures"]+g["oriel_apertures"]+g["corner_lobby_apertures"]+[g["entry"]]
  assert {a["side"] for a in apertures}=={"front","rear","left","right","court_front","court_rear","court_left","court_right"}
  for a in apertures:
   pane,card,back=(named[a[k]] for k in ("glass","card","backing"))
   assert pane["optical_depth_m"]==0 and card["optical_depth_m"]==pytest.approx(.09) and back["optical_depth_m"]==pytest.approx(.32)
   assert card["immediately_behind_pane"] and back["farther_inward"] and back["contains_card_with_margin_m"]==pytest.approx(.07)
   pb,cb,bb=bounds(pane),bounds(card),bounds(back);axis=2 if a["side"] in {"front","rear","court_front","court_rear"} else 0
   # Backing contains the card in aperture-width and height dimensions only;
   # its sightline coordinate remains strictly farther inward.
   uaxis=(0,1) if axis==2 else (2,3)
   assert bb[uaxis[0]]<cb[uaxis[0]]<cb[uaxis[1]]<bb[uaxis[1]] and bb[4]<cb[4]<cb[5]<bb[5]
   assert len(a["interior_cues"])==4 and {named[n]["carrier_kind"] for n in a["interior_cues"]}=={"interior_room_floor","interior_room_ceiling","interior_room_sidewall"}
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="stair_landing"])==4
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="stair_landing_guard"])==4
  assert len([m for m in g["meshes"] if m.get("carrier_kind") in {"bright_lobby_floor","bright_lobby_ceiling","bright_lobby_backing"}])==3

def test_front_datum_frame_and_oriel_terminal_closure_contract(c,e):
 for g in(c,e):
  runs=[m for m in g["meshes"] if m.get("carrier_kind")=="precast_floor_datum"]
  caps=[m for m in g["meshes"] if m.get("carrier_kind")=="precast_datum_endpoint_cap"]
  assert len(runs)==12 and len(caps)==20
  assert all(m["shortened_for_projected_frame"] for m in runs)
  assert all(m["terminal_source_map"]=="pale_precast" and m["material_domain"]=="precast" and m["closed"] and m["outward_winding"] for m in caps)
  assert not [m for m in caps if "dark" in m["terminal_source_map"] or "joint" in m["terminal_source_map"] or "interior" in m["terminal_source_map"]]
  assert {m["terminal"] for m in caps}=={"mega0_left","mega0_right","mega1_left","mega1_right","oriel_junction"}
  assert all(not overlap(a,b) for i,a in enumerate(caps) for b in caps[i+1:])
  assert all(not overlap(a,b) for a in runs for b in caps)
  mega=[m for m in g["meshes"] if m.get("carrier_kind")=="multi_storey_mega_frame"]
  assert all(not overlap(a,b) for a in caps for b in mega)
  junction=[m for m in caps if m["terminal"]=="oriel_junction"]
  assert all(m["closed_against_oriel"] and bounds(m)[0:2]==pytest.approx((14.35,14.55)) for m in junction)

def test_grouped_window_sill_slots_and_datum_face_roles_are_pale(c,e):
 for g in(c,e):
  sills=[m for m in g["meshes"] if m.get("carrier_kind")=="mega_sill_slot_closure"]
  expected_groups=len({(a["level"],a["bay"]) for a in g["apertures"] if a.get("grammar")=="mega_frame"})
  assert len(sills)==expected_groups
  assert all(m["material_domain"]=="precast" and m["terminal_source_map"]=="pale_precast" and m["explicit_underside_role"]=="pale_precast_underside" and m["closed_against_frame"] for m in sills)
  datums=[m for m in g["meshes"] if m.get("carrier_kind") in {"precast_floor_datum","precast_datum_endpoint_cap"}]
  assert all(m["material_domain"]=="precast" and m["terminal_source_map"]=="pale_precast" and m["explicit_underside_role"]=="pale_precast_underside" for m in datums)
  corners=[m for m in g["meshes"] if m.get("datum_corner_endpoint")]
  assert len(corners)==4 and all(m["carrier_kind"]=="outer_level_corner_cap" and m["closed_against_datum"] and m["explicit_underside_role"]=="pale_precast_underside" for m in corners)
  assert all(not overlap(a,b) for a in sills for b in datums+corners)

def test_eight_elevation_closure_continuity_and_global_forbidden_overlap(c,e):
 for g in(c,e):
  closure=[m for m in g["meshes"] if m.get("carrier_kind") in {"segmented_ground_plinth","ground_closure_corner_cap"}]
  x0=min(bounds(m)[0] for m in closure);x1=max(bounds(m)[1] for m in closure);y0=-19.;y1=19.
  cx0,cx1,cy0,cy1=g["courtyard"]["bounds"]
  samples={
   "front":(x0+1.,y0+.15),"rear":(x0+1.,y1-.15),
   "left":(x0+.15,10.),"right":(x1-.15,10.),
   "court_front":(0.,cy0-.15),"court_rear":(0.,cy1+.15),
   "court_left":(cx0-.15,0.),"court_right":(cx1+.15,0.),
  }
  for z,kind,caps in ((.10,"segmented_ground_plinth","ground_closure_corner_cap"),(17.15,"top_crown_gap_closure","top_closure_corner_cap")):
   owners=[m for m in g["meshes"] if m.get("carrier_kind") in {kind,caps}]
   for side,(x,y) in samples.items():
    hit=[m for m in owners if bounds(m)[0]-1e-8<=x<=bounds(m)[1]+1e-8 and bounds(m)[2]-1e-8<=y<=bounds(m)[3]+1e-8 and bounds(m)[4]-1e-8<=z<=bounds(m)[5]+1e-8]
    assert len(hit)==1,(side,z,[m["name"] for m in hit])
  watched={"segmented_ground_plinth","top_crown_gap_closure","ground_closure_corner_cap","top_closure_corner_cap","corner_transition_fabric","precast_floor_datum","closed_parapet_run","parapet_corner_cap","parapet_crown_endpoint_cap","parapet_entry_endpoint_cap","gravel_roof_field","gravel_roof_endpoint_cap","entry_precast_blade","main_coping","outer_brick_panel","courtyard_brick_panel","outer_level_seam_band","courtyard_level_band","outer_level_corner_cap","courtyard_level_corner_cap"}
  items=[m for m in g["meshes"] if m.get("carrier_kind") in watched]
  bad=[(a["name"],b["name"]) for i,a in enumerate(items) for b in items[i+1:] if overlap(a,b)]
  assert not bad,bad
def test_determinism_unknown(c,e):
 assert M.build_geometry("canonical")["geometry_sha256"]==c["geometry_sha256"] and M.build_geometry("extended")["geometry_sha256"]==e["geometry_sha256"] and c["geometry_sha256"]!=e["geometry_sha256"]
 with pytest.raises(KeyError):M.build_geometry("elastic")
