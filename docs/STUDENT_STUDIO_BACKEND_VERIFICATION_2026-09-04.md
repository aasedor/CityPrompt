# Student Studio backend verification — 2026-09-04

This records the backend access, recovery, media-budget, detached-layout, and
report checks for `codex/student-studio-2027`. Work was performed in
`artifacts/worktrees/student-studio-2027`; the pre-existing dirty main checkout
was not edited. No paid image or video calls were made in this workstream.
Provider calls in the database probes were replaced by mocks.

## Verification checkpoint

**535 distinct backend tests passed:** 195 LEGO/layout tests, 323 combined API,
service, and trust tests, 10 subsequently added media-permission tests, and seven
legacy collaboration closure tests.
The final media run also repeated eight reservation/prompt tests, for 18 passing
tests in that invocation. Those eight are not counted twice in the distinct
total. Dependency deprecation warnings remain; there were no failing tests in
these final runs.

All commands below were run from the worktree's `backend` directory using the
existing main-checkout virtual environment. The ignored `runtime.py` harness
overrides **both** asynchronous and synchronous database settings, Redis,
storage, authentication configuration, and external-service settings before
importing the application. Do not run these commands against a deployed database
or substitute an unreviewed inherited environment.

```powershell
$studioPython = 'C:/Users/andre/OneDrive/Documents/CityPrompt/backend/.venv/Scripts/python.exe'
```

Final combined run: **323 passed, 26 warnings**, 156.16 seconds.

```powershell
& $studioPython ../artifacts/student-studio/runtime.py tests tests/test_project_access.py tests/test_file_read_tickets.py tests/test_files.py tests/test_security.py tests/test_auth_api.py tests/test_oauth_redirect_origin.py tests/test_zone_save_concurrency.py tests/test_site_zone_schema.py tests/test_optional_site_boundary.py tests/test_site_zones_generate_all_api.py tests/test_master_plan_2d_api.py tests/test_video_scene_revision.py tests/test_render_api.py tests/test_render_reservations.py tests/test_render_prompt_contract.py tests/test_direct_3d_render.py tests/test_direct_3d_presentation_first.py tests/test_render_fidelity_provenance.py tests/test_student_report.py tests/test_reference_import.py tests/test_reference_layers_api.py --basetemp='../artifacts/student-studio/pytest-backend-final' -q
```

LEGO/layout run: **195 passed, 266 warnings**, 49.61 seconds. This includes 180
existing LEGO tests and 15 new detached-layout tests. Some existing tests read
generated family manifests outside the source-only worktree. For this run only,
`frontend/public` was a temporary junction to the existing main-checkout public
asset directory. It was used for reads, then removed with an exact-path native
Windows operation. The original assets remain intact. A source-only checkout
needs those existing test fixtures to reproduce this run; their absence is not
a compiler regression. No family files were generated or promoted.

```powershell
& $studioPython ../artifacts/student-studio/runtime.py tests tests/test_lego_assembly.py tests/test_detached_assembly.py --basetemp='../artifacts/student-studio/pytest-lego-final' -q
```

Final permission follow-up: **18 passed**, 2.60 seconds. This was run after
tightening classic and Direct3D generation to require project editor permission.

```powershell
& $studioPython ../artifacts/student-studio/runtime.py tests tests/test_media_permissions.py tests/test_render_reservations.py tests/test_render_prompt_contract.py --basetemp='../artifacts/student-studio/pytest-media-permissions' -q
```

The public-link DELETE routing regression was also checked through actual ASGI
HTTP requests: **2 passed, 21 deselected**. These two cases are included in the
323-test run, not additional to it.

```powershell
& $studioPython ../artifacts/student-studio/runtime.py tests tests/test_project_access.py -k actual_routes --basetemp='../artifacts/student-studio/pytest-share-revoke-route' -q
```

Ruff passed for the touched security/files/render/LEGO/report code and its new
tests, including the final media-permission test. Scoped `git diff --check`
passed. The worktree's `frontend/public` junction is absent at this checkpoint.
Root owns the final combined source review, backend restart, and local commit.

## Real PostgreSQL concurrency probes

These used independent asynchronous sessions against isolated PostGIS on
`127.0.0.1:55432/cityprompt_studio`, with unique `studio-probe-*` fixture records.
This exercised actual PostgreSQL advisory locks, row locks, and transactions;
the external provider boundary was mocked. Scratch users/projects were removed
after the probes.

```powershell
& $studioPython ../artifacts/student-studio/postgres_probes.py
```

