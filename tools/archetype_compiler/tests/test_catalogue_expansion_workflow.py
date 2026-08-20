"""Regression coverage for review and durable seed promotion."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest
from PIL import Image

import approve_family_review
import create_wave14_comparison_sheets


REPO = Path(__file__).resolve().parents[3]
PROMOTION_PATH = REPO / "tools" / "promote_compiled_families_to_seed.py"
SPEC = importlib.util.spec_from_file_location(
    "promote_compiled_families_to_seed", PROMOTION_PATH
)
assert SPEC and SPEC.loader
promotion = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = promotion
SPEC.loader.exec_module(promotion)

SEED_COLUMNS = [
    "id",
    "owner_id",
    "source_building_id",
    "source_project_id",
    "name",
    "description",
    "category",
    "tags",
    "model_url",
    "lod_urls",
    "thumbnail_url",
    "generation_prompt",
    "generation_engine",
    "architectural_style",
    "is_public",
    "use_count",
    "metadata",
    "created_at",
]


def write_image(path: Path, size: tuple[int, int] = (128, 128)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", size)
    pixels = image.load()
    for y in range(size[1]):
        for x in range(size[0]):
            pixels[x, y] = ((x * 7) % 255, (y * 11) % 255, ((x + y) * 13) % 255)
    image.save(path)


def write_family(tmp_path: Path, *, quality_status: str = "pass") -> Path:
    family = "test-review-family"
    root = tmp_path / family
    root.mkdir()
    (root / f"{family}_podium.glb").write_bytes(b"glTF" + b"\0" * 252)
    (root / f"{family}_assembled.glb").write_bytes(b"glTF" + b"\1" * 252)
    write_image(root / f"{family}_preview.png")
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {"name": "test-generator", "version": "1.0.0"},
        "created_at": "2026-08-19T00:00:00+00:00",
        "family": family,
        "archetype_id": "test_archetype",
        "archetype_label": "Test Review Family",
        "variant_id": "test_variant",
        "generation_archetype_id": "test_variant",
        "archetype_aliases": ["test_archetype", "test_variant"],
        "aesthetic_category_id": "test_style",
        "reuse_keys": ["test_variant", "test reuse"],
        "coordinate_contract": {
            "origin": "bottom centre",
            "gltf_up": "+Y (export_yup)",
        },
        "footprint_compatibility": {"preferredProfiles": ["rectangle"]},
        "placement_contract": {},
        "massing_graph": {"type": "fixed_test"},
        "dimensions": {
            "width_m": 10.0,
            "depth_m": 8.0,
            "height_m": 6.0,
            "floor_height_m": 3.0,
        },
        "modules": [
            {
                "role": "podium",
                "variant_key": "default",
                "lod": 0,
                "filename": f"{family}_podium.glb",
                "width_m": 10.0,
                "depth_m": 8.0,
                "height_m": 3.0,
                "floor_height_m": 3.0,
                "repeatable_z": False,
                "triangle_count": 12,
                "material_count": 1,
                "allow_inset_footprint": True,
            }
        ],
        "assembled": {
            "filename": f"{family}_assembled.glb",
            "width_m": 10.0,
            "depth_m": 8.0,
            "height_m": 6.0,
            "floors": 2,
            "triangle_count": 24,
            "material_count": 1,
        },
        "thumbnail": f"{family}_preview.png",
    }
    manifest_path = root / f"{family}_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    validation = root / "validation_report.json"
    validation.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
    quality = root / "quality_assessment.json"
    quality.write_text(
        json.dumps(
            {
                "memory_version": promotion.current_memory_version(),
                "status": quality_status,
                "high_quality_ready": quality_status == "pass",
                "hard_failures": [],
                "review_findings": []
                if quality_status == "pass"
                else [{"id": "approval"}],
            }
        ),
        encoding="utf-8",
    )
    base = 1_700_000_000_000_000_000
    os.utime(manifest_path, ns=(base, base))
    os.utime(validation, ns=(base + 1_000, base + 1_000))
    os.utime(quality, ns=(base + 2_000, base + 2_000))
    return root


def write_seed(tmp_path: Path) -> Path:
    seed = tmp_path / "seed"
    seed.mkdir()
    (seed / "model_library.json").write_text(
        json.dumps(
            {"table": "model_library", "count": 0, "columns": SEED_COLUMNS, "rows": []}
        ),
        encoding="utf-8",
    )
    return seed


def test_seed_promotion_is_dry_run_by_default_and_idempotent(tmp_path: Path) -> None:
    family = write_family(tmp_path)
    seed = write_seed(tmp_path)

    dry_run = promotion.promote([family], seed_dir=seed)
    assert dry_run["rows_added"] == 2
    assert dry_run["objects_planned"] == 3
    assert json.loads((seed / "model_library.json").read_text())["count"] == 0

    applied = promotion.promote([family], seed_dir=seed, apply=True)
    assert applied["rows_after"] == 2
    assert applied["objects_changed"] == 3
    payload = json.loads((seed / "model_library.json").read_text())
    assert payload["count"] == 2
    identities = {
        (
            row["metadata"]["lego"]["family"],
            row["metadata"]["lego"]["role"],
            row["metadata"]["lego"]["variant_key"],
        )
        for row in payload["rows"]
    }
    assert identities == {
        ("test-review-family", "podium", "default"),
        ("test-review-family", "assembled", "default"),
    }

    repeated = promotion.promote([family], seed_dir=seed, apply=True)
    assert repeated["rows_added"] == 0
    assert repeated["rows_updated"] == 2
    assert repeated["objects_changed"] == 0
    assert json.loads((seed / "model_library.json").read_text())["count"] == 2


def test_seed_promotion_fails_closed_on_unapproved_quality(tmp_path: Path) -> None:
    family = write_family(tmp_path, quality_status="review")
    seed = write_seed(tmp_path)
    with pytest.raises(ValueError, match="not approved and ready"):
        promotion.promote([family], seed_dir=seed)


def test_seed_promotion_rejects_lfs_pointer(tmp_path: Path) -> None:
    family = write_family(tmp_path)
    seed = write_seed(tmp_path)
    (family / "test-review-family_podium.glb").write_text(
        "version https://git-lfs.github.com/spec/v1\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Git LFS pointer"):
        promotion.promote([family], seed_dir=seed)


def test_visual_approval_requires_every_locked_view_and_is_dry_run(
    tmp_path: Path,
) -> None:
    family = "reviewed-family"
    root = tmp_path / family
    root.mkdir()
    evidence = {
        "comparison_views": list(approve_family_review.REQUIRED_VIEWS),
        "comparison_sheet": f"{family}_comparison.jpg",
        "photoreal_skin_approved": False,
        "human_visual_approval": False,
    }
    manifest_path = root / f"{family}_manifest.json"
    manifest_path.write_text(
        json.dumps({"family": family, "quality_standard_evidence": evidence}),
        encoding="utf-8",
    )
    for view in approve_family_review.REQUIRED_VIEWS:
        write_image(root / f"{family}_{view}.png")
    write_image(root / f"{family}_comparison.jpg")

    approve_family_review.approve_manifest(manifest_path, reviewer="Drew", apply=False)
    assert (
        json.loads(manifest_path.read_text())["quality_standard_evidence"][
            "human_visual_approval"
        ]
        is False
    )
    approved = approve_family_review.approve_manifest(
        manifest_path, reviewer="Drew", apply=True
    )
    assert approved["quality_standard_evidence"]["human_visual_approval"] is True
    assert approved["quality_standard_evidence"]["photoreal_skin_approved"] is True
    assert approved["quality_standard_evidence"]["human_visual_reviewer"] == "Drew"

    (root / f"{family}_street.png").unlink()
    with pytest.raises(ValueError, match="comparison view is missing"):
        approve_family_review.approve_manifest(manifest_path, reviewer="Drew")


def test_wave14_comparison_sheet_supports_external_artifact_root(
    tmp_path: Path,
) -> None:
    family = "red-machiya-cafe-gallery"
    root = tmp_path / family
    source = root / "textures" / "source"
    for name in (
        "street-hero-source-v1.png",
        "front-elevation-source-v1.png",
        "aerial-roof-source-v1.png",
        "rear-corner-source-v1.png",
        "material-construction-source-v1.png",
    ):
        write_image(source / name)
    for role in (
        "preview",
        "front_elevation",
        "aerial",
        "rear_corner_oblique",
        "facade_close",
    ):
        write_image(root / f"{family}_{role}.png")

    destination = create_wave14_comparison_sheets.create_sheet(family, tmp_path)
    assert destination == root / f"{family}_comparison.jpg"
    assert destination.is_file()
    assert (tmp_path / f"wave14-{family}-comparison.jpg").is_file()
