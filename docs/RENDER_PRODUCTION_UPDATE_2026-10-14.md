# Production update checkpoint — October 14, 2026

This is an incomplete deployment checkpoint, not release acceptance. The owner
authorized replacing the existing CityPrompt.ca services in place with
`aasedor/CityPrompt`, branch `deployment-version`. Do not synchronize the old
Blueprint or create replacement databases, buckets, or paid services.

## Confirmed

- The pre-update production database backup was restored successfully in an
  isolated PostgreSQL 16 container. Its SHA-256 is
  `5f39e8aba34f58168b11476ba63da8f9f75486b4c46e320adbe4e35f27777ab6`.
- The legacy `022_document_processing_task` migration is preserved and merged
  with the current graph at `031_merge_legacy_documents`. Fresh, current, and
  restored-legacy database upgrade tests passed. Comparison of existing columns
  and rows in 16 restored tables found no changes from the original backup.
- API and worker deployed commit `e24c1608bae041fe77331f85242528f8389f426f`.
  The public API health endpoint identifies that commit; readiness passed for
  database, Redis, storage, image worker, and reference worker.
- Hosted Google sign-in succeeded and returned the existing projects. This
  exercised the new API with the still-old frontend, not final UI acceptance.
- Existing provider keys were configured on the API and worker. The owner
  specifically approved transferring the existing fal key to these services.
- The approved private-model transfer package was uploaded, downloaded, and
  checked against SHA-256
  `a20cd46020a70b9f99f06b3ba2a494ace70a530bf0243e3e84629996dcdf51a0`.
  The duplex pilot was installed and verified. The other 58 models await the
  hosted browser pilot before publication; their finite local dry runs passed.
- The selective LFS checkout, missing Git LFS executable, and stripped Git
  origin build issues have targeted fixes and tests. See the selective LFS
  runbook. The latest website build result is not yet verified.

## Existing service configuration

API and worker use `./backend/Dockerfile.render`, repository-root build context
`.`, blank Root Directory, and Auto-Deploy Off. API Docker Command and Pre-Deploy
Command are blank; its startup script runs the database preparation.

Worker `RUN_DATABASE_MIGRATIONS=false`. Its Render Docker Command is:

```sh
python -m celery -A app.tasks.worker:celery_app worker --pool=prefork --concurrency=2 --queues=celery,direct3d,direct3d-maintenance --beat --schedule=/tmp/celerybeat --loglevel=warning
```

Use `python -m celery`: the console-script form failed to import the existing
`scripts.prepare_database` module in the worker readiness task. There is one
existing worker with one scheduler; do not add a second scheduler.

Frontend Root Directory is blank, publish directory `frontend/dist`, with:

```sh
npm ci --prefix frontend && python3 scripts/build_hosted_frontend.py --fetch-lfs
```

The frontend uses `VITE_CLAUDE_FIVE_TRIAL=true`, Node 24.14.0 and Python 3.12.10.
Private provider keys belong on the backend services, never in VITE variables.

## Hosted acceptance checkpoint (11:02 MDT)

Workspace access was restored through the owner's approved invitation. API,
worker and frontend reached `8dd56dc`; the frontend serves the new 156-choice
catalogue. The expired Google Maps key was replaced with the owner-approved
working local key on all three services. Saved values were compared without
printing credentials. Address autocomplete and Fort Calgary Google 3D terrain
now work in the live browser after reload. The approved CSP change adds only
`'wasm-unsafe-eval'`; JavaScript `unsafe-eval` remains absent.

The separate trial project is `6c68f75a-5df4-46bd-bd23-71719b0f3719`.
Site-boundary creation/save and the default flat redevelopment surface passed.
The first duplex placement exposed a hosted-only recipe mismatch: the response
interceptor adds the API origin and download ticket, while locked server
validation expects its original relative file path. A read-only server
comparison confirmed URL decoration was the only recipe difference.

The frontend submission fix restores own-API file paths for placement,
community compilation and recipe saving. It preserves version parameters,
foreign URLs and caller state. Three new regression cases failed before the
fix; all 71 focused tests and TypeScript checks passed afterward. Independent
review found no issues. Local landing-page browser check passed without console
errors. Hosted verification of this fix is still pending.

Remaining: finish the duplex placement/move/rotate/reload pilot; publish and
verify the remaining 58 private models; complete the hosted catalogue audit,
student workflow and the approved three paid tests (US$5 total ceiling).
No paid test has started. The frontend version stamp currently reports
`source_dirty=true`; its cause is not yet proven and must not be reported as a
verified clean hosted checkout.

## Earlier access interruption (resolved)

During the frontend build, the Render dashboard began returning Access denied
for the existing frontend service. A fresh sign-in to the same account showed
only its empty personal workspace; Walid's workspace was absent. Do not bypass
that access boundary. The owner was asked to verify workspace membership.

The frontend build started from `e47423c5b9196288a572e3b40d465b212cdf968c`
at approximately 10:12 MDT. CityPrompt.ca still served the previous interface
at the last check; `/version.json` returned 404. A subsequent focused Axios
update was pushed at `95a3378d7`. It passed 35 request/authentication tests,
TypeScript checks, and a local landing-page browser check. The production npm
dependency audit reports zero advisories after that update; development-tool
advisories remain and are not represented as resolved.

Original acceptance checklist (still track outstanding items above):

1. Inspect the existing frontend build outcome, then deploy the latest reviewed
   `deployment-version` commit. Confirm `/version.json` and the actual website.
2. Complete the duplex browser placement/save/reload pilot, then publish and
   verify the remaining exact 58 private model bindings and storage bytes.
3. Run the complete hosted asset audit and student workflow checks. Check
   renderer decoding and video playback under the actual response CSP.
4. Run the owner-approved one aerial image, one street image, and one short
   animation, with a combined provider-cost ceiling of US$5. None has started
   at this checkpoint; no credits or subscriptions were purchased.
5. Record screenshots, actual results, limitations, and final source identity.
   Do not claim all models or the paid provider paths pass before these checks.

Backups, transfer receipts, screenshots, and temporary verification output are
outside Git at `D:/CityPrompt-production-update-2026-10-14/`. Original geometry
and unrelated local work were not changed by this deployment checkpoint.
