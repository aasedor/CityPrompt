"""Run a finite, credit-capped Meshy park-object batch with failure isolation.

The batch file is declarative and reviewed in Git. Heavy raw outputs are kept
outside the repository. Every object still uses the proven single-object
multi-view -> Multi-Image-to-3D path, while this wrapper bounds concurrency,
checks the account balance, and writes a durable batch report.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from generate_meshy_park_object_pilot import _load_backend_client, generate


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch",
        default=str(Path(__file__).with_name("meshy_park_object_batch_v1.json")),
    )
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--max-credits", type=int, default=7000)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--target-polycount", type=int, default=24_000)
    parser.add_argument("--hd-texture", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_batch(path: Path, only: set[str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    batch = json.loads(path.read_text(encoding="utf-8"))
    objects = batch.get("objects")
    if not isinstance(objects, list) or not objects:
        raise ValueError("Batch must contain a non-empty objects array")
    ids = [item.get("assetId") for item in objects]
    if len(ids) != len(set(ids)) or any(not value for value in ids):
        raise ValueError("Every object needs a unique assetId")
    selected = [item for item in objects if not only or item["assetId"] in only]
    missing = sorted(only - {item["assetId"] for item in selected})
    if missing:
        raise ValueError(f"Unknown --only asset IDs: {missing}")
    return batch, selected


async def account_balance() -> int | None:
    client_type = _load_backend_client()
    response = await client_type().get_balance()
    return response.get("balance") if isinstance(response.get("balance"), int) else None


async def run(args: argparse.Namespace) -> None:
    batch_path = Path(args.batch).resolve()
    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    batch, selected = load_batch(batch_path, set(args.only))
    batch_ceiling = int(batch.get("creditCeiling", args.max_credits))
    effective_ceiling = min(args.max_credits, batch_ceiling)
    estimated_each = int(batch.get("estimatedCreditsPerAsset", 45))
    estimated_total = len(selected) * estimated_each
    if estimated_total > effective_ceiling:
        raise ValueError(
            f"Estimated spend {estimated_total} exceeds credit ceiling {effective_ceiling}"
        )
    if args.concurrency < 1 or args.concurrency > 3:
        raise ValueError("Concurrency must be between 1 and 3")

    balance_before = None if args.dry_run else await account_balance()
    if balance_before is not None and balance_before < estimated_total:
        raise RuntimeError(
            f"Meshy balance {balance_before} is below estimated batch spend {estimated_total}"
        )

    semaphore = asyncio.Semaphore(args.concurrency)
    results: list[dict[str, Any]] = []
    results_lock = asyncio.Lock()

    async def one(index: int, item: dict[str, Any]) -> None:
        async with semaphore:
            # Stagger the initial API request when multiple workers become ready.
            if index:
                await asyncio.sleep((index % args.concurrency) * 4)
            asset_id = item["assetId"]
            destination = output_root / asset_id
            references = [str(repo_root() / value) for value in item["references"]]
            namespace = Namespace(
                asset_id=asset_id,
                reference=references,
                output_dir=str(destination),
                multiview_prompt=item["multiviewPrompt"],
                texture_prompt=item["texturePrompt"],
                target_polycount=args.target_polycount,
                hd_texture=args.hd_texture,
                poll_interval=10,
                multiview_timeout=900,
                model_timeout=2400,
                dry_run=args.dry_run,
            )
            started = datetime.now(timezone.utc)
            try:
                await generate(namespace)
                outcome = "dry-run" if args.dry_run else "completed"
                error = None
            except Exception as exc:  # isolate paid-task failures from the rest of the finite batch
                outcome = "failed"
                error = f"{type(exc).__name__}: {exc}"
            entry = {
                "assetId": asset_id,
                "family": item["family"],
                "dimensionsM": item["dimensionsM"],
                "orientation": item["orientation"],
                "placementRole": item["placementRole"],
                "outcome": outcome,
                "error": error,
                "outputDir": str(destination),
                "startedAt": started.isoformat(),
                "finishedAt": datetime.now(timezone.utc).isoformat(),
            }
            async with results_lock:
                results.append(entry)
                checkpoint = {
                    "batchId": batch["batchId"],
                    "balanceBefore": balance_before,
                    "estimatedCredits": estimated_total,
                    "creditCeiling": effective_ceiling,
                    "objects": sorted(results, key=lambda value: value["assetId"]),
                }
                (output_root / "batch-checkpoint.json").write_text(
                    json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8"
                )

    await asyncio.gather(*(one(index, item) for index, item in enumerate(selected)))
    balance_after = None if args.dry_run else await account_balance()
    report = {
        "batchId": batch["batchId"],
        "batchFile": str(batch_path),
        "dryRun": args.dry_run,
        "selectedCount": len(selected),
        "completedCount": sum(item["outcome"] == "completed" for item in results),
        "failedCount": sum(item["outcome"] == "failed" for item in results),
        "estimatedCredits": estimated_total,
        "creditCeiling": effective_ceiling,
        "balanceBefore": balance_before,
        "balanceAfter": balance_after,
        "creditsUsed": (
            balance_before - balance_after
            if isinstance(balance_before, int) and isinstance(balance_after, int)
            else 0 if args.dry_run else None
        ),
        "objects": sorted(results, key=lambda value: value["assetId"]),
    }
    (output_root / "batch-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    if report["failedCount"]:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run(parse_args()))
