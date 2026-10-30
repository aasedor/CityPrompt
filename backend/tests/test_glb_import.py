import json
import base64
import struct
import uuid
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, UploadFile

from app.services.glb_import import inspect_glb
from app.services.user_generated_models import generated_entry, is_user_generated
from app.models.models import Building


def glb(width=12, height=9, depth=20, translation=None, external=False):
    vertices = [(x, y, z) for x in (0, width) for y in (0, height) for z in (0, depth)]
    raw = struct.pack("<24f", *(v for p in vertices for v in p))
    raw += struct.pack(
        "<36H",
        *[0, 1, 2, 1, 3, 2, 4, 6, 5, 5, 6, 7, 0, 4, 1, 1, 4, 5, 2, 3, 6, 3, 7, 6, 0, 2, 4, 2, 6, 4, 1, 5, 3, 3, 5, 7],
    )
    doc = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "translation": translation or [0, 0, 0]}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
        "buffers": [{"byteLength": len(raw)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": 96},
            {"buffer": 0, "byteOffset": 96, "byteLength": 72},
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 8,
                "type": "VEC3",
                "min": [0, 0, 0],
                "max": [width, height, depth],
            },
            {"bufferView": 1, "componentType": 5123, "count": 36, "type": "SCALAR"},
        ],
    }
    if external:
        doc["images"] = [{"uri": "https://example.com/private.png"}]
    text = json.dumps(doc).encode()
    text += b" " * (-len(text) % 4)
    return (
        struct.pack("<4sII", b"glTF", 2, 28 + len(text) + len(raw))
        + struct.pack("<II", len(text), 0x4E4F534A)
        + text
        + struct.pack("<II", len(raw), 0x004E4942)
        + raw
    )


def test_measures_original_geometry_with_offset_origin_and_converts_units():
    result = inspect_glb(glb(1200, 900, 2000, [10000, -4000, 500]), "centimetres")
    assert result["width_m"] == pytest.approx(12)
    assert result["depth_m"] == pytest.approx(20)
    assert result["height_meters"] == pytest.approx(9)
    assert result["triangles"] == 12


def repeated_primitive_glb(vertices=100000, copies=200):
    original = glb()
    length = struct.unpack_from("<I", original, 12)[0]
    doc = json.loads(original[20 : 20 + length])
    binary = original[28 + length : 28 + length + 96] + bytes(vertices * 12 - 96)
    binary += original[28 + length + 96 :]
    doc["bufferViews"][0]["byteLength"] = vertices * 12
    doc["bufferViews"][1]["byteOffset"] = vertices * 12
    doc["accessors"][0]["count"] = vertices
    doc["buffers"][0]["byteLength"] = len(binary)
    doc["meshes"][0]["primitives"] *= copies
    encoded = json.dumps(doc).encode()
    encoded += b" " * (-len(encoded) % 4)
    return (
        struct.pack("<4sII", b"glTF", 2, 28 + len(encoded) + len(binary))
        + struct.pack("<II", len(encoded), 0x4E4F534A)
        + encoded
        + struct.pack("<II", len(binary), 0x004E4942)
        + binary
    )


def test_repeated_primitive_expansion_is_bounded_before_native_decode(monkeypatch):
    decoder = MagicMock(side_effect=AssertionError("Oversized geometry reached decoder"))
    monkeypatch.setattr("trimesh.load", decoder)
    with pytest.raises(HTTPException, match="128 MB"):
        inspect_glb(repeated_primitive_glb(), "metres")
    decoder.assert_not_called()


def test_small_shared_primitive_reuse_still_imports():
    assert inspect_glb(repeated_primitive_glb(vertices=8, copies=2), "metres")["triangles"] == 24


def overlapping_views_glb(copies):
    raw = repeated_primitive_glb(vertices=10000, copies=1)
    length = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20 : 20 + length])
    doc["bufferViews"].extend([{"buffer": 0, "byteOffset": 0, "byteLength": 120000}] * copies)
    encoded = json.dumps(doc).encode()
    encoded += b" " * (-len(encoded) % 4)
    tail = raw[20 + length :]
    return (
        struct.pack("<4sII", b"glTF", 2, 20 + len(encoded) + len(tail))
        + struct.pack("<II", len(encoded), 0x4E4F534A)
        + encoded
        + tail
    )


def test_overlapping_unused_buffer_views_are_bounded_before_native_decode(monkeypatch):
    decoder = MagicMock(side_effect=AssertionError("Oversized views reached decoder"))
    monkeypatch.setattr("trimesh.load", decoder)
    with pytest.raises(HTTPException, match="128 MB"):
        inspect_glb(overlapping_views_glb(2000), "metres")
    decoder.assert_not_called()


