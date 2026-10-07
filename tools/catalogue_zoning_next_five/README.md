# Next five zoning-gap building studies — 2026-10-06

Finite RLASM v6.1 architectural-clay batch following the previous five studies.
Four new source-specific constructors and one correction of an existing exact
warehouse envelope. This source folder does not install models, change zoning
matches, update the database, or publish the application.

Generated output and independent review records are external:
`C:/dev-artifacts/CityPrompt/rlasm-next-five-zoning-gaps-2026-10-06`.
The source/reference gate is `reviews/five-source-gate-2026-10-06.json`.

| Kind | Exact variant | Programme |
| --- | --- | --- |
| `tiltup` | `industrial_tilt_up_concrete` | Two-level office strip within a high industrial hall |
| `factory` | `factory_sawtooth_roof` | Single industrial hall, glazed roof teeth and chimney |
| `warehouse` | `warehouse_tilt_wall_mega` | One high warehouse with three local office levels |
| `admin` | `admin_faculty_brick_bronze_fins` | Five occupied office storeys and roof plant |
| `peaks` | `rndsqr_townhome_scandinavian_peaks` | Six front homes, three complete storeys plus an occupied gabled fourth level |

The factory sources conflict: front and oblique show seven roof teeth, while
the top view shows six bands. Seven follows the two exterior views; the top
view still governs orientation and depth. This is a disclosed interpretation,
not a contradiction-free photographic reconstruction. The townhouse overhead
also contains three separate rear roof pavilions; these are retained as
inferred service rooms. Absolute dimensions and hidden interiors are inferred
from generated design references, not surveyed existing buildings.

## Review boundary

The tilt-up building is the pilot. Each correction receives a new external
version. Earlier candidates and the old warehouse remain untouched. The old
warehouse v003 failed fresh independent review because its office stair
intersected the rear partition and lacked complete supported/guarded arrivals.
`warehouse.py` preserves its envelope while rebuilding the circulation.

Pass/fail decisions belong to the exact external independent review record,
never to a constructor or a successful export. Source and GLB hashes, complete
renders of the reimported GLB, source comparisons, phone construction boards,
carrier aperture audits and runtime acceptance checklists accompany candidates.

No textured-keeper or runtime activation is implied. Student placement,
terrain, editing, persistence, walking and classroom performance remain
**NOT TESTED** for this batch. Models retain fixed native dimensions; no mesh
stretching, arbitrary resizing or automatic legal-use approval is allowed.

## Bounded reproduction

Run from this worktree with Python 3.12, Pillow, trimesh and Blender 5.2. The
primary checkout contains hydrated reference images; LFS pointers are rejected.

```powershell
python -m tools.catalogue_zoning_next_five.plan --source-root 'C:/Users/andre/OneDrive/Documents/CityPrompt'

# Use a fresh output directory and version. Never overwrite an earlier model.
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python-exit-code 1 --python tools/catalogue_zoning_next_five/build.py -- --kind factory --source-root 'C:/Users/andre/OneDrive/Documents/CityPrompt' --output 'C:/dev-artifacts/CityPrompt/NEW-BOUNDED-BATCH/factory-v001' --version 1 --dry-run

# After an authorized build is complete, assemble unchanged evidence:
python -m tools.catalogue_zoning_five.prepare_review 'C:/dev-artifacts/CityPrompt/NEW-BOUNDED-BATCH/factory-v001'
python 'C:/Users/andre/.codex/skills/rlasm-expert/scripts/validate_candidate.py' 'C:/dev-artifacts/CityPrompt/NEW-BOUNDED-BATCH/factory-v001'
```

`build.py` snapshots its source, `plan.py`, `warehouse.py` and the unchanged
shared clay core into every candidate. Fine object microbevels are outside the
clay profile; openings, roof topology, supports, joinery and circulation remain
physical geometry. Geometry is consolidated by material, exported to GLB and
reimported unchanged for every review render. QA lights, cameras and backdrop
are excluded from the GLB.

The gallery packages copies of original evidence images without retouching.
It verifies the exact reviewed GLB hash and every reviewed image hash before
writing a fresh gallery directory.

## Delivered clay candidates

| Model | External directory | Triangles | GLB size | Original review views |
| --- | --- | ---: | ---: | ---: |
| Tilt-up industrial | `tiltup-v004` | 14,706 | 0.73 MB | 17 |
| Sawtooth factory | `factory-v003` | 40,820 | 2.19 MB | 17 |
| Tilt-wall warehouse | `warehouse-v004` | 25,868 | 1.31 MB | 17 |
| Brick-and-bronze faculty office | `admin-v003` | 48,682 | 2.41 MB | 16 |
| Scandinavian townhouse row | `peaks-v003` | 69,452 | 3.74 MB | 19 |

Each directory contains a GLB, authoring file, immutable source-code snapshot,
source manifest, deterministic delivery checks and the original render evidence.
External `reviews/` contains separate builder and independent review records,
including failed earlier versions. Build reports retain their original pending
review fields: the later, hash-linked review records are the decision authority.

All five final candidates passed independent holistic architectural-clay review
with zero unresolved P0/P1 blockers. The reviewer inspected 121 images at their
original resolution: 15 sources, 86 mandatory model views and 20 review boards.
This closes the clay review only; final material work and City Prompt acceptance
remain separate. No models were installed or published.

`gallery-v001/index.html` presents original source/model pairs, roof and rear
views, construction boards, exact independent reports and downloadable GLBs.
It was checked in Edge: five cards, all ten comparison images loaded, the
townhouse full-size link worked, no horizontal overflow and no console errors.
Browser screenshots are retained alongside it. This checks the review gallery,
not City Prompt runtime behaviour or laptop performance.

Validation: all five passed the deterministic candidate/delivery checks.
The source-lock and RLASM regression suite passed **16 tests**, and all four
batch Python modules compiled. No production TypeScript or backend service code
changed. Generated models, images and review records remain outside Git.

```powershell
python -m pytest tools/archetype_compiler/tests/test_zoning_next_five_sources.py tools/archetype_compiler/tests/test_zoning_five_sources.py tools/archetype_compiler/tests/test_rlasm_method.py -q

# Run only after the five exact candidate reviews are complete.
python tools/catalogue_zoning_next_five/gallery.py --batch-root 'C:/dev-artifacts/CityPrompt/rlasm-next-five-zoning-gaps-2026-10-06' --output 'C:/dev-artifacts/CityPrompt/rlasm-next-five-zoning-gaps-2026-10-06/gallery-v001'
```
