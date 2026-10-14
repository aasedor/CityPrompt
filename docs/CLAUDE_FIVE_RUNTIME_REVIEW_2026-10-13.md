# Claude five-building local trial — 2026-10-13

Source branch: `origin/claude/ten-new-buildings`, commit `0dea20a092b20ac4055d66f75307827bb364a7cf`. Working branch: `codex/claude-five-runtime-review`. All five below passed independent architectural-clay review with zero unresolved P0/P1 and are accepted for the local trial. This is not human keeper approval or production release. No push, merge or deployment has occurred at this checkpoint.

## Accepted repairs and limitations

| Building | Accepted repair/review | Remaining scope limit |
|---|---|---|
| Hotel v006 | Original bytes retained; pointed passage, courtyard, turreted skyline and recessed glazing passed independent review. | Five authored levels; working doors, full furnished interiors and upper-floor navigation unverified. |
| Zinc Corner v007 | Corrected balcony tier/sequence; lowered and broadened dome seating; supported single oculus and continuous corner cornice. | Extended storey programme and simplified roof/ironwork remain architectural-clay abstractions. |
| Grand Magasin v008 | Corrected dome/drum contacts and closed roof cheeks; restored windowed attic with cornice above openings; replaced solid gilt balcony fronts with open guards; improved interior proof. | Retail detailing and interiors remain simplified; glazing is preserved, not an occupied-building simulation. |
| Modernista Market v007 | Repaired lantern/roof support contacts and roundel carrier seams; checked crest and rake/pier contact, glazing and interior views. | Decorative tracery, market fittings and roof finish remain clay abstractions. |
| City Hall v010 | Restored facade/balcony articulation; closed tower dormer tympana and cap ends; grounded stair cheeks and landing. | Clock pediments, crown/lantern, roof seams and ironwork simplified; ordinary dormers use arched apertures against largely rectangular source glazing. |

All buildings are complete fixed native assemblies in metres with Y-up runtime delivery. Resizing the surrounding plot does not stretch the building or generate repeatable floors. Locked original reference images remain the picker/source authority.

## Exact runtime artifacts

The authoritative manifest is `seed/claude-five-trial/library.json`. Models reside in `seed/model-library/objects/claude-five/models/`; reviews reside in `seed/model-library/rlasm-architectural-clay/evidence/` at the exact manifest paths.

| Candidate | GLB bytes | SHA-256 |
|---|---:|---|
| clay-baronial-railway-hotel-clay-v006 | 4,172,400 | `424b00606c40c0bb455bf00d0af51fd12d0506049b065863fdc7827b4e9ffbd9` |
| clay-zinc-dome-corner-block-clay-v007 | 3,844,876 | `ff3718dd13d63e0380674bca3a5a1d9f07b613c9c9601fb5972d411f6fbbe179` |
| clay-grand-magasin-clay-v008 | 6,811,612 | `fa054051b06e3596376ffbad1df78697cc53b3fbe01014021067aac490b4ad82` |
| clay-modernista-market-hall-clay-v007 | 6,719,068 | `8a861c3172158a552b3896fcfec89bce09eda40489db6b8f051538fd2f94e03f` |
| clay-second-empire-city-hall-clay-v010 | 4,419,620 | `e6cc51be3727b71a75c96ecc647c3b94ca2733558f478ed6891c046e47b5bfc1` |

## Durable proof packages

Each accepted candidate has `seed/model-library/objects/claude-five/evidence/<candidate>.zip`, under the existing LFS rule. These deterministic ZIPs preserve the exact review bytes, every inspected render/board/source image, build/source/prework reports and recorded authoring scripts. `package-manifest.json` maps original paths to portable ZIP entries with SHA-256 and byte counts. The hotel’s missing exported scripts were recovered as exact hash-matching Git blobs from the recorded source commit. No `.blend` or duplicate GLB is included; failed candidates are excluded.

All five archives passed CRC, every mapped SHA-256/size, review-to-inspected-file linkage and LFS filter checks. Total ZIP size: 151,387,790 bytes. Archive contents provide portable evidence even when original absolute paths are unavailable.

