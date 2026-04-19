# Globe Render Pipeline Migration Plan

Port per-zone sequential rendering, sophisticated masking, and structured prompts from the Mapbox `useAIRender.ts` to the globe `useGlobeAIRender.ts`.

## Current State

- **Globe** (`useGlobeAIRender.ts`): 487 lines, single-shot render only, one color-coded mask, basic SCHEMA prompt (~350 lines of prompt logic)
- **Mapbox** (`useAIRender.ts`): 3,200+ lines, per-zone sequential, 4 mask types, 1,500+ lines of prompt logic with thinking budgets

## Architecture Decision: Expand In-Place

Expand `useGlobeAIRender.ts` rather than creating new files. The globe version already has the right projection utilities (`projectToPixels`, `WGS84_ELLIPSOID`), camera handling, and API integration. Extract helpers only when they exceed ~150 lines.

---

## Phase 1: Sophisticated Masking (Foundation)

Everything else depends on having the right masks. Port 4 mask types from Mapbox.

### 1A. Perspective Headroom Calculation

Port `calculatePerspectiveHeadroom()` (Mapbox lines 811–837) adapted for globe camera.

**Globe-specific change:** Mapbox uses `map.getPitch()` and `map.project()`. Globe must derive pitch from the Three.js camera and use `projectToPixels()` for the pixels-per-meter calculation.

```
New function: calculateGlobeHeadroom(camera, lat, lng, buildingHeightM, canvasWidth, canvasHeight)
- Derive pitch from camera.rotation or dot product of camera.forward vs surface normal
- Project two points 100m apart vertically to get pixel scale
- Apply sin(pitch) * buildingHeight * pixelsPerMeter * 2.0 safety margin
```

### 1B. Binary Mask (`generateBinaryMask`)

Port from Mapbox lines 518–601. White-on-black, all zones combined.

- Reuse existing `generateMask()` canvas setup but fill zones as WHITE instead of per-zone colors
- Add headroom expansion for building zones (from 1A)
- Add feathered top edge: `globalCompositeOperation: 'destination-out'` with gradient
- Feather height: `Math.min(20 * dpr, headroom * 0.25)`

### 1C. Single-Zone Mask (`generateSingleZoneMask`)

Port from Mapbox lines 846–933. White-on-black for ONE zone only.

- Black canvas, draw only the target zone polygon as white
- If building: add headroom rectangle above + feathered top edge
- Log white pixel coverage % for debugging

### 1D. Combined Mask (`generateCombinedMask`)

Port from Mapbox lines 940–986. White-on-black for a SET of zones.

- Black canvas, draw each specified zone polygon as white
- No headroom (used for ground-plane-only pass)
- Log white pixel coverage %

### 1E. Keep Existing Color-Coded Mask

Rename current `generateMask()` → `generateColorCodedMask()`. Still needed for single-shot renders where Gemini needs the color-to-zone legend.

**Estimated size:** ~250 new lines

---

## Phase 2: Compositing Engine

Port the layer-by-layer compositing that makes per-zone rendering work.

### 2A. `compositeZoneRender()`

Port from Mapbox lines 1404–1553. Two-step hybrid compositing:

**Step 1 — Polygon-Clipped Composite:**
- Create feathered mask from zone footprint polygon (4px blur on edges)
- For buildings: extend mask upward by headroom
- `globalCompositeOperation: 'destination-in'` to clip AI render to mask
- Draw clipped result onto cumulative base image

**Step 2 — Pixel-Diff for 3D Silhouette (buildings only):**
- Compare original screenshot vs AI render in headroom region above polygon
- `DIFF_THRESHOLD = 18` per RGB channel
- Replace pixels that differ → captures roof/spire/antenna silhouettes without horizontal bleed

**Globe-specific:** Use `projectToPixels()` to get polygon screen coordinates instead of `map.project()`.

### 2B. `stitchWithBoundaryMask()`

Port from Mapbox lines 627–804. Used for single-shot (non-per-zone) renders.

- Build white-on-black mask from site boundary polygon
- Extend upward for each building by headroom
- `destination-in` composite to clip full render
- Pixel-diff above each building for 3D extent

**Estimated size:** ~300 new lines

---

## Phase 3: Per-Zone Sequential Rendering

The main render loop. Depends on Phase 1 (masks) and Phase 2 (compositing).

### 3A. Zone Categorization

Split zones into two groups:
- **Ground zones:** `green_space`, `park`, `road`, `street`, `path`, `plaza`, `parking`, `water`, `development_area`
- **Building zones:** `building`, `residential`, `commercial`, `industrial`, `mixed_use`

Sort buildings by polygon area descending (render largest first for better compositing).

### 3B. `renderPerZone()` Function

New function alongside existing `render()`. Two-pass flow:

**Setup:**
- Capture base screenshot (Google 3D Tiles context)
- Create cumulative result canvas initialized with base screenshot
- Separate zones into ground vs building arrays
- Set thinking budget by zone count: ≥30→24576, ≥16→16384, ≥6→8192