| Probe | Inputs | Observed result |
| --- | --- | --- |
| Last-credit race | Two concurrent requests for one account with 13 credits; each render costs 13 | Results 200 and 403; one provider invocation; balance 0; audit spend 13 |
| Global daily cap | Two funded accounts competing for the remaining 13-credit global allowance | Results 200 and 429; one provider invocation; balances 0 and 13; audit spend 13 |
| Duplicate refund | Two concurrent refund attempts for one 13-credit reservation | Balance restored to 13 once; audit spend 0 |
| Retried zone creation | Two concurrent creates with the same client request ID and semantic payload | One zone and one create-history entry |
| Reused request ID | Same request ID with changed semantic payload | 409 conflict |
| Competing edits | Two updates with the same expected version | Results 200 and 409 |
| Stale deletion | Delete using the superseded version | 409; the zone remains; two total history entries after the successful edit |
| Invitation access | Newly registered account matching pending invitation email, before token redemption | 403 |
| Invitation redemption/revocation | Intended account accepts its token, then owner revokes membership | Editor access after acceptance; 403 after revocation |
| Public serialization | Public project with spatial geometry | Valid ProjectResponse serialization |

Ordinary image generation now reserves credits and an audit entry before the
provider call, commits to release the transaction during paid work, and refunds
a failed generation once. Failure of optional post-processing or audit-image
storage after an image exists does not trigger a refund and second generation.
Its global-cap advisory-lock key matches the existing Direct3D reservation path.

## Migration order and integrity

```powershell
& $studioPython ../artifacts/student-studio/migration_probes.py
```

The probe created a separate disposable database
`studio_migration_probe_3c3997251761` on port 55432, leaving the browser fixture
database untouched. It verified:

- One Alembic head: `029_student_reports`; `028_reference_layers` follows 027,
  and 029 follows 028.
- Fresh upgrade through the complete migration chain.
- Project indexes on both new tables.
- Duplicate reference content hashes in the same project raise an integrity
  error.
- Deleting an author keeps the reference/report and sets the author foreign
  key to NULL.
- Deleting the project cascades to its references/reports.
- Downgrade 029 to 028 removes the report table and keeps reference layers;
  downgrade 028 to 027 removes reference layers; upgrading to head restores both.

The disposable database was removed after verification. The probe never
downgraded the browser database or a deployed database.

## Permission and presentation contracts

Project membership is established by the authenticated user's accepted
`ProjectShare.user_id`. A matching email address alone no longer grants access.
Invitations remain usable for local registrations: the authenticated intended
email address must also possess and redeem the invitation token. This is token
possession plus intended-recipient matching, not a new verified-email system.
Acceptance locks the share row, is idempotent for the same accepted account,
and refuses rebinding to a different account.

- `GET /api/v1/shares/invitations/{token}` returns invitation details for the
  acceptance page. It accepts invitation tokens, not public presentation tokens.
- `POST /api/v1/shares/invitations/{token}/accept` requires a bearer account and
  the intended recipient email. Pending invited-email registration is not enough.
- Project/building/zone/activity/annotation/report/model-library reads now use
  project access checks; applicable mutations require editor access.
- Classic project rendering and Direct3D rendering require editor permission
  before credit reservation or generation. Gallery save/delete and all video
  mutation endpoints also require editor. Viewers retain read/download access.
- Public project tokens grant scoped presentation reads, including the saved
  plan, approved saved image variants, and completed video URLs. They do not
  grant editor entry, private reports/documents, capture guides, provider-original
  images, or private prompt text.
- Public project serialization converts PostGIS values and omits documents and
  private building generation fields.
- The dynamic DELETE share path uses `{share_id:uuid}`. Therefore the static
  `.../shares/public-link` DELETE reaches its own handler instead of returning
  UUID-parsing 422. Browser verification/restart is coordinated separately.

### URL-based asset access

Ordinary image/video/GLTF loaders can use short-lived read tickets without
putting an account access JWT in a URL:

1. A bearer-authenticated request to
   `POST /api/v1/shares/projects/{project_id}/asset-ticket` returns
   `{ "asset_ticket": "...", "expires_in": 900 }`. Append `asset_ticket` to
   that project's protected resource URLs. Each read rechecks account activity
   and current project membership; revocation is effective before ticket expiry.
2. A bearer-authenticated request to `POST /api/v1/files/read-ticket` with
   `{ "file_path": "library/.../model.glb" }` returns
   `{ "file_ticket": "...", "expires_in": 900 }`. `file_path` is the decoded,
   canonical storage key, without a leading slash or query string. Append
   `file_ticket` to `/api/v1/files/{key}` GET/HEAD. The credential covers exactly
   that key, and ownership/admin authorization is revalidated on every read.
   The same contract supports private audit images.
