"""Run the finite, no-API geometry-evidence pass for the v75 museum pilot.

The script intentionally stops after three reference views and an evidence
contract. Learned proxy meshes are never copied into the production model.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import cv2
import numpy as np


REPO = Path(__file__).resolve().parents[2]
REFERENCE = REPO / "frontend/public/archetypes/buildings/large-art-museum-gallery"
CONTRACT = Path(__file__).with_name("reference_fidelity_contracts") / "titanium_museum_sam_ab_v74.json"


def run(command: list[str], env: dict[str, str] | None = None) -> None:
    print(subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, check=True, env=env)


def audited_mask(image_path: Path, output: Path) -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    polygon = next(view for view in contract["views"] if view["role"] == "street_identity")[
        "reference_silhouette_polygon"
    ]
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read {image_path}")
    height, width = image.shape[:2]
    points = np.array([[round(x * width), round(y * height)] for x, y in polygon], np.int32)
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    cv2.imwrite(str(output), mask)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO / "artifacts/archetype-geometry-pass-v75")
    parser.add_argument("--moge", default="moge", help="MoGe CLI executable from the isolated model environment")
    parser.add_argument("--da3", default="da3", help="DA3 CLI executable from the isolated model environment")
    args = parser.parse_args()

    root = args.output.resolve()
    inputs = root / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    source_images = [
        REFERENCE / "variant_0.png",
        REFERENCE / "variant_0_angle_60.jpg",
        REFERENCE / "variant_0_angle_90.jpg",
    ]
    input_images = [inputs / "01-street.png", inputs / "02-oblique.jpg", inputs / "03-roof.jpg"]
    for source, destination in zip(source_images, input_images):
        shutil.copy2(source, destination)
    discovered = {
        path.resolve() for path in inputs.iterdir()
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    }
    expected = {path.resolve() for path in input_images}
    if discovered != expected:
        unexpected = sorted(str(path) for path in discovered - expected)
        raise RuntimeError(f"Bounded pass requires exactly three input views; remove or relocate: {unexpected}")
    mask = root / "01-street-mask.png"
    audited_mask(input_images[0], mask)

    run([
        args.moge, "infer", "-i", str(input_images[0]), "-o", str(root / "moge"),
        "--pretrained", "Ruicheng/moge-2-vits-normal", "--version", "v2", "--device", "cuda",
        "--fp16", "--resize", "768", "--num_tokens", "1200", "--threshold", "0.008", "--maps", "--glb",
    ])
    utf8_env = dict(os.environ, PYTHONUTF8="1")
    run([
        args.da3, "auto", str(inputs), "--model-dir", "depth-anything/DA3-BASE",
        "--export-dir", str(root / "da3"), "--export-format", "npz-glb", "--device", "cuda",
        "--process-res", "420", "--process-res-method", "upper_bound_resize", "--ref-view-strategy", "first",
        "--conf-thresh-percentile", "35", "--num-max-points", "300000", "--no-show-cameras",
    ], env=utf8_env)

    moge = root / "moge/01-street"
    run([
        sys.executable, str(Path(__file__).with_name("archetype_geometry_pass.py")),
        "--archetype-id", "large_art_museum_gallery", "--variant-id", "deconstructivist_titanium_pavilion",
        "--street-image", str(input_images[0]), "--oblique-image", str(input_images[1]), "--roof-image", str(input_images[2]),
        "--street-mask", str(mask), "--moge-depth", str(moge / "depth.exr"), "--moge-mask", str(moge / "mask.png"),
        "--moge-normal", str(moge / "normal.png"), "--moge-glb", str(moge / "mesh.glb"),
        "--da3-npz", str(root / "da3/exports/npz/results.npz"), "--da3-glb", str(root / "da3/scene.glb"),
        "--contract", str(CONTRACT), "--width-m", "80", "--depth-m", "60", "--height-m", "30",
        "--output-dir", str(root / "evidence"),
    ])


if __name__ == "__main__":
    main()
