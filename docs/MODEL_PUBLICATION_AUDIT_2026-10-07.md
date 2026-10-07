# Model publication evidence audit — 7 October 2026

This audit covers the 19 selected `local_trial_only` clay models at `dfa104ec2`. The latest request authorizes resolving and testing release blockers; it does not create human visual, keeper or publication approval. Only this report and its JSON companion were written. Library flags and approvals are preserved.

All 19 independent review-file hashes and embedded model hashes match the library. All 19 have architectural-clay passes with zero P0/P1 findings. Sixteen lack a populated `local_trial` record despite later evidence. No candidate can close all eight promotion checks solely from the inspected evidence.

Exact full hashes, current flags, check-specific evidence/scope, and proposed next tests are in [the machine-readable audit](MODEL_PUBLICATION_AUDIT_2026-10-07.json). `supported_historical` means an existing bounded check can be reconciled, not that the current hosted build has passed. `partial` and `not_tested` require the listed next test.

## Required promotion checks

`tools/catalogue_promotion.py::TRIAL_CHECKS` requires exactly the eight checks below. Trial identity must also include model SHA, project URL, tester, date and evidence. Activation separately requires an existing human quote/date bound to exact model bytes. No activation is inferred here. The tool does not define exhaustive scenarios; the following is the proposed smallest reproducible bounded matrix.

| Check | Minimum next test |
| --- | --- |
| `catalogue_card` | Search the exact candidate in the normal catalogue; verify label, photographic reference hero and successful selection. Save a screenshot and selected identity. |
| `exact_variant` | Place it once; record candidate/variant, mounted revision and downloaded GLB SHA-256 against this audit. Compare visible silhouette with the locked reference and retain mounted native scale. |
| `ground_contact` | On a disposable prepared-level site, inspect the complete envelope at low and oblique views, including projecting steps/porches; retain ground-support diagnostics and screenshots. This establishes prepared-site scope only. |
| `small_and_large_plot` | On a vacant site large enough for the candidate, place at picker minimum width/depth and enlarge to the supported maximum. Verify complete unchanged native geometry and identity at both sizes. Record dimensions, scale and screenshots; also record clean rejection below the supported minimum without replacing the saved model. |
| `rotation` | Rotate the selected native model by 15 degrees through ordinary controls; verify model and plot rotate together with unchanged scale and supported ground contact. Record before/after and persisted rotation. |
| `save_reload` | Save after the size and rotation edits; cold-reload/reopen the project and compare candidate, exact revision, transform and footprint. Record the saved binding and mounted model SHA. |
| `close_and_occluded_capture` | Create a free exact 3D capture of the model close up and a second with partial foreground occlusion. Complete both downloads, open the files, and compare framing, visible model identity and silhouette with their same-camera scene views. Record paths/hashes and screenshot evidence; preview alone is insufficient. |
| `no_console_errors` | Capture browser console and failed application requests across selection, placement, both size cases, rotation, save/reload and captures; explain unrelated environmental messages and retain zero unexplained application errors. |

Use the per-candidate minimum plot and maximum dimension in the JSON. One disposable prepared-level project can cover size, rotation, cold reopen, both captures and console collection. Reconcile proven historical checks first; do not repeat them merely to fill a newer form. Current-release regressions still warrant focused retests. Never replace a missing receipt with a sibling-model pass.

## Per-candidate evidence and remaining checks

Evidence abbreviations resolve to exact paths below. Every candidate also retains its exact independent-review path/hash in JSON. Ground support is scoped to prepared sites unless explicitly stated.

