"""Validate embedded buffers, allocations and textures before geometry decoding."""

import base64
from io import BytesIO
import struct

from fastapi import HTTPException
from PIL import Image

MAX_SCENE_NODES = 10_000
MAX_SCENE_EDGES = 20_000
MAX_SCENE_DEPTH = 128
MAX_REFERENCED_VERTICES = 10_000_000


def _validate_scene_graph(doc: dict, mesh_vertices: list[int], mesh_primitives: list[int]) -> None:
    """Bound traversal and transformed vertex work before entering trimesh.

    Accessor memory alone does not bound scene.bounds: it transforms every
    vertex for every referencing node. Multiple primitives also become extra
    native graph nodes. Validate the forest iteratively, including unused
    nodes, then count expansion across all scenes for the browser as well.
    """

    def invalid(message="The GLB scene must use an acyclic hierarchy with one parent per node and unique scene roots."):
        raise HTTPException(422, message)

    def budget():
        invalid(
            "The GLB scene exceeds its inspection work budget (10,000 nodes, 20,000 edges, "
            "128 hierarchy levels or 10 million referenced vertices). Reduce repeated scene nodes before importing."
        )

    nodes, scenes = doc.get("nodes", []), doc.get("scenes", [])
    if not isinstance(nodes, list) or not isinstance(scenes, list):
        invalid()
    if len(nodes) + len(scenes) > MAX_SCENE_NODES or sum(mesh_primitives) > MAX_SCENE_NODES:
        budget()
    if "scene" in doc and (type(doc["scene"]) is not int or not 0 <= doc["scene"] < len(scenes)):
        invalid()

    parents = [-1] * len(nodes)
    children = []
    referenced_vertices, expanded_nodes, expanded_edges = [], [], []
    declared_edges = 0
    for parent, node in enumerate(nodes):
        if not isinstance(node, dict) or not isinstance(node.get("children", []), list):
            invalid()
        child_indices = node.get("children", [])
        declared_edges += len(child_indices)
        if declared_edges > MAX_SCENE_EDGES:
            budget()
        for child in child_indices:
            if type(child) is not int or not 0 <= child < len(nodes) or parents[child] != -1:
                invalid()
            parents[child] = parent
        children.append(child_indices)
        vertex_count, synthetic_nodes = 0, 0
        if "mesh" in node:
            reference = node["mesh"]
            if type(reference) is not int or not 0 <= reference < len(mesh_vertices):
                invalid("The GLB scene refers to an invalid mesh.")
            vertex_count = mesh_vertices[reference]
            # Trimesh adds a child node for each primitive when a mesh has
            # multiple primitives, while retaining the original parent node.
            if mesh_primitives[reference] > 1:
                synthetic_nodes = mesh_primitives[reference]
        referenced_vertices.append(vertex_count)
        expanded_nodes.append(1 + synthetic_nodes)
        expanded_edges.append(len(child_indices) + synthetic_nodes)

    order = []
    pending = [(node, 1) for node, parent in enumerate(parents) if parent == -1]
    while pending:
        node, depth = pending.pop()
        if depth > MAX_SCENE_DEPTH:
            budget()
        order.append(node)
        pending.extend((child, depth + 1) for child in children[node])
    if len(order) != len(nodes):
        invalid()
    # The single-parent forest makes each subtree disjoint. Its totals can be
    # accumulated once without recursion or repeated subtree traversals.
    for node in reversed(order):
        parent = parents[node]
        if parent != -1:
            referenced_vertices[parent] += referenced_vertices[node]
            expanded_nodes[parent] += expanded_nodes[node]
            expanded_edges[parent] += expanded_edges[node]

    scene_nodes, scene_edges, vertex_work = len(scenes), 0, 0
    for scene in scenes:
        if not isinstance(scene, dict) or not isinstance(scene.get("nodes", []), list):
            invalid()
        roots = scene.get("nodes", [])
        declared_edges += len(roots)
        if declared_edges > MAX_SCENE_EDGES:
            budget()
        seen = set()
        for root in roots:
            if type(root) is not int or not 0 <= root < len(nodes) or parents[root] != -1 or root in seen:
                invalid()
            seen.add(root)
            scene_nodes += expanded_nodes[root]
            scene_edges += 1 + expanded_edges[root]
            vertex_work += referenced_vertices[root]
            if scene_nodes > MAX_SCENE_NODES or scene_edges > MAX_SCENE_EDGES or vertex_work > MAX_REFERENCED_VERTICES:
                budget()


