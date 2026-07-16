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

SCHEMA_VERSION = 3
GENERATOR_VERSION = "0.5.0"

VALID_ROOF_TYPES = ("flat", "gabled", "mono_pitch")
VALID_BALCONY_MODES = ("none", "recessed", "projecting")
VALID_CORNER_CONDITIONS = ("midblock", "corner")
VALID_FACADE_SYSTEMS = ("regular", "timber_grid", "punched_render", "brick_bays", "stone_frame")
VALID_BALCONY_GUARDS = ("solid", "metal", "glass", "planter")
VALID_ENTRANCE_TYPES = ("canopy", "portal", "recessed", "arched", "colonnade")
VALID_FACADE_ZONE_KINDS = ("base", "middle", "upper", "crown")
VALID_OPENING_KINDS = ("window", "door", "curtain_wall", "juliet_door", "shopfront")
VALID_ATTACHMENT_KINDS = (
    "balcony", "juliet", "planter", "oriel", "canopy",
    "portal", "arch", "colonnade", "screen", "cornice",
)

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
    system: str = "regular"
    window_recess_m: float = 0.18
    panel_projection_m: float = 0.08
    material_bay_frequency: int = 3
    feature_bay_frequency: int = 3
    planter_frequency: int = 0
    balcony_guard: str = "metal"
    entrance_type: str = "canopy"
    top_band: bool = True

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
        _require_range("facade.window_recess_m", self.window_recess_m, 0.02, 0.6)
        _require_range("facade.panel_projection_m", self.panel_projection_m, 0.0, 0.5)
        _require_range("facade.material_bay_frequency", self.material_bay_frequency, 1, 8)
        _require_range("facade.feature_bay_frequency", self.feature_bay_frequency, 1, 8)
        _require_range("facade.planter_frequency", self.planter_frequency, 0, 8)
        if self.balcony_mode not in VALID_BALCONY_MODES:
            raise GrammarError(f"facade.balcony_mode={self.balcony_mode!r} must be one of {VALID_BALCONY_MODES}")
        if self.system not in VALID_FACADE_SYSTEMS:
            raise GrammarError(f"facade.system={self.system!r} must be one of {VALID_FACADE_SYSTEMS}")
        if self.balcony_guard not in VALID_BALCONY_GUARDS:
            raise GrammarError(f"facade.balcony_guard={self.balcony_guard!r} must be one of {VALID_BALCONY_GUARDS}")
        if self.entrance_type not in VALID_ENTRANCE_TYPES:
            raise GrammarError(f"facade.entrance_type={self.entrance_type!r} must be one of {VALID_ENTRANCE_TYPES}")


@dataclass(slots=True)
class OpeningSpec:
    id: str
    kind: str = "window"
    width_ratio: float = 0.55
    height_ratio: float = 0.62
    sill_m: float = 0.8
    reveal_depth_m: float = 0.18
    frame_profile_id: str = "standard"
    mullion_pattern: str = "single"

    def validate(self) -> None:
        if not self.id:
            raise GrammarError("facade_graph.openings[].id is required")
        if self.kind not in VALID_OPENING_KINDS:
            raise GrammarError(f"opening {self.id!r} kind={self.kind!r} must be one of {VALID_OPENING_KINDS}")
        _require_range(f"opening.{self.id}.width_ratio", self.width_ratio, 0.1, 0.95)
        _require_range(f"opening.{self.id}.height_ratio", self.height_ratio, 0.1, 0.95)
        _require_range(f"opening.{self.id}.sill_m", self.sill_m, 0.0, 2.0)
        _require_range(f"opening.{self.id}.reveal_depth_m", self.reveal_depth_m, 0.02, 0.8)


@dataclass(slots=True)
class AttachmentSpec:
    id: str
    kind: str
    geometry_profile_id: str
    material_slots: list[str] = field(default_factory=list)
    anchor: str = "bay"
    width_bays: int = 1
    height_floors: int = 1

    def validate(self) -> None:
        if not self.id or not self.geometry_profile_id:
            raise GrammarError("facade_graph.attachments require id and geometry_profile_id")
        if self.kind not in VALID_ATTACHMENT_KINDS:
            raise GrammarError(f"attachment {self.id!r} kind={self.kind!r} must be one of {VALID_ATTACHMENT_KINDS}")
        _require_range(f"attachment.{self.id}.width_bays", self.width_bays, 1, 8)
        _require_range(f"attachment.{self.id}.height_floors", self.height_floors, 1, 40)


