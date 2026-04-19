# Pass 2 Prompt Assembly Audit — SiteForge Aerial Render Pipeline

Date: 2026-04-18
Scope: Mapbox two-pass aerial pipeline (`useAIRender.ts`) and Google 3D Tiles per-zone pipeline (`useGlobeAIRender.ts`). Street view (single-pass) is out of scope.
Method: Read-only code audit + reconstructed prompt dumps.

---

## 1. Executive summary

1. **It is both — more contradictions than gaps, but the biggest single win is a gap.** The prompt concatenates several text blocks that were written for different modes and then glues them together without reconciliation. Stronger, more specific signals can mask these contradictions in easy cases, but at nadir (0°) and on ambiguous polygons they drive the inconsistency the user is seeing.
2. **Camera angle is never actually in the Pass 2 prompt text.** `buildSCHEMAPrompt` mode='building' hard-codes the line "Oblique aerial, drone 60m" (useAIRender.ts:1866). The Mapbox camera pitch/zoom/bearing are never read. Site-plan style flips the STYLE line to nadir verbiage but leaves the COMPOSITION line at 60m oblique — a direct contradiction the same prompt. This is likely the largest single cause of nadir vs. oblique inconsistency.
3. **The "Winter Pass 2" is a different thing from the "Pass 2 buildings".** Winter Pass 2 (useAIRender.ts:3054) is a second Gemini call that re-paints the unmasked satellite context with winter grading on the single-shot path. It is unrelated to the per-zone two-pass flow described in anchor 1624. The two need separate names to avoid confusion.
4. **The MANDATORY block is reused verbatim for ground and building zones.** Pass 1 (parks, roads, plazas) is told "THE POLYGON EDGES ARE THE BUILDING'S EXTERIOR WALLS" (useAIRender.ts:1900). This is the single worst contradiction in the pipeline and the first thing to fix.
5. **The backend relabels attached images in ways that lie about what they are.** Every primary screenshot is announced as "Image N (SPATIAL LAYOUT): This is a 3D clay massing model" (render.py:420) even when the caller sent a full photographic 3D Tiles capture or a 2D Mapbox satellite tile. Every side image is relabeled "ARCHETYPE REFERENCE" (render.py:439) — including the nadir top-down scene capture that the frontend intended as layout context (useAIRender.ts:3710).
6. **Material lists get run through `condenseToKeywords` and re-joined with `+`** (useAIRender.ts:1713–1724), which drops articles, truncates after ~3 tokens, and produces near-duplicate fragments like "warm brown sandstone+carved brownstone door surrounds" appearing twice in the same line.
7. **The globe per-zone Pass 2 (`buildSingleZonePromptForPerZone`, useGlobeAIRender.ts:1152) strips the camera pitch entirely** — the `_camera` and `_terrainHeight` args are unused. The legacy single-shot `buildPrompt` does inject a pitch label (line 752), so the two code paths send materially different prompts for the same scene.
8. **Single highest-impact change: centralise the "what angle is this?" fact in one place and interpolate it into the COMPOSITION line, the archetype feature list, and the MANDATORY block.** Today each of those three blocks makes independent assumptions about angle and they disagree. Fixing this one seam removes at least three of the contradictions listed below.

---

## 2. Pass 2 prompt assembly map

### 2a. Mapbox pipeline — `buildBuildingPrompt` at useAIRender.ts:1628

