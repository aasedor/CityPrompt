# Archetype Sizes & Heights — Fix Plan (2026-04-28)

Plan for fixing the issues in [docs/ARCHETYPE_SIZES_AUDIT_2026_04_28.md](ARCHETYPE_SIZES_AUDIT_2026_04_28.md). Four phases ordered by risk and dependency. Phase 1 is mechanical and same-day; Phases 2–3 are scripted bulk edits; Phase 4 is a one-time schema decision.

**Hard rule throughout:** never `json.dump` the catalog. All edits via TEXT-LEVEL splice (the established pattern in `scripts/applyDimensions.mjs` and `scripts/apply_variant_specs.py`). The audit script (`scripts/audit_archetype_sizes.py`) re-runs cleanly in <2 s and is the validation oracle after each batch.

---

## Open questions before I touch anything

Three decisions need user input before Phase 1 can run cleanly. I'd like answers (or "use your judgement") on these first.

### Q1. Five variant-vs-parent floor conflicts — widen parent or reclassify variant?

| # | Archetype + variant | Conflict | A) widen parent | B) reclassify variant | My pick |
|---|---|---|---|---|---|
| a | `nordic_timber_midrise` / Contemporary Log Construction | parent 4-8, variant 2-3 | 2-8 (parent name "midrise" gets weird at 2 floors) | move to a new `nordic_timber_lowrise` archetype | **A** — 2-floor "mid-rise" is fine; 1 line change vs new archetype + image regen |
| b | `mediterranean_arcade_mixed_use` / Moorish Arched Souk | parent 3-6, variant 1-2 | 1-6 (a 1-floor "mixed-use arcade" is what a souk actually is) | move to vernacular_courtyard or new souk archetype | **A** — souks ARE single-storey arcades; widen and let parent typology stretch |
| c | `vernacular_courtyard_housing` / Chinese Siheyuan | parent 2-4, variant 1-1 | 1-4 | reclassify | **A** — siheyuan are correctly described as 1-storey courtyard housing; widen |
| d | `skyline_glass_office_cluster` / Low-Rise Glass Campus | parent 20-50, variant 3-6 | 3-50 (a 3-floor "skyline cluster" reads wrong) | move variant to `corporate_office_campus_headquarters` (already exists) | **B** — drastic widening damages the parent's identity; reclassify |
| e | `climbing_wall_building` / The Spine | parent 1-6, variant 20-35 | 1-35 (a "climbing facility" with 35 floors is wrong) | new `climbing_tower_mixed_use` archetype OR move to `condo_podium_tower` | **B** — clearly a different building type; reclassify into new archetype |

**Default if you don't answer:** I'll go with my picks (A for a/b/c, B for d/e). For d and e I'd splice the variant into the receiving archetype (with full metadata) and remove it from the source — both are TEXT-LEVEL diff, but the spawned variant ID needs an updated `thumbnailUrl` rewrite.

### Q2. Two duplicate archetype pairs — which slug is canonical?

| Pair | Option A (keep) | Option B (keep) | My pick |
|---|---|---|---|
| Nordic timber duplicates | `nordic_timber_midrise` (W=20, D=16, floors 4-8, subcat="High-Rise/Tower") | `nordic_timber_mid_rise` (W=28, D=18, floors 3-10, subcat="Mid-Rise Apartment") | **B** — wider floor range, more accurate subcategory; underscored hyphen-form shows up in `applyDimensions.mjs` already, so it's also been validated. Actually, **A**'s slug matches the rest of the catalog's underscore convention but **A**'s subcat is wrong. **Strongest pick: keep slug `nordic_timber_midrise` (A), backfill it with B's floor range and subcategory, then delete B.** |
| Distribution warehouse duplicates | `midcentury_distribution_warehouse` (W=80, D=50) | `mid_century_distribution_warehouse` (W=45, D=35) | **B** — underscore-separated `mid_century` is more readable and matches the rest of the catalog (`mid_century_modern_pavilion_block`, `mid_century_apartment`). 45×35 is more typical of a distribution warehouse than 80×50, which is closer to a fulfillment center. **Keep B, delete A.** |

**Default if you don't answer:** I'll use the picks above (compose the survivor from both metadata sets where they disagree, take the better field per row).

### Q3. `suggestedAreaSqm` semantic — what does it mean going forward?

Three options as outlined in the audit doc §4:
- **Document & accept** (no migration): a one-line schema comment + leave the catalog as-is.
- **Split into multiple fields** (`footprintArea_sqm` / `gfa_sqm` / `siteArea_sqm`): biggest payoff, breaks every consumer.
- **Standardise on GFA** (= footprint × avgFloors), migrate the ~6 outliers to match.

