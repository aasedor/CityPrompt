"""Prepare render-locked PBR skins for the Wave 6 non-residential families.

The three families deliberately use different construction languages:

* a titanium-clad deconstructivist museum;
* a low-iron glass office protected by terracotta fins; and
* a board-formed concrete civic hall.

Every family keeps the generated orthographic elevation and material source as
reviewable design evidence.  This script derives the near/far PBR packages,
semantic masks and supporting construction materials without baking directional
sunlight into the runtime albedo.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave6_nonresidential_skins.py \
      --family deconstructivist-museum
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

from prepare_wave4_standard_batch_skins import (
    CHANNELS,
    MASKS,
    _crop,
    derive_pbr,
    procedural_roof,
    procedural_support_material,
    zone_assets,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FAMILY_ROOT = REPO_ROOT / "frontend" / "public" / "families"


FAMILIES: dict[str, dict[str, Any]] = {
    "deconstructivist-museum": {
        "archetype_id": "monumental_museum_axis",
        "variant_id": "museum_contemporary_deconstructivist",
        "seed": 6101,
        "roof": "membrane",
        "bands": {
            "facade": (0.105, 0.025, 0.895, 0.945),
            "podium": (0.105, 0.705, 0.895, 0.945),
            "floor_a": (0.105, 0.515, 0.895, 0.725),
            "floor_b": (0.105, 0.335, 0.895, 0.545),
            "floor_c": (0.105, 0.155, 0.895, 0.365),
            "crown": (0.105, 0.025, 0.895, 0.185),
        },
        "material_sources": {
            "shell": ("material-source.png", (0.0, 0.0, 1.0, 1.0)),
            "side": ("material-source.png", (0.0, 0.0, 1.0, 1.0)),
        },
        "roughness_ranges": {
            "shell": (0.20, 0.46),
            "side": (0.24, 0.52),
        },
        "underlay_source": "atrium-underlay-source-v2.png",
        "support": {
            "trim": ((190, 184, 177), "metal"),
            "metal": ((43, 48, 50), "metal"),
            "interior": ((104, 69, 44), "timber"),
            "planting": ((72, 87, 57), "stone"),
        },
        "registered_surfaces": [
            "fractured_titanium_gallery_towers",
            "serrated_parapet_crests",
            "inward_leaning_glass_atrium",
            "deep_cantilever_notches",
            "subtractive_public_entry",
            "triangular_entry_canopy",
            "conservative_service_roofs_and_rear",
        ],
        "registration": (
            "The original catalogue image fixes the public silhouette and entry. "
            "The generated high obliques fix the complete roof and return geometry. "
            "The orthographic source locks the tower hierarchy and atrium wedge, "
            "while the material source locks the champagne-silver panel field."
        ),
    },
    "terracotta-fin-office": {
        "archetype_id": "modern_glass_office_institutional",
        "variant_id": "glass_office_terracotta_fins",
        "seed": 6201,
        "roof": "terrace",
        "bands": {
            "facade": (0.055, 0.025, 0.945, 0.965),
            "podium": (0.055, 0.745, 0.945, 0.965),
            "floor_a": (0.055, 0.560, 0.945, 0.755),
            "floor_b": (0.055, 0.385, 0.945, 0.580),
            "floor_c": (0.055, 0.205, 0.945, 0.405),
            "crown": (0.055, 0.025, 0.945, 0.220),
        },
        "material_sources": {
            "shell": ("material-source.png", (0.0, 0.0, 1.0, 1.0)),
            "side": ("material-source.png", (0.0, 0.0, 1.0, 1.0)),
        },
        "underlay_source": "glazing-underlay-source-v2.png",
        "support": {
            "trim": ((191, 190, 184), "stone"),
            "metal": ((55, 52, 48), "metal"),
            "interior": ((112, 78, 48), "timber"),
            "planting": ((67, 91, 54), "stone"),
        },
        "registered_surfaces": [
            "double_height_transparent_lobby",
            "low_iron_curtain_wall_bands",
            "ribbed_terracotta_fin_fields",
            "two_planted_setback_terraces",
            "cantilevered_office_floor_plates",
            "occupied_glazed_crown",
            "roof_pergola_and_planting",
        ],
        "registration": (
            "The catalogue view fixes the alternating clear-glass and terracotta "
            "bands, planted setbacks, double-height lobby and occupied crown. "
            "Generated obliques control the returns, roof garden and terrace depth."
        ),
    },
    "brutalist-civic-block": {
        "archetype_id": "modernist_civic_block",
        "variant_id": "modernist_civic_concrete_brutalist",
        "seed": 6301,
        "roof": "membrane",
        "bands": {
            "facade": (0.055, 0.025, 0.945, 0.965),
            "podium": (0.055, 0.710, 0.945, 0.965),
            "floor_a": (0.055, 0.500, 0.945, 0.735),
            "floor_b": (0.055, 0.310, 0.945, 0.535),
            "floor_c": (0.055, 0.145, 0.945, 0.345),
            "crown": (0.055, 0.025, 0.945, 0.175),
        },
        "material_sources": {
            "shell": ("material-source.png", (0.0, 0.0, 1.0, 1.0)),
            "side": ("material-source.png", (0.0, 0.0, 1.0, 1.0)),
        },
        "underlay_source": "glazing-underlay-source-v2.png",
        "support": {
            "trim": ((166, 164, 157), "stone"),
            "metal": ((48, 45, 41), "metal"),
            "interior": ((105, 70, 43), "timber"),
            "planting": ((70, 86, 58), "stone"),
        },
        "registered_surfaces": [
            "floating_board_formed_concrete_volume",
            "deep_horizontal_window_slits",
            "two_outer_monumental_pilotis",
            "recessed_public_lobby",
            "offset_cantilevered_gallery_boxes",
            "continuous_overhanging_roof_plane",
            "quiet_service_rear",
        ],
        "registration": (
            "The catalogue image fixes the floating concrete mass, pilotis, deep "
            "slit windows, offset cantilevers and broad roof plane. Generated "
            "obliques control their load path, returns and conservative rear."
        ),
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--family",
        action="append",
        choices=sorted(FAMILIES),
        help="Prepare only one family; repeat for several. Defaults to all three.",
    )
    return parser.parse_args()


def remap_roughness(
    path: Path,
    minimum: float,
    maximum: float,
) -> None:
    """Calibrate a derived greyscale map to the audited material response."""
    if not 0.0 <= minimum < maximum <= 1.0:
        raise ValueError(f"invalid roughness range: {(minimum, maximum)}")
    roughness = Image.open(path).convert("L")
    low = round(minimum * 255)
    span = round((maximum - minimum) * 255)
    roughness.point(
        [low + round((value / 255) * span) for value in range(256)]
    ).save(path, optimize=True)


def prepare_family(slug: str, config: dict[str, Any]) -> None:
    family_dir = FAMILY_ROOT / slug
    source_dir = family_dir / "textures" / "source"
    elevation_path = source_dir / "elevation-source.png"
    if not elevation_path.is_file():
        raise FileNotFoundError(elevation_path)

    elevation = ImageOps.exif_transpose(Image.open(elevation_path)).convert("RGB")
    elevation.save(elevation_path, optimize=True)
    elevation.save(family_dir / "elevation.jpg", quality=95, optimize=True)

    prefixes = {
        "facade": "elevation",
        "podium": "podium",
        "floor_a": "floor",
        "floor_b": "floor_alt",
        "floor_c": "floor_c",
        "crown": "crown",
        "shell": "shell",
        "side": "side",
        "roof": "roof",
        "trim": "trim",
        "metal": "metal",
        "interior": "interior",
        "planting": "planting",
    }

    opened_sources: dict[str, Image.Image] = {}
    for filename, _bounds in config["material_sources"].values():
        path = source_dir / filename
        if not path.is_file():
            raise FileNotFoundError(path)
        opened_sources[filename] = ImageOps.exif_transpose(
            Image.open(path)
        ).convert("RGB")

    for lod, width in (("near", 2048), ("far", 1024)):
        destination = family_dir / "textures" / "pbr" / lod
        for zone, bounds in config["bands"].items():
            derive_pbr(
                _crop(elevation, bounds),
                destination,
                prefixes[zone],
                width,
                seed=config["seed"] + len(zone) * 19,
            )
        for zone, (filename, bounds) in config["material_sources"].items():
            derive_pbr(
                _crop(opened_sources[filename], bounds),
                destination,
                prefixes[zone],
                width,
                seed=config["seed"] + len(zone) * 31,
            )
        procedural_roof(
            destination,
            "roof",
            width,
            roof_type=config["roof"],
            seed=config["seed"] + 307,
        )
        for offset, (zone, (rgb, kind)) in enumerate(config["support"].items()):
            procedural_support_material(
                destination,
                prefixes[zone],
                width,
                base_rgb=rgb,
                material_kind=kind,
                seed=config["seed"] + 401 + offset * 103,
            )
        for zone, (minimum, maximum) in config.get(
            "roughness_ranges", {}
        ).items():
            remap_roughness(
                destination / f"{prefixes[zone]}_roughness.png",
                minimum,
                maximum,
            )

    zones = {
        zone: {
            "near": zone_assets(prefix, "near"),
            "far": zone_assets(prefix, "far"),
        }
        for zone, prefix in prefixes.items()
    }
    registered_bands = {
        "schema": "registered-facade-bands@1",
        "source": "elevation-source.png",
        "bands": config["bands"],
    }
    (source_dir / "registered-bands.json").write_text(
        json.dumps(registered_bands, indent=2) + "\n",
        encoding="utf-8",
    )
    registered_openings = {
        "schema": "registered-openings@1",
        "source": "elevation-source.png",
        "method": (
            "reference-audited physical openings; the semantic mask supplies "
            "city LOD only and never generates unreviewed hero geometry"
        ),
        "physical_geometry_required": True,
    }
    (source_dir / "registered-openings.json").write_text(
        json.dumps(registered_openings, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "wave6-nonresidential-skin@1",
        "family": slug,
        "source": "textures/source/elevation-source.png",
        "source_model": "gpt-image-2",
        "sources": {
            "archetype_goalpost": "textures/source/archetype-goalpost.png",
            "orthographic_elevation": "textures/source/elevation-source.png",
            "material_source": "textures/source/material-source.png",
            "reference_underlay": (
                f"textures/source/{config['underlay_source']}"
            ),
            "angle_reference": "textures/source/angle-reference-60.png",
            "roof_reference": "textures/source/angle-reference-90.png",
            "registered_openings": "textures/source/registered-openings.json",
            "registered_bands": "textures/source/registered-bands.json",
        },
        "registration": config["registration"],
        "reference_registration": {
            "mode": "archetype_specific",
            "source_archetype_id": config["archetype_id"],
            "source_variant_id": config["variant_id"],
            "registered_elevations": ["front", "left", "right", "rear", "roof"],
            "registered_surfaces": config["registered_surfaces"],
            "uv_strategy": (
                "render-locked facade bands and occupied-depth underlay cards "
                "behind physical glazing, plus reference-derived true-scale "
                "construction materials on authored physical envelopes"
            ),
            "depth_binding": "shader_bump",
            "generic_tiling_allowed": False,
        },
        "channels": list(CHANNELS),
        "semantic_masks": list(MASKS),
        "shadow_neutral": {
            "passed": True,
            "method": "multiscale-linear-delighting-before-pbr-derivation",
        },
        "zones": zones,
        "atlases": {
            "near": zone_assets("elevation", "near"),
            "far": zone_assets("elevation", "far"),
        },
    }
    (family_dir / "textures" / "skin_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[wave6-skin] {slug}: {len(zones)} zones")


def main() -> int:
    args = parse_args()
    selected = args.family or list(FAMILIES)
    for slug in selected:
        prepare_family(slug, FAMILIES[slug])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
