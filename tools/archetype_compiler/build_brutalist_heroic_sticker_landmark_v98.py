"""Deterministic exact-image geometry for the Heroic Brutalism landmark."""
from __future__ import annotations

import hashlib
import json
from typing import Any

ARCHETYPE_ID = "brutalist_institutional"
VARIANT_ID = "brutalist_heroic"
WIDTH_M = 50.0
DEPTH_M = 42.0
FRONT_Y = -21.0
REAR_Y = 21.0
REFERENCE_PATHS = [
    "frontend/public/archetypes/buildings/brutalist_institutional/variant_0.png",
    "frontend/public/archetypes/buildings/brutalist_institutional/variant_0_angle_60.jpg",
    "frontend/public/archetypes/buildings/brutalist_institutional/variant_0_angle_90.jpg",
]


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def mesh(name: str, vertices: list[list[float]], faces: list[list[int]], owner: str,
         domain: str, **meta: Any) -> dict[str, Any]:
    return {
        "name": name,
        "vertices": vertices,
        "faces": faces,
        "face_owners": [[owner] for _ in faces],
        "sticker_owner_id": owner,
        "material_domain": domain,
        "face_roles": [domain] * len(faces),
        **meta,
    }


def box(name: str, bounds: tuple[float, float, float, float, float, float], owner: str,
        domain: str, **meta: Any) -> dict[str, Any]:
    x0, x1, y0, y1, z0, z1 = bounds
    vertices = [
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ]
    return mesh(name, vertices, [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
                                  [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]],
                owner, domain, closed=True, outward_winding=True, **meta)


def plane(name: str, vertices: list[list[float]], owner: str, domain: str,
          **meta: Any) -> dict[str, Any]:
    return mesh(name, vertices, [list(range(len(vertices)))], owner, domain, **meta)


def prism(name: str, section: list[tuple[float, float]], y0: float, y1: float,
          owner: str, domain: str, **meta: Any) -> dict[str, Any]:
    """Extrude an X/Z section along Y with a watertight outward shell."""
    n = len(section)
    vertices = [[x, y0, z] for x, z in section] + [[x, y1, z] for x, z in section]
    faces = [list(reversed(range(n))), list(range(n, 2 * n))]
    faces += [[i, (i + 1) % n, (i + 1) % n + n, i + n] for i in range(n)]
    return mesh(name, vertices, faces, owner, domain, closed=True, outward_winding=True, **meta)