| # | Source | File:line | Contributes | Per-zone or global |
|---|---|---|---|---|
| 1 | Style preset `.prompt`, truncated to first sentence / 200 chars | useAIRender.ts:1848–1857 (text at 273–334) | `STYLE: …` first line | Global (per render, from `options.renderStyleId`) |
| 2 | Composition — hard-coded literal for mode='building' | useAIRender.ts:1866 | `COMPOSITION: Oblique aerial, drone 60m, single building on {color} footprint…` | Global. `{color}` is per-zone but the rest is a literal string. |
| 3 | Lighting — one of 4 literals selected by styleId | useAIRender.ts:1871–1882 | `LIGHTING: …` | Global |
| 4 | Context preservation preamble — hard-coded literal | useAIRender.ts:1885 | `CONTEXT: Preserve all unmasked satellite imagery…` | Global |
| 5 | Zone label from `buildCompressedZoneLabel` | useAIRender.ts:1750, invoked 1892 | `ZONES:\n1. [color] Title \| scale \| footprintDims \| features` | Per-zone |
| 5a | `entry.color` ← archetype shade → `colorName()` | useAIRender.ts:1630, shade map frontend/src/data/archetypeShadeMap.ts | Color token ("red", "olive", …) | Per-zone |
| 5b | `archetypeTitle` ← catalog `entry.title` | useAIRender.ts:2404 | "Brownstone Rowhouse Frontage" | Per-zone |
| 5c | `scale` ← zone props `floors`, `height_m` | useAIRender.ts:1761–1766 | "3F 12m" | Per-zone |
| 5d | `footprintDims` ← computed from polygon, two longest edges | useAIRender.ts:1608, `computeFootprintDims` | "18m×8m" | Per-zone |
| 5e | Materials — joined `styleProfile.materials`, condensed | useAIRender.ts:2392, condensed at 1787 | "warm brown sandstone+carved brownstone door surrounds" | Per-zone |
| 5f | Facade description — joined `facadeDetail.*`, condensed | useAIRender.ts:2377–2382, 1788 | "warm brown sandstone+ashlar" | Per-zone |
| 5g | Roof description — joined `roofDetail.*`, condensed | useAIRender.ts:2385–2389, 1789 | "flat+low stone parapet" | Per-zone |
| 5h | User-entered `description_text` — condensed and appended | useAIRender.ts:1810–1815 | Free-text keywords (often empty) | Per-zone |
| 5i | Image-index token "match style of Image N" — ONLY when `imageIndices` map is supplied. `buildBuildingPrompt` does NOT supply it. | useAIRender.ts:1776–1779 | "match style of Image N" | Per-zone. **Currently inactive for Pass 2** — dead code in the Pass 2 path. |
| 6 | MANDATORY block — hard-coded paragraph | useAIRender.ts:1900 | Polygon/footprint rules | Global. **Same text used for Pass 1 ground and Pass 2 buildings.** |
| 7 | PROHIBITIONS — hard-coded array + conditional style adds | useAIRender.ts:1904–1921 | Negatives inlined into the user-visible prompt | Global |
| 8 | `options.customPrompt` | useAIRender.ts:1923–1926 | `ADDITIONAL: …` | Global |
| 9 | Separate negative prompt (sent as `negative_prompt` field, appended by backend) | useAIRender.ts:2645 (builder), render.py:469–470 | Deduplicated list of negatives | Global |
| 10 | Archetype card image (Image N) | useAIRender.ts:3697 `getZoneArchetypeCard` | Attached as an image, labelled by backend | Per-zone |
| 11 | Backend label for primary screenshot | render.py:420 | Text part "Image 1 (SPATIAL LAYOUT): This is a 3D clay massing model…" | Global, injected by proxy |
| 12 | Backend label for archetype image | render.py:439 | "Image N (ARCHETYPE REFERENCE — {label}): …" + color ref | Per-zone |
| 13 | Top-down orthographic capture (site-plan styles only) | useAIRender.ts:3710 | Extra image; client label "spatial layout reference"; backend overwrites to ARCHETYPE REFERENCE | Global (but labelled per-zone by proxy) |
| 14 | Clay anchor image (globe only via `maybeCaptureClayAnchor`) | render.py:400–415 | "Image N (CLAY MASSING ANCHOR): …" | Global. Not sent for the Mapbox Pass 2 path. |
| 15 | Mask image | render.py:455–465 | "The following black-and-white mask shows the exact area to edit…" | Per-zone (each Pass 2 call sends a single-zone mask) |

