# Five community buildings — local trial

This bounded batch adds five exact variants using RLASM 6.1 architectural-clay
geometry. Existing front, oblique and top references own each design. Catalogue
cards retain the realistic reference images. The models have physical openings,
interiors, complete envelopes and native dimensions; they are untextured clay,
not photorealistic or engineering-certified buildings.

| Catalogue name | Exact variant | Programme | Storeys |
| --- | --- | --- | --- |
| Brick Corner Grocery | `montreal_depanneur_modern` | Grocery and one dwelling above | 2 |
| Clerestory Neighbourhood Hall | `rec_clerestory_modern` | Community recreation and meetings | 1 |
| Log Recreation Cabin | `rec_log_cabin_vernacular` | Day-use recreation shelter | 1 |
| Inglewood Corner Merchants | `inglewood_deco_infill` | Retail and upper offices | 2 |
| Prairie Neighbourhood Shops | `strip_weathered_1980s` | Deli, hardware, liquor and gifts | 1 |

The complete native envelope includes balconies, roof rooms, signs and steps.
Plot dimensions come from that envelope plus clearance. Enlarging a plot must
not stretch the building. Floor counts are fixed for these exact models.
Concealed layouts, dimensions and occupancies are explicit teaching assumptions
in `tools/community_buildings_five/plan.py` and `buildingPrograms.json`.
The liquor tenancy remains **needs review** because it is not in the researched
district-use snapshot. The other uses reuse the existing screening rules;
permitted/discretionary results remain subject to site-specific rules.

## Evidence and lifecycle

Source, build and complete reimport-render evidence lives outside the checkout:
`C:/dev-artifacts/CityPrompt/community-buildings-five-2026-10-07/`.
Every version is immutable, including rejected versions. The grocery pilot was
reviewed and installed before scaling to the other four designs. The independent
reviewer is separate from the builder. Exact accepted model hashes and reviews
are copied into `seed/model-library/rlasm-architectural-clay/`.

These are local catalogue trials. Independent architectural-clay review does
not grant human keeper, textured fidelity, full runtime or publication approval.
No paid image provider was used. No production service was changed.

## Runtime review scope

Review project: `http://127.0.0.1:5181/projects/d7eb67d6-11a5-41ad-84d8-c48872fbb465`
(Community buildings · five new designs). This is a separate vacant-field site
near Range Road 284, approximately 185 × 140 m. Its boundary and location are
visual test fixtures, not surveyed data. Browser viewport: 1280 × 720, mouse and
keyboard. Ground mode: clear site for redevelopment.

The grocery pilot was placed through ordinary controls, enlarged to 20 × 20 m,
rotated 15 degrees, undone, redone and reloaded. Its native proportions and
saved binding persisted. A shared lane and reading garden form the mixed-scene
pilot. Ordinary Walk produced a close exterior view; sustained traversal through
doors and up every staircase is **not verified**. No walking code was changed.

The free exact 3D capture produced a preview. Download completion was not proved
(the browser download attempt timed out); `pilot-export-browser.png` records
the preview only. It must not be counted as a full export-delivery pass.

Full C1–C9/B1–B5 certification remains open. In particular: natural/sloped and
exposed-edge sites, approach authoring, multi-entrance street recovery, touch
input, adverse-network recovery, and a fresh empty DB/bucket installation have
not been tested. The new models reuse the existing walk and placement systems.
Road/public-network connections and accessible routes are student design work.

## Entrance inventory

Coordinates below use the author's Blender frame: X right, Y rear, Z up,
metres, base Z=0. They are nominal opening dimensions; frames reduce clear
passage. They are **not** installed automatic approach anchors. Delivered GLB
axis conversion and placement centring must be applied before authoring anchors.

| Model | Entrances and connections |
| --- | --- |
| Grocery | Corner shop at (4.775, -5.275, .16), 1.48 m opening; residence at (-4.65, -6, .16), 1.05 m; rear service at (0, 6, .16), 1.20 m. Internal 22-step flight joins upper floor at 4.10 m. |
| Hall | Main lobby at (-9.5, -6, .16): 3.80 m glazed assembly with narrower active leaf; rear exit at (0, 15, .16), 1.50 m assembly. Open internal passages connect the hall and low wing. |
| Cabin | Front door (0, -4, .575), 1.12 m; porch edge Y=-6.5, three 0.31 m treads, 2 m width. Rear door (0, 4, .575), 1.05 m; 1.2 m landing and three 0.31 m treads, 1.7 m width. |
| Inglewood | Front (0, -8, .17) and side (7, 0, .17), 3.30 m assemblies with central active leaf/sidelights; rear (0, 8, .17) and left (-7, 0, .17), 1.25 m service openings. Upper balconies and roof service door are not grade entrances. |
| Shops | Four single-leaf 1 m openings at X=-10.35, -2.85, 4.65, 12.15; Y=-11, Z=.15. Four inferred 1.1 m rear service openings at X=-11.25, -3.75, 3.75, 11.25; Y=11, Z=.15. |

## Reproduction and local installation

Build one immutable candidate at a time with Blender 5.2, using
`tools/community_buildings_five/build.py -- --kind <kind> --version <n>
--source-root <hydrated-repository> --output <external-new-directory>`.
Start with `--dry-run`. Generate boards with
`python -m tools.catalogue_zoning_five.prepare_review <candidate>`; run the
RLASM skill validator and obtain a fresh independent holistic review.
Do not reuse a failed candidate directory or relabel its review.

Package and preview with `package_trial.py <kind> <candidate>` and
`python -m tools.catalogue_promotion trial <candidate>/trial-package.json`.
Only after the reviewed package passes, apply the local trial and add its exact
identity to `frontend/src/data/communityBuildingBatch.json`.

`install_local.py` uses the backend's existing loopback DB/storage configuration
and supports dry-run (default), `--apply`, and `--verify`. Set
`MODEL_LIBRARY_SEED_OWNER_ID` to an existing local account; never copy secrets
into source. It accepts only this batch's registered candidates. Run
`verify_runtime.py --user-id <local-user> --project-id <test-project>
--output <external-report.json>` to verify authenticated native plans and
downloaded GLB hashes. This script does not prove browser walking or terrain.

## Checks

Final check results and browser observations are recorded alongside this file
in `COMMUNITY_BUILDINGS_FIVE_2026-10-07.json`. Heavy rendered images, source
copies, Blender files and logs remain external. Intentional model deliverables
use Git LFS. Unrelated runtime-guard work is preserved and excluded from this
initiative's commit. No push is authorized for this batch.
