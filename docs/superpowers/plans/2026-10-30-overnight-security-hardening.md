# Overnight security hardening and release QA

> Execute with the systematic-debugging, test-driven-development and dispatching-parallel-agents workflows. One owner per security boundary; review the combined diff before committing each coherent unit.

**Goal:** Repair reproduced security defects and exercise the current City Prompt candidate for the user's morning review, preserving student workflows and the verified source checkpoint.

**Authorization:** On 30 October the user requested autonomous overnight testing/fixing, explicitly including cybersecurity work, and allowed 10 images plus 5 video renders. This is maintenance under the existing product design, not a new feature/design consultation. Existing catalogue keeper and live-deployment approvals are not implied.

**Baseline:** `d405cda4437cc6accc9d89931f42b917ce06a527`, preserved on `codex/deployment-handoff-20261029` in draft PR #38. Work in the already-isolated checkout on `codex/security-hardening-20261030`. Nine pre-existing hydrated media/model status entries match committed LFS payloads and are outside this initiative.

**Architecture:** Retain FastAPI, SQLAlchemy/PostgreSQL, existing JWT/OAuth and storage boundaries, React and the established render pipeline. Repair authorization/session invariants server-side, bound untrusted input before decoding, and preserve current student flows. Use isolated test schemas and mocked paid providers for regressions. Keep attack proofs and private credentials outside public Git.

## Work ownership and independently testable units

- [x] Authentication owner: reproduce/fix email-only OAuth credential retention, provider identity binding and disabled-account behavior; password change/reset revocation and reset replay; meaningful auth regression tests and minimal migration if necessary. Own auth/OAuth/core security/user-model/migration files; coordinate configuration/rate-limit changes explicitly.
- [x] Untrusted-input owner: reproduce/fix compressed GLB declared allocation bypass and compiler-manifest validation bypass; bound shapefile archive work; give reference PDFs a genuinely text-only path and budget raster modes. Own upload/validation/extraction services and their routers/tests, excluding documents.py/buildings.py and core auth.
- [x] Background access owner: reproduce/fix unscoped document task status and arbitrary preview source URL fetching. Own documents.py/buildings.py, preview task/service and their tests. Preserve tenant revocation and classroom gates; no generic HTTP fetcher accepting client-supplied URLs.
- [ ] Coordinator: trusted-client IP and provider-quota boundary review, dependency security audit, integration/migration/quality checks, local browser regression testing and finite render batch. Avoid overlapping agents' files; handle remaining issues after their patches are reviewed.

## Verification per security unit

1. Read the actual current code and prior private security finding; reproduce with a small safe fixture.
2. Add a focused regression and observe the correct failure, without resource exhaustion, live attacks or provider calls.
3. Implement the smallest durable fix; retain normal owner/student behavior tests.
4. Run narrow pytest/Vitest checks, formatting/lint and relevant schema/migration checks. Preserve failing/unrun checks explicitly.
5. Review the diff and test evidence, then commit only that unit's intended source/tests.

## Integration and delivery

- [x] Review all patches for tenant isolation, old-session behavior, migration safety, bounded decoding and API/client compatibility.
- [x] Run full backend/frontend tests and existing lint/type/build/catalogue/runtime guards after the final edits. Obtain an independent review.
- [ ] Exercise the browser as a student on a disposable project, including save/reload, import, walking, streets/intersections and free capture. Preserve existing projects and the original 5174 server.
- [ ] Produce at most 10 image submissions and 5 video submissions in City Prompt. Five photographic guide images plus five additional stills is the initial allocation; guides count within the ten. Use source-locked scenes, people/characters, close views and the established photographic-guide-plus-polygon-video process. Recover durable jobs rather than submitting duplicate paid retries. No credit purchases.
- [ ] Deliver completed originals/source captures/comparisons and labelled screenshots to a dated private subfolder under Drive `1ShDXmefQd-1bUGqPN3pK9dGAHrxcLvXZ`; verify metadata and record IDs/quality/missing outputs in the local manifest.
- [ ] Update the review candidate only after relevant verification, preserve the rollback source and keep PR #38 draft while publication gates remain. No shared deployment-branch update, keeper promotion or live deployment is authorized by this overnight task.

## Verified source checkpoint

- `5f546df5895f1d44d58adf682e7bacb765b6de28`: account/session, upload-resource and background-job hardening, additive migrations032/033, quota admission, frontend refresh/cache compatibility and regression tests.
- `fcca92f23d762fa69e7735142667a36bd942740a`: compatible dependency security upgrades with explicit cached U2-Net selection.
- `b209537c870c0c8fb6922d62235c114ead38eb2b`: validated queue names preserve production defaults and allow local/staging worker isolation;81 focused checks passed, with14 opt-in skips.
- Upgraded-environment full backend suite, including queue isolation: **3114 passed, 3 skipped** in a disposable PostgreSQL database migrated from scratch; that database was removed after the run.
- Frontend full suite: **4208 passed, 23 skipped**, under both the local Node24 runtime and the configured Node20 runtime. TypeScript and ESLint pass.
- Backend full Ruff/Black checks and the existing mypy boundary pass. Migration graph/repair checks pass. Real Redis concurrency admits10 of100 simultaneous requests at a10-request cap and stores only10 entries.
- Two independent code reviews completed; reproduced important findings were fixed and verified. No security certification is implied. Existing OAuth query-token delivery, unsupported-browser cross-tab refresh, native process isolation and unpatched dependency advisories remain documented limitations.
- Configured hosted-build preflight passes: initialJS466.2KiB, totalJS8447.9KiB/8448KiB, CSS190.3KiB/192KiB. The186-choice release asset packet verifies3730files/585dependencies without catalogue activation. A final commit-stamped build remains part of delivery.
- Publication preflight remains blocked by human activation for the seven previously identified pilots. Exact LFS model/reference bytes were hydrated and verified first. No guard was bypassed and no shared deployment branch or live deployment changed.
- Browser/render evidence and delivery are continuing in the private overnight batch; source commits and ignored outputs are recorded separately.

## Morning continuation

Heartbeat `city-prompt-overnight-hardening-and-qa` provides bounded continuation during the night. Stop paid submissions by 08:30 America/Edmonton on 30 October. Shared budget, durable receipts, rulings and remaining work live in `C:/dev-artifacts/CityPrompt/overnight-hardening-20261030/`; consult them before resuming. Report exact completed fixes, verification results, remaining release blockers and actual delivered media, without claiming a security certification.