Sources that the user's checklist asked about but that are **NOT** currently concatenated into Pass 2 prompt text:

- Parcel/zone lat/lng coordinates — not in text prompt (globe legacy single-shot adds `polygon@(px,py)…` at useGlobeAIRender.ts:846; per-zone globe does not).
- Pixel coordinates — same as above (globe legacy only).
- Adjacent-parcel anchor chain — no "north of X, east of Y" text anywhere.
- Sun position / time of day — implicit in the LIGHTING line ("warm southwest sun") but not parameterised per scene.
- Camera altitude or zoom — hard-coded "60m" for oblique and "100m" in the site-plan STYLE literal.
- Explicit camera pitch number — never sent in the Mapbox pipeline. Globe legacy single-shot injects "~N°" (useGlobeAIRender.ts:757).
- Pass 1 output content — not described in the Pass 2 text prompt. The Pass 1 render is shown to the model visually via the cumulative screenshot, but no sentence like "ground plane already rendered, do not touch" exists.
- Scale-reference entourage (trees, vehicles, people) — not mentioned; `people` appears only in PROHIBITIONS.

### 2b. Globe pipeline — `buildSingleZonePromptForPerZone` at useGlobeAIRender.ts:1152

Shorter: this builder is deliberately minimal. It assembles six lines in order: STYLE, TASK, BUILDING, DETAILS (optional), CONTEXT, MANDATORY, ADDITIONAL (optional). Camera pitch args are accepted but **marked unused** (`_camera`, `_terrainHeight`). See `pass2-building-brownstone_rowhouse-globe-oblique.txt` for the reconstructed prompt.

---

## 3. Dumped prompts

Four reconstructed prompts live in this directory. Captured logs were not found in `artifacts/` — only the master-plan-smoke and ui-concepts folders exist there, none of which contain Gemini prompt text. All four reconstructions are built directly from the builder code paths and a representative `brownstone_rowhouse_frontage` archetype.

| File | Description |
|---|---|
| `pass2-building-brownstone_rowhouse-mapbox-oblique.txt` | Pass 2 building prompt at oblique aerial, photorealistic style, Mapbox pipeline |
| `pass2-building-brownstone_rowhouse-siteplan-nadir.txt` | Same zone at site-plan-photo style — shows the STYLE/COMPOSITION contradiction at nadir |
| `pass1-ground-mapbox.txt` | Pass 1 ground-plane prompt on same site, showing the MANDATORY block mismatch |
| `pass2-building-brownstone_rowhouse-globe-oblique.txt` | Globe per-zone Pass 2 for the same archetype, different builder |

---

## 4. Contradictions table

Quoted text is copy-pasted verbatim from the referenced lines so paraphrasing cannot hide the mismatch.

