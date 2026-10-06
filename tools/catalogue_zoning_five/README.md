# Five zoning-gap building studies — 2026-10-05

Finite RLASM v6.1 architectural-clay batch for the five reference-backed
archetypes selected in this session. Three models were authored here. Two
existing exact-variant clay models were recovered unchanged and received a
fresh independent holistic review, including the shed pilot before new builds.
This is a model-review checkpoint, not a runtime catalogue expansion.

## Roster and exact outputs

Generated artifacts stay outside Git. Batch root:
`C:/dev-artifacts/CityPrompt/rlasm-five-zoning-gaps-2026-10-05`.

| Study | Exact variant | Candidate | GLB MB / triangles |
| --- | --- | --- | --- |
| Industrial shed | `industrial_gabled_metal_shed` | Revalidated `industrial-gabled-metal-shed-clay-v002` | 1.23 / 24,280 |
| Classic retail strip | `strip_single_storey_classic` | Revalidated `commercial-strip-single-storey-classic-clay-v002` | 1.53 / 32,894 |
| Neoclassical office | `neoclassical_brick_headquarters` | New `office-v004` | 3.80 / 65,316 |
| RNDSQR contextual townhouses | `rndsqr_townhome_brick_contextual` | New `row-v004` | 2.02 / 39,554 |
| Provincial Brick school | `ecole-republicaine-provincial-brick` | New `school-v004` | 3.34 / 62,864 |

The two revalidated models remain at their original paths:

- `C:/dev-artifacts/CityPrompt/2026-09-02_clay-eight-10h/08-corrugated-vernacular-industrial/v002`
- `C:/dev-artifacts/CityPrompt/2026-09-02_clay-eight-10h/07-commercial-strip-mall/v002`

Current independent decisions are retained under the batch root's
`independent-review/`, one report per exact version. The gallery reads those
decisions rather than inferring approval from generation success. Each report
identifies the model hash and the images actually inspected. A clay pass is
limited to the fixed native-scale architectural-clay representation.

All five exact candidates above received `PASS_ARCHITECTURAL_CLAY_ONLY` with
zero unresolved P0/P1 findings. The delivered comparison gallery is
`gallery-v001/index.html` under the batch root. Independent review covers the
complete sources, render sets and phone boards, rather than selected hero views.

## What is built

`build.py` constructs family-specific whole envelopes, roofs, physical wall
openings, recessed optical panes, rooms and stairs using the existing
`catalogue_services_batch/clay_core.py`. It exports the model and reimports
that exact GLB for the complete review camera set. QA lights, cameras and
background are excluded from the GLB. Models have no textures or external
buffers. Runtime meshes are consolidated by material.

The three new candidates retain 17 / 17 / 19 mandatory views respectively,
source manifests, complete source bytes, build scripts, Blender authoring
files, carrier-aperture audits, full-resolution renders and phone boards.
Source and model hashes, grade, finite geometry and GLB roundtrip bounds are
checked. The microbevel helper is disabled in this bounded clay builder to
avoid costly per-object modifier work; authored silhouette and opening depth
remain real geometry.

The office has two occupied floors, a four-column portico, stone roof
balustrade and glazed cupola. Fine pediment carving and planting are simplified.
The townhouses contain four units, three full floors, roof access rooms and
connected roof stairs; the ground-floor corner studio's use remains provisional.
The school has three occupied floors around an open court, a high unoccupied
front roof bridge, a separate arched gate and a clock/bell lantern.

The school references conflict: the aerial defines the roof graph and dormer
positions, while the front defines curved dormer heads and standing seams.
This reconciliation is disclosed in the source contract and independent review.
All absolute dimensions, hidden elevations and room layouts are inferred from
uncalibrated design references, not surveyed photographs or approved plans.

## Reproduce a bounded build

Run from the repository root with Python 3.12, Pillow, trimesh and Blender 5.2.
The primary checkout has hydrated reference images; a new worktree may contain
only LFS pointers, which the source preflight rejects.

```powershell
python -m tools.catalogue_zoning_five.plan --source-root 'C:/Users/andre/OneDrive/Documents/CityPrompt'

# A fresh version/output directory is required; never overwrite a candidate.
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python-exit-code 1 --python tools/catalogue_zoning_five/build.py -- --kind office --source-root 'C:/Users/andre/OneDrive/Documents/CityPrompt' --output 'C:/dev-artifacts/CityPrompt/rlasm-five-zoning-gaps-2026-10-05/office-v005' --version 5

# After build-report.json and every render exist:
python -m tools.catalogue_zoning_five.prepare_review 'C:/dev-artifacts/CityPrompt/rlasm-five-zoning-gaps-2026-10-05/office-v005'
python 'C:/Users/andre/.codex/skills/rlasm-expert/scripts/validate_candidate.py' 'C:/dev-artifacts/CityPrompt/rlasm-five-zoning-gaps-2026-10-05/office-v005'
```

Use `--kind row` or `--kind school` for the other new models. Preflight alone
does not approve visual fidelity. A separate verifier must inspect every
source, full-resolution view and phone board for each changed candidate.

Once independent reports exist, assemble an offline comparison gallery into a
fresh directory:

```powershell
python -m tools.catalogue_zoning_five.gallery --batch-root 'C:/dev-artifacts/CityPrompt/rlasm-five-zoning-gaps-2026-10-05' --output 'C:/dev-artifacts/CityPrompt/rlasm-five-zoning-gaps-2026-10-05/gallery-v001' --office office-v004 --row row-v004 --school school-v004
```

The gallery copies original images unchanged and verifies hashes against
independent evidence. Its manifest records exact candidates, model hashes and
review decisions. It contains no runtime catalogue mutation or cloud upload.

## Preserved revision history

Interrupted office/row v001 and the school v001 grade assertion remain external.
The completed v002 candidates and failed review records remain unchanged.
V003 corrected the main source-identity and enclosure findings, but independent
review still found office stair guards/evidence, townhouse corner returns/roof
arrival, and school rear roof closure/stair evidence issues. V004 addresses
those findings and rerenders the complete evidence sets. No failed version was
overwritten or relabelled as passed.

## Checks and remaining acceptance

Narrow source/preparation tests and the canonical RLASM contract tests:

```powershell
python -m pytest tools/archetype_compiler/tests/test_zoning_five_sources.py tools/archetype_compiler/tests/test_rlasm_method.py -q
python -m compileall -q tools/catalogue_zoning_five
git diff --check
```

The three v004 candidates pass delivery checks and canonical deterministic
preflight. Builder visual records are separate from independent decisions.
Each new candidate retains `evidence/runtime-review.md` with the full runtime
checklist explicitly **NOT TESTED**.

Final focused verification: 10 tests passed; Python compilation passed. The
offline gallery was opened in connected Edge on 2026-10-06: all 10 source/model
images loaded, the school comparison link opened at 1080 x 1920, and the
captured browser log contained no warnings or errors. The browser CLI and
in-app browser were unavailable, so the connected Edge tool supplied this
visual check. This checked the review gallery, not City Prompt runtime.

Human aesthetic review, catalogue mapping, native-scale student placement,
terrain/entrance handling, editing and persistence, browser capture, and
classroom performance remain separate work. Final source-conditioned textures,
arbitrary resizing, legal zoning permission and a textured keeper decision are
not established by this batch. Model byte size is not a performance test.

No frontend/backend production files, reference originals, seed records or
database records changed. Source work is isolated on
`codex/rlasm-five-zoning-gaps-2026-10-05`. No commit, push or deployment was made.
