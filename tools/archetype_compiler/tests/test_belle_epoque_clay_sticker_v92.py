from __future__ import annotations

from compile_belle_epoque_clay_sticker_v92 import build_profile


def test_profile_binds_stickers_to_locked_clay() -> None:
    profile, registry = build_profile()
    graph = profile["massing_graph"]
    assert graph["nodes"][0]["kind"] == "locked_mesh_bundle"
    assert len(graph["nodes"][0]["meshes"]) >= 53
    assert {item["kind"] for item in graph["assemblies"]} == {"carrier_skin"}
    assert len(graph["assemblies"]) >= 27
    assert profile["production_contract"]["clay_lock"]["status"] == "approved"
    assert profile["production_contract"]["placement_contract"]["mode"] == "fixed_select_and_place"
    assert registry["entries"][0]["family_id"] == "belle-epoque-grand-magasin-v92"


def test_domes_keep_glass_and_radial_mapping() -> None:
    profile, _ = build_profile()
    skins = {item["surface_id"]: item for item in profile["massing_graph"]["assemblies"]}
    for surface in ("central_dome", "corner_dome"):
        assert skins[surface]["axis"] == "dome_radial"
        assert skins[surface]["material_role"] == "glass"
    assert skins["corner_pavilion"]["axis"] == "cylindrical_segment"
    for surface in ("roof_front", "roof_right", "roof_rear", "roof_left"):
        assert skins[surface]["axis"] == "plan"