| Candidate | SHA-256 | Strongest evidence | Required checks still needing evidence |
| --- | --- | --- | --- |
| `calgary-side-by-side-duplex-clay-v004` | `1414b17d3ebec4aa87529da16dcc3a8f10305b51eaa3d129fb5a5c6c0d296f92` | L, W | `small_and_large_plot`, `close_and_occluded_capture` |
| `montreal-plateau-duplex-clay-v004` | `28fe10a3f8c5fc2e96b1e7c01382d6ec8ce546410a4976cd13c35b26c5cc4ab3` | L, W | `small_and_large_plot`, `close_and_occluded_capture` |
| `courtyard-brick-modern-clay-v004` | `6aedca74a28fd10deddda1659556968b86c9b32310b0697523559888b4ecd55a` | L, W | `small_and_large_plot`, `close_and_occluded_capture` |
| `showcase-market-clay-v006` | `ea1d0d55ccfe5de9ce74bd8a8e2b998748f045728bd674195cb1f6f1323e0074` | SHOW, W | `catalogue_card`, `exact_variant`, `ground_contact`, `small_and_large_plot`, `rotation`, `save_reload`, `close_and_occluded_capture`, `no_console_errors` |
| `showcase-aquatic-clay-v004` | `f81cd1aadb24768d513cea6a87fa9ff26e5ec5736349d195d195c257f0ed9041` | SHOW, W | `catalogue_card`, `exact_variant`, `ground_contact`, `small_and_large_plot`, `rotation`, `save_reload`, `close_and_occluded_capture`, `no_console_errors` |
| `showcase-tower-clay-v005` | `a0b4f53281c43b0cd3a98f057a5da4ea0de5f56476e7a6227074d79e61a54b80` | SHOW, W | `catalogue_card`, `exact_variant`, `ground_contact`, `small_and_large_plot`, `rotation`, `save_reload`, `close_and_occluded_capture`, `no_console_errors` |
| `autumn-timber-clay-v004` | `b640a836d5364e6d06e3dcd2f84b63cf56d233f4185b251383a717da9267cbe3` | AUT, W | `catalogue_card`, `exact_variant`, `ground_contact`, `small_and_large_plot`, `rotation`, `save_reload`, `close_and_occluded_capture`, `no_console_errors` |
| `autumn-villa-clay-v004` | `4d7c8d4647cd5b384ba36124c6fd3b16f9bb82c1a26ccdce8b05a66d28a5c84c` | AUT, W | `catalogue_card`, `exact_variant`, `ground_contact`, `small_and_large_plot`, `rotation`, `save_reload`, `close_and_occluded_capture`, `no_console_errors` |
| `autumn-cinema-clay-v004` | `318112940fbccf95c705771ec73498bb30a99525d3a2f33801e3572c3e00c5c1` | AUT, W | `catalogue_card`, `exact_variant`, `ground_contact`, `small_and_large_plot`, `rotation`, `save_reload`, `close_and_occluded_capture`, `no_console_errors` |
| `neighbourhood-library-clay-v003` | `7515d9c43e64c9b172d937b754b1d22ce71a89066fc2e57d4e6d0b9c8248449b` | N, NC, NM, W | `small_and_large_plot`, `close_and_occluded_capture` |
| `neighbourhood-corner-cafe-clay-v010` | `bbfd154388f29ed53aa80369635d2fdac76a2e4e9518650027268525d3ddf47b` | N, NC, NM, W | `small_and_large_plot`, `close_and_occluded_capture` |
| `victorian-station-interior-clay-v007` | `fd009321f395d1d17410997c392805a0bcb5c199f22038377d8cb7e39019faa7` | S | `catalogue_card`, `small_and_large_plot`, `rotation`, `close_and_occluded_capture` |
| `interior-school-clay-v003` | `179d762168f9eefe07161b7c6f5b5911f50cc66150c9e4d53fb7f702a13a4add` | I | `catalogue_card`, `small_and_large_plot`, `rotation`, `close_and_occluded_capture` |
| `interior-hotel-clay-v006` | `dd021c969344cf7380320665a431ccacf190bc8a5a5b3967d7a4aaff8d205a8f` | I | `catalogue_card`, `small_and_large_plot`, `rotation`, `close_and_occluded_capture` |
| `brick-corner-grocery-clay-v002` | `81134899b4385206676907ef9258a37f896c6a79a4ec03ad4380fd59230ce462` | API, C | `ground_contact`, `small_and_large_plot`, `close_and_occluded_capture` |
| `clerestory-neighbourhood-hall-clay-v002` | `187a30c9057bb87a86c1dec1e58d42a63e1c6f4e364be2a50a72b1f2cb1c792f` | API, C | `ground_contact`, `small_and_large_plot`, `rotation`, `close_and_occluded_capture` |
| `log-recreation-cabin-clay-v002` | `b41eabe070792f0560f1ab6c9d7c3df3893e0b569c5eda1dc11d70c56407df4e` | API, C | `ground_contact`, `small_and_large_plot`, `rotation`, `close_and_occluded_capture` |
| `prairie-neighbourhood-shops-clay-v002` | `c956b8c73d7e09c712e738a1e7ef0c5322a73fe7bab576410a8b80a16cb6753b` | API, C | `ground_contact`, `small_and_large_plot`, `rotation`, `close_and_occluded_capture` |
| `inglewood-corner-merchants-clay-v003` | `f907f31e1f2e64e1c3b2d76261d6c4695b9fdd2b743dff5abd635496540f940f` | API, C | `ground_contact`, `small_and_large_plot`, `rotation`, `close_and_occluded_capture` |

