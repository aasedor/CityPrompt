from __future__ import annotations

import importlib.util
from pathlib import Path
import pytest

MODULE_PATH=Path(__file__).parents[1]/"build_halifax_waterfront_warehouse_sticker_lego_v98.py"
SPEC=importlib.util.spec_from_file_location("halifax_warehouse_v98",MODULE_PATH);assert SPEC and SPEC.loader
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)

@pytest.fixture(scope="module")
def canonical(): return MODULE.build_geometry("canonical")

@pytest.fixture(scope="module")
def extended(): return MODULE.build_geometry("extended")

def test_exact_image_identity_overrides_conflicting_metadata(canonical):
    assert len(canonical["reference_evidence"])==3
    assert canonical["dimensions"]=={"width_m":20.0,"depth_m":15.0,"occupied_storeys":2,"wall_top_m":9.7,"parapet_top_m":11.82}
    assert len(canonical["floor_bands"])==2
    assert "no_gable_roof_or_stone_warehouse_substitution" in canonical["geometry_hard_stops"]

def test_extended_adds_only_two_complete_front_bays(canonical,extended):
    assert extended["dimensions"]["width_m"]==25.0
    assert extended["dimensions"]["depth_m"]==canonical["dimensions"]["depth_m"]==15.0
    assert extended["dimensions"]["occupied_storeys"]==2
    assert extended["structural_grid"]["ordinary_front_bays"]-canonical["structural_grid"]["ordinary_front_bays"]==2
    assert extended["fixed_modules"]==canonical["fixed_modules"]

def test_upper_windows_are_true_round_arch_assemblies(canonical):
    named={m["name"]:m for m in canonical["meshes"]}; names=set(named)
    upper=[a for a in canonical["apertures"] if a["level"]==1]
    assert upper and all(a["shape"]=="true_round_arch" for a in upper)
    for a in upper:
        assert a["flat_printed_void"] is False and a["recess_depth_m"]>=.7
        assert len(a["contour_uz_m"])>=15 and len(a["arch_surround_meshes"])>=15
        assert len(a["outer_archivolt_meshes"])>=15 and len(a["impost_meshes"])==2
        assert set(a["return_meshes"]+a["arch_surround_meshes"]+a["outer_archivolt_meshes"]+a["impost_meshes"]+a["mullion_meshes"])<=names
        assert a["keystone_mesh"] in names
        assert a["recessed_glass_mesh"] in names and a["interior_card_mesh"] in names
        glass=named[a["recessed_glass_mesh"]];card=named[a["interior_card_mesh"]]
        for carrier in (glass,card):
            assert carrier["clipped_to_arch_contour"] is True
            assert carrier["carrier_shape"]=="split_rectangle_plus_semicircular_fan"
            assert len(carrier["faces"])==13
            assert len(carrier["faces"][0])==4
            assert all(len(face)==3 for face in carrier["faces"][1:])

def test_upper_glass_and_cards_have_no_vertices_outside_approved_arch(canonical):
    named={m["name"]:m for m in canonical["meshes"]}
    for aperture in [a for a in canonical["apertures"] if a["level"]==1]:
        contour=aperture["contour_uz_m"]
        u0,u1=contour[0][0],contour[1][0]; sill=contour[0][1]; spring=contour[2][1]
        centre=(u0+u1)/2; radius=(u1-u0)/2
        for mesh_name in (aperture["recessed_glass_mesh"],aperture["interior_card_mesh"]):
            mesh=named[mesh_name]
            # Convert oriented world positions back to aperture u/z.
            if aperture["side"]=="front": uz=[(v[0],v[2]) for v in mesh["vertices"]]
            elif aperture["side"]=="rear": uz=[(-v[0],v[2]) for v in mesh["vertices"]]
            elif aperture["side"]=="left": uz=[(-v[1],v[2]) for v in mesh["vertices"]]
            else: uz=[(v[1],v[2]) for v in mesh["vertices"]]
            for u,z in uz:
                assert u0-1e-8<=u<=u1+1e-8 and z>=sill-1e-8
                if z>spring:
                    assert (u-centre)**2+(z-spring)**2<=radius**2+1e-7

