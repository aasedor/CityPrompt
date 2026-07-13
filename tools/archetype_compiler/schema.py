"""Typed, renderer-agnostic building grammar used by the Blender compiler."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(slots=True)
class MaterialPalette:
    primary: str = "#d8d2c4"
    secondary: str = "#8a8176"
    accent: str = "#222222"
    glazing: str = "#7fa8b8"
    roof: str = "#555555"


@dataclass(slots=True)
class FacadeGrammar:
    bay_width_m: float = 3.0
    window_width_m: float = 1.8
    window_height_m: float = 1.8
    sill_height_m: float = 0.9
    frame_depth_m: float = 0.12
    balcony_probability: float = 0.0
    balcony_depth_m: float = 1.5
    storefront_ratio: float = 0.72


@dataclass(slots=True)
class BuildingGrammar:
    family: str
    archetype_id: str
    reuse_keys: list[str]
    width_m: float
    depth_m: float
    podium_height_m: float = 4.5
    floor_height_m: float = 3.2
    setback_height_m: float = 3.2
    roof_height_m: float = 1.2
    default_floors: int = 6
    has_setback: bool = True
    roof_type: str = "flat"
    facade: FacadeGrammar = field(default_factory=FacadeGrammar)
    palette: MaterialPalette = field(default_factory=MaterialPalette)
    source_style_profile: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
