# Urban DNA — Candidate Dataset Research: Findings (Free vs Paid)

*2026-07-07. Deep-research run (110 agents, 28 sources fetched, 126 claims extracted, 25 adversarially verified 3-vote, 23 confirmed / 2 refuted). Companion to [URBAN_DNA_DATASET_RESEARCH_PROMPT_2026_07_07.md](./URBAN_DNA_DATASET_RESEARCH_PROMPT_2026_07_07.md).*

> **Verification legend.** `VERIFIED-LIVE` = live catalog/API metadata (and, for Socrata, a live SoQL query) hit this session. `CATALOG-LISTED` = source page exists and was read, but the geometry column / spatial query was not independently confirmed. **Every Socrata id below must still be re-run through `scripts/verify_calgary_datasets.py` at integration time** — the whole reason this discipline exists is the stale-but-authoritative `mw9j-jik5` land-use id.

---

## TL;DR

- **Environment** (near-empty today, top priority) has **four strong free fills**: Alberta flood hazard polygons, NRCan HRDEM LiDAR terrain, Calgary Public Trees, Calgary Air Quality — all commercially licensed for a SaaS.
- **Market** (also near-empty) splits cleanly: **free public sources give indicators only** (CMHC vacancy/rent tables, StatCan cubes) at coarse geographies with **no polygon query**; **transactional depth** (sales comps, absorption, development pipeline, purpose-built rental) is **paid** — Altus and Zonda both cover Calgary, **pricing on request, embedding rights not published**.
- The tool's existing Socrata `intersects()` mechanism is **confirmed correct and reusable** — the only per-dataset gate is verifying the geometry column is a real `point`/`line`/`polygon` type, not the legacy `location` type (which fails polygon queries).

---

## 1. FREE datasets (integrate first)

### Environment (highest-value gap)

