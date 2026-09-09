# Skyscraper student trial — 2026-09-08

Local project: **Skyscraper trio — student trial**

http://127.0.0.1:5177/projects/9b77dbcd-b21b-4dbf-a425-216db44ed183

## Scope and result

Installed the reviewed blue glass office v003, Vancouver residential podium v004,
and twisting sky-garden v005 models in the isolated local catalogue/storage.
Seeder dry run, installation, and exact-byte readback passed for all three.
These remain pilot entries, not approved published catalogue assets.

Created a new Currie site through the UI and placed all three through the asset
picker. Reshaped the Vancouver plot from 52 m to 65 m wide and rotated it 8 degrees;
the native building dimensions remained intact. Reload preserved all three zones.
The final project contains those three buildings and the two saved renders.

## Fixes discovered through the trial

- Focus Plan and Focus Building now frame roof heights as well as footprints.
  Previously the tallest tower extended beyond the screen.
- Switching to Top View after focusing retains the site ground anchor, avoiding
  a centre-ray intersection far behind the site when the camera targets a tower.
- A rejected boundary that excludes an existing building can now be discarded
  safely. Unknown conflicts and uncertain saves retain their existing protections.
- Ground Review disables saving against an unsaved boundary and explains how to
  resolve it, instead of attempting to update a temporary zone ID.

## Render results

Two paid image calls were made, using 166 local application credits in total.
Actual provider dollar cost was not independently verified. All outputs and
provenance are outside Git at:

`C:/dev-artifacts/CityPrompt/skyscraper-trio-2026-09-08/`

1. Photorealistic overview: main tower positions and shapes were retained, but
   ground/landscape changes still require review. The final output is marked
   `review_required`; it is not an exact-geometry certification.
2. Cropped watercolour: the tall tower remained cropped, but the provider invented
   roads, crossings, planting and landscaping. The application selected the
   authoritative 3D source as its safe final output. The attractive watercolour
   original is retained for review, not accepted as a faithful final render.

Files: `trial-photorealistic-provider_original.png`,
`trial-photorealistic-final.png`, `trial-watercolour-provider_original.png`,
`trial-watercolour-final.png`, and matching provenance JSON.

## Remaining ground limitation

A correctly enclosing diagnostic boundary was created through the local API
after the student UI boundary attempt was rejected. Its retained-terrain review
detected an abrupt height change and made the shared surface unavailable. All
three buildings then disappeared with `ground_not_ready`. This is a whole-site
ground readiness limitation, not evidence that the three GLBs failed to load.

Removed only that diagnostic boundary (HTTP 204), then reloaded and verified
all three buildings visible again, with no grounding issues reported. The final
working project has no site boundary. No existing user project was modified.

Next priority: validate ground locally per footprint, isolate unreliable patches,
and retain previously verified placements during remeasurement without permitting
unverified render captures. Flat plot aprons and terrain joins also need refinement.
Do not simply disable ground validation to make the models visible.

## Verification and publication status

- Focused tests cover framing, frame retries, zone save/discard, and Ground Review.
- TypeScript type-check passed.
- Browser reload and placement checks passed; no uncaught browser errors reported.
- A 120-frame browser sample measured median 17.8 ms and p95 18.1 ms. This is a
  short browser frame-interval sample, not a GPU benchmark or large-project test.
- Catalogue registry tests passed; the publication readiness test intentionally
  fails while these entries have `pilot` readiness. Do not weaken that gate.

Source fixes and this report are separate from the local trial catalogue wiring,
GLBs, generated imagery and pre-existing PNG working-tree differences. Nothing
was pushed to main. Ground integration and render fidelity remain open review
items before these towers can be described as fully accepted student assets.
