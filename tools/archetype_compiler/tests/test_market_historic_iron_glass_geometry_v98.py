import importlib.util
from collections import Counter
from pathlib import Path
import pytest

P=Path(__file__).parents[1]/"build_market_historic_iron_glass_sticker_lego_v98.py";S=importlib.util.spec_from_file_location("market",P);M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
@pytest.fixture(scope="module")
def g():return M.build_geometry()
def bounds(m):return tuple(f(v[i] for v in m["vertices"]) for i in range(3) for f in(min,max))
def overlap(a,b):
 x,y=bounds(a),bounds(b);return all(min(x[i+1],y[i+1])-max(x[i],y[i])>1e-8 for i in(0,2,4))
def face_normal(m):
 a,b,c=(m["vertices"][i] for i in m["faces"][0][:3]);u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
 return (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])

def test_fixed_landmark_dimensions_and_evidence(g):
 assert g["dimensions"]=={"width_m":45.,"depth_m":60.,"occupied_hall_levels":1,"partial_mezzanines":2,"nave_width_m":27.,"aisle_width_m":9.,"spring_m":8.35,"barrel_crown_m":15.35,"lantern_crown_m":16.72}
 assert g["scale_contract"]=={"canonical":"45x60","fixed_landmark":True,"extended_tier":None,"nonuniform_scale_forbidden":True}
 assert len(g["reference_evidence"])==3 and all(Path(__file__).parents[3].joinpath(p).is_file() for p in g["reference_evidence"])
 with pytest.raises(KeyError):M.build_geometry("extended")

def test_one_hall_two_mezzanines_and_clear_nave(g):
 k=Counter(m.get("carrier_kind") for m in g["meshes"])
 assert k["open_market_floor"]==1 and k["gallery_deck"]==k["gallery_soffit"]==k["gallery_edge_girder"]==2
 decks=[m for m in g["meshes"] if m.get("carrier_kind")=="gallery_deck"]
 assert all(bounds(m)[1]<=-13.5 or bounds(m)[0]>=13.5 for m in decks)
 assert all(not (bounds(m)[0]<13.5 and bounds(m)[1]>-13.5) for m in decks)
 assert all(not overlap(a,b) for i,a in enumerate(decks) for b in decks[i+1:])

def test_eight_complete_frame_lines_and_seven_bays(g):
 assert len(g["frame_lines"])==8 and len(set(round(g["frame_lines"][i+1]-g["frame_lines"][i],2) for i in range(7)))==1
 k=Counter(m.get("carrier_kind") for m in g["meshes"])
 assert k["cast_iron_column_base"]==k["cast_iron_column_shaft"]==k["cast_iron_column_capital"]==k["gallery_upper_iron_post"]==16
 assert k["barrel_truss_rib"]==160 and k["iron_cross_tie"]==8
 for frame in range(8):
  assert len([m for m in g["meshes"] if m.get("frame")==frame and m.get("carrier_kind")=="barrel_truss_rib"])==20

def test_open_front_cavern_and_physical_gable(g):
 k=Counter(m.get("carrier_kind") for m in g["meshes"])
 assert k["front_terminal_stone_pier"]==2 and k["front_gable_arch_ring"]==24
 assert k["front_iron_lattice_girder"]==1 and k["iron_lattice_diagonal"]==24
 assert k["front_gable_mullion"]==19 and k["front_gable_glass"]==18 and k["front_gable_horizontal_rail"]==3
 assert k["occupied_front_side_bay"]==k["front_timber_stall"]==k["front_stall_door"]==0
 assert k["recessed_shop_back_wall"]==10 and k["recessed_shopfront_joinery"]==18
 assert k["recessed_shopfront_glass"]==k["recessed_shopfront_card"]==k["recessed_shopfront_backing"]==4
 assert k["recessed_shop_counter"]==2 and k["recessed_shop_counter_cavity"]==0
 assert k["recessed_shop_bay_side_cue"]==4 and k["recessed_shop_bay_ceiling_cue"]==2
 assert k["front_iron_half_gable"]==2 and k["front_side_fan_glass"]==8
 assert k["front_principal_column"]==k["front_principal_capital"]==2
 assert not [m for m in g["meshes"] if m.get("carrier_kind") in {"constrained_rear_wall","side_brick_pier"} and bounds(m)[2]<-29.28]