**My pick:** the third — standardise on **total GFA** for buildings, define a separate `siteArea_sqm` only on infrastructure variants (solar, transit). It's the meaning that's already implicit on the majority of rows (≈210/220) and only needs a handful of corrections. Document in the schema's leading comment so the next contributor doesn't drift.

**Default if you don't answer:** Phase 4 stays unscheduled; I'll log it as a follow-up but not act on it. The current ambiguity isn't actively breaking anything.

---

## Phase 1 — Hard bugs (same day, mechanical)

**Effort:** ~2 hours including validation. **Risk:** low. Each edit is a surgical TEXT-LEVEL splice on a known JSON range.

### 1.1 Backup the catalog
```bash
cp frontend/src/data/buildingArchetypes.json frontend/src/data/buildingArchetypes.json.bak-2026-04-28
```
One-line rollback if anything goes sideways.

### 1.2 Bump `glass_tower_modern` to tower scale

Single archetype, two field edits at the parent level.

| Path | Current | New |
|---|---|---|
| `glass_tower_modern.minFloors` | `2` | `12` |
| `glass_tower_modern.maxFloors` | `6` | `50` |
| `glass_tower_modern.suggestedAreaSqm` | (absent) | `2500` (typical floor plate ≈ footprint, since towers don't multiply footprint with floors in this field's de-facto floor-plate semantic on similar archetypes like `art_deco_setback_tower`) |

The 4 placeholder variants stay placeholder until Phase 3. No `thumbnailUrl` changes.

### 1.3 Fix two legacy-schema archetypes

**`mall_redevelopment`** — replace `floorRange` + `suggestedArea_m2` with the new fields. Variant rollup gives 1-8, area average ~50000:

| Path | Current | New |
|---|---|---|
| `mall_redevelopment.floorRange` | `[1, 5]` | (delete) |
| `mall_redevelopment.suggestedArea_m2` | `50000` | (delete) |
| `mall_redevelopment.minFloors` | (absent) | `1` |
| `mall_redevelopment.maxFloors` | (absent) | `8` |
| `mall_redevelopment.suggestedAreaSqm` | (absent) | `50000` |

**`terraced_stepped_building`** — same migration. Variant rollup gives 2-27, area average ~6500:

| Path | Current | New |
|---|---|---|
| `terraced_stepped_building.floorRange` | `[3, 20]` | (delete) |
| `terraced_stepped_building.suggestedArea_m2` | `5000` | (delete) |
| `terraced_stepped_building.minFloors` | (absent) | `2` |
| `terraced_stepped_building.maxFloors` | (absent) | `27` |
| `terraced_stepped_building.suggestedAreaSqm` | (absent) | `6500` |

### 1.4 Resolve the 5 envelope conflicts

Per the Q1 picks above. Concrete edits:

**a) `nordic_timber_midrise`** — widen parent.
- `minFloors`: 4 → 2.

**b) `mediterranean_arcade_mixed_use`** — widen parent.
- `minFloors`: 3 → 1.

**c) `vernacular_courtyard_housing`** — widen parent.
- `minFloors`: 2 → 1.

**d) `skyline_glass_office_cluster` / Low-Rise Glass Campus** — reclassify.
- Splice the variant out of `skyline_glass_office_cluster.variants` (now 3 variants).
- Splice it into `corporate_office_campus_headquarters.variants` (now 5 variants).
- Update `thumbnailUrl` from `/archetypes/buildings/skyline_glass_office_cluster/variant_1.png` to `/archetypes/buildings/corporate_office_campus_headquarters/variant_4.png`. Image file move + rename done in same commit.
- ⚠️ Variant count constraint: per `feedback_no_hero_image.md` and the existing audit's UI assumption, **archetypes have exactly 4 variants**. So either (a) we add a 5th variant slot to corporate_office_campus_headquarters (breaks UI) or (b) we drop one of corporate_office_campus_headquarters's existing variants. **Cleaner alternative:** keep `Low-Rise Glass Campus` in `skyline_glass_office_cluster` and instead widen the parent to 3-50, accepting the name is a slight stretch. *Flagging this as needing a decision — see below.*

**e) `climbing_wall_building` / The Spine** — reclassify.
- Same 4-variant constraint. **Cleaner alternative:** widen parent to 1-35, but that breaks the typology semantic harder than `skyline_glass_office_cluster`. Or: rename the variant from "The Spine" (30-storey tower) to a building-scale climbing-feature variant (1-6 floors), preserving the archetype but redefining the variant. The image and description would need a regen.

