# Polygon + Subvariant Authority Plan — Globe Render Pipeline

Date: 2026-04-18
Scope: Globe Pass 2 / single-shot render pipeline only (`useGlobeAIRender.ts`, `render.py` relabeling, `buildingArchetypes.json` variant fields).
Out of scope: Mapbox pipeline, street view, archetype schema redesign, new Gemini model, prompt-builder architectural rewrite.
Primary sources this plan builds on (do not duplicate, reference):
- `artifacts/prompt-audit/AUDIT_REPORT.md` — round 1, globe sections only
- `artifacts/prompt-audit/globe-v2/GLOBE_POLYGON_AUDIT.md` — round 2, globe-only polygon audit
- `artifacts/prompt-audit/globe-v2/scenario-*.txt` — 8 reconstructed Pass 2 prompts
- `docs/tooling-plan-v3.md` — tooling plan this plan integrates with
- `CLAUDE.md` — project conventions, including the NEVER-`json.dump` rule

Terminology: "Pass 2" here refers to the per-zone/single-shot Gemini call that produces the finished render — what the globe `render()` at `useGlobeAIRender.ts:1585` actually fires. The "per-zone Pass 2" code path (`buildSingleZonePromptForPerZone` at `useGlobeAIRender.ts:1152`) is dead code because `PERZONE_THRESHOLD = 99` (`useGlobeAIRender.ts:1070`). This plan targets the live single-shot `buildPrompt` path at `useGlobeAIRender.ts:744`.

---

## 1. Executive summary

