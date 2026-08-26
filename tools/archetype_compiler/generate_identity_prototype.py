"""Prototype: build a family from its catalogue identity, not only its dimensions.

    python tools/archetype_compiler/generate_identity_prototype.py \
        --source frontend/public/families/deco-theater-mainstreet/archetype-source.json \
        --output /tmp/out

Runs under the ``bpy`` wheel or inside Blender. The point of the prototype is
the comparison: the same catalogue entry that produces a dimensionally correct
box through ``compiler.py`` produces an archetype-shaped building once the
identity words are resolved to parametric signature assemblies.

Ordinary bays absorb width; the signature assemblies keep authored proportions.
Nothing here is a baked mesh, so the same declaration serves any footprint in
the archetype's declared band.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

import bpy  # noqa: E402

import blender_generate as bg  # noqa: E402
from identity_kit import (  # noqa: E402
    BayGraph,
    FacadeReservations,
    build_signature,
    derive_signatures,
)


def _srgb(hex_value: str) -> tuple[float, float, float, float]:
    return bg.hex_rgba(hex_value, 1.0)


def _material(name: str, hex_value: str, roughness: float, metallic: float = 0.0,
              emission: str | None = None, emission_strength: float = 0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = _srgb(hex_value)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = _srgb(emission)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def build_materials(payload: dict) -> dict:
    variant = payload.get("selectedVariant") or {}
    palette = variant.get("palette") or payload.get("palette") or {}
    primary = palette.get("primary") or "#883907"
    return {
        # Terra cotta is a glazed ceramic: mid roughness, no metal.
        "primary": _material("MAT_Primary_TerraCotta", primary, 0.52),
        "secondary": _material("MAT_Secondary_CastStone", "#cbbda4", 0.68),
        "ornament": _material("MAT_Ornament_Gold", "#b08a3c", 0.34, metallic=0.75),
        "signage": _material("MAT_Signage", "#2b1410", 0.45),
        # Lamps and neon are the only emissive surfaces; glazing stays passive.
        "lamp": _material("MAT_Lamp", "#ffe6b0", 0.30, emission="#ffdda0", emission_strength=6.0),
        "glass": _material("MAT_Glass", "#2a2f33", 0.09),
        "shadow": _material("MAT_Reveal", "#150d0a", 0.85),
        "interior": _material("MAT_Occupied", "#6b4a2a", 0.72),
    }


def build_shell(graph: BayGraph, mats: dict) -> list[bpy.types.Object]:
    """Wall envelope with storey datums and a recessed entrance podium."""
    objects: list[bpy.types.Object] = []
    height = graph.storey_z(graph.floors)

    objects.append(
        bg.add_beveled_box(
            "Shell_Core",
            (graph.width, graph.depth, height),
            (0.0, 0.0, height / 2),
            mats["primary"],
            bevel_m=0.05,
        )
    )
    # Side and rear walls take the cheaper cast-stone material the catalogue
    # names, so the terra cotta front reads as the designed elevation.
    for sign in (-1.0, 1.0):
        objects.append(
            bg.add_box(
                f"Shell_SideSkin_{'L' if sign < 0 else 'R'}",
                (0.12, graph.depth - 0.4, height - 0.3),
                (sign * (graph.width / 2 + 0.04), 0.0, height / 2),
                mats["secondary"],
            )
        )
    # Storey datums: shallow courses that catch light and stop the wall reading
    # as one flat slab.
    for storey in range(1, graph.floors):
        z = graph.storey_z(storey)
        objects.append(
            bg.add_box(
                f"Shell_Datum_{storey}",
                (graph.width + 0.16, 0.14, 0.18),
                (0.0, -graph.depth / 2 - 0.07, z),
                mats["ornament"],
            )
        )
    return objects


def build_windows(graph: BayGraph, mats: dict) -> list[bpy.types.Object]:
    """Recessed openings on ordinary bays only.

    Entrance bays are reserved for the fixed identity, which is what stops a
    marquee or arch from landing across a window.
    """
    objects: list[bpy.types.Object] = []
    front_y = -graph.depth / 2
    for storey in range(graph.floors):
        for bay in graph.bays:
            if bay.role == "entrance" and storey == 0:
                continue  # ticket lobby glazing, built with the entrance
            w = bay.width * 0.46
            h = graph.floor_height * (0.30 if storey == 0 else 0.44)
            z = graph.storey_z(storey) + graph.floor_height * (0.55 if storey == 0 else 0.52)
            objects.append(
                bg.add_box(f"Win_Reveal_{storey}_{bay.index}", (w + 0.2, 0.42, h + 0.2),
                           (bay.centre_x, front_y + 0.19, z), mats["shadow"]))
            objects.append(
                bg.add_box(f"Win_Occupied_{storey}_{bay.index}", (w, 0.1, h),
                           (bay.centre_x, front_y + 0.34, z), mats["interior"]))
            objects.append(
                bg.add_box(f"Win_Glass_{storey}_{bay.index}", (w, 0.06, h),
                           (bay.centre_x, front_y + 0.06, z), mats["glass"]))
            # Surround: jambs, head and cill give the opening real depth.
            for sx in (-1.0, 1.0):
                objects.append(
                    bg.add_box(f"Win_Jamb_{storey}_{bay.index}_{sx:+.0f}", (0.11, 0.3, h + 0.28),
                               (bay.centre_x + sx * (w / 2 + 0.05), front_y - 0.02, z), mats["ornament"]))
            objects.append(
                bg.add_box(f"Win_Head_{storey}_{bay.index}", (w + 0.3, 0.32, 0.14),
                           (bay.centre_x, front_y - 0.03, z + h / 2 + 0.12), mats["ornament"]))
            objects.append(
                bg.add_box(f"Win_Cill_{storey}_{bay.index}", (w + 0.34, 0.36, 0.11),
                           (bay.centre_x, front_y - 0.05, z - h / 2 - 0.1), mats["ornament"]))
    return objects


def build_entrance(graph: BayGraph, mats: dict) -> list[bpy.types.Object]:
    """Recessed ticket lobby: a sectional void, not a bright card."""
    span = graph.span("entrance")
    if span is None:
        return []
    x0, x1 = span
    centre_x, width = (x0 + x1) / 2, x1 - x0
    front_y = -graph.depth / 2
    h = graph.floor_height * 0.72
    objects = [
        bg.add_box("Ent_Recess", (width, 1.6, h), (centre_x, front_y + 0.8, h / 2), mats["shadow"]),
        bg.add_box("Ent_Backplate", (width - 0.6, 0.12, h - 0.4), (centre_x, front_y + 1.5, h / 2), mats["interior"]),
        bg.add_box("Ent_Soffit", (width, 1.6, 0.12), (centre_x, front_y + 0.8, h), mats["ornament"]),
    ]
    doors = 5
    for i in range(doors):
        x = centre_x - width / 2 + width * (i + 0.5) / doors
        objects.append(bg.add_box(f"Ent_Door_{i}", (width / doors * 0.72, 0.08, h * 0.82),
                                  (x, front_y + 0.1, h * 0.41), mats["glass"]))
        objects.append(bg.add_box(f"Ent_DoorFrame_{i}", (0.09, 0.16, h * 0.86),
                                  (x - width / doors * 0.40, front_y + 0.08, h * 0.43), mats["ornament"]))
    return objects


def main() -> int:
    parser = argparse.ArgumentParser(prog="generate_identity_prototype.py")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=float, default=None)
    parser.add_argument("--depth", type=float, default=None)
    parser.add_argument("--floors", type=int, default=None)
    parser.add_argument("--engine", default="cycles")
    parser.add_argument("--samples", type=int, default=24)
    parser.add_argument("--view-set", default="preview")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)

    payload = json.loads(args.source.read_text(encoding="utf-8"))
    variant = payload.get("selectedVariant") or {}
    dims = payload.get("dimensions") or {}
    width = args.width or float(dims.get("suggestedWidth_m") or 20.0)
    depth = args.depth or float(dims.get("suggestedDepth_m") or 30.0)
    floors = args.floors or int(variant.get("minFloors") or dims.get("minFloors") or 3)
    floor_height = float(variant.get("suggestedFloorHeight") or dims.get("suggestedFloorHeight") or 5.0)

    family = str(variant.get("id") or payload.get("archetypeId") or args.source.parent.name)
    signatures = derive_signatures(payload)

    print(f"[identity] family        : {family}")
    print(f"[identity] footprint     : {width:.1f} x {depth:.1f} m, {floors} floors @ {floor_height:.1f} m")
    print(f"[identity] signatures    : {len(signatures)} derived from catalogue prose")
    for item in signatures:
        print(f"             - {item['type']:<20} evidence {item['evidence']}")
    if not signatures:
        print("[identity] no identity words found; this family would build as a plain box")

    bg.reset_scene()
    bg.configure_units()
    mats = build_materials(payload)
    graph = BayGraph.from_dimensions(width, depth, floor_height, floors)
    print(f"[identity] bay graph     : {len(graph.bays)} bays "
          f"({len(graph.of_role('entrance'))} entrance, {len(graph.of_role('end'))} end)")

    objects: list[bpy.types.Object] = []
    objects += build_shell(graph, mats)
    objects += build_windows(graph, mats)
    objects += build_entrance(graph, mats)

    reservations = FacadeReservations()
    for item in signatures:
        built = build_signature(item["type"], graph, mats, reservations, item["params"])
        objects += built
        print(f"[identity] built {item['type']:<20} {len(built):>4} objects")

    args.output.mkdir(parents=True, exist_ok=True)
    glb = args.output / f"{family}_identity.glb"
    bg.export_objects(glb, objects)
    tris = sum(len(o.data.loop_triangles) if o.type == "MESH" else 0 for o in objects)
    print(f"[identity] exported {glb.name} ({len(objects)} objects)")

    manifest = {
        "family": family,
        "generator": "identity_prototype@1",
        "footprint": {"width_m": width, "depth_m": depth, "floors": floors, "floor_height_m": floor_height},
        "bays": {"count": len(graph.bays), "entrance": len(graph.of_role("entrance"))},
        "signature_assemblies": signatures,
        "object_count": len(objects),
    }
    (args.output / f"{family}_identity_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    bg.render_presentation_views(
        args.output, family, graph.storey_z(floors), width, depth,
        preferred_engine=args.engine, samples=args.samples, view_set=args.view_set,
    )
    print(f"[identity] done -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
