# Globe Polygon-Shape Audit — how polygon geometry reaches (and fails to reach) Gemini

Date: 2026-04-18
Scope: `frontend/src/components/viewer/globe/useGlobeAIRender.ts` + `globe/GlobeSitePlannerMap.tsx` + `globe/useGlobeDrawing.ts` + backend relabelling in `backend/app/api/v1/render.py`. Mapbox pipeline out of scope (per user request).
Focus: how polygon shape, size, orientation, vertex count, irregularity and aspect ratio flow into the three signals Gemini sees — metadata text, images, prompt text — and where those signals contradict each other.

Builds on the prior round's §2b and §4 globe rows (`artifacts/prompt-audit/AUDIT_REPORT.md`). Where a prior finding still applies it is cited briefly; where it was underweighted the text says so.

---

## 1. Executive summary

1. **The single biggest globe-specific gap is the absence of any computed polygon-actual dimensions in the prompt text.** Mapbox's `computeFootprintDims` (two-longest-edges → `"18m×8m"`) is not duplicated anywhere in `useGlobeAIRender.ts`. The zone line carries archetype NOMINAL width/depth (`suggestedWidth_m`, `suggestedDepth_m`) or NOMINAL area (`suggestedAreaSqm`) — never the user's polygon. For the reference archetype `brownstone_rowhouse_frontage` the only dimensional field present is `suggestedAreaSqm: 150`, so the zone line reads `3F 12m ~150m²` regardless of whether the polygon is 6×4m (scenario 5) or 80×40m (scenario 6). The text actively misinforms by a factor of 21× in scenario 6. (useGlobeAIRender.ts:812-813)
2. **Three of the four recent Mapbox polygon-authority fixes are NOT ported to globe.** Only `4e23345` (site_boundary as clip) has an effective equivalent (useGlobeAIRender.ts:322, 1105). `b9cea11` ("polygon edges ARE building walls"), `7202d32` ("polygon size is authoritative"), and `279868f` (auto-delegate to per-zone on partial occlusion) are absent. Because `PERZONE_THRESHOLD = 99` (line 1070) effectively disables the per-zone path, the fixes the user made in Mapbox protect a pipeline globe no longer touches. This is the user's recent work protecting the wrong surface.
3. **Polygon shape is described only geometrically (mask pixels + `polygon@(x,y)` coord list) — never in words.** The tokens "rectangular", "L-shaped", "elongated", "narrow", "square", "irregular" are literally absent from `buildPrompt` and `buildSingleZonePromptForPerZone`. When the archetype image depicts a rectangle and the polygon is an L, the prompt TEXT says nothing about the mismatch. (useGlobeAIRender.ts:838-848; scenario-4-L-shape.txt)
4. **Archetype `renderPrompt.mapOverlay` is pasted verbatim into the zone-line features block, carrying assumptions that can contradict the polygon.** Brownstone's mapOverlay contains literal strings "Keep the exact same building footprint and height" and "3-4 storey townhouse rhythm"; civic plaza's says "Large RECTANGULAR hardscape". On a non-rectangular or non-typical polygon these clauses fight the mask. (useGlobeAIRender.ts:823-825; buildingArchetypes.json:387; openSpaceArchetypes.json:1620)
5. **The per-zone and single-shot paths see different polygon shapes.** `buildSingleZonePromptForPerZone` drops `_camera` and `_terrainHeight` (line 1155-1156) AND drops the `polygon@(…)` coord token AND drops the pixel-coord list entirely — only archetype dims reach it. This is strictly less polygon information. With PERZONE_THRESHOLD=99 this path is de facto dead for real sites, but the ~18m×8m reconstructed prompt in the prior round is from this dead code path; a real globe render has MORE polygon text than that dump suggests.
6. **`roofView` archetype text is never selected at nadir, even though nadir is exactly when it becomes correct.** `getMapOverlayPrompt` (line 819) unconditionally returns `renderPrompt.mapOverlay` (facade-heavy), never `renderPrompt.roofView`, despite both existing on every archetype. (scenario-1-nominal-rectangle-nadir.txt)
7. **The mask-image and the text are the only two signals that CAN represent an irregular polygon faithfully; the archetype image ALWAYS depicts a simple rectangular footprint.** Three-way contradiction for any L-shape or concave polygon; the prompt never tells Gemini which of the three signals to trust. `clipRenderToZones` (line 904) is a cosmetic fix — it crops the output but does not re-render architecture to honour the shape.
8. **Mask dilation (`DILATION_PX = 8`, ~2m) is a constant regardless of polygon size.** On a 4m-wide polygon (scenario 5) that's a 50% inflation; on 80m (scenario 6) it's 2.5%. Gemini's effective editable area for scenario 5 is ~50% larger than the user's polygon, which creates a systematic bias toward "polygon smaller than user thinks" — concealing the archetype-too-big-for-polygon failure the user would otherwise spot. (useGlobeAIRender.ts:334)

