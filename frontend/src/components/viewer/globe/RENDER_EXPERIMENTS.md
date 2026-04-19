# Globe AI Render — Experiment Log (April 12, 2026)

## Branch: `feature/google-3d-globe-stable`

This documents all render pipeline experiments attempted on the globe version, what worked, what didn't, and why. Use this to avoid re-trying failed approaches.

---

## Starting Point: v1.9-globe (commit `52380dc`)

Single-shot render with colored mask, SCHEMA prompt, archetype images disabled (502 payload errors).

**Result:** Renders worked for 1-2 zones but builds rendered generically — no archetype differentiation. Color temperature mismatch (cool buildings in golden-hour scenes).

---

## Experiment 1: Color Temperature Matching (commit `3a5a047`) ✅ KEPT

**What:** Added `COLOR TEMPERATURE MATCHING` and `ATMOSPHERIC PERSPECTIVE` prompt sections telling Gemini to match the existing scene's warmth/haze.

**Result:** Dramatic improvement — the High-Tech Structural Arena render blended naturally with warm golden-hour Google 3D Tiles context. Previously rendered buildings had cool grey tones that looked "pasted on."

**Status:** KEPT in current build.

---

## Experiment 2: Per-Zone Sequential Rendering (commit `b9584c7`) ❌ REVERTED

**What:** Ported the full Mapbox 2-pass system:
- Phase 1: Masking (4 types: color-coded, binary, single-zone, combined + perspective headroom)
- Phase 2: Compositing engine (polygon-clip + 4px feather + pixel-diff for 3D silhouettes)
- Phase 3: renderPerZone (ground pass → individual building passes)
- Phase 4: Structured prompts (mode parameter, compressed labels, priority zones)

**Result:** Each API call took **~50 seconds** on globe vs ~5s on Mapbox. 29 zones = 21 calls = ~17 minutes. The Mapbox version was fast because satellite screenshots are simpler than 3D tile captures.

**Why reverted:** Impractically slow. The per-building approach is the right architecture but needs faster API calls.

---

## Experiment 3: 3-Pass Category Rendering (commit `32299e0`) ❌ REVERTED

**What:** Instead of 21 individual calls, grouped into 3 passes:
1. Parks & Plazas (all green zones)
2. Streets & Roads (all road zones)
3. Buildings (all building zones)

Each pass got a category-specific prompt and combined mask.

**Result:** Fast (3 calls × 50s = 2.5 min) but inaccurate — buildings rendered generically because the prompt only described that category's zones. Gemini didn't know what the adjacent streets/parks were.

---

## Experiment 4: Full Zone Legend + Category Masks (commit `dd747a3`) ❌ REVERTED

**What:** Same 3-pass approach but every pass gets the FULL prompt with all 29 zones listed. MASK SCOPE instruction tells Gemini to only edit masked zones. All zone polygons painted on every screenshot.

**Research backing:** NeurIPS 2024 hierarchical inpainting paper, Google prompting guide — models need surrounding context.

**Result:** Better coherence but still generic buildings. With 29 zones in a single prompt (5700+ chars), Gemini can't reliably match each colored polygon to its specific archetype.

---

## Experiment 5: Numbered Zone Labels (commit `72f7724`) ❌ REVERTED

**What:** Drew bold numbered circles (1-29) at each zone centroid on the screenshot. Prompt referenced zones by both number and color.

**Result:** WORSE — Gemini rendered the number circles INTO the final image as architectural features. Numbers appeared as white discs on rooftops and facades.

**Lesson:** Visual noise on screenshots gets rendered into the scene. Don't add overlays that Gemini can't distinguish from content.

---

## Experiment 6: Distinct Color Vocabulary (commit `e97510e`) ✅ KEPT

**What:** `colorName()` generates descriptive names: "bright vermillion #E03C31", "deep maroon #C62828", "burnt sienna #D84315" instead of generic "red", "dark red".

