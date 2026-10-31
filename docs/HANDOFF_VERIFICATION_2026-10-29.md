# Company handoff verification — 29 October 2026

The fresh local student exercise passed core authoring. This checkpoint does
not certify a recipient installation, hosted deployment or paid-provider output.
Production changes are in `bfcae57d9`; the matching asset packet and static build
record that commit. The later request-bound HTTP test fixture is `d39519c67`.
Nothing was pushed or deployed.

## Confirmed results

| Scope | Evidence |
| --- | --- |
| Fresh browser authoring | Project `324a8846-e4b6-4efc-9ae5-ac5d62220d10`: address search, saved four-corner boundary, oblique junction between two street types, diagonal pathway crossing roads, detailed café/apartments, pocket garden, park Delete/Undo/Redo and persistence. |
| Frontend baseline | 476 suites / 4,089 tests passed; TypeScript passed. |
| Final credit UI | Four suites / 55 tests passed; TypeScript passed. Includes free capture without a paid request, unavailable metadata and stale-account responses. |
| Backend focused checks | 91 credit, admission, responsiveness and reservation checks passed. |
| Final full backend | 2,706 passed, 71 skipped, zero failed in 452.13 seconds. Seventy applicable opt-in checks are covered by the separate isolated batch; the Linux prefork check remains unrun. |
| Isolated integrations | 89 passed, zero failures/skips: real PostgreSQL, Redis and private S3; credit rejection, duplicate handling, 60-student queue exercise, persistence and image/video recovery. Providers were stubbed. |
| Isolated cleanup | All three disposable databases absent, six temporary buckets removed, Redis test namespaces empty. Shared student data was preserved. |
| Catalogue delivery | Production: 186 choices, 578 dependencies, no failures. Development: 201 choices, 607 dependencies, no failures. These are file/contract audits, not individual browser visual approval of every asset. |
| Stored models | 111/111 present; 19/19 selected catalogue models matched exact readback bytes. |
| Portable packet | 3,723 files / 1,667,410,799 bytes; 4,583 current source fingerprints and payload hashes verified. Production profile excludes local trials. |
| Final static build | Compile and TypeScript build passed in 87.33 seconds. Four bundled landing media match exact committed LFS bytes; zero pointer or environment files. Version/service-worker identity stamped for `bfcae57d9`. |
| Other guards | Landing media: four tests plus exact source check passed. Catalogue numeric comparison: 38 tests passed. Twelve policy maps / 724 hydrated images passed; both Beltline maps returned the expected source features. |
| Running local services | After final API restart, frontend HTTP 200; `/health` healthy; `/ready` ready for enabled dependencies/workers. Classroom release mode is false. Authenticated image-model discovery returned the QA editor's correct zero balance and minimum costs. |
| Saved scene readback | Read-only HTTP after API restart confirmed six zones: one boundary, three routes, one building and one green space. |

The initial full-backend run found nine stale length assertions. They were
corrected, rechecked, and the final full rerun above passed. The final static
build was created while documentation and the request-bound test fixture were
being finalized, so its receipt truthfully records `source_dirty: true`.
Frontend production inputs match the verified packet fingerprints.

## Corrections made

- The paid-image UI checks authenticated effective credits and all selected
  engine minimums. The API checks exact capture cost before consuming a trial
  slot or admitting a new job; existing jobs remain recoverable.
- CPU-heavy admission validation runs in a bounded two-worker pool without
  retaining a database connection or global admission lock. Tests cover
  responsive recovery, expired ORM state, duplicate races and cancellation.
- Builds reject missing/corrupt landing media and LFS placeholders. Four exact
  committed source originals were hydrated from local cache; no asset revision
  changed.
- Publication metadata comparison accepts equivalent numeric spellings while
  preserving string, value and wrapper checks. Nine stale assertions now match
  the existing 2 km route policy.
- The [company runbook](COMPANY_HANDOFF_2026-10-29.md) documents the matching
  assets, database/storage, keys, workers and scheduler needed for reproduction.

## Remaining acceptance gaps

1. Both external nearby-road providers timed out, including independent minimal
   requests. Manual road authoring passed; nearby lookup is not a pass.
2. Computer Use stopped because it could no longer verify the active browser
   URL sufficiently to enforce policy. It was not retried or bypassed. A free
   export click was interrupted and no file was verified. Actual free browser
   export, video preview, fresh GLB upload and post-fix credit UI need rechecking.
3. No paid images/videos, purchases, deployments, sharing changes or Git pushes
   were performed. Provider configuration is not output-quality or billing proof.
4. Linux prefork integration remains unrun on Windows. A clean recipient install
   and hosted HTTPS frontend/API build remain untested. The static review build
   requires same-origin API routing.
5. Fifteen development-only choices are outside the 186-choice company baseline.
   The stepped terraced plaza still has an unresolved P1 visual review and is
   excluded from that production baseline.
6. Broader historical hydration checks remain separate failures: 1,981 missing
   or pointer inputs in the desktop root, and an unhydrated reference image in
   full source-checkout publication preflight. Active catalogue delivery and
   metadata-only publication passes do not approve those gates.
7. The configured production build exceeds the total JavaScript budget:
   8,904.18 KiB versus 8,448 KiB. Initial shell (475.6 KiB), largest chunk
   (2,841.3 KiB) and CSS (190.3 KiB) pass their budgets. The configured pre-credit
   build already failed; the credit fix adds 1,542 bytes. An earlier smaller
   keyless build omitted the Maps/globe route and is not a valid working-map
   performance baseline. No budget was relaxed. Treat total bundle size as an
   open performance/release gate, even though compilation passes.

Review screenshots and receipts are in the private
[Google Drive batch](https://drive.google.com/drive/folders/1yFgJqVcpEoLAGfGEvxkTZnQnaWrNlN7M).
The JPEGs are exact source screenshots, not AI originals or exported render
files. No generation job IDs exist for this round.
