"""Locked clay geometry for the exact Privateer's Wharf image set.

Despite the catalogue's inherited stone/gable prose, the three exact images
show a two-storey red-brick Italianate corner commercial hall with pale stone
trim and a flat roof.  This module therefore treats the images as massing
authority.  Only complete 2.5 m ordinary front stacks can be inserted; the
two tall storeys, depth, corner piers, entrance, cornice and roof remain fixed.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


ARCHETYPE_ID = "halifax_waterfront_warehouse"
VARIANT_ID = "warehouse_privateers_wharf"
DEPTH_M = 15.0
ORDINARY_FRONT_BAY_M = 2.5
FIXED_ENTRANCE_BAY_M = 5.0
SIDE_BAY_M = 3.0
WALL_TOP_M = 9.70
ROOF_DECK_M = 10.92
PARAPET_TOP_M = 11.82
SIZE_MATRIX = {
    "canonical": {"width_m": 20.0, "depth_m": 15.0, "ordinary_front_bays": 6, "side_bays": 5, "storeys": 2},
    "extended": {"width_m": 25.0, "depth_m": 15.0, "ordinary_front_bays": 8, "side_bays": 5, "storeys": 2},
}
REFERENCE_EVIDENCE = (
    "frontend/public/archetypes/buildings/halifax-waterfront-warehouse/variant_0.png",
    "frontend/public/archetypes/buildings/halifax-waterfront-warehouse/variant_0_angle_60.jpg",
    "frontend/public/archetypes/buildings/halifax-waterfront-warehouse/variant_0_angle_90.jpg",
)


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _mesh(name: str, vertices: list[list[float]], faces: list[list[int]], owner: str,
          domain: str, *, face_roles: list[str] | None = None, **metadata: Any) -> dict[str, Any]:
    roles = face_roles or [domain] * len(faces)
    if len(roles) != len(faces):
        raise ValueError(f"{name}: role/face mismatch")
    return {"name": name, "vertices": vertices, "faces": faces,
            "face_owners": [[owner] for _ in faces], "sticker_owner_id": owner,
            "material_domain": domain, "face_roles": roles, **metadata}


def _box(name: str, bounds: tuple[float, float, float, float, float, float],
         owner: str, domain: str, **metadata: Any) -> dict[str, Any]:
    x0, x1, y0, y1, z0, z1 = bounds
    vertices = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
             [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return _mesh(name, vertices, faces, owner, domain, **metadata)


def _point(side: str, u: float, inset: float, z: float, width: float, depth: float) -> list[float]:
    if side == "front": return [u, -depth / 2 + inset, z]
    if side == "rear": return [-u, depth / 2 - inset, z]
    if side == "left": return [-width / 2 + inset, -u, z]
    if side == "right": return [width / 2 - inset, u, z]
    raise KeyError(side)


def _oriented_box(name: str, orientation: str, u0: float, u1: float, z0: float, z1: float,
                  inset0: float, inset1: float, width: float, depth: float,
                  owner: str, domain: str, **metadata: Any) -> dict[str, Any]:
    vertices = [_point(orientation, u0, inset0, z0, width, depth), _point(orientation, u1, inset0, z0, width, depth),
                _point(orientation, u1, inset1, z0, width, depth), _point(orientation, u0, inset1, z0, width, depth),
                _point(orientation, u0, inset0, z1, width, depth), _point(orientation, u1, inset0, z1, width, depth),
                _point(orientation, u1, inset1, z1, width, depth), _point(orientation, u0, inset1, z1, width, depth)]
    return _mesh(name, vertices, [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]], owner, domain, **metadata)


def _arched_contour(centre: float, half: float, sill: float, spring: float,
                    segments: int = 12) -> list[tuple[float, float]]:
    pts = [(centre - half, sill), (centre + half, sill), (centre + half, spring)]
    for i in range(1, segments + 1):
        theta = i * math.pi / segments
        pts.append((centre + half * math.cos(theta), spring + half * math.sin(theta)))
    return pts


def _arched_carrier(orientation: str, name: str, contour: list[tuple[float, float]],
                    centre: float, spring: float, inset: float, width: float, depth: float,
                    owner: str, domain: str, **metadata: Any) -> dict[str, Any]:
    """Return an explicitly clipped arch carrier, never a bounding rectangle.

    A lower quadrilateral owns only the jamb-to-spring zone.  A fan of twelve
    triangles owns the semicircular head.  Keeping these faces explicit avoids
    downstream sticker consumers interpreting one large n-gon through its
    rectangular bounds and producing dark bands above/between arch crowns.
    """
    centre_index = len(contour)
    vertices = [_point(orientation, u, inset, z, width, depth) for u, z in contour]
    vertices.append(_point(orientation, centre, inset, spring, width, depth))
    faces = [[0, 1, 2, len(contour) - 1]]
    faces.extend([[centre_index, i, i + 1] for i in range(2, len(contour) - 1)])
    return _mesh(name, vertices, faces, owner, domain,
                 face_roles=[domain] * len(faces), clipped_to_arch_contour=True,
                 carrier_shape="split_rectangle_plus_semicircular_fan", **metadata)


def _closed_oriented_quad_prism(name: str, orientation: str,
                                contour_uz: list[tuple[float, float]],
                                inset0: float, inset1: float, width: float, depth: float,
                                owner: str, domain: str, **metadata: Any) -> dict[str, Any]:
    """Extrude one non-self-intersecting facade quad into a closed solid.

    The two caps use opposite winding and every boundary edge is shared by two
    faces.  This is robust in Cycles and does not rely on material backface or
    EEVEE's more forgiving single-sided rasterization.
    """
    front = [_point(orientation, u, inset0, z, width, depth) for u, z in contour_uz]
    back = [_point(orientation, u, inset1, z, width, depth) for u, z in contour_uz]
    vertices = front + back
    faces = [[0, 3, 2, 1], [4, 5, 6, 7],
             [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return _mesh(name, vertices, faces, owner, domain,
                 watertight=True, consistent_outward_winding=True,
                 non_overlapping_tile=True, **metadata)


def _arched_aperture(side: str, bay: int, centre: float, module0: float, module1: float,
                     width: float, depth: float, *, half: float = 0.84,
                     sill: float = 5.48, spring: float = 8.15,
                     evidence: str = "exact") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    prefix = f"{side}_upper_arch_{bay:02d}"
    contour = _arched_contour(centre, half, sill, spring)
    crown = spring + half
    meshes = [
        _oriented_box(f"{prefix}_brick_left", side, module0, centre-half, 5.0, WALL_TOP_M, 0, .42, width, depth,
                      f"sticker_{prefix}_brick", "red_brick", side=side, bay=bay, level=1, carrier_kind="extruded_wall_bay"),
        _oriented_box(f"{prefix}_brick_right", side, centre+half, module1, 5.0, WALL_TOP_M, 0, .42, width, depth,
                      f"sticker_{prefix}_brick", "red_brick", side=side, bay=bay, level=1, carrier_kind="extruded_wall_bay"),
        _oriented_box(f"{prefix}_brick_apron", side, centre-half, centre+half, 5.0, sill, 0, .42, width, depth,
                      f"sticker_{prefix}_brick", "red_brick", side=side, bay=bay, level=1, carrier_kind="extruded_wall_bay"),
    ]
    # One tiled central closure owns the complete region from the true arch
    # contour to the wall top.  The former full-module brick-head cuboid
    # overlapped the already full-height left/right brick piers; Cycles exposed
    # that double shell as one black rectangle per bay.  These twelve closed
    # tiles share boundaries only and never overlap the side piers.
    arc = contour[2:]
    for i, (a, b) in enumerate(zip(arc, arc[1:])):
        tile = [(a[0], a[1]), (b[0], b[1]), (b[0], WALL_TOP_M), (a[0], WALL_TOP_M)]
        meshes.append(_closed_oriented_quad_prism(
            f"{prefix}_above_arch_brick_closure_{i:02d}", side, tile, 0.0, .42, width, depth,
            f"sticker_{prefix}_brick", "red_brick", side=side, bay=bay, level=1,
            carrier_kind="closed_above_arch_brick_closure",
            arc_interval_u_m=[min(a[0], b[0]), max(a[0], b[0])],
            lower_chord_uz_m=[list(a), list(b)], wall_top_z_m=WALL_TOP_M,
            exterior_face_index=0, replaces_overlapping_brick_head=True))
    glass_inset = .76
    returns, ring = [], []
    for i, (a, b) in enumerate(zip(contour, contour[1:] + contour[:1])):
        name = f"{prefix}_return_{i:02d}"; returns.append(name)
        meshes.append(_mesh(name, [_point(side,a[0],0,a[1],width,depth), _point(side,b[0],0,b[1],width,depth),
                                  _point(side,b[0],glass_inset,b[1],width,depth), _point(side,a[0],glass_inset,a[1],width,depth)],
                            [[0,1,2,3]], f"sticker_{prefix}_stone_returns", "pale_stone_return",
                            side=side, bay=bay, level=1, carrier_kind="opening_return_tunnel"))
    outer = _arched_contour(centre, half+.15, sill-.15, spring, 12)
    for i, (inner_a, inner_b, outer_a, outer_b) in enumerate(zip(contour, contour[1:]+contour[:1], outer, outer[1:]+outer[:1])):
        name = f"{prefix}_stone_arch_ring_{i:02d}"; ring.append(name)
        meshes.append(_mesh(name, [_point(side,outer_a[0],-.06,outer_a[1],width,depth), _point(side,outer_b[0],-.06,outer_b[1],width,depth),
                                  _point(side,inner_b[0],-.06,inner_b[1],width,depth), _point(side,inner_a[0],-.06,inner_a[1],width,depth)],
                            [[0,1,2,3]], f"sticker_{prefix}_stone_arch", "pale_stone_trim",
                            side=side, bay=bay, level=1, carrier_kind="physical_round_arch_surround"))
    # A second shallow archivolt reads as a constructed stepped molding rather
    # than a single flat border.  Impost blocks and a small keystone supply the
    # characteristic restrained Italianate termination visible in the refs.
    outer2 = _arched_contour(centre, half+.25, sill-.25, spring, 12)
    archivolt2=[]
    for i,(inner_a,inner_b,outer_a,outer_b) in enumerate(zip(outer,outer[1:]+outer[:1],outer2,outer2[1:]+outer2[:1])):
        name=f"{prefix}_outer_archivolt_{i:02d}";archivolt2.append(name)
        meshes.append(_mesh(name,[_point(side,outer_a[0],-.10,outer_a[1],width,depth),_point(side,outer_b[0],-.10,outer_b[1],width,depth),
                                  _point(side,inner_b[0],-.10,inner_b[1],width,depth),_point(side,inner_a[0],-.10,inner_a[1],width,depth)],[[0,1,2,3]],
                            f"sticker_{prefix}_outer_archivolt","pale_stone_trim",side=side,bay=bay,level=1,
                            carrier_kind="physical_outer_archivolt"))
    impost=[]
    for label,u in (("left",centre-half),("right",centre+half)):
        name=f"{prefix}_{label}_impost_block";impost.append(name)
        meshes.append(_oriented_box(name,side,u-.18,u+.18,spring-.17,spring+.12,-.13,.02,width,depth,
                                    f"sticker_{prefix}_imposts","pale_stone_trim",side=side,bay=bay,level=1,
                                    carrier_kind="physical_arch_impost"))
    keystone=f"{prefix}_keystone_crest"
    meshes.append(_oriented_box(keystone,side,centre-.13,centre+.13,crown-.10,crown+.31,-.16,.01,width,depth,
                                f"sticker_{prefix}_keystone","pale_stone_trim",side=side,bay=bay,level=1,
                                carrier_kind="physical_arch_keystone"))
    glass_name = f"{prefix}_recessed_glass"
    meshes.append(_arched_carrier(side, glass_name, contour, centre, spring, glass_inset, width, depth,
                                  f"sticker_{prefix}_glass", "recessed_glazing",
                                  side=side, bay=bay, level=1, carrier_kind="recessed_glass"))
    card_name = f"{prefix}_interior_card"
    meshes.append(_arched_carrier(side, card_name, contour, centre, spring, glass_inset+.32, width, depth,
                                  f"sticker_{prefix}_interior", "interior_card",
                                  side=side, bay=bay, level=1, occupied=True,
                                  behind_glass_m=.32, carrier_kind="recessed_interior_card"))
    mullions=[]
    for idx, u in enumerate((centre-.28, centre+.28)):
        n=f"{prefix}_mullion_{idx}"; mullions.append(n)
        meshes.append(_oriented_box(n,side,u-.025,u+.025,sill+.05,spring+.55,glass_inset-.04,glass_inset-.01,width,depth,
                                    f"sticker_{prefix}_mullions","dark_metal_frame",side=side,bay=bay,level=1,carrier_kind="physical_mullion"))
    n=f"{prefix}_transom"; mullions.append(n)
    meshes.append(_oriented_box(n,side,centre-half+.04,centre+half-.04,7.15,7.21,glass_inset-.04,glass_inset-.01,width,depth,
                                f"sticker_{prefix}_mullions","dark_metal_frame",side=side,bay=bay,level=1,carrier_kind="physical_mullion"))
    return meshes, {"aperture_id":prefix,"side":side,"bay":bay,"level":1,"kind":"window","shape":"true_round_arch",
                    "contour_uz_m":[list(p) for p in contour],"recess_depth_m":glass_inset,"return_meshes":returns,
                    "arch_surround_meshes":ring,"outer_archivolt_meshes":archivolt2,"impost_meshes":impost,
                    "keystone_mesh":keystone,"recessed_glass_mesh":glass_name,"interior_card_mesh":card_name,
                    "mullion_meshes":mullions,"completion_evidence":evidence,"flat_printed_void":False}


def _ground_opening(side: str, bay: int, centre: float, module0: float, module1: float,
                    width: float, depth: float, *, entrance: bool = False,
                    evidence: str = "exact") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    prefix=f"{side}_ground_{'entrance' if entrance else 'storefront'}_{bay:02d}"
    half=min(1.55 if entrance else .90,(module1-module0)*.38); u0,u1=centre-half,centre+half
    z0,z1=.20,4.05; inset=.92 if entrance else .68
    meshes=[
        _oriented_box(f"{prefix}_left_pier",side,module0,u0,0,4.40,0,.46,width,depth,f"sticker_{prefix}_stone","pale_stone_rustication",side=side,bay=bay,level=0,carrier_kind="rusticated_ground_pier"),
        _oriented_box(f"{prefix}_right_pier",side,u1,module1,0,4.40,0,.46,width,depth,f"sticker_{prefix}_stone","pale_stone_rustication",side=side,bay=bay,level=0,carrier_kind="rusticated_ground_pier"),
        _oriented_box(f"{prefix}_apron",side,u0,u1,0,z0,0,.46,width,depth,f"sticker_{prefix}_stone","pale_stone_rustication",side=side,bay=bay,level=0,carrier_kind="opening_apron"),
        _oriented_box(f"{prefix}_lintel",side,u0,u1,z1,4.40,0,.46,width,depth,f"sticker_{prefix}_stone","pale_stone_trim",side=side,bay=bay,level=0,carrier_kind="opening_lintel"),
    ]
    contour=[(u0,z0),(u1,z0),(u1,z1),(u0,z1)]; returns=[]
    for i,(a,b) in enumerate(zip(contour,contour[1:]+contour[:1])):
        n=f"{prefix}_return_{i}"; returns.append(n)
        meshes.append(_mesh(n,[_point(side,a[0],0,a[1],width,depth),_point(side,b[0],0,b[1],width,depth),
                              _point(side,b[0],inset,b[1],width,depth),_point(side,a[0],inset,a[1],width,depth)],[[0,1,2,3]],
                            f"sticker_{prefix}_returns","pale_stone_return",side=side,bay=bay,level=0,carrier_kind="opening_return_tunnel"))
    glass=f"{prefix}_recessed_glass"; card=f"{prefix}_interior_card"
    meshes.append(_mesh(glass,[_point(side,u,inset,z,width,depth) for u,z in contour],[list(range(4))],f"sticker_{prefix}_glass","recessed_glazing",side=side,bay=bay,level=0,carrier_kind="recessed_glass"))
    meshes.append(_mesh(card,[_point(side,u,inset+.35,z,width,depth) for u,z in contour],[list(range(4))],f"sticker_{prefix}_interior","interior_card",face_roles=["interior_card"],side=side,bay=bay,level=0,occupied=True,behind_glass_m=.35,carrier_kind="recessed_interior_card"))
    frames=[]
    # Heavy dark-green perimeter framing, a high transom and a low rail/stall
    # riser are mandatory on every commercial opening.
    for label,fu0,fu1,fz0,fz1 in (
        ("left_jamb",u0,u0+.10,z0,z1),("right_jamb",u1-.10,u1,z0,z1),
        ("head",u0,u1,z1-.12,z1),("sill",u0,u1,z0,z0+.14),
        ("high_transom",u0+.08,u1-.08,3.18,3.31),("lower_rail",u0+.08,u1-.08,.88,1.02),
        ("stall_riser",u0+.08,u1-.08,z0+.12,.88),
    ):
        n=f"{prefix}_{label}";frames.append(n)
        meshes.append(_oriented_box(n,side,fu0,fu1,fz0,fz1,inset-.065,inset-.01,width,depth,
                                    f"sticker_{prefix}_dark_green_frames","dark_green_painted_metal",
                                    side=side,bay=bay,level=0,carrier_kind="heavy_storefront_frame"))
    for idx,u in enumerate((centre,) if entrance else (centre-.30,centre+.30)):
        n=f"{prefix}_vertical_frame_{idx}";frames.append(n)
        meshes.append(_oriented_box(n,side,u-.04,u+.04,z0+.03,z1-.03,inset-.06,inset-.01,width,depth,f"sticker_{prefix}_dark_green_frames","dark_green_painted_metal",side=side,bay=bay,level=0,carrier_kind="physical_mullion"))
    door_leaves=[]
    if entrance:
        gap=.035
        for label,du0,du1 in (("left",u0+.14,centre-gap),("right",centre+gap,u1-.14)):
            n=f"{prefix}_{label}_door_leaf";door_leaves.append(n)
            meshes.append(_oriented_box(n,side,du0,du1,z0+.14,3.12,inset-.055,inset-.015,width,depth,
                                        f"sticker_{prefix}_paired_doors","dark_green_painted_metal",
                                        side=side,bay=bay,level=0,carrier_kind="paired_entrance_door_leaf",fixed_identity=True))
    return meshes,{"aperture_id":prefix,"side":side,"bay":bay,"level":0,"kind":"entrance" if entrance else "storefront",
                   "shape":"rectangular","contour_uz_m":[list(p) for p in contour],"recess_depth_m":inset,
                   "return_meshes":returns,"recessed_glass_mesh":glass,"interior_card_mesh":card,"mullion_meshes":frames,
                   "storefront_frame_meshes":frames,"paired_door_leaf_meshes":door_leaves,
                   "completion_evidence":evidence,"fixed_identity":entrance,"flat_printed_void":False}


def _cornice(width: float, depth: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    meshes=[]; layers=[]
    for idx,(out,z0,z1) in enumerate(((.10,9.64,9.86),(.22,9.86,10.14),(.34,10.14,10.42),(.46,10.42,10.72))):
        n=f"cornice_layer_{idx}";layers.append(n)
        meshes.append(_box(n,(-width/2-out,width/2+out,-depth/2-out,depth/2+out,z0,z1),f"sticker_cornice_layer_{idx}","pale_stone_trim",carrier_kind="projecting_cornice_layer",fixed_identity=True))
    modillions=[]
    spacing=1.0
    for side,extent in (("front",width),("rear",width),("left",depth),("right",depth)):
        count=int(extent//spacing)
        for i in range(count):
            u=-extent/2+(i+.5)*extent/count
            n=f"{side}_modillion_{i:02d}";modillions.append(n)
            meshes.append(_oriented_box(n,side,u-.11,u+.11,9.72,9.96,-.38,-.05,width,depth,"sticker_cornice_modillions","pale_stone_trim",side=side,carrier_kind="physical_modillion",fixed_identity=True))
    return meshes,{"layer_meshes":layers,"modillion_meshes":modillions}


def _roof(width: float, depth: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    meshes=[_box("flat_membrane_roof",(-width/2+.25,width/2-.25,-depth/2+.25,depth/2-.25,10.86,10.94),"sticker_flat_membrane_roof","weathered_membrane_roof",carrier_kind="roof_deck",fixed_identity=True)]
    parapets=[]
    for n,b in (("front",(-width/2-.08,width/2+.08,-depth/2-.05,-depth/2+.34,10.72,PARAPET_TOP_M)),
                ("rear",(-width/2-.08,width/2+.08,depth/2-.34,depth/2+.05,10.72,PARAPET_TOP_M)),
                ("left",(-width/2-.05,-width/2+.34,-depth/2,depth/2,10.72,PARAPET_TOP_M)),
                ("right",(width/2-.34,width/2+.05,-depth/2,depth/2,10.72,PARAPET_TOP_M))):
        name=f"{n}_roof_parapet";parapets.append(name)
        meshes.append(_box(name,b,f"sticker_{n}_roof_parapet","red_brick",carrier_kind="roof_parapet",fixed_identity=True))
    copings=[]
    # Straight coping runs terminate at the inside edge of dedicated corner
    # caps.  No two volumes overlap; shared boundaries are exact.
    for n,b in (("front",(-width/2+.42,width/2-.42,-depth/2-.13,-depth/2+.42,PARAPET_TOP_M,PARAPET_TOP_M+.14)),
                ("rear",(-width/2+.42,width/2-.42,depth/2-.42,depth/2+.13,PARAPET_TOP_M,PARAPET_TOP_M+.14)),
                ("left",(-width/2-.13,-width/2+.42,-depth/2+.42,depth/2-.42,PARAPET_TOP_M,PARAPET_TOP_M+.14)),
                ("right",(width/2-.42,width/2+.13,-depth/2+.42,depth/2-.42,PARAPET_TOP_M,PARAPET_TOP_M+.14))):
        name=f"{n}_parapet_coping";copings.append(name);meshes.append(_box(name,b,f"sticker_{n}_parapet_coping","patinated_coping",carrier_kind="parapet_coping",fixed_identity=True))
    coping_corners=[]
    for corner,(x0,x1,y0,y1) in {
        "front_left":(-width/2-.16,-width/2+.42,-depth/2-.13,-depth/2+.42),
        "front_right":(width/2-.42,width/2+.16,-depth/2-.13,-depth/2+.42),
        "rear_left":(-width/2-.16,-width/2+.42,depth/2-.42,depth/2+.13),
        "rear_right":(width/2-.42,width/2+.16,depth/2-.42,depth/2+.13),
    }.items():
        name=f"{corner}_closed_coping_corner_cap";coping_corners.append(name)
        meshes.append(_box(name,(x0,x1,y0,y1,PARAPET_TOP_M,PARAPET_TOP_M+.14),
                           f"sticker_{corner}_patinated_coping_cap","patinated_coping",
                           carrier_kind="closed_coping_corner_cap",fixed_identity=True,
                           coping_corner=corner,watertight=True))
    step="front_stepped_parapet_brick_infill"
    stepped_parts=[step]
    meshes.append(_box(step,(-3.05,3.05,-depth/2-.08,-depth/2+.38,PARAPET_TOP_M,12.33),"sticker_front_stepped_brick_infill","red_brick",carrier_kind="stepped_front_parapet_brick_infill",fixed_identity=True))
    for label,x0,x1 in (("left",-3.52,-3.05),("right",3.05,3.52)):
        n=f"front_stepped_parapet_{label}_stone_upright";stepped_parts.append(n)
        meshes.append(_box(n,(x0,x1,-depth/2-.14,-depth/2+.43,PARAPET_TOP_M,12.55),f"sticker_{n}","pale_stone_trim",carrier_kind="stepped_parapet_stone_upright",fixed_identity=True))
        n=f"front_stepped_parapet_{label}_pilaster_cap";stepped_parts.append(n)
        meshes.append(_box(n,(x0-.10,x1+.10,-depth/2-.20,-depth/2+.49,12.55,12.72),f"sticker_{n}","pale_stone_trim",carrier_kind="stepped_parapet_pilaster_cap",fixed_identity=True))
    for idx,(out,z0,z1,domain) in enumerate(((.05,12.30,12.43,"pale_stone_trim"),(.13,12.43,12.54,"oxidized_metal_coping"))):
        n=f"front_stepped_parapet_layered_coping_{idx}";stepped_parts.append(n)
        meshes.append(_box(n,(-3.05-out,3.05+out,-depth/2-.10-out,-depth/2+.40+out,z0,z1),f"sticker_{n}",domain,carrier_kind="stepped_parapet_layered_coping",fixed_identity=True))
    n="front_stepped_parapet_continued_cornice";stepped_parts.append(n)
    meshes.append(_box(n,(-3.38,3.38,-depth/2-.25,-depth/2+.49,PARAPET_TOP_M-.16,PARAPET_TOP_M+.04),"sticker_front_stepped_continued_cornice","pale_stone_trim",carrier_kind="stepped_parapet_continued_cornice",fixed_identity=True))
    chimney_assemblies=[]
    for idx,x in enumerate((-width*.28,width*.19)):
        shaft=f"rear_brick_chimney_{idx}_shaft";cap=f"rear_brick_chimney_{idx}_independent_cap"
        meshes.append(_box(shaft,(x-.36,x+.36,depth/2-1.22,depth/2-.50,10.92,13.05),f"sticker_{shaft}","red_brick",carrier_kind="roof_chimney_shaft",fixed_identity=True,chimney_assembly=idx))
        meshes.append(_box(cap,(x-.47,x+.47,depth/2-1.33,depth/2-.39,13.05,13.19),f"sticker_{cap}","pale_stone_trim",carrier_kind="independent_chimney_cap",fixed_identity=True,chimney_assembly=idx))
        chimney_assemblies.append({"assembly_id":f"rear_chimney_{idx}","shaft_mesh":shaft,"cap_mesh":cap})
    vents=[]
    for i,(x,y) in enumerate(((-1.8,1.1),(2.5,-.2))):
        n=f"low_roof_vent_{i}";vents.append(n);meshes.append(_box(n,(x-.20,x+.20,y-.20,y+.20,10.94,11.30),"sticker_roof_vents","dark_metal",carrier_kind="roof_vent"))
    return meshes,{"deck_mesh":"flat_membrane_roof","parapet_meshes":parapets,"coping_meshes":copings,
                   "coping_corner_cap_meshes":coping_corners,"stepped_front_mesh":step,"stepped_front_subpart_meshes":stepped_parts,
                   "chimney_assemblies":chimney_assemblies,"chimney_meshes":[p[k] for p in chimney_assemblies for k in ("shaft_mesh","cap_mesh")],"vent_meshes":vents}


def build_geometry(size: str = "canonical") -> dict[str, Any]:
    if size not in SIZE_MATRIX: raise KeyError(size)
    spec=SIZE_MATRIX[size]; width=float(spec["width_m"]); depth=float(spec["depth_m"])
    meshes=[]; apertures=[]
    ordinary=int(spec["ordinary_front_bays"]); entrance0=-FIXED_ENTRANCE_BAY_M/2; entrance1=FIXED_ENTRANCE_BAY_M/2
    left_count=ordinary//2
    front_modules=[]
    for i in range(left_count):
        front_modules.append((-width/2+i*ORDINARY_FRONT_BAY_M,-width/2+(i+1)*ORDINARY_FRONT_BAY_M))
    front_modules.append((entrance0,entrance1))
    for i in range(left_count):
        front_modules.append((entrance1+i*ORDINARY_FRONT_BAY_M,entrance1+(i+1)*ORDINARY_FRONT_BAY_M))
    for bay,(u0,u1) in enumerate(front_modules):
        centre=(u0+u1)/2; entrance=(u0,u1)==(entrance0,entrance1)
        gm,ga=_ground_opening("front",bay,centre,u0,u1,width,depth,entrance=entrance);meshes+=gm;apertures.append(ga)
        am,aa=_arched_aperture("front",bay,centre,u0,u1,width,depth,half=1.48 if entrance else .80);meshes+=am;apertures.append(aa)
    # Exact corner side: five equal arched stacks; constrained rear repeats subordinate rhythm.
    for side in ("right","left","rear"):
        extent=depth if side in {"left","right"} else width
        count=5 if side in {"left","right"} else (ordinary+1)
        module=extent/count
        for bay in range(count):
            u0=-extent/2+bay*module;u1=u0+module;centre=(u0+u1)/2
            ev="exact" if side=="right" else "constrained"
            gm,ga=_ground_opening(side,bay,centre,u0,u1,width,depth,evidence=ev);meshes+=gm;apertures.append(ga)
            am,aa=_arched_aperture(side,bay,centre,u0,u1,width,depth,half=min(.82,module*.31),evidence=ev);meshes+=am;apertures.append(aa)
    # Continuous stone belt, corner quoins and layered cornice establish the exact hierarchy.
    for side in ("front","rear","left","right"):
        extent=width if side in {"front","rear"} else depth
        meshes.append(_oriented_box(f"{side}_stone_belt",side,-extent/2-.08,extent/2+.08,4.38,5.02,-.12,.18,width,depth,f"sticker_{side}_stone_belt","pale_stone_trim",side=side,carrier_kind="projecting_belt_course",fixed_identity=True))
    quoins=[]
    for corner,(x0,x1,y0,y1) in {"front_left":(-width/2-.12,-width/2+.46,-depth/2-.12,-depth/2+.46),"front_right":(width/2-.46,width/2+.12,-depth/2-.12,-depth/2+.46),"rear_left":(-width/2-.12,-width/2+.46,depth/2-.46,depth/2+.12),"rear_right":(width/2-.46,width/2+.12,depth/2-.46,depth/2+.12)}.items():
        for course in range(10):
            z0=course*.97;name=f"{corner}_rusticated_quoin_{course:02d}";quoins.append(name)
            meshes.append(_box(name,(x0,x1,y0,y1,z0,min(z0+.82,WALL_TOP_M)),f"sticker_{corner}_quoins","pale_stone_rustication",carrier_kind="rusticated_corner_quoin",fixed_identity=True))
    cm,cornice=_cornice(width,depth);meshes+=cm
    rm,roof=_roof(width,depth);meshes+=rm
    geometry={"archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,"size":size,"reference_evidence":list(REFERENCE_EVIDENCE),
              "identity_mode":"semantic_stack","dimensions":{"width_m":width,"depth_m":depth,"occupied_storeys":2,"wall_top_m":WALL_TOP_M,"parapet_top_m":PARAPET_TOP_M},
              "floor_bands":[{"level":0,"role":"tall_commercial_ground","z_min_m":0.0,"z_max_m":4.4},{"level":1,"role":"tall_arched_upper_hall","z_min_m":5.0,"z_max_m":9.7}],
              "structural_grid":{"ordinary_front_bays":ordinary,"ordinary_front_bay_m":ORDINARY_FRONT_BAY_M,"fixed_entrance_bays":1,"fixed_entrance_bay_m":FIXED_ENTRANCE_BAY_M,"side_bays":5},
              "fixed_modules":{"corner_quoin_assemblies":4,"entrances":1,"cornices":1,"stepped_front_parapets":1,"chimneys":2},
              "apertures":apertures,"cornice":cornice,"roof":roof,"quoin_meshes":quoins,"meshes":meshes,
              "completion_policy":{"right":"exact_corner_side","left":"constrained_same_building_no_invented_entry","rear":"constrained_fully_covered_no_invented_entry"},
              "geometry_hard_stops":["occupied_storeys_must_equal_2","canonical_footprint_must_equal_20x15","depth_must_equal_15","extended_width_must_equal_25","capacity_changes_require_complete_2_5m_front_bays","entrance_count_must_equal_1","rear_independently_capped_chimney_assemblies_must_equal_2","all_upper_windows_require_true_round_arch_contours_returns_recessed_glass_interior_cards_physical_mullions_outer_archivolts_imposts_and_keystones","all_ground_openings_require_deep_returns_recessed_glass_interior_cards_heavy_green_frames_high_transoms_and_stall_risers","fixed_entrance_requires_paired_double_door_leaves","corner_quoins_must_remain_physical_and_rusticated","cornice_requires_layered_projection_and_physical_modillions","roof_must_remain_flat_membrane_behind_coped_parapet","front_stepped_parapet_requires_brick_infill_stone_uprights_layered_coping_and_continued_cornice","no_gable_roof_or_stone_warehouse_substitution","no_depth_or_vertical_scaling","no_invented_rear_entry","every_visible_face_requires_exactly_one_sticker_owner"]}
    geometry["geometry_sha256"]=_hash({k:v for k,v in geometry.items() if k!="geometry_sha256"})
    return geometry


if __name__ == "__main__":
    for tier in SIZE_MATRIX:
        g=build_geometry(tier);print(tier,len(g["meshes"]),g["geometry_sha256"])
