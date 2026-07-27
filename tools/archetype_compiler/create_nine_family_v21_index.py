"""Consolidate the two pilot batches into one City Prompt import index."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "build" / "codex-lego-nine-family-v21" / "worldclass-library-index.json"

FAMILIES = [
    ("collegiate_gothic_education", "collegiate-gothic-education", ROOT / "build/codex-lego-four-family-v20/families/collegiate-gothic-education"),
    ("modern_glass_office_institutional", "modern-glass-office-institutional", ROOT / "build/codex-lego-four-family-v20/families/modern-glass-office-institutional"),
    ("nordic_timber_midrise", "nordic-timber-midrise", ROOT / "build/codex-lego-four-family-v20/families/nordic-timber-midrise"),
    ("civic_classical_building", "civic-classical-building", ROOT / "build/codex-lego-four-family-v20/families/civic-classical-building"),
    ("london_heritage_mansion_block", "london-heritage-mansion-block", ROOT / "build/codex-lego-five-family-v21/london-heritage-mansion-block"),
    ("industrial_brick_mixed_use", "industrial-brick-mixed-use", ROOT / "build/codex-lego-five-family-v21r/industrial-brick-mixed-use"),
    ("eixample_apartment_block", "eixample-apartment-block", ROOT / "build/codex-lego-five-family-v21r/eixample-apartment-block"),
    ("modernist_civic_block", "modernist-civic-block", ROOT / "build/codex-lego-five-family-v21/modernist-civic-block"),
    ("chateauesque_grand_railway_hotel", "chateauesque-grand-railway-hotel", ROOT / "build/codex-lego-five-family-v21r/chateauesque-grand-railway-hotel"),
]


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    families = []
    for archetype_id, slug, directory in FAMILIES:
        manifest_path = directory / f"{slug}_manifest.json"
        assessment_path = directory / "quality_assessment.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assessment = json.loads(assessment_path.read_text(encoding="utf-8"))
        assembled = manifest["assembled"]
        entry = {
            "archetype_id": archetype_id,
            "family": slug,
            "output_directory": relative(directory),
            "manifest": relative(manifest_path),
            "assembled": relative(directory / assembled["filename"]),
            "preview": relative(directory / f"{slug}_preview.png"),
            "triangle_count": assembled["triangle_count"],
            "floors": assembled["floors"],
            "footprint_target": assembled["footprint_target"],
            "validation": "pass",
            "city_prompt_ready": bool(assessment.get("high_quality_ready")),
            "quality_status": assessment["status"],
            "quality_memory_version": assessment["memory_version"],
        }
        ktx_manifest_path = directory / "ktx2" / f"{slug}_manifest.json"
        if ktx_manifest_path.exists():
            ktx_manifest = json.loads(ktx_manifest_path.read_text(encoding="utf-8"))
            entry["ktx2_manifest"] = relative(ktx_manifest_path)
            entry["ktx2_modules"] = [
                relative(ktx_manifest_path.parent / module["filename"])
                for module in ktx_manifest.get("modules", [])
            ]
            entry["texture_delivery"] = ktx_manifest.get("texture_delivery")
        families.append(entry)

    payload = {
        "schema": "worldclass-lego-build-index@1",
        "library": "Codex LEGO v21 - Nine-Family Methodology Validation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "quality_memory_version": "2026-07-18-nine-family-v21",
        "city_prompt_ready_count": sum(item["city_prompt_ready"] for item in families),
        "families": families,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