| # | Seam | Severity | Statement A | Statement B | Recommended single source of truth |
|---|---|---|---|---|---|
| C1 | STYLE ↔ COMPOSITION at nadir | **Hard contradiction** | `STYLE: Professional near-top-down drone photomontage at 100m altitude, 15-20 degrees from nadir.` (useAIRender.ts:297, selected 1838–1857) | `COMPOSITION: Oblique aerial, drone 60m, single building on {color} footprint, full 3D mass extending into sky` (useAIRender.ts:1866) | Drop the literal camera description from COMPOSITION. Compute pitch/altitude from map state once and interpolate one camera descriptor into both STYLE and COMPOSITION. |
| C2 | MANDATORY block reused for ground zones | **Hard contradiction** | Pass 1 ground plane prompt contains: `THE POLYGON EDGES ARE THE BUILDING'S EXTERIOR WALLS. The building MUST FILL the entire polygon area…` (useAIRender.ts:1900, reached for mode='ground') | Pass 1 COMPOSITION reads: `COMPOSITION: Oblique aerial, drone 60m altitude, ground-level zones only, no vertical structures` (useAIRender.ts:1863) | Branch the MANDATORY string by `mode`. Buildings get the footprint-equals-polygon block. Ground gets a surface-material block. |
| C3 | Primary screenshot label lies about content | **Hard contradiction** | Backend always labels the primary image: `Image {N} (SPATIAL LAYOUT): This is a 3D clay massing model showing the exact spatial arrangement…` (render.py:420) | For the Mapbox Pass 2 path, the attached image is a Mapbox satellite capture with colored zone polygons drawn over it — not a clay massing model. For the globe path it is a photographic 3D Tiles capture with painted labels. Neither is "a 3D clay massing model". | The only real clay anchor is `req.clay_anchor_base64` (render.py:400). The primary-screenshot label should say "map composite with colored zone footprint polygons" for Mapbox and "photographic 3D city model capture with painted zone labels" for globe. Pass the provenance from the client. |
| C4 | "ARCHETYPE REFERENCE" used for nadir scene capture | **Soft tension** | Backend labels every extra image: `Image {N} (ARCHETYPE REFERENCE — {label}): Apply the exact architectural style, materials, and textures from this reference image…` (render.py:439) | Client attaches a top-down nadir screenshot with label `Top-down orthographic view — use as spatial layout reference. Maintain exact zone positions and proportions.` (useAIRender.ts:3710). The backend label overrides "spatial layout reference" and tells the model to apply the *style* of the nadir capture. | Add a `role` field (`archetype_reference` \| `scene_reference` \| `ground_render`) to the `ArchetypeImage` Pydantic model and branch the prefix accordingly. |
| C5 | Materials appear twice in every zone line | Redundancy risk | `if (entry.materials) parts.push(condenseToKeywords(entry.materials, priority ? 3 : 2));` (useAIRender.ts:1787) | `if (entry.facadeDescription) parts.push(condenseToKeywords(entry.facadeDescription, priority ? 3 : 2));` (useAIRender.ts:1788) — and `facadeDescription` is built from `facadeDetail` which starts with `fd.primaryMaterial` (line 2378), the same material string that feeds `sp.materials`. | Make `facadeDescription` deliberately exclude the primary material so the two fields are complementary, or drop the materials token when facadeDescription is present. |
| C6 | Negatives stated in both prompt text and negative_prompt field | Soft tension | Prompt text ends with: `PROHIBITIONS: buildings extending beyond polygon boundaries, colored polygon fills visible on rooftops or facades, boundary lines or outlines visible in final image, people or pedestrians…` (useAIRender.ts:1904–1921) | Backend appends to the same prompt: `Do NOT include: … buildings extending beyond polygon boundaries, architecture outside polygon, walls outside boundary…` (render.py:470; frontend builds at useAIRender.ts:2645–2699). The two overlap by ~60% of tokens. | Pick one channel. Gemini 3 obeys the `negative_prompt` field reliably enough that the inline PROHIBITIONS line can go — or keep PROHIBITIONS and drop the generic half of `buildNegativePrompt`. |
| C7 | Style name vs. scene modality | Soft tension | `STYLE: Hyper-realistic exterior architectural rendering with cinematic lighting.` (first sentence of useAIRender.ts:277) | `MANDATORY: … render ONLY within its colored polygon boundary. Realistic rooftop materials …` (useAIRender.ts:1900). The word "exterior" in STYLE collides with "rooftop" emphasis in MANDATORY at nadir. | At 0° nadir there is no "exterior" to emphasise. Rewrite STYLE to omit viewpoint-specific adjectives; keep viewpoint info in a single CAMERA line. |
| C8 | Per-zone prompt ignores camera, single-shot prompt uses it | Soft tension | Globe per-zone: `function buildSingleZonePromptForPerZone(zone, style, _camera, _terrainHeight, customPrompt)` — both camera args underscored as unused (useGlobeAIRender.ts:1152–1157) | Globe single-shot: `pitchDesc = \`oblique aerial (~${pitchDeg}°)\`; …` injected into COMPOSITION (useGlobeAIRender.ts:756–763) | Extract `pitchDesc` into a helper and call it from both builders. |
| C9 | Hardcoded "drone 60m" vs. actual map state | Redundancy risk escalating to contradiction at high zoom | COMPOSITION: `drone 60m` (useAIRender.ts:1863, 1866, 1868) | Mapbox zoom can set the ground-sample distance anywhere from 2m/pixel to 30m/pixel; 60m drone altitude is only approximately right for zoom ~17. At zoom 19 a building polygon occupies 4–6× the frame it would at 60m. | Compute altitude from map zoom + DPR or drop the number and say "aerial"/"low-oblique" by pitch bucket. |
| C10 | Archetype card ↔ polygon footprint | Soft tension | Archetype card image shows a real photograph of a rowhouse terrace at oblique ground level | MANDATORY: `Archetype metadata (floor count, height, nominal dimensions) describes STYLE, MATERIALS, and CHARACTER only — adjust facade rhythm… to suit the polygon's actual footprint, but the footprint itself MUST equal the polygon.` (useAIRender.ts:1900) | This one reads as deliberate — the user documented the fix in project_reference_image_quality.md. Keep but ensure the archetype card LABEL says "style only" (it does not today; it says "Apply the exact architectural style, materials, and textures" at render.py:439). |
| C11 | Ground zones use ground fill on prompt screenshot; Pass 2 buildings don't | Soft tension | `annotateScreenshotForPrompt` fills ground polygons with alien hot-pink/cyan/neon-green at 75% alpha so Gemini sees them (useAIRender.ts:575–586) | Pass 2 per-zone never re-runs annotation — the Pass 2 screenshot is re-captured fresh with the building polygon painted in its archetype shade (useAIRender.ts:3630, `getZoneRenderColor`). The neon-border convention does not apply. | Document this asymmetry in `buildSCHEMAPrompt` or unify the annotation helper. |
| C12 | Duplicate footprint size statement | Redundancy risk | Zone line carries `… \| 18m×8m \| …` (useAIRender.ts:1771–1772, 1824) | MANDATORY paragraph repeats in prose: `… the footprint itself MUST equal the polygon.` | Fine in itself, but the polygon image + the footprint-dims text + the MANDATORY prose are three overlapping signals. If the render misunderstands size (documented as a recurring issue in git log b9cea11, 7202d32), the three signals are racing. |