def validate_glb_resources(doc: dict, payload: bytes, json_end: int) -> None:
    def invalid(message="The GLB has broken embedded resources. Export it again with textures embedded."):
        raise HTTPException(422, message)

    def index(items, value):
        if type(value) is not int or not 0 <= value < len(items):
            invalid()
        return items[value]

    def data_uri(uri):
        if not isinstance(uri, str) or not uri.startswith("data:") or ";base64," not in uri:
            invalid()
        return base64.b64decode(uri.split(";base64,", 1)[1], validate=True)

    # Draco's stream determines output counts independently of glTF accessors.
    # There is no bounded Draco decoder in the backend. Meshopt is supported
    # below: its complete output allocation is declared in the buffer view.
    unsupported = {"KHR_meshopt_compression", "KHR_draco_mesh_compression"}

    def check_compression(value):
        if isinstance(value, dict):
            if "EXT_mesh_gpu_instancing" in value.get("extensions", {}):
                invalid(
                    "GPU-instanced GLBs are not supported for import measurement. Bake the instances into ordinary mesh nodes and export again."
                )
            if unsupported.intersection(value.get("extensions", {})):
                invalid(
                    "This geometry compression codec is not supported for imports. Export a GLB without Draco compression, or Meshopt with an embedded fallback."
                )
            for key, child in value.items():
                if key in ("extensionsUsed", "extensionsRequired") and "EXT_mesh_gpu_instancing" in child:
                    invalid(
                        "GPU-instanced GLBs are not supported for import measurement. Bake the instances into ordinary mesh nodes and export again."
                    )
                if key in ("extensionsUsed", "extensionsRequired") and unsupported.intersection(child):
                    invalid(
                        "This geometry compression codec is not supported for imports. Export a GLB without Draco compression, or Meshopt with an embedded fallback."
                    )
                check_compression(child)
        elif isinstance(value, list):
            for child in value:
                check_compression(child)

    check_compression(doc)

    binary = b""
    offset = json_end
    while offset < len(payload):
        if offset + 8 > len(payload):
            invalid()
        length, kind = struct.unpack_from("<II", payload, offset)
        if length % 4 or offset + 8 + length > len(payload):
            invalid()
        if kind == 0x004E4942:
            if binary:
                invalid()
            binary = payload[offset + 8 : offset + 8 + length]
        offset += length + 8
    buffers = []
    for i, item in enumerate(doc.get("buffers", [])):
        raw = data_uri(item["uri"]) if "uri" in item else binary if i == 0 else b""
        length = item.get("byteLength")
        if type(length) is not int or not 0 <= length <= len(raw):
            if (
                "uri" not in item
                and i > 0
                and any("EXT_meshopt_compression" in view.get("extensions", {}) for view in doc.get("bufferViews", []))
            ):
                invalid(
                    "Meshopt compression imports require an embedded uncompressed fallback for server inspection. Export with fallback buffers included."
                )
            invalid()
        buffers.append(raw[:length])
    views = doc.get("bufferViews", [])
    decoded_bytes = 0
    for view in views:
        raw = index(buffers, view.get("buffer"))
        start, length = view.get("byteOffset", 0), view.get("byteLength")
        if type(start) is not int or type(length) is not int or start < 0 or length < 0 or start + length > len(raw):
            invalid()
        # The native loader copies every view, even unused overlapping ranges.
        # Charge each view separately before it can materialize those copies.
        decoded_bytes += length
        if decoded_bytes > 128 * 1024 * 1024:
            invalid(
                "The GLB needs more than 128 MB of decoded geometry memory. Reduce its embedded geometry data before importing."
            )
        extension = view.get("extensions", {}).get("EXT_meshopt_compression")
        if extension is not None:

            def invalid_meshopt():
                invalid(
                    "The Meshopt compression layout or decoded memory budget is invalid. Export again with valid embedded fallback buffers."
                )

            if not isinstance(extension, dict):
                invalid_meshopt()
            count, stride = extension.get("count"), extension.get("byteStride")
            mode, filter_ = extension.get("mode"), extension.get("filter", "NONE")
            if type(count) is not int or type(stride) is not int or count <= 0 or not 1 <= stride <= 256:
                invalid_meshopt()
            decoded_bytes += count * stride
            if decoded_bytes > 128 * 1024 * 1024 or count * stride != length:
                invalid_meshopt()
            if view.get("byteStride", stride) != stride:
                invalid_meshopt()
            if mode not in ("ATTRIBUTES", "TRIANGLES", "INDICES") or filter_ not in (
                "NONE",
                "OCTAHEDRAL",
                "QUATERNION",
                "EXPONENTIAL",
            ):
                invalid_meshopt()
            if (
                (mode == "ATTRIBUTES" and stride % 4)
                or (mode in ("TRIANGLES", "INDICES") and (stride not in (2, 4) or filter_ != "NONE"))
                or (mode == "TRIANGLES" and count % 3)
                or (filter_ == "OCTAHEDRAL" and stride not in (4, 8))
                or (filter_ == "QUATERNION" and stride != 8)
                or (filter_ == "EXPONENTIAL" and stride % 4)
            ):
                invalid_meshopt()
            compressed = index(buffers, extension.get("buffer"))
            offset, size = extension.get("byteOffset", 0), extension.get("byteLength")
            if (
                type(offset) is not int
                or type(size) is not int
                or offset < 0
                or size <= 0
                or offset + size > len(compressed)
            ):
                invalid_meshopt()
    components = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}
    byte_sizes = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
    for accessor in doc.get("accessors", []):
        count, kind, component = accessor.get("count"), accessor.get("type"), accessor.get("componentType")
        if type(count) is not int or count < 0 or kind not in components or component not in byte_sizes:
            invalid("The GLB has invalid geometry data. Export it again as a static GLB 2.0.")
        element = components[kind] * byte_sizes[component]
        decoded_bytes += count * element
        # Bound decoded allocations (including sparse/implicit zero arrays),
        # rather than rejecting valid models for an arbitrary element count.
        if decoded_bytes > 128 * 1024 * 1024:
            invalid(
                "The GLB needs more than 128 MB of decoded geometry memory. Reduce its embedded geometry data before importing."
            )
        if "bufferView" in accessor:
            view = index(views, accessor["bufferView"])
            start, stride = accessor.get("byteOffset", 0), view.get("byteStride", element)
            if (
                type(start) is not int
                or type(stride) is not int
                or start < 0
                or stride < element
                or start + max(0, count - 1) * stride + (element if count else 0) > view["byteLength"]
            ):
                invalid()
        if "sparse" in accessor:
            sparse = accessor["sparse"]
            sparse_count = sparse.get("count")
            if type(sparse_count) is not int or not 0 <= sparse_count <= count:
                invalid()
            for field, size in [
                ("indices", byte_sizes.get(sparse.get("indices", {}).get("componentType"), 0)),
                ("values", element),
            ]:
                record = sparse.get(field, {})
                view = index(views, record.get("bufferView"))
                start = record.get("byteOffset", 0)
                if not size or type(start) is not int or start < 0 or start + sparse_count * size > view["byteLength"]:
                    invalid()
    # Native geometry is materialized per primitive, even when primitives reuse
    # the same compact accessors. Account for copies and float64 promotion before
    # entering the decoder; shared scene nodes still reuse these geometries.
    expanded_bytes = decoded_bytes
    accessors = doc.get("accessors", [])
    mesh_vertices, mesh_primitives = [], []
    for mesh in doc.get("meshes", []):
        vertices = 0
        for primitive in mesh.get("primitives", []):
            attributes = primitive.get("attributes", {})
            position = index(accessors, attributes.get("POSITION"))
            if position.get("type") != "VEC3":
                invalid("The GLB POSITION attribute must be VEC3.")
            vertices += position["count"]
            for name, reference in attributes.items():
                attribute = index(accessors, reference)
                if name == "NORMAL" and attribute.get("type") != "VEC3":
                    invalid("The GLB NORMAL attribute must be VEC3.")
                expanded_bytes += attribute["count"] * components[attribute["type"]] * 8
            count = position["count"]
            if "indices" in primitive:
                indices = index(accessors, primitive["indices"])
                if indices.get("type") != "SCALAR" or indices.get("componentType") not in (5121, 5123, 5125):
                    invalid("The GLB indices must use unsigned scalar values.")
                count = indices["count"]
            mode = primitive.get("mode", 4)
            expanded_bytes += (max(0, count - 2) * 3 if mode in (5, 6) else count) * 8
            if expanded_bytes > 128 * 1024 * 1024:
                invalid(
                    "The GLB needs more than 128 MB of decoded geometry memory. Reduce its embedded geometry data before importing."
                )
        mesh_vertices.append(vertices)
        mesh_primitives.append(len(mesh.get("primitives", [])))
    _validate_scene_graph(doc, mesh_vertices, mesh_primitives)
    images = doc.get("images", [])
    pixels = 0
    texture_bytes = 0
    for image in images:
        if "uri" in image:
            raw = data_uri(image["uri"])
        else:
            view = index(views, image.get("bufferView"))
            buffer = index(buffers, view.get("buffer"))
            raw = buffer[view.get("byteOffset", 0) : view.get("byteOffset", 0) + view["byteLength"]]
        if raw.startswith(b"\xabKTX 20\xbb\r\n\x1a\n"):
            if len(raw) < 80:
                invalid()
            width, height, depth, layers, faces, levels, scheme = struct.unpack_from("<7I", raw, 20)
            # glTF material textures are 2D. Browser KTX loaders otherwise
            # iterate layers/faces and trust Zstd's declared output size.
            if depth or layers not in (0, 1) or faces != 1 or not 1 <= levels <= max(width, height).bit_length():
                invalid("KTX2 imports require bounded 2D textures with one layer and valid mip levels.")
            index_end = 80 + levels * 24
            if levels > 14 or index_end > len(raw) or scheme not in (0, 1, 2):
                invalid()
            dfd_offset, dfd_size, kvd_offset, kvd_size, sgd_offset, sgd_size = struct.unpack_from("<4I2Q", raw, 48)
            for start, size in ((dfd_offset, dfd_size), (kvd_offset, kvd_size), (sgd_offset, sgd_size)):
                if size and (start < index_end or start + size > len(raw)):
                    invalid()
            if dfd_size < 28 or struct.unpack_from("<I", raw, dfd_offset)[0] != dfd_size:
                invalid()
            for level in range(levels):
                start, size, expanded = struct.unpack_from("<3Q", raw, 80 + level * 24)
                if not size or start < index_end or start + size > len(raw):
                    invalid()
                level_width, level_height = max(1, width >> level), max(1, height >> level)
                if (
                    (scheme == 0 and expanded != size)
                    or (scheme == 1 and expanded != 0)
                    or (scheme != 1 and not 0 < expanded <= max(4, level_width) * max(4, level_height) * 16)
                ):
                    invalid("The KTX2 texture has invalid decoded memory declarations.")
                texture_bytes += max(expanded, level_width * level_height * 4)
        else:
            with Image.open(BytesIO(raw)) as picture:
                width, height = picture.size
                picture.verify()
            texture_bytes += width * height * 4
        pixels += width * height
        if (
            not 0 < width <= 8192
            or not 0 < height <= 8192
            or pixels > 64 * 1024 * 1024
            or texture_bytes > 512 * 1024 * 1024
        ):
            invalid("The textures are too large. Use smaller embedded textures before importing.")
    textures = doc.get("textures", [])
    for texture in textures:
        source = texture.get("source", texture.get("extensions", {}).get("KHR_texture_basisu", {}).get("source"))
        index(images, source)

    def material_textures(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.lower().endswith("texture") and isinstance(item, dict):
                    index(textures, item.get("index"))
                material_textures(item)
        elif isinstance(value, list):
            for item in value:
                material_textures(item)

    material_textures(doc.get("materials", []))
    for mesh in doc.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            if "material" in primitive:
                index(doc.get("materials", []), primitive["material"])