@dataclass(slots=True)
class BaySpec:
    id: str
    opening_id: str | None = None
    material_slot: str = "primary"
    projection_m: float = 0.0
    attachment_ids: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.id:
            raise GrammarError("facade_graph.bays[].id is required")
        _require_range(f"bay.{self.id}.projection_m", self.projection_m, 0.0, 2.5)


@dataclass(slots=True)
class FloorVariant:
    key: str
    bay_sequence: list[str]
    facade_zone: str = "middle"
    left_corner_id: str = "standard"
    right_corner_id: str = "standard"
    slab_edge_profile_id: str = "standard"
    allowed_levels: list[int] | None = None
    repeat_every: int | None = None

    def validate(self) -> None:
        if not self.key or not self.bay_sequence:
            raise GrammarError("facade_graph.floor_variants require key and non-empty bay_sequence")
        if self.facade_zone not in VALID_FACADE_ZONE_KINDS:
            raise GrammarError(
                f"floor variant {self.key!r} facade_zone={self.facade_zone!r} "
                f"must be one of {VALID_FACADE_ZONE_KINDS}"
            )
        if self.repeat_every is not None:
            _require_range(f"floor_variant.{self.key}.repeat_every", self.repeat_every, 1, 20)


@dataclass(slots=True)
class FacadeZone:
    kind: str
    start_level: int
    end_level: int
    primary_material_slot: str
    floor_variant_sequence: list[str]
    projection_m: float = 0.0
    inset_m: float = 0.0

    def validate(self) -> None:
        if self.kind not in VALID_FACADE_ZONE_KINDS:
            raise GrammarError(f"facade zone kind={self.kind!r} must be one of {VALID_FACADE_ZONE_KINDS}")
        _require_range(f"facade_zone.{self.kind}.start_level", self.start_level, 0, 120)
        _require_range(f"facade_zone.{self.kind}.end_level", self.end_level, self.start_level, 120)
        _require_range(f"facade_zone.{self.kind}.projection_m", self.projection_m, 0.0, 3.0)
        _require_range(f"facade_zone.{self.kind}.inset_m", self.inset_m, 0.0, 10.0)
        if not self.floor_variant_sequence:
            raise GrammarError(f"facade zone {self.kind!r} requires a floor_variant_sequence")


@dataclass(slots=True)
class FacadeGraph:
    openings: list[OpeningSpec] = field(default_factory=list)
    attachments: list[AttachmentSpec] = field(default_factory=list)
    bays: list[BaySpec] = field(default_factory=list)
    floor_variants: list[FloorVariant] = field(default_factory=list)
    zones: list[FacadeZone] = field(default_factory=list)
    sides: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def regular(cls, facade: Facade | None = None, floors: int = 6) -> "FacadeGraph":
        facade = facade or Facade()
        opening = OpeningSpec(
            id="standard_window",
            width_ratio=facade.window_width_ratio,
            height_ratio=facade.window_height_ratio,
            sill_m=facade.sill_height_m,
            reveal_depth_m=facade.window_recess_m,
        )
        bay = BaySpec(id="standard", opening_id=opening.id)
        front_sequence = [bay.id] * max(1, facade.front_bay_count)
        side_sequence = [bay.id] * max(1, facade.side_bay_count)
        variant = FloorVariant(key="typical_a", bay_sequence=front_sequence)
        return cls(
            openings=[opening],
            bays=[bay],
            floor_variants=[variant],
            zones=[
                FacadeZone("base", 0, 0, "primary", ["typical_a"]),
                FacadeZone("middle", 1, max(1, floors - 1), "primary", ["typical_a"]),
            ],
            sides={
                "front": front_sequence,
                "rear": front_sequence,
                "left": side_sequence,
                "right": side_sequence,
            },
        )

    def validate(self) -> None:
        for collection_name, values in (
            ("openings", self.openings),
            ("attachments", self.attachments),
            ("bays", self.bays),
            ("floor_variants", self.floor_variants),
        ):
            ids = [getattr(value, "id", None) or getattr(value, "key", None) for value in values]
            if len(ids) != len(set(ids)):
                raise GrammarError(f"facade_graph.{collection_name} contains duplicate ids")
            for value in values:
                value.validate()

        for zone in self.zones:
            zone.validate()

        opening_ids = {opening.id for opening in self.openings}
        attachment_ids = {attachment.id for attachment in self.attachments}
        bay_ids = {bay.id for bay in self.bays}
        variant_ids = {variant.key for variant in self.floor_variants}
        for bay in self.bays:
            if bay.opening_id and bay.opening_id not in opening_ids:
                raise GrammarError(f"bay {bay.id!r} references unknown opening {bay.opening_id!r}")
            missing = set(bay.attachment_ids) - attachment_ids
            if missing:
                raise GrammarError(f"bay {bay.id!r} references unknown attachments {sorted(missing)}")
        for variant in self.floor_variants:
            missing = set(variant.bay_sequence) - bay_ids
            if missing:
                raise GrammarError(f"floor variant {variant.key!r} references unknown bays {sorted(missing)}")
        for zone in self.zones:
            missing = set(zone.floor_variant_sequence) - variant_ids
            if missing:
                raise GrammarError(f"zone {zone.kind!r} references unknown floor variants {sorted(missing)}")
        for side in ("front", "rear", "left", "right"):
            if side not in self.sides or not self.sides[side]:
                raise GrammarError(f"facade_graph.sides.{side} is required")
            missing = set(self.sides[side]) - bay_ids
            if missing:
                raise GrammarError(f"facade side {side!r} references unknown bays {sorted(missing)}")


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
    # canonical key into tools/archetype_compiler/textures/<key>/; None = flat colour
    texture_key: str | None = None

    def validate(self, slot: str) -> None:
        _require_hex(f"materials.{slot}.base_color", self.base_color)
        _require_range(f"materials.{slot}.roughness", self.roughness, 0.0, 1.0)
        _require_range(f"materials.{slot}.metallic", self.metallic, 0.0, 1.0)
        if self.texture_key is not None and not re.match(r"^[a-z0-9_]+$", self.texture_key):
            raise GrammarError(f"materials.{slot}.texture_key={self.texture_key!r} must be a snake_case slug")


