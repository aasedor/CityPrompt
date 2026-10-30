# Snug footprints for the newest building batch

User requirement: make the newest batch's footprint as snug to each building as possible.
Continue the building-only initiative on the deployment base; do not modify older families,
source GLBs, or the held Mews candidate.

Use the 18 exact retained geometry bounds already proved by hydrated GLB tests. Round each
horizontal extent outward to 0.1m after adding 0.02m total numerical tolerance. This yields
roughly 1–6cm per side, not a planning setback. Keep complete steps/projections inside the
rectangle and preserve unit geometry scale. Arbitrary concave/roof-outline polygons are out
of scope: the fixed native placement/compiler contract uses rectangular local axes.

- [x] Tests first: exact 18 runtime assets expose retained dimensions and snug default/minimum
  plots; old families and Mews remain unchanged. Backend fit must accept these plots at unit
  scale, reject undersized plots, and ignore unknown/mismatched model identities.
- [x] Add a packaged backend companion of the exact frontend envelope policy; assert equality
  in tests. Substitute measured dimensions only for registered immutable architectural-clay
  assembled sources. Preserve original descriptor/GLB metadata rather than editing seed data.
- [x] Map these bounds into the runtime registry. On explicit building replacement, save the
  new snug coordinates and model properties atomically through existing validation/history.
  Preserve saved plot coordinates on ordinary load. Offer Fit footprint to building for old
  enlarged placements; Place another starts snug.
- [x] Run narrow frontend/backend tests and frontend type check. Trial a fresh default drop,
  the photo's Old Montreal replacement and an old 150m plot repair through the browser;
  verify save/reload and geometry scale, capture evidence and deliver to existing private Drive.
- [x] Review diff, record exact scope/untested cases and commit locally. No paid generation,
  publication, push, live deployment, or unrelated work.
