"""Seed the Calgary policy corpus from live calgary.ca URLs.

Run INSIDE the backend container/image (PDFs are never committed to the repo).
Lives under backend/scripts/ so it ships in the production image
(render.yaml builds with dockerContext ./backend, and the production DB is
internal-only — a Render shell on the API service is the ONLY place this can
run in production):
    # local Docker:
    docker exec -w /app devplatform-backend python scripts/seed_policy_corpus.py
    # production (Render shell on 3d-platform-api):
    python scripts/seed_policy_corpus.py

Each manifest URL is verified at runtime (content-type + size); a failed
download is REPORTED and skipped — corpus_status="partial" is a designed state.
Re-running replaces documents idempotently (city, slug, version).
"""

from __future__ import annotations

import sys

import httpx

sys.path.insert(0, ".")  # allow `app.` imports when run from backend/

from app.services.policy_intelligence.ingest import ingest_policy_pdf  # noqa: E402
from app.tasks.processing import _get_sync_session  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

CITY = "calgary"

# Sources per docs/MUNICIPAL_POLICY_SPATIAL_AI_RESEARCH_2026_06_25.md §9.
# URLs are best-known; this script IS the verifier — failures are reported.
MANIFEST = [
    {
        # NOTE: the council-policy-library lup009 PDF is a 2-page cover sheet;
        # this is the actual MDP 2020 volume (~200 pages).
        "slug": "mdp-lup009",
        "title": "Municipal Development Plan 2020 (LUP009)",
        "instrument_type": "statutory",
        "url": "https://www.calgary.ca/content/dam/www/pda/pd/documents/municipal-development-plan/mdp-municipal-development-plan.pdf",
    },
    {
        "slug": "csps033-emergency-services",
        "title": "Integration of Emergency Services (CSPS033)",
        "instrument_type": "policy",
        "url": "https://www.calgary.ca/content/dam/www/ca/city-clerks/documents/council-policy-library/csps033-integration-of-emergency-services.pdf",
    },
    {
        "slug": "tp021-complete-streets",
        "title": "Complete Streets Policy (TP021)",
        "instrument_type": "policy",
        "url": "https://www.calgary.ca/content/dam/www/ca/city-clerks/documents/council-policy-library/tp021-complete-streets-policy.pdf",
    },
    {
        "slug": "tp012-calgary-transportation-plan",
        "title": "Calgary Transportation Plan (TP012)",
        "instrument_type": "statutory",
        "url": "https://www.calgary.ca/content/dam/www/ca/city-clerks/documents/council-policy-library/tp012-calgary-transportation-plan-and-policies.pdf",
    },
    {
        "slug": "climate-strategy-2050",
        "title": "Calgary Climate Strategy — Pathways to 2050",
        "instrument_type": "strategy",
        "url": "https://www.calgary.ca/content/dam/www/uep/esm/documents/esm-documents/climate-strategy-pathways-to-2050.pdf",
    },
    {
        "slug": "home-is-here-housing-strategy",
        "title": "Home is Here — The City of Calgary's Housing Strategy 2024-2030",
        "instrument_type": "strategy",
        "url": "https://www.calgary.ca/content/dam/www/programs-services/property-housing-and-neighbourhoods/housing-in-calgary/housing-strategy/calgary-housing-strategy-full.pdf",
    },
]


def _download(url: str) -> bytes | None:
    try:
        response = httpx.get(url, timeout=120.0, follow_redirects=True,
                             headers={"User-Agent": "cityprompt-policy-seeder"})
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        print(f"    DOWNLOAD FAILED: {exc}")
        return None
    content_type = response.headers.get("content-type", "")
    body = response.content
    if "pdf" not in content_type and not body[:5].startswith(b"%PDF"):
        print(f"    NOT A PDF (content-type={content_type!r}, {len(body)} bytes)")
        return None
    if len(body) < 50_000:
        print(f"    SUSPICIOUSLY SMALL ({len(body)} bytes) — skipping")
        return None
    return body


def main() -> None:
    session = _get_sync_session()
    seeded, skipped = [], []
    try:
        for entry in MANIFEST:
            print(f"\n=== {entry['slug']} ===\n    {entry['url']}")
            pdf_bytes = _download(entry["url"])
            if pdf_bytes is None:
                skipped.append(entry["slug"])
                continue
            try:
                document = ingest_policy_pdf(
                    session,
                    city=CITY,
                    slug=entry["slug"],
                    title=entry["title"],
                    instrument_type=entry["instrument_type"],
                    source_url=entry["url"],
                    pdf_bytes=pdf_bytes,
                )
                print(f"    OK: {document.page_count} pages, {len(document.chunks)} chunks")
                seeded.append(entry["slug"])
            except Exception as exc:  # noqa: BLE001
                session.rollback()
                print(f"    INGEST FAILED: {exc}")
                skipped.append(entry["slug"])
    finally:
        session.close()

    print(f"\nSeeded {len(seeded)}: {seeded}")
    print(f"Skipped {len(skipped)}: {skipped}")
    if not seeded:
        sys.exit(1)


if __name__ == "__main__":
    main()
