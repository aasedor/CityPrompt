# Seedance photoreal finish

## What changed and why

City Prompt already had the whole "greybox → video model" pipeline:
`captureVideoRouteControls` in `GlobeSitePlannerMap.tsx` records a deterministic
192-frame (8 s @ 24 fps) camera move through one frozen Three.js scene — LEGO
massing plus Google 3D Tiles — and `seedance_video.py` submits it to
`bytedance/seedance-2.0/mini/reference-to-video` as `video_urls[0]`, with three
chronological route keyframes as `image_urls`.

What was missing was permission. Every Seedance submission carried the
appearance lock:

> APPEARANCE LOCK — SEEDANCE MINI IS THE ANIMATOR ONLY … do not improve,
> beautify, materialize, regenerate, relight, recolor, sharpen, restyle, or add
> detail.

plus an actor lock that removed every pedestrian and vehicle. Those two
instructions forbid exactly the transformation that makes a clay-massing render
worth sending to a video model at all. The result was a faithfully animated clay
model, which is what was asked for.

`finish_mode` makes that a choice instead of an assumption.

## The two modes

| | `massing_fidelity` (default) | `photoreal` |
|---|---|---|
| Appearance | Locked. Animate captured pixels only. | Unlocked. Materialize the study massing. |
| Entourage | Stripped — no pedestrians or vehicles. | Sparse pedestrians and slow traffic permitted. |
| Geometry, topology, object counts | Locked | Locked — identically |
| Camera, timing, route | From the preview video | From the preview video |
| Prompt length | ~1,230 words | ~720 words |
| Fidelity scoring | SSIM + edges + histogram | Edge overlap dominant (`geometry_only`) |

`photoreal` is scoped to the Seedance pilot. Omni keeps its own long-form
controlled-finish prompt untouched, so its tuned baseline does not move.

## Design notes

**The compact prompt is deliberate.** `OMNI_PILOT_3_BASELINE.md` records that
City Prompt's strongest video result came from a short prompt with one countable
scene inventory and a single finishing instruction, and warns that a longer
prompt is not a stronger prompt. A model being asked to change every surface has
to reconcile every lock it is handed; the photoreal body drops the redundant
sections and keeps geometry, topology, ground contact, and clean plate.

**The scene contract changes with the mode.** `videoSceneContract.ts` previously
told the model to preserve each zone's "materials, lighting, and level of detail
without enhancement" — which contradicts a photoreal request. Under `photoreal`
those clauses become materialization instructions while every geometry,
topology, count, and archetype-scope lock survives verbatim. Archetype names,
style words, and catalog images stay withheld in both modes.

**Fidelity scoring had to change or it would punish success.** The scorer
compares generated frames against the clay preview using
`0.58·SSIM + 0.32·edges + 0.10·histogram`. A correct materialization changes
local luminance and the entire histogram while leaving silhouettes in place, so
it would score as `drift` for doing the right thing. `geometry_only` reweights to
`0.85·edges + 0.15·SSIM`, which still catches a building that moves, merges,
splits, or duplicates. Scores from the two bases are not comparable; attempts
record `fidelity_geometry_only` so the UI can say so.

## Running the pilot

The Seedance cap is a hard server-side 4 submissions per project
(`SEEDANCE_PILOT_MAX_PROVIDER_CALLS`), about $1.98 each. Suggested spend:

1. One `photoreal` + "Preview + 3 views" on a scene with a known-good
   `massing_fidelity` attempt to compare against.
2. Read the result for the failure modes the locks target — merged buildings,
   filled courtyards, a propagated facade in the background, drifting ground
   contact — not just for whether it looks good.
3. Only then spend a second call changing one variable.

Keep the exact expanded prompt with every saved attempt, as Pilot 3 does.

## Open questions

- Whether `preview_only` or `preview_plus_keyframes` serves photoreal better.
  Keyframes anchor geometry, but they are also clay, and three more clay
  references may reinforce the clay look.
- Whether the compact body should drop `cinematography_lock` too. It is the
  longest surviving section and its restrictions may already be implied by
  copying the source camera exactly.
- Whether photoreal is worth offering for `multi_keyframe`, which has no video
  to hold the silhouette still. It currently falls back to the appearance lock.