def test_fourteen_real_side_arches_are_panelized_and_optically_ordered(g):
 assert len(g["apertures"])==14 and {a["side"] for a in g["apertures"]}=={"left","right"}
 named={m["name"]:m for m in g["meshes"]}
 for a in g["apertures"]:
  glass,card,back=(named[a[x]] for x in ("glass","card","backing"));gx=bounds(glass)[0];cx=bounds(card)[0];bx=bounds(back)[0]
  assert (gx>cx>bx) if a["side"]=="right" else (gx<cx<bx)
  assert abs(gx-cx)==pytest.approx(.06)
  assert not overlap(glass,card) and not overlap(card,back)
 k=Counter(m.get("carrier_kind") for m in g["meshes"])
 assert k["aperture_sill_wall"]==k["aperture_head_wall"]==14
 assert k["physical_arch_ring"]==140 and k["arch_jamb_return"]==28 and k["arch_sill_return"]==14

def test_closed_barrel_asymmetric_aisles_rooflights_and_lantern(g):
 k=Counter(m.get("carrier_kind") for m in g["meshes"])
 assert k["barrel_glass_panel"]==30 and k["barrel_longitudinal_rail"]==30
 panels=[m for m in g["meshes"] if m.get("carrier_kind")=="barrel_glass_panel"]
 assert all(m["watertight"] and m["closed"] and m["outward_winding"] for m in panels)
 aisle=[m for m in g["meshes"] if m.get("carrier_kind")=="closed_aisle_roof_panel"]
 assert len(aisle)==30 and {m["material_domain"] for m in aisle}=={"slate_roof","standing_seam_zinc"}
 assert all(m["asymmetric_finish"] for m in aisle)
 assert k["rooflight_curb"]==32 and k["rooflight_glass"]==8
 assert k["zinc_roof_dormer"]==1 and k["zinc_roof_dormer_wall"]==0
 assert k["ridge_lantern_sill_head_rail"]==4 and k["ridge_lantern_frame_post"]==20
 assert k["ridge_lantern_glass"]==18 and k["ridge_lantern_end"]==2 and k["ridge_lantern_cap"]==1
 rooflights=[m for m in g["meshes"] if m.get("carrier_kind")=="rooflight_curb"]
 assert all(not overlap(a,b) for a in rooflights for b in aisle)
 assert all(bounds(m)[2]==pytest.approx(-30.) or bounds(m)[3]==pytest.approx(30.) or (bounds(m)[2]>-30 and bounds(m)[3]<30) for m in aisle)

def test_rear_and_terminal_completion_do_not_intersect(g):
 rear=[m for m in g["meshes"] if m.get("carrier_kind")=="constrained_rear_wall"]
 sides=[m for m in g["meshes"] if m.get("carrier_kind") in {"side_brick_pier","stone_end_quoin","side_wall_coping"}]
 assert len(rear)==3 and len([m for m in g["meshes"] if m.get("carrier_kind")=="rear_service_door"])==1
 assert len([m for m in g["meshes"] if m.get("carrier_kind")=="rear_gable_arch_ring"])==36
 assert len([m for m in g["meshes"] if m.get("carrier_kind")=="rear_gable_glass"])==18
 assert len([m for m in g["meshes"] if m.get("carrier_kind")=="rear_gable_mullion"])==19
 assert len([m for m in g["meshes"] if m.get("carrier_kind")=="rear_gable_horizontal_rail"])==3
 assert len([m for m in g["meshes"] if m.get("carrier_kind")=="rear_spring_pier"])==2
 assert len([m for m in g["meshes"] if m.get("carrier_kind")=="rear_spring_capital"])==2
 assert len([m for m in g["meshes"] if m.get("carrier_kind")=="rear_fan_spring_sill"])==1
 assert all(not overlap(a,b) for a in rear for b in sides)

