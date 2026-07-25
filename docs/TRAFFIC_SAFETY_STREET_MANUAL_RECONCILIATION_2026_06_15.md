# Traffic-Safety Archetypes ↔ Calgary Street Manual Chapter 10 — Reconciliation
**Date:** 2026-06-15
**Trigger:** User (City of Calgary planner) supplied the full Street Manual — **Draft 4.0a** (146 pp, Oct 2025, full content) and **Draft 4.B** (117 pp, Mar 2026, *new* Ch 9 Intersections/Crossings + Ch 10 Retrofit & Traffic Calming). Copied to `artifacts/street-manual/Street_Manual_Draft_4.0A.pdf` / `_4.0B.pdf` (gitignored scratch).
**Scope of this doc:** Chapter 10 (Retrofit & Traffic Calming) only, per user direction ("Ch 10 calming/retrofit first"). Chapter 9 (intersections/crossings) reconciliation is deferred to a later pass.

---

## 0. The reframe (why this is a reconciliation, not net-new build)

The `traffic_safety_vision_zero` category **already exists with 20 archetypes**, fully dimensioned via `docs/TRAFFIC_SAFETY_DIMENSION_STANDARDS_2026_06_14.md` (clauses in `scripts/_traffic_safety_dims.py`, appended to prompts by `scripts/_patch_traffic_safety_dimensions.py`). Those dimensions were sourced from **NACTO / FHWA / TAC + City of Calgary web pages** — because the Street Manual was not yet available.

Chapter 10 is now **Calgary's own official version of that toolkit.** This matters: City engineers will check renders against *their* manual, not generic NACTO. So the job is to reconcile the existing 20 against Ch 10's **Table 10.19 (suitability matrix)**, **§10.4 (treatment definitions)**, and **§10.3 (design-domain / constrained widths)**.

**Good news:** the set is ~80% aligned, and Ch 10 *confirms* the Calgary conventions already baked in — 40 km/h residential default, playground (not school) zones at 30 km/h, no speed tables in 30-zones → 4.0 m humps, 5 m daylighting clearance. No change needed there.

---

## 1. Authoritative crosswalk — Table 10.19 ↔ existing archetypes

Table 10.19 "Traffic Calming Element Suitability" defines **16 elements in 3 families**. Suitability key: **Y** = suitable, **M** = may be suitable, blank = not listed for that class.

| Ch 10 element | §ref | Local / Collector / Arterial | Existing archetype | Status |
|---|---|---|---|---|
| **Vertical deflection** | | | | |
| Raised Crossing | 10.4.3.1 | Y / Y / M | `raised_crossing_collector` | ⚠ rename (drop class pin) |
| Continuous Crossing | 10.4.3.1 | Y / Y / — | `continuous_sidewalk_street` | ⚠ rename + concept fix |
| Raised Intersection | 10.4.3.1 | Y / Y / M | `raised_intersection` | ✓ aligned |
| Speed Hump | 10.4.3.2 | Y / M / — | *(folded into `traffic_calmed_local_street`)* | ➕ gap: standalone |
| Speed Table | 10.4.3.2 | Y / Y / M | `traffic_calmed_local_street` | ⚠ Calgary: not used in 30-zones |
| Speed Cushion | 10.4.3.3 | Y / Y / — | `speed_cushion_street` | ✓ aligned |
| **Horizontal deflection** | | | | |
| Curb Extension | 10.4.4.1 | Y / Y / M | `curb_extension_crossing_street` | ✓ aligned (broaden class) |
| Two-Stage Crossing Median (Pedestrian Refuge) | 10.4.4.2 | Y / Y / M | `refuge_island_arterial` | ⚠ rename (not arterial-only) |
| Chicane | 10.4.4.3 | Y / — / — | *(folded into `traffic_calmed_local_street`)* | ✓ scope OK |
| Roundabout | 10.4.4.4 | M / Y / M | `compact_safety_roundabout` | ✓ (state class scope) |
| High-Entry Angle Right Turn | 10.4.4.5 | — / M / Y | *(none)* | ➕ **gap** |
| **Obstruction** | | | | |
| Right-In/Right-Out Access Median | 10.4.5.1 | — / M / Y | *(none)* | ➕ **gap** |
| Left Turn Calming | 10.4.5.2 | — / Y / Y | `left_turn_calming_intersection` | ✓ aligned |
| Diverter | 10.4.5.3 | Y / — / — | `modal_filter_diverter` | ✓ (Calgary term) |
| Directional Closure | 10.4.5.3 | Y / M / — | *(partial in `modal_filter_diverter`)* | ➕ **gap** |
| Full Closure | 10.4.5.3 | Y / — / — | *(partial in `school_street`)* | ➕ **gap** |

