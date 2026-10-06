# Five original catalogue studies — 6 October 2026

This initiative creates original reference images, metadata and source-locked
RLASM v6.1 architectural-clay models for five missing dedicated programmes.
These are new fictional designs. They are not photographs of real Calgary
properties, surveyed buildings or replacement references for existing models.

| Design | Programme | Design character |
| --- | --- | --- |
| Prairie Fold Manufactured Home | Manufactured Home | Cedar and charcoal; one longitudinal gable and a modest porch |
| Copperline Municipal Works Depot | Municipal Works Depot | Four service bays, copper fascia and a lower dispatch wing |
| Folded-Roof Materials Recovery Hall | General Industrial — Light, conditional on operations | Enclosed dry-recyclables hall with three roof teeth |
| Corten & Timber Equipment Yard | Storage Yard | Screened usable equipment and material storage with ancillary servicing |
| Meadow Court Childcare Centre | Child Care Service | Three timber gables, a veranda and a secure play courtyard |

The selection audit compared the primary catalogue and current zoning
programme inventory. It found no dedicated named reference set for these
five programmes. This is not a claim that every old photograph was visually
inspected or that no existing building could be adapted to these uses.

## Files and authority

- `designs.json`: authored programme, dimensions, search/style tags, exact
  Calgary use definitions, candidate districts and remaining conditions.
- `plan.py`: refuses changed sources, LFS pointers, missing roles and
  undeclared extra reference views.
- `capture_reference.py`: copies generated originals unchanged and records
  prompts, input roles, image dimensions, byte size and SHA-256.
- `build.py`: new source-specific geometry and proof cameras. Shared
  `clay_core.py` supplies primitive geometry and delivery machinery; no
  unrelated building family is relabelled.
- Each new `frontend/public/archetypes/buildings/<slug>/` contains three
  locked reference images and `generation-provenance.json`.
- Heavy Blender output, exported GLBs, actual GLB reimport renders, boards,
  review records and local gallery live under
  `C:/dev-artifacts/CityPrompt/rlasm-original-five-2026-10-06`.

The generated pixels govern visible topology. Metric dimensions are authored
design assumptions and are reconciled to the images where needed. Unseen
interiors, rear details and structures are explicitly inferred. Each model
has one fixed authored storey programme; arbitrary vertical stretching is
not supported. Render lights and cameras are excluded from the GLB.

## Review sequence

The manufactured home is the pilot. Run source validation and a dry run,
build it, compare all original images, correct a finite blocker list, and
obtain a separate holistic visual review before the bounded four-model
scale-up. Preserve every version and its review. Do not approve by counts,
file size, a contact sheet alone, or a successful export.

Every delivered candidate requires complete baseline and detail renders,
phone comparison boards, unchanged source/script hashes, canonical
preflight checks and a fresh independent review with no unresolved P0/P1
defects. The proof images are rendered from the actual optimized GLB after
reimport. Contact sheets only letterbox and label those unchanged images.

Example commands, from this worktree:

```powershell
python tools/catalogue_original_five/plan.py --kind home --source-root .
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python-exit-code 1 --python tools/catalogue_original_five/build.py -- --kind home --source-root . --output C:/dev-artifacts/CityPrompt/rlasm-original-five-2026-10-06/home-dry-run --dry-run
python -m pytest tools/archetype_compiler/tests/test_original_five_sources.py -q
```

Builds require a fresh external output folder. Review preparation uses the
unchanged `tools/catalogue_zoning_five/prepare_review.py`. The canonical
validator is the RLASM skill's `scripts/validate_candidate.py`.

## Limits of this delivery

Architectural clay establishes geometry, real apertures, roofs, supports and
programme. Final source-conditioned textures, live catalogue activation and
student runtime acceptance are separate steps. No model in this initiative
is a textured keeper or a demonstration of classroom performance.

Candidate use routes are teaching metadata, not zoning approvals. In
particular, the equipment-yard asset is much smaller than the I-O minimum
parcel; recycling remains conditional on fully enclosed operations; the
manufactured home needs specialist certification; and the childcare asset
needs three drop-off spaces in the surrounding site design. DC is never
assigned automatically. Height relaxation and redesignation require their
own planning review.

The seed catalogue, project databases and hosted application are unchanged.
No publication is authorized by this package. The existing Wave 1/Wave 2
human-review gates and canonical RLASM method/policy files remain unchanged.

## Local review gallery

All five selected candidates passed fresh independent architectural-clay
review with zero unresolved P0/P1 blockers:

| Design | Selected external folder | Review scope |
| --- | --- | --- |
| Prairie Fold Manufactured Home | `home-v003` | Architectural clay |
| Copperline Municipal Works Depot | `depot-v003` | Architectural clay |
| Folded-Roof Materials Recovery Hall | `recovery-v002` | Architectural clay |
| Corten & Timber Equipment Yard | `yard-v002` | Architectural clay |
| Meadow Court Childcare Centre | `childcare-v003` | Architectural clay |

`checkpoint.json` records their exact GLB/review hashes, source inventory and
verification results. The selected evidence includes 87 original model
renders, 15 unchanged source images and 20 comparison/construction boards.

`gallery.py` packages the exact reviewed GLBs, unchanged original references,
model views, metadata, prompts and independent review records. It refuses a
missing/failed review, unresolved P0/P1 issue, incomplete image inspection or
changed evidence hash. It does not activate catalogue entries.

```powershell
python tools/catalogue_original_five/gallery.py --batch-root C:/dev-artifacts/CityPrompt/rlasm-original-five-2026-10-06 --output C:/dev-artifacts/CityPrompt/rlasm-original-five-2026-10-06/gallery-v001
python -m http.server 8793 --bind 127.0.0.1 --directory C:/dev-artifacts/CityPrompt/rlasm-original-five-2026-10-06/gallery-v001
```

Open `http://127.0.0.1:8793/` on this computer. The saved `index.html` also
opens locally with its sibling asset folders. Each card links to original
reference views, roof/rear/interior model renders, the comparison and
construction boards, full metadata and the GLB download. District-specific
conditions remain visible alongside permitted/discretionary classifications.

Browser verification passed at the normal desktop width and 390px phone
width. All ten page images loaded, anchor navigation and the childcare
metadata disclosure worked, and neither layout overflowed horizontally.
All 65 local asset endpoints returned successfully; all five downloaded GLBs
matched their reviewed hashes. Screenshots and `verification.json` are in
the external gallery folder. The browser viewport was restored afterward.

Source verification and narrow compiler checks pass: **18 tests** across
`test_original_five_sources.py`, `test_rlasm_method.py` and
`test_rlasm_delivery_contract.py`. The existing pytest-asyncio fixture-scope
deprecation warning remains. No frontend production code changed.

Source changes consist of this initiative's scripts/metadata, its source-lock
tests and the five new reference folders. PNGs follow existing Git LFS rules.
Blender scenes, GLBs, QA renders, boards and failed/superseded candidates stay
in external artifact storage. Nothing from the earlier batches is staged or
modified by this initiative.