## Supersession and limits

- The Sep27 ledger retains Side-by-side duplex identity/reopen `FAIL` values. Its linked retest explicitly passes both after full reload. Keep the original snapshot and link the superseding textual observation; a new close screenshot is still absent.
- Sep24 first-three trial records already pass six checks. Their plot enlargement and existing captures do not close `small_and_large_plot` or `close_and_occluded_capture`.
- Oct4 W supplies exact-SHA doorway geometry evidence for the first 11 candidates. Timber has 0.48m of straight interior movement before a connected detour; library has 0.72m. Do not relabel these as straight 1.6m routes, whole-building walking or individual browser passes.
- Station, school and hotel have exact-SHA geometry and prepared-site browser occupied-level walking/reload evidence in S/I. The separate Oct4 embedded-network rows omit hashes; prefer S/I. These receipts predate the Oct6 continuous-walking behavior change.
- The community-five API receipt verifies all five exact model hashes at native scale. All five were placed and reopened; only grocery has recorded resize/rotation/Undo/Redo. Grocery capture reached a preview, but download completion was not proved. Do not transfer its edit/capture observations to its four siblings.
- All six artifact hashes listed in C were verified during the read-only audit, including the API receipt. External evidence remains local to this machine; durable delivery is separate.
- Prairie Neighbourhood Shops liquor-tenancy `needs review` remains a real zoning data limitation. Timber (~48 MB) and hotel (~32 MB) have unresolved dense-scene/low-end performance coverage.

## Separate broader reviews

Full natural/sloped terrain, every entrance/upper floor and street-to-door connection, accessibility, touch, adverse-network recovery, dense-scene performance and fresh empty DB/bucket installation are not extra independent booleans in `TRIAL_CHECKS`. Keep them as explicit scoped limitations or separate project requirements. In particular, walking everywhere remains user-requested product behavior and should be tested in its own current-runtime matrix. Do not require a photorealistic keeper or paid AI capture for an architectural-clay publication trial. Human approval remains separate from technical test completion.

## Evidence paths

- **W**: `C:/dev-artifacts/CityPrompt/student-community-trial-2026-10-04/walking-access-results.json`
- **L**: `C:/dev-artifacts/CityPrompt/catalogue-visual-review-2026-09-27/exact-variant-ledger.json`
- **R**: `C:/dev-artifacts/CityPrompt/building-runtime-retest-2026-09-27/retest-report.md`
- **N**: `docs/NEIGHBOURHOOD_BUILDINGS_2026-10-01.json`
- **NM**: `docs/NEIGHBOURHOOD_BUILDINGS_2026-10-01.md`
- **S**: `docs/STATION_INTERIOR_PILOT_2026-10-01.json`
- **I**: `docs/INTERIOR_BUILDING_PAIR_2026-10-01.json`
- **C**: `docs/COMMUNITY_BUILDINGS_FIVE_2026-10-07.json`
- **API**: `C:/dev-artifacts/CityPrompt/community-buildings-five-2026-10-07/five-model-api-check.json`
- **SHOW**: `docs/SHOWCASE_BUILDING_TRIO_2026-09-28.md`
- **AUT**: `docs/AUTUMN_BUILDING_TRIO_2026-09-30.md`
- **NC**: `C:/dev-artifacts/CityPrompt/neighbourhood-four-2026-10-01/combined-runtime-final.json`

## Verification

Audit validation checks: 19 unique selected candidates; exact library SHA bindings; 19 review-file digests and embedded model hashes; eight check names equal the source tuple; referenced evidence files exist; JSON and Markdown candidate sets agree; source flags remain unchanged. No browser, build, paid generation or publication action was performed.

