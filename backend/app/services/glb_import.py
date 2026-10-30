"""Bounded, self-contained student GLB imports. Never fetch external resources."""

import hashlib
from io import BytesIO
import json
import math
import struct

import boto3
from botocore.config import Config
from fastapi import HTTPException

from app.core.config import get_settings

MAX_GLB_BYTES = 50 * 1024 * 1024
UNIT_SCALE = {"metres": 1, "centimetres": 0.01, "millimetres": 0.001, "feet": 0.3048}


def inspect_glb(
    payload: bytes, units: str, target_height_m: float | None = None, *, max_upload_bytes: int = MAX_GLB_BYTES
) -> dict:
    """Measure the default scene without changing its original buffers/materials."""

    def invalid(message):
        raise HTTPException(422, message)

    if units not in UNIT_SCALE:
        invalid("Choose metres, centimetres, millimetres or feet for the model units.")
    if target_height_m is not None and (not math.isfinite(target_height_m) or not 0.25 <= target_height_m <= 500):
        invalid("Choose a building height between 0.25 and 500 m.")
    if len(payload) > max_upload_bytes:
        raise HTTPException(413, f"Choose a GLB smaller than {max_upload_bytes // (1024 * 1024)} MB.")
    if len(payload) < 20 or payload[:4] != b"glTF":
        invalid("This is not a GLB file. Export your building as a self-contained GLB 2.0 file.")
    _, version, length = struct.unpack_from("<4sII", payload)
    if version != 2 or length != len(payload):
        invalid("The GLB is incomplete or unsupported. Export it again as GLB 2.0.")
    chunk_length, chunk_type = struct.unpack_from("<II", payload, 12)
    if chunk_type != 0x4E4F534A or chunk_length % 4 or 20 + chunk_length > len(payload):
        invalid("The GLB scene description is invalid.")
    try:
        doc = json.loads(payload[20 : 20 + chunk_length])

        def check_resources(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == "uri" and (not isinstance(item, str) or not item.startswith("data:")):
                        invalid(
                            "This model refers to separate files. Export a GLB with all textures and geometry embedded."
                        )
                    check_resources(item)
            elif isinstance(value, list):
                for item in value:
                    check_resources(item)

        check_resources(doc)
        if not isinstance(doc, dict) or doc.get("asset", {}).get("version") != "2.0":
            invalid("Export your building as a GLB 2.0 file.")
        from app.services.glb_import_resources import validate_glb_resources

        validate_glb_resources(doc, payload, 20 + chunk_length)
        import numpy as np
        import trimesh

        scene = trimesh.load(BytesIO(payload), file_type="glb", force="scene", process=False, skip_materials=True)
        triangles = sum(len(scene.geometry[scene.graph[node][1]].faces) for node in scene.graph.nodes_geometry)
        bounds = scene.bounds
        if triangles < 1 or bounds is None or not np.isfinite(bounds).all():
            invalid("The GLB has no usable building geometry.")
        size = (bounds[1] - bounds[0]) * UNIT_SCALE[units]
        if target_height_m is not None:
            if size[1] <= 0:
                invalid("The GLB has no usable building height.")
            size *= target_height_m / size[1]
        width, depth = sorted((float(size[0]), float(size[2])))
        height = float(size[1])
        if not all(math.isfinite(dimension) and dimension > 0 for dimension in (width, depth, height)):
            invalid("The GLB must have finite, non-zero width, depth and height. Check its geometry and units.")
        # Preserve the author's native scale. Plot fit belongs to placement;
        # import must also support small objects and normalized Meshy exports.
        return {
            "version": 1,
            "units": units,
            "target_height_m": target_height_m,
            "width_m": width,
            "depth_m": depth,
            "height_meters": height,
            "triangles": triangles,
            "source_sha256": hashlib.sha256(payload).hexdigest(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            422,
            "The GLB could not be read. Export a static GLB 2.0 with embedded textures and standard triangle meshes.",
        ) from exc


def store_glb(key: str, payload: bytes) -> None:
    settings = get_settings()
    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )
    client.put_object(Bucket=settings.s3_bucket_name, Key=key, Body=payload, ContentType="model/gltf-binary")