> **⚠️ Q1 supplemental decision:** the 4-variant slot constraint changes the calculus on (d) and (e). The realistic options are:
> - Widen parent to encompass the variant (compromises typology name, no image work).
> - Replace the misfit variant with a regenerated one (preserves typology, costs 1 archetype-card image regen ≈ $0.25 + ~3 min).
> - Add a `variantOverflow` field to the catalog and surface a 5th card in the picker (UI work, defer).
>
> **My pick for both (d) and (e):** option 2 — regenerate the variant. For `skyline_glass_office_cluster/Low-Rise Glass Campus`, replace with another 20+-storey skyline cluster variant (e.g. "Bronze Diagrid Twin Towers"). For `climbing_wall_building/The Spine`, replace with "The Tribute" (5-storey adaptive-reuse climbing gym in a former power station). This is a Phase 1 decision but the regen is Phase 3 work.

### 1.5 Fix `solar_csp_tower` field misuse

Two field edits on one variant.

| Path | Current | New |
|---|---|---|
| `solar_farm_agrivoltaics.variants[3].suggestedFloorHeight` | `200.0` | `10.0` |
| `solar_farm_agrivoltaics.variants[3].suggestedAreaSqm` | `500000` | `400` (footprint of receiver tower base only) |

The 200 m receiver-tower vertical extent is conveyed in the variant's `description` field, which already says "gleaming 200-meter tower". No data loss. The 500 000 sqm heliostat field is also in the description ("over 10,000 heliostats in precise radial concentric rings, and molten salt storage at base") so that's not lost either. If we ever introduce a `featureHeight_m` field, this is the canonical example.

### 1.6 Resolve duplicate archetype pairs

Per Q2 picks. Each removal needs:
- Splice the loser archetype out of `archetypes` array.
- Confirm no zone/preset code references the loser ID (grep before delete).
- Migrate the better metadata onto the survivor (TEXT-LEVEL splice).
- Decide what to do with the loser's image directory (delete OR symlink survivor → loser dir).

**Pair 1:** `nordic_timber_midrise` (keep — slug matches catalog convention) ← gets `nordic_timber_mid_rise`'s `subcategory: "Residential — Mid-Rise Apartment"` and floor range widened to `3-10`. Loser's image dir `/archetypes/buildings/nordic-timber-mid-rise/` already cross-referenced by survivor's `thumbnailUrl` — needs path rewrite to `/archetypes/buildings/nordic_timber_midrise/`.

**Pair 2:** `mid_century_distribution_warehouse` (keep — readable underscoring) ← already has correct dims. Just delete `midcentury_distribution_warehouse` and its image dir.

⚠️ **Both removals are destructive.** Need explicit user OK before merging. Backup-then-stage approach: I'd land Phase 1.2-1.5 first and confirm, then run 1.6 as a separate commit so it can be reverted independently.

### 1.7 Phase 1 validation

After each surgical edit (or at minimum at end of phase):

```bash
# 1. JSON still parses
python -c "import json; json.load(open('frontend/src/data/buildingArchetypes.json'))"

# 2. Archetype count: 220 → expected post-1.6: 218 (two duplicate removals)
python -c "import json; print(len(json.load(open('frontend/src/data/buildingArchetypes.json'))['archetypes']))"

# 3. Variant count: 880 → 872 if duplicates also removed (8 variants gone)
python -c "import json; d=json.load(open('frontend/src/data/buildingArchetypes.json'))['archetypes']; print(sum(len(a.get('variants',[])) for a in d))"

# 4. thumbnailUrl count unchanged
grep -o 'thumbnailUrl' frontend/src/data/buildingArchetypes.json | wc -l

# 5. No duplicate archetype IDs
python -c "import json; ids=[a['id'] for a in json.load(open('frontend/src/data/buildingArchetypes.json'))['archetypes']]; assert len(ids)==len(set(ids))"

# 6. Audit re-run: hard-bug findings should drop from 6 → 0 (or 0–1 if (d)/(e) deferred)
python scripts/audit_archetype_sizes.py
```

After 1.6: spot-check the two consolidated archetypes load in the picker UI on localhost:5174 (per CLAUDE.md "Test locally before pushing").

---

## Phase 2 — Schema completeness backfill (mechanical, scripted)

**Effort:** ~4 hours including dimension research. **Risk:** low–medium (bulk edits across 52 archetypes). **Pattern:** extends the existing `scripts/applyDimensions.mjs`.

