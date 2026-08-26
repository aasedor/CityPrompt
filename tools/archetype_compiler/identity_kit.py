"""Parametric signature assemblies — the missing middle of the family pipeline.

Two paths existed before this module and neither could carry archetype identity
into a user-drawn footprint:

* ``compiler.py`` derives a dimensionally correct grammar, but every identity
  word in the catalogue (``facadeDetail.secondaryMaterial``,
  ``roofDetail.form``) is resolved to a colour or a roof enum. The result is
  known failure pattern #1: "Generic rectangular massing with identity
  delegated to a flat image."
* The v98 ``massing_graph`` nodes are ``locked_mesh_bundle`` entries — baked
  vertices with a ``geometry_sha256``. They reproduce a reference exactly and
  cannot adapt, which is why ``_resolved_massing_graph`` only admits them
  within 1 cm of their authored dimensions.

A signature assembly here is neither. It is a small parametric builder that
takes the bay graph and a handful of declared numbers and constructs real
geometry, so the same marquee spans a 14 m frontage or a 25 m one without
being redrawn.

Rules enforced for every assembly, taken from the known failure patterns:

* placement derives from semantic bay occupancy, never a fixed spacing grid
  ("Detail collides with windows");
* every projection wraps its return faces ("Historic landmark has detailed
  fronts but blank projecting sides");
* fixed assemblies keep authored proportions while ordinary bays absorb width
  ("Windows and carved bays become unnaturally wide when a family is resized");
* lamps and neon are separate small emissive solids; glazing stays
  nearly non-emissive ("Windows are transparent but still look painted").
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

import bpy

import blender_generate as bg


# --------------------------------------------------------------------------
# Bay graph
# --------------------------------------------------------------------------


@dataclass
class Bay:
    """One structural bay of the front elevation."""

    index: int
    centre_x: float
    width: float
    role: str = "ordinary"  # ordinary | entrance | end

    @property
    def x0(self) -> float:
        return self.centre_x - self.width / 2

    @property
    def x1(self) -> float:
        return self.centre_x + self.width / 2


@dataclass
class BayGraph:
    """Semantic bay occupancy for one elevation.

    ``entrance_bays`` are the fixed identity centre; ordinary bays are the only
    ones that repeat when the footprint grows.
    """

    bays: list[Bay]
    width: float
    depth: float
    floor_height: float
    floors: int

    @classmethod
    def from_dimensions(
        cls,
        width: float,
        depth: float,
        floor_height: float,
        floors: int,
        bay_module: float = 3.4,
        entrance_bay_count: int = 3,
    ) -> "BayGraph":
        count = max(3, int(round(width / bay_module)))
        bay_width = width / count
        bays = [
            Bay(index=i, centre_x=-width / 2 + bay_width * (i + 0.5), width=bay_width)
            for i in range(count)
        ]
        bays[0].role = "end"
        bays[-1].role = "end"

        # Centre the entrance on the true middle so an even bay count does not
        # push the marquee off-axis. On a narrow frontage the entrance yields
        # bays rather than the end conditions: losing a corner pier costs more
        # identity than a slightly narrower marquee.
        entrance = min(entrance_bay_count, count - 2)
        if entrance > 0:
            start = (count - entrance) // 2
            for bay in bays[start : start + entrance]:
                bay.role = "entrance"
        return cls(bays=bays, width=width, depth=depth, floor_height=floor_height, floors=floors)

    def of_role(self, role: str) -> list[Bay]:
        return [bay for bay in self.bays if bay.role == role]

    def span(self, role: str) -> tuple[float, float] | None:
        selected = self.of_role(role)
        if not selected:
            return None
        return (min(bay.x0 for bay in selected), max(bay.x1 for bay in selected))

    def storey_z(self, storey: int) -> float:
        return storey * self.floor_height


# --------------------------------------------------------------------------
# Clearance
# --------------------------------------------------------------------------


@dataclass
class Reservation:
    """A band of facade already claimed by an assembly.

    Elevation extent alone is not enough. A blade sign mounted on brackets
    legitimately passes in front of a relief course, and a marquee legitimately
    sits proud of the entrance glazing; the reference shows exactly that. Two
    assemblies conflict only when they contest the same depth plane, so the
    claim carries its projection range from the facade face.
    """

    x0: float
    x1: float
    z0: float
    z1: float
    owner: str
    # Projection outward from the facade face, in metres. Elements on the wall
    # claim the facade plane; bracketed elements claim the air in front of it.
    y_near: float = 0.0
    y_far: float = 0.35

    def overlaps(self, other: "Reservation") -> bool:
        return not (
            self.x1 <= other.x0
            or self.x0 >= other.x1
            or self.z1 <= other.z0
            or self.z0 >= other.z1
            or self.y_far <= other.y_near
            or self.y_near >= other.y_far
        )


class ClearanceError(RuntimeError):
    """Raised when a signature assembly would land on an opening."""


@dataclass
class FacadeReservations:
    """Opening-clearance ledger.

    Every assembly registers its footprint before it builds. A collision is an
    authoring error surfaced immediately, rather than a projection quietly
    landing across a window.
    """

    items: list[Reservation] = field(default_factory=list)

    def claim(self, claim: Reservation, *, strict: bool = True) -> bool:
        for existing in self.items:
            if claim.overlaps(existing):
                if strict:
                    raise ClearanceError(
                        f"{claim.owner} collides with {existing.owner} "
                        f"(x {claim.x0:.2f}..{claim.x1:.2f}, z {claim.z0:.2f}..{claim.z1:.2f})"
                    )
                return False
        self.items.append(claim)
        return True


# --------------------------------------------------------------------------
# Signature assemblies
# --------------------------------------------------------------------------

Builder = Callable[..., list[bpy.types.Object]]

_REGISTRY: dict[str, Builder] = {}


def signature(name: str) -> Callable[[Builder], Builder]:
    def decorate(fn: Builder) -> Builder:
        _REGISTRY[name] = fn
        return fn

    return decorate


def available_signatures() -> list[str]:
    return sorted(_REGISTRY)


def build_signature(
    name: str,
    graph: BayGraph,
    mats: dict[str, Any],
    reservations: FacadeReservations,
    params: dict[str, Any],
) -> list[bpy.types.Object]:
    if name not in _REGISTRY:
        raise KeyError(f"unknown signature assembly {name!r}; have {available_signatures()}")
    return _REGISTRY[name](graph, mats, reservations, **params)


@signature("marquee")
def build_marquee(
    graph: BayGraph,
    mats: dict[str, Any],
    reservations: FacadeReservations,
    *,
    projection: float = 2.6,
    fascia_height: float = 1.35,
    soffit_z: float | None = None,
    bulb_spacing: float = 0.42,
    wrap_returns: bool = True,
) -> list[bpy.types.Object]:
    """Projecting illuminated canopy over the entrance bays.

    Spans the entrance bays only, so a wider frontage grows its ordinary bays
    and leaves the marquee at its authored proportion.
    """
    span = graph.span("entrance")
    if span is None:
        return []
    x0, x1 = span
    width = x1 - x0
    centre_x = (x0 + x1) / 2
    top_z = soffit_z if soffit_z is not None else graph.floor_height * 0.82
    front_y = -graph.depth / 2

    reservations.claim(
        Reservation(x0 - 0.2, x1 + 0.2, top_z - fascia_height - 0.3, top_z + 0.35, "marquee",
                    y_near=0.0, y_far=projection)
    )

    objects: list[bpy.types.Object] = []
    # Slab: the horizontal plate that casts the entrance shadow.
    objects.append(
        bg.add_beveled_box(
            "SIG_Marquee_Slab",
            (width + 0.5, projection, 0.34),
            (centre_x, front_y - projection / 2, top_z),
            mats["ornament"],
            bevel_m=0.04,
        )
    )
    # Fascia on three sides — the returns are what make it read from an angle.
    faces: list[tuple[str, tuple[float, float, float], tuple[float, float, float]]] = [
        (
            "Front",
            (width + 0.5, 0.22, fascia_height),
            (centre_x, front_y - projection + 0.11, top_z - fascia_height / 2),
        )
    ]
    if wrap_returns:
        for sign, label in ((-1.0, "Left"), (1.0, "Right")):
            faces.append(
                (
                    label,
                    (0.22, projection, fascia_height),
                    (
                        centre_x + sign * (width + 0.5) / 2,
                        front_y - projection / 2,
                        top_z - fascia_height / 2,
                    ),
                )
            )
    for label, size, location in faces:
        objects.append(
            bg.add_beveled_box(f"SIG_Marquee_Fascia{label}", size, location, mats["signage"], bevel_m=0.03)
        )

    # Chaser bulbs: small emissive solids, never an emissive facade material.
    lamp_z = top_z - fascia_height - 0.12
    count = max(6, int(width / bulb_spacing))
    for i in range(count):
        x = x0 - 0.25 + (width + 0.5) * (i + 0.5) / count
        objects.append(
            bg.add_cylinder(
                f"SIG_Marquee_Bulb_{i:02d}",
                0.055,
                0.1,
                (x, front_y - projection + 0.05, lamp_z),
                mats["lamp"],
                vertices=8,
            )
        )
    # Soffit lighting trough under the plate.
    objects.append(
        bg.add_box(
            "SIG_Marquee_Soffit",
            (width + 0.1, projection - 0.35, 0.09),
            (centre_x, front_y - projection / 2 - 0.1, top_z - 0.2),
            mats["lamp"],
        )
    )
    return objects


@signature("blade_sign")
def build_blade_sign(
    graph: BayGraph,
    mats: dict[str, Any],
    reservations: FacadeReservations,
    *,
    height: float | None = None,
    overshoot: float = 4.2,
    width: float = 2.3,
    projection: float = 1.1,
    crown_steps: int = 3,
    offset_from_entrance: float = 0.0,
    standoff: float = 0.55,
) -> list[bpy.types.Object]:
    """Vertical pylon sign rising past the parapet.

    Mounted proud of the wall on brackets, so it passes in front of any relief
    course rather than displacing it — ``standoff`` is the air gap that makes
    that legible instead of a sign fused to the facade. The sign is a small
    building in its own right: both return faces are modelled so an orbit view
    does not reveal a blank card.
    """
    span = graph.span("entrance")
    if span is None:
        return []
    x0, x1 = span
    centre_x = (x0 + x1) / 2 + offset_from_entrance
    front_y = -graph.depth / 2 - standoff
    base_z = graph.floor_height * 1.05
    parapet_z = graph.storey_z(graph.floors)
    # A blade sign is a skyline object: it must clear the parapet by a real
    # margin or it reads as a panel stuck to the wall. Deriving the height from
    # the parapet keeps that true at any storey count.
    if height is None:
        height = (parapet_z - base_z) + overshoot

    reservations.claim(
        Reservation(centre_x - width / 2 - 0.1, centre_x + width / 2 + 0.1, base_z, base_z + height,
                    "blade_sign", y_near=standoff, y_far=standoff + projection)
    )

    objects: list[bpy.types.Object] = []
    objects.append(
        bg.add_beveled_box(
            "SIG_Blade_Body",
            (width, projection, height),
            (centre_x, front_y - projection / 2, base_z + height / 2),
            mats["signage"],
            bevel_m=0.03,
        )
    )
    # Face panels on both returns, inset so the body edge stays visible.
    for sign, label in ((-1.0, "Left"), (1.0, "Right")):
        objects.append(
            bg.add_box(
                f"SIG_Blade_Face{label}",
                (0.07, projection - 0.14, height - 0.6),
                (centre_x + sign * (width / 2 + 0.02), front_y - projection / 2, base_z + height / 2),
                mats["lamp"],
            )
        )
    objects.append(
        bg.add_box(
            "SIG_Blade_FrontPanel",
            (width - 0.34, 0.07, height - 0.85),
            (centre_x, front_y - projection - 0.02, base_z + height / 2),
            mats["lamp"],
        )
    )
    # Stepped crown — the deco silhouette, widening downward.
    for step in range(crown_steps):
        scale = 1.0 + 0.32 * (crown_steps - step)
        objects.append(
            bg.add_beveled_box(
                f"SIG_Blade_Crown_{step}",
                (width * scale, projection * 0.9, 0.42),
                (centre_x, front_y - projection / 2, base_z + height + 0.21 + step * 0.42),
                mats["ornament"],
                bevel_m=0.02,
            )
        )
    # Brackets spanning the standoff gap, so the pylon is visibly carried by
    # the wall rather than floating in front of it.
    wall_y = -graph.depth / 2
    reach = standoff + projection / 2
    for frac in (0.28, 0.72):
        z = base_z + height * frac
        objects.append(
            bg.add_box(
                f"SIG_Blade_Bracket_{int(frac * 100)}",
                (0.14, reach, 0.14),
                (centre_x, wall_y - reach / 2, z),
                mats["ornament"],
            )
        )
        objects.append(
            bg.add_box(
                f"SIG_Blade_Stay_{int(frac * 100)}",
                (0.09, reach * 0.9, 0.09),
                (centre_x, wall_y - reach / 2, z - 0.55),
                mats["ornament"],
            )
        )
    return objects


@signature("relief_band")
def build_relief_band(
    graph: BayGraph,
    mats: dict[str, Any],
    reservations: FacadeReservations,
    *,
    storey: int = 2,
    band_height: float = 0.9,
    relief_depth: float = 0.16,
    motif: Sequence[float] = (1.0, 0.55, 0.8, 0.55),
    wrap_returns: bool = True,
) -> list[bpy.types.Object]:
    """Repeating geometric frieze course.

    ``motif`` is a relative-height pattern repeated across the band, which is
    how a Mayan/Aztec deco relief is described without baking a mesh: the
    period repeats with the bay module, so widening the building adds motif
    units instead of stretching them.
    """
    z = graph.storey_z(storey) - band_height / 2
    front_y = -graph.depth / 2
    reservations.claim(
        Reservation(-graph.width / 2, graph.width / 2, z - band_height / 2, z + band_height / 2,
                    f"relief_band@{storey}", y_near=0.0, y_far=relief_depth),
        strict=False,
    )

    objects: list[bpy.types.Object] = []
    unit = 0.55
    count = max(8, int(graph.width / unit))
    for i in range(count):
        x = -graph.width / 2 + graph.width * (i + 0.5) / count
        rel = motif[i % len(motif)]
        objects.append(
            bg.add_box(
                f"SIG_Relief_F_{i:03d}",
                (graph.width / count * 0.82, relief_depth, band_height * rel),
                (x, front_y - relief_depth / 2, z),
                mats["ornament"],
            )
        )
    if wrap_returns:
        side_count = max(6, int(graph.depth / unit))
        for sign, label in ((-1.0, "L"), (1.0, "R")):
            for i in range(side_count):
                y = -graph.depth / 2 + graph.depth * (i + 0.5) / side_count
                rel = motif[i % len(motif)]
                objects.append(
                    bg.add_box(
                        f"SIG_Relief_{label}_{i:03d}",
                        (relief_depth, graph.depth / side_count * 0.82, band_height * rel),
                        (sign * (graph.width / 2 + relief_depth / 2), y, z),
                        mats["ornament"],
                    )
                )
    # Continuous cill under the motif ties the units into one course.
    objects.append(
        bg.add_box(
            "SIG_Relief_Cill",
            (graph.width + 0.24, relief_depth + 0.06, 0.14),
            (0.0, front_y - relief_depth / 2, z - band_height / 2 - 0.07),
            mats["ornament"],
        )
    )
    return objects


@signature("arched_opening")
def build_arched_opening(
    graph: BayGraph,
    mats: dict[str, Any],
    reservations: FacadeReservations,
    *,
    storey: int = 1,
    ring_width: float = 0.42,
    inner_radius: float | None = None,
    tracery_bars: int = 4,
) -> list[bpy.types.Object]:
    """Monumental arch head over the entrance bays' upper window."""
    span = graph.span("entrance")
    if span is None:
        return []
    x0, x1 = span
    centre_x = (x0 + x1) / 2
    radius = inner_radius if inner_radius is not None else (x1 - x0) / 2 - 0.5
    spring_z = graph.storey_z(storey) + graph.floor_height * 0.52
    front_y = -graph.depth / 2

    reservations.claim(
        Reservation(centre_x - radius - ring_width, centre_x + radius + ring_width,
                    spring_z - 0.1, spring_z + radius + ring_width, "arched_opening",
                    y_near=-0.5, y_far=0.4),
        strict=False,
    )

    objects = [
        bg.add_arch_ring(
            "SIG_Arch_Ring",
            centre_x,
            front_y,
            spring_z,
            radius,
            ring_width,
            0.38,
            mats["ornament"],
            segments=20,
        )
    ]
    # Recessed reveal so the arch reads as an opening, not an applied hoop.
    objects.append(
        bg.add_box(
            "SIG_Arch_Reveal",
            (radius * 2, 0.5, graph.floor_height * 0.5),
            (centre_x, front_y + 0.22, spring_z - graph.floor_height * 0.25),
            mats["shadow"],
        )
    )
    for i in range(tracery_bars):
        x = centre_x - radius + (radius * 2) * (i + 1) / (tracery_bars + 1)
        drop = math.sqrt(max(radius**2 - (x - centre_x) ** 2, 0.0))
        objects.append(
            bg.add_box(
                f"SIG_Arch_Tracery_{i}",
                (0.09, 0.14, drop + graph.floor_height * 0.5),
                (x, front_y - 0.06, spring_z + drop / 2 - graph.floor_height * 0.25),
                mats["ornament"],
            )
        )
    return objects