1. The user's priority is two sentences long: the polygon the user draws must be the footprint that gets rendered, and the subvariant image card the user picks must be the style that gets rendered. Today's pipeline honors neither reliably.
2. Image selection ALREADY resolves the user's selected variant at `useGlobeAIRender.ts:487-500`. The prompt text does NOT — `getMapOverlayPrompt` at `:652` resolves variant only by `archetypeId` string match, and `getZoneArchetypeInfo` at `:676` never consults variants. Image and text disagree on every zone whose user-picked variant differs from the parent archetype id.
3. `suggestedAreaSqm` (the catalog's typical area) is interpolated into the prompt's scale token at `:813` and `:1184`. For the reference brownstone archetype this literal is 150 m². When the user draws an 80x40 m polygon (3,200 m²), Gemini reads "~150 m²" verbatim — a 21x lie. Reconstructed in `globe-v2/scenario-6-huge-80x40.txt`.
4. `computeFootprintDims` exists in the Mapbox pipeline at `useAIRender.ts:493` but is absent from globe code. Globe's `GlobeSitePlannerMap.tsx:47` and `GlobeDrawingTool.tsx:24` already import `haversineDistance` from `mapEngine/geoUtils.ts:127` — so porting the function body is one file edit. This is the lowest-cost, highest-impact change on this list.
5. Three of the four recent Mapbox polygon-authority commits (`b9cea11`, `7202d32`, `279868f`) never reached globe. The fourth (`4e23345`, site-boundary clip) predated Mapbox on globe. Globe's MANDATORY block at `:871` still contains the permissive word "landscaping" (which invites greenery inside building footprint) and does not contain "polygon edges ARE building walls" or "polygon size is authoritative".
6. `renderPrompt.roofView` text exists on every archetype (`buildingArchetypes.json:326`, `:388`, etc.) and is never called from `useGlobeAIRender.ts`. At nadir the globe prompt still describes facades, stoops, and double-hung windows — all invisible-pixel features at 0 degrees pitch.
7. Backend `render.py:420` relabels every primary image as "a 3D clay massing model" regardless of what the client sent; `:439` labels every side image "ARCHETYPE REFERENCE — Apply the exact architectural style". On an irregular polygon paired with a convex reference card, "exact style" is a direct contradiction of "match the polygon shape".
8. Mask dilation `DILATION_PX = 8` at `useGlobeAIRender.ts:334` is a constant in pixels. On a 4 m polygon edge that is ~50% mask inflation; on an 80 m polygon it's 2.5%. Tiny polygons get fuzzy edges that hide the archetype-too-big failure.
9. Camera pitch IS read into `pitchDesc` at `useGlobeAIRender.ts:746-758` and substituted into COMPOSITION. But pitch never influences which archetype prompt field is selected, nor whether roof or facade features are promoted in the zone line.
10. Polygon shape is represented in exactly one signal: the mask pixels. The prompt text never says "rectangular", "L-shaped", "elongated", or "irregular". Tokens like `polygon@(x,y)(x,y)...` give Gemini coordinates without semantic shape help.
11. Backwards compatibility with legacy archetypes is explicitly not a goal of this plan. Variant-level fields added to the JSON are optional — absence means fall back to parent, which is today's behavior.
12. Seed forwarding (tooling-plan-v3 Phase 0 at `render.py:476`) is a hard prerequisite. Without deterministic output you cannot A/B-test any phase of this plan. Land seed forwarding first.

---

## 2. Goals and priority order (each tied to an acceptance criterion)

| # | Goal | Acceptance criterion |
|---|---|---|
| G1 | Polygon footprint (shape + dims + orientation) overrides archetype nominal in every signal the model sees | Re-run scenarios 1-6 from `globe-v2/`. Prompt text for scenario 6 no longer contains `~150m²`; it contains computed area and shape adjective. `diff` of scenario 2 vs scenario 6 prompt text is non-trivial beyond the pixel-coord token. |
| G2 | Subvariant authority: selected variant's text (if any) shadows parent archetype text | Select "brownstone" within "rowhouse" parent in UI. Prompt text references brownstone-specific language, not parent defaults. Image AND text label match. |
| G3 | Camera-angle correctness: nadir prompt emphasizes roofs; oblique emphasizes facades | At `pitch < 20deg` the zone-line features for brownstone include `roofView` language; at `pitch > 40deg` they include `mapOverlay`. Binary differentiable by reading the prompt text. |
| G4 | No render-quality regression on scenes that currently work | Scenario 3 (near-square 15x14 rectangle, matching archetype nominal) renders indistinguishably in blind A/B between pre- and post-change branches. |
| G5 | Every change cited at `file:line` level, rollback is git-revertable per phase | No feature flags added unless a phase requires one. Each phase is a single logical revert. |

Priority order is G1 > G2 > G3 > G4 > G5. G1 fixes the user's most common complaint (toy-in-big-polygon). G2 fixes the second complaint (wrong subvariant). G3 is the biggest remaining render-quality lever; it also unblocks the paper-thin-at-nadir memory `project_z_axis_nadir_refs.md`.

---

## 3. Non-goals / explicitly out of scope

- **No prompt builder rearchitecture.** `buildPrompt` stays a flat function that returns a string. No class hierarchy, no templating engine, no shared prompt DSL. Surgical edits only. If a change wants to add >40 lines of builder structure, it is out of scope.
- **No Mapbox pipeline changes.** `useAIRender.ts` is dead for end users per the user's 2026-04-18 confirmation. Do not edit it even when copy-pasting utility functions — put shared helpers in a new file or the globe file.
- **No archetype JSON schema rewrite.** Adding OPTIONAL variant-level fields is allowed (Phase 3). Renaming, restructuring, migrating, or re-validating existing fields is not. No `json.dump` — all JSON edits use text-level splice per `CLAUDE.md`.
- **No new Gemini model.** Plan assumes `gemini-3.1-flash-image-preview` as the active model. If the user upgrades to `gemini-3-pro-image-preview` mid-plan, the plan still applies.
- **No new image pipelines.** No new image captures, no new clay anchors, no orthographic refs authored in this plan. The existing inputs are enough.
- **No visual regression harness build.** Visual regression is addressed by tooling-plan Phase 8 and is explicitly deferred there. Validation in this plan is manual A/B against reference screenshots.
- **No street view changes.** Street view uses `useStreetViewRender.ts` which is out of scope per audit.

---

## 4. Failure mode map

| Observed failure (user words) | Failing signal(s) today | Plan phase addressing it |
|---|---|---|
| "Toy building in a large polygon" | `suggestedAreaSqm` literal in scale token; MANDATORY permits `landscaping`; no "polygon size is authoritative" rule; Mapbox commit `7202d32` unported | Phase 2 (computed area swap), Phase 4 (MANDATORY port) |
| "Building extends past my polygon to match the archetype" | MANDATORY lacks `b9cea11` "polygon edges ARE walls" clause | Phase 4 |
| "Wrong subvariant rendered — I picked brownstone and it rendered generic rowhouse" | `getMapOverlayPrompt` matches by archetypeId only; `getZoneArchetypeInfo` never reads variant fields; variant text not present in prompt | Phase 5 (variant-resolved text), Phase 6 (variant-level JSON fields) |
| "Paper-thin building at 0deg" | `renderPrompt.roofView` never selected; `info.aerialAppearance` only added at certain code paths; facade language reaches Gemini at nadir | Phase 7 (camera-angle branch) |
| "L-shape becomes half-rectangle with hard crop" | No "L-shaped" token anywhere; archetype card image depicts rectangle; `clipRenderToZones` crops post-hoc | Phase 3 (shape adjective), Phase 4 (mask-is-authoritative language) |
| "Long strip becomes short chunky building" | No aspect ratio computed; archetype nominal overwrites expectation | Phase 2 (computed dims), Phase 3 (shape adjective) |
| "Tiny polygon produces fuzzy edges" | `DILATION_PX = 8` constant; 8 px is 50% of a 4 m polygon | Phase 8 (scale-aware dilation) |
| "Reference image label lies" | `render.py:420` hardcoded "3D clay massing model"; `:439` "ARCHETYPE REFERENCE" overwrites client role | Phase 9 (backend relabel) |

---

## 5. Design principles

1. **Mask and polygon geometry are hard constraints; text descriptions are soft.** Every conflicting-text fix in this plan serves making the text agree with the mask. If mask says X and text says not-X, the fix removes the not-X text, it does not try to re-convince Gemini with more text.
2. **Variant beats parent archetype whenever a variant is selected.** If `zone.properties.development_selected_variant_id` resolves to a variant with a field, that field shadows the parent's field. Parent fields persist only when variant is null.
3. **Scale-invariant archetype facts (materials, proportions, bay rhythm, cornice style) stay. Scale-bound facts (absolute width, depth, typical area, "3-4 storey rhythm") are demoted or derived from polygon.** The heuristic: if a sentence begins with a number, ask whether the polygon authority rule contradicts it. If yes, either drop or derive from polygon.
4. **Angle-specific prompt variant is selected from `renderPrompt` by pitch bucket.** Nadir (< 20deg) -> `roofView`. Oblique (20-60deg) -> `mapOverlay`. Low-oblique / ground (> 60deg) -> `mapOverlay` + foreground cues. There is no new angle bucket; it reuses the bucketing at `useGlobeAIRender.ts:753-756`.
5. **Every change has an a/b-testable before/after state.** No change ships without a paired screenshot of the same scene before and after.
6. **Backwards-compat not a goal.** This plan changes rendering behavior deliberately. Variant fields are optional so legacy archetypes continue to work.
7. **Prefer one code path.** When two signals could convey the same fact, pick one. Duplicated text (e.g. footprint dims in zone line AND in MANDATORY prose) is adversarial when the two disagree.
8. **Plain declarative prompt language, short clauses, numerical where possible.** "polygon = 270 m^2" beats "polygon area measured in square meters is approximately 270". Gemini weights later instructions more heavily per `CLAUDE.md`; put the authoritative rule last in MANDATORY.

---

## 6. Phased work plan

Eight phases, gated. Sizes: S = <1 hour, M = 1-3 hours, L = 3-8 hours. Every phase lists files, a pseudo-diff, dependencies, validation method, and rollback.

### Phase 0 — Seed forwarding (PREREQUISITE, from tooling-plan-v3 Phase 0)

**Goal.** Make Gemini deterministic given the same seed so every subsequent A/B in this plan is meaningful.

**Files.** `backend/app/api/v1/render.py` around `:476` (current code at `:489-494` actually already forwards seed; tooling-plan-v3 line 156 says seed is broken; verify before fixing).

**Untested assumption.** The tooling plan references `render.py:476` as the bug site; current read shows seed is forwarded at `:493-494` (`gen_config["seed"] = int(req.seed)`). Re-verify against `docs/SAME_ANGLE_DEGRADATION_DIAGNOSTIC.md` before declaring this phase done. If seed is already forwarding, measure pixel-diff variance before moving on.

**Validation.** Run identical camera + identical seed twice; pixel-diff variance drops measurably.

**Rollback.** Git revert; no semantic pipeline change.

**Size.** S.

**Gate.** Variance measured and documented. Without this gate, later phases cannot be A/B-tested.

---

### Phase 1 — Helper: polygon metrics module

**Goal.** Add a single function that returns all polygon-derived facts the rest of the plan needs. Put it where both pipelines could share it, but only globe calls it in this plan.

**Files.** New file OR top of `useGlobeAIRender.ts` (before line 80). Pick one; a new file `frontend/src/components/viewer/globe/polygonMetrics.ts` is cleaner.

**Pseudo-diff.**

```typescript
// frontend/src/components/viewer/globe/polygonMetrics.ts (new)
import { haversineDistance } from '../mapEngine/geoUtils';

export interface PolygonMetrics {
  lengthM: number;          // longest edge, meters
  widthM: number;           // second (or third if >=4 verts) longest, meters
  areaM2: number;           // shoelace * lat/lon correction
  aspectRatio: number;      // lengthM / widthM
  vertexCount: number;
  bearingDeg: number;       // compass bearing of longest edge, 0=N
  shape: 'rectangular' | 'elongated' | 'near-square' | 'L-shaped' | 'irregular';
}

export function computePolygonMetrics(coords?: number[][]): PolygonMetrics | null {
  if (!coords || coords.length < 3) return null;
  // ... edges, area, bearing, shape classification ...
  // Shape heuristic:
  //   verts === 3 || verts === 4 with aspectRatio < 1.25 -> 'near-square'
  //   verts === 4 && aspectRatio >= 1.25 && <= 3 -> 'rectangular'
  //   verts === 4 && aspectRatio > 3 -> 'elongated'
  //   verts >= 6 && (area / bboxArea) < 0.75 -> 'L-shaped'
  //   else -> 'irregular'
}
```

The shape heuristic is an **untested assumption**; tune the thresholds on real zones before declaring Phase 1 done. `bboxArea` can be computed as `(maxLon - minLon) * metersPerDegLon * (maxLat - minLat) * metersPerDegLat`. See `frontend/src/components/viewer/mapEngine/geoUtils.ts` for the correct constants (noting the three-site duplication problem flagged in tooling-plan-v3 section 5.1; this plan does not fix that, it just uses one of them).

**Dependencies.** None. Standalone helper. Imported by Phase 2 onwards.

**Validation.** Unit test with 6 known polygons from `globe-v2/scenario-*.txt`. Expected outputs: scenario 1 (18x8) -> rectangular, 2.25 AR. Scenario 2 (40x4) -> elongated, 10 AR. Scenario 4 (L-shape) -> L-shaped, 8 verts, bbox fill < 0.75. Scenario 5 (6x4) -> near-square or rectangular.

**Rollback.** Delete the file.

**Size.** S.

**Gate.** Unit tests pass on all 6 fixtures.

---

### Phase 2 — Use computed polygon dims in scale token (the biggest single fix)

**Goal.** Stop interpolating archetype `suggestedAreaSqm` into the prompt. Interpolate the polygon's own area and dims instead.

**Files.** `useGlobeAIRender.ts:803-816` (scale token in `buildPrompt`). Optional: `useGlobeAIRender.ts:1180-1185` (same logic in dead `buildSingleZonePromptForPerZone`).

**Pseudo-diff.**

```typescript
// useGlobeAIRender.ts:803 area
const metrics = computePolygonMetrics(zone.coordinates);

// inside the building-scale branch:
let scale = '';
if (zone.zone_type === 'building' || zone.zone_type === 'residential') {
  if (floors > 0 && heightM > 0) scale = `${floors}F ${Math.round(heightM)}m`;
  else if (floors > 0) scale = `${floors}F`;
  else if (heightM > 0) scale = `${Math.round(heightM)}m`;
  else if (info.minFloors && info.maxFloors) { /* as today */ }
  else scale = 'multi-story';

  // REPLACED: no longer uses info.suggestedWidth_m, info.suggestedDepth_m, or info.suggestedAreaSqm
  if (metrics) {
    scale += ` | polygon ${metrics.lengthM}x${metrics.widthM}m (${Math.round(metrics.areaM2)}m²)`;
  }
} else {
  scale = 'gnd';
  if (metrics) scale += ` | ${Math.round(metrics.areaM2)}m²`;
}
```

**Dependencies.** Phase 1.

**Downstream.** Phase 3 reuses `metrics` in the same loop — compute it once, pass it down.

**Validation.** Re-generate scenario-1 through scenario-6 prompts (a text diff pass; no Gemini call needed). Expect the `~150m²` literal to disappear from every building zone's scale token in every scenario. Expect each scenario's scale token to contain unique numbers matching its polygon dims. Then run scenarios 1, 4, and 6 through Gemini and compare against pre-change renders. Scenario 6 expected delta: fewer "toy building in corner" outcomes.

**Rollback.** Git revert the scale-token hunk. `info.suggestedAreaSqm` stays in `getZoneArchetypeInfo`'s return shape so nothing else breaks.

**Size.** S.

**Gate.** Scenarios 1 and 6 each show a prompt text delta that names the polygon's dims, not the archetype's. Scenario 3 (matches archetype nominal) looks visually equivalent pre- and post-change.

---

### Phase 3 — Shape adjective in zone line

**Goal.** Give Gemini one word describing the polygon shape so it can choose between an L-plan building, a long strip, or a near-square massing.

**Files.** `useGlobeAIRender.ts:801-816`, `:856-857`.

**Pseudo-diff.**

```typescript
// after computing metrics:
const shapeToken = metrics ? ` (${metrics.shape})` : '';
const name = (info.archetypeTitle || zone.name || ...) + shapeToken;

// OR as a separate field in the zone line:
zoneLines.push(
  `${i + 1}. [${color}] ${name} | ${scale} | shape: ${metrics?.shape || 'unknown'} | ${featureStr || 'render as described'}...`
);
```

Pick whichever reads cleaner in a dumped prompt — author's suggestion is a dedicated `shape:` field per the second form, so the word isn't hiding inside parentheses after the name.

**Dependencies.** Phase 1, Phase 2.

**Validation.** Diff scenario-4 (L-shape) prompt text before and after. Expect the literal token `shape: L-shaped` (or `(L-shaped)`) to appear. Render scenario 4 through Gemini and eyeball: expect fewer cases of Gemini rendering a rectangular building across the L's notch.

**Rollback.** Git revert. No schema change.

**Size.** S.

**Gate.** Scenario 4 prompt text shows the L-shape token. Render visibly respects the notch more often than not (N/5 manual trials).

---

### Phase 4 — MANDATORY block: polygon edges = walls, size authoritative, no landscaping

**Goal.** Port the two Mapbox prompt-text fixes that the polygon audit identified as HIGH severity: `b9cea11` (polygon edges ARE walls) and `7202d32` (polygon size is authoritative). Remove the permissive word "landscaping" from the building branch.

**Files.** `useGlobeAIRender.ts:871` (the MANDATORY line). Consider also branching MANDATORY by `hasBuildings` to avoid telling ground zones that "polygon edges are building walls" (the round-1 audit's C2).

**Pseudo-diff.**

```typescript
// useGlobeAIRender.ts:871
const mandatoryBuildings = `MANDATORY: The white mask shows the EXACT area to edit. \
THE POLYGON EDGES ARE THE BUILDING'S EXTERIOR WALLS. The building MUST FILL the entire polygon area — \
its footprint must match the polygon shape and size exactly, edge-to-edge. \
Do NOT render driveways, plazas, gardens, or unused space between the building and the polygon edge. \
Do NOT place a smaller building inside a larger polygon. \
Archetype metadata (floor count, height, nominal dimensions) describes STYLE, MATERIALS, and CHARACTER only. \
If the polygon is smaller than a typical archetype example, render a smaller building in that style. \
If larger, scale it up. Polygon size is authoritative. \
Match scale and density of surrounding real 3D buildings. \
Rendered building facades and roofs MUST have the same color cast, warmth, and atmospheric tint as adjacent real buildings.`;

const mandatoryGround = `MANDATORY: The white mask shows the EXACT area to edit. \
Replace the colored polygon overlays with the specified ground material (grass, pavement, gravel, water). \
No buildings or vertical structures in this mask. Match lighting and atmospheric tint of adjacent real buildings.`;

sections.push(hasBuildings ? mandatoryBuildings : mandatoryGround);
```

Note: in practice a globe prompt often has BOTH buildings and ground zones in one render. In that case concatenate the relevant building rule with a shorter "ground zones render as surface materials only" clause. The round-1 audit's C2 documents why the one-size-fits-all block is adversarial.

**Dependencies.** None (text-only).

**Validation.** Run scenarios 6 (huge), 5 (tiny), 4 (L-shape) through Gemini. Expected failure-rate drop for "building shrinks to archetype size" and "building has garden between wall and polygon edge".

**Rollback.** Git revert. This is literally one `const`.

**Size.** S.

**Gate.** Scenario 6 produces a full-size building at the polygon's edges in N/5 manual trials (baseline is 0/5 per the audit).

---

### Phase 5 — Variant-resolved text: `getMapOverlayPrompt` + `getZoneArchetypeInfo`

**Goal.** Make the two helpers that feed the prompt text consult the user's selected variant first, falling back to the parent archetype only when no variant is selected.

**Files.** `useGlobeAIRender.ts:652-671` (`getMapOverlayPrompt`), `useGlobeAIRender.ts:676-738` (`getZoneArchetypeInfo`).

**Pseudo-diff (the function that already exists for images).**

```typescript
// useGlobeAIRender.ts:487-500 already does this for IMAGES.
// Extract to a helper, then reuse in both getters:
function resolveVariant(zone: SiteZone, entry: any): any | null {
  const props = zone.properties || {};
  const selectedVariantId =
    (props.development_selected_variant_id as string) ||
    (props.road_selected_variant_id as string) ||
    (props.green_space_selected_variant_id as string) ||
    (props.plaza_selected_variant_id as string) ||
    '';
  if (selectedVariantId) {
    const hit = entry.variants?.find((v: any) => v.id === selectedVariantId);
    if (hit) return hit;
  }
  return null;
}

// getMapOverlayPrompt now reads:
function getMapOverlayPrompt(zone: SiteZone, pitchDeg?: number): string | undefined {
  // ... archetypeId + entry resolution as today ...
  const variant = resolveVariant(zone, entry);
  const src = variant?.renderPrompt || entry.renderPrompt || {};

  // Phase 7 adds the pitch branch; for Phase 5 just use mapOverlay:
  const base = src.mapOverlay || entry.prompt?.subject || '';
  const variantDesc = variant?.description ? ` Style: ${variant.description}` : '';
  return base ? `${base}${variantDesc}` : variantDesc || undefined;
}

// getZoneArchetypeInfo returns a variant-shadowed view:
function getZoneArchetypeInfo(zone: SiteZone) {
  // ... entry resolution as today ...
  const variant = resolveVariant(zone, entry);

  // Variant fields shadow parent fields. If variant.facadeDetail exists, use it;
  // else fall back to entry.facadeDetail.
  const sp = variant?.styleProfile || entry.styleProfile || {};
  const fd = variant?.facadeDetail || entry.facadeDetail || {};
  const rd = variant?.roofDetail || entry.roofDetail || {};
  // ... rest unchanged, but reading from sp/fd/rd which are now variant-shadowed ...

  return {
    archetypeTitle: variant?.label || entry.title,
    // ...
  };
}
```

**Dependencies.** None. Variants already in data.

**Downstream.** Phase 6 adds variant-level fields to the JSON; this phase makes the code ready to read them.

**Validation.** Pick a zone where the UI lets the user select a variant whose description differs from parent (`ZonePropertiesPanel.tsx:462-481` writes these fields today — `development_selected_variant_id`, `development_facade_detail`, etc.). Console log the assembled prompt; expect the variant's description to appear. Compare image attached to prompt vs text content of prompt — they now reference the same variant.

**Rollback.** Git revert the two helpers. Image selection path untouched.

**Size.** M.

**Gate.** A zone with a non-null `development_selected_variant_id` produces a prompt whose text explicitly mentions variant-level vocabulary, and the attached thumbnail URL matches that variant (already works).

---

### Phase 6 — Variant-level overrides in `buildingArchetypes.json` (optional-field additive)

**Goal.** Allow a variant to declare its own `facadeDetail`, `roofDetail`, `renderPrompt`, `materials`, `suggestedAreaSqm`. Phase 5 already reads these via the shadow pattern; this phase authors a minimal set of overrides for a pilot of 3 archetypes.

**Files.** `frontend/src/data/buildingArchetypes.json` — text-level splice per `CLAUDE.md` "NEVER json.dump" rule. Pick 3 archetypes with meaningfully distinct variants (e.g. `brownstone_rowhouse_frontage`, `collegiate_gothic`, and one where the variants differ most from parent).

**Pseudo-diff (conceptual, not a real JSON patch).**

```json
// inside one archetype's "variants" array, append optional fields to ONE variant:
{
  "id": "brownstone_rowhouse_mansard_variant",
  "label": "Mansard Brownstone",
  "thumbnailUrl": "...",
  "description": "Mansard-roofed brownstone with slate roof",
  "renderPrompt": {
    "mapOverlay": "Replace the colored building block with a photorealistic mansard-roofed brownstone. ...",
    "roofView": "Replace the colored block viewed from above with a steeply-pitched slate mansard. ..."
  },
  "roofDetail": {
    "form": "mansard, 4-sided steep pitch",
    "material": "dark slate shingles",
    "aerialAppearance": "steeply-pitched dark slate surfaces with dormer windows"
  }
}
```

Text-level splice rule: find the closing `}` of the variant object, insert new fields before it. Never `JSON.parse` + `JSON.stringify` on this file.

**Dependencies.** Phase 5 must be in place; otherwise the new fields go unread.

**Validation.** Select the new variant in UI. Prompt text now contains mansard-specific language even though the parent archetype stays flat-roofed.

**Rollback.** Git revert the JSON edit. Optional-field absence falls back to parent.

**Size.** M for 3 archetypes; L for all 97.

**Gate.** At least 3 pilot variants produce prompts with variant-distinct text.

---

### Phase 7 — Camera-angle branching: roofView at nadir

**Goal.** At nadir (< 20deg pitch) switch archetype renderPrompt selection from `.mapOverlay` to `.roofView`. At the same time, promote `info.aerialAppearance` in the zone-line features for nadir and demote facade-heavy `info.facadeDescription`.

**Files.** `useGlobeAIRender.ts:652` (`getMapOverlayPrompt` accepts pitch), `useGlobeAIRender.ts:819` (call site supplies pitch), `useGlobeAIRender.ts:822-832` (zone-line features branch).

**Pseudo-diff.**

```typescript
// Pass pitch into the helper:
function getMapOverlayPrompt(zone: SiteZone, pitchDeg?: number): string | undefined {
  // ... entry + variant resolution as Phase 5 ...
  const src = variant?.renderPrompt || entry.renderPrompt || {};
  const isNadir = pitchDeg != null && pitchDeg < 20;
  const base = (isNadir && src.roofView) ? src.roofView : src.mapOverlay;
  // ...
}

// In buildPrompt, at line 819:
const pitchDeg = /* the number already computed at :752 */;
const overlayPrompt = getMapOverlayPrompt(zone, pitchDeg);

// In the features block :822-832:
if (overlayPrompt) {
  features.push(overlayPrompt);
} else {
  if (isNadir) {
    if (info.aerialAppearance) features.push(`Aerial: ${info.aerialAppearance}`);
    if (info.roofDescription) features.push(info.roofDescription);
  } else {
    if (info.facadeDescription) features.push(info.facadeDescription);
    if (info.roofDescription) features.push(info.roofDescription);
  }
  if (info.materials) features.push(info.materials);
  if (info.publicRealm) features.push(info.publicRealm);
}
```

Also: consider a parallel branch in the MANDATORY block for nadir that includes the shadow-direction cue from `project_z_axis_nadir_refs.md`. That memory says "12m tall, cast shadow ~6m NE" is the missing signal at 0deg. This plan scopes that to a short opt-in: if `pitchDeg < 20 && zone.properties.height_m > 0`, append a shadow hint. Exact sun azimuth stays a literal in LIGHTING (`:768`).

**Dependencies.** Phase 5 (variant resolution) so that `variant.renderPrompt.roofView` works, not just parent's.

**Downstream.** None.

**Validation.** Render the same scene at 0deg and 45deg. At 0deg the prompt contains "flat or low-slope brownstone roof with brick chimneys" (from `roofView` at `buildingArchetypes.json:388`). At 45deg it still contains "stoop entries and planted tree pits" (from `mapOverlay` at `:387`).

**Rollback.** Git revert both hunks.

**Size.** M.

**Gate.** scenario-1-nadir.txt reconstructed post-change shows `roofView` language; scenario-1-oblique.txt still shows `mapOverlay` language.

---

### Phase 8 — Mask refinements: scale-aware dilation + erode/blur/clamp feather

**Goal.** Make dilation proportional to polygon size so small polygons don't get 50% mask inflation. Implement the feather upgrade that tooling-plan-v3 Phase 7 item #5 flagged. Absorb that item into this plan so it doesn't get double-done.

**Files.** `useGlobeAIRender.ts:334` (`DILATION_PX = 8`), `:904` (`clipRenderToZones` feather), `:1110` (`generateSingleZoneMask` dilation — dead but same fix for consistency).

**Pseudo-diff.**

```typescript
// useGlobeAIRender.ts:334
const metrics = computePolygonMetrics(zone.coordinates); // per zone
const minEdgeM = metrics ? Math.min(metrics.lengthM, metrics.widthM) : 10;
const dilationPx = Math.min(8, Math.max(2, Math.round(minEdgeM * 0.05)));
// 5% of smaller edge, clamped [2, 8] pixels. A 4m polygon now gets 2px, not 8.
```

For feather: rather than the current blur-everywhere, erode the mask by N pixels, then blur by N pixels, then clamp alpha to [0,1]. Net effect is an inward-only soft edge. This is the pattern tooling-plan-v3 Phase 7 #5 calls for. Suggested implementation uses `ctx.filter = 'blur(Npx)'` after drawing an eroded mask.

**Dependencies.** Phase 1 (metrics helper).

**Validation.** Scenario 5 (6x4 m polygon). Pre-change mask white area = ~24 m^2 + 50% inflation = ~36 m^2. Post-change = ~24 m^2 + 10% = ~26 m^2. Measure in pixels.

**Rollback.** Git revert both hunks.

**Size.** S.

**Gate.** Scenario 5 render produces a building whose visible footprint more closely matches the 6x4 mask than the pre-change mask.

---

### Phase 9 — Backend `render.py` role-honoring labels

**Goal.** Stop hardcoding "3D clay massing model" and "ARCHETYPE REFERENCE — Apply the exact architectural style" regardless of what the client sent. Accept a client-supplied role; fall back to today's text if missing.

**Files.** `backend/app/api/v1/render.py:54-58` (`ArchetypeImage` Pydantic model), `:378-465` (parts assembly).

**Pseudo-diff.**

```python
# render.py:54
class ArchetypeImage(BaseModel):
    image_base64: str
    label: str
    zone_color: Optional[str] = None
    role: Optional[Literal['archetype_reference', 'scene_reference', 'ground_render']] = None
    # role controls the prefix text.

# render.py:417 — primary image
# Today: hardcoded "Image N (SPATIAL LAYOUT): This is a 3D clay massing model..."
# New: accept optional req.image_role; if missing, use a neutral description.
primary_role = req.image_role or 'spatial_layout'
primary_prefix_map = {
    'spatial_layout': "map composite with colored zone footprint polygons showing the proposed site layout",
    'clay_massing': "3D clay massing model showing the exact spatial arrangement of all structures",
    'photographic_scene': "photographic 3D city model capture with colored zone labels over real buildings",
}
parts.append({
    "text": f"Image {next_img_index} (SPATIAL LAYOUT): This is {primary_prefix_map.get(primary_role, primary_prefix_map['spatial_layout'])}. Use this as the definitive spatial reference."
})

# render.py:439 — archetype images
role_prefix_map = {
    'archetype_reference': "Apply the architectural style, materials, and textures from this reference image to the corresponding zone. The polygon shape is authoritative — adapt the style to fit the polygon.",
    'scene_reference': "This is a spatial reference image showing the site layout from a different angle; preserve zone positions and proportions; do NOT copy its style.",
}
for arch_img in req.archetype_images[:6]:
    role = arch_img.role or 'archetype_reference'
    parts.append({
        "text": f"Image {img_idx} ({role.upper()} — {arch_img.label}): {role_prefix_map.get(role, role_prefix_map['archetype_reference'])}{color_ref}"
    })
```

Note the `archetype_reference` wording: it no longer says "apply the exact style". It says "apply the style; the polygon is authoritative". This resolves the audit's C10 contradiction between the archetype card (rectangular building photo) and the MANDATORY (polygon edges = walls) — the image is instructed to yield on shape when they conflict.

**Dependencies.** None. Backward compatible — absence of `role` keeps today's behavior.

**Downstream.** Client (globe) can start passing `role` when it sends images (outside the must-have scope; a follow-up).

**Validation.** Call `render.py` with `role='archetype_reference'`; observe the new prefix in the logged prompt. Regression: call without `role`; observe the legacy-equivalent prefix.

**Rollback.** Git revert the Pydantic + parts-assembly edits.

**Size.** S-M.

**Gate.** Both labeled-and-unlabeled requests produce expected prefixes in the logged prompt body.

---

## 7. Integration with `docs/tooling-plan-v3.md`

Named cross-references only. Do not restate the tooling plan's content here.

1. **tooling-plan-v3 Phase 0 (seed forwarding) is a hard prerequisite** for this plan. That phase is documented at `docs/tooling-plan-v3.md:246-258`. Land it before the Phase 0 gate in this plan (same phase, same fix). Without deterministic renders, every A/B here is contaminated.
2. **tooling-plan-v3 Phase 4b (`siteforge-render-diagnostics` skill) IS the validation harness for this plan.** That phase is documented at `docs/tooling-plan-v3.md:340-348`. Recommend authoring that skill before or in parallel with Phase 2 of this plan so the multi-zoom A/B methodology is available when you need it. If that skill hasn't been authored yet, document manual A/B procedure in each phase's validation note.
3. **tooling-plan-v3 Phase 7 item #5 (erode->blur->clamp feather)** at `docs/tooling-plan-v3.md:412` is ABSORBED into this plan's Phase 8. Do not execute it separately.
4. **tooling-plan-v3 Phase 7 item #7 (building `rotation_degrees` threading)** at `docs/tooling-plan-v3.md:414` is ABSORBED conceptually into this plan's Phase 1 (the metrics helper exposes `bearingDeg`) and Phase 3 (shape adjective). If the tooling plan's item #7 is a separate property on the zone (not derived from polygon geometry), it is still out of scope here — do it in the tooling plan.
5. **tooling-plan-v3 §6.1 gemskills `edit-image` skill source** at `docs/tooling-plan-v3.md:199` can inform prompt phrasing for "white mask = exact footprint, do not extrapolate outside". Skim that skill's `SKILL.md` for inpaint-mask conventions before authoring the Phase 4 MANDATORY language. Do not block Phase 4 on installing the skill.
6. **tooling-plan-v3 §5.1 Globe viewport shim** at `docs/tooling-plan-v3.md:159` is orthogonal. This plan does not touch the shim.
7. **tooling-plan-v3 §11 "Out of scope"** at `docs/tooling-plan-v3.md:463-469` explicitly excludes prompt-engineering. This plan IS the prompt-engineering plan that picks up where the tooling plan leaves off. Confirm with the user this separation is intentional — the user's prompt to author this plan implies yes.

---

## 8. Backend `render.py` changes

Covered in detail in Phase 9. Summary:

- Add optional `role` to `ArchetypeImage` Pydantic (`render.py:54`).
- Add optional `image_role` top-level field to `RenderRequest` (`:61`).
- Branch the labeled text at `:420` and `:439` off those fields; fall back to today's strings if absent.
- Do NOT change the order or count of `parts[]` entries.
- Do NOT change the seed/thinking/config behavior.

Risk flag: other callers of `/api/v1/render/generate` (notably Mapbox `useAIRender.ts`, though unused in production, and any Celery worker) send `ArchetypeImage` without `role`. Pydantic default of `None` plus fallback prefix means they keep working — verify by searching repo for `archetype_images` call sites before shipping.

---

## 9. Subvariant-authority section

The user's second priority. Three concrete changes.

**9.1 `getMapOverlayPrompt` resolves variant first.** Today at `useGlobeAIRender.ts:666` it does `entry.variants?.find((v: any) => v.id === archetypeId)` — it matches the variant by archetype ID, not by the user's selection. Change to use the same `_selected_variant_id` priority chain that image selection already uses at `:487-491`. See Phase 5 pseudo-diff.

**9.2 `getZoneArchetypeInfo` returns variant-shadowed view.** Today at `:703-735` it reads `entry.styleProfile`, `entry.facadeDetail`, `entry.roofDetail`, `entry.title`, `entry.minFloors`, etc. — all from the parent. Variant fields are never consulted. Change to construct `sp = variant?.styleProfile || entry.styleProfile`, `fd = variant?.facadeDetail || entry.facadeDetail`, and so on. This is additive — variants without these fields continue to return parent data.

**9.3 Variant-level fields in JSON (pilot: 3 archetypes).** Add optional `facadeDetail`, `roofDetail`, `renderPrompt`, `suggestedAreaSqm`, `styleProfile.materials` to variant objects. Optional-field absence = fall back. No migration. Pilot on `brownstone_rowhouse_frontage` mansard variant, `collegiate_gothic` stone-tower variant, and one city-kit variant (if directory/ID mapping permits — see `docs/IMAGE_CARD_GAP_ANALYSIS.md`). Use text-level JSON splice per `CLAUDE.md`.

**Why 3 archetypes not 97.** The user's memory `project_chat_history_analysis.md` and `feedback_reference_image_quality.md` both emphasize validating before scaling. A 3-archetype pilot surfaces integration bugs (e.g. shadow-field precedence, when variant overrides only some fields) before you've spent hours on 94 more edits. Gate: pilot passes user-level blind A/B of "rendered variant matches selected image card". Then scale.

**Test the fallback path.** Select a variant that has only a `thumbnailUrl` and a `label`, no overrides. Prompt text should read exactly as it did pre-Phase-5 — proving the shadow pattern falls through cleanly.

---

## 10. Polygon-authority section

The user's first priority. Beyond Phase 1-4, a few specific prompt-text additions.

**10.1 Computed polygon area and dims replace archetype nominal.** Covered in Phase 2. The `suggestedAreaSqm` literal at `useGlobeAIRender.ts:813` goes away; computed `areaM2` from metrics replaces it.

**10.2 Oriented bounding box + longest-edge bearing.** Exposed by `computePolygonMetrics.bearingDeg` (Phase 1). Could feed a future "facade faces north" cue for street-front archetypes. Not in the Phase 1-8 must-do list — add only if Phase 3's shape adjective proves insufficient for orientation-sensitive archetypes (e.g. brownstone rowhouse terraces). Opt-in via archetype flag `orientationSensitive: true`.

**10.3 Shape descriptor token.** Covered in Phase 3. Heuristic in Phase 1 pseudo-diff. Shape values: `rectangular`, `elongated`, `near-square`, `L-shaped`, `irregular`. No more, no less — adding categories risks Gemini not recognizing the word.

**10.4 Mask-is-authoritative prompt language.** Phase 4's MANDATORY. Concrete phrasing: "The white mask shows the EXACT area to edit. THE POLYGON EDGES ARE THE BUILDING'S EXTERIOR WALLS. The building MUST FILL the entire polygon area — edge-to-edge. ... Polygon size is authoritative." This is a direct port from Mapbox `b9cea11` + `7202d32`.

**10.5 Remove "landscaping" from the building branch of MANDATORY.** Current text at `:871` reads "Realistic rooftop materials, facades, and landscaping." On large polygons Gemini reads this permissively and fills with gardens. Phase 4 deletes "and landscaping" from the building branch; keeps it in the ground branch.

**10.6 Scale-aware mask dilation.** Phase 8. 5% of min edge, clamped [2, 8] pixels. Small polygons stop getting ~50% inflated masks.

**10.7 Feather via erode -> blur -> clamp.** Phase 8. Inward-only soft edge. Replaces today's outward blur at `useGlobeAIRender.ts:904`.

Three things NOT to add:
- Do NOT add raw vertex lat/lng to the prompt. Numerical coords without spatial context are noise, per the audit's §8.
- Do NOT add "N-sided polygon" unless it pairs with a shape adjective. "8-sided polygon" alone means nothing useful to Gemini.
- Do NOT try to replace the archetype card image with a polygon-shape-matched generated image in this plan. That's a different project (reference-generation workflow, per `feedback_reference_image_quality.md`).

---

## 11. Camera-angle section

**11.1 Read pitch from the Three.js camera.** Already happens at `useGlobeAIRender.ts:746-757`. `pitchDeg` is computed. Plan does not change this.

**11.2 Map pitch to angle band.**

| pitchDeg | Band | Archetype field | Feature emphasis |
|---|---|---|---|
| < 20 | nadir | `renderPrompt.roofView` | `info.aerialAppearance`, `info.roofDescription`, demoted `info.facadeDescription` |
| 20-60 | oblique | `renderPrompt.mapOverlay` | `info.facadeDescription`, `info.roofDescription`, `info.materials` |
| > 60 | low-oblique / ground | `renderPrompt.mapOverlay` | `info.facadeDescription`, foreground cues (not in scope — street view owns ground) |

**11.3 Branch `getMapOverlayPrompt` by pitch band.** Phase 7 pseudo-diff.

**11.4 Branch zone-line features by pitch.** Phase 7 pseudo-diff, lines `:822-832`.

**11.5 Branch MANDATORY by pitch (optional).** Nadir benefit: add shadow-direction cue if `pitchDeg < 20` and building height is known. Text suggestion: "Building is Xm tall; cast a realistic shadow to the NE based on golden-hour sun." Derives direction from the LIGHTING text ("warm southwest sun" -> shadow NE). This is optional in Phase 7; tune based on visual results.

**11.6 Include computed altitude and frame footprint in the prompt.** Untested assumption: the `camera.position.length()` gives altitude above ellipsoid on globe. Frame footprint in meters can be derived from canvas width/height and camera FOV. If this proves accurate, add to the COMPOSITION line: "Camera altitude X m; frame covers ~Y m x Z m at ground." Skip if the math is fiddly; not a blocker for the main polygon-authority goals.

---

## 12. Prompt structure — the new skeleton

What every globe Pass 2 prompt should look like after Phase 1-9 land. Section order is significant: Gemini weights later instructions more heavily per `CLAUDE.md`, so MANDATORY stays last.

```
STYLE: <style preset, per useGlobeAIRender.ts :862>
COMPOSITION: <pitchDesc> view from 3D photorealistic city model. Camera altitude ~<alt>m, frame ~<frameW>x<frameH>m. Render buildings with correct 3D perspective for this viewing angle. (Phase 11.6 adds the altitude clause if feasible.)
LIGHTING: <lighting preset>
CONTEXT: <unchanged, :865>
COLOR TEMPERATURE MATCHING: <unchanged, :866>
ATMOSPHERIC PERSPECTIVE: <unchanged, :867>
NUMERICAL INVENTORY: <unchanged, :868>
ZONES:
  1. [deep maroon] Mansard Brownstone (rectangular) | 3F 12m | polygon 18x8m (144m²) | shape: rectangular | <variant-resolved renderPrompt + features matching pitch> | polygon@(...)
  2. [steel blue] Parisian Corner Dome (near-square) | 4F 16m | polygon 22x20m (440m²) | shape: near-square | <variant renderPrompt for oblique> | polygon@(...)
ZONE IDENTIFICATION: <unchanged, :870>
MANDATORY (buildings): The white mask shows the EXACT area to edit. THE POLYGON EDGES ARE THE BUILDING'S EXTERIOR WALLS. The building MUST FILL the entire polygon area — edge-to-edge. Do NOT render driveways, plazas, or gardens between the building and the polygon edge. Do NOT place a smaller building inside a larger polygon. Archetype metadata describes STYLE, MATERIALS, and CHARACTER only. If the polygon is smaller than a typical archetype example, render a smaller building in that style. If larger, scale it up. Polygon size is authoritative.
(at nadir pitch < 20deg, append:) Each building is <H>m tall; cast a realistic shadow toward the NE based on the golden-hour sun direction.
PROHIBITIONS: <unchanged, :872>
SITE BOUNDARY: <unchanged, :873>
OCCLUSION: <unchanged, :874>
FINAL CONSTRAINT: <unchanged, :875>

ARCHETYPE STYLE REFERENCES: <unchanged, :1597-1606>
```

Example interpolation for a brownstone rowhouse variant at 45deg oblique, 18x8 m polygon:

```
1. [deep maroon] Brownstone Rowhouse Frontage (rectangular) | 3F 12m | polygon 18x8m (144m²) | shape: rectangular | Replace the colored building block with a photorealistic brownstone rowhouse frontage. The building has warm brown sandstone facades with carved entry stoops, tall double-hung windows with stone lintels, decorative cornices, and wrought-iron railings. Townhouse rhythm with stoop entries and planted tree pits. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k Style: Mansard-roofed brownstone with slate roof. | polygon@(500,420)(520,420)(520,500)(500,500)
```

Same archetype at 0deg nadir:

```
1. [deep maroon] Brownstone Rowhouse Frontage (rectangular) | 3F 12m | polygon 18x8m (144m²) | shape: rectangular | Replace the colored block viewed from above with a flat or low-slope brownstone roof with brick chimneys, dark membrane roofing, and occasional roof gardens. Low stone parapet walls. Keep surrounding context exactly as-is. | polygon@(500,420)(520,420)(520,500)(500,500)
```

Notice the archetype-feature text is entirely different between the two; today's pipeline produces byte-identical feature text across the pair (reconstructed in `globe-v2/scenario-1-nominal-rectangle-nadir.txt`).

---

## 13. Validation harness (ties to tooling-plan Phase 4b)

**Fixture zones.** Reuse the 6 polygon shapes already dumped in `globe-v2/scenario-*.txt`:

| Fixture | Shape | Dims | Notes |
|---|---|---|---|
| F1 | Nominal rectangle | 18x8 | Matches brownstone archetype. Baseline. |
| F2 | Elongated | 40x4 | Aspect 10:1. Tests shape adjective. |
| F3 | Near-square | 15x14 | Tests the shape threshold. |
| F4 | L-shape | 200m², 8 vertices | Tests irregular + clipping. |
| F5 | Tiny | 6x4 | Tests dilation scaling. |
| F6 | Huge | 80x40 | Tests "polygon size authoritative". |

**Grid.** Each fixture x 2 camera pitches (0deg, 45deg) x 2 variants (parent, selected subvariant where applicable) = 24 renders per regression pass. Scripted via the `siteforge-render-diagnostics` skill (tooling-plan Phase 4b) once it exists.

**Success criteria per render.**

1. Polygon coverage: building pixels cover >= 85% of the mask area, <= 105% of the polygon area. Measure: count non-background pixels inside polygon vs total polygon area in pixels.
2. Subvariant recognition: blind visual compare against the thumbnail of the selected variant. Pass if a human can identify it as the same variant vs a random other variant from the archetype.
3. No rendered content outside the mask boundary. Measure: pixel-level diff of rendered image vs original satellite outside the mask. Target: <= 0.5% changed pixels outside mask (small amount allowed for blending).

**A/B gate.** Every phase is compared against its prior phase's baseline on all 24 renders. A phase ships only if:
- It improves at least one success criterion on >= 1 fixture.
- It does NOT regress any fixture's success criterion by more than 1%.

**Manual fallback.** If the diagnostics skill isn't authored yet, run fixtures 1, 4, 6 manually for each phase, eyeball the three criteria, and log results in a phase-specific markdown note under `artifacts/prompt-audit/phase-<N>-results.md`. Do not block phases on the skill; manual validation is acceptable.

---

## 14. Risk register

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Gemini ignores the new "polygon edges ARE walls" language the same way it ignores the mask boundary | High | Measure. If scenario 6 doesn't improve, the one-line port was insufficient — escalate to stronger image-side signals (clay anchor enforcement) rather than adding more words. |
| R2 | New shape adjective words ("L-shaped", "elongated") degrade prompt quality by confusing Gemini | Medium | Test each word independently. If "L-shaped" produces weirder renders than unspecified, strip it from the adjective vocabulary. Keep the vocabulary tiny. |
| R3 | Variant metadata is inconsistent across 97 archetypes (some have renderPrompt.roofView, some don't) | High | Already confirmed: `renderPrompt` has `mapOverlay` and `roofView` on every building archetype checked. For archetypes missing `roofView`, the Phase 7 code path falls back to `mapOverlay` — no crash, just no nadir improvement. Audit `buildingArchetypes.json` with `grep -c '"roofView"'` to confirm count before assuming ubiquity. |
| R4 | Camera pitch reading breaks on first-load before map ready (pitchDeg = NaN) | Medium | Add `isFinite(pitchDeg)` guard. Default to oblique bucket on NaN. |
| R5 | Backend label change breaks other callers (Mapbox file, Celery workers) | Medium | Grep for `archetype_images` and `ArchetypeImage` to enumerate callers. Default of `role=None` preserves legacy behavior. No caller is known to set `role`; therefore no caller breaks. Verify on branch before merging. |
| R6 | Feather change (erode -> blur -> clamp) breaks renders that currently look good | Medium | Phase 8 has an explicit rollback clause. If scenarios 1-4 look worse post-change, revert. Dilation change is separable from feather change — roll them out in two sub-steps. |
| R7 | `computePolygonMetrics` shape heuristic misclassifies (e.g. a trapezoid becoming "rectangular") | Low | Heuristic is explicitly "untested assumption" in Phase 1. Tune on the 6 fixtures before declaring done. Easy to fix; isolated. |
| R8 | User's selected variant ID doesn't actually reach `zone.properties.development_selected_variant_id` due to a UI bug | Low-Medium | `ZonePropertiesPanel.tsx:462-481` shows the writes happen. Verify end-to-end on `localhost:5174` before Phase 5 validation (per `CLAUDE.md` rule "test locally before pushing"). |
| R9 | Adding shape token to zone line pushes prompt over a length that Gemini handles well | Low | Audit shows prompt sweet spot is ~200 chars per zone. Added shape token adds ~10 chars. Safe. Monitor with the existing log at `useGlobeAIRender.ts:1610`. |
| R10 | Phase 6 JSON edits corrupt `thumbnailUrl` paths | Medium | Explicit `CLAUDE.md` rule: never `json.dump` `buildingArchetypes.json`. Use text-level splice. Run `grep -c 'thumbnailUrl' buildingArchetypes.json` before and after — count must not change (add is additive). |
| R11 | Seed-forwarding prerequisite isn't actually broken; plan's Phase 0 is a no-op | Low | Verify first (see Phase 0 note). If seed is already forwarded, measure variance anyway — if >0, the non-determinism has a different root cause (LOD streaming, per `SAME_ANGLE_DEGRADATION_DIAGNOSTIC.md`), and later phases' A/B testing carries that noise until LOD stabilizes. |
| R12 | Globe single-shot path already renders "good enough" for some scenes and these changes reduce quality on them | High | G4 is the explicit acceptance criterion. Run scenario 3 (near-square, matches archetype) through every phase's A/B. If it regresses, stop and re-tune. |

---

## 15. Rollback strategy

File-by-file revert map. Every phase is a single revert unit; no feature flags proposed.

| Phase | Files to revert | Revert notes |
|---|---|---|
| 0 | `backend/app/api/v1/render.py` | Revert to pre-seed-forwarding commit if user confirms Phase 0 was the seed fix. |
| 1 | `frontend/src/components/viewer/globe/polygonMetrics.ts` (delete) | New file; delete whole. Nothing else imports it until Phase 2. |
| 2 | `useGlobeAIRender.ts:803-816` | Single-function hunk. `info.suggestedAreaSqm` read path still present in `getZoneArchetypeInfo`, no side effect. |
| 3 | `useGlobeAIRender.ts:801-816, :856-857` | Shape-token hunk. Can revert independently of Phase 2 (Phase 2 still works without shape token). |
| 4 | `useGlobeAIRender.ts:871` | One-line revert. |
| 5 | `useGlobeAIRender.ts:652-738` | Two-function revert. Variant resolution reverts to match-by-archetypeId. |
| 6 | `frontend/src/data/buildingArchetypes.json` | Text-level splice reversed (undo the 3 pilot inserts). Variants without overrides fall back to parent — already works. |
| 7 | `useGlobeAIRender.ts:652, :819, :822-832` | Camera-angle branch revert. Zone-line features revert to unbranched. |
| 8 | `useGlobeAIRender.ts:334, :904, :1110` | Dilation and feather revert. Two independent hunks. |
| 9 | `backend/app/api/v1/render.py:54, :420, :439` | Pydantic + parts-assembly revert. Pydantic field with default None is additive — safe to leave in even if parts assembly reverts. |

Feature flags explicitly NOT proposed, because:
- Each phase is small enough to revert quickly.
- Flag surface adds coupling between phases (flag X enables both Phase 5 and Phase 7 behavior).
- The user is a solo developer working over a week; there's no production cutover timeline demanding toggles.

If a longer-lived flag IS needed: propose `enablePolygonAuthoritySchema: boolean` in `frontend/.env` gating Phase 2-4 prompt text swap only. Phases 5-9 are additive enough to not need a flag.

---

## 16. Test plan before shipping

Per `CLAUDE.md`: "Test locally before pushing." Test on `localhost:5174`.

**End-to-end scenarios on localhost:**

1. **Rectangle, matches archetype.** Draw an 18x8 m rectangle. Assign `brownstone_rowhouse_frontage` parent variant. Render at 45deg oblique. Verify: no crash, building fills polygon, style matches thumbnail.

2. **L-shape, selected mansard variant.** Draw an 8-vertex L. Assign `brownstone_rowhouse_frontage`, select the mansard subvariant (Phase 6 pilot). Render at 45deg oblique. Verify: prompt text contains "mansard" (console log), image shows mansard roof, building respects L shape.

3. **Huge rectangle, nadir.** Draw an 80x40 m rectangle. Assign any building archetype. Render at 0deg nadir. Verify: building fills polygon edge-to-edge (not a single small building in a corner with garden), prompt text mentions "roof" language not "facade".

**Regression probes.**

- Remove variant selection, re-render. Verify fallback path produces the parent-archetype prompt text (exactly what it did pre-Phase 5).
- Tiny polygon (4x3 m) render at 45deg. Verify no crash, dilation reasonable.
- Huge polygon (500x500 m) render. Verify no crash (caps/clamps engage).

**Before pushing per `CLAUDE.md`:**
- `cd frontend && npm run type-check && npm run lint`.
- Check both remotes: `git log origin/master --oneline -5` and `git log beeman/master --oneline -5`.
- No force push.

---

## 17. Prioritized changes — "if you only do N, do these"

If time is scarce, work down this list. Each item is ranked by impact-per-effort. The user's priority-1 and priority-2 are both front-loaded.

1. **Phase 4 — MANDATORY port.** One-line edit. Covers scenarios 5 and 6 (tiny and huge). Directly addresses the user's most common complaint. Size S.
2. **Phase 2 — Computed area in scale token.** Kills the 150 m^2 vs 3200 m^2 lie. Requires Phase 1 helper. Size S.
3. **Phase 5 — Variant-resolved prompt text.** Fixes the image-says-brownstone-text-says-rowhouse contradiction. Size M.
4. **Phase 7 — Pitch-branched renderPrompt selection.** Unlocks `roofView` at nadir. Biggest quality lever after the two polygon fixes. Size M.
5. **Phase 3 — Shape adjective.** Adds one word per zone line. Cheap, measurable. Size S.

Stop here if time is tight. Phases 6, 8, 9 are polish that improves the long tail without fundamentally shifting the user's top complaints.

---

## 18. File index

- This plan: `artifacts/prompt-audit/POLYGON_AUTHORITY_PLAN.md`
- One-page summary: `artifacts/prompt-audit/CHANGES_AT_A_GLANCE.md`
- Primary audits: `artifacts/prompt-audit/AUDIT_REPORT.md`, `artifacts/prompt-audit/globe-v2/GLOBE_POLYGON_AUDIT.md`
- Scenario fixtures: `artifacts/prompt-audit/globe-v2/scenario-*.txt`
- Related tooling plan: `docs/tooling-plan-v3.md`
- Project conventions: `CLAUDE.md`
