# Neighbourhood library and corner café

This finite RLASM v6.1 batch extends the local validation catalogue with two
exact-reference architectural-clay models. Human publication remains pending.
These are fixed native assemblies; enlarging the plot does not stretch the model.

## Source and visual contract

- Mass-timber Library: `university_library / mass_timber_biophilic_barn`,
  exact catalogue variant 2, front/60-degree/top references.
- Corner Café & Apartments: `parisian_boulevard_corner /
  parisian_corner_cafe_culture`, exact variant 1 and the same three view roles.
- Each package includes the locked originals, source hashes, measurements,
  authoring snapshot, exact exported GLB, 14 reimported views, three
  1080 × 1920 comparison boards and an independent holistic review.
- The library retains planted stepped roofs, branching timber supports,
  recessed glazing, visible reading spaces and book stacks.
- The café retains the open courtyard, ochre brick and cream stone courses,
  iron balconies, continuous green canopy, clear central entrance, two tiers
  of seated curved dormers and multi-pot chimneys.

The delivery tier is architectural clay, matching the catalogue's native clay
assets. It is not a textured keeper or a surveyed construction model.

## Review and runtime

Library v003 passed independent review with zero P0/P1 findings. Its exact
local storage binding passed byte-hash verification. Catalogue placement,
48 × 43 m plot resize, 15-degree rotation, moving, undo/redo and reopening
passed in the disposable prepared-site project. All 14 meshes remain visible
at world scale 1:1, with no grounding issues after preparing the site.
The reviewed entrance is locked to this variant and revision and stays fixed
when its parcel grows. Earlier natural-terrain placement correctly raised
the existing foundation-height limit.

Café v010 passed independent holistic review with zero P0/P1 findings.
Its 292,176-triangle export has 14 runtime meshes and SHA-256
`bbfd154388f29ed53aa80369635d2fdac76a2e4e9518650027268525d3ddf47b`.
The exact local storage binding passed byte-hash verification. Its minimum plot
is 49 × 48 m. Catalogue search, placement, enlargement to 52 × 52 m,
5-degree rotation, undo/redo, moving and reopening all passed. Moving with
automatic street facing enabled realigned the model to the nearby street
(0.4356 degrees); the enlarged parcel, revision and measured entrance persisted.
All 14 café meshes are visible at world scale 1:1.

The combined library/café/two-park scene settles with no grounding issues and
no browser errors. Exact readback is in `combined-runtime-final.json`, with
screenshots beside it in the external evidence root. Focused frontend tests:
35 pass in the combined checkout; the building checkout's TypeScript check
passes. The two exact-revision entrance tests include fixed world anchors
when plots grow and correct UTF-8 catalogue labels.

## Reproducibility and evidence

`tools/neighbourhood_buildings/prepare.py` locks exactly these two source sets.
The two builders use explicit external output directories and reject existing
candidates. `review_boards.py` preserves the source/render pixels in the
comparison boards. `stage.py` uses canonical promotion with `trial_only=True`.
Only exact reviewed models and review records enter the canonical clay seed;
GLB binaries use Git LFS. No release catalogue activation is implied.

Full generated evidence and failed candidates remain at
`C:/dev-artifacts/CityPrompt/neighbourhood-four-2026-10-01/`.
The café's failed roof iterations remain preserved. Its final cap uses a simple
inward ring, a shared cap/carrier datum, and 11 explicit planar faces generated
from a straight skeleton. This prevents openings, folded surfaces and shading
across roof breaklines. `prepare_cafe_roof.py` verifies complete coverage and
no overlap before writing `cafe_roof.json`; the Blender builder checks every
face is planar. The optional preparation dependency is
[py_straight_skeleton 0.1.0](https://github.com/iconbuild/py_straight_skeleton),
installed externally. The normal build reads the retained JSON directly.

## Verification limits

The local validation project is `888a5b24-0ec2-4458-915d-757b6395d495`, served
at localhost:5185 from the park worktree stacked on the building commits.
Public street connections and paid image generation were not exercised.
The legacy `reviewedEntrances.test.ts` fixture references a beltline asset
absent from the current local catalogue and fails at module initialization;
the new exact-revision entrance tests run independently.
No source changes were made in the user's dirty primary checkout, and nothing
was pushed or deployed.