---

## 2. Polygon-property flow map (globe pipeline only)

Where each geometric property of the user's polygon ends up, for the single-shot render path (the one realistically used, per `PERZONE_THRESHOLD = 99`).

| Polygon property | Computed? | Reaches prompt text? | Reaches mask? | Influences archetype image choice? | Globe code — file:line |
|---|---|---|---|---|---|
| Raw lat/lng vertex list | Yes — passed through unchanged from drawing state | No (only via `polygon@(px,py)` pixel projection) | Yes (projected to pixels, drawn as white) | No | useGlobeDrawing.ts:67, useGlobeAIRender.ts:342-357 |
| Vertex count (3, 4, 8, …) | Implicitly | Implicitly — more (x,y) pairs in `polygon@(…)` token. No explicit "N-sided" text. | Yes (more path vertices) | No | useGlobeAIRender.ts:845-846 |
| Pixel-projected polygon (current camera) | Yes via `projectToPixels` | Yes — `polygon@(x,y)(x,y)…` string | Yes | No | useGlobeAIRender.ts:840-847, 345-354 |
| Polygon area (degree² shoelace, NOT m²) | Yes, for SORTING only | No (sort order changes zone ordering in ZONES block; the area itself is never printed) | No | No | useGlobeAIRender.ts:779-790 |
| Polygon area (m²) | **NEVER COMPUTED** for the user's polygon | No. Zone line's `~{N}m²` (line 813) is `info.suggestedAreaSqm` from archetype, not polygon | No | No | absent |
| Polygon perimeter | Never computed | No | No | No | absent |
| Two longest edges (Mapbox `computeFootprintDims` pattern) | **NEVER COMPUTED** | No | No | No | absent — `haversineDistance` is imported in useGlobeDrawing.ts:47 but never called on zone polygons |
| Axis-aligned bounding box | Only in mask height-extension (min/max of pixel X/Y — line 1273-1274, 1309) | No | Indirectly via the rect used to height-extend a building's roof region | No | useGlobeAIRender.ts:1273-1276 |
| Oriented bounding box (min-area) | Never computed | No | No | No | absent |
| Aspect ratio | Never computed from polygon. Archetype `aspectRatio` field IS read (line 691, 733, 1182) but describes the ARCHETYPE, not the polygon | Only when `info.aspectRatio` is set by the archetype entry and the per-zone builder is hit (per-zone is dead code at threshold=99) | No | No | useGlobeAIRender.ts:1180-1182 |
| Convexity / concavity | Never detected | No | Yes (mask reflects it) | No | absent |
| Orientation / bearing of longest edge | Never computed | No | Indirectly (mask is oriented) | No | absent |
| Polygon dominance in frame (% of canvas) | Never computed | No | N/A | No | absent |
| Shape SEMANTICS (rectangle vs strip vs L) | Never inferred | No text | Yes visually | No | absent |

Complementary (textual) surfaces where polygon info COULD go but doesn't:

- The `scale` token in zone line (line 804-816) has a specific slot `~{W}×{D}m` that is populated from archetype, not polygon — a one-line change would swap it.
- The MANDATORY line (line 871) is a natural place for "polygon size is authoritative" text (the Mapbox commit 7202d32 modification) and is not there.
- The `ZONE IDENTIFICATION` line (line 870) could note "polygon shape: irregular" but doesn't.

---

## 3. Scenario prompt dumps

All under `artifacts/prompt-audit/globe-v2/`. Each is a reconstructed (not captured — no logs in repo) single-shot `buildPrompt` output using `brownstone_rowhouse_frontage` except 4b. Each scenario header lists file:line sources and polygon vertex assumptions.