def test_above_arch_brick_closures_are_closed_non_overlapping_solids(canonical):
    spandrels=[m for m in canonical["meshes"] if m.get("carrier_kind")=="closed_above_arch_brick_closure"]
    upper=[a for a in canonical["apertures"] if a["level"]==1]
    assert len(spandrels)==len(upper)*12
    assert not [m for m in canonical["meshes"] if m["name"].endswith("_brick_head")]
    grouped={a["aperture_id"]:[] for a in upper}
    for mesh in spandrels:
        aperture_id=mesh["name"].rsplit("_above_arch_brick_closure_",1)[0]
        grouped[aperture_id].append(mesh)
        assert mesh["watertight"] and mesh["consistent_outward_winding"]
        assert mesh["non_overlapping_tile"] and len(mesh["faces"])==6
        assert mesh["replaces_overlapping_brick_head"] is True
        # Closed quad prism topology: 8 vertices, and each undirected edge is
        # referenced by exactly two faces.
        assert len(mesh["vertices"])==8
        edges={}
        for face in mesh["faces"]:
            for a,b in zip(face,face[1:]+face[:1]):
                edge=tuple(sorted((a,b)));edges[edge]=edges.get(edge,0)+1
        assert set(edges.values())=={2}
    for tiles in grouped.values():
        intervals=sorted(tuple(m["arc_interval_u_m"]) for m in tiles)
        assert all(a1<=b0+1e-9 for (_,a1),(b0,_) in zip(intervals,intervals[1:]))

def test_all_above_arch_visible_caps_have_outward_normals(canonical):
    outward={"front":(0,-1,0),"rear":(0,1,0),"left":(-1,0,0),"right":(1,0,0)}
    closures=[m for m in canonical["meshes"] if m.get("carrier_kind")=="closed_above_arch_brick_closure"]
    assert {m["side"] for m in closures}==set(outward)
    for mesh in closures:
        face=mesh["faces"][mesh["exterior_face_index"]]
        a,b,c=(mesh["vertices"][i] for i in face[:3])
        ab=tuple(b[i]-a[i] for i in range(3));ac=tuple(c[i]-a[i] for i in range(3))
        normal=(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])
        assert sum(normal[i]*outward[mesh["side"]][i] for i in range(3))>1e-8
        # The cap must be red-brick owned on every engine, not an inward or
        # default-material face accidentally exposed above the arch.
        assert mesh["material_domain"]=="red_brick"
        assert mesh["face_owners"][mesh["exterior_face_index"]]==[mesh["sticker_owner_id"]]

def test_ground_openings_are_deep_and_entry_is_singular(canonical):
    ground=[a for a in canonical["apertures"] if a["level"]==0]
    entries=[a for a in ground if a["kind"]=="entrance"]
    assert len(entries)==1 and entries[0]["side"]=="front" and entries[0]["fixed_identity"]
    assert all(a["recess_depth_m"]>=.68 and len(a["return_meshes"])==4 for a in ground)
    assert all(not a["flat_printed_void"] for a in ground)
    names={m["name"]:m for m in canonical["meshes"]}
    assert all(len(a["storefront_frame_meshes"])>=8 for a in ground)
    for aperture in ground:
        frames=[names[name] for name in aperture["storefront_frame_meshes"]]
        assert all(frame["material_domain"]=="dark_green_painted_metal" for frame in frames)
        assert any("high_transom" in frame["name"] for frame in frames)
        assert any("lower_rail" in frame["name"] for frame in frames)
        assert any("stall_riser" in frame["name"] for frame in frames)
    assert len(entries[0]["paired_door_leaf_meshes"])==2
    assert all(names[name]["carrier_kind"]=="paired_entrance_door_leaf" for name in entries[0]["paired_door_leaf_meshes"])

def test_every_transmissive_aperture_has_separate_interior_card(canonical):
    names={m["name"]:m for m in canonical["meshes"]}
    for a in canonical["apertures"]:
        glass=names[a["recessed_glass_mesh"]];card=names[a["interior_card_mesh"]]
        assert glass["carrier_kind"]=="recessed_glass"
        assert card["carrier_kind"]=="recessed_interior_card" and card["behind_glass_m"]>0
        assert set(card["face_roles"])=={"interior_card"}

