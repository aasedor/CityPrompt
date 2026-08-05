"""Run a bounded paired-provider park composition image study.

Generated images are training references for the deterministic park LEGO
compiler. They are not City Prompt production renders.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
MANIFEST_PATH = Path(__file__).with_name("park_composition_api_study.json")
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "park-composition-api-study-2026-08-05"


def _settings():
    sys.path.insert(0, str(BACKEND_ROOT))
    from app.core.config import get_settings

    return get_settings()


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _resolved_prompt(manifest: dict, scene: dict) -> str:
    focus = "; ".join(scene["studyFocus"])
    return "\n\n".join(
        [
            manifest["basePrompt"],
            f"SITE: {scene['site']}",
            f"COMPOSITION: {scene['compositionBrief']}",
            f"STUDY PRIORITIES: {focus}.",
            f"FINAL CONSTRAINTS: {manifest['negativePrompt']}",
        ]
    )


def _load_run(output: Path, manifest: dict) -> dict:
    run_path = output / "run.json"
    if run_path.exists():
        return json.loads(run_path.read_text(encoding="utf-8"))
    return {
        "schemaVersion": 1,
        "studyId": manifest["studyId"],
        "targetApiCalls": manifest["targetApiCalls"],
        "attemptedApiCalls": 0,
        "results": [],
    }


def _save_run(output: Path, run: dict) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "run.json").write_text(json.dumps(run, indent=2), encoding="utf-8")


def _provider_spec(manifest: dict, provider_id: str) -> dict:
    return next(item for item in manifest["providers"] if item["id"] == provider_id)


def _gemini_image(prompt: str, spec: dict, api_key: str) -> tuple[bytes, str, dict]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{spec['model']}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "imageSize": spec["imageSize"],
                "aspectRatio": spec["aspectRatio"],
            },
        },
    }
    with httpx.Client(timeout=300.0) as client:
        response = client.post(url, json=payload)
    response.raise_for_status()
    body = response.json()
    candidates = body.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates")
    for part in candidates[0].get("content", {}).get("parts", []):
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            return base64.b64decode(inline["data"]), mime, body.get("usageMetadata", {})
    raise RuntimeError("Gemini returned no inline image")


def _openai_image(prompt: str, spec: dict, api_key: str) -> tuple[bytes, str, dict]:
    payload = {
        "model": spec["model"],
        "prompt": prompt,
        "n": 1,
        "size": spec["size"],
        "quality": spec["quality"],
        "output_format": spec["outputFormat"],
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    with httpx.Client(timeout=300.0) as client:
        response = client.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers)
    response.raise_for_status()
    body = response.json()
    data = body.get("data") or []
    if not data or not data[0].get("b64_json"):
        raise RuntimeError("OpenAI returned no base64 image")
    return base64.b64decode(data[0]["b64_json"]), "image/jpeg", body.get("usage", {})


def _extension(mime: str) -> str:
    return ".jpg" if mime in {"image/jpeg", "image/jpg"} else ".png"


def _call_key(scene_id: str, provider_id: str) -> str:
    return f"{scene_id}:{provider_id}"


def generate(args: argparse.Namespace) -> None:
    manifest = _load_manifest()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    resolved = {
        **manifest,
        "scenes": [
            {**scene, "resolvedPrompt": _resolved_prompt(manifest, scene)}
            for scene in manifest["scenes"]
        ],
    }
    (output / "study_manifest.json").write_text(json.dumps(resolved, indent=2), encoding="utf-8")

    providers = [item["id"] for item in manifest["providers"]]
    if args.provider != "all":
        providers = [args.provider]
    scenes = manifest["scenes"]
    if args.scene:
        scenes = [scene for scene in scenes if scene["id"] == args.scene]
        if not scenes:
            raise SystemExit(f"Unknown scene: {args.scene}")

    scheduled = [(scene, provider) for scene in scenes for provider in providers]
    if args.dry_run:
        print(f"study={manifest['studyId']} scheduled_calls={len(scheduled)} target_calls={manifest['targetApiCalls']}")
        for scene, provider in scheduled:
            print(f"{scene['id']} -> {provider}")
        return

    settings = _settings()
    if "gemini" in providers and not settings.gemini_api_key:
        raise SystemExit("Gemini credential is not configured")
    if "openai" in providers and not settings.openai_api_key:
        raise SystemExit("OpenAI credential is not configured")

    run = _load_run(output, manifest)
    attempted_keys = {_call_key(item["sceneId"], item["provider"]) for item in run["results"]}
    invocation_calls = 0
    for scene, provider_id in scheduled:
        key = _call_key(scene["id"], provider_id)
        if key in attempted_keys:
            print(f"skip attempted {key}")
            continue
        if run["attemptedApiCalls"] >= manifest["targetApiCalls"]:
            print("study call cap reached")
            break
        if args.max_calls is not None and invocation_calls >= args.max_calls:
            break

        spec = _provider_spec(manifest, provider_id)
        prompt = _resolved_prompt(manifest, scene)
        started = time.monotonic()
        result = {
            "sceneId": scene["id"],
            "provider": provider_id,
            "model": spec["model"],
            "startedAt": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
        }
        # Persist the attempted call before sending it so an interrupted run can
        # never exceed the declared paid-call cap.
        run["attemptedApiCalls"] += 1
        run["results"].append(result)
        _save_run(output, run)
        invocation_calls += 1
        print(f"call {run['attemptedApiCalls']}/{manifest['targetApiCalls']} {key}", flush=True)

        try:
            if provider_id == "gemini":
                image_bytes, mime, usage = _gemini_image(prompt, spec, settings.gemini_api_key)
            else:
                image_bytes, mime, usage = _openai_image(prompt, spec, settings.openai_api_key)
            filename = f"{scene['id']}__{provider_id}{_extension(mime)}"
            (output / filename).write_bytes(image_bytes)
            result.update(
                {
                    "status": "succeeded",
                    "file": filename,
                    "mimeType": mime,
                    "bytes": len(image_bytes),
                    "durationSeconds": round(time.monotonic() - started, 2),
                    "usage": usage,
                }
            )
            print(f"wrote {filename} ({len(image_bytes)} bytes)", flush=True)
        except Exception as exc:
            result.update(
                {
                    "error": f"{type(exc).__name__}: {str(exc)[:800]}",
                    "durationSeconds": round(time.monotonic() - started, 2),
                }
            )
            print(f"FAILED {key}: {result['error']}", flush=True)
        finally:
            _save_run(output, run)


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def compose(output: Path) -> None:
    manifest = _load_manifest()
    output = output.resolve()
    sheets = output / "comparison-sheets"
    sheets.mkdir(parents=True, exist_ok=True)
    cell_w, cell_h, header = 720, 480, 72
    all_rows: list[Image.Image] = []
    for scene in manifest["scenes"]:
        pair: list[Image.Image] = []
        for provider in ("gemini", "openai"):
            matches = list(output.glob(f"{scene['id']}__{provider}.*"))
            if not matches:
                continue
            image = Image.open(matches[0]).convert("RGB")
            image.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
            cell = Image.new("RGB", (cell_w, cell_h), "#15191b")
            cell.paste(image, ((cell_w - image.width) // 2, (cell_h - image.height) // 2))
            pair.append(cell)
        if len(pair) != 2:
            continue
        sheet = Image.new("RGB", (cell_w * 2, cell_h + header), "#15191b")
        draw = ImageDraw.Draw(sheet)
        draw.text((18, 10), scene["title"], fill="white", font=_font(24, True))
        draw.text((18, 42), "Gemini", fill="#b9d8ff", font=_font(18, True))
        draw.text((cell_w + 18, 42), "GPT Image", fill="#c8f0c0", font=_font(18, True))
        sheet.paste(pair[0], (0, header))
        sheet.paste(pair[1], (cell_w, header))
        path = sheets / f"{scene['id']}__comparison.jpg"
        sheet.save(path, quality=90, optimize=True)
        all_rows.append(sheet)
        print(f"wrote {path}")

    if all_rows:
        overview = Image.new("RGB", (cell_w * 2, len(all_rows) * (cell_h + header)), "#15191b")
        for index, row in enumerate(all_rows):
            overview.paste(row, (0, index * (cell_h + header)))
        overview_path = output / "park-composition-provider-comparison.jpg"
        overview.save(overview_path, quality=88, optimize=True)
        print(f"wrote {overview_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--provider", choices=("all", "gemini", "openai"), default="all")
    parser.add_argument("--scene")
    parser.add_argument("--max-calls", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--compose", action="store_true")
    args = parser.parse_args()
    if args.compose:
        compose(args.output)
    else:
        generate(args)


if __name__ == "__main__":
    main()
