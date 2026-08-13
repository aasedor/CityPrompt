from __future__ import annotations
import importlib.util
from pathlib import Path
import pytest
P=Path(__file__).parents[1]/"build_civic_modernism_rec_centre_sticker_lego_v98.py"
S=importlib.util.spec_from_file_location("civic_rec_v98",P);assert S and S.loader
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
@pytest.fixture(scope="module")
def canonical():return M.build_geometry("canonical")
@pytest.fixture(scope="module")
def extended():return M.build_geometry("extended")

def test_exact_three_views_lock_stepped_55x35_massing(canonical):
 assert len(canonical["reference_evidence"])==3
 assert canonical["dimensions"]=={"width_m":55.0,"depth_m":35.0,"low_wing_top_m":9.0,"gym_hall_top_m":13.5}
 assert canonical["massing"]["pool_public_wing"]=={"width_m":30.0,"height_m":9.0,"fixed":True}
 assert canonical["massing"]["blind_gym_hall"]["height_m"]==13.5

def test_extended_adds_only_one_whole_blind_gym_bay(canonical,extended):
 assert extended["dimensions"]["width_m"]==61.25 and extended["dimensions"]["depth_m"]==35.0
 assert canonical["structural_grid"]["gym_bays"]==4 and canonical["structural_grid"]["gym_bay_m"]==6.25
 assert extended["structural_grid"]["gym_bays"]-canonical["structural_grid"]["gym_bays"]==1
 assert extended["massing"]["blind_gym_hall"]["width_m"]-canonical["massing"]["blind_gym_hall"]["width_m"]==6.25
 assert extended["fixed_modules"]==canonical["fixed_modules"]
 assert extended["massing"]["pool_public_wing"]==canonical["massing"]["pool_public_wing"]

def test_pool_and_entry_glazing_are_complete_3d_assemblies(canonical):
 names={m["name"]:m for m in canonical["meshes"]};assert len(canonical["apertures"])==4
 entries=[a for a in canonical["apertures"] if a["kind"]=="entrance"]
 assert len(entries)==1 and len(entries[0]["door_assemblies"])==2
 for a in canonical["apertures"]:
  assert not a["flat_printed_void"] and a["recess_depth_m"]>=.56 and len(a["mullion_meshes"])==5
  assert names[a["recessed_glass_mesh"]]["carrier_kind"]=="recessed_glass"
  assert names[a["interior_card_mesh"]]["carrier_kind"]=="recessed_interior_card"
  assert names[a["interior_card_mesh"]]["behind_glass_m"]==.40
 entry=entries[0]
 assert not [m for m in canonical["meshes"] if m.get("carrier_kind")=="paired_entry_door_leaf"]
 for door in entry["door_assemblies"]:
  assert len(door["frame_meshes"])==5
  assert all(names[n]["material_domain"]=="silver_aluminum" for n in door["frame_meshes"])
  assert names[door["glass_mesh"]]["carrier_kind"]=="glazed_door_pane"
  assert names[door["lobby_card_mesh"]]["carrier_kind"]=="glazed_door_lobby_card"
  assert names[door["lobby_card_mesh"]]["behind_glass_m"]>0

def test_blind_gym_has_physical_concrete_grid_and_brick_infill(canonical):
 meshes=canonical["meshes"]
 assert [m for m in meshes if m.get("carrier_kind")=="blind_gym_brick_infill"]
 assert [m for m in meshes if m.get("carrier_kind")=="exposed_concrete_grid_pier"]
 assert [m for m in meshes if m.get("carrier_kind")=="exposed_concrete_grid_beam"]
 assert not [a for a in canonical["apertures"] if a["side"] in {"right","rear"}]

def test_front_gym_grid_exact_source_range_no_overlap(canonical,extended):
 for g in (canonical,extended):
  u0,u1=g["structural_grid"]["gym_front_u_range_m"]
  infill=sorted([m for m in g["meshes"] if m.get("carrier_kind")=="blind_gym_brick_infill" and m.get("side")=="front"],key=lambda m:min(v[0] for v in m["vertices"]))
  assert len(infill)==g["structural_grid"]["gym_bays"]*2
  assert min(v[0] for v in infill[0]["vertices"])==pytest.approx(u0+.22)
  assert max(v[0] for v in infill[-1]["vertices"])==pytest.approx(u1-.22)
  bay_bounds=sorted({(min(v[0] for v in m["vertices"]),max(v[0] for v in m["vertices"])) for m in infill})
  assert len(bay_bounds)==g["structural_grid"]["gym_bays"]
  assert all(a1<b0 for (_,a1),(b0,_) in zip(bay_bounds,bay_bounds[1:]))

