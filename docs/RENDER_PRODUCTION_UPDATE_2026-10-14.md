# Production update checkpoint — October 14, 2026

The hosted demonstration workflow passed on October 14; see the final acceptance
record below for exact coverage and remaining limitations. Earlier sections are
historical checkpoints, not the current deployment status. The owner
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

## Hosted acceptance checkpoint (11:35 MDT)

Frontend `775ce0c` passed the actual hosted duplex placement, move, rotation
and reload pilot. The trial also contains a shared courtyard, a standalone
sidewalk, a tree, and a proposed zoning overlay. Reports export successfully.
All 59 approved private model assemblies are installed. Signed byte reads,
GLB headers, hashes and database metadata passed for all 59. The verifier now
recognizes R2's exact unsigned HTTP 400 / InvalidArgument / Authorization
response as a denial; unrelated 400/500 responses remain unverified. This
narrow change passed 37 tests and independent review. No bucket permissions
were changed. The full public audit passed 156 choices and 514 dependencies
with zero failures; receipts are in the external deployment evidence folder.

The approved street and aerial image tests both completed and saved. Animation
has not been submitted: preflight exposed KLING_ANIMATION_ENABLED=false despite
the existing FAL credential. The flag is now saved and read back as true on
API and worker; deployment and the single animation test remain pending.
The total approved paid-test ceiling remains US$5; no additional images are
approved by this checkpoint.

A walk view showed gaps at the flattened site's terrain edge; the generated
street image also interpreted distant context as water near the site. These
are visual fidelity limitations still needing assessment, not passing claims.
Google sign-in passed earlier; a final session check and animation playback
remain before declaring the hosted acceptance complete.

## Animation blocker and fix (11:48 MDT)

API and worker `3063d7c` are live with animation enabled. Google sign-out,
Google OAuth callback, and return to the saved project passed on the current
frontend. A fresh report includes proposed R-CG zoning and current compiled
housing quantities. The first animation request returned provider HTTP422:
2032×736 is wider than its 2.5 maximum ratio. No video was produced; it must
not be called a passing animation test. Its billing outcome is not verified.

The tested fix preserves gallery originals, prepares a black-padded provider
copy only when needed, discloses it in preflight and treats completed422 as
terminal. 31 backend tests,10 frontend tests,tsc,local browser and independent
review passed. Deployment/retest remain. Do not automatically resubmit the
existing rejected request or claim a final provider invoice total.

## Final hosted demonstration acceptance

API, worker and frontend are live at
`a100a7b78320dafbe1ea7faac0f15d2411c69e2e` from `deployment-version`.
The website is https://www.cityprompt.ca. Existing data, domains and storage
were preserved. No old Blueprint synchronization or replacement services were
used. API readiness passed for database, Redis, storage and both worker checks.

The saved trial is `6c68f75a-5df4-46bd-bd23-71719b0f3719`, named
"Hosted release trial — October 14". Hosted checks passed for Google sign-in,
maps and terrain, duplex placement/movement/rotation/save/reload, a courtyard,
standalone sidewalk, a tree, zoning and transport layers, and updated report
export. All 59 installed private model assemblies passed byte/hash/metadata
checks; all 156 catalogue choices and 514 public dependencies passed the asset
audit. This is not a claim of individual interactive placement testing for all
59 private models or of measured student-laptop suitability.

The approved aerial and street images completed, saved and downloaded. One
animation completed after the initial aspect-ratio rejection. The successful
attempt is `bc0966c7-db50-46b3-baa3-c426f6d0f981`, based on saved aerial
`2156bb85-a1ac-4a88-ae53-a080db04b794`. Playback after reload, replay and the
gallery's Download MP4 control passed in Edge: 5.041667 seconds, 2272 × 908,
21,788,077 bytes. Download SHA-256 matches the stored MP4:
`dd9b927d13d70745d7be641927d4c36187f257e433709fd49eb354b14cb1056b`.

With explicit owner approval, the frontend response CSP now adds only
`media-src 'self' blob: https://threed-platform-api.onrender.com` for playback.
The live HTTP header was verified; the earlier approved `wasm-unsafe-eval`
remains present and JavaScript `unsafe-eval` remains absent. No browser security
warning was bypassed. The first blocked download was not counted as a pass;
the final visible Download MP4 click produced the verified local file.

Two images and two animation submissions (one failed, one completed) were made.
The conservative application estimate including both animation requests is
US$2.68 against the US$5 authorization. This is not a provider invoice total.
No further paid generation, credit purchase or subscription change was made.

Google OAuth, Google Maps, OpenAI image generation, fal animation, object
storage, database and Redis were functionally exercised. Gemini, Anthropic,
Meshy, Mapbox-specific functions and SMTP were not functionally tested; their
keys are neither certified working nor identified as needing replacement.

Remaining limitations: low walking views can show gaps at flattened terrain
edges, and the street AI output interpreted some surrounding context as water.
Dark-mode panel contrast remains an observed issue. The hosted version stamp
reports `source_dirty=true`; the local release checkout was clean, but the
hosted flag's cause has not been proven. These are disclosed follow-up items,
not claims of a flawless visual result or exhaustive acceptance of every feature.

Evidence remains outside Git in `D:/CityPrompt-production-update-2026-10-14/`,
including `hosted-animation-playback-passed.png`, model/catalogue audit receipts,
the updated planning report and the two render screenshots. The MP4 is also in
the owner's Downloads folder. This documentation-only checkpoint does not
require another application deploy.
