# Main merge readiness — 2026-10-03

## Result

The requested integration is prepared in [PR #29](https://github.com/aasedor/CityPrompt/pull/29).
It has no Git conflicts, but required release checks block merging. Main remains
`42b262f0d0106757073524e9b980364758c06fdc`.

The integration starts from `2f2c993669c94c25f5975c75fc192546be18dc88` on
`codex/large-civic-archetypes`: 156 commits accumulated after main. The separate,
unfinished neighbourhood essentials work is excluded. The live browser checkout,
database, project and external model packages were preserved.

The user's merge request authorizes this integration. The blockers below are
failed technical/release checks, not a request for another general merge approval.

## Verified cleanup

- Backend formatting and lint now pass. Of 81 changed Python files, 73 have
  identical syntax trees. The remaining changes replace two assigned lambdas,
  remove unused test imports, and preserve intentional task exports and pytest
  fixture registration. Backend mypy also passes for the CI boundary.
- Frontend lint, TypeScript checking and dependency reachability pass. Park
  effects now include their actual dependencies; generated building dimensions
  use nanometre precision to avoid Python/JavaScript decimal-printing drift.
- All 13 Playwright workflows pass after mocking the read-only render capability
  endpoint. Image and video controls are still asserted in the browser.
- 34 targeted frontend tests and 18 API/auth dependency regression tests pass.
- 18 catalogue-promotion tool tests pass. Metadata validation with local trials
  explicitly included passes for all 23 entries; this is not a release pass.
- 30 targeted backend tests pass; 10 PostgreSQL-dependent cases are skipped in
  this local check because no isolated test database was configured.
- Available dependency fixes update Axios to 1.20.0, brace-expansion to 1.1.21
  and 5.0.12, and Undici to 7.30.0. A fresh isolated `npm ci` and production
  build pass. The running preview's dependency directory was not modified.

## Remaining blockers

1. **Catalogue release records:** 14 seed-library entries still have
   `local_trial_only: true`. Three record six of the eight required checks;
   eleven record none in their local-trial field. Their activation records are
   absent. Complete and record the actual exact-model trials before release;
   do not infer missing results or flip flags to satisfy CI.
2. **Asset portability:** the tracked runtime-manifest check reports 33 missing
   direct references, including native park assets and street pilot reference
   images. Recover the exact reviewed files, publish them through the existing
   LFS/artifact workflow, and regenerate and verify the manifest. Local church
   review packages also remain external as documented in their trial runbook.
3. **Regression suite:** at the starting commit, the full frontend run had
   25 failing tests and two suite-import errors (14 failed files; 2,512 passing
   tests). A full rerun after cleanup and dependency updates has the same
   failures and pass counts. The backend CI run had 32 failures, 1,881 passes
   and 26 skips. Failures
   include outdated catalogue expectations, unhydrated model bytes, placement
   contracts and render settings fixtures. Resolve each against the intended
   current behavior; do not simply remove assertions or accept new counts.
4. **Dependency security:** the audit still reports five high-severity entries
   from the Tailwind 3 dependency chain through `braces`. The
   [upstream advisory](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) lists
   no patched version. npm proposes a breaking Tailwind 4 upgrade. That needs a
   separate migration and visual verification, or a maintained compatible fix;
   the audit threshold has not been weakened.
5. **Repository blob limit:** both copies of `nativeStreetPilots.json`
   (1,118,053 bytes each) and `buildingArchetypes.json` (2,341,883 bytes) exceed
   the 1 MiB ordinary-Git limit. The building catalogue was already oversized on
   main, but this integration touches it. Split/compact the data with compatible
   consumers and generators; preserve the repository's text-only catalogue
   editing rule. No blanket exemption was added.
6. **Bundle budget:** the production build succeeds, but total JavaScript is
   9,501.7 KiB against the existing 8,448 KiB budget. The largest chunk and CSS
   pass their individual budgets. Reduce shipped code/data before claiming the
   complete frontend release check passes.

## Evidence and workspace

- Initial [required CI run](https://github.com/aasedor/CityPrompt/actions/runs/37129125896).
- Initial [complete backend run](https://github.com/aasedor/CityPrompt/actions/runs/37129125895).
- Isolated integration checkout:
  `C:/Users/andre/.codex/worktrees/working-state-merge/CityPrompt`.
- Local logs and generated build/test output are outside tracked source, under
  `C:/dev-artifacts/CityPrompt/working-state-merge-2026-10-03/` or ignored
  frontend output directories. No generated asset directory was staged.

Continue release repair in this isolated checkout. Re-run the relevant failed
checks, then the required PR checks. Merge only after they pass; main's branch
protection remains enabled.