def test_binding_section_and_roof_aperture_topology(g):
 columns=[m for m in g["meshes"] if m.get("carrier_kind")=="cast_iron_column_shaft"]
 assert {round((bounds(m)[0]+bounds(m)[1])/2,1) for m in columns}=={-13.5,13.5}
 assert all(m["lands_at_spring"] for m in g["meshes"] if m.get("carrier_kind") in {"iron_cross_tie","front_principal_column","front_principal_capital"})
 panels=[m for m in g["meshes"] if m.get("carrier_kind") in {"barrel_glass_panel","closed_aisle_roof_panel"}]
 assert all(bounds(m)[2]>=-30 and bounds(m)[3]<=30 for m in panels)
 lantern=[m for m in g["meshes"] if m.get("carrier_kind") in {"ridge_lantern_sill_head_rail","ridge_lantern_frame_post","ridge_lantern_end","ridge_lantern_cap"}]
 ribs=[m for m in g["meshes"] if m.get("carrier_kind") in {"barrel_truss_rib","barrel_longitudinal_rail"}]
 assert all(not overlap(a,b) for a in lantern for b in ribs)
 assert all(m["slope_aligned"] for m in g["meshes"] if m.get("carrier_kind") in {"rooflight_curb","rooflight_glass"})

def test_literal_front_cavern_roof_verges_and_cutouts(g):
 # No opaque occupied frontage may intrude into the exact 27 m cavern below
 # the fan; the two 9 m side territories remain physically occupied.
 opaque={"recessed_shop_back_wall","recessed_shop_counter","front_terminal_stone_pier"}
 front=[m for m in g["meshes"] if m.get("carrier_kind") in opaque]
 assert all(bounds(m)[1]<=-13.5 or bounds(m)[0]>=13.5 for m in front)
 assert {m["side"] for m in g["meshes"] if m.get("carrier_kind")=="recessed_shop_counter"}=={"left","right"}
 # Every roof family reaches both gable/verge planes; openings are real gaps
 # in the panel schedule rather than glass laid over an uncut roof.
 barrel=[m for m in g["meshes"] if m.get("carrier_kind")=="barrel_glass_panel"]
 aisle=[m for m in g["meshes"] if m.get("carrier_kind")=="closed_aisle_roof_panel"]
 assert min(bounds(m)[2] for m in barrel)==pytest.approx(-30.) and max(bounds(m)[3] for m in barrel)==pytest.approx(30.)
 for side in ("left","right"):
  side_panels=[m for m in aisle if m["side"]==side]
  assert min(bounds(m)[2] for m in side_panels)==pytest.approx(-30.)
  assert max(bounds(m)[3] for m in side_panels)==pytest.approx(30.)
 for light in [m for m in g["meshes"] if m.get("carrier_kind") in {"rooflight_curb","rooflight_glass"}]:
  assert all(not overlap(light,p) for p in aisle)

