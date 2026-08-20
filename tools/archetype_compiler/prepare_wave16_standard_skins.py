"""Prepare catalogue-registered PBR packs for Wave 16 commonplace buildings.

Wave 16 deliberately reuses the source cards already shipped with CityPrompt.
The cards are immutable visual goalposts; this pass extracts only building and
material regions, derives near/far PBR channels, and records that provenance.
No external image API or API key is required.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family
from prepare_wave14_variant_skins import bind_atlas
from wave16_standard_specs import FAMILIES


REPO = Path(__file__).resolve().parents[2]


# Keep generated material studies versioned beside their registered catalogue
# goalposts.  These atlases are projection-clean construction sources, not
# replacement beauty renders.  Their quadrants deliberately exclude foliage,
# people, reflections and baked sunlight before PBR derivation.
MATERIAL_ATLAS_V2: dict[str, dict] = {
    "craftsman-brick-bungalow": {
        "file": "material-atlas-v2.png",
        "provider": "OpenAI built-in image generation",
        "prompt": (
            "Derive a clean, shadow-neutral 2x2 material study from the registered "
            "Craftsman bungalow: warm variegated running-bond red brick, pale warm "
            "textured stucco, honey-brown vertical-grain porch timber, and weathered "
            "charcoal asphalt shingles. Use orthographic true-scale material planes "
            "with neutral diffuse light; exclude perspective, scenery, openings, "
            "people, objects, text, borders, gutters and baked shadows."
        ),
        "quadrants": {
            "primary": (0, 0),
            "secondary": (1, 0),
            "ornament": (0, 1),
            "roof": (1, 1),
        },
    },
}


def _crop(image: Image.Image, bounds: tuple[float, float, float, float]) -> Image.Image:
    width, height = image.size
    x0, y0, x1, y1 = bounds
    return image.crop(
        (
            round(width * x0),
            round(height * y0),
            round(width * x1),
            round(height * y1),
        )
    )


def _bands(shape: str) -> dict[str, tuple[float, float, float, float]]:
    if shape in {"craftsman_bungalow", "edwardian_foursquare"}:
        return {
            "facade": (0.03, 0.04, 0.97, 0.98),
            "podium": (0.05, 0.60, 0.95, 0.98),
            "floor_a": (0.07, 0.39, 0.93, 0.72),
            "floor_b": (0.10, 0.20, 0.90, 0.48),
            "crown": (0.08, 0.02, 0.92, 0.31),
            "side": (0.03, 0.18, 0.32, 0.94),
        }
    if shape in {"classic_strip_mall", "tilt_up_industrial"}:
        return {
            "facade": (0.02, 0.12, 0.98, 0.94),
            "podium": (0.03, 0.58, 0.97, 0.94),
            "floor_a": (0.04, 0.38, 0.96, 0.70),
            "floor_b": (0.05, 0.22, 0.95, 0.49),
            "crown": (0.04, 0.08, 0.96, 0.34),
            "side": (0.04, 0.20, 0.28, 0.91),
        }
    return {
        "facade": (0.04, 0.03, 0.96, 0.97),
        "podium": (0.05, 0.70, 0.95, 0.97),
        "floor_a": (0.07, 0.48, 0.93, 0.75),
        "floor_b": (0.09, 0.25, 0.91, 0.52),
        "crown": (0.10, 0.03, 0.90, 0.29),
        "side": (0.04, 0.18, 0.30, 0.94),
    }


def skin_config(family: str) -> dict:
    spec = FAMILIES[family]
    prefixes = {
        "facade": f"{family}_registered_facade",
        "podium": f"{family}_registered_podium",
        "floor_a": f"{family}_registered_floor_a",
        "floor_b": f"{family}_registered_floor_b",
        "crown": f"{family}_registered_crown",
        "side": f"{family}_registered_side",
        "interior": f"{family}_occupied_depth",
    }
    support: dict[str, tuple[tuple[int, int, int], str, int]] = {}
    # The catalogue cards are excellent whole-building goalposts but include
    # vegetation, reflections and directional light.  Material zones therefore
    # use clean palette-calibrated procedural PBR instead of baking those scene
    # effects into repeatable walls.  The crops remain in provenance for review.
    support_sources: dict[str, str] = {}
    if family in MATERIAL_ATLAS_V2:
        support_sources.update(
            {
                key: f"{key}-material-source-v2.png"
                for key in MATERIAL_ATLAS_V2[family]["quadrants"]
            }
        )
    for index, (key, (description, rgb, kind)) in enumerate(spec["palette"].items()):
        prefixes[key] = f"{family}_{key}_{description.replace(' ', '_')}"
        support[key] = (rgb, kind, 16001 + index * 31 + len(family))
    return {
        "archetype_id": spec["archetype_id"],
        "variant_id": spec["variant_id"],
        "skin_schema": f"{family}-skin@1",
        "elevation_source": "elevation-source-v1.png",
        "occupied_depth_source": "occupied-depth-source-v1.png",
        "bands": _bands(spec["shape"]),
        "prefixes": prefixes,
        "support": support,
        "support_sources": support_sources,
        "registered_surfaces": [
            "catalogue_card_building_envelope",
            "physical_recessed_glazing_and_occupied_depth",
            "complete_grounded_threshold_and_entrance",
            "variant_specific_roof_and_crown",
            "wrapped_left_right_and_rear_elevations",
            "repeatable_complete_construction_bays",
        ],
        "registration": (
            f"The shipped catalogue card for {spec['label']} fixes material, "
            f"massing and identity. The deterministic geometry owns openings, "
            f"structure, roof and silhouette: {spec['design_lock']}"
        ),
        "opening_method": (
            "Every visible opening uses a separate occupied-depth backing, pane, "
            "frame, sill and surrounding return. Balconies, stairs, guards, "
            "canopies and screens remain independent true-depth geometry."
        ),
        "generic_tiling_allowed": False,
    }


def write_sources(family: str) -> None:
    spec = FAMILIES[family]
    source_file = REPO / "frontend" / "public" / spec["source_path"]
    if not source_file.is_file():
        raise FileNotFoundError(source_file)
    source_root = FAMILY_ROOT / family / "textures" / "source"
    source_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_file, source_root / "archetype-goalpost.png")
    card = ImageOps.exif_transpose(Image.open(source_file)).convert("RGB")
    elevation = _crop(card, spec["building_crop"])
    elevation = ImageOps.fit(
        elevation,
        (1600, 1200),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.55),
    )
    elevation.save(source_root / "elevation-source-v1.png", optimize=True)
    occupied = _crop(card, spec["occupied_crop"])
    occupied = ImageOps.fit(
        occupied,
        (1024, 1024),
        method=Image.Resampling.LANCZOS,
    )
    occupied.save(source_root / "occupied-depth-source-v1.png", optimize=True)
    for key, bounds in spec["material_crops"].items():
        sample = _crop(card, bounds)
        sample = ImageOps.fit(
            sample,
            (1024, 1024),
            method=Image.Resampling.LANCZOS,
        )
        sample.save(source_root / f"{key}-material-source.png", optimize=True)

    atlas_config = MATERIAL_ATLAS_V2.get(family)
    atlas_sources: list[dict] = []
    if atlas_config:
        atlas_path = source_root / atlas_config["file"]
        if not atlas_path.is_file():
            raise FileNotFoundError(atlas_path)
        atlas = ImageOps.exif_transpose(Image.open(atlas_path)).convert("RGB")
        midpoint_x = atlas.width // 2
        midpoint_y = atlas.height // 2
        for key, (column, row) in atlas_config["quadrants"].items():
            bounds = (
                column * midpoint_x,
                row * midpoint_y,
                atlas.width if column else midpoint_x,
                atlas.height if row else midpoint_y,
            )
            destination = source_root / f"{key}-material-source-v2.png"
            atlas.crop(bounds).save(destination, optimize=True)
            atlas_sources.append(
                {
                    "file": destination.name,
                    "source_id": f"imagegen:{family}:material-atlas-v2:{key}",
                    "role": f"projection_clean_{key}_construction_source",
                }
            )

    provenance = {
        "schema": "reference-generation@1",
        "family": family,
        "archetype_id": spec["archetype_id"],
        "variant_id": spec["variant_id"],
        "provider": "CityPrompt registered catalogue asset",
        "model": "pre-existing-catalogue-reference",
        "generated_at": date.today().isoformat(),
        "status": "catalogue-source-registered",
        "input_paths": [f"/{spec['source_path']}"],
        "catalogue_card_path": f"/{spec['source_path']}",
        "source_mode": "existing_catalogue_card_material_and_shape_goalpost",
        "design_lock": {
            "native_envelope_dimensions_m": list(spec["native"]),
            "occupied_storeys": spec["native_floors"],
            "variant_specific_contract": spec["design_lock"],
            "material_zones": spec["material_zones"],
            "glass_profile": spec["glass_profile"],
            "coverage_cohort": spec["cohort"],
        },
        "sources": [
            {
                "file": "archetype-goalpost.png",
                "source_id": f"catalogue:{spec['archetype_id']}:{spec['variant_id']}",
                "role": "immutable_shipped_catalogue_goalpost",
            },
            {
                "file": "elevation-source-v1.png",
                "source_id": f"catalogue-crop:{spec['variant_id']}:building",
                "role": "registered_building_crop_for_colour_and_material_scale",
            },
            {
                "file": "occupied-depth-source-v1.png",
                "source_id": f"catalogue-crop:{spec['variant_id']}:occupied",
                "role": "registered_occupied_window_depth_crop",
            },
            *(
                {
                    "file": f"{key}-material-source.png",
                    "source_id": f"catalogue-crop:{spec['variant_id']}:{key}",
                    "role": f"registered_{key}_material_crop",
                }
                for key in spec["material_crops"]
            ),
            *(
                [
                    {
                        "file": atlas_config["file"],
                        "source_id": f"imagegen:{family}:material-atlas-v2",
                        "role": "projection_clean_four_zone_material_atlas",
                        "provider": atlas_config["provider"],
                        "prompt": atlas_config["prompt"],
                    },
                    *atlas_sources,
                ]
                if atlas_config
                else []
            ),
        ],
    }
    (source_root / "reference-generation.json").write_text(
        json.dumps(provenance, indent=2) + "\n",
        encoding="utf-8",
    )


def compact_texture_lods(family: str) -> None:
    """Use an adaptive everyday-catalogue delivery texture budget.

    These buildings rely on physical parts and moderate viewing distance, so
    the 2048/1024 landmark defaults waste bandwidth without visible benefit.
    The two material-rich apartment families use a slightly tighter LOD so
    their assembled GLBs stay inside the same 9 MB delivery contract as the
    smaller houses and shops.
    """
    apartment_budget = family in {
        "new-law-brick-walkup",
        "midcentury-balcony-apartment-slab",
    }
    budgets = (("near", 832), ("far", 416)) if apartment_budget else (
        ("near", 1024),
        ("far", 512),
    )
    texture_root = FAMILY_ROOT / family / "textures" / "pbr"
    for lod, maximum in budgets:
        for path in (texture_root / lod).glob("*.png"):
            image = ImageOps.exif_transpose(Image.open(path))
            if max(image.size) <= maximum:
                continue
            image.thumbnail((maximum, maximum), Image.Resampling.LANCZOS)
            image.save(path, optimize=True)


def prepare_one(family: str) -> None:
    write_sources(family)
    prepare_family(family, skin_config(family), batch_label="wave16")
    compact_texture_lods(family)
    bind_atlas(family)
    manifest_path = FAMILY_ROOT / family / "textures" / "skin_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_model"] = "pre-existing-catalogue-reference"
    manifest["source_provider"] = "CityPrompt registered catalogue asset"
    manifest["catalogue_card_path"] = f"/{FAMILIES[family]['source_path']}"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), action="append")
    args = parser.parse_args()
    for family in args.family or sorted(FAMILIES):
        prepare_one(family)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