| File | Polygon | Camera | Purpose |
|---|---|---|---|
| `scenario-1-nominal-rectangle-oblique.txt` | 18m×8m rect, 4 verts | 45° | Baseline — archetype-matching polygon |
| `scenario-1-nominal-rectangle-nadir.txt` | same 18×8 | 0° | Shows what changes by angle (exactly one line) |
| `scenario-2-long-skinny-40x4.txt` | 40×4 (10:1), 4 verts | 45° | Aspect-ratio mismatch vs chunky archetype |
| `scenario-3-near-square-15x14.txt` | 15×14, 4 verts | 45° | Polygon-vs-rowhouse-rhythm mismatch |
| `scenario-4-L-shape.txt` | L, 8 verts ~200m² | 45° | Irregular vs convex-archetype |
| `scenario-4b-L-shape-plaza-ground-zone.txt` | same L, ~200m² | 45° | Ground-zone path, archetype says "rectangular" |
| `scenario-5-tiny-6x4.txt` | 6×4 rect, 24m² | 45° | Polygon SMALLER than archetype nominal |
| `scenario-6-huge-80x40.txt` | 80×40 rect, 3200m² | 45° | Polygon LARGER than archetype nominal by 21× |

Key takeaways across scenarios:
- Text-level delta between scenarios 2, 3, 5, 6 (all rectangles) is literally only the `polygon@(…)` pixel string. Every other word identical. Gemini receives near-identical text for wildly different polygon sizes.
- Scenarios 4 and 4b add one extra pair of `(x,y)` tokens each for the notch vertices. No semantic text ever changes.
- Between oblique and nadir (scenario 1 pair), exactly one line differs — the `pitchDesc` substitution. Shape description is invariant to camera.

---

## 4. Conflicts grouped by polygon characteristic

Verbatim quotes from source.

### 4.1 Polygon SIZE vs archetype nominal size

| # | Characteristic | Text that implies one thing | Visual/mask that implies another | Severity | File:line |
|---|---|---|---|---|---|
| S1 | Polygon area | Zone line: `3F 12m ~150m²` (literal archetype `suggestedAreaSqm`) — useGlobeAIRender.ts:813 | Mask can be anywhere from 24m² (scenario 5) to 3200m² (scenario 6). Discrepancy is UNSTATED. | **Hard contradiction** at both size extremes | useGlobeAIRender.ts:803-817 |
| S2 | Polygon-must-equal-footprint authority | MANDATORY: `Replace the colored polygon overlays visible in the screenshot with photorealistic architectural materials` (line 871) — permissive | Mapbox equivalent (post-b9cea11): `THE POLYGON EDGES ARE THE BUILDING'S EXTERIOR WALLS. The building MUST FILL the entire polygon area — edge-to-edge. Do NOT render landscaping, driveways, plazas … between the building and the polygon edge.` | **Hard contradiction** — unported fix | useGlobeAIRender.ts:871; missing equivalent for useAIRender.ts:1820 |
| S3 | Scale-up-vs-scale-down guidance | **Nothing** in the globe prompt tells Gemini what to do when polygon is larger or smaller than archetype | Mapbox MANDATORY (post-7202d32): `If the polygon is smaller than a typical archetype example, render a smaller building in that style. If larger, scale it up. Polygon size is authoritative.` | **Hard contradiction** — unported fix | missing — single-line addition at line 871 is the fix |
| S4 | Floor count interpretation at size extremes | Zone line fixes `3F 12m` from zone props, whatever polygon size | Archetype image shows one archetype at one scale. On a 3200m² polygon, is it 1 building at 3F or 20 at 3F? Nothing says. | Soft tension → hard at extremes | useGlobeAIRender.ts:799-816 |

### 4.2 Polygon SHAPE / VERTEX COUNT / IRREGULARITY