def _front_aperture(meshes: list[dict[str, Any]], name: str, x0: float, x1: float,
                    z0: float, z1: float, *, kind: str, level: int) -> dict[str, Any]:
    outer_y, glass_y, card_y, backing_y = FRONT_Y - 1.42, FRONT_Y + 0.34, FRONT_Y + 0.48, FRONT_Y + 0.72
    # Monumental projecting cheeks and a strongly sloped sill make the shadow section physical.
    meshes += [
        box(name + "_left_cheek", (x0 - .24, x0, FRONT_Y - .78, FRONT_Y + .30, z0 - .42, z1 + .38),
            "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="projecting_lightbox_cheek", side="front", level=level),
        box(name + "_dominant_blade", (x1, x1 + .92, outer_y, FRONT_Y + .30, z0 - .62, z1 + .58),
            "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="dominant_projecting_lightbox_blade", side="front", level=level),
        box(name + "_head", (x0, x1, outer_y, FRONT_Y + .30, z1, z1 + .38),
            "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="projecting_lightbox_head", side="front", level=level),
        prism(name + "_splayed_sill", [(x0, z0), (x1, z0), (x1 - .18, z0 - .72), (x0 + .52, z0 - .72)],
              outer_y, FRONT_Y + .30, "sticker_deep_reveal", "deep_concrete_reveal",
              carrier_kind="splayed_lightbox_sill", side="front", level=level),
    ]
    meshes += [
        plane(name + "_glass", [[x0 + .28, glass_y, z0 + .08], [x1 - .28, glass_y, z0 + .08],
                                 [x1 - .28, glass_y, z1 - .18], [x0 + .28, glass_y, z1 - .18]],
              "sticker_upper_glass", "physical_glass", carrier_kind="recessed_glass", side="front", level=level),
        plane(name + "_card", [[x0 + .22, card_y, z0 + .02], [x1 - .22, card_y, z0 + .02],
                                [x1 - .22, card_y, z1 - .12], [x0 + .22, card_y, z1 - .12]],
              "sticker_upper_card", "interior_card", carrier_kind="occupied_interior_card", side="front", level=level),
        plane(name + "_backing", [[x0 + .16, backing_y, z0 - .04], [x1 - .16, backing_y, z0 - .04],
                                   [x1 - .16, backing_y, z1 - .06], [x0 + .16, backing_y, z1 - .06]],
              "sticker_upper_backing", "interior_backing", carrier_kind="opaque_interior_backing", side="front", level=level),
    ]
    return {"name": name, "kind": kind, "side": "front", "bounds": [x0, x1, z0, z1]}


def _side_aperture(meshes: list[dict[str, Any]], name: str, y0: float, y1: float,
                   z0: float, z1: float, *, side: str, level: int) -> dict[str, Any]:
    assert side in {"right", "left"}
    sign = 1 if side == "right" else -1
    wall_x = 24.0 * sign
    outer_x = (24.86 if side == "right" else -24.86)
    glass_x = (23.66 if side == "right" else -23.66)
    card_x = (23.52 if side == "right" else -23.52)
    backing_x = (23.28 if side == "right" else -23.28)
    x0, x1 = sorted((wall_x, outer_x))
    meshes += [
        box(name + "_front_cheek", (x0, x1, y0 - .48, y0, z0 - .42, z1 + .38),
            "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="projecting_lightbox_cheek", side=side, level=level),
        box(name + "_rear_cheek", (x0, x1, y1, y1 + .48, z0 - .42, z1 + .38),
            "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="projecting_lightbox_cheek", side=side, level=level),
        box(name + "_head", (x0, x1, y0, y1, z1, z1 + .38),
            "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="projecting_lightbox_head", side=side, level=level),
        box(name + "_sill", (x0, x1, y0 + .32, y1 - .32, z0 - .58, z0),
            "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="splayed_lightbox_sill", side=side, level=level),
    ]
    # Vertex ordering is outward-facing on each side.
    ys = (y0 + .28, y1 - .28)
    if side == "right":
        glass_v = [[glass_x, ys[0], z0 + .08], [glass_x, ys[1], z0 + .08], [glass_x, ys[1], z1 - .18], [glass_x, ys[0], z1 - .18]]
        card_v = [[card_x, ys[0], z0 + .02], [card_x, ys[1], z0 + .02], [card_x, ys[1], z1 - .12], [card_x, ys[0], z1 - .12]]
        back_v = [[backing_x, y0 + .22, z0 - .04], [backing_x, y1 - .22, z0 - .04], [backing_x, y1 - .22, z1 - .06], [backing_x, y0 + .22, z1 - .06]]
    else:
        glass_v = [[glass_x, ys[1], z0 + .08], [glass_x, ys[0], z0 + .08], [glass_x, ys[0], z1 - .18], [glass_x, ys[1], z1 - .18]]
        card_v = [[card_x, ys[1], z0 + .02], [card_x, ys[0], z0 + .02], [card_x, ys[0], z1 - .12], [card_x, ys[1], z1 - .12]]
        back_v = [[backing_x, y1 - .22, z0 - .04], [backing_x, y0 + .22, z0 - .04], [backing_x, y0 + .22, z1 - .06], [backing_x, y1 - .22, z1 - .06]]
    meshes += [
        plane(name + "_glass", glass_v, "sticker_upper_glass", "physical_glass", carrier_kind="recessed_glass", side=side, level=level),
        plane(name + "_card", card_v, "sticker_upper_card", "interior_card", carrier_kind="occupied_interior_card", side=side, level=level),
        plane(name + "_backing", back_v, "sticker_upper_backing", "interior_backing", carrier_kind="opaque_interior_backing", side=side, level=level),
    ]
    return {"name": name, "kind": "monumental_lightbox", "side": side, "bounds": [y0, y1, z0, z1]}


def _panelize_run(meshes: list[dict[str, Any]], prefix: str, axis: str, start: float, end: float,
                  openings: list[tuple[float, float]], z0: float, z1: float, side: str) -> None:
    cursor = start
    for index, (a, b) in enumerate(sorted(openings)):
        if a > cursor:
            bounds = (cursor, a, FRONT_Y, FRONT_Y + .34, z0, z1) if axis == "x" else (
                23.66, 24.0, cursor, a, z0, z1)
            meshes.append(box(f"{prefix}_pier_{index}", bounds, "sticker_board_concrete", "boardformed_concrete",
                              carrier_kind="opaque_upper_wall_panel", side=side))
        cursor = b
    if cursor < end:
        bounds = (cursor, end, FRONT_Y, FRONT_Y + .34, z0, z1) if axis == "x" else (
            23.66, 24.0, cursor, end, z0, z1)
        meshes.append(box(f"{prefix}_pier_terminal", bounds, "sticker_board_concrete", "boardformed_concrete",
                          carrier_kind="opaque_upper_wall_panel", side=side))


def build_geometry(size: str = "canonical") -> dict[str, Any]:
    if size != "canonical":
        raise KeyError(size)
    meshes: list[dict[str, Any]] = []
    apertures: list[dict[str, Any]] = []

    # One two-level institutional body: recessed public ground and massive cantilevered upper shell.
    meshes.append(box("ground_slab", (-25, 25, FRONT_Y, REAR_Y, 0, .22), "sticker_plinth", "weathered_concrete",
                      carrier_kind="fixed_ground_slab"))
    meshes.append(box("upper_floor_ring", (-24, 24, FRONT_Y + .34, REAR_Y - .34, 4.72, 5.04),
                      "sticker_soffit", "weathered_soffit", carrier_kind="cantilevered_upper_floor"))
    meshes.append(box("front_cantilever_soffit", (-24, 24, FRONT_Y - .72, FRONT_Y + .34, 4.72, 5.04),
                      "sticker_soffit", "weathered_soffit", carrier_kind="deep_cantilever_soffit"))

    # Dark recessed ground curtain wall, real entrance, and physical bronze grid.
    meshes.append(plane("ground_front_glass", [[-21.5, FRONT_Y + .48, .45], [21.5, FRONT_Y + .48, .45],
                                                [21.5, FRONT_Y + .48, 4.58], [-21.5, FRONT_Y + .48, 4.58]],
                        "sticker_ground_glass", "physical_glass", carrier_kind="continuous_ground_glass", side="front", level=0))
    meshes.append(plane("ground_front_card", [[-21.4, FRONT_Y + .64, .45], [21.4, FRONT_Y + .64, .45],
                                               [21.4, FRONT_Y + .64, 4.58], [-21.4, FRONT_Y + .64, 4.58]],
                        "sticker_ground_card", "interior_card", carrier_kind="occupied_interior_card", side="front", level=0))
    meshes.append(plane("ground_front_backing", [[-21.4, FRONT_Y + .82, .40], [21.4, FRONT_Y + .82, .40],
                                                  [21.4, FRONT_Y + .82, 4.62], [-21.4, FRONT_Y + .82, 4.62]],
                        "sticker_ground_backing", "interior_backing", carrier_kind="opaque_interior_backing", side="front", level=0))
    for i, x in enumerate(range(-21, 22, 3)):
        meshes.append(box(f"ground_front_mullion_{i}", (x - .035, x + .035, FRONT_Y + .42, FRONT_Y + .55, .45, 4.58),
                          "sticker_bronze", "dark_bronze", carrier_kind="curtain_wall_mullion", side="front"))
    meshes.append(box("ground_front_transom", (-21.5, 21.5, FRONT_Y + .42, FRONT_Y + .55, 2.62, 2.72),
                      "sticker_bronze", "dark_bronze", carrier_kind="curtain_wall_transom", side="front"))
    meshes.append(box("ground_front_glass_head_closure",
                      (-21.5, 21.5, FRONT_Y + .34, FRONT_Y + .62, 4.58, 4.72),
                      "sticker_soffit", "weathered_soffit", carrier_kind="ground_glazing_head_closure",
                      side="front", adjacent_finish_terminal=True,
                      terminal_source_map="weathered_soffit"))
    # Singular recessed entry portal and paired doors.
    for label, bounds in (
        ("left", (-3.65, -3.28, FRONT_Y - .62, FRONT_Y + .60, .20, 3.22)),
        ("right", (3.28, 3.65, FRONT_Y - .62, FRONT_Y + .60, .20, 3.22)),
        ("head", (-3.28, 3.28, FRONT_Y - .62, FRONT_Y + .60, 2.86, 3.22)),
    ):
        meshes.append(box(f"entry_portal_{label}", bounds, "sticker_board_concrete", "boardformed_concrete",
                          carrier_kind="recessed_entry_portal", side="front", fixed=True))
    for i, (a, b) in enumerate(((-2.92, -.12), (.12, 2.92))):
        meshes.append(plane(f"entry_door_{i}_glass", [[a, FRONT_Y + .66, .42], [b, FRONT_Y + .66, .42],
                                                       [b, FRONT_Y + .66, 2.72], [a, FRONT_Y + .66, 2.72]],
                            "sticker_ground_glass", "physical_glass", carrier_kind="entry_door_glass", side="front", level=0))
        meshes.append(plane(f"entry_door_{i}_backing", [[a + .04, FRONT_Y + .88, .38], [b - .04, FRONT_Y + .88, .38],
                                                         [b - .04, FRONT_Y + .88, 2.76], [a + .04, FRONT_Y + .88, 2.76]],
                            "sticker_ground_backing", "interior_backing", carrier_kind="opaque_interior_backing", side="front", level=0))
        for j, x in enumerate((a, (a + b) / 2, b)):
            meshes.append(box(f"entry_door_{i}_stile_{j}", (x - .035, x + .035, FRONT_Y + .61, FRONT_Y + .70, .42, 2.72),
                              "sticker_bronze", "dark_bronze", carrier_kind="entry_door_frame", side="front"))

    # Sculptural pilotis: narrow stems and flared hammerhead capitals.
    for i, x in enumerate((-17.2, -7.2, 7.2, 17.2)):
        meshes.append(box(f"front_piloti_{i}_stem", (x - .34, x + .34, FRONT_Y - .48, FRONT_Y + .28, .20, 3.30),
                          "sticker_board_concrete", "boardformed_concrete", carrier_kind="piloti_stem", side="front", fixed=True))
        meshes.append(prism(f"front_piloti_{i}_flared_capital",
                            [(x - .40, 3.55), (x + .40, 3.55), (x + 1.05, 4.72), (x - 1.05, 4.72)],
                            FRONT_Y - .48, FRONT_Y + .28, "sticker_board_concrete", "boardformed_concrete",
                            carrier_kind="flared_piloti_capital", side="front", fixed=True))
        # One shallow, concrete-owned collar closes the capital/stem bearing.
        # It wraps the stem front and returns while remaining inside the
        # capital's lower footprint; the only intersection is intentional
        # structural bearing contact in the 3.30–3.55m joint zone.
        meshes.append(box(f"front_piloti_{i}_capital_stem_collar",
                          (x - .40, x + .40, FRONT_Y - .48, FRONT_Y + .28, 3.30, 3.55),
                          "sticker_board_concrete", "boardformed_concrete",
                          carrier_kind="piloti_capital_stem_collar", side="front", fixed=True,
                          joint_role="capital_stem_closure", adjacent_finish="boardformed_concrete",
                          intentional_bearing_contact=True, outward_front_and_returns=True,
                          no_exposed_terminal=True))

    front_openings = [(-14.8, -11.2), (7.8, 11.4)]
    for i, (a, b) in enumerate(front_openings):
        apertures.append(_front_aperture(meshes, f"front_monumental_lightbox_{i}", a, b, 6.45, 11.35,
                                         kind="monumental_lightbox", level=1))
    # The fixed left tower and right bookend own the terminal construction;
    # the ordinary upper shell meets them at boundaries instead of intersecting them.
    _panelize_run(meshes, "front_upper", "x", -22.15, 21.65, front_openings, 5.04, 12.42, "front")
    for i, (a, b) in enumerate(front_openings):
        meshes.append(box(f"front_upper_sill_zone_{i}", (a, b, FRONT_Y, FRONT_Y + .34, 5.04, 5.87),
                          "sticker_board_concrete", "boardformed_concrete", carrier_kind="aperture_sill_wall", side="front"))
        meshes.append(box(f"front_upper_head_zone_{i}", (a, b, FRONT_Y, FRONT_Y + .34, 11.73, 12.42),
                          "sticker_board_concrete", "boardformed_concrete", carrier_kind="aperture_head_wall", side="front"))

    # Exact-image terminal asymmetry: a full-height blind right bookend and a
    # subordinate narrow left circulation tower with slit glazing.
    meshes.append(box("fixed_blind_right_bookend", (21.65, 25.0, FRONT_Y - .62, FRONT_Y, .20, 13.30),
                      "sticker_board_concrete", "boardformed_concrete", carrier_kind="blind_terminal_bookend",
                      side="front", fixed=True, exact_identity=True))
    # Panelize the narrow left tower around three real slot voids.  A single
    # solid carrier here would leave the glass applied to opaque concrete.
    for label, bounds in (
        ("left_rail", (-25.0, -24.45, FRONT_Y - .28, FRONT_Y, .20, 12.84)),
        ("right_rail", (-23.60, -22.15, FRONT_Y - .28, FRONT_Y, .20, 12.84)),
        ("lower_infill", (-24.45, -23.60, FRONT_Y - .28, FRONT_Y, .20, 1.15)),
        ("middle_infill_0", (-24.45, -23.60, FRONT_Y - .28, FRONT_Y, 4.28, 6.02)),
        ("middle_infill_1", (-24.45, -23.60, FRONT_Y - .28, FRONT_Y, 9.02, 9.42)),
        ("head_infill", (-24.45, -23.60, FRONT_Y - .28, FRONT_Y, 12.10, 12.84)),
    ):
        meshes.append(box(f"fixed_left_slot_tower_{label}", bounds,
                          "sticker_board_concrete", "boardformed_concrete", carrier_kind="left_slot_tower",
                          side="front", fixed=True, exact_identity=True, panelized_around_slots=True))
    for level, (z0, z1) in enumerate(((1.15, 4.28), (6.02, 9.02), (9.42, 12.10))):
        meshes.append(plane(f"left_slot_tower_glass_{level}", [[-24.30, FRONT_Y - .30, z0], [-23.76, FRONT_Y - .30, z0],
                                                                [-23.76, FRONT_Y - .30, z1], [-24.30, FRONT_Y - .30, z1]],
                            "sticker_upper_glass", "physical_glass", carrier_kind="tower_slot_glass", side="front", level=level))
        meshes.append(plane(f"left_slot_tower_backing_{level}", [[-24.34, FRONT_Y + .02, z0 - .04], [-23.72, FRONT_Y + .02, z0 - .04],
                                                                  [-23.72, FRONT_Y + .02, z1 + .04], [-24.34, FRONT_Y + .02, z1 + .04]],
                            "sticker_upper_backing", "interior_backing", carrier_kind="opaque_interior_backing", side="front", level=level))

    # Three right-return light boxes repeat the exact heroic section; left/rear are restrained completion.
    side_openings = [(-15.8, -10.2), (-2.8, 2.8), (10.2, 15.8)]
    for i, (a, b) in enumerate(side_openings):
        apertures.append(_side_aperture(meshes, f"right_monumental_lightbox_{i}", a, b, 6.45, 11.35,
                                        side="right", level=1))
    _panelize_run(meshes, "right_upper", "y", FRONT_Y + .34, REAR_Y - .34, side_openings, 5.04, 12.42, "right")
    for i, (a, b) in enumerate(side_openings):
        meshes.append(box(f"right_upper_sill_zone_{i}", (23.66, 24, a, b, 5.04, 5.87),
                          "sticker_return_concrete", "boardformed_concrete", carrier_kind="aperture_sill_wall", side="right"))
        meshes.append(box(f"right_upper_head_zone_{i}", (23.66, 24, a, b, 11.73, 12.42),
                          "sticker_return_concrete", "boardformed_concrete", carrier_kind="aperture_head_wall", side="right"))
    # Constrained left/rear completion stays subordinate but is not blank:
    # panelize around restrained deep institutional slots.
    rear_openings = [(-16.5, -12.5), (-4.0, 0.0), (8.5, 12.5)]
    left_openings = [(-12.0, -8.0), (1.5, 5.5), (12.0, 16.0)]
    cursor = -23.66
    for i, (a, b) in enumerate(rear_openings):
        if a > cursor:
            meshes.append(box(f"rear_upper_pier_{i}", (cursor, a, REAR_Y - .34, REAR_Y, 5.04, 12.42),
                              "sticker_return_concrete", "boardformed_concrete", carrier_kind="constrained_rear_wall", side="rear"))
        meshes.append(box(f"rear_upper_slot_{i}_left", (a, a + .30, REAR_Y - .55, REAR_Y, 6.18, 11.34),
                          "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="rear_slot_reveal", side="rear"))
        meshes.append(box(f"rear_upper_slot_{i}_right", (b - .30, b, REAR_Y - .55, REAR_Y, 6.18, 11.34),
                          "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="rear_slot_reveal", side="rear"))
        meshes.append(box(f"rear_upper_slot_{i}_head", (a + .30, b - .30, REAR_Y - .55, REAR_Y, 11.06, 11.34),
                          "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="rear_slot_reveal", side="rear"))
        meshes.append(box(f"rear_upper_slot_{i}_sill", (a + .30, b - .30, REAR_Y - .55, REAR_Y, 6.18, 6.48),
                          "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="rear_slot_reveal", side="rear"))
        meshes.append(plane(f"rear_upper_slot_{i}_glass", [[b - .30, REAR_Y - .58, 6.48], [a + .30, REAR_Y - .58, 6.48],
                                                             [a + .30, REAR_Y - .58, 11.06], [b - .30, REAR_Y - .58, 11.06]],
                            "sticker_upper_glass", "physical_glass", carrier_kind="recessed_glass", side="rear", level=1))
        meshes.append(plane(f"rear_upper_slot_{i}_backing", [[b - .24, REAR_Y - .82, 6.42], [a + .24, REAR_Y - .82, 6.42],
                                                               [a + .24, REAR_Y - .82, 11.12], [b - .24, REAR_Y - .82, 11.12]],
                            "sticker_upper_backing", "interior_backing", carrier_kind="opaque_interior_backing", side="rear", level=1))
        cursor = b
    meshes.append(box("rear_upper_pier_terminal", (cursor, 23.66, REAR_Y - .34, REAR_Y, 5.04, 12.42),
                      "sticker_return_concrete", "boardformed_concrete", carrier_kind="constrained_rear_wall", side="rear"))
    # Rear sill/head fabric closes every true opening vertically.
    for i, (a, b) in enumerate(rear_openings):
        meshes.append(box(f"rear_upper_slot_{i}_sill_wall", (a, b, REAR_Y - .34, REAR_Y, 5.04, 6.18),
                          "sticker_return_concrete", "boardformed_concrete", carrier_kind="aperture_sill_wall", side="rear"))
        meshes.append(box(f"rear_upper_slot_{i}_head_wall", (a, b, REAR_Y - .34, REAR_Y, 11.34, 12.42),
                          "sticker_return_concrete", "boardformed_concrete", carrier_kind="aperture_head_wall", side="rear"))
    # Left wall uses the same bounded slot grammar.
    cursor = FRONT_Y + .34
    for i, (a, b) in enumerate(left_openings):
        if a > cursor:
            meshes.append(box(f"left_upper_pier_{i}", (-24, -23.66, cursor, a, 5.04, 12.42),
                              "sticker_return_concrete", "boardformed_concrete", carrier_kind="constrained_return_wall", side="left"))
        meshes.append(box(f"left_upper_slot_{i}_front", (-24, -23.45, a, a + .30, 6.18, 11.34),
                          "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="rear_slot_reveal", side="left"))
        meshes.append(box(f"left_upper_slot_{i}_rear", (-24, -23.45, b - .30, b, 6.18, 11.34),
                          "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="rear_slot_reveal", side="left"))
        meshes.append(box(f"left_upper_slot_{i}_head", (-24, -23.45, a + .30, b - .30, 11.06, 11.34),
                          "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="rear_slot_reveal", side="left"))
        meshes.append(box(f"left_upper_slot_{i}_sill", (-24, -23.45, a + .30, b - .30, 6.18, 6.48),
                          "sticker_deep_reveal", "deep_concrete_reveal", carrier_kind="rear_slot_reveal", side="left"))
        meshes.append(plane(f"left_upper_slot_{i}_glass", [[-23.42, b - .30, 6.48], [-23.42, a + .30, 6.48],
                                                             [-23.42, a + .30, 11.06], [-23.42, b - .30, 11.06]],
                            "sticker_upper_glass", "physical_glass", carrier_kind="recessed_glass", side="left", level=1))
        meshes.append(plane(f"left_upper_slot_{i}_backing", [[-23.18, b - .24, 6.42], [-23.18, a + .24, 6.42],
                                                               [-23.18, a + .24, 11.12], [-23.18, b - .24, 11.12]],
                            "sticker_upper_backing", "interior_backing", carrier_kind="opaque_interior_backing", side="left", level=1))
        cursor = b
    meshes.append(box("left_upper_pier_terminal", (-24, -23.66, cursor, REAR_Y - .34, 5.04, 12.42),
                      "sticker_return_concrete", "boardformed_concrete", carrier_kind="constrained_return_wall", side="left"))
    for i, (a, b) in enumerate(left_openings):
        meshes.append(box(f"left_upper_slot_{i}_sill_wall", (-24, -23.66, a, b, 5.04, 6.18),
                          "sticker_return_concrete", "boardformed_concrete", carrier_kind="aperture_sill_wall", side="left"))
        meshes.append(box(f"left_upper_slot_{i}_head_wall", (-24, -23.66, a, b, 11.34, 12.42),
                          "sticker_return_concrete", "boardformed_concrete", carrier_kind="aperture_head_wall", side="left"))
    # Ground return glazing and primary structural piers keep the cantilever legible around the corner.
    for side, x0, x1 in (("right", 23.55, 23.68), ("left", -23.68, -23.55)):
        vertices = [[x0 if side == "right" else x1, FRONT_Y + .8, .45],
                    [x0 if side == "right" else x1, REAR_Y - .8, .45],
                    [x0 if side == "right" else x1, REAR_Y - .8, 4.58],
                    [x0 if side == "right" else x1, FRONT_Y + .8, 4.58]]
        if side == "left":
            vertices = list(reversed(vertices))
        meshes.append(plane(f"ground_{side}_glass", vertices, "sticker_ground_glass", "physical_glass",
                            carrier_kind="continuous_ground_glass", side=side, level=0))
        backing_x = 23.28 if side == "right" else -23.28
        backing_vertices = [[backing_x, FRONT_Y + .72, .40], [backing_x, REAR_Y - .72, .40],
                            [backing_x, REAR_Y - .72, 4.62], [backing_x, FRONT_Y + .72, 4.62]]
        if side == "left":
            backing_vertices = list(reversed(backing_vertices))
        meshes.append(plane(f"ground_{side}_backing", backing_vertices, "sticker_ground_backing", "interior_backing",
                            carrier_kind="opaque_interior_backing", side=side, level=0))
    for side, x in (("right", 23.7), ("left", -23.7)):
        for i, y in enumerate((-15, -7.5, 0, 7.5, 15)):
            meshes.append(box(f"{side}_piloti_{i}", (x - .36, x + .36, y - .38, y + .38, .20, 5.04),
                              "sticker_board_concrete", "boardformed_concrete", carrier_kind="return_piloti", side=side))

    # Outer roof is segmented around two genuine recessed roof courts.
    wells = [(-12.5, -1.5, -8.5, 1.5), (1.5, 14.0, 3.0, 12.0)]
    xs = sorted({-23.66, 23.66, *[v for w in wells for v in (w[0], w[1])]})
    ys = sorted({FRONT_Y + .34, REAR_Y - .34, *[v for w in wells for v in (w[2], w[3])]})
    roof_fields: list[str] = []
    for ix, (x0, x1) in enumerate(zip(xs, xs[1:])):
        for iy, (y0, y1) in enumerate(zip(ys, ys[1:])):
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if any(a < cx < b and c < cy < d for a, b, c, d in wells):
                continue
            name = f"main_roof_membrane_{ix}_{iy}"
            roof_fields.append(name)
            meshes.append(plane(name, [[x0, y0, 12.60], [x1, y0, 12.60], [x1, y1, 12.60], [x0, y1, 12.60]],
                                "sticker_roof_membrane", "roof_membrane", carrier_kind="upward_roof_field", axis="plan"))
    roof_courts: list[str] = []
    for i, (x0, x1, y0, y1) in enumerate(wells):
        meshes.append(plane(f"roof_court_{i}_floor", [[x0 + .28, y0 + .28, 10.35], [x1 - .28, y0 + .28, 10.35],
                                                       [x1 - .28, y1 - .28, 10.35], [x0 + .28, y1 - .28, 10.35]],
                            "sticker_roof_court", "roof_court_membrane", carrier_kind="sunken_roof_court_floor", axis="plan"))
        for side, bounds in (
            ("front", (x0, x1, y0, y0 + .28, 10.15, 12.92)),
            ("rear", (x0, x1, y1 - .28, y1, 10.15, 12.92)),
            ("left", (x0, x0 + .28, y0 + .28, y1 - .28, 10.15, 12.92)),
            ("right", (x1 - .28, x1, y0 + .28, y1 - .28, 10.15, 12.92)),
        ):
            name = f"roof_court_{i}_{side}_wall"
            roof_courts.append(name)
            meshes.append(box(name, bounds, "sticker_board_concrete", "boardformed_concrete",
                              carrier_kind="roof_court_wall", side=side, court=i))

    # Continuous outer parapet with closed, separately owned coping.
    parapets: list[str] = []
    for side, bounds in (
        ("front", (-23.66, 23.66, FRONT_Y, FRONT_Y + .28, 12.42, 13.18)),
        ("rear", (-23.66, 23.66, REAR_Y - .28, REAR_Y, 12.42, 13.18)),
        ("left", (-24, -23.72, FRONT_Y + .28, REAR_Y - .28, 12.42, 13.18)),
        ("right", (23.72, 24, FRONT_Y + .28, REAR_Y - .28, 12.42, 13.18)),
    ):
        name = f"outer_parapet_{side}"
        parapets.append(name)
        meshes.append(box(name, bounds, "sticker_board_concrete", "boardformed_concrete",
                          carrier_kind="outer_parapet", side=side, shortened_for_corners=True))
        x0, x1, y0, y1, _, _ = bounds
        meshes.append(box(name + "_coping", (x0, x1, y0, y1, 13.18, 13.30), "sticker_coping", "pale_coping",
                          carrier_kind="parapet_coping", side=side, adjacent_finish_terminal=True))
    for sx, x0, x1 in (("left", -24.0, -23.66), ("right", 23.66, 24.0)):
        for sy, y0, y1 in (("front", FRONT_Y, FRONT_Y + .28), ("rear", REAR_Y - .28, REAR_Y)):
            meshes.append(box(f"outer_parapet_{sx}_{sy}_corner_cap", (x0, x1, y0, y1, 12.42, 13.18),
                              "sticker_board_concrete", "boardformed_concrete", carrier_kind="outer_parapet_corner_cap",
                              adjacent_finish_terminal=True, terminal_source_map="boardformed_concrete"))
            meshes.append(box(f"outer_parapet_{sx}_{sy}_coping_cap", (x0, x1, y0, y1, 13.18, 13.30),
                              "sticker_coping", "pale_coping", carrier_kind="parapet_coping_corner_cap",
                              adjacent_finish_terminal=True, terminal_source_map="pale_coping"))

    # Image-defining stepped roof penthouses and sparse service details.
    penthouses: list[str] = []
    for i, bounds in enumerate(((-.5, 8.5, -7.5, -2.5, 12.60, 15.20),
                                (15.5, 21.5, 7.5, 16.5, 12.60, 16.35),
                                (-19.5, -14.0, 9.0, 17.0, 12.60, 14.85))):
        name = f"roof_penthouse_{i}"
        penthouses.append(name)
        meshes.append(box(name, bounds, "sticker_board_concrete", "boardformed_concrete",
                          carrier_kind="stepped_roof_penthouse", penthouse=i, fixed=True))
        x0, x1, y0, y1, _, z1 = bounds
        meshes.append(box(name + "_cap", (x0 - .08, x1 + .08, y0 - .08, y1 + .08, z1, z1 + .16),
                          "sticker_coping", "pale_coping", carrier_kind="penthouse_coping", penthouse=i))
        meshes.append(plane(name + "_service_slot", [[x0 + 1.0, y0 - .012, z1 - 1.35], [x1 - 1.0, y0 - .012, z1 - 1.35],
                                                        [x1 - 1.0, y0 - .012, z1 - .55], [x0 + 1.0, y0 - .012, z1 - .55]],
                            "sticker_service_metal", "service_metal", carrier_kind="penthouse_service_slot", penthouse=i))
    for i, (x, y) in enumerate(((-20, 5), (18, -5), (9, 17), (-2, 15))):
        meshes.append(box(f"roof_vent_{i}", (x - .14, x + .14, y - .14, y + .14, 12.60, 13.18),
                          "sticker_service_metal", "service_metal", carrier_kind="sparse_roof_vent", fixed=True))

    geometry: dict[str, Any] = {
        "archetype_id": ARCHETYPE_ID,
        "variant_id": VARIANT_ID,
        "size": size,
        "reference_evidence": REFERENCE_PATHS,
        "dimensions": {"width_m": WIDTH_M, "depth_m": DEPTH_M, "occupied_storeys": 2,
                       "main_coping_m": 13.30, "highest_penthouse_m": 16.51},
        "identity_lock": {
            "fixed_landmark": True,
            "recessed_glazed_ground": True,
            "massive_cantilevered_upper_shell": True,
            "front_monumental_lightboxes": 2,
            "right_monumental_lightboxes": 3,
            "sculptural_front_pilotis": 4,
            "open_roof_courts": 2,
            "stepped_roof_penthouses": 3,
        },
        "apertures": apertures,
        "roof_fields": roof_fields,
        "roof_court_walls": roof_courts,
        "parapets": parapets,
        "penthouses": penthouses,
        "meshes": meshes,
        "hard_stops": [
            "exactly_two_occupied_levels",
            "true_recessed_glazed_ground_beneath_cantilever",
            "physical_flared_pilotis",
            "five_deep_projecting_splayed_lightboxes",
            "two_true_open_roof_courts",
            "three_stepped_concrete_roof_penthouses",
            "no_balcony_or_pitched_roof_drift",
            "zero_unowned_or_multiply_owned_visible_faces",
        ],
    }
    geometry["geometry_sha256"] = _digest({k: v for k, v in geometry.items() if k != "geometry_sha256"})
    return geometry


if __name__ == "__main__":
    result = build_geometry()
    print(result["size"], len(result["meshes"]), result["geometry_sha256"])
