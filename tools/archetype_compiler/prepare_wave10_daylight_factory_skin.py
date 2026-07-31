"""Prepare the reference-locked PBR package for the historic daylight factory.

The source board fixes one coherent factory in four views.  This adapter
extracts those views, isolates six construction materials from the generated
material plate, then delegates deterministic near/far PBR derivation to the
shared reference-skin pipeline.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_daylight_factory_skin.py
"""
from __future__ import annotations

import json

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


FAMILY = "historic-daylight-factory"
SOURCE_ROOT = FAMILY_ROOT / FAMILY / "textures" / "source"

# Four equal views on the render-locked goalpost board.
GOALPOST_CELLS = {
    "street-hero-source-v1.png": (0.010, 0.016, 0.494, 0.491),
    "loading-court-source-v1.png": (0.504, 0.016, 0.990, 0.491),
    "aerial-roof-source-v1.png": (0.010, 0.507, 0.494, 0.984),
    "front-elevation-source-v1.png": (0.504, 0.507, 0.990, 0.984),
}

# Clean 3 x 2 plate with narrow neutral gutters.
MATERIAL_CELLS = {
    "red-brick-material-source-v1.png": (0.002, 0.002, 0.331, 0.493),
    "zinc-roof-material-source-v1.png": (0.337, 0.002, 0.665, 0.493),
    "black-steel-material-source-v1.png": (0.670, 0.002, 0.998, 0.493),
    "industrial-glass-material-source-v1.png": (0.002, 0.507, 0.331, 0.998),
    "limestone-material-source-v1.png": (0.337, 0.507, 0.665, 0.998),
    "concrete-material-source-v1.png": (0.670, 0.507, 0.998, 0.998),
}

CONFIG = {
    "archetype_id": "daylight_factory",
    "variant_id": "factory_sawtooth_roof",
    "skin_schema": "historic-daylight-factory-skin@1",
    "elevation_source": "front-elevation-source-v1.png",
    "occupied_depth_source": "occupied-workshop-source-v1.png",
    "bands": {
        "facade": (0.025, 0.315, 0.975, 0.930),
        "podium": (0.025, 0.755, 0.975, 0.930),
        "floor_a": (0.025, 0.500, 0.975, 0.825),
        "floor_b": (0.105, 0.455, 0.430, 0.825),
        "crown": (0.025, 0.315, 0.975, 0.525),
        "side": (0.025, 0.405, 0.245, 0.930),
    },
    "prefixes": {
        "facade": "elevation",
        "podium": "factory_podium",
        "floor_a": "arched_window_register",
        "floor_b": "brick_pier_register",
        "crown": "corbelled_brick_crown",
        "side": "factory_return",
        "interior": "occupied_workshop",
        "red_brick": "red_brick",
        "zinc_roof": "oxidized_zinc_roof",
        "black_steel": "blackened_steel",
        "industrial_glass": "industrial_low_e_glass",
        "limestone": "pale_limestone",
        "concrete": "broom_finish_concrete",
        "loading_door": "dark_green_loading_door",
        "asphalt": "aged_factory_asphalt",
        "timber": "workshop_timber",
    },
    "support": {
        "red_brick": ((126, 66, 46), "brick", 18101),
        "zinc_roof": ((104, 119, 127), "metal", 18111),
        "black_steel": ((27, 30, 31), "metal", 18121),
        "industrial_glass": ((79, 100, 115), "glass", 18131),
        "limestone": ((187, 181, 167), "stone", 18141),
        "concrete": ((157, 155, 148), "stone", 18151),
        "loading_door": ((31, 50, 43), "metal", 18161),
        "asphalt": ((54, 54, 52), "stone", 18171),
        "timber": ((111, 70, 40), "wood", 18181),
    },
    "support_sources": {
        "red_brick": "red-brick-material-source-v1.png",
        "zinc_roof": "zinc-roof-material-source-v1.png",
        "black_steel": "black-steel-material-source-v1.png",
        "industrial_glass": "industrial-glass-material-source-v1.png",
        "limestone": "limestone-material-source-v1.png",
        "concrete": "concrete-material-source-v1.png",
        "loading_door": "black-steel-material-source-v1.png",
        "asphalt": "concrete-material-source-v1.png",
        "timber": "red-brick-material-source-v1.png",
    },
    "registered_surfaces": [
        "exactly_seven_repeating_northlight_roof_teeth",
        "seven_opaque_zinc_slopes_and_seven_steep_glazed_clerestories",
        "red_brown_load_bearing_brick_perimeter",
        "eleven_deep_segmental_arch_steel_sash_front_bays",
        "physical_low_e_panes_with_occupied_workshop_depth",
        "corbelled_brick_eaves_and_pale_limestone_sills",
        "projecting_brick_administration_vestibule",
        "three_recessed_rear_loading_docks",
        "complete_dock_stairs_bumpers_canopies_and_service_doors",
        "visible_steel_roof_trusses_columns_gutters_and_downpipes",
    ],
    "registration": (
        "The canonical four-view board locks one sixty-by-forty-metre historic "
        "daylight factory: seven repeatable northlight teeth, a red-brown "
        "brick perimeter, tall segmental-arched steel-sash windows, a small "
        "projecting administration entry, and three working rear loading docks."
    ),
    "opening_method": (
        "Every public window, clerestory and loading opening is physical "
        "geometry. Brick walls are assembled around voids; panes sit behind "
        "deep jambs and steel mullions, with workshop structure and fixtures "
        "placed behind the glass for real parallax."
    ),
    "generic_tiling_allowed": False,
}


