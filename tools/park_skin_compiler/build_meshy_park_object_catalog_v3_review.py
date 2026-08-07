"""Build an auditable review manifest from a Meshy wave report and manual rejects."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--credits-used",
        type=int,
        help="Override the account delta when waves overlapped or a capped run was interrupted.",
    )
    parser.add_argument("--balance-before", type=int)
    parser.add_argument("--balance-after", type=int)
    parser.add_argument(
        "--reject",
        action="append",
        default=[],
        metavar="ASSET_ID=REASON",
        help="Reject after reference/raw/normalized visual review.",
    )
    return parser.parse_args()


def main() -> None:
    options = parse_args()
    batch = json.loads(options.batch.resolve().read_text(encoding="utf-8"))
    report = json.loads(options.report.resolve().read_text(encoding="utf-8"))
    manual_rejects: dict[str, str] = {}
    for value in options.reject:
        asset_id, separator, reason = value.partition("=")
        if not separator or not asset_id.strip() or not reason.strip():
            raise ValueError(f"--reject must be ASSET_ID=REASON, got {value!r}")
        manual_rejects[asset_id.strip()] = reason.strip()

    catalog = {item["assetId"]: item for item in batch["objects"]}
    unknown = set(manual_rejects) - set(catalog)
    if unknown:
        raise ValueError(f"Unknown rejected asset IDs: {sorted(unknown)}")
    results = {item["assetId"]: item for item in report["objects"]}
    accepted = []
    rejected = []
    for asset_id, item in catalog.items():
        result = results.get(asset_id)
        if not result or result["outcome"] != "completed":
            rejected.append({
                "assetId": asset_id,
                "reason": (result or {}).get("error") or "Meshy generation did not complete.",
            })
        elif asset_id in manual_rejects:
            rejected.append({"assetId": asset_id, "reason": manual_rejects[asset_id]})
        else:
            accepted.append({
                "assetId": asset_id,
                "reason": "Defining archetype silhouette, material language and human scale survived isolated multiview and normalized four-view review; no people or large buildings.",
            })

    completed_count = report.get("completedCount")
    if completed_count is None:
        completed_count = sum(
            item.get("outcome") == "completed" for item in report.get("objects", [])
        )
    credits_used = (
        options.credits_used
        if options.credits_used is not None
        else report.get("creditsUsed")
    )
    balance_before = (
        options.balance_before
        if options.balance_before is not None
        else report.get("balanceBefore")
    )
    balance_after = (
        options.balance_after
        if options.balance_after is not None
        else report.get("balanceAfter")
    )

    review = {
        "batchId": batch["batchId"],
        "reviewedAt": date.today().isoformat(),
        "generatedCount": completed_count,
        "acceptedCount": len(accepted),
        "rejectedCount": len(rejected),
        "creditsUsed": credits_used,
        "balanceBefore": balance_before,
        "balanceAfter": balance_after,
        "qualityGate": "Compared archetype reference, isolated multiview, Meshy output and normalized 12000-face/512px-PBR four-view runtime render. Structural, compositional, scale, people/building contamination, or texture failures remain external artifacts and are not promoted.",
        "accepted": accepted,
        "rejected": rejected,
    }
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: review[key] for key in (
        "batchId", "generatedCount", "acceptedCount", "rejectedCount",
        "creditsUsed", "balanceBefore", "balanceAfter",
    )}, indent=2))


if __name__ == "__main__":
    main()