def test_low_wing_glass_identity_and_opaque_envelope(canonical):
 assert canonical["structural_grid"]["dominant_pool_curtain_walls"]==1
 pool=[a for a in canonical["apertures"] if a["kind"]=="pool_glazing"]
 assert len([a for a in pool if a["side"]=="front"])==1
 assert len([a for a in pool if a["side"]=="left"])==2
 fields=[m for m in canonical["meshes"] if m.get("carrier_kind")=="opaque_envelope_field"]
 assert {m["name"] for m in fields}=={"front_pool_brick_field","left_return_upper_brick_field","left_return_rear_brick_field"}

def test_canopy_has_all_surfaces_ribs_and_posts(canonical):
 c=canonical["canopy"];names={m["name"] for m in canonical["meshes"]}
 assert c["top"] in names and c["soffit"] in names
 assert len(c["fascias"])==4 and len(c["ribs"])==18 and len(c["posts"])==2
 assert set(c["fascias"]+c["ribs"]+c["posts"])<=names

def test_nested_roofs_two_rooflights_and_open_mechanical_well(canonical):
 r=canonical["roof"];names={m["name"]:m for m in canonical["meshes"]}
 assert names[r["low_deck"]]["carrier_kind"]=="low_roof_deck"
 assert names[r["high_deck"]]["carrier_kind"]=="high_roof_deck"
 assert len(r["parapets"])==6 and len(r["parapet_corner_caps"])==4 and len(r["rooflights"])==2
 assert all({unit["curb"],unit["glass"]}<=set(names) for unit in r["rooflights"])
 assert r["mechanical_well_open_to_sky"] is True and len(r["mechanical_well_walls"])==4
 assert len(r["mechanical_well_corner_caps"])==4
 assert len(r["mechanical_equipment"])==3
 assert not [m for m in canonical["meshes"] if m.get("carrier_kind")=="mechanical_well_roof"]
 p=r["small_pyramidal_rooflight"];glass=names[p["glass"]]
 assert names[p["curb"]]["carrier_kind"]=="pyramidal_rooflight_curb"
 assert glass["watertight"] and glass["outward_winding"] and len(glass["faces"])==5
 edges={}
 for face in glass["faces"]:
  for a,b in zip(face,face[1:]+face[:1]):
   edge=tuple(sorted((a,b)));edges[edge]=edges.get(edge,0)+1
 assert set(edges.values())=={2}
 ladder=[names[n] for n in r["gym_access_ladder_meshes"]]
 assert len(ladder)==11
 assert len([m for m in ladder if m["carrier_kind"]=="access_ladder_rail"])==2
 assert len([m for m in ladder if m["carrier_kind"]=="access_ladder_rung"])==9

def test_rear_is_constrained_and_has_no_public_entry(canonical):
 assert canonical["completion_policy"]["rear"].endswith("no_invented_public_entrance")
 rear=[m for m in canonical["meshes"] if m.get("side")=="rear"]
 assert rear and all(m.get("completion_evidence")=="constrained" for m in rear if "completion_evidence" in m)

def test_rear_high_gym_domain_and_low_completion_are_separate(canonical,extended):
 for g in (canonical,extended):
  w=g["dimensions"]["width_m"];pool_end=-w/2+30.0
  high=[m for m in g["meshes"] if m.get("grid_zone")=="rear" and m.get("carrier_kind")=="blind_gym_brick_infill"]
  low=[m for m in g["meshes"] if m.get("grid_zone")=="rear_low"]
  assert len(high)==g["structural_grid"]["gym_bays"]*2
  assert all(max(v[2] for v in m["vertices"])<=13.5 for m in high)
  assert min(v[0] for m in high for v in m["vertices"])>=pool_end
  assert max(v[0] for m in high for v in m["vertices"])<=w/2
  assert low and all(max(v[2] for v in m["vertices"])<=9.0 for m in low)
  # Rear orientation negates u, so low-wing world x runs -w/2..pool_end;
  # 0.13 m end-pier projection is an intentional exterior grid return.
  assert min(v[0] for m in low for v in m["vertices"])>=-w/2-.13
  assert max(v[0] for m in low for v in m["vertices"])<=pool_end

