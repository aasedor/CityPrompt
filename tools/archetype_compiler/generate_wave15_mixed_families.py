"""Generate the ten reference-locked Wave 15 LEGO building families.

Each family ships as a fixed whole-building landmark plus six semantic fallback
modules.  The fixed landmark owns the reviewed silhouette and construction;
the fallback repeats complete bays so approximate user footprints do not
stretch entrances, long-span roofs, glazing, structure, or ornament.

Run from the repository root with Blender 5.x::

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave15_mixed_families.py -- \
      --family copenhill-ski-slope-energy-plant --view-set pilot
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

import generate_wave14_variant_families as core  # noqa: E402
from wave15_mixed_specs import FAMILIES, with_family  # noqa: E402


_CORE_LOAD_PALETTE = core.load_palette
_CORE_VIEW_MAP = core.view_map


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("frontend/public/families"),
    )
    parser.add_argument(
        "--view-set",
        choices=(
            "preview",
            "pilot",
            "assessment",
            "all",
            "street",
            "context",
            "front_elevation",
            "front_corner_oblique",
            "rear_corner_oblique",
            "aerial",
            "facade_close",
        ),
        default="all",
    )
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-modules", action="store_true")
    parser.add_argument("--skip-assembled-export", action="store_true")
    parser.add_argument("--render-existing", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def load_palette(folder: Path, cfg: dict) -> tuple[dict[str, bpy.types.Material], dict]:
    mats, skin = _CORE_LOAD_PALETTE(folder, cfg)
    for key, (_description, rgb, kind) in cfg["palette"].items():
        material = mats[key]
        material["wave15_reference_locked_material"] = True
        material["coverage_cohort"] = cfg["cohort"]
        if kind == "glass" and key != "glass":
            tint = tuple(channel / 255.0 for channel in rgb)
            core.configure_glass(
                material,
                cfg,
                tint=tint,
                transmission=0.42,
                alpha=0.52,
            )
    for material in mats.values():
        material["wave15_reference_locked_material"] = True
        material["coverage_cohort"] = cfg["cohort"]
    if cfg["shape"] == "ski_slope_energy_plant":
        mats["aluminum_dark"] = core.grade_material(
            mats["primary"].copy(), saturation=0.78, value=0.47
        )
        mats["aluminum_dark"].name = f"MAT_W15_{cfg['family']}_AluminumDark"
        mats["aluminum_mid"] = core.grade_material(
            mats["primary"].copy(), saturation=0.86, value=0.72
        )
        mats["aluminum_mid"].name = f"MAT_W15_{cfg['family']}_AluminumMid"
        mats["concrete"] = core.material(
            f"MAT_W15_{cfg['family']}_PaleConcrete",
            (0.38, 0.39, 0.38, 1.0),
            0.84,
        )
        mats["ski_light"] = core.grade_material(
            mats["secondary"].copy(), saturation=0.92, value=1.10
        )
        mats["ski_light"].name = f"MAT_W15_{cfg['family']}_SkiLight"
        mats["plant_dark"] = core.grade_material(
            mats["secondary"].copy(), saturation=1.08, value=0.66
        )
        mats["plant_dark"].name = f"MAT_W15_{cfg['family']}_PlantDark"
        mats["path"] = core.material(
            f"MAT_W15_{cfg['family']}_AggregatePath",
            (0.48, 0.45, 0.38, 1.0),
            0.92,
        )
        for key, colour in {
            "hold_red": (0.62, 0.08, 0.035, 1.0),
            "hold_yellow": (0.92, 0.49, 0.035, 1.0),
            "hold_blue": (0.035, 0.22, 0.56, 1.0),
            "hold_green": (0.08, 0.42, 0.16, 1.0),
        }.items():
            mats[key] = core.material(
                f"MAT_W15_{cfg['family']}_{key}", colour, 0.42
            )
        for key in (
            "aluminum_dark",
            "aluminum_mid",
            "concrete",
            "ski_light",
            "plant_dark",
            "path",
            "hold_red",
            "hold_yellow",
            "hold_blue",
            "hold_green",
        ):
            mats[key]["wave15_reference_locked_material"] = True
            mats[key]["coverage_cohort"] = cfg["cohort"]
    if cfg["shape"] == "deconstructivist_fire_station":
        # Preserve the authored fibre-cement skin while restoring the strong
        # charcoal/concrete contrast visible in the reference sheet.
        mats["charcoal_dark"] = core.grade_material(
            mats["secondary"].copy(), saturation=0.92, value=0.42
        )
        mats["charcoal_dark"].name = f"MAT_W15_{cfg['family']}_CharcoalFibreCementDark"
        mats["charcoal_dark"]["wave15_reference_locked_material"] = True
        mats["charcoal_dark"]["coverage_cohort"] = cfg["cohort"]
    if cfg["shape"] == "titanium_fold_museum":
        mats["titanium_mid"] = core.grade_material(
            mats["primary"].copy(), saturation=0.82, value=0.70
        )
        mats["titanium_mid"].name = f"MAT_W15_{cfg['family']}_PerforatedTitaniumMid"
        mats["titanium_mid"]["wave15_reference_locked_material"] = True
        mats["titanium_mid"]["coverage_cohort"] = cfg["cohort"]
    return mats, skin


def view_map(cfg: dict) -> dict[str, tuple[tuple[float, float, float], tuple[float, float, float], float]]:
    views = _CORE_VIEW_MAP(cfg)
    if cfg["shape"] == "ski_slope_energy_plant":
        views.update(
            {
                "preview": ((145.0, -235.0, 78.0), (0.0, 0.0, 32.0), 50),
                "front_corner_oblique": ((128.0, -220.0, 66.0), (0.0, -4.0, 31.0), 58),
                "aerial": ((125.0, -102.0, 220.0), (0.0, 0.0, 24.0), 54),
                "facade_close": ((85.0, -132.0, 35.0), (10.0, -32.0, 27.0), 62),
            }
        )
    return views


def add_mesh(
    objects: list[bpy.types.Object],
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    *,
    role: str = "assembled",
) -> bpy.types.Object:
    return core.create_mesh_object(
        objects, name, vertices, faces, mat, cfg, semantic, role=role
    )


def add_wedge_x(
    objects: list[bpy.types.Object],
    *,
    name: str,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    base_z: float,
    top_z0: float,
    top_z1: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    role: str = "assembled",
) -> bpy.types.Object:
    vertices = [
        (x0, y0, base_z),
        (x1, y0, base_z),
        (x1, y1, base_z),
        (x0, y1, base_z),
        (x0, y0, top_z0),
        (x1, y0, top_z1),
        (x1, y1, top_z1),
        (x0, y1, top_z0),
    ]
    faces = [
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]
    return add_mesh(objects, name, vertices, faces, mat, cfg, semantic, role=role)


def add_slope_plate_x(
    objects: list[bpy.types.Object],
    *,
    name: str,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    role: str = "assembled",
) -> bpy.types.Object:
    vertices = [
        (x0, y0, z0 - thickness),
        (x1, y0, z1 - thickness),
        (x1, y1, z1 - thickness),
        (x0, y1, z0 - thickness),
        (x0, y0, z0),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z0),
    ]
    faces = [
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]
    return add_mesh(objects, name, vertices, faces, mat, cfg, semantic, role=role)


def add_extruded_footprint(
    objects: list[bpy.types.Object],
    *,
    name: str,
    footprint: list[tuple[float, float]],
    base_z: float,
    top_z: float | list[float],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    role: str = "assembled",
) -> bpy.types.Object:
    count = len(footprint)
    tops = [float(top_z)] * count if isinstance(top_z, (float, int)) else top_z
    vertices = [(x, y, base_z) for x, y in footprint] + [
        (x, y, tops[index]) for index, (x, y) in enumerate(footprint)
    ]
    faces: list[tuple[int, ...]] = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    return add_mesh(objects, name, vertices, faces, mat, cfg, semantic, role=role)


def add_cone(
    objects: list[bpy.types.Object],
    *,
    name: str,
    radius_bottom: float,
    radius_top: float,
    depth: float,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    vertices_count: int = 16,
    role: str = "assembled",
) -> bpy.types.Object:
    cx, cy, cz = location
    points: list[tuple[float, float, float]] = []
    for z, radius in ((cz - depth / 2, radius_bottom), (cz + depth / 2, radius_top)):
        for index in range(vertices_count):
            angle = math.tau * index / vertices_count
            points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius, z))
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(vertices_count))),
        tuple(range(vertices_count, vertices_count * 2)),
    ]
    for index in range(vertices_count):
        nxt = (index + 1) % vertices_count
        faces.append((index, nxt, vertices_count + nxt, vertices_count + index))
    return add_mesh(objects, name, points, faces, mat, cfg, semantic, role=role)


def add_revolved_profile(
    objects: list[bpy.types.Object],
    *,
    name: str,
    centre: tuple[float, float],
    profile: list[tuple[float, float]],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    segments: int = 32,
) -> bpy.types.Object:
    cx, cy = centre
    vertices: list[tuple[float, float, float]] = []
    for z, radius in profile:
        for segment in range(segments):
            angle = math.tau * segment / segments
            vertices.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius, z))
    faces: list[tuple[int, ...]] = []
    for ring in range(len(profile) - 1):
        for segment in range(segments):
            nxt = (segment + 1) % segments
            a = ring * segments + segment
            b = ring * segments + nxt
            c = (ring + 1) * segments + nxt
            d = (ring + 1) * segments + segment
            faces.append((a, b, c, d))
    faces.append(tuple(reversed(range(segments))))
    top = (len(profile) - 1) * segments
    faces.append(tuple(top + index for index in range(segments)))
    return add_mesh(objects, name, vertices, faces, mat, cfg, semantic)


def add_vertical_disk_y(
    objects: list[bpy.types.Object],
    *,
    name: str,
    centre: tuple[float, float, float],
    radius: float,
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    role: str = "assembled",
    segments: int = 24,
) -> bpy.types.Object:
    cx, cy, cz = centre
    vertices: list[tuple[float, float, float]] = []
    for y in (cy - thickness / 2, cy + thickness / 2):
        vertices.append((cx, y, cz))
        for index in range(segments):
            angle = math.tau * index / segments
            vertices.append((cx + math.cos(angle) * radius, y, cz + math.sin(angle) * radius))
    stride = segments + 1
    faces: list[tuple[int, ...]] = []
    for side in range(2):
        base = side * stride
        for index in range(segments):
            nxt = (index + 1) % segments
            faces.append((base, base + 1 + index, base + 1 + nxt))
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.append((1 + index, 1 + nxt, stride + 1 + nxt, stride + 1 + index))
    return add_mesh(objects, name, vertices, faces, mat, cfg, semantic, role=role)


def add_arch_ring_x(
    objects: list[bpy.types.Object],
    *,
    name: str,
    centre_y: float,
    facade_x: float,
    spring_z: float,
    inner_radius: float,
    ring_width: float,
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
    segments: int = 20,
) -> bpy.types.Object:
    """Physical semicircular ring for side-facing arcades."""
    outer = inner_radius + ring_width
    vertices: list[tuple[float, float, float]] = []
    for x in (facade_x - thickness / 2, facade_x + thickness / 2):
        for radius in (inner_radius, outer):
            for index in range(segments + 1):
                angle = math.pi * index / segments
                vertices.append((x, centre_y + math.cos(angle) * radius, spring_z + math.sin(angle) * radius))
    stride = segments + 1
    faces: list[tuple[int, ...]] = []
    for side in range(2):
        base = side * stride * 2
        for index in range(segments):
            if side == 0:
                faces.append((base + index, base + stride + index, base + stride + index + 1, base + index + 1))
            else:
                faces.append((base + index, base + index + 1, base + stride + index + 1, base + stride + index))
    for radius_index in range(2):
        front = radius_index * stride
        back = stride * 2 + radius_index * stride
        for index in range(segments):
            faces.append((front + index, front + index + 1, back + index + 1, back + index))
    faces.extend(((0, stride, stride * 3, stride * 2), (segments, stride + segments, stride * 3 + segments, stride * 2 + segments)))
    return add_mesh(objects, name, vertices, faces, mat, cfg, "physical_side_arch_ring", role=role)


def add_polyline_beams(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    points: list[tuple[float, float, float]],
    radius: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    role: str = "assembled",
) -> None:
    for index, (start, end) in enumerate(zip(points, points[1:])):
        core.add_beam(
            objects,
            f"{prefix}_{index}",
            start,
            end,
            radius,
            mat,
            cfg,
            semantic,
            role=role,
        )


def add_path_ribbon(
    objects: list[bpy.types.Object],
    *,
    name: str,
    points: list[tuple[float, float, float]],
    width: float,
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for z_offset in (-thickness, 0.0):
        for index, point in enumerate(points):
            previous = Vector(points[max(0, index - 1)])
            following = Vector(points[min(len(points) - 1, index + 1)])
            tangent = following - previous
            normal = Vector((-tangent.y, tangent.x, 0.0)).normalized()
            for side in (-1.0, 1.0):
                vertices.append(
                    (
                        point[0] + normal.x * width / 2 * side,
                        point[1] + normal.y * width / 2 * side,
                        point[2] + z_offset,
                    )
                )
    layer = len(points) * 2
    faces: list[tuple[int, ...]] = []
    for index in range(len(points) - 1):
        base = index * 2
        faces.append((base, base + 2, base + 3, base + 1))
        top = layer + base
        faces.append((top, top + 1, top + 3, top + 2))
        faces.append((base, layer + base, layer + base + 2, base + 2))
        faces.append((base + 1, base + 3, layer + base + 3, layer + base + 1))
    faces.append((0, 1, layer + 1, layer))
    end = (len(points) - 1) * 2
    faces.append((end, layer + end, layer + end + 1, end + 1))
    return add_mesh(objects, name, vertices, faces, mat, cfg, semantic)


def add_guard_run(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    posts: int,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
) -> None:
    core.add_beam(objects, prefix + "_TopRail", start, end, 0.075, mat, cfg, "open_guard_top_rail", role=role)
    a, b = Vector(start), Vector(end)
    for index in range(posts + 1):
        point = a.lerp(b, index / posts)
        core.add_beam(
            objects,
            f"{prefix}_Post_{index}",
            (point.x, point.y, point.z - 1.05),
            tuple(point),
            0.055,
            mat,
            cfg,
            "open_guard_post",
            role=role,
        )


def build_ski_slope_energy_plant(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    x0, x1 = -80.0, 80.0
    y0, y1 = -34.0, 34.0
    low_z, high_z = 18.0, 61.0
    add_wedge_x(
        objects,
        name="WTE_ProcessEnvelope",
        x0=x0,
        x1=x1,
        y0=y0,
        y1=y1,
        base_z=0.0,
        top_z0=low_z,
        top_z1=high_z,
        mat=mats["primary"],
        cfg=cfg,
        semantic="complete_sloped_process_envelope",
    )
    core.add_box(objects, "WTE_ConcreteProcessBase", (158.0, 68.5, 6.5), (0.0, 0.0, 3.25), mats["concrete"], cfg, "continuous_exposed_concrete_process_plinth")
    add_slope_plate_x(
        objects,
        name="WTE_ContinuousSkiSlope",
        x0=-80.5,
        x1=80.5,
        y0=-32.2,
        y1=32.2,
        z0=18.35,
        z1=61.35,
        thickness=0.42,
        mat=mats["secondary"],
        cfg=cfg,
        semantic="continuous_inhabited_three_gradient_ski_roof",
    )
    # A physical 3.3 m horizontal by 1.2 m vertical cassette field makes the
    # long public elevation read at construction scale instead of as one image.
    panel_groups: dict[int, tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]] = {
        index: ([], []) for index in range(3)
    }
    perforation_vertices: list[tuple[float, float, float]] = []
    perforation_faces: list[tuple[int, ...]] = []
    panel_w, panel_h = 3.25, 1.18
    column_count = 48
    for column in range(column_count):
        px0 = x0 + 1.8 + column * (156.4 / column_count)
        px1 = px0 + panel_w * 0.91
        local_top = low_z + (high_z - low_z) * ((px0 + 80.0) / 160.0) - 0.8
        rows = max(1, int((local_top - 7.0) / panel_h))
        for row in range(rows):
            pz0 = 6.8 + row * panel_h
            pz1 = min(local_top, pz0 + panel_h * 0.91)
            if pz1 <= pz0:
                continue
            tone = (column * 5 + row * 3 + (row // 3)) % 3
            vertices, faces = panel_groups[tone]
            relief = (0.12, 0.25, 0.38)[tone]
            front_y = y0 - relief
            back_y = y0 - 0.04
            base = len(vertices)
            vertices.extend(
                [
                    (px0, back_y, pz0), (px1, back_y, pz0),
                    (px1, back_y, pz1), (px0, back_y, pz1),
                    (px0, front_y, pz0), (px1, front_y, pz0),
                    (px1, front_y, pz1), (px0, front_y, pz1),
                ]
            )
            faces.extend(
                [
                    (base, base + 3, base + 2, base + 1),
                    (base + 4, base + 5, base + 6, base + 7),
                    (base, base + 1, base + 5, base + 4),
                    (base + 1, base + 2, base + 6, base + 5),
                    (base + 2, base + 3, base + 7, base + 6),
                    (base + 3, base, base + 4, base + 7),
                ]
            )
            rear_base = len(vertices)
            rear_back_y = y1 + 0.04
            rear_front_y = y1 + relief
            vertices.extend(
                [
                    (px0, rear_back_y, pz0), (px1, rear_back_y, pz0),
                    (px1, rear_back_y, pz1), (px0, rear_back_y, pz1),
                    (px0, rear_front_y, pz0), (px1, rear_front_y, pz0),
                    (px1, rear_front_y, pz1), (px0, rear_front_y, pz1),
                ]
            )
            faces.extend(
                [
                    (rear_base, rear_base + 1, rear_base + 2, rear_base + 3),
                    (rear_base + 4, rear_base + 7, rear_base + 6, rear_base + 5),
                    (rear_base, rear_base + 4, rear_base + 5, rear_base + 1),
                    (rear_base + 1, rear_base + 5, rear_base + 6, rear_base + 2),
                    (rear_base + 2, rear_base + 6, rear_base + 7, rear_base + 3),
                    (rear_base + 3, rear_base + 7, rear_base + 4, rear_base),
                ]
            )
            if tone == 2:
                for dot_x in range(4):
                    for dot_z in range(2):
                        cx = px0 + (dot_x + 0.5) * (px1 - px0) / 4
                        cz = pz0 + (dot_z + 0.5) * (pz1 - pz0) / 2
                        half = 0.075
                        for dot_y in (front_y - 0.012, rear_front_y + 0.012):
                            dot_base = len(perforation_vertices)
                            perforation_vertices.extend(
                                [
                                    (cx - half, dot_y, cz - half),
                                    (cx + half, dot_y, cz - half),
                                    (cx + half, dot_y, cz + half),
                                    (cx - half, dot_y, cz + half),
                                ]
                            )
                            perforation_faces.append((dot_base, dot_base + 1, dot_base + 2, dot_base + 3))
    for tone, material_key in enumerate(("primary", "aluminum_mid", "aluminum_dark")):
        vertices, faces = panel_groups[tone]
        add_mesh(objects, f"WTE_AluminumBoxCassetteField_{tone}", vertices, faces, mats[material_key], cfg, "metric_overlapping_aluminum_box_cassettes")
    add_mesh(objects, "WTE_PerforatedCassetteApertures", perforation_vertices, perforation_faces, mats["frame"], cfg, "physical_perforation_shadow_field")
    # Visitor lobby at the low end, with physical pane, cap grid and occupied depth.
    lobby_start = len(objects)
    core.add_window_band_y(objects, prefix="WTE_VisitorLobby", width=31.0, facade_y=y0 - 0.48, centre_z=9.1, height=11.4, bays=7, outward_sign=-1.0, mats=mats, cfg=cfg, margin=0.2)
    for obj in objects[lobby_start:]:
        obj.location.x -= 61.5
    core.add_window_band_x(objects, prefix="WTE_LowEndVisitorHall", depth=57.0, facade_x=x0 - 0.12, centre_z=9.0, height=13.2, bays=12, outward_sign=-1.0, mats=mats, cfg=cfg, margin=0.2)
    for index in range(4):
        core.add_box(objects, f"WTE_VisitorCanopy_{index}", (7.0, 5.0, 0.28), (-68.0 + index * 7.0, y0 - 2.3, 5.8 + index * 0.18), mats["frame"], cfg, "integrated_low_end_visitor_canopy")
    # The climbing wall is a recessed construction field with hundreds of
    # visible holds, not a bright rectangle pasted on top of the cassette skin.
    core.add_box(objects, "WTE_ClimbingWallBacking", (34.0, 0.42, 39.0), (50.0, y0 - 0.54, 29.0), mats["concrete"], cfg, "integrated_eighty_five_metre_climbing_wall")
    hold_colours = (mats["hold_red"], mats["hold_yellow"], mats["hold_blue"], mats["hold_green"])
    for row in range(15):
        for column in range(11):
            x = 34.5 + column * 3.05 + math.sin(row * 1.7 + column) * 0.55
            z = 10.5 + row * 2.45 + math.sin(column * 0.9) * 0.45
            core.add_sphere(objects, f"WTE_ClimbingHold_{row}_{column}", 0.16 + ((row + column) % 3) * 0.035, (x, y0 - 0.72, z), hold_colours[(row + column) % len(hold_colours)], cfg, "physical_colour_coded_climbing_hold", scale=(1.25, 0.55, 0.8))
    # Three roof gradients and the winding public path are explicit thin layers.
    slope = (high_z - low_z) / (x1 - x0)
    for suffix, band_y0, band_y1, material_key in (
        ("MainRun", -23.5, -7.0, "ski_light"),
        ("TrainingRun", -4.5, 8.5, "secondary"),
        ("PlantedShoulder", 11.0, 28.0, "plant_dark"),
    ):
        add_slope_plate_x(
            objects,
            name=f"WTE_RoofBand_{suffix}",
            x0=-76.0,
            x1=76.0,
            y0=band_y0,
            y1=band_y1,
            z0=low_z + 1.42,
            z1=high_z + 1.42,
            thickness=0.16,
            mat=mats[material_key],
            cfg=cfg,
            semantic="physically_separate_inhabited_roof_program_band",
        )
    path_points: list[tuple[float, float, float]] = []
    for index in range(17):
        x = -75.0 + index * 9.2
        y = 20.0 + 6.0 * math.sin(index * 0.72)
        z = low_z + (x + 80.0) * slope + 1.72
        path_points.append((x, y, z))
    add_path_ribbon(objects, name="WTE_PublicRoofPath", points=path_points, width=2.6, thickness=0.14, mat=mats["path"], cfg=cfg, semantic="flat_meandering_public_roof_path")
    for index, (x, y, z) in enumerate(path_points[1:-1]):
        for side in (-1.0, 1.0):
            plant_y = y + side * (2.3 + (index % 3) * 0.45)
            core.add_sphere(
                objects,
                f"WTE_RoofPlant_{index}_{side:+.0f}",
                0.42 + (index % 4) * 0.08,
                (x + side * 0.35, plant_y, z + 0.10),
                mats["plant_dark" if (index + int(side)) % 2 else "secondary"],
                cfg,
                "physical_low_roof_landscape_planting",
                scale=(1.8, 1.1, 0.55),
            )
    lift_points: list[tuple[float, float, float]] = []
    for lift_index in range(9):
        x = -69.0 + lift_index * 17.2
        z = low_z + (x + 80.0) * slope + 1.55
        lift_points.append((x, -15.0, z + 3.1))
        core.add_cylinder(objects, f"WTE_SkiLiftPylon_{lift_index}", 0.16, 3.0, (x, -15.0, z + 1.5), mats["frame"], cfg, "working_ski_lift_pylon", vertices=10)
        core.add_beam(objects, f"WTE_SkiLiftCrossbar_{lift_index}", (x, -17.2, z + 3.0), (x, -12.8, z + 3.0), 0.09, mats["frame"], cfg, "ski_lift_crossbar")
    add_polyline_beams(objects, prefix="WTE_SkiLiftCable", points=lift_points, radius=0.035, mat=mats["frame"], cfg=cfg, semantic="continuous_ski_lift_cable")
    for side, y in (("Front", y0 - 0.30), ("Rear", y1 + 0.30)):
        start = (x0 + 1.0, y, low_z + 1.45)
        end = (x1 - 1.0, y, high_z + 1.45)
        add_guard_run(objects, prefix=f"WTE_{side}SlopeGuard", start=start, end=end, posts=34, mat=mats["frame"], cfg=cfg)
    # Summit plant, glass elevator and the separate faceted emissions stack.
    core.add_box(objects, "WTE_SummitProcessDeck", (25.0, 42.0, 7.2), (67.0, 4.0, 64.9), mats["frame"], cfg, "occupied_summit_process_equipment")
    for index in range(4):
        core.add_cylinder(objects, f"WTE_SummitDuct_{index}", 0.85 + index * 0.10, 5.0, (58.0 + index * 5.4, 6.0, 71.0), mats["frame"], cfg, "summit_process_duct", vertices=12)
    core.add_box(objects, "WTE_GlassElevatorDepth", (5.2, 6.0, 57.0), (73.0, -25.5, 34.5), mats["interior"], cfg, "summit_elevator_occupied_depth")
    core.add_box(objects, "WTE_GlassElevator", (5.6, 6.4, 57.0), (73.0, -25.5, 34.5), mats["glass"], cfg, "transparent_slope_access_elevator")
    for z in range(8, 64, 5):
        core.add_box(objects, f"WTE_ElevatorRail_{z}", (5.9, 6.7, 0.16), (73.0, -25.5, float(z)), mats["frame"], cfg, "physical_elevator_floor_datum")
    add_cone(objects, name="WTE_FacetedStackBase", radius_bottom=4.4, radius_top=3.2, depth=18.0, location=(63.0, 23.5, 67.0), mat=mats["roof"], cfg=cfg, semantic="faceted_white_emissions_stack", vertices_count=10)
    add_cone(objects, name="WTE_FacetedStack", radius_bottom=3.2, radius_top=2.25, depth=9.0, location=(63.0, 23.5, 80.5), mat=mats["roof"], cfg=cfg, semantic="faceted_white_emissions_stack", vertices_count=10)
    core.add_cylinder(objects, "WTE_StackDarkOpening", 1.8, 0.45, (63.0, 23.5, 85.15), mats["frame"], cfg, "open_stack_terminal", vertices=20)
    return objects


def wave_shell_height(x: float, y: float, *, width: float, depth: float) -> float:
    nx = max(-1.0, min(1.0, x / (width / 2)))
    ny = max(-1.0, min(1.0, y / (depth / 2)))
    crest = 1.0 - ((nx + 0.12) / 1.12) ** 2
    crest = max(0.0, crest)
    longitudinal = 0.84 + 0.08 * math.cos(ny * math.pi)
    return 7.8 + 26.0 * crest * longitudinal + 2.8 * (ny + 1.0) / 2.0


def add_wave_shell(
    objects: list[bpy.types.Object],
    *,
    name: str,
    width: float,
    depth: float,
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
    x_segments: int = 28,
    y_segments: int = 12,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for offset in (-thickness, 0.0):
        for yi in range(y_segments + 1):
            y = -depth / 2 + depth * yi / y_segments
            for xi in range(x_segments + 1):
                x = -width / 2 + width * xi / x_segments
                vertices.append((x, y, wave_shell_height(x, y, width=width, depth=depth) + offset))
    stride = x_segments + 1
    layer_size = stride * (y_segments + 1)
    faces: list[tuple[int, ...]] = []
    for layer in range(2):
        base = layer * layer_size
        for yi in range(y_segments):
            for xi in range(x_segments):
                a = base + yi * stride + xi
                quad = (a, a + 1, a + stride + 1, a + stride)
                faces.append(tuple(reversed(quad)) if layer == 0 else quad)
    # Close all four shell edges so the polycarbonate has visible thickness.
    for xi in range(x_segments):
        low_a = xi
        low_b = xi + 1
        high_a = layer_size + low_a
        high_b = layer_size + low_b
        faces.append((low_a, high_a, high_b, low_b))
        back_a = y_segments * stride + xi
        back_b = back_a + 1
        faces.append((back_a, back_b, layer_size + back_b, layer_size + back_a))
    for yi in range(y_segments):
        left_a = yi * stride
        left_b = (yi + 1) * stride
        faces.append((left_a, left_b, layer_size + left_b, layer_size + left_a))
        right_a = yi * stride + x_segments
        right_b = (yi + 1) * stride + x_segments
        faces.append((right_a, layer_size + right_a, layer_size + right_b, right_b))
    return add_mesh(objects, name, vertices, faces, mat, cfg, "continuous_double_curved_wave_shell", role=role)


def build_wave_shell_natatorium(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    width, depth = 82.0, 56.0
    core.add_box(objects, "NAT_ConcretePoolPlinth", (80.0, 54.0, 5.6), (0.0, 0.0, 2.8), mats["secondary"], cfg, "continuous_board_formed_pool_hall_plinth")
    # The glazed front and rear sit inside the shell edge; their occupied layer
    # reveals the blue pool hall while the exterior pane remains neutral.
    for y, sign, face in ((-27.45, -1.0, "Front"), (27.45, 1.0, "Rear")):
        core.add_window_band_y(objects, prefix=f"NAT_{face}PoolHall", width=68.0, facade_y=y, centre_z=10.0, height=12.4, bays=12, outward_sign=sign, mats=mats, cfg=cfg, margin=0.2)
        for index, x in enumerate((-35.0, -27.5, 27.5, 35.0)):
            top_z = wave_shell_height(x, y, width=width, depth=depth) - 0.5
            core.add_beam(objects, f"NAT_{face}ConcreteStrut_{index}", (x * 0.86, y + sign * 0.4, 5.4), (x, y + sign * 0.2, top_z), 0.52, mats["secondary"], cfg, "branching_concrete_shell_strut")
    # Secondary glazing completes the transparent pool enclosure.
    for x, sign, face in ((-40.4, -1.0, "Left"), (40.4, 1.0, "Right")):
        core.add_window_band_x(objects, prefix=f"NAT_{face}PoolHall", depth=48.0, facade_x=x, centre_z=8.6, height=9.8, bays=10, outward_sign=sign, mats=mats, cfg=cfg, margin=0.3)
    # Blue water, deck and diving block silhouettes are physical interior depth.
    core.add_box(objects, "NAT_MainPoolWater", (52.0, 20.0, 0.22), (0.0, 2.5, 5.92), mats["glass"], cfg, "visible_blue_pool_water_plane")
    core.add_box(objects, "NAT_PoolDeck", (70.0, 33.0, 0.22), (0.0, 2.5, 5.70), mats["ornament"], cfg, "pale_terrazzo_pool_deck")
    for index in range(6):
        core.add_box(objects, f"NAT_LaneLine_{index}", (0.10, 18.5, 0.08), (-20.0 + index * 8.0, 2.5, 6.08), mats["frame"], cfg, "visible_pool_lane_line")
    add_wave_shell(objects, name="NAT_ContinuousWaveShell", width=82.0, depth=56.0, thickness=0.44, mat=mats["primary"], cfg=cfg)
    # Transverse ribs follow the exact shell equation.
    for rib_index in range(11):
        y = -25.5 + rib_index * 5.1
        points = []
        for step in range(21):
            x = -40.0 + step * 4.0
            points.append((x, y, wave_shell_height(x, y, width=width, depth=depth) + 0.22))
        add_polyline_beams(objects, prefix=f"NAT_RoofRib_{rib_index}", points=points, radius=0.19, mat=mats["frame"], cfg=cfg, semantic="continuous_wave_shell_roof_rib")
    # Twin masts and stays visibly terminate at shell nodes.
    for side, x in (("Left", -34.0), ("Right", 34.0)):
        mast_name = f"NAT_MainCableMast_{side}"
        core.add_beam(objects, mast_name, (x, -17.0, 5.4), (x, -17.0, 34.5), 0.42, mats["secondary"], cfg, "grounded_cable_stay_mast")
        for index, y in enumerate((-23.0, -11.5, 0.0, 11.5, 23.0)):
            target_x = x * 0.72
            target_z = wave_shell_height(target_x, y, width=width, depth=depth) + 0.3
            core.add_beam(objects, f"NAT_Stay_{side}_{index}", (x, -17.0, 33.6), (target_x, y, target_z), 0.065, mats["ornament"], cfg, "tension_cable_to_shell_node")
    # Entry canopy is held by the same front strut datum.
    core.add_box(objects, "NAT_EntryCanopy", (24.0, 7.0, 0.38), (0.0, -30.0, 7.0), mats["roof"], cfg, "integrated_pool_hall_entry_canopy")
    core.add_window_band_y(objects, prefix="NAT_Entry", width=11.0, facade_y=-28.6, centre_z=4.0, height=5.0, bays=4, outward_sign=-1.0, mats=mats, cfg=cfg, margin=0.1)
    return objects


def add_mansard_roof(
    objects: list[bpy.types.Object],
    *,
    name: str,
    width: float,
    depth: float,
    base_z: float,
    height: float,
    inset: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
) -> bpy.types.Object:
    lower = [
        (-width / 2, -depth / 2),
        (width / 2, -depth / 2),
        (width / 2, depth / 2),
        (-width / 2, depth / 2),
    ]
    upper = [
        (-width / 2 + inset, -depth / 2 + inset),
        (width / 2 - inset, -depth / 2 + inset),
        (width / 2 - inset, depth / 2 - inset),
        (-width / 2 + inset, depth / 2 - inset),
    ]
    vertices = [(x, y, base_z) for x, y in lower] + [(x, y, base_z + height) for x, y in upper]
    faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)]
    return add_mesh(objects, name, vertices, faces, mat, cfg, "continuous_four_sided_mansard_roof", role=role)


def add_city_window_rows(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    y: float,
    sign: float,
    x_positions: list[float],
    levels: int,
    mats: dict,
    cfg: dict,
) -> None:
    for level in range(levels):
        z = 7.2 + level * 4.25
        for index, x in enumerate(x_positions):
            core.add_punched_window_y(objects, prefix=f"{prefix}_{level}_{index}", centre_x=x, facade_y=y, centre_z=z, width=2.25, height=2.75 if level else 3.15, outward_sign=sign, mats=mats, cfg=cfg)
            core.add_box(objects, f"{prefix}_Sill_{level}_{index}", (2.7, 0.44, 0.22), (x, y + sign * 0.20, z - 1.55), mats["ornament"], cfg, "projecting_limestone_window_sill")
            core.add_box(objects, f"{prefix}_Lintel_{level}_{index}", (2.75, 0.46, 0.30), (x, y + sign * 0.21, z + 1.55), mats["ornament"], cfg, "carved_limestone_window_lintel")
            for side in (-1.0, 1.0):
                core.add_box(objects, f"{prefix}_Jamb_{level}_{index}_{side:+.0f}", (0.24, 0.46, 3.05), (x + side * 1.28, y + sign * 0.21, z), mats["ornament"], cfg, "deep_limestone_window_jamb")


def add_pediment_y(
    objects: list[bpy.types.Object],
    *,
    name: str,
    centre_x: float,
    facade_y: float,
    width: float,
    base_z: float,
    rise: float,
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
) -> bpy.types.Object:
    x0, x1 = centre_x - width / 2, centre_x + width / 2
    y0, y1 = facade_y - thickness / 2, facade_y + thickness / 2
    vertices = [
        (x0, y0, base_z), (x1, y0, base_z), (centre_x, y0, base_z + rise),
        (x0, y1, base_z), (x1, y1, base_z), (centre_x, y1, base_z + rise),
    ]
    faces = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    return add_mesh(objects, name, vertices, faces, mat, cfg, "carved_stone_civic_pediment")


def build_second_empire_city_hall(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    # Rear body and front wings leave a true deep central portal volume.
    core.add_box(objects, "CITY_RearOccupiedBody", (60.0, 31.0, 20.2), (0.0, 5.4, 10.1), mats["primary"], cfg, "complete_limestone_civic_body")
    core.add_box(objects, "CITY_LeftFrontWing", (23.5, 11.5, 20.2), (-18.25, -15.8, 10.1), mats["primary"], cfg, "projecting_limestone_end_pavilion")
    core.add_box(objects, "CITY_RightFrontWing", (23.5, 11.5, 20.2), (18.25, -15.8, 10.1), mats["primary"], cfg, "projecting_limestone_end_pavilion")
    core.add_box(objects, "CITY_CentrePavilionBridge", (13.0, 11.5, 10.0), (0.0, -15.8, 15.2), mats["primary"], cfg, "fixed_central_civic_pavilion_above_portal")
    for suffix, x in (("Left", -24.3), ("Right", 24.3)):
        core.add_box(objects, f"CITY_{suffix}EndPavilionFace", (12.4, 1.8, 21.0), (x, -22.0, 10.5), mats["primary"], cfg, "deep_projecting_end_pavilion_face")
        add_pediment_y(objects, name=f"CITY_{suffix}EndPediment", centre_x=x, facade_y=-23.05, width=13.2, base_z=20.8, rise=4.2, thickness=1.1, mat=mats["ornament"], cfg=cfg)
        for level, z in enumerate((5.8, 10.0, 14.2, 18.3)):
            for window_side in (-1.0, 1.0):
                wx = x + window_side * 2.55
                core.add_punched_window_y(objects, prefix=f"CITY_{suffix}PavilionWindow_{level}_{window_side:+.0f}", centre_x=wx, facade_y=-22.94, centre_z=z, width=2.15, height=3.0, outward_sign=-1.0, mats=mats, cfg=cfg)
                core.add_box(objects, f"CITY_{suffix}PavilionSill_{level}_{window_side:+.0f}", (2.65, 0.46, 0.22), (wx, -23.10, z - 1.58), mats["ornament"], cfg, "projecting_pavilion_window_sill")
                core.add_box(objects, f"CITY_{suffix}PavilionLintel_{level}_{window_side:+.0f}", (2.65, 0.46, 0.28), (wx, -23.10, z + 1.58), mats["ornament"], cfg, "carved_pavilion_window_lintel")
    add_pediment_y(objects, name="CITY_CentralCivicPediment", centre_x=0.0, facade_y=-22.65, width=16.0, base_z=20.2, rise=4.8, thickness=0.9, mat=mats["ornament"], cfg=cfg)
    for level, z in enumerate((14.0, 18.0)):
        for window_side in (-1.0, 1.0):
            wx = window_side * 3.15
            core.add_punched_window_y(objects, prefix=f"CITY_CentrePavilionWindow_{level}_{window_side:+.0f}", centre_x=wx, facade_y=-21.65, centre_z=z, width=2.15, height=3.1, outward_sign=-1.0, mats=mats, cfg=cfg)
    core.add_box(objects, "CITY_StonePlinth", (62.0, 44.0, 1.1), (0.0, 0.0, 0.55), mats["ornament"], cfg, "continuous_rusticated_limestone_plinth")
    # Deep portal, triple doors and continuous ceremonial stair.
    core.add_box(objects, "CITY_PortalDepth", (12.4, 12.2, 10.5), (0.0, -15.4, 5.25), mats["interior"], cfg, "deep_three_arch_civic_entry_void")
    for portal, x in enumerate((-4.0, 0.0, 4.0)):
        core.add_arch_ring_y(objects, name=f"CITY_PortalArch_{portal}", centre_x=x, facade_y=-22.0, spring_z=4.9, inner_radius=1.65, ring_width=0.42, thickness=0.55, mat=mats["ornament"], cfg=cfg, segments=28)
        core.add_box(objects, f"CITY_PortalDoor_{portal}", (2.75, 0.15, 4.8), (x, -21.74, 2.5), mats["frame"], cfg, "recessed_bronze_civic_door")
    for step in range(8):
        core.add_box(objects, f"CITY_CeremonialStep_{step}", (24.0 - step * 0.75, 0.72, 0.18), (0.0, -24.5 + step * 0.48, 0.18 + step * 0.18), mats["ornament"], cfg, "broad_integral_ceremonial_stair")
    wing_windows = [-27.0, -22.5, -14.0, -9.5, 9.5, 14.0, 22.5, 27.0]
    add_city_window_rows(objects, prefix="CITY_FrontWindow", y=-21.65, sign=-1.0, x_positions=wing_windows, levels=4, mats=mats, cfg=cfg)
    add_city_window_rows(objects, prefix="CITY_RearWindow", y=21.1, sign=1.0, x_positions=[-25.0, -18.0, -11.0, -4.0, 4.0, 11.0, 18.0, 25.0], levels=4, mats=mats, cfg=cfg)
    # Carved engaged columns and balustrades make the civic hierarchy readable.
    for column_index, x in enumerate((-7.2, -5.9, 5.9, 7.2)):
        core.add_cylinder(objects, f"CITY_EntryEngagedColumn_{column_index}", 0.48, 8.8, (x, -22.15, 7.0), mats["ornament"], cfg, "carved_limestone_entry_column", vertices=16)
        core.add_box(objects, f"CITY_EntryColumnCapital_{column_index}", (1.25, 1.0, 0.46), (x, -22.15, 11.4), mats["ornament"], cfg, "carved_entry_column_capital")
    for segment, x0, x1 in (("Left", -29.0, -8.5), ("CentreLeft", -7.5, -1.2), ("CentreRight", 1.2, 7.5), ("Right", 8.5, 29.0)):
        core.add_box(objects, f"CITY_BalustradeBase_{segment}", (x1 - x0, 0.72, 0.34), ((x0 + x1) / 2, -22.4, 21.0), mats["ornament"], cfg, "continuous_roofline_balustrade_base")
        core.add_box(objects, f"CITY_BalustradeTop_{segment}", (x1 - x0, 0.68, 0.28), ((x0 + x1) / 2, -22.4, 22.35), mats["ornament"], cfg, "continuous_roofline_balustrade_cap")
        post_count = max(2, round((x1 - x0) / 2.0))
        for post in range(post_count + 1):
            x = x0 + (x1 - x0) * post / post_count
            core.add_box(objects, f"CITY_Baluster_{segment}_{post}", (0.26, 0.55, 1.25), (x, -22.4, 21.68), mats["ornament"], cfg, "individual_stone_baluster")
    for x, sign, face in ((-30.2, -1.0, "Left"), (30.2, 1.0, "Right")):
        for level in range(4):
            z = 7.2 + level * 4.25
            for index, y in enumerate((-13.5, -5.0, 4.0, 12.5)):
                core.add_punched_window_x(objects, prefix=f"CITY_{face}Window_{level}_{index}", centre_y=y, facade_x=x, centre_z=z, width=2.35, height=2.8, outward_sign=sign, mats=mats, cfg=cfg)
    # Cornices wrap the entire stone body before the mansard begins.
    for z, size in ((4.8, 0.34), (13.4, 0.42), (20.4, 0.72)):
        core.add_box(objects, f"CITY_FrontCornice_{z}", (62.2, 0.62, size), (0.0, -22.15, z), mats["ornament"], cfg, "continuous_wrapped_limestone_cornice")
        core.add_box(objects, f"CITY_RearCornice_{z}", (62.2, 0.62, size), (0.0, 21.15, z), mats["ornament"], cfg, "continuous_wrapped_limestone_cornice")
        core.add_box(objects, f"CITY_LeftCornice_{z}", (0.62, 43.0, size), (-30.15, -0.5, z), mats["ornament"], cfg, "continuous_wrapped_limestone_cornice")
        core.add_box(objects, f"CITY_RightCornice_{z}", (0.62, 43.0, size), (30.15, -0.5, z), mats["ornament"], cfg, "continuous_wrapped_limestone_cornice")
    add_mansard_roof(objects, name="CITY_ContinuousSlateMansard", width=62.0, depth=44.0, base_z=20.5, height=9.5, inset=5.8, mat=mats["secondary"], cfg=cfg)
    # Dormers are physical occupied sash boxes with little slate pediments.
    for face, y, sign in (("Front", -19.0, -1.0), ("Rear", 19.0, 1.0)):
        for index, x in enumerate((-24.0, -16.0, -8.0, 8.0, 16.0, 24.0)):
            core.add_box(objects, f"CITY_{face}DormerBody_{index}", (3.25, 2.2, 4.5), (x, y, 25.0), mats["primary"], cfg, "occupied_stone_mansard_dormer")
            core.add_punched_window_y(objects, prefix=f"CITY_{face}DormerWindow_{index}", centre_x=x, facade_y=y + sign * 1.15, centre_z=25.1, width=1.75, height=2.45, outward_sign=sign, mats=mats, cfg=cfg)
            core.add_pyramid_roof(objects, name=f"CITY_{face}DormerCap_{index}", width=3.8, depth=2.8, base_z=27.2, height=1.7, mat=mats["secondary"], cfg=cfg)
    # Four corner turrets seat directly on the body and terminate in slate caps.
    for index, (x, y) in enumerate(((-27.0, -17.5), (27.0, -17.5), (-27.0, 17.0), (27.0, 17.0))):
        core.add_cylinder(objects, f"CITY_CornerTurret_{index}", 3.6, 13.0, (x, y, 24.5), mats["primary"], cfg, "occupied_corner_turret", vertices=12)
        add_cone(objects, name=f"CITY_CornerTurretSlateCap_{index}", radius_bottom=4.2, radius_top=0.22, depth=6.2, location=(x, y, 34.1), mat=mats["secondary"], cfg=cfg, semantic="pointed_slate_corner_turret_cap", vertices_count=12)
    # Central clock tower, four faces, copper dome and finial.
    core.add_box(objects, "CITY_ClockTower", (13.5, 13.5, 20.0), (0.0, 2.0, 36.0), mats["primary"], cfg, "central_occupied_limestone_clock_tower")
    for z, width in ((27.0, 15.2), (32.0, 14.2), (44.8, 15.0), (46.0, 14.0)):
        core.add_box(objects, f"CITY_TowerCornice_{z}", (width, width, 0.48), (0.0, 2.0, z), mats["ornament"], cfg, "layered_clock_tower_stone_cornice")
    for face, y, sign in (("Front", -4.86, -1.0), ("Rear", 8.86, 1.0)):
        for x in (-3.1, 3.1):
            core.add_punched_window_y(objects, prefix=f"CITY_TowerArcade_{face}_{x:+.0f}", centre_x=x, facade_y=y, centre_z=32.7, width=2.05, height=4.1, outward_sign=sign, mats=mats, cfg=cfg)
            core.add_arch_ring_y(objects, name=f"CITY_TowerArcadeRing_{face}_{x:+.0f}", centre_x=x, facade_y=y + sign * 0.15, spring_z=32.8, inner_radius=1.05, ring_width=0.25, thickness=0.30, mat=mats["ornament"], cfg=cfg, segments=18)
    for face, centre, axis in (
        ("Front", (0.0, -4.85, 40.0), "y"),
        ("Rear", (0.0, 8.85, 40.0), "y"),
    ):
        add_vertical_disk_y(objects, name=f"CITY_ClockFace_{face}", centre=centre, radius=3.0, thickness=0.26, mat=mats["ornament"], cfg=cfg, semantic="physical_clock_face")
        for hour in range(12):
            angle = math.tau * hour / 12
            x = math.cos(angle) * 2.45
            z = 40.0 + math.sin(angle) * 2.45
            core.add_sphere(objects, f"CITY_{face}HourMark_{hour}", 0.13, (x, centre[1] - (0.18 if face == "Front" else -0.18), z), mats["frame"], cfg, "clock_hour_marker", scale=(1.0, 0.45, 1.0))
        hand_y = centre[1] - (0.32 if face == "Front" else -0.32)
        core.add_beam(objects, f"CITY_{face}ClockHourHand", (0.0, hand_y, 40.0), (-0.9, hand_y, 41.4), 0.105, mats["frame"], cfg, "physical_clock_hour_hand")
        core.add_beam(objects, f"CITY_{face}ClockMinuteHand", (0.0, hand_y, 40.0), (1.7, hand_y, 40.65), 0.075, mats["frame"], cfg, "physical_clock_minute_hand")
    for side, x in (("Left", -6.88), ("Right", 6.88)):
        clock = core.add_cylinder(objects, f"CITY_ClockFace_{side}", 3.0, 0.26, (x, 2.0, 40.0), mats["ornament"], cfg, "physical_clock_face", vertices=32)
        clock.rotation_euler.y = math.radians(90.0)
    core.add_cylinder(objects, "CITY_CopperDomeDrum", 6.1, 2.4, (0.0, 2.0, 47.2), mats["roof"], cfg, "patinated_copper_dome_drum", vertices=24)
    add_revolved_profile(
        objects,
        name="CITY_CopperDome",
        centre=(0.0, 2.0),
        profile=[(47.6, 5.9), (48.4, 6.55), (49.6, 6.75), (51.0, 6.15), (52.4, 4.9), (53.6, 3.0), (54.2, 1.45)],
        mat=mats["roof"],
        cfg=cfg,
        semantic="patinated_copper_clock_tower_dome",
        segments=32,
    )
    core.add_cylinder(objects, "CITY_DomeLantern", 1.45, 2.2, (0.0, 2.0, 55.0), mats["primary"], cfg, "open_civic_dome_lantern", vertices=16)
    add_cone(objects, name="CITY_LanternCap", radius_bottom=1.8, radius_top=0.18, depth=1.8, location=(0.0, 2.0, 57.0), mat=mats["roof"], cfg=cfg, semantic="patinated_copper_lantern_cap", vertices_count=16)
    core.add_cylinder(objects, "CITY_DomeFinial", 0.20, 1.4, (0.0, 2.0, 58.3), mats["frame"], cfg, "civic_dome_finial", vertices=12)
    # Small chimney clusters articulate the roof plan without competing with the tower.
    for index, (x, y) in enumerate(((-18.0, -5.0), (18.0, -5.0), (-18.0, 9.0), (18.0, 9.0))):
        core.add_box(objects, f"CITY_Chimney_{index}", (2.1, 2.1, 4.2), (x, y, 31.8), mats["primary"], cfg, "limestone_mansard_chimney")
        core.add_box(objects, f"CITY_ChimneyCap_{index}", (2.6, 2.6, 0.35), (x, y, 34.0), mats["ornament"], cfg, "carved_chimney_cap")
    return objects


def build_greenhouse_vertical_farm(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    width, depth = 36.0, 34.0
    base_z = 5.0
    level_height = 3.45
    levels = 30
    core.add_box(objects, "VF_ConcretePodium", (width, depth, 5.0), (0.0, 0.0, 2.5), mats["secondary"], cfg, "public_vertical_farm_processing_podium")
    core.add_window_band_y(objects, prefix="VF_PublicLobby", width=28.0, facade_y=-17.25, centre_z=2.9, height=4.6, bays=8, outward_sign=-1.0, mats=mats, cfg=cfg, margin=0.2)
    core.add_box(objects, "VF_RearServiceCore", (8.0, 13.5, levels * level_height), (13.0, 8.7, base_z + levels * level_height / 2), mats["ornament"], cfg, "continuous_rear_irrigation_and_lift_core")
    # Thirty countable cultivation decks and varied crop trays remain visible
    # through the continuous greenhouse enclosure.
    for level in range(levels):
        z = base_z + level * level_height
        core.add_box(objects, f"VF_CultivationDeck_{level}", (34.8, 32.8, 0.24), (0.0, 0.0, z + 0.12), mats["secondary"], cfg, "physical_cultivation_floor_datum")
        for row, tray_y in enumerate((-10.5, 1.5)):
            for tray in range(4):
                x = -12.0 + tray * 8.0
                tray_mat = mats["primary"] if (level + tray + row) % 4 else mats["secondary"]
                suffix = row * 4 + tray
                core.add_box(objects, f"VF_CropTray_{level}_{suffix}", (6.6, 4.4, 0.55), (x, tray_y, z + 1.15), tray_mat, cfg, "visible_hydroponic_crop_tray")
                core.add_box(objects, f"VF_GrowLight_{level}_{suffix}", (6.2, 0.16, 0.12), (x, tray_y - 1.7, z + 2.55), mats["interior"], cfg, "restrained_hydroponic_grow_light")
    # The curtain wall is grouped into ten three-storey greenhouse bays so it
    # can remain transparent without creating a blue office checkerboard.
    group_height = level_height * 3
    for group in range(10):
        z0 = base_z + group * group_height
        centre_z = z0 + group_height / 2
        for y, sign, face in ((-17.05, -1.0, "Front"), (17.05, 1.0, "Rear")):
            core.add_box(objects, f"VF_{face}Glass_{group}", (35.0, 0.10, group_height - 0.22), (0.0, y, centre_z), mats["glass"], cfg, "continuous_three_storey_greenhouse_glass")
            for mullion in range(10):
                x = -17.5 + mullion * 35.0 / 9
                core.add_box(objects, f"VF_{face}Mullion_{group}_{mullion}", (0.11, 0.20, group_height), (x, y + sign * 0.08, centre_z), mats["frame"], cfg, "physical_greenhouse_mullion")
        for x, sign, face in ((-18.05, -1.0, "Left"), (18.05, 1.0, "Right")):
            core.add_box(objects, f"VF_{face}Glass_{group}", (0.10, 33.0, group_height - 0.22), (x, 0.0, centre_z), mats["glass"], cfg, "continuous_three_storey_greenhouse_glass")
            for mullion in range(9):
                y = -16.5 + mullion * 33.0 / 8
                core.add_box(objects, f"VF_{face}Mullion_{group}_{mullion}", (0.20, 0.11, group_height), (x + sign * 0.08, y, centre_z), mats["frame"], cfg, "physical_greenhouse_mullion")
        for z in (z0, z0 + group_height):
            core.add_box(objects, f"VF_FrontRail_{group}_{z:.2f}", (36.2, 0.20, 0.16), (0.0, -17.15, z), mats["frame"], cfg, "greenhouse_floor_pressure_cap")
            core.add_box(objects, f"VF_RearRail_{group}_{z:.2f}", (36.2, 0.20, 0.16), (0.0, 17.15, z), mats["frame"], cfg, "greenhouse_floor_pressure_cap")
    # Alternating double-height winter gardens break mechanical repetition.
    for garden_index, level in enumerate((7, 16, 25)):
        z = base_z + level * level_height + 1.8
        core.add_box(objects, f"VF_WinterGardenVoid_{garden_index}", (15.0, 7.0, 6.2), (-7.0 if garden_index % 2 == 0 else 6.0, -13.0, z + 1.2), mats["interior"], cfg, "double_height_winter_garden_depth")
        for tree in range(4):
            x = (-12.0 if garden_index % 2 == 0 else 0.0) + tree * 3.2
            core.add_cylinder(objects, f"VF_WinterGardenTrunk_{garden_index}_{tree}", 0.10, 2.4, (x, -13.0, z), mats["ornament"], cfg, "visible_winter_garden_tree", vertices=10)
            core.add_sphere(objects, f"VF_WinterGardenCrown_{garden_index}_{tree}", 0.82, (x, -13.0, z + 1.6), mats["primary"], cfg, "visible_winter_garden_tree", scale=(1.0, 0.8, 1.2))
    # Three giant X-fields are integrated with real deck nodes, matching the
    # reference tower's structural scale instead of reading as applied trim.
    for field in range(3):
        z0 = base_z + field * 10 * level_height
        z1 = z0 + 10 * level_height
        for diagonal, (x0, x1) in enumerate(((-17.5, 17.5), (17.5, -17.5))):
            core.add_beam(objects, f"VF_ExteriorBrace_Front_{field}_{diagonal}", (x0, -17.45, z0), (x1, -17.45, z1), 0.28, mats["frame"], cfg, "external_greenhouse_cross_brace")
        for diagonal, (y0, y1) in enumerate(((-16.5, 16.5), (16.5, -16.5))):
            core.add_beam(objects, f"VF_ExteriorBrace_Right_{field}_{diagonal}", (18.45, y0, z0), (18.45, y1, z1), 0.28, mats["frame"], cfg, "external_greenhouse_cross_brace")
    for corner, (x, y) in enumerate(((-18.35, -17.35), (18.35, -17.35), (-18.35, 17.35), (18.35, 17.35))):
        core.add_box(objects, f"VF_ExteriorCornerColumn_{corner}", (0.42, 0.42, levels * level_height), (x, y, base_z + levels * level_height / 2), mats["frame"], cfg, "continuous_greenhouse_corner_column")
    # Vented greenhouse crown and roof service rails complete the native height.
    crown_base = base_z + levels * level_height
    core.add_box(objects, "VF_GreenhouseCrown", (31.0, 29.0, 3.2), (0.0, 0.0, crown_base + 1.6), mats["roof"], cfg, "vented_translucent_greenhouse_crown")
    core.add_hip_roof(objects, name="VF_GreenhouseCrownRoof", width=33.0, depth=31.0, base_z=crown_base + 3.2, height=3.4, ridge_fraction=0.45, mat=mats["roof"], cfg=cfg)
    for index in range(9):
        x = -15.0 + index * 3.75
        core.add_beam(objects, f"VF_CrownVentRib_{index}", (x, -15.1, crown_base + 3.4), (x, 15.1, crown_base + 3.4), 0.11, mats["frame"], cfg, "operable_greenhouse_crown_vent_rib")
    return objects


def hub_roof_height(x: float, y: float, *, width: float, depth: float) -> float:
    nx = min(1.0, abs(x) / (width / 2))
    ny = min(1.0, abs(y) / (depth / 2))
    return 8.0 + 25.0 * (1.0 - nx**1.55) * (0.88 + 0.12 * math.cos(ny * math.pi / 2))


def add_hub_roof(
    objects: list[bpy.types.Object],
    *,
    name: str,
    width: float,
    depth: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
    x_segments: int = 30,
    y_segments: int = 14,
) -> bpy.types.Object:
    thickness = 0.30
    vertices: list[tuple[float, float, float]] = []
    for dz in (-thickness, 0.0):
        for yi in range(y_segments + 1):
            y = -depth / 2 + yi * depth / y_segments
            for xi in range(x_segments + 1):
                x = -width / 2 + xi * width / x_segments
                vertices.append((x, y, hub_roof_height(x, y, width=width, depth=depth) + dz))
    stride = x_segments + 1
    layer = stride * (y_segments + 1)
    faces: list[tuple[int, ...]] = []
    for side in range(2):
        base = side * layer
        for yi in range(y_segments):
            for xi in range(x_segments):
                a = base + yi * stride + xi
                quad = (a, a + 1, a + stride + 1, a + stride)
                faces.append(tuple(reversed(quad)) if side == 0 else quad)
    for xi in range(x_segments):
        faces.append((xi, layer + xi, layer + xi + 1, xi + 1))
        a = y_segments * stride + xi
        faces.append((a, a + 1, layer + a + 1, layer + a))
    for yi in range(y_segments):
        a = yi * stride
        b = (yi + 1) * stride
        faces.append((a, b, layer + b, layer + a))
        a += x_segments
        b += x_segments
        faces.append((a, layer + a, layer + b, b))
    return add_mesh(objects, name, vertices, faces, mat, cfg, "continuous_translucent_station_roof", role=role)


def build_steel_rib_transit_hub(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    # The long axis runs away from the public front: the entry is a narrow
    # glazed gable, not the broad side wall of a generic exhibition shed.
    width, depth = 65.0, 100.0
    core.add_box(objects, "HUB_BrickPlinth", (63.0, 98.0, 5.8), (0.0, 0.0, 2.9), mats["secondary"], cfg, "warm_brick_and_glass_station_plinth")
    core.add_box(objects, "HUB_ConcourseFloor", (58.0, 92.0, 0.28), (0.0, 0.0, 6.0), mats["ornament"], cfg, "continuous_terrazzo_concourse_floor")
    core.add_box(objects, "HUB_CentralPlatformVoid", (18.0, 86.0, 0.20), (0.0, 2.0, 5.75), mats["frame"], cfg, "central_platform_and_track_axis")
    for y, sign, face in ((-49.0, -1.0, "Front"), (49.0, 1.0, "Rear")):
        core.add_window_band_y(objects, prefix=f"HUB_{face}Concourse", width=58.0, facade_y=y, centre_z=11.0, height=10.0, bays=12, outward_sign=sign, mats=mats, cfg=cfg, margin=0.25)
    for x, sign, face in ((-31.5, -1.0, "Left"), (31.5, 1.0, "Right")):
        core.add_window_band_x(objects, prefix=f"HUB_{face}Concourse", depth=88.0, facade_x=x, centre_z=10.0, height=8.0, bays=18, outward_sign=sign, mats=mats, cfg=cfg, margin=0.25)
    core.add_box(objects, "HUB_EntryDepth", (24.0, 4.0, 10.5), (0.0, -47.0, 9.5), mats["interior"], cfg, "deep_luminous_central_station_entry")
    core.add_box(objects, "HUB_EntryGlass", (23.5, 0.12, 10.0), (0.0, -50.05, 9.5), mats["glass"], cfg, "high_transmission_central_entry_glass")
    # Two longitudinal parabolic arches are primary load paths.
    for suffix, x in (("Left", -13.0), ("Right", 13.0)):
        points = []
        for step in range(25):
            y = -49.0 + step * (98.0 / 24)
            z = 7.0 + 27.0 * max(0.0, 1.0 - (y / 50.5) ** 2)
            points.append((x, y, z))
        add_polyline_beams(objects, prefix=f"HUB_PrimaryArch_{suffix}", points=points, radius=0.52, mat=mats["primary"], cfg=cfg, semantic="grounded_longitudinal_parabolic_arch")
    # Fan ribs span from perimeter shoes through the twin arches to the opposite
    # shoe, remaining coincident with the roof equation.
    for rib_index in range(21):
        y = -46.0 + rib_index * (92.0 / 20)
        points = []
        for step in range(21):
            x = -31.5 + step * 3.15
            points.append((x, y, hub_roof_height(x, y, width=width, depth=depth) + 0.22))
        add_polyline_beams(objects, prefix=f"HUB_FanRib_{rib_index}", points=points, radius=0.28, mat=mats["primary"], cfg=cfg, semantic="continuous_fan_rib_to_perimeter_shoes")
        for side, x in (("L", -31.5), ("R", 31.5)):
            core.add_box(objects, f"HUB_StructuralShoe_{rib_index}_{side}", (1.8, 2.2, 1.4), (x, y, 6.8), mats["ornament"], cfg, "visible_cast_structural_shoe")
    add_hub_roof(objects, name="HUB_ContinuousGlazedRoof", width=65.0, depth=100.0, mat=mats["roof"], cfg=cfg)
    # Suspended concourse bridges, open guards and stairs reveal usable levels.
    for level, z in enumerate((11.5, 17.0)):
        core.add_box(objects, f"HUB_ConcourseBridge_{level}", (46.0, 8.0, 0.45), (0.0, 4.0, z), mats["ornament"], cfg, "occupied_cross_concourse_bridge")
        add_guard_run(objects, prefix=f"HUB_BridgeGuardFront_{level}", start=(-22.0, -0.15, z + 1.2), end=(22.0, -0.15, z + 1.2), posts=16, mat=mats["frame"], cfg=cfg)
        add_guard_run(objects, prefix=f"HUB_BridgeGuardRear_{level}", start=(-22.0, 8.15, z + 1.2), end=(22.0, 8.15, z + 1.2), posts=16, mat=mats["frame"], cfg=cfg)
    for stair in range(11):
        core.add_box(objects, f"HUB_EntryStep_{stair}", (19.0, 0.62, 0.18), (0.0, -54.0 + stair * 0.52, 0.18 + stair * 0.18), mats["ornament"], cfg, "integral_station_entry_stair")
    return objects


def build_monumental_silo_cluster(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    silo_positions = [
        (x, y)
        for y in (-13.0, 13.0)
        for x in (-27.0, -9.0, 9.0, 27.0)
    ]
    # Eight real vessels, with a conical hopper and cap for each bank position.
    for index, (x, y) in enumerate(silo_positions):
        core.add_cylinder(
            objects,
            f"SILO_Bank{'A' if y < 0 else 'B'}_{index % 4}",
            8.15,
            43.0,
            (x, y, 27.0),
            mats["primary"],
            cfg,
            "full_height_slip_formed_storage_vessel",
            vertices=32,
        )
        add_cone(
            objects,
            name=f"SILO_Hopper_{index}",
            radius_bottom=2.1,
            radius_top=7.8,
            depth=5.0,
            location=(x, y, 3.0),
            mat=mats["frame"],
            cfg=cfg,
            semantic="visible_bulk_discharge_hopper",
            vertices_count=24,
        )
        add_cone(
            objects,
            name=f"SILO_ConicalCap_{index}",
            radius_bottom=8.2,
            radius_top=0.75,
            depth=5.8,
            location=(x, y, 51.4),
            mat=mats["secondary"],
            cfg=cfg,
            semantic="galvanized_conical_silo_cap",
            vertices_count=32,
        )
        core.add_cylinder(objects, f"SILO_Vent_{index}", 0.7, 2.2, (x, y, 55.4), mats["ornament"], cfg, "working_silo_roof_vent", vertices=16)
        for ring_z in (8.0, 22.0, 36.0, 48.0):
            add_cone(
                objects,
                name=f"SILO_Ring_{index}_{int(ring_z)}",
                radius_bottom=8.28,
                radius_top=8.28,
                depth=0.16,
                location=(x, y, ring_z),
                mat=mats["frame"],
                cfg=cfg,
                semantic="continuous_silo_maintenance_ring",
                vertices_count=32,
            )
    # Headworks span and transfer galleries are supported by visible trusses.
    core.add_box(objects, "SILO_ConveyorHeadhouse", (74.0, 18.0, 7.2), (0.0, 0.0, 58.1), mats["secondary"], cfg, "occupied_glazed_conveyor_headhouse")
    core.add_window_band_y(objects, prefix="SILO_HeadhouseFront", width=68.0, facade_y=-9.05, centre_z=58.4, height=4.4, bays=14, outward_sign=-1.0, mats=mats, cfg=cfg, margin=0.3)
    core.add_window_band_y(objects, prefix="SILO_HeadhouseRear", width=68.0, facade_y=9.05, centre_z=58.4, height=4.4, bays=14, outward_sign=1.0, mats=mats, cfg=cfg, margin=0.3)
    # Two compact cross-bank transfer galleries replace unsupported floating
    # sheds. Each lands on the silo shoulders and ties into the headhouse.
    for x in (-18.0, 18.0):
        core.add_box(objects, f"SILO_CrossBankGallery_{x:+.0f}", (6.0, 43.0, 4.6), (x, 0.0, 49.8), mats["secondary"], cfg, "supported_cross_bank_transfer_gallery")
        for y in range(-18, 19, 6):
            core.add_beam(objects, f"SILO_GalleryDiagA_{x:+.0f}_{y}", (x - 3.1, y, 47.7), (x - 3.1, y + 5.5, 51.9), 0.16, mats["frame"], cfg, "load_bearing_gallery_side_truss")
            core.add_beam(objects, f"SILO_GalleryDiagB_{x:+.0f}_{y}", (x + 3.1, y + 5.5, 47.7), (x + 3.1, y, 51.9), 0.16, mats["frame"], cfg, "load_bearing_gallery_side_truss")
    # A deliberately open central catwalk proves access between the two banks.
    core.add_box(objects, "SILO_CentralCatwalkDeck", (70.0, 2.0, 0.24), (0.0, 0.0, 46.5), mats["frame"], cfg, "open_maintenance_catwalk_deck")
    add_guard_run(objects, prefix="SILO_CatwalkGuardFront", start=(-34.0, -1.0, 47.6), end=(34.0, -1.0, 47.6), posts=22, mat=mats["frame"], cfg=cfg)
    add_guard_run(objects, prefix="SILO_CatwalkGuardRear", start=(-34.0, 1.0, 47.6), end=(34.0, 1.0, 47.6), posts=22, mat=mats["frame"], cfg=cfg)
    # A switchback stair is physically grounded against the west end vessel.
    for flight in range(6):
        direction = 1.0 if flight % 2 == 0 else -1.0
        base_z = 4.0 + flight * 7.1
        base_y = -23.0 if direction > 0 else -17.0
        for step in range(12):
            y = base_y + direction * step * 0.48
            z = base_z + step * 0.54
            core.add_box(objects, f"SILO_Stair_{flight}_{step}", (3.0, 0.58, 0.16), (-37.0, y, z), mats["frame"], cfg, "integrated_external_access_stair")
        core.add_box(objects, f"SILO_Landing_{flight}", (3.4, 3.0, 0.24), (-37.0, base_y + direction * 5.7, base_z + 6.5), mats["frame"], cfg, "supported_stair_landing")
    for column_index, y in enumerate((-23.0, -17.3)):
        core.add_beam(objects, f"SILO_StairTowerColumn_{column_index}_A", (-38.5, y, 0.0), (-38.5, y, 47.0), 0.16, mats["frame"], cfg, "grounded_external_stair_tower")
        core.add_beam(objects, f"SILO_StairTowerColumn_{column_index}_B", (-35.5, y, 0.0), (-35.5, y, 47.0), 0.16, mats["frame"], cfg, "grounded_external_stair_tower")
    for landing in range(7):
        z = 4.0 + landing * 7.1
        add_guard_run(objects, prefix=f"SILO_StairLandingGuard_{landing}", start=(-38.4, -23.0, z + 1.1), end=(-35.6, -23.0, z + 1.1), posts=3, mat=mats["frame"], cfg=cfg)
    # Process pipes terminate at real loading equipment rather than floating.
    for pipe_index, x in enumerate((-31.0, -25.5, 25.5, 31.0)):
        core.add_cylinder(objects, f"SILO_ProcessPipe_{pipe_index}", 0.45, 40.0, (x, -22.5, 24.0), mats["ornament"], cfg, "continuous_process_transfer_pipe", vertices=12)
        core.add_beam(objects, f"SILO_ProcessPipeElbow_{pipe_index}", (x, -22.5, 44.0), (x, -27.0, 44.0), 0.45, mats["ornament"], cfg, "continuous_process_transfer_pipe")
    core.add_beam(objects, "SILO_FrontProcessHeader", (-32.0, -27.0, 10.5), (32.0, -27.0, 10.5), 0.55, mats["ornament"], cfg, "continuous_front_process_header")
    core.add_box(objects, "SILO_LoadingHall", (76.0, 12.0, 9.0), (0.0, -25.0, 4.5), mats["secondary"], cfg, "separate_low_bulk_loading_hall")
    core.add_hip_roof(objects, name="SILO_LoadingHallRoof", width=77.0, depth=13.0, base_z=9.0, height=2.4, ridge_fraction=0.72, mat=mats["roof"], cfg=cfg)
    for bay, x in enumerate((-27.0, -9.0, 9.0, 27.0)):
        core.add_box(objects, f"SILO_LoadingPortalDepth_{bay}", (12.0, 1.0, 6.0), (x, -31.1, 4.0), mats["interior"], cfg, "deep_operational_loading_portal")
        core.add_box(objects, f"SILO_LoadingDoor_{bay}", (11.4, 0.16, 5.6), (x, -31.7, 4.0), mats["frame"], cfg, "physical_industrial_loading_door")
    return objects


def add_curved_gallery_shell(
    objects: list[bpy.types.Object],
    *,
    name: str,
    centre: tuple[float, float],
    inner_radius: float,
    thickness: float,
    angle_start: float,
    angle_end: float,
    base_z: float,
    crest_z: float,
    mat: bpy.types.Material,
    cfg: dict,
) -> bpy.types.Object:
    segments = 30
    cx, cy = centre
    vertices: list[tuple[float, float, float]] = []
    for z_band in (base_z, crest_z):
        for radius in (inner_radius, inner_radius + thickness):
            for index in range(segments + 1):
                t = index / segments
                angle = angle_start + (angle_end - angle_start) * t
                # The slight changing crest makes the rolled volumes civic,
                # not extruded pipes, while preserving closed weathering.
                z = z_band if z_band == base_z else crest_z + math.sin(t * math.pi) * 3.0
                vertices.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius, z))
    stride = segments + 1
    layer = stride * 2
    faces: list[tuple[int, ...]] = []
    for radial in range(2):
        bottom = radial * stride
        top = layer + radial * stride
        for index in range(segments):
            quad = (bottom + index, bottom + index + 1, top + index + 1, top + index)
            faces.append(tuple(reversed(quad)) if radial == 0 else quad)
    for index in range(segments):
        faces.append((index, stride + index, stride + index + 1, index + 1))
        a = layer + index
        faces.append((a, a + 1, layer + stride + index + 1, layer + stride + index))
    for end in (0, segments):
        faces.append((end, layer + end, layer + stride + end, stride + end))
    return add_mesh(objects, name, vertices, faces, mat, cfg, "closed_rolled_titanium_gallery_shell")


def build_titanium_fold_museum(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "MUSEUM_ConcretePlinth", (86.0, 61.0, 5.2), (0.0, 0.0, 2.6), mats["ornament"], cfg, "continuous_architectural_concrete_public_plinth")
    # Two rolled shells are genuine closed wall volumes with materially thick
    # returns. Their opposed curvature frames the central canyon.
    add_curved_gallery_shell(objects, name="MUSEUM_RolledShell_Left", centre=(-37.0, 0.0), inner_radius=17.0, thickness=5.2, angle_start=-1.12, angle_end=1.18, base_z=5.2, crest_z=26.0, mat=mats["titanium_mid"], cfg=cfg)
    add_curved_gallery_shell(objects, name="MUSEUM_RolledShell_Right", centre=(37.0, 2.0), inner_radius=18.0, thickness=5.8, angle_start=1.96, angle_end=4.28, base_z=5.2, crest_z=27.0, mat=mats["titanium_mid"], cfg=cfg)
    wedges = [
        ("North", [(-33.0, 5.0), (-4.0, 2.0), (0.0, 28.0), (-39.0, 24.0)], [17.0, 31.0, 24.0, 20.0]),
        ("East", [(4.0, -25.0), (39.0, -19.0), (35.0, 12.0), (8.0, 8.0)], [15.0, 23.0, 30.0, 18.0]),
        ("South", [(-34.0, -26.0), (-5.0, -31.0), (7.0, -7.0), (-25.0, -5.0)], [16.0, 25.0, 19.0, 29.0]),
    ]
    for suffix, footprint, tops in wedges:
        add_extruded_footprint(objects, name=f"MUSEUM_FoldedWedge_{suffix}", footprint=footprint, base_z=5.2, top_z=tops, mat=mats["titanium_mid"], cfg=cfg, semantic="closed_folded_titanium_gallery_volume")
        for edge_index in range(len(footprint)):
            nxt = (edge_index + 1) % len(footprint)
            core.add_beam(objects, f"MUSEUM_FoldedWedge{suffix}TopReveal_{edge_index}", (footprint[edge_index][0], footprint[edge_index][1], tops[edge_index]), (footprint[nxt][0], footprint[nxt][1], tops[nxt]), 0.12, mats["frame"], cfg, "continuous_dark_titanium_fold_reveal")
            core.add_beam(objects, f"MUSEUM_FoldedWedge{suffix}VerticalReveal_{edge_index}", (footprint[edge_index][0], footprint[edge_index][1], 5.2), (footprint[edge_index][0], footprint[edge_index][1], tops[edge_index]), 0.10, mats["frame"], cfg, "continuous_dark_titanium_fold_reveal")
    # Glass canyon has occupied depth, floor plates, real panes and mullions.
    core.add_box(objects, "MUSEUM_AtriumOccupiedDepth", (12.0, 45.0, 22.0), (0.0, 0.0, 16.5), mats["interior"], cfg, "deep_occupied_central_museum_canyon")
    for x, sign, side in ((-6.2, -1.0, "Left"), (6.2, 1.0, "Right")):
        core.add_window_band_x(objects, prefix=f"MUSEUM_Canyon{side}", depth=43.0, facade_x=x, centre_z=16.5, height=21.0, bays=10, outward_sign=sign, mats=mats, cfg=cfg, margin=0.2)
    for z in (9.5, 14.5, 19.5, 24.5):
        core.add_box(objects, f"MUSEUM_AtriumFloor_{z}", (11.0, 42.0, 0.28), (0.0, 0.0, z), mats["ornament"], cfg, "visible_occupied_atrium_floor_datum")
    core.add_box(objects, "MUSEUM_GalleryBridge", (28.0, 12.0, 6.4), (0.0, -6.0, 23.2), mats["secondary"], cfg, "supported_rectilinear_gallery_bridge")
    core.add_window_band_y(objects, prefix="MUSEUM_BridgeFront", width=26.0, facade_y=-12.1, centre_z=23.2, height=4.8, bays=7, outward_sign=-1.0, mats=mats, cfg=cfg, margin=0.2)
    # The public entrance is a carved slot beneath the bridge, with a deep
    # timber-warm lobby and a continuous folded soffit.
    core.add_box(objects, "MUSEUM_EntryDepth", (18.0, 6.0, 7.5), (0.0, -29.0, 8.7), mats["interior"], cfg, "deep_public_entry_between_gallery_masses")
    core.add_box(objects, "MUSEUM_EntryGlass", (17.4, 0.12, 7.0), (0.0, -32.05, 8.7), mats["glass"], cfg, "physical_museum_entry_glass")
    add_slope_plate_x(objects, name="MUSEUM_EntrySoffit", x0=-12.0, x1=12.0, y0=-34.0, y1=-26.0, z0=14.5, z1=17.5, thickness=0.45, mat=mats["secondary"], cfg=cfg, semantic="integral_folded_entry_soffit")
    # Shingle seams follow every shell rather than relying on flat image detail.
    for shell, cx, cy, radius, a0, a1 in (("L", -37.0, 0.0, 22.3, -1.12, 1.18), ("R", 37.0, 2.0, 23.9, 1.96, 4.28)):
        top_edge: list[tuple[float, float, float]] = []
        for seam_index in range(13):
            t = seam_index / 12
            angle = a0 + (a1 - a0) * t
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            top = 27.0 + math.sin(t * math.pi) * 3.0
            top_edge.append((x, y, top))
            core.add_beam(objects, f"MUSEUM_RoofSeam_{shell}_{seam_index}", (x, y, 5.5), (x, y, top), 0.10, mats["frame"], cfg, "physical_titanium_shingle_seam")
        add_polyline_beams(objects, prefix=f"MUSEUM_ShellTopEdge_{shell}", points=top_edge, radius=0.14, mat=mats["frame"], cfg=cfg, semantic="continuous_folded_titanium_shell_edge")
    # A sparse physical perforation shadow field keeps the signature punched
    # titanium legible at street-view distance, where a texture alone aliases
    # into a blank white shell.
    perforation_fields = (
        ("Left", -37.0, 0.0, 22.42, -1.02, -0.08),
        ("Right", 37.0, 2.0, 24.02, 3.28, 4.18),
    )
    for field_name, cx, cy, radius, angle0, angle1 in perforation_fields:
        for column in range(13):
            angle = angle0 + (angle1 - angle0) * column / 12
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            for row, z in enumerate((8.0, 10.5, 13.0, 15.5, 18.0, 20.5, 23.0, 25.5)):
                if (column + row) % 3 == 0:
                    continue
                core.add_box(objects, f"MUSEUM_PerforationShadow_{field_name}_{column}_{row}", (0.24, 0.14, 0.24), (x, y, z), mats["frame"], cfg, "physical_perforated_titanium_shadow")
    for field_name, start, end, top_start, top_end in (
        ("SouthFold", (-34.0, -26.0), (-5.0, -31.0), 16.0, 25.0),
        ("EastFold", (4.0, -25.0), (39.0, -19.0), 15.0, 23.0),
    ):
        for column in range(10):
            t = (column + 0.5) / 10
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t - 0.12
            top = top_start + (top_end - top_start) * t
            for row in range(7):
                z = 7.0 + row * max(1.0, (top - 8.0) / 6)
                if z > top - 0.7 or (column + row) % 3 == 0:
                    continue
                core.add_box(objects, f"MUSEUM_PerforationShadow_{field_name}_{column}_{row}", (0.24, 0.14, 0.24), (x, y, z), mats["frame"], cfg, "physical_perforated_titanium_shadow")
    return objects


def add_barrel_shell_y(
    objects: list[bpy.types.Object],
    *,
    name: str,
    centre_x: float,
    half_width: float,
    y0: float,
    y1: float,
    spring_z: float,
    rise: float,
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
) -> bpy.types.Object:
    segments = 28
    vertices: list[tuple[float, float, float]] = []
    for offset in (0.0, thickness):
        for y in (y0, y1):
            for index in range(segments + 1):
                angle = math.pi * index / segments
                x = centre_x - math.cos(angle) * half_width
                z = spring_z + math.sin(angle) * rise + offset
                vertices.append((x, y, z))
    stride = segments + 1
    layer = stride * 2
    faces: list[tuple[int, ...]] = []
    for skin in range(2):
        base = skin * layer
        for index in range(segments):
            quad = (base + index, base + stride + index, base + stride + index + 1, base + index + 1)
            faces.append(tuple(reversed(quad)) if skin == 0 else quad)
    for end_base in (0, stride):
        for index in range(segments):
            faces.append((end_base + index, end_base + index + 1, layer + end_base + index + 1, layer + end_base + index))
    for index in (0, segments):
        faces.append((index, stride + index, layer + stride + index, layer + index))
    return add_mesh(objects, name, vertices, faces, mat, cfg, "continuous_rippled_glass_barrel_shell")


def build_historic_iron_glass_market(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "MARKET_StonePlinth", (67.0, 41.0, 1.1), (0.0, 0.0, 0.55), mats["secondary"], cfg, "continuous_honey_stone_market_plinth")
    aisle_centres = (-22.0, 0.0, 22.0)
    aisle_width = 22.0
    spring_z = 9.4
    for aisle_index, centre_x in enumerate(aisle_centres):
        # Brick base and clear occupied hall are discrete physical layers.
        core.add_box(objects, f"MARKET_BrickBase_{aisle_index}", (21.5, 40.0, 8.3), (centre_x, 0.0, 5.25), mats["primary"], cfg, "weathered_brick_market_aisle_base")
        core.add_box(objects, f"MARKET_HallDepth_{aisle_index}", (19.5, 37.0, 11.0), (centre_x, 0.0, 11.5), mats["interior"], cfg, "warm_occupied_market_stall_depth")
        add_barrel_shell_y(objects, name=f"MARKET_{'CentralBarrelGlass' if aisle_index == 1 else f'BarrelGlass_{aisle_index}'}", centre_x=centre_x, half_width=10.8, y0=-20.0, y1=20.0, spring_z=spring_z, rise=10.8 if aisle_index == 1 else 9.6, thickness=0.18, mat=mats["glass"], cfg=cfg)
        # Fourteen load-bearing arch frames align across all three aisles.
        for rib_index in range(14):
            y = -19.0 + rib_index * (38.0 / 13)
            points = []
            for segment in range(17):
                angle = math.pi * segment / 16
                points.append((centre_x - math.cos(angle) * 10.9, y, spring_z + math.sin(angle) * (10.8 if aisle_index == 1 else 9.6) + 0.25))
            add_polyline_beams(objects, prefix=f"MARKET_IronArch_{aisle_index}_{rib_index}", points=points, radius=0.17, mat=mats["ornament"], cfg=cfg, semantic="continuous_wrought_iron_barrel_arch")
        # Front and rear fanlight glazing and radial ironwork belong to the arch.
        for y, face in ((-20.15, "Front"), (20.15, "Rear")):
            add_vertical_disk_y(objects, name=f"MARKET_{face}FanGlass_{aisle_index}", centre=(centre_x, y, spring_z), radius=10.5, thickness=0.09, mat=mats["glass"], cfg=cfg, semantic="physical_clear_gable_fanlight")
            core.add_arch_ring_y(objects, name=f"MARKET_{face}Arch_{'Centre' if aisle_index == 1 else aisle_index}", centre_x=centre_x, facade_y=y + (-0.08 if y < 0 else 0.08), spring_z=spring_z, inner_radius=10.2, ring_width=0.45, thickness=0.28, mat=mats["ornament"], cfg=cfg, segments=28)
            for spoke_index in range(9):
                angle = math.pi * spoke_index / 8
                start = (centre_x, y + (-0.12 if y < 0 else 0.12), spring_z)
                end = (centre_x - math.cos(angle) * 10.0, start[1], spring_z + math.sin(angle) * 10.0)
                core.add_beam(objects, f"MARKET_{face}FanSpoke_{aisle_index}_{spoke_index}", start, end, 0.10, mats["frame"], cfg, "radial_cast_iron_gable_fan")
            for support_x in (centre_x - 10.35, centre_x + 10.35):
                core.add_box(objects, f"MARKET_{face}ArchSupport_{aisle_index}_{support_x:+.1f}", (0.42, 0.32, 8.3), (support_x, y, 5.25), mats["ornament"], cfg, "continuous_cast_iron_arch_support")
            core.add_box(objects, f"MARKET_{face}ArchTransom_{aisle_index}", (20.7, 0.34, 0.32), (centre_x, y, spring_z), mats["ornament"], cfg, "continuous_cast_iron_arch_transom")
        # Each aisle entry is actually recessed and arcaded.
        core.add_box(objects, f"MARKET_EntryDepth_{aisle_index}", (13.0, 1.4, 7.0), (centre_x, -20.1, 4.6), mats["interior"], cfg, "deep_arcaded_market_entrance")
        for leaf in (-3.1, 0.0, 3.1):
            core.add_box(objects, f"MARKET_EntryDoor_{aisle_index}_{leaf}", (2.7, 0.12, 5.8), (centre_x + leaf, -20.86, 4.35), mats["glass"], cfg, "physical_market_entry_leaf")
    # Shared party piers and continuous valley gutters make the three vaults one hall.
    for x in (-33.6, -11.0, 11.0, 33.6):
        core.add_box(objects, f"MARKET_BrickPier_{x:+.0f}", (1.3, 41.0, 9.5), (x, 0.0, 4.75), mats["primary"], cfg, "continuous_brick_aisle_spring_pier")
    for x in (-11.0, 11.0):
        core.add_box(objects, f"MARKET_ValleyGutter_{x:+.0f}", (0.45, 41.5, 0.36), (x, 0.0, 9.35), mats["roof"], cfg, "continuous_patinated_zinc_valley_gutter")
    # Both long walls are real arcades with recessed glazing, masonry piers,
    # spring rings and continuous stone strings. The original blank side slab
    # was the largest mismatch against the archetype sheet.
    for side_name, x, sign in (("Left", -34.30, -1.0), ("Right", 34.30, 1.0)):
        for bay, y in enumerate((-15.5, -10.3, -5.1, 0.1, 5.3, 10.5, 15.7)):
            core.add_box(objects, f"MARKET_{side_name}ArcadeDepth_{bay}", (0.55, 4.25, 6.8), (x - sign * 0.15, y, 5.0), mats["interior"], cfg, "deep_side_market_arcade")
            core.add_box(objects, f"MARKET_{side_name}ArcadeGlass_{bay}", (0.12, 4.0, 5.1), (x + sign * 0.22, y, 4.15), mats["glass"], cfg, "physical_side_market_glass")
            add_arch_ring_x(objects, name=f"MARKET_{side_name}ArcadeRing_{bay}", centre_y=y, facade_x=x + sign * 0.32, spring_z=5.7, inner_radius=2.0, ring_width=0.28, thickness=0.30, mat=mats["ornament"], cfg=cfg)
            for jamb_y in (y - 2.15, y + 2.15):
                core.add_box(objects, f"MARKET_{side_name}ArcadeJamb_{bay}_{jamb_y:+.1f}", (0.48, 0.34, 5.8), (x + sign * 0.15, jamb_y, 3.6), mats["secondary"], cfg, "load_bearing_side_arcade_jamb")
        core.add_box(objects, f"MARKET_{side_name}StoneString", (0.62, 39.0, 0.42), (x + sign * 0.12, 0.0, 8.25), mats["secondary"], cfg, "continuous_honey_stone_side_string")
        core.add_box(objects, f"MARKET_{side_name}IronCornice", (0.66, 40.0, 0.28), (x + sign * 0.14, 0.0, 9.25), mats["ornament"], cfg, "continuous_cast_iron_side_cornice")
    # Raised glazed lanterns articulate the three roof ridges and ventilate the
    # market hall, matching the layered roof silhouette in the reference.
    for aisle_index, centre_x in enumerate(aisle_centres):
        lantern_z = 20.5 if aisle_index == 1 else 19.4
        core.add_box(objects, f"MARKET_RidgeLanternDepth_{aisle_index}", (8.0, 31.0, 2.0), (centre_x, 1.5, lantern_z), mats["interior"], cfg, "occupied_ridge_ventilation_lantern")
        for x_face, sign, face in ((centre_x - 4.05, -1.0, "Left"), (centre_x + 4.05, 1.0, "Right")):
            core.add_window_band_x(objects, prefix=f"MARKET_Lantern{aisle_index}{face}", depth=29.0, facade_x=x_face, centre_z=lantern_z, height=1.7, bays=10, outward_sign=sign, mats=mats, cfg=cfg, margin=0.18)
        core.add_hip_roof(objects, name=f"MARKET_RidgeLanternRoof_{aisle_index}", width=8.8, depth=32.0, base_z=lantern_z + 1.0, height=1.3, ridge_fraction=0.78, mat=mats["roof"], cfg=cfg)
    # Market stalls, counters and mezzanine edges remain visible through the ends.
    for aisle_index, centre_x in enumerate(aisle_centres):
        for row in (-8.0, 0.0, 8.0):
            core.add_box(objects, f"MARKET_Stall_{aisle_index}_{row:+.0f}", (10.0, 3.8, 2.7), (centre_x, row, 2.45), mats["secondary"], cfg, "occupied_individual_market_stall")
            core.add_box(objects, f"MARKET_StallCanopy_{aisle_index}_{row:+.0f}", (10.4, 4.2, 0.20), (centre_x, row, 4.05), mats["roof"], cfg, "market_stall_canopy")
    core.add_box(objects, "MARKET_NarrowMezzanine", (64.0, 7.0, 0.32), (0.0, 12.0, 7.6), mats["secondary"], cfg, "narrow_occupied_market_mezzanine")
    add_guard_run(objects, prefix="MARKET_MezzanineGuard", start=(-31.0, 8.5, 8.75), end=(31.0, 8.5, 8.75), posts=24, mat=mats["ornament"], cfg=cfg)
    return objects


def add_variable_ribbon_wall(
    objects: list[bpy.types.Object],
    *,
    name: str,
    side: float,
    mat: bpy.types.Material,
    cfg: dict,
) -> bpy.types.Object:
    segments = 36
    half_thickness = 2.3
    vertices: list[tuple[float, float, float]] = []
    centres: list[tuple[float, float, float]] = []
    for index in range(segments + 1):
        t = index / segments
        y = -29.0 + t * 58.0
        x = side * (23.0 + 10.0 * math.sin((t - 0.15) * math.pi))
        top = 15.0 + (17.5 * (1.0 - t) if side < 0 else 17.5 * t) + 3.0 * math.sin(t * math.pi)
        centres.append((x, y, top))
    for z_mode in ("bottom", "top"):
        for edge in (-1.0, 1.0):
            for index, (x, y, top) in enumerate(centres):
                prev = centres[max(0, index - 1)]
                nxt = centres[min(segments, index + 1)]
                tangent = Vector((nxt[0] - prev[0], nxt[1] - prev[1], 0.0)).normalized()
                normal = Vector((-tangent.y, tangent.x, 0.0))
                z = 5.2 if z_mode == "bottom" else top
                vertices.append((x + normal.x * half_thickness * edge, y + normal.y * half_thickness * edge, z))
    stride = segments + 1
    layer = stride * 2
    faces: list[tuple[int, ...]] = []
    for edge in range(2):
        bottom = edge * stride
        top = layer + edge * stride
        for index in range(segments):
            quad = (bottom + index, bottom + index + 1, top + index + 1, top + index)
            faces.append(tuple(reversed(quad)) if edge == 0 else quad)
    for index in range(segments):
        faces.append((index, stride + index, stride + index + 1, index + 1))
        faces.append((layer + index, layer + index + 1, layer + stride + index + 1, layer + stride + index))
    for end in (0, segments):
        faces.append((end, layer + end, layer + stride + end, stride + end))
    return add_mesh(objects, name, vertices, faces, mat, cfg, "thick_weather_tight_bronze_acoustic_shell")


def build_bronze_curve_concert_hall(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "CONCERT_ConcretePlinth", (86.0, 60.0, 5.2), (0.0, 0.0, 2.6), mats["ornament"], cfg, "continuous_architectural_concrete_concert_plinth")
    add_variable_ribbon_wall(objects, name="CONCERT_LeftBronzeShell", side=-1.0, mat=mats["primary"], cfg=cfg)
    add_variable_ribbon_wall(objects, name="CONCERT_RightBronzeShell", side=1.0, mat=mats["primary"], cfg=cfg)
    # A solid acoustic room anchors both curved shells and explains their mass.
    core.add_box(objects, "CONCERT_CentralAuditorium", (43.0, 43.0, 23.0), (0.0, 4.0, 16.7), mats["ornament"], cfg, "solid_central_acoustic_auditorium")
    # The foyer canyon is a multi-level occupied room, not blue glazing pasted
    # between metal fins.
    core.add_box(objects, "CONCERT_FoyerDepth", (28.0, 16.0, 20.0), (0.0, -21.0, 15.2), mats["interior"], cfg, "deep_warm_timber_lined_foyer_canyon")
    core.add_window_band_y(objects, prefix="CONCERT_EntryCanyonGlass", width=27.0, facade_y=-29.15, centre_z=14.8, height=19.0, bays=8, outward_sign=-1.0, mats=mats, cfg=cfg, margin=0.15)
    for z in (9.0, 13.6, 18.2, 22.8):
        core.add_box(objects, f"CONCERT_FoyerFloor_{z}", (26.0, 15.0, 0.26), (0.0, -21.0, z), mats["secondary"], cfg, "visible_timber_foyer_balcony_floor")
        add_guard_run(objects, prefix=f"CONCERT_BalconyGuard_{z}", start=(-12.0, -28.1, z + 1.15), end=(12.0, -28.1, z + 1.15), posts=10, mat=mats["frame"], cfg=cfg)
    core.add_box(objects, "CONCERT_TimberEntrySoffit", (31.0, 15.0, 0.58), (0.0, -24.5, 9.1), mats["secondary"], cfg, "integral_warm_timber_entry_soffit")
    for door_index, x in enumerate((-8.0, -2.7, 2.7, 8.0)):
        core.add_box(objects, f"CONCERT_EntryDoor_{door_index}", (4.3, 0.16, 5.0), (x, -29.4, 7.7), mats["glass"], cfg, "physical_recessed_concert_entry_door")
    # Standing seams follow the wall curvature at a construction-scale cadence.
    for side, prefix in ((-1.0, "Left"), (1.0, "Right")):
        seam_centres: list[tuple[float, float, float]] = []
        for seam_index in range(29):
            t = seam_index / 28
            y = -28.0 + t * 56.0
            x = side * (23.0 + 10.0 * math.sin((t - 0.15) * math.pi))
            top = 15.0 + (17.5 * (1.0 - t) if side < 0 else 17.5 * t) + 3.0 * math.sin(t * math.pi)
            seam_centres.append((x, y, top))
        for seam_index, (x, y, top) in enumerate(seam_centres):
            prev = seam_centres[max(0, seam_index - 1)]
            nxt = seam_centres[min(len(seam_centres) - 1, seam_index + 1)]
            tangent = Vector((nxt[0] - prev[0], nxt[1] - prev[1], 0.0)).normalized()
            normal = Vector((-tangent.y, tangent.x, 0.0))
            # Put seams on both weather faces so they remain visible around the
            # full curved shell rather than hovering on a single approximation.
            for weather_face, offset in (("Outer", 2.34), ("Inner", -2.34)):
                sx = x + normal.x * offset
                sy = y + normal.y * offset
                core.add_beam(objects, f"CONCERT_{prefix}{weather_face}StandingSeam_{seam_index}", (sx, sy, 5.5), (sx, sy, top - 0.3), 0.075, mats["frame"], cfg, "physical_bronze_standing_seam")
            if seam_index:
                px, py, ptop = seam_centres[seam_index - 1]
                pprev = seam_centres[max(0, seam_index - 2)]
                ptangent = Vector((x - pprev[0], y - pprev[1], 0.0)).normalized()
                pnormal = Vector((-ptangent.y, ptangent.x, 0.0))
                core.add_beam(objects, f"CONCERT_{prefix}RoofEdge_{seam_index}", (px + pnormal.x * 2.34, py + pnormal.y * 2.34, ptop), (x + normal.x * 2.34, y + normal.y * 2.34, top), 0.12, mats["frame"], cfg, "continuous_bronze_shell_edge_cap")
    # Opposite low corners become planted terraces with real parapets.
    for suffix, x, y, z in (("West", -20.0, 17.0, 13.3), ("East", 20.0, -2.0, 13.3)):
        core.add_box(objects, f"CONCERT_PlantedTerrace_{suffix}", (15.0, 12.0, 0.55), (x, y, z), mats["roof"], cfg, "occupied_planted_roof_terrace")
        add_guard_run(objects, prefix=f"CONCERT_TerraceGuard_{suffix}", start=(x - 6.5, y - 5.2, z + 1.2), end=(x + 6.5, y - 5.2, z + 1.2), posts=7, mat=mats["frame"], cfg=cfg)
        for planter in range(4):
            px = x - 5.0 + planter * 3.3
            core.add_box(objects, f"CONCERT_TerracePlanter_{suffix}_{planter}", (2.4, 4.2, 0.45), (px, y, z + 0.55), mats["primary"], cfg, "integrated_roof_garden_planter")
            for shrub in range(3):
                core.add_sphere(objects, f"CONCERT_TerraceShrub_{suffix}_{planter}_{shrub}", 0.38, (px - 0.7 + shrub * 0.7, y, z + 1.0), mats["roof"], cfg, "living_roof_garden_shrub", scale=(1.1, 0.8, 0.75))
    # Rear stage loading is intentionally composed rather than left blank.
    core.add_box(objects, "CONCERT_RearStageDoorDepth", (18.0, 1.2, 7.0), (0.0, 29.4, 7.2), mats["interior"], cfg, "deep_rear_stage_loading_portal")
    core.add_box(objects, "CONCERT_RearStageDoor", (17.4, 0.16, 6.5), (0.0, 30.1, 7.2), mats["frame"], cfg, "physical_stage_loading_door")
    return objects


def add_leaning_prism(
    objects: list[bpy.types.Object],
    *,
    name: str,
    footprint: list[tuple[float, float]],
    top_shift: tuple[float, float],
    base_z: float,
    top_z: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
) -> bpy.types.Object:
    dx, dy = top_shift
    count = len(footprint)
    vertices = [(x, y, base_z) for x, y in footprint] + [
        (x + dx, y + dy, top_z) for x, y in footprint
    ]
    faces: list[tuple[int, ...]] = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    return add_mesh(objects, name, vertices, faces, mat, cfg, semantic)


def build_deconstructivist_fire_station(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    # The apparatus hall is built around three true open portals. There is no
    # concealed front wall behind the recesses.
    hall_footprint = [(-25.0, -12.0), (10.0, -14.0), (14.0, 5.0), (8.0, 14.0), (-24.0, 12.0)]
    add_extruded_footprint(objects, name="FIRE_ApparatusHallRearVolume", footprint=hall_footprint, base_z=0.0, top_z=[11.5, 12.8, 14.0, 12.0, 10.8], mat=mats["primary"], cfg=cfg, semantic="canted_board_formed_apparatus_hall")
    # A freestanding inner front line makes bay depth legible. Openings are
    # divided by structural piers and topped by a continuous black lintel.
    portal_centres = (-19.0, -8.0, 3.0)
    for bay, x in enumerate(portal_centres):
        core.add_box(objects, f"FIRE_ApparatusDepth_{bay}", (9.2, 6.0, 8.4), (x, -10.2 + x * -0.025, 4.4), mats["interior"], cfg, "deep_unobstructed_apparatus_bay")
        core.add_box(objects, f"FIRE_ApparatusDoor_{bay}", (8.6, 0.18, 7.7), (x, -13.35 + x * -0.025, 4.3), mats["ornament"], cfg, "physical_red_sectional_engine_door")
        for rail in range(5):
            core.add_box(objects, f"FIRE_DoorRail_{bay}_{rail}", (8.35, 0.22, 0.10), (x, -13.48 + x * -0.025, 1.0 + rail * 1.45), mats["frame"], cfg, "apparatus_door_section_joint")
    for pier_index, x in enumerate((-24.5, -13.5, -2.5, 8.5)):
        core.add_box(objects, f"FIRE_PortalPier_{pier_index}", (2.0, 6.2, 10.6), (x, -10.5 + x * -0.025, 5.3), mats["primary"], cfg, "load_bearing_canted_apparatus_pier")
    core.add_beam(objects, "FIRE_ContinuousPortalLintel", (-25.0, -12.55, 10.6), (9.5, -13.4, 12.0), 0.62, mats["frame"], cfg, "continuous_structural_apparatus_lintel")
    # Crew wing folds around a genuinely sheltered public entrance.
    crew_footprint = [(9.0, -14.0), (25.0, -12.0), (25.0, 9.0), (17.0, 16.0), (10.0, 9.0)]
    add_extruded_footprint(objects, name="FIRE_FoldedCrewWing", footprint=crew_footprint, base_z=0.0, top_z=[15.0, 18.5, 17.0, 20.0, 16.5], mat=mats["charcoal_dark"], cfg=cfg, semantic="folded_occupied_crew_wing")
    core.add_box(objects, "FIRE_PublicEntryDepth", (7.6, 5.5, 6.4), (17.0, -10.6, 4.0), mats["interior"], cfg, "deep_sheltered_public_entry")
    core.add_box(objects, "FIRE_PublicEntryGlass", (7.2, 0.12, 6.0), (17.0, -13.45, 4.0), mats["glass"], cfg, "physical_operations_entry_glass")
    add_slope_plate_x(objects, name="FIRE_EntryCanopy", x0=10.0, x1=25.0, y0=-16.0, y1=-8.0, z0=9.8, z1=12.0, thickness=0.38, mat=mats["roof"], cfg=cfg, semantic="integral_folded_public_entry_canopy")
    # Windows are recessed individually into the crew wing and wrap its return.
    for floor_index, z in enumerate((11.5, 15.5)):
        for window_index, x in enumerate((12.5, 16.5, 20.5)):
            front_y = -14.0 + (x - 9.0) * (2.0 / 16.0)
            core.add_box(objects, f"FIRE_CrewDepth_{floor_index}_{window_index}", (2.65, 0.52, 2.1), (x, front_y + 0.18, z), mats["interior"], cfg, "occupied_crew_room_depth")
            core.add_box(objects, f"FIRE_CrewGlass_{floor_index}_{window_index}", (2.4, 0.12, 1.85), (x, front_y - 0.15, z), mats["glass"], cfg, "physical_recessed_operations_window")
            for edge in (-1.17, 1.17):
                core.add_box(objects, f"FIRE_CrewReveal_{floor_index}_{window_index}_{edge}", (0.14, 0.6, 2.25), (x + edge, front_y, z), mats["frame"], cfg, "deep_window_reveal")
    core.add_window_band_x(objects, prefix="FIRE_CrewReturnWindows", depth=13.0, facade_x=25.15, centre_z=12.8, height=3.2, bays=4, outward_sign=1.0, mats=mats, cfg=cfg, margin=0.35)
    # The hose tower leans, but its entire base lands within the concrete hall.
    tower_fp = [(14.0, 2.0), (22.0, 1.2), (23.0, 9.0), (15.0, 11.2)]
    add_leaning_prism(objects, name="FIRE_LeaningHoseTower", footprint=tower_fp, top_shift=(2.8, -1.2), base_z=0.0, top_z=27.2, mat=mats["primary"], cfg=cfg, semantic="grounded_tapered_leaning_hose_tower")
    # The slit is a physical glass/interior assembly placed on the tower face.
    core.add_box(objects, "FIRE_TowerSlitDepth", (1.55, 0.48, 16.0), (21.0, 0.42, 17.0), mats["interior"], cfg, "deep_vertical_hose_tower_slit")
    core.add_box(objects, "FIRE_TowerSlitGlass", (1.20, 0.12, 15.4), (21.0, 0.13, 17.0), mats["glass"], cfg, "physical_vertical_hose_tower_glass")
    for edge_x in (20.32, 21.68):
        core.add_box(objects, f"FIRE_TowerSlitJamb_{edge_x:.2f}", (0.16, 0.58, 16.2), (edge_x, 0.31, 17.0), mats["frame"], cfg, "continuous_hose_tower_slit_jamb")
    for rail in range(5):
        core.add_box(objects, f"FIRE_TowerSlitRail_{rail}", (1.5, 0.58, 0.14), (21.0, 0.31, 10.5 + rail * 3.2), mats["frame"], cfg, "hose_tower_slit_transom")
    core.add_cylinder(objects, "FIRE_RoofBeacon", 0.65, 1.6, (24.0, 5.0, 28.0), mats["ornament"], cfg, "integrated_civic_emergency_beacon", vertices=20)
    # Dark folded roof planes close the angular volumes.
    add_slope_plate_x(objects, name="FIRE_ApparatusRoof", x0=-25.0, x1=11.0, y0=-9.0, y1=13.0, z0=11.4, z1=13.4, thickness=0.32, mat=mats["roof"], cfg=cfg, semantic="closed_folded_zinc_apparatus_roof")
    add_slope_plate_x(objects, name="FIRE_CrewWingRoof", x0=9.0, x1=25.0, y0=-11.0, y1=14.0, z0=16.0, z1=19.0, thickness=0.32, mat=mats["roof"], cfg=cfg, semantic="closed_folded_zinc_crew_roof")
    core.add_box(objects, "FIRE_RearOperationsGlass", (19.0, 0.12, 4.2), (-3.0, 14.1, 8.0), mats["glass"], cfg, "complete_rear_operations_glazing")
    core.add_box(objects, "FIRE_RearOperationsDepth", (19.0, 0.40, 4.2), (-3.0, 13.8, 8.0), mats["interior"], cfg, "occupied_rear_operations_depth")
    return objects


def build_assembled(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    return {
        "ski_slope_energy_plant": build_ski_slope_energy_plant,
        "wave_shell_natatorium": build_wave_shell_natatorium,
        "second_empire_city_hall": build_second_empire_city_hall,
        "greenhouse_vertical_farm": build_greenhouse_vertical_farm,
        "steel_rib_transit_hub": build_steel_rib_transit_hub,
        "monumental_silo_cluster": build_monumental_silo_cluster,
        "titanium_fold_museum": build_titanium_fold_museum,
        "historic_iron_glass_market": build_historic_iron_glass_market,
        "bronze_curve_concert_hall": build_bronze_curve_concert_hall,
        "deconstructivist_fire_station": build_deconstructivist_fire_station,
    }[cfg["shape"]](mats, cfg)


def build_module(
    role: str,
    variant: str,
    mats: dict,
    cfg: dict,
) -> tuple[list[bpy.types.Object], float]:
    """Build a complete semantic fallback bay, never a stretched pane."""
    objects: list[bpy.types.Object] = []
    width = cfg["native"][0] * 0.82
    depth = cfg["native"][1] * 0.78
    shape = cfg["shape"]
    if role == "podium":
        height = cfg["podium_height"]
        core.add_box(objects, "MODULE_PodiumPlinth", (width, depth, 0.35), (0.0, 0.0, 0.175), mats["secondary"], cfg, "complete_variant_podium_plinth", role=role)
        core.add_box(objects, "MODULE_PodiumEnvelope", (width, depth - 0.8, height - 0.35), (0.0, 0.4, 0.35 + (height - 0.35) / 2), mats["primary"], cfg, "complete_variant_podium_envelope", role=role)
        core.add_box(objects, "MODULE_EntranceDepth", (width * 0.34, 0.85, height * 0.68), (0.0, -depth / 2, height * 0.45), mats["interior"], cfg, "fixed_deep_public_entrance", role=role)
        core.add_box(objects, "MODULE_EntranceGlass", (width * 0.32, 0.10, height * 0.62), (0.0, -depth / 2 - 0.48, height * 0.45), mats["glass"], cfg, "physical_public_entry_glass", role=role)
    elif role == "floor":
        height = cfg["floor_height"]
        phase = {"typical_a": 0, "typical_b": 1, "typical_c": 2}[variant]
        if shape == "monumental_silo_cluster":
            for index, x in enumerate((-width * 0.28, 0.0, width * 0.28)):
                core.add_cylinder(objects, f"MODULE_Silo_{variant}_{index}", width * 0.105, height, (x, 0.0, height / 2), mats["primary"], cfg, "repeatable_complete_silo_course", vertices=20, role=role)
            core.add_box(objects, f"MODULE_SiloCatwalk_{variant}", (width * 0.85, 2.0, 0.20), (0.0, -depth * 0.32, height * (0.35 + phase * 0.15)), mats["frame"], cfg, "repeatable_supported_process_catwalk", role=role)
        else:
            core.add_box(objects, f"MODULE_FloorDepth_{variant}", (width, depth - 0.7, height), (0.0, 0.35, height / 2), mats["interior"], cfg, "repeatable_complete_occupied_bay_depth", role=role)
            core.add_window_band_y(objects, prefix=f"MODULE_Front_{variant}", width=width - 0.4, facade_y=-depth / 2, centre_z=height / 2, height=max(1.0, height - 0.45), bays=7 + phase, outward_sign=-1.0, mats=mats, cfg=cfg, role=role, margin=0.2)
            core.add_window_band_y(objects, prefix=f"MODULE_Rear_{variant}", width=width - 0.4, facade_y=depth / 2, centre_z=height / 2, height=max(1.0, height - 0.45), bays=6 + phase, outward_sign=1.0, mats=mats, cfg=cfg, role=role, margin=0.2)
            core.add_window_band_x(objects, prefix=f"MODULE_Left_{variant}", depth=depth - 0.4, facade_x=-width / 2, centre_z=height / 2, height=max(1.0, height - 0.45), bays=4 + phase, outward_sign=-1.0, mats=mats, cfg=cfg, role=role, margin=0.2)
            core.add_window_band_x(objects, prefix=f"MODULE_Right_{variant}", depth=depth - 0.4, facade_x=width / 2, centre_z=height / 2, height=max(1.0, height - 0.45), bays=4 + phase, outward_sign=1.0, mats=mats, cfg=cfg, role=role, margin=0.2)
            if shape == "greenhouse_vertical_farm":
                for crop in range(5):
                    core.add_box(objects, f"MODULE_CropTray_{variant}_{crop}", (width * 0.75, depth * 0.10, 0.28), (0.0, -depth * 0.25 + crop * depth * 0.12, 0.8 + phase * 0.12), mats["primary"], cfg, "repeatable_visible_hydroponic_crop_tray", role=role)
            elif shape in {"steel_rib_transit_hub", "wave_shell_natatorium", "historic_iron_glass_market"}:
                core.add_beam(objects, f"MODULE_LongSpanBraceA_{variant}", (-width / 2, -depth / 2, 0.2), (width / 2, -depth / 2, height - 0.2), 0.18, mats["frame"], cfg, "repeatable_complete_long_span_structural_bay", role=role)
                core.add_beam(objects, f"MODULE_LongSpanBraceB_{variant}", (width / 2, depth / 2, 0.2), (-width / 2, depth / 2, height - 0.2), 0.18, mats["frame"], cfg, "repeatable_complete_long_span_structural_bay", role=role)
    elif role == "crown":
        height = max(0.45, cfg["crown_height"])
        core.add_box(objects, "MODULE_CrownTransition", (width, depth, height), (0.0, 0.0, height / 2), mats["ornament"], cfg, "fixed_variant_crown_transition", role=role)
    else:
        height = max(0.55, cfg["roof_height"])
        if shape in {"ski_slope_energy_plant", "bronze_curve_concert_hall", "deconstructivist_fire_station"}:
            add_slope_plate_x(objects, name="MODULE_SlopedRoof", x0=-width / 2, x1=width / 2, y0=-depth / 2, y1=depth / 2, z0=0.55, z1=height, thickness=0.30, mat=mats["roof"], cfg=cfg, semantic="fixed_variant_sloped_roof", role=role)
        elif shape in {"wave_shell_natatorium", "historic_iron_glass_market", "steel_rib_transit_hub"}:
            add_barrel_shell_y(objects, name="MODULE_LongSpanRoof", centre_x=0.0, half_width=width / 2, y0=-depth / 2, y1=depth / 2, spring_z=0.15, rise=height, thickness=0.20, mat=mats["roof"], cfg=cfg)
            for rib in range(5):
                y = -depth / 2 + rib * depth / 4
                points = []
                for segment in range(13):
                    angle = math.pi * segment / 12
                    points.append((-math.cos(angle) * width / 2, y, 0.15 + math.sin(angle) * height + 0.2))
                add_polyline_beams(objects, prefix=f"MODULE_RoofRib_{rib}", points=points, radius=0.13, mat=mats["frame"], cfg=cfg, semantic="fixed_long_span_roof_rib", role=role)
        else:
            core.add_box(objects, "MODULE_Roof", (width, depth, min(0.60, height)), (0.0, 0.0, min(0.60, height) / 2), mats["roof"], cfg, "fixed_variant_roof", role=role)
    for marker in core.module_contract_markers(role, variant, height):
        objects.append(core.tag_object(marker, "four_elevation_material_contract", cfg, role=role))
    return objects, height


def footprint_contract(cfg: dict) -> dict:
    width, depth, _height = cfg["native"]
    bay = round(width / (8 if width >= 70 else 6), 2)
    floors = [cfg["min_floors"], cfg["max_floors"]]
    rectangle = {
        "recommendedWidth_m": [round(width * 0.66, 1), round(width * 1.80, 1)],
        "recommendedDepth_m": [round(depth * 0.66, 1), round(depth * 1.58, 1)],
        "recommendedFloors": floors,
        "scaleMin": 0.62,
        "scaleMax": 1.40,
        "maxAxisRatio": 1.30,
        "preferredBayMultiple_m": bay,
    }
    profiles = {"rectangle": rectangle}
    preferred = ["rectangle"]
    if cfg["shape"] == "deconstructivist_fire_station":
        profiles["l_shape"] = {
            "recommendedWidth_m": [round(width * 0.72, 1), round(width * 2.05, 1)],
            "recommendedDepth_m": [round(depth * 0.70, 1), round(depth * 1.80, 1)],
            "recommendedFloors": floors,
            "scaleMin": 0.62,
            "scaleMax": 1.40,
            "maxAxisRatio": 1.32,
            "preferredBayMultiple_m": bay,
            "wingDepth_m": [round(depth * 0.28, 1), round(depth * 0.65, 1)],
        }
        preferred.append("l_shape")
    return {
        "preferredProfiles": preferred,
        "minimumPreferredProfiles": len(preferred),
        "profileRationale": (
            "The complete reference landmark tolerates independent-axis drawing error from 0.62x to 1.40x. "
            f"Oversized targets repeat whole {bay:.2f} m structural or occupied construction bays along the long axis; "
            "entrances, structural spring points, process equipment, roof topology, crowns and end conditions remain fixed."
        ),
        "fixedLandmarkScaleBand": {"scaleMin": 0.62, "scaleMax": 1.40, "maxAxisRatio": 1.30},
        **rectangle,
        "profiles": profiles,
    }


def massing_graph(cfg: dict) -> dict:
    features = {
        "ski_slope_energy_plant": ["continuous_inhabited_ski_slope", "integrated_climbing_wall", "summit_process_deck", "glass_public_elevator", "faceted_emissions_stack"],
        "wave_shell_natatorium": ["continuous_double_curved_shell", "branching_concrete_struts", "grounded_cable_masts", "visible_pool_hall", "deep_glazed_gables"],
        "second_empire_city_hall": ["deep_triple_arch_civic_portal", "continuous_mansard", "four_corner_turrets", "dormers_and_chimneys", "clock_tower_and_copper_dome"],
        "greenhouse_vertical_farm": ["thirty_visible_cultivation_decks", "real_hydroponic_crop_trays", "clear_greenhouse_enclosure", "external_structural_braces", "vented_greenhouse_crown"],
        "steel_rib_transit_hub": ["twin_grounded_parabolic_arches", "continuous_fan_rib_field", "translucent_station_roof", "deep_luminous_concourse", "occupied_cross_concourse_bridges"],
        "monumental_silo_cluster": ["exactly_eight_full_height_silos", "individual_hoppers_and_caps", "glazed_conveyor_headhouse", "enclosed_truss_galleries", "supported_catwalks_stairs_and_pipes"],
        "titanium_fold_museum": ["two_closed_rolled_gallery_shells", "three_closed_folded_gallery_wedges", "full_height_glazed_canyon", "supported_gallery_bridge", "deep_public_entry"],
        "historic_iron_glass_market": ["three_connected_barrel_vaults", "fourteen_aligned_iron_arch_frames", "radial_gable_fanlights", "shared_brick_spring_piers", "visible_market_stalls_and_mezzanine"],
        "bronze_curve_concert_hall": ["two_opposing_thick_bronze_shells", "solid_central_auditorium", "timber_lined_glazed_foyer_canyon", "descending_planted_terraces", "complete_rear_stage_loading"],
        "deconstructivist_fire_station": ["three_true_deep_apparatus_portals", "folded_occupied_crew_wing", "sheltered_public_entry", "grounded_leaning_hose_tower", "closed_angular_roof_planes"],
    }[cfg["shape"]]
    return {
        "type": f"fixed_{cfg['shape']}_with_repeatable_complete_middle_bays",
        "variant_id": cfg["variant_id"],
        "occupied_storeys": cfg["native_floors"],
        "features": features,
        "physical_window_layers": ["occupied_depth", "physical_pane", "separate_frame", "structural_or_screen_layer", "floor_datum", "material_return"],
        "fallback_policy": "fixed identity ends plus repeatable complete middle construction bays",
    }


def install_wave15_hooks() -> None:
    core.FAMILIES = FAMILIES
    core.load_palette = load_palette
    core.build_assembled = build_assembled
    core.build_module = build_module
    core.footprint_contract = footprint_contract
    core.massing_graph = massing_graph
    core.view_map = view_map


def postprocess_manifest(output_root: Path, cfg: dict) -> None:
    folder = (output_root / cfg["family"]).resolve()
    manifest_path = folder / f"{cfg['family']}_manifest.json"
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["generator"] = {
        **(manifest.get("generator") or {}),
        "name": "archetype_compiler/generate_wave15_mixed_families.py",
        "version": "1.0.0",
    }
    graph = massing_graph(cfg)
    manifest["generation_tags"] = [
        "wave15",
        cfg["cohort"],
        "reference_locked_goalpost",
        "six_zone_custom_pbr_skin",
        "fixed_landmark_and_modular_fallback",
        "physical_separate_glazing",
        "occupied_interior_depth",
        "continuous_program_topology",
        "credible_structural_load_paths",
        "complete_semantic_bay_repeat",
        *graph["features"],
    ]
    provenance = manifest.get("source_provenance") or {}
    provenance["method"] = (
        "variant-locked four-view construction goalpost, separate six-zone material capture, deterministic true-metric geometry, "
        "continuous program and roof topology, physical load paths, physical layered glazing, occupied depth, complete secondary "
        "elevations, fixed whole-building landmark and complete-semantic-bay LEGO fallback modules"
    )
    provenance["coverage_cohort"] = cfg["cohort"]
    manifest["source_provenance"] = provenance
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (folder / "archetype-source.json").write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    cfg = with_family(args.family)
    install_wave15_hooks()
    if args.render_existing:
        core.render_existing(args.output_root, cfg, view_set=args.view_set)
    else:
        core.build_family(
            args.output_root,
            cfg,
            view_set=args.view_set,
            skip_renders=args.skip_renders,
            skip_modules=args.skip_modules,
            skip_assembled_export=args.skip_assembled_export,
        )
    postprocess_manifest(args.output_root, cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
