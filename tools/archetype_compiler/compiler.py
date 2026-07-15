"""Compile a real archetype export (export_catalog.ts output) into a Building Grammar.

Every derivation decision is recorded in ``grammar.notes`` so aesthetic review can
trace a generated building back to the catalogue prose that produced it.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

try:  # package-style import (tests) and script-style import (blender/CLI) both work
    from .schema import (
        BuildingGrammar,
        Dimensions,
        Facade,
        GrammarError,
        GrammarSource,
        Massing,
        Material,
        Materials,
        Roof,
    )
except ImportError:  # pragma: no cover - script mode
    from schema import (
        BuildingGrammar,
        Dimensions,
        Facade,
        GrammarError,
        GrammarSource,
        Massing,
        Material,
        Materials,
        Roof,
    )


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "archetype"


def _num(value: Any, default: float | None = None) -> float | None:
    if isinstance(value, (int, float)) and math.isfinite(value) and value > 0:
        return float(value)
    return default


def _strings(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _clamp(value: float, lo: float | None, hi: float | None) -> float:
    if lo is not None:
        value = max(value, lo)
    if hi is not None:
        value = min(value, hi)
    return value


# ---------------------------------------------------------------------------
# Material derivation: catalogue prose -> deterministic PBR values.
# Ordered list — the FIRST matching keyword wins, so put specific phrases first.
# ---------------------------------------------------------------------------
_MATERIAL_KEYWORDS: list[tuple[str, tuple[str, float, float]]] = [
    ("shou sugi ban", ("#2e2a26", 0.62, 0.0)),
    ("charred timber", ("#2e2a26", 0.62, 0.0)),
    ("charred black", ("#26221f", 0.62, 0.0)),
    ("black metal", ("#26282c", 0.4, 0.75)),
    ("dark metal", ("#33363b", 0.4, 0.7)),
    ("charcoal-black metal", ("#2c2e32", 0.4, 0.75)),
    ("corrugated steel", ("#7d8286", 0.5, 0.8)),
    ("corten", ("#8a4a2e", 0.7, 0.35)),
    ("weathering steel", ("#8a4a2e", 0.7, 0.35)),
    ("zinc", ("#8d939a", 0.45, 0.8)),
    ("copper", ("#9a5b3c", 0.4, 0.85)),
    ("standing seam", ("#4c5257", 0.45, 0.75)),
    ("metal panel", ("#5a5e63", 0.45, 0.7)),
    ("aluminium", ("#9aa0a6", 0.4, 0.8)),
    ("aluminum", ("#9aa0a6", 0.4, 0.8)),
    ("glulam", ("#c9a878", 0.6, 0.0)),
    ("cross-laminated", ("#cbb089", 0.6, 0.0)),
    ("clt", ("#cbb089", 0.6, 0.0)),
    ("birch", ("#dcc9a3", 0.6, 0.0)),
    ("pine", ("#d3b98a", 0.6, 0.0)),
    ("larch", ("#b08a5a", 0.65, 0.0)),
    ("cedar", ("#a87848", 0.65, 0.0)),
    ("oak", ("#a8845c", 0.65, 0.0)),
    ("natural timber", ("#b08a5a", 0.65, 0.0)),
    ("warm natural wood", ("#a97f52", 0.65, 0.0)),
    ("timber", ("#a97f52", 0.65, 0.0)),
    ("wood", ("#a97f52", 0.65, 0.0)),
    ("red brick", ("#8a4a3a", 0.85, 0.0)),
    ("redbrick", ("#8a4a3a", 0.85, 0.0)),
    ("buff brick", ("#c8a878", 0.85, 0.0)),
    ("blonde brick", ("#cfb289", 0.85, 0.0)),
    ("brick", ("#96503e", 0.85, 0.0)),
    ("white plaster", ("#e8e6e0", 0.8, 0.0)),
    ("white render", ("#e8e6e0", 0.8, 0.0)),
    ("render", ("#ddd9d0", 0.8, 0.0)),
    ("plaster", ("#e0dcd3", 0.8, 0.0)),
    ("stucco", ("#ddd5c6", 0.8, 0.0)),
    ("limestone", ("#d5cbb8", 0.75, 0.0)),
    ("sandstone", ("#c9b090", 0.78, 0.0)),
    ("granite", ("#8c8c8c", 0.6, 0.0)),
    ("natural stone", ("#9a938a", 0.72, 0.0)),
    ("stone", ("#9a938a", 0.72, 0.0)),
    ("precast", ("#bcb8af", 0.8, 0.0)),
    ("concrete", ("#b5b1a8", 0.82, 0.0)),
    ("curtain wall", ("#6e8ea4", 0.1, 0.1)),
    ("glass", ("#6e8ea4", 0.1, 0.1)),
    ("fiber cement", ("#a8a49c", 0.75, 0.0)),
    ("terracotta", ("#b06a48", 0.75, 0.0)),
]

_DEFAULT_MATERIAL_COLORS = {
    "primary": ("#c9c2b4", 0.7, 0.0),
    "secondary": ("#8a8176", 0.7, 0.0),
    "accent": ("#2b2e33", 0.45, 0.6),
}


def _derive_material(slot: str, text: str | None, mat_name: str, notes: list[str]) -> Material:
    fallback_color, fallback_rough, fallback_metal = _DEFAULT_MATERIAL_COLORS.get(slot, ("#c9c2b4", 0.7, 0.0))
    if not text:
        notes.append(f"materials.{slot}: no facadeDetail text; using neutral default {fallback_color}")
        return Material(name=mat_name, base_color=fallback_color, roughness=fallback_rough, metallic=fallback_metal)

    lowered = text.lower()
    for keyword, (color, rough, metal) in _MATERIAL_KEYWORDS:
        if keyword in lowered:
            notes.append(f"materials.{slot}: '{keyword}' in \"{text[:60]}...\" -> {color}")
            return Material(name=mat_name, base_color=color, roughness=rough, metallic=metal, source_text=text)
    notes.append(f"materials.{slot}: no keyword matched \"{text[:60]}...\"; using neutral default {fallback_color}")
    return Material(name=mat_name, base_color=fallback_color, roughness=fallback_rough, metallic=fallback_metal, source_text=text)


def _derive_glass(palette: dict[str, Any], notes: list[str]) -> Material:
    window = palette.get("window") if isinstance(palette, dict) else None
    if isinstance(window, str) and re.match(r"^#[0-9a-fA-F]{6}$", window):
        notes.append(f"materials.glass: from catalogue palette.window {window}")
        return Material(name="MAT_Glass", base_color=window, roughness=0.08, metallic=0.0, source_text="palette.window")
    notes.append("materials.glass: default cool blue-grey")
    return Material(name="MAT_Glass", base_color="#5f7f95", roughness=0.08, metallic=0.0)


# ---------------------------------------------------------------------------
# Roof / balcony / retail inference from catalogue prose + tags
# ---------------------------------------------------------------------------

def _derive_roof(roof_detail: dict[str, Any], style_profile: dict[str, Any], notes: list[str]) -> Roof:
    form_text = " ".join(
        str(v) for v in [roof_detail.get("form"), roof_detail.get("aerialAppearance"), style_profile.get("roofForm")]
        if isinstance(v, str)
    ).lower()
    material_text = str(roof_detail.get("material") or "").lower()
    features_text = str(roof_detail.get("features") or "").lower()

    # mansard/hipped are pitched silhouettes — gabled is the closest available form
    if re.search(r"\bgable|pitched|asymmetric pitch|mansard|hipped", form_text) and "flat" not in form_text.split(" or ")[0]:
        roof_type = "gabled"
    elif "mono-pitch" in form_text or "monopitch" in form_text or "shed roof" in form_text:
        # "flat or shallow mono-pitch" reads as flat-first; only pick mono when flat is absent
        roof_type = "mono_pitch" if "flat" not in form_text else "flat"
    elif re.search(r"\bgable|pitched|mansard|hipped", form_text):
        roof_type = "gabled"
    else:
        roof_type = "flat"

    green = any(k in material_text or k in features_text or k in form_text for k in ("green roof", "sedum", "meadow", "roof garden"))
    mech = "mechanical" in features_text or "mechanical" in form_text
    parapet = roof_type == "flat"
    notes.append(
        f"roof: type={roof_type} green_roof={green} mechanical_screen={mech} "
        f"from roofDetail.form=\"{str(roof_detail.get('form'))[:60]}\""
    )
    return Roof(type=roof_type, parapet=parapet, green_roof=green, mechanical_screen=mech or roof_type == "flat")


def _derive_balconies(combined: str, development_type: str, facade_text: str, notes: list[str]) -> tuple[str, int]:
    residential = "residential" in development_type or "residential" in combined or "apartment" in combined
    mentions_balcony = "balcon" in combined or "balcon" in facade_text
    if not (residential or mentions_balcony):
        notes.append("balconies: none (no residential use or balcony mention)")
        return "none", 2
    if "recessed" in facade_text or "recessed" in combined:
        mode = "recessed"
    else:
        # 'deep balconies', 'cantilevered', or unspecified residential -> projecting
        mode = "projecting"
    frequency = 1 if ("deep" in facade_text and "balcon" in facade_text) else 2
    notes.append(f"balconies: mode={mode} every {frequency} bay(s) (residential={residential})")
    return mode, frequency


def _derive_retail(development_type: str, combined: str, ground_text: str, notes: list[str]) -> bool:
    retail = (
        "mixed_use" in development_type
        or "mixed-use" in combined
        or "mixed use" in combined
        or any(k in ground_text for k in ("retail", "storefront", "shopfront", "cru", "restaurant", "commercial"))
        or any(k in combined for k in ("ground_floor_retail", "storefront"))
    )
    notes.append(f"podium retail: {retail} (developmentType={development_type or 'n/a'}, groundFloor=\"{ground_text[:50]}\")")
    return retail


def compile_archetype(
    payload: dict[str, Any],
    *,
    floors: int | None = None,
    width_m: float | None = None,
    depth_m: float | None = None,
) -> BuildingGrammar:
    """Derive a BuildingGrammar from an export_catalog.ts payload.

    Also accepts the older ``generation_style_input``-style dicts for backward
    compatibility with zone properties captured at runtime.
    """
    notes: list[str] = []

    style_input = payload.get("generationStyleInput") or payload.get("generation_style_input") or {}
    hints = style_input.get("downstreamHints") or {}
    style_profile = payload.get("styleProfile") or style_input.get("styleProfile") or {}
    dims = payload.get("dimensions") or payload  # runtime dicts carry dims at top level

    variant = payload.get("selectedVariant") or None
    variant_facade = (variant or {}).get("facadeDetail") or {}
    variant_roof = (variant or {}).get("roofDetail") or {}
    facade_detail = {**(payload.get("facadeDetail") or {}), **variant_facade}
    roof_detail = {**(payload.get("roofDetail") or {}), **variant_roof}
    palette = (variant or {}).get("palette") or payload.get("palette") or {}

    archetype_id = str(
        payload.get("archetypeId")
        or style_input.get("archetypeId")
        or payload.get("development_archetype_id")
        or ""
    )
    if not archetype_id:
        raise GrammarError("payload has no archetypeId — export it with export_catalog.ts first")

    reuse_keys = list(dict.fromkeys(
        _strings(hints.get("reuseKeys"))
        + [archetype_id, str(payload.get("aestheticCategoryId") or "")]
    ))
    reuse_keys = [key for key in reuse_keys if key]

    # --- dimensions ---------------------------------------------------------
    min_w, max_w = _num(dims.get("minWidth_m")), _num(dims.get("maxWidth_m"))
    min_d, max_d = _num(dims.get("minDepth_m")), _num(dims.get("maxDepth_m"))
    width = _num(width_m) or _num(dims.get("suggestedWidth_m")) or 24.0
    depth = _num(depth_m) or _num(dims.get("suggestedDepth_m")) or 18.0
    clamped_width = _clamp(width, min_w, max_w)
    clamped_depth = _clamp(depth, min_d, max_d)
    if clamped_width != width:
        notes.append(f"width {width}m clamped to {clamped_width}m (catalogue bounds {min_w}-{max_w}m)")
    if clamped_depth != depth:
        notes.append(f"depth {depth}m clamped to {clamped_depth}m (catalogue bounds {min_d}-{max_d}m)")
    width, depth = clamped_width, clamped_depth

    variant_min_floors = _num((variant or {}).get("minFloors"))
    variant_max_floors = _num((variant or {}).get("maxFloors"))
    min_floors = int(variant_min_floors or _num(dims.get("minFloors")) or 1)
    max_floors = int(variant_max_floors or _num(dims.get("maxFloors")) or max(min_floors, 8))
    default_floors = int(floors) if floors else int(round((min_floors + max_floors) / 2))
    if not (min_floors <= default_floors <= max_floors):
        clamped = max(min_floors, min(max_floors, default_floors))
        notes.append(f"floors {default_floors} clamped to {clamped} (catalogue range {min_floors}-{max_floors})")
        default_floors = clamped

    floor_height = (
        _num((variant or {}).get("suggestedFloorHeight"))
        or _num(dims.get("suggestedFloorHeight"))
        or 3.2
    )

    # --- semantic inference --------------------------------------------------
    development_type = str(payload.get("developmentType") or style_input.get("developmentType") or "").lower()
    tags = " ".join(_strings(payload.get("generationTags") or style_input.get("generationTags"))).lower()
    profile_text = " ".join(str(v) for v in style_profile.values() if isinstance(v, str)).lower()
    variant_desc = str((variant or {}).get("description") or "").lower()
    combined = f"{archetype_id.lower()} {development_type} {tags} {profile_text} {variant_desc}"

    ground_text = str(facade_detail.get("groundFloor") or "").lower()
    upper_text = str(facade_detail.get("upperFloors") or "").lower()

    retail = _derive_retail(development_type, combined, ground_text, notes)
    podium_height = 4.5 if retail else max(3.8, round(floor_height * 1.25, 2))
    podium_height = _clamp(podium_height, 3.6, 5.2)

    balcony_mode, balcony_frequency = _derive_balconies(combined, development_type, upper_text, notes)

    roof = _derive_roof(roof_detail, style_profile, notes)

    massing_text = f"{str(style_profile.get('massing') or '').lower()} {combined}"
    has_setback = (
        max_floors >= 6
        and any(k in massing_text for k in ("setback", "step", "terrace", "stepped", "crown"))
    ) or default_floors >= 6
    notes.append(f"setback: {has_setback} (default_floors={default_floors}, massing hints in text={any(k in massing_text for k in ('setback','step','terrace'))})")

    # bays: Nordic/tall-window styles read better slightly narrower
    bay = 3.0
    if "townhouse" in combined or "rowhouse" in combined or "row house" in combined:
        bay = 5.4  # one unit-ish per bay
    elif "tower" in combined or "curtain wall" in profile_text:
        bay = 2.4
    front_bays = max(1, round(width / bay))
    side_bays = max(1, round(depth / bay))

    window_height_ratio = 0.62 if any(k in combined for k in ("tall window", "floor-to-ceiling", "nordic", "scandinavian")) else 0.52

    grammar = BuildingGrammar(
        family_id=_slug((variant or {}).get("id") or archetype_id),
        source=GrammarSource(
            archetype_id=archetype_id,
            archetype_label=str(payload.get("archetypeLabel") or style_input.get("archetypeLabel") or archetype_id),
            variant_id=(variant or {}).get("id"),
            variant_label=(variant or {}).get("label"),
            generation_archetype_id=style_input.get("archetypeId"),
            aesthetic_category_id=payload.get("aestheticCategoryId") or style_input.get("aestheticCategoryId"),
            aesthetic_category_label=payload.get("aestheticCategoryLabel") or style_input.get("aestheticCategoryLabel"),
            development_type=development_type or None,
            building_subcategory=payload.get("buildingSubcategory") or style_input.get("buildingSubcategory"),
            reuse_keys=reuse_keys,
            generation_tags=_strings(payload.get("generationTags") or style_input.get("generationTags")),
            catalog_palette={k: v for k, v in palette.items() if isinstance(v, str)},
            thumbnail_url=payload.get("thumbnailUrl"),
            exported_at=payload.get("exportedAt"),
        ),
        dimensions=Dimensions(
            width_m=round(width, 2),
            depth_m=round(depth, 2),
            podium_height_m=round(podium_height, 2),
            floor_height_m=round(floor_height, 2),
            setback_height_m=round(floor_height, 2),
            roof_height_m=1.2 if roof.type == "flat" else roof.pitch_height_m,
            default_floors=default_floors,
            min_floors=min_floors,
            max_floors=max_floors,
        ),
        facade=Facade(
            bay_width_m=bay,
            front_bay_count=front_bays,
            side_bay_count=side_bays,
            window_height_ratio=window_height_ratio,
            balcony_mode=balcony_mode,
            balcony_frequency=balcony_frequency,
            storefront_height_ratio=0.78 if retail else 0.6,
        ),
        massing=Massing(
            has_setback=has_setback,
            has_podium_retail=retail,
            setback_front_m=min(2.0, depth / 8),
            setback_side_m=min(1.2, width / 12),
        ),
        roof=roof,
        materials=Materials(
            primary=_derive_material("primary", facade_detail.get("primaryMaterial"), "MAT_Facade_Primary", notes),
            secondary=_derive_material("secondary", facade_detail.get("secondaryMaterial"), "MAT_Facade_Secondary", notes),
            accent=_derive_material("accent", facade_detail.get("accentMaterial"), "MAT_Accent", notes),
            glass=_derive_glass(palette, notes),
            roof=_derive_material("roof", roof_detail.get("material"), "MAT_Roof", notes)
            if not roof.green_roof
            else Material(name="MAT_Roof", base_color="#4a4d4f", roughness=0.85, metallic=0.0),
        ),
        notes=notes,
    )
    grammar.validate()
    return grammar


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile an archetype export into a Building Grammar")
    parser.add_argument("input", type=Path, help="archetype-source.json from export_catalog.ts")
    parser.add_argument("output", type=Path, help="compiled grammar JSON path")
    parser.add_argument("--floors", type=int, default=None, help="override default floor count")
    parser.add_argument("--width", type=float, default=None, help="override width in metres")
    parser.add_argument("--depth", type=float, default=None, help="override depth in metres")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    grammar = compile_archetype(payload, floors=args.floors, width_m=args.width, depth_m=args.depth)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(grammar.to_dict(), indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
