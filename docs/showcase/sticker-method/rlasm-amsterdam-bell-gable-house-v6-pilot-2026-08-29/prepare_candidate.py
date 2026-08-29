from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def font(size: int):
    for candidate in (
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def record(relative: str, role: str) -> dict:
    path = ROOT / relative
    with Image.open(path) as image:
        dimensions = list(image.size)
    return {
        "role": role,
        "path": relative.replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
        "pixel_dimensions": dimensions,
    }


sources = [
    record("references/catalogue/variant_0.png", "front"),
    record("references/catalogue/variant_0_angle_60.jpg", "oblique"),
    record("references/catalogue/variant_0_angle_90.jpg", "top"),
]

board = Image.new("RGB", (1800, 1500), (8, 13, 16))
draw = ImageDraw.Draw(board)
draw.text((52, 34), "RLASM v6.1 — AMSTERDAM BELL GABLE HOUSE — LOCKED SOURCE", fill=(242, 246, 248), font=font(40))
draw.text((52, 88), "Exact catalogue variant 0 · no sibling mixing · pixels override prose", fill=(141, 186, 199), font=font(24))
placements = [
    ("references/catalogue/variant_0.png", (45, 145, 870, 760), "FRONT / STREET IDENTITY"),
    ("references/catalogue/variant_0_angle_60.jpg", (930, 145, 825, 615), "60° / MASSING + ROOF CONTACT"),
    ("references/catalogue/variant_0_angle_90.jpg", (360, 850, 1080, 560), "TRUE TOP / PLAN + RIDGE GRAPH"),
]
for relative, (x, y, width, height), label in placements:
    with Image.open(ROOT / relative).convert("RGB") as source:
        source.thumbnail((width, height), Image.Resampling.LANCZOS)
        px = x + (width - source.width) // 2
        py = y + 42 + (height - source.height) // 2
        board.paste(source, (px, py))
        draw.rectangle((x, y, x + width, y + height + 42), outline=(87, 112, 122), width=3)
        draw.text((x + 16, y + 8), label, fill=(232, 236, 238), font=font(22))
board_path = ROOT / "references/locked-source-board.png"
board.save(board_path, optimize=True)

materials = [
    ("aged red-brown Dutch brick", "references/materials/amsterdam-aged-red-brick-albedo-v1.png", "ImageGen built-in", "Exact variant-0 references; seamless narrow handmade running-bond brick; material only; no architecture or lighting."),
    ("charcoal Dutch pantile", "references/materials/amsterdam-charcoal-pantile-albedo-v1.png", "ImageGen built-in", "Exact variant-0 references; seamless weathered charcoal pantile; material only; no ridge, dormer, sky, or lighting."),
    ("warm Amsterdam sandstone", "references/materials/amsterdam-warm-sandstone-albedo-v1.png", "ImageGen built-in", "Exact variant-0 references; seamless fine-grained warm grey-beige sandstone; no carving, border, joint, or lighting."),
    ("dark stained sash timber", "references/materials/amsterdam-stained-timber-albedo-v1.png", "ImageGen built-in", "Exact variant-0 references; seamless dark warm stained hardwood; no door panel, glass, hardware, or lighting."),
]
material_records = []
for role, relative, provider, prompt_summary in materials:
    path = ROOT / relative
    with Image.open(path) as image:
        dimensions = list(image.size)
    material_records.append({
        "role": role,
        "path": relative,
        "provider": provider,
        "prompt_summary": prompt_summary,
        "bytes": path.stat().st_size,
        "sha256": digest(path),
        "pixel_dimensions": dimensions,
        "generic_fallback": False,
    })

provenance = {
    "schema": "cityprompt.rlasm.asset-provenance@1",
    "candidate": ROOT.name,
    "catalogue_sources": sources,
    "material_derivatives": material_records,
    "identity_derivatives": [],
    "whole_facade_generation_used": False,
    "prebuilt_model_used": False,
}
(ROOT / "references/asset-provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")

manifest = {
    "schema": "cityprompt.rlasm.v6.prework@1",
    "candidate": ROOT.name,
    "title": "Amsterdam Bell Gable House",
    "status": "prework",
    "method": "Reference-Locked Atomic Sticker-and-Massing (RLASM) v6.1",
    "source_contract": {
        "archetype_id": "amsterdam_bell_gable_house",
        "variant_id": "amsterdam_bell_gable_house_variant_0",
        "variant_index": 0,
        "sources": sources,
        "sibling_variant_mixing_allowed": False,
        "catalogue_pixels_are_tier_one_authority": True,
        "prebuilt_model_used": False,
    },
    "locked_reference": {
        "path": "references/locked-source-board.png",
        "bytes": board_path.stat().st_size,
        "sha256": digest(board_path),
    },
    "identity_statement": "A narrow three-storey red-brown brick Amsterdam corner canal house whose street facade rises into one continuous curved bell gable with warm sandstone coping, restrained scrolls, a central hoisting beam, tall dark timber sash windows, and a deep longitudinal charcoal pantile roof.",
    "measured_contract": {
        "dimensions_m": [8.4, 15.2, 15.31],
        "floor_datums_m": [0.36, 3.36, 6.42, 9.42],
        "eave_m": 9.55,
        "roof_ridge_m": 13.84,
        "bell_gable_finial_m": 15.31,
        "front_bay_count": 3,
        "side_bay_count": 4,
        "asymmetry": "The street facade is symmetric around the center entrance, while the roof carries one source-visible side dormer and the exposed corner side continues a four-bay residential schedule.",
        "source_conflicts": ["Catalogue family prose mentions white-painted sash and an elevated stoep, but exact variant-0 pixels show dark warm sash/door timber and a near-grade threshold; the images control."],
    },
    "plan_and_roof_graph": {
        "plan": "one closed narrow rectangular corner-house envelope",
        "roof": "two closed longitudinal pitched pantile slopes meeting at one bounded ridge; front bell gable masks the roof end; rear triangular gable closes the opposite end; one integrated right-slope dormer crosses the carrier and owns cap/flashing",
        "circulation": "center-front entrance connects to occupied residential floors through an interior stair",
    },
    "bay_schedule": {
        "front_ground": "two tall sash windows flanking one centered paneled entrance with transom",
        "front_upper": "three aligned tall sash openings on each of two full upper floors plus one central bell-gable sash",
        "sides": "four residential bays across three occupied wall levels on both side elevations",
        "rear": "three residential bays across three levels plus one central rear-gable sash",
    },
    "program_contract": {
        "visible_use": "occupied Amsterdam residential canal house",
        "required_objects": ["connected interior stair", "tables and chairs", "bookcases", "restrained warm room lighting behind optical panes"],
        "transparent_shell_may_be_empty": False,
    },
    "identity_contract": {
        "geometry_owners": ["continuous curved bell-gable silhouette", "sandstone coping and scrolls", "hoisting beam and hook", "three-by-four sash schedule", "longitudinal pantile roof", "integrated side dormer"],
        "registered_identity_roles": [],
        "identity_is_fully_constructed": True,
        "one_visual_owner_per_feature": True,
    },
    "material_contract": {
        "generic_fallbacks_forbidden": True,
        "dominant_source_conditioned_roles": [item[0] for item in materials],
        "registered_material_sheets": material_records,
        "provenance": "references/asset-provenance.json",
    },
    "opening_and_contact_contract": {
        "opening_order": ["cut carrier", "stone/brick return", "recessed timber sash", "neutral optical glass", "separately offset occupied layer", "enclosed room depth"],
        "fragile_contacts": ["bell-gable coping to brick silhouette", "hoisting beam to gable", "roof slopes to front/rear gables", "dormer cheeks to actual roof plane", "dormer cap and flashing", "threshold and foundation to grade"],
    },
    "mandatory_review_views": ["front", "front_corner", "aerial", "left_side", "right_side", "rear", "rear_side", "facade_close", "architecture_close", "glass_close", "bell_gable_close", "dormer_contact_close", "true_top", "residential_interior_close"],
    "builder_self_approval": False,
    "keeper_status": "NOT_A_KEEPER",
}
(ROOT / "prework-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

ledger = {
    "schema": "cityprompt.rlasm.discrepancy-ledger@1",
    "candidate": ROOT.name,
    "status": "prework",
    "source_conflicts": manifest["measured_contract"]["source_conflicts"],
    "finite_blockers": [],
    "iteration_history": [],
}
(ROOT / "discrepancy-ledger.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")

print(json.dumps({"candidate": ROOT.name, "sources": sources, "materials": material_records, "locked_board": manifest["locked_reference"]}, indent=2))