| # | Characteristic | What prompt says | What the actual polygon is | Severity | File:line |
|---|---|---|---|---|---|
| SH1 | Shape keyword | Prompt NEVER says "rectangle" / "L" / "irregular" / "n-sided" | Any shape the user drew | Hard gap (always) | useGlobeAIRender.ts: entire `buildPrompt` |
| SH2 | Archetype mapOverlay references "rectangular hardscape" etc | `Large rectangular hardscape of cut stone or granite pavers` (civic plaza archetype) | Polygon may be L-shaped or trapezoidal | Hard contradiction for non-rectangular polygons | openSpaceArchetypes.json:1620; propagates via useGlobeAIRender.ts:819 |
| SH3 | Archetype image always simple convex | hero.png + variant_N.png are typically a single rectangle-looking building | Polygon L or concave | Hard contradiction; no text acknowledges it | useGlobeAIRender.ts:502, render.py:439 |
| SH4 | Backend label forces style application | `Apply the EXACT architectural style, materials, and textures from this reference image to the corresponding zone.` — render.py:439 | When the zone is L and the image is a rectangle, "exact" is undefined | Soft tension → hard on complex polygons | render.py:439 |
| SH5 | Vertex count has zero textual representation | Gemini can count (x,y) pairs in `polygon@(...)` but is not instructed to | N/A | Gap — low severity; visual signal carries the info | useGlobeAIRender.ts:845-846 |
| SH6 | `clipRenderToZones` is post-process cosmetic | `For each zone, only keep the AI render within that zone's polygon (with a soft 6px blur feather)` — line 895-902 | If Gemini rendered a rectangular building straddling the L notch, the clip straight-cuts through the architecture — half-building artifact | Severe for L-shapes specifically | useGlobeAIRender.ts:904 |

### 4.3 Polygon ASPECT RATIO / PROPORTIONS

| # | Characteristic | Text signal | Visual/image signal | Severity | File:line |
|---|---|---|---|---|---|
| AR1 | Archetype `aspectRatio` string (e.g. "4:3") is in the type | Only injected when `suggestedWidth_m && suggestedDepth_m` present in the per-zone builder (line 1180-1182). Not injected in `buildPrompt` (single-shot) at all | Archetype image shows inherent proportions | Soft gap — nullified by PERZONE_THRESHOLD=99 | useGlobeAIRender.ts:733, 1182 |
| AR2 | 10:1 strip vs 1:1 square polygons → same text | Zone line identical except pixel coords | Mask differs wildly; archetype image same | Hard contradiction at extremes (scenarios 2 & 3) | useGlobeAIRender.ts:803-816 |
| AR3 | Polygon aspect computed? | No (two-longest-edges pattern missing) | N/A | Pure gap | absent |

### 4.4 Polygon ORIENTATION / BEARING

| # | Characteristic | Text signal | Visual signal | Severity | File:line |
|---|---|---|---|---|---|
| O1 | Long axis of polygon (N–S vs E–W) | None — no "bearing", "orientation", "facing" token | Mask reflects it | Gap — relies on Gemini's spatial inference | absent |
| O2 | Archetype reference image "front entrance facade" | Backend label: `Brownstone Rowhouse Frontage (front entrance facade)` — implies the image's left side is the front | Polygon has no front/back indicator | Soft contradiction when orientation matters (street-frontage buildings) | useGlobeAIRender.ts:524 |
| O3 | Roof aerial view | `info.aerialAppearance` (line 830) is added as `Aerial: ...` token in zone-line features | Mapped to orientation unclearly | Soft | useGlobeAIRender.ts:830 |

### 4.5 Mask vs text arbitration

| # | Seam | Text | Mask | Severity | File:line |
|---|---|---|---|---|---|
| M1 | "Exact area to edit" vs "colored polygon" identity | MANDATORY: `The white mask shows the EXACT area to edit. Replace the colored polygon overlays` — two rules, slightly different. The mask is dilated by ~2m (line 334) so the white area is SLIGHTLY LARGER than the colored polygon | Mask = dilated polygon; colored overlay (in screenshot) = exact polygon | Soft tension; magnified at small polygons (scenario 5) where dilation = 50% inflation | useGlobeAIRender.ts:871, 334 |
| M2 | `polygon@(x,y)` pixel list vs mask | Pixel list is the TIGHT polygon; mask is DILATED + HEIGHT-EXTENDED for buildings | Three different shape signals: text-coords, mask, colored overlay | Soft — unlikely to be semantically parsed by Gemini | useGlobeAIRender.ts:845-847 vs 334, 365-370 |

### 4.6 Site-boundary interaction

