# Classroom operations checkpoint

This is local implementation evidence for milestone 5 of
[the release plan](STUDENT_READY_RELEASE_PLAN_2026-09-23.md). It is not a deployed
classroom approval. No paid provider calls, credit refills or publication were
performed for this checkpoint.

## Startup and readiness

`backend/scripts/start.sh` now completes PostGIS/UUID setup and Alembic migrations
before starting the API. A PostgreSQL advisory lock serializes concurrent replica
startup. Migration errors stop startup; the API cannot accept work against an
unfinished schema. The release Docker entry point uses this script.

Automatic default-password administrators and hard-coded email promotions have
been removed. An optional one-time bootstrap requires both
`BOOTSTRAP_ADMIN_EMAIL` and a unique `BOOTSTRAP_ADMIN_PASSWORD` of at least 16
characters. It never promotes an existing student or changes an existing admin's
password. Remove these variables after creating the intended administrator.
Existing local accounts and privileges were not changed.

`/health` is process liveness. `/ready` is operational readiness: current migration
heads, required render tables/columns, Redis, the configured private object bucket,
an image worker consuming `direct3d`, and a recent maintenance heartbeat. It
returns HTTP 503 for unavailable dependencies without exposing exception text or
credentials. Probes have bounded waits. A disabled optional check says
`not_enabled`, not `ready`.

`CLASSROOM_RELEASE=true` additionally requires a byte-verified starter receipt
from `scripts/classroom_release.py preflight --require-release --report ...` via
`CLASSROOM_ASSET_RECEIPT`. The receipt must match the current roster and all exact
runtime reviews must pass. Today's roster intentionally cannot pass this gate:
final integrated acceptance is still partial.

The restarted local API at port 8003 returned HTTP 200 with database, Redis,
storage and image worker ready. `classroom_release` is false and starter acceptance
is `not_enabled`; this result establishes operational health only. The existing
Currie project reopened in the browser with drawings/3D saved, four saved renders
and the unchanged 14-token account balance.

## Finite paid scope

The classroom profile requires durable current-view image attempts. It rejects
credentials for deferred AI planning, mesh and video providers and uses the
existing deterministic layout fallback. Legacy paid generation endpoints are
refused before dispatch. Custom AI ground artwork also checks the boundary inside
the shared renderer, since internal calls bypass router dependencies.

The classroom UI hides optional video and custom ground artwork. Free 3D landscape
presets, existing landscape textures, catalogue placement, reference-image uploads,
advisory reports and exact downloads remain available. Existing work and the wider
development configuration are preserved. Deferred features need their own budget
and recovery integration before classroom enablement; a hidden button alone is
not the enforcement mechanism.

`DIRECT_3D_IMAGES_ENABLED=false` pauses new image generation. Durable attempt
recovery and saved results remain readable. With paid images enabled in production,
`RENDER_GLOBAL_DAILY_TOKEN_CAP` must be positive. The finite admission limits remain
16 global, 2 per project and 1 per student; tokens are an application allowance,
not a dollar-denominated provider invoice. Decide the funded allowance and apply
provider-side spending limits before enabling paid images.

## Database recovery evidence

The pre-migration archive is outside source:
`C:/dev-artifacts/CityPrompt/classroom-release/backups/before-render-attempts-20260924T003538Z.dump`.
It is 2,079,734 bytes, SHA-256
`2ac7dd3752bfc70d6d67d9bc45cb202001963563379a0ef119db81abb94ce615`.

This archive was restored into a uniquely named disposable PostgreSQL database,
then migrated through the new startup routine to `030_render_attempts`. Readback
verified 71 projects, 444 site zones and zero attempts. Only that disposable
database was removed; the live database was untouched. Ignored evidence:
`artifacts/restore-check.log`, `artifacts/restore-migration.log` and
`artifacts/verify-classroom-restore.py`.

A database archive alone does not recover models, attachments or images. The
object-store recovery package and actual hosting-specific backup schedule remain
separate requirements. Redis is delivery/cache state, not the source of truth
for image identity or refunds. Never replay a restored running paid attempt.

## Checks and remaining gates