def _crop_cells(
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


def _prepare_occupied_depth() -> None:
    """Use the hero's transparent workshop register as depth authority."""
    hero = ImageOps.exif_transpose(
        Image.open(SOURCE_ROOT / "street-hero-source-v1.png")
    ).convert("RGB")
    width, height = hero.size
    # The upper-left hero places the clearest occupied sash run centrally.
    hero.crop(
        (
            round(width * 0.155),
            round(height * 0.245),
            round(width * 0.820),
            round(height * 0.780),
        )
    ).save(SOURCE_ROOT / "occupied-workshop-source-v1.png", optimize=True)


def _write_provenance() -> None:
    payload = {
        "schema": "reference-generation@1",
        "family": FAMILY,
        "archetype_id": "daylight_factory",
        "variant_id": "factory_sawtooth_roof",
        "model": "gpt-image-2",
        "generated_at": "2026-07-31",
        "status": "source-pack-complete",
        "design_lock": {
            "native_building_dimensions_m": [60.0, 38.0, 10.15],
            "northlight_roof_teeth": 7,
            "front_window_openings": 10,
            "primary_material": "red-brown fired common brick",
            "window_rule": "deep physical segmental-arched black steel sash",
            "front_entry": "one projecting brick administration vestibule",
            "rear_service": "three recessed working loading docks",
        },
        "research": [
            {
                "title": "The Legacy of the Sawtooth Roof",
                "url": "https://www.archdaily.com/1012186/the-legacy-of-the-sawtooth-roof-an-icon-of-industrial-architecture",
                "lesson": (
                    "The steep glazed faces should turn away from direct sun and "
                    "repeat as a complete structural daylighting system across a "
                    "deep industrial plan."
                ),
            },
            {
                "title": "Preservation Brief 13: Repair and Thermal Upgrading of Historic Steel Windows",
                "url": "https://www.nps.gov/orgs/1739/upload/preservation-brief-13-steel-windows.pdf",
                "lesson": (
                    "Historic rolled-steel sash relies on very slender frames, "
                    "many small panes, expressed perimeter putty lines and real "
                    "wall depth rather than dark window decals."
                ),
            },
            {
                "title": "Heritage Steel Windows",
                "url": "https://www.portamet.com/heritage-steel-windows",
                "lesson": (
                    "Contemporary heritage-compatible assemblies can keep the "
                    "thin industrial profile while using thermally broken frames "
                    "and physically plausible insulated glazing."
                ),
            },
        ],
        "sources": [
            {
                "file": "archetype-goalpost.png",
                "source_id": "call_ztjdW2Ylj0c4YiteaBj0LqAm",
                "role": "canonical_four_view_reference_board",
                "prompt_summary": (
                    "One coherent red-brick daylight factory in front, rear, "
                    "aerial and elevation views with seven northlight teeth."
                ),
            },
            {
                "file": "front-elevation-source-v1.png",
                "source_id": "call_ztjdW2Ylj0c4YiteaBj0LqAm:front-elevation-crop",
                "role": "shadow_neutral_front_elevation",
                "prompt_summary": (
                    "Straight-on facade authority for brick piers, segmental "
                    "steel sash, corbel course and the projecting entry."
                ),
            },
            {
                "file": "loading-court-source-v1.png",
                "source_id": "call_ztjdW2Ylj0c4YiteaBj0LqAm:loading-court-crop",
                "role": "rear_loading_goalpost",
                "prompt_summary": (
                    "Rear service authority for three recessed loading doors, "
                    "dock platforms, stairs, canopies and exhaust stack."
                ),
            },
            {
                "file": "aerial-roof-source-v1.png",
                "source_id": "call_ztjdW2Ylj0c4YiteaBj0LqAm:aerial-roof-crop",
                "role": "roof_geometry_and_drainage_goalpost",
                "prompt_summary": (
                    "High aerial authority for exactly seven zinc-and-glass "
                    "northlight teeth, valleys, gutters and roof penetrations."
                ),
            },
            {
                "file": "occupied-workshop-source-v1.png",
                "source_id": "call_ztjdW2Ylj0c4YiteaBj0LqAm:occupied-depth-crop",
                "role": "window_materiality_and_occupied_depth",
                "prompt_summary": (
                    "Hero crop locking blue-grey glass, thin steel subdivisions, "
                    "visible trusses, benches and warm workshop depth."
                ),
            },
            {
                "file": "material-construction-source-v1.png",
                "source_id": "call_nV6NGwlLlCGDJOhtECMUm2V7",
                "role": "six_zone_pbr_material_plate",
                "prompt_summary": (
                    "Orthographic plate of fired brick, oxidized zinc, black "
                    "steel, industrial glass, limestone and concrete."
                ),
            },
        ],
    }
    (SOURCE_ROOT / "reference-generation.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    _crop_cells("archetype-goalpost.png", GOALPOST_CELLS)
    _crop_cells("material-construction-source-v1.png", MATERIAL_CELLS)
    _prepare_occupied_depth()
    _write_provenance()
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
