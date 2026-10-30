# Final candidate security and QA checkpoint — 30 October 2026

This is a review candidate, not a security certification or a deployed release.
It extends the consolidated company handoff with verified account, upload and
background-job protections. The shared deployment branch remains a separate
release decision. Keep draft PR #38 open while its publication gate is failing.

## Implemented protections

- OAuth identities bind to the provider's immutable subject. Email hints do not
  silently merge Microsoft accounts. Password recovery is single-use, revokes
  previous sessions and removes prior provider bindings when required.
- Refresh sessions rotate, detect reuse and serialize browser refresh requests.
  Account session versions also apply to temporary asset access and caches.
- OAuth callbacks carry a short-lived, single-use code bound to the initiating
  tab's S256 proof. Tokens are returned by the exchange response rather than in
  URLs. Account commit precedes the first-login redirect; exchange success follows
  refresh-session persistence. Telemetry starts after callback URL scrubbing,
  and the service worker bypasses auth navigation and retires its old cache.
- Redis admission is atomic and bounded. Rejected requests do not grow the
  limiter indefinitely; Redis failures fail closed. Authentication and address /
  elevation lookups have endpoint-specific limits, including shared classroom
  networks. Client IP forwarding is trusted only from configured proxy ranges.
- GLB validation budgets decoded buffers, textures, primitive copies and scene
  traversal before expensive work. Table, shapefile and PDF processing have
  explicit size and work limits. Reference-only PDFs use text extraction.
- Document status requires the persisted task binding and current project
  access. Preview jobs accept bounded, authorized same-project sources and
  recheck the requester's access in the worker.
- Runtime dependency pins were updated and tested. Image isolation explicitly
  retains U2-Net rather than silently adopting a new default model.
- Queue names can be isolated for local / staging workers. Production defaults
  remain `celery`, `direct3d` and `direct3d-maintenance`.
- Both Docker contexts exclude the documented `vertex-key.json` credential file.
  Production rejects short, known-placeholder and obvious repeated signing keys.
  Development database, Redis and MinIO ports bind to loopback while preserving
  their port numbers and internal service connections.
- Vite exposes only 11 inventoried public settings by exact name, preserving
  Maps, Mapbox, API, telemetry and public flags. Unused provider credentials and
  prefix-collision names stay out of browser environment objects. The unused
  frontend `VITE_FAL_KEY` Compose injection was removed; `FAL_KEY` stays server-side.

## Installation and compatibility

Use the [company runbook](COMPANY_HANDOFF_2026-10-29.md) with the exact supplied
commit and a newly validated asset packet. Configure secrets privately; never
copy a developer's dotenv file or QA database to the recipient.

Run the normal database preparation / migration procedure before starting the
new API. Migration 032 adds account session versions and refresh-session rows.
Migration 033 repairs a historically missing document-task binding column and
index, including databases previously stamped past its original introduction.
Both the fresh migration graph and the repair path were tested.

Existing unversioned sign-in tokens require one fresh login. Passwords, account
roles and credit balances are preserved. Legacy Microsoft accounts lacking a
saved provider subject may require the normal account-recovery process.
Deploy the matching frontend and API together and use HTTPS on the hosted site.
The OAuth frontend and API must ship coherently: mixed versions fail closed.
Old open tabs should reload and restart sign-in. OAuth requires tab-scoped
session storage and Web Crypto; password sign-in remains available.

`TRUSTED_PROXY_CIDRS` must describe the actual reverse proxies; a universal
trust range is rejected. Keep the configured JWT algorithm restricted and use
a private, random HMAC secret for the standard `HS256` configuration. For
isolated workers, set `DIRECT_3D_QUEUE_NAME` and `CELERY_DEFAULT_QUEUE` consistently
on the API, worker and scheduler; the direct-render maintenance queue appends
`-maintenance`. Do not attach a review worker to another environment's queues.
Production signing keys must contain at least 32 bytes and be generated randomly;
the startup guard cannot prove that a supplied value has sufficient entropy.
Replacing a previously weak production signing key requires users to sign in again.
These source changes do not reconfigure any existing desktop containers.

## Verification and evidence boundaries

- Full upgraded backend after the reviewed OAuth fixes: **3,133 passed, 3 skipped**, using a fresh disposable
  PostgreSQL database migrated through 033. The test database was removed.