def test_pool_gym_junction_has_no_positive_aabb_overlap(canonical,extended):
 def bounds(m):
  return tuple(f(v[i] for v in m["vertices"]) for i in range(3) for f in (min,max))
 def positive_overlap(a,b):
  ax0,ax1,ay0,ay1,az0,az1=bounds(a);bx0,bx1,by0,by1,bz0,bz1=bounds(b)
  return min(ax1,bx1)-max(ax0,bx0)>1e-9 and min(ay1,by1)-max(ay0,by0)>1e-9 and min(az1,bz1)-max(az0,bz0)>1e-9
 for g in (canonical,extended):
  assert not [m for m in g["meshes"] if m.get("carrier_kind")=="fixed_massing_seam"]
  junction=[m for m in g["meshes"] if m.get("carrier_kind") in {"localized_massing_junction_pier","localized_massing_junction_beam"}]
  candidates=[m for m in g["meshes"] if (m.get("side") in {"front","rear"} and m.get("carrier_kind") in {"exposed_concrete_grid_pier","exposed_concrete_grid_beam"}) or (m.get("carrier_kind")=="nested_roof_parapet" and ("front" in m["name"] or "rear" in m["name"]))]
  assert len(junction)==4 and candidates
  assert all(not positive_overlap(j,m) for j in junction for m in candidates)

def test_massing_junction_is_localized_and_inner_wall_is_owned(canonical):
 named={m["name"]:m for m in canonical["meshes"]};j=canonical["massing_junction"]
 parts=[named[n] for n in j["pier_beam_meshes"]]
 structural=[m for m in parts if m.get("carrier_kind") in {"localized_massing_junction_pier","localized_massing_junction_beam"}]
 terminals=[m for m in parts if m.get("carrier_kind")=="junction_beam_outward_terminal_cap"]
 assert len(structural)==4 and {m["junction_side"] for m in structural}=={"front","rear"}
 assert len(terminals)==2 and all(m["cap_role"].startswith("outward_") for m in terminals)
 assert all(max(v[1] for v in m["vertices"])-min(v[1] for v in m["vertices"])<=.55+1e-9 for m in structural)
 wall=named[j["stepped_brick_wall_mesh"]];coping=named[j["coping_mesh"]]
 assert wall["material_domain"]=="warm_red_brick" and min(v[2] for v in wall["vertices"])==9.0
 assert coping["material_domain"]=="pale_exposed_concrete"
 assert all(len(owner)==1 and owner[0] for m in (wall,coping) for owner in m["face_owners"])

def test_image_identified_endpoint_contract(canonical,extended):
 def bounds(m):return tuple(f(v[i] for v in m["vertices"]) for i in range(3) for f in (min,max))
 def overlap(a,b):
  aa=bounds(a);bb=bounds(b)
  return all(min(aa[i+1],bb[i+1])-max(aa[i],bb[i])>1e-9 for i in (0,2,4))
 for g in (canonical,extended):
  named={m["name"]:m for m in g["meshes"]}
  endpoint_names=g["roof"]["junction_endpoint_caps"]+[n for n in g["massing_junction"]["pier_beam_meshes"] if "outward_cap" in n]+[g["massing_junction"]["central_step_cap_mesh"]]
  endpoints=[named[n] for n in endpoint_names]
  assert len(endpoints)==7
  assert all(m["material_domain"]=="pale_exposed_concrete" for m in endpoints)
  assert all(m["closed_box"] and m["consistent_outward_winding"] and m["cap_role"].startswith("outward_") for m in endpoints)
  assert all(len(m["cap_face_indices"])==4 and all(len(o)==1 and o[0] for o in m["face_owners"]) for m in endpoints)
  roof_runs=[named[n] for n in g["roof"]["parapets"]]
  assert all(not overlap(cap,run) for cap in [named[n] for n in g["roof"]["junction_endpoint_caps"]] for run in roof_runs)
  wedge=named[g["massing_junction"]["central_step_wedge_mesh"]]
  assert wedge["closed_box"] and wedge["material_domain"]=="warm_red_brick"

