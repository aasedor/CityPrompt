# Three-building local trial

This branch supplies a development-only catalogue gate and an installer for three independently reviewed RLASM 6.1 architectural-clay candidates. It does not modify the public catalogue seed or authorize publishing the assets.

The source builds are separate, coherent branches:

| Building | Branch | Candidate |
| --- | --- | --- |
| Post-war bungalow | `codex/clay-calgary-ranch` | `calgary-inner-city-bungalow-clay-v005` |
| Edwardian Foursquare | `codex/clay-toronto-foursquare` | `toronto-edwardian-foursquare-clay-v004` |
| Sandstone civic hall | `codex/clay-calgary-sandstone` | `calgary-sandstone-heritage-clay-v007` |

## Local environment

The current trial project is `http://127.0.0.1:5174/projects/0c5c0816-3c68-4eea-8b74-150b84c59259`, named **Three building trial — easy, medium and complex**. It uses an open field at Fort Calgary, with a synthetic local student account. Existing projects are preserved.

The isolated backend uses database port **55432**, Redis **56379** and MinIO **59002**, bucket `student-studio-2027`. The external runtime bootstrap is `C:/dev-artifacts/CityPrompt/building-trio-2026-09-06/runtime-trio.py`; it explicitly loads this worktree's backend, disables paid image/video providers and enables only the existing elevation key for this test. It runs on port 8002. Never substitute production service ports or dotenv credentials.

Install one completed candidate with:

```powershell
python tools/catalogue_trio_trial/install_local.py --runtime <isolated-runtime.py> --candidate <candidate-directory> --receipt <new-dry-run-receipt.json>
```

Inspect the dry run, then repeat with `--apply` and a new receipt path. The installer checks exact candidate/model/review hashes, independent review, zero unresolved P0/P1 findings, native grade zero and the isolated service endpoints. It rejects conflicting active variants. Receipts and generated assets stay outside Git.

Start the local frontend using the existing prepared-public launcher:

```powershell
$env:VITE_LOCAL_TRIO_TRIAL='1'
./tools/catalogue_runtime/serve.ps1 -PreparedPublicRoot <prepared-public-directory> -SourceRoot <hydrated-original-source> -Port 5174
```

The gate requires both Vite development mode and `VITE_LOCAL_TRIO_TRIAL=1`; production builds omit all three cards. This machine's prepared directory is `C:/dev-artifacts/CityPrompt/catalogue-cycle-2026-09-05/runtime-v4/public`.

## Integration correction

The UI trial revealed that the Foursquare family was missing from the planner's explicit detached-home allowlist. A native-home plot therefore fell back to plain massing. The family now participates in whole-house repetition. A regression test verifies exact-variant selection, two distinct houses, native scale, containment and spacing. Attached homes and civic landmarks remain excluded from repetition.

## Verification

- 37 backend tests passed in `test_native_home_plot.py` and `test_detached_assembly.py`.
- 10 frontend tests passed across the local trio, registry and catalogue tests; TypeScript checking passed.
- Both homes were selected and placed through the actual catalogue UI. Widening each plot to 30 m produced two complete houses. The Foursquare was rotated 20 degrees and retained its architecture. All three zones and all five native instances survived reload.
- The trial's generated evidence is under `C:/dev-artifacts/CityPrompt/building-trio-2026-09-06`. Civic-hall, grounding and reload verification are recorded in `trial-report.json`. The civic plot was widened to 70 x 70 m and rotated 10 degrees while retaining one native-size model.

These are detailed native clay models. The Foursquare is approximately 10.3 MB, so a separately reviewed lower-detail version is advisable before populating large student scenes. QA lighting and final image styling are separate from the current Google-tiles viewport's lighting. No paid renders were used in this batch.
