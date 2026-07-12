# Research Prompt — Candidate Datasets for Urban DNA Analysis (Free vs Paid)

*Authored 2026-07-07. Paste the block below into a Claude research session (or run via deep-research).*

---

## Mission

You are researching external datasets that could extend the **Urban Intelligence DNA** analysis in City Prompt, an AI municipal-planning tool. Given a site boundary polygon, the tool pulls city datasets, runs spatial analysis, and produces an 8-section "Urban DNA" profile (site, land_use, mobility, public_realm, environment, built_form, market, policy) that feeds AI planning agents and scenario generation.

Your job: find datasets we do NOT yet have, **classify each as FREE or PAID** (with actual pricing where published), verify they really exist and are queryable, and rank them by value to the DNA analysis.

## Product context (read before searching)

- **V1 city is Calgary, Alberta**; the architecture is multi-city (Socrata adapter + OSM Overpass fallback exist today; an ArcGIS REST adapter and a GTFS adapter are planned). Datasets that generalize across Canadian cities — or globally — score higher.
- A dataset plugs in as a declarative spec + one transform function. Integration cost is low **if** the source is spatially queryable via API; bulk downloads that must be self-hosted cost more.
- The product is commercial SaaS sold to municipalities and planning consultants. **Licence terms for commercial use matter as much as price.** Canadian data residency is a stated client concern — note where data is hosted/processed.
- Dataset failure never fails generation; each dataset carries a confidence weight. Imperfect data is usable if honestly flagged.

## Already integrated — do NOT re-research these

Calgary Socrata (data.calgary.ca): Land Use Districts (qe6k-p9nh), Parcels/Current Year Property Assessments (4bsw-nn7w), Policy Plan Boundaries ARP/ASP/LAP (yi6d-a7q5), Street Centreline (4dx8-rtm5), Transit Stops (muzh-c9qc) + Routes (hpnd-riq4), Bikeways (jjqk-9b73), Parks Pathways (qndb-27qm), Parks Sites (kami-qbfh), 3D Buildings LiDAR (cchr-krqg). Plus OSM via Overpass as fallback context.

## Known dead-ends — do NOT resurface these as findings

- Calgary publishes **no sidewalk dataset** (confirmed 2026-07-05). A *substitute* (e.g., OSM sidewalk tags, provincial/commercial pedestrian-network data) IS in scope.
- Calgary Land Use dataset mw9j-jik5 is stale/geometry-less; qe6k-p9nh is the live one.

## Technical fit criteria (evaluate every candidate against these)

1. **Spatial queryability**: can we fetch features intersecting a site polygon or bbox via API (SoQL `intersects()`, ArcGIS REST `query`, WFS, Overpass, vector tiles)? Or is it bulk-download only (GeoJSON/Shapefile/GeoPackage/CSV) — and if so, how big is the full extract?
2. **Real geometry** (point/line/polygon). Socrata `location`-type columns fail spatial queries — check column types, not just the catalog page.
3. **Update cadence** and whether the source states it.
4. **Licence**: OGL-Alberta / OGL-Canada / CC-BY / proprietary — and whether it permits commercial redistribution of *derived analysis* (our use) vs raw data.
5. **Auth/cost**: anonymous, free API key, rate limits, or paid tiers.

## Research areas, in priority order

Sections **environment** and **market** are nearly empty today — weight them highest.