## Focused frontend contract verification

`releaseCandidateContracts.test.ts` passes **77 tests across all 19 candidates** with `npx vitest run src/features/pickPlace/releaseCandidateContracts.test.ts --maxWorkers=2` from `frontend/`. It exercises ordinary placement controls at default/minimum/maximum sizes, independent undersized width/depth rejection and recovery, exact compiler requests without forced fit, minimum-plot rotation including fractional dimensions, and saved-revision restoration/refusal. No frontend contract defect was found.

These are JSDOM component and metadata-contract checks. They do not load/render the GLBs, establish compiled instance scale, or complete browser ground, capture or walking acceptance. All eight per-candidate promotion statuses remain as audited above.

## Later bounded runtime follow-up — 7 October 2026

This later follow-up preserves the original historical entries and their eight-check statuses. It records subsequent work by the root agent in local project `ca33c3b0-1cde-448d-aea8-85a270b222cd` at `http://127.0.0.1:5183`. It does not mark all eight checks closed or change any model, publication or approval flag.

| Area | New evidence and exact limit |
| --- | --- |
| Catalogue cards | Six stale hero references were repaired. Normal UI searches now show all 19 cards with decoded, nonzero-size images in `catalogue-cards-fixed.json`; `market-card-fixed.jpg` records the market result. |
| Mounted models | Root observed all 19 exact candidates mounted as compiled `lego_assembly`, at 15-degree rotation, surviving normal save/reload without grounding diagnostics. These observations are in the root tool transcript, not a separate retained JSON runtime receipt. |
| Authoring path | Duplex was placed through normal UI, resized to 100×100 m and rotated 15 degrees through controls, then restored to its minimum plot. The other 18 were developer/API fixtures; their presence/reload is not a normal placement/edit-path pass. |
| Native compiler | Root reports 57 requests: minimum, maximum and 1×1 m too-small cases for all 19 candidates, zero unexpected failures and native scale `[1,1,1]`. These are transcript observations, not an independent file receipt or browser size-extremes pass. |
| Visible review | All 19 close 1280×656 PNGs were saved externally. Independent `model-release-2026-10-07.json` records category closure only, zero observed P0/P1, and seven camera-limited follow-ups. |
| Capture delivery | The browser download event timed out. External close PNGs do not prove the student download flow; no close/occluded pair is claimed. This promotion check remains open for every candidate. |
| Console | Fresh errors/warnings were empty after fixed-hero searches, per root transcript. This is not a retained clean log of every earlier action. |
| Hosted packet | Fresh `assets-model-fix`: 2,471 files, 879,155,156 bytes, 133 choices and 437 dependencies; zero delivery failures. This is local packaging evidence, not a Render deployment. |
| DB/private objects | Readback verifies all 49 expected exact private objects. Overall status remains `failed` solely because 19 records remain `local_trial_only`; no technical errors are recorded. |

The new evidence narrows the blockers but does not replace missing normal-authoring checks, student-download completion, occluded-capture pairs or exact-byte human activation. The JSON follow-up retains a per-candidate record and check-by-check scope. No live service was deployed.

### Follow-up receipt hashes

SHA-256 values below were recomputed from the saved receipts. Model/capture hashes for each candidate remain in the JSON companion. The 57-request and save/reload observations have no separate fuller receipt and are deliberately labelled transcript evidence.

| Receipt | SHA-256 |
| --- | --- |
| `C:/dev-artifacts/CityPrompt/model-release-trial-2026-10-07/catalogue-cards-fixed.json` | `4bfe4a23199d558ae0cd9494ffb30014c2cb6c01c0d9f88de92b4ababb4a6321` |
| `C:/dev-artifacts/CityPrompt/model-release-trial-2026-10-07/market-card-fixed.jpg` | `99064ec2251ffbf0f1c08102704ced1df55111459316cd88845424e02ffba8dd` |
| `C:/dev-artifacts/CityPrompt/model-release-trial-2026-10-07/close-capture-receipts.json` | `a71844bcd5e87e16f7524cc23055a4360705085289a24f9dcd70c8eaed6f769c` |
| `docs/runtime-reviews/model-release-2026-10-07.json` | `c9d061d5c850f9b127bb55c19c0816b579f90023779dce0afa65cd2d6136e72a` |
| `C:/dev-artifacts/CityPrompt/render-readiness-2026-10-07/assets-model-fix/assets.json` | `787951523cee29f5e760f0d83a23dee05abd9c7a460e17fa89a061bf0a40978d` |
| `C:/dev-artifacts/CityPrompt/render-readiness-2026-10-07/assets-model-fix/catalogue-audit.json` | `a5c6bce665d111af068332ec1cd49ef4a6c8cd9a0fd7c33334c328b9d7f0d41a` |
| `C:/dev-artifacts/CityPrompt/model-release-trial-2026-10-07/final-delivery.json` | `6cb3984f0db94a63667fb4a0cab70200536f3f110c995dd9e2297b6b4d006397` |
| `C:/dev-artifacts/CityPrompt/hosted-catalogue-local-readback-2026-10-07.json` | `69213ea1fbd840e36e3a98ae15050af2dd7ce7006b14b521e194ed92aeb26247` |