3. Anonymous presentation resource URLs use their `share_token`, with the
   project and public-resource scope checked on each read. Private library/audit
   files are not covered by a public project token.

Ticket token types are distinct from login tokens. Private and revocable
resources use `Cache-Control: private, no-store` and `Referrer-Policy: no-referrer`.
Only canonical `archetype-cache/*` content is treated as immutable public cache
content; explicitly public library entries remain revocable. Unknown storage
roots and noncanonical path forms are denied.

## Recoverable zone saves

`SiteZoneCreate.client_request_id` is an optional UUID. Under the existing project
lock, identical retries return the existing zone, with no second design or
history entry. Reusing a key with different canonical request content returns
409. The server stores and protects `_client_request_id` and
`_client_request_hash` in zone properties.

Update and delete can supply `expected_updated_at`. It must include a timezone;
the server refreshes and checks the row under the project lock. A stale value
returns 409 instead of overwriting or undoing another editor's work. These
fields remain optional for backward compatibility. Retry markers currently live
on the zone row: deletion removes them, so this is not a persistent tombstone
ledger for retries after deletion.

## Detached housing layout and report quantities

The compiler dispatches only these known detached parent IDs and their catalog
variants to the new native-dwelling layout:

- `calgary_inner_city_bungalow`
- `calgary_modern_infill_house`
- `detached_contemporary_infill`
- `mediterranean_villa_estate`
- `vancouver_craftsman_bungalow`
- `vancouver_laneway_house`

It uses the selected family's native assembly envelope, including roof extents,
and places independent instances without stretching houses to fill the plot.
Deterministic candidate layouts use 3 m side gaps, 6 m row gaps, and a 1.5 m
concept edge setback where the plot supports it. The edge setback is relaxed
for a native-depth strip; separation and native geometry remain enforced.
These are concept-layout parameters, not municipal setback determinations.
Placements must be contained in the supplied polygon. Bounded search permits
at most 256 dwellings and 4,096 candidate grid positions.

Tests cover wide, long, thin, rotated, and concave plots; containment,
nonoverlap, deterministic counts, native scale, and incompatible floor requests.
Other archetypes continue through the existing planner, including tower floor
constraints. One inherited Spanish-villa expectation was updated because that
known detached family now follows separated native-dwelling behavior.

The plan request accepts optional `footprint_local_m`. Saved-zone compilation
and recipe certification derive the polygon from the actual zone geometry;
they do not trust the client ring as the persisted plot boundary. The canonical
frame mirrors the existing globe's mean-vertex metric conversion, longest-edge
orientation, oriented-envelope centering, dimension-dependent 90-degree turn,
and reflected local Y axis. Polygon holes and multipolygons are rejected for
this detached layout.

Recipe metadata identifies `fit.placement_mode = "detached_lots"`,
`fit.dwelling_count`, native envelope dimensions, and individually positioned
`footprint_segments`. Instances retain ordinary recipe transforms and scale
`[1, 1, 1]`; repeated podium/floor/roof pieces share one dwelling segment ID.

The advisory report uses only a current compiled source hash and a consistent
recipe count for compiled detached dwellings. It deduplicates linked building
records and repeated pieces within a dwelling. Missing/stale/malformed recipes
produce pending plot quantities; any student-entered unit counts are labelled
estimates. Whole housing plots contain yards, so they are excluded from known
building-footprint and gross-floor-area totals until trustworthy individual
floor plates are available. The report explicitly states that dependency.

### Local approved bungalow fixture

For the separate browser capture work, the existing approved v020 bungalow was
copied unchanged into isolated MinIO and linked to one private fixture-library
entry. There was no global catalog promotion or new building generation.

- Source: `artifacts/cityprompt-rlasm-delivery-2026-08-31/models/calgary-bungalow-v020-cityprompt-v001.glb`
  in the main checkout's ignored delivery artifacts.
- SHA-256: `d5b32558a15d4771f28efb84c81b06fcf3b7e98fc59abf7aab1dae62c6628416`.
- Measured transformed mesh extents: approximately 13.21 m wide, 17.60 m deep,
  and 7.41 m high. Because the approved source origin is asymmetric and its
  bytes were retained, placement uses a conservative centered envelope of
  approximately 13.64 by 20.46 m.
- Private fixture family: `studio-calgary-bungalow-v020`; no runtime global seed
  or Wave 2 family was changed.

## Mocked media lifecycle rehearsal

