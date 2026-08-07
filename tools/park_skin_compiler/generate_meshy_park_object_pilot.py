"""Generate one reviewed park-object GLB through Meshy's multi-view pipeline.

The script deliberately handles a single object per invocation.  A catalogue
reference image seeds Meshy's consistent multi-view image task, then the
resulting views feed Multi-Image-to-3D.  Outputs stay in an explicit artifact
directory until Blender cleanup and visual review are complete.

Example (run from ``backend`` so its configured Meshy credentials are used)::

    python ../tools/park_skin_compiler/generate_meshy_park_object_pilot.py \
      --asset-id nature-play-climbing-log-v1 \
      --reference ../frontend/public/archetypes/openspaces/nature-play-area/variant_0.png \
      --output-dir C:/dev-artifacts/3D-Maps/meshy-park-pilot/nature-play-climbing-log-v1
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import mimetypes
import sys
from pathlib import Path
from typing import Any

import httpx


DEFAULT_MULTIVIEW_PROMPT = """Create three mutually consistent orthographic product views of one natural climbing log for a public nature-play park. Use the weathered fallen hardwood log shown in the reference only as design guidance: irregular bark, visible cut end grain, subtle moss and age variation, rounded child-safe edges, no manufactured plastic. Isolate the single log horizontally on a neutral light-gray studio background. The same exact object must appear in front three-quarter, rear three-quarter, and side views, fully visible and not cropped. No people, buildings, plants, ground, text, ropes, platforms, tools, or extra objects."""

DEFAULT_TEXTURE_PROMPT = """Photoreal weathered hardwood bark derived from the nature-play archetype: varied gray-brown bark plates, exposed warm end grain, subtle moss in creases, dirt near the underside, matte roughness. No painted colors, labels, people, ground plane, or attached equipment."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_backend_client() -> type:
    backend = _repo_root() / "backend"
    sys.path.insert(0, str(backend))
    from app.generation.meshy_client import MeshyClient  # noqa: PLC0415

    return MeshyClient


def _data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


async def _download(client: httpx.AsyncClient, url: str, destination: Path) -> None:
    response = await client.get(url)
    response.raise_for_status()
    destination.write_bytes(response.content)


def _safe_summary(result: dict[str, Any]) -> dict[str, Any]:
    """Keep durable QA facts without persisting expiring signed URLs."""
    model_urls = result.get("model_urls") or {}
    image_urls = result.get("image_urls") or []
    texture_urls = result.get("texture_urls") or []
    if isinstance(texture_urls, dict):
        texture_urls_present: list[str] = sorted(texture_urls.keys())
    else:
        texture_urls_present = [f"texture_{index}" for index, _ in enumerate(texture_urls, start=1)]
    return {
        "id": result.get("id") or result.get("task_id"),
        "status": result.get("status"),
        "progress": result.get("progress"),
        "created_at": result.get("created_at"),
        "finished_at": result.get("finished_at"),
        "texture_urls_present": texture_urls_present,
        "model_formats_present": sorted(model_urls.keys()),
        "multiview_image_count": len(image_urls),
        "thumbnail_present": bool(result.get("thumbnail_url")),
    }


async def generate(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    references = [Path(value).resolve() for value in args.reference]
    missing = [str(path) for path in references if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing reference images: {missing}")

    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "asset_id": args.asset_id,
                    "source_references": [str(path) for path in references],
                    "output_dir": str(output_dir),
                    "target_polycount": args.target_polycount,
                    "hd_texture": args.hd_texture,
                    "paid_calls": 0,
                },
                indent=2,
            )
        )
        return

    MeshyClient = _load_backend_client()
    meshy = MeshyClient()
    balance_before = await meshy.get_balance()

    multiview_id = await meshy.image_to_image_multiview(
        [_data_uri(path) for path in references],
        args.multiview_prompt,
    )
    multiview = await meshy.poll_until_done(
        multiview_id,
        timeout=args.multiview_timeout,
        poll_interval=args.poll_interval,
        task_type="image_to_image",
    )

    model_id = await meshy.multi_image_to_3d(
        input_task_id=multiview_id,
        texture_prompt=args.texture_prompt,
        enable_pbr=True,
        target_polycount=args.target_polycount,
        should_remesh=True,
        image_enhancement=False,
        remove_lighting=True,
        hd_texture=args.hd_texture,
    )
    model = await meshy.poll_until_done(
        model_id,
        timeout=args.model_timeout,
        poll_interval=args.poll_interval,
        task_type="multi_image",
    )

    model_url = (model.get("model_urls") or {}).get("glb")
    if not model_url:
        raise RuntimeError("Meshy completed without a GLB URL")

    async with httpx.AsyncClient(timeout=180.0, follow_redirects=True) as client:
        await _download(client, model_url, output_dir / f"{args.asset_id}-raw.glb")
        for index, url in enumerate(multiview.get("image_urls") or [], start=1):
            await _download(client, url, output_dir / f"multiview-{index}.png")
        if model.get("thumbnail_url"):
            await _download(client, model["thumbnail_url"], output_dir / "meshy-thumbnail.png")
        for index, url in enumerate(model.get("multi_view_thumbnails") or [], start=1):
            await _download(client, url, output_dir / f"model-view-{index}.png")

    balance_after = await meshy.get_balance()
    metadata = {
        "asset_id": args.asset_id,
        "source_references": [str(path) for path in references],
        "multiview_prompt": args.multiview_prompt,
        "texture_prompt": args.texture_prompt,
        "target_polycount": args.target_polycount,
        "hd_texture": args.hd_texture,
        "balance_before": balance_before.get("balance"),
        "balance_after": balance_after.get("balance"),
        "credits_used": (
            balance_before.get("balance") - balance_after.get("balance")
            if isinstance(balance_before.get("balance"), int)
            and isinstance(balance_after.get("balance"), int)
            else None
        ),
        "multiview_task": _safe_summary(multiview),
        "model_task": _safe_summary(model),
    }
    (output_dir / "generation-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--reference", action="append", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--multiview-prompt", default=DEFAULT_MULTIVIEW_PROMPT)
    parser.add_argument("--texture-prompt", default=DEFAULT_TEXTURE_PROMPT)
    parser.add_argument("--target-polycount", type=int, default=24_000)
    parser.add_argument("--hd-texture", action="store_true")
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--multiview-timeout", type=int, default=600)
    parser.add_argument("--model-timeout", type=int, default=1_800)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(generate(parse_args()))
