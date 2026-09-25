# High-quality 3D park memory

## User direction — 2026-09-25

The user especially likes the **Conservatory botanical garden** and wants
future park builds constructed to its standard. Treat this as a durable visual
quality benchmark, not an instruction to copy its garden program into every
park.

The exact reference is `botanical_garden/botanical_garden_v3`, asset
`conservatory-v013`, assembly SHA-256
`464f2968e652c84136c1858d3d0d1a1fe7d6bd956824dfc7f785752f3ec551d2`,
native footprint **48 × 62 m**. Its model and near/far review views are in the
local evidence package at
`C:/dev-artifacts/CityPrompt/showcase-six-2026-09-24/parks/conservatory-v013/`.
The versioned catalogue record is in
[`frontend/src/data/validationCatalogue.json`](../frontend/src/data/validationCatalogue.json).

## What future parks should carry forward

- **An authored, legible plan.** The conservatory is a clear focal point;
  connected curving paths lead to it through distinct planting rooms. At aerial
  scale, the path network, entrance, central feature and edge planting remain
  readable rather than dissolving into generic scatter.
- **Landscape richness with control.** Dense planting uses varied height,
  colour and texture while preserving the paths and focal spaces. Repetition
  creates coherent beds and borders rather than a uniform lawn or random props.
- **A convincing pedestrian-scale scene.** The gate, paving, low edges,
  planting, small amenities and glass structure have enough physical detail and
  material separation to hold up from an entrance or walking view as well as
  from above. Openings and routes remain usable, not merely decorative.
- **One cohesive material language.** Paving, edging, planting, timber details
  and the conservatory frame feel designed together. New parks should reach the
  same degree of coherence using materials and forms appropriate to their own
  reference photos and program.
- **Complete 3D composition.** Build the program and defining landscape as
  actual grounded geometry with reliable spacing, containment and shadows;
  do not rely on an image finish to invent the park's identity. Preserve
  metric scale and whole elements when fitting different site shapes.

For every new park, compare an aerial view and at least one pedestrian-height
view against this benchmark. Ask whether the proposed park is as recognizable,
composed and finished at both scales, while still accurately resembling its
*own* archetype references. Use the existing pilot-before-scale workflow and
record evidence in the exact-variant runtime review.

## Approval boundary

This is **visual baseline approval only**. The exact conservatory record is
currently marked `user_approved_visual_baseline`, `app_eligible: false`, and
`runtime_status: NOT TESTED`; it must not be described as fully completed or
published on this preference alone. Future parks still need the fit, terrain,
access, editing, capture and in-app checks in
[`ARCHETYPE_RUNTIME_INTEGRATION.md`](ARCHETYPE_RUNTIME_INTEGRATION.md) and
[`ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md`](ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md).
