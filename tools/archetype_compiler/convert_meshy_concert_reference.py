"""Convert a fused Meshy concert-hall GLB into a bounded fixed LEGO assembly.

The image-to-3D source is useful for its crown, apertures and roof, but its
warehouse base must remain a repeatable City Prompt kit. This Blender script
normalizes the source to the authored 90 x 65 x 57.2 m envelope, removes
geometry below the crown interface, decimates the retained surface and
downsamples embedded textures for a practical runtime reference module.

Run with Blender:

  blender --background --factory-startup --python convert_meshy_concert_reference.py -- \
      --source source.glb --output concert-hall-modern-v1-meshy-crown.glb
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


TARGET_SIZE = (90.0, 65.0, 57.2)
CROWN_INTERFACE_Z_M = 17.4
TARGET_TRIANGLES = 120_000
MAX_TEXTURE_PX = 1024
ROOF_CLASSIFICATION_Z_M = 38.0
ROOF_NORMAL_Z = 0.22
TRANSITION_CLASSIFICATION_Z_M = 23.5
GLASS_TEXTURE_REPEATS = 3.4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--interface-z", type=float, default=CROWN_INTERFACE_Z_M)
    parser.add_argument("--target-triangles", type=int, default=TARGET_TRIANGLES)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners))),
        Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners))),
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _principled_input(node: bpy.types.ShaderNodeBsdfPrincipled, *names: str):
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            return socket
    raise KeyError(f"Principled BSDF has none of these inputs: {names}")


def _load_color_texture(path: Path) -> bpy.types.Image:
    if not path.exists():
        raise FileNotFoundError(path)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "sRGB"
    width, height = image.size
    maximum_dimension = max(width, height)
    if maximum_dimension > MAX_TEXTURE_PX:
        ratio = MAX_TEXTURE_PX / maximum_dimension
        image.scale(max(1, round(width * ratio)), max(1, round(height * ratio)))
    return image


def _make_surface_material(
    name: str,
    *,
    base_color: tuple[float, float, float, float],
    roughness: float,
    metallic: float,
    texture_path: Path | None = None,
    transmission: float = 0.0,
    coat: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    _principled_input(principled, "Base Color").default_value = base_color
    _principled_input(principled, "Roughness").default_value = roughness
    _principled_input(principled, "Metallic").default_value = metallic
    _principled_input(principled, "IOR").default_value = 1.47
    transmission_socket = principled.inputs.get("Transmission Weight") or principled.inputs.get("Transmission")
    if transmission_socket is not None:
        transmission_socket.default_value = transmission
    coat_socket = principled.inputs.get("Coat Weight") or principled.inputs.get("Clearcoat")
    if coat_socket is not None:
        coat_socket.default_value = coat
    if texture_path is not None:
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = _load_color_texture(texture_path)
        texture.interpolation = "Linear"
        links.new(texture.outputs["Color"], _principled_input(principled, "Base Color"))
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    return material


def _apply_semantic_materials(crown: bpy.types.Object, texture_root: Path) -> dict[str, int]:
    """Replace Meshy's baked scene texture with construction-specific skins."""
    glass = _make_surface_material(
        "MAT_Concert_CrystallineGlass",
        base_color=(0.38, 0.52, 0.64, 1.0),
        roughness=0.12,
        metallic=0.10,
        texture_path=texture_root / "concert_crystalline_glass" / "albedo.jpg",
        transmission=0.16,
        coat=0.58,
    )
    roof = _make_surface_material(
        "MAT_Concert_SilverTensileRoof",
        base_color=(0.70, 0.76, 0.82, 1.0),
        roughness=0.27,
        metallic=0.52,
        texture_path=texture_root / "concert_tensile_roof" / "albedo.jpg",
        coat=0.34,
    )
    transition = _make_surface_material(
        "MAT_Concert_HistoricTransition",
        base_color=(0.39, 0.16, 0.10, 1.0),
        roughness=0.78,
        metallic=0.0,
        texture_path=texture_root / "concert_warehouse_brick" / "albedo.jpg",
    )
    crown.data.materials.clear()
    for material in (glass, roof, transition):
        crown.data.materials.append(material)

    counts = {"glass": 0, "roof": 0, "historic_transition": 0}
    uv_layer = crown.data.uv_layers.get("UVMap") or crown.data.uv_layers.new(name="UVMap")
    for polygon in crown.data.polygons:
        centre = polygon.center
        normal_z = polygon.normal.z
        if centre.z <= TRANSITION_CLASSIFICATION_Z_M and abs(normal_z) < 0.45:
            material_index = 2
            counts["historic_transition"] += 1
        elif centre.z >= ROOF_CLASSIFICATION_Z_M and normal_z >= ROOF_NORMAL_Z:
            material_index = 1
            counts["roof"] += 1
        else:
            material_index = 0
            counts["glass"] += 1
        polygon.material_index = material_index

        for loop_index in polygon.loop_indices:
            coordinate = crown.data.vertices[crown.data.loops[loop_index].vertex_index].co
            if material_index == 1:
                u = (coordinate.x / TARGET_SIZE[0]) + 0.5
                v = (coordinate.y / TARGET_SIZE[1]) + 0.5
            else:
                theta = math.atan2(
                    coordinate.y / (TARGET_SIZE[1] * 0.5),
                    coordinate.x / (TARGET_SIZE[0] * 0.5),
                ) % math.tau
                u = theta / math.tau * GLASS_TEXTURE_REPEATS
                if material_index == 2:
                    v = max(
                        0.0,
                        min(
                            1.0,
                            (coordinate.z - CROWN_INTERFACE_Z_M)
                            / (TRANSITION_CLASSIFICATION_Z_M - CROWN_INTERFACE_Z_M),
                        ),
                    )
                else:
                    v = max(
                        0.0,
                        min(1.0, (coordinate.z - CROWN_INTERFACE_Z_M) / 29.0),
                    )
            uv_layer.data[loop_index].uv = (u, v)
    return counts


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    manifest = (args.manifest or output.with_suffix(".manifest.json")).resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = [
        obj for obj in bpy.data.objects
        if obj not in before and obj.type == "MESH"
    ]
    if not imported:
        raise RuntimeError(f"no mesh objects imported from {source}")
    crown = max(imported, key=lambda obj: len(obj.data.polygons))
    source_triangles = len(crown.data.polygons)

    minimum, maximum = world_bounds(crown)
    source_size = maximum - minimum
    crown.scale = (
        TARGET_SIZE[0] / source_size.x,
        TARGET_SIZE[1] / source_size.y,
        TARGET_SIZE[2] / source_size.z,
    )
    bpy.context.view_layer.objects.active = crown
    crown.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    minimum, maximum = world_bounds(crown)
    crown.location += Vector((
        -(minimum.x + maximum.x) / 2,
        -(minimum.y + maximum.y) / 2,
        -minimum.z,
    ))
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    mesh = crown.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    below = [vertex for vertex in bm.verts if vertex.co.z < float(args.interface_z)]
    bmesh.ops.delete(bm, geom=below, context="VERTS")
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    if not mesh.polygons:
        raise RuntimeError("crown cut removed every source polygon")

    pre_decimate_triangles = len(mesh.polygons)
    if pre_decimate_triangles > args.target_triangles:
        modifier = crown.modifiers.new(name="RuntimeTriangleBudget", type="DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = max(0.01, args.target_triangles / pre_decimate_triangles)
        modifier.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = crown
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    texture_root = Path(__file__).resolve().parent / "textures"
    semantic_face_counts = _apply_semantic_materials(crown, texture_root)

    for image in bpy.data.images:
        if image.source == "GENERATED":
            continue
        width, height = image.size
        maximum_dimension = max(width, height)
        if maximum_dimension > MAX_TEXTURE_PX:
            ratio = MAX_TEXTURE_PX / maximum_dimension
            image.scale(max(1, round(width * ratio)), max(1, round(height * ratio)))

    crown.name = "FIXED_ConcertHall_MeshyCrown"
    crown.data.name = crown.name
    crown["lego_role"] = "fixed_crown_roof"
    crown["source_kind"] = "meshy_image_to_3d"
    crown["interface_z_m"] = float(args.interface_z)
    crown["target_dimensions_m"] = list(TARGET_SIZE)

    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    crown.select_set(True)
    bpy.context.view_layer.objects.active = crown
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12,
    )

    payload = {
        "schema": "external-fixed-assembly@1",
        "source_file": source.name,
        "source_sha256": sha256(source),
        "output_file": output.name,
        "output_sha256": sha256(output),
        "source_triangles": source_triangles,
        "pre_decimate_triangles": pre_decimate_triangles,
        "output_triangles": len(crown.data.polygons),
        "target_dimensions_m": list(TARGET_SIZE),
        "interface_z_m": float(args.interface_z),
        "max_texture_px": MAX_TEXTURE_PX,
        "material_segmentation": {
            "schema": "concert-crown-material-segmentation@1",
            "face_counts": semantic_face_counts,
            "roof_classification_z_m": ROOF_CLASSIFICATION_Z_M,
            "roof_normal_z": ROOF_NORMAL_Z,
            "transition_classification_z_m": TRANSITION_CLASSIFICATION_Z_M,
            "glass_texture_repeats": GLASS_TEXTURE_REPEATS,
            "materials": {
                "glass": "concert_crystalline_glass",
                "roof": "concert_tensile_roof",
                "historic_transition": "concert_warehouse_brick",
            },
        },
        "lego_contract": {
            "role": "fixed_crown_roof",
            "repeatable": False,
            "paired_repeatable_kit": "concert_warehouse_brick",
        },
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
