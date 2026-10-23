# People wardrobe and inclusion — local delivery, 2026-10-23

Status: implemented and locally registered on `codex/inclusive-people-20261023`. No push, production publication, database migration or paid AI acceptance generation in this batch.

## What changed

The existing 23 stable People IDs now load versioned wardrobe GLBs matching their previously approved realistic picker outfits. Actual clothing geometry includes two dresses, a skirt, a jumpsuit, hoodies, knitwear, polo shirts, rugby stripes, plaid, shorts, tailoring and campus backpacks/accessories. The original GLBs and the existing 23 photo records remain unchanged. All 23 retain their 65-bone rigs, Walk/Idle clips and existing procedural action system; catalogue strides use measured revised geometry.

Eight additional People entries have matching realistic picker images and usable fixed-pose models:

| Model | Actual outfit / aid | Supported pose |
|---|---|---|
| Ava | Teal track jacket, white cane with grounded tip | Standing |
| Mateo | Camel hoodie, navy trousers, golden guide dog and harness | Standing |
| Maya | Coral knit top, detailed manual wheelchair | Sitting |
| Andre | Plum short-sleeve polo, cream trousers, powered wheelchair | Sitting |
| Clara | Sage coat and green trousers, older adult | Standing |
| Eli | Blue jacket, beige trousers, four-wheel rollator | Standing |
| Imani and child | Sand overshirt and taupe trousers; child in blue/navy | Standing together |
| Noah and baby | Navy/cream striped short-sleeve tee, sage trousers, stroller and infant | Adult standing; infant in stroller |

These entries share the existing detail placement, selection, rotation, copy, delete, undo/redo and serialization path. The UI exposes only their authored pose. Server-authoritative render directions preserve the aids, group person counts and infant placement. Static batches use shared consolidated geometry/materials; rigged actors retain independent pose resources. The preview ghost and saved model use the same people ground datum.

## Exact assets and provenance

`tools/people_pilot/people_model_delivery.json` is the complete 31-model inventory: stable ID, label, dimensions (width/depth/height, metres), URL, GLB bytes/hash, source thumbnail hash, action contract and 70 new publication-file hashes. Total GLB bytes: **43,623,736**. All 31 picker WebPs total **398,498 bytes**. The 70 new files are 31 GLBs, 31 truthful model thumbnails and eight new photos; the previous 23 photo URLs are retained.

Runtime assets are external to Git:

- `C:/dev-artifacts/CityPrompt/people-wardrobe-2026-10-23`
- `C:/dev-artifacts/CityPrompt/people-inclusive-2026-10-23`
- Local HTTP public root: `C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public`
- Versioned URLs: `/street-kits/people-wardrobe-v1/`, `/street-kits/people-inclusive-v1/`, `/street-kits/people-appearance-v3/`.

Human anatomy derives from the existing immutable Quaternius CC0 source packs. The guide dog derives from Quaternius's CC0 Animal Pack Vol. 2 (OpenGameArt source linked in external provenance). Manual/powered wheelchairs, rollator, stroller, cane, harness and wardrobe additions are authored derivatives. The inspected Kenney block wheelchair was rejected and is not part of the final runtime geometry. Source inputs, generator hashes, Blender files, exact-byte measurements, image-generation prompts/receipts and rejected pilots remain external. Realistic picker photographs are style interpretations, not photographs of real identified people.

The local promotion script verifies frozen input/review hashes and rejects conflicting destination bytes. `promote_local_people.py --promote` is local publication only; it does not upload to production. It backs up the four catalogue/registry files before changes. The source inventory alone is not a hosted asset bundle.

## Checks actually executed