def test_small_overlapping_buffer_views_preserve_valid_imports():
    assert inspect_glb(overlapping_views_glb(2), "metres")["triangles"] == 12


def test_arbitrary_game_scale_can_be_given_a_real_building_height_without_distortion():
    result = inspect_glb(glb(1.2, 1, 2), "metres", target_height_m=10)
    assert result["width_m"] == pytest.approx(12)
    assert result["depth_m"] == pytest.approx(20)
    assert result["height_meters"] == pytest.approx(10)


def changed_glb(change, raw=None):
    raw = glb() if raw is None else raw
    length = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20 : 20 + length])
    change(doc)
    text = json.dumps(doc).encode()
    text += b" " * (-len(text) % 4)
    tail = raw[20 + length :]
    return (
        struct.pack("<4sII", b"glTF", 2, 20 + len(text) + len(tail))
        + struct.pack("<II", len(text), 0x4E4F534A)
        + text
        + tail
    )


@pytest.mark.parametrize(
    "nodes,roots",
    [
        ([{"mesh": 0, "children": [0]}], [0]),
        ([{"mesh": 0}, {"children": [2]}, {"children": [1]}], [0]),
        ([{"children": [2]}, {"children": [2]}, {"mesh": 0}], [0, 1]),
        ([{"children": [1, 1]}, {"mesh": 0}], [0]),
        ([{"children": [1]}, {"mesh": 0}], [0, 1]),
        ([{"mesh": 0}], [0, 0]),
        ([{"children": [False], "mesh": 0}], [0]),
        ([{"children": [999], "mesh": 0}], [0]),
    ],
    ids=[
        "self-cycle",
        "unused-cycle",
        "two-parents",
        "duplicate-edge",
        "child-root",
        "duplicate-root",
        "bool-index",
        "bad-index",
    ],
)
def test_scene_topology_rejected_before_geometry_decoder(monkeypatch, nodes, roots):
    decoder = MagicMock(side_effect=AssertionError("Invalid graph reached native decoder"))
    monkeypatch.setattr("trimesh.load", decoder)
    payload = changed_glb(lambda doc: doc.update(nodes=nodes, scenes=[{"nodes": roots}]))
    with pytest.raises(HTTPException):
        inspect_glb(payload, "metres")
    decoder.assert_not_called()


@pytest.mark.parametrize("kind", ["nodes", "edges", "depth", "primitive-nodes", "vertex-work"])
def test_scene_work_amplification_rejected_before_geometry_decoder(monkeypatch, kind):
    def amplify(doc):
        if kind == "nodes":
            doc["nodes"] = [{"mesh": 0}] * 10001
            doc["scenes"] = [{"nodes": list(range(10001))}]
        elif kind == "edges":
            doc["scenes"] = [{"nodes": [0] * 20001}]
        elif kind == "depth":
            doc["nodes"] = [{"children": [index + 1]} for index in range(128)] + [{"mesh": 0}]
        else:
            doc["nodes"] = [{"mesh": 0}] * 101
            doc["scenes"] = [{"nodes": list(range(101))}]
            if kind == "primitive-nodes":
                doc["meshes"][0]["primitives"] *= 101

    original = repeated_primitive_glb(vertices=100000, copies=1) if kind == "vertex-work" else glb()
    payload = changed_glb(amplify, original)
    decoder = MagicMock(side_effect=AssertionError("Unbounded scene work reached native decoder"))
    monkeypatch.setattr("trimesh.load", decoder)
    with pytest.raises(HTTPException):
        inspect_glb(payload, "metres")
    decoder.assert_not_called()


def test_gpu_instancing_rejected_before_decoder_with_precise_export_guidance(monkeypatch):
    def add_instancing(doc):
        doc["accessors"].append({"count": 1000000, "componentType": 5126, "type": "VEC3"})
        doc["meshes"][0]["primitives"] *= 100
        doc["extensionsUsed"] = ["EXT_mesh_gpu_instancing"]
        doc["nodes"][0]["extensions"] = {"EXT_mesh_gpu_instancing": {"attributes": {"TRANSLATION": 2}}}

    decoder = MagicMock(side_effect=AssertionError("Instanced geometry reached native decoder"))
    monkeypatch.setattr("trimesh.load", decoder)
    with pytest.raises(HTTPException) as exc:
        inspect_glb(changed_glb(add_instancing), "metres")
    assert "instanc" in exc.value.detail.lower() and "bake" in exc.value.detail.lower()
    decoder.assert_not_called()


