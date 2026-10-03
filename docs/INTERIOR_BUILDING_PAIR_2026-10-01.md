# Art school and courtyard hotel interiors

Two local RLASM v6.1 architectural-clay pilots extend the library and station
interior work. They use exact existing catalogue references and the shared
version 2 building walking system. The primary checkout, earlier park work and
street assets are preserved.

## Buildings

| Building | Occupied levels | Explore | Native footprint / plot |
| --- | --- | --- | --- |
| Timber Art & Design School | 4 | Exhibition gallery, easels and painting tables, pottery wheels and kiln, critique lounge and planted roof terrace | 36 x 30 m / 40 x 34 m |
| Mediterranean Courtyard Hotel | 3 | Concierge lounge, furnished guest suites, courtyard fountain, upper galleries, open loggia and pool promenade | 40 x 36 m / 44 x 40 m |

The school is `university_academic_complex / biophilic_mass_timber_campus`.
The hotel is `boutique_hotel / mediterranean_resort_courtyard`. Catalogue search
uses their displayed titles; their groups are Schools, civic & recreation and
Hotels & visitor accommodation.

Each complete assembly retains its native dimensions. Plot resizing does not
stretch its rooms or stairs. Internal stairs rise 3.6 m per storey using 22
risers of about 0.164 m, below the existing 0.20 m walking step limit. Visible
floor and tread faces supply the navigation triangles. Walls, furniture,
planters, railings and the hotel pool have explicit collision boundaries.

## Reference and scope

The three existing references for each exact variant lock exterior identity.
Interior rooms, furnishings and circulation are authored interpretations. The
hotel top view defines roof apertures where the oblique source conflicts; its
ground courtyard is an explicit interpretation. Plants and materials retain the
catalogue's simplified clay appearance. Artwork, pottery, fountain and pool are
static details; this adds walking exploration, not interactive hotel services
or art-making tools.

Both are prepared-level-site pilots. Natural terrain, external street approach
connections, accessibility design, touch input and the broader landscape/export
matrix remain separate tests. The result JSON and external runtime-review
records keep those cases explicit. No exhaustive movement guarantee is claimed.

## Verification and evidence

The companion JSON records exact model hashes, dimensions, independent review,
route checks and browser results. All 19 exported-GLB renders and three phone
comparison boards per final candidate require independent holistic review with
zero unresolved P0/P1 findings. The verifier sweeps a 0.44 m body along every
declared route in both directions and compares height against the exported mesh.
Registration separately rejects any blocked carrier-aperture ray. During the
hotel's final audit this caught an upper doorway crossing a perpendicular room
partition; the corrected candidate moves the entire opening clear of that wall.

[Build, verification and registration commands](../tools/interior_building_pair/README.md)
use immutable candidate folders under:

`C:/dev-artifacts/CityPrompt/interior-building-pair-2026-10-01/`

Rejected and interrupted candidates remain there. Only reviewed GLBs under Git
LFS, compact independent reviews, additive local registrations, scripts and
result documents belong in this source checkpoint. Human visual activation and
remote publication remain separate; these entries are local trials and their
completed-catalogue flags remain false.

[Open the local test project](http://localhost:5186/projects/aff432a5-63cf-4027-86f4-4841b6203b39).
Choose **Top View**, then **Walk** and click inside either building. The
**Return to building entrance** button provides a quick way back.

## Final checks

The retained versions are school `v003` and hotel `v006`. Both have independent
architectural-clay approval with zero P0/P1 findings. Their 6,152 route samples
pass on the actual exported geometry; another 194 samples check the corrected
hotel doorway in both directions. Every carrier-aperture ray passes.

The desktop browser checks cover all occupied levels in both directions,
furnished rooms after reload, Move/Undo/Redo, collision recovery and the entrance
return controls. The school rises 10.8 m and the hotel 7.2 m. Both retain their
exact model revision and moved coordinates after reopening the project.

Checks passed: 25 frontend tests, 38 backend clay-runtime tests, 24 catalogue
promotion/workflow tests, TypeScript type-check and Python compilation. Seven
historical clay-fixture tests were skipped because their separate historical
fixture was not configured. Exact final GLB storage readback passes, and all
37 current local Model Library objects are present.

Source changes contain the two generators/registration scripts, exact local
catalogue entries, independent reviews, result documents and two GLBs under
Git LFS. Blender scenes, review renders, rejected versions and browser records
remain in the external evidence directory. Shared walking/runtime code is
unchanged. No remote publication or push is included.
