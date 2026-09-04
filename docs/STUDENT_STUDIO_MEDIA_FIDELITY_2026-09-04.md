# Student Studio media fidelity — 2026-09-04

This update supersedes the unchecked ordinary `scene` acceptance described in
the July presentation-first pipeline. It does not turn off presentation-first
or change the archetype assets.

## Exact scene capture

- Google tile masking tests the actual simple polygon with even/odd crossings.
  Concave notches remain outside the proposal; no convex hull expands the site.
- Invalid rings or the existing 8-polygon/32-edge budget retain context. The
  projected stencil-volume fallback has been removed because it erased unrelated
  context along camera rays. Dense unsupported boundaries still need a future
  capacity solution; they are not silently simplified.
- The mask cache includes geographic position, so moving the same-shaped site
  invalidates the mask correctly. Prepared site elevation is shared.
- Depth and normal capture materials inherit tile-mask logic and source alpha,
  sidedness and depth policies. Demolished tile geometry cannot return solely
  because a capture pass used a global override material.
- Depth uses opaque 24-bit RGB packing: packed RGBA depth lost its RGB values
  when Canvas2D premultiplied the fractional depth alpha during PNG encoding.
  Depth and normal targets use linear numeric encoding (`NoColorSpace`).
- Real facade normal/bump maps are retained only by the normal control material;
  attaching them to a depth material crashes Three's uniform refresh. The GPU
  fixture includes mapped materials, and empty rendered map context is rejected.

## Shared prepared ground

Authored zones wholly inside the active cleared boundary use that boundary's
saved ellipsoidal datum. Polygon containment checks every edge interval after
boundary intersections, including narrow concave notches. Street fills, curbs,
paint, roundabouts, junctions, park props and residual trees no longer sample
the old photogrammetry inside that prepared site. Imported relief is disabled
there as well. Model ownership includes secondary building IDs without moving
their individual footprints. Outside zones and existing context retain their
own terrain. All visible geometry continues to test depth.

The prepared backing is 6 cm below the authored ground surface: its local lift
is 2 cm, while street/park fill remains at 8 cm, road details at 10 cm and paint
at 10.6 cm. Live ECEF probes confirmed this ordering, replacing the former
coplanar lawn/road fill and street paint that jumped 6–9 m to old tile surfaces.

The disposable QA fixture originally used the elevation API's approximate
geoid conversion (1022.89 m). Actual local tile probes around the street/site
perimeter measured about 1031.1–1032.4 m, with excavation/roof outliers at
1025/1106 m. Only that fixture was calibrated to a documented 1031.3 m datum;
no global correction heuristic was added. The normal drawing UI instead stores
representative heights collected from drawing-point hits. Boundary corners on
roofs and the API's approximate vertical reference still need calibration;
this patch is not a terrain estimator or survey-grade grading system.

## Images

- The final prompt constrains custom style to finishes, decor and activity.
  Buildings cannot gain height or footprint or move to expose hidden objects.
  The final preservation suffix survives prompt-length truncation for both
  Classic providers as well as Direct 3D.
- Same-camera aerial presentation registers the candidate, preserves every
  source pixel outside the visible proposal mask, restores certified RLASM
  instance pixels, then measures macro layout, visible-instance edges and
  unsupported new structure. Missing/failed evidence returns the clean source.
- Empty instance evidence is `not_evaluated`, not a successful check. Fully
  occluded instances are not demanded in the image. Blank macro evidence fails.
- All generative presentation results are `review_required`. Registration and
  edge similarity are useful drift checks, not proof of exact 3D identity.
- Street and projection-changing views remain review-first and use content
  sanity rather than aerial registration assumptions. A content failure returns
  their own source capture and explicitly retains its camera. There is no
  substitution of an unrelated aerial view.
- A failed finish returns `returned_safety_strategy=authoritative_source`.
  The produced provider original remains a separate review artifact.

## Persistent provenance

Before the provider request, the server freezes the validated rendered zones,
scenario properties and linked buildings. A JSON sidecar stores this plan and
the capture camera; the gallery PNG embeds their revision identifiers and
sidecar URL. Camera evidence is explicitly a validated client capture manifest,
not an independently measured server camera. Missing cameras have no fabricated
camera revision. Source-identical images from different plans are separate saves.

