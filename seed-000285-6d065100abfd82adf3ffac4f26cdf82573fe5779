# Assessment of Gemini's Code Review Claims

**Date:** 2026-04-17
**Method:** 3 parallel research agents, evidence-based verification against actual codebase + user memory
**Bottom line:** 2 actionable wins, 1 already handled, 4 should be ignored/contradict proven findings

---

## ACT ON — real bugs with clear fixes

### 1. Stencil volume has no altitude cap ★
**Claim validated.** `GlobeZoneLayer.tsx:415` calls `createStencilVolume(pts, Math.max(extrudeHeight * 2, 200))`:
- Floor: 200m (10m building → 200m volume)
- Tall buildings: 600m+ (300m building → 600m volume)
- `StencilMaskPlugin.ts:44–47` has no check against camera altitude

At top-down views, camera enters the volume → stencil test fails, faces clip.

**Proposed fix:** Cap height to `cameraAltitude - 10m` before creating the volume. Small, surgical change.

### 2. Hardcoded geoid offsets → buildings float
**Claim validated.** `backend/app/api/v1/elevation.py:23-37`:
```python
GEOID_UNDULATIONS = {
    (25, 55, -130, -60): -25,   # ← Calgary lives in this coarse region
    (35, 70, -15, 45): 40,
    ...
}
```
6 coarse regional bins, ±40m delta at region edges. Google Elevation returns MSL; tiles use WGS84 ellipsoid; this lookup does MSL→ellipsoidal conversion.

**Agent caveat:** EGM96 would improve precision, BUT the real root of floating is the raycast-drape fallback chain in `GlobeZoneLayer.tsx:251` — if raycast fails (tiles not loaded), zone falls back to the hardcoded-offset backend value. Fix = EGM96 + tighter drape retry logic.

**Priority:** medium. The raycast drape is usually succeeding (that's why your current renders look OK); this is the failure mode.

---

## ALREADY HANDLED — no action needed

### 3. Bearing null at 0° pitch
**Bug is real** at `GlobeSitePlannerMap.tsx:198–200`: `computeBearingFromCamera()` returns `null` when `Math.hypot(eastComponent, northComponent) < 1e-3`.

But line 1228 already has defensive fallback:
```ts
return bearing ?? preferredView?.cameraPosition?.bearing ?? 0;
```

The prompt never sees null. Closed.

---

## IGNORE — contradicts existing evidence

### 4. COMMAND: VALUE pseudo-code reformat
**NEUTRAL.** Your SCHEMA prompt (`useAIRender.ts:1299–1397`) is already structured with STYLE/COMPOSITION/LIGHTING/CONTEXT/ZONES/MANDATORY/PROHIBITIONS headers. Marginal gain at best. Memory: *"Simple natural prompts beat complex structured ones"*.

### 5. "Command the model to calculate vanishing points before rendering"
**CONTRADICTS.** Your memory (`feedback_globe_render_experiments.md:57`): *"thinking_budget=0 saves ~30-50% latency. No benefit for image generation."* Gemini is conflating text-gen thinking with image-gen. Official Vertex docs have no parameter controlling thinking during image generation. Adding this sacrifices 30-50% latency for zero proven benefit.

### 6. 0–1000 normalized coordinate grid for placement
**CONTRADICTS.** You already tried pixel coords and they failed (`project_occluded_zone_rendering.md`: *"Pixel coordinates in prompt — no spatial grounding for generation"*). The 0-1000 normalized format is Gemini's bounding box *output* format for vision/understanding tasks, not a generation input constraint. Gemini 3.1 Flash Image has no documented mechanism to honor bounding-box constraints in the prompt. Your mask-based approach is the correct spatial grounding.

### 7. 3×3 grid layout directive
**SPECULATIVE.** No evidence. Current ZONES list already gives Gemini a numbered inventory of regions, which is functionally the same thing. The memory lesson *"Zone ordering in prompt matters"* + per-zone sequential rendering already address spatial accuracy through different means. Adding "3x3 grid" text would be noise.

---

## Items Gemini didn't raise that matter more

These weren't in Gemini's list but should be on the radar:
- **SSAO contact shadows** — Gemini mentioned this; not fully researched tonight. Would add realism but requires post-processing pipeline work. Defer.
- **Shadow-map patching via `onBeforeCompile`** — Gemini's "biggest fidelity gain" claim. Complex to implement but could genuinely help. Worth investigating before committing time.
- **Mask-based correctness fixes (#6b occlusion subtraction)** on our port plan — higher ROI than any of Gemini's suggestions for a *correctness* bug users see daily.

---

## Recommended next steps (in priority order)

1. **#6b mask subtraction** (already on the plan, real correctness bug)
2. **Stencil volume altitude cap** (one-liner-ish fix; prevents clipping at nadir)
3. **EGM96 geoid + raycast retry tightening** (polish; only matters when tiles load slowly)
4. Skip everything else from Gemini's list.
