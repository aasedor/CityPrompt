"""Extract immutable curb-bulb placement evidence, never regenerate model geometry."""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_SHA256 = "12524be5dba5d9db363a7cf764052b747f48875d8682053ba200f90d047c6354"


def extract(source: Path, destination: Path) -> None:
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Unapproved footprint bytes; resolve source authority before importing")
    footprints = json.loads(raw)
    if len(footprints) != 12:
        raise ValueError("Expected the 12 independently audited standard curb bulbs")
    result = {
        "sourceSha256": SOURCE_SHA256,
        "coordinates": "metres, local East/North; original theoretical curb-intersection or midblock attachment pivot",
        "contracts": {
            key: {
                "polygon": value["polygon"],
                "attachment": value["attachment"],
                "parameters": value["parameters"],
            }
            for key, value in sorted(footprints.items())
        },
    }
    destination.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    extract(args.source, args.destination)
