# Omni Pilot 3 baseline

## Why this result is preserved

Original Omni Pilot 3 is the earliest strong City Prompt video result for the
Calgary two-building/one-park scene. Its opening four seconds kept the two
buildings stable, retained the left building's two-courtyard topology, and
closely reflected the authored 3D massing.

Treat this attempt as a prompt and visual-comparison baseline. Do not overwrite
or silently modernize the prompt below when the production prompt changes.

## Saved attempt

- Attempt ID: `b8c855ac-5319-49e9-9dae-082296b23b7d`
- Created: `2026-08-03T04:34:23.684514+00:00`
- Provider: Omni
- Duration: 8 seconds
- Camera motion: `path_follow`
- Control input: one City Prompt planning image with temporary route markup
- Route: lower center to upper center, nearly straight, three guide bends
- Status: complete

## Exact expanded prompt

```text
Create one single continuous, unbroken 8-second 16:9 professional architectural drone shot from the supplied City Prompt planning image. This is one coherent camera take—no cuts, montage, jump transitions, or time lapse.

FLIGHT PATH: The red line, start circle, waypoints, and arrow in the source image are temporary navigation markup only. Remove all route graphics before the first visible frame. Strictly follow the route from its start circle to its arrowhead at a smooth, physically plausible speed. The route begins in the lower center of frame and finishes in the upper center, nearly straight, using 3 guide bends. Follow the drawn route precisely as a smooth forward drone flight. Translate continuously through space with gentle banking only where the route curves.

SCENE IDENTITY: Preserve the exact site plan and recognizable spatial identity of the source. Two masonry courtyard buildings frame a formal rectangular central park with paths, lawns, and trees. Keep exactly the same two dominant buildings and the same central park, at the same locations, footprints, heights, proportions, setbacks, rooflines, courtyard openings, paths, and street relationships from beginning to end. Architecture and site geometry are immutable.

VISUAL FINISH: Transform planning-view materials into photoreal, construction-plausible architecture and landscape. A refined after-rain atmosphere with damp paving, subtle physically plausible reflections, soft overcast-to-sun light, rich planting, and cinematic contrast. Use realistic PBR materials, coherent reflections, detailed planting, a few naturally scaled pedestrians, and sparse slow vehicles only where streets already exist.

CONTINUITY LOCKS: Maintain one stable world coordinate system and physically realistic parallax. Do not add, remove, duplicate, repeat, resize, bend, melt, or redesign any building, road, park, path, tree mass, or landmark. No facade warping, sliding textures, floating objects, fisheye distortion, excessive motion blur, visible red route, pins, labels, captions, logos, borders, or split screens. Keep the horizon level, motion fluid, exposure stable, and the final composition calm and sharp. Output polished 720p 24 fps cinematic footage.
```

## Learnings to retain

### Observed

1. The prompt used a short, explicit scene inventory: exactly two dominant
   courtyard buildings framing one rectangular park.
2. Geometry requirements were direct and concrete: same locations, footprints,
   heights, proportions, rooflines, courtyard openings, paths, and street
   relationships.
3. The route was simple and nearly straight, with only three guide bends.
4. Visual finishing was constrained to plausible materials, lighting,
   landscaping, and sparse entourage.
5. A compact continuity block prohibited the most common temporal failures.
6. The opening four seconds were stronger than the later part of the clip.

### Working hypotheses

- The compact prompt left less room for competing instructions than later,
  substantially longer prompts.
- The explicit two-building/one-park inventory helped Omni preserve object
  count and scene topology.
- The simple camera path reduced the amount of unseen geometry Omni had to
  invent.
- Restrained PBR finishing gave Omni a narrow task instead of inviting a scene
  redesign.
- The after-rain look may have improved perceived polish, but it is not proven
  to have improved spatial stability and should remain optional.

## Product rules derived from the pilot

1. Keep a **Simple Fidelity** prompt recipe available as a regression baseline.
2. Describe the visible scene with a compact, countable inventory before adding
   visual direction.
3. Prefer short routes and gentle camera motion when fidelity is more important
   than coverage.
4. Use Omni primarily for visual finish and animation; City Prompt remains the
   geometry, context, and camera authority.
5. Add prompt constraints only when they address a measured failure. Do not
   assume a longer prompt is a stronger prompt.
6. Compare future prompt variants against Pilot 3's first four seconds for
   building count, courtyard topology, context stability, and visual quality.
7. Change one prompt variable at a time in bounded trials and retain the exact
   expanded prompt with every saved render.

## Important limitation

This was a single-image generation. It is evidence that a compact prompt can
work well, not proof that one image is the best control method. The current
preview-video workflow should keep the deterministic City Prompt video as
camera and geometry ground truth while borrowing Pilot 3's concise inventory,
finishing discipline, and continuity language.
