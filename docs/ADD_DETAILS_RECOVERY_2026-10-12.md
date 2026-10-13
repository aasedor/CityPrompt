# Recovered Add Details: local integration and review

Branch: `codex/add-details-recovery`, baseline `5ea34c7cc`. No merge, push,
deployment, generation, remesh or retexture was performed. Separate building
worktrees and their changes were left untouched.

## Result

196 concepts reconciled: **185 enabled for local trial**, **11 held**. These are
137 older designs and 48 newly exported designs, added to the existing 165 choices
(350 total). Exact binaries did not duplicate existing extra-detail hashes;
similar uses such as benches remain distinct designs, not deduplicated by name.

| New choices by category | Count |
| --- | ---: |
| Landscape | 34 |
| Water & landmarks | 31 |
| Seating | 30 |
| Garden & growing | 22 |
| Vehicles | 20 |
| Play | 19 |
| Shelters & markets | 13 |
| Street furniture | 13 |
| Planting | 2 |
| Trees | 1 |

The complete 196-row [CSV](add-details-recovery/inventory.csv) and
[JSON](add-details-recovery/inventory.json) record source lineage, selected task
IDs, exact source/runtime hashes, physical bounds, geometry/texture cost,
browser loader measurements, limitations and holds. `accepted_local_trial`
does not mean every asset received every manual interaction or laptop testing.

## Held assets

- Two inherited seating holds: corten planter bench (seat ~0.67 m) and concrete
  timber seat (low/deep lounger awaiting functional review).
- Three older visual holds: woven willow tunnel (floating leaves), cantilevered
  steel lounger and sculptural sun lounger (noisy bright material).
- Four source rework holds: outdoor chime, game drum, quiet petal nook and juniper.
  These were not exported or silently replaced with earlier versions.
- White spruce and balsam fir: flat/angular foliage, especially in close-up.
  Both current exports remain archived. The earlier fir colour variant was not
  compared; no conifer is represented as a finished replacement.

## Source and runtime handling

Read `00_START_HERE.txt` and the full integration prompt from the supplied private
Drive folder. Handoff ZIP checksums passed. Downloaded 142 preferred older files
(with the 20 metric-v2 versions selected once) and verified exact hashes/sizes.
Original Drive assets remain untouched. Exported 50 existing approved colour
Meshy tasks via the normal signed-in download interface; actual GLBs and task
receipts are saved. No credits were spent. Four rework concepts were not exported.

Older files remain byte-for-byte identical; placement uses their measured offset
with the existing Y-up to Z-up transform. New runtime copies use uniform metric
scaling and centred ground pivots. Vehicles are rotated once from source X-length
to app Z-depth. Intended sizes are targets, not claimed measured dimensions;
catalogue dimensions are measured. Pebble balance crescent uses 3.6 m width to
avoid disproportionate scaling; its resulting height is ~0.18 m.

New textures are bounded at 1024 pixels rather than 2048. Across all 50 candidates,
raw transfer bytes are 276.0 MB versus 158.7 MB for derived copies (42.5% reduction).
Estimated decoded texture memory falls from ~64 to ~16 MiB per new textured model,
including mipmaps. This estimate is not a measured total GPU allocation.
Thirteen source files contained zero/non-unit normals. Runtime copies repair only
invalid normals using adjoining face sums, with an up normal for vertices supported
only by zero-area faces. Positions, indices, UVs, material distinctions and valid
normals are preserved. All 50 derived files pass formal glTF validation with zero
errors. Tangent-generation warnings remain on 49; the app generates tangents as
before. Originals are never overwritten.

185 enabled GLBs total 376.5 MB on disk, loaded only when selected/placed.
Reviewed model-derived WebP cards avoid decoding all models to browse the library.
Existing instancing shares source geometry/materials/textures across copies.
There is no global material override or new model loader.

## Verification

- All 142 older GLBs: zero glTF errors; embedded textures and source checksums verified.
- All 50 exported candidates: real nonempty unique bytes and task receipts.
- Actual app thumbnails rendered and inspected for all 140 older non-inherited-hold
  candidates and all 50 new exports. Additional visual holds excluded afterwards.
