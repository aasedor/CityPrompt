"""Prepare the variant-locked PBR source packs for Wave 14.

The source boards are intentionally generated outside this script with the
built-in image-generation workflow, visually reviewed, and copied into each
family's ``textures/source`` directory.  This deterministic pass registers the
views, derives near/far PBR channels, writes the elevation sheet, and records
the exact prompts and source ids needed to reproduce the approved design.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family
from wave14_variant_specs import (
    FAMILIES,
    GOALPOST_CELLS,
    MATERIAL_CELLS,
    goalpost_prompt,
    material_prompt,
)


# Filled only after each source board has been generated and reviewed.  The id
# is also embedded into reference-generation.json so a rendered family can be
# audited without relying on chat history.
SOURCE_IDS: dict[str, dict[str, str]] = {
    "art-deco-black-chrome-tower": {
        "goalpost": "exec-24648a31-ba31-4ed2-989e-d3ae4363c842",
        "material": "exec-fd5a4a91-3050-493b-a585-9d9e0b06b438",
    },
    "art-deco-polychrome-zigzag-tower": {
        "goalpost": "exec-0c5d9771-c9ad-4473-a62a-7f68909086a8",
        "material": "exec-a0644f1c-5db6-4fef-809e-7ea86101583c",
    },
    "dark-frame-clear-glass-office": {
        "goalpost": "exec-acd1527c-dfbc-4b9a-8ede-871fcfd692d0",
        "material": "exec-3d5514c4-e250-4c03-830f-f71902639c25",
    },
    "egyptian-revival-theater": {
        "goalpost": "exec-2c1d1271-9af5-423f-99d6-3beb2b188a95",
        "material": "exec-4a401fa9-ff95-494e-a78f-a7ce0faf24af",
    },
    "mass-timber-glass-office": {
        "goalpost": "exec-98730f61-010c-4a33-98ee-ba172d5f2e2c",
        "material": "exec-6952db15-812e-408a-a018-42ec58cf5374",
    },
    "mid-century-white-brise-soleil-pavilion": {
        "goalpost": "exec-9672f5fd-5031-490d-8900-674dca2f4228",
        "material": "exec-aec0ed04-57d4-48e3-9358-83f949173269",
    },
    "mid-century-wood-stone-pavilion": {
        "goalpost": "exec-1a3f2312-d542-49f6-84a5-5abdbc635b8c",
        "material": "exec-8e4f85b1-1e19-4e79-8a98-6ebc0debb7e7",
    },
    "modern-black-screen-machiya": {
        "goalpost": "exec-77afb736-e194-4ee2-b36f-e561143a2050",
        "material": "exec-9703a87a-9c65-4adf-b812-c853afa8c1e6",
    },
    "red-machiya-cafe-gallery": {
        "goalpost": "exec-f2666381-82e9-4070-b4dd-f35428c9df95",
        "material": "exec-09822413-e947-4567-97b3-04df69050ba7",
    },
    "streamline-moderne-theater": {
        "goalpost": "exec-1bc69c09-9568-45f4-b6f6-597959bceb04",
        "material": "exec-3f24a2c1-52e9-4f4f-a976-5dd4a6f0f7f5",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), action="append")
    return parser.parse_args()


def crop_cells(
    source_root: Path,
    source_name: str,
    cells: dict[str, tuple[float, float, float, float]],
) -> None:
    source = ImageOps.exif_transpose(Image.open(source_root / source_name)).convert("RGB")
    width, height = source.size
    for filename, (x0, y0, x1, y1) in cells.items():
        source.crop(
            (
                round(width * x0),
                round(height * y0),
                round(width * x1),
                round(height * y1),
            )
        ).save(source_root / filename, optimize=True)


def _bands(shape: str) -> dict[str, tuple[float, float, float, float]]:
    # Bounds are normalized within the dead-front goalpost cell.  The skin is a
    # registered underlay; all openings, screens, stairs, roofs and ornaments
    # still exist as separate true-depth geometry.
    if "theater" in shape:
        return {
            "facade": (0.08, 0.08, 0.92, 0.94),
            "podium": (0.09, 0.58, 0.91, 0.94),
            "floor_a": (0.12, 0.34, 0.88, 0.62),
            "floor_b": (0.16, 0.16, 0.84, 0.38),
            "crown": (0.26, 0.04, 0.74, 0.24),
            "side": (0.08, 0.25, 0.28, 0.92),
        }
    if "pavilion" in shape or "machiya" in shape:
        return {
            "facade": (0.06, 0.16, 0.94, 0.94),
            "podium": (0.07, 0.62, 0.93, 0.94),
            "floor_a": (0.09, 0.43, 0.91, 0.70),
            "floor_b": (0.11, 0.27, 0.89, 0.52),
            "crown": (0.12, 0.08, 0.88, 0.32),
            "side": (0.06, 0.25, 0.26, 0.91),
        }
    return {
        "facade": (0.10, 0.03, 0.90, 0.96),
        "podium": (0.10, 0.73, 0.90, 0.96),
        "floor_a": (0.12, 0.50, 0.88, 0.76),
        "floor_b": (0.18, 0.28, 0.82, 0.54),
        "crown": (0.25, 0.02, 0.75, 0.30),
        "side": (0.10, 0.25, 0.28, 0.92),
    }


def skin_config(family: str) -> dict:
    spec = FAMILIES[family]
    prefixes = {
        "facade": f"{family}_registered_front",
        "podium": f"{family}_registered_podium",
        "floor_a": f"{family}_registered_floor_a",
        "floor_b": f"{family}_registered_floor_b",
        "crown": f"{family}_registered_crown",
        "side": f"{family}_registered_side",
        "interior": f"{family}_occupied_depth",
    }
    support = {}
    support_sources = {}
    filenames = list(MATERIAL_CELLS)
    palette_keys = list(spec["palette"])
    for index, key in enumerate(palette_keys):
        description, rgb, kind = spec["palette"][key]
        prefixes[key] = f"{family}_{key}_{description.replace(' ', '_')}"
        support[key] = (rgb, kind, 14001 + index * 19 + len(family))
        support_sources[key] = filenames[index]
    return {
        "archetype_id": spec["archetype_id"],
        "variant_id": spec["variant_id"],
        "skin_schema": f"{family}-skin@1",
        "elevation_source": "front-elevation-source-v1.png",
        "occupied_depth_source": "occupied-depth-source-v1.png",
        "bands": _bands(spec["shape"]),
        "prefixes": prefixes,
        "support": support,
        "support_sources": support_sources,
        "registered_surfaces": [
            "complete_dead_front_variant_elevation",
            "variant_specific_primary_and_secondary_massing",
            "physical_recessed_glazing_with_occupied_depth",
            "complete_structural_bay_and_floor_datum_schedule",
            "integral_entrance_and_public_threshold",
            "variant_specific_roof_crown_and_ornament",
            "wrapped_left_right_and_rear_elevations",
            "semantic_repeatable_complete_middle_bays",
        ],
        "registration": (
            f"The four-view board locks one {spec['label']} with {spec['design_lock']}. "
            "The fixed landmark consumes that complete topology; LEGO fallback "
            "modules repeat only audited ordinary middle bays."
        ),
        "opening_method": (
            "Every opening is separate return, frame, physical pane and occupied-"
            "depth geometry. Screens, louvers, glass block, lattice and columns "
            "use real gaps rather than opaque facade textures."
        ),
        "generic_tiling_allowed": False,
    }


def write_provenance(family: str) -> None:
    spec = FAMILIES[family]
    source_ids = SOURCE_IDS.get(family)
    if not source_ids or not all(source_ids.get(key) for key in ("goalpost", "material")):
        raise RuntimeError(f"{family}: reviewed source ids have not been recorded")
    source_root = FAMILY_ROOT / family / "textures" / "source"
    config = skin_config(family)
    goal_id = source_ids["goalpost"]
    material_id = source_ids["material"]
    payload = {
        "schema": "reference-generation@1",
        "family": family,
        "archetype_id": spec["archetype_id"],
        "variant_id": spec["variant_id"],
        "provider": "OpenAI built-in image generation",
        "model": "gpt-image-2",
        "generated_at": date.today().isoformat(),
        "status": "source-pack-complete",
        "input_paths": [f"/archetypes/buildings/{spec['catalogue_slug']}/variant_{spec['catalogue_variant_index']}.png"],
        "design_lock": {
            "native_envelope_dimensions_m": list(spec["native"]),
            "occupied_storeys": spec["native_floors"],
            "variant_specific_contract": spec["design_lock"],
            "material_zones": spec["material_zones"],
            "glass_profile": spec["glass_profile"],
        },
        "sources": [
            {
                "file": "archetype-goalpost.png",
                "source_id": goal_id,
                "role": "canonical_four_view_variant_reference_board",
                "prompt": goalpost_prompt(family),
                "registered_surfaces": config["registered_surfaces"],
            },
            *(
                {
                    "file": filename,
                    "source_id": f"{goal_id}:{Path(filename).stem}",
                    "role": f"registered_goalpost_crop:{Path(filename).stem}",
                }
                for filename in GOALPOST_CELLS
            ),
            {
                "file": "material-construction-source-v1.png",
                "source_id": material_id,
                "role": "six_zone_shadow_neutral_variant_material_plate",
                "prompt": material_prompt(family),
            },
            *(
                {
                    "file": filename,
                    "source_id": f"{material_id}:{Path(filename).stem}",
                    "role": f"registered_material_crop:{Path(filename).stem}",
                }
                for filename in MATERIAL_CELLS
            ),
        ],
    }
    (source_root / "reference-generation.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def bind_atlas(family: str) -> None:
    manifest_path = FAMILY_ROOT / family / "textures" / "skin_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["atlases"] = {
        lod: dict(payload["zones"]["facade"][lod]) for lod in ("near", "far")
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def prepare_one(family: str) -> None:
    source_root = FAMILY_ROOT / family / "textures" / "source"
    crop_cells(source_root, "archetype-goalpost.png", GOALPOST_CELLS)
    crop_cells(source_root, "material-construction-source-v1.png", MATERIAL_CELLS)
    write_provenance(family)
    prepare_family(family, skin_config(family), batch_label="wave14")
    bind_atlas(family)


def main() -> int:
    args = parse_args()
    for family in args.family or sorted(FAMILIES):
        prepare_one(family)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