**Existing archetypes NOT in Table 10.19** (valid NACTO/FHWA treatments; Calgary covers them in Ch 5/8/9 or as corridor reconfigurations — leave as-is, no Ch 10 conflict): `road_diet_complete_street`, `protected_intersection` (Ch 9.9), `pedestrian_scramble_intersection`, `daylighted_intersection`, `floating_bus_stop_transit_street` (Ch 5/transit), `neighborhood_greenway` (Ch 5.2.3 local street bikeway), `advisory_bike_lane_street` (Ch 5.2.4), `neighborhood_gateway` (Ch 10.4.2 gateway concept), `school_street` (playground-zone policy).

---

## 2. The four buckets of change

### Bucket 1 — Terminology (align display names to Calgary's official vocabulary)
*Safe edit: change `title`, `description`, and `renderPrompt` text only. **Keep `id`, `thumbnailUrl`, variant ids, and image folders unchanged** — `thumbnailUrl` is an explicit id-based path and nothing re-slugifies the title at runtime, so display renames don't move images. Do NOT regenerate images under a new title without also renaming the folder (slug-mismatch trap — see Landmines).* Add a `calgaryStreetManualRef` string for traceability.

| id (unchanged) | title → | Calgary §ref | Note |
|---|---|---|---|
| `refuge_island_arterial` | **Two-Stage Crossing Median (Pedestrian Refuge)** | §10.4.4.2 | Calgary's official name; applies Local + Collector + Arterial(M), not arterial-only |
| `continuous_sidewalk_street` | **Continuous Crossing** | §10.4.3.1 | Calgary distinction: *material continuation of the walking/wheeling zone, typically **no marked crosswalk***; at side-street/alley mouths. It's a *sub-type of raised crossing.* Ensure prompt says "unmarked / continuous paving." |
| `raised_crossing_collector` | **Raised Crossing** | §10.4.3.1 | Drop the "Collector" pin — Local Y, Collector Y, Arterial M |
| `modal_filter_diverter` | **Diverter (Modal Filter)** | §10.4.5.3 | Keep as the *diverter* representative; Directional + Full Closure split out as gap-fill (Bucket 3) |

### Bucket 2 — Suitability (street-class scope per Table 10.19 / §10.4)
*Safe edit: `description`/`renderPrompt`/width-range text. No id/image change.*

| id | Correction | §ref |
|---|---|---|
| `neighborhood_traffic_circle` | **Local × Local intersections only**; typically **no splitter islands**; fits *within the existing intersection footprint*. (Current prompt is close — confirm "no splitter islands, local-only.") | §10.4.4.4 |
| `compact_safety_roundabout` | State scope: **Collector & Arterial**; *preferred form for Collector × Collector.* | §9.8, §10.4.4.4 |
| `curb_extension_crossing_street` | Broaden: Local Y, Collector Y, Arterial M (currently reads crossing-centric). | §10.4.4.1 |
| `traffic_calmed_local_street` (chicane + table sub-elements) | Chicane = **Local** (Collector w/o transit *may* be suitable). **Speed tables are not used in Calgary 30-zones** → lean the local device on the 4.0 m hump; keep the table mention for Collector context only. | §10.4.4.3, §10.4.3.2 |
| `speed_cushion_street` | Confirm scope Local + Collector (cushions = the bus/fire-route device; humps = the pure-local device). | §10.4.3.3 |