- 246 backend tests passed across startup, scope, configuration, image service,
  presentation and OAuth; the optional Redis OAuth integration test was skipped
  in that invocation (its earlier real-Redis evidence remains recorded).
- 13 durable-attempt integration tests passed against disposable PostgreSQL state,
  actual Redis/Celery and object storage, using mocked paid providers.
- 40 scope, landscape and credit-reservation tests passed. Two initially failed
  because the local Python installation lacked the already-declared SciPy
  dependency; installing it fixed the environment without changing assertions.
- Frontend workflow/attempt client/landscape tests and TypeScript checking passed.
- Docker context now excludes local environment files, credentials and test output.

## Deployment packet and complete restore follow-up

The portable application configuration and operator steps are now in
[`deployment/classroom/README.md`](../deployment/classroom/README.md). Compose
schema validation passed without starting or deploying its services. The profile
separates image, maintenance and reference-document workers and starts web only
after API readiness. Reference PDFs commit before queue dispatch; broker failure
preserves the saved file with a readable failed-extraction status. Classroom
workers reject the paid document pipeline before loading data.

The infill's exact database binding existed only in the local database. All three
starter bindings are now packaged without account/project identities in
`seed/classroom-release/model-bindings.json`. The additive installer dry-runs by
default, hashes each GLB, refuses conflicting rows/objects, and verifies readback.
Actual installation into a disposable PostgreSQL schema and S3 bucket passed,
including repeat installation, runtime descriptor acceptance and preservation of
a changed binding. The existing live bindings were only read and all three passed.
The shared runtime checklist and review template capture this rule for new assets.
The starter closure now contains **48 pinned dependencies**, all verified locally.

The first broader hydration check exposed 518 missing direct catalogue references.
Expanding to the finite full inventory found **2,198 missing/pointer files**; all
were recoverable from existing tracked Git/LFS data. They were restored to the
external public root without replacing existing binary assets or generating any
new models. Local recovery copied 8,718,385,840 bytes. Ignored inventory:
`artifacts/classroom-runtime/asset-recovery.json`.

`scripts/classroom_frontend_packet.py` produced a candidate at
`C:/dev-artifacts/CityPrompt/classroom-release/candidate-20260924-a`:

- TypeScript and the optimized Vite build passed (15.79 seconds for bundling).
- All **4,480 required runtime files** copied with byte validation and LFS hashes:
  **11,192,774,728 bytes**. Historical experiment folders were excluded.
- `packet.json` contains actual copied-file hashes and source identity;
  `starter-receipt.json` explicitly says runtime reviews were **not required**.
- This is a development candidate from a dirty source tree, **not a qualifying
  release packet**, and was not uploaded or deployed. Existing large-chunk build
  warnings remain; browser load timing is the acceptance evidence still needed.

A second coordinated backup paused the local API/scheduler/workers, saved the
database and all objects, then restarted them. The archive and media snapshot
were restored into a disposable DB and new private bucket; all **71 projects,
444 zones, zero attempts and 123 objects (235,117,267 bytes)** verified. Every
object's SHA-256 and serving metadata matched. The disposable restore destinations
were removed; the live data and backup were preserved.

Evidence directory:
`C:/dev-artifacts/CityPrompt/classroom-release/backups/coordinated-20260924T021438Z`.
DB archive SHA-256:
`c7d0bfb22fc8afeb2489df091aa45204d028bcce18015dd00bb0dd114d736a20`.
Media manifest SHA-256:
`3a2ddc070ce8b0aee081627f4da48356ce279e09740b6ce5599f94d87922b017`.
`restore-evidence.json` records counts, hashes and the write pause. The reusable
object backup tool has no prune/delete or overwrite-existing-bucket mode.

Follow-up checks: seven storage-backup tests, seven packet-copy tests, ten roster
tests, three model-binding tests (including real disposable DB/S3), and 47 backend
document/startup/processing/media/auth/file tests passed. No paid provider was used.

Remaining: actual container execution and destination asset delivery; current
separate-account sharing/access checks; final starter/browser rehearsal; chosen
HTTPS destination, funding decision and hosted checks. Faithful AI output remains
its own open gate. Preserve these distinctions in deployment approval.
