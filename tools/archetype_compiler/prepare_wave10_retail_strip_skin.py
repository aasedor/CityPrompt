"""Prepare the reference-locked PBR package for the contemporary retail strip.

The source pack fixes one raised brick anchor, six smaller tenant bays, a
continuous steel-and-cedar canopy, transparent occupied storefronts, a
restaurant patio, and a complete roof/rear-service envelope. This adapter
extracts clean construction samples before delegating deterministic near/far
PBR derivation to the shared reference-skin pipeline.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_retail_strip_skin.py
"""
from __future__ import annotations

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


FAMILY = "contemporary-prairie-retail-strip"
SOURCE_ROOT = FAMILY_ROOT / FAMILY / "textures" / "source"

# The material source is a clean 3 x 2 plate with narrow neutral gutters.
MATERIAL_CELLS = {
    "russet-brick-material-source-v1.png": (0.002, 0.002, 0.302, 0.493),
    "charcoal-metal-material-source-v1.png": (0.311, 0.002, 0.612, 0.493),
    "cedar-soffit-material-source-v1.png": (0.620, 0.002, 0.998, 0.493),
    "storefront-glass-material-source-v1.png": (0.002, 0.507, 0.302, 0.998),
    "sidewalk-concrete-material-source-v1.png": (0.311, 0.507, 0.612, 0.998),
    "roof-membrane-material-source-v1.png": (0.620, 0.507, 0.998, 0.998),
}

CONFIG = {
    "archetype_id": "commercial_strip_mall",
    "variant_id": "strip_contemporary_retail",
    "skin_schema": "contemporary-prairie-retail-strip-skin@1",
    "elevation_source": "front-elevation-source-v1.png",
    "occupied_depth_source": "storefront-detail-source-v1.png",
    "bands": {
        "facade": (0.028, 0.285, 0.972, 0.690),
        "podium": (0.028, 0.455, 0.972, 0.690),
        "floor_a": (0.028, 0.385, 0.972, 0.665),
        "floor_b": (0.165, 0.315, 0.918, 0.500),
        "crown": (0.028, 0.285, 0.972, 0.445),
        "side": (0.030, 0.285, 0.210, 0.690),
    },
    "prefixes": {
        "facade": "elevation",
        "podium": "storefront_podium",
        "floor_a": "tenant_storefront_band",
        "floor_b": "signage_fascia_band",
        "crown": "parapet_crown",
        "side": "anchor_return",
        "interior": "occupied_retail_interior",
        "russet_brick": "russet_brick",
        "charcoal_metal": "charcoal_metal",
        "cedar_soffit": "cedar_soffit",
        "storefront_glass": "storefront_glass",
        "sidewalk_concrete": "sidewalk_concrete",
        "roof_membrane": "roof_membrane",
        "service_metal": "service_metal",
        "meter_bank": "meter_bank",
        "patio_timber": "patio_timber",
        "patio_railing": "patio_railing",
        "black_steel": "black_steel",
        "sign_panels": "sign_panels",
        "hvac_metal": "hvac_metal",
        "asphalt": "asphalt",
        "prairie_planting": "prairie_planting",
    },
    "support": {
        "russet_brick": ((145, 70, 44), "brick", 17101),
        "charcoal_metal": ((31, 35, 38), "metal", 17111),
        "cedar_soffit": ((165, 92, 42), "wood", 17121),
        "storefront_glass": ((69, 91, 104), "glass", 17131),
        "sidewalk_concrete": ((190, 187, 179), "stone", 17141),
        "roof_membrane": ((194, 196, 193), "stone", 17151),
        "service_metal": ((39, 42, 43), "metal", 17161),
        "meter_bank": ((89, 91, 88), "metal", 17171),
        "patio_timber": ((159, 91, 45), "wood", 17181),
        "patio_railing": ((24, 27, 28), "metal", 17191),
        "black_steel": ((18, 21, 23), "metal", 17201),
        "sign_panels": ((178, 105, 58), "metal", 17211),
        "hvac_metal": ((139, 143, 141), "metal", 17221),
        "asphalt": ((53, 54, 52), "stone", 17231),
        "prairie_planting": ((111, 101, 62), "stone", 17241),
    },
    "support_sources": {
        "russet_brick": "russet-brick-material-source-v1.png",
        "charcoal_metal": "charcoal-metal-material-source-v1.png",
        "cedar_soffit": "cedar-soffit-material-source-v1.png",
        "storefront_glass": "storefront-glass-material-source-v1.png",
        "sidewalk_concrete": "sidewalk-concrete-material-source-v1.png",
        "roof_membrane": "roof-membrane-material-source-v1.png",
        # Reuse the orthographic construction samples for surfaces whose
        # close-up reference views contain perspective and reflected context.
        # This keeps the skin source-derived without baking a photograph of a
        # whole wall or patio into a repeating material.
        "service_metal": "charcoal-metal-material-source-v1.png",
        "patio_timber": "cedar-soffit-material-source-v1.png",
        "patio_railing": "charcoal-metal-material-source-v1.png",
    },
    "registered_surfaces": [
        "sixty_metre_one_storey_retail_bar",
        "one_raised_left_russet_brick_anchor",
        "six_smaller_repeatable_tenant_bays",
        "continuous_charcoal_micro_ribbed_parapet",
        "continuous_thin_black_steel_canopy",
        "warm_cedar_linear_soffit_and_recessed_lights",
        "physical_low_e_storefronts_with_transoms",
        "seven_recessed_entries_and_real_thresholds",
        "occupied_retail_depth_shelves_counters_and_lighting",
        "abstract_backlit_sign_panels_without_brand_text",
        "brick_pilaster_tenant_bay_rhythm",
        "integrated_right_restaurant_corner_and_patio",
        "aligned_timber_pergola_black_rail_and_planters",
        "seven_rooftop_hvac_units_and_two_exhaust_fans",
        "seven_aligned_rear_service_zones",
        "screened_two_bin_garbage_enclosure_and_meter_banks",
        "sidewalk_joints_bollards_curb_ramps_and_drains",
    ],
    "registration": (
        "The canonical, elevation, aerial, storefront, patio and rear sources "
        "lock one contemporary prairie retail strip: a raised brick anchor at "
        "the left, six smaller tenant bays, one continuous black-and-cedar "
        "canopy, a transparent occupied storefront register, and an integrated "
        "restaurant patio at the right."
    ),
    "opening_method": (
        "Each tenant has a physical recessed storefront assembly with modeled "
        "jambs, sill, head, thermally broken frames, transoms, separate low-E "
        "panes, doors, hardware and thresholds. Occupied retail depth is placed "
        "behind the panes and reinforced with modeled shelves, counters, lights "
        "and merchandise for real parallax."
    ),
    "generic_tiling_allowed": False,
}


def _split_plate(
    source_name: str,
    cells: dict[str, tuple[float, float, float, float]],
) -> None:
    source = ImageOps.exif_transpose(
        Image.open(SOURCE_ROOT / source_name)
    ).convert("RGB")
    width, height = source.size
    for filename, (x0, y0, x1, y1) in cells.items():
        source.crop(
            (
                round(width * x0),
                round(height * y0),
                round(width * x1),
                round(height * y1),
            )
        ).save(SOURCE_ROOT / filename, optimize=True)


def main() -> int:
    _split_plate("material-construction-source-v1.png", MATERIAL_CELLS)
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
