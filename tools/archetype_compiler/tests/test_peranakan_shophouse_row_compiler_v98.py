from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


TOOL_DIR = Path(__file__).parents[1]
SCRIPT = TOOL_DIR / "compile_peranakan_shophouse_row_sticker_lego_v98.py"
SPEC = importlib.util.spec_from_file_location("peranakan_compiler_v98", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)


def _outputs() -> list[Path]:
    return [MODULE.OUTPUT, MODULE.REGISTRY, MODULE.PACKAGE, MODULE.CONTRACT]


def _snapshot() -> dict[str, str]:
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in _outputs()}


@pytest.fixture(scope="module")
def compiled() -> dict:
    MODULE.main(); first = _snapshot(); MODULE.main(); second = _snapshot(); assert first == second
    return {path.name: json.loads(path.read_text(encoding="utf-8")) for path in _outputs()}


def _profile(compiled: dict, size: str) -> dict:
    document = compiled[MODULE.OUTPUT.name]
    return document["profiles"][MODULE.profile_id(size)]


def test_geometry_reference_asset_locks_and_registry(compiled: dict) -> None:
    registry = compiled[MODULE.REGISTRY.name]
    assert registry["representation"] == "whole_attached_unit_lego"
    assert len(registry["registered_assets"]) == 44
    assert {tier["geometry_sha256"] for tier in registry["tiers"]} == set(MODULE.EXPECTED_GEOMETRY_HASHES.values())
    for ref, digest in MODULE.REFERENCE_HASHES.items(): assert MODULE._sha(MODULE.REPO / ref) == digest
    assert [(tier["units"], tier["width_m"]) for tier in registry["tiers"]] == [(6, 30.0), (7, 35.0)]


def test_every_visible_face_owned_exactly_once_and_roles_disjoint(compiled: dict) -> None:
    required = {"fixed_arcade_cavern", "fixed_ground_shop", "fixed_upper_residential", "fixed_crown_fretwork",
                "main_roof", "main_roof_dormer", "party_roof_boundary", "open_airwell", "constrained_rear",
                    "rear_service", "service_roof", "end_return_lower_rear", "end_return_upper_front"}
    for size in MODULE.SIZES:
        profile = _profile(compiled, size); graph = profile["massing_graph"]; audit = graph["surface_audit"]
        assert audit["status"] == "pass" and audit["visible_face_count"] == audit["owned_once_count"]
        assert not audit["missing_faces"] and not audit["multiply_owned_faces"]
        carriers = graph["assemblies"]
        assert {carrier["floor_role"] for carrier in carriers} == required
        geometry = MODULE.build_geometry(size)
        assert audit["visible_face_count"] == sum(len(mesh["faces"]) for mesh in geometry["meshes"])


def test_exact_per_unit_plaster_map_and_metric_uv_constant(compiled: dict) -> None:
    expected = {"canonical": ["turquoise", "turquoise", "coral", "ochre", "mint", "lavender"],
                "extended": ["turquoise", "turquoise", "coral", "ochre", "mint", "lavender", "cream"]}
    scales = {}
    for size, colours in expected.items():
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        for unit, colour in enumerate(colours):
            unit_carriers = [c for c in carriers if f"unit_{unit}_" in c["surface_id"] and
                             c["sticker_layer"].endswith("_plaster_front")]
            assert unit_carriers and all(c["sticker_layer"].startswith(colour + "_") for c in unit_carriers)
        for layer in ("turquoise_plaster_front", "terracotta_roof_field"):
            scales[(size, layer)] = {c["world_metric_uv_tile_m"] for c in carriers if c["sticker_layer"] == layer}
        scales[(size, "ceramic_panels")] = {c["world_metric_uv_tile_m"] for c in carriers
                                             if c["sticker_layer"].startswith("peranakan_ceramic_panel_family_")}
    for layer in ("turquoise_plaster_front", "terracotta_roof_field", "ceramic_panels"):
        assert scales[("canonical", layer)] == scales[("extended", layer)] and len(scales[("canonical", layer)]) == 1