def test_open_lantern_fan_envelopes_and_dormer_cut(g):
 k=Counter(m.get("carrier_kind") for m in g["meshes"])
 # No side-long opaque lantern slab remains: each side has two rails, ten
 # posts, and nine unobscured panes bounded inside those frames.
 assert not [m for m in g["meshes"] if m.get("carrier_kind")=="ridge_lantern_frame"]
 for side in ("left","right"):
  rails=[m for m in g["meshes"] if m.get("carrier_kind")=="ridge_lantern_sill_head_rail" and m["side"]==side]
  posts=[m for m in g["meshes"] if m.get("carrier_kind")=="ridge_lantern_frame_post" and m["side"]==side]
  panes=[m for m in g["meshes"] if m.get("carrier_kind")=="ridge_lantern_glass" and m["side"]==side]
  assert len(rails)==2 and len(posts)==10 and len(panes)==9
  assert all(m["exposed_between_frames"] and bounds(m)[4]>15.12 and bounds(m)[5]<16.38 for m in panes)
 # The main fan reaches both spring lines; every pane has independently
 # evaluated curved endpoints and every rail is clipped inside the ellipse.
 for prefix in ("front","rear"):
  panes=[m for m in g["meshes"] if m.get("carrier_kind")==f"{prefix}_gable_glass"]
  mullions=[m for m in g["meshes"] if m.get("carrier_kind")==f"{prefix}_gable_mullion"]
  rails=[m for m in g["meshes"] if m.get("carrier_kind")==f"{prefix}_gable_horizontal_rail"]
  assert min(bounds(m)[0] for m in mullions)==pytest.approx(-13.535)
  assert max(bounds(m)[1] for m in mullions)==pytest.approx(13.535)
  assert all(m["endpoint_clipped"] and m["vertices"][2][2]!=pytest.approx(m["vertices"][3][2]) for m in panes if abs((bounds(m)[0]+bounds(m)[1])/2)>.1)
  for rail in rails:
   z=(bounds(rail)[4]+bounds(rail)[5])/2
   assert bounds(rail)[1] <= M.ellipse_x(z)-.17
 # The dormer is one closed shell seated on the right aisle slope and its
 # entire 15.15..19.50 by 20..24 footprint is absent from the roof panels.
 dormer=[m for m in g["meshes"] if m.get("carrier_kind")=="zinc_roof_dormer"]
 assert len(dormer)==1 and dormer[0]["closed"] and dormer[0]["slope_following_base"] and dormer[0]["closed_end_caps"]
 assert bounds(dormer[0])[:4]==pytest.approx((15.15,19.50,20.,24.))
 assert all(not overlap(dormer[0],p) for p in g["meshes"] if p.get("carrier_kind")=="closed_aisle_roof_panel")

def test_side_fans_are_slope_clipped_and_rear_spring_is_closed(g):
 side_fans=[m for m in g["meshes"] if m.get("carrier_kind")=="front_side_fan_glass"]
 assert len(side_fans)==8 and all(m["endpoint_clipped"] for m in side_fans)
 assert all(m["vertices"][2][2]!=pytest.approx(m["vertices"][3][2]) for m in side_fans)
 rear=[m for m in g["meshes"] if m.get("carrier_kind") in {"constrained_rear_wall","rear_spring_pier","rear_spring_capital"}]
 capitals=[m for m in rear if m.get("carrier_kind")=="rear_spring_capital"]
 assert {round((bounds(m)[0]+bounds(m)[1])/2,1) for m in capitals}=={-13.5,13.5}
 assert all(bounds(m)[3]==pytest.approx(30.) and bounds(m)[4]==pytest.approx(8.) and bounds(m)[5]==pytest.approx(8.38) and m["material_domain"]=="painted_iron" for m in capitals)
 walls=[m for m in rear if m.get("carrier_kind")=="constrained_rear_wall"]
 piers=[m for m in rear if m.get("carrier_kind") in {"rear_spring_pier","rear_spring_capital"}]
 assert all(not overlap(a,b) for a in walls for b in piers)

def test_ridge_end_bands_rear_sill_and_pane_winding(g):
 end_glass=[m for m in g["meshes"] if m.get("carrier_kind")=="barrel_ridge_end_glass_panel"]
 end_rails=[m for m in g["meshes"] if m.get("carrier_kind")=="barrel_ridge_end_rail"]
 assert len(end_glass)==12 and len(end_rails)==14
 for end,ya,yb in (("front",-30.,-27.2),("rear",27.2,30.)):
  glass=[m for m in end_glass if m["end"]==end];rails=[m for m in end_rails if m["end"]==end]
  assert len(glass)==6 and len(rails)==7
  assert min(bounds(m)[0] for m in glass+rails)<=-2.30 and max(bounds(m)[1] for m in glass+rails)>=2.30
  assert min(bounds(m)[2] for m in glass+rails)==pytest.approx(ya) and max(bounds(m)[3] for m in glass+rails)==pytest.approx(yb)
  assert all(m["closed"] and m["outward_winding"] for m in glass+rails)
 sill=[m for m in g["meshes"] if m.get("carrier_kind")=="rear_fan_spring_sill"]
 assert len(sill)==1 and bounds(sill[0])==pytest.approx((-13.,13.,29.62,30.,8.,8.38))
 walls=[m for m in g["meshes"] if m.get("carrier_kind")=="constrained_rear_wall"]
 assert all(not overlap(sill[0],w) for w in walls)
 left=[m for m in g["meshes"] if m.get("carrier_kind")=="ridge_lantern_glass" and m["side"]=="left"]
 right=[m for m in g["meshes"] if m.get("carrier_kind")=="ridge_lantern_glass" and m["side"]=="right"]
 assert all(face_normal(m)[0]<0 for m in left) and all(face_normal(m)[0]>0 for m in right)
 fans=[m for m in g["meshes"] if m.get("carrier_kind")=="front_side_fan_glass"]
 assert sum(bool(m["triangular_outer_taper"]) for m in fans)==2
 assert all(m["vertices"][3][2]>m["vertices"][0][2] and m["vertices"][2][2]>m["vertices"][1][2] for m in fans)
 assert all(face_normal(m)[1]<0 for m in fans)