### Bucket 3 — Coverage gaps (author as new archetypes; Phase 2, pilot one first)
Same authoring pattern as the existing 20 + Calgary Street Manual set: text-splice into `streetPathArchetypes.json`, no hero, `thumbnailUrl`→`variant_0.png`, slug = `_slugify(title)`, GRAY shade family, dimension clause from a new `_traffic_safety_dims.py` entry, then card + section + aerial imagery.

| New archetype | Calgary §ref | Class (Table 10.19) | Render-critical content |
|---|---|---|---|
| **High-Entry Angle Right Turn** | §10.4.4.5, §9.7.3.1, Fig 9.5 | Collector(M) / Arterial(Y), non-High-Activity | Channelized right-turn island with a **near-perpendicular (high) entry angle**, slow yield-condition turn, pedestrian/wheeling crossing of the island, defined paths via geometry + markings |
| **Right-In/Right-Out Access Control Median** | §10.4.5.1 | Collector(M) / Arterial(Y) | Continuous raised median blocking left-turn + through movements from minor approaches / commercial driveways; channelizes to right-in/right-out only |
| **Speed Hump (Local)** | §10.4.3.2, Fig (hump) | Local(Y) / Collector(M, no transit) | Calgary's **4.0 m rounded local hump**, 75–90 mm; placement ≥10 m from crossings, ≥75 m from signals; the preferred 30-km/h local device (vs the bus-route cushion) |
| **Directional / Full Closure** | §10.4.5.3, Fig 10.15/10.16 | Local(Y); Directional also Collector(M) | Volume-management closures: directional restricts through/left movements; full closure terminates a leg with a turnaround; emergency-access mountable/removable; reduces short-cutting |

*Decision to confirm with user:* author Directional + Full Closure as **one** archetype (two variants) or **two** entries. Calgary lists them as distinct rows but groups them in one § (10.4.5.3) with the diverter.

### Bucket 4 — Dimensions & context (Phase 3 — needs the figures read)
Calgary-official refinements to fold into the dimension clauses once verified against the drawings:

- **Placement rules (§10.4.3.2, §10.4.2):** humps/tables **≥10 m from crosswalks/multi-use crossings/intersections**, **≥75 m from signalized intersections**; not in front of driveways/accessible parking/residential windows. Traffic-calming **spacing ≤100 m** (not exceeding 125 m) for speed; **200–400 m** for volume-management closures/diverters.
- **§10.3 Design-Domain (constrained) widths** (PDF p85–94): Calgary's official *minimum/constrained* zone widths (frontage, walking/wheeling, furnishing, curbside, travelled-way, median) for retrofit conditions — the authoritative source to cite in `road_diet_complete_street` and any constrained-retrofit variant, replacing generic NACTO minimums.
- **Confirmed-as-correct (no change):** 40 km/h residential default; playground zones 30 km/h 7:30 a.m.–9 p.m.; speed tables not used in Calgary 30-zones; 5 m daylighting clearance; raised crossing/intersection 80 mm @ ~6% ramps.

