# Classroom release implementation checkpoint

This continues the approved release plan on `codex/currie-student-trial` in
`C:/dev/CityPrompt-sol-empty-lot-trial`. It supersedes the interrupted-runtime
and remaining-check statements in the earlier September 24 records. It is local
implementation evidence, not a completed hosted classroom release.

## Completed locally

- Preserved the existing dedicated database, Redis, object bucket, accounts,
  original Currie rehearsal and detailed-trial project. Restored API 8003 and
  frontend 5178 with the existing external public assets. Final saved-zone
  readback matches both implementation baselines exactly.
- Closed image/video access gaps. Raw `render-attempts/**` objects are unavailable
  through the general file proxy; requester-authorized recovery remains usable.
  Saved video output follows current project access while private controls,
  source guide and submission details remain requester-only. Revocation blocks
  lists, GET, HEAD, Range requests and previously issued tickets. Range requests
  returned complete 200 bodies when authorized; 206 support is not claimed.
- Exercised owner/editor/viewer/revoked roles, invitation acceptance and restored
  editor access. No email or public presentation link was sent/enabled.
- Downloaded and opened wide and close exact 1440 × 836 PNGs in installed Chrome
  and Edge. These were automated desktop sessions, not independent novices.
  An additional court/garden overhead was downloaded/opened in Edge.
- Finished four new bounded photographic comparisons and one paid video after
  a retained, reviewed free guide and successful Seedance preflight. Stopped
  further paid work after review; unspent reservations are not a target.
- Fixed the account header remaining stale after video billing. It refreshes
  only the same still-current account and cannot restore a signed-out session.
- Completed the [nine exact prepared-site reviews](CLASSROOM_STARTER_ACCEPTANCE_2026-09-24.md).
  Broader terrain/race/detail tests remain explicitly outside that acceptance.
- Built the actual Linux API image and ran full migrations plus a real prefork
  failure/recovery probe with mocked providers and disposable PostgreSQL,
  Redis and MinIO. No live trial rows or billing were used by the probe.

## Bounded media and fidelity

Account `c71ac999-cfd8-44c7-9817-7884607acffe`, trial
`d51b3d3f-a143-419e-8d91-014e4d5cc7ea`. Final balance **9,125 application tokens**.
The one previously authorized 10,000-token grant was not repeated. Provider
dollar balances are unverified; application tokens are not a dollar budget.

| Slot | Result | Application tokens | Review |
| --- | --- | ---: | --- |
| Images 1–2 | Failed before provider dispatch | 0 | Still consume two conservative admission slots |
| Image 3 | Historical Flare wide view | 212 | Review required; exact primary retained |
| Image 4 | Flare close buildings/entrances | 138 | Layout/instance/unsupported-structure checks failed |
| Image 5 | Sunburst, same camera as 4 | 138 | Unsupported-structure check failed; added planting/context detail |
| Image 6 | Flare curved street/junction detail | 138 | Layout/instance/unsupported-structure checks failed |
| Image 7 | Flare overhead court/garden detail | 138 | Layout/unsupported-structure checks failed; added northern path and altered roofs/planting |
| Video 1 | Seedance Mini, eight-second HQ aerial guide | 125 | Completed; broad arrangement retained, small details softer/changed |

Seven of ten image slots and one of three video slots are consumed. **Three
image slots and two video slots remain**, with no automatic retry or reset.
The four new images use GPT Image 2.5, photographic style and Concept/balanced
fidelity; full prompt, camera, source/plan revisions and model settings are in
each immutable request. All five paid images remain `review_required`. The exact
3D source is primary and the provider original is separately unverified.

Offline replay reproduced image 3's edge-density failure (4.1014, maximum 3.0)
and 162-pixel unsupported component. The component lies on added planting near
the neighbourhood park edge; it is not evidence of a moved building. Texture
can contribute to the metric, but the observed changes do not justify loosening
thresholds. Later comparisons also show real introduced details. No production
fidelity threshold, diagnostic or failed status was waived.

Video attempt `3f2ecf17-7436-4963-a559-290c8c43f35b` retained its route, keyframes,
depth/normal checkpoints and source guide. The free guide is 1920 × 1080,
192 frames at 24 fps, eight seconds. The first free preflight timed out after
30 seconds under local memory pressure; the server took 33.69 seconds. A second
free check succeeded before the single paid submission. No paid retry occurred.
The result is 1280 × 720, 193 frames, 8.041667 seconds, 5,026,657 bytes. Its 86/100
advisory similarity and `stable` flag do not certify fine geometry. It was
downloaded normally, opened and played to the end in Edge, then reopened from
the project gallery. It adds limited photographic improvement, so further
video spending stopped. Classroom video remains disabled in the release profile.
Omni's rejected leaked key was removed from the local runtime and never retried.

## Verification and operational limits

Local commits: `3ecd72fbd` media privacy, `e002e20d7` real prefork probe,
`65ecc7540` video balance refresh. Focused results: 64 authorization/file tests;
24 integration recovery/render/trial tests plus the added real-DB video access
test; 15 frontend auth/video tests and TypeScript; 76 starter frontend and 53
starter backend tests. The relevant earlier assembly/backup evidence is reused.
No persistence change requires another live restore trial.

Linux API image: `cityprompt-classroom-api:local-20260924`, image ID
`sha256:3f6cb8dbb0892f368a8e28121950a606a6bacac18e83cc466ffbec7ae4bd0f60`.
The probe reached migration `030_render_attempts` and passed in 29.14 seconds.
It occupied two prefork children, caused real hard timeouts and abrupt child
loss, kept separate maintenance responsive, recovered already-stored provider
bytes and verified single billing/refunds under duplicate delivery. Its ten-second
test limit and aged disposable rows do not change production's 600-second hard
limit or 900-second recovery threshold. Test fixtures were mounted read-only;
application code came from the built image. Services stopped after completion.

