import importlib.util
from pathlib import Path
import pytest
P=Path(__file__).parents[1]/"build_industrial_tilt_up_concrete_sticker_lego_v98.py";S=importlib.util.spec_from_file_location("it",P);M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
@pytest.fixture(scope="module")
def c():return M.build_geometry("canonical")
@pytest.fixture(scope="module")
def e():return M.build_geometry("extended")
def bounds(m):return tuple(f(v[i] for v in m["vertices"]) for i in range(3) for f in(min,max))
def overlap(a,b):
 x,y=bounds(a),bounds(b);return all(min(x[i+1],y[i+1])-max(x[i],y[i])>1e-8 for i in(0,2,4))
def test_locked_dimensions_and_extension(c,e):
 assert c["dimensions"]=={"width_m":60.,"depth_m":42.,"shell_height_m":11.1,"office_storeys":2}
 assert e["dimensions"]["width_m"]==60. and e["dimensions"]["depth_m"]==48.
 assert c["scale_contract"]["extension"]=="one complete 6m rear operational depth bay" and c["scale_contract"]["front_fixed"]
def test_front_identity_is_fixed(c,e):
 for g in(c,e):
  assert len(g["office_windows"])==3 and {a["level"] for a in g["office_windows"]}=={0,1}
  assert sum(a["level"]==0 for a in g["office_windows"])==2 and sum(a["level"]==1 for a in g["office_windows"])==1
  assert all(a["continuous_ribbon"] for a in g["office_windows"])
  assert g["office_frontage_ratio"]==pytest.approx(34/60)
  assert g["entrance"]["fixed"] and g["entrance"]["kind"]=="entrance"
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="raised_blind_pylon"])==1
  p=next(m for m in g["meshes"] if m.get("carrier_kind")=="raised_blind_pylon");assert p["raise_above_shell_m"]==pytest.approx(2.25)
  assert len(g["vertical_slots"])==85
  fins=[m for m in g["meshes"] if m.get("carrier_kind")=="vertical_openwork_fin"]
  assert len(fins)==85 and all(m["bounded_before_pylon"] and max(v[0] for v in m["vertices"])<17.8 and max(v[2] for v in m["vertices"])>11.1 for m in fins)
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="openwork_screen_backing"])==1
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="openwork_top_coping"])==1
  mullions=[m for m in g["meshes"] if m.get("carrier_kind")=="office_window_mullion"]
  assert 15<=len(mullions)<=22
 assert [(a["name"],a.get("level"),a.get("ribbon_role")) for a in c["office_windows"]]==[(a["name"],a.get("level"),a.get("ribbon_role")) for a in e["office_windows"]]
def test_real_recessed_apertures_and_cards(c,e):
 for g in(c,e):
  for a in g["office_windows"]+[g["entrance"]]:
   assert len(a["reveals"])==4 and a["glass"] and a["card"]
  for a in g["loading_doors"]+g["rear_receiving"]:
   assert len(a["reveals"])==3 and a["door_plane"] and "glass" not in a and "card" not in a
  doors=[m for m in g["meshes"] if m.get("carrier_kind")=="opaque_ribbed_door_plane"]
  assert len(doors)==9 and all(m["material_domain"]=="ribbed_overhead_door" and m["recessed_inward"] for m in doors)
  assert all(m["material_domain"]=="recessed_glazing" for m in g["meshes"] if m.get("carrier_kind")=="recessed_glass")
  assert all(m["material_domain"]=="interior_card" for m in g["meshes"] if m.get("carrier_kind")=="recessed_interior_card")
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="slim_entry_frame_member"])==10
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="entry_door_pane"])==2
def test_supported_canopy_and_terminal_caps(c,e):
 for g in(c,e):
  named={m["name"]:m for m in g["meshes"]};slab=named["entrance_canopy_slab"]
  posts=[m for m in g["meshes"] if m.get("carrier_kind")=="canopy_post"]
  caps=[m for m in g["meshes"] if m.get("carrier_kind")=="adjacent_finish_endpoint_cap" and m.get("assembly")=="canopy"]
  assert len(posts)==len(caps)==2 and all(not overlap(slab,p) for p in posts)
  assert all(not overlap(slab,cap) for cap in caps) and all(cap["outward_terminal_faces"] for cap in caps)