**Pass 1 — Ground Plane (single API call):**
- Generate combined mask for all ground zones (`generateCombinedMask`)
- Capture screenshot showing colored ground zone polygons on the 3D tiles
- Build ground-plane prompt via `buildGroundPlanePrompt()`
- POST to `/api/v1/render/generate` with `thinking_budget`
- Composite each ground zone onto cumulative result via `compositeZoneRender()`

**Pass 2 — Buildings (one API call per building):**
- For each building zone (largest first):
  - Generate single-zone mask (`generateSingleZoneMask`)
  - Capture screenshot showing only this building's colored polygon on cumulative result
  - Build building prompt via `buildBuildingPrompt()`
  - Fetch archetype card image if available (single image, not 6)
  - POST to `/api/v1/render/generate`
  - Composite building onto cumulative result via `compositeZoneRender()`
  - Report progress: "Building 3/7: Glass Office Tower..."

**Globe-specific challenges:**
- Cannot show/hide individual zone polygons on the R3F canvas mid-render like Mapbox can toggle map layers
- **Solution:** Render zone polygons onto the screenshot canvas programmatically using `projectToPixels()` rather than relying on the live 3D scene. Capture base screenshot once, then paint colored polygons onto copies for each API call.

### 3C. Auto-Select Mode

- `< 10 zones` → single-shot render (existing `render()`)
- `≥ 10 zones` → per-zone sequential (`renderPerZone()`)
- User can force either mode via UI toggle

### 3D. Progress Callback

Add `onProgress` callback to `renderPerZone()`:
```typescript
onProgress?: (status: string, current: number, total: number) => void
```
GlobeAIRenderPanel.tsx wires this to a progress bar.

**Estimated size:** ~400 new lines

---

## Phase 4: Structured Prompts

Port the sophisticated prompt generation from Mapbox.

### 4A. `buildCompressedZoneLabel()`

Port from Mapbox lines 1227–1293. Compact single-line zone descriptions.

- Format: `[color] Name | scale | feature-keywords`
- Priority zone detection (arena, stadium, hotel, transit, church → 6 keywords)
- Standard zones → 3 keywords
- `condenseToKeywords()` helper to extract from materials, facade, roof, massing

### 4B. `buildSCHEMAPrompt()` with Mode Parameter

Expand current `buildPrompt()` to accept a `mode` parameter: `'full' | 'ground' | 'building'`.

**Mode-specific COMPOSITION lines:**
- `ground`: "Oblique aerial, ground-level zones only, no vertical structures"
- `building`: "Oblique aerial, single building on [color] footprint, full 3D mass extending into sky"
- `full`: Current behavior (all zones at once)

**Additional sections for per-zone mode:**
- Thinking budget hint in prompt: "Take your time analyzing the spatial layout"
- Single-zone focus: shorter, more detailed description (~500 chars per zone)

### 4C. `buildGroundPlanePrompt()` and `buildBuildingPrompt()`

Port from Mapbox lines 1076–1130. Thin wrappers that:
- Filter zones by type
- Map to `ZonePromptEntry` objects with archetype metadata
- Call `buildSCHEMAPrompt()` with appropriate mode

### 4D. Color Name Mapping

Port `colorName()` helper — maps hex colors to human-readable names for prompts:
- `#E03C31` → "red", `#4A90D9` → "blue", etc.
- Fallback: derive from HSL hue angle

**Estimated size:** ~350 new lines

---

## Phase Summary

| Phase | What | New Lines | Dependencies |
|-------|------|-----------|--------------|
| 1 | Masking (4 types + headroom) | ~250 | None |
| 2 | Compositing engine | ~300 | Phase 1 |
| 3 | Per-zone sequential render loop | ~400 | Phase 1 + 2 |
| 4 | Structured prompts | ~350 | None (parallel with 1-2) |

**Total:** ~1,300 new lines in `useGlobeAIRender.ts` (bringing it to ~1,800 lines)

**Implementation order:** Phase 1 → Phase 4 (parallel) → Phase 2 → Phase 3

Phase 4 (prompts) has no dependency on masking/compositing, so it can be built in parallel with Phase 1. Phase 3 requires everything else to be in place.

---

## Testing Strategy

- **Phase 1:** Visual inspection of mask canvases (log `canvas.toDataURL()` to console)
- **Phase 2:** Composite test with synthetic colored rectangles before live API calls
- **Phase 3:** Full end-to-end test with 10+ zone site — compare single-shot vs per-zone quality
- **Phase 4:** Log prompt strings, verify compressed labels and mode-specific composition lines

## Risk: Globe-Specific Projection

The biggest porting risk is the projection difference. Mapbox's `map.project()` returns stable 2D Mercator pixels. Globe's `projectToPixels()` uses Three.js `Vector3.project()` which depends on the 3D camera frustum. This affects:
- Headroom calculation accuracy at extreme pitch angles
- Mask polygon accuracy when zones are near screen edges (perspective distortion)
- Pixel-diff region alignment

Mitigation: Add 10% padding to all mask regions to absorb projection error.
