# Development render mode — archetype-refs A/B (2026-07-14)

Pilot for the "Development" globe render style (C2 of
`docs/LEGO_TEXTURES_PLACE_RENDER_PLAN.md`). One scene, one camera, both arms:
the Lego Test project (`c21ff031-0f60-4486-91f8-351f94d794b0`) with three
placed `calgary_modern_infill_house` LEGO stacks in view among real downtown
Calgary tiles. Engine: GPT Image 2 (the panel's two preview variants per arm).
Prompt in both arms: the Development style prompt + per-building identity tail
+ end-anchored massing/floor/roof preservation constraint.

| Arm | Setting | Images |
|---|---|---|
| A — refs ON (default) | archetype card refs attached (9 refs incl. plan diagram) | `lego_previews/dev_render_ab/devrender-refs-on-{A,B}.jpg` |
| B — refs OFF | `localStorage.cc_development_refs = '0'` (plan diagram kept) | `lego_previews/dev_render_ab/devrender-refs-off-{A,B}.jpg` |

## What both arms got right

- All three stacks resolved into finished 3-storey infill townhouses at the
  exact stack positions, footprints, floor counts and flat roof forms — the
  placed massing worked as geometry conditioning, no invented buildings.
- Landscaped frontages, entry stairs, street trees, cars, pedestrians.
- Watermark + save pipeline untouched.

## Where they differ (why refs stay ON)

- **Context fidelity:** refs-ON keeps the surrounding photograph's neutral
  daylight — the frame still reads as the same capture. refs-OFF re-toned the
  ENTIRE image into golden hour (and lit interior windows mid-day in variant
  B), drifting from photomontage honesty.
- **Material identity:** refs-ON facades track the archetype cards more
  closely (charred timber / wood / white-panel mix); refs-OFF is attractive
  but more generic modern-infill.

**Default shipped: refs ON.** The `cc_development_refs` flag stays as a debug
lever.

## Notes / limits

- The fourth placed building (contemporary midrise pair) was out of the
  render frame in this pilot; nothing observed about tall-building behaviour.
- Both arms ran GPT Image 2 (panel default variants). A Gemini-arm comparison
  is untested.
