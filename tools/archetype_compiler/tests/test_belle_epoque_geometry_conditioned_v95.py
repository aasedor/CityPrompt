from __future__ import annotations

from build_belle_epoque_continuous_geometry_v94 import build_continuous_geometry
from compile_belle_epoque_geometry_conditioned_v95 import build_outputs, build_profile, build_v95_geometry
from glass_profiles import glass_profile
from sticker_carrier_space import condition_profile


def test_every_sticker_is_fingerprinted_against_the_locked_final_carrier() -> None:
    profile, package = build_profile()
    assert package["status"] == "pass"
    assert package["carrier_count"] > 100
    assert package["locked_geometry_sha256"] == build_v95_geometry()["geometry_sha256"]
    assert package["locked_geometry_sha256"] != build_continuous_geometry()["geometry_sha256"]
    stickers = [item for item in profile["massing_graph"]["assemblies"] if item.get("kind") == "carrier_skin"]
    assert len(stickers) == package["carrier_count"]
    assert all(item["carrier_space"]["approval_space"] == "rendered_on_locked_carrier" for item in stickers)
    assert all(not item["carrier_space"]["post_generation_nonuniform_scale_allowed"] for item in stickers)


def test_carrier_package_changes_when_locked_geometry_changes() -> None:
    profile, package = build_profile()
    changed = build_continuous_geometry()
    changed["meshes"][0]["vertices"][0][0] += 0.01
    changed["geometry_sha256"] = "changed-geometry"
    _, changed_package = condition_profile(profile, changed, score_target=95)
    assert changed_package["package_sha256"] != package["package_sha256"]
    assert changed_package["locked_geometry_sha256"] == "changed-geometry"


def test_v95_uses_face_specific_dormer_ownership_and_physical_trim() -> None:
    profile, _ = build_profile()
    assemblies = profile["massing_graph"]["assemblies"]
    dormer_skins = [item for item in assemblies if str(item.get("id", "")).startswith("v95_dormer_")]
    assert len(dormer_skins) == 20
    assert all(item.get("face_indices") for item in dormer_skins)
    assert not any(
        "dormer" in str(item.get("id", "")).lower() and item.get("sticker_layer") == "coverage_seal"
        for item in assemblies
    )
    assert sum(item.get("kind") == "dormer_trim_system" for item in assemblies) == 4
    trim_systems = [item for item in assemblies if item.get("kind") == "dormer_trim_system"]
    assert all(item.get("glass_profile") == "heritage_dormer_dark" for item in trim_systems)
    assert all(item.get("window_width_m", 99) <= 0.70 for item in trim_systems)
    assert all(item.get("window_height_m", 99) <= 0.65 for item in trim_systems)
    geometry = build_v95_geometry()
    dormers = [mesh for mesh in geometry["meshes"] if str(mesh["name"]).startswith("dormer_")]
    assert all(max(vertex[2] for vertex in mesh["vertices"]) <= 24.0 for mesh in dormers)
    fronts = [item for item in dormer_skins if item.get("sticker_layer") == "dormer_front"]
    assert all(item["material_role"] == "roof" for item in fronts)
    assert all(str(item["source_image_path"]).endswith("dormer_zinc_intrinsic.png") for item in fronts)
    assert all(
        str(item["source_image_path"]).endswith("dormer_zinc_intrinsic.png")
        for item in dormer_skins
    )


def test_v95_broadens_canopy_and_adds_luminous_dome_sections() -> None:
    profile, _ = build_profile()
    assemblies = profile["massing_graph"]["assemblies"]
    canopy = next(item for item in assemblies if item.get("id") == "v94_curved_iron_glass_canopy")
    assert canopy["angle_end_deg"] - canopy["angle_start_deg"] >= 70
    assert canopy["segments"] >= 18
    domes = [item for item in assemblies if item.get("glass_profile") == "heritage_stained_glass_luminous"]
    assert {item["id"] for item in domes} == {"v92_skin_central_dome", "v92_skin_corner_dome"}
    assert sum(item.get("kind") == "dome_light_well" for item in assemblies) == 2
    assert glass_profile("heritage_stained_glass_luminous")["glass_emission_strength"] > 0.02


def test_every_outer_streetwall_end_cap_has_a_shared_boundary_sticker() -> None:
    profile, _ = build_profile()
    returns = [
        item for item in profile["massing_graph"]["assemblies"]
        if item.get("sticker_layer") == "corner_return"
    ]
    assert len(returns) == 40
    assert all(item.get("construction_joint") for item in returns)
    assert all(str(item["source_image_path"]).endswith("textures/limestone/albedo.jpg") for item in returns)
    assert all(item.get("floor_role") in {"ground", "middle", "top_crown"} for item in returns)
    assert all(item.get("floor_role") != "all_occupied_floors" for item in returns)
    assert not any(item.get("id") == "v94_principal_corner_front_return" for item in returns)


def test_entrance_identity_sign_is_geometry_conditioned() -> None:
    profile, package = build_profile()
    assemblies = profile["massing_graph"]["assemblies"]
    assert any(item.get("id") == "v95_entrance_sign_panel" for item in assemblies)
    sticker = next(item for item in assemblies if item.get("id") == "v95_entrance_sign_sticker")
    assert sticker["carrier_space"]["approval_space"] == "rendered_on_locked_carrier"
    assert any(record["carrier_id"] == sticker["id"] for record in package["carriers"])


def test_roof_landmarks_and_corner_tower_have_disjoint_floor_roles() -> None:
    profile, _ = build_profile()
    assemblies = profile["massing_graph"]["assemblies"]
    roof_carriers = [
        item for item in assemblies
        if item.get("kind") == "carrier_skin" and item.get("material_role") == "roof"
    ]
    assert roof_carriers and all(item.get("floor_role") == "roof" for item in roof_carriers)
    tower = next(item for item in assemblies if item.get("id") == "v92_skin_coverage_068_corner_upper_tower")
    assert tower["floor_role"] == "top_crown"
    assert tower["z_max_m"] == 20.5
    transition = next(
        item for item in assemblies
        if item.get("id") == "v95_corner_upper_tower_roof_transition_sticker"
    )
    assert transition["floor_role"] == "roof"
    geometry = build_v95_geometry()
    roof_targets = {
        mesh["name"] for mesh in geometry["meshes"]
        if mesh.get("material_domain") == "roof_only"
    }
    for item in assemblies:
        if item.get("kind") != "carrier_skin" or not item.get("target_ids"):
            continue
        targets = item["target_ids"]
        if all(any(name == target or name.startswith(f"{target}_") for name in roof_targets) for target in targets):
            assert item.get("floor_role") == "roof", item["id"]


def test_v95_outputs_raise_the_individual_architect_gate_to_95() -> None:
    _, registry, package, contract = build_outputs()
    assert registry["pipeline_version"] == "v95"
    assert package["score_target"] == contract["score_target"] == 95
    assert contract["status"] == "pass"


def test_landmark_projection_envelope_is_explicit_and_bounded() -> None:
    profile, _ = build_profile()
    contract = profile["massing_graph"]["recipe_contract"]
    assert contract["kind"] == "belle_epoque_geometry_conditioned_landmark"
    assert contract["projection_source"] == "locked_corner_pavilion_and_moulded_returns"
    assert 1.18 <= contract["footprint_projection_allowance_m"] <= 1.25