- Frontend: **73 tests passed in 14 suites**, plus **11 placement tests passed** in `useDetailPlacement.test.tsx`. Includes supported actions, existing 23 semantics, static defaults, preview metadata, placement, editing, dynamic catalogue counts and image/video directions.
- Backend: **114 passed** across `test_people_actions.py` and `test_project_details.py` on the final local source. Existing 15 action names remain available for rigged people; invalid fixed-pose actions are rejected.
- Generator: seven pure wardrobe/proportion regression tests passed during the independent final review.
- `npm run type-check`: completed successfully. Scoped ESLint on the nine touched production TypeScript/TSX files: successful. No full production build is claimed for this local asset batch.
- `verify_appearance_previews.py`: **31/31** picker images, exact GLB bytes and exact truthful thumbnail bytes returned successfully from local HTTP.
- Actual Three.js GLTFLoader checks: all 31 decode, finite geometry/index data; 23 rigs retain the expected skeleton and Walk/Idle clips; eight fixed models have no animation clips.
- Actual Edge/WebGL QA page: all **31 GLBs decoded and drawn**, with no warning/error console entries during that check. Browser report saved as `browser-all31.json`.
- Blender evaluated **1,886 Walk/Idle frames** across the revised 23. Sole heights ranged approximately -2.191 to +7.505 mm. Hands/aid contacts and wheelchair footplates were checked; the parent-child hand gap was corrected to under 1 mm. Measurements are retained per asset.
- Local CityPrompt project contained all 31 actual models. Via UI: manual-wheelchair rotation to 195 degrees; copy to a new field position; move; delete; undo restored the copy; redo removed it. Reload restored 31 entries and the saved rotation. All eight fixed-action selectors displayed the expected Standing/Sitting default and honest limitation. A dress model's Walking action saved successfully. Separate actual-runtime browser views inspected dress walking/sitting and shorts running.
- The details-only scene opened Present → Image successfully with an enabled free export control. The final **free export download is unverified**: browser control disconnected while waiting for it. No paid image/video generation was submitted.
- Independent visual, runtime and final code/data reviews completed. Two contact issues were repaired and re-reviewed. Final reviewer reported no critical/important source findings; device/AI-output testing remains outside these results.

## Performance, with limits

Standalone Edge desktop, 1280 × 720, DPR 1, antialiasing, cached assets, 120 sampled frames; no Google tiles or app UI in this measurement:

| Fixed people/groups | Triangles (incl. QA floor) | Draw calls | Build/load on cached assets | CPU render median / p95 | Frame median / p95 |
|---|---:|---:|---:|---:|---:|
| 8 | 216,637 | 131 | Not timed | Not timed | Not timed |
| 80 | 2,166,352 | 131 | 7.2 ms | 1.1 / 2.1 ms | 16.7 / 16.8 ms |
| 160 | 4,332,702 | 131 | 9.0 ms | 1.1 / 1.8 ms | 33.3 / 66.6 ms |

Both measured runs reported 131 geometries and 17 textures. Draw calls remain bounded through batching, but geometry still grows with the instance count and 160 was visibly more costly. These are not whole-app FPS, GPU timings, cold-network timings or laptop/mobile suitability claims. Physical student laptop and mobile checks have not been performed. Memory estimates in loader/Blender reports are decoded data estimates, not measured GPU memory.

## Try locally / recovery

Open `http://127.0.0.1:5184/projects/8e3d8c3b-b734-4c90-a444-2e7d79ff9bbd` while the existing local API/frontend are running. This owned disposable project is named “People wardrobe & inclusion — local QA”. Use Add details → People, or Placed items to select the 31-model comparison. A separate `http://127.0.0.1:5184/people-model-review.html` page provides actual runtime model/action views and isolated measurements.

To reproduce local publication, restore the external package paths and run `python tools/people_pilot/promote_local_people.py --promote`, followed by `python tools/people_pilot/verify_appearance_previews.py`. The script's local path defaults are documented in its arguments. Restart the existing local API after a registry update so its process sees the new entries. Do not run this against production as a migration.

For rollback, return the initiative's source changes to the preceding commit (`e69795cae`) through a normal revert, and restore the local catalogue/registry backups under `people-wardrobe-2026-10-23/publication-backups`. Keep all versioned assets: originals are immutable and older saved scene IDs remain valid. Preserve unrelated hydrated LFS files; none are part of this initiative.

Remaining limitations: architectural rather than photoreal 3D anatomy/faces; fixed poses for the inclusive eight; ordinary skinning rather than cloth simulation; minor stripe curvature at the stroller parent's shoulders; no automatic route/seat/obstacle finding; no medical-equipment certification; final free-export result, new paid AI outputs, physical student devices and live publication not verified in this batch.