| # | Characteristic | Globe behaviour | Mapbox fix 4e23345 | Port status |
|---|---|---|---|---|
| SB1 | site_boundary as clip | Uses `ctx.save` + path + `ctx.clip()` at line 317-322 (inside `generateMask`) and at line 1094-1105 (inside `generateSingleZoneMask`) | Mapbox added `ctx.clip()` at `generateBinaryMask` in commit 4e23345 | **Ported** (actually predated Mapbox fix — globe already had it) |
| SB2 | Text statement "stay inside site boundary" | `SITE BOUNDARY:` line at 873 explicitly warns not to add things outside the colored zone polygons | Mapbox commit 4e23345 added a line `All rendered changes must remain strictly within the site boundary polygon; preserve the satellite imagery exactly as-is beyond it.` | Globe has an EQUIVALENT worded slightly differently (line 873) |
| SB3 | Overlap of site_boundary with an irregular zone near the edge | Zone polygons are clipped to boundary. Good. | same | fine |

### 4.7 Occlusion / adjacency

| # | Characteristic | Globe | Mapbox 279868f | Port status |
|---|---|---|---|---|
| OC1 | Partial-occlusion detection → per-zone delegation | None. `render()` single-shot only. `renderPerZone` only fires when `editableZones.length >= PERZONE_THRESHOLD` (99). | `render()` at useAIRender.ts: if `partialOcclusion.size > 0`, delegates via `renderPerZoneRef.current` | **NOT ported** — high severity |
| OC2 | Inline occlusion hint in zone line | Yes (line 852-854: `PARTIALLY BEHIND A BUILDING (~N% hidden) — render ONLY the visible portion`) | Yes, different text | Present in both (pre-279868f logic) |
| OC3 | Mask subtraction for occluded ground zones | Yes — `subtractBuildingSilhouettes` at line 258; `occluderGeometry` wired through `generateMask` line 381-398 | Yes | Present in both |

---

## 5. Unported polygon fixes from Mapbox

For each of the four recent Mapbox-only commits, verify whether the equivalent exists in `useGlobeAIRender.ts`.

### 5.1 `b9cea11` — "polygon edges ARE building walls"

- **What it fixed (Mapbox):** replaced `The polygon IS the building's exact footprint area and shape — scale each archetype to fit the polygon` with `THE POLYGON EDGES ARE THE BUILDING'S EXTERIOR WALLS. The building MUST FILL the entire polygon area — its footprint must match the polygon shape and size exactly, edge-to-edge. Do NOT render landscaping, driveways, plazas, gardens, or any unused space between the building and the polygon edge. Do NOT place a smaller building inside a larger polygon. The building's floor plan conforms to the polygon's shape.` in `buildSCHEMAPrompt` MANDATORY.
- **Globe equivalent:** NONE. The closest globe text is the MANDATORY at useGlobeAIRender.ts:871:
  > `The white mask shows the EXACT area to edit. Replace the colored polygon overlays visible in the screenshot with photorealistic architectural materials. Read the text label on each polygon to identify what to render there. Realistic rooftop materials, facades, and landscaping. Match scale and density of surrounding real 3D buildings. Rendered building facades and roofs MUST have the same color cast, warmth, and atmospheric tint as adjacent real buildings.`
  Note "Realistic rooftop materials, facades, and **landscaping**" — the word "landscaping" here is the OPPOSITE of what Mapbox explicitly prohibits. On a big polygon, this actively invites the toy-castle-on-a-pedestal failure.
- **Severity:** HIGH. The user saw this failure mode in Mapbox and explicitly fixed it; the same mode is reproducible in globe for any polygon larger than the archetype nominal (scenario 6).
- **Evidence:** `Grep "EXTERIOR WALLS\|FILL the entire"` returns 0 matches in `useGlobeAIRender.ts`.

### 5.2 `7202d32` — "polygon size is authoritative"

- **What it fixed (Mapbox):** added to MANDATORY: `Archetype metadata (floor count, height, nominal dimensions) describes STYLE, MATERIALS, and CHARACTER only; do NOT extend the building beyond the polygon to match the archetype's nominal size. If the polygon is smaller than a typical archetype example, render a smaller building in that style. If larger, scale it up. Polygon size is authoritative.`
- **Globe equivalent:** NONE. `Grep "authoritative"` returns 0 matches in `useGlobeAIRender.ts`.
- **Severity:** HIGH. This fix is ONE LINE of prompt text, and it covers scenarios 5 (too small) AND 6 (too big). Lowest-cost port in the whole audit.
- **Recommendation:** literal text insertion after line 871.

### 5.3 `279868f` — auto-delegate to per-zone on partial occlusion