def test_glass_and_cards_stay_inside_terminal_reveal_caps(canonical):
 named={m["name"]:m for m in canonical["meshes"]}
 for aperture in canonical["apertures"]:
  u0,u1=aperture["u_bounds_m"];gu0,gu1=aperture["glass_u_bounds_m"]
  assert u0<gu0<gu1<u1 and gu0==pytest.approx(u0+.18) and gu1==pytest.approx(u1-.18)
  assert len(aperture["terminal_cap_meshes"])==2
  caps=[named[n] for n in aperture["terminal_cap_meshes"]]
  assert all(m["material_domain"]=="pale_exposed_concrete" and m["cap_role"].startswith("outward_") for m in caps)
  for mesh_name in (aperture["recessed_glass_mesh"],aperture["interior_card_mesh"]):
   mesh=named[mesh_name]
   if aperture["side"]=="front":us=[v[0] for v in mesh["vertices"]]
   else:us=[-v[1] for v in mesh["vertices"]]
   assert min(us)>=gu0-1e-9 and max(us)<=gu1+1e-9

def test_hard_stops_match_final_extension_and_roof_schedule(canonical):
 stops=set(canonical["geometry_hard_stops"])
 assert "extended_tier_adds_exactly_one_complete_6_25m_blind_gym_bay" in stops
 assert "roof_schedule_requires_exactly_2_long_plus_1_pyramidal_rooflights" in stops
 assert not any("two_complete_5m" in stop or stop=="rooflight_count_must_equal_2" for stop in stops)

def test_thin_corner_assemblies_do_not_overlap_and_caps_are_owned(canonical,extended):
 def bounds(m):return tuple(f(v[i] for v in m["vertices"]) for i in range(3) for f in (min,max))
 def overlap(a,b):
  aa=bounds(a);bb=bounds(b)
  return all(min(aa[i+1],bb[i+1])-max(aa[i],bb[i])>1e-9 for i in (0,2,4))
 for g in (canonical,extended):
  named={m["name"]:m for m in g["meshes"]};r=g["roof"]
  families=[r["parapets"]+r["parapet_corner_caps"],r["mechanical_well_walls"]+r["mechanical_well_corner_caps"]]
  for family in families:
   meshes=[named[n] for n in family]
   assert all(not overlap(a,b) for i,a in enumerate(meshes) for b in meshes[i+1:])
  caps=[named[n] for n in r["parapet_corner_caps"]+r["mechanical_well_corner_caps"]]
  assert all(m["closed_box"] and m["consistent_outward_winding"] for m in caps)
  assert all(m["cap_role"].startswith("outward_") for m in caps)
  assert all(len(m["cap_face_indices"])==4 and all(len(o)==1 and o[0] for o in m["face_owners"]) for m in caps)

def test_reveals_and_grid_beams_are_split_around_terminal_solids(canonical):
 meshes=canonical["meshes"]
 reveals=[m for m in meshes if m.get("carrier_kind")=="deep_opening_reveal"]
 assert reveals and all(m["closed_box"] and m["consistent_outward_winding"] for m in reveals)
 beams=[m for m in meshes if m.get("carrier_kind")=="exposed_concrete_grid_beam"]
 assert beams and all(m["end_caps_outward"] for m in beams)
 # Every beam is bay-local, so it never crosses a pier at either end.
 assert all("_bay_" in m["name"] for m in beams)

def test_every_face_has_one_owner(canonical,extended):
 for g in (canonical,extended):
  for m in g["meshes"]:
   assert len(m["faces"])==len(m["face_owners"])
   assert all(len(o)==1 and o[0] for o in m["face_owners"])

def test_hashes_are_deterministic(canonical,extended):
 assert M.build_geometry("canonical")["geometry_sha256"]==canonical["geometry_sha256"]
 assert M.build_geometry("extended")["geometry_sha256"]==extended["geometry_sha256"]
 assert canonical["geometry_sha256"]!=extended["geometry_sha256"]

def test_unknown_tier_rejected():
 with pytest.raises(KeyError):M.build_geometry("elastic")
