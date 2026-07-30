"""Prepare the render-locked PBR package for the Calgary library pilot.

The pilot deliberately keeps three separate image sources:

* an orthographic facade elevation controlling the public skin;
* a shadow-neutral cedar batten swatch controlling the carved soffit; and
* an occupied four-level library plate placed behind physical glazing.

Run from the repository root:

    python tools/archetype_compiler/prepare_calgary_library_pilot_skin.py
"""
from __future__ import annotations

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
FAMILY = "calgary-central-library"
FAMILY_ROOT = REPO_ROOT / "frontend" / "public" / "families" / FAMILY
SOURCE_ROOT = FAMILY_ROOT / "textures" / "source"

BANDS = {
    "facade": (0.028, 0.052, 0.988, 0.958),
    "podium": (0.028, 0.598, 0.988, 0.958),
    "floor_a": (0.028, 0.448, 0.988, 0.635),
    "floor_b": (0.028, 0.292, 0.988, 0.482),
    "floor_c": (0.028, 0.142, 0.988, 0.330),
    "crown": (0.028, 0.052, 0.988, 0.180),
    "shell": (0.028, 0.052, 0.988, 0.720),
    "side": (0.028, 0.052, 0.988, 0.720),
}

PREFIXES = {
    "facade": "elevation",
    "podium": "podium",
    "floor_a": "floor",
    "floor_b": "floor_alt",
    "floor_c": "floor_c",
    "crown": "crown",
    "shell": "shell",
    "side": "side",
    "cedar": "cedar",
    "concrete": "concrete",
    "metal": "metal",
    "interior": "interior",
    "roof": "roof",
}


def prepare() -> None:
    elevation_path = SOURCE_ROOT / "elevation-source.png"
    cedar_path = SOURCE_ROOT / "cedar-material-source.png"
    interior_path = SOURCE_ROOT / "occupied-depth-source-v1.png"
    for path in (elevation_path, cedar_path, interior_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    elevation = ImageOps.exif_transpose(Image.open(elevation_path)).convert("RGB")
    cedar = ImageOps.exif_transpose(Image.open(cedar_path)).convert("RGB")
    interior = ImageOps.exif_transpose(Image.open(interior_path)).convert("RGB")
    elevation.save(elevation_path, optimize=True)
    cedar.save(cedar_path, optimize=True)
    interior.save(interior_path, optimize=True)
    elevation.save(FAMILY_ROOT / "elevation.jpg", quality=95, optimize=True)

    for lod, width in (("near", 2048), ("far", 1024)):
        destination = FAMILY_ROOT / "textures" / "pbr" / lod
        for zone, bounds in BANDS.items():
            derive_pbr(
                _crop(elevation, bounds),
                destination,
                PREFIXES[zone],
                width,
                seed=7101 + len(zone) * 37,
            )
        derive_pbr(
            cedar,
            destination,
            PREFIXES["cedar"],
            width,
            seed=7301,
        )
        derive_pbr(
            interior,
            destination,
            PREFIXES["interior"],
            width,
            seed=7401,
        )
        procedural_support_material(
            destination,
            PREFIXES["concrete"],
            width,
            base_rgb=(170, 168, 162),
            material_kind="stone",
            seed=7501,
        )
        procedural_support_material(
            destination,
            PREFIXES["metal"],
            width,
            base_rgb=(218, 222, 222),
            material_kind="metal",
            seed=7601,
        )
        procedural_support_material(
            destination,
            PREFIXES["roof"],
            width,
            base_rgb=(178, 183, 184),
            material_kind="metal",
            seed=7701,
        )

    zones = {
        zone: {
            "near": zone_assets(prefix, "near"),
            "far": zone_assets(prefix, "far"),
        }
        for zone, prefix in PREFIXES.items()
    }

    registered_bands = {
        "schema": "registered-facade-bands@1",
        "source": "elevation-source.png",
        "bands": BANDS,
        "notes": (
            "The fixed landmark consumes the complete elevation. The fallback "
            "stack consumes only the audited podium, three floor and crown bands."
        ),
    }
    (SOURCE_ROOT / "registered-bands.json").write_text(
        json.dumps(registered_bands, indent=2) + "\n",
        encoding="utf-8",
    )
    registered_openings = {
        "schema": "registered-openings@1",
        "source": "elevation-source.png",
        "method": (
            "The procedural triangular panel schedule is the physical opening "
            "authority. The image mask is city-LOD evidence only."
        ),
        "physical_geometry_required": True,
        "target_glazed_ratio": 0.40,
        "panel_families": [
            "clear_low_iron",
            "lightly_fritted_low_iron",
            "opaque_iridescent_aluminum",
        ],
    }
    (SOURCE_ROOT / "registered-openings.json").write_text(
        json.dumps(registered_openings, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schema": "calgary-library-pilot-skin@1",
        "family": FAMILY,
        "source": "textures/source/elevation-source.png",
        "source_model": "gpt-image-2",
        "sources": {
            "archetype_goalpost": "textures/source/archetype-goalpost.png",
            "orthographic_elevation": "textures/source/elevation-source.png",
            "cedar_material": "textures/source/cedar-material-source.png",
            "reference_underlay": "textures/source/occupied-depth-source-v1.png",
            "reference_generation": "textures/source/reference-generation.json",
            "research_sources": "textures/source/research-sources.json",
            "registered_openings": "textures/source/registered-openings.json",
            "registered_bands": "textures/source/registered-bands.json",
        },
        "registration": (
            "The Snøhetta and DIALOG exterior photographs, published plans and "
            "sections fix the almond-shaped envelope, four occupied levels, "
            "transit portal, faceted roof and carved Chinook arch. The Vitro "
            "enclosure case study fixes the 60/40 opaque-to-glazed ratio and "
            "the low-iron triple-glazed optical response."
        ),
        "reference_registration": {
            "mode": "archetype_specific",
            "source_archetype_id": "calgary_new_central_library",
            "source_variant_id": "library_original_snohetta",
            "registered_elevations": ["front", "left", "right", "rear", "roof"],
            "registered_surfaces": [
                "faceted_almond_envelope",
                "irregular_hexagonal_panel_field",
                "clear_and_fritted_low_iron_openings",
                "carved_chinook_cedar_soffit",
                "transparent_public_lobby",
                "transit_portal_and_concrete_bridge",
                "central_atrium_skylight",
            ],
            "uv_strategy": (
                "camera-registered facade atlas on the public elevation; "
                "true-scale cedar PBR on the doubly curved soffit; occupied-depth "
                "underlay immediately behind physical clear and fritted panes; "
                "related procedural panel schedules wrap all secondary elevations"
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
    (FAMILY_ROOT / "textures" / "skin_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[calgary-library-skin] {len(zones)} custom zones")


if __name__ == "__main__":
    prepare()
