"""Compile Urban Intelligence DNA / aesthetic-catalog values into geometry rules."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from schema import BuildingGrammar, FacadeGrammar, MaterialPalette


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "archetype"


def _number(source: dict[str, Any], *keys: str, default: float) -> float:
    for key in keys:
        value = source.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
    return default


def _strings(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def compile_archetype(payload: dict[str, Any]) -> BuildingGrammar:
    """Accepts either generation_style_input or a full zone-properties object."""
    style = payload.get("generation_style_input") or payload
    hints = style.get("downstreamHints") or style.get("downstream_hints") or {}
    profile = style.get("styleProfile") or style.get("style_profile") or {}
    palette_data = payload.get("development_palette") or profile.get("palette") or {}
    facade_data = payload.get("development_facade_detail") or profile.get("facade") or {}

    archetype_id = str(
        style.get("archetypeId")
        or style.get("archetype_id")
        or payload.get("development_archetype_id")
        or style.get("buildingSubcategory")
        or "generic-midrise"
    )
    reuse_keys = list(dict.fromkeys(
        _strings(hints.get("reuseKeys") or hints.get("reuse_keys"))
        + [archetype_id, str(style.get("aestheticCategoryId") or "")]
    ))
    reuse_keys = [key for key in reuse_keys if key]

    width = _number(payload, "suggestedWidth_m", "suggested_width_m", "width_m", default=24.0)
    depth = _number(payload, "suggestedDepth_m", "suggested_depth_m", "depth_m", default=18.0)
    min_floors = int(_number(payload, "minFloors", "min_floors", default=4))
    max_floors = int(_number(payload, "maxFloors", "max_floors", default=max(6, min_floors)))
    floors = max(min_floors, min(max_floors, int(round((min_floors + max_floors) / 2))))

    tags = " ".join(_strings(style.get("generationTags") or style.get("generation_tags"))).lower()
    description = " ".join(str(v) for v in profile.values() if isinstance(v, str)).lower()
    combined = f"{archetype_id} {tags} {description}"

    balcony_probability = 0.45 if any(k in combined for k in ("balcony", "residential", "apartment")) else 0.0
    roof_type = "gabled" if any(k in combined for k in ("gable", "pitched", "traditional")) else "flat"
    has_setback = any(k in combined for k in ("setback", "terrace", "midrise", "mixed-use", "mixed use"))

    return BuildingGrammar(
        family=_slug(archetype_id),
        archetype_id=archetype_id,
        reuse_keys=reuse_keys,
        width_m=width,
        depth_m=depth,
        default_floors=floors,
        has_setback=has_setback,
        roof_type=roof_type,
        facade=FacadeGrammar(
            bay_width_m=_number(facade_data, "bayWidth_m", "bay_width_m", default=3.0),
            window_width_m=_number(facade_data, "windowWidth_m", "window_width_m", default=1.8),
            window_height_m=_number(facade_data, "windowHeight_m", "window_height_m", default=1.8),
            balcony_probability=balcony_probability,
        ),
        palette=MaterialPalette(
            primary=str(palette_data.get("primary") or "#d8d2c4"),
            secondary=str(palette_data.get("secondary") or "#8a8176"),
            accent=str(palette_data.get("accent") or "#222222"),
            glazing=str(palette_data.get("glazing") or "#7fa8b8"),
            roof=str(palette_data.get("roof") or "#555555"),
        ),
        source_style_profile=profile if isinstance(profile, dict) else {},
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Urban DNA/generation_style_input JSON")
    parser.add_argument("output", type=Path, help="Compiled building grammar JSON")
    args = parser.parse_args()

    grammar = compile_archetype(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(grammar.to_dict(), indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
