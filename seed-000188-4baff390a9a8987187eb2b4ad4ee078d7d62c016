"""Seed Edmonton Bylaw 20001 zone regulation pages (HTML) into the policy corpus.

Edmonton's zoning layer (fixa-tstc) deep-links every polygon to its zone's
structured HTML page on zoningbylaw.edmonton.ca — the highest-precision zoning
text of any supported city. This script enumerates the distinct standard +
special-area zone pages from the live dataset and ingests each as a
`zoning_rule` document slugged `zone-<code>`, so BM25 retrieval (which keys on
district codes) surfaces exactly the applicable zone's regulations.

Per-provision DC/DC1/DC2 pages (~900 of them, one per site) are intentionally
excluded — fetch-on-demand is a designed future enhancement.

Run INSIDE the backend container:
    docker exec -w /app devplatform-backend python scripts/seed_edmonton_zone_pages.py
"""

from __future__ import annotations

import json
import sys
import urllib.parse

import httpx

sys.path.insert(0, ".")  # allow `app.` imports when run from backend/

from app.services.policy_intelligence.ingest import ingest_policy_html  # noqa: E402
from app.tasks.processing import _get_sync_session  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

CITY = "edmonton"
ZONING_RESOURCE = "https://data.edmonton.ca/resource/fixa-tstc.json"
ZONE_PAGE_PREFIX = "https://zoningbylaw.edmonton.ca/part-"  # standard + special-area zones only


def enumerate_zone_pages() -> list[dict]:
    params = urllib.parse.urlencode({"$select": "zoning,url", "$group": "zoning,url", "$limit": "5000"})
    response = httpx.get(f"{ZONING_RESOURCE}?{params}", timeout=60.0,
                         headers={"User-Agent": "cityprompt-zone-page-seeder"})
    response.raise_for_status()
    pages = [
        {"zoning": row["zoning"], "url": row["url"]}
        for row in json.loads(response.text)
        if (row.get("url") or "").startswith(ZONE_PAGE_PREFIX) and row.get("zoning")
    ]
    # One page per zone code (DC/DC2 multi-page codes are already excluded).
    return sorted(pages, key=lambda p: p["zoning"])


def main() -> None:
    pages = enumerate_zone_pages()
    print(f"{len(pages)} zone pages to ingest")

    session = _get_sync_session()
    seeded, skipped = [], []
    try:
        with httpx.Client(timeout=60.0, follow_redirects=True,
                          headers={"User-Agent": "cityprompt-zone-page-seeder"}) as client:
            for page in pages:
                code = page["zoning"]
                slug = f"zone-{code.lower()}"
                try:
                    response = client.get(page["url"])
                    response.raise_for_status()
                    document = ingest_policy_html(
                        session,
                        city=CITY,
                        slug=slug,
                        title=f"Zoning Bylaw 20001 — {code} Zone Regulations",
                        source_url=page["url"],
                        html=response.text,
                    )
                    print(f"  {slug}: OK ({len(document.chunks)} chunks)")
                    seeded.append(slug)
                except Exception as exc:  # noqa: BLE001 — report and continue; partial is designed
                    session.rollback()
                    print(f"  {slug}: FAILED - {exc}")
                    skipped.append(slug)
    finally:
        session.close()

    print(f"\nSeeded {len(seeded)}, skipped {len(skipped)}")
    if skipped:
        print(f"Skipped: {skipped}")
    if not seeded:
        sys.exit(1)


if __name__ == "__main__":
    main()
