# Concert hall refinement: preserve the original default

The bounded refinement trial produced a cleaner geometric concept, but independent
review did **not** establish better fidelity to Walt Disney Concert Hall. The
original photo-generated GLB was restored as the private trial's default. No
catalogue entries or application source were changed, and no paid generation or
image-render requests were submitted.

Starting source commit: `fe154cdcc`, branch `codex/house-flex-pilot`.

## Delivered comparison and decision

The first two material/smoothing candidates retained unacceptable mesh artifacts.
The subsequent source-guided reconstruction replaced the generated geometry with
separate swept shells, panel courses, roof returns, recessed framed glazing,
stairs and a planted terrace. Later bounded corrections restored front orientation,
recessed the auditorium body, closed lower roofs and removed zero-area roof-tip
triangles. This was manual authoring, **not an improvement automatically available
to students through the photo generator**.

Final comparison candidate: `walt-disney-concert-hall-rebuilt-v006`.
GLB SHA-256: `18e2dec2c9aa472eeab27871f12f976a6b69117944068ea0361ff60943a1421a`.
The model contains 15 meshes, 256,796 triangles, no image dependencies, finite
coordinates and zero degenerate triangles. Those checks establish delivery validity,
not architectural correctness. Actual landmark dimensions remain unverified; the
existing private trial uses an approximate contain-fit placement.

Independent holistic review inspected all 12 exact-GLB renders, two phone boards,
the source board, the three source photos, original model views and an application
screenshot. Its decision is `visual_rework_required`, with three P0 and three P1
findings:

- The roof and corner forecourt are too regularized relative to the photographs.
- A continuous roof-to-shell slit remains visible.
- Some lower shells lack convincing enclosure/support.
- Sail proportions remain approximate.
- Glazing reads opaque and does not demonstrate interior depth.
- Material appearance is too uniform offline and too dark in the globe lighting.

The reviewer judged it useful as a labelled private concept comparison, but not
more faithful than the original. It is not a keeper, classroom catalogue asset,
or approved architectural-clay delivery. Future correction should use measured
source silhouettes/plan traces and solve roof contacts before additional detail;
another unbounded generation or polishing loop is not justified by this trial.

## City Prompt check and rollback

Local frontend: `http://127.0.0.1:5183`; backend: `http://127.0.0.1:8007`.
Disposable project: `a4b28067-b47a-4daf-9faf-e9e505daa595`.
Building: `f465419b-4a10-49e1-91ce-60e117e18d6a`.

The comparison was installed only in this disposable project using a hash-verified
new private storage key. Existing source/reference photos, placement and original
model bytes were retained. The manual replacement initially inherited the Meshy
untextured/clay treatment. Setting its private authoring engine to `rlasm` preserved
its authored PBR materials; this renderer binding does not confer visual approval.

Browser checks confirmed loading after reopen, oblique/top views and entry into
Walk on a valid off-site ground point. The first prepared-lawn Walk start was
rejected as above ground; choosing the visible surrounding ground recovered. No
uncaught browser errors were reported. Shell materials remained too dark for a
successful visual acceptance result. Ground continuity, entrance routing, movement,
undo/redo, exact capture and paid rendering were not accepted by this limited test.

After review, the original model URL, LODs, preview, specifications, generation
status and engine were restored through the shared representation-invalidation
hooks. Original model SHA-256:
`9c251dc59b2b22a17601fcf5196530f5368bb6fc769c1798db3ecc8c77b96bef`.
The account remains at 550 City Prompt tokens.

## Evidence and reproducibility

All source locks, authored scripts, GLBs, intermediate history, 12-view render sets,
phone boards, browser screenshots, rollback snapshot and independent JSON review
are outside Git under:

`C:/dev-artifacts/CityPrompt/concert-hall-refinement-2026-09-30/`.

The source authority remains the user's front photo and Carol M. Highsmith's two
real aerials documented in [the web-reference trial](PHOTO_BUILDING_WEB_REFERENCES_2026-09-30.md).
The [LA Phil panel description](https://www.laphil.com/posts/walt-disney-concert-hall-in-numbers)
informed panel proportions; it does not establish this model's dimensions.

Deterministic candidate preflight passed without a keeper request. The independent
visual review failed keeper acceptance as recorded above. No TypeScript/backend
production code changed, so unrelated application tests were not repeated.
