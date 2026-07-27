#!/usr/bin/env python3
"""Upload a compiled archetype family into the SiteForge model library.

Takes the output folder of ``generate_family.py`` (module GLBs + assembled GLB
+ preview PNG + *_manifest.json + validation_report.json) and POSTs it to
``/api/v1/lego-assembly/import-manifest``, which creates or refreshes one
``ModelLibraryEntry`` per module with planner-ready LEGO metadata.

Usage::

    python import_manifest.py build/archetypes/nordic_timber_midrise \
        --api-base http://localhost:8000 --email you@example.com --password ...

Auth resolution order: --token, SITEFORGE_TOKEN, then --email/--password
(or SITEFORGE_EMAIL/SITEFORGE_PASSWORD) via POST /api/v1/auth/login.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Windows consoles default to legacy code pages; never crash on em-dashes etc.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests

GLB_CONTENT_TYPE = "model/gltf-binary"


def _fail(message: str) -> "SystemExit":
    print(f"ERROR: {message}", file=sys.stderr)
    return SystemExit(1)


def resolve_token(args: argparse.Namespace) -> str:
    """Return a bearer token from --token/env, or by logging in."""
    token = args.token or os.environ.get("SITEFORGE_TOKEN")
    if token:
        return token

    email = args.email or os.environ.get("SITEFORGE_EMAIL")
    password = args.password or os.environ.get("SITEFORGE_PASSWORD")
    if not email or not password:
        raise _fail(
            "No credentials. Pass --token (or SITEFORGE_TOKEN), or --email/--password "
            "(or SITEFORGE_EMAIL/SITEFORGE_PASSWORD)."
        )

    login_url = f"{args.api_base.rstrip('/')}/api/v1/auth/login"
    try:
        response = requests.post(login_url, json={"email": email, "password": password}, timeout=30)
    except requests.RequestException as exc:
        raise _fail(f"Login request to {login_url} failed: {exc}")
    if response.status_code != 200:
        raise _fail(f"Login failed ({response.status_code}): {response.text[:300]}")
    token = response.json().get("access_token")
    if not token:
        raise _fail("Login response had no access_token")
    return token


def collect_family_payload(manifest_path: Path) -> tuple[dict, list[Path], Path | None, Path | None]:
    """Read the manifest and locate the sibling files it references."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    folder = manifest_path.parent

    filenames = [m.get("filename") for m in manifest.get("modules") or [] if m.get("filename")]
    assembled_filename = (manifest.get("assembled") or {}).get("filename")
    if assembled_filename:
        filenames.append(assembled_filename)

    glbs: list[Path] = []
    for filename in filenames:
        path = folder / filename
        if path.is_file():
            glbs.append(path)
        else:
            print(f"  WARNING: {filename} listed in manifest but missing on disk — skipping")

    thumbnail: Path | None = None
    thumbnail_name = manifest.get("thumbnail")
    if thumbnail_name and (folder / thumbnail_name).is_file():
        thumbnail = folder / thumbnail_name

    report_path = folder / "validation_report.json"
    report: Path | None = report_path if report_path.is_file() else None
    return manifest, glbs, thumbnail, report


def import_family(args: argparse.Namespace, token: str, manifest_path: Path) -> bool:
    """POST one family to the import endpoint. Returns True on success."""
    try:
        manifest, glbs, thumbnail, report = collect_family_payload(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read {manifest_path.name}: {exc}", file=sys.stderr)
        return False

    family = manifest.get("family", manifest_path.stem)
    print(f"\nImporting family '{family}' from {manifest_path.name}")
    if not glbs:
        print("ERROR: no module GLBs found next to the manifest", file=sys.stderr)
        return False

    multipart: list[tuple[str, tuple[str, bytes, str]]] = [
        ("manifest", (manifest_path.name, manifest_path.read_bytes(), "application/json"))
    ]
    for glb in glbs:
        multipart.append(("files", (glb.name, glb.read_bytes(), GLB_CONTENT_TYPE)))
    if thumbnail is not None:
        multipart.append(("thumbnail", (thumbnail.name, thumbnail.read_bytes(), "image/png")))
    if report is not None:
        multipart.append(("validation_report", (report.name, report.read_bytes(), "application/json")))

    url = f"{args.api_base.rstrip('/')}/api/v1/lego-assembly/import-manifest"
    params = {"force": "true"} if args.force else None
    try:
        response = requests.post(
            url,
            files=multipart,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=600,
        )
    except requests.RequestException as exc:
        print(f"ERROR: request to {url} failed: {exc}", file=sys.stderr)
        return False

    if response.status_code != 200:
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = response.text[:500]
        print(f"ERROR: import failed ({response.status_code}): {detail}", file=sys.stderr)
        return False

    payload = response.json()
    counts = {"created": 0, "updated": 0}
    for item in payload.get("imported", []):
        counts[item.get("action", "created")] = counts.get(item.get("action", "created"), 0) + 1
        print(f"  {item.get('action', '?'):8s} {item.get('role', '?'):10s} -> {item.get('model_url', '')}")
    for filename in payload.get("skipped", []):
        print(f"  skipped  {filename} (no matching manifest entry)")
    print(f"  Done: {counts.get('created', 0)} created, {counts.get('updated', 0)} updated")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_dir", type=Path, help="generate_family.py output folder containing *_manifest.json")
    parser.add_argument("--api-base", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--token", default=None, help="Bearer token (or env SITEFORGE_TOKEN)")
    parser.add_argument("--email", default=None, help="Login email (or env SITEFORGE_EMAIL)")
    parser.add_argument("--password", default=None, help="Login password (or env SITEFORGE_PASSWORD)")
    parser.add_argument("--force", action="store_true", help="Import even if validation_report status != pass")
    args = parser.parse_args(argv)

    if not args.output_dir.is_dir():
        print(f"ERROR: {args.output_dir} is not a directory", file=sys.stderr)
        return 2

    manifests = sorted(args.output_dir.glob("*_manifest.json"))
    if not manifests:
        print(f"ERROR: no *_manifest.json found in {args.output_dir}", file=sys.stderr)
        return 2

    token = resolve_token(args)

    failures = 0
    for manifest_path in manifests:
        if not import_family(args, token, manifest_path):
            failures += 1

    if failures:
        print(f"\n{failures}/{len(manifests)} families failed to import", file=sys.stderr)
        return 1
    print(f"\nAll {len(manifests)} families imported successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
