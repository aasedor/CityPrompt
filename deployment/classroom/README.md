# Classroom deployment candidate

This is a portable setup for the existing FastAPI/PostGIS/Redis/S3 application.
It does not select or provision a host. The active acceptance gates remain in
[`STUDENT_READY_RELEASE_PLAN_2026-09-23.md`](../../docs/STUDENT_READY_RELEASE_PLAN_2026-09-23.md).
Do not run an external rollout until its concrete destination and budget are approved.

## Required services and configuration

- One dedicated PostgreSQL/PostGIS database; migration role can create the needed
  extensions or the operator installs them first. Do not reuse a developer DB.
- Dedicated private Redis with persistence and `maxmemory-policy noeviction`.
  Image messages contain IDs; database attempts own durable state. Do not restore
  an old broker queue after database rollback or share the development broker.
- A private S3-compatible bucket supporting conditional `PutObject` with
  `IfNoneMatch="*"`. The API serves permission-checked files; do not make the
  bucket public. Enable versioning/retention or equivalent recoverable storage.
- A selected HTTPS origin with a restricted Maps key and quotas. The static web
  image and API use the same origin. `VITE_API_URL` must be empty, not `/api`.
- Private backend configuration based on `backend.env.example`, stored outside
  source. Use unique DB/storage/JWT secrets, a working reset-email sender, and
  exact OAuth callbacks if social sign-in is enabled. The browser Maps key is
  public by design; restrict its permitted origins and APIs at the provider.

The application Compose file has a one-shot migration, API, two image execution
slots, a separate maintenance worker, an extraction-only reference-document
worker, one scheduler, and a static web server. Maintenance can run even when
both image slots are busy. Production uses prefork so Celery's hard timeout
works; the local Windows threads test is not proof of that process behaviour.
No service consumes the legacy default `celery` queue.

Only web HTTP is published, on `127.0.0.1:8088` by default. Connect the chosen
HTTPS edge to it; do not expose Redis, PostgreSQL, object storage or the API
directly. Configure trusted proxy IPs for that actual network. `/health` is
liveness and `/ready` is readiness. Web startup depends on API readiness; the
API does not depend on its workers starting through the web server, avoiding a
readiness dependency cycle.

## Prepare exact assets and builds

1. Freeze the intended source revision. Keep the nine-variant roster and exact
   runtime reviews current. Preserve unapproved candidate assets without claiming
   publication approval. A review-only packet may use `--candidate`; it cannot
   produce a qualifying classroom receipt.
2. Hydrate the referenced Git LFS assets. The complete UI, including Explore more
   and compatibility with existing projects, currently references 4,480 files,
   about 11.23 GB. This does not expand the verified starter catalogue. Do not
   copy old experiment folders wholesale. Use
   `node frontend/scripts/generate-runtime-asset-manifest.mjs --tracked-metadata --list-required-files-json`
   for the finite inventory. Metadata output alone is not hydrated-byte proof.
3. Install the locked frontend dependencies with `npm ci` in `frontend`. Set
   `VITE_GOOGLE_MAPS_API_KEY` (and optional `VITE_MAPBOX_TOKEN`/`VITE_SENTRY_DSN`)
   explicitly for the selected environment. Do not supply backend provider keys
   to a browser build.
4. From the repository root, run:

   ```text
   python scripts/classroom_frontend_packet.py --public-root <hydrated-public-directory> --output <new-external-packet-directory>
   ```

   The command checks the roster and current complete inventory, type-checks,
   builds against an empty public directory and isolated dotenv directory, then
   copies only required assets with byte/hash validation. It refuses an existing
   output directory, unexpected replacement, LFS pointer, revision mismatch or
   insufficient disk space. It preserves per-file hashes, build log, source commit
   and source-dirty status in the packet. A failed packet has no final `packet.json`.
   `--candidate` permits a dirty development build and partial runtime reviews,
   clearly recorded in its receipt. Use a new directory after correcting failure.
5. Build the web image from that packet using its `Dockerfile.web`, with an
   explicitly selected `NGINX_BASE_IMAGE` digest. Build the API from `backend`
   using `infrastructure/docker/Dockerfile.render`. Its Docker context excludes
   local environment files and credentials. Capture dependency/image digests and
   scan the actual image before external release; local unit tests do not replace
   an actual container build/run. No dev bind mounts belong in these images.
6. Create the intended administrator explicitly, using temporary
   `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD`, then remove those
   bootstrap variables. Never use a shared student login. Do not delete the model
   library owner account; its rows have an ownership foreign key.