| Candidate | ZIP bytes | ZIP SHA-256 |
|---|---:|---|
| clay-baronial-railway-hotel-clay-v006 | 6,710,712 | `c055ce7febdc95611aa7e806dfc25f186deb283372aebba9f0cf7fdd983ef1d2` |
| clay-grand-magasin-clay-v008 | 36,127,917 | `62ce548fff9350a39077283a316a75973c6763f2d8d6f60cb7b7be7a4f1c85c0` |
| clay-modernista-market-hall-clay-v007 | 40,326,210 | `93caf05109092b38513b0f1b13b3e65928d1346886b6ee3ef89fa79ef5c67860` |
| clay-second-empire-city-hall-clay-v010 | 33,540,239 | `eca1dd6e27103b6b83b5b957cde23184ad44d6f5d32a369e9585d41aee9fbb7e` |
| clay-zinc-dome-corner-block-clay-v007 | 34,682,712 | `01f7057c48a234520c2946875fcaa8f40b16d7678b1d0f8e2102f86a0e973e53` |

## Static runtime cost

Same-parser counts from exact manifest-verified GLBs; one copy of each building. Packed accessor payload is logical decoded geometry, not measured browser heap or GPU allocation. Primitive counts assume every primitive visible with no merging and exclude shadow/transmission/depth/other passes.

| Building | GLB bytes | Packed geometry bytes | Scene triangles | Materials / base primitive draws |
|---|---:|---:|---:|---:|
| Scottish Baronial railway hotel | 4,172,400 | 4,151,712 | 83,012 | 16 / 16 |
| Zinc Dome Corner Block | 3,844,876 | 3,821,562 | 73,763 | 18 / 18 |
| Grand Magasin | 6,811,612 | 6,790,860 | 123,442 | 16 / 16 |
| Modernista Market Hall | 6,719,068 | 6,689,952 | 124,860 | 22 / 22 |
| Second Empire City Hall | 4,419,620 | 4,392,432 | 84,140 | 21 / 21 |
| Victorian Grand Station | 12,906,244 | 12,857,604 | 234,162 | 14 / 14 |

Five trial buildings total 25,967,576 GLB bytes, 25,846,518 packed geometry bytes, 489,217 triangles and 93 base primitive draws. All six measured GLBs have zero asset images/textures; scene environment maps and render targets are excluded. Station is the canonical runtime artifact `victorian-station-interior-clay-v007`, resolved from registered asset `clay_station_victorian_iron_glass` and verified against hash `fd009321f395d1d17410997c392805a0bcb5c199f22038377d8cb7e39019faa7`; this is not a live station DB readback. No FPS, frame-time or student-laptop suitability claim follows from these counts.

## Install and try locally

Hydrate the LFS models and locked references with `git lfs pull`. With the local backend environment configured, run from `backend/`:

```text
python ../scripts/claude_five_library.py
python ../scripts/claude_five_library.py --apply --owner-project-id <existing-local-project-id>
python ../scripts/claude_five_library.py --verify
```

The default root is `seed/claude-five-trial`; model paths resolve relative to that manifest. An external delivery may override it with `--artifact-root`, but is no longer required for the default installation. The installer requires loopback database/storage endpoints and refuses conflicting bindings or objects. Plain invocation validates exact bytes, dimensions, sources and review evidence without installing.

The roster is enabled in Vite development (`import.meta.env.DEV`) or explicitly with `VITE_CLAUDE_FIVE_TRIAL=true`. Production builds leave it off by default. Installing local objects does not publish or deploy the roster.

Picker groups: hotel → Hotels; Zinc Corner → Mixed; Magasin and Market → Shops; City Hall → Civic. Field project: `http://127.0.0.1:5184/projects/0ecbd3af-aeb7-4218-ad7f-d3b4b5263164`. This is a controlled vacant-field trial, not a development proposal.

## Verification completed

