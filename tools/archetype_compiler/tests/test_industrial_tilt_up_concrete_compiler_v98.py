from __future__ import annotations
import hashlib
import sys
from pathlib import Path

TOOL_DIR=Path(__file__).resolve().parents[1]
if str(TOOL_DIR) not in sys.path:sys.path.insert(0,str(TOOL_DIR))
from build_industrial_tilt_up_concrete_sticker_lego_v98 import build_geometry
from compile_industrial_tilt_up_concrete_sticker_lego_v98 import ASSETS,REFERENCE_HASHES,SIZE_MATRIX,_build_profile,_carrier,_face_groups
from glass_profiles import GLASS_PROFILES


def _carriers(size="canonical"):return [_carrier(m,g) for m in build_geometry(size)["meshes"] for g in _face_groups(m)]


def test_exact_refs_geometry_hashes_and_tiers_are_locked():
 assert set(REFERENCE_HASHES)==set(build_geometry("canonical")["reference_evidence"])
 assert build_geometry("canonical")["geometry_sha256"].startswith("9c51f0b0")
 assert build_geometry("extended")["geometry_sha256"].startswith("f7ffcae4")
 for size in SIZE_MATRIX:
  p,pkg=_build_profile(size);assert pkg["status"]=="pass" and not pkg["failures"]
  assert p["production_contract"]["clay_lock"]["geometry_sha256"]==build_geometry(size)["geometry_sha256"]
 assert SIZE_MATRIX["extended"]["depth_m"]-SIZE_MATRIX["canonical"]["depth_m"]==6


def test_every_visible_face_exactly_once_and_no_fallback():
 for size in SIZE_MATRIX:
  g=build_geometry(size);p,_=_build_profile(size);cs=p["massing_graph"]["assemblies"]
  expected={(m["name"],i) for m in g["meshes"] for i in range(len(m["faces"]))};actual=[(c["surface_id"],i) for c in cs for i in c["face_indices"]]
  assert set(actual)==expected and len(actual)==len(set(actual));assert p["massing_graph"]["surface_audit"]["status"]=="pass"
  assert all(c["final_surface_coverage"] and "generic" not in c["sticker_layer"] for c in cs)


def test_roles_are_disjoint_complete_and_semantic():
 cs=_carriers();required={"office_ground","office_upper","entry","high_bay","pylon","loading","rear","crown","roof","roof_equipment"}
 assert {c["floor_role"] for c in cs}==required
 by={}
 for c in cs:by.setdefault(c["surface_id"],set()).add(c["floor_role"])
 assert all(len(v)==1 or (name.startswith("tpo_roof_") and v=={"roof","crown"}) for name,v in by.items())


def test_panel_joints_are_physical_sealant_and_concrete_assets_print_none():
 g=build_geometry("canonical");by={c["surface_id"]:c for c in _carriers()}
 joints=[m for m in g["meshes"] if m["material_domain"]=="joint_recess"]
 assert joints and all(by[m["name"]]["source_image_path"]==ASSETS["joint"] for m in joints)
 import json
 prov=json.loads((TOOL_DIR/"sticker_assets/industrial_tilt_up_concrete_v98/provenance.json").read_text())
 for role in ("warm_buff_concrete_front","warm_buff_concrete_return","cool_gray_side_rear_concrete","weathered_plinth_reveal_concrete"):
  assert prov["assets"][role]["contains_printed_panel_joints"] is False


def test_glass_supported_and_cards_separate_exact_cells():
 first=_carriers();second=_carriers();glass=[c for c in first if c["material_role"]=="glass"]
 assert glass and {c["glass_profile"] for c in glass}<={*GLASS_PROFILES}
 assert all(c["source_image_path"] in {ASSETS["glass"],ASSETS["rooflight_glass"]} for c in glass)
 cards=[c for c in first if "_card" in c["sticker_layer"]];cards2=[c for c in second if "_card" in c["sticker_layer"]]
 assert cards and all(c["source_image_path"] in {ASSETS["lower_interior"],ASSETS["upper_interior"]} for c in cards)
 assert all(c["uv_u_max"]-c["uv_u_min"]==.25 and c["uv_v_max"]-c["uv_v_min"]==.5 for c in cards)
 assert [(c["surface_id"],c["atlas_cell_index"]) for c in cards]==[(c["surface_id"],c["atlas_cell_index"]) for c in cards2]


def test_canopy_roof_loading_and_caps_are_role_correct():
 g=build_geometry("canonical");cs=_carriers();by={}
 for c in cs:by.setdefault(c["surface_id"],[]).append(c)
 slab=by["entrance_canopy_slab"]
 assert next(c for c in slab if c["face_indices"]==[1])["source_image_path"]==ASSETS["canopy_top"]
 assert next(c for c in slab if c["face_indices"]==[0])["source_image_path"]==ASSETS["canopy_soffit"]
 assert all(c["source_image_path"]==ASSETS["overhead_door"] for n,v in by.items() if "ribbed_door" in n for c in v)
 caps=[m for m in g["meshes"] if m.get("carrier_kind")=="adjacent_finish_endpoint_cap"]
 forbidden={ASSETS["joint"],ASSETS["dock"],ASSETS["grille"]}
 assert caps and not any(c["source_image_path"] in forbidden for m in caps for c in by[m["name"]])
 parapets=[m for m in g["meshes"] if m.get("carrier_kind") in {"parapet_run","adjacent_finish_endpoint_cap"} and ("parapet" in m["name"] or "pylon" in m["name"])]
 assert parapets and all(next(c for c in by[m["name"]] if c["face_indices"]==[1])["source_image_path"]==ASSETS["coping"] for m in parapets)
 assert all(next(c for c in by[m["name"]] if c["face_indices"]!=[1])["source_image_path"] in {ASSETS["warm_return"],ASSETS["cool_concrete"]} for m in parapets)


