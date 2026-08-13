import importlib.util
from pathlib import Path
import pytest
P=Path(__file__).parents[1]/"build_peranakan_shophouse_row_sticker_lego_v98.py";S=importlib.util.spec_from_file_location("p",P);M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
@pytest.fixture(scope="module")
def c():return M.build_geometry("canonical")
@pytest.fixture(scope="module")
def e():return M.build_geometry("extended")
def test_atomic_lock_and_color_order(c,e):
 assert c["dimensions"]=={"width_m":30.,"depth_m":28.,"storeys":2};assert e["dimensions"]["width_m"]==35.;assert c["canonical_color_order"]==["turquoise_plaster","turquoise_plaster","coral_plaster","ochre_plaster","mint_plaster","lavender_plaster"]
def test_arch_cut_panels_have_no_backing_wall(c,e):
 for g in(c,e):
  assert len(g["apertures"])==g["unit_contract"]["count"]*3
  assert not [m for m in g["meshes"] if m.get("carrier_kind")=="unit_upper_shell"]
  assert [m for m in g["meshes"] if m.get("carrier_kind")=="arch_cut_wall_panel"]
  assert all(len(a["returns"])==15 and not a["flat_printed"] for a in g["apertures"])
def test_contour_aware_upper_arch_backing_prevents_environment_leaks(c,e):
 def extents(points):
  return min(x for x,z in points),max(x for x,z in points),min(z for x,z in points),max(z for x,z in points)
 for g,expected in ((c,18),(e,21)):
  named={m["name"]:m for m in g["meshes"]}
  backings=[m for m in g["meshes"] if m.get("carrier_kind")=="arch_contour_interior_backing"]
  assert len(backings)==expected
  assert all(m["material_domain"]=="interior_backing" and m["opaque"] and m["environment_occlusion"] and m["contour_aware"] for m in backings)
  for aperture in g["apertures"]:
   glass=named[aperture["glass"]];card=named[aperture["card"]];backing=named[aperture["backing"]]
   opening=aperture["approved_opening_contour"];optical=aperture["optical_contour"];back=aperture["backing_contour"]
   ox0,ox1,oz0,oz1=extents(optical);bx0,bx1,bz0,bz1=extents(back);ax0,ax1,az0,az1=extents(opening)
   # Opaque contour contains the pane/card by an exact 80 mm X/Z envelope.
   assert (ox0-bx0,bx1-ox1,oz0-bz0,bz1-oz1)==pytest.approx((.08,.08,.08,.08))
   # It still remains strictly within the return/opening negative space.
   assert ax0<bx0<bx1<ax1 and az0<bz0<bz1<az1
   assert all(ax0<x<ax1 and az0<z<az1 for x,z in back)
   # Three distinct depth planes: transmissive pane, card, then opaque backing.
   gy={v[1] for v in glass["vertices"]};cy={v[1] for v in card["vertices"]};by={v[1] for v in backing["vertices"]}
   assert len(gy)==len(cy)==len(by)==1 and max(gy)<min(cy)<min(by)
   assert glass["sticker_owner_id"]!=card["sticker_owner_id"]!=backing["sticker_owner_id"]
def test_tunnel_and_parties_do_not_conflict(c,e):
 for g in(c,e):
  assert all(t["depth"]==1.7 and t["street_open"] for t in g["tunnels"])
  walls=[m for m in g["meshes"] if m.get("carrier_kind")=="roof_profile_party_fire_wall"]
  assert len(walls)==2*(g["unit_contract"]["count"]-1) and all(m["starts_above_arcade"] for m in walls)
  assert all(min(v[2] for v in m["vertices"])>=6.1 for m in walls)
def test_real_shopfronts(c,e):
 for g in(c,e):
  assert len(g["shopfronts"])==g["unit_contract"]["count"]
  for s in g["shopfronts"]:
   expected={"floral_panel":["window","carved_door","window"],"pilaster_capital":["carved_door","window","window"],"shuttered_bay":["window","window","carved_door"],"tile_dado_balcony":["carved_door","window","carved_door"]}[s["template"]]
   assert [o["kind"] for o in s["openings"]]==expected
   assert s["tile_dado"] and s["transom"] and s["grille"]
   assert len(s["tile_dado"])==len(s["transom"])==3 and len(s["ground_piers"])==2
   assert all(len(o["frame_members"])==4 and 0<=len(o["mullions"])<=1 for o in s["openings"])
   assert all(len(o["carvings"])==3 for o in s["openings"] if o["kind"]=="carved_door")
  assert len({tuple(o["kind"] for o in s["openings"]) for s in g["shopfronts"]})==4
  assert all(len(s["pale_surrounds"]) in {0,3,6} for s in g["shopfronts"])
  assert all(not s["pale_surrounds"] for s in g["shopfronts"] if s["template"]=="shuttered_bay")
  surrounds=[m for m in g["meshes"] if m.get("carrier_kind")=="selective_pale_shopfront_surround"]
  assert all(m["material_domain"]=="plaster_trim" and m["does_not_close_tunnel"] for m in surrounds)
  assert not [m for m in g["meshes"] if m.get("carrier_kind")=="shopfront_frame"]