External evidence roots:

- `C:/dev-artifacts/CityPrompt/classroom-release/detailed-trial-20260924/`:
  image attempts 01–07, video attempt 01, native downloads, access receipts,
  preserved scene baselines, accounting and focused test receipts.
- `C:/dev-artifacts/CityPrompt/classroom-release/prefork-20260924/`:
  `prefork-receipt.json`, actual worker logs and Compose output.

The accepted frontend packet and final API image are recorded below. The earlier
`candidate-20260924-a` is obsolete. A local Linux worker pass is not a hosted
API, TLS, SMTP, quota, cold-load or classroom-concurrency pass.

The first frozen packet (`candidate-20260924-b`, source `e1303bd94`) passed all
4,480 asset hashes but failed real HTTP/browser checks: Nginx's extension regex
intercepted `/api/v1/files/.../*.glb` before the API proxy, returning static 404s
and leaving buildings as placeholders. It is rejected as a delivery candidate.
The API prefix now uses `^~` so authenticated file requests reach the backend.
This also protects PNG/JSON file routes from the static rule. The failed packet
is preserved; the corrected packet passed actual routed byte readback and
browser capture. Readiness alone did not catch this defect.

## Final local delivery

Accepted frontend packet:
`C:/dev-artifacts/CityPrompt/classroom-release/candidate-20260924-c/`, built from
clean source `b504ee6deeed5e2c65cfd784565290eaa70210a3`. TypeScript and Vite passed;
4,480 runtime files, **11,192,774,728 bytes**, were copied and independently
rehashed with zero mismatches. The 48-dependency release preflight passed. All
44 public/model assets reachable through HTTP returned their exact pinned bytes,
including the three API-served building GLBs. The packet's `candidate_only=false`
means asset/runtime gates were required; it is not hosted-release approval.

The browser reopened the saved trial through packaged Nginx/API at
`http://127.0.0.1:8088`, displayed all five native buildings, three streets and
three parks, and downloaded/opened a 1440 × 836 exact PNG (2,735,226 bytes).
It showed no captured console errors. The PNG bytes match the earlier wide
exact export. Source `packaged-project.png`, `browser-verification.json`,
`verification.json` and `final-api-verification.json` retain the checks.
The earlier failed packet has `REJECTED.txt` and its failure receipt.

The real browser check also found Uvicorn access logs retaining signed asset
ticket URLs. `backend/scripts/start.sh` now uses `--no-access-log`; application
errors and readiness logging remain. A rebuilt API served a newly issued signed
ticket without writing it to access logs. All 44 routed assets were rechecked
against that image. Its startup-script bytes match the committed source.

Final API image `cityprompt-classroom-api:local-20260924-c`:
`sha256:4c5b5e7cb8b0268dddff87e69439f4d70b54db901d505d5687d26dfc26c923a8`.
Frontend source stays `b504ee6de`; the subsequent backend startup/logging change
does not change its source tree or packet. `delivery.json` records the final
Git revision, matching frontend tree, API image, pinned Nginx and receipt hashes.
Nginx base is
`sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236`.
Local verification uses the packet mounted read-only in that Linux Nginx image;
an immutable copied web image and host infrastructure still belong to deployment.

Final `/ready`: HTTP 200, database/Redis/storage/reference worker/starter assets
ready, image worker explicitly `not_enabled`. Paid images are paused and the
video POST boundary returns 403. This local classroom-profile API uses the
preserved dedicated trial DB/Redis/MinIO and a Linux prefork reference worker;
it is not a production host or a new isolated data installation. The owned
Windows API/frontend/image/maintenance/scheduler processes were stopped after
final access and unchanged-project readback. The final packet remains available
on loopback 8088 (API loopback 8004); old failed verification containers and the
disposable prefork probe are stopped. No existing data volume was removed.

Final roster/scope/model-binding regressions: 36 passed, with the opt-in isolated
DB/S3 installation test skipped here because its prior successful evidence was
reused. Startup/readiness tests: 10 passed. The initial roster test assumed the
real roster would always remain partial; it now explicitly constructs pending
and partial review fixtures and still rejects both. Asset keeper flags remain
false. Git diff checks pass; generated media, packets and runtime credentials
remain outside tracked source.

Local resource contention caused transient startup 502s and one storage-readiness
503 while copying/hashing assets; settled checks passed. No classroom cold-load,
minimum-hardware or concurrency timing claim follows from this machine. Preserve
the external evidence and stopped debug containers privately before cleanup.

## Remaining release gates and stopping rule

1. Faithful AI finish remains unresolved. Continue using exact exports; diagnose
   stored comparisons offline before considering another bounded paid experiment.
2. Select and authorize the actual hosting destination, provider budgets and
   restricted durable evidence/backup storage. Then verify exact asset and Model
   Library bytes, API readiness, TLS/routing, SMTP, quotas, cold-load timings,
   save/reopen/export and the 60-student/eight-group load on that destination.
3. Run an independent beginner exercise on representative classroom hardware.
   Agent-assisted trials do not answer novice usability or 35-minute completion.

Do not expand the catalogue, consume remaining slots by default, grant credits,
push or publish. The bounded local implementation ends with the clean packet,
evidence and explicit gates; it does not declare the classroom milestone done.