- Full frontend including the OAuth flow: **4,226 passed, 23 skipped** under
  Node 20. Full TypeScript, strict ESLint and the existing dead-code check pass
  after the build-environment changes. The combined catalogue / public-environment
  suite passes **92 tests**, including actual Vite dev and production transforms
  of synthetic private canaries. The relevant public-flag checks pass **42 / 42**.
- Full backend Ruff / Black checks and the existing mypy boundary pass. Real
  Redis concurrency admitted 10 of 100 simultaneous requests at a cap of 10,
  and retained only those 10 entries.
- Real 29.4 MB and 10.6 MB third-party CC0 GLBs passed import and exact-byte
  authenticated readback; the latter contains approximately 150,000 faces.
  Browser file-transfer automation remains blocked by the Edge
  extension's file-URL permission; this is not a passed file-chooser test.
- Student browser trials saved and reloaded five routes, including a 333 m
  greenway, a 320 m street, oblique intersections and a ground path across a
  building plot. The report reflects the saved route counts and areas.
- A browser regression proves Import GLB receives its first physical click while
  terrain preparation is still pending, and retains the file selection afterward.
  Project name fields now expose their existing labels to assistive technology.
- All **13** existing offline browser workflows and the separate **1** startup
  regression pass under Node 20 with an empty environment directory and mocked
  providers. These are separate from the blocked interactive keyed-browser trial.
- Independent reviews examined the account, input and job-access changes, then
  the UI regression fixes. Reproduced important findings were fixed and retested.
- OAuth protocol tests passed **149 / 149** with real isolated Redis and
  PostgreSQL, including concurrent redemption, reset / disabled-user checks and
  both providers' first-login commit visibility. Its 70 focused frontend checks
  passed, with 21 independently rerun by the reviewer.
- Deployment-secret and network-boundary checks pass with synthetic credentials
  and parsed source profiles; CI runs them before the separate publication gate.
  They do not establish actual image-layer or running-firewall behavior.

The fresh portable production packet contains **186 choices, 585 distinct
dependencies and 3,730 public files / 1,672,384,795 bytes**. Its payloads and
source fingerprints verify. This is storage size, not initial download size or
individual visual acceptance. The 15 development-only choices remain outside
that production baseline. The configured hosted build must retain the original
600 KiB initial-JS, 8,448 KiB total-JS, 3,584 KiB largest-chunk and 192 KiB CSS
budgets. Deliver its matching commit-stamped receipt with the output; a smaller
keyless build is not evidence for the Maps-enabled application.

The retained local QA environment uses a separate database, secret and worker
queues. Its fixture contains only the selected review account/project/catalogue
data; no original project was used for destructive test cases. Original local
services and projects remain available.

## Open release items

1. Seven catalogue pilots still require their successful trial evidence and
   human activation approval. Publication preflight correctly rejects them.
   Local visibility and an asset hash match do not grant publication approval.
2. The resolved dependency audit still reports advisories in Black,
   python-jose and its ecdsa dependency. Alias records are not distinct
   vulnerabilities. Black is a developer tool; its formatter migration is
   deferred. The current restricted HMAC JWT path does not use the advisory's
   asymmetric signing/key-generation paths. No clean audit is claimed.
3. Cross-tab refresh in browsers without Web Locks and server-side logout
   revocation remain follow-up items. Historical proxy / telemetry logs and
   previously built image layers were not audited or retroactively erased;
   no actual credential leak was observed in this work.
4. A clean Linux/Python 3.11 container installation, Linux prefork integration,
   actual U2-Net inference and recipient-hosted acceptance remain unverified.
   Native decoder/process isolation and infrastructure controls require the
   deployment operator's configuration and review.
5. Draco-compressed and GPU-instanced imports require the documented re-export
   or bake step. Valid large models are supported within bounded resource
   limits; arbitrary malformed or unbounded GLBs are deliberately rejected.
6. Windows Security currently blocks interactive browser input with a network
   permission prompt. No additional firewall access was granted. Remaining
   placement/walking/free-export and paid image/video trials are not passed.
   The overnight allowance is 10 image submissions and 5 videos; none has been
   submitted at this checkpoint.

Detailed raw test logs, audit receipts and delivery manifests are retained
outside the source tree. Credentials and attack fixtures are not included in
the company-facing media folder. Completed review screenshots are in the
private [overnight Drive batch](https://drive.google.com/drive/folders/1uw6fkI26aznA57wdl5cinfpH4l_AuFgC).
