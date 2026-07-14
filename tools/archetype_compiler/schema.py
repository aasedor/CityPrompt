"""Versioned, renderer-agnostic Building Grammar for the archetype compiler.

The grammar is the contract between three consumers:

1. ``compiler.py`` derives it from a real archetype export (never hand-authored),
2. ``blender_generate.py`` turns it into modular GLBs inside Blender,
3. ``validate_outputs.py`` checks the GLBs against the same numbers.

Coordinate contract (documented once, enforced everywhere):
- metres
- Z up in Blender source (glTF export converts to Y-up)
- origin at bottom centre of every module (geometry spans x/y in [-w/2, w/2] x
  [-d/2, d/2], z in [0, height])
- front facade faces negative Y in Blender
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any

SCHEMA_VERSION = 1
GENERATOR_VERSION = "0.2.0"

VALID_ROOF_TYPES = ("flat", "gabled", "mono_pitch")
VALID_BALCONY_MODES = ("none", "recessed", "projecting")
VALID_CORNER_CONDITIONS = ("midblock", "corner")

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class GrammarError(ValueError):
    """Raised when a grammar value is missing or out of range. Message names the field."""


def _require_range(name: str, value: float, lo: float, hi: float) -> None:
    if not isinstance(value, (int, float)) or not (lo <= float(value) <= hi):
        raise GrammarError(
            f"{name}={value!r} is outside the allowed range [{lo}, {hi}]. "
            f"Check the archetype's recommended dimensions or your CLI overrides."
        )


def _require_hex(name: str, value: str) -> None:
    if not isinstance(value, str) or not _HEX_RE.match(value):
        raise GrammarError(f"{name}={value!r} must be a #rrggbb hex colour")


@dataclass(slots=True)
class GrammarSource:
    """Provenance: ties the grammar back to the real catalogue entry."""

    archetype_id: str
    archetype_label: str = ""
    variant_id: str | None = None
    variant_label: str | None = None
    generation_archetype_id: str | None = None  # runtime id, e.g. `<id>_variant_0` / `<id>_front_day`
    aesthetic_category_id: str | None = None
    aesthetic_category_label: str | None = None
    development_type: str | None = None
    building_subcategory: str | None = None
    reuse_keys: list[str] = field(default_factory=list)
    generation_tags: list[str] = field(default_factory=list)
    catalog_palette: dict[str, str] = field(default_factory=dict)
    thumbnail_url: str | None = None
    exported_at: str | None = None


@dataclass(slots=True)
class Dimensions:
    width_m: float
    depth_m: float
    podium_height_m: float = 4.5
    floor_height_m: float = 3.2
    setback_height_m: float = 3.2
    roof_height_m: float = 1.2
    default_floors: int = 6
    min_floors: int = 1
    max_floors: int = 12

    def validate(self) -> None:
        _require_range("dimensions.width_m", self.width_m, 3.0, 200.0)
        _require_range("dimensions.depth_m", self.depth_m, 3.0, 200.0)
        _require_range("dimensions.podium_height_m", self.podium_height_m, 2.4, 12.0)
        _require_range("dimensions.floor_height_m", self.floor_height_m, 2.2, 6.0)
        _require_range("dimensions.setback_height_m", self.setback_height_m, 2.2, 6.0)
        _require_range("dimensions.roof_height_m", self.roof_height_m, 0.2, 8.0)
        _require_range("dimensions.min_floors", self.min_floors, 1, 100)
        _require_range("dimensions.max_floors", self.max_floors, self.min_floors, 120)
        if not (self.min_floors <= self.default_floors <= self.max_floors):
            raise GrammarError(
                f"dimensions.default_floors={self.default_floors} must lie within "
                f"[min_floors={self.min_floors}, max_floors={self.max_floors}]"
            )


@dataclass(slots=True)
class Facade:
    bay_width_m: float = 3.0
    front_bay_count: int = 6
    side_bay_count: int = 5
    window_width_ratio: float = 0.55
    window_height_ratio: float = 0.52
    sill_height_m: float = 0.9
    frame_depth_m: float = 0.12
    storefront_height_ratio: float = 0.78
    balcony_mode: str = "none"
    balcony_frequency: int = 2  # a balcony every N bays
    balcony_depth_m: float = 1.5
    vertical_rhythm: str = "regular"
    mullions: bool = True

    def validate(self) -> None:
        _require_range("facade.bay_width_m", self.bay_width_m, 1.2, 12.0)
        _require_range("facade.front_bay_count", self.front_bay_count, 1, 64)
        _require_range("facade.side_bay_count", self.side_bay_count, 1, 64)
        _require_range("facade.window_width_ratio", self.window_width_ratio, 0.1, 0.95)
        _require_range("facade.window_height_ratio", self.window_height_ratio, 0.1, 0.95)
        _require_range("facade.sill_height_m", self.sill_height_m, 0.0, 2.0)
        _require_range("facade.storefront_height_ratio", self.storefront_height_ratio, 0.3, 0.95)
        _require_range("facade.balcony_frequency", self.balcony_frequency, 1, 8)
        _require_range("facade.balcony_depth_m", self.balcony_depth_m, 0.6, 3.0)
        if self.balcony_mode not in VALID_BALCONY_MODES:
            raise GrammarError(f"facade.balcony_mode={self.balcony_mode!r} must be one of {VALID_BALCONY_MODES}")


@dataclass(slots=True)
class Massing:
    podium_inset_m: float = 0.0
    upper_floor_inset_m: float = 0.0
    setback_front_m: float = 2.0
    setback_side_m: float = 1.0
    corner_condition: str = "midblock"
    has_setback: bool = False
    has_podium_retail: bool = False

    def validate(self, width_m: float, depth_m: float) -> None:
        _require_range("massing.setback_front_m", self.setback_front_m, 0.0, depth_m / 3)
        _require_range("massing.setback_side_m", self.setback_side_m, 0.0, width_m / 3)
        if self.corner_condition not in VALID_CORNER_CONDITIONS:
            raise GrammarError(
                f"massing.corner_condition={self.corner_condition!r} must be one of {VALID_CORNER_CONDITIONS}"
            )


@dataclass(slots=True)
class Roof:
    type: str = "flat"
    parapet: bool = True
    green_roof: bool = False
    mechanical_screen: bool = True
    pitch_height_m: float = 2.4  # ridge height for gabled / high edge for mono_pitch

    def validate(self) -> None:
        if self.type not in VALID_ROOF_TYPES:
            raise GrammarError(f"roof.type={self.type!r} must be one of {VALID_ROOF_TYPES}")
        _require_range("roof.pitch_height_m", self.pitch_height_m, 0.5, 8.0)


@dataclass(slots=True)
class Material:
    name: str
    base_color: str
    roughness: float = 0.6
    metallic: float = 0.0
    source_text: str = ""  # the catalogue prose this colour was derived from

    def validate(self, slot: str) -> None:
        _require_hex(f"materials.{slot}.base_color", self.base_color)
        _require_range(f"materials.{slot}.roughness", self.roughness, 0.0, 1.0)
        _require_range(f"materials.{slot}.metallic", self.metallic, 0.0, 1.0)


def _default_material(name: str, color: str, roughness: float = 0.6, metallic: float = 0.0) -> Material:
    return Material(name=name, base_color=color, roughness=roughness, metallic=metallic)


@dataclass(slots=True)
class Materials:
    primary: Material = field(default_factory=lambda: _default_material("MAT_Facade_Primary", "#d8d2c4"))
    secondary: Material = field(default_factory=lambda: _default_material("MAT_Facade_Secondary", "#8a8176"))
    accent: Material = field(default_factory=lambda: _default_material("MAT_Accent", "#2b2e33", 0.45, 0.6))
    glass: Material = field(default_factory=lambda: _default_material("MAT_Glass", "#5f7f95", 0.08, 0.0))
    concrete: Material = field(default_factory=lambda: _default_material("MAT_Concrete", "#b5b1a8", 0.8, 0.0))
    roof: Material = field(default_factory=lambda: _default_material("MAT_Roof", "#4a4d4f", 0.85, 0.0))
    green_roof: Material = field(default_factory=lambda: _default_material("MAT_GreenRoof", "#5f7a48", 0.9, 0.0))

    def validate(self) -> None:
        for slot in ("primary", "secondary", "accent", "glass", "concrete", "roof", "green_roof"):
            getattr(self, slot).validate(slot)


@dataclass(slots=True)
class BuildingGrammar:
    family_id: str
    source: GrammarSource
    dimensions: Dimensions
    facade: Facade = field(default_factory=Facade)
    massing: Massing = field(default_factory=Massing)
    roof: Roof = field(default_factory=Roof)
    materials: Materials = field(default_factory=Materials)
    schema_version: int = SCHEMA_VERSION
    generator_version: str = GENERATOR_VERSION
    notes: list[str] = field(default_factory=list)  # human-readable derivation decisions

    def validate(self) -> None:
        if not self.family_id or not re.match(r"^[a-z0-9][a-z0-9-]*$", self.family_id):
            raise GrammarError(f"family_id={self.family_id!r} must be a non-empty kebab-case slug")
        if not self.source.archetype_id:
            raise GrammarError("source.archetype_id is required — the grammar must trace back to a real archetype")
        self.dimensions.validate()
        self.facade.validate()
        self.massing.validate(self.dimensions.width_m, self.dimensions.depth_m)
        self.roof.validate()
        self.materials.validate()
        if self.facade.bay_width_m > self.dimensions.width_m:
            raise GrammarError(
                f"facade.bay_width_m={self.facade.bay_width_m} exceeds dimensions.width_m={self.dimensions.width_m}"
            )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        # asdict on slots dataclasses keeps nesting; keep key order stable for diffs
        payload["schema_version"] = self.schema_version
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuildingGrammar":
        version = data.get("schema_version")
        if version != SCHEMA_VERSION:
            raise GrammarError(
                f"grammar schema_version={version!r} not supported by this generator "
                f"(expected {SCHEMA_VERSION}). Re-run the compiler."
            )
        materials = data.get("materials", {})

        def mat(slot: str) -> Material:
            raw = materials.get(slot, {})
            defaults = getattr(Materials(), slot)
            return Material(
                name=raw.get("name", defaults.name),
                base_color=raw.get("base_color", defaults.base_color),
                roughness=raw.get("roughness", defaults.roughness),
                metallic=raw.get("metallic", defaults.metallic),
                source_text=raw.get("source_text", ""),
            )

        grammar = cls(
            family_id=data["family_id"],
            source=GrammarSource(**data.get("source", {"archetype_id": ""})),
            dimensions=Dimensions(**data["dimensions"]),
            facade=Facade(**data.get("facade", {})),
            massing=Massing(**data.get("massing", {})),
            roof=Roof(**data.get("roof", {})),
            materials=Materials(
                primary=mat("primary"),
                secondary=mat("secondary"),
                accent=mat("accent"),
                glass=mat("glass"),
                concrete=mat("concrete"),
                roof=mat("roof"),
                green_roof=mat("green_roof"),
            ),
            generator_version=data.get("generator_version", GENERATOR_VERSION),
            notes=list(data.get("notes", [])),
        )
        grammar.validate()
        return grammar
