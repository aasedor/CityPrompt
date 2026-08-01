"""Generate the reference-locked Wave 13 LEGO building families.

Wave 13 applies the mature image-to-construction workflow to five unrelated
ordinary and civic archetypes.  Each building is assembled from real metric
parts (slabs, piers, panes, occupied-depth cards, roofs and ornament), exports
as a fixed landmark, and also ships with six semantic LEGO modules whose
ordinary bays can repeat when a user's drawn footprint differs from the source.

Run from the repository root with Blender 5.x::

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave13_diverse_families.py -- \
      --family art-deco-cream-terracotta-tower --view-set pilot
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from generate_wave3_landmark_families import (  # noqa: E402
    COORDINATE_CONTRACT,
    aim_camera,
    clear_scene,
    delete_objects,
    export_glb,
    facade_contract,
    load_skin_manifest,
    material,
    module_contract_markers,
    skin_material,
    texture_inventory,
)
from generate_wave12_diverse_families import (  # noqa: E402
    add_beam,
    add_box,
    add_cylinder,
    add_layered_window_x,
    add_layered_window_y,
    add_sphere,
    bounds_dimensions,
    bsdf_for,
    configure_glass,
    configure_occupied,
    create_gable_roof,
    create_mesh_object,
    evaluated_triangle_count,
    grade_material,
    material_count,
    normalize_bottom_centre,
    set_normal_strength,
    tag_object,
    wash_material,
)


FAMILIES: dict[str, dict] = {
    "art-deco-cream-terracotta-tower": {
        "archetype_id": "art_deco_setback_tower",
        "variant_id": "art_deco_cream_terracotta",
        "aliases": [
            "art_deco_setback_tower",
            "art_deco_cream_terracotta",
            "cream_terracotta_art_deco_tower",
            "gilded_setback_tower",
        ],
        "label": "Art Deco Setback Tower - Cream Terracotta",
        "aesthetic": "art_deco_streamline_moderne",
        "development_type": "mixed_use_highrise",
        "glass_profile": "neutral_smoky_bronze_framed_occupied",
        "native": (31.0, 29.0, 77.0),
        "native_floors": 15,
        "min_floors": 10,
        "max_floors": 28,
        "floor_height": 4.0,
        "podium_height": 7.2,
        "crown_height": 3.0,
        "roof_height": 14.8,
        "catalogue_slug": "art_deco_setback_tower",
        "catalogue_variant_index": 0,
        "identity": (
            "A fifteen-level cream glazed-terra-cotta tower rises from a black "
            "granite and bronze double-height podium through seven-, five- and "
            "three-bay setback stages to an octagonal smoky-glass lantern held "
            "by eight gilded posts beneath a faceted gold cap and finial."
        ),
        "material_zones": (
            "cream glazed architectural terra cotta with fine ashlar joints; "
            "charcoal polished granite podium; aged dark bronze entrance and "
            "window frames; neutral smoky physical low-e glass; warm occupied "
            "room depth; restrained gold-leaf belts, lantern posts and finial; "
            "dark setback terrace membrane"
        ),
        "reuse_keys": [
            "Cream Terracotta Art Deco Tower",
            "Gilded Setback Tower",
            "Art Deco Wedding Cake Tower",
            "Bronze and Terracotta High Rise",
        ],
    },
    "restored-kyoto-machiya": {
        "archetype_id": "japanese_machiya_mixed_use",
        "variant_id": "machiya_traditional_restored",
        "aliases": [
            "japanese_machiya_mixed_use",
            "machiya_traditional_restored",
            "restored_kyoto_machiya",
            "traditional_koshi_lattice_shop_house",
        ],
        "label": "Japanese Machiya - Traditional Restored",
        "aesthetic": "traditional_japanese_machiya",
        "development_type": "mixed_use_lowrise",
        "glass_profile": "neutral_smoky_lattice_screened_occupied",
        "native": (19.4, 15.4, 11.4),
        "native_floors": 2,
        "min_floors": 2,
        "max_floors": 4,
        "floor_height": 3.35,
        "podium_height": 3.35,
        "crown_height": 0.85,
        "roof_height": 4.7,
        "catalogue_slug": "japanese_machiya_mixed_use",
        "catalogue_variant_index": 0,
        "identity": (
            "A restored two-storey Kyoto machiya uses a dark cedar post-and-beam "
            "frame, white clay infill and continuous fine koshi lattice in front "
            "of warm occupied glazing beneath a deep kawara gable, with a lower "
            "street eave, recessed entry and three plain indigo noren panels."
        ),
        "material_zones": (
            "dark weathered Japanese cedar and cypress; warm brown fine koshi "
            "lattice; matte white lime-clay plaster; charcoal glazed kawara "
            "tiles; neutral smoky physical glass; warm occupied tatami-room "
            "depth; plain woven indigo noren; grey stone sill; dark gutters"
        ),
        "reuse_keys": [
            "Restored Kyoto Machiya",
            "Traditional Koshi Lattice Shop House",
            "Japanese Timber Mixed Use House",
            "Kawara Tile Machiya",
        ],
    },
    "mid-century-glass-steel-pavilion": {
        "archetype_id": "mid_century_modern_pavilion_block",
        "variant_id": "mid_century_pavilion_glass_steel",
        "aliases": [
            "mid_century_modern_pavilion_block",
            "mid_century_pavilion_glass_steel",
            "glass_steel_gallery_pavilion",
            "floating_roof_modern_pavilion",
        ],
        "label": "Mid-Century Pavilion - Glass and Steel",
        "aesthetic": "mid_century_modern",
        "development_type": "commercial_cultural_lowrise",
        "glass_profile": "neutral_low_iron_gallery_occupied",
        "native": (29.0, 22.0, 12.6),
        "native_floors": 3,
        "min_floors": 1,
        "max_floors": 5,
        "floor_height": 3.65,
        "podium_height": 3.65,
        "crown_height": 0.28,
        "roof_height": 0.34,
        "catalogue_slug": "mid_century_modern_pavilion_block",
        "catalogue_variant_index": 0,
        "identity": (
            "Three transparent occupied levels sit inside a complete matte-black "
            "steel post-and-beam grid, beside one pale travertine service core "
            "and below an exceptionally thin warm-white roof plane whose deep "
            "asymmetric cantilever makes the pavilion appear to float."
        ),
        "material_zones": (
            "matte-black painted structural steel; neutral physical low-iron "
            "glass; warm occupied gallery depth; pale honed travertine; light "
            "grey concrete slab edges and plinth; warm-white ribbed aluminum "
            "soffit and smooth knife-edge roof fascia"
        ),
        "reuse_keys": [
            "Mid Century Glass Steel Pavilion",
            "Floating Roof Modern Pavilion",
            "Transparent Gallery Pavilion",
            "Travertine Core Pavilion",
        ],
    },
    "timber-glass-transit-station-block": {
        "archetype_id": "transit_oriented_station_block",
        "variant_id": "transit_station_modern_glass",
        "aliases": [
            "transit_oriented_station_block",
            "transit_station_modern_glass",
            "timber_glass_transit_station_block",
            "green_roof_station_concourse",
        ],
        "label": "Transit Station Block - Timber and Glass",
        "aesthetic": "contemporary_sustainable_transit",
        "development_type": "transportation_mixed_use",
        "glass_profile": "high_transmission_transit_concourse_occupied",
        "native": (62.0, 38.0, 29.5),
        "native_floors": 6,
        "min_floors": 4,
        "max_floors": 10,
        "floor_height": 4.05,
        "podium_height": 4.35,
        "crown_height": 1.15,
        "roof_height": 3.0,
        "catalogue_slug": "transit_oriented_station_block",
        "catalogue_variant_index": 0,
        "identity": (
            "A transparent three-level public station concourse with real floor "
            "plates, entrances and escalator depth supports three warm timber "
            "rainscreen levels of alternating clear windows and external louver "
            "screens beneath a planted roof and two photovoltaic canopy rows."
        ),
        "material_zones": (
            "neutral high-transmission curtain wall; graphite aluminum pressure "
            "caps and steel canopy; warm occupied transit-hall depth; pale "
            "concrete slabs; reddish-brown timber rainscreen; dark timber louver "
            "blades with real gaps; extensive sedum roof; dark-blue PV glass"
        ),
        "reuse_keys": [
            "Timber Glass Transit Station Block",
            "Modern Glass Station Concourse",
            "Green Roof Transit Hub",
            "Timber Louver Station",
        ],
    },
    "passive-house-timber-block": {
        "archetype_id": "eco_urban_bioclimatic_block",
        "variant_id": "eco_bioclimatic_passive",
        "aliases": [
            "eco_urban_bioclimatic_block",
            "eco_bioclimatic_passive",
            "passive_house_timber_block",
            "larch_pv_sedum_urban_block",
        ],
        "label": "Bioclimatic Block - Passive House Timber",
        "aesthetic": "eco_urban_bioclimatic",
        "development_type": "residential_midrise",
        "glass_profile": "neutral_triple_glazed_deep_reveal_occupied",
        "native": (37.2, 21.0, 18.2),
        "native_floors": 4,
        "min_floors": 3,
        "max_floors": 8,
        "floor_height": 3.25,
        "podium_height": 3.25,
        "crown_height": 0.45,
        "roof_height": 4.65,
        "catalogue_slug": "eco_urban_bioclimatic_block",
        "catalogue_variant_index": 0,
        "identity": (
            "A four-level six-bay passive urban block is wrapped in naturally "
            "weathering vertical larch, with deeply recessed triple glazing, "
            "selective exterior blinds and a central timber entry beneath an "
            "asymmetric roof combining continuous PV, sedum and rooflights."
        ),
        "material_zones": (
            "honey-brown vertical larch rainscreen; dark timber-aluminum frames "
            "and insulated reveals; neutral physical triple glazing; warm "
            "occupied room depth; black real external blind blades; pale "
            "insulated panels; dark-blue PV glass; dense sedum; zinc edges"
        ),
        "reuse_keys": [
            "Passive House Timber Block",
            "Larch PV Sedum Urban Block",
            "Bioclimatic Timber Apartment Block",
            "Deep Reveal Passive Housing",
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), required=True)
    parser.add_argument(
        "--output-root", type=Path, default=Path("frontend/public/families")
    )
    parser.add_argument(
        "--view-set",
        choices=(
            "preview",
            "pilot",
            "all",
            "front_elevation",
            "front_corner_oblique",
            "rear_corner_oblique",
            "aerial",
            "facade_close",
            "identity_close",
            "street",
            "context",
        ),
        default="all",
    )
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-modules", action="store_true")
    parser.add_argument("--skip-assembled-export", action="store_true")
    parser.add_argument("--render-existing", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def _pbr_material(
    folder: Path,
    near: dict,
    cfg: dict,
    key: str,
    name: str,
    *,
    metallic: float = 0.0,
    transmission: float = 0.0,
    saturation: float = 1.0,
    value: float = 1.0,
    normal: float = 0.42,
) -> bpy.types.Material:
    result = skin_material(
        name,
        folder,
        near[key],
        key,
        metallic=metallic,
        transmission=transmission,
    )
    grade_material(result, saturation=saturation, value=value)
    set_normal_strength(result, normal)
    result["source_variant_id"] = cfg["variant_id"]
    result["generation_archetype_id"] = cfg["variant_id"]
    result["reference_locked"] = True
    result["wave13_custom_material"] = True
    return result


def configure_photovoltaic(
    mat: bpy.types.Material,
    cfg: dict,
) -> bpy.types.Material:
    """Keep the authored cell grid readable beneath a restrained glass coat."""
    bsdf = bsdf_for(mat)
    bsdf.inputs["Roughness"].default_value = 0.16
    if bsdf.inputs.get("Metallic"):
        bsdf.inputs["Metallic"].default_value = 0.12
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.42
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.055
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.48
    mat.diffuse_color = (0.025, 0.045, 0.085, 1.0)
    mat["photovoltaic_module"] = True
    mat["cell_topology"] = "6_columns_x_10_rows"
    mat["source_variant_id"] = cfg["variant_id"]
    mat["generation_archetype_id"] = cfg["variant_id"]
    return mat


def load_palette(folder: Path, cfg: dict) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = load_skin_manifest(folder)
    if not skin:
        raise FileNotFoundError(folder / "textures" / "skin_manifest.json")
    near = {zone: values["near"] for zone, values in skin["zones"].items()}

    def pbr(key: str, name: str, **kwargs) -> bpy.types.Material:
        return _pbr_material(folder, near, cfg, key, name, **kwargs)

    family = cfg["family"]
    if family == "restored-kyoto-machiya":
        mats = {
            "timber": wash_material(pbr("timber", "MAT_W13_MACHIYA_DarkWeatheredCedar", saturation=0.78, value=0.62, normal=0.55), tint=(0.20, 0.12, 0.065), factor=0.38, roughness=0.68),
            "lattice": wash_material(pbr("lattice", "MAT_W13_MACHIYA_WarmKoshiLattice", saturation=0.82, value=0.70, normal=0.42), tint=(0.28, 0.16, 0.085), factor=0.30, roughness=0.62),
            "tile": wash_material(pbr("tile", "MAT_W13_MACHIYA_CharcoalKawaraTile", saturation=0.24, value=0.58, normal=0.68), tint=(0.12, 0.13, 0.13), factor=0.42, roughness=0.48),
            "plaster": wash_material(pbr("plaster", "MAT_W13_MACHIYA_WhiteClayPlaster", saturation=0.30, value=1.03, normal=0.36), tint=(0.79, 0.77, 0.69), factor=0.18, roughness=0.82),
            "glass": configure_glass(pbr("vision_glass", "MAT_W13_MACHIYA_NeutralSmokyGlass", transmission=0.54, saturation=0.28, value=0.66, normal=0.06), cfg, tint=(0.17, 0.20, 0.18), transmission=0.72, alpha=0.38),
            "interior": configure_occupied(pbr("interior", "MAT_W13_MACHIYA_OccupiedRoomDepth", saturation=0.70, value=0.62, normal=0.08), warmth=(0.32, 0.17, 0.05), emission=0.15),
            "indigo": wash_material(pbr("indigo", "MAT_W13_MACHIYA_PlainIndigoNoren", saturation=0.90, value=0.65, normal=0.44), tint=(0.025, 0.055, 0.13), factor=0.36, roughness=0.83),
            "stone": pbr("stone", "MAT_W13_MACHIYA_GreyStoneSill", saturation=0.25, value=0.72, normal=0.55),
            "facade_skin": pbr("facade", "MAT_W13_MACHIYA_RegisteredFacadeUnderlay", saturation=0.68, value=0.82, normal=0.12),
            "podium_skin": pbr("podium", "MAT_W13_MACHIYA_RegisteredShopfrontUnderlay", saturation=0.68, value=0.78, normal=0.12),
            "floor_a_skin": pbr("floor_a", "MAT_W13_MACHIYA_RegisteredGroundBayUnderlay", saturation=0.68, value=0.78, normal=0.12),
            "floor_b_skin": pbr("floor_b", "MAT_W13_MACHIYA_RegisteredUpperBayUnderlay", saturation=0.68, value=0.80, normal=0.12),
            "crown_skin": pbr("crown", "MAT_W13_MACHIYA_RegisteredRoofUnderlay", saturation=0.48, value=0.68, normal=0.14),
            "side_skin": pbr("side", "MAT_W13_MACHIYA_RegisteredSideUnderlay", saturation=0.62, value=0.78, normal=0.10),
        }
        mats["frame"] = mats["lattice"]
        mats["roof"] = mats["tile"]
        return mats, skin
    if family == "mid-century-glass-steel-pavilion":
        mats = {
            "steel": wash_material(pbr("steel", "MAT_W13_PAVILION_MatteBlackSteel", metallic=0.44, saturation=0.20, value=0.50, normal=0.22), tint=(0.035, 0.038, 0.038), factor=0.48, roughness=0.42),
            "glass": configure_glass(pbr("vision_glass", "MAT_W13_PAVILION_CrystalLowIronGlass", transmission=0.70, saturation=0.10, value=0.88, normal=0.018), cfg, tint=(0.38, 0.42, 0.40), transmission=0.86, alpha=0.30),
            "interior": configure_occupied(pbr("interior", "MAT_W13_PAVILION_DaylightGalleryDepth", saturation=0.30, value=1.04, normal=0.045), warmth=(0.08, 0.055, 0.025), emission=0.035),
            "interior_evening": configure_occupied(pbr("interior_evening", "MAT_W13_PAVILION_EveningGalleryDepth", saturation=0.50, value=0.86, normal=0.045), warmth=(0.20, 0.11, 0.045), emission=0.10),
            "travertine": wash_material(pbr("travertine", "MAT_W13_PAVILION_HonedTravertine", saturation=0.54, value=0.98, normal=0.40), tint=(0.76, 0.72, 0.64), factor=0.20, roughness=0.62),
            "concrete": pbr("concrete", "MAT_W13_PAVILION_SmoothConcrete", saturation=0.24, value=0.92, normal=0.30),
            "ceiling": pbr("ceiling", "MAT_W13_PAVILION_PaleAcousticCeiling", saturation=0.20, value=1.02, normal=0.16),
            "gallery_floor": pbr("gallery_floor", "MAT_W13_PAVILION_PaleHonedGalleryFloor", saturation=0.22, value=0.98, normal=0.24),
            "soffit": pbr("soffit", "MAT_W13_PAVILION_RibbedAluminumSoffit", metallic=0.22, saturation=0.30, value=1.02, normal=0.32),
            "roof": pbr("roof", "MAT_W13_PAVILION_KnifeEdgeRoof", metallic=0.16, saturation=0.20, value=1.00, normal=0.18),
            "facade_skin": pbr("facade", "MAT_W13_PAVILION_RegisteredFacadeUnderlay", saturation=0.48, value=0.86, normal=0.08),
            "podium_skin": pbr("podium", "MAT_W13_PAVILION_RegisteredPodiumUnderlay", saturation=0.52, value=0.86, normal=0.08),
            "floor_a_skin": pbr("floor_a", "MAT_W13_PAVILION_RegisteredBayAUnderlay", saturation=0.52, value=0.86, normal=0.08),
            "floor_b_skin": pbr("floor_b", "MAT_W13_PAVILION_RegisteredBayBUnderlay", saturation=0.52, value=0.86, normal=0.08),
            "crown_skin": pbr("crown", "MAT_W13_PAVILION_RegisteredRoofUnderlay", saturation=0.34, value=0.94, normal=0.08),
            "side_skin": pbr("side", "MAT_W13_PAVILION_RegisteredSideUnderlay", saturation=0.46, value=0.84, normal=0.08),
        }
        mats["gallery_wall"] = material("MAT_W13_PAVILION_WarmWhiteGalleryWall", (0.78, 0.76, 0.70, 1.0), 0.72)
        mats["gallery_wood"] = material("MAT_W13_PAVILION_OiledOakFurniture", (0.34, 0.20, 0.095, 1.0), 0.58)
        mats["frame"] = mats["steel"]
        return mats, skin
    if family == "timber-glass-transit-station-block":
        mats = {
            "timber": wash_material(pbr("timber", "MAT_W13_TRANSIT_ReddishTimberRainscreen", saturation=0.82, value=0.86, normal=0.46), tint=(0.48, 0.23, 0.105), factor=0.28, roughness=0.58),
            "louver": wash_material(pbr("louver", "MAT_W13_TRANSIT_DarkTimberLouver", saturation=0.64, value=0.52, normal=0.38), tint=(0.18, 0.105, 0.07), factor=0.38, roughness=0.62),
            "glass": configure_glass(pbr("vision_glass", "MAT_W13_TRANSIT_HighTransmissionGlass", transmission=0.66, saturation=0.16, value=0.98, normal=0.04), cfg, tint=(0.50, 0.56, 0.56), transmission=0.90, alpha=0.24),
            "steel": wash_material(pbr("steel", "MAT_W13_TRANSIT_GraphiteSteel", metallic=0.58, saturation=0.16, value=0.52, normal=0.20), tint=(0.055, 0.065, 0.07), factor=0.44, roughness=0.38),
            "interior": configure_occupied(pbr("interior", "MAT_W13_TRANSIT_OccupiedConcourseDepth", saturation=0.72, value=0.86, normal=0.06), warmth=(0.30, 0.18, 0.07), emission=0.20),
            "green_roof": wash_material(pbr("green_roof", "MAT_W13_TRANSIT_ExtensiveGreenRoof", saturation=0.74, value=0.68, normal=0.58), tint=(0.23, 0.30, 0.10), factor=0.30, roughness=0.84),
            "pv": configure_glass(pbr("pv", "MAT_W13_TRANSIT_PhotovoltaicGlass", transmission=0.04, saturation=0.56, value=0.62, normal=0.14), cfg, tint=(0.035, 0.07, 0.13), transmission=0.04, alpha=1.0),
            "concrete": pbr("concrete", "MAT_W13_TRANSIT_PaleConcreteSlab", saturation=0.20, value=0.94, normal=0.30),
            "facade_skin": pbr("facade", "MAT_W13_TRANSIT_RegisteredFacadeUnderlay", saturation=0.58, value=0.86, normal=0.08),
            "podium_skin": pbr("podium", "MAT_W13_TRANSIT_RegisteredConcourseUnderlay", saturation=0.46, value=0.88, normal=0.08),
            "floor_a_skin": pbr("floor_a", "MAT_W13_TRANSIT_RegisteredGlazedBayUnderlay", saturation=0.46, value=0.88, normal=0.08),
            "floor_b_skin": pbr("floor_b", "MAT_W13_TRANSIT_RegisteredTimberBayUnderlay", saturation=0.68, value=0.82, normal=0.10),
            "crown_skin": pbr("crown", "MAT_W13_TRANSIT_RegisteredRoofUnderlay", saturation=0.58, value=0.76, normal=0.12),
            "side_skin": pbr("side", "MAT_W13_TRANSIT_RegisteredSideUnderlay", saturation=0.54, value=0.82, normal=0.08),
        }
        mats["frame"] = mats["steel"]
        mats["roof"] = mats["green_roof"]
        return mats, skin
    if family == "passive-house-timber-block":
        mats = {
            "larch": wash_material(pbr("larch", "MAT_W13_PASSIVE_VerticalLarch", saturation=0.80, value=0.92, normal=0.48), tint=(0.58, 0.36, 0.16), factor=0.27, roughness=0.62),
            "frame": wash_material(pbr("frame", "MAT_W13_PASSIVE_DarkTimberAluminumFrame", metallic=0.20, saturation=0.24, value=0.48, normal=0.22), tint=(0.055, 0.05, 0.042), factor=0.46, roughness=0.44),
            "glass": configure_glass(pbr("vision_glass", "MAT_W13_PASSIVE_HighPerformanceTripleGlass", transmission=0.66, saturation=0.10, value=0.84, normal=0.018), cfg, tint=(0.25, 0.28, 0.26), transmission=0.80, alpha=0.31),
            "blind": wash_material(pbr("blind", "MAT_W13_PASSIVE_ExteriorBlind", metallic=0.34, saturation=0.12, value=0.40, normal=0.18), tint=(0.025, 0.027, 0.028), factor=0.52, roughness=0.40),
            "interior": configure_occupied(pbr("interior", "MAT_W13_PASSIVE_DaylightRoomDepth", saturation=0.38, value=1.00, normal=0.045), warmth=(0.09, 0.055, 0.025), emission=0.025),
            "interior_evening": configure_occupied(pbr("interior_evening", "MAT_W13_PASSIVE_EveningRoomDepth", saturation=0.52, value=0.82, normal=0.045), warmth=(0.22, 0.12, 0.045), emission=0.095),
            "pv": configure_photovoltaic(pbr("pv", "MAT_W13_PASSIVE_MonocrystallinePVModule", metallic=0.10, saturation=0.76, value=0.72, normal=0.07), cfg),
            "green_roof": wash_material(pbr("green_roof", "MAT_W13_PASSIVE_SedumRoof", saturation=0.72, value=0.66, normal=0.60), tint=(0.24, 0.27, 0.095), factor=0.28, roughness=0.86),
            "zinc": pbr("zinc", "MAT_W13_PASSIVE_ZincEdges", metallic=0.62, saturation=0.12, value=0.68, normal=0.20),
            "facade_skin": pbr("facade", "MAT_W13_PASSIVE_RegisteredFacadeUnderlay", saturation=0.66, value=0.84, normal=0.10),
            "podium_skin": pbr("podium", "MAT_W13_PASSIVE_RegisteredPodiumUnderlay", saturation=0.62, value=0.82, normal=0.10),
            "floor_a_skin": pbr("floor_a", "MAT_W13_PASSIVE_RegisteredBayAUnderlay", saturation=0.62, value=0.84, normal=0.10),
            "floor_b_skin": pbr("floor_b", "MAT_W13_PASSIVE_RegisteredBayBUnderlay", saturation=0.62, value=0.84, normal=0.10),
            "crown_skin": pbr("crown", "MAT_W13_PASSIVE_RegisteredRoofUnderlay", saturation=0.54, value=0.76, normal=0.12),
            "side_skin": pbr("side", "MAT_W13_PASSIVE_RegisteredSideUnderlay", saturation=0.60, value=0.82, normal=0.10),
        }
        mats["panel"] = material("MAT_W13_PASSIVE_PaleInsulatedPanel", (0.70, 0.70, 0.66, 1.0), 0.56)
        mats["larch_plain"] = material("MAT_W13_PASSIVE_LarchGableField", (0.58, 0.38, 0.19, 1.0), 0.64)
        mats["room_shadow"] = material("MAT_W13_PASSIVE_DeepWarmRoomShadow", (0.095, 0.078, 0.060, 1.0), 0.84)
        mats["curtain"] = material("MAT_W13_PASSIVE_NaturalLinenCurtain", (0.67, 0.64, 0.56, 1.0), 0.82)
        mats["pv_frame"] = material("MAT_W13_PASSIVE_DarkAnodizedPVFrame", (0.055, 0.060, 0.065, 1.0), 0.27, 0.58)
        mats["roof"] = mats["zinc"]
        return mats, skin

    mats = {
        "terracotta": wash_material(
            pbr(
                "terracotta",
                "MAT_W13_DECO_CreamGlazedTerracotta",
                saturation=0.72,
                value=1.02,
                normal=0.42,
            ),
            tint=(0.73, 0.66, 0.52),
            factor=0.24,
            roughness=0.48,
        ),
        "granite": wash_material(
            pbr(
                "granite",
                "MAT_W13_DECO_CharcoalPolishedGranite",
                saturation=0.24,
                value=0.50,
                normal=0.25,
            ),
            tint=(0.045, 0.05, 0.048),
            factor=0.52,
            roughness=0.22,
        ),
        "frame": wash_material(
            pbr(
                "bronze",
                "MAT_W13_DECO_AgedDarkBronze",
                metallic=0.62,
                saturation=0.56,
                value=0.70,
                normal=0.18,
            ),
            tint=(0.22, 0.13, 0.065),
            factor=0.38,
            roughness=0.30,
        ),
        "glass": configure_glass(
            pbr(
                "vision_glass",
                "MAT_W13_DECO_NeutralSmokyLowEGlass",
                transmission=0.60,
                saturation=0.30,
                value=0.72,
                normal=0.06,
            ),
            cfg,
            tint=(0.18, 0.22, 0.21),
            transmission=0.80,
            alpha=0.34,
        ),
        "interior": configure_occupied(
            pbr(
                "interior",
                "MAT_W13_DECO_OccupiedRoomDepth",
                saturation=0.66,
                value=0.62,
                normal=0.08,
            ),
            warmth=(0.30, 0.15, 0.045),
            emission=0.12,
        ),
        "gold": wash_material(
            pbr(
                "gold",
                "MAT_W13_DECO_RestrainedGoldLeaf",
                metallic=0.78,
                saturation=0.78,
                value=0.94,
                normal=0.19,
            ),
            tint=(0.66, 0.43, 0.12),
            factor=0.30,
            roughness=0.27,
        ),
        "roof": pbr(
            "roof",
            "MAT_W13_DECO_DarkTerraceMembrane",
            saturation=0.22,
            value=0.46,
            normal=0.35,
        ),
        # Registered elevation strips are restrained underlays behind real parts.
        "facade_skin": pbr(
            "facade",
            "MAT_W13_DECO_RegisteredFacadeUnderlay",
            saturation=0.62,
            value=0.84,
            normal=0.12,
        ),
        "podium_skin": pbr(
            "podium",
            "MAT_W13_DECO_RegisteredPodiumUnderlay",
            saturation=0.64,
            value=0.70,
            normal=0.12,
        ),
        "floor_a_skin": pbr(
            "floor_a",
            "MAT_W13_DECO_RegisteredSevenBayUnderlay",
            saturation=0.66,
            value=0.84,
            normal=0.12,
        ),
        "floor_b_skin": pbr(
            "floor_b",
            "MAT_W13_DECO_RegisteredFiveBayUnderlay",
            saturation=0.66,
            value=0.84,
            normal=0.12,
        ),
        "crown_skin": pbr(
            "crown",
            "MAT_W13_DECO_RegisteredCrownUnderlay",
            saturation=0.70,
            value=0.88,
            normal=0.10,
        ),
        "side_skin": pbr(
            "side",
            "MAT_W13_DECO_RegisteredSideUnderlay",
            saturation=0.62,
            value=0.82,
            normal=0.10,
        ),
    }
    return mats, skin


def add_regular_polygon_prism(
    objects: list[bpy.types.Object],
    *,
    name: str,
    radius_bottom: float,
    radius_top: float,
    z_bottom: float,
    z_top: float,
    sides: int,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    rotation: float = math.pi / 8,
    role: str = "assembled",
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for z, radius in ((z_bottom, radius_bottom), (z_top, radius_top)):
        for index in range(sides):
            angle = rotation + math.tau * index / sides
            vertices.append((math.cos(angle) * radius, math.sin(angle) * radius, z))
    faces: list[tuple[int, ...]] = [tuple(reversed(range(sides))), tuple(range(sides, sides * 2))]
    for index in range(sides):
        nxt = (index + 1) % sides
        faces.append((index, nxt, sides + nxt, sides + index))
    return create_mesh_object(objects, name, vertices, faces, mat, cfg, semantic, role=role)


def _add_window_y_compact(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    facade_y: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    centre_mullion: bool = True,
) -> None:
    """Physical pane, occupied depth and separate bronze perimeter."""
    glass_y = facade_y
    interior_y = facade_y - outward_sign * 0.32
    frame_y = facade_y + outward_sign * 0.08
    add_box(objects, prefix + "_Occupied", (width - 0.18, 0.08, height - 0.16), (centre_x, interior_y, centre_z), mats["interior"], cfg, "occupied_depth", role=role)
    add_box(objects, prefix + "_Glass", (width - 0.12, 0.09, height - 0.10), (centre_x, glass_y, centre_z), mats["glass"], cfg, "physical_glazing", role=role)
    for x in (centre_x - width / 2, centre_x + width / 2):
        add_box(objects, prefix + f"_Jamb_{x:.2f}", (0.10, 0.18, height), (x, frame_y, centre_z), mats["frame"], cfg, "bronze_window_frame", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, prefix + f"_Rail_{z:.2f}", (width, 0.18, 0.10), (centre_x, frame_y, z), mats["frame"], cfg, "bronze_window_frame", role=role)
    if centre_mullion:
        add_box(objects, prefix + "_Mullion", (0.085, 0.18, height), (centre_x, frame_y, centre_z), mats["frame"], cfg, "bronze_window_mullion", role=role)


def _add_window_x_compact(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_y: float,
    facade_x: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    glass_x = facade_x
    interior_x = facade_x - outward_sign * 0.32
    frame_x = facade_x + outward_sign * 0.08
    add_box(objects, prefix + "_Occupied", (0.08, width - 0.18, height - 0.16), (interior_x, centre_y, centre_z), mats["interior"], cfg, "occupied_depth", role=role)
    add_box(objects, prefix + "_Glass", (0.09, width - 0.12, height - 0.10), (glass_x, centre_y, centre_z), mats["glass"], cfg, "physical_glazing", role=role)
    for y in (centre_y - width / 2, centre_y + width / 2):
        add_box(objects, prefix + f"_Jamb_{y:.2f}", (0.18, 0.10, height), (frame_x, y, centre_z), mats["frame"], cfg, "bronze_window_frame", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, prefix + f"_Rail_{z:.2f}", (0.18, width, 0.10), (frame_x, centre_y, z), mats["frame"], cfg, "bronze_window_frame", role=role)
    add_box(objects, prefix + "_Mullion", (0.18, 0.085, height), (frame_x, centre_y, centre_z), mats["frame"], cfg, "bronze_window_mullion", role=role)


def add_deco_storey(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    height: float,
    front_bays: int,
    side_bays: int,
    mats: dict,
    cfg: dict,
    variant: str,
    role: str = "assembled",
) -> None:
    """Construct one complete four-sided bay row with no painted openings."""
    slab = 0.18
    spandrel = 0.76
    # The reference is a masonry tower with narrow punched openings, not a
    # curtain-wall grid.  Leave substantial lintel and spandrel construction.
    window_height = height - slab - spandrel - 0.36
    window_z = base_z + slab + spandrel + window_height / 2
    add_box(objects, prefix + "_FloorSlab", (width, depth, slab), (0.0, 0.0, base_z + slab / 2), mats["terracotta"], cfg, "complete_terracotta_floor_edge", role=role)

    underlay = mats["floor_a_skin"] if variant in {"typical_a", "typical_c"} else mats["floor_b_skin"]
    # Registered elevation information is carried just behind physical openings.
    add_box(objects, prefix + "_FrontRegisteredUnderlay", (width - 0.45, 0.045, height - 0.28), (0.0, -depth / 2 + 0.44, base_z + height / 2), underlay, cfg, "registered_reference_underlay", role=role)
    add_box(objects, prefix + "_RearRegisteredUnderlay", (width - 0.45, 0.045, height - 0.28), (0.0, depth / 2 - 0.44, base_z + height / 2), mats["side_skin"], cfg, "registered_secondary_elevation_underlay", role=role)

    for face, y, sign in (("Front", -depth / 2 - 0.01, -1.0), ("Rear", depth / 2 + 0.01, 1.0)):
        pitch = width / front_bays
        for bay in range(front_bays):
            centre_x = -width / 2 + pitch * (bay + 0.5)
            window_width = min(pitch - 1.70, 2.25)
            _add_window_y_compact(
                objects,
                prefix=f"{prefix}_{face}_Window_{bay}",
                centre_x=centre_x,
                facade_y=y,
                centre_z=window_z,
                width=window_width,
                height=window_height,
                outward_sign=sign,
                mats=mats,
                cfg=cfg,
                role=role,
                centre_mullion=bay % 3 != 1,
            )
        add_box(objects, prefix + f"_{face}_Spandrel", (width, 0.34, spandrel), (0.0, y, base_z + slab + spandrel / 2), mats["terracotta"], cfg, "geometric_terracotta_spandrel", role=role)
        for index in range(front_bays + 1):
            x = -width / 2 + pitch * index
            add_box(objects, prefix + f"_{face}_Pier_{index}", (0.78, 0.48, height - slab), (x, y, base_z + slab + (height - slab) / 2), mats["terracotta"], cfg, "continuous_terracotta_pier", role=role)

    for face, x, sign in (("Left", -width / 2 - 0.01, -1.0), ("Right", width / 2 + 0.01, 1.0)):
        pitch = depth / side_bays
        for bay in range(side_bays):
            centre_y = -depth / 2 + pitch * (bay + 0.5)
            _add_window_x_compact(
                objects,
                prefix=f"{prefix}_{face}_Window_{bay}",
                centre_y=centre_y,
                facade_x=x,
                centre_z=window_z,
                width=min(pitch - 1.62, 2.20),
                height=window_height,
                outward_sign=sign,
                mats=mats,
                cfg=cfg,
                role=role,
            )
        add_box(objects, prefix + f"_{face}_Spandrel", (0.34, depth, spandrel), (x, 0.0, base_z + slab + spandrel / 2), mats["terracotta"], cfg, "wrapped_terracotta_spandrel", role=role)
        for index in range(side_bays + 1):
            y = -depth / 2 + pitch * index
            add_box(objects, prefix + f"_{face}_Pier_{index}", (0.48, 0.78, height - slab), (x, y, base_z + slab + (height - slab) / 2), mats["terracotta"], cfg, "wrapped_terracotta_pier", role=role)


def add_deco_podium(
    objects: list[bpy.types.Object],
    *,
    base_z: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    module: bool = False,
) -> None:
    width, depth, height = 31.0, 29.0, cfg["podium_height"]
    add_box(objects, "DECO_PodiumFloor", (width, depth, 0.30), (0.0, 0.0, base_z + 0.15), mats["granite"], cfg, "fixed_black_granite_podium_floor", role=role)
    add_box(objects, "DECO_PodiumRegisteredFront", (width - 0.6, 0.05, height - 0.4), (0.0, -depth / 2 + 0.48, base_z + height / 2), mats["podium_skin"], cfg, "registered_podium_reference_underlay", role=role)
    # Granite piers and real display windows create a public base, not a solid box.
    pitch = width / 7
    for bay in range(7):
        centre_x = -width / 2 + pitch * (bay + 0.5)
        if bay == 3:
            continue
        _add_window_y_compact(
            objects,
            prefix=f"DECO_PodiumDisplay_{bay}",
            centre_x=centre_x,
            facade_y=-depth / 2 - 0.02,
            centre_z=base_z + 3.05,
            width=pitch - 0.82,
            height=5.1,
            outward_sign=-1.0,
            mats=mats,
            cfg=cfg,
            role=role,
        )
    for index in range(8):
        x = -width / 2 + pitch * index
        add_box(objects, f"DECO_PodiumFrontPier_{index}", (0.62, 0.58, height), (x, -depth / 2, base_z + height / 2), mats["granite"], cfg, "polished_granite_podium_pier", role=role)
    add_box(objects, "DECO_PodiumFrontHeader", (width, 0.62, 1.05), (0.0, -depth / 2, base_z + height - 0.525), mats["granite"], cfg, "polished_granite_podium_header", role=role)
    # Deep, clearly recessed central entrance.
    portal_width = pitch - 0.55
    add_box(objects, "DECO_EntranceRecessCeiling", (portal_width, 2.1, 0.34), (0.0, -depth / 2 + 0.95, base_z + 5.7), mats["granite"], cfg, "deep_integral_entrance_recess", role=role)
    for side in (-1.0, 1.0):
        add_box(objects, f"DECO_EntranceBronzeReveal_{side}", (0.28, 2.2, 5.5), (side * portal_width / 2, -depth / 2 + 0.95, base_z + 2.95), mats["frame"], cfg, "bronze_entrance_reveal", role=role)
    for door in (-1.0, 1.0):
        add_box(objects, f"DECO_EntranceDoorGlass_{door}", (portal_width / 2 - 0.18, 0.12, 4.25), (door * portal_width / 4, -depth / 2 + 2.0, base_z + 2.3), mats["glass"], cfg, "recessed_glazed_entrance_door", role=role)
        add_box(objects, f"DECO_EntranceDoorFrame_{door}", (0.11, 0.20, 4.4), (door * 0.04, -depth / 2 + 1.92, base_z + 2.3), mats["frame"], cfg, "bronze_entrance_door_frame", role=role)
    add_box(objects, "DECO_EntranceCanopy", (portal_width + 0.9, 2.5, 0.22), (0.0, -depth / 2 - 1.0, base_z + 5.65), mats["gold"], cfg, "integral_gilded_entrance_canopy", role=role)
    # Side and rear elevations retain full construction hierarchy.
    for face, x, sign in (("Left", -width / 2, -1.0), ("Right", width / 2, 1.0)):
        side_pitch = depth / 6
        for bay in range(6):
            centre_y = -depth / 2 + side_pitch * (bay + 0.5)
            _add_window_x_compact(objects, prefix=f"DECO_Podium{face}_{bay}", centre_y=centre_y, facade_x=x, centre_z=base_z + 3.0, width=side_pitch - 0.92, height=4.75, outward_sign=sign, mats=mats, cfg=cfg, role=role)
        for index in range(7):
            y = -depth / 2 + side_pitch * index
            add_box(objects, f"DECO_Podium{face}Pier_{index}", (0.56, 0.62, height), (x, y, base_z + height / 2), mats["granite"], cfg, "wrapped_granite_podium_pier", role=role)
    rear_pitch = width / 7
    for bay in range(7):
        _add_window_y_compact(objects, prefix=f"DECO_PodiumRear_{bay}", centre_x=-width / 2 + rear_pitch * (bay + 0.5), facade_y=depth / 2, centre_z=base_z + 3.0, width=rear_pitch - 0.85, height=4.7, outward_sign=1.0, mats=mats, cfg=cfg, role=role)
    if not module:
        # Bronze geometric grille panels flank the public door.
        for side in (-1.0, 1.0):
            centre = side * (portal_width / 2 + 0.8)
            for offset in (-0.38, 0.0, 0.38):
                add_beam(objects, f"DECO_EntranceGrille_{side}_{offset}", (centre - 0.65, -depth / 2 - 0.38, base_z + 0.8 + offset), (centre + 0.65, -depth / 2 - 0.38, base_z + 4.8 - offset), 0.045, mats["frame"], cfg, "art_deco_entrance_grille", role=role)


def add_deco_crown(
    objects: list[bpy.types.Object],
    *,
    base_z: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    include_roof: bool = True,
) -> None:
    # Three full terraces make the silhouette legible at thumbnail scale.
    for index, (width, depth, height, mat) in enumerate(
        ((16.8, 16.8, 0.7, mats["terracotta"]), (13.2, 13.2, 0.9, mats["terracotta"]), (9.6, 9.6, 1.4, mats["terracotta"]))
    ):
        z = base_z + sum((0.7, 1.0, 1.3)[:index]) + height / 2
        add_box(objects, f"DECO_CrownStep_{index}", (width, depth, height), (0.0, 0.0, z), mat, cfg, "fixed_stepped_crown_plinth", role=role)
    lantern_base = base_z + 3.0
    # Warm interior and smoky glass form a true faceted lantern volume.
    add_regular_polygon_prism(objects, name="DECO_LanternOccupiedCore", radius_bottom=2.95, radius_top=2.95, z_bottom=lantern_base + 0.2, z_top=lantern_base + 5.7, sides=8, mat=mats["interior"], cfg=cfg, semantic="occupied_octagonal_lantern_depth", role=role)
    add_regular_polygon_prism(objects, name="DECO_LanternSmokyGlass", radius_bottom=3.42, radius_top=3.42, z_bottom=lantern_base, z_top=lantern_base + 6.0, sides=8, mat=mats["glass"], cfg=cfg, semantic="physical_octagonal_lantern_glazing", role=role)
    for post in range(8):
        angle = math.pi / 8 + math.tau * post / 8
        x, y = math.cos(angle) * 3.48, math.sin(angle) * 3.48
        add_cylinder(objects, f"DECO_LanternGoldPost_{post}", 0.14, 6.5, (x, y, lantern_base + 3.25), mats["gold"], cfg, "eight_separate_gilded_lantern_posts", vertices=10, role=role)
    add_regular_polygon_prism(objects, name="DECO_LanternGoldSill", radius_bottom=3.84, radius_top=3.84, z_bottom=lantern_base - 0.12, z_top=lantern_base + 0.20, sides=8, mat=mats["gold"], cfg=cfg, semantic="gilded_lantern_sill", role=role)
    if include_roof:
        roof_base = lantern_base + 6.0
        add_regular_polygon_prism(objects, name="DECO_FacetedGoldLanternCap", radius_bottom=4.15, radius_top=0.48, z_bottom=roof_base, z_top=roof_base + 2.55, sides=8, mat=mats["gold"], cfg=cfg, semantic="fixed_faceted_gilded_lantern_cap", role=role)
        add_cylinder(objects, "DECO_GoldFinialStem", 0.12, 1.55, (0.0, 0.0, roof_base + 3.28), mats["gold"], cfg, "fixed_gilded_finial", vertices=10, role=role)
        add_regular_polygon_prism(objects, name="DECO_GoldFinialTip", radius_bottom=0.34, radius_top=0.0, z_bottom=roof_base + 4.0, z_top=roof_base + 4.65, sides=8, mat=mats["gold"], cfg=cfg, semantic="fixed_gilded_finial_tip", role=role)


def add_sunburst(
    objects: list[bpy.types.Object],
    *,
    centre: tuple[float, float, float],
    radius: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    cx, cy, cz = centre
    for ray in range(9):
        angle = math.radians(18 + ray * 18)
        end = (cx + math.cos(angle) * radius, cy, cz + math.sin(angle) * radius)
        add_beam(objects, f"DECO_SunburstRay_{ray}", (cx, cy, cz), end, 0.065, mats["gold"], cfg, "fixed_shallow_sunburst_ornament", role=role)
    add_box(objects, "DECO_SunburstBase", (radius * 2.1, 0.18, 0.14), (cx, cy, cz), mats["gold"], cfg, "fixed_sunburst_base", role=role)


def add_front_rosette(
    objects: list[bpy.types.Object],
    *,
    name: str,
    x: float,
    y: float,
    z: float,
    mats: dict,
    cfg: dict,
) -> None:
    disc = add_cylinder(objects, name, 0.22, 0.12, (x, y, z), mats["gold"], cfg, "gilded_setback_belt_rosette", vertices=12)
    disc.rotation_euler[0] = math.radians(90.0)


def build_art_deco(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_deco_podium(objects, base_z=0.0, mats=mats, cfg=cfg)
    z = cfg["podium_height"]
    tiers = (
        # width, depth, floors, front bays, side bays
        (30.0, 26.0, 8, 7, 6),
        (23.0, 21.0, 3, 5, 4),
        (16.0, 15.0, 2, 3, 3),
    )
    floor_index = 0
    for tier_index, (width, depth, floors, front_bays, side_bays) in enumerate(tiers):
        if tier_index:
            add_box(objects, f"DECO_SetbackTerrace_{tier_index}", (width + 3.0, depth + 3.0, 0.35), (0.0, 0.0, z + 0.175), mats["roof"], cfg, "complete_setback_terrace")
            add_box(objects, f"DECO_SetbackGoldBelt_{tier_index}", (width + 0.42, depth + 0.42, 0.28), (0.0, 0.0, z + 0.58), mats["gold"], cfg, "continuous_gilded_setback_belt")
        tier_base = z
        for local_floor in range(floors):
            variant = ("typical_a", "typical_b", "typical_c")[(floor_index + tier_index) % 3]
            add_deco_storey(objects, prefix=f"DECO_Tier{tier_index}_Floor{local_floor}", width=width, depth=depth, base_z=z, height=cfg["floor_height"], front_bays=front_bays, side_bays=side_bays, mats=mats, cfg=cfg, variant=variant)
            z += cfg["floor_height"]
            floor_index += 1
        tier_height = floors * cfg["floor_height"]
        # Raised full-tier fins restore the strong continuous vertical reading
        # of the source tower and visually bind the per-floor LEGO modules.
        for face, y in (("Front", -depth / 2 - 0.27), ("Rear", depth / 2 + 0.27)):
            pitch = width / front_bays
            for index in range(front_bays + 1):
                x = -width / 2 + pitch * index
                add_box(objects, f"DECO_Tier{tier_index}_{face}ContinuousFin_{index}", (0.44, 0.34, tier_height + 0.75), (x, y, tier_base + tier_height / 2 + 0.25), mats["terracotta"], cfg, "full_tier_projecting_terracotta_fin")
        for face, x in (("Left", -width / 2 - 0.27), ("Right", width / 2 + 0.27)):
            pitch = depth / side_bays
            for index in range(side_bays + 1):
                y = -depth / 2 + pitch * index
                add_box(objects, f"DECO_Tier{tier_index}_{face}ContinuousFin_{index}", (0.34, 0.44, tier_height + 0.75), (x, y, tier_base + tier_height / 2 + 0.25), mats["terracotta"], cfg, "wrapped_full_tier_projecting_fin")
        # Deep paired pylons bookend the central bay group and create the same
        # layered shaft-with-shoulders reading as the four-view goalpost.
        central_half = width * (0.35 if front_bays >= 5 else 0.30)
        for face, y in (("Front", -depth / 2 - 0.46), ("Rear", depth / 2 + 0.46)):
            for x in (-central_half, central_half):
                add_box(objects, f"DECO_Tier{tier_index}_{face}CentralPylon_{x}", (0.92, 0.48, tier_height + 1.15), (x, y, tier_base + tier_height / 2 + 0.34), mats["terracotta"], cfg, "integral_central_shaft_pylon")
                for flute in (-0.24, 0.0, 0.24):
                    add_box(objects, f"DECO_Tier{tier_index}_{face}CentralPylonFlute_{x}_{flute}", (0.055, 0.54, tier_height - 0.5), (x + flute, y - (0.04 if face == "Front" else -0.04), tier_base + tier_height / 2), mats["gold"], cfg, "restrained_vertical_pylon_flute")
        if tier_index < 2:
            # Integral shoulder pylons grow directly out of each setback corner.
            for x in (-width / 2 + 1.0, width / 2 - 1.0):
                for y in (-depth / 2 + 1.0, depth / 2 - 1.0):
                    add_box(objects, f"DECO_Tier{tier_index}_ShoulderPylon_{x}_{y}", (1.35, 1.35, 3.25), (x, y, z + 1.40), mats["terracotta"], cfg, "integral_setback_shoulder_pylon")
                    add_cylinder(objects, f"DECO_Tier{tier_index}_ShoulderPylonCap_{x}_{y}", 0.19, 1.15, (x, y, z + 3.48), mats["gold"], cfg, "restrained_gilded_shoulder_finial", vertices=8)
        if tier_index == 0:
            # A shallow registered belt with individual metal rosettes replaces
            # the first-render's lone decorative fan.
            belt_z = z - 0.38
            add_box(objects, "DECO_FirstSetbackTerracottaBelt", (width + 0.55, 0.48, 0.72), (0.0, -depth / 2 - 0.29, belt_z), mats["terracotta"], cfg, "continuous_geometric_setback_belt")
            for bay in range(front_bays):
                add_front_rosette(objects, name=f"DECO_FirstSetbackRosette_{bay}", x=-width / 2 + (bay + 0.5) * width / front_bays, y=-depth / 2 - 0.56, z=belt_z, mats=mats, cfg=cfg)
    # First major terrace identity relief, clearly integrated with the facade.
    add_sunburst(objects, centre=(0.0, -13.58, cfg["podium_height"] + 8 * cfg["floor_height"] + 0.20), radius=1.55, mats=mats, cfg=cfg)
    # Fluted corner caps reinforce the vertical silhouette without becoming columns pasted on top.
    for x in (-8.0, 8.0):
        for y in (-7.5, 7.5):
            add_box(objects, f"DECO_UpperCornerCap_{x}_{y}", (0.62, 0.62, 8.7), (x, y, z - 4.0), mats["terracotta"], cfg, "integral_fluted_corner_cap")
            for groove in (-0.18, 0.0, 0.18):
                add_box(objects, f"DECO_UpperCornerFlute_{x}_{y}_{groove}", (0.055, 0.68, 7.8), (x + groove, y, z - 4.0), mats["gold"], cfg, "restrained_corner_flute")
    add_deco_crown(objects, base_z=z, mats=mats, cfg=cfg)
    return objects


def add_koshi_panel_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    facade_y: float,
    base_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    slat_pitch: float = 0.27,
) -> None:
    """Fine timber lattice with real gaps, physical pane and room depth."""
    centre_z = base_z + height / 2
    add_box(objects, prefix + "_OccupiedDepth", (width - 0.16, 0.08, height - 0.14), (centre_x, facade_y - outward_sign * 0.34, centre_z), mats["interior"], cfg, "warm_occupied_machiya_depth", role=role)
    add_box(objects, prefix + "_PhysicalGlass", (width - 0.12, 0.08, height - 0.10), (centre_x, facade_y - outward_sign * 0.08, centre_z), mats["glass"], cfg, "physical_smoky_machiya_glazing", role=role)
    screen_y = facade_y + outward_sign * 0.11
    slats = max(5, round(width / slat_pitch))
    actual_pitch = width / slats
    for index in range(slats + 1):
        x = centre_x - width / 2 + index * actual_pitch
        add_box(objects, prefix + f"_VerticalKoshi_{index}", (0.055, 0.105, height), (x, screen_y, centre_z), mats["lattice"], cfg, "real_gap_preserving_koshi_lattice", role=role)
    for ratio in (0.0, 0.34, 0.68, 1.0):
        add_box(objects, prefix + f"_HorizontalKoshi_{ratio}", (width + 0.10, 0.13, 0.075), (centre_x, screen_y, base_z + height * ratio), mats["lattice"], cfg, "koshi_lattice_cross_rail", role=role)
    for x in (centre_x - width / 2, centre_x + width / 2):
        add_box(objects, prefix + f"_Frame_{x}", (0.16, 0.18, height + 0.14), (x, screen_y, centre_z), mats["timber"], cfg, "machiya_post_and_beam_frame", role=role)


def add_machiya_gable_roof(
    objects: list[bpy.types.Object],
    *,
    base_z: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    compact: bool = False,
) -> None:
    width = 19.4 if not compact else 18.4
    depth = 15.4 if not compact else 14.4
    ridge_z = base_z + 4.55
    create_gable_roof(objects, name="MACHIYA_KawaraGableMass", centre=(0.0, 0.0), length=depth, depth=width, base_z=base_z, ridge_z=ridge_z, orientation="y", mat=mats["tile"], cfg=cfg, role=role)
    # The ridge runs away from the street so the public facade owns the broad
    # framed gable shown in the locked reference board.
    half_span = width / 2
    for row in range(17):
        x = -half_span + width * row / 16
        z = base_z + (ridge_z - base_z) * (1.0 - abs(x) / half_span) + 0.08
        add_beam(objects, f"MACHIYA_KawaraRow_{row}", (x, -depth / 2 - 0.18, z), (x, depth / 2 + 0.18, z), 0.072, mats["tile"], cfg, "individual_kawara_tile_row", role=role)
    add_beam(objects, "MACHIYA_KawaraRidgeCap", (0.0, -depth / 2 - 0.30, ridge_z + 0.18), (0.0, depth / 2 + 0.30, ridge_z + 0.18), 0.19, mats["tile"], cfg, "continuous_kawara_ridge_cap", role=role)
    # Hundreds of shallow overlapping modules replace a smooth roof texture.
    slope_angle = math.atan2(ridge_z - base_z, half_span)
    for side in (-1.0, 1.0):
        for slope_row in range(11):
            distance = (slope_row + 0.5) * half_span / 11
            x = side * (half_span - distance)
            z = base_z + (ridge_z - base_z) * distance / half_span + 0.13
            for column in range(17):
                y = -depth / 2 + (column + 0.5) * depth / 17
                tile = add_box(objects, f"MACHIYA_KawaraModule_{side}_{slope_row}_{column}", (half_span / 10.5, depth / 16.4, 0.065), (x, y, z), mats["tile"], cfg, "overlapping_physical_kawara_tile_module", role=role)
                tile.rotation_euler[1] = slope_angle if side > 0 else -slope_angle
    # Exposed rafters run beneath both planes and project beyond the walls.
    for index in range(19):
        y = -depth / 2 + index * depth / 18
        add_beam(objects, f"MACHIYA_LeftRafter_{index}", (-half_span - 0.12, y, base_z - 0.10), (0.0, y, ridge_z - 0.08), 0.055, mats["timber"], cfg, "exposed_deep_eave_rafter", role=role)
        add_beam(objects, f"MACHIYA_RightRafter_{index}", (0.0, y, ridge_z - 0.08), (half_span + 0.12, y, base_z - 0.10), 0.055, mats["timber"], cfg, "exposed_deep_eave_rafter", role=role)
    for x in (-half_span - 0.08, half_span + 0.08):
        add_beam(objects, f"MACHIYA_EaveGutter_{x}", (x, -depth / 2, base_z - 0.02), (x, depth / 2, base_z - 0.02), 0.105, mats["tile"], cfg, "blackened_copper_eave_gutter", role=role)
        # Rounded ceramic noses make the long kawara eaves read as an
        # overlapping tile assembly instead of a smooth dark roof edge.
        for index in range(18):
            y = -depth / 2 + (index + 0.5) * depth / 18
            nose = add_cylinder(objects, f"MACHIYA_MainEaveTileNose_{x}_{index}", 0.105, 0.20, (x, y, base_z + 0.01), mats["tile"], cfg, "individual_kawara_eave_tile_nose", vertices=8, role=role)
            nose.rotation_euler[1] = math.radians(90.0)
    # White clay gables and dark timber geometry sit just outside the tiled end caps.
    for face, y in (("Front", -depth / 2 - 0.03), ("Rear", depth / 2 + 0.03)):
        vertices = [(-half_span, y, base_z), (half_span, y, base_z), (0.0, y, ridge_z)]
        create_mesh_object(objects, f"MACHIYA_{face}WhiteClayGable", vertices, [(0, 1, 2)], mats["plaster"], cfg, "white_clay_gable_infill", role=role)
        add_beam(objects, f"MACHIYA_{face}LeftGableRake", (-half_span, y - (0.03 if face == "Front" else -0.03), base_z), (0.0, y - (0.03 if face == "Front" else -0.03), ridge_z), 0.10, mats["timber"], cfg, "exposed_gable_rake_timber", role=role)
        add_beam(objects, f"MACHIYA_{face}RightGableRake", (0.0, y - (0.03 if face == "Front" else -0.03), ridge_z), (half_span, y - (0.03 if face == "Front" else -0.03), base_z), 0.10, mats["timber"], cfg, "exposed_gable_rake_timber", role=role)
        add_box(objects, f"MACHIYA_{face}GableTie", (width, 0.18, 0.20), (0.0, y, base_z + 0.18), mats["timber"], cfg, "continuous_gable_tie_beam", role=role)
        for x in (-4.5, 0.0, 4.5):
            top = ridge_z - abs(x) / half_span * (ridge_z - base_z)
            add_box(objects, f"MACHIYA_{face}GablePost_{x}", (0.16, 0.20, top - base_z), (x, y, (top + base_z) / 2), mats["timber"], cfg, "visible_gable_post_and_beam", role=role)


def build_machiya(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    width, depth, wall_height = 18.0, 14.0, 6.70
    add_box(objects, "MACHIYA_StoneSill", (18.6, 14.6, 0.30), (0.0, 0.0, 0.15), mats["stone"], cfg, "fixed_stone_and_pebble_sill")
    # Thin registered underlays remain behind separately constructed frames.
    add_box(objects, "MACHIYA_FrontRegisteredUnderlay", (width - 0.25, 0.055, wall_height - 0.22), (0.0, -depth / 2 + 0.36, wall_height / 2), mats["facade_skin"], cfg, "registered_machiya_reference_underlay")
    add_box(objects, "MACHIYA_RearPlasterWall", (width, 0.28, wall_height), (0.0, depth / 2, wall_height / 2), mats["plaster"], cfg, "complete_rear_clay_infill")
    add_box(objects, "MACHIYA_LeftPlasterWall", (0.28, depth, wall_height), (-width / 2, 0.0, wall_height / 2), mats["plaster"], cfg, "complete_side_clay_infill")
    add_box(objects, "MACHIYA_RightPlasterWall", (0.28, depth, wall_height), (width / 2, 0.0, wall_height / 2), mats["plaster"], cfg, "complete_side_clay_infill")
    # Structural grid on every elevation.
    for x in (-9.0, -6.0, -3.0, 0.0, 3.0, 6.0, 9.0):
        add_box(objects, f"MACHIYA_FrontPost_{x}", (0.22, 0.32, wall_height), (x, -7.05, wall_height / 2), mats["timber"], cfg, "continuous_machiya_timber_post")
        add_box(objects, f"MACHIYA_RearPost_{x}", (0.22, 0.32, wall_height), (x, 7.05, wall_height / 2), mats["timber"], cfg, "continuous_machiya_timber_post")
    for z in (0.35, 3.35, 6.55):
        add_box(objects, f"MACHIYA_FrontBeam_{z}", (18.2, 0.34, 0.24), (0.0, -7.08, z), mats["timber"], cfg, "continuous_machiya_timber_beam")
        add_box(objects, f"MACHIYA_RearBeam_{z}", (18.2, 0.34, 0.24), (0.0, 7.08, z), mats["timber"], cfg, "continuous_machiya_timber_beam")
    # Six upper panels form one continuous screen; ground level retains entry.
    for bay in range(6):
        cx = -7.5 + bay * 3.0
        add_koshi_panel_y(objects, prefix=f"MACHIYA_UpperKoshi_{bay}", centre_x=cx, facade_y=-7.12, base_z=3.62, width=2.70, height=2.55, outward_sign=-1.0, mats=mats, cfg=cfg)
        if bay not in (1, 2):
            add_koshi_panel_y(objects, prefix=f"MACHIYA_GroundKoshi_{bay}", centre_x=cx, facade_y=-7.13, base_z=0.58, width=2.65, height=2.35, outward_sign=-1.0, mats=mats, cfg=cfg, slat_pitch=0.23)
    # Entrance is carved behind the street eave and framed by plain noren.
    add_box(objects, "MACHIYA_EntranceOccupied", (5.4, 0.08, 2.55), (-1.5, -6.62, 1.62), mats["interior"], cfg, "deeply_recessed_machiya_entrance")
    add_box(objects, "MACHIYA_EntranceDoor", (2.25, 0.12, 2.45), (-0.45, -6.78, 1.58), mats["glass"], cfg, "recessed_glazed_machiya_door")
    for panel in range(3):
        x = -4.05 + panel * 1.45
        add_box(objects, f"MACHIYA_PlainIndigoNoren_{panel}", (1.25, 0.055, 1.30), (x, -7.46, 2.36), mats["indigo"], cfg, "three_separate_plain_indigo_noren_panels")
    # Lower tiled street eave is a genuine sloped plane with rafters and rows.
    lower = add_box(objects, "MACHIYA_LowerStreetKawaraRoof", (19.1, 3.2, 0.24), (0.0, -7.15, 3.66), mats["tile"], cfg, "fixed_lower_tiled_street_eave")
    lower.rotation_euler[0] = math.radians(9.0)
    for index in range(19):
        x = -9.0 + index
        add_beam(objects, f"MACHIYA_LowerEaveRafter_{index}", (x, -8.7, 3.35), (x, -5.6, 3.88), 0.045, mats["timber"], cfg, "exposed_lower_eave_rafter")
    for row, y in enumerate((-8.55, -7.95, -7.35, -6.75, -6.15)):
        z = 3.35 + (y + 8.55) * 0.17
        add_beam(objects, f"MACHIYA_LowerKawaraRow_{row}", (-9.55, y, z), (9.55, y, z), 0.07, mats["tile"], cfg, "individual_lower_kawara_row")
    for index in range(24):
        x = -9.2 + (index + 0.5) * 18.4 / 24
        nose = add_cylinder(objects, f"MACHIYA_LowerEaveTileNose_{index}", 0.095, 0.20, (x, -8.67, 3.34), mats["tile"], cfg, "individual_lower_kawara_eave_tile_nose", vertices=8)
        nose.rotation_euler[0] = math.radians(90.0)
    # Side/rear timber grid and a few true openings prevent blank elevations.
    for x, sign in ((-9.08, -1.0), (9.08, 1.0)):
        for y in (-6.8, -3.4, 0.0, 3.4, 6.8):
            add_box(objects, f"MACHIYA_SidePost_{x}_{y}", (0.32, 0.22, wall_height), (x, y, wall_height / 2), mats["timber"], cfg, "wrapped_machiya_timber_post")
        for z in (0.35, 3.35, 6.55):
            add_box(objects, f"MACHIYA_SideBeam_{x}_{z}", (0.34, depth, 0.22), (x, 0.0, z), mats["timber"], cfg, "wrapped_machiya_timber_beam")
        for y in (-4.8, 2.0):
            _add_window_x_compact(objects, prefix=f"MACHIYA_SideWindow_{x}_{y}", centre_y=y, facade_x=x + sign * 0.08, centre_z=4.7, width=2.0, height=1.65, outward_sign=sign, mats=mats, cfg=cfg)
    for x in (-5.5, 0.0, 5.5):
        add_koshi_panel_y(objects, prefix=f"MACHIYA_RearKoshi_{x}", centre_x=x, facade_y=7.14, base_z=3.7, width=3.6, height=2.3, outward_sign=1.0, mats=mats, cfg=cfg, slat_pitch=0.32)
    # Integral side garden and drainage details.
    garden_mat = material("MAT_W13_MACHIYA_Bamboo", (0.18, 0.28, 0.08, 1.0), 0.78)
    for stem, (x, y, height) in enumerate(((8.45, -4.8, 2.2), (8.55, -3.9, 2.8), (8.42, -3.1, 2.45))):
        add_cylinder(objects, f"MACHIYA_BambooStem_{stem}", 0.045, height, (x, y, 0.3 + height / 2), garden_mat, cfg, "integral_side_garden_bamboo", vertices=7)
    for x in (-8.85, 8.85):
        add_cylinder(objects, f"MACHIYA_Downpipe_{x}", 0.07, 6.45, (x, -7.38, 3.28), mats["tile"], cfg, "blackened_copper_downpipe", vertices=10)
    add_machiya_gable_roof(objects, base_z=6.65, mats=mats, cfg=cfg)
    return objects


def add_pavilion_window_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    facade_y: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str,
    phase: int,
) -> None:
    """Build a clear pane in front of a genuinely deep gallery section."""
    pane_y = facade_y - outward_sign * 0.10
    frame_y = facade_y + outward_sign * 0.025
    interior_y = facade_y - outward_sign * 2.65
    cavity_mid_y = (pane_y + interior_y) / 2
    cavity_depth = abs(interior_y - pane_y)
    add_box(objects, prefix + "_LowIronPane", (width - 0.10, 0.055, height - 0.08), (centre_x, pane_y, centre_z), mats["glass"], cfg, "high_transmission_low_iron_pane", role=role)
    for edge, z, mat in (
        ("Floor", centre_z - height / 2 + 0.035, mats["gallery_floor"]),
        ("Ceiling", centre_z + height / 2 - 0.035, mats["ceiling"]),
    ):
        add_box(objects, prefix + f"_{edge}Return", (width - 0.08, cavity_depth, 0.055), (centre_x, cavity_mid_y, z), mat, cfg, "physical_gallery_floor_or_ceiling_return", role=role)
    for x in (centre_x - width / 2, centre_x + width / 2):
        add_box(objects, prefix + f"_PressureCap_{x:.2f}", (0.055, 0.105, height), (x, frame_y, centre_z), mats["steel"], cfg, "slender_pavilion_pressure_cap", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, prefix + f"_Rail_{z:.2f}", (width, 0.105, 0.055), (centre_x, frame_y, z), mats["steel"], cfg, "slender_pavilion_pressure_cap", role=role)
    add_box(objects, prefix + "_FineMullion", (0.045, 0.095, height - 0.08), (centre_x, frame_y, centre_z), mats["steel"], cfg, "fine_pavilion_mullion", role=role)


def add_pavilion_window_x(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_y: float,
    facade_x: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str,
    phase: int,
) -> None:
    pane_x = facade_x - outward_sign * 0.10
    frame_x = facade_x + outward_sign * 0.025
    interior_x = facade_x - outward_sign * 2.65
    cavity_mid_x = (pane_x + interior_x) / 2
    cavity_depth = abs(interior_x - pane_x)
    add_box(objects, prefix + "_LowIronPane", (0.055, width - 0.10, height - 0.08), (pane_x, centre_y, centre_z), mats["glass"], cfg, "high_transmission_low_iron_pane", role=role)
    for edge, z, mat in (
        ("Floor", centre_z - height / 2 + 0.035, mats["gallery_floor"]),
        ("Ceiling", centre_z + height / 2 - 0.035, mats["ceiling"]),
    ):
        add_box(objects, prefix + f"_{edge}Return", (cavity_depth, width - 0.08, 0.055), (cavity_mid_x, centre_y, z), mat, cfg, "physical_gallery_floor_or_ceiling_return", role=role)
    for y in (centre_y - width / 2, centre_y + width / 2):
        add_box(objects, prefix + f"_PressureCap_{y:.2f}", (0.105, 0.055, height), (frame_x, y, centre_z), mats["steel"], cfg, "slender_pavilion_pressure_cap", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, prefix + f"_Rail_{z:.2f}", (0.105, width, 0.055), (frame_x, centre_y, z), mats["steel"], cfg, "slender_pavilion_pressure_cap", role=role)
    add_box(objects, prefix + "_FineMullion", (0.095, 0.045, height - 0.08), (frame_x, centre_y, centre_z), mats["steel"], cfg, "fine_pavilion_mullion", role=role)


def add_curtain_storey(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    height: float,
    front_bays: int,
    side_bays: int,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    structure_semantic: str = "complete_curtain_wall_structural_bay",
) -> None:
    pavilion = cfg["family"] == "mid-century-glass-steel-pavilion"
    slab = 0.20 if pavilion else 0.24
    add_box(objects, prefix + "_FloorPlate", (width, depth, slab), (0.0, 0.0, base_z + slab / 2), mats["concrete"], cfg, "visible_concrete_floor_plate", role=role)
    panel_height = height - 0.48
    centre_z = base_z + slab + panel_height / 2
    for face, y, sign in (("Front", -depth / 2, -1.0), ("Rear", depth / 2, 1.0)):
        pitch = width / front_bays
        for bay in range(front_bays):
            if pavilion:
                add_pavilion_window_y(objects, prefix=f"{prefix}_{face}_{bay}", centre_x=-width / 2 + pitch * (bay + 0.5), facade_y=y, centre_z=centre_z, width=pitch - 0.16, height=panel_height, outward_sign=sign, mats=mats, cfg=cfg, role=role, phase=bay + sum(ord(char) for char in prefix))
            else:
                _add_window_y_compact(objects, prefix=f"{prefix}_{face}_{bay}", centre_x=-width / 2 + pitch * (bay + 0.5), facade_y=y, centre_z=centre_z, width=pitch - 0.16, height=panel_height, outward_sign=sign, mats=mats, cfg=cfg, role=role, centre_mullion=False)
        for index in range(front_bays + 1):
            x = -width / 2 + pitch * index
            add_box(objects, f"{prefix}_{face}_Structure_{index}", (0.14 if pavilion else 0.17, 0.21 if pavilion else 0.25, height), (x, y + sign * 0.09, base_z + height / 2), mats["steel"], cfg, structure_semantic, role=role)
    for face, x, sign in (("Left", -width / 2, -1.0), ("Right", width / 2, 1.0)):
        pitch = depth / side_bays
        for bay in range(side_bays):
            if pavilion:
                add_pavilion_window_x(objects, prefix=f"{prefix}_{face}_{bay}", centre_y=-depth / 2 + pitch * (bay + 0.5), facade_x=x, centre_z=centre_z, width=pitch - 0.16, height=panel_height, outward_sign=sign, mats=mats, cfg=cfg, role=role, phase=bay + sum(ord(char) for char in prefix))
            else:
                _add_window_x_compact(objects, prefix=f"{prefix}_{face}_{bay}", centre_y=-depth / 2 + pitch * (bay + 0.5), facade_x=x, centre_z=centre_z, width=pitch - 0.16, height=panel_height, outward_sign=sign, mats=mats, cfg=cfg, role=role)
        for index in range(side_bays + 1):
            y = -depth / 2 + pitch * index
            add_box(objects, f"{prefix}_{face}_Structure_{index}", (0.21 if pavilion else 0.25, 0.14 if pavilion else 0.17, height), (x + sign * 0.09, y, base_z + height / 2), mats["steel"], cfg, structure_semantic, role=role)


def build_pavilion(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    width, depth, storey = 24.0, 16.5, 3.65
    add_box(objects, "PAVILION_TravertinePlinth", (25.0, 17.4, 0.46), (0.0, 0.0, 0.23), mats["travertine"], cfg, "fixed_honed_travertine_plinth")
    for floor in range(3):
        add_curtain_storey(objects, prefix=f"PAVILION_Floor_{floor}", width=width, depth=depth, base_z=0.35 + floor * storey, height=storey, front_bays=7, side_bays=5, mats=mats, cfg=cfg)
        # A dark perimeter fascia hides the pale slab edge and creates the
        # strong horizontal steel datum visible in the reference elevations.
        slab_z = 0.35 + floor * storey + 0.13
        for face, y in (("Front", -depth / 2 - 0.12), ("Rear", depth / 2 + 0.12)):
            add_box(objects, f"PAVILION_{face}SlabFascia_{floor}", (width + 0.24, 0.16, 0.30), (0.0, y, slab_z), mats["steel"], cfg, "continuous_black_steel_slab_edge_fascia")
        for face, x in (("Left", -width / 2 - 0.12), ("Right", width / 2 + 0.12)):
            add_box(objects, f"PAVILION_{face}SlabFascia_{floor}", (0.16, depth + 0.24, 0.30), (x, 0.0, slab_z), mats["steel"], cfg, "continuous_black_steel_slab_edge_fascia")
        # Two-piece recessed downlights give the transparent pavilion real
        # occupied ceiling depth.  Their repeated circular trims are visible
        # through the low-iron glass without baking lights into every pane.
        ceiling_z = 0.35 + floor * storey + storey - 0.20
        for ix, x in enumerate((-8.0, -4.0, 0.0, 4.0, 8.0)):
            for iy, y in enumerate((-5.5, -1.85, 1.85, 5.5)):
                add_cylinder(objects, f"PAVILION_CeilingLightTrim_{floor}_{ix}_{iy}", 0.12, 0.055, (x, y, ceiling_z), mats["steel"], cfg, "physical_recessed_gallery_downlight_trim", vertices=12)
                add_cylinder(objects, f"PAVILION_CeilingLightLens_{floor}_{ix}_{iy}", 0.078, 0.060, (x, y, ceiling_z - 0.038), mats["interior_evening"], cfg, "warm_recessed_gallery_downlight_lens", vertices=12)
        # Sparse real furniture and partitions make the transparent envelope
        # spatial without turning each pane into the same opaque room picture.
        occupied_z = 0.35 + floor * storey + 0.55
        for item, (x, y) in enumerate(((-6.2 + floor, 2.8), (2.8, -2.5 + floor), (7.0 - floor, 4.3))):
            add_box(objects, f"PAVILION_GalleryBench_{floor}_{item}", (2.2, 0.62, 0.13), (x, y, occupied_z + 0.42), mats["gallery_wood"], cfg, "sparse_physical_gallery_bench", role="assembled")
            for leg in (-0.78, 0.78):
                add_box(objects, f"PAVILION_GalleryBenchLeg_{floor}_{item}_{leg}", (0.07, 0.48, 0.42), (x + leg, y, occupied_z + 0.20), mats["steel"], cfg, "sparse_physical_gallery_bench_leg", role="assembled")
        add_box(objects, f"PAVILION_GalleryPartition_{floor}", (0.10, 3.4, 2.45), (5.1 - floor * 1.8, 1.0, occupied_z + 1.25), mats["gallery_wall"], cfg, "restrained_gallery_partition_depth", role="assembled")
    # Continuous columns bind the modular storeys into one freestanding frame.
    for x in (-12.0, -8.57, -5.14, -1.71, 1.71, 5.14, 8.57, 12.0):
        for y in (-8.34, 8.34):
            add_box(objects, f"PAVILION_ContinuousColumn_{x}_{y}", (0.18, 0.21, 11.15), (x, y, 5.75), mats["steel"], cfg, "continuous_freestanding_black_steel_column")
    # The service core is a genuine solid counterweight to the transparent box.
    add_box(objects, "PAVILION_TravertineServiceCore", (6.3, 7.0, 7.45), (-8.75, -4.65, 3.90), mats["travertine"], cfg, "fixed_pale_travertine_service_core")
    add_box(objects, "PAVILION_CoreDoor", (1.25, 0.12, 2.65), (-8.75, -8.22, 1.76), mats["steel"], cfg, "recessed_service_core_door")
    # Double entry doors and handles are separate physical components.
    for door in (-1.0, 1.0):
        x = door * 1.05
        add_box(objects, f"PAVILION_EntrancePane_{door}", (1.9, 0.10, 2.85), (x, -8.40, 1.84), mats["glass"], cfg, "physical_recessed_pavilion_entry")
        add_box(objects, f"PAVILION_EntranceHandle_{door}", (0.035, 0.12, 0.78), (x - door * 0.25, -8.48, 1.70), mats["steel"], cfg, "steel_entry_pull")
    # Knife-edge roof is only 34 cm thick despite its deep asymmetrical overhang.
    add_box(objects, "PAVILION_RibbedSoffit", (29.0, 22.0, 0.18), (0.65, -0.35, 11.38), mats["soffit"], cfg, "fixed_deep_floating_ribbed_soffit")
    add_box(objects, "PAVILION_KnifeEdgeRoof", (29.2, 22.2, 0.16), (0.65, -0.35, 11.55), mats["roof"], cfg, "exceptionally_thin_cantilevered_roof_plane")
    for x in (-13.95, 15.25):
        add_box(objects, f"PAVILION_RoofEdgeX_{x}", (0.08, 22.2, 0.22), (x, -0.35, 11.48), mats["steel"], cfg, "crisp_black_roof_knife_edge")
    return objects


def add_external_louver_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    facade_y: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    add_box(objects, prefix + "_Occupied", (width - 0.18, 0.08, height - 0.16), (centre_x, facade_y - outward_sign * 0.34, centre_z), mats["interior"], cfg, "occupied_depth_behind_louver", role=role)
    add_box(objects, prefix + "_Glass", (width - 0.14, 0.08, height - 0.12), (centre_x, facade_y - outward_sign * 0.07, centre_z), mats["glass"], cfg, "physical_glazing_behind_louver", role=role)
    louver_y = facade_y + outward_sign * 0.16
    slats = 10
    for index in range(slats):
        z = centre_z - height / 2 + (index + 0.5) * height / slats
        add_box(objects, prefix + f"_LouverBlade_{index}", (width, 0.13, 0.095), (centre_x, louver_y, z), mats["louver"], cfg, "real_external_timber_louver_blade", role=role)
    for x in (centre_x - width / 2, centre_x + width / 2):
        add_box(objects, prefix + f"_LouverJamb_{x}", (0.13, 0.20, height), (x, louver_y, centre_z), mats["timber"], cfg, "timber_louver_frame", role=role)


def add_timber_upper_storey(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    height: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    phase: int = 0,
) -> None:
    add_box(objects, prefix + "_Slab", (width, depth, 0.24), (0.0, 0.0, base_z + 0.12), mats["concrete"], cfg, "complete_upper_floor_plate", role=role)
    add_box(objects, prefix + "_FrontRegisteredUnderlay", (width - 0.4, 0.05, height - 0.3), (0.0, -depth / 2 + 0.42, base_z + height / 2), mats["floor_b_skin"], cfg, "registered_timber_louver_underlay", role=role)
    front_bays = 12
    pitch = width / front_bays
    centre_z = base_z + 0.40 + (height - 0.70) / 2
    panel_height = height - 0.70
    for face, y, sign in (("Front", -depth / 2, -1.0), ("Rear", depth / 2, 1.0)):
        for bay in range(front_bays):
            x = -width / 2 + pitch * (bay + 0.5)
            if (bay + phase) % 3 != 1:
                add_external_louver_y(objects, prefix=f"{prefix}_{face}_Louver_{bay}", centre_x=x, facade_y=y, centre_z=centre_z, width=pitch - 0.72, height=panel_height, outward_sign=sign, mats=mats, cfg=cfg, role=role)
            else:
                _add_window_y_compact(objects, prefix=f"{prefix}_{face}_Window_{bay}", centre_x=x, facade_y=y, centre_z=centre_z, width=pitch - 0.68, height=panel_height, outward_sign=sign, mats=mats, cfg=cfg, role=role, centre_mullion=False)
        for index in range(front_bays + 1):
            x = -width / 2 + pitch * index
            add_box(objects, f"{prefix}_{face}_TimberPier_{index}", (0.52, 0.40, height), (x, y, base_z + height / 2), mats["timber"], cfg, "complete_timber_rainscreen_pier", role=role)
        add_box(objects, f"{prefix}_{face}_Belt", (width + 0.5, 0.52, 0.36), (0.0, y, base_z + height - 0.18), mats["timber"], cfg, "continuous_projecting_timber_belt_course", role=role)
    side_bays = 7
    pitch_y = depth / side_bays
    for face, x, sign in (("Left", -width / 2, -1.0), ("Right", width / 2, 1.0)):
        for bay in range(side_bays):
            y = -depth / 2 + pitch_y * (bay + 0.5)
            _add_window_x_compact(objects, prefix=f"{prefix}_{face}_{bay}", centre_y=y, facade_x=x, centre_z=centre_z, width=pitch_y - 0.78, height=panel_height, outward_sign=sign, mats=mats, cfg=cfg, role=role)
        for index in range(side_bays + 1):
            y = -depth / 2 + pitch_y * index
            add_box(objects, f"{prefix}_{face}_TimberPier_{index}", (0.40, 0.52, height), (x, y, base_z + height / 2), mats["timber"], cfg, "wrapped_timber_rainscreen_pier", role=role)


def add_escalator(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    x: float,
    y0: float,
    z0: float,
    y1: float,
    z1: float,
    mats: dict,
    cfg: dict,
) -> None:
    for side in (-0.75, 0.75):
        add_beam(objects, f"{prefix}_Rail_{side}", (x + side, y0, z0 + 0.65), (x + side, y1, z1 + 0.65), 0.055, mats["steel"], cfg, "visible_transit_escalator_handrail")
    for step in range(13):
        t = step / 12
        y = y0 + (y1 - y0) * t
        z = z0 + (z1 - z0) * t
        add_box(objects, f"{prefix}_Step_{step}", (1.42, 0.42, 0.10), (x, y, z), mats["steel"], cfg, "visible_transit_escalator_step")


def build_transit(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    width, depth = 58.0, 34.0
    add_box(objects, "TRANSIT_ConcretePlinth", (60.0, 36.0, 0.40), (0.0, 0.0, 0.20), mats["concrete"], cfg, "fixed_station_concrete_plinth")
    lower_height = 4.15
    for floor in range(3):
        add_curtain_storey(objects, prefix=f"TRANSIT_ConcourseFloor_{floor}", width=width, depth=depth, base_z=0.35 + floor * lower_height, height=lower_height, front_bays=12, side_bays=7, mats=mats, cfg=cfg, structure_semantic="complete_transit_curtain_wall_bay")
    # Multiple recessed doors and visible internal circulation make the base read as a station.
    for door, x in enumerate((-18.0, -9.0, 0.0, 9.0, 18.0)):
        add_box(objects, f"TRANSIT_EntranceDoor_{door}", (3.1, 0.11, 3.25), (x, -17.20, 2.05), mats["glass"], cfg, "recessed_transit_entrance_door")
        add_box(objects, f"TRANSIT_EntranceHeader_{door}", (3.35, 0.23, 0.16), (x, -17.30, 3.73), mats["steel"], cfg, "graphite_entrance_frame")
    add_escalator(objects, prefix="TRANSIT_EscalatorA", x=-7.5, y0=-8.5, z0=0.65, y1=1.0, z1=4.35, mats=mats, cfg=cfg)
    add_escalator(objects, prefix="TRANSIT_EscalatorB", x=7.5, y0=-2.0, z0=4.55, y1=7.5, z1=8.45, mats=mats, cfg=cfg)
    # Broad entrance canopy is tied back to the first concourse datum.
    add_box(objects, "TRANSIT_EntranceCanopyGlass", (61.0, 5.8, 0.18), (0.0, -19.5, 4.65), mats["glass"], cfg, "integral_broad_glass_station_canopy")
    add_beam(objects, "TRANSIT_CanopyBuildingHeader", (-30.5, -16.7, 4.63), (30.5, -16.7, 4.63), 0.14, mats["steel"], cfg, "integral_canopy_building_header")
    add_beam(objects, "TRANSIT_CanopyStreetHeader", (-30.5, -22.4, 4.63), (30.5, -22.4, 4.63), 0.14, mats["steel"], cfg, "integral_canopy_street_header")
    for x in range(-30, 31, 5):
        add_beam(objects, f"TRANSIT_CanopyRafter_{x}", (x, -16.8, 4.62), (x, -22.4, 4.62), 0.09, mats["steel"], cfg, "integral_canopy_steel_rafter")
    for x in (-27.0, -18.0, -9.0, 0.0, 9.0, 18.0, 27.0):
        add_cylinder(objects, f"TRANSIT_CanopyColumn_{x}", 0.12, 4.55, (x, -21.4, 2.28), mats["steel"], cfg, "integral_canopy_column", vertices=10)
    z = 0.35 + 3 * lower_height
    for floor in range(3):
        add_timber_upper_storey(objects, prefix=f"TRANSIT_TimberFloor_{floor}", width=56.0, depth=32.0, base_z=z, height=3.65, mats=mats, cfg=cfg, phase=floor)
        z += 3.65
    add_box(objects, "TRANSIT_RoofSlab", (58.0, 34.0, 0.38), (0.0, 0.0, z + 0.19), mats["concrete"], cfg, "complete_green_roof_structural_slab")
    add_box(objects, "TRANSIT_ExtensiveGreenRoof", (56.5, 32.5, 0.34), (0.0, 0.0, z + 0.55), mats["green_roof"], cfg, "fixed_extensive_planted_station_roof")
    add_box(objects, "TRANSIT_ScreenedRoofPlant", (8.0, 6.5, 2.0), (0.0, 0.0, z + 1.62), mats["steel"], cfg, "screened_rooftop_service_zone")
    for row, y in enumerate((-8.0, 8.0)):
        for post in (-24.0, -12.0, 0.0, 12.0, 24.0):
            add_cylinder(objects, f"TRANSIT_PVPost_{row}_{post}", 0.09, 2.0, (post, y, z + 1.55), mats["steel"], cfg, "photovoltaic_canopy_support", vertices=8)
        for panel in range(10):
            x = -25.2 + panel * 5.6
            pv = add_box(objects, f"TRANSIT_PVCanopy_{row}_{panel}", (5.2, 3.0, 0.11), (x, y, z + 2.58), mats["pv"], cfg, "two_long_photovoltaic_canopy_rows")
            pv.rotation_euler[0] = math.radians(5.0 if row == 0 else -5.0)
    for shrub, (x, y, scale) in enumerate(((-21.0, -1.0, 0.8), (-13.0, 4.5, 0.6), (15.0, -3.0, 0.7), (23.0, 4.0, 0.65))):
        add_sphere(objects, f"TRANSIT_RoofShrub_{shrub}", scale, (x, y, z + 1.0), mats["green_roof"], cfg, "restrained_integral_roof_planting", scale=(1.4, 1.0, 0.65))
    return objects


def add_passive_window_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    facade_y: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str,
    phase: int,
) -> None:
    """Recess split triple panes behind a complete insulated reveal."""
    pane_y = facade_y - outward_sign * 0.34
    frame_y = pane_y + outward_sign * 0.018
    interior_y = facade_y - outward_sign * 1.52
    reveal_mid_y = (facade_y + pane_y) / 2
    reveal_depth = abs(pane_y - facade_y) + 0.05
    # A deep warm room backing prevents the clear panes from looking empty.
    # Only a minority of bays carry an authored occupied-room card; otherwise
    # the facade would repeat the same photograph behind every window.
    add_box(objects, prefix + "_RoomShadow", (width - 0.30, 0.055, height - 0.34), (centre_x, interior_y, centre_z), mats["room_shadow"], cfg, "deep_warm_passive_room_shadow", role=role)
    if phase % 6 in {0, 5}:
        occupied = mats["interior_evening"] if phase % 5 in {1, 4} else mats["interior"]
        add_box(objects, prefix + "_SelectiveOccupiedDepth", (width - 0.88, 0.060, height - 0.70), (centre_x, interior_y - outward_sign * 0.025, centre_z), occupied, cfg, "selective_day_or_evening_passive_room_depth", role=role)
    elif phase % 4 == 2:
        curtain_width = max(0.28, (width - 0.55) * 0.22)
        for side in (-1.0, 1.0):
            curtain_x = centre_x + side * (width / 2 - curtain_width / 2 - 0.18)
            add_box(objects, prefix + f"_LinenCurtain_{side}", (curtain_width, 0.065, height - 0.42), (curtain_x, interior_y - outward_sign * 0.035, centre_z), mats["curtain"], cfg, "physical_natural_linen_room_depth", role=role)
    pane_width = (width - 0.17) / 2
    for pane, offset in (("Left", -pane_width / 2 - 0.025), ("Right", pane_width / 2 + 0.025)):
        add_box(objects, prefix + f"_{pane}TriplePane", (pane_width, 0.06, height - 0.13), (centre_x + offset, pane_y, centre_z), mats["glass"], cfg, "physical_split_high_performance_triple_pane", role=role)
    for edge, x in (("Left", centre_x - width / 2), ("Right", centre_x + width / 2)):
        add_box(objects, prefix + f"_{edge}InsulatedJamb", (0.15, reveal_depth, height), (x, reveal_mid_y, centre_z), mats["larch"], cfg, "deep_larch_insulated_window_return", role=role)
    for edge, z in (("Sill", centre_z - height / 2), ("Head", centre_z + height / 2)):
        add_box(objects, prefix + f"_{edge}InsulatedReturn", (width, reveal_depth, 0.15), (centre_x, reveal_mid_y, z), mats["larch"], cfg, "deep_larch_insulated_window_return", role=role)
    for x in (centre_x - width / 2 + 0.055, centre_x + width / 2 - 0.055):
        add_box(objects, prefix + f"_FrameJamb_{x:.2f}", (0.065, 0.11, height - 0.08), (x, frame_y, centre_z), mats["frame"], cfg, "slim_timber_aluminum_triple_glazing_frame", role=role)
    for z in (centre_z - height / 2 + 0.055, centre_z + height / 2 - 0.055):
        add_box(objects, prefix + f"_FrameRail_{z:.2f}", (width - 0.08, 0.11, 0.065), (centre_x, frame_y, z), mats["frame"], cfg, "slim_timber_aluminum_triple_glazing_frame", role=role)
    add_box(objects, prefix + "_CentralMullion", (0.055, 0.10, height - 0.10), (centre_x, frame_y, centre_z), mats["frame"], cfg, "slim_timber_aluminum_triple_glazing_mullion", role=role)


def add_passive_blind_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    y: float,
    centre_z: float,
    width: float,
    height: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    add_box(objects, f"{prefix}_BlindHeadbox", (width + 0.10, 0.15, 0.18), (centre_x, y, centre_z + height / 2 + 0.09), mats["blind"], cfg, "integrated_external_blind_headbox", role=role)
    for slat in range(11):
        z = centre_z - height / 2 + (slat + 0.5) * height / 11
        blade = add_box(objects, f"{prefix}_BlindBlade_{slat}", (width, 0.11, 0.075), (centre_x, y, z), mats["blind"], cfg, "real_external_venetian_blind_blade", role=role)
        blade.rotation_euler[0] = math.radians(-12.0)
    for side in (-1.0, 1.0):
        add_cylinder(objects, f"{prefix}_BlindGuide_{side}", 0.012, height + 0.12, (centre_x + side * (width / 2 - 0.05), y - 0.025, centre_z), mats["blind"], cfg, "slim_external_blind_guide_cable", vertices=6, role=role)


def add_passive_storey(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    base_z: float,
    height: float,
    floor_index: int,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    width, depth, bays = 36.0, 20.0, 6
    pitch = width / bays
    add_box(objects, prefix + "_FloorPlate", (width, depth, 0.20), (0.0, 0.0, base_z + 0.10), mats["zinc"], cfg, "airtight_passive_floor_edge", role=role)
    add_box(objects, prefix + "_FrontRegisteredUnderlay", (width - 0.5, 0.05, height - 0.25), (0.0, -depth / 2 + 1.72, base_z + height / 2), mats["floor_a_skin"] if floor_index % 2 == 0 else mats["floor_b_skin"], cfg, "registered_passive_bay_underlay_behind_room_depth", role=role)
    centre_z = base_z + 0.40 + (height - 0.74) / 2
    window_height = height - 0.74
    for face, y, sign in (("Front", -depth / 2, -1.0), ("Rear", depth / 2, 1.0)):
        for bay in range(bays):
            cx = -width / 2 + pitch * (bay + 0.5)
            if floor_index == 0 and face == "Front" and bay in (2, 3):
                continue
            add_passive_window_y(objects, prefix=f"{prefix}_{face}_Window_{bay}", centre_x=cx, facade_y=y, centre_z=centre_z, width=4.25 if face == "Front" else 3.10, height=window_height, outward_sign=sign, mats=mats, cfg=cfg, role=role, phase=floor_index * bays + bay + (0 if face == "Front" else 2))
            if face == "Front" and floor_index in (1, 2) and bay in (0, 1, 3, 4):
                add_passive_blind_y(objects, prefix=f"{prefix}_{face}_{bay}", centre_x=cx, y=y - sign * 0.12, centre_z=centre_z, width=4.05, height=window_height * (0.48 if (floor_index + bay) % 2 else 0.62), mats=mats, cfg=cfg, role=role)
            if face == "Front" and floor_index == 3 and bay in (0, 2, 3, 5):
                add_box(objects, f"{prefix}_{face}_InsulatedPanel_{bay}", (4.05, 0.08, 0.72), (cx, y - sign * 0.30, centre_z - 0.49), mats["panel"], cfg, "pale_translucent_insulated_balcony_panel", role=role)
        add_box(objects, f"{prefix}_{face}_LarchSpandrel", (width, 0.48, 0.54), (0.0, y, base_z + 0.37), mats["larch"], cfg, "continuous_vertical_larch_spandrel", role=role)
        for index in range(bays + 1):
            x = -width / 2 + pitch * index
            add_box(objects, f"{prefix}_{face}_DeepLarchPier_{index}", (0.88, 0.58, height), (x, y, base_z + height / 2), mats["larch"], cfg, "deep_insulated_larch_window_reveal", role=role)
            for offset in (-0.28, 0.0, 0.28):
                add_box(objects, f"{prefix}_{face}_PierBoardJoint_{index}_{offset}", (0.018, 0.625, height - 0.18), (x + offset, y + sign * 0.025, base_z + height / 2), mats["frame"], cfg, "fine_vertical_larch_pier_board_joint", role=role)
        for bay in range(bays):
            cx = -width / 2 + pitch * (bay + 0.5)
            for offset in (-1.65, 0.0, 1.65):
                add_box(objects, f"{prefix}_{face}_SpandrelBoardJoint_{bay}_{offset}", (0.016, 0.585, 0.46), (cx + offset, y + sign * 0.025, base_z + 0.37), mats["frame"], cfg, "fine_vertical_larch_spandrel_board_joint", role=role)
    # Solid gable-end construction has smaller punched windows.
    for face, x, sign in (("Left", -width / 2, -1.0), ("Right", width / 2, 1.0)):
        add_box(objects, f"{prefix}_{face}_LarchWall", (0.46, depth, height), (x, 0.0, base_z + height / 2), mats["larch"], cfg, "complete_vertical_larch_gable_end", role=role)
        for y in (-4.8, 4.8):
            _add_window_x_compact(objects, prefix=f"{prefix}_{face}_Window_{y}", centre_y=y, facade_x=x + sign * 0.05, centre_z=centre_z, width=1.65, height=1.75, outward_sign=sign, mats=mats, cfg=cfg, role=role)


def slope_point(
    *,
    centre_y: float,
    centre_z: float,
    local_y: float,
    angle: float,
    lift: float,
) -> tuple[float, float]:
    return (
        centre_y + local_y * math.cos(angle) - lift * math.sin(angle),
        centre_z + local_y * math.sin(angle) + lift * math.cos(angle),
    )


def add_slope_pv_module(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    local_y: float,
    width: float,
    depth: float,
    roof_centre_y: float,
    roof_centre_z: float,
    angle: float,
    mats: dict,
    cfg: dict,
    role: str,
) -> None:
    lift = 0.19
    y, z = slope_point(centre_y=roof_centre_y, centre_z=roof_centre_z, local_y=local_y, angle=angle, lift=lift)
    panel = add_box(objects, prefix + "_CellLaminate", (width, depth, 0.065), (centre_x, y, z), mats["pv"], cfg, "individual_6_by_10_cell_photovoltaic_module", role=role)
    panel.rotation_euler[0] = angle
    for edge, offset in (("Low", -depth / 2), ("High", depth / 2)):
        rail_y, rail_z = slope_point(centre_y=roof_centre_y, centre_z=roof_centre_z, local_y=local_y + offset, angle=angle, lift=lift + 0.025)
        rail = add_box(objects, prefix + f"_{edge}Frame", (width + 0.045, 0.040, 0.082), (centre_x, rail_y, rail_z), mats["pv_frame"], cfg, "dark_anodized_photovoltaic_module_frame", role=role)
        rail.rotation_euler[0] = angle
    for edge, offset in (("Left", -width / 2), ("Right", width / 2)):
        rail = add_box(objects, prefix + f"_{edge}Frame", (0.040, depth + 0.045, 0.082), (centre_x + offset, y, z), mats["pv_frame"], cfg, "dark_anodized_photovoltaic_module_frame", role=role)
        rail.rotation_euler[0] = angle


def add_vertical_pv_module_x(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    facade_x: float,
    centre_y: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
) -> None:
    panel_x = facade_x + outward_sign * 0.04
    add_box(objects, prefix + "_CellLaminate", (0.065, width, height), (panel_x, centre_y, centre_z), mats["pv"], cfg, "vertical_6_by_10_cell_photovoltaic_module")
    frame_x = panel_x + outward_sign * 0.035
    for edge, y in (("Left", centre_y - width / 2), ("Right", centre_y + width / 2)):
        add_box(objects, prefix + f"_{edge}Frame", (0.085, 0.045, height + 0.045), (frame_x, y, centre_z), mats["pv_frame"], cfg, "dark_anodized_photovoltaic_module_frame")
    for edge, z in (("Low", centre_z - height / 2), ("High", centre_z + height / 2)):
        add_box(objects, prefix + f"_{edge}Frame", (0.085, width + 0.045, 0.045), (frame_x, centre_y, z), mats["pv_frame"], cfg, "dark_anodized_photovoltaic_module_frame")


def add_passive_roof(
    objects: list[bpy.types.Object],
    *,
    base_z: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    width = 37.2
    front_depth = math.hypot(12.5, 4.4)
    rear_depth = math.hypot(8.5, 4.4)
    front_angle = math.atan2(4.4, 12.5)
    rear_angle = -math.atan2(4.4, 8.5)
    front = add_box(objects, "PASSIVE_FrontRoofStructure", (width, front_depth, 0.24), (0.0, -4.25, base_z + 2.2), mats["zinc"], cfg, "asymmetric_sun_facing_roof_plane", role=role)
    front.rotation_euler[0] = front_angle
    rear = add_box(objects, "PASSIVE_RearGreenRoofStructure", (width, rear_depth, 0.24), (0.0, 6.25, base_z + 2.2), mats["green_roof"], cfg, "asymmetric_sedum_roof_plane", role=role)
    rear.rotation_euler[0] = rear_angle
    # The upper roof field is a real racked array: each module retains one
    # complete cell texture, perimeter frame and visible inter-module gap.
    field_width = 35.6
    columns = 30
    rows = 3
    column_gap = 0.075
    row_gap = 0.11
    panel_width = (field_width - column_gap * (columns - 1)) / columns
    panel_depth = (5.45 - row_gap * (rows - 1)) / rows
    for row in range(rows):
        local_y = 0.58 + panel_depth / 2 + row * (panel_depth + row_gap)
        for column in range(columns):
            x = -field_width / 2 + panel_width / 2 + column * (panel_width + column_gap)
            add_slope_pv_module(objects, prefix=f"PASSIVE_RoofPVModule_{row}_{column}", centre_x=x, local_y=local_y, width=panel_width, depth=panel_depth, roof_centre_y=-4.25, roof_centre_z=base_z + 2.2, angle=front_angle, mats=mats, cfg=cfg, role=role)
        rail_y, rail_z = slope_point(centre_y=-4.25, centre_z=base_z + 2.2, local_y=local_y, angle=front_angle, lift=0.125)
        support = add_box(objects, f"PASSIVE_PVContinuousMountingRail_{row}", (field_width + 0.12, 0.075, 0.075), (0.0, rail_y, rail_z), mats["pv_frame"], cfg, "continuous_photovoltaic_mounting_rail", role=role)
        support.rotation_euler[0] = front_angle
    front_sedum = add_box(objects, "PASSIVE_PublicSedumRoofBand", (35.8, front_depth * 0.54, 0.12), (0.0, -7.12, base_z + 1.37), mats["green_roof"], cfg, "continuous_public_sedum_roof_band", role=role)
    front_sedum.rotation_euler[0] = front_angle
    # Rooflights interrupt the public sedum field as real proud glazed units.
    for index, x in enumerate((-4.2, 0.0, 4.2)):
        light = add_box(objects, f"PASSIVE_SedumRooflight_{index}", (1.55, 2.10, 0.15), (x, -6.55, base_z + 1.52), mats["glass"], cfg, "three_physical_sedum_rooflights", role=role)
        light.rotation_euler[0] = front_angle
        for edge, local_y in (("Low", -1.08), ("High", 1.08)):
            rail = add_box(objects, f"PASSIVE_RooflightFrame_{index}_{edge}", (1.72, 0.10, 0.08), (x, -6.55 + local_y * math.cos(front_angle), base_z + 1.61 + local_y * math.sin(front_angle)), mats["zinc"], cfg, "zinc_rooflight_frame", role=role)
            rail.rotation_euler[0] = front_angle
        for edge, local_x in (("Left", -0.81), ("Right", 0.81)):
            rail = add_box(objects, f"PASSIVE_RooflightFrame_{index}_{edge}", (0.10, 2.25, 0.08), (x + local_x, -6.55, base_z + 1.61), mats["zinc"], cfg, "zinc_rooflight_frame", role=role)
            rail.rotation_euler[0] = front_angle
    add_beam(objects, "PASSIVE_RidgeCap", (-width / 2, 2.0, base_z + 4.52), (width / 2, 2.0, base_z + 4.52), 0.13, mats["zinc"], cfg, "continuous_zinc_ridge_cap", role=role)
    for y, z in ((-10.5, base_z + 0.02), (10.5, base_z + 0.02)):
        add_beam(objects, f"PASSIVE_Gutter_{y}", (-width / 2, y, z), (width / 2, y, z), 0.11, mats["zinc"], cfg, "continuous_zinc_gutter", role=role)
    # Close both gable triangles with the same real larch envelope.
    for x in (-18.05, 18.05):
        vertices = [(x, -10.0, base_z), (x, 10.0, base_z), (x, 2.0, base_z + 4.4)]
        create_mesh_object(objects, f"PASSIVE_LarchGable_{x}", vertices, [(0, 1, 2)], mats["larch_plain"], cfg, "complete_larch_clad_gable_triangle", role=role)


def build_passive(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "PASSIVE_InsulatedPlinth", (36.8, 20.6, 0.40), (0.0, 0.0, 0.20), mats["zinc"], cfg, "fixed_thermally_broken_plinth")
    z = 0.35
    for floor in range(4):
        add_passive_storey(objects, prefix=f"PASSIVE_Floor_{floor}", base_z=z, height=3.20, floor_index=floor, mats=mats, cfg=cfg)
        z += 3.20
    # Deep central entry is set behind the surrounding larch piers.
    add_box(objects, "PASSIVE_CentralEntryRecess", (5.4, 1.3, 2.75), (0.0, -9.30, 1.77), mats["interior"], cfg, "deeply_recessed_central_timber_entry")
    for door in (-1.0, 1.0):
        add_box(objects, f"PASSIVE_CentralEntryDoor_{door}", (1.85, 0.12, 2.45), (door * 0.98, -9.62, 1.66), mats["larch"], cfg, "insulated_timber_entry_door")
    add_box(objects, "PASSIVE_CentralEntryCanopy", (6.4, 1.6, 0.20), (0.0, -10.65, 3.12), mats["zinc"], cfg, "integral_entry_rain_canopy")
    # Fine full-height board joints keep large side walls from reading as panels.
    for x, sign in ((-18.24, -1.0), (18.24, 1.0)):
        for joint in range(37):
            y = -9.75 + joint * 19.5 / 36
            add_box(objects, f"PASSIVE_SideBoardJoint_{x}_{joint}", (0.055, 0.035, 12.65), (x + sign * 0.02, y, 6.68), mats["frame"], cfg, "fine_vertical_larch_rainscreen_joint")
    # Side-wall PV bank is separate from the roof array.
    for row, zc in enumerate((6.2, 9.25)):
        for column, y in enumerate((3.8, 7.0)):
            add_vertical_pv_module_x(objects, prefix=f"PASSIVE_GablePV_{row}_{column}", facade_x=18.28, centre_y=y, centre_z=zc, width=2.75, height=2.55, outward_sign=1.0, mats=mats, cfg=cfg)
    for x in (-17.7, 17.7):
        add_cylinder(objects, f"PASSIVE_Downpipe_{x}", 0.07, 12.5, (x, -10.35, 6.45), mats["zinc"], cfg, "zinc_rainwater_downpipe", vertices=10)
    add_passive_roof(objects, base_z=z, mats=mats, cfg=cfg)
    return objects


def build_assembled(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    family = cfg["family"]
    if family == "art-deco-cream-terracotta-tower":
        return build_art_deco(mats, cfg)
    if family == "restored-kyoto-machiya":
        return build_machiya(mats, cfg)
    if family == "mid-century-glass-steel-pavilion":
        return build_pavilion(mats, cfg)
    if family == "timber-glass-transit-station-block":
        return build_transit(mats, cfg)
    return build_passive(mats, cfg)


def build_module(
    role: str,
    variant: str,
    mats: dict,
    cfg: dict,
) -> tuple[list[bpy.types.Object], float]:
    objects: list[bpy.types.Object] = []
    family = cfg["family"]
    if family != "art-deco-cream-terracotta-tower":
        if family == "restored-kyoto-machiya":
            if role == "podium":
                height = 3.35
                add_box(objects, "MACHIYA_MODULE_StoneSill", (18.6, 14.6, 0.28), (0.0, 0.0, 0.14), mats["stone"], cfg, "fixed_machiya_stone_podium", role=role)
                for bay in range(6):
                    cx = -7.5 + bay * 3.0
                    if bay not in (1, 2):
                        add_koshi_panel_y(objects, prefix=f"MACHIYA_MODULE_Ground_{bay}", centre_x=cx, facade_y=-7.05, base_z=0.45, width=2.65, height=2.35, outward_sign=-1.0, mats=mats, cfg=cfg, role=role, slat_pitch=0.23)
                for x in (-9.0, -6.0, -3.0, 0.0, 3.0, 6.0, 9.0):
                    add_box(objects, f"MACHIYA_MODULE_GroundPost_{x}", (0.22, 0.32, height), (x, -7.05, height / 2), mats["timber"], cfg, "complete_ground_post_and_beam_bay", role=role)
            elif role == "floor":
                height = 3.35
                for bay in range(6):
                    add_koshi_panel_y(objects, prefix=f"MACHIYA_MODULE_{variant}_{bay}", centre_x=-7.5 + bay * 3.0, facade_y=-7.05, base_z=0.40, width=2.70, height=2.55, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
                add_box(objects, "MACHIYA_MODULE_UpperBeam", (18.2, 0.34, 0.24), (0.0, -7.08, 3.15), mats["timber"], cfg, "complete_upper_koshi_bay_row", role=role)
            elif role == "crown":
                height = 0.85
                add_box(objects, "MACHIYA_MODULE_CrownBeam", (18.6, 14.4, 0.34), (0.0, 0.0, 0.17), mats["timber"], cfg, "fixed_deep_eave_crown_beam", role=role)
                for y in (-7.2, 7.2):
                    add_beam(objects, f"MACHIYA_MODULE_Gutter_{y}", (-9.4, y, 0.55), (9.4, y, 0.55), 0.10, mats["tile"], cfg, "fixed_kawara_eave_gutter", role=role)
            else:
                height = 4.70
                add_machiya_gable_roof(objects, base_z=0.10, mats=mats, cfg=cfg, role=role, compact=True)
        elif family == "mid-century-glass-steel-pavilion":
            if role == "podium":
                height = 3.65
                add_box(objects, "PAVILION_MODULE_Plinth", (25.0, 17.4, 0.42), (0.0, 0.0, 0.21), mats["travertine"], cfg, "fixed_travertine_pavilion_podium", role=role)
                add_curtain_storey(objects, prefix="PAVILION_MODULE_Ground", width=24.0, depth=16.5, base_z=0.35, height=3.30, front_bays=7, side_bays=5, mats=mats, cfg=cfg, role=role)
            elif role == "floor":
                height = 3.65
                add_curtain_storey(objects, prefix=f"PAVILION_MODULE_{variant}", width=24.0, depth=16.5, base_z=0.0, height=height, front_bays=7, side_bays=5, mats=mats, cfg=cfg, role=role)
            elif role == "crown":
                height = 0.28
                add_box(objects, "PAVILION_MODULE_CrownSoffit", (29.0, 22.0, height), (0.0, 0.0, height / 2), mats["soffit"], cfg, "fixed_floating_roof_soffit", role=role)
            else:
                height = 0.34
                add_box(objects, "PAVILION_MODULE_KnifeEdgeRoof", (29.2, 22.2, height), (0.0, 0.0, height / 2), mats["roof"], cfg, "fixed_knife_edge_roof_plane", role=role)
        elif family == "timber-glass-transit-station-block":
            if role == "podium":
                height = 4.35
                add_box(objects, "TRANSIT_MODULE_Plinth", (60.0, 36.0, 0.35), (0.0, 0.0, 0.175), mats["concrete"], cfg, "fixed_station_concourse_podium", role=role)
                add_curtain_storey(objects, prefix="TRANSIT_MODULE_Ground", width=58.0, depth=34.0, base_z=0.30, height=4.05, front_bays=12, side_bays=7, mats=mats, cfg=cfg, role=role, structure_semantic="complete_transit_curtain_wall_bay")
            elif role == "floor":
                if variant == "typical_a":
                    height = 4.05
                    add_curtain_storey(objects, prefix="TRANSIT_MODULE_Glazed", width=58.0, depth=34.0, base_z=0.0, height=height, front_bays=12, side_bays=7, mats=mats, cfg=cfg, role=role, structure_semantic="repeatable_complete_transit_glazed_bay")
                else:
                    height = 3.65
                    add_timber_upper_storey(objects, prefix=f"TRANSIT_MODULE_{variant}", width=56.0, depth=32.0, base_z=0.0, height=height, mats=mats, cfg=cfg, role=role, phase=1 if variant == "typical_b" else 2)
            elif role == "crown":
                height = 1.15
                add_box(objects, "TRANSIT_MODULE_RoofSlab", (58.0, 34.0, 0.38), (0.0, 0.0, 0.19), mats["concrete"], cfg, "fixed_green_roof_crown_slab", role=role)
                add_box(objects, "TRANSIT_MODULE_GreenRoof", (56.5, 32.5, 0.34), (0.0, 0.0, 0.55), mats["green_roof"], cfg, "fixed_extensive_green_roof", role=role)
            else:
                height = 3.0
                for row, y in enumerate((-8.0, 8.0)):
                    for post in (-24.0, -12.0, 0.0, 12.0, 24.0):
                        add_cylinder(objects, f"TRANSIT_MODULE_PVPost_{row}_{post}", 0.09, 2.0, (post, y, 1.0), mats["steel"], cfg, "fixed_pv_canopy_support", vertices=8, role=role)
                    for panel in range(10):
                        add_box(objects, f"TRANSIT_MODULE_PV_{row}_{panel}", (5.2, 3.0, 0.11), (-25.2 + panel * 5.6, y, 2.10), mats["pv"], cfg, "fixed_twin_pv_canopy_rows", role=role)
        else:
            if role == "podium":
                height = 3.25
                add_box(objects, "PASSIVE_MODULE_Plinth", (36.8, 20.6, 0.38), (0.0, 0.0, 0.19), mats["zinc"], cfg, "fixed_thermally_broken_podium", role=role)
                add_passive_storey(objects, prefix="PASSIVE_MODULE_Ground", base_z=0.30, height=2.95, floor_index=0, mats=mats, cfg=cfg, role=role)
            elif role == "floor":
                height = 3.25
                floor_index = {"typical_a": 1, "typical_b": 2, "typical_c": 3}[variant]
                add_passive_storey(objects, prefix=f"PASSIVE_MODULE_{variant}", base_z=0.0, height=height, floor_index=floor_index, mats=mats, cfg=cfg, role=role)
            elif role == "crown":
                height = 0.45
                add_box(objects, "PASSIVE_MODULE_CrownEdge", (36.8, 20.5, height), (0.0, 0.0, height / 2), mats["larch"], cfg, "fixed_larch_roof_crown", role=role)
            else:
                height = 4.65
                add_passive_roof(objects, base_z=0.05, mats=mats, cfg=cfg, role=role)
        for marker in module_contract_markers(role, variant, height):
            objects.append(tag_object(marker, "four_elevation_material_contract", cfg, role=role))
        return objects, height
    if role == "podium":
        height = cfg["podium_height"]
        add_deco_podium(objects, base_z=0.0, mats=mats, cfg=cfg, role=role, module=True)
    elif role == "floor":
        height = cfg["floor_height"]
        add_deco_storey(objects, prefix=f"DECO_MODULE_{variant}", width=30.0, depth=26.0, base_z=0.0, height=height, front_bays=7, side_bays=6, mats=mats, cfg=cfg, variant=variant, role=role)
    elif role == "crown":
        height = 3.0
        for index, (width, depth, step_height, mat) in enumerate(((16.8, 16.8, 0.7, mats["terracotta"]), (13.8, 13.8, 1.0, mats["terracotta"]), (10.8, 10.8, 1.3, mats["gold"]))):
            z = sum((0.7, 1.0, 1.3)[:index]) + step_height / 2
            add_box(objects, f"DECO_MODULE_CrownStep_{index}", (width, depth, step_height), (0.0, 0.0, z), mat, cfg, "fixed_stepped_crown_plinth", role=role)
    else:
        height = 11.65
        add_deco_crown(objects, base_z=-3.0, mats=mats, cfg=cfg, role=role, include_roof=True)
        # Remove crown plinths: this module starts at lantern sill.
        plinths = [obj for obj in objects if "CrownStep" in obj.name]
        delete_objects(plinths)
        objects = [obj for obj in objects if obj not in plinths]
    for marker in module_contract_markers(role, variant, height):
        objects.append(tag_object(marker, "four_elevation_material_contract", cfg, role=role))
    return objects, height


def module_payload(
    role: str,
    variant: str,
    filename: str,
    objects: list[bpy.types.Object],
    size_bytes: int,
    skin: dict,
    cfg: dict,
) -> dict:
    repeatable = role == "floor"
    width, depth, actual_height = bounds_dimensions(objects)
    return {
        "role": role,
        "variant_key": variant,
        "assembly_class": "repeatable_middle" if repeatable else "fixed_semantic",
        "fixed_semantic": not repeatable,
        "lod": 0,
        "allowed_levels": [0, 1, 2],
        "filename": filename,
        "module_family": cfg["family"],
        "width_m": width,
        "depth_m": depth,
        "height_m": actual_height,
        "floor_height_m": cfg["floor_height"],
        "repeatable_z": repeatable,
        "allow_inset_footprint": True,
        "triangle_count": evaluated_triangle_count(objects),
        "material_count": material_count(objects),
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
        "size_bytes": size_bytes,
    }


def build_modules(
    folder: Path,
    mats: dict[str, bpy.types.Material],
    skin: dict,
    cfg: dict,
) -> list[dict]:
    specs = (
        ("podium", "default"),
        ("floor", "typical_a"),
        ("floor", "typical_b"),
        ("floor", "typical_c"),
        ("crown", "crown"),
        ("roof", "default"),
    )
    payloads: list[dict] = []
    for role, variant in specs:
        objects, _height = build_module(role, variant, mats, cfg)
        normalize_bottom_centre(objects)
        suffix = role if variant == "default" else f"{role}_{variant}"
        filename = f"{cfg['family']}_{suffix}.glb"
        destination = folder / filename
        export_glb(destination, objects)
        payloads.append(module_payload(role, variant, filename, objects, destination.stat().st_size, skin, cfg))
        delete_objects(objects)
    return payloads


def configure_render(cfg: dict) -> list[bpy.types.Object]:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 980
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.18
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.62, 0.69, 0.74, 1.0)
    background.inputs["Strength"].default_value = 0.72
    presentation: list[bpy.types.Object] = []
    ground_mat = material("MAT_W13_PresentationGround", (0.39, 0.40, 0.39, 1.0), 0.92)
    from generate_wave3_landmark_families import box

    presentation.append(box("PRESENTATION_W13_Ground", (250.0, 250.0, 0.10), (0.0, 0.0, -0.10), ground_mat))
    bpy.ops.object.light_add(type="SUN", location=(-70.0, -100.0, 130.0), rotation=(math.radians(27), math.radians(-18), math.radians(-36)))
    sun = bpy.context.object
    sun.name = "PRESENTATION_W13_Sun"
    sun.data.color = (1.0, 0.90, 0.78)
    sun.data.energy = 1.75
    sun.data.angle = math.radians(9.0)
    presentation.append(sun)
    target_z = cfg["native"][2] * 0.40
    for name, location, energy, size, color in (
        ("Key", (-72.0, -88.0, 92.0), 5400, 20.0, (1.0, 0.84, 0.70)),
        ("Fill", (78.0, -24.0, 62.0), 3700, 19.0, (0.70, 0.83, 1.0)),
        ("Rim", (-4.0, 84.0, 80.0), 4500, 18.0, (0.78, 0.90, 1.0)),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"PRESENTATION_W13_{name}"
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        light.rotation_euler = (Vector((0.0, 0.0, target_z)) - light.location).to_track_quat("-Z", "Y").to_euler()
        presentation.append(light)
    return presentation


def view_map(cfg: dict) -> dict[str, tuple[tuple[float, float, float], tuple[float, float, float], float]]:
    family = cfg["family"]
    if family == "restored-kyoto-machiya":
        return {
            "preview": ((31.0, -43.0, 22.0), (0.0, 0.0, 4.6), 55),
            "front_corner_oblique": ((28.0, -39.0, 14.5), (0.0, -0.5, 4.3), 58),
            "front_elevation": ((0.0, -49.0, 6.0), (0.0, -0.5, 5.1), 62),
            "rear_corner_oblique": ((-29.0, 34.0, 17.0), (0.0, 0.0, 4.3), 58),
            "aerial": ((31.0, -29.0, 34.0), (0.0, 0.0, 3.7), 55),
            "facade_close": ((12.0, -20.0, 5.2), (2.0, -6.0, 4.3), 70),
            "identity_close": ((-4.0, -18.0, 5.0), (-2.0, -6.5, 3.1), 72),
            "street": ((25.0, -48.0, 4.2), (0.0, -1.0, 4.6), 65),
            "context": ((42.0, -55.0, 27.0), (0.0, 0.0, 3.7), 52),
        }
    if family == "mid-century-glass-steel-pavilion":
        return {
            "preview": ((38.0, -50.0, 25.0), (0.0, 0.0, 5.2), 55),
            "front_corner_oblique": ((35.0, -46.0, 18.0), (0.0, 0.0, 5.0), 58),
            "front_elevation": ((0.0, -58.0, 7.0), (0.0, 0.0, 5.7), 61),
            "rear_corner_oblique": ((-35.0, 42.0, 20.0), (0.0, 0.0, 5.0), 58),
            "aerial": ((39.0, -36.0, 39.0), (0.0, 0.0, 4.0), 55),
            "facade_close": ((17.0, -27.0, 8.0), (5.0, -7.0, 6.0), 72),
            "identity_close": ((-20.0, -29.0, 8.5), (-7.0, -4.0, 5.0), 70),
            "street": ((32.0, -57.0, 5.2), (0.0, 0.0, 5.4), 64),
            "context": ((55.0, -67.0, 34.0), (0.0, 0.0, 4.5), 52),
        }
    if family == "timber-glass-transit-station-block":
        return {
            "preview": ((86.0, -108.0, 57.0), (0.0, 0.0, 12.0), 56),
            "front_corner_oblique": ((78.0, -100.0, 42.0), (0.0, -1.0, 11.5), 59),
            "front_elevation": ((0.0, -125.0, 17.0), (0.0, -2.0, 12.0), 62),
            "rear_corner_oblique": ((-81.0, 94.0, 46.0), (0.0, 1.0, 11.0), 58),
            "aerial": ((87.0, -83.0, 92.0), (0.0, 0.0, 8.0), 55),
            "facade_close": ((37.0, -57.0, 14.0), (13.0, -15.0, 10.0), 72),
            "identity_close": ((45.0, -53.0, 26.0), (14.0, -10.0, 22.0), 72),
            "street": ((71.0, -120.0, 8.0), (0.0, -2.0, 11.0), 64),
            "context": ((118.0, -139.0, 74.0), (0.0, 0.0, 8.0), 52),
        }
    if family == "passive-house-timber-block":
        return {
            "preview": ((50.0, -66.0, 34.0), (0.0, 0.0, 7.0), 55),
            "front_corner_oblique": ((45.0, -60.0, 25.0), (0.0, 0.0, 7.0), 58),
            "front_elevation": ((0.0, -76.0, 10.0), (0.0, 0.0, 8.0), 62),
            "rear_corner_oblique": ((-47.0, 56.0, 28.0), (0.0, 0.0, 7.0), 58),
            "aerial": ((51.0, -48.0, 54.0), (0.0, 0.0, 5.5), 55),
            "facade_close": ((24.0, -37.0, 12.0), (7.0, -8.0, 9.0), 72),
            "identity_close": ((27.0, -31.0, 20.0), (6.0, -4.0, 16.0), 72),
            "street": ((42.0, -74.0, 6.0), (0.0, 0.0, 7.5), 64),
            "context": ((72.0, -88.0, 45.0), (0.0, 0.0, 5.5), 52),
        }
    return {
        "preview": ((92.0, -123.0, 79.0), (0.0, 0.0, 34.0), 50),
        "front_corner_oblique": ((81.0, -110.0, 67.0), (0.0, 0.0, 33.0), 53),
        "front_elevation": ((0.0, -172.0, 43.0), (0.0, 0.0, 36.0), 58),
        "rear_corner_oblique": ((-73.0, 88.0, 62.0), (0.0, 0.0, 31.0), 57),
        "aerial": ((88.0, -86.0, 126.0), (0.0, 0.0, 28.0), 55),
        "facade_close": ((29.0, -49.0, 32.0), (8.0, -8.0, 30.0), 72),
        "identity_close": ((31.0, -42.0, 70.0), (4.0, -3.0, 65.0), 76),
        "street": ((51.0, -96.0, 11.5), (0.0, 0.0, 29.0), 65),
        "context": ((109.0, -132.0, 91.0), (0.0, 0.0, 26.0), 52),
    }


def render_views(folder: Path, cfg: dict, *, view_set: str) -> list[str]:
    presentation = configure_render(cfg)
    views = view_map(cfg)
    selected = {
        "preview": {"preview"},
        "pilot": {"preview", "front_corner_oblique", "front_elevation", "aerial", "facade_close", "identity_close"},
        "all": set(views),
    }.get(view_set, {view_set})
    rendered: list[str] = []
    for role, (location, target, lens) in views.items():
        if role not in selected:
            continue
        aim_camera(location, target, lens)
        filename = f"{cfg['family']}_{role}.png"
        bpy.context.scene.render.filepath = str(folder / filename)
        bpy.ops.render.render(write_still=True)
        rendered.append(filename)
    delete_objects(presentation)
    return rendered


def footprint_contract(cfg: dict) -> dict:
    family = cfg["family"]
    if family != "art-deco-cream-terracotta-tower":
        if family == "restored-kyoto-machiya":
            profiles = {
                "rectangle": {"recommendedWidth_m": [13.0, 38.0], "recommendedDepth_m": [10.0, 25.0], "recommendedFloors": [2, 4], "scaleMin": 0.76, "scaleMax": 1.28, "maxAxisRatio": 1.20, "preferredBayMultiple_m": 3.0},
                "l_shape": {"recommendedWidth_m": [16.0, 44.0], "recommendedDepth_m": [12.0, 30.0], "recommendedFloors": [2, 4], "scaleMin": 0.72, "scaleMax": 1.30, "maxAxisRatio": 1.22, "preferredBayMultiple_m": 3.0, "wingDepth_m": [5.5, 10.0]},
            }
            preferred = ["rectangle", "l_shape"]
            rationale = "The entry, lower eave, gable ends and roof terminals remain fixed. Differently sized rectangles or L-shaped plots repeat complete three metre post-and-koshi bays with real lattice gaps rather than stretching slats, tiles or noren."
        elif family == "mid-century-glass-steel-pavilion":
            profiles = {
                "rectangle": {"recommendedWidth_m": [18.0, 55.0], "recommendedDepth_m": [14.0, 40.0], "recommendedFloors": [1, 5], "scaleMin": 0.72, "scaleMax": 1.32, "maxAxisRatio": 1.22, "preferredBayMultiple_m": 3.43},
                "l_shape": {"recommendedWidth_m": [22.0, 68.0], "recommendedDepth_m": [16.0, 46.0], "recommendedFloors": [1, 5], "scaleMin": 0.70, "scaleMax": 1.34, "maxAxisRatio": 1.24, "preferredBayMultiple_m": 3.43, "wingDepth_m": [7.0, 14.0]},
            }
            preferred = ["rectangle", "l_shape"]
            rationale = "The travertine core and knife-edge roof remain fixed while complete 3.43 metre steel-and-glass structural bays repeat along rectangle or L-shaped gallery wings; panes, columns and slab edges never stretch independently."
        elif family == "timber-glass-transit-station-block":
            profiles = {
                "rectangle": {"recommendedWidth_m": [43.0, 150.0], "recommendedDepth_m": [28.0, 100.0], "recommendedFloors": [4, 10], "scaleMin": 0.68, "scaleMax": 1.34, "maxAxisRatio": 1.26, "preferredBayMultiple_m": 4.83},
                "l_shape": {"recommendedWidth_m": [48.0, 170.0], "recommendedDepth_m": [30.0, 112.0], "recommendedFloors": [4, 10], "scaleMin": 0.66, "scaleMax": 1.36, "maxAxisRatio": 1.28, "preferredBayMultiple_m": 4.83, "wingDepth_m": [16.0, 30.0]},
            }
            preferred = ["rectangle", "l_shape"]
            rationale = "The entrance canopy, concourse hierarchy and PV roof remain fixed. Oversized station plots repeat complete 4.83 metre glass or timber-louver bays, including pane, pressure cap, slab, occupied depth and real louver blades."
        else:
            profiles = {
                "rectangle": {"recommendedWidth_m": [28.0, 90.0], "recommendedDepth_m": [16.0, 45.0], "recommendedFloors": [3, 8], "scaleMin": 0.72, "scaleMax": 1.32, "maxAxisRatio": 1.22, "preferredBayMultiple_m": 6.0},
                "l_shape": {"recommendedWidth_m": [32.0, 105.0], "recommendedDepth_m": [18.0, 52.0], "recommendedFloors": [3, 8], "scaleMin": 0.70, "scaleMax": 1.34, "maxAxisRatio": 1.24, "preferredBayMultiple_m": 6.0, "wingDepth_m": [9.0, 18.0]},
            }
            preferred = ["rectangle", "l_shape"]
            rationale = "The central entry, PV and sedum roof fields and gable terminals remain fixed. Complete six metre passive-house bays repeat along the long axis with deep reveal, triple pane, occupied depth and optional real blind blades intact."
        primary = profiles["rectangle"]
        return {
            "preferredProfiles": preferred,
            "minimumPreferredProfiles": len(preferred),
            "profileRationale": rationale,
            "fixedLandmarkScaleBand": {"scaleMin": primary["scaleMin"], "scaleMax": primary["scaleMax"], "maxAxisRatio": primary["maxAxisRatio"]},
            "recommendedWidth_m": primary["recommendedWidth_m"],
            "recommendedDepth_m": primary["recommendedDepth_m"],
            "recommendedFloors": primary["recommendedFloors"],
            "preferredBayMultiple_m": primary["preferredBayMultiple_m"],
            "scaleMin": primary["scaleMin"],
            "scaleMax": primary["scaleMax"],
            "maxAxisRatio": primary["maxAxisRatio"],
            "profiles": profiles,
        }
    profiles = {
        "rectangle": {
            "recommendedWidth_m": [23.0, 75.0],
            "recommendedDepth_m": [21.0, 45.0],
            "recommendedFloors": [10, 28],
            "scaleMin": 0.74,
            "scaleMax": 1.26,
            "maxAxisRatio": 1.18,
            "preferredBayMultiple_m": 4.29,
        }
    }
    primary = profiles["rectangle"]
    return {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": (
            "The exact seven-five-three setback landmark tolerates ordinary independent-axis drawing error. "
            "Oversized targets repeat complete 4.29 metre terra-cotta bays along the long axis, preserving pier, "
            "pane, occupied depth and spandrel rather than stretching ornament or windows."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": primary["scaleMin"],
            "scaleMax": primary["scaleMax"],
            "maxAxisRatio": primary["maxAxisRatio"],
        },
        "recommendedWidth_m": primary["recommendedWidth_m"],
        "recommendedDepth_m": primary["recommendedDepth_m"],
        "recommendedFloors": primary["recommendedFloors"],
        "preferredBayMultiple_m": primary["preferredBayMultiple_m"],
        "scaleMin": primary["scaleMin"],
        "scaleMax": primary["scaleMax"],
        "maxAxisRatio": primary["maxAxisRatio"],
        "profiles": profiles,
    }


def massing_graph(cfg: dict) -> dict:
    family = cfg["family"]
    if family == "restored-kyoto-machiya":
        return {"type": "fixed_two_storey_machiya_with_repeatable_complete_post_and_koshi_bays", "occupied_storeys": 2, "post_and_beam_bays": 6, "continuous_upper_koshi_screen": True, "real_gap_preserving_lattice": True, "deep_recessed_entries": 1, "plain_indigo_noren_panels": 3, "large_kawara_gable_roofs": 1, "lower_tiled_street_eaves": 1, "individual_kawara_rows": 22, "integral_side_garden": True, "physical_window_layers": ["warm_occupied_depth", "smoky_pane", "real_koshi_screen", "timber_post_and_beam", "deep_eave"]}
    if family == "mid-century-glass-steel-pavilion":
        return {"type": "fixed_three_level_transparent_pavilion_with_repeatable_complete_structural_bays", "occupied_storeys": 3, "front_structural_bays": 7, "side_structural_bays": 5, "continuous_freestanding_columns": True, "pale_travertine_service_cores": 1, "floating_knife_edge_roofs": 1, "roof_overhang_axes": 2, "occupied_depth_variants": ["daylight_gallery", "evening_gallery"], "minimum_room_depth_m": 1.4, "physical_window_layers": ["day_or_evening_gallery_depth", "physical_floor_and_ceiling_returns", "crystal_low_iron_pane", "fine_pressure_cap_and_mullion", "black_steel_column", "concrete_slab_edge"]}
    if family == "timber-glass-transit-station-block":
        return {"type": "fixed_six_level_station_with_repeatable_glazed_and_timber_louver_bays", "occupied_storeys": 6, "transparent_concourse_levels": 3, "timber_upper_levels": 3, "front_bays": 12, "visible_escalators": 2, "recessed_public_doors": 5, "integral_glass_canopies": 1, "external_louver_blades_per_screen": 10, "extensive_green_roofs": 1, "photovoltaic_canopy_rows": 2, "physical_window_layers": ["occupied_transit_depth", "high_transmission_pane", "pressure_cap", "floor_plate", "timber_rainscreen", "real_external_louver"]}
    if family == "passive-house-timber-block":
        return {"type": "fixed_four_level_passive_timber_block_with_repeatable_complete_environmental_bays", "occupied_storeys": 4, "front_bays": 6, "deep_insulated_reveals": True, "physical_triple_glazing": True, "split_panes_per_opening": 2, "occupied_depth_variants": ["daylight_room", "evening_room"], "real_external_blind_sets": 8, "deep_recessed_entries": 1, "asymmetric_roof_planes": 2, "individually_framed_roof_pv_modules": 90, "pv_cell_topology": "6_columns_x_10_rows", "continuous_pv_mounting_rails": 3, "sedum_roof_fields": 1, "physical_rooflights": 3, "vertical_gable_pv_panels": 4, "physical_window_layers": ["day_or_evening_occupied_depth", "split_neutral_triple_panes", "slim_dark_frame", "physical_larch_head_sill_and_jamb_returns", "real_blind_blades_headbox_and_guides", "vertical_larch_rainscreen"]}
    return {
        "type": "fixed_art_deco_setback_landmark_with_repeatable_complete_terracotta_bays",
        "occupied_storeys": 15,
        "double_height_public_podium": True,
        "setback_stages": [
            {"bays": 7, "floors": 8, "width_m": 30.0, "depth_m": 26.0},
            {"bays": 5, "floors": 3, "width_m": 23.0, "depth_m": 21.0},
            {"bays": 3, "floors": 2, "width_m": 16.0, "depth_m": 15.0},
        ],
        "real_setback_terraces": 2,
        "integral_sunburst_relief": True,
        "octagonal_lantern_posts": 8,
        "physical_window_layers": [
            "warm_occupied_depth",
            "neutral_smoky_pane",
            "aged_bronze_frame",
            "deep_reveal",
            "terracotta_pier",
            "geometric_spandrel",
        ],
    }


def facade_sheet_contract(skin: dict, cfg: dict) -> dict:
    family = cfg["family"]
    contract = facade_contract(family, skin, f"/families/{family}/textures/source/archetype-goalpost.png")
    contract["geometry_detail_profile"] = "hero"
    if family != "art-deco-cream-terracotta-tower":
        if family == "restored-kyoto-machiya":
            contract["bay_strategy"] = {"fixed_end_bays": ["recessed_noren_entry", "lower_street_eave", "gable_end_frames", "ridge_terminals"], "repeatable_middle_bays": list(range(6)), "middle_variants": ["typical_a", "typical_b", "typical_c"], "rule": "Repeat one complete three metre post-and-koshi bay; lattice slats, glass, occupied depth, beam and eave datum remain one unit."}
            coverage = {"front": "continuous upper koshi screen, ground shop lattice, three plain indigo noren and recessed entrance", "left": "complete clay-infill timber frame with punched occupied openings", "right": "complete clay-infill timber frame, drainage and integral bamboo passage", "rear": "complete service elevation with upper koshi panels and lower timber doors", "roof": "large kawara gable, exposed rafters, individual tile rows, ridge cap, gutters and lower street eave"}
            fixed = ["podium/entrance", "corner returns", "crown", "roof", "noren entry", "lower street eave", "gable ends", "ridge cap", "gutters and downpipes"]
        elif family == "mid-century-glass-steel-pavilion":
            contract["bay_strategy"] = {"fixed_end_bays": ["travertine_service_core", "double_entry", "cantilevered_roof_edges"], "repeatable_middle_bays": list(range(7)), "middle_variants": ["typical_a", "typical_b", "typical_c"], "rule": "Repeat one complete 3.43 metre steel-and-glass bay containing pane, occupied depth, mullion, column and slab edge."}
            coverage = {"front": "three transparent occupied levels with crystal low-iron panes, fine pressure caps, deep day/evening gallery cavities and a recessed double entry below the floating roof", "left": "wrapped clear curtain wall with physical floor and ceiling returns beneath the deep roof overhang", "right": "pale travertine service core beside complete transparent structural bays", "rear": "complete day/evening occupied rear curtain wall, service door and continuous steel frame", "roof": "one exceptionally thin warm-white roof plane with deep two-axis cantilever and crisp fascia"}
            fixed = ["podium/entrance", "corner returns", "crown", "roof", "travertine service core", "double entry", "continuous steel frame", "knife-edge roof"]
        elif family == "timber-glass-transit-station-block":
            contract["bay_strategy"] = {"fixed_end_bays": ["five_public_doors", "broad_integral_canopy", "glass_to_timber_transition", "green_roof_and_pv_rows"], "repeatable_middle_bays": list(range(12)), "middle_variants": ["typical_a", "typical_b", "typical_c"], "rule": "Repeat a whole 4.83 metre transit bay with pane, cap, slab, occupied depth and either timber rainscreen plus real louvers or complete concourse glazing."}
            coverage = {"front": "three transparent concourse levels with visible circulation, five doors and broad integral canopy below three timber-louver levels", "left": "complete glazed public base and wrapped timber upper construction", "right": "complete glazed public base and wrapped timber upper construction", "rear": "occupied platform-side curtain wall and alternating timber-louver bays", "roof": "extensive green roof, screened service zone, restrained planting and two long PV canopy rows"}
            fixed = ["podium/entrance", "corner returns", "crown", "roof", "public door bank", "integral glass canopy", "visible escalators", "glass-to-timber transition", "green roof", "two PV rows"]
        else:
            contract["bay_strategy"] = {"fixed_end_bays": ["deep_central_entry", "larch_gable_ends", "asymmetric_environmental_roof", "vertical_gable_pv_bank"], "repeatable_middle_bays": list(range(6)), "middle_variants": ["typical_a", "typical_b", "typical_c"], "rule": "Repeat one complete six metre passive bay with larch piers, physical insulated returns, split triple panes, alternating occupied depth and optional in-reveal blind or insulated panel."}
            coverage = {"front": "six deep split-triple-glazed larch bays, alternating day/evening room depth, in-reveal external blinds, pale panels and recessed timber entrance", "left": "complete larch gable with small punched windows", "right": "complete larch gable with small openings and four individually framed vertical PV modules", "rear": "complete occupied secondary facade with mixed deep openings, service doors and drainage", "roof": "ninety individually framed 6x10-cell PV modules on three physical mounting rails above the upper slope, sedum lower field, three rooflights, zinc ridge, gutters and downpipes"}
            fixed = ["podium/entrance", "corner returns", "crown", "roof", "deep central entry", "larch gable ends", "ninety-module photovoltaic array", "sedum roof", "rooflights", "four-module vertical PV bank"]
        contract["assembly_contract"] = {"fixed": fixed, "repeatable": ["typical_a", "typical_b", "typical_c"], "side_elevations": coverage["left"] + "; " + coverage["right"], "elevation_coverage": coverage, "variation_policy": "Use the complete fixed landmark inside its independent-axis scale band. Oversized targets use long-axis streetwall repeat of complete semantic bays, never family_incompatible."}
        return contract
    contract["bay_strategy"] = {
        "fixed_end_bays": [
            "deep_bronze_public_entrance",
            "seven_five_three_setback_transition",
            "sunburst_relief",
            "octagonal_gilded_lantern",
        ],
        "repeatable_middle_bays": list(range(7)),
        "middle_variants": ["typical_a", "typical_b", "typical_c"],
        "rule": "Repeat one whole 4.29 metre bay with its physical pane, occupied depth, bronze frame, terra-cotta piers and geometric spandrel.",
    }
    coverage = {
        "front": "deep central bronze entrance, black granite public windows and seven-five-three terra-cotta setback hierarchy",
        "left": "complete wrapped terra-cotta bays, real glazing and setback terrace returns",
        "right": "complete wrapped terra-cotta bays, real glazing and setback terrace returns",
        "rear": "complete occupied secondary elevation with matching vertical piers and service-door hierarchy",
        "roof": "two full setback terraces, three crown plinths, octagonal lantern, eight gilded posts, faceted cap and finial",
    }
    contract["assembly_contract"] = {
        "fixed": [
            "podium/entrance",
            "corner returns",
            "crown",
            "roof",
            "deep bronze public entrance",
            "seven-five-three setback transition",
            "sunburst relief",
            "octagonal lantern",
            "eight gilded posts",
            "faceted cap and finial",
        ],
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": coverage["left"] + "; " + coverage["right"],
        "elevation_coverage": coverage,
        "variation_policy": "Use the complete fixed landmark inside its independent-axis scale band. Oversized targets use long-axis streetwall repeat of complete semantic bays, never family_incompatible.",
    }
    return contract


def promote_catalogue_thumbnail(folder: Path, cfg: dict) -> None:
    preview = folder / f"{cfg['family']}_preview.png"
    if not preview.is_file():
        return
    catalogue = folder.parents[1] / "archetypes" / "buildings" / cfg["catalogue_slug"]
    catalogue.mkdir(parents=True, exist_ok=True)
    shutil.copy2(preview, catalogue / "hero.png")
    index = cfg.get("catalogue_variant_index")
    if index is not None:
        shutil.copy2(preview, catalogue / f"variant_{index}.png")


def build_family(
    output_root: Path,
    cfg: dict,
    *,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool,
    skip_assembled_export: bool,
) -> None:
    clear_scene()
    family = cfg["family"]
    folder = (output_root / family).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(folder, cfg)
    objects = build_assembled(mats, cfg)
    normalize_bottom_centre(objects)
    actual_native = bounds_dimensions(objects)
    assembled_path = folder / f"{family}_assembled.glb"
    manifest_path = folder / f"{family}_manifest.json"
    previous = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    if not skip_assembled_export:
        export_glb(assembled_path, objects)
        assembled_triangles = evaluated_triangle_count(objects)
        assembled_materials = material_count(objects)
    else:
        assembled_triangles = int((previous.get("assembled") or {}).get("triangle_count") or evaluated_triangle_count(objects))
        assembled_materials = int((previous.get("assembled") or {}).get("material_count") or material_count(objects))
    renders = list(previous.get("renders") or []) if skip_renders else render_views(folder, cfg, view_set=view_set)
    delete_objects(objects)
    modules = list(previous.get("modules") or []) if skip_modules else build_modules(folder, mats, skin, cfg)
    footprint = footprint_contract(cfg)
    graph = massing_graph(cfg)
    width, depth, height = actual_native
    assembled = {
        "filename": assembled_path.name,
        "module_family": family,
        "assembly_class": "fixed_landmark",
        "fixed_semantic": True,
        "repeatable_z": False,
        "source_variant_id": cfg["variant_id"],
        "generation_archetype_id": cfg["variant_id"],
        "width_m": width,
        "depth_m": depth,
        "floors": cfg["native_floors"],
        "uses_setback": family == "art-deco-cream-terracotta-tower",
        "uses_crown": True,
        "height_m": height,
        "triangle_count": assembled_triangles,
        "material_count": assembled_materials,
        "stack": [{"role": "assembled", "variant_key": "reference_locked", "level": 0, "z_m": 0.0, "height_m": height}],
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": width,
            "depth_m": depth,
            "segments": [{"id": "complete_fixed_landmark", "centre_x_m": 0.0, "centre_y_m": 0.0, "length_m": width, "thickness_m": depth, "rotation_degrees": 0.0}],
        },
        "massing_graph": graph,
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    aliases = cfg["aliases"]
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave13_diverse_families.py",
            "version": "1.0.0",
            "blender_version": bpy.app.version_string,
            "render_engine": "BLENDER_EEVEE",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": family,
        "archetype_id": cfg["archetype_id"],
        "archetype_label": cfg["label"],
        "variant_id": cfg["variant_id"],
        "generation_archetype_id": cfg["variant_id"],
        "archetype_aliases": aliases,
        "aesthetic_category_id": cfg["aesthetic"],
        "development_type": cfg["development_type"],
        "reuse_keys": [*aliases, *cfg["reuse_keys"]],
        "generation_tags": [
            "wave13",
            "fixed_landmark_and_modular_fallback",
            "custom_pbr_skin",
            "physical_separate_glazing",
            "occupied_interior_depth",
            "complete_semantic_bay_repeat",
            *(
                ["seven_five_three_setback_massing", "deep_integral_public_entrance", "octagonal_gilded_lantern"]
                if family == "art-deco-cream-terracotta-tower"
                else ["real_gap_preserving_koshi_lattice", "individual_kawara_rows", "plain_indigo_noren"]
                if family == "restored-kyoto-machiya"
                else ["continuous_black_steel_frame", "transparent_occupied_gallery", "floating_knife_edge_roof"]
                if family == "mid-century-glass-steel-pavilion"
                else ["transparent_station_concourse", "real_external_timber_louvers", "green_roof_and_twin_pv_canopies"]
                if family == "timber-glass-transit-station-block"
                else ["deep_triple_glazed_reveals", "real_external_blind_blades", "pv_and_sedum_environmental_roof"]
            ),
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin, cfg),
        "massing_graph": graph,
        "material_budget": {
            "max_assembled_materials": 18,
            "rationale": "Opaque construction, physical glazing, occupied depth, structure, environmental roof elements and registered elevation underlays remain distinct because their contrasting material response carries the source archetype identity.",
        },
        "dimensions": {
            "width_m": width,
            "depth_m": depth,
            "podium_height_m": cfg["podium_height"],
            "floor_height_m": cfg["floor_height"],
            "setback_height_m": cfg["floor_height"],
            "roof_height_m": cfg["roof_height"],
            "crown_height_m": cfg["crown_height"],
            "default_floors": cfg["native_floors"],
            "min_floors": cfg["min_floors"],
            "max_floors": cfg["max_floors"],
        },
        "native_width_m": width,
        "native_depth_m": depth,
        "native_height_m": height,
        "native_floors": cfg["native_floors"],
        "min_floors": cfg["min_floors"],
        "max_floors": cfg["max_floors"],
        "default_floors": cfg["native_floors"],
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{family}_preview.png",
        "renders": renders,
        "architectural_identity": cfg["identity"],
        "material_zones": cfg["material_zones"],
        "glass_profile": cfg["glass_profile"],
        "source_provenance": {
            "catalogue_archetype_id": cfg["archetype_id"],
            "catalogue_variant_id": cfg["variant_id"],
            "catalogue_alias_ids": aliases[2:],
            "elevation_source": f"/families/{family}/elevation.jpg",
            "goalpost": f"/families/{family}/textures/source/archetype-goalpost.png",
            "reference_generation": f"/families/{family}/textures/source/reference-generation.json",
            "method": "reference-locked four-view source board, six-zone material construction plate, deterministic true-metric parts, physical layered glazing, occupied depth, complete secondary elevations and semantic LEGO fallback modules",
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    grammar = {
        "family_id": family,
        "source": {
            "archetype_id": cfg["archetype_id"],
            "variant_id": cfg["variant_id"],
            "generation_archetype_id": cfg["variant_id"],
            "reuse_keys": manifest["reuse_keys"],
        },
        "dimensions": manifest["dimensions"],
        "architectural_signature": {
            "identity": cfg["identity"],
            "material_zones": cfg["material_zones"],
            "glass_profile": cfg["glass_profile"],
            "kits": [
                "reference_locked_fixed_landmark",
                "physical_layered_glazing",
                "occupied_interior_depth",
                "semantic_repeatable_middle_bays",
                "fixed_crown_and_roof_kit",
            ],
        },
        "archetype_aliases": aliases,
        "footprint_compatibility": footprint,
        "massing_graph": graph,
    }
    (folder / "grammar.json").write_text(json.dumps(grammar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (folder / "archetype-source.json").write_text(json.dumps(manifest["source_provenance"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    promote_catalogue_thumbnail(folder, cfg)
    print(f"[wave13] {family}: {assembled_triangles} triangles, {assembled_materials} materials, {len(modules)} modules, {len(renders)} renders, native={actual_native}", flush=True)


def render_existing(output_root: Path, cfg: dict, *, view_set: str) -> None:
    clear_scene()
    folder = (output_root / cfg["family"]).resolve()
    mats, _skin = load_palette(folder, cfg)
    objects = build_assembled(mats, cfg)
    normalize_bottom_centre(objects)
    rendered = render_views(folder, cfg, view_set=view_set)
    delete_objects(objects)
    promote_catalogue_thumbnail(folder, cfg)
    print(f"[wave13] {cfg['family']}: rendered {len(rendered)} views", flush=True)


def main() -> int:
    args = parse_args()
    cfg = dict(FAMILIES[args.family])
    cfg["family"] = args.family
    if args.render_existing:
        render_existing(args.output_root, cfg, view_set=args.view_set)
    else:
        build_family(
            args.output_root,
            cfg,
            view_set=args.view_set,
            skip_renders=args.skip_renders,
            skip_modules=args.skip_modules,
            skip_assembled_export=args.skip_assembled_export,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
