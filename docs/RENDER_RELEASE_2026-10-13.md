# City Prompt — October 13 release preparation

This is the current release checklist for `codex/picker-category-audit-2026-10-13`, extending the verified Render preparation at `86f64d31e`. It supersedes the October 7 catalogue counts and asset-delivery limitations. Preparation is not a live deployment or a 40-student performance certification.

## What this release fixes

- The hosted build explicitly preserves the selected Claude five-building profile instead of silently omitting it. Production metadata checks use production feature flags, and reused asset packets must match the requested profile and source fingerprints.
- The backend model contract includes the five exact new model revisions. Hosted database/storage verification includes their separate manifest.
- The 185 recovered Add Details entries now have a portable, exact-hash LFS archive and manifest. The build verifies the member inventory, sizes and hashes; it also enumerates the existing 155 detail models. Eleven held concepts and pending Meshy exports remain excluded.
- The hosted build hydrates the four tracked landing-page image/video imports from verified Git LFS bytes, including reused public packets.
- Render configuration requires a separate server-side Google Maps key for address and site-context services, in addition to the browser key.
- Nineteen older candidates' publication records are reconciled with the completed October 7 trials. Ten remaining buildings completed a new local browser trial with independent screenshot and saved-byte reviews. All 59 current private catalogue models now pass publication gates; geometry, hashes and supported operations are unchanged.

The new recovered-details archive is `seed/model-library/objects/recovered-details-v1.zip`, 357,238,418 bytes, SHA-256 `2e3adfd2dac8f1e0763540e0fd5ec734a15a7cac22f05e3868d1e5320cfaff26`. Git stores an LFS pointer. Its 370 payload files total 377,275,164 bytes. These assets load when used; archive size is not initial page download or decoded GPU memory.

## Render setup, in order

