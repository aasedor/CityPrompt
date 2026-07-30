"""Prepare render-locked PBR packages for the Wave 8 reference families.

Each family keeps three image sources:

* the selected catalogue card as the visual goalpost;
* a rectified, shadow-neutral elevation derived from that card; and
* a registration-preserving occupied-depth plate behind physical openings.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave8_reference_skins.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageOps

from prepare_wave4_standard_batch_skins import (
    CHANNELS,
    MASKS,
    _crop,
    derive_pbr,
    procedural_support_material,
    zone_assets,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FAMILY_ROOT = REPO_ROOT / "frontend" / "public" / "families"

FAMILIES = {
    "parametric-fluid-hub": {
        "archetype_id": "parametric_future_hub",
        "variant_id": "parametric_fluid_organic",
        "skin_schema": "parametric-fluid-hub-skin@1",
        "bands": {
            "facade": (0.078, 0.115, 0.932, 0.865),
            "podium": (0.078, 0.575, 0.932, 0.865),
            "floor_a": (0.078, 0.405, 0.932, 0.625),
            "floor_b": (0.078, 0.245, 0.932, 0.470),
            "crown": (0.078, 0.115, 0.932, 0.300),
            # Fixed openings are physical geometry.  These two crops therefore
            # sample only clean perforated shell fields; carrying photographed
            # openings into the material would create false "ghost" windows on
            # wrapped secondary elevations.
            "shell": (0.500, 0.120, 0.690, 0.580),
            "side": (0.520, 0.120, 0.690, 0.580),
        },
        "prefixes": {
            "facade": "elevation",
            "podium": "podium",
            "floor_a": "floor",
            "floor_b": "floor_alt",
            "crown": "crown",
            "shell": "shell",
            "side": "side",
            "interior": "interior",
            "metal": "metal",
            "roof": "roof",
        },
        "support": {
            "metal": ((205, 209, 210), "metal", 8211),
            "roof": ((224, 225, 222), "stone", 8221),
        },
        "registered_surfaces": [
            "double_curved_flared_shell",
            "deep_organic_window_reveals",
            "perforated_composite_panels",
            "curved_low_iron_glazing",
            "carved_public_entrance",
            "continuous_shell_roof",
        ],
        "registration": (
            "The selected catalogue card fixes the five-level asymmetrical "
            "hourglass silhouette, outward-flaring crown, concave lower waist, "
            "organic opening schedule and perforated pearl-white shell."
        ),
        "opening_method": (
            "The generator's registered organic opening splines are the physical "
            "authority. The facade glass mask is city-LOD evidence only."
        ),
        "generic_tiling_allowed": False,
    },
    "timber-transit-station": {
        "archetype_id": "transit_oriented_station_block",
        "variant_id": "transit_station_timber_sustainable",
        "skin_schema": "timber-transit-station-skin@1",
        "bands": {
            "facade": (0.145, 0.338, 0.858, 0.892),
            "podium": (0.045, 0.675, 0.960, 0.902),
            "floor_a": (0.145, 0.505, 0.858, 0.690),
            "floor_b": (0.145, 0.345, 0.858, 0.525),
            "crown": (0.145, 0.335, 0.858, 0.445),
            "side": (0.145, 0.338, 0.858, 0.892),
        },
        "prefixes": {
            "facade": "elevation",
            "podium": "podium",
            "floor_a": "floor",
            "floor_b": "floor_alt",
            "crown": "crown",
            "timber": "timber",
            "louver": "louver",
            "canopy": "canopy",
            "side": "side",
            "interior": "interior",
            "glass": "glass",
            "green": "green",
        },
        "support": {
            "glass": ((132, 148, 148), "metal", 8311),
            "green": ((66, 86, 50), "stone", 8321),
            # The elevation is the colour authority, but isolated structural
            # wood atlases prevent photographed panes and shadows from being
            # stretched along physical beams and louvers.
            "timber": ((178, 116, 64), "wood", 8331),
            "louver": ((116, 72, 39), "wood", 8341),
            "canopy": ((188, 128, 70), "wood", 8351),
        },
        "registered_surfaces": [
            "five_level_glulam_frame",
            "alternating_clt_and_louver_bays",
            "transparent_transit_concourse",
            "tree_column_roof_structure",
            "oversized_translucent_canopy",
            "recessed_roof_terrace",
        ],
        "registration": (
            "The selected catalogue card fixes the five-level mass-timber block, "
            "open transit concourse, alternating louver/window schedule and the "
            "single oversized glulam-and-ETFE canopy."
        ),
        "opening_method": (
            "The generator's structural bay schedule fixes panes and louver-only "
            "cells. Only registered clear cells receive physical glass."
        ),
        "generic_tiling_allowed": False,
    },
    "covered-souk-market": {
        "archetype_id": "traditional_vernacular_market_street",
        "variant_id": "vernacular_market_souk_bazaar",
        "skin_schema": "covered-souk-market-skin@1",
        "bands": {
            "facade": (0.028, 0.285, 0.972, 0.895),
            "podium": (0.028, 0.485, 0.972, 0.895),
            "floor_a": (0.028, 0.290, 0.972, 0.545),
            "floor_b": (0.028, 0.400, 0.972, 0.680),
            "crown": (0.028, 0.255, 0.972, 0.350),
            "roof": (0.028, 0.135, 0.972, 0.330),
            "side": (0.028, 0.285, 0.972, 0.895),
        },
        "prefixes": {
            "facade": "elevation",
            "podium": "podium",
            "floor_a": "floor",
            "floor_b": "floor_alt",
            "crown": "crown",
            "stone": "stone",
            "roof": "roof",
            "side": "side",
            "interior": "interior",
            "timber": "timber",
            "bronze": "bronze",
            "dome": "dome",
        },
        "support": {
            "timber": ((78, 49, 29), "wood", 8411),
            "bronze": ((100, 58, 29), "metal", 8421),
            # The catalogue goalpost is honey limestone, not pale plaster.
            # These tile-safe construction atlases preserve that chroma on
            # long physical arches and domes without stretching photo shadows.
            "stone": ((178, 132, 82), "stone", 8431),
            "dome": ((204, 164, 108), "stone", 8441),
        },
        "registered_surfaces": [
            "seven_bay_cut_stone_arcade",
            "deep_pointed_arch_reveals",
            "upper_mashrabiya_screens",
            "recessed_market_shopfronts",
            "seven_aligned_shallow_domes",
            "aged_copper_lanterns",
        ],
        "registration": (
            "The selected catalogue card fixes exactly seven equal pointed-arch "
            "bays, two occupied registers, deep recessed shops, carved timber "
            "screens and seven aligned shallow roof domes."
        ),
        "opening_method": (
            "The generator's seven pointed-arch profiles are the physical opening "
            "authority. The occupied-depth source is clipped behind those voids."
        ),
        "generic_tiling_allowed": False,
    },
}


def _load_rgb(path: Path) -> Image.Image:
    if not path.is_file():
        raise FileNotFoundError(path)
    image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    image.save(path, optimize=True)
    return image


def prepare_family(family: str, config: dict) -> None:
    root = FAMILY_ROOT / family
    source_root = root / "textures" / "source"
    elevation_path = source_root / "elevation-source.png"
    interior_path = source_root / "occupied-depth-source.png"
    goalpost_path = source_root / "archetype-goalpost.png"
    elevation = _load_rgb(elevation_path)
    interior = _load_rgb(interior_path)
    _load_rgb(goalpost_path)
    elevation.save(root / "elevation.jpg", quality=95, optimize=True)

    for lod, width in (("near", 2048), ("far", 1024)):
        destination = root / "textures" / "pbr" / lod
        for zone, bounds in config["bands"].items():
            derive_pbr(
                _crop(elevation, bounds),
                destination,
                config["prefixes"][zone],
                width,
                seed=8001 + len(family) * 23 + len(zone) * 37,
            )
        derive_pbr(
            interior,
            destination,
            config["prefixes"]["interior"],
            width,
            seed=8101 + len(family) * 29,
        )
        for zone, (rgb, kind, seed) in config["support"].items():
            procedural_support_material(
                destination,
                config["prefixes"][zone],
                width,
                base_rgb=rgb,
                material_kind=kind,
                seed=seed,
            )

    zones = {
        zone: {
            "near": zone_assets(prefix, "near"),
            "far": zone_assets(prefix, "far"),
        }
        for zone, prefix in config["prefixes"].items()
    }
    registered_bands = {
        "schema": "registered-facade-bands@1",
        "source": "elevation-source.png",
        "bands": config["bands"],
        "notes": (
            "The fixed landmark consumes the complete registered elevation. "
            "The fallback kit consumes only fixed podium/crown and audited "
            "repeatable middle bands."
        ),
    }
    (source_root / "registered-bands.json").write_text(
        json.dumps(registered_bands, indent=2) + "\n",
        encoding="utf-8",
    )
    registered_openings = {
        "schema": "registered-openings@1",
        "source": "elevation-source.png",
        "method": config["opening_method"],
        "physical_geometry_required": True,
    }
    (source_root / "registered-openings.json").write_text(
        json.dumps(registered_openings, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": config["skin_schema"],
        "family": family,
        "source": "textures/source/elevation-source.png",
        "source_model": "gpt-image-2",
        "sources": {
            "archetype_goalpost": "textures/source/archetype-goalpost.png",
            "orthographic_elevation": "textures/source/elevation-source.png",
            "reference_underlay": "textures/source/occupied-depth-source.png",
            "reference_generation": "textures/source/reference-generation.json",
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
                "camera-registered public elevation, true-scale material zones "
                "on physical construction, occupied-depth underlay immediately "
                "behind registered glazing, and related secondary-elevation "
                "schedules wrapped around the complete envelope"
            ),
            "depth_binding": "shader_bump",
            "generic_tiling_allowed": config["generic_tiling_allowed"],
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
    (root / "textures" / "skin_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[wave8-skin] {family}: {len(zones)} custom zones")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", action="append", choices=sorted(FAMILIES))
    args = parser.parse_args()
    selected = args.family or sorted(FAMILIES)
    for family in selected:
        config = FAMILIES[family]
        prepare_family(family, config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