def test_roofs_dormers_firewalls_are_constructed(c,e):
 for g in(c,e):
  n=g["unit_contract"]["count"]
  roofs=[m for m in g["meshes"] if m.get("carrier_kind")=="closed_pitched_roof"]
  assert len(roofs)==n*3 and all(m["closed"] and m["eaves"] and m["gables"] and m["ridge"] and m["returns"] for m in roofs)
  assert all(m["ridge_y_m"]==pytest.approx((min(v[1] for v in m["vertices"])+max(v[1] for v in m["vertices"]))/2) for m in roofs)
  assert len(g["dormers"])==n and len([m for m in g["meshes"] if m.get("carrier_kind")=="dormer_louvre"])==n*5
  assert len(g["party_walls"])==n-1 and len({p["seam"] for p in g["party_walls"]})==n-1
def test_dormers_are_seated_clear_of_local_main_roof(c,e):
 for g in(c,e):
  named={m["name"]:m for m in g["meshes"]}
  for u,roof_name in enumerate(g["roofs"]):
   roof=named[roof_name];ry=roof["ridge_y_m"]
   y0=min(v[1] for v in roof["vertices"]);y1=max(v[1] for v in roof["vertices"])
   eave=min(v[2] for v in roof["vertices"]);ridge=max(v[2] for v in roof["vertices"])
   frame=named[f"unit_{u}_louvred_dormer_frame"]
   fy0=min(v[1] for v in frame["vertices"]);fy1=max(v[1] for v in frame["vertices"])
   def roof_z(y):
    return eave+(ridge-eave)*((y-y0)/(ry-y0) if y<=ry else (y1-y)/(y1-ry))
   assert min(v[2] for v in frame["vertices"])>max(roof_z(fy0),roof_z(fy1))+.25
   assert frame["seated_above_main_roof"]
   cap=named[f"unit_{u}_dormer_cap_roof"]
   assert min(v[2] for v in cap["vertices"])>=11.17 and cap["shallow_cap_depth_m"]==pytest.approx(.60)
   assert frame["shallow_depth_m"]==pytest.approx(.20)
   assert all(m["seated_above_main_roof"] and m["horizontal_louvre"] for m in g["meshes"] if m.get("unit")==u and m.get("carrier_kind")=="dormer_louvre")
def test_balconies_are_selective_varied_and_complete(c):
 assert [b["unit"] for b in c["balconies"]]==[2,3,4] and len({b["width"] for b in c["balconies"]})==3
 assert all(len(b["parts"])==17 for b in c["balconies"])
 assert len([m for m in c["meshes"] if m.get("carrier_kind")=="balcony_side_return_guard"])==6
def test_balcony_roles_are_fixed_when_row_extends(c,e):
 assert [(b["unit"],b["width"]) for b in e["balconies"]]==[(b["unit"],b["width"]) for b in c["balconies"]]
def test_four_physical_templates_and_detail_families(c):
 assert set(c["physical_templates"])==set(M.TEMPLATES)
 kinds={m.get("carrier_kind") for m in c["meshes"]}
 assert {"relief_frieze","physical_shutter","physical_window_mullion","tile_dado","shopfront_perimeter_member","relief_medallion","shaped_pilaster","shaped_capital","open_shutter_frame_member","side_shutter_leaf","tile_relief_cluster","floral_motif_cluster","faunal_motif_cluster"}<=kinds
 assert "deep_shutter_frame" not in kinds
 shaped=[m for m in c["meshes"] if m.get("carrier_kind") in {"relief_medallion","shaped_capital","floral_motif_cluster","faunal_motif_cluster"}]
 assert shaped and all(m.get("shaped_relief") and len(m["vertices"])>=18 for m in shaped)
 assert {m.get("motif") for m in shaped}>={"six_lobed_flower","scrolled_capital","hanging_floral_pendant","paired_bird_wings"}
 fret=[m for m in c["meshes"] if m.get("carrier_kind")=="continuous_fretwork_relief"]
 pendants=[m for m in c["meshes"] if m.get("carrier_kind")=="continuous_pendant_relief"]
 assert len(fret)==12+14+13+11+12+14 and len(pendants)==3+4+3+3+3+4
 assert all(m["motif"]=="small_rounded_flower_center" and m["thin_band"] for m in fret)
 assert all(m["motif"]=="thin_drop_pendant" and m["thin_band"] for m in pendants)
 assert len({sum(1 for m in fret if m["unit"]==u) for u in range(6)})>=3