def test_glass_cards_tile_relief_and_no_fake_geometry_assets(compiled: dict) -> None:
    provenance = MODULE._provenance()
    for record in provenance["assets"].values():
        assert not record["contains_printed_openings"]
        assert not record["contains_printed_pilasters_or_arches"]
        assert not record["contains_printed_rails_or_mullions"]
    for size in MODULE.SIZES:
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        glass = [c for c in carriers if c["material_role"] == "glass"]
        cards = [c for c in carriers if "interior_card" in c["sticker_layer"]]
        assert glass and cards and all(c["source_image_path"].endswith("physical_clear_glass_intrinsic.png") for c in glass)
        assert {c["glass_profile"] for c in glass} == {"low_iron_clear"}
        assert {c["source_image_path"].rsplit("/",1)[-1] for c in cards} == {
            "ground_shop_interior_atlas.png", "upper_residential_interior_atlas.png"}
        assert all(c["uv_u_max"]-c["uv_u_min"] == pytest.approx(.25) and
                   c["uv_v_max"]-c["uv_v_min"] == pytest.approx(.5) for c in cards)
        ceramic_sources = [c for c in carriers if "peranakan_ceramic_dado_family_" in c["source_image_path"]]
        assert ceramic_sources and all(c["sticker_layer"].startswith("peranakan_ceramic_panel_family_") for c in ceramic_sources)
        assert "fine_plaster_ornament" in {c["sticker_layer"] for c in carriers}


def test_revised_relief_dormer_and_rear_service_stack(compiled: dict) -> None:
    for size in MODULE.SIZES:
        profile = _profile(compiled, size); carriers = profile["massing_graph"]["assemblies"]
        geometry = MODULE.build_geometry(size); named = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        relief = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") in
                  {"floral_motif_cluster", "faunal_motif_cluster"}]
        assert relief and all(c["floor_role"] == "fixed_upper_residential" and
                              c["sticker_layer"] == "fine_plaster_ornament" and c["axis"] == "front" for c in relief)
        dormers = [mesh for mesh in geometry["meshes"] if mesh.get("carrier_kind") == "dormer_frame"]
        caps = [mesh for mesh in geometry["meshes"] if mesh.get("shallow_cap_depth_m") == .60]
        assert len(dormers) == geometry["unit_contract"]["count"] and all(mesh["shallow_depth_m"] == .20 for mesh in dormers)
        assert len(caps) == geometry["unit_contract"]["count"]
        assert profile["massing_graph"]["height_m"] == 11.45
        service = [c for c in carriers if named[c["surface_id"]].get("carrier_kind", "").startswith("service_rear_")]
        assert service and all(c["floor_role"] == "rear_service" and c["axis"] == "rear" for c in service)
        panels = [c for c in service if named[c["surface_id"]].get("carrier_kind") == "service_rear_wall_panel"]
        frames = [c for c in service if named[c["surface_id"]].get("carrier_kind") == "service_rear_window_frame"]
        glazing = [c for c in service if named[c["surface_id"]].get("carrier_kind") == "service_rear_glass"]
        cards = [c for c in service if named[c["surface_id"]].get("carrier_kind") == "service_rear_interior_card"]
        count = geometry["unit_contract"]["count"]
        assert len(panels) == count * 5 and len(frames) == count * 8 and len(glazing) == count * 2 and len(cards) == count * 2
        assert all(c["sticker_layer"].endswith("_plaster_rear") for c in panels)
        assert all(c["source_image_path"].endswith("physical_clear_glass_intrinsic.png") for c in glazing)
        assert all(c["source_image_path"].endswith("upper_residential_interior_atlas.png") and
                   c["uv_u_max"] - c["uv_u_min"] == pytest.approx(.25) and
                   c["uv_v_max"] - c["uv_v_min"] == pytest.approx(.5) for c in cards)


def test_material_v2_roof_plan_frequency_optics_and_card_containment_limit(compiled: dict) -> None:
    for size in MODULE.SIZES:
        profile = _profile(compiled, size); carriers = profile["massing_graph"]["assemblies"]
        roofs = [c for c in carriers if c["sticker_layer"] == "terracotta_roof_field"]
        assert roofs and all(c["axis"] == "plan" and c["plan_bounds"] and
                             c["world_metric_uv_tile_m"] == pytest.approx(1.0) for c in roofs)
        glass = [c for c in carriers if c["material_role"] == "glass"]
        assert all(c["surface_alpha_override"] == pytest.approx(.27) and
                   c["transmission_override"] == pytest.approx(.92) and
                   c["roughness_override"] == pytest.approx(.05) for c in glass)
        cards = [c for c in carriers if "interior_card" in c["sticker_layer"]]
        assert {c["emission_strength_override"] for c in cards} == {.042, .05, .06}
        arch_cards = [c for c in cards if c["sticker_layer"] == "upper_residential_interior_card" and
                      "_arch_" in c["surface_id"]]
        assert arch_cards and all(c["aperture_containment_status"] == "contained" for c in arch_cards)
        tile = [c for c in carriers if c["sticker_layer"].startswith("peranakan_ceramic_panel_family_") or
                c["sticker_layer"] == "five_foot_way_walkway_tile"]
        assert tile and all(c["world_metric_uv_tile_m"] == pytest.approx(1.0) for c in tile)


