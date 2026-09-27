"""Contact sheets and a summary table for saved Video Render attempts.

Reads the attempt ledger straight from the project's metadata in Postgres and
the media straight from the S3 bucket, so it works against the local
validation stack without an API login and never calls a provider.

Usage (defaults match the local validation stack on this machine):

    python tools/video_eval/attempt_report.py --project <uuid> \
        --out docs/video-pilots/eval-2026-09-26 [--attempts id,id] [--since 2026-09-26T00:00]

Environment overrides: DATABASE_URL_SYNC, S3_ENDPOINT_URL, S3_BUCKET_NAME,
S3_ACCESS_KEY, S3_SECRET_KEY.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DEFAULT_DATABASE_URL = "postgresql://studio:studio-local-only@127.0.0.1:55432/cityprompt_validation_20260924"
DEFAULT_S3_ENDPOINT = "http://127.0.0.1:19002"
DEFAULT_BUCKET = "cityprompt-validation-20260924"
DEFAULT_S3_KEY = "studio-local-only"
FRAME_PROGRESS = (0.0, 0.25, 0.5, 0.75, 1.0)
THUMB_WIDTH = 320
THUMB_HEIGHT = 180
LABEL_WIDTH = 300
GUTTER = 6


@dataclass(frozen=True)
class Media:
    video: bytes | None
    preview: bytes | None
    anchor: bytes | None


def storage_key(url: str) -> str:
    prefix = "/api/v1/files/"
    return url[len(prefix) :] if url.startswith(prefix) else url.lstrip("/")


def load_attempts(database_url: str, project_id: str) -> list[dict]:
    import psycopg2

    with psycopg2.connect(database_url) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT metadata FROM projects WHERE id = %s", (project_id,))
        row = cursor.fetchone()
    if not row:
        raise SystemExit(f"Project {project_id} not found.")
    metadata = row[0] or {}
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return [dict(item) for item in metadata.get("video_pilot_attempts", [])]


def s3_client(endpoint: str, access_key: str, secret_key: str):
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1",
        config=Config(signature_version="s3v4"),
    )


def download(client, bucket: str, url: str | None) -> bytes | None:
    if not url:
        return None
    response = client.get_object(Bucket=bucket, Key=storage_key(url))
    return response["Body"].read()


def sample_frames(video: bytes, suffix: str = ".mp4") -> list[np.ndarray]:
    """Return BGR frames at FRAME_PROGRESS positions, decoding from a temp file."""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(video)
        path = handle.name
    frames: list[np.ndarray] = []
    try:
        capture = cv2.VideoCapture(path)
        total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total <= 0:
            decoded: list[np.ndarray] = []
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                decoded.append(frame)
            total = len(decoded)
            for progress in FRAME_PROGRESS:
                if decoded:
                    frames.append(decoded[min(total - 1, int(round(progress * (total - 1))))])
        else:
            for progress in FRAME_PROGRESS:
                capture.set(cv2.CAP_PROP_POS_FRAMES, min(total - 1, int(round(progress * (total - 1)))))
                ok, frame = capture.read()
                if ok:
                    frames.append(frame)
        capture.release()
    finally:
        os.unlink(path)
    return frames


def to_thumb(frame_bgr: np.ndarray | None) -> Image.Image:
    if frame_bgr is None:
        return Image.new("RGB", (THUMB_WIDTH, THUMB_HEIGHT), (40, 40, 40))
    image = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    image.thumbnail((THUMB_WIDTH, THUMB_HEIGHT))
    canvas = Image.new("RGB", (THUMB_WIDTH, THUMB_HEIGHT), (20, 20, 20))
    canvas.paste(image, ((THUMB_WIDTH - image.width) // 2, (THUMB_HEIGHT - image.height) // 2))
    return canvas


def image_thumb(data: bytes | None) -> Image.Image:
    if not data:
        return Image.new("RGB", (THUMB_WIDTH, THUMB_HEIGHT), (40, 40, 40))
    array = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    return to_thumb(array)


def score_text(prefix: str, score, minimum, status) -> str:
    if score is None:
        return f"{prefix} —"
    text = f"{prefix} {float(score):.0f}"
    if minimum is not None:
        text += f" (min {float(minimum):.0f})"
    if status:
        text += f" {status}"
    return text


def attempt_lines(attempt: dict) -> list[str]:
    cost = attempt.get("provider_cost_usd")
    cost_text = f"${float(cost):.2f} billed" if cost is not None else f"~${float(attempt.get('estimated_cost_usd') or 0):.2f} est."
    return [
        f"{attempt.get('provider', 'omni')} · {attempt.get('look_style') or attempt.get('style')}"
        + (" · anchor" if attempt.get("anchor_attached") else ""),
        f"{attempt.get('control_mode', '')} · {attempt.get('camera_motion', '')} · {attempt.get('render_quality', '')}",
        str(attempt.get("model") or ""),
        score_text("fidelity", attempt.get("fidelity_score"), attempt.get("fidelity_min_score"), attempt.get("fidelity_status")),
        score_text("geometry", attempt.get("geometry_score"), attempt.get("geometry_min_score"), attempt.get("geometry_status")),
        f"{cost_text} · {attempt.get('prompt_chars') or '?'} chars · {str(attempt.get('created_at') or '')[:16]}",
        str(attempt.get("id") or "")[:8],
    ]


def contact_sheet(rows: list[tuple[list[str], Image.Image | None, list[Image.Image]]]) -> Image.Image:
    columns = 1 + len(FRAME_PROGRESS)
    width = LABEL_WIDTH + columns * (THUMB_WIDTH + GUTTER) + GUTTER
    height = GUTTER + len(rows) * (THUMB_HEIGHT + GUTTER) + 24
    sheet = Image.new("RGB", (width, height), (12, 12, 12))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    x = LABEL_WIDTH + GUTTER
    draw.text((x, 4), "anchor / source", fill=(200, 200, 200), font=font)
    for index, progress in enumerate(FRAME_PROGRESS):
        draw.text((x + (index + 1) * (THUMB_WIDTH + GUTTER), 4), f"t = {progress * 8:.0f}s", fill=(200, 200, 200), font=font)
    y = 24 + GUTTER
    for lines, lead, thumbs in rows:
        for offset, line in enumerate(lines):
            draw.text((GUTTER, y + offset * 16), line[:48], fill=(235, 235, 235), font=font)
        sheet.paste(lead or Image.new("RGB", (THUMB_WIDTH, THUMB_HEIGHT), (40, 40, 40)), (x, y))
        for index in range(len(FRAME_PROGRESS)):
            thumb = thumbs[index] if index < len(thumbs) else to_thumb(None)
            sheet.paste(thumb, (x + (index + 1) * (THUMB_WIDTH + GUTTER), y))
        y += THUMB_HEIGHT + GUTTER
    return sheet


def summary_markdown(project_id: str, attempts: list[dict]) -> str:
    header = (
        "| attempt | provider | model | look | anchor | mode · motion · quality | fidelity | geometry | cost | prompt chars | created |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|"
    )
    lines = [f"# Video Render evaluation · project `{project_id}`", "", header]
    for attempt in attempts:
        cost = attempt.get("provider_cost_usd")
        cost_text = f"${float(cost):.2f}" if cost is not None else f"~${float(attempt.get('estimated_cost_usd') or 0):.2f}"
        lines.append(
            "| `{id}` | {provider} | `{model}` | {look} | {anchor} | {mode} · {motion} · {quality} | {fid} | {geo} | {cost} | {chars} | {created} |".format(
                id=str(attempt.get("id") or "")[:8],
                provider=attempt.get("provider", "omni"),
                model=attempt.get("model") or "",
                look=attempt.get("look_style") or attempt.get("style") or "",
                anchor="yes" if attempt.get("anchor_attached") else "no",
                mode=attempt.get("control_mode", ""),
                motion=attempt.get("camera_motion", ""),
                quality=attempt.get("render_quality", ""),
                fid=score_text("", attempt.get("fidelity_score"), attempt.get("fidelity_min_score"), attempt.get("fidelity_status")).strip(),
                geo=score_text("", attempt.get("geometry_score"), attempt.get("geometry_min_score"), attempt.get("geometry_status")).strip(),
                cost=cost_text,
                chars=attempt.get("prompt_chars") or "",
                created=str(attempt.get("created_at") or "")[:19],
            )
        )
    lines.append("")
    lines.append("Frames sampled at 0 / 2 / 4 / 6 / 8 s. `fidelity` is the legacy appearance score; `geometry` compares depth silhouettes and is lighting-invariant.")
    return "\n".join(lines) + "\n"


def select_attempts(attempts: list[dict], ids: set[str], since: datetime | None) -> list[dict]:
    chosen = []
    for attempt in attempts:
        if attempt.get("status") != "complete" or not attempt.get("video_url"):
            continue
        if ids and not any(str(attempt.get("id", "")).startswith(prefix) for prefix in ids):
            continue
        if since:
            created = str(attempt.get("created_at") or "")
            try:
                if datetime.fromisoformat(created.replace("Z", "+00:00")).replace(tzinfo=None) < since:
                    continue
            except ValueError:
                pass
        chosen.append(attempt)
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", required=True)
    parser.add_argument("--out", required=True, help="Output folder for the contact sheet, summary and MP4 copies.")
    parser.add_argument("--attempts", default="", help="Comma-separated attempt id prefixes; default = every completed attempt.")
    parser.add_argument("--since", default=None, help="ISO timestamp; only attempts created after it.")
    parser.add_argument("--no-copy", action="store_true", help="Do not copy the MP4s into the output folder.")
    args = parser.parse_args()

    database_url = os.environ.get("DATABASE_URL_SYNC", DEFAULT_DATABASE_URL)
    client = s3_client(
        os.environ.get("S3_ENDPOINT_URL", DEFAULT_S3_ENDPOINT),
        os.environ.get("S3_ACCESS_KEY", DEFAULT_S3_KEY),
        os.environ.get("S3_SECRET_KEY", DEFAULT_S3_KEY),
    )
    bucket = os.environ.get("S3_BUCKET_NAME", DEFAULT_BUCKET)
    since = datetime.fromisoformat(args.since) if args.since else None
    ids = {value.strip() for value in args.attempts.split(",") if value.strip()}

    attempts = select_attempts(load_attempts(database_url, args.project), ids, since)
    if not attempts:
        raise SystemExit("No completed attempts matched.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[list[str], Image.Image | None, list[Image.Image]]] = []
    seen_previews: set[str] = set()
    for attempt in attempts:
        media = Media(
            video=download(client, bucket, attempt.get("video_url")),
            preview=download(client, bucket, attempt.get("preview_video_url")),
            anchor=download(client, bucket, attempt.get("anchor_image_url")),
        )
        preview_key = str(attempt.get("preview_video_url") or "")
        if media.preview and preview_key not in seen_previews:
            seen_previews.add(preview_key)
            suffix = ".webm" if preview_key.endswith(".webm") else ".mp4"
            rows.append(
                (
                    ["SOURCE · deterministic route preview", str(attempt.get("camera_motion") or ""), preview_key.rsplit("/", 2)[-2][:8]],
                    None,
                    [to_thumb(frame) for frame in sample_frames(media.preview, suffix)],
                )
            )
        frames = sample_frames(media.video) if media.video else []
        rows.append((attempt_lines(attempt), image_thumb(media.anchor) if media.anchor else None, [to_thumb(frame) for frame in frames]))
        if media.video and not args.no_copy:
            (out / f"{attempt.get('provider', 'omni')}-{attempt.get('look_style') or 'legacy'}-{str(attempt.get('id'))[:8]}.mp4").write_bytes(media.video)
        print(f"{str(attempt.get('id'))[:8]}  {attempt.get('provider'):<16} {str(attempt.get('look_style')):<16} "
              f"fidelity={attempt.get('fidelity_score')} geometry={attempt.get('geometry_score')} status={attempt.get('geometry_status')}")

    sheet = contact_sheet(rows)
    # JPEG keeps a nine-row sheet under a megabyte so it can live in docs/.
    sheet.save(out / "contact-sheet.jpg", quality=86, optimize=True)
    (out / "summary.md").write_text(summary_markdown(args.project, attempts), encoding="utf-8")
    (out / "attempts.json").write_text(json.dumps(attempts, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out / 'contact-sheet.jpg'} and {out / 'summary.md'} ({len(attempts)} attempts)")
    if shutil.which("ffmpeg") is None:
        print("note: ffmpeg not found; OpenCV decoded the videos directly.")


if __name__ == "__main__":
    main()