#### Phase-3 figure-read checklist (read via `scripts/_render_sm_page.py <page> [scale] [crop]`, Draft 4.B)
| Figure | Page | Verifies archetype number |
|---|---|---|
| Fig 10.1 Raised Crossing (mid-block + intersection) | ~99 | `raised_crossing_collector` 80 mm / 6.5 m / 2.0 m@6% |
| Fig 10.3 Raised Intersection | ~101 | `raised_intersection` plateau/ramps/min crosswalk 2.5 m |
| Fig 10.5 Speed Table (+ hump dims) | ~103 | `traffic_calmed_local_street` table; new Speed Hump |
| Fig 10.6 Speed Cushion | ~104 | `speed_cushion_street` pad/gap |
| Fig 10.7 Curb Extension (mid-block + intersection) | ~106 | `curb_extension_crossing_street` depth |
| Fig 10.8 Two-Stage Crossing Median | ~108 | refuge width / cut-through / nose |
| Fig 10.9 Chicane | ~109 | chicane lateral shift |
| Fig 10.x Roundabout / Traffic Circle | ~110–111 | circle dia / apron / splitter |
| Fig 9.5 High-Entry Angle Right Turn | (Ch 9) | new High-Entry archetype |
| Fig 10.15 / 10.16 Directional / Full Closure | ~116 | new Closure archetype(s) |
| §10.3 tables | 85–94 | constrained widths for road-diet/retrofit |

---

## 3. Phased plan

- **Phase 1 — Terminology + Suitability** (this pass, low-risk, no re-render): Buckets 1 & 2. Backup `streetPathArchetypes.json` → `.bak-ts-reconcile`; text-level Edits to `title`/`description`/`renderPrompt` + add `calgaryStreetManualRef`; keep ids/images. Validate: archetype count unchanged (95), all 20 ts ids + thumbnailUrls byte-identical, JSON parses, no dup ids. **Never json.dump.**
- **Phase 2 — Coverage gaps** (Bucket 3): pilot ONE new archetype end-to-end (recommend **Speed Hump (Local)** — simplest, pure Calgary device), review inline, then author the other 3. New `_traffic_safety_dims.py` clauses + card/section/aerial imagery (Style 6 / Gemini 3.1 per `[[feedback_style6_card_pipeline]]`).
- **Phase 3 — Dimension reconciliation** (Bucket 4): execute the figure-read checklist; correct any baked-in number that differs from Calgary's drawings; add §10.3 constrained widths; re-cite the Street Manual in clauses.

---

## 4. Landmines
- **NEVER `json.dump` the archetype JSON** — corrupts thumbnailUrl paths. Text-level splice/Edit only. (`[[feedback_json_dump]]`)
- **Slug-mismatch trap:** image folders are id-based (`/archetypes/streets/<id-hyphenated>/`). Renaming a `title` is display-only and safe *now*, but the generation scripts use `_slugify(title)` → regenerating imagery under a renamed title creates a *new* folder the stored `thumbnailUrl` won't point to. If a renamed archetype ever needs new imagery, rename the folder + thumbnailUrl together. (`[[feedback_archetype_slug_mismatch]]`)
- **Backup before the splice** (`.bak-ts-reconcile`) for one-line rollback. Validate non-target archetypes are byte-identical after.
- **Dimensions are provisional until Phase 3:** §10.4 text is largely qualitative; the hard numbers live in Figures 10.1–10.16 (vector) — do not assert exact Calgary dimension matches before reading them.
- **Draft status:** 4.B is "FOR DISCUSSION (March 2026)", under internal review; Appendix A summary tables and the compiled standard-intersection/cross-section drawing PDFs are *circulated separately* and still being developed. Numbers may shift before Draft 5.

## 5. Source map
- Suitability matrix: **Table 10.19** (Draft 4.B p96).
- Treatment definitions/context: **§10.4.3** vertical (p98–104), **§10.4.4** horizontal (p105–112), **§10.4.5** obstruction (p113–116).
- Spacing/placement: **§10.4.2** (p97).
- Constrained widths: **§10.3** (p85–94). Retrofit priorities by class: **§10.2** (p73–84).
- Existing archetype dims: `docs/TRAFFIC_SAFETY_DIMENSION_STANDARDS_2026_06_14.md`. Prioritized viz list: `docs/TRAFFIC_SAFETY_VISUALIZATION_RESEARCH_2026_06_12.md` (§6).
