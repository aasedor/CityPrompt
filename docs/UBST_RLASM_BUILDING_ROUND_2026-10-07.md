# UBST student-inspired RLASM building round

This initiative follows the user's approval of the next generation round. It
uses the current RLASM 6.1 method and starts with one representative live/work
pilot before expanding the bounded five-building batch.

## Bounded scope

| Building | Student-project motivation | Proposed programme |
|---|---|---|
| Live/Work Townhouse Row — pilot | GenEx and small mixed-use proposals | Three studio/shop units with independently entered homes above |
| Neighbourhood Courtyard Block | Cascade Heights and Westbrook | Modest mixed-use perimeter block enclosing a usable courtyard |
| Student Courtyard Residence | East Edge | Student housing with shared study and social space |
| Timber Co-housing Terrace | Fort Calgary and winter housing | Family homes with shared amenities and timber expression |
| Garden Hotel | Green Gardens | Small hotel with planted terraces and an active entrance |

The proposed parks and streets belong to separate initiatives. This branch
does not modify them or the live student catalogue.

## Pilot source authority

Three newly generated original images are locked under
`frontend/public/archetypes/buildings/ubst-live-work-row/`. Exact prompts,
generation inputs, SHA-256, byte counts and image dimensions are retained in
`generation-provenance.json`. These are original teaching designs, not photos
or surveyed drawings of an existing building.

An independent source-only review found the three images compatible. The front
controls the three-bay and window schedule; the high oblique view controls the
three parallel gable ridges and two shared valleys. At the authored 18m frontage,
the front reference indicates approximately 9.33m eaves and 11.60m ridge above
entrance grade. The 10m depth, rear, left side and internal programme are inferred.

The first output is architectural clay with source-derived proportions and
physical cedar-board relief. It is not a final textured keeper. A photoreal
original reference remains the future catalogue hero image.

## Reproduce

```powershell
python -m pytest tools/ubst_rlasm_buildings/test_references.py -q
blender -b --python tools/ubst_rlasm_buildings/build.py -- --output C:/dev-artifacts/CityPrompt/ubst-rlasm-buildings-2026-10-07/live-work-v002 --version 2 --dry-run
blender -b --python tools/ubst_rlasm_buildings/build.py -- --output C:/dev-artifacts/CityPrompt/ubst-rlasm-buildings-2026-10-07/live-work-v002 --version 2 --resolution 1440
python -m tools.ubst_rlasm_buildings.prepare_review C:/dev-artifacts/CityPrompt/ubst-rlasm-buildings-2026-10-07/live-work-v002
blender -b --python tools/ubst_rlasm_buildings/audit_routes.py -- C:/dev-artifacts/CityPrompt/ubst-rlasm-buildings-2026-10-07/live-work-v002
```

Use a new version and output directory for every changed candidate. The build
refuses to overwrite an existing candidate. A completed package includes exact
sources, scripts, prework manifest, authoring Blender file, optimized GLB,
21 actual-GLB review renders, phone boards and deterministic evidence.

Version 001 is preserved with its failed visual review. Version 002 corrects
public studio entrances, upper window alignment, the side entrance position,
continuous gable cladding, bathroom camera occlusion and matched phone views.
It passes deterministic delivery verification and all 171 sampled centreline
floor/headroom probes. The delivered file is 2,072,236 bytes, 12 meshes and
41,304 triangles, with zero measured export/reimport bounds drift. These counts
are not a browser performance measurement or runtime acceptance.

## Acceptance boundary

Delivery checks and source review do not approve visual fidelity. Full-resolution
builder review and a separate holistic review must be recorded. CityPrompt
placement, walking, persistence, terrain and performance remain untested until
the candidate is trialled. Runtime activation and publication are separate
decisions. No push is authorized by this generation request.

## Round checkpoint

External deliverables are retained at
`C:/dev-artifacts/CityPrompt/ubst-rlasm-buildings-2026-10-07/`.
Open `round-overview.png` or `index.html` there for reference/model comparisons.
The synchronized JSON companion records exact candidate hashes and decisions.
All four listed models passed separate holistic architectural-clay review with
zero unresolved P0/P1 blockers. Each independent record identifies the exact
GLB and all 28 inspected images (three references, 21 views and four boards).
This approves the geometry-stage presentation only; runtime and textured keeper
approval remain false.

| Family | Candidate directory | Triangles | GLB bytes | Sampled floor/headroom probes |
|---|---|---:|---:|---:|
| Live/work townhouse row | `live-work-v002` | 41,304 | 2,072,236 | 171 |
| Student courtyard residence | `student-v004` | 34,826 | 1,780,968 | 52 |
| Timber co-housing terrace | `timber-v003` | 34,360 | 1,754,572 | 116 |
| Garden hotel | `hotel-v005` | 36,846 | 1,911,024 | 57 |
| Neighbourhood courtyard block | `courtyard-source-blocked` | — | — | — |

The four generated models contain actual openings, rooms and stairs. Each has
21 views rendered from its exported GLB, four comparison/construction boards,
source and script hashes, delivery checks, and offline circulation evidence.
The 396 prescribed samples passed floor support and 1.85m vertical clearance;
they do not test continuous body collision or establish building-code compliance.

The courtyard block remains source-blocked. Four bounded top-view attempts
contradicted the front/oblique references in courtyard elevation or floor count.
Exact originals, prompts, rejection reasons and hashes are preserved externally.
No mixed-reference model was constructed. Resolve a coherent reference set
before another generation batch for this family.

Earlier failed candidates remain unchanged beside the latest candidates. In
particular, `timber-v002` accidentally carried an internal v001 label; it was
preserved, superseded by correctly identified v003, and the batch runner now
requires an explicit version. Other corrections include real public entrances,
unblocked stairs, window frame contacts, roof/wall contacts and review framing.

Source changes are confined to this initiative's builders, tests, provenance,
12 original reference PNGs and documentation. Original PNGs use existing Git
LFS rules. GLBs, Blender files, failed attempts and QA images remain in the
external artifact directory; a source-only Git checkpoint does not back them up.
No seed, catalogue activation, frontend or backend behavior was changed.

The next production stage is source-conditioned materials and landscape polish,
another complete independent visual review, then an isolated CityPrompt trial
covering placement, walking, save/reload and performance. These geometry-stage
models must not be represented as finished textured keepers.

For the other three generated families, use the explicit bounded runner:

```powershell
blender -b --python tools/ubst_rlasm_buildings/batch_build.py -- student --version 5 --output C:/dev-artifacts/CityPrompt/ubst-rlasm-buildings-2026-10-07/student-v005 --dry-run
```

Replace `student` with `timber` or `hotel` as needed, choose a fresh version and
directory, then omit `--dry-run` to build. Rebuilding an approved candidate under
changed bytes invalidates its approval; always review a new version separately.