def test_side_aisle_entries_are_open_and_shops_are_recessed(g):
 assert not [m for m in g["meshes"] if m.get("carrier_kind") in {"occupied_front_side_bay","front_timber_stall","front_stall_door"}]
 # There is no closure within the first four metres behind either side-bay
 # frontage; the first shop fabric and joinery is about 4.7 m inboard.
 shop_kinds={"recessed_shop_back_wall","recessed_shopfront_joinery","recessed_shopfront_glass","recessed_shopfront_card","recessed_shopfront_backing","recessed_shop_counter","recessed_shop_bay_side_cue","recessed_shop_bay_ceiling_cue"}
 shops=[m for m in g["meshes"] if m.get("carrier_kind") in shop_kinds]
 assert min(bounds(m)[2] for m in shops)>-25.7
 for side in ("left","right"):
  glass=[m for m in shops if m.get("carrier_kind")=="recessed_shopfront_glass" and m["side"]==side]
  cards=[m for m in shops if m.get("carrier_kind")=="recessed_shopfront_card" and m["side"]==side]
  backs=[m for m in shops if m.get("carrier_kind")=="recessed_shopfront_backing" and m["side"]==side]
  assert len(glass)==len(cards)==len(backs)==2
  assert max(bounds(m)[2] for m in glass)<min(bounds(m)[2] for m in cards)<min(bounds(m)[2] for m in backs)
  assert min(bounds(m)[2] for m in cards)-max(bounds(m)[2] for m in glass)==pytest.approx(.035)
  assert all(m["brought_forward_for_cycles"] for m in cards)
  assert all(not overlap(a,b) for a in glass for b in cards+backs)
  joinery=[m for m in shops if m.get("carrier_kind")=="recessed_shopfront_joinery" and m["side"]==side]
  assert len(joinery)==9 and all(not overlap(a,b) for i,a in enumerate(joinery) for b in joinery[i+1:])
  cues=[m for m in shops if m.get("carrier_kind") in {"recessed_shop_bay_side_cue","recessed_shop_bay_ceiling_cue"} and m["side"]==side]
  assert len(cues)==3 and all(bounds(c)[2]>bounds(cards[0])[2] and bounds(c)[3]<bounds(backs[0])[2] for c in cues)
 walls=[m for m in shops if m.get("carrier_kind")=="recessed_shop_back_wall"]
 assert {m["part"] for m in walls}=={"left","right","sill","lower_head","upper"}
 # Galleries, soffits, edge girders and longitudinal rails now meet the
 # principal frontage structure rather than stopping at the first frame line.
 for kind in ("gallery_deck","gallery_soffit","gallery_edge_girder","gallery_rail_top","gallery_rail_mid"):
  members=[m for m in g["meshes"] if m.get("carrier_kind")==kind]
  assert len(members)==2 and all(bounds(m)[2]==pytest.approx(-29.66) and m["extended_to_entrance"] for m in members)
 decks={m["side"]:m for m in g["meshes"] if m.get("carrier_kind")=="gallery_deck"}
 soffits={m["side"]:m for m in g["meshes"] if m.get("carrier_kind")=="gallery_soffit"}
 assert bounds(decks["left"])[0]==bounds(soffits["left"])[0]==pytest.approx(-21.45)
 assert bounds(decks["right"])[1]==bounds(soffits["right"])[1]==pytest.approx(21.45)
 uppers=[m for m in walls if m["part"]=="upper"]
 assert len(uppers)==2 and all(m["slope_capped"] and m["roof_clearance_m"]==pytest.approx(.22) and m["clear_of_roof_underside_m"]==pytest.approx(.04) for m in uppers)
 for m in uppers:
  for x in {v[0] for v in m["vertices"]}:
   wall_top=max(v[2] for v in m["vertices"] if v[0]==x)
   roof_underside=M.aisle_z(m["side"],x)-.18
   assert wall_top==pytest.approx(M.aisle_z(m["side"],x)-.22)
   assert wall_top<roof_underside and roof_underside-wall_top==pytest.approx(.04)
  matching=[r for r in g["meshes"] if r.get("carrier_kind")=="closed_aisle_roof_panel" and r["side"]==m["side"] and bounds(r)[2]<=bounds(m)[2] and bounds(r)[3]>=bounds(m)[3]]
  assert len(matching)==1
  roof=matching[0];rx0,rx1=bounds(roof)[:2]
  rz0=min(v[2] for v in roof["vertices"] if v[0]==rx0);rz1=min(v[2] for v in roof["vertices"] if v[0]==rx1)
  def actual_roof_underside(x):return rz0+(rz1-rz0)*(x-rx0)/(rx1-rx0)
  # Literal non-positive-overlap proof using the matching roof mesh's actual
  # underside vertices, rather than its overly conservative sloped AABB.
  assert all(max(v[2] for v in m["vertices"] if v[0]==x)<actual_roof_underside(x) for x in {v[0] for v in m["vertices"]})