---

## 5. Missing angle / viewpoint information table

| Item | Currently in prompt? | Where | Most-affected angle | Suggested insertion point |
|---|---|---|---|---|
| Explicit camera pitch (degrees) | No, for Mapbox. Yes, for globe single-shot only. | useGlobeAIRender.ts:752–757 (globe single-shot only) | Nadir (where oblique text actively misleads) and ground-level | Add a `CAMERA:` line to `buildSCHEMAPrompt` that interpolates from map.getPitch(). Use it in both builders. |
| Explicit camera altitude (meters above terrain) | No — hardcoded "60m" or "100m" in style literals | useAIRender.ts:277, 297, 1863, 1866, 1868 | Oblique (wrong at high-zoom close-ups) | Same CAMERA line as above; compute from map zoom or camera.position.length() for globe. |
| Ground footprint of the frame (GSD or frame width in meters) | No | — | All, especially nadir where scale is hard to read from context | Add to CAMERA line: `frame covers ~{N}m × {M}m at ground`. Easy to compute from bounds. |
| Sun position / azimuth / elevation | Partially — "warm southwest sun" is a literal in LIGHTING | useAIRender.ts:1881 | Oblique (shadow direction is the main height cue); degraded at nadir too | Lock to a site-plus-season triple, or read from Mapbox `map.light`. The per-zone Pass 2 and Pass 1 need IDENTICAL sun text; today they do (both use the same LIGHTING line), which is good — don't break this. |
| Time of day | Implicit in "golden hour" literal | useAIRender.ts:1881 | All | Same. |
| Roof-vs-facade emphasis by angle | No | — | **Nadir — highest-impact gap.** At 0° the whole facade description is invisible pixels. | Branch zone-line features by pitch: if pitch < 20°, promote roofDescription + aerialAppearance, demote facadeDescription. `roofDetail.aerialAppearance` already exists in archetypes (line 404, "dark flat surface with occasional brick chimneys…") and is currently dropped except for "priority" zones (useAIRender.ts:1790). |
| Height / massing cues | Partially — "3F 12m" scale token | useAIRender.ts:1761–1766 | Nadir (height is invisible without shadow reasoning) | Add a shadow-direction + shadow-length cue at nadir. E.g. "12m tall, cast shadow should be {N}m to the north-east". The user's memory `project_z_axis_nadir_refs.md` already flags this. |
| Foreshortening / perspective cues | No | — | Oblique and ground | In the CAMERA line: "near field at bottom, far field at top; apply atmospheric perspective". Only applies at pitch > ~30°. |
| Occlusion handling | Yes for Mapbox MANDATORY ("If a zone is partially occluded by a foreground building, render only the visible portion"). Yes for globe legacy (`OCCLUSION` section, useGlobeAIRender.ts:874). **No** for globe per-zone Pass 2 (shorter prompt omits it). | useAIRender.ts:1900 and useGlobeAIRender.ts:874 | Oblique and ground | Add an OCCLUSION line to `buildSingleZonePromptForPerZone`. |
| Scale-reference entourage (known-height elements) | No. `people` only appears in PROHIBITIONS. | useAIRender.ts:1908, 2656 | Ground-level and 30° oblique (where relative scale is critical) | Opt-in trees/cars as scale cues. Today they're banned by "people, pedestrians" and may be over-negated since trees often come along. Check `buildNegativePrompt` output for this archetype. |
| Pass 1 carryover ("ground plane already rendered") | No. The Pass 1 render is only VISUAL, never textual. | — | Oblique and ground, especially when Pass 2 accidentally repaints a road that Pass 1 already handled | Add one sentence in Pass 2 MANDATORY: "The ground plane in the image is already finished; do not re-render roads, grass, or pavement — only the building within the white mask." |