def test_upper_opaque_backings_close_all_arches_without_optical_or_emission_leak(compiled: dict) -> None:
    for size, expected in (("canonical", 18), ("extended", 21)):
        profile = _profile(compiled, size); carriers = profile["massing_graph"]["assemblies"]
        geometry = MODULE.build_geometry(size); named = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        backings = [c for c in carriers if c["sticker_layer"] == "upper_residential_opaque_backing"]
        assert len(backings) == expected
        assert all(named[c["surface_id"]]["carrier_kind"] == "arch_contour_interior_backing" and
                   named[c["surface_id"]]["opaque"] and named[c["surface_id"]]["environment_occlusion"] for c in backings)
        assert all(c["material_role"] == "elevation" and c["floor_role"] == "fixed_upper_residential" and
                   c["surface_alpha_override"] == pytest.approx(1.0) and
                   c["transmission_override"] == pytest.approx(0.0) and
                   c["emission_strength_override"] == pytest.approx(0.0) and
                   c["opaque_environment_backing"] and c["aperture_containment_status"] == "contained" and
                   c["backing_authority"] == "dark_neutral_residential_atlas_opaque" and
                   c["backing_luminance_cap"] == pytest.approx(.28) and
                   c["diagnostic_no_environment_leak"] for c in backings)
        assert not [c for c in backings if "glass_profile" in c]
        assert all(c["uv_u_max"]-c["uv_u_min"] == pytest.approx(.25) and
                   c["uv_v_max"]-c["uv_v_min"] == pytest.approx(.5) for c in backings)


def test_material_v3_ornament_authority_and_per_unit_ceramic_phase(compiled: dict) -> None:
    for size in MODULE.SIZES:
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        ornament = [c for c in carriers if c["sticker_layer"] == "fine_plaster_ornament"]
        assert ornament and all(any(c["world_metric_uv_tile_m"] == pytest.approx(v) for v in (.52, .64)) and
                                any(c["roughness_override"] == pytest.approx(v) for v in (.58, .61)) and
                                c["ornament_relief_authority"] == "physical_shaped_motif_plus_dense_intrinsic" and
                                c["physical_silhouette_authority"] for c in ornament)
        ceramic = [c for c in carriers if c["sticker_layer"].startswith("peranakan_ceramic_panel_family_") or
                   c["sticker_layer"] == "five_foot_way_walkway_tile"]
        assert ceramic and len({(c["world_metric_uv_u_offset"], c["world_metric_uv_v_offset"])
                                for c in ceramic}) == MODULE.build_geometry(size)["unit_contract"]["count"]
        assert all(c["world_metric_uv_tile_m"] == pytest.approx(1.0) and
                   0 <= c["whole_panel_phase_index"] < 8 for c in ceramic)


def test_split_row_end_closures_preserve_tunnel_clearance_and_finish_ownership(compiled: dict) -> None:
    for size in MODULE.SIZES:
        geometry = MODULE.build_geometry(size)
        named = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        ends = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") in
                {"row_end_gable_wall", "row_end_gable_upper_closure"}]
        assert len(ends) == 4
        lower = [c for c in ends if named[c["surface_id"]]["carrier_kind"] == "row_end_gable_wall"]
        upper = [c for c in ends if named[c["surface_id"]]["carrier_kind"] == "row_end_gable_upper_closure"]
        assert {c["floor_role"] for c in lower} == {"end_return_lower_rear"}
        assert {c["floor_role"] for c in upper} == {"end_return_upper_front"}
        assert all(c["sticker_layer"].endswith("_plaster_return") and
                   named[c["surface_id"]]["starts_behind_arcade"] for c in lower)
        assert all(c["sticker_layer"].endswith("_plaster_front") and
                   named[c["surface_id"]]["clear_above_arcade"] for c in upper)
        assert {c["axis"] for c in ends} == {"left", "right"}
        # Exact split leaves the five-foot-way street opening unobstructed:
        # rear closure starts at TD and front closure starts at arcade head.
        assert all(min(v[1] for v in named[c["surface_id"]]["vertices"]) == pytest.approx(-14 + 1.70)
                   for c in lower)
        assert all(min(v[2] for v in named[c["surface_id"]]["vertices"]) == pytest.approx(4.25)
                   for c in upper)