**Result:** Prompt-only change. Hard to isolate the effect but makes the zone legend more readable. No downside.

**Status:** KEPT in current build.

---

## Experiment 7: Rainbow Color Palette (commit `fa8483a`) ❌ REVERTED

**What:** 30 maximally distinct colors assigned at render time. Each zone gets a visually unique color (pure red, blue, green, magenta, yellow, cyan, etc.) instead of zone-type-based colors.

**Result:** WORSE — the distinct colors bled through into rendered surfaces. Magenta walls, blue roofs, red roads. Gemini was supposed to replace the colors with materials but failed.

**Lesson:** The mask tells Gemini WHERE to edit but colored fills in the screenshot influence WHAT it renders. Distinct colors work against you when they leak through.

---

## Experiment 8: Compressed Archetype Reference Images (commit `761faec`) ✅ KEPT

**What:** `compressImage()` resizes archetype card thumbnails to 512px wide JPEG at 70% quality (~30-50KB each vs ~500KB PNG). Re-enabled `collectArchetypeImages()`.

**Result:** 502 payload errors eliminated. Gemini now SEES what each archetype looks like. Renders show more architectural variety — Parametric Hub has honeycomb mesh, Civic Classical has columned facade, Warehouse Lofts have industrial brick.

**Status:** KEPT in current build. Currently only 3 of 6 zones get images (debug logging added).

---

## Experiment 9: Site Boundary Mask Clipping ✅ KEPT (after 2 failed attempts)

**Attempt 1: `destination-in` compositing (commit `85eb191`)** ❌
- Clipped mask to boundary using `ctx.globalCompositeOperation = 'destination-in'`
- Result: Entire mask turned black. Zone polygons were colored (not white), so destination-in erased them.

**Attempt 2: White boundary outline (commit `3c45396`)** ❌
- Drew thin white outline of boundary on mask + prompt instruction
- Result: Gemini ignored the outline. Builds still rendered outside boundary.

**Attempt 3: `ctx.clip()` (commit `3ad5ca3`)** ✅
- Uses `ctx.save()` → `ctx.clip(boundaryPath)` → draw zones → `ctx.restore()`
- Result: Works correctly even when boundary extends off-screen. Zones outside boundary are silently clipped.

---

## Experiment 10: DRACOLoader Fix (commit `c1a3300`) ✅ REQUIRED FIX

**What:** Google started serving Draco-compressed GLB tiles. Added `GLTFExtensionsPlugin` with `DRACOLoader` pointing to Google's hosted Draco decoders at `https://www.gstatic.com/draco/versioned/decoders/1.5.7/`.

**Status:** Required — 3D tiles won't load without it.

---

## Experiment 11: Extended Street Descriptions (commit `d4b7c3d`) ❌ REVERTED

**What:** Increased feature description limit from 200 to 500 chars for ground zones. Added `corridorDescription` (corridorCharacter, surfaceType, plantingCharacter, edgeConditions) to `getZoneArchetypeInfo`.

**Result:** Made renders WORSE — skate park became oversized, zones rendered in wrong positions. The longer prompt confused Gemini.

**Lesson:** More detail ≠ better renders. Keep per-zone descriptions concise (~200 chars). The mapOverlay prompt (already ~400 chars) was being truncated, but feeding the full version made things worse.

---

## Current Architecture (after all experiments)

```
useGlobeAIRender.ts (~750 lines)
├── captureCanvasBase64() — PNG from R3F canvas
├── findOccludedZones() — screen-space occlusion culling (>60% = cull)
├── generateMask() — BINARY white-on-black mask with ctx.clip() boundary + 2m dilation
├── compressImage() — JPEG 512px at 70% quality
├── collectArchetypeImages() — up to 6 compressed card images
├── colorName() — descriptive hex names (vermillion, maroon, etc.)
├── getMapOverlayPrompt() — archetype-specific render instruction
├── getZoneArchetypeInfo() — facade, roof, materials, public realm
├── buildPrompt() — SCHEMA format with camera pitch, 13 sections
├── clipRenderToZones() — POST-PROCESSING polygon clip with 6px feathered edges
└── render() — single-shot API call to Gemini 3.1 Flash + post-process clip
```

