# Same-Angle Degradation Bug — Diagnostic Report

**Date:** 2026-04-17
**Method:** 2 parallel research agents, diagnostic only (no code changes per user's "don't skip ahead" rule)
**Bottom line:** 3 independent causes found. The big one is a seed-not-sent bug in the backend. Implementation (steps 3-7 in your plan) should wait until you see this.

---

## TL;DR — three distinct root causes

1. **🚨 Seed is discarded by the backend** — frontend generates a random seed, sends it to the backend, backend **never forwards it to Gemini**. Every render is a fresh random sample.
2. **Screenshot capture is non-deterministic** — tile LOD streaming + fade animations + race conditions in `map.once('idle')` mean two clicks at the "same" angle feed Gemini different pixels.
3. **Pass 1 output can flow into Pass 2 input** (only when per-zone rendering is triggered, which is currently gated off). Lower priority.

---

## Cause #1: Backend silently drops the seed ★ most impactful

**Evidence (`backend/app/api/v1/render.py`):**

- Lines 93–96: Request *accepts* a `seed` field
- Lines 476–477: `generationConfig` payload is built **without** a `seed` key:
  ```python
  gen_config = {
      "responseModalities": ["TEXT", "IMAGE"],
      "temperature": temperature,
  }
  # no "seed" field added
  ```
- Line 595: Response *echoes* the input seed back, making it look like the seed was honored:
  ```python
  return RenderResponse(image_base64=image_b64, seed=req.seed)
  ```

**Frontend does randomize per call** (`useAIRender.ts:2544`):
```ts
const seed = options.seed ?? Math.floor(Math.random() * 2147483647);
```
...but this is ceremony — the seed is never used.

**Answer to your Q4 ("is seed fixed, randomized, or unset"):** Randomized frontend, **unset on the actual Gemini call**. This is the simplest and highest-ROI fix: add `"seed": req.seed` to `gen_config` in `render.py` so the seed actually reaches Gemini.

---

## Cause #2: Screenshot non-determinism

**Evidence:**
- Capture code: `useAIRender.ts:362–373` — reads directly from `map.getCanvas().toBlob()`.
- Before capture, code awaits `map.on('idle', ...)` with a 500–2000ms timeout fallback (`useAIRender.ts:2651-2654, 2922, 2946-2956`).
- `map.once('idle')` fires when Mapbox reports tile loading done — but 3D Tiles progressive refinement (`GlobeSitePlannerMap.tsx:1610, 1612`: `UpdateOnChangePlugin`, `TilesFadePlugin`) continues AFTER idle.
- Three.js fade animations use `requestAnimationFrame` (`GlobeSitePlannerMap.tsx:975-980`) — timing varies per frame.

**Answer to your Q2 ("does capture produce pixel-identical output for the same camera"):** No. Two clicks at the same camera, 2 seconds apart, will very likely produce non-identical bytes due to:
- Tile LOD streaming (labels + detail load progressively)
- 3D-Tile fade animations still in progress
- `idle` event racing a timeout

Combined with Cause #1 (no seed → different sampling anyway), small input variance compounds into visible output drift.

---

## Cause #3: Pass 1 → Pass 2 feedback loop (conditional)

**Evidence (`useAIRender.ts:3020-3225`):**

Two-pass architecture exists for complex sites:
- Pass 1 (line 3020-3093): renders all ground zones (parks/roads/water) in one call
- Pass 2 (line 3100-3225): renders each building sequentially

Line 3085: `cumulativeDataUri` is built from Pass 1 output. Line 3216: subsequent building renders receive `cumulativeDataUri` as their `imageBase64` input.

**BUT:** This path is gated by `PERZONE_THRESHOLD`. On the current branch (port/phase-1-polish) and codex, threshold is 99 — per-zone sequential essentially never triggers. You always hit the single-shot path (line 2458 `renderSingle`).

**Answer to your Q6 ("confirm no output-to-input feedback"):**
- Single-shot path: **No feedback**. `imageBase64` is always re-captured from the map canvas.
- Per-zone sequential path: **Yes, feedback exists** — Pass 1 AI output flows into Pass 2 input. Not currently firing.

When/if you lower `PERZONE_THRESHOLD`, this becomes Cause #1-scale critical.

---

## What's NOT the problem

Ruled out by the diagnostic:
- ❌ Prompt variance — `buildSCHEMAPrompt` is byte-deterministic for the same zones (no timestamps, `Math.random`, shuffled arrays).
- ❌ Caching of stale intermediate state — `cumulativeDataUri` is per-call local, zones are re-read, mask is re-generated each click.
- ❌ Prompt or mask being fed back from prior renders — nothing in `rendersApi` or store gets re-injected as context.

---

## Answers to your 7-step plan, per the diagnostic

| Step | Verdict after diagnosis |
|---|---|
| 1. Trace pipeline | DONE (this doc) |
| 2. Check seed determinism | DONE — randomized frontend, **discarded backend** |
| 3. Implement camera jitter | **LOW PRIORITY** — fixing seed + screenshot timing addresses root cause first; jitter would only be needed if degenerate attention *still* occurs after those fixes |
| 4. Add seed randomization + logging | **Seed randomization already exists; the fix is making the backend actually FORWARD it to Gemini.** Logging the seed alongside output still worth doing |
| 5. Cache Pass 1 | **NOT NEEDED today** (PERZONE_THRESHOLD=99, per-zone path doesn't fire) — add if you drop the threshold |
| 6. Verify no output→input feedback | DONE — none in the single-shot path; exists in the dormant per-zone path |
| 7. Debug-dump mode | Recommended — still valuable for validating fixes |

---

## Recommended order when you resume

1. **Fix backend seed forwarding** (one line in `render.py`). Immediate determinism win.
2. **Tighten screenshot capture timing** — either (a) wait longer after `idle` (cheap), (b) explicitly gate on 3D-Tiles fade completion, or (c) add the debug-dump from step 7 and measure variance before choosing.
3. Implement the debug-dump (step 7) — lets you quantify the improvement from (1) and (2).
4. Only if variance still visible after 1-3: consider camera jitter (step 3).
5. Skip steps 4 ("add seed randomization") — redundant after fixing #1. Skip step 5 — not firing.