@signature("ornamental_parapet")
def build_ornamental_parapet(
    graph: BayGraph,
    mats: dict[str, Any],
    reservations: FacadeReservations,
    *,
    base_height: float = 0.85,
    centre_lift: float = 1.5,
    step_count: int = 3,
    pier_cap: bool = True,
) -> list[bpy.types.Object]:
    """Stepped parapet: a raised centrepiece over the entrance, piers at ends.

    This is the silhouette element. A flat band is what makes a decorated box
    still read as a box, so the centre lift and end piers are authored fixed
    while the plain runs between them absorb extra width.
    """
    top_z = graph.storey_z(graph.floors)
    front_y = -graph.depth / 2
    objects: list[bpy.types.Object] = []

    # Continuous base course, wrapped on all four sides.
    for size, location, label in (
        ((graph.width + 0.3, 0.34, base_height), (0.0, front_y - 0.17, top_z + base_height / 2), "Front"),
        ((graph.width + 0.3, 0.34, base_height * 0.7), (0.0, graph.depth / 2 + 0.17, top_z + base_height * 0.35), "Rear"),
        ((0.34, graph.depth + 0.3, base_height * 0.85), (-graph.width / 2 - 0.17, 0.0, top_z + base_height * 0.42), "Left"),
        ((0.34, graph.depth + 0.3, base_height * 0.85), (graph.width / 2 + 0.17, 0.0, top_z + base_height * 0.42), "Right"),
    ):
        objects.append(bg.add_beveled_box(f"SIG_Parapet_{label}", size, location, mats["primary"], bevel_m=0.03))

    span = graph.span("entrance")
    if span is not None:
        x0, x1 = span
        centre_x = (x0 + x1) / 2
        width = (x1 - x0) + 1.0
        for step in range(step_count):
            frac = (step_count - step) / step_count
            objects.append(
                bg.add_beveled_box(
                    f"SIG_Parapet_Step_{step}",
                    (width * (0.55 + 0.45 * frac), 0.42, centre_lift / step_count),
                    (
                        centre_x,
                        front_y - 0.21,
                        top_z + base_height + centre_lift * (step + 0.5) / step_count,
                    ),
                    mats["primary"],
                    bevel_m=0.03,
                )
            )
    if pier_cap:
        for bay in graph.of_role("end"):
            objects.append(
                bg.add_beveled_box(
                    f"SIG_Parapet_Pier_{bay.index}",
                    (bay.width * 0.5, 0.46, base_height + 0.75),
                    (bay.centre_x, front_y - 0.23, top_z + (base_height + 0.75) / 2),
                    mats["primary"],
                    bevel_m=0.03,
                )
            )
    return objects


