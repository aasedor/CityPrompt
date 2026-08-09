"""Create one fixed-building Meshy pilot from an existing catalogue reference."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import mimetypes
import sys
from pathlib import Path

import httpx
from dotenv import dotenv_values


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def safe_task_summary(payload: dict) -> dict:
    return {
        "id": payload.get("id") or payload.get("task_id") or payload.get("result"),
        "status": payload.get("status"),
        "progress": payload.get("progress"),
        "created_at": payload.get("created_at"),
        "started_at": payload.get("started_at"),
        "finished_at": payload.get("finished_at"),
        "task_error": payload.get("task_error"),
        "triangle_count": payload.get("triangle_count"),
        "credit_balance": payload.get("credit_balance"),
    }


async def download(url: str, path: Path) -> None:
    async with httpx.AsyncClient(timeout=180.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        path.write_bytes(response.content)


async def main(args) -> None:
    backend_root = args.repo_root / "backend"
    sys.path.insert(0, str(backend_root))
    from app.generation.meshy_client import MeshyClient

    env = dotenv_values(args.env_file)
    key = env.get("MESHY_API_KEY")
    if not key:
        raise SystemExit(f"MESHY_API_KEY is missing from {args.env_file}")

    args.output.mkdir(parents=True, exist_ok=True)
    client = MeshyClient(api_key=key)
    before_payload = await client.get_balance()
    before = int(before_payload.get("balance", 0))
    if before <= args.min_balance + args.estimated_credits:
        raise SystemExit(
            f"Meshy balance {before} is too close to the {args.min_balance} credit floor "
            f"for an estimated {args.estimated_credits}-credit pilot"
        )

    plan = {
        "pipeline": "meshy_image_to_image_multiview_then_multi_image_to_3d",
        "reference": str(args.reference),
        "target_dimensions_m": [40.0, 20.0, 12.5],
        "target_polycount": args.target_polycount,
        "balance_before": before,
        "minimum_balance_floor": args.min_balance,
        "estimated_credits": args.estimated_credits,
        "modular": False,
    }
    (args.output / "meshy_plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(json.dumps(plan, indent=2), flush=True)
    if args.dry_run:
        print("dry-run complete; no Meshy generation started", flush=True)
        return

    prompt = (
        "Create three mutually consistent turntable views of exactly the same two-storey adaptive-reuse "
        "brick warehouse shown in the reference. Preserve its long rectangular mass, eight-bay street "
        "facade, tall bronzed factory windows, recessed central entrance, preserved timber loading dock, "
        "dark standing-seam pitched roof and rooflights. Show the complete building alone from front-left, "
        "rear-right and high oblique views on a plain neutral studio ground. Remove trees, streets, vehicles, "
        "people and neighbouring buildings. Do not crop the building and do not add extensions."
    )
    i2i_id = await client.image_to_image_multiview([data_uri(args.reference)], prompt)
    print(f"Meshy multiview task started: {i2i_id}", flush=True)
    i2i = await client.poll_until_done(i2i_id, timeout=900, poll_interval=10, task_type="image_to_image")
    (args.output / "meshy_multiview_task.json").write_text(
        json.dumps(safe_task_summary(i2i), indent=2), encoding="utf-8"
    )
    for index, url in enumerate(i2i.get("image_urls") or []):
        await download(url, args.output / f"meshy_input_view_{index + 1}.png")
    print("Meshy multiview synthesis complete", flush=True)

    texture_prompt = (
        "Photoreal adaptive-reuse architecture: aged red brick with lime mortar, bronzed steel factory "
        "window frames, warm occupied loft interiors, reclaimed timber loading dock, dark charcoal standing-"
        "seam roof. Keep brick, glass, timber and metal physically distinct; no text, trees, people or ground."
    )
    model_id = await client.multi_image_to_3d(
        input_task_id=i2i_id,
        texture_prompt=texture_prompt,
        enable_pbr=True,
        target_polycount=args.target_polycount,
        should_remesh=True,
        topology="triangle",
        ai_model="meshy-6",
        image_enhancement=False,
        remove_lighting=True,
        hd_texture=True,
    )
    print(f"Meshy 3D task started: {model_id}", flush=True)
    model = await client.poll_until_done(model_id, timeout=1200, poll_interval=10, task_type="multi_image")
    urls = model.get("model_urls") or {}
    glb_url = urls.get("glb") or model.get("model_url")
    if not glb_url:
        raise RuntimeError(f"Meshy task {model_id} succeeded without a GLB URL")
    raw_glb = args.output / "adaptive_warehouse_meshy_raw.glb"
    await download(glb_url, raw_glb)

    after_payload = await client.get_balance()
    after = int(after_payload.get("balance", 0))
    summary = safe_task_summary(model)
    summary.update(
        {
            "pipeline": plan["pipeline"],
            "multiview_task_id": i2i_id,
            "model_task_id": model_id,
            "glb": raw_glb.name,
            "glb_bytes": raw_glb.stat().st_size,
            "balance_before": before,
            "balance_after": after,
            "credits_used": before - after,
        }
    )
    (args.output / "meshy_model_task.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-polycount", type=int, default=30000)
    parser.add_argument("--min-balance", type=int, default=100)
    parser.add_argument("--estimated-credits", type=int, default=45)
    parser.add_argument("--dry-run", action="store_true")
    asyncio.run(main(parser.parse_args()))