- All five accepted GLBs: Khronos validation, zero errors and warnings (`gltf-validation.json`).
- Fresh isolated local DB schema and object bucket: empty-state apply, exact-object readback, idempotence, runtime descriptors and refusal of DB/storage conflicts all passed; temporary schema/bucket removed (`clean-install-verification.json/md`).
- Focused backend verification: 12 pytest passed, including the durable-path external-root regression.
- Final frontend verification: 91 tests in four focused suites passed; `npm run type-check` passed.
- Hotel earlier browser checks: picker, native placement, move/rotation, save/reload, entry passage, glazing, courtyard and deterministic capture passed. These do not substitute for the remaining five-building UI acceptance.

## Rendering and UI final results

All five buildings were placed at native scale in the vacant-field project and survived browser reloads. All five were inspected in aerial and eye-level browser views; transparent windows retain visible depth. Hotel previously passed UI placement, movement, rotation, duplicate deletion and walking checks. City Hall additionally passed UI selection, rotation to 15 degrees, reload/readback, and restoration to zero degrees. Browser drag was exercised but its displacement was not independently quantified.

A separate disposable project passed API placement, translation (+8m/+12m), rotation (23 degrees), exact-byte/native-scale verification and reload for every model. All test zones/buildings and that project were removed. These API checks are distinguished from pointer-driven UI testing. The final field project remains saved; other user projects were untouched. Final captured browser error log was empty. Full upper-floor navigation, working doors and student-laptop frame times were not tested.

Exactly ten paid image generations completed: one aerial and one street view for each of the five buildings, all using the existing Sunburst precise engine and Photo Realistic style. Street views included people. Account balance went from 7,480 to 6,460: 1,020 application tokens, no refunds. Twenty gallery files represent final/original variants of those ten calls, not twenty paid generations. One stale-scene preflight rejection occurred before provider submission/charge and was resolved by reload. No video or additional paid retry was submitted.

| Building | Aerial | Street | Visual observations |
|---|---|---|---|
| Scottish Baronial railway hotel | Saved | Saved | Towers and courtyard remain recognizable; AI added unverified background water and material detail. |
| Zinc Dome Corner Block | Saved | Saved | Dome/massing readable aerially; close storefront glazing and interior depth visible. |
| Grand Magasin | Saved | Saved | Courtyard and domes readable; street canopy and shop windows preserved, with AI furnishing/material interpretation. |
| Modernista Market Hall | Saved | Saved | Coloured glazing and exposed structure read particularly well; interior visible through entrance. |
| Second Empire City Hall | Saved | Saved | Stair/portico and roof silhouette readable; AI introduced brick infill treatment, so colour/material fidelity is approximate. |

These images demonstrate successful capture/generation/storage, not exact geometric or material fidelity. Original 3D inputs are preserved alongside outputs. Close street frames intentionally crop upper roofs.

Portable field evidence is `seed/model-library/objects/claude-five/evidence/field-trial-2026-10-13.zip`: ten full-resolution outputs, ten corresponding inputs, ten result screenshots, inventories and verification reports, using existing LFS rules. The final field overview is stored beside it. Hashes and exact image dimensions are recorded inside the archive inventory.

Two existing UI/API limitations were observed: reopening street rendering after a completed preview can display the previous preview until refresh; an immediate GET after deleting a disposable project briefly preceded transaction completion, but a later GET returned 404. No project deletion defect is claimed. These are follow-up observations, not model failures.

## Evidence storage and delivery status

Working evidence path `C:/dev-artifacts/CityPrompt/claude-five-repairs-2026-10-13` is a junction to `D:/CityPrompt-trial-backup/claude-five-repairs-2026-10-13`. The original source ZIP was moved to D: after checksum verification to recover C: space; original extracted review evidence remains at `C:/dev-artifacts/CityPrompt/claude-five-review-2026-10-13/source`. Runtime-cost and proof verification reports are in the repairs root. Heavy failed studies remain external; reviewed GLBs and proof ZIPs follow existing LFS storage conventions.

Only this local trial is active. The verified source, exact runtime models and portable evidence are prepared for the authorized origin feature-branch push. No merge or deployment is implied.

Explicit `--artifact-root PATH` uses `PATH/models/<candidate>.glb` for validation and upload, while retaining the manifest hash/reference/review checks and source provenance. The old original-only external delivery lacks the four repaired files; prefer the hydrated default Git package.