7. With the chosen backend environment, run the exact three-building seed dry
   run, then apply with the existing library-owner UUID and verify:

   ```text
   python scripts/classroom_model_library.py
   python scripts/classroom_model_library.py --apply --owner-id <existing-owner-uuid>
   python scripts/classroom_model_library.py --verify
   ```

   The installer checks reviewed GLB bytes, exact variants, runtime metadata,
   current DB bindings and stored bytes. It inserts only missing rows/objects and
   refuses conflicts. `--local-trial` permits unfinished reviews only against
   loopback services; it does not qualify an external release. Do not use a broad
   replacement seed or overwrite user models. New class databases require these
   bindings as well as the static assets.

## Start the reviewed candidate

Set these operator variables outside source:
`CLASSROOM_API_IMAGE`, `CLASSROOM_WEB_IMAGE`, `CLASSROOM_BACKEND_ENV` (absolute path),
`CLASSROOM_ASSET_RECEIPT` (absolute packet receipt path), and optionally
`CLASSROOM_HTTP_PORT`. Freeze the two application image digests after actual
container verification. Do not log or attach resolved Compose output containing
secrets; use `config --quiet` to validate.

```text
docker compose -f deployment/classroom/compose.yaml config --quiet
docker compose -f deployment/classroom/compose.yaml up -d
```

Starting a local disposable candidate is separate from deploying the classroom
destination. After external approval and startup, verify `/ready` shows all
checks ready, including starter assets and reference worker. An operational
development server with `classroom_release=false` is not this evidence.

Use 60 separate student accounts and approximately eight group projects. One
owner per group sends named editor invitations to group members and a viewer
invitation to the instructor. Test invitation redemption, revocation and asset
access with separate accounts before importing a class roster. Reference-image
uploads need no worker; reference PDFs use `classroom-documents` with no AI
interpretation or automatic model generation.

## Funding and predictable failure

The supplied profile starts paid images paused. Exact 3D downloads and free 3D
landscape presets remain available. Enabling images requires a funded application
allowance, a positive global daily token cap and a provider-side spending limit.
Application tokens are not a USD guarantee; model-specific provider charges and
Maps traffic need their own budget. Do not infer a funded class budget from the
current test account's 14 tokens or refill it automatically.

The admission limits are 16 total, 2 per project and 1 per student. One explicit
request owns one idempotency key; a lost response does not justify another paid
request. Keep the image worker and scheduler enabled when pausing new image
admission so saved attempts can recover. Produced safety-refused images can
still cost money. Unknown provider outcomes refund the student once but retain
the global reservation until reconciled, preventing a retry loophole.

Instructor response: preserve the project, open Recover recent images, and check
the original attempt. Never ask a student to repeatedly click Generate. If the
service is unavailable, pause paid admission and continue with exact downloads.
Store source, original AI result and fidelity status together. Attractive output
is not proof of preserved geometry; the faithful-AI release gate remains open.

## Backup, restore and rollback

For a consistent checkpoint, pause incoming writes and stop the API, scheduler
and workers after active jobs finish. Save a custom-format PostgreSQL `pg_dump`
and object snapshot during that same pause. Preserve the release revision,
configuration identity (not secrets), hashes and migration version alongside it.
Keep daily copies off-host with restricted access and retention long enough to
cover the teaching term; verify a sample restore before each teaching block.
Do not run inherited backup scripts with deletion/pruning defaults unreviewed.

```text
python scripts/classroom_storage_backup.py snapshot <new-private-backup-directory>
python scripts/classroom_storage_backup.py verify <backup-directory>
python scripts/classroom_storage_backup.py restore-new <backup-directory> --destination-bucket cityprompt-restore-<unique-suffix>
```

The object command preserves full bytes and serving metadata, verifies every
restored object, and refuses existing/live restore buckets. It never applies a
public ACL or deletes/prunes anything. Pause writers to align it with the DB
archive; inventory-change detection alone cannot establish transaction-level
consistency. Restore the DB into a separate disposable database, verify project
and zone counts plus actual project/media access, and never attach workers to it
until queued/running historical attempts have been reconciled. A new empty
Redis does not mean those attempts are safe to replay.

For an application-only rollback, pause admission, allow active workers to
finish, take a coordinated backup, and restore the known-good frontend/API image
digests together. Keep additive migration 030 in place; do not blindly downgrade
or erase render attempts/refund markers. Verify readiness and one save/reopen/
download before reopening access. A data rollback requires separate DB and
bucket restores plus account/billing reconciliation, not a destructive restore
over the live database.

## Actual remaining approval evidence

The portable Compose schema validates locally. Database/object restore and
isolated three-model installation have passed. Actual Linux container execution,
TLS/routing, SMTP delivery, provider quotas, destination asset readback, cold-load
timing and the class-shaped browser rehearsal remain checks on the chosen host.
The final Currie exercise and Chrome/Edge exact downloads also remain integrated
acceptance gates. Do not mark them passed from this configuration file.