| Dataset | Provider | ID / URL | Access | Geometry | Licence | Status | DNA fields |
|---|---|---|---|---|---|---|---|
| **Alberta FHIP Flood Hazard Mapping** | Gov. of Alberta | [open.canada.ca d192b9b1](https://open.canada.ca/data/en/dataset/d192b9b1-caac-405e-8d2a-ba6b21929c3f) | Bulk FGDB-ZIP (~25 MB) **or** [Esri Canada REST mirror](https://services.arcgis.com/wjcPoefzjpzCgffS/arcgis/rest/services/AlbertaFloodMapping_gdb/FeatureServer) (third-party) | Polygon (floodway / flood-fringe) | OGL-Alberta (commercial OK) | VERIFIED-LIVE | `environment.flood_hazard`, floodway/fringe flags |
| **NRCan HRDEM (CanElevation)** | NRCan | [open.canada.ca 957782bf](https://open.canada.ca/data/en/dataset/957782bf-847c-4644-a757-e383c0057995) | **STAC API** (bbox/polygon) + ESRI REST; tiles are COG-GeoTIFF | 1–2 m raster DEM | OGL-Canada (commercial OK) | VERIFIED-LIVE | `environment.slope`, `environment.ground_elevation` (upgrade from current LiDAR-derived proxy) |
| **Calgary Public Trees** | City of Calgary | [tfs4-3wwa](https://data.calgary.ca/Environment/Public-Trees/tfs4-3wwa) | Socrata SoQL (live query confirmed) | **point** | OGL-Calgary | VERIFIED-LIVE | `environment.tree_density`, canopy proxy; attrs DBH/genus/species/condition/heritage/appraised value |
| **Calgary Air Quality (near real-time)** | City of Calgary / CRAZ | [g9s5-qhu5](https://data.calgary.ca/Environment/Air-Quality-Data-near-real-time-/g9s5-qhu5) | Socrata SoQL (live query confirmed) | **point** (fixed stations) | OGL-Calgary | VERIFIED-LIVE | `environment.air_quality` (nearest-station, not a surface) |
| **ClimateData.ca projections** | ECCC + PCIC/Ouranos/etc. | [climatedata.ca/download](https://climatedata.ca/download/) | Bulk + API; ~6–10 km grid | Grid | ⚠️ **Per-source, heterogeneous** | VERIFIED-LIVE | `environment.climate_projections` — **legal review before shipping** (see §3) |

### Mobility & safety (fill gaps)

| Dataset | ID / URL | Geometry | Status | Note |
|---|---|---|---|---|
| **Calgary Transit GTFS-RT** Vehicle Positions | [am7c-qe3u](https://data.calgary.ca/Transportation-Transit/Calgary-Transit-Realtime-Vehicle-Positions-GTFS-RT/am7c-qe3u) (+ Trip Updates gs4m-mdc2, Alerts jhgn-ynqj) | feed | CATALOG-LISTED | Static GTFS gives **headways/frequency** — upgrades our stop-count metric to service-level. Needs the planned GTFS adapter. |
| **Calgary Traffic Incidents** | [35ra-9556](https://data.calgary.ca/Transportation-Transit/Traffic-Incidents/35ra-9556) | **point** | VERIFIED-LIVE | Vision-Zero / safety proxy; spatially queryable. |
| **Calgary Community Crime Statistics** | [78gh-n26t](https://data.calgary.ca/Health-and-Safety/Community-Crime-Statistics/78gh-n26t) | **none (community NAME)** | VERIFIED-LIVE | ⚠️ **Not polygon-queryable** — join by community name only. See dead-end log. |

### Demographics & built-form fallback (multi-city)

| Dataset | ID / URL | Access | Geometry | Licence | Status |
|---|---|---|---|---|---|
| **StatCan 2021 Census Boundary Files** (92-160-X) + WDS statistical API | [WDS guide](https://www.statcan.gc.ca/en/developers/wds/user-guide) / [92-160-G](https://www150.statcan.gc.ca/n1/pub/92-160-g/92-160-g2021001-eng.htm) | Boundary files (shp/GeoJSON) for geometry; WDS cubes for values (anonymous, 25 req/s/IP) | DA/DB **polygon** | StatCan Open Licence (commercial OK) | VERIFIED-LIVE — WDS is **non-spatial**, geometry via separate boundary channel |
| **CensusMapper / cancensus** | [censusmapper.ca/api](https://censusmapper.ca/api) | REST wrapper, 1996–2021, fine geography | polygon | Freemium (free key) | CATALOG-LISTED — national demographics fallback |
| **Overture Maps buildings** | [docs.overturemaps.org](https://docs.overturemaps.org/getting-data/) | Cloud GeoParquet, **bbox query** (no full download) | polygon | CDLA / community | CATALOG-LISTED — global built-form fallback |
| **Microsoft Canadian Building Footprints** | [github.com/microsoft/CanadianBuildingFootprints](https://github.com/microsoft/CanadianBuildingFootprints) | Bulk GeoJSON (AB = 1.78 M) | polygon | ODbL | CATALOG-LISTED — national fallback when a city lacks a 3D-buildings layer |

---

## 2. PAID datasets — the market-depth tier

Free portals **cannot** provide transactional / pipeline market data. These vendors can; both were confirmed to cover Calgary + our multi-city targets, but **no pricing is published and — more importantly — SaaS-embedding/redistribution rights are not published.** Treat embedding as *not granted* until a redistribution licence is negotiated.

| Vendor | Coverage (confirmed) | What it buys | Pricing | Status |
|---|---|---|---|---|
| **Altus Data Studio** | Vancouver, Calgary, Edmonton, GTA, GGH, Ottawa, Gatineau, Montreal (**not Winnipeg**) | 180K+ CRE transactions, 50K+ office/industrial leasing, 11K+ new-home projects, dev-application monitoring | **On request** | VERIFIED-LIVE (coverage + data types) |
| **Zonda Urban (NHSLive)** | Calgary & Edmonton + BC/Prairies/ON/QC/Maritimes | Absorption & value for multifamily + rental; land transactions; "only regularly-updated purpose-built rental data in Canada" | **On request** | VERIFIED-LIVE (coverage + scope) |
| **StreetLight Data** | US + Canada | Mobility/OD analytics | **On request** | CATALOG-LISTED |
| **Walk Score API** | US + Canada (Calgary in scope) | Walk / Transit / Bike Score | Published tiers (pro page) | CATALOG-LISTED |

**Why pay:** the free market sources answer "what's the vacancy rate in this CMA?" The paid ones answer "what did comparable sites trade for, how fast are units absorbing, what's in the development pipeline within this block?" — the transactional/pipeline granularity a proforma or feasibility view needs. That depth is the entire case for a paid tier; verify the embedding licence before building on it.

---

## 3. Licensing flags

- **OGL-Alberta / OGL-Canada / StatCan Open Licence / OGL-Calgary** all permit commercial use and redistribution of derived analysis — **clear to embed.** Attribution is mandatory (e.g. "Contains information licensed under the Open Government Licence – Canada"); omitting it auto-terminates the licence.
- **ClimateData.ca is the one open-source with a real snag.** A blanket "commercial use prohibited" reading was **refuted 0-3** — it is *not* categorically blocked. But (a) each dataset inherits its **source org's** licence (ECCC/CanDCS-M6 vs Ouranos vs PCIC differ) and (b) the portal Terms add a commercial-exploitation clause. **Per-dataset legal review before any climate layer ships** — do not treat as fully-open or fully-blocked.
- **Paid vendors:** standard subscriptions typically grant *internal analyst* use, not third-party-SaaS embedding. This is the gating question, not price.

---

## 4. Recommended integration order

Ranked by (DNA value × section weakness ÷ integration effort); free outranks paid at equal value.

1. **Calgary Public Trees** (tfs4-3wwa) — same Socrata adapter, real point geometry, fills environment. Suggested confidence weight ~0.9. *Lowest-effort win.*
2. **Alberta FHIP flood hazard** — high planning value (floodway = hard constraint). Effort: bulk FGDB extract-and-cache, or lean on the Esri mirror with a supportability caveat. Weight ~0.9.
3. **Calgary Air Quality** (g9s5-qhu5) — cheap Socrata add; weight ~0.6 (point stations, not a surface).
4. **NRCan HRDEM slope** — STAC API is a genuinely new adapter but reusable nationally; upgrades environment + built-form grading. Weight ~0.8.
5. **Calgary Traffic Incidents** (35ra-9556) — Socrata point, safety proxy for mobility. Weight ~0.7.
6. **StatCan Census (boundary files + WDS)** — opens the whole demographics dimension; two-channel (geometry + values) integration. Weight ~0.85.
7. **GTFS static/RT** — headway metrics; needs the planned GTFS adapter. Weight ~0.8.
8. **Overture / MS building footprints** — multi-city fallback, not needed for Calgary (we have cchr-krqg). Weight ~0.7 for cities without a 3D layer.
9. **Paid market (Altus or Zonda)** — highest *market-section* value but gated on pricing **and** embedding licence; a procurement task, not an eng task.

---

## 5. Multi-city matrix (for city #2/#3)

| Category | Calgary | Edmonton | Vancouver | Toronto | National fallback |
|---|---|---|---|---|---|
| Zoning / land use | Socrata qe6k-p9nh ✓ | Socrata (Open Edmonton) | [OpenDataSoft Explore API, GeoJSON polygon](https://vancouver.opendatasoft.com/explore/dataset/zoning-districts-and-labels/custom/) | [CKAN zoning-by-law 569-2013](https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/zoning-by-law) | — |
| Buildings | Socrata cchr-krqg ✓ | Socrata | ArcGIS | CKAN | Overture / MS footprints |
| Demographics | — | — | — | — | StatCan Census + CensusMapper (all cities) |
| Terrain | — | — | — | — | NRCan HRDEM (all metros) |
| Flood | Alberta FHIP | Alberta FHIP | prov. BC | prov. ON | provincial programs |
| Market (paid) | Altus + Zonda | Altus + Zonda | Altus | Altus | Altus (not Winnipeg) |

**Adapter implication:** Calgary/Edmonton stay on Socrata; **Vancouver = OpenDataSoft**, **Toronto = CKAN**, national environment = **STAC (HRDEM)** and **ArcGIS REST (FHIP mirror)**. The planned ArcGIS adapter covers some but **not all** — an OpenDataSoft/CKAN and a STAC path are also needed for full national coverage.

---

## 6. Dead-end log (do not re-research)

- **Calgary Community Crime Statistics (78gh-n26t)** — has **no geometry**; crime counts aggregated by community *name*. Usable only by name-join, **not** site-polygon intersection. (Point-level crime, if needed, is not in this dataset.)
- **CMHC Rental Market Survey / StatCan WDS** — real and free, but **no spatial API**: geography is a table dimension, not geometry. Fine for CMA/CSD-level context; cannot answer a site-polygon query. (The finer HMIP survey-zone geography exists but is not exposed as a queryable spatial API.)
- **CoStar terms page** — flagged unreliable/unreadable by the fetcher; no usable pricing or licence detail extracted. Revisit directly if CoStar becomes a candidate.

---

## 7. Open questions before building

1. **Paid embedding rights** (Altus & Zonda): does the licence permit *displaying* derived market data inside a commercial SaaS, or internal use only? This gates whether paid market data is usable at all. → procurement call.
2. **ClimateData.ca per-dataset audit**: which specific layers (ECCC/CanDCS-M6 under OGL-Canada?) are commercially redistributable, and does the portal clause bind the underlying data or only the website presentation?
3. **Geometry-type verification** of the still-unconfirmed Socrata candidates (building/development permits, business licences, heritage inventory, 311) — `point`/`polygon` vs failing `location` — via the verify script.
4. **Adapter scope**: confirm whether ArcGIS-REST alone reaches national fallback, or whether OpenDataSoft + CKAN + STAC adapters are also required (see §5).