def test_historic_iron_motif_kit_is_physical_and_three_zone(g):
 k=Counter(m.get("carrier_kind") for m in g["meshes"])
 assert k["historic_curved_knee_brace"]==12 and k["historic_capital_rosette"]==2
 assert k["historic_brace_terminal_connector"]==4
 assert k["historic_shaped_spandrel"]==2
 assert k["front_gallery_filigree_rail"]==4 and k["front_gallery_filigree"]==24 and k["front_gallery_filigree_rosette"]==14
 assert {m["zone"] for m in g["meshes"] if m.get("carrier_kind")=="front_gallery_filigree_rail"}=={"left","right"}
 assert not [m for m in g["meshes"] if m.get("carrier_kind"," ").startswith("front_gallery_filigree") and m.get("zone")=="centre"]
 capitals=[m for m in g["meshes"] if m.get("carrier_kind")=="front_principal_capital"]
 assert len(capitals)==2 and all(m["shaped_historic_capital"] and len(m["vertices"])==16 for m in capitals)
 relief=[m for m in g["meshes"] if m.get("carrier_kind") in {"historic_curved_knee_brace","historic_capital_rosette","historic_shaped_spandrel","front_gallery_filigree_rosette"}]
 assert all(len(m["faces"])>1 and m["closed"] and m["outward_winding"] for m in relief)
 connectors=[m for m in g["meshes"] if m.get("carrier_kind")=="historic_brace_terminal_connector"]
 braces=[m for m in g["meshes"] if m.get("carrier_kind")=="historic_curved_knee_brace" and m["segment"]==2]
 targets=[m for m in g["meshes"] if m.get("carrier_kind") in {"front_iron_half_gable","front_iron_lattice_girder"}]
 for c in connectors:
  brace=next(m for m in braces if m["side"]==c["side"] and m["direction"]==c["direction"])
  target=next(m for m in targets if (c["target"]=="lattice" and m.get("carrier_kind")=="front_iron_lattice_girder") or (c["target"]=="half_gable" and m.get("carrier_kind")=="front_iron_half_gable" and m["side"]==c["side"]))
  assert bounds(brace)[3]==pytest.approx(bounds(c)[2]) and bounds(c)[3]==pytest.approx(bounds(target)[2])
  assert not overlap(brace,c) and not overlap(c,target)
 rails=[m for m in g["meshes"] if m.get("carrier_kind")=="front_gallery_filigree_rail" and m["part"]=="bottom"]
 decks=[m for m in g["meshes"] if m.get("carrier_kind")=="gallery_deck"]
 assert all(bounds(r)[3]==pytest.approx(-29.66) and any(bounds(d)[2]==pytest.approx(-29.66) and min(bounds(r)[1],bounds(d)[1])>max(bounds(r)[0],bounds(d)[0]) for d in decks) for r in rails)

