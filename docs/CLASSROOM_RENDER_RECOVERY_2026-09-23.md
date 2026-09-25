# Classroom render fidelity and recovery

## Concept fidelity checkpoint

The default same-camera AI finish now uses the existing `balanced` policy,
labelled **Concept finish**. Its prompt preserves building count, placement,
footprint, height and roof massing, street routes and junctions, pedestrian
access, and park programme. Materials, foliage, lighting and small details can
improve. **Strict detail** remains available in Source checks, alongside
Expressive interpretation. All results still require comparison with the source.

No gate threshold was changed. This corrects the mismatch between the classroom
ideation target and a default requiring exact facade openings. It is not evidence
that previous failed images now pass, or that every gate failure was a false
positive. The old Currie outputs do not retain the full control-image bundle,
so an exact offline replay is not possible. Future attempts need the immutable
source, controls, settings, provider original and diagnostics retained together.

Validation: 36 focused frontend tests passed; TypeScript check passed. No image
provider was called. The funded close/wide comparison and independent visual
review remain open.

## Durable recovery implemented locally

Migration `030_render_attempts` adds a durable attempt table and a once-only
student refund timestamp. The new `/render/direct-3d-attempts` API binds each
user's UUID idempotency key to the exact validated request bytes. A different
request cannot reuse that identity. The frontend stores only the key/attempt ID,
and polls the saved attempt. A dropped connection or polling timeout leaves it
recoverable; it does not automatically dispatch another image.

PostgreSQL owns the queue and reservation state; Redis/Celery carries attempt
IDs. Duplicate broker delivery can claim a queued row only once. Running rows
never requeue. Defaults admit 16 active attempts globally, one per student and
two per project. The image worker runs two concurrent jobs. Queued requests
expire uncharged after 15 minutes. A stopped worker's running attempt becomes
recoverable after 15 minutes, beyond the production worker's 10-minute hard limit.

Private immutable object evidence under each project's `render-attempts` prefix
includes the source/control request, server-validated source snapshot, original
provider result and diagnostics. Evidence must persist before a paid call; the
returned result persists before optional gallery work. Gallery or final-response
failure can recover the retained pixels without another provider request. A crash
before result persistence cannot guarantee image recovery: restore student credits
once, retain uncertain provider cost in the global cap, and show an interrupted
attempt. Known unproduced failures also release the cap reservation. Produced
safety failures remain charged and retain the rejected original as private evidence.

**Recover recent images** opens the saved result beside its own original source,
with the existing fidelity review notice and exact download buttons. It requires
the requesting account and current project access. Account switching during a
request discards the previous account's response. The previous gallery remains
available; old renders are not falsely represented as having full retained controls.

Validation performed without paid image calls:

- 193 existing Direct 3D service/presentation regression tests passed.
- 13 integration cases passed using disposable PostgreSQL schemas, including the
  actual migration, concurrent duplicate requests/deliveries/refunds, stopped
  workers, expired queues, access revocation, HTTP recovery, provider failure
  classifications, and paid-result recovery despite gallery/storage errors.
- One integration case submitted 60 students across eight projects concurrently:
  16 admitted, 44 refused uncharged, two mock worker slots; the configured 1,000
  test-token daily cap allowed 14 images and refused the other two before dispatch.
- Real Redis/Celery delivery on an isolated queue invoked the mock provider once
  for duplicate deliveries. Real local S3 storage verified immutable evidence
  writes and full request/control readback. No shared broker flush or live row
  deletion occurred.
- 43 focused frontend tests and TypeScript check passed. Browser check on port
  5178 showed Concept finish and the recovery empty state; the existing four
  gallery images remained visible. Local evidence:
  `artifacts/classroom-runtime/render-recovery-panel.png`.

## Local activation and deployment contract

The local trial database was backed up before migration at
`C:/dev-artifacts/CityPrompt/classroom-release/backups/before-render-attempts-20260924T003538Z.dump`
(2,079,734 bytes; SHA-256
`2ac7dd3752bfc70d6d67d9bc45cb202001963563379a0ef119db81abb94ce615`).
The archive catalogue was readable. All 71 projects, 444 zones and a checksum of
the Currie zone properties were unchanged by migration. This is a database backup
checkpoint; full database-plus-object-storage restoration remains a separate gate.

The local API and worker have `DIRECT_3D_JOBS_ENABLED=true` in their process
environment. Start Celery beat once and an image worker consuming only
`direct3d,direct3d-maintenance`. The dedicated queues avoid consuming unrelated
legacy generation work. Windows local validation uses a two-thread worker;
production must use the prefork worker with its hard time limit:

```sh
celery -A app.tasks.worker:celery_app worker --concurrency=2 -Q direct3d,direct3d-maintenance
celery -A app.tasks.worker:celery_app beat
```

Apply migration 030 before enabling this flag. Set a positive
`RENDER_GLOBAL_DAILY_TOKEN_CAP` for production; configuration refuses durable
production image dispatch without it. `DIRECT_3D_IMAGES_ENABLED=false` pauses new
Direct 3D requests while preserving recovery and free exact exports. Existing
local credit limits were preserved; no balance refill was made. These settings
govern Direct 3D only: other paid features still require the classroom-wide
budget/feature audit before deployment.

Keep both the database and private evidence objects in backups. Never delete
idempotency rows while a client or worker could still retry delivery. Do not flip
back to the legacy synchronous route while active attempts exist. Keep the image
worker/beat/API on the same release, database and bucket. A broker restart can
redeliver committed queued rows; it must never reset running rows to queued.

Remaining gates: deployed prefork-worker interruption/recovery; destination asset
and private-bucket checks; instructor-funded close/wide image comparison; regular
browser exact downloads; full release-roster rehearsal; independent novice use.