- **What it fixed (Mapbox):** added `renderPerZoneRef` forward-ref, wired via useEffect, and delegates in `render()` when `partialOcclusion.size > 0`. Added `forceSingleShot` escape hatch.
- **Globe equivalent:** NONE. `render()` calculates `partialOcclusion` (line 1378), uses it to skip labels/borders (line 1515-1519), adds hint text to zone lines (line 852-854), but NEVER delegates to `renderPerZone`. With `PERZONE_THRESHOLD = 99` in `GlobeAIRenderPanel.tsx:87`, `renderPerZone` is only called for 99+ zones — effectively never.
- **Severity:** MEDIUM. The existing single-shot hint text ("PARTIALLY BEHIND A BUILDING") does some of the work, but the painter's-algorithm benefit of rendering ground first is absent.
- **Recommendation:** port the delegation pattern, or rely on the hint text and accept the gap.

### 5.4 `4e23345` — site_boundary clips mask

- **What it fixed (Mapbox):** replaced white-fill of site_boundary polygon with `ctx.clip()` on the boundary.
- **Globe equivalent:** PRESENT AND CORRECT. `ctx.clip()` at useGlobeAIRender.ts:322 (inside `generateMask`) and line 1105 (inside `generateSingleZoneMask`). Confirmed by `Grep "ctx\.clip"`.
- **Severity:** none — fix is effectively already in place on globe.

---

## 6. Recommendations (prioritised)

### 6.1 Fixes that are prompt-text-only ports from Mapbox

| # | Fix | Where | Effort | Expected impact |
|---|---|---|---|---|
| R1 | Port commit 7202d32's "polygon size is authoritative" sentence into MANDATORY line | useGlobeAIRender.ts:871 | 1 line | Covers scenarios 5 AND 6; reduces "tiny building in big polygon" and "building extends past polygon to hit nominal floor count" |
| R2 | Port commit b9cea11's "polygon edges ARE building walls" clause and remove the permissive word "landscaping" from that sentence | useGlobeAIRender.ts:871 | 1 line | Prevents garden/driveway fill at large polygons; the exact user-observed bug |
| R3 | Port commit 279868f's per-zone delegation on partial occlusion | useGlobeAIRender.ts: render() at line 1380 after occlusion calc; and bump `PERZONE_THRESHOLD` conditionally down | ~20 lines | Reduces ground-zone relocation behind buildings |

### 6.2 Globe-specific new work (no Mapbox precedent to port)

| # | Fix | Where | Effort | Expected impact |
|---|---|---|---|---|
| R4 | Add a `computePolygonMeters(zone.coordinates)` helper: returns {lengthM, widthM, aspectRatio, vertexCount, areaM2}. Use `haversineDistance` already imported in useGlobeDrawing.ts:47 — copy the Mapbox `computeFootprintDims` implementation (useAIRender.ts:493) | new helper near line 676 | ~30 lines | Unblocks R5–R9 |
| R5 | Change zone line `scale` token to use polygon-computed dims when available, falling back to archetype nominal | useGlobeAIRender.ts:812-813 | 3-line change | Eliminates the 150m² vs 3200m² lie |
| R6 | Add shape adjective to zone line: `rectangular`/`elongated`/`near-square`/`L-shaped`/`irregular (N vertices)`. Classify by aspect ratio + vertex count + (area / bbox area) ratio | useGlobeAIRender.ts:801-816 | ~15 lines | First-time-ever textual representation of polygon shape |
| R7 | Branch `getMapOverlayPrompt` by camera pitch: return `renderPrompt.roofView` at nadir, `renderPrompt.mapOverlay` at oblique/street | useGlobeAIRender.ts:819 (and 1161) | ~10 lines | Aligns facade/roof emphasis with angle; fixes scenario-1-nadir |
| R8 | Drop the `polygon@(x,y)` pixel-coord token OR replace it with a polygon-shape description. Pixel coordinates without a frame-size reference are probably noise for Gemini | useGlobeAIRender.ts:845-846 | delete or rewrite | Reduces text volume; minor |
| R9 | Scale DILATION_PX by polygon size (e.g. 8px or 5% of min bbox dim, whichever is larger minimum, capped) so small polygons don't get 50% inflated masks | useGlobeAIRender.ts:334 | ~5 lines | Fixes scenario 5 mask bloat |

### 6.3 Dead-code cleanup

