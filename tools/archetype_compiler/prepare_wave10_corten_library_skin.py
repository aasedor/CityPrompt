"""Prepare the reference-locked PBR package for the corten arch library.

The source board fixes one coherent university library in four views. This
adapter extracts those views, isolates six construction materials from the
generated material plate, then delegates deterministic near/far PBR
derivation to the shared reference-skin pipeline.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_corten_library_skin.py
"""
from __future__ import annotations

import json

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


FAMILY = "corten-arch-university-library"
SOURCE_ROOT = FAMILY_ROOT / FAMILY / "textures" / "source"

# Four equal views on the render-locked 2 x 2 goalpost board.
GOALPOST_CELLS = {
    "street-hero-source-v1.png": (0.003, 0.004, 0.498, 0.496),
    "rear-corner-source-v1.png": (0.503, 0.004, 0.996, 0.496),
    "aerial-roof-source-v1.png": (0.003, 0.502, 0.498, 0.996),
    "front-elevation-source-v1.png": (0.503, 0.502, 0.996, 0.996),
}

# Clean 3 x 2 construction plate with narrow neutral gutters.
MATERIAL_CELLS = {
    "corten-material-source-v1.png": (0.002, 0.002, 0.331, 0.493),
    "board-concrete-material-source-v1.png": (0.337, 0.002, 0.665, 0.493),
    "bronze-steel-material-source-v1.png": (0.670, 0.002, 0.998, 0.493),
    "low-iron-glass-material-source-v1.png": (0.002, 0.507, 0.331, 0.998),
    "oak-material-source-v1.png": (0.337, 0.507, 0.665, 0.998),
    "precast-material-source-v1.png": (0.670, 0.507, 0.998, 0.998),
}