def test_bounded_hierarchy_and_shared_mesh_nodes_keep_exact_bounds():
    def hierarchy(doc):
        doc["nodes"] = [{"children": [1, 2]}, {"mesh": 0}, {"mesh": 0, "translation": [12, 0, 0]}]
        # glTF permits a root to be used by multiple scenes.
        doc["scenes"] = [{"nodes": [0]}, {"nodes": [0]}]

    result = inspect_glb(changed_glb(hierarchy), "metres")
    assert result["triangles"] == 24
    assert (result["width_m"], result["depth_m"], result["height_meters"]) == (20, 24, 9)


def test_imports_valid_dense_geometry_beyond_standard_building_complexity():
    # Meshy exports can have >3M index elements while remaining within the
    # upload and decoded-resource budgets. Repeated box faces keep this fixture
    # self-contained and exercise the real geometry decoder without a binary.
    original = glb()
    length = struct.unpack_from("<I", original, 12)[0]
    doc = json.loads(original[20 : 20 + length])
    triangles = 1_000_004
    indices = struct.pack("<3I", 0, 1, 2) * triangles
    binary = original[28 + length : 28 + length + 96] + indices
    doc["buffers"][0]["byteLength"] = len(binary)
    doc["bufferViews"][1]["byteLength"] = len(indices)
    doc["accessors"][1].update(componentType=5125, count=triangles * 3)
    text = json.dumps(doc).encode()
    text += b" " * (-len(text) % 4)
    payload = (
        struct.pack("<4sII", b"glTF", 2, 28 + len(text) + len(binary))
        + struct.pack("<II", len(text), 0x4E4F534A)
        + text
        + struct.pack("<II", len(binary), 0x004E4942)
        + binary
    )
    result = inspect_glb(payload, "metres")
    assert result["triangles"] == triangles
    assert (result["width_m"], result["height_meters"], result["depth_m"]) == (12, 9, 20)


def test_large_scene_description_is_bounded_by_upload_size_not_building_complexity():
    payload = changed_glb(lambda d: d.update(extras={"source_note": "a" * (4 * 1024 * 1024)}))
    assert inspect_glb(payload, "metres")["triangles"] == 12


@pytest.mark.parametrize("width,height,depth", [(0.5, 1, 0.8), (1200, 900, 2000), (1e-6, 2e-6, 3e-6)])
def test_valid_native_dimensions_are_preserved_without_building_size_restrictions(width, height, depth):
    result = inspect_glb(glb(width, height, depth), "metres")
    assert result["width_m"] == pytest.approx(width)
    assert result["depth_m"] == pytest.approx(depth)
    assert result["height_meters"] == pytest.approx(height)


@pytest.mark.parametrize("kind,count", [("SCALAR", 100_000_000), ("MAT4", 3_000_000)])
def test_bounds_all_accessor_allocations_before_loading_geometry(monkeypatch, kind, count):
    import trimesh

    loader = MagicMock(side_effect=RuntimeError("Geometry loader must not run"))
    monkeypatch.setattr(trimesh, "load", loader)
    raw = changed_glb(lambda d: d["accessors"].append({"componentType": 5126, "type": kind, "count": count}))
    with pytest.raises(HTTPException):
        inspect_glb(raw, "metres")
    loader.assert_not_called()


def test_rejects_broken_embedded_texture_before_the_browser_loads_it():
    def break_image(d):
        d["images"] = [{"bufferView": 999, "mimeType": "image/png"}]
        d["textures"] = [{"source": 0}]
        d["materials"] = [{"pbrMetallicRoughness": {"baseColorTexture": {"index": 0}}}]
        d["meshes"][0]["primitives"][0]["material"] = 0

    with pytest.raises(HTTPException, match=""):
        inspect_glb(changed_glb(break_image), "metres")


@pytest.mark.parametrize("extension", ["EXT_meshopt_compression", "KHR_draco_mesh_compression"])
def test_rejects_unvalidated_compressed_geometry_before_decoder(monkeypatch, extension):
    # A normal fallback box must not hide instructions for a different browser
    # decoding path. No actual compressed decoding or large allocation occurs.
    def add_compression(doc):
        doc["extensionsUsed"] = [extension]
        doc["bufferViews"][0]["extensions"] = {
            extension: {"buffer": 0, "byteOffset": 0, "byteLength": 8, "count": 268435456, "byteStride": 12}
        }

    payload = changed_glb(add_compression)
    with pytest.raises(HTTPException) as exc:
        inspect_glb(payload, "metres")
    assert exc.value.status_code == 422
    assert "compression" in exc.value.detail.lower()