### 2.1 Backfill `min/maxWidth_m` and `min/maxDepth_m` on the 52 archetypes that lack them

The list is in [audit §3.2](ARCHETYPE_SIZES_AUDIT_2026_04_28.md#32-52-archetypes-lack-minwidth_m--maxwidth_m--mindepth_m--maxdepth_m). All 52 already carry `suggestedWidth_m` and `suggestedDepth_m`, so the operation is **deterministic ±50 % envelope** for most rows, with manual overrides for a few where the catalog's typology demands a tighter or wider range.

**Approach:**
1. Add a new `BUILDING_DIMS_BACKFILL` array to `scripts/applyDimensions.mjs` with one entry per missing archetype (just `minWidth_m`, `maxWidth_m`, `minDepth_m`, `maxDepth_m`, `aspectRatio` — leave the existing `suggestedWidth_m`/`suggestedDepth_m` alone).
2. Default formula: `min = 0.55 × suggested`, `max = 1.7 × suggested`, rounded to nice integers, then manually override ~5–10 outliers (e.g. `boutique_hotel` should have a wider span because variants range from courtyard mansion to parametric tower).
3. Run the existing TEXT-LEVEL splice that `applyDimensions.mjs` already implements.

**Manual overrides expected** (rows where the default formula will be wrong):
- `boutique_hotel` — variants span 3-storey courtyard to 22-storey tower; widen to 0.4× / 2.2×.
- `terraced_stepped_building` — already has wide variant range; widen.
- `outdoor_sports_stadium` — stadiums vary 80×60 → 200×180; default is too tight.
- `airport_terminal_building`, `convention_exhibition_center`, `cruise_ferry_terminal` — same.

### 2.2 Backfill `suggestedAreaSqm` on the 54 archetypes that lack it

Similar pattern. **Pre-condition:** Q3 decided. Once the semantic is locked, the formula is `suggestedAreaSqm = suggestedWidth_m × suggestedDepth_m × ((minFloors + maxFloors) / 2)` for buildings.

For the ~5 archetypes where this formula gives an absurd result (e.g. `parking_garage` shouldn't multiply by floor count, since parking is open-deck), override manually.

### 2.3 Phase 2 validation

```bash
# 1-5: same as Phase 1.7 (parse, counts, no dup ids)
# 6. Audit re-run: presence stats should hit 100 % on width/depth/area
python scripts/audit_archetype_sizes.py | grep -E "(minWidth_m|maxWidth_m|minDepth_m|maxDepth_m|suggestedAreaSqm)"
# 7. Spot-check: pick 5 random archetypes and eyeball that the new ranges make sense
```

---

## Phase 3 — Variant scale enrichment (taste-required, scripted)

**Effort:** multi-day across many archetypes. **Risk:** medium (judgement calls per row). **Pattern:** extends `scripts/apply_variant_specs.py`.

### 3.1 Priority A: 5 archetypes where the parent typology demands per-variant scale

These five are "test these first" picks because the parent's wide range guarantees current renders are inconsistent across variants:

1. **`art_deco_setback_tower`** (parent 8-25). Per-variant ranges:
   - Cream Terra Cotta & Gold (Chrysler-style) → 30-50 floors
   - Black Granite & Chrome (corporate) → 20-35
   - Polychrome Zigzag Moderne (Empire State-ish) → 25-40
   - Streamline Moderne (lower, sleek) → 8-15
2. **`glass_tower_modern`** — depends on Phase 1.2 first; once parent is 12-50, give variants distinct ranges (slab 25-40, parametric 30-55, terraced biophilic 18-30, monolith 40-60).
3. **`parametric_future_hub`** (parent 5-30) — the only existing variant with scale (`parametric_diagrid_tower` 10-50) is good; the other 4 need explicit ranges.
4. **`autonomous_tech_campus`** (parent 3-10) — variants span pavilion (2-floor) to research lab (5-8) to data-center monolith (1-3 with high floor heights). Per-variant required.
5. **`boutique_hotel`** (parent 3-20) — explicit 4 variants already span courtyard mansion (3-5), industrial loft (4-7), beaux-arts mansion (4-6), parametric tower (15-22). Just record what's already implied.

### 3.2 Priority B: 47 archetypes from audit §3.1 where the parent range spans 4 + floors and ≥ 1 variant has no scale

Same approach but lower priority. Address as time permits between launch sprints.

### 3.3 Phase 3 validation

After each archetype enrichment:
```bash
# Audit: VARIANT_NO_SCALE finding for that archetype should disappear
python scripts/audit_archetype_sizes.py 2>&1 | grep '<archetype-id>'
```

After all of Priority A:
- VARIANT_NO_SCALE finding count should drop from 135 → ~115 (5 archetypes × 4 variants = 20 cleared).
- VARIANT_TYPOLOGY_FLOOR_MISMATCH count should also drop where variants now correctly express their typology.

Visual validation (per CLAUDE.md "Test locally before pushing"): pick 1–2 enriched archetypes, render in localhost:5174, confirm the picker shows the right scale info on hover/in the panel.

---

## Phase 4 — `suggestedAreaSqm` semantic decision (deferred)

**Effort:** 1 day. **Risk:** medium (touches every reader of the field).

Pre-condition: Q3 above answered. If "document & accept" — done in 5 min, just a schema comment. If "standardise on GFA" — write a one-time migration script that recomputes `suggestedAreaSqm = footprint × avgFloors` for the ~6 outliers (modern_sports_arena, barcelona_mercat, amsterdam_hofje, art_deco_setback_tower, senior_living_complex variants, solar_csp_tower).

If "split into multiple fields" — defer indefinitely; this is a schema migration of comparable scope to the legacy-schema work in pre-launch dive issue #16.

---

## Validation oracle: the audit script

`scripts/audit_archetype_sizes.py` is the single re-runnable check. After **every** edit batch:

```bash
python scripts/audit_archetype_sizes.py 2>&1 | tail -40
```

Expected progression:
| After phase | High-sev findings | Med-sev findings | Notes |
|---|---|---|---|
| Baseline (today) | 2 | 356 | mall + terraced_stepped legacy |
| Phase 1 done | 0 | ~340 | -2 high (legacy fixed); ~5 less med (envelope conflicts) |
| Phase 2 done | 0 | ~230 | -52 MISSING_RANGE, -54 MISSING_AREA |
| Phase 3 Priority A done | 0 | ~210 | -20 VARIANT_NO_SCALE |
| Phase 3 Priority B done | 0 | ~75 | -135 VARIANT_NO_SCALE |
| Phase 4 done | 0 | ~70 | -3 AREA_LT_FOOTPRINT, -2 VARIANT_AREA_HUGE |

The remaining ~70 mid-sev findings will mostly be the typology classifier's known false positives (per audit doc methodology). Acceptable noise floor.

---

## Rollback strategy

Each phase commits independently with the `.bak` file from Phase 1.1 retained throughout. Single-file rollback at any point:

```bash
cp frontend/src/data/buildingArchetypes.json.bak-2026-04-28 frontend/src/data/buildingArchetypes.json
```

For Phase 1.6 specifically (duplicate removals): commit separately so it can be reverted with `git revert` without taking down the rest of the work.

---

## Suggested execution order

1. **Wait for Q1, Q2, Q3 answers (or "use your judgement").**
2. Run **Phase 1.1** (backup) and **Phase 1.2–1.5** as one commit ("Phase 1: hard-bug fixes for archetype sizes/heights"). Re-run audit, confirm 0 high-sev findings. Test in browser.
3. Run **Phase 1.6** as a separate commit ("Resolve duplicate archetype pairs"). Re-run audit. Test in browser.
4. Run **Phase 2.1** as one commit ("Backfill min/max width/depth on 52 archetypes"). Re-run audit, confirm 100% presence on those fields. Test in browser.
5. Run **Phase 2.2** as one commit ("Backfill suggestedAreaSqm on 54 archetypes"). Pending Q3.
6. **Phase 3 Priority A** as one commit ("Per-variant scale on 5 priority tower/campus archetypes"). Render-test the 5 archetypes in `localhost:5174` to confirm visual consistency.
7. **Phase 3 Priority B** in batches of ~10 archetypes each — chunked commits so any taste-call mistake reverts cleanly.
8. **Phase 4** if Q3 picked "standardise".

Total wall-clock: 2–3 days of focused work, mostly Phase 3.

---

## Out of scope for this plan

- **Image regeneration** beyond the (d)/(e) variant replacements is not included — addressed in pre-launch dive issues #19 (45 missing card images) and #20 (47 hero=V0 dups). Tracked separately.
- **Schema-fragmentation cleanup** (10 generations of building schemas) is pre-launch dive #16 — covers far more than just sizes/heights and should not be bundled.
- **Aspect ratio rewriting** — none of the catalog rows have an `aspectRatio` that mismatches `suggestedWidth_m / suggestedDepth_m` by more than 12 %, so this is not included.
- **Streets and openspaces archetypes** — the audit was buildings-only. A separate sizes audit for the 62 streets and 104 openspaces is a follow-up.