def test_loading_and_rear_counts_are_fixed(c,e):
 for g in(c,e):
  assert len(g["loading_doors"])==6 and len(g["rear_receiving"])==3
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="loading_bollard"])==12
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="loading_door_concrete_head"])==6
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="receiving_door_concrete_head"])==3
  assert all(a["side"]=="right" and a["fixed"] for a in g["loading_doors"])
  wall=[m for m in g["meshes"] if m.get("side")=="right" and m.get("carrier_kind") in {"tilt_up_panel","loading_door_concrete_head","rear_depth_module"}]
  bollards=[m for m in g["meshes"] if m.get("carrier_kind")=="loading_bollard"]
  assert all(min(v[0] for v in b["vertices"])>=30.02 and b["exterior_clearance_m"]==pytest.approx(.02) for b in bollards)
  assert all(not overlap(b,w) for b in bollards for w in wall)
  rear_planes=[m for m in g["meshes"] if m.get("carrier_kind")=="opaque_ribbed_door_plane" and m.get("side")=="rear"]
  assert len(rear_planes)==3 and all(m["exterior_normal"]==[0,1,0] for m in rear_planes)
  for m in rear_planes:
   a,b,d=m["vertices"][0],m["vertices"][1],m["vertices"][2]
   ux,uy,uz=(b[i]-a[i] for i in range(3));vx,vy,vz=(d[i]-a[i] for i in range(3))
   normal=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx)
   assert normal[1]>0 and normal[0]==pytest.approx(0) and normal[2]==pytest.approx(0)
 assert [a["name"] for a in c["loading_doors"]]==[a["name"] for a in e["loading_doors"]]
def test_roof_and_parapet_contract(c,e):
 for g in(c,e):
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="fixed_tpo_roof"])==3
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="roof_rtu"])==2
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="rooflight_curb"])==12
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="recessed_rooflight_top_glass"])==3
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="sparse_roof_vent"])==3
  runs=[m for m in g["meshes"] if m.get("carrier_kind")=="parapet_run"];caps=[m for m in g["meshes"] if m.get("carrier_kind")=="adjacent_finish_endpoint_cap" and m.get("assembly")=="parapet"]
  assert len(runs)==5 and len(caps)==4 and all(not overlap(a,b) for a in runs for b in caps)
  pylon_caps=[m for m in g["meshes"] if m.get("carrier_kind")=="adjacent_finish_endpoint_cap" and m.get("assembly")=="pylon_parapet"]
  assert len(pylon_caps)==2
def test_panel_joints_are_physical_recesses(c,e):
 for g in(c,e):
  joints=[m for m in g["meshes"] if m.get("carrier_kind")=="physical_panel_joint_recess"]
  assert len(joints)==15 and all(len(m["faces"])==1 and m["material_domain"]=="joint_recess" for m in joints)
  assert all(min(v[2] for v in m["vertices"])>=4.45 for m in joints)
def test_discrete_rear_module_and_invariant_fixed_front(c,e):
 cm=[m for m in c["meshes"] if m.get("carrier_kind")=="rear_depth_module"];em=[m for m in e["meshes"] if m.get("carrier_kind")=="rear_depth_module"]
 assert not cm and len(em)==6
 assert all(m["module_depth_m"]==pytest.approx(6.) and m["uv_scale_m"]==pytest.approx(1.) for m in em)
 # Fixed front and roof meshes are bit-identical; only rear terminal translates 6m.
 def sig(m):return (m["name"],m["vertices"],m["faces"],m["sticker_owner_id"])
 cf={m["name"]:sig(m) for m in c["meshes"] if m.get("carrier_kind") in {"fixed_floor_slab","fixed_side_wall","fixed_tpo_roof","raised_blind_pylon"}}
 ef={m["name"]:sig(m) for m in e["meshes"] if m.get("carrier_kind") in {"fixed_floor_slab","fixed_side_wall","fixed_tpo_roof","raised_blind_pylon"}}
 assert cf==ef
 assert all(a["terminal_translated_m"]==pytest.approx(0.) for a in c["rear_receiving"])
 assert all(a["terminal_translated_m"]==pytest.approx(6.) for a in e["rear_receiving"])
def test_mesh_closure_ownership_uniqueness_and_aabb(c,e):
 for g in(c,e):
  names=[m["name"] for m in g["meshes"]];assert len(names)==len(set(names))
  assert all(len(m["faces"])==len(m["face_owners"]) and all(o==[m["sticker_owner_id"]] for o in m["face_owners"]) for m in g["meshes"])
  assert all(m["closed"] and m["outward_winding"] for m in g["meshes"] if len(m["faces"])>1)
  # Critical thin terminal families have zero positive AABB overlap.
  caps=[m for m in g["meshes"] if m.get("carrier_kind")=="adjacent_finish_endpoint_cap"]
  assert all(not overlap(a,b) for i,a in enumerate(caps) for b in caps[i+1:])
def test_determinism_and_unknown(c,e):
 assert M.build_geometry("canonical")["geometry_sha256"]==c["geometry_sha256"] and M.build_geometry("extended")["geometry_sha256"]==e["geometry_sha256"] and c["geometry_sha256"]!=e["geometry_sha256"]
 with pytest.raises(KeyError):M.build_geometry("elastic")