def meshopt_glb(change=None):
    # Real Meshopt ATTRIBUTES stream for the fixture's eight XYZ vertices,
    # generated with the installed meshoptimizer encoder. Retain the valid
    # uncompressed fallback so trimesh and the browser measure the same box.
    compressed = base64.b64decode(
        "oAAAAQDAAACAAQDAAACCAAABDMwAACAfIAEMzAAAgoGCAAABP/8AAL/Av8C/wL8BP/8AAIKBgoGCgYIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=="
    )
    original = glb()
    length = struct.unpack_from("<I", original, 12)[0]
    doc = json.loads(original[20 : 20 + length])
    binary = original[28 + length :] + compressed
    binary += b"\0" * (-len(binary) % 4)
    doc["buffers"][0]["byteLength"] = len(binary)
    doc["extensionsUsed"] = ["EXT_meshopt_compression"]
    extension = {
        "buffer": 0,
        "byteOffset": 168,
        "byteLength": len(compressed),
        "byteStride": 12,
        "count": 8,
        "mode": "ATTRIBUTES",
    }
    doc["bufferViews"][0]["extensions"] = {"EXT_meshopt_compression": extension}
    if change:
        change(extension)
    text = json.dumps(doc).encode()
    text += b" " * (-len(text) % 4)
    return (
        struct.pack("<4sII", b"glTF", 2, 28 + len(text) + len(binary))
        + struct.pack("<II", len(text), 0x4E4F534A)
        + text
        + struct.pack("<II", len(binary), 0x004E4942)
        + binary
    )


def test_safe_meshopt_with_embedded_fallback_preserves_supported_geometry():
    result = inspect_glb(meshopt_glb(), "metres")
    assert result["triangles"] == 12
    assert (result["width_m"], result["height_meters"], result["depth_m"]) == (12, 9, 20)


@pytest.mark.parametrize(
    "change",
    [
        {"count": 268435456},
        {"byteStride": 256},
        {"byteOffset": 100000},
        {"buffer": 42},
        {"mode": "TRIANGLES"},
        {"filter": "QUATERNION"},
        {"count": True},
        {"filter": "UNKNOWN"},
    ],
)
def test_meshopt_rejects_invalid_decoded_layout_and_source_ranges(change):
    with pytest.raises(HTTPException) as exc:
        inspect_glb(meshopt_glb(lambda extension: extension.update(change)), "metres")
    assert exc.value.status_code == 422


def ktx2_glb(change=None):
    # A one-pixel RGBA8 KTX2 with a complete basic data-format descriptor.
    dfd = struct.pack("<IIHH4B4B8B", 92, 0, 2, 88, 1, 1, 2, 0, *([0] * 4), 4, *([0] * 7))
    dfd += b"".join(
        struct.pack("<HBB4BII", i * 8, 7, channel, 0, 0, 0, 0, 0, 255) for i, channel in enumerate([0, 1, 2, 15])
    )
    raw = bytearray(
        b"\xabKTX 20\xbb\r\n\x1a\n"
        + struct.pack("<13I2Q", 37, 1, 1, 1, 0, 0, 1, 1, 0, 104, 92, 0, 0, 0, 0)
        + struct.pack("<3Q", 196, 4, 4)
        + dfd
        + b"\xff\xff\xff\xff"
    )
    if change:
        change(raw)

    def add_image(doc):
        doc["images"] = [{"uri": "data:image/ktx2;base64," + base64.b64encode(raw).decode()}]
        doc["textures"] = [{"extensions": {"KHR_texture_basisu": {"source": 0}}}]

    return changed_glb(add_image)


def test_bounded_2d_ktx2_texture_keeps_supported_import():
    assert inspect_glb(ktx2_glb(), "metres")["triangles"] == 12


@pytest.mark.parametrize(
    "offset,value",
    [(28, 268435456), (32, 268435456), (36, 100000), (40, 100000)],
    ids=["depth", "layers", "faces", "levels"],
)
def test_ktx2_dimensions_cannot_hide_decoded_texture_work(offset, value):
    with pytest.raises(HTTPException) as exc:
        inspect_glb(ktx2_glb(lambda raw: struct.pack_into("<I", raw, offset, value)), "metres")
    assert exc.value.status_code == 422


def test_ktx2_zstd_declared_allocation_is_bounded_without_decompression():
    def oversized(raw):
        struct.pack_into("<I", raw, 44, 2)
        struct.pack_into("<Q", raw, 96, 3 * 1024 * 1024 * 1024)

    with pytest.raises(HTTPException) as exc:
        inspect_glb(ktx2_glb(oversized), "metres")
    assert exc.value.status_code == 422