def test_shuttered_template_preserves_clear_openings(c,e):
 for g in(c,e):
  shutter_units=[u for u,t in enumerate(g["physical_templates"]) if t=="shuttered_bay"]
  members=[m for m in g["meshes"] if m.get("carrier_kind")=="open_shutter_frame_member"]
  leaves=[m for m in g["meshes"] if m.get("carrier_kind")=="side_shutter_leaf"]
  assert len(members)==len(shutter_units)*12 and len(leaves)==len(shutter_units)*6
  for u in shutter_units:
   for opening in range(3):
    mm=[m for m in members if m["unit"]==u and m["opening"]==opening]
    ll=[m for m in leaves if m["unit"]==u and m["opening"]==opening]
    assert len(mm)==4 and len(ll)==2
    assert max(v[2] for m in mm for v in m["vertices"])==pytest.approx(7.0) # arch spring/crown remains visible
    # Two narrow side leaves leave the middle of the approved aperture clear.
    assert max(v[0] for v in ll[0]["vertices"])<min(v[0] for v in ll[1]["vertices"])
def test_rear_airwells_openings_service_roofs(c,e):
 for g in(c,e):
  n=g["unit_contract"]["count"];assert len(g["rear_air_wells"])==len(g["service_wings"])==n
  assert all(w["open_to_sky"] and len(w["parts"])==4 and w["opening"] for w in g["rear_air_wells"])
  named={m["name"]:m for m in g["meshes"]};assert all(named[s["roof"]]["closed"] for s in g["service_wings"])
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="row_end_gable_wall"])==2
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="row_end_gable_upper_closure"])==2
  assert all(len(s["rear_enclosures"])==2 for s in g["service_wings"])
  assert all(len(s["openings"])==2 and len(s["rear_panels"])==5 for s in g["service_wings"])
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="service_rear_glass"])==n*2
  assert len([m for m in g["meshes"] if m.get("carrier_kind")=="service_rear_interior_card"])==n*2
def test_airwell_has_true_open_sky_volume_and_separated_rear_completion(c,e):
 def bounds(m):return tuple(f(v[i] for v in m["vertices"]) for i in range(3) for f in(min,max))
 def overlap(a,z):
  x,y=bounds(a),bounds(z);return all(min(x[i+1],y[i+1])-max(x[i],y[i])>1e-8 for i in(0,2,4))
 for g in(c,e):
  named={m["name"]:m for m in g["meshes"]}
  for u,(roof_name,well,service) in enumerate(zip(g["roofs"],g["rear_air_wells"],g["service_wings"])):
   main=named[roof_name];rear=named[service["roof"]];wing=named[service["wing"]];opening=named[well["opening"]]
   assert max(v[1] for v in main["vertices"])==pytest.approx(2.2)
   assert min(v[1] for v in rear["vertices"])==pytest.approx(5.3)
   assert service["airwell_y_range_m"]==[2.2,5.2]
   assert main["ridge_y_m"]==pytest.approx((-14+2.2)/2)
   assert rear["ridge_y_m"]==pytest.approx((5.3+14)/2)
   assert max(v[1] for v in opening["vertices"])<min(v[1] for v in wing["vertices"])
   for enclosure_name in service["rear_enclosures"]:
    enclosure=named[enclosure_name]
    assert max(v[1] for v in enclosure["vertices"])==pytest.approx(5.2)
    assert not overlap(enclosure,wing) and not overlap(enclosure,opening)
   # No pitched roof occupies any positive y interval inside the well.
   unit_roofs=[m for m in g["meshes"] if m.get("unit")==u and m.get("carrier_kind")=="closed_pitched_roof"]
   assert not [m for m in unit_roofs if min(v[1] for v in m["vertices"])<5.2 and max(v[1] for v in m["vertices"])>2.2 and "dormer" not in m["name"]]
