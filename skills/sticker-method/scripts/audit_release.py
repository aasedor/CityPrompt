#!/usr/bin/env python3
"""Fail-closed audit for a Sticker Method batch ledger and review packages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def numeric_scores(record: dict[str, Any]) -> tuple[list[float], float | None, int | None]:
    architect = record.get("architect_scores")
    if not isinstance(architect, dict):
        return [], None, None
    hard_stops = architect.get("hard_stops")
    tier_scores = [
        float(value)
        for key, value in architect.items()
        if key not in {"hard_stops", "components", "mean"}
        and isinstance(value, (int, float))
    ]
    mean = architect.get("mean")
    if mean is None and tier_scores:
        mean = sum(tier_scores) / len(tier_scores)
    return tier_scores, float(mean) if mean is not None else None, hard_stops


def approval_scores(path: Path) -> tuple[list[float], float, int]:
    approval = load_json(path)
    if approval.get("status") not in {"pass", "approved_95_plus"}:
        raise ValueError(f"approval is not pass: {path}")
    hard_stops = approval.get("hard_stop_count", approval.get("hard_stops"))
    if isinstance(hard_stops, dict):
        hard_stops = hard_stops.get("count")
    scores = approval.get("scores")
    tier_scores: list[float] = []
    if isinstance(scores, dict):
        for value in scores.values():
            if isinstance(value, dict) and isinstance(value.get("total"), (int, float)):
                tier_scores.append(float(value["total"]))
    mean = approval.get("mean_score_unrounded")
    if mean is None and tier_scores:
        mean = sum(tier_scores) / len(tier_scores)
    if not tier_scores or not isinstance(mean, (int, float)) or not isinstance(hard_stops, int):
        raise ValueError(f"approval lacks exact scores or hard stops: {path}")
    return tier_scores, float(mean), hard_stops


def audit(repo: Path, batch_path: Path, review_root: Path) -> dict[str, Any]:
    batch = load_json(batch_path)
    buildings = batch.get("buildings")
    if not isinstance(buildings, list) or not buildings:
        raise ValueError("batch buildings must be a non-empty list")

    policy = batch.get("policy") if isinstance(batch.get("policy"), dict) else {}
    expected_count = policy.get("building_count", len(buildings))
    minimum = float(policy.get("minimum_tier_score", 95.0))
    if len(buildings) != expected_count:
        raise ValueError(f"expected {expected_count} buildings, found {len(buildings)}")

    results: list[dict[str, Any]] = []
    for building in buildings:
        if not isinstance(building, dict):
            raise ValueError("building entry must be an object")
        order = building.get("order")
        if building.get("status") != "approved_95_plus":
            raise ValueError(f"order {order} is not approved_95_plus")

        review_value = building.get("review_path")
        if not isinstance(review_value, str):
            matches: list[Path] = []
            needles = {str(building.get("archetype_id", "")), str(building.get("variant_id", ""))}
            needles.discard("")
            for candidate in review_root.iterdir():
                if not candidate.is_dir():
                    continue
                texts = []
                for json_path in candidate.glob("*.json"):
                    try:
                        texts.append(json_path.read_text(encoding="utf-8"))
                    except OSError:
                        continue
                if any(needle in text for needle in needles for text in texts):
                    matches.append(candidate)
            if len(matches) != 1:
                raise ValueError(f"order {order} lacks an unambiguous review_path")
            review_dir = matches[0]
        else:
            review_dir = repo / review_value

        machine = review_dir / "machine-evidence.json"
        if not machine.is_file():
            raise ValueError(f"missing machine evidence for order {order}: {machine}")

        tier_scores, mean, hard_stops = numeric_scores(building)
        approval = review_dir / "visual-approval.json"
        if not tier_scores or mean is None or hard_stops is None:
            if not approval.is_file():
                raise ValueError(f"missing visual approval for order {order}: {approval}")
            tier_scores, mean, hard_stops = approval_scores(approval)

        if hard_stops != 0:
            raise ValueError(f"order {order} has {hard_stops} hard stops")
        if min(tier_scores) < minimum:
            raise ValueError(f"order {order} tier score below {minimum}: {tier_scores}")
        if len(tier_scores) > 1 and mean <= 95.0:
            raise ValueError(f"order {order} mean is not strictly above 95: {mean}")
        if len(tier_scores) == 1 and mean < minimum:
            raise ValueError(f"order {order} fixed score below {minimum}: {mean}")

        results.append(
            {
                "order": order,
                "variant_id": building.get("variant_id"),
                "tier_scores": tier_scores,
                "mean": mean,
                "hard_stops": hard_stops,
                "review_path": str(review_dir.relative_to(repo)).replace("\\", "/"),
            }
        )

    return {"status": "pass", "building_count": len(results), "buildings": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--batch", type=Path)
    parser.add_argument("--review-root", type=Path)
    args = parser.parse_args()

    repo = args.repo.resolve()
    batch = (args.batch or repo / "tools/archetype_compiler/sticker_method_batch_01.json").resolve()
    review_root = (
        args.review_root
        or repo / "docs/reviews/catalogue-rollout-v98/sticker-method-batch-01"
    ).resolve()
    try:
        result = audit(repo, batch, review_root)
    except ValueError as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