1. Confirm the Render workspace is active and review the quoted cost. Use a separate staging environment first; do not replace the existing database or media bucket.
2. Select the verified release branch/commit in `aasedor/CityPrompt`. Create a Blueprint with **`render.staging.yaml`** as its path. The old `render.yaml` is not the configuration for this release. Keep service auto-deploy and automatic Blueprint sync off during the rehearsal.
3. Supply the configuration below in Render's environment settings. Never paste secrets into Git or a support report. Ensure the GitHub integration can fetch the private repository's required Git LFS objects.
4. Start the database, queue, API, workers and single scheduler. The API pre-deploy command runs migrations. Verify `/health` and `/ready`; inspect failed migrations or worker startup before opening the app to visitors.
5. Publish the approved private Model Library records and exact object bytes to the staging database/bucket using the existing finite seed workflow. A successful frontend build alone does not perform this step. Run `backend/scripts/verify_hosted_catalogue.py` against staging and the frontend delivery audit against its public URL; both must pass. Follow the detailed commands in [the original runbook](RENDER_RELEASE_2026-10-07.md#model-library-publication-and-data-transfer).
6. Open the staging URL in an ordinary browser. Check sign-in, landing images, maps without a site boundary, site levelling, zoning selection, buildings/parks/streets/details placement and editing, walking, save/reload, deletion/undo and reports. Confirm frontend `/version.json` and backend `/health` identify the intended clean commit.
7. Check a saved image, image-job recovery and source-linked animation. Provider-mocked tests do not establish hosted provider connectivity or output quality. Agree on a finite allowance before a new paid smoke test.
8. After staging acceptance, back up the existing production database and media, retain the previous working deployment, and coordinate the API/workers/frontend update. Then connect or switch `CityPrompt.ca`. Do not automatically downgrade the database on rollback.

## Exact private-model seed handoff

Run from the reviewed checkout with explicitly configured staging `DATABASE_URL_SYNC`, `S3_ENDPOINT_URL`, `S3_BUCKET_NAME`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, and `MODEL_LIBRARY_SEED_OWNER_ID`. Hydrate the selected tracked GLBs and reference images first. Preparation and the commands below do not authorize a remote installation; perform writes only during the separately approved staging step, after backups.

The five Claude buildings remain in their separate manifest. Use the explicit manifest option so they are selected without duplicating the canonical catalogue or verifier records. Start with one exact pilot:

```sh
python -m tools.seed_model_library --rlasm-clay-only --clay-library seed/claude-five-trial/library.json --candidate clay-baronial-railway-hotel-clay-v006 --dry-run
```

After the pilot's approved installation and `--verify` readback, the bounded five-model dry run is:

```sh
python -m tools.seed_model_library --rlasm-clay-only --clay-library seed/claude-five-trial/library.json --candidate clay-baronial-railway-hotel-clay-v006 --candidate clay-zinc-dome-corner-block-clay-v007 --candidate clay-grand-magasin-clay-v008 --candidate clay-modernista-market-hall-clay-v007 --candidate clay-second-empire-city-hall-clay-v010 --dry-run
```

For an authorized installation, remove `--dry-run`; then repeat the same exact selection with `--verify`. Dry runs validate local bytes and reviews without constructing storage or database clients. `--clay-library` normalizes paths in memory, keeps source manifests unchanged, requires a finite candidate selection, prohibits `--replace`, and refuses conflicting existing object bytes or database bindings. It does not bypass local-trial publication gates. `--local-trial` is exclusively for isolated loopback targets.

Use `--clay-library seed/model-library/rlasm-architectural-clay/library.json` with exact approved candidates for the main catalogue when the same conflict refusal is desired. The legacy command without `--clay-library` retains its existing behavior: it can overwrite a conflicting object and skips existing row IDs unless `--replace` is requested. Keep backups, select a finite approved batch, and verify the final target in every case.

## Configuration to enter

| Where | Configuration |
| --- | --- |
| Static site | `VITE_API_URL`: actual HTTPS API origin; `VITE_GOOGLE_MAPS_API_KEY`: browser key restricted to the staging/live origins. `VITE_CLAUDE_FIVE_TRIAL=true` is already declared in the Blueprint. |
| API | `FRONTEND_URL`: the actual frontend origin. `ALLOWED_ORIGINS`: comma-separated exact allowed origins, not a JSON array. `GOOGLE_MAPS_API_KEY`: a server-compatible key for the enabled address/elevation APIs. |
| API, shared with workers | Private `S3_*` storage settings, `OPENAI_API_KEY`, `FAL_KEY`, and a chosen positive `RENDER_GLOBAL_DAILY_TOKEN_CAP`. The latter is an application-credit allowance, not a dollar cap. |
| Supplied by Blueprint | Private database/queue connections and a staging JWT secret. Preserve the existing live JWT secret during a later in-place production upgrade. |
| Google/Microsoft sign-in, if offered | Existing OAuth client IDs/secrets and exact HTTPS callback URLs. These are separate from Google Maps keys and credits. Verify the provider console registrations. |
| Password reset and invitations | Working SMTP host/port/user/password/sender configuration. |
| Additional AI features, if offered | Anthropic and Gemini/Vertex credentials appropriate to those existing features. Local ComfyUI remains disabled on Render. |

Google credits must belong to the billing project used by the relevant keys/services. They do not automatically cover OpenAI, fal or Render charges.

The Blueprint structure was checked against Render's current published JSON Schema on October 13. This checks configuration structure, not account eligibility, secret values, deployment success or capacity. See [Render's Blueprint reference](https://render.com/docs/blueprint-spec).

## Evidence and remaining acceptance

- Full frontend suite: **393 files, 3,270 tests passed** after catalogue/UI/programme corrections.
- Backend preparation suite: **342 passed, 26 skipped**, with providers mocked. The skipped opt-in database/storage cases are not counted as hosted acceptance.
- Final promotion checks: 103 focused frontend tests, 9 catalogue checks, 34 hosted-verifier tests and 16 local-installer tests passed. Explicit-manifest seed checks: 45 passed. Ten new trial buildings have paired capture/occlusion evidence and independently verified saved dimensions, identities and served GLB hashes. These checks do not certify interiors, student-laptop performance or hosted services.
- Hosted asset and Blueprint checks: **17 passed**. Catalogue packing: **18 passed**, using the browser's actual decoder. Current Blueprint also passed Render's published JSON Schema.
- The production-profile asset audit found **153 catalogue choices and 511 image/model dependencies**, with no asset-delivery failures. Add Details separately contributes **525 locked model/thumbnail requirements**. The complete prepared public packet contains 3,505 files, approximately 1.42 GiB, loaded on demand rather than on the landing page.

The first complete production build exposed accumulated bundle growth: 8,738.6 KiB JavaScript against the existing 8,448 KiB budget, and 188.6 KiB CSS against the older 175 KiB budget. Additional catalogue domains now use the existing lossless compression mechanism; decoder round-trip tests include preservation of signed zero. The JavaScript and route-isolation limits are unchanged.

The CSS increase represents the implemented landing/catalogue interface: approximately 150.8 KiB application CSS plus 37.8 KiB Mapbox CSS, which is loaded for its map route. Excluding test files saved only 30 bytes; a stronger minification experiment did not meet the old limit and was not adopted. The CSS-only regression budget is explicitly revised to 192 KiB, retaining little headroom and preserving the interface. This is a documented baseline change, not a claim that CSS shrank.

Current generated evidence is outside Git at `D:/CityPrompt-render-readiness-2026-10-13/`. Source changes and reviewed LFS deliverables are separate from build output. Do not publish a build receipt reporting dirty source as the final release identity.

Hosted credentials, remote model/database readback, backup restoration, live OAuth/mail and a staging browser rehearsal must be verified on the actual Render environment. Basic-laptop and 40-concurrent-student capacity remain separate measurements; more server capacity does not make the browser's GPU faster.

## Picker follow-up

The live local picker was checked on October 13 after the release build: all 74 building, 38 park and 41 street cards appeared and their preview images loaded. All 26 populated category tiles were opened and paginated to their full lists; their totals covered all 153 choices. This is discovery/preview evidence, not a new placement or rendering trial of every model.

Corrected Blue Glass Office Tower and Gilded Terracotta Tower to Offices, consistent with their exact model programmes. Corrected Timber-Screen Townhouse to Rowhouses & townhomes. Height alone can no longer move an office, hotel, civic, mixed-use or shop building into Residential towers. These browsing changes preserve all model bindings, geometry and zoning-use rules.

Validation: 39 focused picker tests and TypeScript no-emit checks passed. Local browser evidence is in `D:/CityPrompt-render-readiness-2026-10-13/picker-category-browser-audit.json` and `picker-offices.png`. The prior complete production build remains evidence for `86f64d31e`; Render must build the newer branch for these corrections.