def test_all_nine_loading_receiving_leaves_share_metric_sectional_door_finish():
 g=build_geometry("canonical");cs=_carriers();by={c["surface_id"]:c for c in cs}
 leaves=[m for m in g["meshes"] if m.get("carrier_kind")=="opaque_ribbed_door_plane"]
 assert len(leaves)==9
 assert {m.get("side") for m in leaves}=={"right","rear"}
 for mesh in leaves:
  carrier=by[mesh["name"]]
  assert carrier["source_image_path"]==ASSETS["overhead_door"]
  assert carrier["sticker_layer"]=="opaque_overhead_door"
  assert carrier["world_metric_uv_tile_m"]==4.0
  assert carrier["roughness_override"]==.60


def test_roof_upfaces_have_plan_bounds_and_membrane_does_not_leak():
 cs=_carriers();tops=[c for c in cs if c["axis"]=="plan"]
 assert tops and all(c["face_indices"]==[1] and len(c["plan_bounds"])==4 and c["source_image_path"]==ASSETS["tpo"] for c in tops)
 assert not any(c["source_image_path"]==ASSETS["tpo"] for c in cs if c["floor_role"]!="roof")
 assert not any(c["source_image_path"]==ASSETS["tpo"] for c in cs if c["axis"]!="plan")


def test_roof_material_faces_respect_declared_11_1m_datum_and_returns_are_crown():
 for size in SIZE_MATRIX:
  g=build_geometry(size);p,_=_build_profile(size);graph=p["massing_graph"]
  datum=graph["floor_sticker_contract"]["roof_starts_at_z_m"]
  assert datum==11.1 and graph["floor_sticker_contract"]["forbid_roof_below_roof_datum"] is True
  meshes={m["name"]:m for m in g["meshes"]}
  roof_assets={ASSETS["tpo"],ASSETS["roof_patch"]}
  selected=[c for c in graph["assemblies"] if c["source_image_path"] in roof_assets]
  assert selected
  for c in selected:
   mesh=meshes[c["surface_id"]]
   centres=[]
   for fi in c["face_indices"]:
    zs=[mesh["vertices"][vi][2] for vi in mesh["faces"][fi]]
    centres.append(sum(zs)/len(zs))
    assert min(zs)>=datum-1e-9
   assert min(centres)>=datum-1e-9
   if c["source_image_path"]==ASSETS["tpo"]:
    assert c["floor_role"]=="roof" and c["face_indices"]==[1]
   else:
    assert c["floor_role"]=="crown" and c["face_indices"]!=[1]


def test_constant_concrete_metric_uv_and_whole_rear_module():
 allc=[]
 for size in SIZE_MATRIX:allc += [c for c in _carriers(size) if "concrete" in c["sticker_layer"]]
 assert {c["world_metric_uv_tile_m"] for c in allc}=={1.5}
 c=build_geometry("canonical");e=build_geometry("extended")
 modules=[m for m in e["meshes"] if m.get("carrier_kind")=="rear_depth_module"]
 assert len(modules)==6 and not [m for m in c["meshes"] if m.get("carrier_kind")=="rear_depth_module"]
 assert all(m.get("module_depth_m")==6.0 for m in modules)


def test_openwork_screen_and_continuous_office_ribbons_are_semantically_owned():
 g=build_geometry("canonical");cs=_carriers();by={}
 for c in cs:by.setdefault(c["surface_id"],[]).append(c)
 fins=[m for m in g["meshes"] if m.get("carrier_kind")=="vertical_openwork_fin"]
 assert len(fins)==85
 assert all(c["source_image_path"]==ASSETS["aluminum"] and c["floor_role"]=="crown" for m in fins for c in by[m["name"]])
 backing=next(m for m in g["meshes"] if m.get("carrier_kind")=="openwork_screen_backing")
 coping=next(m for m in g["meshes"] if m.get("carrier_kind")=="openwork_top_coping")
 assert by[backing["name"]][0]["source_image_path"]==ASSETS["openwork_backing"] and by[backing["name"]][0]["floor_role"]=="crown"
 assert by[coping["name"]][0]["source_image_path"]==ASSETS["aluminum"] and by[coping["name"]][0]["floor_role"]=="crown"
 ribbons=[m for m in g["meshes"] if m.get("carrier_kind") in {"recessed_glass","recessed_interior_card"} and m["name"].startswith("front_office_ribbon_")]
 assert len(ribbons)==6
 assert {c["floor_role"] for m in ribbons for c in by[m["name"]]}=={"office_ground","office_upper"}
 cards=[by[m["name"]][0] for m in ribbons if m["material_domain"]=="interior_card"]
 assert len({c["atlas_cell_index"] for c in cards})==3