def _default_material(name: str, color: str, roughness: float = 0.6, metallic: float = 0.0) -> Material:
    return Material(name=name, base_color=color, roughness=roughness, metallic=metallic)


@dataclass(slots=True)
class Materials:
    primary: Material = field(default_factory=lambda: _default_material("MAT_Facade_Primary", "#d8d2c4"))
    secondary: Material = field(default_factory=lambda: _default_material("MAT_Facade_Secondary", "#8a8176"))
    accent: Material = field(default_factory=lambda: _default_material("MAT_Accent", "#2b2e33", 0.45, 0.6))
    glass: Material = field(default_factory=lambda: _default_material("MAT_Glass", "#5f7f95", 0.08, 0.0))
    concrete: Material = field(default_factory=lambda: Material(
        name="MAT_Concrete", base_color="#b5b1a8", roughness=0.8, metallic=0.0, texture_key="concrete"))
    roof: Material = field(default_factory=lambda: _default_material("MAT_Roof", "#4a4d4f", 0.85, 0.0))
    green_roof: Material = field(default_factory=lambda: Material(
        name="MAT_GreenRoof", base_color="#5f7a48", roughness=0.9, metallic=0.0, texture_key="sedum_roof"))

    def validate(self) -> None:
        for slot in ("primary", "secondary", "accent", "glass", "concrete", "roof", "green_roof"):
            getattr(self, slot).validate(slot)


@dataclass(slots=True)
class BuildingGrammar:
    family_id: str
    source: GrammarSource
    dimensions: Dimensions
    facade: Facade = field(default_factory=Facade)
    facade_graph: FacadeGraph = field(default_factory=FacadeGraph)
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
        if not self.facade_graph.floor_variants:
            self.facade_graph = FacadeGraph.regular(self.facade, self.dimensions.default_floors)
        self.facade_graph.validate()
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
        if version not in (1, 2, SCHEMA_VERSION):
            raise GrammarError(
                f"grammar schema_version={version!r} not supported by this generator "
                f"(expected 1, 2, or {SCHEMA_VERSION}). Re-run the compiler."
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
                texture_key=raw.get("texture_key", defaults.texture_key),
            )

        facade = Facade(**data.get("facade", {}))
        graph_raw = data.get("facade_graph") or {}
        facade_graph = FacadeGraph(
            openings=[OpeningSpec(**item) for item in graph_raw.get("openings", [])],
            attachments=[AttachmentSpec(**item) for item in graph_raw.get("attachments", [])],
            bays=[BaySpec(**item) for item in graph_raw.get("bays", [])],
            floor_variants=[FloorVariant(**item) for item in graph_raw.get("floor_variants", [])],
            zones=[FacadeZone(**item) for item in graph_raw.get("zones", [])],
            sides={str(key): list(value) for key, value in graph_raw.get("sides", {}).items()},
        ) if graph_raw else FacadeGraph.regular(
            facade,
            int(data.get("dimensions", {}).get("default_floors", 6)),
        )

        grammar = cls(
            family_id=data["family_id"],
            source=GrammarSource(**data.get("source", {"archetype_id": ""})),
            dimensions=Dimensions(**data["dimensions"]),
            facade=facade,
            facade_graph=facade_graph,
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
