"""Prepare the reference-locked PBR package for the Wave 10 hospital.

The source pack fixes the U-shaped clinical plan, public timber atrium,
patient-room glazing, planted envelope, service arrival and photovoltaic
healing roof.  This adapter promotes the material/detail-sheet cells and
occupied-depth captures into clean source plates before the shared
high-quality PBR builder derives near/far channel sets.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_hospital_skin.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


FAMILY = "biophilic-healthcare-mass-timber"
SOURCE_ROOT = FAMILY_ROOT / FAMILY / "textures" / "source"

MATERIAL_CELLS = {
    # Keep construction textures free of the photographed fins and beam
    # junctions.  Those features are modeled separately; including them in a
    # repeating source made false rails and joinery recur across every solid.
    "honey-timber-material-source-v1.png": (0.0, 0.03, 0.14, 0.48),
    "glulam-material-source-v1.png": (0.513, 0.30, 0.535, 0.49),
    "charred-timber-material-source-v1.png": (0.67, 0.03, 0.90, 0.48),
    "concrete-paving-material-source-v1.png": (
        0.0,
        0.54,
        0.30,
        0.80,
    ),
    "paving-material-source-v1.png": (0.03, 0.80, 0.30, 0.97),
    "living-wall-material-source-v1.png": (
        0.39,
        0.55,
        0.59,
        0.94,
    ),
    "solar-roof-material-source-v1.png": (
        0.70,
        0.55,
        0.98,
        0.94,
    ),
    "green-roof-material-source-v1.png": (0.68, 0.65, 0.79, 0.715),
}

OCCUPIED_CELLS = {
    "patient-interior-source-v1.png": (0.0, 0.0, 0.5, 1.0),
    "atrium-interior-source-v1.png": (0.5, 0.0, 1.0, 1.0),
}

CONFIG = {
    "archetype_id": "biophilic_healthcare",
    "variant_id": "healthcare_mass_timber",
    "skin_schema": "biophilic-healthcare-mass-timber-skin@1",
    "elevation_source": "front-elevation-source-v1.png",
    "occupied_depth_source": "patient-interior-source-v1.png",
    "bands": {
        "facade": (0.012, 0.165, 0.988, 0.865),
        "podium": (0.012, 0.595, 0.988, 0.865),
        "floor_a": (0.012, 0.385, 0.988, 0.645),
        "floor_b": (0.012, 0.245, 0.988, 0.505),
        "crown": (0.012, 0.165, 0.988, 0.315),
        "side": (0.012, 0.250, 0.295, 0.825),
    },
    "prefixes": {
        "facade": "elevation",
        "podium": "podium",
        "floor_a": "floor",
        "floor_b": "floor_alt",
        "crown": "crown",
        "side": "side",
        "interior": "patient_interior",
        "atrium": "atrium_interior",
        "honey_timber": "honey_timber",
        "glulam": "glulam",
        "charred_timber": "charred_timber",
        "concrete": "concrete",
        "living_wall": "living_wall",
        "green_roof": "green_roof",
        "solar_metal": "solar_metal",
        "paving": "paving",
    },
    "support": {
        "atrium": ((112, 80, 51), "wood", 14101),
        "honey_timber": ((184, 126, 70), "wood", 14111),
        "glulam": ((192, 136, 78), "wood", 14121),
        "charred_timber": ((29, 29, 28), "wood", 14131),
        "concrete": ((176, 172, 164), "stone", 14141),
        "living_wall": ((66, 93, 48), "stone", 14151),
        "green_roof": ((82, 92, 46), "stone", 14156),
        "solar_metal": ((39, 47, 56), "metal", 14161),
        "paving": ((157, 156, 151), "stone", 14171),
    },
    "support_sources": {
        "atrium": "atrium-interior-source-v1.png",
        "honey_timber": "honey-timber-material-source-v1.png",
        "glulam": "glulam-material-source-v1.png",
        "charred_timber": "charred-timber-material-source-v1.png",
        "concrete": "concrete-paving-material-source-v1.png",
        "living_wall": "living-wall-material-source-v1.png",
        "green_roof": "green-roof-material-source-v1.png",
        "solar_metal": "solar-roof-material-source-v1.png",
        "paving": "paving-material-source-v1.png",
    },
    "registered_surfaces": [
        "seventy_by_fifty_metre_four_storey_u_shaped_hospital",
        "two_patient_room_wings_and_rear_clinical_bar",
        "open_landscaped_healing_courtyard",
        "integrated_triple_height_glass_and_glulam_atrium",
        "deep_honey_glulam_public_entry_canopy",
        "three_rows_of_deep_paired_patient_room_windows",
        "physical_low_e_glazing_curtains_and_occupied_care_room_depth",
        "honey_timber_rainscreen_fins_and_clt_slab_edges",
        "charred_timber_public_and_service_plinth",
        "living_wall_strips_and_integrated_planter_ledges",
        "separate_two_bay_ambulance_and_service_arrival",
        "extensive_meadow_roof_gravel_breaks_and_skylights",
        "two_screened_mechanical_penthouses",
        "large_photovoltaic_healing_terrace_canopy",
    ],
    "registration": (
        "The canonical, rectified, aerial and rear sources lock one four-storey "
        "U-shaped hospital: two patient-room wings frame an open therapeutic "
        "courtyard, an integrated triple-height glulam atrium anchors the rear "
        "of that court, and a broad timber canopy reaches the public arrival. "
        "The rear source locks a separate two-bay ambulance arrival while the "
        "roof source fixes meadow roofs, service paths, screened plant and the "
        "photovoltaic healing-terrace canopy."
    ),
    "opening_method": (
        "Every patient-room, clinical, public and ambulance opening is a real "
        "wall void with modeled timber or charred returns, thermally broken "
        "frames, mullions, transoms, sills and separate physical panes. "
        "Patient-room and atrium source plates sit behind that glazing; the "
        "atrium contains physical glulam trees, bridges, floors and stairs."
    ),
    "generic_tiling_allowed": False,
}


def _split_cells(
    source_name: str,
    destinations: dict[str, tuple[float, float, float, float]],
) -> None:
    source = ImageOps.exif_transpose(
        Image.open(SOURCE_ROOT / source_name)
    ).convert("RGB")
    width, height = source.size
    for filename, (x0, y0, x1, y1) in destinations.items():
        crop = source.crop(
            (
                round(width * x0),
                round(height * y0),
                round(width * x1),
                round(height * y1),
            )
        )
        if filename == "green-roof-material-source-v1.png":
            # The late-summer aerial crop skewed too brown once repeated over
            # the full roof. Preserve its real sedum detail while grading it
            # toward the mixed olive/green field in the complete goalpost.
            green_grade = ImageOps.colorize(
                ImageOps.grayscale(crop),
                black="#263018",
                white="#91a458",
            )
            crop = Image.blend(crop, green_grade, 0.62)
            crop = ImageEnhance.Color(crop).enhance(1.16)
            crop = ImageEnhance.Brightness(crop).enhance(1.06)
        crop.save(SOURCE_ROOT / filename, optimize=True)


def split_source_sheets() -> None:
    """Promote clean material and occupied-depth cells for PBR derivation."""
    _split_cells("material-construction-source-v1.png", MATERIAL_CELLS)
    _split_cells("glazing-occupied-depth-source-v1.png", OCCUPIED_CELLS)


def main() -> int:
    split_source_sheets()
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
