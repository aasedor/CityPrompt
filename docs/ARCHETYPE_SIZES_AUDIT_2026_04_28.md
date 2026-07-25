# Archetype Sizes & Heights Audit — Buildings (2026-04-28)

**Scope:** all 220 building archetypes and their 880 variants in `frontend/src/data/buildingArchetypes.json`. This audit focuses specifically on **recommended size/height accuracy** (footprint dimensions, floor counts, floor heights, areas) and consistency between archetype-level and variant-level metadata.

**Branch:** `feature/merge-codex-ux-onto-stable @ 1900392`.

**Method:** programmatic checks (`scripts/audit_archetype_sizes.py`) over (a) field presence, (b) internal consistency (suggested between min/max, area vs footprint × floors, aspectRatio vs w:d), (c) variant-vs-parent envelope conflicts, (d) typology-realism priors, (e) explicit numeric scale clues from variant descriptions. 376 findings raised, then triaged manually for false positives (typology classifier had ~70% noise on text-pattern-matched calls; the script outputs are kept as a re-runnable signal source but the "real bugs" list below is filtered).

---

## TL;DR — what's actually wrong

The catalog is **mostly accurate at the typology level** — 220/220 archetypes have a sensible suggestedWidth/Depth pair, and most floor counts match the typology of the archetype. The real issues fall into three buckets:

1. **A small number of unambiguous metadata bugs** (1 mislabeled archetype, 5 variant-vs-parent floor conflicts, 1 unit-of-measurement misuse, 2 duplicate archetype pairs).
2. **Schema completeness gaps that match the pre-launch deep dive's #21:** 65 % of variants (575 / 880) have no per-variant scale info; 52 / 220 archetypes have no min/max width/depth ranges.
3. **A field-semantic ambiguity** in `suggestedAreaSqm` — sometimes footprint, sometimes typical floor plate, sometimes total GFA, sometimes "primary use area" (e.g. solar field). This isn't wrong on a per-row basis; it's an unresolved schema decision.

---

## 1 — Hard catalog bugs (fix these first)

### 1.1 `glass_tower_modern` is a tower with mid-rise metadata

| field | value | should be |
|---|---|---|
| `minFloors` / `maxFloors` | **2 – 6** | ~12 – 50 |
| variant scale info | none on any of 4 variants | each variant should have its own range |
| variant labels | `Style Variant 1/2/3/4` (placeholder) | named tower typologies |

The catalog already noted (per `docs/ARCHETYPE_AUDIT_2026_04_26.md`) that this archetype has placeholder variant descriptions and renders well thanks to Gemini's "glass tower" prior — but the **scale metadata still describes a 2–6-storey building**, not a tower. If a user assigns this archetype to a small zone, the rendered building will not be a tower; if they assign it to a large zone the in-app dimensions won't reflect it either.

**Fix:** raise parent floors to `[12, 50]`; add per-variant floors so the four variants span the typology (curved parametric ~30, biophilic terraced ~25, dark monolith ~50, classic slab ~30).

### 1.2 Two archetypes still on the legacy schema (no minFloors/maxFloors at all)

| id | has | needs |
|---|---|---|
| `mall_redevelopment` | only `suggestedWidth_m=150`, `suggestedDepth_m=100` | minFloors / maxFloors / suggestedAreaSqm |
| `terraced_stepped_building` | only `suggestedWidth_m=40`, `suggestedDepth_m=30` | minFloors / maxFloors / suggestedAreaSqm |