A subsequent **$0** rehearsal submitted the captured QA request through the
application's ASGI API with the image-provider response mocked. The capture had
not passed visual review and lacked usable surrounding context. It was used
only to exercise the lifecycle, never to establish image or source quality.
The mock returned the normalized source capture as its image; the service's
image checks therefore cannot be interpreted as evidence of AI fidelity.

From the worktree `backend` directory:

```powershell
& $studioPython ../artifacts/student-studio/live_image_test.py 'C:/Users/andre/OneDrive/Documents/CityPrompt/artifacts/worktrees/student-studio-2027/artifacts/student-studio/media-fidelity/pilot-direct3d-request.json'
& $studioPython ../artifacts/student-studio/verify_mock_media_lifecycle.py
```

The first command was run **without `--live`**. It intercepted exactly one
provider request and made no paid call. The follow-up script performs reads and
issues scoped read tickets; it never submits another generation.

Observed results:

- API 200, outcome `review_required`.
- One finalized audit reservation, ID
  `13d959d1-a5e2-44a0-b01a-a7bac2fc4a57`, recording **59 local application
  credits** for this Direct3D configuration. This is not a dollar charge.
  Audit creation preceded gallery persistence, with both input/output objects
  present. The first harness did not record the account balance immediately
  before the request, so this read-back does not establish its balance delta.
- Final render `0bad2553-360b-4ea0-acf9-54656388d2c5` and provider-original
  render `a1d9bab7-5b24-46c2-991b-ba0af5813917` both appeared unchanged in the
  authenticated gallery listing.
- Exact-file tickets for both images returned GET/HEAD 200 and a 900-second
  lifetime. Anonymous reads returned 401. Reusing an image's ticket for its
  different provenance key returned 403.
- Downloaded image bytes exactly matched isolated MinIO objects. Responses
  carried private/no-store and no-referrer headers. Input/output audit-image
  downloads were also verified against isolated storage.
- Embedded PNG provenance and separate provenance JSON matched the saved
  capture, plan, camera, scene, and original-output identifiers. Recomputed
  hashes of the saved four-zone/one-building plan and camera snapshot matched
  the reported revisions. The gallery image includes its illustrative label;
  the output fingerprint identifies the original pre-label pixels.

Evidence is under `artifacts/student-studio/media-fidelity/dry-run/`:
`lifecycle-verification.json`, `response.json`, `image_base64.png`,
`saved_render-download.png`, `provider_original_render-download.png`, and each
variant's `.provenance.json`. The read-only verifier is
`artifacts/student-studio/verify_mock_media_lifecycle.py`. These are ignored
local QA outputs. The browser backend's image-provider settings were not
enabled by this rehearsal. Live image submission remains a separate
root-coordinated action following visual source approval.

## Frontend undo and request-history follow-up

The project-switch regression fix was separately verified with **24 frontend
tests**: 15 undo project-scope cases, six undo revision/action cases, and three
actual Axios-adapter header cases. These are additional frontend checks, not
part of the 535-backend-test count.

Changing projects resets operation flags. Completion or failure of an older
project's undo/redo cannot change the new project's flags, action stacks, or
notifications. This is checked for undo, redo, and their zone-specific forms,
with both successful and failed older operations.

`X-Skip-History` is now an explicit property of a zone mutation request instead
of a global flag read by an asynchronous Axios interceptor. Zone undo actions
pass `{ skipHistory: true }` as the optional third argument to
`siteZonesApi.create`, `update`, and `delete`. Normal authored requests omit it.
Tests queue A's system request and B's authored request together and verify
that only A suppresses history, even while A remains unresolved. A new B system
request retains its own header when A subsequently finishes.

From the worktree `frontend` directory:

```powershell
$studioNode = 'C:/Users/andre/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
& $studioNode node_modules/vitest/vitest.mjs run src/store/undoProjectScope.test.ts src/store/undoRevision.test.ts src/services/api.zoneHistory.test.ts
& $studioNode node_modules/typescript/bin/tsc --noEmit
& $studioNode node_modules/eslint/bin/eslint.js src/store/undoRedo.ts src/store/undoActions.ts src/store/undoProjectScope.test.ts src/store/undoRevision.test.ts src/services/api.zoneHistory.test.ts src/services/api.ts
```

All three commands passed; `tsc --noEmit` is the repository's `type-check`
script command. Scoped whitespace checks also passed. After the hook owner's
save-error and normal-authored-action fixes, the combined run passed **50 tests
in four files**, including the 24 above and 26 hook tests:

