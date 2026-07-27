"""Convert the supplied Meshy Markthal GLB into a bounded fixed landmark.

The image-to-3D source carries the inhabited arch, market interior, side
lattice and roof court convincingly, but arrives as a unitless 1.4M-triangle
single mesh with open end walls. This converter:

* rotates the long axis onto Blender Y so the principal facade faces -Y;
* normalizes the source without distortion to a 60 x 96 x 36.75 m envelope;
* decimates and downsamples its embedded textures for runtime delivery; and
* authors transparent arched end walls with a physical cable grid.

Run with Blender:

  blender --background --factory-startup --python \
      convert_meshy_markthal_reference.py -- \
      --source source.glb --output food-hall-market-hall_markthal.glb
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


TARGET_SIZE = (60.0, 96.0, 36.75)
TARGET_TRIANGLES = 160_000
MAX_TEXTURE_PX = 1024
ARCH_HALF_WIDTH_M = 19.0
ARCH_SPRING_Z_M = 13.8
GLASS_INSET_M = 0.32
CABLE_SPACING_M = 2.35
CABLE_PROFILE_M = 0.075


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--target-triangles", type=int, default=TARGET_TRIANGLES)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[index] for point in corners) for index in range(3))),
        Vector(tuple(max(point[index] for point in corners) for index in range(3))),
    )


def _principled_input(node: bpy.types.ShaderNodeBsdfPrincipled, *names: str):
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            return socket
    raise KeyError(f"Principled BSDF has none of these inputs: {names}")


def make_material(
    name: str,
    *,
    base_color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
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
    _principled_input(principled, "IOR").default_value = 1.46
    alpha = float(base_color[3])
    alpha_socket = principled.inputs.get("Alpha")
    if alpha_socket is not None:
        alpha_socket.default_value = alpha
    material.diffuse_color = base_color
    if alpha < 0.999:
        try:
            material.surface_render_method = "DITHERED"
        except (AttributeError, TypeError):
            pass
    transmission_socket = (
        principled.inputs.get("Transmission Weight")
        or principled.inputs.get("Transmission")
    )
    if transmission_socket is not None:
        transmission_socket.default_value = transmission
    coat_socket = principled.inputs.get("Coat Weight") or principled.inputs.get("Clearcoat")
    if coat_socket is not None:
        coat_socket.default_value = coat
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    return material


def add_box(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    material: bpy.types.Material,
    *,
    rotation_y: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    obj.rotation_euler.y = rotation_y
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj


def join_objects(objects: list[bpy.types.Object], name: str) -> bpy.types.Object:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    objects[0].name = name
    objects[0].data.name = name
    return objects[0]


def arch_height_at(x: float) -> float:
    return ARCH_SPRING_Z_M + math.sqrt(
        max(0.0, ARCH_HALF_WIDTH_M**2 - x**2)
    )


def arch_half_width_at(z: float) -> float:
    if z <= ARCH_SPRING_Z_M:
        return ARCH_HALF_WIDTH_M
    return math.sqrt(
        max(0.0, ARCH_HALF_WIDTH_M**2 - (z - ARCH_SPRING_Z_M) ** 2)
    )


def add_arch_glazing(
    *,
    elevation: str,
    y: float,
    glass: bpy.types.Material,
    cable: bpy.types.Material,
) -> list[bpy.types.Object]:
    """Author one planar cable-net arch while leaving the market visible."""
    segments = 48
    vertices = [
        (-ARCH_HALF_WIDTH_M, y, 0.0),
        (ARCH_HALF_WIDTH_M, y, 0.0),
        (ARCH_HALF_WIDTH_M, y, ARCH_SPRING_Z_M),
    ]
    for index in range(1, segments + 1):
        angle = math.pi * index / segments
        vertices.append(
            (
                ARCH_HALF_WIDTH_M * math.cos(angle),
                y,
                ARCH_SPRING_Z_M + ARCH_HALF_WIDTH_M * math.sin(angle),
            )
        )
    faces = [tuple(range(len(vertices)))]
    mesh = bpy.data.meshes.new(f"Markthal_{elevation}_GlassMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(glass)
    glass_obj = bpy.data.objects.new(f"Markthal_{elevation}_CableNetGlass", mesh)
    bpy.context.collection.objects.link(glass_obj)

    cable_parts: list[bpy.types.Object] = []
    x = -ARCH_HALF_WIDTH_M
    cable_index = 0
    while x <= ARCH_HALF_WIDTH_M + 0.001:
        height = arch_height_at(x)
        cable_parts.append(add_box(
            f"Markthal_{elevation}_VerticalCable{cable_index:02d}",
            (CABLE_PROFILE_M, 0.105, height),
            (x, y - 0.065 if y < 0 else y + 0.065, height / 2),
            cable,
        ))
        cable_index += 1
        x += CABLE_SPACING_M

    z = 0.0
    cable_index = 0
    arch_top = ARCH_SPRING_Z_M + ARCH_HALF_WIDTH_M
    while z <= arch_top + 0.001:
        half_width = arch_half_width_at(z)
        if half_width > 0.08:
            cable_parts.append(add_box(
                f"Markthal_{elevation}_HorizontalCable{cable_index:02d}",
                (half_width * 2, 0.105, CABLE_PROFILE_M),
                (0.0, y - 0.065 if y < 0 else y + 0.065, z),
                cable,
            ))
        cable_index += 1
        z += CABLE_SPACING_M

    # A stronger perimeter ring makes the glass opening legible at city LOD.
    cable_parts.extend([
        add_box(
            f"Markthal_{elevation}_LeftJamb",
            (0.22, 0.18, ARCH_SPRING_Z_M),
            (-ARCH_HALF_WIDTH_M, y, ARCH_SPRING_Z_M / 2),
            cable,
        ),
        add_box(
            f"Markthal_{elevation}_RightJamb",
            (0.22, 0.18, ARCH_SPRING_Z_M),
            (ARCH_HALF_WIDTH_M, y, ARCH_SPRING_Z_M / 2),
            cable,
        ),
    ])
    previous = Vector(
        (ARCH_HALF_WIDTH_M, y, ARCH_SPRING_Z_M)
    )
    for index in range(1, segments + 1):
        angle = math.pi * index / segments
        current = Vector((
            ARCH_HALF_WIDTH_M * math.cos(angle),
            y,
            ARCH_SPRING_Z_M + ARCH_HALF_WIDTH_M * math.sin(angle),
        ))
        delta = current - previous
        midpoint = (current + previous) * 0.5
        cable_parts.append(add_box(
            f"Markthal_{elevation}_ArchRing{index:02d}",
            (delta.length + 0.03, 0.18, 0.22),
            tuple(midpoint),
            cable,
            rotation_y=-math.atan2(delta.z, delta.x),
        ))
        previous = current
    cable_obj = join_objects(cable_parts, f"FIXED_Markthal_{elevation}_CableGrid")
    return [glass_obj, cable_obj]


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
    landmark = max(imported, key=lambda obj: len(obj.data.polygons))
    source_triangles = len(landmark.data.polygons)
    for extra in imported:
        if extra is not landmark:
            bpy.data.objects.remove(extra, do_unlink=True)

    # Bake the glTF import hierarchy before rotating. Meshy parents the mesh to
    # a coordinate-conversion node; editing only the child's Euler Z otherwise
    # leaves the apparent facade on X after re-export.
    world_matrix = landmark.matrix_world.copy()
    landmark.parent = None
    landmark.matrix_world = world_matrix
    bpy.context.view_layer.objects.active = landmark
    landmark.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Meshy's long axis is X and its arched end faces -X. Rotate +90 degrees
    # so the long axis becomes Y and the principal facade faces Blender -Y.
    landmark.data.transform(Matrix.Rotation(math.pi / 2, 4, "Z"))
    landmark.data.update()
    minimum, maximum = world_bounds(landmark)
    source_size = maximum - minimum
    landmark.scale = (
        TARGET_SIZE[0] / source_size.x,
        TARGET_SIZE[1] / source_size.y,
        TARGET_SIZE[2] / source_size.z,
    )
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    minimum, maximum = world_bounds(landmark)
    landmark.location += Vector((
        -(minimum.x + maximum.x) / 2,
        -(minimum.y + maximum.y) / 2,
        -minimum.z,
    ))
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    if len(landmark.data.polygons) > int(args.target_triangles):
        modifier = landmark.modifiers.new(name="RuntimeTriangleBudget", type="DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = max(
            0.01, int(args.target_triangles) / len(landmark.data.polygons)
        )
        modifier.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = landmark
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    if landmark.data.materials:
        landmark.data.materials[0].name = "MAT_Markthal_MeshySurface"
    for image in bpy.data.images:
        if image.source in {"GENERATED", "VIEWER"}:
            continue
        width, height = image.size
        maximum_dimension = max(width, height)
        if maximum_dimension > MAX_TEXTURE_PX:
            ratio = MAX_TEXTURE_PX / maximum_dimension
            image.scale(max(1, round(width * ratio)), max(1, round(height * ratio)))
            image.pack()

    glass = make_material(
        "MAT_Markthal_CableNetGlass",
        base_color=(0.21, 0.35, 0.43, 0.22),
        roughness=0.12,
        metallic=0.04,
        transmission=0.18,
        coat=0.46,
    )
    cable = make_material(
        "MAT_Markthal_CableNetSteel",
        base_color=(0.10, 0.12, 0.14, 1.0),
        roughness=0.28,
        metallic=0.78,
        coat=0.22,
    )
    delivery = [landmark]
    delivery.extend(add_arch_glazing(
        elevation="Front",
        y=-TARGET_SIZE[1] / 2 - GLASS_INSET_M,
        glass=glass,
        cable=cable,
    ))
    delivery.extend(add_arch_glazing(
        elevation="Rear",
        y=TARGET_SIZE[1] / 2 + GLASS_INSET_M,
        glass=glass,
        cable=cable,
    ))

    landmark.name = "FIXED_Markthal_MeshyLandmark"
    landmark.data.name = landmark.name
    landmark["lego_role"] = "assembled"
    landmark["source_kind"] = "meshy_image_to_3d"
    landmark["target_dimensions_m"] = list(TARGET_SIZE)
    landmark["front_facade"] = "-Y in Blender / +Z in glTF"
    for obj in delivery:
        obj["lego_role"] = "assembled"
        obj["module_family"] = "food-hall-market-hall"

    bpy.ops.object.select_all(action="DESELECT")
    for obj in delivery:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = landmark
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

    output_triangles = sum(len(obj.data.polygons) for obj in delivery)
    payload = {
        "schema": "external-fixed-assembly@1",
        "source_file": source.name,
        "source_sha256": sha256(source),
        "output_file": output.name,
        "output_sha256": sha256(output),
        "source_triangles": source_triangles,
        "output_triangles": output_triangles,
        "target_dimensions_m": list(TARGET_SIZE),
        "max_texture_px": MAX_TEXTURE_PX,
        "source_material": "MAT_Markthal_MeshySurface",
        "authored_materials": [
            "MAT_Markthal_CableNetGlass",
            "MAT_Markthal_CableNetSteel",
        ],
        "corrections": [
            "metric scale and bottom-centre origin",
            "principal facade rotated to Blender -Y / glTF +Z",
            "front and rear cable-net glass arch walls",
            "runtime triangle and embedded texture budgets",
        ],
        "lego_contract": {
            "role": "assembled",
            "assembly_class": "fixed_landmark",
            "repeatable": False,
            "family": "food-hall-market-hall",
            "source_variant_id": "market_contemporary",
            "generation_archetype_id": "market_contemporary",
            "native_floors": 3,
        },
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
