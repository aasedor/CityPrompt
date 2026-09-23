# Two more models before the combined Sol trial

User direction: build a few more models with Astra, then test the combined batch
with Sol. Work stays in `C:/dev/CityPrompt-grounding-edit-race` on
`codex/astra-catalogue-models`. No browser trial, database seeding, paid image call,
catalogue activation or publication is performed in this phase.

## Finite batch

| Model | Exact identity | Purpose |
| --- | --- | --- |
| Timber community hall | `community_recreation_centre / rec_centre_timber_hall` | Civic gathering use; pitched timber hall and wraparound veranda. |
| Tilt-wall warehouse | `modern_bigbox_warehouse / warehouse_tilt_wall_mega` | Industrial/employment use; high-bay warehouse, freight docks and separate corner office. |

Both are existing expansion-plan nominations. They are brought forward while the
townhouse and timber-apartment references remain unresolved. This does not replace
the two pending housing slots or count the starter catalogue as complete.

Sources: exact `variant_1.png`, `variant_1_angle_60.jpg` and
`variant_1_angle_90.jpg` in each authoritative building directory. All six images
were inspected before construction. Only the main building is modeled: surrounding
streets, trucks, yards, guardhouse, mature trees and play equipment are context.

Replay: `tools/catalogue_services_batch/`. Dry runs validated both three-image
source sets and fourteen-view camera rosters before geometry. Heavy assets and
complete evidence remain externally under
`C:/dev-artifacts/CityPrompt/services-model-batch-2026-09-22/`.

## Integration constraints for Sol

- Keep full native dimensions, including veranda, roof overhangs, canopy and
  mechanical equipment. Do not derive fit from parent catalogue suggestions.
- Hall: connect to the paired public door through the veranda. Verify the 0.2 m
  raised slab against actual terrain and approach; no accessible-route claim yet.
  Rear fenestration, stage, tables/chairs and service room are inferred.
- Warehouse: one high-bay industrial storey with a local three-level office.
  The 1.2 m dock thresholds are freight access, not sidewalk destinations.
  Main office entrance is on the front-right glazed corner. Interior shelving,
  office circulation and partially occluded dock count are inferred.
- The warehouse is a large industrial building. Use a separate disposable Currie
  test layout if its full envelope cannot fit the mixed-neighbourhood layout.
  If even the parcel cannot fit it, report incompatibility rather than shrinking
  the building or letting it cross roads. Do not disturb protected projects.
- Shared paths, landscaping exclusion, move/rotation, resize, Undo/Redo, reload
  and exact export remain NOT TESTED for both models.

Follow the [combined Astra-to-Sol handoff](ASTRA_MODEL_BUILD_SOL_HANDOFF_2026-09-22.md)
for the trial process. Review status and exact hashes are recorded at the final
checkpoint below. Model review alone is not classroom/runtime acceptance.

## Bounded correction history

Hall v001 exposed timber braces through the main roof and oriented side-gable
seams across the slope. Hall v002 seats the frames below the weathering skin and
aligns those seams downhill. The complete v001 package and builder findings remain
preserved; v002 delivery checks and skill preflight pass.

Warehouse v001 inherited house-scale QA lighting that sat near/inside its much
larger roof. Its side service exits also disagreed with the raised goods floor.
V002 scales the neutral inspection environment and provides grounded service
stairs. V002 delivery checks pass, but the close view exposed canopy posts ending
0.3 m above grade and an insufficiently distinct public door. V003 adds grounded
plinths, paired entry handles/transom and seated approach steps. All earlier
candidates and findings are retained externally; none is silently relabelled.

These checks apply to future archetypes too: measure the complete envelope before
placing review lights; distinguish freight, public and service thresholds; inspect
post feet in close views; and carry roof-seam direction through each separate
slope. The batch code and records capture these applications without changing
the canonical RLASM method or granting automatic runtime approval.

## Reviewed hall checkpoint

- Package: `hall-v002/timber-community-hall-clay-v002.glb`.
- Model SHA-256: `72ae51df5f50e350fc509286e14b23d5fabc286af5d6f53dc112adea296e6ea4`.
- 1,234,044 bytes; 21,280 triangles; ten meshes/materials; no textures/images.
- Complete dimensions: 16.4 × 20.4 × 9.65 m. Suggested starting test plot: 20 × 24 m.
- Independent review: `hall-v002-review.json`, SHA-256
  `f8637a06ee87851b4e927ad7bc8e8fe145b8bdca4dd4008bb0cece79553f19c7`.
- Zero P0/P1 after all fourteen individual renders, three sources and four boards.
  Canonical review validation passes. Ready for a local Sol trial only.

## Warehouse delivery checkpoint

- Package: `warehouse-v003/tilt-wall-warehouse-clay-v003.glb`.
- Model SHA-256: `1350d1d48d055fe351aee6a4b832be49fa63bef9edc243e78fbf4b7e7a2561c4`.
- 3,824,844 bytes; 56,548 triangles; ten meshes/materials; no textures/images.
- Complete envelope: 150.320007 × 89 × 16.35 m. The main wall footprint is
  144 × 86 m; use the larger complete envelope for fit and exclusion.
- Delivery audit and skill preflight pass. Builder inspected all fourteen
  individual final renders and all four boards; no unresolved P0/P1 found.
- Public office approach remains 0.3 m above native grade; freight docks are
  1.2 m above grade. Runtime terrain and pedestrian connections remain untested.

## Combined test batch

The next Sol session covers the Calgary duplex, Montreal stacked duplex, brick
courtyard building, timber community hall and tilt-wall warehouse. Test each
individually before the mixed neighbourhood exercise. The industrial model needs
its own suitable parcel-fit check, not forced placement in the housing layout.
The model-building stage makes no classroom-readiness claim until these runtime
checks and exact export succeed.

Independent warehouse review: `warehouse-v003-review.json`, SHA-256
`e1b9bc71b856700a75cec6281032cef8440105514a07bba2ab9c18309ac5721f`.
All fourteen renders, three exact sources and four boards inspected. Zero P0/P1;
canonical review validation passes. Both additions are ready for local Sol runtime
trials, with no runtime activation or textured-keeper approval implied.