The Direct 3D response includes nullable `saved_render` and
`provider_original_render` entries so accepting the result can reuse its server
artifact. Manual save requests cannot attach authoritative source metadata.
Classic renders lack an exact validated scene/camera claim and retain that
limitation; a prompt lock alone is not geometry enforcement.

Gallery `outcome` is the stable review status; `presentation_strategy` separately
records a clean-source fallback, repaired finish or provider original. Both are
embedded in the PNG and sidecar. Equal image bytes are reused only when these
fields, source/camera/output revisions and render settings also match. Historical
compound outcome labels are normalized when read, preserving their stored audit.

## Verification and remaining visual checks

The final targeted shared-ground/capture tests (61), full frontend type check,
and scoped ESLint passed. Report component tests (4) passed during implementation.
After the gallery outcome fix, the combined Direct 3D, provider prompt and
fidelity/provenance suite passed 156 tests, including 14 focused provenance cases.
This workstream's checks made no provider calls; the root's separate live pilot
is described below.

The live disposable L-shaped site was reviewed in an oblique aerial view. Its
concave notch retains an existing building, surrounding context remains visible,
and foreground buildings naturally occlude the proposal. The road fill, paint,
park and backing now share a consistent surface. The square 1024 capture and its
complete unsent request are in the ignored directory
`artifacts/student-studio/media-fidelity/`: `pilot-beautyImageBase64.png` and
`pilot-direct3d-request.json`. The capture fingerprint is
`d3d-1024x1024-16a1decc`, with visible proposal coverage of 6.11%. Geometry-control
PNGs and the persisted zone snapshot are alongside them. This is a reviewed
source for a bounded fidelity pilot; coarse photogrammetry and conceptual
site-edge grading remain visible.

The root agent's one live image pilot returned HTTP 200 but failed the layout,
visible-instance and unsupported-structure checks. It returned the clean source
with `outcome=review_required` and `presentation_strategy=authoritative_source`;
the provider original was retained separately. Independent visual review found
a larger side volume and altered bungalow roof/porch, revised park treatment and
road margins. The more polished finish is not evidence of matching authored
geometry. This pilot also exposed a gallery deduplication collision with an
earlier mocked result; the separate status/strategy contract above fixes that
mislabeling, with recorded-output replay requiring no second paid call.

The unchanged approved bungalow in this local fixture is compiled as a LEGO
assembly, without server-certified RLASM source-lock metadata. This pilot tests
the generic layout, visible-instance and context checks; it does not demonstrate
certified RLASM pixel restoration. Compare any actual AI finish with the source
before presenting it. Street-level, relocated-site and over-budget mask cases
still need live visual review in addition to their deterministic test coverage.

The free GPU regression `frontend/scripts/verify-direct3d-capture.cjs` uses an
existing Vite server (`CAPTURE_QA_BASE_URL`) and writes only to an artifact
directory (`CAPTURE_QA_OUTPUT_DIR`). It compares the real clipping shader with
explicitly cut concave geometry, decodes exported PNG depth against the camera,
and checks encoded normals. The 640² fixture passed with only 26 depth and 13
normal/mask boundary raster pixels differing, and no shader errors. It makes
no authenticated API requests or provider calls.

Detached-house plots now use a separate bounded planner: native house envelopes
are repeated inside the actual plot with setbacks and gaps, without stretching
one house across the block or borrowing the streetwall layout. The planner caps
each plot at 256 dwellings and rejects a plot where no native house fits. The
approved v020 Calgary bungalow remains unchanged; its conservative placement
envelope is 13.64 × 20.46 m. A local 120 × 40 m fixture contains eight independent
houses, and the live L-shaped QA scene contains one house on a 29 × 28 m plot.
Access and planning compliance still need review against the surrounding plan;
these placements are not proof that every house has suitable street access.

The current paid-action tile wait now requires a stable, nonempty set of visible
tiles for 900 ms, with an eight-second deadline. Background downloads outside
the current view do not block a complete visible capture; an empty or continually
changing visible set still stops the render before credits are used. Because
Google's visible set may initially contain coarse ancestor tiles, the aerial
capture additionally requires actual context pixels to cover at least 1% of
the frame; a proposal floating against empty sky cannot pass this check.

The deterministic capture controls support future walkthrough/video work, but
this patch does not deliver a persistent generated world. Different-camera
street finishes and video remain generative review outputs; image checks do not
prove cross-frame identity, accessibility, physical simulation or exact geometry.
