# Five zoning-coverage building studies

User-authorized roster: Maple Porch Manufactured Cottage, Horizon Manufactured
Home, Narrow-lot Craftsman Cottage, Garden Mews Courtyard Housing and
Brick-and-timber Courtyard Office. These are original fictional concepts with
generated references, explicit programmes and RLASM v6.1 architectural clay.

The next batch is reserved for affordable housing inspired by Attainable Homes
Calgary. That future batch is not started here. Modular construction will be a
separate attribute from Calgary's Manufactured Home use classification.

The initiative reuses the existing rlasm-five-zoning-gaps worktree, preserving
all previous work. Only this folder, its narrow tests and the five new canonical
reference folders belong to this batch. Heavy output is kept externally at
`C:/dev-artifacts/CityPrompt/rlasm-coverage-five-2026-10-06`.

`designs.json` owns programmes, authored metric dimensions, storey limits,
search/style tags and independently researched candidate zoning routes.
`plan.py` verifies source bytes, hashes, dimensions and compatible role inventory.
`capture_reference.py` preserves generated PNGs unchanged with complete prompts.
`assemblies.py` reuses only opening/furniture/contact primitives; each whole
building composition is authored separately in `build.py` from its own pixels.

## Finite workflow

1. Generate Maple Porch front, oblique and top references; lock their bytes.
2. Dry-run, build and inspect the actual GLB reimport renders, then obtain a
   separate holistic independent architectural-clay review.
3. Once the pilot passes, build the remaining four as a bounded batch.
4. Preserve failed versions; every correction gets a new version and full
   rerender, with a fresh independent review of all required images.
5. Deliver a local gallery, exact model downloads, source provenance, metadata
   and a checkpoint that distinguishes generated assets from source changes.

Models are fixed authored assemblies at native dimensions. Their clay material
colours help interpretation; final source-conditioned textures remain a separate
stage. No source image is replaced by a model render. No runtime activation,
publication, database seeding or hosted deployment is implied. Runtime acceptance
records stay NOT TESTED until an actual student-facing trial is performed.

Zoning routes are preliminary educational matches, not parcel approvals. The
office is limited to about 224 m² gross floor area to keep a possible I-E route.
C-R1 additionally requires a larger principal building on the same parcel.
Garden Mews has six direct grade entrances and six private patios, but its
assembly footprint is not a complete zoning parcel. Density, street-facing
entrances, landscape, setbacks and parking require site-specific checks.

## Reproduction

Run `build.py` through Blender 5.2 with `--kind`, `--source-root`, `--version`
and an unused external `--output` directory. Run first with `--dry-run`, then
without it. Supported kinds are `maple`, `horizon`, `craftsman`, `mews`, `office`.
Completed candidates preserve their exact scripts and reference hashes, so use
that candidate's `scripts/` snapshot when reproducing a specific reviewed version.
The source folder continues to accumulate later-family refinements.

After all renders finish, run `prepare_review.py <candidate-folder>` once with
Python from this folder, followed by the RLASM skill's canonical validator and
fresh independent review. `gallery.py` requires a selection JSON mapping every
kind to its candidate `folder` and independent `review` path relative to the batch
root. It rejects failed reviews, missing inspected views, changed model bytes and
changed reviewed images.

The one-time extraction helper is preserved with external experiment records.
`assemblies.py` is the maintained implementation; do not regenerate it.

## Completed checkpoint — 6 October 2026

Final reviewed versions: Maple v004, Horizon v003, Craftsman v003, Mews v003
and Office v004. All five passed independent architectural-clay review with no
remaining P0/P1 findings. The reviewer inspected 135 original images and boards.
The earlier Mews v002 pass was withdrawn after a missed guard support was found;
its correction, reopening record and failed candidates are preserved externally.

`selection.json` identifies only the final versions. `checkpoint.json` records
exact model/review hashes and output locations. The local gallery is available
at <http://127.0.0.1:8794/> while its local server is running, or as `index.html`
under the external batch's `gallery-v001/` folder.

Verification: 25 narrow source/delivery tests passed; all five candidates passed
canonical validation. All 67 gallery URLs returned their expected bytes. Edge
checks at 1420×1158 and 390×844 verified image loading, the zoning disclosure and
no horizontal overflow, with no captured console errors or warnings. Browser
screenshots and the detailed verification records remain in external storage.
This is gallery verification, not student placement or classroom performance
acceptance. The office clay mesh is about 10.15 MB; a runtime performance and
material pass is still needed before catalogue activation.

Source, metadata and 15 intentional reference PNGs are checkpointed in Git;
PNGs use Git LFS. GLBs, Blender files, render experiments, QA boards and browser
captures remain outside the repository. No push, deployment or runtime seeding
was performed. The Attainable Homes-inspired affordable-housing batch is next.