def test_overlap_and_ownership_audit(c,e):
 def b(m):return tuple(f(v[i] for v in m["vertices"]) for i in range(3) for f in(min,max))
 def ov(a,z):
  x,y=b(a),b(z);return all(min(x[i+1],y[i+1])-max(x[i],y[i])>1e-8 for i in(0,2,4))
 for g in(c,e):
  parties=[m for m in g["meshes"] if m.get("carrier_kind") in {"roof_profile_party_fire_wall","airwell_vertical_party_wall"}]
  assert all(not ov(a,z) for i,a in enumerate(parties) for z in parties[i+1:])
  wells=[m for m in g["meshes"] if m.get("carrier_kind")=="air_well_wall"]
  assert all(not ov(a,z) for i,a in enumerate(wells) for z in wells[i+1:] if a.get("unit")==z.get("unit"))
  # Each disjoint roof-profile wall is a watertight extrusion.
  for wall in parties:
   edges={}
   for face in wall["faces"]:
    for aa,zz in zip(face,face[1:]+face[:1]):q=tuple(sorted((aa,zz)));edges[q]=edges.get(q,0)+1
   assert set(edges.values())=={2}
  assert all(len(p["copings"])==6 and len(p["walls"])==4 for p in g["party_walls"])
  slope_copings=[m for m in g["meshes"] if m.get("carrier_kind")=="slope_following_party_coping"]
  ridge_caps=[m for m in g["meshes"] if m.get("carrier_kind")=="party_ridge_cap"]
  assert len(slope_copings)==4*(g["unit_contract"]["count"]-1) and len(ridge_caps)==2*(g["unit_contract"]["count"]-1)
  assert all(len(m["vertices"])==8 and len(m["faces"])==6 and m["thin_slope_prism"] and m["x_clearance_m"]==pytest.approx(.01) for m in slope_copings)
  assert all(len({round(v[2],5) for v in m["vertices"]})>2 for m in slope_copings)
  assert all(m["compact"] and m["x_clearance_m"]==pytest.approx(.01) for m in ridge_caps)
  # Roofs terminate 0.08 m from each seam; 0.14 m coping width leaves 0.01 m each side.
  for coping in slope_copings+ridge_caps:
   seam=-g["dimensions"]["width_m"]/2+coping["seam"]*M.UW
   assert min(v[0] for v in coping["vertices"])>=seam-.07-1e-8
   assert max(v[0] for v in coping["vertices"])<=seam+.07+1e-8
  # Expanded family overlap audit: panes do not overlap perimeter members;
  # parties are seam-singletons and balconies belong only to their unit.
  named={m["name"]:m for m in g["meshes"]}
  for s in g["shopfronts"]:
   for o in s["openings"]:
    assert all(not ov(named[o["glass"]],named[f]) for f in o["frame_members"])
  assert len({p["seam"] for p in g["party_walls"]})==len(g["party_walls"])
  assert all(m.get("unit") in {b["unit"] for b in g["balconies"]} for m in g["meshes"] if str(m.get("carrier_kind","")).startswith("balcony_"))
  assert all(len(m["faces"])==len(m["face_owners"]) and all(len(o)==1 and o[0] for o in m["face_owners"]) for m in g["meshes"])
  names=[m["name"] for m in g["meshes"]]
  assert len(names)==len(set(names)),"mesh names must be globally unique for name-keyed ownership"
  assert all(m["sticker_owner_id"] and all(owner==[m["sticker_owner_id"]] for owner in m["face_owners"]) for m in g["meshes"])
def test_party_schedule_matches_disjoint_main_airwell_service_roofs(c,e):
 for g in(c,e):
  named={m["name"]:m for m in g["meshes"]}
  for party in g["party_walls"]:
   assert party["main_profile"]==[(-14.,8.25),(-5.9,11.0),(2.2,8.25)]
   assert party["service_profile"]==[(5.3,6.1),(9.65,7.35),(14.,6.1)]
   assert party["open_sky_y_range_m"]==[2.2,5.2]
   walls=[named[n] for n in party["walls"]]
   main=next(m for m in walls if m.get("zone")=="main")
   service=next(m for m in walls if m.get("zone")=="service")
   airwell=next(m for m in walls if m.get("carrier_kind")=="airwell_vertical_party_wall")
   cap=next(m for m in walls if m.get("carrier_kind")=="airwell_party_wall_cap")
   assert main["roof_profile_points"]==party["main_profile"]
   assert service["roof_profile_points"]==party["service_profile"]
   assert (min(v[1] for v in airwell["vertices"]),max(v[1] for v in airwell["vertices"]))==pytest.approx((2.2,5.2))
   assert cap["not_roofing"] and max(v[2] for v in cap["vertices"])==pytest.approx(2.5)
   copings=[named[n] for n in party["copings"]]
   assert {m["zone"] for m in copings}=={"main","service"}
   # No roof-following coping or ridge bridges any positive open-well interval.
   assert not [m for m in copings if min(v[1] for v in m["vertices"])<5.2 and max(v[1] for v in m["vertices"])>2.2]