```powershell
& $studioNode node_modules/vitest/vitest.mjs run src/hooks/useSiteZones.test.ts src/store/undoProjectScope.test.ts src/store/undoRevision.test.ts src/services/api.zoneHistory.test.ts
```

Normal hook mutations retain their active-project check and record their own
successful authored action even while an independent undo operation is pending.
Undo actions call the API directly, so hook-level global suppression is not
needed. The hook owner separately performs its final TypeScript verification.

## Asset renewal and closed legacy collaboration follow-up

Private asset renewal identifies the current account by the access JWT's `sub`
claim for cache partitioning only; the server still verifies every ticket and
permission. Routine same-account access-token rotation retains known renewal
targets, including video/range and exact-file scopes after a suspended tab
returns. Logout, failed authentication refresh, or a different account discards
all tickets and scopes. An operation generation prevents an older account's
pending response or failure from altering the new account's requests or tickets.
Old URL ticket parameters are removed before current-account decoration.

The existing collaboration hook has no production call sites. Its optional live
presence/edit adapter now explicitly returns `status: 'unavailable'`, with no
WebSocket construction, keepalive, or reconnect timers. The registered server
route `/ws/projects/{project_id}` closes with policy code 1008 **before accepting
the handshake or reading a message**. There is no room manager or broadcast
path. Anonymous requests, bearer tokens, and query tokens all receive the same
denial, without exposing project existence. OpenAPI's feature description now
states this limitation. Authenticated HTTP sharing and versioned saves remain
available. Enabling live collaboration later requires server-verified identity,
accepted membership, editor-only edits, and revocation/expiry checks for every
recipient; the old relay must not be restored.

Backend follow-up: **34 passed, five dependency warnings**, 6.15 seconds. Seven
are new closure tests; the other 27 repeat existing access/save checks. Six
handshake cases exercise the actual registered application route, and an ASGI
message-level case confirms the only emitted event is close, with no receives.

```powershell
& $studioPython ../artifacts/student-studio/runtime.py tests tests/test_collaboration_access.py tests/test_project_access.py tests/test_zone_save_concurrency.py --basetemp='../artifacts/student-studio/pytest-collaboration-closed' -q
& $studioPython -m ruff check app/api/v1/collaboration.py tests/test_collaboration_access.py app/main.py
```

Frontend follow-up from `frontend`: **30 passed in five files** (13 asset cache,
five collaboration closure, and 12 request-history/public/auth policy cases).
This supersedes the preceding 25-test asset/policy run; it is not an additional
30 distinct cases. TypeScript, scoped ESLint, and whitespace checks passed.

```powershell
& $studioNode node_modules/vitest/vitest.mjs run src/services/collaboration.test.ts src/services/assetAccess.test.ts src/services/api.zoneHistory.test.ts src/services/publicReadPolicy.test.ts src/services/authRefreshPolicy.test.ts
& $studioNode node_modules/typescript/bin/tsc --noEmit
& $studioNode node_modules/eslint/bin/eslint.js src/services/collaboration.ts src/services/collaboration.test.ts
```

No process was restarted by this follow-up. The closure takes effect on running
backends after the coordinated restart; source/ASGI verification already uses
the updated route.

## Local evidence and remaining limits

The isolated services use PostGIS port 55432, Redis 56379, backend
`127.0.0.1:8001`, and MinIO 59002. The browser-test harness later enabled only
the existing Maps elevation configuration for Calgary terrain checks. Paid
provider credentials stayed disabled for this workstream's tests. Service
setup, logs, scratch data, and copied fixture content are local outputs, not
source deliverables.

Ignored evidence under the worktree's `artifacts/student-studio/`:

- `compose.yaml`, `runtime.py`: isolated service and environment harness.
- `postgres_probes.py`, `postgres-probes.json`: live transaction race checks.
- `migration_probes.py`, `migration-probes.json`: migration/FK round trip.
- `seed_accepted_bungalow.py`, `bungalow-fixture.json`: immutable approved local
  model fixture and measured dimensions.
- `pytest-backend-final/`, `pytest-lego-final/`, `pytest-media-permissions/`,
  `pytest-share-revoke-route/`, and `pytest-collaboration-closed/`: bounded test
  temporary directories.

These checks establish the tested local behaviors, not production deployment
readiness or classroom-scale load performance. Optional live presence/edit
broadcasting is explicitly unavailable and its legacy WebSocket route is closed.
These changes do not repair OAuth state validation or replace the older video
reservation/accounting path. Deployment
worker/startup configuration and production migration rollout remain separate
work. The geometry report remains advisory, with explicit unknown quantities;
it is not a zoning, accessibility, infrastructure-capacity, or planning approval.