---

## Experiments 12-16 (continued, April 12)

### Experiment 12: Post-Processing Polygon Clip (commit `dad57db`) ✅ KEPT

**What:** After Gemini returns, `clipRenderToZones()` clips the result to zone polygons:
- Original screenshot = base layer
- AI render masked through feathered polygon mask (6px blur)
- Only AI content within zone boundaries shows through
- Buildings get upward mask extension for 3D height

**Result:** Zones no longer bleed into each other. The "fail-safe" works.

### Experiment 13: Mask Dilation ~2m (commit `28615a5`) ✅ KEPT

**What:** Draw zone polygons with 8px thick stroke in the mask, giving Gemini "peripheral vision" to see curbs, sidewalks, neighboring facades. Post-processing clip uses original tight polygons.

**Result:** Better edge integration — buildings look seated in context rather than "stickers."

### Experiment 14: Camera Pitch in Prompt (commit `538461b`) ✅ KEPT

**What:** Compute camera pitch from Three.js quaternion, include in COMPOSITION: "oblique aerial (~52°) view..."

**Result:** Helps Gemini render correct 3D perspective for the viewing angle.

### Experiment 15: Screen-Space Occlusion Culling (commit `69cb983`) ✅ KEPT

**What:** `findOccludedZones()` checks which zones are >60% covered by taller buildings in screen space. Culled zones removed from mask AND prompt.

**Result:** Partially effective — works when buildings truly overlap, but doesn't prevent Gemini from distorting scale on visible zones.

### Experiment 16: Binary Mask (commit `6ae1953`) ✅ KEPT

**What:** Switched from color-coded mask to white-on-black binary mask. Zone colors only appear in the screenshot (baked in by R3F canvas capture). Prompt tells Gemini to "replace the colored polygon overlays visible in the screenshot."

**Result:** Eliminates colored polygon fill bleeding onto rendered surfaces (no more red patches on facades).

---

## Current VFX Pipeline (after all experiments)

1. **Capture** — R3F canvas with colored zone polygons visible on 3D tiles
2. **Occlusion cull** — remove zones >60% hidden by taller buildings
3. **Mask** — binary white-on-black with 2m dilation + site boundary clip
4. **Prompt** — SCHEMA format with camera pitch, archetype descriptions, color legend
5. **Archetype images** — compressed JPEG card thumbnails (up to 6)
6. **API call** — Gemini 3.1 Flash, temperature 0.0
7. **Post-process clip** — polygon-clip with 6px feathered edges back to original boundaries

---

## Experiment 12: Multi-Angle Aerial Reference Images (April 15, 2026) ⚠️ PARTIAL SUCCESS

**What:** Based on Gemini's own guidance, added multiple aerial reference images per archetype (90°, 60°, 45°, 30° drone views) alongside the existing street-level image. Goal: give Gemini complete 3D understanding of each building/space.

**Setup:**
- Generated aerial images using `gemini-3.1-flash-image-preview` with existing street-level variant as style anchor
- `MULTI_VIEW_IMAGES` map in `useGlobeAIRender.ts` keyed by variant ID
- `collectArchetypeImages()` loads all angle views for matched variants
- Image cap raised from 6 to 48 (backend + frontend)

**Results — What worked:**
- **Civic Monumental Institution (Neoclassical)** — dramatic improvement. Copper dome, white marble, Corinthian columns all rendered accurately from multiple angles. Previously rendered as generic modern office.
- **Gothic Revival variant** — also rendered correctly with spires, rose window, brick facade (even without multi-view aerials, just street-level reference)
- Variant selection fix (`development_selected_variant_id` etc.) correctly resolves user's chosen variant

