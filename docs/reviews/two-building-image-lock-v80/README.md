# Two-building image-lock pilot v80 — v81 refinement

This bounded pilot tests whether exact archetype images can drive construction
topology instead of serving only as informal inspiration. It uses the Amsterdam
Step-Gable House and Barcelona Mercat because they stress different failure
modes: exact vertical/opening proportions versus open spatial sections and an
intersecting roof plan.

## Result

- **Amsterdam Step-Gable House — keeper.** Three occupied levels, a capped
  flat-topped crow-step profile, ten scheduled front openings, sparse side
  openings, a recessed timber entrance and a steep charcoal tile roof are now
  fixed in the graph. The image comparison caught and removed an extra storey
  and rejected an orange/white roof response after machine validation had
  passed.
- **Barcelona Mercat — provisional.** The near-square market now has six front
  and five side open bays, four genuinely permeable frontages, recessed stall
  backdrops, coloured perimeter awnings, dark standing-seam cross roofs,
  stained skylight bands, four arched clerestories and occupied produce
  counters. The remaining fidelity gap is fine iron ornament, signage, people
  and photographic context—not a flat-wall or generic-box failure.

## V81 refinement round

- Amsterdam now has a separately glazed diamond fanlight, a paneled oak leaf
  and image-consistent black masonry anchors on all exposed elevations. The
  entrance and side wall no longer read as flat placeholder surfaces.
- Mercat brick piers continue through the contrasting header, and every open
  frontage now contains a bounded low-poly stall kit with counters, crates,
  produce and warm task lights. This preserves the validated void section and
  roof graph while adding the activity that carries the archetype photograph.
- The Mercat comparison camera is closer and less oblique, matching the
  reference framing more directly. Fine iron ornament, signage and people
  remain outside this bounded refinement, so its status remains provisional.

## Method now encoded in the pipeline

1. Exact street, oblique and roof images become a numeric feature schedule.
2. Every measurement names the graph node, assembly or void it drives.
3. Production preflight requires the named topology and material bindings.
4. Metadata is selected field by field only when it agrees with the images;
   the market disables it because the prose describes a conflicting building.
5. Openings are real sections with foreground construction and a deeper
   occupied termination.
6. Automated validation and human visual keeper status remain separate.

See `two-building-comparison.png`, `two-building-roof-audit.png` and
`review-summary.json` in this folder for the publishable evidence.