def test_shaped_flora_scroll_pendant_and_bird_motifs_have_exact_semantic_owner(compiled: dict) -> None:
    expected = {"six_lobed_flower", "scrolled_capital", "hanging_floral_pendant", "paired_bird_wings"}
    shaped_kinds = {"relief_medallion", "shaped_capital", "floral_motif_cluster", "faunal_motif_cluster"}
    for size in MODULE.SIZES:
        geometry = MODULE.build_geometry(size); named = {m["name"]: m for m in geometry["meshes"]}
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        motifs = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") in shaped_kinds]
        assert expected <= {named[c["surface_id"]].get("motif") for c in motifs}
        assert all(c["sticker_layer"] == "fine_plaster_ornament" and c["axis"] == "front" and
                   c["world_metric_uv_tile_m"] == pytest.approx(.52) and
                   c["roughness_override"] == pytest.approx(.58) and
                   c["ornament_motif_semantic"] == named[c["surface_id"]]["motif"] and
                   c["physical_silhouette_authority"] for c in motifs)
        pilasters = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") == "shaped_pilaster"]
        assert pilasters and all(c["sticker_layer"] == "pale_plaster_trim" for c in pilasters)


def test_repaired_soffit_beams_and_endpoint_caps_are_pale_and_nonoverlapping(compiled: dict) -> None:
    for size, cap_count in (("canonical", 12), ("extended", 14)):
        geometry = MODULE.build_geometry(size); named = {m["name"]: m for m in geometry["meshes"]}
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        caps = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") == "pale_trim_endpoint_cap"]
        beams = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") == "tunnel_soffit_beam"]
        assert len(caps) == cap_count and len(beams) == geometry["unit_contract"]["count"]
        pale = caps + beams
        assert all(c["sticker_layer"] == "pale_arcade_soffit_beam" and
                   c["source_image_path"].endswith("arcade_soffit_reveal_intrinsic.png") and
                   not any(token in c["source_image_path"] for token in ("timber", "iron")) and
                   c["floor_role"] == "fixed_arcade_cavern" for c in pale)
        # Geometry provides one left/right cap per unit and trims each beam to
        # the inner cap edges, so no carrier spans a neighbouring seam.
        for unit in range(geometry["unit_contract"]["count"]):
            unit_caps = [named[c["surface_id"]] for c in caps if named[c["surface_id"]].get("unit") == unit]
            unit_beam = [named[c["surface_id"]] for c in beams if named[c["surface_id"]].get("unit") == unit]
            assert len(unit_caps) == 2 and len(unit_beam) == 1
            bx = [v[0] for v in unit_beam[0]["vertices"]]
            assert min(bx) >= min(max(v[0] for v in cap["vertices"]) for cap in unit_caps) - 5.0


def test_continuous_diamond_fretwork_and_drop_pendants_are_readable_ornament(compiled: dict) -> None:
    for size in MODULE.SIZES:
        geometry = MODULE.build_geometry(size); named = {m["name"]: m for m in geometry["meshes"]}
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        ornament = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") in
                    {"continuous_fretwork_relief", "continuous_pendant_relief"}]
        units = geometry["unit_contract"]["count"]
        assert ornament and {named[c["surface_id"]].get("motif") for c in ornament} == {
            "small_rounded_flower_center", "thin_drop_pendant"}
        assert all(c["sticker_layer"] == "fine_plaster_ornament" and c["axis"] == "front" and
                   c["world_metric_uv_tile_m"] == pytest.approx(.52) and
                   c["roughness_override"] == pytest.approx(.58) and
                   c["physical_silhouette_authority"] for c in ornament)


def test_ground_topology_has_explicit_assets_roles_and_unit_ceramic_phase(compiled: dict) -> None:
    for size in MODULE.SIZES:
        geometry = MODULE.build_geometry(size); named = {m["name"]: m for m in geometry["meshes"]}
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        kinds = {"ground_shopfront_pier", "shopfront_perimeter_member", "shopfront_mullion",
                 "shopfront_transom", "vent_grille", "tile_dado", "shopfront_glass", "shopfront_interior"}
        ground = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") in kinds]
        assert ground and all(c["floor_role"] == "fixed_ground_shop" for c in ground)
        assert all(c["sticker_layer"].endswith("_plaster_front") for c in ground
                   if named[c["surface_id"]].get("carrier_kind") == "ground_shopfront_pier")
        assert all(c["sticker_layer"] == "carved_dark_timber" for c in ground
                   if named[c["surface_id"]].get("carrier_kind") in
                   {"shopfront_perimeter_member", "shopfront_mullion", "shopfront_transom", "vent_grille"})
        dado = [c for c in ground if named[c["surface_id"]].get("carrier_kind") == "tile_dado"]
        assert len({(c["world_metric_uv_u_offset"], c["world_metric_uv_v_offset"])
                    for c in dado}) == geometry["unit_contract"]["count"]
        assert all(c["world_metric_uv_tile_m"] == pytest.approx(1.0) for c in dado)