**Results — What failed:**
- **AI-generated aerial references hallucinate.** Tennis court "Urban Athletic" 90° image contained a skatepark underneath. Beach volleyball images had oversized multi-story structures. These hallucinated elements were faithfully reproduced in renders.
- **Too many reference images → spatial confusion.** With 4 zones × 4 images each = 16 images, Gemini placed content in wrong zones. Elements rendered outside their polygons, zones got mixed up.
- **Street-level "rear/side" views are useless.** Model already has that perspective from the existing variant image. Only TRUE aerial views (drone/satellite) add new information.

**Key findings:**
1. Multi-angle aerials dramatically improve building accuracy — but ONLY if the reference images themselves are accurate
2. AI-generated reference images must be grounded in real architecture research — vague descriptions → hallucinated elements
3. Fewer accurate images >>> many inaccurate images
4. 1 good street-level image per zone + 3 verified aerials for key buildings = optimal
5. Image cap of 6 was too low (Gemini accepts 3,600/20MB). Raised to 48.
6. Compositing must use clean screenshot (`rawBase64`) not annotated version (`imageBase64`) as background — otherwise borders bleed through
7. Variant lookup must read `development_selected_variant_id` / `road_selected_variant_id` / `green_space_selected_variant_id` / `plaza_selected_variant_id` — NOT `selected_variant`

**Current state:** Multi-view aerials enabled ONLY for `civic_monumental_neoclassical` (verified accurate). All others disabled pending research-grounded image generation.

**Render quality observations (multiple angles, 3 zones):**

At 45° oblique:
- Gothic church: correct variant identity, spires + rose window + brick, good zone fill
- Beach volleyball: tensile canopy + sand visible, correct variant
- Promenade: tree-lined corridor with herringbone paving visible

At 59° oblique:
- Gothic church: correct identity but doesn't fill polygon width, slight floating at base
- Beach volleyball Indoor-Outdoor: tensile canopy correct but small within zone, has unexpected solid wall
- Promenade Miami Ocean Drive: trees visible but missing cafe terraces, mosaic paving, tropical character
- General: zone fill sparse — elements smaller than polygon zones

At 68° steep oblique:
- Gothic church: excellent — green copper roof visible from above, rose window, fills zone well
- Beach volleyball: sand courts visible with nets/bleachers BUT tensile canopy MISSING at steep angles — variant identity lost
- Promenade: herringbone paving visible BUT rendered on WRONG SIDE of building — spatial mapping error for thin linear zones
- Context blending excellent — Calgary skyline in background, nothing looks pasted

**Recurring issues across angles:**
- Open space/street archetypes lose variant identity at steep aerial angles (canopy, kiosks, terraces disappear)
- Thin linear zones (promenades) get spatially confused — content placed in gaps between zones instead of actual zone location
- Zone fill inconsistent — sometimes sparse, sometimes good depending on angle
- No border bleed-through after `rawBase64` fix ✓

**Status:** KEPT (variant fix, image cap, clean compositing, civic aerials). Tennis/volleyball/promenade aerials DISABLED.

**Next steps:**
- Use research agents to study real-world examples before generating aerial refs
- Generate research-grounded aerial images with explicit negative constraints
- Roll out to more archetypes only after verifying image accuracy

---

## Open Questions

1. **How to get faster API calls?** Image compression/resizing before sending? Different model?
2. **Is per-building rendering viable if we reduce image size?** Mapbox sends simpler images.
3. **Port watercolor/charcoal/clay styles from Mapbox?** User wants them.
4. **200 char limit on features** — too short for streets but longer breaks things. Is there a sweet spot?
5. **Archetype images** — some zones still missing thumbnailUrl. Debug logging shows which ones.
6. **Research-grounded aerial refs** — need agent pipeline to research real buildings before generating images
7. **Zone fill sparsity** — rendered elements don't fill their full polygon area. Prompt or massing issue?
