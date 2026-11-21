# City Prompt student-release checklist

This is the active release gate for the first clean City Prompt release. It
replaces the historical MVP schedule, which no longer described the current
application.

## Release definition

The application is student-ready when a fresh clone can complete the core
workflow without repository knowledge:

1. configure the documented local environment;
2. start the stack;
3. register and sign in;
4. create a project and site;
5. draw, edit, and save zones;
6. assign available building and public-realm archetypes;
7. generate and refine a master plan;
8. open the 2D and 3D views;
9. use every catalogue item marked available; and
10. save, reopen, and export the result.

Provider-dependent AI features must either work with a configured key or show
a clear disabled/error state. An incomplete asset must never appear as fully
available.

## Repository gates

- [x] Latest fixes can fast-forward onto local `deployment-version`.
- [x] Broken nested-repository metadata is removed.
- [x] Tracked smoke output and obvious root-level binary clutter are removed.
- [x] Forbidden legacy public-asset trees are removed.
- [x] Public documentation consistently names City Prompt and
      `deployment-version` as the canonical branch, with `main` frozen and unused.
- [x] All Markdown links resolve, excluding explicit external or archived
      historical references.
- [x] No credentials or local-machine secrets exist in the current tree.
- [x] ESLint 9 has a flat configuration and passes.
- [x] CI treats lint, type-check, tests, build, security audit, bundle budget,
      and asset validation as required.
- [x] Runtime assets have a generated, reproducible manifest.
- [ ] Compiler output and visual-QA batches are outside the source repository.
- [x] Unreachable application code is removed in verified subsystem-sized
      commits.
- [x] Catalogue entries are generated and classified as complete, partial, or
      unavailable; selectors expose only usable references.
- [ ] Merged pilot branches contain no unique deliverables before retirement.

## Verification gates

- [x] Frontend lint passes.
- [x] Frontend type-check passes.
- [x] All frontend Vitest tests pass (1,054 tests).
- [x] Production frontend build and enforced bundle budget pass.
- [x] Backend pytest suite passes (1,063 tests).
- [x] Archetype and Sticker Method asset checks pass.
- [ ] Compiler tests pass against hydrated image assets (current unhydrated
      checkout: 547 passed, 86 failed, 55 errors).
- [x] Controlled browser smoke passes 13 current auth, project, and integrated
      3D-workspace tests with no uncaught page errors, unexpected HTTP errors,
      or console errors.
- [x] A depth-one clean checkout passes `npm ci`, the controlled browser suite,
      production build, bundle budget, and the unhydrated manifest check.
- [ ] Fresh-clone Docker startup passes.
- [ ] Fresh-clone student workflow passes end to end.

## Release steps

- [x] Direct the receiving team to `deployment-version`; `main` stays frozen
      at its 3 October 2026 state.
- [ ] Make required GitHub checks mandatory in branch protection on
      `deployment-version` (only `main` is protected today).
- [ ] Remove merged remote pilot branches only after unique-commit and asset
      audits.
- [ ] Tag the first clean release.
- [ ] Record the tag, test evidence, known optional-provider requirements, and
      asset-manifest checksum in release notes.

Until every verification gate is checked, the repository should be described
as release-candidate work, not as flawless or fully student-ready.