def test_long_eave_clerestories_are_bay_split_and_closed(g):
 panes=[m for m in g["meshes"] if m.get("carrier_kind")=="eave_clerestory_glass"]
 rails=[m for m in g["meshes"] if m.get("carrier_kind")=="eave_clerestory_rail"]
 posts=[m for m in g["meshes"] if m.get("carrier_kind")=="gallery_upper_iron_post"]
 assert len(panes)==18 and len(rails)==36 and len(posts)==16
 assert all(m["supports_eave_clerestory"] and m["seated_on_edge_girder"] and bounds(m)[4]==pytest.approx(4.42) for m in posts)
 for side in ("left","right"):
  p=[m for m in panes if m["side"]==side];r=[m for m in rails if m["side"]==side]
  assert len(p)==9 and len(r)==18 and {m["bay"] for m in p}==set(range(9))
  assert min(bounds(m)[2] for m in p+r)==pytest.approx(-29.66) and max(bounds(m)[3] for m in p+r)==pytest.approx(29.62)
  assert all(bounds(m)[4]>=7.9 and bounds(m)[5]<=8.35 for m in p+r)
  assert all(not overlap(a,b) for a in r for b in posts)
  roof=[m for m in g["meshes"] if m.get("carrier_kind")=="closed_aisle_roof_panel" and m["side"]==side]
  assert all(not overlap(a,b) for a in p+r for b in roof)
  if side=="left":assert all(bounds(m)[0]>=-13.50-1e-8 and bounds(m)[1]<=-13.38+1e-8 for m in p+r)
  else:assert all(bounds(m)[0]>=13.38-1e-8 and bounds(m)[1]<=13.50+1e-8 for m in p+r)
  expected=1 if side=="left" else -1
  assert all(face_normal(m)[0]*expected>0 for m in p)

def test_cycles_occupied_bay_sightlines_have_no_dark_geometry_blocker(g):
 k=Counter(m.get("carrier_kind") for m in g["meshes"])
 assert k["recessed_shop_counter_cavity"]==0
 warm=[m for m in g["meshes"] if m.get("carrier_kind")=="gallery_bay_warm_backplane"]
 counters=[m for m in g["meshes"] if m.get("carrier_kind")=="gallery_bay_counter_front"]
 assert len(warm)==len(counters)==14
 for side in ("left","right"):
  planes=[m for m in warm if m["side"]==side];backs=[m for m in g["meshes"] if m.get("carrier_kind")=="opaque_interior_backing" and m["side"]==side]
  assert len(planes)==len(backs)==7
  expected=-1 if side=="right" else 1
  assert all(face_normal(m)[0]*expected>0 and m["nave_facing"] and m["bounded_to_arch"] for m in planes)
  for p,b in zip(sorted(planes,key=lambda m:m["name"]),sorted(backs,key=lambda m:m["name"])):
   # Warm face is on the nave side of the otherwise black optical backing.
   assert (bounds(p)[0]<bounds(b)[0]) if side=="right" else (bounds(p)[0]>bounds(b)[0])
 assert all(bounds(m)[1]<=-21.70 or bounds(m)[0]>=21.70 for m in warm+counters)

def test_unique_one_owner_closed_outward_and_deterministic(g):
 names=[m["name"] for m in g["meshes"]];assert len(names)==len(set(names))
 assert all(len(m["faces"])==len(m["face_owners"]) and all(o==[m["sticker_owner_id"]] for o in m["face_owners"]) for m in g["meshes"])
 assert all(m["closed"] and m["outward_winding"] for m in g["meshes"] if len(m["faces"])>1)
 assert M.build_geometry()["geometry_sha256"]==g["geometry_sha256"]
