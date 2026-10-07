# Current City Prompt: Render staging preparation

This release prepares the consolidated 133-choice application for a 40-student rehearsal. It does **not** deploy services, change CityPrompt.ca, move student data, purchase infrastructure or approve catalogue candidates. The current source work is on `codex/render-readiness-2026-10-07`, based on `893c641c6bddff483ac1d3ac22e7691160c91e08`.

## Hosting recommendation

Keep Render for the first hosted trial. Its static CDN, long-running Docker services, background workers, managed Postgres with PostGIS, and private Key Value service match the existing application. Put uploads, source models and generated media in a separate private S3-compatible bucket. Container filesystems are not durable media storage.

Railway is a reasonable alternative if usage-based billing or a different operations workflow becomes important. Moving now does not resolve missing assets, incomplete catalogue publication records, queue configuration or browser rendering performance. A larger server also cannot improve the student's local GPU performance directly. Test a representative 20-building, five-park, eight-street project on basic Windows laptops, a Mac and an iPad before changing platforms.

Official references checked 2026-10-07: [Render Postgres](https://render.com/docs/postgresql), [Blueprint specification](https://render.com/docs/blueprint-spec), [static sites](https://render.com/docs/static-sites), [Key Value](https://render.com/docs/key-value), [pricing](https://render.com/pricing), [Railway pricing](https://docs.railway.com/pricing/plans).

## What is prepared

- `render.staging.yaml`: separate, manually deployed `cityprompt-staging-*` resources. No custom domain or production resource name is assigned. Creating this Blueprint incurs charges; reviewing this file does not.
- Repository-root backend Docker context with a restrictive `.dockerignore`. Includes the house-flex contract previously absent from backend-only builds; excludes dotenv files, credentials, tests and experimental output.
- Explicit pre-deploy migrations. API restarts skip migrations only when `RUN_DATABASE_MIGRATIONS=false`; the default remains compatible with existing installations.
- Dedicated `direct3d`, `direct3d-maintenance`, and `celery` workers plus exactly one scheduler. Redis uses `noeviction` so it cannot silently evict queued jobs. Video still-animation retains its existing request/poll recovery behavior.
- A finite public asset pack assembled from committed sources and SHA-locked seeds. Includes current catalogue choices, older saved model revisions, policy maps, render examples, people and park surfaces. Missing files, HTML error pages and LFS pointers fail the build. No new catalogue entry is activated by packaging.
- Frontend build uses an isolated environment directory and an allowlist of browser configuration; server AI/storage keys do not enter Vite. Maps configuration and an HTTPS API origin are mandatory. Version receipt and release-specific service-worker cache prevent silent identity/cache drift.
- Model contract regenerated from the current catalogue; 30 missing current definitions are now included. Park variant selection and saved building/street/entrance lookup regressions are repaired.

## Provisioning configuration

Create a **new staging Blueprint** from this branch and select the custom path `render.staging.yaml`. Do not sync the legacy `render.yaml` as the configuration for this release. Disable automatic Blueprint synchronization as well as the service auto-deploys when creating the staging environment. No deployment has been attempted as part of preparation.

Initial proposed resources, all private services in Oregon:

| Role | Initial capacity |
| --- | --- |
| Static frontend | Render CDN |
| API | 1 CPU / 2 GB |
| Image worker | 1 CPU / 2 GB, concurrency 2 |
| General/document worker | 1 CPU / 2 GB, concurrency 2 |
| Maintenance worker | 0.5 CPU / 512 MB, concurrency 1; verify memory on staging |
| Scheduler | 0.5 CPU / 512 MB, one instance; verify memory on staging |
| Postgres 16 + PostGIS | 0.5 CPU / 1 GB, 15 GB disk |
| Key Value | Paid 256 MB instance, private access, no eviction |

The listed compute/database/queue instances total approximately **US$118/month** at the published rates checked 2026-10-07: three $25 services, two $7 services, $19 Postgres and $10 Key Value. Confirm the current Render checkout estimate and the user's budget before provisioning. Database disk, object storage, egress, the Render workspace plan, Google Maps and AI usage are separate costs. These capacities are a starting point, not a measured 40-browser guarantee. API/general worker pools plus short-lived image connections are approximately 27 database connections before additional operational clients; retain headroom within the database limit.

Enter configuration in Render, never in Git:

| Variable | Where / requirement |
| --- | --- |
| `VITE_API_URL` | Static site; actual HTTPS API origin, without `/api` or a trailing path |
| `VITE_GOOGLE_MAPS_API_KEY` | Static site; browser key restricted to the actual staging origin and intended Google APIs |
| `FRONTEND_URL`, `ALLOWED_ORIGINS` | API; actual staging frontend origin, exact allowed origins, no localhost/wildcard |
| `JWT_SECRET_KEY` | Generated on staging API, shared to workers through Blueprint references; preserve the live secret when later updating the existing live deployment |
| `S3_ENDPOINT_URL`, `S3_REGION`, `S3_BUCKET_NAME` | API; staging's private S3-compatible bucket; workers reference the same values |
| `S3_ACCESS_KEY`, `S3_SECRET_KEY` | API; least-privilege credentials to the staging bucket; workers reference them |
| `OPENAI_API_KEY`, `FAL_KEY` | API; server credentials, also referenced by workers. No assumed educator discounts |
| `RENDER_GLOBAL_DAILY_TOKEN_CAP` | API; explicitly chosen positive application-token allowance; **not** a dollar spending cap |
| `DATABASE_URL`, `REDIS_URL` | Private Render references supplied by Blueprint |

The API service is the source of shared worker environment values. Render refreshes those references on Blueprint sync; when rotating keys, synchronize and restart all affected workers, not just the API. The frontend deliberately has no provider or storage credentials.

The current app uses `CLASSROOM_RELEASE=false`: the older `true` profile intentionally restricts the app to a different starter catalogue and excludes video providers. Local ComfyUI stays disabled on the host. Optional existing services such as mail/password reset, OAuth, server-side Google APIs, Anthropic/Gemini and Socrata tokens need their own existing production credentials and callbacks if those workflows are used; do not copy the desktop dotenv wholesale. Verify these before opening student registration.

The image queue initially allows 16 global outstanding jobs and two per project. Two image calls execute concurrently; further submissions receive the existing retry-later response without starting a paid call. Increase the bounded capacity only after measuring throughput and confirming the spending allowance. The database-backed recovery path does not resubmit an uncertain paid attempt.

## Reproducible build and asset delivery

Use the committed branch with Git LFS installed. The full repository contains much more artwork than a deployment needs. `GIT_LFS_SKIP_SMUDGE=1` avoids eagerly hydrating all experiments at checkout; `--fetch-lfs` retrieves exact requested tracked objects only. Authenticated Git LFS access to this private repository must work from the build environment. If Render cannot fetch LFS with its integration, prepare the same verified packet in CI with the authorized repository credentials; do not publish credentials in command output.

```sh
npm ci --prefix frontend
# Supply the two browser variables through the build environment first.
python3 scripts/build_hosted_frontend.py --fetch-lfs
```

This runs catalogue JSON and backend contract checks, policy-map and render-example checks, full delivery audit, TypeScript, Vite and bundle budgets. Default output is `frontend/dist`; it refuses to replace an existing output directory. Review builds can use a new external `--output` directory and `--work-dir` for durable evidence outside a desktop temp folder. A separately prepared packet can be reused with `--assets` only when its source fingerprints still match the checkout, every payload hash matches, and no unlisted files exist in its public folder:

```sh
python3 scripts/hosted_assets.py --output /tmp/cityprompt-reviewed-assets --fetch-lfs
python3 scripts/build_hosted_frontend.py --assets /tmp/cityprompt-reviewed-assets --output /tmp/cityprompt-review-build
```

The prepared packet has 2,438 public files, about 826 MiB total; these include optional park skins and 724 policy-map images loaded on demand. This is **not** the initial page download. The catalogue dependency audit covers 133 choices and 404 image/model dependencies. A receipt is written outside the source tree. `/version.json` exposes only commit identity, choice count and whether the source was dirty, and is served without caching. API `/health` includes its valid Render commit ID. A release must use matching clean source commits.

SPA rewrites cover application routes explicitly. Missing `.glb`, map or image URLs return a real 404 instead of receiving `index.html`. Fingerprinted JS and immutable model revisions can be cached long-term; mutable hero/model paths use shorter caching. The build stamps the service worker with a release-specific cache name so its cache does not preserve an earlier deployment's images/models.

## Model Library publication and data transfer

The current catalogue references 49 exact private Model Library seeds; all match a single committed candidate by variant, SHA-256 and source path. Fifteen other exact/native fixtures use frontend GLBs directly. A static frontend build **does not upload private Model Library objects or create database model rows**.

Nineteen selected private candidates still carry `local_trial_only=true`. The existing seed tool refuses to publish them to a remote target. These records must be reconciled with the human visual review before all 133 current choices can work remotely. Keep the latest UBST pilot and historical unapproved expansion waves outside the active catalogue. Do not remove publication guards, silently fall back to older models, or relabel generated output as approved.

For eligible candidates, the existing finite command is run from the repository root with explicitly supplied staging `DATABASE_URL_SYNC`, `S3_*`, and `MODEL_LIBRARY_SEED_OWNER_ID` environment values:

```sh
python -m tools.seed_model_library --rlasm-clay-only --candidate EXACT_CANDIDATE --dry-run
python -m tools.seed_model_library --rlasm-clay-only --candidate EXACT_CANDIDATE
python -m tools.seed_model_library --rlasm-clay-only --candidate EXACT_CANDIDATE --verify
```

Run one reviewed pilot first, verify remote bytes, placement and save/reload, then use the finite approved list. The tool reads `DATABASE_URL_SYNC` directly, not the app's `DATABASE_URL` or dotenv loader. Never use `--local-trial` to try to bypass remote publication checks. Some house-flex/storey assemblies have additional review-pending records; review them separately before claiming floor-count variants are published.

Do not use `scripts/validation_runtime.py` or the loopback-only classroom seed scripts against Render. A `/ready` success verifies dependencies and workers, but deliberately does not certify every private Model Library asset in this full-catalogue profile. Read back each selected remote GLB and compare its hash and model row explicitly.

Existing student accounts/projects and private media need a separate, backed-up migration or use of the existing production database/bucket during the eventual coordinated upgrade. Deploying Git alone does not transfer local projects, reference photos or user balances. Staging uses separate data.

## Staging acceptance and live cutover

1. Back up the existing production database and preserve its media bucket and current deployed commit identities. Test restoring a backup into an isolated database. Enable bucket versioning or equivalent retention.
2. Apply migrations through revision 030 on staging; start all consumers and exactly one scheduler. Confirm API `/ready` returns ready for database, storage, Redis, images and general/document worker. Confirm API `/health` and frontend `/version.json` match the intended clean commit.
3. Resolve the candidate publication records and seed/verify each approved exact revision. Check representative missing URLs return 404, not HTML; verify all policy tiles and catalogue hero images load.
4. Browser rehearsal: login, draw site, inspect zoning/LAP/MDP/CTP, place 20 buildings/five parks/eight street segments, walk inside buildings and across beach/parks, save/reload, delete/undo, inspect imagery. Check alternate storeys only for their supported published programs.
5. Mock providers while testing image queuing/recovery and source-linked video records. A real paid still/video smoke test needs a deliberate finite trial with the configured allowance. Check mail/password reset/OAuth if enabled.
6. Rehearse 40 concurrent sessions with measured API latency, connection counts, worker memory and queue delay. Test representative low-spec student hardware. The automated admission test is not a substitute for this browser/provider-latency rehearsal.
7. After staging passes, coordinate API/workers/frontend to the same commit and then move the custom domain or update the existing production services. Preserve production secrets and data. Keep the previous static artifact available.

Rollback is an application rollback to the previous compatible API/worker/frontend commits, keeping the database and media intact. Do not automatically downgrade migrations or delete a bucket. Pause new paid submissions during an uncertain rollout and let durable job reconciliation finish; never restart jobs by resubmitting provider calls. Verify compatibility before rollback if the old application cannot read the newer schema.

## Remaining release gates

Preparation can be verified locally, but a hosted release still needs Render access/configuration and budget, exact model publication review and storage seeding, data/backup decisions, and a staging browser rehearsal. No claim of completed live deployment or measured classroom capacity is made here.

## Verification recorded during preparation

- Full frontend suite: 357 files, 2,957 tests passed with two workers; TypeScript and touched-source lint passed. Two unrestricted runs encountered load-sensitive test timeouts on the busy desktop; assertions/timeouts were not weakened.
- Production Vite output and existing budgets passed: initial JavaScript 470.6 KiB, all JavaScript 8,438 KiB against the 8,448 KiB limit, CSS 170.9 KiB against 175 KiB. Catalogue reference metadata uses the existing lossless packed-data mechanism; every field is verified by browser-decoder round-trip tests. The total bundle budget has little remaining headroom.
- 23 Node delivery/packing tests and 12 Python asset/Blueprint checks passed. Blueprint validated against Render's published JSON Schema.
- Final Linux Docker image built successfully; 120 focused tests passed offline. Another 66 host checks included isolated PostGIS migrations 000–030, real Redis/Celery delivery and private MinIO persistence with providers mocked. These counts have overlapping coverage.
- Under 512 MiB / 0.5 CPU limits, idle maintenance used approximately 109 MiB and beat 91 MiB, with no OOM. This verifies startup/idle capacity only.
- Local production-artifact browser smoke: landing images, registration navigation and direct reload rendered without console errors. No registration, login to a hosted backend, or paid provider call was submitted.
- Full 40-browser concurrency, live Render configuration, private hosted model readback and paid image/video quality remain staging checks.

Evidence and generated builds are outside Git under `C:/dev-artifacts/CityPrompt/render-readiness-2026-10-07/`, with backend validation and library audit JSON alongside that directory. The frontend full-test log is ignored under `artifacts/frontend-release-full-bounded.log`. Generated build output is not a source commit or a publication approval.


### Current private candidates with local-only publication records

| Catalogue label | Exact candidate |
| --- | --- |
| Side-by-side duplex | `calgary-side-by-side-duplex-clay-v004` |
| Plateau stacked duplex | `montreal-plateau-duplex-clay-v004` |
| Brick courtyard entrance building | `courtyard-brick-modern-clay-v004` |
| Grand Iron & Glass Market | `showcase-market-clay-v006` |
| Living-Roof Aquatic Centre | `showcase-aquatic-clay-v004` |
| Gilded Terracotta Tower | `showcase-tower-clay-v005` |
| Nordic Roof-Garden Apartments | `autumn-timber-clay-v004` |
| Tuscan Arcade Villa | `autumn-villa-clay-v004` |
| Grand Deco Cinema | `autumn-cinema-clay-v004` |
| Mass-timber Library | `neighbourhood-library-clay-v003` |
| Corner CafÃ© & Apartments | `neighbourhood-corner-cafe-clay-v010` |
| Victorian Grand Station | `victorian-station-interior-clay-v007` |
| Timber Art & Design School | `interior-school-clay-v003` |
| Mediterranean Courtyard Hotel | `interior-hotel-clay-v006` |
| Brick Corner Grocery | `brick-corner-grocery-clay-v002` |
| Clerestory Neighbourhood Hall | `clerestory-neighbourhood-hall-clay-v002` |
| Log Recreation Cabin | `log-recreation-cabin-clay-v002` |
| Prairie Neighbourhood Shops | `prairie-neighbourhood-shops-clay-v002` |
| Inglewood Corner Merchants | `inglewood-corner-merchants-clay-v003` |

This list is a source-record inventory, not a new visual quality judgment. Reconcile each existing review before remote publication.