The separate duplex close image is `C:/dev-artifacts/CityPrompt/model-release-trial-2026-10-07/calgary-side-by-side-duplex-clay-v004.png`: 717,853 bytes, SHA-256 `9687a78fc65796005666f56edc519a2cb2533f55942a53371e352eb763c584fb`. The close-capture collection receipt contains the other 18 images.

Root also reports final validation passes: 79 focused frontend tests, 17 Node delivery tests, 21 verifier tests, Ruff, TypeScript, ESLint and production-build budgets (initial 470.6 KiB; total 8,437.9 KiB). These are reported validation results, not new runs by this audit writer. The build used placeholder configuration and is not claimed as a deployable production artifact.

## Completed bounded student-controls trial — 7 October 2026

The subsequent [completion record](runtime-reviews/model-release-trial-completion-2026-10-07.json) closes the eight local technical trial checks for all **19 exact candidates**, within the prepared-flat-site scope. It supersedes the earlier missing-evidence statements above; the historical snapshots remain intact. No model geometry, application code, activation or publication flag changed in this trial.

- All 19 models were selected and resized through the normal reshape panel to their supported maximum and minimum plot sizes, with rotation changes. The saved models retained native dimensions and unit scale. A final normal reload returned all 19 compiled models at their restored minimum plots and 15-degree rotation, with no grounding diagnostics.
- **48 normal UI exports/downloads** match their preview SHA-256 hashes and sizes: 19 close views, 19 partially occluded views, seven low views and three supplemental side attempts. The former download timeout was an automation false negative: the actual Windows download existed. No download implementation fix was necessary.
- All 19 close/occluded pairs preserve foreground depth ordering. The obstruction was an explicitly synthetic, temporary camera-aligned box, removed after each capture and absent after reload. This tests the capture pipeline, not a natural-occluder or paid-AI scenario.
- Independent pixel review closed all seven previously limited entrance/contact views. The library gable and cinema sign needed additional side views. No actionable P0/P1 display or visible-contact defect was observed within this scope. See the [download review](runtime-reviews/model-release-download-review-2026-10-07.json) and [final supplement](runtime-reviews/model-release-occlusion-review-2026-10-07.json).
- The normal site-boundary guard rejected oversized rotated plots for the aquatic centre and library. Their maximum-size trials passed at zero degrees before restoring the smaller rotated plots. Initial stale-state measurements, expected boundary rejections, a duplicate capture receipt and the cropped cinema attempt are retained and explained; none is silently counted as a passing observation.
- No application console errors were observed. The one Three.js warning came from the developer import used for the transient test fixture before reload. Normal post-reload checks were clean. Test-instrumentation errors are disclosed separately in the completion record.

Camera placement used developer controls, and the original test scene contained 18 API-created fixtures plus one UI-placed duplex. All follow-up plot edits and downloads used ordinary student controls. This is a deliberately spaced inspection grid, not a designed community.

Raw images and receipts remain under `C:/dev-artifacts/CityPrompt/model-release-trial-2026-10-07/`. Their hashes, per-candidate checks, exact GLB identities, plot measurements and independent decisions are retained in source JSON. The local publication flags remain unchanged. Walking throughout interiors, natural slopes, low-end-device/classroom performance, human activation and hosted staging remain separate work; the earlier technical evidence gaps should not be reopened merely because those broader checks remain.