---

## 6. Recommended single-source-of-truth mapping

| Fact | Currently stated in | Keep in | Remove from |
|---|---|---|---|
| Camera pitch | None (globe single-shot derives; Mapbox hardcodes "oblique") | New `computeCameraDescriptor(map)` helper, injected as CAMERA line in `buildSCHEMAPrompt` | COMPOSITION literals at useAIRender.ts:1861, 1863, 1866, 1868 |
| Camera altitude | Style literals at useAIRender.ts:282, 297; COMPOSITION line 1863, 1866, 1868 | Same CAMERA helper | All style literals (styles should describe RENDERING CHARACTER, not camera position) |
| Sun / golden hour | LIGHTING line (useAIRender.ts:1881) AND style modifier at 277 ("Golden hour sunlight") | LIGHTING line only | Strip from style modifiers |
| Primary material | `styleProfile.materials` (catalog 2392) → `entry.materials`; and `facadeDetail.primaryMaterial` (catalog 2378) → `entry.facadeDescription` | `facadeDetail.primaryMaterial` only (richer context) | Drop from `styleProfile.materials` in the zone-line builder, or stop concatenating both at useAIRender.ts:1787–1788 |
| Polygon shape / size | Colored polygon in screenshot, footprintDims in zone line, MANDATORY prose | Screenshot + zone-line dims | Trim MANDATORY prose to a single sentence — the repetition is adversarial when the three disagree |
| Archetype style | Archetype card image + zone-line features + backend "Apply the exact architectural style" label | Image + zone-line name | Drop or weaken the backend "Apply the EXACT style" wording (render.py:439) — it overrides footprint constraints in practice |
| Building-footprint-must-equal-polygon | MANDATORY prose + PROHIBITIONS + negative_prompt | MANDATORY only | Remove from PROHIBITIONS and from buildNegativePrompt's hard-coded list (useAIRender.ts:2656) |
| Image labels / provenance | Backend hard-codes all labels (render.py:420, 439, 457) | Client passes `role` on `ArchetypeImage`, backend uses it | Hardcoded strings in render.py |