@pytest.mark.parametrize(
    "payload,units",
    [
        (b"not a model", "metres"),
        (glb()[:-4], "metres"),
        (glb(external=True), "metres"),
        (glb(0, 9, 20), "metres"),
        (glb(), "furlongs"),
        (glb(float("inf"), 9, 20), "metres"),
    ],
)
def test_rejects_unusable_models_without_storage_or_network(payload, units):
    with pytest.raises(HTTPException) as exc:
        inspect_glb(payload, units)
    assert exc.value.status_code == 422


def test_private_uploaded_source_is_discoverable_at_measured_size():
    building = Building(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        name="My GLB",
        generation_engine="imported_glb",
        model_url="/api/v1/files/projects/p/models/a.glb",
        generation_status="completed",
        height_meters=9,
        specifications={"imported_glb": {"width_m": 12, "depth_m": 20, "height_meters": 9}},
    )
    assert is_user_generated(building)
    entry = generated_entry(building)
    assert (entry["width_m"], entry["depth_m"], entry["size_estimated"], entry["source_kind"]) == (
        12,
        20,
        False,
        "imported_glb",
    )


@pytest.mark.asyncio
async def test_upload_checks_editor_before_reading_or_storing(monkeypatch):
    from app.api.v1 import model_library as api

    denied = AsyncMock(side_effect=HTTPException(403, "Editor required"))
    monkeypatch.setattr(api, "check_project_permission", denied)
    upload = SimpleNamespace(read=AsyncMock(), filename="building.glb")
    with pytest.raises(HTTPException) as exc:
        await api.import_glb(
            uuid.uuid4(), upload, "My GLB", "metres", SimpleNamespace(id=uuid.uuid4()), SimpleNamespace(), None
        )
    assert exc.value.status_code == 403
    upload.read.assert_not_awaited()


@pytest.mark.asyncio
async def test_upload_preserves_bytes_in_protected_project_storage(monkeypatch):
    from app.api.v1 import model_library as api
    from app.services import glb_import

    payload = glb()
    stored = MagicMock()
    monkeypatch.setattr(api, "check_project_permission", AsyncMock())
    monkeypatch.setattr(glb_import, "store_glb", stored)
    db = SimpleNamespace(add=MagicMock(), flush=AsyncMock(), commit=AsyncMock())
    pid = uuid.uuid4()
    result = await api.import_glb(
        pid,
        UploadFile(filename="house.glb", file=BytesIO(payload)),
        "My GLB",
        "metres",
        SimpleNamespace(id=uuid.uuid4()),
        db,
        None,
    )
    assert stored.call_args.args[1] == payload
    assert stored.call_args.args[0].startswith(f"projects/{pid}/models/")
    assert result["name"] == "My GLB" and result["source_kind"] == "imported_glb"
    assert result["model_url"].startswith(f"/api/v1/files/projects/{pid}/models/")
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_storage_failure_does_not_save_a_bogus_model(monkeypatch):
    from app.api.v1 import model_library as api
    from app.services import glb_import

    monkeypatch.setattr(api, "check_project_permission", AsyncMock())
    monkeypatch.setattr(glb_import, "store_glb", MagicMock(side_effect=RuntimeError("offline")))
    db = SimpleNamespace(add=MagicMock(), commit=AsyncMock())
    with pytest.raises(HTTPException) as exc:
        await api.import_glb(
            uuid.uuid4(),
            UploadFile(filename="house.glb", file=BytesIO(glb())),
            "House",
            "metres",
            SimpleNamespace(id=uuid.uuid4()),
            db,
            None,
        )
    assert exc.value.status_code == 503
    db.add.assert_not_called()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_imported_model_attachment_does_not_invent_two_storeys(monkeypatch):
    from app.services import user_generated_models as models

    original = Building(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        name="Import",
        generation_engine="imported_glb",
        generation_status="completed",
        model_url="/api/v1/files/projects/p/models/a.glb",
        height_meters=40,
        specifications={"imported_glb": {"width_m": 12, "depth_m": 14, "height_meters": 40}},
    )
    result = MagicMock()
    result.scalar_one_or_none.return_value = original
    db = SimpleNamespace(execute=AsyncMock(return_value=result), add=MagicMock(), flush=AsyncMock())
    zone = SimpleNamespace(zone_type="building", project_id=uuid.uuid4(), geometry="footprint", properties={})
    monkeypatch.setattr(models, "copy_generated_file", lambda url, key: f"/api/v1/files/{key}")
    await models.attach_generated_model(db, zone, SimpleNamespace(id=uuid.uuid4()), str(original.id))
    assert "floors" not in zone.properties and "floor_count" not in zone.properties
