"""
Pre-warm the archetype model cache: pilot -> confirm -> scale.

Reads buildingArchetypes.json READ-ONLY (never json.dump — it corrupts
thumbnailUrl paths), builds one job per archetype (variant_id="default")
or per named variant (--variants all), and POSTs them to the admin
/model-cache/prewarm endpoint. Card images are read from frontend/public
on the HOST and sent as base64 — the backend container cannot see them.

Modes:
  text        text-to-3D from catalog metadata prompt
  image       single card image (variant_N.png), rembg-isolated in the worker
  multi-image street card + 45 deg oblique (_angle_60.jpg) + nadir (_angle_90.jpg)
              to Meshy multi-image-to-3D; prompt = materials-only texture_prompt

Usage (from repo root):
  python scripts/prewarm_archetype_models.py --dry-run --all
  python scripts/prewarm_archetype_models.py --ids contemporary_midrise_residential,collegiate_gothic
  python scripts/prewarm_archetype_models.py --all --limit 20 --stagger 45
  python scripts/prewarm_archetype_models.py --mode multi-image --ids rndsqr_terraced_mixed_use_midrise \
      --force --download-artifacts artifacts/model_library_multiimage

Auth: SITEFORGE_ADMIN_EMAIL + SITEFORGE_ADMIN_PASSWORD env vars (login is
performed against --api-url), or a ready token in SITEFORGE_ADMIN_TOKEN.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "frontend/src/data/buildingArchetypes.json"
PUBLIC = ROOT / "frontend/public"


def api(base_url: str, method: str, path: str, payload: dict | None = None, token: str | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"{base_url}{path}",
        method=method,
        headers=headers,
        data=json.dumps(payload).encode() if payload is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} failed: HTTP {e.code} — {e.read()[:300].decode(errors='replace')}")


def get_token(base_url: str) -> str:
    token = os.environ.get("SITEFORGE_ADMIN_TOKEN")
    if token:
        return token
    email = os.environ.get("SITEFORGE_ADMIN_EMAIL")
    password = os.environ.get("SITEFORGE_ADMIN_PASSWORD")
    if not (email and password):
        raise SystemExit(
            "Set SITEFORGE_ADMIN_TOKEN, or SITEFORGE_ADMIN_EMAIL + SITEFORGE_ADMIN_PASSWORD"
        )
    data = api(base_url, "POST", "/api/v1/auth/login", {"email": email, "password": password})
    return data["access_token"]


def build_prompt(arch: dict, variant: dict | None) -> str:
    """Compact text-to-3D prompt from catalog metadata (client caps at 800)."""
    title = arch.get("title", arch["id"].replace("_", " "))
    floors = f"{arch.get('minFloors', 3)}-{arch.get('maxFloors', 6)} storeys"
    facade = (variant or arch).get("facadeDetail") or arch.get("facadeDetail") or {}
    roof = (variant or arch).get("roofDetail") or arch.get("roofDetail") or {}
    parts = [
        f"{title} building",
        floors,
        facade.get("primaryMaterial", ""),
        f"{roof.get('form', 'flat')} roof",
        "single isolated building, realistic architectural massing, no ground plane",
    ]
    if variant is not None and variant.get("label"):
        parts.insert(1, f"{variant['label']} variant")
    return ", ".join(p for p in parts if p)


def image_data(arch: dict, variant: dict | None) -> tuple[str, Path] | None:
    """base64 of the card image for image mode, or None if missing on disk."""
    url = (variant or {}).get("thumbnailUrl") or arch.get("thumbnailUrl")
    if not url:
        return None
    path = PUBLIC / url.lstrip("/")
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode(), path


_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


def multi_image_data(arch: dict, variant: dict | None) -> tuple[list[str], list[Path]] | None:
    """[street, oblique_60, nadir_90] as data URIs, or None if any is missing.

    Street card first — Meshy treats the first image as the primary view.
    The default (variant=None) target resolves via variants[0].thumbnailUrl,
    NOT the archetype-level thumbnailUrl: that points at hero.png, which has
    no _angle_60/_angle_90 siblings for 218 of 223 archetypes.
    """
    variants = arch.get("variants") or []
    url = (variant or (variants[0] if variants else {})).get("thumbnailUrl") or arch.get("thumbnailUrl")
    if not url:
        return None
    street = PUBLIC / url.lstrip("/")
    stem = street.with_suffix("")
    paths = [street, Path(f"{stem}_angle_60.jpg"), Path(f"{stem}_angle_90.jpg")]
    if not all(p.exists() for p in paths):
        return None
    uris = [
        f"data:{_MIME[p.suffix.lower()]};base64," + base64.b64encode(p.read_bytes()).decode()
        for p in paths
    ]
    return uris, paths


def build_texture_prompt(arch: dict, variant: dict | None) -> str:
    """Materials-and-colors-only prompt for Meshy's 600-char texture_prompt.

    Geometry comes from the three views, so massing language (floors, dims)
    is wasted budget. Greedy field packing: drop whole trailing fields that
    do not fit; the fixed tail is always kept.
    """
    tail = (
        "photorealistic architectural materials, true-to-reference colors, "
        "crisp window reveals, no text or signage artifacts"
    )
    limit = 600
    title = arch.get("title", arch["id"].replace("_", " "))
    facade = (variant or {}).get("facadeDetail") or arch.get("facadeDetail") or {}
    roof = (variant or {}).get("roofDetail") or arch.get("roofDetail") or {}
    roof_desc = roof.get("material") or roof.get("form") or ""
    fields = [
        f"{title} facade",
        facade.get("primaryMaterial", ""),
        facade.get("secondaryMaterial", ""),
        facade.get("groundFloor", ""),
        f"roof: {roof_desc}" if roof_desc else "",
    ]
    parts: list[str] = []
    budget = limit - len(tail) - 2  # ", " before the tail
    for f in fields:
        f = (f or "").strip()
        if not f:
            continue
        cost = len(f) + (2 if parts else 0)
        if cost > budget:
            continue
        parts.append(f)
        budget -= cost
    parts.append(tail)
    return ", ".join(parts)


# --- two-stage chain (Image-to-Image multi-view -> multi-image-to-3d) --------
# Reflective glass curtain-wall breaks Meshy's 3D reconstruction (deep reveals +
# spandrel bands -> carved holes). For glass-dominant buildings we push both
# chain stages toward a flat, flush, band-less facade so Meshy meshes a clean
# solid volume while the texture still reads as glazing (validated 2026-07-12).
_GLASS_TERMS = ("glass", "curtain wall", "curtain-wall", "curtainwall", "glazed curtain", "glazing")
_MASONRY_TERMS = (
    "brick", "stone", "limestone", "sandstone", "granite", "masonry",
    "terracotta", "terra cotta", "terra-cotta", "concrete", "cement",
    "render", "stucco", "timber", "wood", "steel panel", "metal panel",
)
_TOWER_TERMS = ("tower", "high-rise", "highrise", "high rise")

_GLASS_MV_PROMPT = (
    "Multiple consistent views of the exact same building as a single smooth "
    "monolithic tower volume. The ENTIRE facade is ONE continuous flush glass skin "
    "from base to top: uniform light-tinted glazing, thin flush mullions, NO "
    "horizontal spandrel bands, no floor separation lines, no reveals, no ledges, "
    "no setbacks, no recesses anywhere. Even matte non-reflective glass under flat "
    "overcast light. Preserve the overall tower shape and proportions as one clean "
    "smooth solid mass."
)
_GLASS_TEX_PROMPT = (
    "Glass tower facade, one continuous flush curtain wall, uniform light-tinted "
    "glazing in a fine even grid, thin flush mullions, minimal tonal variation "
    "between floors, no dark spandrel bands, smooth flat non-reflective surface, "
    "photorealistic architectural glass, crisp even grid, no text or signage artifacts"
)


_CURTAIN_TERMS = ("curtain wall", "curtain-wall", "curtainwall")


def _classify_material(hay: str) -> str | None:
    """'glass' | 'masonry' | None from a material/name haystack. Masonry is
    checked BEFORE bare glass so a brick building described with 'stained glass'
    windows (or a concrete/timber tower variant) is NOT read as glass-dominant."""
    if any(t in hay for t in _CURTAIN_TERMS):
        return "glass"
    if any(t in hay for t in _MASONRY_TERMS):
        return "masonry"
    if any(t in hay for t in _GLASS_TERMS):
        return "glass"
    return None


def is_glass_dominant(arch: dict, variant: dict | None, force_ids: set[str] | None = None) -> bool:
    """True when a building needs the flush-glass prompt route (reflective
    curtain-wall Meshy can't otherwise mesh). Precedence:
      1. --glass-ids operator override
      2. the VARIANT's own material/label/id — wins over archetype-level
         signals so a concrete or mass-timber variant of a curtain-wall tower
         is NOT flush-glass routed
      3. archetype-level curtain-wall, then a thin-metadata tall-tower default
    Validated cases: student_residence_tower default -> glass; its brutalist-
    concrete / mass-timber variants -> not glass; art_deco_setback_tower
    (limestone/granite/terracotta/cement variants) -> not glass; collegiate
    gothic (limestone, 'stained glass' keyword) -> not glass; calgary_plus_15
    (glass curtain wall) -> glass."""
    if force_ids and arch.get("id") in force_ids:
        return True
    facade = (variant or {}).get("facadeDetail") or arch.get("facadeDetail") or {}
    primary = str(facade.get("primaryMaterial", "")).lower()
    material_hay = " ".join([
        primary, str((variant or {}).get("label", "")), str((variant or {}).get("id", "")),
    ]).lower()
    verdict = _classify_material(material_hay)
    if verdict == "glass":
        return True
    if verdict == "masonry":
        return False
    # The variant stated no material — fall back to archetype-level signals.
    sp = arch.get("styleProfile") or {}
    arch_hay = " ".join([
        str(arch.get("aestheticCategory", "")), str(arch.get("title", "")), str(arch.get("id", "")),
        " ".join(sp.get("materials", []) or []),
    ]).lower()
    if any(t in arch_hay for t in _CURTAIN_TERMS):
        return True
    is_tower = any(t in arch_hay for t in _TOWER_TERMS)
    tall = (arch.get("maxFloors") or 0) >= 12
    return is_tower and tall


def chain_prompts(arch: dict, variant: dict | None, force_ids: set[str] | None = None) -> tuple[str, str, bool]:
    """(multiview_prompt, texture_prompt, is_glass) for the two-stage chain."""
    if is_glass_dominant(arch, variant, force_ids):
        return _GLASS_MV_PROMPT, _GLASS_TEX_PROMPT, True
    materials = build_texture_prompt(arch, variant)
    mv = (
        "Multiple consistent views of the exact same building, preserving its "
        "architecture, facade materials, window layout, and proportions. " + materials
    )
    return mv, materials, False


def street_card_data(arch: dict, variant: dict | None) -> tuple[str, Path] | None:
    """The single street card as a data URI — the chain's seed. Resolves
    variants[0].thumbnailUrl (not hero.png); aerials are NOT required."""
    variants = arch.get("variants") or []
    url = (variant or (variants[0] if variants else {})).get("thumbnailUrl") or arch.get("thumbnailUrl")
    if not url:
        return None
    p = PUBLIC / url.lstrip("/")
    if not p.exists():
        return None
    uri = f"data:{_MIME[p.suffix.lower()]};base64," + base64.b64encode(p.read_bytes()).decode()
    return uri, p


def collect_jobs(args) -> list[dict]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    archetypes = catalog["archetypes"]
    if args.ids:
        wanted = {a.strip() for a in args.ids.split(",")}
        archetypes = [a for a in archetypes if a["id"] in wanted]
        missing = wanted - {a["id"] for a in archetypes}
        if missing:
            raise SystemExit(f"Unknown archetype ids: {sorted(missing)}")
    if args.limit:
        archetypes = archetypes[: args.limit]

    mode = args.mode.replace("-", "_")  # CLI "multi-image" -> API "multi_image"
    glass_ids = {i.strip() for i in (args.glass_ids or "").split(",") if i.strip()}
    jobs = []
    for arch in archetypes:
        targets: list[dict | None] = [None]  # "default" key = archetype-level prompt
        if args.variants == "all":
            targets += list(arch.get("variants") or [])
        seen_image_sets: set[tuple] = set()  # dedupe: default resolves variants[0]'s refs
        for variant in targets:
            variant_id = variant["id"] if variant else "default"
            if args.variant_key:
                variant_id = args.variant_key  # cache-key override (A/B runs)
            job = {
                "archetype_id": arch["id"],
                "variant_id": variant_id,
                "engine": args.engine,
                "mode": mode,
            }
            if mode == "multi_image" and args.chain:
                # Two-stage chain: seed from the single street card; Meshy
                # synthesizes consistent isolated views, then reconstructs.
                card = street_card_data(arch, variant)
                if card is None:
                    print(f"  SKIP {job['archetype_id']}/{job['variant_id']}: no street card")
                    continue
                if str(card[1]) in seen_image_sets:
                    print(f"  SKIP {job['archetype_id']}/{job['variant_id']}: same card as default target")
                    continue
                seen_image_sets.add(str(card[1]))
                mv_prompt, tex_prompt, glass = chain_prompts(arch, variant, glass_ids)
                job["prompt"] = tex_prompt
                job["multiview_prompt"] = mv_prompt
                job["image_base64s"] = [card[0]]
                job["_image_paths"] = [str(card[1])]
                job["_glass"] = glass
                if args.target_polycount:
                    job["target_polycount"] = args.target_polycount
                if args.force:
                    job["force"] = True
            elif mode == "multi_image":
                imgs = multi_image_data(arch, variant)
                if imgs is None:
                    print(f"  SKIP {job['archetype_id']}/{job['variant_id']}: incomplete 3-angle ref set")
                    continue
                image_set = tuple(str(p) for p in imgs[1])
                if image_set in seen_image_sets:
                    # The "default" target already generated from these exact
                    # refs (it resolves variants[0]) — a second 30-credit task
                    # would produce a duplicate model under another key.
                    print(f"  SKIP {job['archetype_id']}/{job['variant_id']}: same refs as default target")
                    continue
                seen_image_sets.add(image_set)
                job["prompt"] = build_texture_prompt(arch, variant)
                job["image_base64s"] = imgs[0]
                job["_image_paths"] = [str(p) for p in imgs[1]]
                if args.target_polycount:
                    job["target_polycount"] = args.target_polycount
                if args.isolate:
                    job["isolate_images"] = True
                if args.clean:
                    job["clean_images"] = args.clean
                if args.force:
                    job["force"] = True
            else:
                job["prompt"] = build_prompt(arch, variant)
                if args.force:
                    job["force"] = True
                if mode == "image":
                    img = image_data(arch, variant)
                    if img is None:
                        print(f"  SKIP {job['archetype_id']}/{job['variant_id']}: no card image on disk")
                        continue
                    job["image_base64"], job["_image_path"] = img[0], str(img[1])
            jobs.append(job)
    return jobs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--ids", help="comma-separated archetype ids (pilot mode)")
    parser.add_argument("--all", action="store_true", help="all building archetypes")
    parser.add_argument("--limit", type=int, help="cap number of archetypes (with --all)")
    parser.add_argument("--variants", choices=["default", "all"], default="default")
    parser.add_argument("--mode", choices=["text", "image", "multi-image"], default="text")
    parser.add_argument("--engine", choices=["meshy", "tripo"], default="meshy")
    parser.add_argument("--stagger", type=int, default=45, help="seconds between submissions")
    parser.add_argument("--dry-run", action="store_true", help="print planned jobs, 0 API calls")
    parser.add_argument("--no-poll", action="store_true", help="submit and exit without waiting")
    parser.add_argument("--target-polycount", type=int, help="remesh target tris (multi-image; default 30000)")
    parser.add_argument("--isolate", action="store_true", help="rembg-isolate the street card (multi-image)")
    parser.add_argument("--clean", choices=["entourage", "building_only"],
                        help="Gemini removal edit on refs before Meshy (people/vehicles -> mutant geometry)")
    parser.add_argument("--chain", action="store_true",
                        help="two-stage chain: Meshy Image-to-Image multi-view synth (auto-isolates + "
                             "harmonizes views, glass-tower prompt routing) -> multi-image-to-3d. "
                             "Seeds from the street card only; supersedes --clean/--isolate.")
    parser.add_argument("--glass-ids", help="comma-separated archetype ids to FORCE onto the "
                                            "flush-glass prompt route (overrides auto-detection)")
    parser.add_argument("--force", action="store_true", help="re-generate over completed cache rows")
    parser.add_argument("--variant-key", help="cache variant_id override, e.g. polytest for A/B runs")
    parser.add_argument("--download-artifacts", metavar="DIR", help="download GLB + thumbnails per completed entry")
    args = parser.parse_args()

    if not args.ids and not args.all:
        raise SystemExit("Pick --ids a,b,c (pilot) or --all [--limit N]")
    if args.chain and args.mode != "multi-image":
        raise SystemExit("--chain requires --mode multi-image")

    jobs = collect_jobs(args)
    mode_label = f"{args.mode}+chain" if args.chain else args.mode
    glass_n = sum(1 for j in jobs if j.get("_glass"))
    print(f"{len(jobs)} job(s) planned ({mode_label} mode, engine={args.engine}"
          + (f", {glass_n} glass-routed" if args.chain else "") + "):")
    for j in jobs:
        extra = f"  [{j.get('_image_path', '')}]" if args.mode == "image" else ""
        tag = "  [GLASS]" if j.get("_glass") else ""
        print(f"  {j['archetype_id']:45s} {j['variant_id']:30s}{extra}{tag}")
        for p in j.get("_image_paths", []):
            print(f"    seed: {p}")
        if j.get("multiview_prompt"):
            print(f"    multiview ({len(j['multiview_prompt'])} chars): {j['multiview_prompt'][:90]}")
        print(f"    texture ({len(j['prompt'])} chars): {j['prompt'][:90]}")
    if args.dry_run:
        print("\nDry run — nothing submitted.")
        return

    token = get_token(args.api_url)
    submitted = []
    already_completed = []
    for i, job in enumerate(jobs):
        payload = {k: v for k, v in job.items() if not k.startswith("_")}
        result = api(args.api_url, "POST", "/api/v1/model-cache/prewarm", payload, token)
        print(f"[{job['archetype_id']}/{job['variant_id']}] {result['status']}")
        if result["status"] == "queued":
            submitted.append((job["archetype_id"], job["variant_id"]))
            if i < len(jobs) - 1 and args.stagger:
                time.sleep(args.stagger)
        elif result["status"] == "completed":
            # Already cached (no credits spent) — still include in the
            # summary and artifact download so re-runs can fetch results.
            already_completed.append((job["archetype_id"], job["variant_id"]))

    if args.no_poll or not (submitted or already_completed):
        return

    print(f"\nPolling {len(submitted)} entr(ies)...")
    pending = set(submitted)
    # multi-image tasks run longer and the worker is --concurrency=2, so a
    # 10-archetype batch needs ~1.5-2.5h; the tasks keep running past this
    # window regardless (re-run the command to resume watching — idempotent).
    poll_minutes = 120 if args.mode == "multi-image" else 45
    deadline = time.time() + poll_minutes * 60
    while pending and time.time() < deadline:
        time.sleep(20)
        try:
            entries = api(args.api_url, "GET", "/api/v1/model-cache/entries", token=token)["entries"]
        except SystemExit as exc:
            # A transient /entries error must NOT kill a long batch poll — the
            # Celery tasks keep running regardless. Log and retry next tick.
            print(f"  (transient poll error, retrying: {str(exc)[:90]})")
            continue
        by_key = {(e["archetype_id"], e["variant_id"]): e for e in entries if e["engine"] == args.engine}
        for key in sorted(pending):
            e = by_key.get(key)
            if not e:
                continue
            # A --force supersede parks the row at failed/"superseded: ..."
            # until the worker re-claims it — that is queue state, not a
            # terminal failure.
            if e["status"] == "failed" and (e.get("error") or "").startswith("superseded:"):
                continue
            if e["status"] in ("completed", "failed"):
                size = f"{(e['size_bytes'] or 0) / 1e6:.1f}MB" if e["status"] == "completed" else (e["error"] or "")[:80]
                print(f"  {key[0]}/{key[1]}: {e['status'].upper()} {size}")
                pending.discard(key)

    print("\n=== SUMMARY ===")
    watched = set(submitted) | set(already_completed)
    try:
        entries = api(args.api_url, "GET", "/api/v1/model-cache/entries", token=token)["entries"]
    except SystemExit as exc:
        print(f"  (could not fetch summary: {str(exc)[:90]})")
        entries = []
    completed_entries = []
    for e in entries:
        if (e["archetype_id"], e["variant_id"]) in watched:
            dims = (e.get("metadata") or {}).get("dimensions") or {}
            dims_txt = ""
            if dims:
                dims_txt = (f"  long/h={dims.get('long_per_height', 0):.2f}"
                            f" short/h={dims.get('short_per_height', 0):.2f}")
            print(f"  {e['archetype_id']:45s} {e['variant_id']:20s} {e['status']:10s} "
                  f"{(e['size_bytes'] or 0) / 1e6:.1f}MB use={e['use_count']}{dims_txt}")
            if e["status"] == "completed":
                completed_entries.append(e)
    if pending:
        print(f"  (still pending: {sorted(pending)})")

    if args.download_artifacts and completed_entries:
        download_artifacts(args, token, completed_entries)


def fetch_bytes(base_url: str, path: str, token: str) -> bytes | None:
    """GET a binary file through the API proxy; None on 404."""
    req = urllib.request.Request(
        f"{base_url}{path}", headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def download_artifacts(args, token: str, entries: list[dict]) -> None:
    """Pull each completed entry's GLB + thumbnails for visual QA."""
    out_root = ROOT / args.download_artifacts
    print(f"\nDownloading artifacts to {out_root} ...")
    for e in entries:
        out_dir = out_root / e["archetype_id"] / e["variant_id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        keys = {"model.glb": e["model_key"]}
        prefix = f"archetype-cache/{e['archetype_id']}/{e['variant_id']}/{e['engine']}/{e['id']}"
        keys["thumb.png"] = f"{prefix}_thumb.png"
        for view in ("front", "right", "back", "left"):
            keys[f"thumb_{view}.png"] = f"{prefix}_thumb_{view}.png"
        for i in range(4):  # cleaned inputs (present only when --clean ran)
            for ext in ("png", "jpg"):
                keys[f"input_{i}.{ext}"] = f"{prefix}_input_{i}.{ext}"
        for filename, key in keys.items():
            if not key:
                continue
            data = fetch_bytes(args.api_url, f"/api/v1/files/{key}", token)
            if data is None:
                continue
            (out_dir / filename).write_bytes(data)
            print(f"  {e['archetype_id']}/{e['variant_id']}/{filename}  {len(data) / 1e6:.1f}MB")


if __name__ == "__main__":
    main()
