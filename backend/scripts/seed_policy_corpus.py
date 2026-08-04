"""Seed per-city policy corpora from live municipal URLs.

Run INSIDE the backend container/image (PDFs are never committed to the repo).
Lives under backend/scripts/ so it ships in the production image
(render.yaml builds with dockerContext ./backend, and the production DB is
internal-only — a Render shell on the API service is the ONLY place this can
run in production):
    # local Docker:
    docker exec -w /app devplatform-backend python scripts/seed_policy_corpus.py --city edmonton
    # production (Render shell on 3d-platform-api):
    python scripts/seed_policy_corpus.py            # default: all cities

Each manifest URL is verified at runtime (content-type + size); a failed
download is REPORTED and skipped — corpus_status="partial" is a designed state.
Re-running replaces documents idempotently (city, slug, version).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx

sys.path.insert(0, ".")  # allow `app.` imports when run from backend/

from app.services.policy_intelligence.ingest import ingest_policy_pdf  # noqa: E402
from app.tasks.processing import _get_sync_session  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# URLs are best-known; this script IS the verifier — failures are reported.
# Calgary sources per docs/MUNICIPAL_POLICY_SPATIAL_AI_RESEARCH_2026_06_25.md §9.
# Edmonton sources per the 2026-07-10 multi-city research pass.
MANIFESTS: dict[str, list[dict]] = {
    "calgary": [
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
    ],
    "edmonton": [
        {
            "slug": "city-plan",
            "title": "The City Plan (Charter Bylaw 20000)",
            "instrument_type": "statutory",
            "url": "https://www.edmonton.ca/sites/default/files/public-files/assets/PDF/City_Plan_FINAL.pdf",
        },
        {
            # District Policy + the 15 District Plans consolidated; district
            # names arrive in DNA via the neighbourhoods layer's `district`
            # attribute, which is what retrieval keys on.
            "slug": "district-policy-consolidation",
            "title": "District Policy Consolidation (Charter Bylaw 21472)",
            "instrument_type": "statutory",
            "url": "https://webdocs.edmonton.ca/infraplan/plans_in_effect/District-Policy-Consolidation.pdf",
        },
        {
            # Uses-by-zone matrix for Zoning Bylaw 20001; the per-zone regulation
            # pages are HTML (see scripts/seed_edmonton_zone_pages.py).
            "slug": "zoning-bylaw-land-use-matrix",
            "title": "Zoning Bylaw 20001 — Land Use and Zoning Matrix",
            "instrument_type": "statutory",
            "url": "https://www.edmonton.ca/sites/default/files/public-files/Edmonton-Zoning-Bylaw-Land-Use-and-Zoning-Matrix.pdf",
        },
        {
            "slug": "climate-resilient-edmonton",
            "title": "Climate Resilient Edmonton — Adaptation Strategy and Action Plan",
            "instrument_type": "strategy",
            "url": "https://www.edmonton.ca/sites/default/files/public-files/assets/Climate_Resilient_Edmonton.pdf",
        },
    ],
    # NOTE (verified 2026-07-12): vancouver.ca / bylaws.vancouver.ca /
    # guidelines.vancouver.ca serve PDFs to real browsers but 403 every
    # non-browser client (WAF fingerprinting — browser UA + host TLS both
    # blocked). Seed Vancouver via --from-dir: download the manifest URLs in a
    # browser into a folder named <slug>.pdf and pass that folder.
    "vancouver": [
        {
            # Citywide ODP in effect ~2026-03 (Vancouver Charter amendment);
            # zoning/development decisions must be consistent with it.
            "slug": "official-development-plan",
            "title": "Vancouver Official Development Plan (2026)",
            "instrument_type": "statutory",
            "url": "https://vancouver.ca/files/cov/vancouver-official-development-plan.pdf",
        },
        {
            "slug": "zoning-bylaw-general-regulations",
            "title": "Zoning & Development By-law — Section 2 General Regulations",
            "instrument_type": "statutory",
            "url": "https://bylaws.vancouver.ca/zoning/zoning-by-law-section-2-general-regulations.pdf",
        },
        {
            # The post-2023 consolidated low-density residential district
            # (multiplex up to 6 units, 8 if rental).
            "slug": "r1-1-district-schedule",
            "title": "Zoning & Development By-law — R1-1 District Schedule",
            "instrument_type": "statutory",
            "url": "https://bylaws.vancouver.ca/zoning/zoning-by-law-district-schedule-r1-1.pdf",
        },
        {
            # 29 TOAs designated 2024-06-26; 20/12/8 storeys at 200/400/800m of
            # SkyTrain — pairs with the TOA_DENSITY_TIER note in the DNA.
            "slug": "toa-rezoning-policy",
            "title": "Rezoning Policy for Transit-Oriented Areas",
            "instrument_type": "policy",
            "url": "https://guidelines.vancouver.ca/policy-rezoning-transit-oriented-areas.pdf",
        },
        {
            "slug": "broadway-plan",
            "title": "Broadway Plan",
            "instrument_type": "policy",
            "url": "https://vancouver.ca/files/cov/broadway-plan.pdf",
        },
    ],
    # toronto manifest lands with its connector phase.
}


def _download(url: str) -> bytes | None:
    try:
        response = httpx.get(
            url, timeout=120.0, follow_redirects=True, headers={"User-Agent": "cityprompt-policy-seeder"}
        )
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


def _read_local(from_dir: Path, slug: str) -> bytes | None:
    path = from_dir / f"{slug}.pdf"
    if not path.exists():
        print(f"    NOT IN --from-dir ({path.name} missing)")
        return None
    body = path.read_bytes()
    if not body[:5].startswith(b"%PDF"):
        print(f"    NOT A PDF ({path.name}, {len(body)} bytes)")
        return None
    return body


def seed_city(session, city: str, from_dir: Path | None = None) -> tuple[list[str], list[str]]:
    seeded, skipped = [], []
    for entry in MANIFESTS[city]:
        print(f"\n=== {city}/{entry['slug']} ===\n    {entry['url']}")
        if from_dir is not None:
            pdf_bytes = _read_local(from_dir, entry["slug"])
        else:
            pdf_bytes = _download(entry["url"])
        if pdf_bytes is None:
            skipped.append(entry["slug"])
            continue
        try:
            document = ingest_policy_pdf(
                session,
                city=city,
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
    return seeded, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed per-city policy corpora")
    parser.add_argument("--city", choices=[*MANIFESTS, "all"], default="all")
    parser.add_argument(
        "--from-dir",
        help="ingest <slug>.pdf files from this directory instead of downloading "
        "(for WAF-blocked portals like vancouver.ca)",
    )
    args = parser.parse_args()
    cities = list(MANIFESTS) if args.city == "all" else [args.city]
    from_dir = Path(args.from_dir) if args.from_dir else None

    session = _get_sync_session()
    seeded, skipped = [], []
    try:
        for city in cities:
            city_seeded, city_skipped = seed_city(session, city, from_dir=from_dir)
            seeded += [f"{city}/{slug}" for slug in city_seeded]
            skipped += [f"{city}/{slug}" for slug in city_skipped]
    finally:
        session.close()

    print(f"\nSeeded {len(seeded)}: {seeded}")
    print(f"Skipped {len(skipped)}: {skipped}")
    if not seeded:
        sys.exit(1)


if __name__ == "__main__":
    main()