| # | Item | Where | Effort | Impact |
|---|---|---|---|---|
| R10 | Either lower `PERZONE_THRESHOLD` so per-zone actually runs, OR delete `buildSingleZonePromptForPerZone`/`renderPerZone`/`generateSingleZoneMask`/`compositeZoneRenderForPerZone`. The ~500 lines of per-zone code is currently unreachable for real sites. The prior audit dumped the dead path as if it were active; the real active path is `buildPrompt`. | useGlobeAIRender.ts:1070; 1152-1207; 1343-1936 | Large decision | Reduces audit/maintenance surface by ~25% |

### 6.4 Priority ordering

1. R1 (1-line port — covers size extremes)
2. R2 (1-line port — covers shape adherence)
3. R4 + R5 (compute polygon dims, use in scale token — eliminates the biggest lie)
4. R7 (nadir roof-vs-facade) — independent, high nadir-render value
5. R6 (shape adjective) — needs R4
6. R9 (dilation scaling) — independent, fixes small polygons
7. R3 (per-zone delegation on partial occlusion) — most work
8. R10 (decide what to do with dead per-zone code) — meta-cleanup
9. R8 (drop pixel-coord token) — cosmetic

---

## 7. Confirmations / refutations of prior-round findings

- **Prior C8** (`Per-zone prompt ignores camera, single-shot prompt uses it`): CONFIRMED and underweighted. Prior framing treated it as one contradiction among many; the actual situation is that the per-zone path is dead (PERZONE_THRESHOLD=99), which makes C8 moot in practice but introduces a bigger concern — the prior round's dumped globe prompt (`pass2-building-brownstone_rowhouse-globe-oblique.txt`) is from dead code. The real prompt (this round's scenario-1 dump) is ~40% longer and includes the `polygon@(x,y)` token, numerical inventory, color-temperature matching, and the occlusion section — none of which the prior dump showed. **Refutation**: the prior globe dump is not representative of what Gemini actually receives today.
- **Prior C3** (backend lies about primary image being "3D clay massing model"): CONFIRMED unchanged for globe. Still live at render.py:420.
- **Prior C4** ("ARCHETYPE REFERENCE" override): CONFIRMED unchanged. render.py:439.
- **Prior §5 "Roof-vs-facade emphasis by angle"** was flagged for both pipelines. CONFIRMED for globe specifically: `renderPrompt.roofView` exists on every archetype (brownstone:388) but globe code never calls it. Port is `getMapOverlayPrompt` → `getMapOverlayPromptByPitch`.

---

## 8. Summary of which signals "win" when polygon contradicts archetype

For each polygon characteristic, what Gemini is most likely to prioritise given current prompt weighting. This is empirical judgment, not code-derived.

| Conflict | Strongest signal | Weakest signal | Expected winner |
|---|---|---|---|
| Polygon SHAPE (L vs rect) | Mask (explicit pixels) | Text (no shape keyword) | Mask USUALLY wins — but `clipRenderToZones` cosmetic crop hides rendering failures by cutting off "wrong" architecture |
| Polygon SIZE (polygon 21× archetype) | Mask | Text (`~150m²` literal, conflicts) | Mixed — Gemini often scales one signal to fit; without "authoritative" text, outcome varies per render |
| Polygon ASPECT (10:1 vs archetype chunky) | Mask | Text (no aspect-ratio statement) | Mask wins shape; archetype wins detail — typically produces stretched-but-still-chunky-detail artifacts |
| Polygon ORIENTATION (facing) | Archetype image label `(front entrance facade)` | Polygon (no orientation info) | Archetype image wins — facade appears on whichever mask edge Gemini picks, often mis-oriented |
| Irregularity (concave, L, U) | Mask | Text (no "irregular" token) | Mask wins geometry; but architecture makes no sense inside L → visible failure |

---

## 9. File index

- Main report: this file
- Scenario dumps: `scenario-1-nominal-rectangle-oblique.txt`, `scenario-1-nominal-rectangle-nadir.txt`, `scenario-2-long-skinny-40x4.txt`, `scenario-3-near-square-15x14.txt`, `scenario-4-L-shape.txt`, `scenario-4b-L-shape-plaza-ground-zone.txt`, `scenario-5-tiny-6x4.txt`, `scenario-6-huge-80x40.txt`
- Prior round (referenced, not duplicated): `../AUDIT_REPORT.md`, `../pass2-building-brownstone_rowhouse-globe-oblique.txt`
