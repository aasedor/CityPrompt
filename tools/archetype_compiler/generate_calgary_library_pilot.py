"""Author the Calgary New Central Library LEGO pilot.

This pilot treats the landmark as a constructed enclosure instead of a textured
box.  Its fixed GLB owns the faceted almond plan, crystalline panel schedule,
subtractive Chinook arch, cedar soffit, occupied library depth, transit bridge,
and faceted roof.  A conservative six-module stack preserves the family when a
user's hand-drawn rectangle falls outside the fixed-landmark tolerance.

Run from the repository root with Blender 5.x:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_calgary_library_pilot.py -- \
      --output-root frontend/public/families --view-set pilot
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from generate_wave3_landmark_families import (  # noqa: E402
    COORDINATE_CONTRACT,
    aim_camera,
    box,
    cylinder,
    delete_objects,
    export_glb,
    material,
    module_contract_markers,
    setup_render,
    triangle_count,
)
from generate_wave4_standard_batch import profiled_glass_material  # noqa: E402
from generate_wave4_standard_families import pbr_material  # noqa: E402
from generate_wave6_nonresidential_families import (  # noqa: E402
    join_mesh_group,
    mapped_reference_panel,
    mesh_object,
    rectangular_beam,
    reference_image_material,
)


FAMILY = "calgary-central-library"
ARCHETYPE_ID = "calgary_new_central_library"
VARIANT_ID = "library_original_snohetta"
GLASS_PROFILE = "calgary_library_low_iron_fritted"
WIDTH = 82.3
DEPTH = 58.0
HEIGHT = 25.0
FLOOR_HEIGHT = 5.0
NATIVE_FLOORS = 4
SEGMENTS = 64

CONFIG = {
    "label": "Calgary New Central Library — Original Snøhetta",
    "aesthetic_category_id": "civic_monumental",
    "development_type": "institutional",
    "aliases": [ARCHETYPE_ID, VARIANT_ID],
    "reuse_keys": [
        ARCHETYPE_ID,
        VARIANT_ID,
        "Civic / Institutional",
        "Library",
    ],
    "identity": (
        "A four-level faceted crystalline almond bridges the CTrain, with a "
        "sixty-forty field of iridescent aluminum and low-iron fritted glass "
        "carved away into a continuous double-curved western-red-cedar "
        "Chinook arch and transparent public library."
    ),
    "materials": (
        "iridescent silver-white aluminum unitized panels; clear and graduated-"
        "frit low-iron triple glazing; pale aluminum pressure caps; western red "
        "cedar batten soffit; warm occupied library interiors; board-formed "
        "concrete transit bridge and public plinth; silver membrane roof"
    ),
    "kits": [
        "faceted_almond_envelope",
        "five_family_unitized_panel_schedule",
        "subtractive_chinook_arch",
        "double_curved_cedar_soffit",
        "occupied_low_iron_glazing",
        "transit_bridge",
        "faceted_atrium_roof",
    ],
    "footprint": {
        "recommendedWidth_m": [65, 85],
        "recommendedDepth_m": [50, 70],
        "recommendedFloors": [3, 5],
    },
    "fixed_band": {
        "scaleMin": 0.84,
        "scaleMax": 1.16,
        "maxAxisRatio": 1.14,
    },
    "goalpost": "/archetypes/buildings/calgary-new-central-library/variant_0.png",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("frontend/public/families"),
    )
    parser.add_argument("--view-set", choices=("pilot", "all"), default="all")
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-modules", action="store_true")
    parser.add_argument("--render-existing", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def load_palette(folder: Path) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = json.loads(
        (folder / "textures" / "skin_manifest.json").read_text(encoding="utf-8")
    )
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    clear = profiled_glass_material(
        "MAT_CALGARY_LowIronClear",
        GLASS_PROFILE,
        tint="#819093",
    )
    clear["pane_treatment"] = "clear_low_iron_triple_glazed"
    frit = profiled_glass_material(
        "MAT_CALGARY_GraduatedCeramicFrit",
        GLASS_PROFILE,
        tint="#c8d1d0",
        roughness_scale=1.55,
        transmission_scale=0.48,
    )
    frit["pane_treatment"] = "graduated_ceramic_frit"
    frit["frit_coverage"] = 0.58
    mats = {
        "opaque": pbr_material(
            "MAT_CALGARY_IridescentAluminum",
            folder,
            near["metal"],
            "iridescent_aluminum",
            metallic=0.66,
            saturation=0.72,
            value=1.08,
        ),
        "opaque_alt": pbr_material(
            "MAT_CALGARY_IridescentAluminumCool",
            folder,
            near["metal"],
            "iridescent_aluminum_alt",
            metallic=0.52,
            saturation=0.58,
            value=0.93,
        ),
        "facade_skin": pbr_material(
            "MAT_CALGARY_RenderLockedFacade",
            folder,
            near["facade"],
            "facade",
            emission_strength=0.035,
            saturation=0.92,
            value=0.98,
        ),
        "cedar": pbr_material(
            "MAT_CALGARY_WesternRedCedar",
            folder,
            near["cedar"],
            "cedar",
            saturation=0.88,
            value=0.74,
        ),
        "concrete": pbr_material(
            "MAT_CALGARY_BoardFormConcrete",
            folder,
            near["concrete"],
            "concrete",
            saturation=0.72,
            value=0.88,
        ),
        "roof": pbr_material(
            "MAT_CALGARY_FacetedRoof",
            folder,
            near["roof"],
            "roof",
            metallic=0.34,
            saturation=0.68,
            value=0.92,
        ),
        "interior": pbr_material(
            "MAT_CALGARY_OccupiedLibrary",
            folder,
            near["interior"],
            "interior",
            emission_strength=0.22,
            saturation=1.04,
            value=0.84,
        ),
        "clear": clear,
        "frit": frit,
        "frame": material(
            "MAT_CALGARY_PalePressureCaps",
            (0.48, 0.52, 0.52, 1.0),
            0.27,
            0.64,
        ),
        "dark": material(
            "MAT_CALGARY_ShadowSteel",
            (0.035, 0.045, 0.048, 1.0),
            0.31,
            0.58,
        ),
        "warm": material(
            "MAT_CALGARY_WarmReadingRooms",
            (0.42, 0.19, 0.065, 1.0),
            0.52,
            emission=(1.0, 0.46, 0.17, 1.0),
            emission_strength=0.72,
        ),
        "underlay": reference_image_material(
            "MAT_CALGARY_RenderLockedOccupiedDepth",
            folder,
            "textures/source/occupied-depth-source-v1.png",
            emission_strength=0.17,
        ),
    }
    mats["opaque"]["panel_family"] = "opaque_iridescent_aluminum"
    mats["opaque_alt"]["panel_family"] = "opaque_iridescent_aluminum_alt"
    mats["frame"]["unitized_panel_family_count"] = 5
    mats["cedar"]["soffit_construction"] = "double_curved_prefabricated_batten_panels"
    return mats, skin


def envelope_radius(z: float) -> tuple[float, float]:
    """Slightly swelling crystalline envelope with a tucked roof edge."""
    t = max(0.0, min(1.0, z / HEIGHT))
    roof_tuck = max(0.0, (t - 0.84) / 0.16)
    a = 39.6 + 1.45 * math.sin(t * math.pi * 0.72) - 0.55 * roof_tuck
    b = 25.5 + 1.55 * math.sin(t * math.pi * 0.70) - 0.48 * roof_tuck
    return a, b


def envelope_point(theta: float, z: float, inset: float = 0.0) -> tuple[float, float, float]:
    a, b = envelope_radius(z)
    facet = 1.0 + 0.008 * math.sin(theta * 5.0 + 0.35)
    return (
        (a - inset) * math.cos(theta) * facet,
        (b - inset) * math.sin(theta) * facet,
        z,
    )


def front_boundary_y(x: float, *, inset: float = 0.0) -> float:
    a, b = envelope_radius(4.0)
    ratio = min(0.999, abs(x) / max(0.1, a - inset))
    return -(b - inset) * math.sqrt(max(0.0, 1.0 - ratio * ratio))


def arch_height(x: float) -> float:
    """Asymmetric Chinook opening: rounded west shoulder and long east sweep."""
    if x <= -26.0:
        ratio = min(1.0, max(0.0, (x + 34.5) / 8.5))
        return 3.35 + 6.25 * math.sqrt(max(0.0, 1.0 - (ratio - 1.0) ** 2))
    ratio = min(1.0, max(0.0, (x + 26.0) / 65.0))
    return 9.60 - 5.25 * (ratio ** 1.16)


def is_arch_void(theta: float, z: float) -> bool:
    x, y, _ = envelope_point(theta, z)
    return y < -6.5 and -34.5 < x < 39.0 and 0.7 < z < arch_height(x)


def mesh_group(
    name: str,
    triangles: list[tuple[tuple[float, float, float], ...]],
    mat: bpy.types.Material,
    *,
    uv_scale: float = 1.0,
) -> bpy.types.Object | None:
    if not triangles:
        return None
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    for triangle in triangles:
        start = len(vertices)
        vertices.extend(triangle)
        faces.append((start, start + 1, start + 2))
    return mesh_object(name, vertices, faces, mat, uv_scale=uv_scale)


def polygon_group(
    name: str,
    polygons: list[list[tuple[float, float, float]]],
    mat: bpy.types.Material,
    *,
    uv_scale: float = 1.0,
) -> bpy.types.Object | None:
    if not polygons:
        return None
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for polygon in polygons:
        start = len(vertices)
        vertices.extend(polygon)
        faces.append(tuple(range(start, start + len(polygon))))
    return mesh_object(name, vertices, faces, mat, uv_scale=uv_scale)


def panel_class(segment: int, band: int, half: int, x: float, z: float) -> str:
    """Deterministic 60/40 opaque/glazed panel schedule with a clear centre."""
    clear_probability = 0.29
    if abs(x) < 25.0:
        clear_probability += 0.14
    if z > 19.0:
        clear_probability += 0.08
    if abs(x) > 33.0:
        clear_probability -= 0.14
    if z < 7.0:
        clear_probability += 0.04
    token = ((segment * 47 + band * 67 + half * 29 + 17) % 101) / 100.0
    if token < clear_probability:
        frit_token = ((segment * 31 + band * 19 + half * 43) % 97) / 96.0
        return "frit" if frit_token < 0.34 else "clear"
    return "opaque_alt" if (segment + band + half) % 7 == 0 else "opaque"


def panel_envelope(m: dict[str, bpy.types.Material]) -> tuple[list[bpy.types.Object], dict]:
    """Wrap a true clipped hexagonal unitized panel schedule around the shell."""
    z_min, z_max = 0.85, 24.35
    column_count = 64
    centre_step = 2.0 * math.pi / column_count
    half_width = centre_step / 1.5
    panel_height = 3.35
    grouped: dict[str, list[list[tuple[float, float, float]]]] = {
        "opaque": [],
        "opaque_alt": [],
        "clear": [],
        "frit": [],
    }
    delivered_cells: set[tuple[int, int]] = set()
    open_cells: set[tuple[int, int]] = set()
    edge_points: dict[
        tuple[tuple[float, float, float], tuple[float, float, float]],
        tuple[tuple[float, float, float], tuple[float, float, float]],
    ] = {}
    objects: list[bpy.types.Object] = []

    def clip_z(
        polygon: list[tuple[float, float]],
        boundary: float,
        *,
        keep_above: bool,
    ) -> list[tuple[float, float]]:
        if not polygon:
            return []
        result: list[tuple[float, float]] = []
        for index, current in enumerate(polygon):
            previous = polygon[index - 1]
            current_inside = current[1] >= boundary if keep_above else current[1] <= boundary
            previous_inside = previous[1] >= boundary if keep_above else previous[1] <= boundary
            if current_inside != previous_inside:
                dz = current[1] - previous[1]
                ratio = 0.0 if abs(dz) < 1e-9 else (boundary - previous[1]) / dz
                result.append(
                    (
                        previous[0] + (current[0] - previous[0]) * ratio,
                        boundary,
                    )
                )
            if current_inside:
                result.append(current)
        return result

    def outside_arch(point: tuple[float, float]) -> bool:
        theta, z = point
        x, y, _ = envelope_point(theta, z)
        return not (
            y < -6.5
            and -34.5 < x < 39.0
            and z < arch_height(x)
        )

    def clip_arch(
        polygon: list[tuple[float, float]],
    ) -> list[tuple[float, float]]:
        """Clip one local panel to the exact nonlinear cedar opening."""
        if not polygon:
            return []
        result: list[tuple[float, float]] = []
        for index, current in enumerate(polygon):
            previous = polygon[index - 1]
            current_inside = outside_arch(current)
            previous_inside = outside_arch(previous)
            if current_inside != previous_inside:
                low, high = previous, current
                low_inside = previous_inside
                for _ in range(18):
                    midpoint = (
                        (low[0] + high[0]) * 0.5,
                        (low[1] + high[1]) * 0.5,
                    )
                    if outside_arch(midpoint) == low_inside:
                        low = midpoint
                    else:
                        high = midpoint
                result.append(
                    (
                        (low[0] + high[0]) * 0.5,
                        (low[1] + high[1]) * 0.5,
                    )
                )
            if current_inside:
                result.append(current)
        return result

    for column in range(column_count):
        theta_centre = -math.pi + column * centre_step
        vertical_shift = panel_height * 0.5 if column % 2 else 0.0
        for row in range(-1, 8):
            z_centre = z_min + panel_height * 0.5 + row * panel_height + vertical_shift
            local = [
                (theta_centre - half_width, z_centre),
                (theta_centre - half_width * 0.5, z_centre + panel_height * 0.5),
                (theta_centre + half_width * 0.5, z_centre + panel_height * 0.5),
                (theta_centre + half_width, z_centre),
                (theta_centre + half_width * 0.5, z_centre - panel_height * 0.5),
                (theta_centre - half_width * 0.5, z_centre - panel_height * 0.5),
            ]
            clipped = clip_z(
                clip_z(local, z_min, keep_above=True),
                z_max,
                keep_above=False,
            )
            before_arch_count = len(clipped)
            clipped = clip_arch(clipped)
            if len(clipped) < 3:
                open_cells.add((column, row))
                continue
            if len(clipped) != before_arch_count or is_arch_void(theta_centre, z_centre):
                open_cells.add((column, row))
            polygon = [
                envelope_point(theta, z)
                for theta, z in clipped
            ]
            centre_point = envelope_point(theta_centre, z_centre)
            kind = panel_class(
                column,
                row + 1,
                len(clipped) % 2,
                centre_point[0],
                z_centre,
            )
            pieces: list[tuple[str, list[tuple[float, float, float]]]]
            split_token = (column * 13 + row * 17 + 5) % 11
            if len(polygon) == 6 and split_token in {0, 4}:
                alternate = (
                    "frit"
                    if kind.startswith("opaque") and split_token == 0
                    else "clear"
                    if kind.startswith("opaque")
                    else "opaque"
                )
                pieces = [
                    (kind, polygon[0:4]),
                    (alternate, [polygon[0], polygon[3], polygon[4], polygon[5]]),
                ]
            else:
                pieces = [(kind, polygon)]
            for piece_kind, piece in pieces:
                grouped[piece_kind].append(piece)
                for edge_index, point_a in enumerate(piece):
                    point_b = piece[(edge_index + 1) % len(piece)]
                    key_a = tuple(round(value, 3) for value in point_a)
                    key_b = tuple(round(value, 3) for value in point_b)
                    key = tuple(sorted((key_a, key_b)))
                    edge_points.setdefault(key, (point_a, point_b))
            delivered_cells.add((column, row))

    for kind, polygons in grouped.items():
        obj = polygon_group(
            f"CALGARY_UnitizedPanels_{kind}",
            polygons,
            m[kind],
            uv_scale=5.0 if kind.startswith("opaque") else 1.0,
        )
        if obj:
            obj["panel_topology"] = "clipped_hexagonal_unitized"
            obj["panel_shape_families"] = "triangle,quadrilateral,pentagon,hexagon,cut_return"
            objects.append(obj)

    # Every delivered polygon gets an explicit pressure-cap boundary. Shared
    # edges are deduplicated, preserving the five-family unitized construction
    # without a generic rectangular curtain-wall cage.
    for index, (point_a, point_b) in enumerate(edge_points.values()):
        delta = Vector(point_b) - Vector(point_a)
        if delta.length < 0.08:
            continue
        normal_a = Vector((point_a[0], point_a[1], 0.0)).normalized()
        normal_b = Vector((point_b[0], point_b[1], 0.0)).normalized()
        lifted_a = Vector(point_a) + normal_a * 0.035
        lifted_b = Vector(point_b) + normal_b * 0.035
        objects.append(
            rectangular_beam(
                f"CALGARY_HexPanelJoint_{index}",
                tuple(lifted_a),
                tuple(lifted_b),
                0.038,
                m["frame"],
            )
        )
    return objects, {
        "panel_count": len(delivered_cells),
        "shape_family_count": 5,
        "open_cells": open_cells,
    }


def occupied_depth_underlay(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    # Monotonic x registration across the public front half keeps one authored
    # four-level interior aligned behind the curved physical panel field.
    underlay_segments = 64
    for segment in range(underlay_segments):
        theta0 = -math.pi + math.pi * segment / underlay_segments
        theta1 = -math.pi + math.pi * (segment + 1) / underlay_segments
        points = (
            envelope_point(theta0, 1.15, inset=0.52),
            envelope_point(theta1, 1.15, inset=0.52),
            envelope_point(theta1, 24.05, inset=0.52),
            envelope_point(theta0, 24.05, inset=0.52),
        )
        objects.append(
            mapped_reference_panel(
                f"CALGARY_RenderLockedOccupiedDepthUnderlay_{segment}",
                points,
                m["underlay"],
                model_x_bounds=(-40.5, 40.5),
                model_z_bounds=(1.15, 24.05),
                source_uv_bounds=(0.01, 0.03, 0.99, 0.97),
            )
        )
    return objects


def ellipse_prism(
    name: str,
    radius_x: float,
    radius_y: float,
    z0: float,
    z1: float,
    mat: bpy.types.Material,
    *,
    segments: int = 40,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for z in (z0, z1):
        vertices.extend(
            (
                radius_x * math.cos(2.0 * math.pi * i / segments),
                radius_y * math.sin(2.0 * math.pi * i / segments),
                z,
            )
            for i in range(segments)
        )
    faces: list[tuple[int, ...]] = []
    faces.append(tuple(range(segments - 1, -1, -1)))
    faces.append(tuple(range(segments, segments * 2)))
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, segments + j, segments + i))
    return mesh_object(name, vertices, faces, mat, uv_scale=4.0)


def annular_plate(
    name: str,
    outer: tuple[float, float],
    inner: tuple[float, float],
    z: float,
    thickness: float,
    mat: bpy.types.Material,
    *,
    segments: int = 40,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for level in (z - thickness / 2, z + thickness / 2):
        for radii in (outer, inner):
            vertices.extend(
                (
                    radii[0] * math.cos(2.0 * math.pi * i / segments),
                    radii[1] * math.sin(2.0 * math.pi * i / segments),
                    level,
                )
                for i in range(segments)
            )
    faces: list[tuple[int, ...]] = []
    # Index bases: bottom outer, bottom inner, top outer, top inner.
    bo, bi, to, ti = 0, segments, segments * 2, segments * 3
    for i in range(segments):
        j = (i + 1) % segments
        faces.extend(
            [
                (to + i, to + j, ti + j, ti + i),
                (bo + j, bo + i, bi + i, bi + j),
                (bo + i, bo + j, to + j, to + i),
                (bi + j, bi + i, ti + i, ti + j),
            ]
        )
    return mesh_object(name, vertices, faces, mat, uv_scale=4.0)


def cedar_arch_and_lobby(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    x_values = [-34.2 + 73.0 * i / 28 for i in range(29)]
    depth_steps = 8
    vertices: list[tuple[float, float, float]] = []
    for x in x_values:
        y_front = front_boundary_y(x, inset=-0.08)
        y_back = -5.8 + 0.018 * x
        for step in range(depth_steps + 1):
            t = step / depth_steps
            y = y_front * (1.0 - t) + y_back * t
            crown = arch_height(x) - 0.16
            z = crown - 1.25 * math.sin(math.pi * t) * (
                0.72 + 0.28 * max(0.0, 1.0 - (x / 39.0) ** 2)
            )
            vertices.append((x, y, z))
    faces: list[tuple[int, int, int, int]] = []
    stride = depth_steps + 1
    for ix in range(len(x_values) - 1):
        for iy in range(depth_steps):
            a = ix * stride + iy
            faces.append((a, a + stride, a + stride + 1, a + 1))
    soffit = mesh_object(
        "CALGARY_DoubleCurvedCedarSoffit",
        vertices,
        faces,
        m["cedar"],
        uv_scale=8.0,
    )
    soffit["construction_evidence"] = (
        "continuous subtractive soffit grid with surface-following cedar battens"
    )
    objects.append(soffit)

    # A deep visible cedar fascia hides the discretized edge of the unitized
    # panel field. It is continuous with the soffit, so the arch reads as
    # material carved from the envelope rather than a timber rail attached to it.
    fascia_vertices: list[tuple[float, float, float]] = []
    for x in x_values:
        y = front_boundary_y(x, inset=-0.18)
        fascia_vertices.extend(
            [
                (x, y, arch_height(x) - 0.72),
                (x, y - 0.10, arch_height(x) + 0.62),
            ]
        )
    fascia_faces = [
        (index * 2, index * 2 + 2, index * 2 + 3, index * 2 + 1)
        for index in range(len(x_values) - 1)
    ]
    fascia = mesh_object(
        "CALGARY_IntegratedCedarArchReveal",
        fascia_vertices,
        fascia_faces,
        m["cedar"],
        uv_scale=7.0,
    )
    fascia["subtractive_identity"] = "thick cedar reveal continuous with soffit"
    objects.append(fascia)

    # Fine battens follow the same surface instead of reading as an applied
    # canopy.
    for index in range(len(x_values) - 1):
        x0, x1 = x_values[index], x_values[index + 1]
        p0 = (x0, front_boundary_y(x0, inset=-0.22), arch_height(x0) - 0.63)
        p1 = (x1, front_boundary_y(x1, inset=-0.22), arch_height(x1) - 0.63)
        objects.append(
            rectangular_beam(
                f"CALGARY_CedarArchEdge_{index}",
                p0,
                p1,
                0.11,
                m["cedar"],
                depth=0.13,
            )
        )
    for batten_index, ix in enumerate(range(1, len(x_values) - 1, 2)):
        x = x_values[ix]
        y_front = front_boundary_y(x, inset=-0.03)
        y_back = -5.8 + 0.018 * x
        previous = None
        for step in range(depth_steps + 1):
            t = step / depth_steps
            point = (
                x,
                y_front * (1.0 - t) + y_back * t - 0.035,
                arch_height(x)
                - 0.21
                - 1.25
                * math.sin(math.pi * t)
                * (0.72 + 0.28 * max(0.0, 1.0 - (x / 39.0) ** 2)),
            )
            if previous:
                objects.append(
                    rectangular_beam(
                        f"CALGARY_CedarBatten_{batten_index}_{step}",
                        previous,
                        point,
                        0.055,
                        m["cedar"],
                        depth=0.035,
                    )
                )
            previous = point

    # The lobby glazing sits behind the carved edge, with real mullion depth,
    # doors and an escalator visible from the plaza.
    lobby_x = [-33.0 + 70.0 * i / 36 for i in range(37)]
    for index, (x0, x1) in enumerate(zip(lobby_x, lobby_x[1:])):
        y0 = front_boundary_y(x0, inset=0.58)
        y1 = front_boundary_y(x1, inset=0.58)
        top0 = max(3.0, arch_height(x0) - 0.56)
        top1 = max(3.0, arch_height(x1) - 0.56)
        points = [
            (x0, y0, 1.08),
            (x1, y1, 1.08),
            (x1, y1, top1),
            (x0, y0, top0),
        ]
        objects.append(
            mesh_object(
                f"CALGARY_EntryLobby_Pane_{index}",
                points,
                [(0, 1, 2, 3)],
                m["clear"],
            )
        )
        objects.append(
            rectangular_beam(
                f"CALGARY_EntryLobby_Mullion_{index}",
                (x0, y0 - 0.025, 1.08),
                (x0, y0 - 0.025, top0),
                0.085,
                m["dark"],
                depth=0.12,
            )
        )
    for door_index, x in enumerate((-8.5, -3.8, 1.0, 5.8)):
        y = front_boundary_y(x, inset=0.32)
        objects.append(
            box(
                f"CALGARY_MainEntryDoor_{door_index}",
                (3.7, 0.12, 3.6),
                (x, y, 2.90),
                m["clear"],
                0.03,
            )
        )
        objects.append(
            box(
                f"CALGARY_MainEntryDoorFrame_{door_index}",
                (3.9, 0.18, 0.13),
                (x, y - 0.02, 4.72),
                m["dark"],
            )
        )
    objects.append(
        rectangular_beam(
            "CALGARY_LobbyEscalator",
            (-5.0, -17.0, 1.8),
            (8.0, -8.0, 8.1),
            0.62,
            m["dark"],
            depth=1.8,
        )
    )
    return objects


def interior_construction(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.append(
        ellipse_prism(
            "CALGARY_ConcreteTransitBridge",
            36.7,
            22.4,
            0.12,
            0.85,
            m["concrete"],
        )
    )
    for index, z in enumerate((5.28, 10.03, 14.78, 19.53)):
        objects.append(
            annular_plate(
                f"CALGARY_OccupiedFloorPlate_{index}",
                (36.0, 22.2),
                (10.5, 6.4),
                z,
                0.28,
                m["concrete"],
            )
        )
    for index, angle in enumerate(
        (0.25, 0.72, 1.24, 1.85, 2.45, 2.95, 3.48, 4.02, 4.55, 5.12, 5.65)
    ):
        x = 27.5 * math.cos(angle)
        y = 16.5 * math.sin(angle)
        objects.append(
            cylinder(
                f"CALGARY_InteriorColumn_{index}",
                0.29,
                20.5,
                (x, y, 10.90),
                m["concrete"],
                24,
            )
        )
    # Bounded physical contents add parallax behind the underlay/glass system.
    for floor, z in enumerate((2.0, 6.7, 11.45, 16.2, 20.65)):
        for bay, x in enumerate((-24.0, -15.5, 15.5, 24.0)):
            y = -11.0 + (floor % 2) * 2.4
            objects.append(
                box(
                    f"CALGARY_BookStack_{floor}_{bay}",
                    (4.8, 0.7, 2.1),
                    (x, y, z + 1.05),
                    m["warm"],
                    0.05,
                )
            )
    # The transit line passes below the shell at the east end.
    objects.extend(
        [
            box(
                "CALGARY_CTrainPortalShadow",
                (8.0, 25.0, 4.4),
                (30.5, 9.0, 2.2),
                m["dark"],
                0.4,
            ),
            box(
                "CALGARY_CTrainBridgePierWest",
                (2.0, 9.0, 5.8),
                (25.0, 10.0, 2.9),
                m["concrete"],
                0.18,
            ),
            box(
                "CALGARY_CTrainBridgePierEast",
                (2.0, 9.0, 5.8),
                (36.0, 10.0, 2.9),
                m["concrete"],
                0.18,
            ),
            box(
                "CALGARY_CTrainTrackBed",
                (6.0, 40.0, 0.24),
                (30.5, 7.0, 0.31),
                m["dark"],
            ),
        ]
    )
    return objects


def roof_construction(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    outer_a, outer_b = envelope_radius(24.35)
    inner_a, inner_b = 17.5, 7.4
    roof_triangles: list[tuple[tuple[float, float, float], ...]] = []
    roof_alt_triangles: list[tuple[tuple[float, float, float], ...]] = []
    clear_triangles: list[tuple[tuple[float, float, float], ...]] = []
    frit_triangles: list[tuple[tuple[float, float, float], ...]] = []
    for segment in range(SEGMENTS):
        t0 = 2.0 * math.pi * segment / SEGMENTS
        t1 = 2.0 * math.pi * (segment + 1) / SEGMENTS
        outer0 = (outer_a * math.cos(t0), outer_b * math.sin(t0), 24.30)
        outer1 = (outer_a * math.cos(t1), outer_b * math.sin(t1), 24.30)
        inner0 = (inner_a * math.cos(t0), inner_b * math.sin(t0), 24.88)
        inner1 = (inner_a * math.cos(t1), inner_b * math.sin(t1), 24.88)
        target = roof_alt_triangles if segment % 5 in {1, 4} else roof_triangles
        target.extend([(outer0, outer1, inner1), (outer0, inner1, inner0)])
        centre = (0.0, 0.0, 24.94 + 0.04 * math.cos(t0 * 2.0))
        glass_target = frit_triangles if segment % 4 == 0 else clear_triangles
        glass_target.append((inner0, inner1, centre))
        objects.append(
            rectangular_beam(
                f"CALGARY_RoofRadialFrame_{segment}",
                outer0,
                inner0,
                0.08,
                m["frame"],
            )
        )
        objects.append(
            rectangular_beam(
                f"CALGARY_SkylightFrame_{segment}",
                inner0,
                inner1,
                0.075,
                m["frame"],
            )
        )
    roof = mesh_group(
        "CALGARY_FacetedRoofField",
        roof_triangles,
        m["roof"],
        uv_scale=5.0,
    )
    roof_alt = mesh_group(
        "CALGARY_FacetedRoofIridescentPanels",
        roof_alt_triangles,
        m["opaque_alt"],
        uv_scale=5.0,
    )
    skylight = mesh_group(
        "CALGARY_CentralAtriumSkylight_Clear",
        clear_triangles,
        m["clear"],
    )
    skylight_frit = mesh_group(
        "CALGARY_CentralAtriumSkylight_Frit",
        frit_triangles,
        m["frit"],
    )
    if roof:
        objects.append(roof)
    if roof_alt:
        objects.append(roof_alt)
    if skylight:
        objects.append(skylight)
    if skylight_frit:
        objects.append(skylight_frit)
    objects.append(
        ellipse_prism(
            "CALGARY_AtriumRoofOccupiedDepth",
            15.9,
            6.2,
            24.30,
            24.42,
            m["interior"],
            segments=40,
        )
    )
    return objects


def public_realm(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    # Broad, shallow stairs rise into the carved opening without changing the
    # bottom-centre origin contract.
    for step in range(7):
        width = 64.0 - step * 2.0
        depth = 2.2 + step * 0.18
        height = 0.14 + step * 0.11
        objects.append(
            box(
                f"CALGARY_PublicEntryStep_{step}",
                (width, depth, height),
                (2.0, -29.6 + step * 0.52, height / 2),
                m["concrete"],
                0.04,
            )
        )
    for index, x in enumerate((-35.5, -30.0, 30.0, 35.5)):
        objects.append(
            box(
                f"CALGARY_PlazaBench_{index}",
                (3.6, 0.65, 0.48),
                (x, -30.0 + (index % 2) * 1.1, 0.24),
                m["cedar"],
                0.08,
            )
        )
    return objects


def fixed_landmark(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.extend(interior_construction(m))
    objects.extend(occupied_depth_underlay(m))
    envelope, _schedule = panel_envelope(m)
    objects.extend(envelope)
    objects.extend(cedar_arch_and_lobby(m))
    objects.extend(roof_construction(m))
    objects.extend(public_realm(m))

    # Joining disconnected pieces by system preserves names for the defining
    # assemblies while bounding runtime draw calls.
    for token, joined in (
        ("HexPanelJoint", "CALGARY_FiveFamilyUnitizedPanelJointSystem"),
        ("CedarBatten", "CALGARY_SurfaceFollowingCedarBattenSystem"),
        ("RoofRadialFrame", "CALGARY_FacetedRoofRadialSystem"),
        ("SkylightFrame", "CALGARY_AtriumSkylightFrameSystem"),
    ):
        objects = join_mesh_group(
            objects,
            lambda obj, value=token: value in obj.name,
            joined,
        )
    return objects


def fallback_module(
    role: str,
    variant: str,
    height: float,
    m: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    """Family-shaped modular fallback for imperfect user-drawn rectangles."""
    objects: list[bpy.types.Object] = []
    if role == "roof":
        objects.append(
            ellipse_prism(
                "CALGARYKIT_FacetedRoof",
                WIDTH / 2 - 1.0,
                DEPTH / 2 - 1.0,
                0.0,
                height,
                m["roof"],
                segments=24,
            )
        )
        objects.append(
            ellipse_prism(
                "CALGARYKIT_RoofSkylight",
                13.0,
                5.4,
                height - 0.08,
                height + 0.05,
                m["frit"],
                segments=24,
            )
        )
        return objects

    inset = 1.2 if role == "crown" else 0.0
    body = ellipse_prism(
        f"CALGARYKIT_{role}_{variant}_Envelope",
        WIDTH / 2 - inset,
        DEPTH / 2 - inset,
        0.0,
        height,
        m["opaque_alt"] if variant == "typical_b" else m["opaque"],
        segments=24,
    )
    objects.append(body)
    front_y = -(DEPTH / 2 - inset) - 0.04
    if role == "podium":
        objects.append(
            box(
                "CALGARYKIT_PodiumCedarVoid",
                (WIDTH * 0.70, 0.18, height * 0.70),
                (1.0, front_y, height * 0.42),
                m["cedar"],
                0.18,
            )
        )
        objects.append(
            box(
                "CALGARYKIT_PodiumGlazing",
                (WIDTH * 0.62, 0.12, height * 0.54),
                (4.0, front_y - 0.08, height * 0.40),
                m["clear"],
                0.04,
            )
        )
    else:
        columns = 11
        for index in range(columns):
            x0 = -WIDTH * 0.43 + index * WIDTH * 0.86 / columns
            pane_width = WIDTH * 0.86 / columns * 0.70
            glass = m["frit"] if (index + len(variant)) % 4 == 0 else m["clear"]
            objects.append(
                box(
                    f"CALGARYKIT_{role}_{variant}_Pane_{index}",
                    (pane_width, 0.12, height * 0.58),
                    (x0 + pane_width / 2, front_y - 0.08, height * 0.54),
                    glass,
                    0.03,
                )
            )
    return objects


def render_views(folder: Path, *, view_set: str) -> list[str]:
    setup_render()
    scene = bpy.context.scene
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    distance = max(WIDTH, DEPTH)
    views = {
        "preview": (
            (WIDTH * 0.70, -distance * 1.45, HEIGHT * 0.92),
            (0.0, -1.0, HEIGHT * 0.43),
            54,
        ),
        "street": (
            (0.0, -distance * 1.72, HEIGHT * 0.42),
            (0.0, -1.0, HEIGHT * 0.43),
            62,
        ),
        "front_corner_oblique": (
            (-WIDTH * 0.82, -distance * 1.33, HEIGHT * 0.80),
            (0.0, 0.0, HEIGHT * 0.43),
            54,
        ),
        "rear_corner_oblique": (
            (WIDTH * 0.76, distance * 1.48, HEIGHT * 0.84),
            (0.0, 0.0, HEIGHT * 0.44),
            55,
        ),
        "aerial": (
            (WIDTH * 0.72, -distance * 0.96, HEIGHT * 2.55),
            (0.0, 0.0, HEIGHT * 0.28),
            52,
        ),
        "facade_close": (
            (0.0, -distance * 1.20, HEIGHT * 0.40),
            (0.0, -4.0, HEIGHT * 0.43),
            67,
        ),
        "cedar_close": (
            (-WIDTH * 0.46, -distance * 0.64, HEIGHT * 0.28),
            (-18.0, -11.0, 5.7),
            61,
        ),
        "context": (
            (WIDTH * 0.16, -distance * 2.05, HEIGHT * 0.72),
            (0.0, 0.0, HEIGHT * 0.42),
            58,
        ),
    }
    selected = (
        {"preview", "street", "front_corner_oblique", "aerial", "cedar_close"}
        if view_set == "pilot"
        else set(views)
    )

    snapshots: list[tuple[bpy.types.Material, bpy.types.Node, float, float, str]] = []
    for mat in bpy.data.materials:
        if not mat.get("glazing_profile") or not mat.use_nodes:
            continue
        bsdf = next(
            (
                node
                for node in mat.node_tree.nodes
                if node.bl_idname == "ShaderNodeBsdfPrincipled"
            ),
            None,
        )
        if bsdf is None or not bsdf.inputs.get("Alpha"):
            continue
        transmission = bsdf.inputs.get("Transmission Weight")
        snapshots.append(
            (
                mat,
                bsdf,
                float(bsdf.inputs["Alpha"].default_value),
                float(transmission.default_value) if transmission else 0.0,
                getattr(mat, "surface_render_method", "DITHERED"),
            )
        )
        proof_alpha = 0.32 if mat.get("pane_treatment") == "graduated_ceramic_frit" else 0.22
        bsdf.inputs["Alpha"].default_value = proof_alpha
        mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], proof_alpha)
        if transmission:
            transmission.default_value = 0.0
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"

    rendered: list[str] = []
    try:
        for role, (location, target, lens) in views.items():
            if role not in selected:
                continue
            aim_camera(location, target, lens)
            filename = f"{FAMILY}_{role}.png"
            scene.render.filepath = str(folder / filename)
            bpy.ops.render.render(write_still=True)
            rendered.append(filename)
    finally:
        for mat, bsdf, alpha, transmission_value, method in snapshots:
            bsdf.inputs["Alpha"].default_value = alpha
            transmission = bsdf.inputs.get("Transmission Weight")
            if transmission:
                transmission.default_value = transmission_value
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = method
            mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], 1.0)
    delete_objects(
        [obj for obj in list(bpy.data.objects) if obj.name.startswith("PRESENTATION_")]
    )
    if (folder / "elevation.jpg").is_file():
        rendered.append("elevation.jpg")
    return rendered


def texture_inventory(skin: dict) -> list[dict]:
    inventory: list[dict] = []
    for zone, lods in skin["zones"].items():
        for lod, assets in lods.items():
            for channel, path in assets.items():
                inventory.append(
                    {
                        "key": f"{zone}_{lod}_{channel}",
                        "path": path,
                        "lod": lod,
                        "channel": channel,
                        "zone": zone,
                    }
                )
    return inventory


def module_payload(
    role: str,
    variant: str,
    filename: str,
    height: float,
    objects: list[bpy.types.Object],
    size_bytes: int,
    skin: dict,
) -> dict:
    repeatable = role == "floor"
    return {
        "role": role,
        "variant_key": variant,
        "assembly_class": "repeatable_middle" if repeatable else "fixed_semantic",
        "fixed_semantic": not repeatable,
        "lod": 0,
        "allowed_levels": [],
        "filename": filename,
        "module_family": FAMILY,
        "width_m": WIDTH,
        "depth_m": DEPTH,
        "height_m": height,
        "floor_height_m": FLOOR_HEIGHT,
        "repeatable_z": repeatable,
        "allow_inset_footprint": True,
        "triangle_count": triangle_count(objects),
        "material_count": len(
            {
                mat.name
                for obj in objects
                if obj.type == "MESH"
                for mat in obj.data.materials
            }
        ),
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
        "size_bytes": size_bytes,
    }


def facade_contract(skin: dict) -> dict:
    return {
        "schema": "facade-sheet@5",
        "source_directory": f"/families/{FAMILY}",
        "model": "gpt-image-2",
        "style_reference": "elevation.jpg",
        "goalpost_reference": CONFIG["goalpost"],
        "goalpost_policy": (
            "The catalogue archetype and architect/engineer dossier control the "
            "almond silhouette, 60/40 enclosure ratio, carved cedar arch, "
            "four-level occupied depth, transit bridge and faceted roof."
        ),
        "runtime_material_profile": "pbr_physical_glazing_v2",
        "geometry_detail_profile": "hero",
        "pbr_channels": [
            "albedo",
            "normal",
            "roughness",
            "ao",
            "depth",
            "emissive",
        ],
        "shadow_neutral": {"enabled": True, **skin["shadow_neutral"]},
        "bay_strategy": {
            "fixed_end_bays": [0, 3],
            "repeatable_middle_bays": [1, 2],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": (
                "The complete landmark stays fixed in-band; only the related "
                "fallback panel bands repeat for larger user footprints."
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": "physical unitized panels, cedar soffit and occupied depth",
            "far_usage": "city-scale render-locked archetype material reference",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "corner returns",
                "crown",
                "roof",
                "faceted almond envelope",
                "subtractive cedar arch",
                "transit bridge",
                "atrium skylight",
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "The unitized five-family panel graph and the almond shell wrap "
                "front, returns and rear; roof and cedar soffit are separate "
                "constructed surfaces."
            ),
            "elevation_coverage": {
                "front": "carved cedar arch, transparent lobby and crystalline panel field",
                "left": "rounded panel return and west cedar shoulder",
                "right": "rounded panel return and transit bridge expression",
                "rear": "related unitized panel schedule with quieter transparency",
                "roof": "faceted ring, perimeter pressure caps and atrium skylight",
            },
            "variation_policy": (
                "Mild independent X/Y scaling uses the fixed landmark; larger or "
                "more distorted hand drawings switch to the family-shaped stack "
                "and streetwall repeat."
            ),
        },
        "assets": {
            "skin_manifest": "textures/skin_manifest.json",
            "source": skin["source"],
            "near": skin["zones"]["facade"]["near"],
            "far": skin["zones"]["facade"]["far"],
            "sources": skin["sources"],
        },
        "reference_registration": skin["reference_registration"],
    }


def provenance() -> dict:
    return {
        "kind": "architect_dossier_plus_imagegen_reference_package_and_authored_geometry",
        "catalogue_archetype_id": ARCHETYPE_ID,
        "catalogue_variant_id": VARIANT_ID,
        "goalpost": CONFIG["goalpost"],
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "orthographic_elevation": "textures/source/elevation-source.png",
        "cedar_material_source": "textures/source/cedar-material-source.png",
        "reference_underlay": "textures/source/occupied-depth-source-v1.png",
        "reference_generation": "textures/source/reference-generation.json",
        "research_dossier": "textures/source/research-sources.json",
        "registered_openings": "textures/source/registered-openings.json",
        "registered_bands": "textures/source/registered-bands.json",
        "elevation_source": f"/families/{FAMILY}/elevation.jpg",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": "tools/archetype_compiler/generate_calgary_library_pilot.py",
        "reference_method": (
            "primary architect/enclosure/structure evidence, camera-registered "
            "orthographic goalpost, physical panel schedule, occupied-depth "
            "underlay and finite multi-angle visual comparison"
        ),
    }


def write_metadata(
    folder: Path,
    skin: dict,
    modules: list[dict],
    fixed_triangles: int,
    fixed_materials: int,
    assembled_path: Path,
    renders: list[str],
) -> None:
    footprint = {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": (
            "The native almond shell is authored inside the user's approximate "
            "rectangular envelope. Independent landmark scaling covers ordinary "
            "hand-drawn variation; larger targets repeat the related stack."
        ),
        "fixedLandmarkScaleBand": CONFIG["fixed_band"],
        **CONFIG["footprint"],
        "profiles": {"rectangle": CONFIG["footprint"]},
    }
    assembled = {
        "filename": assembled_path.name,
        "floors": NATIVE_FLOORS,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": HEIGHT,
        "triangle_count": fixed_triangles,
        "material_count": fixed_materials,
        "stack": [
            {
                "role": "assembled",
                "variant_key": "fixed_landmark",
                "level": 0,
                "z_m": 0.0,
                "height_m": HEIGHT,
            }
        ],
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": WIDTH,
            "depth_m": DEPTH,
            "wing_depth_m": DEPTH,
            "segments": [
                {
                    "id": "landmark",
                    "centre_x_m": 0.0,
                    "centre_y_m": 0.0,
                    "length_m": WIDTH,
                    "thickness_m": DEPTH,
                    "rotation_degrees": 0.0,
                }
            ],
        },
        "massing_graph": {
            "type": "fixed_landmark",
            "silhouette": "faceted_almond_over_transit",
        },
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    source = provenance()
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_calgary_library_pilot.py",
            "version": "1.0.0",
            "blender_version": bpy.app.version_string,
            "render_engine": "BLENDER_EEVEE",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": FAMILY,
        "archetype_id": ARCHETYPE_ID,
        "archetype_label": CONFIG["label"],
        "variant_id": VARIANT_ID,
        "generation_archetype_id": VARIANT_ID,
        "archetype_aliases": CONFIG["aliases"],
        "aesthetic_category_id": CONFIG["aesthetic_category_id"],
        "development_type": CONFIG["development_type"],
        "reuse_keys": CONFIG["reuse_keys"],
        "generation_tags": [
            "wave7_pilot",
            "civic_library",
            "fixed_landmark",
            "custom_pbr_skin",
            "physical_glazing",
            "reference_locked",
            *CONFIG["kits"],
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(skin),
        "massing_graph": {
            "type": "fixed_landmark",
            "silhouette": "faceted_almond_over_transit",
            "render_locked": True,
            "goalpost": CONFIG["goalpost"],
            "fallback": "family_shaped_modular_streetwall",
        },
        "material_budget": {
            "max_assembled_materials": 18,
            "rationale": (
                "Clear/fritted glass, occupied depth, aluminum panel variants, "
                "cedar, concrete, structure and roof remain semantically separate."
            ),
        },
        "dimensions": {
            "width_m": WIDTH,
            "depth_m": DEPTH,
            "podium_height_m": FLOOR_HEIGHT,
            "floor_height_m": FLOOR_HEIGHT,
            "setback_height_m": FLOOR_HEIGHT,
            "roof_height_m": 1.0,
            "crown_height_m": FLOOR_HEIGHT,
            "default_floors": NATIVE_FLOORS,
            "min_floors": 3,
            "max_floors": 5,
        },
        "native_width_m": WIDTH,
        "native_depth_m": DEPTH,
        "native_floors": NATIVE_FLOORS,
        "min_floors": 3,
        "max_floors": 5,
        "default_floors": NATIVE_FLOORS,
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{FAMILY}_preview.png",
        "renders": renders,
        "architectural_identity": CONFIG["identity"],
        "material_zones": CONFIG["materials"],
        "glass_profile": GLASS_PROFILE,
        "source_provenance": source,
    }
    (folder / f"{FAMILY}_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    grammar = {
        "family_id": FAMILY,
        "source": {
            "archetype_id": ARCHETYPE_ID,
            "variant_id": VARIANT_ID,
            "generation_archetype_id": VARIANT_ID,
            "reuse_keys": CONFIG["reuse_keys"],
        },
        "dimensions": manifest["dimensions"],
        "architectural_signature": {
            "identity": CONFIG["identity"],
            "material_zones": CONFIG["materials"],
            "glass_profile": GLASS_PROFILE,
            "kits": CONFIG["kits"],
        },
        "archetype_aliases": CONFIG["aliases"],
        "footprint_compatibility": footprint,
        "massing_graph": manifest["massing_graph"],
    }
    (folder / "grammar.json").write_text(
        json.dumps(grammar, indent=2) + "\n",
        encoding="utf-8",
    )
    (folder / "archetype-source.json").write_text(
        json.dumps(source, indent=2) + "\n",
        encoding="utf-8",
    )


def build(output_root: Path, *, view_set: str, skip_renders: bool, skip_modules: bool) -> None:
    clear_scene()
    folder = output_root / FAMILY
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(folder)
    fixed = fixed_landmark(mats)
    assembled_path = folder / f"{FAMILY}_assembled.glb"
    export_glb(assembled_path, fixed)
    fixed_triangles = triangle_count(fixed)
    fixed_materials = len(
        {
            mat.name
            for obj in fixed
            if obj.type == "MESH"
            for mat in obj.data.materials
        }
    )
    renders = (
        sorted(path.name for path in folder.glob(f"{FAMILY}_*.png"))
        if skip_renders
        else render_views(folder, view_set=view_set)
    )
    if skip_modules:
        print(
            f"[calgary-library-pilot] fixed only: {fixed_triangles:,} tris, "
            f"{fixed_materials} materials, {len(renders)} renders",
            flush=True,
        )
        return
    delete_objects(fixed)

    role_specs = [
        ("podium", "default", FLOOR_HEIGHT),
        ("floor", "typical_a", FLOOR_HEIGHT),
        ("floor", "typical_b", FLOOR_HEIGHT),
        ("floor", "typical_c", FLOOR_HEIGHT),
        ("crown", "crown", FLOOR_HEIGHT),
        ("roof", "default", 1.0),
    ]
    modules: list[dict] = []
    for role, variant, height in role_specs:
        objects = fallback_module(role, variant, height, mats)
        objects.extend(module_contract_markers(role, variant, height))
        filename = (
            f"{FAMILY}_{role}.glb"
            if variant == "default"
            else f"{FAMILY}_{role}_{variant}.glb"
        )
        path = folder / filename
        export_glb(path, objects)
        modules.append(
            module_payload(
                role,
                variant,
                filename,
                height,
                objects,
                path.stat().st_size,
                skin,
            )
        )
        delete_objects(objects)
    write_metadata(
        folder,
        skin,
        modules,
        fixed_triangles,
        fixed_materials,
        assembled_path,
        renders,
    )
    print(
        f"[calgary-library-pilot] {fixed_triangles:,} tris, "
        f"{len(modules)} modules, {len(renders)} renders",
        flush=True,
    )


def render_existing(output_root: Path, *, view_set: str) -> None:
    clear_scene()
    folder = output_root / FAMILY
    manifest_path = folder / f"{FAMILY}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.import_scene.gltf(
        filepath=str(folder / manifest["assembled"]["filename"])
    )
    manifest["renders"] = render_views(folder, view_set=view_set)
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"[calgary-library-render] {len(manifest['renders'])} renders",
        flush=True,
    )


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    if args.render_existing:
        render_existing(output_root, view_set=args.view_set)
    else:
        build(
            output_root,
            view_set=args.view_set,
            skip_renders=args.skip_renders,
            skip_modules=args.skip_modules,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
