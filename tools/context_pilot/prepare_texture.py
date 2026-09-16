"""Bounded texture derivative of one licensed context test fixture, not an importer.

Use the backend Python environment (Pillow is already available). The source and
output must be outside the source tree. The original scan is never overwritten.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct

from PIL import Image

SOURCE_SHA256 = "6c712d16b9ede8f5083d7fc82787cf75b913865b157f48db08a61f2154c6bd73"


def prepare(source: Path, output: Path) -> dict:
    source, output = source.resolve(), output.resolve()
    repository = Path(__file__).resolve().parents[2]
    if source == output or source.is_relative_to(repository) or output.is_relative_to(repository):
        raise ValueError("Keep original and derived samples separate and outside the source tree")
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError("This pilot only supports the pinned, reviewed flat-roof sample")
    magic, version, total = struct.unpack_from("<4sII", data)
    json_size, json_type = struct.unpack_from("<II", data, 12)
    assert magic == b"glTF" and version == 2 and total == len(data) and json_type == 0x4E4F534A
    document = json.loads(data[20:20 + json_size])
    bin_size, bin_type = struct.unpack_from("<II", data, 20 + json_size)
    binary = data[28 + json_size:]
    assert bin_type == 0x004E4942 and len(binary) == bin_size
    views = document["bufferViews"]
    assert len(views) == 2 and document["images"] == [{"mimeType": "image/jpeg", "bufferView": 0}]
    assert views[0]["byteOffset"] == 0 and views[1]["byteOffset"] % 4 == 0
    geometry_bytes = binary[views[1]["byteOffset"]:views[1]["byteOffset"] + views[1]["byteLength"]]
    image = Image.open(io.BytesIO(binary[:views[0]["byteLength"]]))
    assert image.size == (8192, 8192)
    resized = image.resize((2048, 2048), Image.Resampling.LANCZOS)
    encoded = io.BytesIO()
    resized.save(encoded, format="JPEG", quality=90, optimize=True)
    jpeg = encoded.getvalue()
    new_binary = jpeg + b"\0" * (-len(jpeg) % 4) + geometry_bytes
    views[0]["byteLength"] = len(jpeg)
    views[1]["byteOffset"] = len(jpeg) + (-len(jpeg) % 4)
    document["buffers"][0]["byteLength"] = len(new_binary)
    metadata = json.dumps(document, separators=(",", ":")).encode("utf-8")
    metadata += b" " * (-len(metadata) % 4)
    new_binary += b"\0" * (-len(new_binary) % 4)
    assert new_binary[views[1]["byteOffset"]:views[1]["byteOffset"] + views[1]["byteLength"]] == geometry_bytes
    result = (struct.pack("<4sII", b"glTF", 2, 28 + len(metadata) + len(new_binary))
              + struct.pack("<II", len(metadata), json_type) + metadata
              + struct.pack("<II", len(new_binary), bin_type) + new_binary)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(result)
    provenance = {
        "source": "https://huggingface.co/datasets/Matt1up/drone-building-scans/tree/fde325fbd1d3636ffcf5d48aedc24cdbfc9a630f",
        "attribution": "Drone Building Scans — Matthew Guertin, 2026. CC BY 4.0.",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "modification": "JPEG texture resized 8192 to 2048 pixels with Lanczos, quality 90. Geometry and scene transforms unchanged.",
        "source_sha256": SOURCE_SHA256, "derived_sha256": hashlib.sha256(result).hexdigest(),
        "source_bytes": len(data), "derived_bytes": len(result),
        "draco_geometry_sha256": hashlib.sha256(geometry_bytes).hexdigest(),
        "approx_rgba_mips_before_bytes": round(8192 ** 2 * 4 * 4 / 3),
        "approx_rgba_mips_after_bytes": round(2048 ** 2 * 4 * 4 / 3),
    }
    output.with_suffix(".provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return provenance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.output), indent=2))