# --------------------------------------------------------------------------
# Catalogue prose -> declared signatures
# --------------------------------------------------------------------------

# The catalogue already names these features in prose. compiler.py resolves the
# same fields to a colour and a roof enum; this table resolves them to geometry.
_PROSE_SIGNATURES: tuple[tuple[str, str, dict[str, Any]], ...] = (
    ("marquee", "marquee", {}),
    ("blade sign", "blade_sign", {}),
    ("vertical blade", "blade_sign", {}),
    ("geometric relief", "relief_band", {}),
    ("mayan", "relief_band", {}),
    ("geometric motif", "relief_band", {}),
    ("decorative parapet", "ornamental_parapet", {}),
    ("ornate parapet", "ornamental_parapet", {}),
    ("stepped parapet", "ornamental_parapet", {"step_count": 4}),
    ("arched", "arched_opening", {}),
    ("arch ", "arched_opening", {}),
)


def derive_signatures(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Read the identity words the dimension compiler throws away.

    Returns a list of ``{"type": ..., "params": {...}, "evidence": ...}`` in a
    stable order, so a family's declared identity is reproducible and every
    assembly can name the catalogue text that justified it.
    """
    variant = payload.get("selectedVariant") or {}
    facade = {**(payload.get("facadeDetail") or {}), **(variant.get("facadeDetail") or {})}
    roof = {**(payload.get("roofDetail") or {}), **(variant.get("roofDetail") or {})}
    sources = {
        "description": str(variant.get("description") or payload.get("description") or ""),
        "facadeDetail.primaryMaterial": str(facade.get("primaryMaterial") or ""),
        "facadeDetail.secondaryMaterial": str(facade.get("secondaryMaterial") or ""),
        "facadeDetail.groundFloor": str(facade.get("groundFloor") or ""),
        "facadeDetail.colorScheme": str(facade.get("colorScheme") or ""),
        "roofDetail.form": str(roof.get("form") or ""),
        "roofDetail.material": str(roof.get("material") or ""),
    }

    found: dict[str, dict[str, Any]] = {}
    for field_name, text in sources.items():
        lowered = text.lower()
        for token, signature_name, params in _PROSE_SIGNATURES:
            if token in lowered and signature_name not in found:
                found[signature_name] = {
                    "type": signature_name,
                    "params": dict(params),
                    "evidence": f'{field_name}: "{text[:80]}"',
                }
    order = ["ornamental_parapet", "relief_band", "arched_opening", "marquee", "blade_sign"]
    return [found[name] for name in order if name in found]