CONFIG = {
    "archetype_id": "university_library",
    "variant_id": "contemporary_corten_arch",
    "skin_schema": "corten-arch-university-library-skin@1",
    "elevation_source": "front-elevation-source-v1.png",
    "occupied_depth_source": "occupied-library-source-v1.png",
    "bands": {
        "facade": (0.025, 0.040, 0.975, 0.950),
        "podium": (0.075, 0.705, 0.925, 0.950),
        "floor_a": (0.135, 0.390, 0.865, 0.845),
        "floor_b": (0.155, 0.155, 0.845, 0.555),
        "crown": (0.045, 0.035, 0.955, 0.310),
        "side": (0.025, 0.060, 0.240, 0.930),
    },
    "prefixes": {
        "facade": "arched_corten_portal",
        "podium": "ceremonial_concrete_podium",
        "floor_a": "lower_honeycomb_glazing",
        "floor_b": "upper_honeycomb_glazing",
        "crown": "barrel_arch_crown",
        "side": "corten_shell_return",
        "interior": "occupied_library",
        "corten": "weathering_steel",
        "board_concrete": "board_formed_concrete",
        "bronze_steel": "dark_bronze_steel",
        "low_iron_glass": "neutral_low_iron_glass",
        "oak": "honey_oak",
        "precast": "honed_precast",
        "roof_membrane": "dark_roof_membrane",
        "vegetation": "campus_native_planting",
        "asphalt": "campus_asphalt",
    },
    "support": {
        "corten": ((143, 67, 37), "metal", 19101),
        "board_concrete": ((174, 170, 161), "stone", 19111),
        "bronze_steel": ((32, 30, 29), "metal", 19121),
        "low_iron_glass": ((92, 111, 125), "glass", 19131),
        "oak": ((145, 93, 49), "wood", 19141),
        "precast": ((172, 169, 161), "stone", 19151),
        "roof_membrane": ((48, 50, 50), "metal", 19161),
        "vegetation": ((77, 91, 47), "wood", 19171),
        "asphalt": ((62, 61, 58), "stone", 19181),
    },
    "support_sources": {
        "corten": "corten-material-source-v1.png",
        "board_concrete": "board-concrete-material-source-v1.png",
        "bronze_steel": "bronze-steel-material-source-v1.png",
        "low_iron_glass": "low-iron-glass-material-source-v1.png",
        "oak": "oak-material-source-v1.png",
        "precast": "precast-material-source-v1.png",
        "roof_membrane": "bronze-steel-material-source-v1.png",
        "vegetation": "oak-material-source-v1.png",
        "asphalt": "precast-material-source-v1.png",
    },
    "registered_surfaces": [
        "one_continuous_symmetric_weathering_steel_barrel_arch_shell",
        "thick_corten_springing_walls_and_recessed_front_glazing",
        "physical_hexagonal_dark_bronze_curtain_wall_lattice",
        "four_visible_occupied_library_floor_plates",
        "double_height_central_reading_hall",
        "broad_concrete_ceremonial_stair_with_real_landings",
        "integrated_accessible_side_ramps_and_continuous_handrails",
        "expressed_corten_panel_seams_flashings_and_crown_skylight",
        "fully_designed_side_reading_windows_and_rear_facade",
        "book_stacks_tables_balustrades_and_warm_linear_lighting",
    ],
    "registration": (
        "The canonical four-view board locks one fifty-eight-by-forty-two-metre "
        "university library: a continuous corten barrel arch rises from two "
        "thick springing walls, enclosing a recessed honeycomb curtain wall, "
        "four occupied reading levels and a broad ceremonial concrete stair."
    ),
    "opening_method": (
        "All public glazing is physical geometry. The curtain wall sits behind "
        "the corten portal with separate glass, perimeter frames, triangular "
        "mullions, four floor plates and populated library depth for parallax."
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
    """Use the hero's transparent reading-hall register as depth authority."""
    hero = ImageOps.exif_transpose(
        Image.open(SOURCE_ROOT / "street-hero-source-v1.png")
    ).convert("RGB")
    width, height = hero.size
    hero.crop(
        (
            round(width * 0.205),
            round(height * 0.135),
            round(width * 0.805),
            round(height * 0.725),
        )
    ).save(SOURCE_ROOT / "occupied-library-source-v1.png", optimize=True)


def _write_provenance() -> None:
    payload = {
        "schema": "reference-generation@1",
        "family": FAMILY,
        "archetype_id": "university_library",
        "variant_id": "contemporary_corten_arch",
        "model": "gpt-image-2",
        "generated_at": "2026-07-31",
        "status": "source-pack-complete",
        "design_lock": {
            "native_building_dimensions_m": [58.0, 42.0, 25.0],
            "barrel_arch_shells": 1,
            "occupied_storeys": 4,
            "primary_material": "variegated weathering-steel plate",
            "window_rule": "recessed low-iron curtain wall with triangular lattice",
            "front_entry": "broad real stair to recessed central glazed doors",
            "roof_rule": "continuous corten barrel with linear crown skylight",
        },
        "research": [
            {
                "title": "SSAB COR-TEN A for facades",
                "url": (
                    "https://www.ssab.com/en/brands-and-products/ssab-cor-ten/"
                    "product-offer/ssab-cor-ten-a-for-facades"
                ),
                "lesson": (
                    "Architectural weathering steel should read as thin facade "
                    "plate with expressed joints and naturally varied patina, "
                    "not as orange-painted concrete."
                ),
            },
            {
                "title": "UFGS 08 44 00 Curtain Wall and Glazed Assemblies",
                "url": "https://www.wbdg.org/FFC/DOD/UFGS/UFGS%2008%2044%2000.pdf",
                "lesson": (
                    "Curtain walls require distinct frames, infill panes, "
                    "anchors and intermediate structure; the model therefore "
                    "separates glazing from its bronze lattice and floor edges."
                ),
            },
            {
                "title": "Pilkington Optiwhite low-iron glass",
                "url": (
                    "https://www.pilkington.com/en/gbl/architectural-and-"
                    "technical-glass/product-categories/enhanced-visibility/"
                    "pilkington-optiwhite"
                ),
                "lesson": (
                    "Low-iron glass is nearly colour-neutral and highly "
                    "transmissive, so the skin preserves interior visibility "
                    "instead of using opaque blue window decals."
                ),
            },
            {
                "title": "AISC Architecturally Exposed Structural Steel",
                "url": (
                    "https://www.aisc.org/architecture-center/"
                    "architecturally-exposed-structural-steel/"
                ),
                "lesson": (
                    "The visible lattice, edge beams, braces, base plates and "
                    "connections are modeled as one legible structural system."
                ),
            },
            {
                "title": "U.S. Access Board guide to stairways",
                "url": "https://www.access-board.gov/ada/guides/chapter-5-stairways/",
                "lesson": (
                    "The ceremonial stair uses uniform closed risers, landings "
                    "and continuous handrails, with an adjacent accessible route."
                ),
            },
        ],
        "sources": [
            {
                "file": "archetype-goalpost.png",
                "source_id": "call_F1o7KQQNOMSnV8WedfsOUY5F",
                "role": "canonical_four_view_reference_board",
                "prompt_summary": (
                    "One coherent four-storey corten barrel-arch library in "
                    "front, rear, aerial and elevation views."
                ),
            },
            {
                "file": "front-elevation-source-v1.png",
                "source_id": (
                    "call_F1o7KQQNOMSnV8WedfsOUY5F:front-elevation-crop"
                ),
                "role": "shadow_neutral_front_elevation",
                "prompt_summary": (
                    "Straight-on authority for arch curvature, honeycomb "
                    "curtain wall, stair, handrails and entrance registration."
                ),
            },
            {
                "file": "rear-corner-source-v1.png",
                "source_id": "call_F1o7KQQNOMSnV8WedfsOUY5F:rear-corner-crop",
                "role": "rear_and_side_goalpost",
                "prompt_summary": (
                    "Rear oblique authority for the continuous shell, quieter "
                    "reading facade, podium and side landscape."
                ),
            },
            {
                "file": "aerial-roof-source-v1.png",
                "source_id": "call_F1o7KQQNOMSnV8WedfsOUY5F:aerial-roof-crop",
                "role": "roof_geometry_and_drainage_goalpost",
                "prompt_summary": (
                    "High aerial authority for the barrel shell, crown "
                    "skylight, panel seams and rectangular footprint."
                ),
            },
            {
                "file": "occupied-library-source-v1.png",
                "source_id": "call_F1o7KQQNOMSnV8WedfsOUY5F:occupied-depth-crop",
                "role": "window_materiality_and_occupied_depth",
                "prompt_summary": (
                    "Hero crop locking neutral low-iron glass, triangular "
                    "mullions, floor plates, stacks and warm reading depth."
                ),
            },
            {
                "file": "material-construction-source-v1.png",
                "source_id": "call_ptjkO7k3DawpCwvYniL071II",
                "role": "six_zone_pbr_material_plate",
                "prompt_summary": (
                    "Orthographic construction plate of weathering steel, "
                    "board concrete, bronze steel, glass, oak and precast."
                ),
            },
        ],
    }
    (SOURCE_ROOT / "reference-generation.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def _bind_atlases_to_registered_facade() -> None:
    """Use the authored facade zone as the public near/far atlas contract."""
    manifest_path = SOURCE_ROOT.parent / "skin_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["atlases"] = {
        lod: dict(payload["zones"]["facade"][lod])
        for lod in ("near", "far")
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    _crop_cells("archetype-goalpost.png", GOALPOST_CELLS)
    _crop_cells("material-construction-source-v1.png", MATERIAL_CELLS)
    _prepare_occupied_depth()
    _write_provenance()
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    _bind_atlases_to_registered_facade()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