- All final 185 models: browser GLTFLoader plus actual `buildDetailInstances` path;
  dimensions/ground offset within 1 mm, including corrected versions. Shared geometry
  verified. Warm local load/decode/assembly: 20.8–160.8 ms, median 39.3 ms.
- Actual UI: urn placement, repeated copy, selection, movement, rotation, deletion,
  save/reload; new bench selection, preview, Q/E rotation and repeated placement.
- Persisted mixed scene: 12 representative items; reloaded successfully. Mixed scene
  was assembled through the existing API for reproducible spacing, not claimed as
  twelve separate manual picker trials.
- Actual deterministic render capture passed at 1600 × 558; recovered objects visible
  in beauty/context output. No paid AI image/video generation was attempted.
- 48 narrow backend tests, 22 narrow frontend tests, five asset-guard tests and
  TypeScript passed. Production build passed with existing bundle-size/dynamic-import
  warnings. The baseline landing-page imported media still build as LFS pointers;
  this is not a production deployment sign-off for the whole application.
- Clean empty-directory hydration reproduced and verified all 370 runtime/thumbnail
  files independently of the developer database. Server registry is source-controlled.

### Performance evidence and limits

Edge, this desktop, 3432 × 1261 viewport, pixel ratio 1, Balanced detail, same camera
for baseline/repeated test. Frame cadence was measured over 180 frames, not GPU
execution time. Development/build processes and Google tiles introduce noise.

| Scene | Median frame interval | p95 | Textures | Draw calls |
| --- | ---: | ---: | ---: | ---: |
| 3 details (urn + 2 benches) | 35.5 ms | 53.5 ms | 410 | 381 |
| 17 details (urn + 16 benches) | 35.4 ms | 53.8 ms | 410 | 379 |
| 12 mixed details | 35.6 ms | 53.1 ms | 443 | 388 |

The repeated test had one 411 ms stall; the mixed test maximum was 54.1 ms.
Tile streaming changes total draw counts. Rapid clicks while saving are ignored by
existing placement logic: the attempted 20-bench trial actually saved 16, verified
through the API. Counts here reflect saved objects. Laptop suitability, sustained
walking performance and all-unique-asset stress testing remain unverified.

Static visualization only: no animated vehicles, working controls, playground
certification, or new walkable surfaces are implied. Detail undo/redo and scene
import/export were not added or represented as tested. Per-asset manual CRUD,
full-size original-versus-1024 texture comparisons and mobile/laptop QA remain
additional validation work. A temporary HMR crash occurred when removing a rejected
fir while it was in the test scene; the saved trial was corrected and a reload
verified the final state. No user project was modified.

## Try it locally

Trial: http://127.0.0.1:5184/projects/eedaefe8-88d6-46ff-bba6-e76fafa36a52
Backend: 8012. Existing app on 5183/8011 was not replaced. Open **Add details**,
search a name or choose a category, then choose/place and use Q/E to rotate.
The project is a QA display, not a finished landscape design.

Large assets, downloads and screenshots are outside Git:
`C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/`.
The reviewed portable bundle is `clean-hydration/park-kits/recovered-details-v1`.
To reproduce in another public directory:

```powershell
python scripts/hydrate_recovered_details.py --bundle <reviewed-bundle-directory> --public-dir <public-directory>
python scripts/hydrate_recovered_details.py --public-dir <public-directory> --check
```

The installer verifies the entire batch before copying and refuses conflicting
files. Vite startup/build checks every model and thumbnail hash and refuses missing
or changed delivery. Keep the bundle with this branch; there is no public storage
URL yet. Publishing/hosting these binaries needs a separately approved storage
handoff. No binaries or generated directories have been staged.

Evidence folder includes `mixed-scene-browser.png`, `mixed-scene-capture.png`,
`browser-transform-metrics.json`, `frame-trial.json`, `mixed-frame-trial.json`,
`gltf-validation.json`, `new-runtime-validation.json` and ten review contact sheets.