def test_arcade_seams_have_no_full_height_blocker(c,e):
 for g in(c,e):
  # Structural arcade columns may edge a seam; no wall or opaque carrier spans
  # the open five-foot-way height and depth at an internal seam.
  blockers=[]
  for m in g["meshes"]:
   if m.get("carrier_kind") in {"arcade_column","open_tunnel_surface"}:continue
   xs=[v[0] for v in m["vertices"]];ys=[v[1] for v in m["vertices"]];zs=[v[2] for v in m["vertices"]]
   for seam in range(1,g["unit_contract"]["count"]):
    x=-g["dimensions"]["width_m"]/2+seam*M.UW
    if min(xs)<x<max(xs) and min(ys)<-12.3 and max(ys)>-14 and min(zs)<4.0 and max(zs)>0.12: blockers.append((m["name"],seam))
  assert not blockers
def test_end_gable_terminal_no_longer_forms_arcade_corner_l(c,e):
 for g in(c,e):
  lowers=[m for m in g["meshes"] if m.get("carrier_kind")=="row_end_gable_wall"]
  uppers=[m for m in g["meshes"] if m.get("carrier_kind")=="row_end_gable_upper_closure"]
  assert len(lowers)==len(uppers)==2
  assert all(m["terminal_overlap_fix"] and m["starts_behind_arcade"] and min(v[1] for v in m["vertices"])==pytest.approx(-14+M.TD) for m in lowers)
  assert all(m["terminal_overlap_fix"] and m["clear_above_arcade"] and min(v[2] for v in m["vertices"])==pytest.approx(4.25) for m in uppers)
  # No end-gable solid occupies the public tunnel volume y<backline,z<4.25.
  for m in lowers+uppers:
   ys=[v[1] for v in m["vertices"]];zs=[v[2] for v in m["vertices"]]
   assert not (min(ys)<-14+M.TD and min(zs)<4.25)
def test_cycles_risk_no_soffit_column_overlap_and_owned_pale_endcaps(c,e):
 def bounds(m):return tuple(f(v[i] for v in m["vertices"]) for i in range(3) for f in(min,max))
 def overlap(a,z):
  x,y=bounds(a),bounds(z);return all(min(x[i+1],y[i+1])-max(x[i],y[i])>1e-8 for i in(0,2,4))
 for g in(c,e):
  beams=[m for m in g["meshes"] if m.get("carrier_kind")=="tunnel_soffit_beam"]
  columns=[m for m in g["meshes"] if m.get("carrier_kind")=="arcade_column"]
  caps=[m for m in g["meshes"] if m.get("carrier_kind")=="pale_trim_endpoint_cap"]
  assert len(beams)==g["unit_contract"]["count"] and len(caps)==2*g["unit_contract"]["count"]
  assert all(not overlap(beam,column) for beam in beams for column in columns)
  assert all(not overlap(cap,column) for cap in caps for column in columns)
  assert all(m["material_domain"]=="plaster_trim" and m["sticker_owner_id"]=="sticker_pale_trim_endpoint" and m["outward_terminal_faces"] and m["cycles_overlap_fix"] for m in caps)
  assert all(len(m["faces"])==len(m["face_owners"]) and all(o==["sticker_pale_trim_endpoint"] for o in m["face_owners"]) for m in caps)
  # Beam/cap pairs terminate on exact x planes, never overlap positively.
  for tunnel in g["tunnels"]:
   named={m["name"]:m for m in g["meshes"]};beam=named[next(n for n in tunnel["parts"] if n.endswith("soffit_beam"))]
   for name in tunnel["endpoint_caps"]:
    cap=named[name];assert not overlap(beam,cap)
def test_hashes(c,e):
 assert M.build_geometry("canonical")["geometry_sha256"]==c["geometry_sha256"] and M.build_geometry("extended")["geometry_sha256"]==e["geometry_sha256"] and c["geometry_sha256"]!=e["geometry_sha256"]
def test_unknown():
 with pytest.raises(KeyError):M.build_geometry("elastic")