These are the two outliers identified in the pre-launch deep dive (issue #18). Both have variant-level scale info already (e.g. `terraced_stepped_building/the_canopy_tower` carries `floors=15-27`), so a parent-level rollup is straightforward:

- `mall_redevelopment` → `minFloors=1, maxFloors=8` (variants span 1–8), `suggestedAreaSqm=50000`
- `terraced_stepped_building` → `minFloors=2, maxFloors=27` (variants span 2–27), `suggestedAreaSqm=8000`

### 1.3 Five variants whose floor range is completely outside the parent's range

| Archetype (parent floors) | Variant | Variant floors | Action |
|---|---|---:|---|
| `nordic_timber_midrise` (4–8) | Contemporary Log Construction | **2–3** | widen parent to 2–8 (this is a real low-rise variant) |
| `mediterranean_arcade_mixed_use` (3–6) | Moorish Arched Souk | **1–2** | widen parent to 1–6 (souks are 1–2 floor) |
| `vernacular_courtyard_housing` (2–4) | Chinese Siheyuan | **1–1** | widen parent to 1–4 (siheyuan are single-storey) |
| `skyline_glass_office_cluster` (20–50) | Low-Rise Glass Campus | **3–6** | widen parent to 3–50 OR move variant to its own archetype (it's not a "skyline cluster") |
| `climbing_wall_building` (1–6) | The Spine | **20–35** | move variant to its own archetype — it's a 30-storey mixed-use tower with a climbing strip, not a climbing facility |

When the user picks an archetype in the UI and the picker shows a variant that the parent's recommended size cannot fit, the resulting render is constrained by the parent range and the variant looks wrong. **This is the highest-impact subset of findings** because every one of the five is a confirmed conflict (no classifier interpretation involved).

### 1.4 `solar_farm_agrivoltaics / csp_tower` — `suggestedFloorHeight = 200 m`

Concentrating-solar tower variant carries `suggestedFloorHeight: 200.0` and `suggestedAreaSqm: 500000`. The 200 m number is **the height of the tower itself**, not the height of one floor — the catalog has no `towerHeight_m` field, so this got crammed into the wrong slot. The 500 000 sqm is the surrounding heliostat field, not the tower footprint.

**Fix:** set `suggestedFloorHeight: 10.0` (the actual receiver-room floor height), keep `minFloors=maxFloors=1`, and either (a) record the true tower height in a new `featureHeight_m` field on the variant, or (b) accept that for "tower-like field equipment" the catalog represents the *building stub* and the 200 m vertical extent is conveyed in the prompt prose only. Same logic for `solar_csp_tower.suggestedAreaSqm` — split into `footprint_sqm` (~few hundred) vs `siteArea_sqm` (~500 000) or just drop the area override.

### 1.5 Two duplicate-archetype pairs with conflicting metadata

| Pair | Members | Different in |
|---|---|---|
| `nordic_timber_midrise` vs `nordic_timber_mid_rise` | both exist, 4 variants each | W (20 vs 28), floors (4-8 vs 3-10), subcategory ("Residential — High-Rise / Tower" vs "Residential — Mid-Rise Apartment"), variant IDs entirely different |
| `midcentury_distribution_warehouse` vs `mid_century_distribution_warehouse` | both exist, 4 variants each | W (80 vs 45), variant IDs entirely different |

These are two different schema generations of the same concept — the picker UI will show them as separate cards. The first pair even cross-references each other's image directory (`nordic_timber_midrise.thumbnailUrl` points at `/nordic_timber_mid_rise/hero.png`).

**Fix:** decide which slug is canonical (recommend the underscored form in both pairs since the rest of the catalog uses underscores), backfill the better metadata onto the survivor, and delete the loser. This needs the TEXT-LEVEL splice approach per `CLAUDE.md`.

---

## 2 — Variant ↔ parent scale envelope mismatches

Many archetypes have variants with per-variant `minFloors`/`maxFloors` that fall **outside** the parent's `minFloors`/`maxFloors`. The five hard cases above are the worst, but 27 archetypes have at least a 2-floor mismatch on one side, and 12 of those have a mismatch ≥ 4 floors. The full list, ordered by severity:

| Archetype | Parent | Variants combined | Direction |
|---|---:|---:|---|
| `climbing_wall_building` | 1–6 | 1–35 | variants spike **+29** above |
| `parametric_future_hub` | 5–30 | 10–50 | +20 above |
| `skyline_glass_office_cluster` | 20–50 | 3–40 | -17 below |
| `transit_podium_residential` | 4–10 | 4–25 | +15 above |
| `boutique_hotel_tower` | 4–25 | 2–12 | -13 below |
| `chateauesque_hotel` | 4–12 | 3–6 | -6 below |
| `autonomous_tech_campus` | 3–10 | 1–4 | -6 below |
| `vertical_farm` | 5–50 | 2–55 | both directions |
| `nordic_timber_midrise` | 4–8 | 2–12 | both directions |
| `eco_urban_bioclimatic_block` | 4–8 | 5–12 | +4 above |
| `hyperscale_data_center` | 1–4 | 1–8 | +4 above |
| `mediterranean_arcade_mixed_use` | 3–6 | 1–2 | -4 below |

For each row, the right call is: either **widen the parent's range to the union of all variant ranges** (cheap, 5-minute edits), **or move the outlier variants to a new archetype** (taste call, more work). The picker UI uses the parent's range to validate "is this archetype possible on this zone?" — so the parent should encompass every variant it advertises.

---

## 3 — Catalog completeness (the schema gap)

### 3.1 Variant-level scale info missing on 575 of 880 variants (65 %)

Already documented as pre-launch issue #21. Of those 575:

- **135** are in archetypes whose parent floor range spans 4 + storeys (so inheriting the parent range is unsafe — e.g. `art_deco_setback_tower` parent says 8–25, all 4 variants inherit, but the 4 variants span Chrysler-style 70-storey to Streamline 8-storey — they should not all be in the same range)
- **97** are in archetypes whose parent range is reasonable (≤ 3 storeys) and inheriting is fine
- **343** are in archetypes whose parent range is ≤ 2 storeys (single typology like townhouse / bungalow / café) — inheriting is correct, no per-variant override needed

**Highest-priority archetypes to enrich** (parent range wide AND variants implied to differ):

| Archetype | Parent | Why per-variant scale matters |
|---|---|---|
| `art_deco_setback_tower` | 8–25 | Chrysler crown vs Streamline mid-rise are different orders of magnitude |
| `glass_tower_modern` | (currently wrong — see #1.1) | placeholder variants but the parent typology demands tower scale |
| `parametric_future_hub` | 5–30 | diagrid tower variant exists; others should also lock scale |
| `autonomous_tech_campus` | 3–10 | ranges from 2-storey pavilion to 8-storey HQ |
| `boutique_hotel` | 3–20 | beaux-arts mansion vs parametric tower vs mediterranean courtyard |
| `condo_podium_tower` | 8–20 | variants range 8 → 25 floors; podium height varies |
| `vertical_farm` (canonical) | 5–50 | per-memory gold standard already enriched; check sister `vertical_farm_indoor_agriculture` |

### 3.2 52 archetypes lack `minWidth_m` / `maxWidth_m` / `minDepth_m` / `maxDepth_m`

All 220 carry `suggestedWidth_m` and `suggestedDepth_m`, but 52 don't carry the min/max range — the picker UI can't tell whether a 30 × 30 zone is "too small" for them. The list (mechanical to fix; same source-of-truth structure as `scripts/applyDimensions.mjs`):

```
administrative_faculty_office_building, airport_terminal_building, annex_mansion,
aquatic_natatorium_complex, bay_and_gable_house, biophilic_modern_healthcare,
boutique_hotel, brick_rowhouse_terrace, calgary_15_connected_tower,
campus_dining_hall_food_court, campus_lecture_hall_complex, campus_parking_structure,
campus_recreation_athletics_centre, central_utilities_plant_energy_centre,
chateauesque_grand_railway_hotel, collegiate_gothic, condo_podium_tower,
contemporary_midrise, convention_exhibition_center, corner_dépanneur,
corporate_office_campus_headquarters, cruise_ferry_terminal, e_commerce_fulfillment_center,
early_20th_century_megastructure, edwardian_foursquare, ev_charging_hub_mobility_station,
glass_tower_modern, graduate_family_housing, high_tech_structural_arena,
intermodal_transit_hub, junction_converted_industrial_loft, large_art_museum_gallery,
mid_century_distribution_warehouse, modern_big_box_logistics, nordic_timber_mid_rise,
outdoor_sports_stadium, parisian_mid_rise, parkitecture, postmodern_community_rec_centre,
regional_hospital_medical_center, research_laboratory, research_laboratory_innovation_hub,
residential_superblock, science_engineering_lab_complex, second_empire_civic_building,
student_residence_tower, student_union_campus_centre, ttc_streetcar_platform_stop,
university_academic_complex, university_library, vertical_farm_indoor_agriculture,
vertiport_evtol_facility
```

For most of these, the suggested W/D is reasonable; just need the ±50 % envelope around it (per the existing `applyDimensions.mjs` pattern).

### 3.3 54 archetypes lack `suggestedAreaSqm`

Mostly the same set as #3.2 (the schema generation that lacked min/max ranges also lacked area). Mechanical fill.

### 3.4 4 archetypes use legacy field names

| Archetype | Legacy field | New field |
|---|---|---|
| `mall_redevelopment` | `floorRange`, `suggestedArea_m2` | `minFloors`/`maxFloors`, `suggestedAreaSqm` |
| `terraced_stepped_building` | `floorRange`, `suggestedArea_m2` | same |

---

## 4 — Field-semantic ambiguity (`suggestedAreaSqm`)

A handful of archetypes have `suggestedAreaSqm` values that don't follow a single rule. Sample interpretations across the catalog:

| Archetype | Footprint (W×D) | suggestedAreaSqm | Likely meaning |
|---|---:|---:|---|
| `modern_sports_arena` | 18 000 | **8 000** | playing surface only |
| `barcelona_mercat` | 2 925 | **2 000** | nave / hall floor area |
| `amsterdam_hofje` | 750 | **200** | individual unit area |
| `art_deco_setback_tower` | 500 | **1 500** | typical floor plate (≈ 3× footprint after setbacks) |
| `senior_living_complex/Garden Courtyard` | 1 500 | **12 000** | total GFA across 8 floors |
| `solar_farm_agrivoltaics/csp_tower` | small tower | **500 000** | 50 ha solar field |

Three documented findings flagged this directly (`AREA_LT_FOOTPRINT` in the script). The field is overloaded.

**Three options:**

1. **Document and accept** — add a comment to the schema saying "for buildings, this is GFA; for amenity spaces / tower equipment, it's the primary usable area; for plant infrastructure, it's the surrounding site". Lowest effort. Risk: future contributors keep guessing.
2. **Split into multiple fields** — `footprintArea_sqm`, `gfa_sqm`, `siteArea_sqm`. Highest effort, breaks every consumer.
3. **Standardise on one meaning** (recommend GFA = footprint × avgFloors) and migrate the outliers. Medium effort. Best UX consistency.

This isn't strictly wrong row-by-row, but it's a foreseeable source of bugs in any UI that reads the field uniformly.

---

## 5 — What I checked and *didn't* find

For confidence, here are the realism checks that came back **clean**:

- **No archetypes with `minFloors ≤ 0`** ✅
- **No archetypes with `minFloors > maxFloors`** at the parent level ✅
- **No "rowhouse / townhouse / brownstone / terrace" archetype with maxFloors > 5** (apart from `coastal_resort_terrace_block` at 3-8, which uses "terrace" to mean linked apartments — correct typology) ✅
- **No "villa / cottage / chalet / bungalow" with maxFloors > 4** ✅
- **No "stadium / arena" with maxFloors > 6** ✅
- **No "cathedral / church / temple" with maxFloors > 4** ✅
- **No `aspectRatio` that disagrees with `suggestedWidth_m : suggestedDepth_m` by more than ~12 %** ✅
- **No variant whose description claims a taller scale than its metadata allows** (the script ran the regex `(\d+)\s*storey/floor` against descriptions; zero matches above the parent's max). ✅
- **No "tower / highrise" archetype with low max floors** — except the one called out in §1.1.
- **No `suggestedWidth_m` outside `[minWidth_m, maxWidth_m]`** on the 168 archetypes that have those ranges ✅
- **No `suggestedDepth_m` outside `[minDepth_m, maxDepth_m]`** on the 168 archetypes that have those ranges ✅

So the catalog isn't riddled with bugs — there's a small concentrated batch of real issues plus the long-known schema completeness gap.

---

## 6 — Recommended action order

1. **Same-day fixes (mechanical, low risk):**
   - Bump `glass_tower_modern` parent floors to `[12, 50]` (§1.1)
   - Backfill `minFloors`/`maxFloors`/`suggestedAreaSqm` on `mall_redevelopment` and `terraced_stepped_building` (§1.2)
   - Widen the 5 parent ranges that don't envelope their variants (§1.3) — but for `climbing_wall_building/The Spine`, prefer reclassifying the variant to its own archetype
   - Fix `solar_csp_tower.suggestedFloorHeight` (§1.4)

2. **One-day cleanup:**
   - Resolve the two duplicate archetype pairs (§1.5)
   - Bring the 27 envelope-mismatch archetypes (§2) into envelope, choosing widen-vs-reclassify per case
   - Backfill min/max width/depth on the 52 archetypes from §3.2 (extend `scripts/applyDimensions.mjs`)

3. **Multi-day taste work:**
   - Add per-variant scale to the ~135 variants in 47 archetypes whose parent range is wide (§3.1) — start with `art_deco_setback_tower`, `glass_tower_modern`, `parametric_future_hub`, `boutique_hotel`, `condo_podium_tower` (the ones the gallery actually shows)
   - Decide and document the `suggestedAreaSqm` semantic (§4)

4. **Schema decision (defer until after launch):**
   - Replace `floorRange`/`suggestedArea_m2` legacy fields, consolidate the 10 schema generations the catalog audit identified as issue #16

---

## Artifacts

- `scripts/audit_archetype_sizes.py` — re-runnable audit tool. `python scripts/audit_archetype_sizes.py --csv --md` writes:
  - `artifacts/audit/archetype_sizes_audit.csv` — full row-by-row findings (376 entries)
  - `artifacts/audit/archetype_sizes_findings.json` — same with metadata + presence stats
- `docs/ARCHETYPE_SIZES_AUDIT_2026_04_28.md` — this report
- Existing prior work consulted: `docs/ARCHETYPE_AUDIT_2026_04_26.md`, `docs/PRE_LAUNCH_DEEP_DIVE_2026_04_26.md` (issue #21 specifically).