def test_six_whole_unit_ceramic_families_and_selective_pale_surrounds(compiled: dict) -> None:
    for size in MODULE.SIZES:
        geometry = MODULE.build_geometry(size); named = {m["name"]: m for m in geometry["meshes"]}
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        panels = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") in {"tile_dado", "tile_relief_cluster"}]
        assert panels
        for c in panels:
            unit = int(named[c["surface_id"]].get("unit", 0)); family = unit % 6
            assert c["source_image_path"].endswith(f"peranakan_ceramic_dado_family_{family}_intrinsic.png")
            assert c["sticker_layer"] == f"peranakan_ceramic_panel_family_{family}"
            assert c["world_metric_uv_tile_m"] == pytest.approx(1.0)
        assert len({c["source_image_path"] for c in panels}) == min(6, geometry["unit_contract"]["count"])
        surrounds = [c for c in carriers if named[c["surface_id"]].get("carrier_kind") == "selective_pale_shopfront_surround"]
        assert len(surrounds) == 18 and all(c["sticker_layer"] == "pale_shopfront_surround" and
                                           c["source_image_path"].endswith("pale_trim_relief_intrinsic.png") and
                                           c["floor_role"] == "fixed_ground_shop" and c["axis"] == "front"
                                           for c in surrounds)


def test_roof_face_semantics_terminal_and_cavern_ownership(compiled: dict) -> None:
    for size in MODULE.SIZES:
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        roof = [c for c in carriers if c["semantic_group"].startswith("roof_")]
        assert {c["semantic_group"] for c in roof} == {"roof_upface", "roof_ridge", "roof_eave_gable", "roof_soffit"}
        assert all(c["source_image_path"].endswith("terracotta_roof_field_intrinsic.png") for c in roof if c["semantic_group"] == "roof_upface")
        assert all(c["source_image_path"].endswith("terracotta_ridge_cap_intrinsic.png") for c in roof if c["semantic_group"] == "roof_ridge")
        party = [c for c in carriers if c["floor_role"] == "party_roof_boundary"]
        assert party and {c["sticker_layer"] for c in party} == {"party_wall_plaster", "party_wall_coping"}
        tunnel = [c for c in carriers if c["floor_role"] == "fixed_arcade_cavern"]
        # The repaired topology replaces the former soffit plane with a
        # physically trimmed beam and pale endpoint-cap set.
        assert {c["semantic_group"] for c in tunnel} >= {"walkway_upface", "whole_mesh"}
        assert any(c["sticker_layer"] == "pale_arcade_soffit_beam" for c in tunnel)
        assert not [c for c in tunnel if "roof" in c["sticker_layer"]]


def test_every_plan_carrier_has_bounded_plan_metadata(compiled: dict) -> None:
    for size in MODULE.SIZES:
        carriers = _profile(compiled, size)["massing_graph"]["assemblies"]
        plan = [carrier for carrier in carriers if carrier["axis"] == "plan"]
        assert plan
        for carrier in plan:
            x0, x1, y0, y1 = carrier["plan_bounds"]
            assert x0 < x1 and y0 < y1
            assert carrier["semantic_group"] == "roof_upface"
        assert not [carrier for carrier in carriers if carrier["axis"] != "plan" and "plan_bounds" in carrier]


def test_whole_unit_contract_and_carrier_packages(compiled: dict) -> None:
    contract = compiled[MODULE.CONTRACT.name]
    assert contract["whole_attached_units_only"] and not contract["continuous_resize_allowed"]
    assert not contract["vertical_scaling_allowed"] and not contract["depth_scaling_allowed"]
    assert contract["unit_width_m"] == 5.0 and contract["registered_asset_count"] == 44
    packages = compiled[MODULE.PACKAGE.name]["packages"]
    for size, package in packages.items():
        assert package["status"] == "pass" and not package["failures"]
        assert package["locked_geometry_sha256"] == MODULE.EXPECTED_GEOMETRY_HASHES[size]
        assert package["carrier_count"] == len(_profile(compiled, size)["massing_graph"]["assemblies"])