---

## 7. Prioritised gap-fill list

Each item is scored by expected impact on render-to-render consistency. A quick rationale follows.

1. **Differentiate MANDATORY by pass (building vs. ground).** Pass 1 is being told the polygon edges are building walls. This is a semantic lie on every park/road prompt and is the single most direct contradiction. Cost: one if-branch. (Contradiction C2.)
2. **Remove the STYLE ↔ COMPOSITION camera mismatch.** Either interpolate one camera descriptor from map state, or strip camera facts out of the style modifier. Nadir renders get a confused model today. (C1, C9, plus the entire §5 camera block.)
3. **Add a CAMERA line to `buildSCHEMAPrompt`** with pitch, altitude (or "aerial/oblique/street-level" label), and frame ground-footprint. Sole source of truth for angle. Makes items 1, 2 and most of §5 fall out.
4. **Branch zone-line features by pitch.** At pitch < 20° promote `aerialAppearance` and `roofDescription`, demote `facadeDescription`. At pitch > 60° invert. Today everything is tuned for oblique. (§5 "Roof-vs-facade emphasis" — high-impact nadir gap.)
5. **Fix backend image labels.** `render.py` should relabel by role, not by slot. Today the nadir scene capture is announced as an ARCHETYPE REFERENCE, and every primary screenshot is announced as "a 3D clay massing model". (C3, C4.)
6. **Add an explicit shadow-length-and-direction cue for nadir renders** derived from sun position + building height. Height is currently textually stated ("12m tall") but with no way for the model to infer shadow length at 0° view. (Memory `project_z_axis_nadir_refs.md` pre-existing.)
7. **De-duplicate negatives.** Collapse PROHIBITIONS line + `buildNegativePrompt` output + per-archetype `renderPrompt.negative`. Keep one channel — `negative_prompt` is preferred by Gemini 3. (C6.)
8. **Add the Pass 2 "ground already rendered" carryover sentence.** One-line addition in MANDATORY when mode='building' and per-zone Pass 1 has run, preventing the model from repainting a road. (§5 "Pass 1 carryover".)
9. **Port pitch injection into globe per-zone builder.** `buildSingleZonePromptForPerZone` already accepts `_camera, _terrainHeight` — wire them up using the same helper added in item 3. (C8.)
10. **Collapse materials/facade redundancy in zone line.** Either make `facadeDescription` skip primary material (upstream in `getZoneArchetypeInfo` line 2378) or drop one of the two `condenseToKeywords` calls. (C5, C12.)
11. **Clearly rename "Winter Pass 2".** It is not Pass 2 of the two-pass pipeline. Call it `enhanceContext` or similar in code comments and status messages to prevent confusing overlap with the per-zone Pass 2 loop. (Executive summary item 3.)

---

## Appendix — "Winter Pass 2" vs. "Per-zone Pass 2"

These are entirely separate features:

- **Per-zone Pass 2** (useAIRender.ts:3608, useGlobeAIRender.ts:1716). The thing this audit is about. Renders each building on top of the Pass 1 ground plane, one Gemini call per building.
- **Winter Pass 2** (useAIRender.ts:3054). A follow-up Gemini call on the single-shot render path that re-paints the unmasked satellite context with winter grading (snow on existing rooftops, bare trees, etc.). It runs only when `styleId === 'winter'` AND per-zone pass is not active. It uses an *inverted* mask — the opposite of every other pass. Its prompt is a short inline literal at useAIRender.ts:3070–3076; no archetype information is attached.

The user's debugging attention should be focused on the per-zone Pass 2. Winter Pass 2 only matters if a winter render is showing a separate class of bug (grey blocky existing buildings).
