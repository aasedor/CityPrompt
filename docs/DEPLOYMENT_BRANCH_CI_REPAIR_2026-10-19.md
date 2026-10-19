# Deployment branch preflight: backend CI fixture repair

The user requested pushing the reviewed parking/parkade work to
`deployment-version`. Before promotion, PR #33's backend job was checked:
run `39099220972` failed with 35 failures, 2,248 passes and 45 skips.
The release branch was not updated while that check was failing.

The failed job exposed two existing test-infrastructure problems:

- Checkout deliberately leaves historical Git LFS objects as pointers. Backend
  tests need a finite set of actual starter, flexible-house, Claude-trial and
  traffic-detail binaries. CI never downloaded them. A new manifest-driven
  helper selects exactly 38 required files, downloads only those paths and
  verifies their pinned SHA-256 hashes before testing. Both backend workflows
  use it. Global LFS policy and the runtime model validators are unchanged.
- Eight assertions/mocks were stale against the already deployed contracts:
  Haussmann's canonical alias, 118 public-realm street parents, built Calgary
  local street variants, eight narrow pathways including the three sidewalks,
  the renderer's `project_details` keyword, and its explicit image/job settings.
  The six affected test files now exercise those current contracts. Unknown
  variants and changed binary bytes still fail; no test was disabled.

The original eight failures were reproduced locally before edits. The first
finite fixture download/hash check passed for all 38 files. After updating the
expectations, all ten affected backend test files plus the helper integrity
tests passed: **313 passed, one optional disposable DB/S3 integration skipped**.
The helper's tests reject pointer files and altered payloads; the recipe tests
still reject unsupported Calgary variants and forged junction components.

This repair changes CI setup and test fixtures only, not application behavior.
It does not approve or enable the local-only parkade catalogue gate, publish
models to production storage, buy renders, or change any service settings.
The separate frontend/local student checks remain recorded in the parking and
parkade trial reports. GitHub must rerun the fixed workflow before promotion.

The original failed log is external at
`C:/dev-artifacts/CityPrompt/parkade-family-2026-10-17/pr33-ci-failure.log`.