def test_stone_hierarchy_cornice_modillions_and_roof_are_physical(canonical):
    meshes=canonical["meshes"]
    assert len(canonical["quoin_meshes"])==40
    assert len(canonical["cornice"]["layer_meshes"])==4
    assert len(canonical["cornice"]["modillion_meshes"])>=60
    assert len(canonical["roof"]["parapet_meshes"])==4 and len(canonical["roof"]["coping_meshes"])==4
    corner_caps=[next(m for m in meshes if m["name"]==name) for name in canonical["roof"]["coping_corner_cap_meshes"]]
    assert len(corner_caps)==4 and {m["coping_corner"] for m in corner_caps}=={"front_left","front_right","rear_left","rear_right"}
    assert all(m["watertight"] and len(m["faces"])==6 for m in corner_caps)
    assert all(m["material_domain"]=="patinated_coping" for m in corner_caps)
    assert all(set(owner[0] for owner in m["face_owners"])=={m["sticker_owner_id"]} for m in corner_caps)
    straight=[next(m for m in meshes if m["name"]==name) for name in canonical["roof"]["coping_meshes"]]
    # Straight runs and corner caps may meet on a boundary but cannot overlap
    # in both horizontal axes with positive area.
    def xy_bounds(mesh):
        return min(v[0] for v in mesh["vertices"]),max(v[0] for v in mesh["vertices"]),min(v[1] for v in mesh["vertices"]),max(v[1] for v in mesh["vertices"])
    for run in straight:
        rx0,rx1,ry0,ry1=xy_bounds(run)
        for cap in corner_caps:
            cx0,cx1,cy0,cy1=xy_bounds(cap)
            overlap_x=min(rx1,cx1)-max(rx0,cx0)
            overlap_y=min(ry1,cy1)-max(ry0,cy0)
            assert overlap_x<=1e-9 or overlap_y<=1e-9
    assert canonical["roof"]["stepped_front_mesh"]
    stepped=[next(m for m in meshes if m["name"]==name) for name in canonical["roof"]["stepped_front_subpart_meshes"]]
    assert {m["carrier_kind"] for m in stepped}>={"stepped_front_parapet_brick_infill","stepped_parapet_stone_upright","stepped_parapet_pilaster_cap","stepped_parapet_layered_coping","stepped_parapet_continued_cornice"}
    assert all(len(m["face_owners"])==len(m["faces"]) for m in stepped)
    chimneys=canonical["roof"]["chimney_assemblies"]
    assert canonical["fixed_modules"]["chimneys"]==2 and len(chimneys)==2
    assert len({c["assembly_id"] for c in chimneys})==2
    assert all(c["shaft_mesh"]!=c["cap_mesh"] for c in chimneys)
    assert len({c["shaft_mesh"] for c in chimneys})==2 and len({c["cap_mesh"] for c in chimneys})==2
    assert len(canonical["roof"]["vent_meshes"])==2
    assert len([m for m in meshes if m.get("carrier_kind")=="roof_deck"])==1

def test_secondary_elevations_are_covered_and_constrained(canonical):
    assert canonical["completion_policy"]["rear"].endswith("no_invented_entry")
    for side in ("left","rear"):
        apertures=[a for a in canonical["apertures"] if a["side"]==side]
        assert apertures and all(a["completion_evidence"]=="constrained" for a in apertures)
        assert not [a for a in apertures if a["kind"]=="entrance"]

def test_every_face_has_exactly_one_owner(canonical,extended):
    for geometry in (canonical,extended):
        for mesh in geometry["meshes"]:
            assert len(mesh["faces"])==len(mesh["face_owners"])
            assert all(len(owner)==1 and owner[0] for owner in mesh["face_owners"])

def test_hashes_are_deterministic_and_tier_specific(canonical,extended):
    assert MODULE.build_geometry("canonical")["geometry_sha256"]==canonical["geometry_sha256"]
    assert MODULE.build_geometry("extended")["geometry_sha256"]==extended["geometry_sha256"]
    assert canonical["geometry_sha256"]!=extended["geometry_sha256"]

def test_unknown_tier_rejected():
    with pytest.raises(KeyError): MODULE.build_geometry("elastic")