### 1. Environment (near-empty: only ground elevation today)
- Flood hazard: Alberta flood hazard mapping, Calgary river flood/overland flow layers, federal flood layers
- Tree canopy / urban forest inventories (Calgary Trees dataset? LiDAR canopy?)
- Terrain: NRCan HRDEM / provincial LiDAR DEM for slope-aspect analysis
- Climate: ClimateData.ca projections, historical normals, urban heat island layers
- Air quality (Alberta Airsheds, federal NAPS), noise mapping if any
- Solar potential, wind, wildfire risk (relevant to Calgary's fire-review angle)
- Contaminated / environmentally sensitive sites

### 2. Market (explicit stub section today)
- CMHC: rental market survey, housing starts/completions, Housing Market Information Portal — API or bulk? free?
- Statistics Canada: building permits, housing price indexes
- Calgary open data: building permits, development permits, business licences (all exist? ids?)
- Teranet–National Bank HPI; CREB/Pillar 9 MLS data (paid — terms?)
- Commercial: CoStar, Altus Group, Zonda/Urban Analytics (Calgary coverage!), local land-value products — pricing model, API availability, licensing for embedding in a SaaS report
- Land titles: Alberta SPIN2 per-parcel costs

### 3. Demographics & social (feeds public_realm/site; no source today)
- StatCan Census profiles at dissemination-area/block level — access path for polygon-based aggregation (are there free APIs or third-party wrappers like CensusMapper/tongfen?)
- Schools (locations + capacity), childcare, community/rec facilities, libraries, healthcare
- Calgary community profiles, equity indexes
- Crime/safety: Calgary Police open data — spatial granularity and licence
- 311 service requests

### 4. Mobility (good coverage; fill gaps)
- Calgary Transit GTFS + GTFS-RT (headways/frequency would upgrade our stop-count metrics)
- Traffic volumes, collision/traffic-incident data (Vision Zero relevance)
- Pedestrian counts; sidewalk substitutes (OSM footway completeness in Calgary?)
- Paid mobility analytics: StreetLight, Replica — Canadian coverage, pricing
- Walk Score API — pricing tiers, terms for display in reports

### 5. Built form & site (good coverage; fill gaps)
- Heritage: Calgary heritage inventory, provincial/federal registers
- Utilities/servicing: water/sewer/storm mains, franchise utility corridors, easements — public anywhere?
- Overture Maps / Microsoft-Google open building footprints (multi-city fallback when a city lacks a 3D-buildings layer)
- Development permit applications in progress (pipeline awareness)

### 6. Policy (RAG corpus exists; spatial policy layers wanted)
- Main Streets, TOD/station-area, established-area growth strategy boundaries, off-site levy zones, airport vicinity protection area, height-restriction overlays (airport/heliport)

### 7. Multi-city generalization
For each *category* above, name the best national-scale (Canada) and global-scale source, so city #2 and #3 don't require bespoke research. Flag which Canadian cities (Edmonton, Vancouver, Toronto, Ottawa, Winnipeg) expose equivalents on Socrata vs ArcGIS Open Data vs CKAN.

## Verification protocol (non-negotiable)

- **Never trust dataset ids or claims from blogs, aggregator sites, or your own memory.** Hit the live catalog/API metadata endpoint for every dataset you recommend. We have been burned by a stale id that looked authoritative.
- For each candidate, mark verification status: `VERIFIED-LIVE` (you fetched metadata/sample rows this session), `CATALOG-LISTED` (page exists, API untested), or `UNVERIFIED` (mentioned in secondary sources only).
- For Socrata datasets, confirm the geometry column name and type. For ArcGIS REST, confirm the layer supports `query` with geometry filters.
- For paid sources with unpublished pricing, say "pricing on request" — do not invent numbers. Cite where any quoted price came from and its date.

## Deliverables

1. **Master table** — every candidate: name · provider · dataset id/URL · coverage · access mechanism (Socrata/ArcGIS/WFS/GTFS/bulk/commercial API) · geometry type · update cadence · licence · **FREE / FREEMIUM / PAID (+price)** · DNA section(s) it feeds · verification status · one-line caveat.
2. **Ranked top-10 shortlist** by (DNA value × section weakness ÷ integration effort). Free sources outrank paid at equal value. For each: which DNA fields it would populate and a suggested confidence weight (0–1).
3. **Paid-data brief** — what paid data buys that free data cannot (esp. market section), with pricing, contract model (seat/API-call/site licence), and any licence terms that restrict embedding outputs in client-facing reports.
4. **Multi-city matrix** — category × {Calgary, Edmonton, Vancouver, Toronto, national fallback}.
5. **Dead-end log** — datasets you checked that do NOT exist, are stale, or fail the technical fit criteria, so we never re-research them.

Cite a URL for every factual claim. Prefer primary sources (the data portal itself, the vendor's pricing page) over articles about them.
