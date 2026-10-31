# Court-only sports implementation

Spec: `docs/superpowers/specs/2026-10-24-court-only-sports-design.md`
Base: `ca6c65e97`; branch: `codex/court-only-sports-20261024`.
Execute inline in the existing clean attached worktree. Ledger and heavy output:
`artifacts/court-only-sports-20261024/`. No push or deployment.

## Task 1 — reusable court geometry

Write failing Python tests for independent court-only specifications, fixed
playing/reserve dimensions and preservation of the full garden specifications.
Add a backward-compatible enclosure option to the existing sports builder and
a finite standalone builder. Dry-run, build basketball, inspect actual GLB
renders, then build tennis, pickleball and beach volleyball. Independently verify
the exported bounds, surfaces, equipment heights and absence of amenities.

Expected: four self-contained exact GLBs; no fence/landscape geometry; unchanged
default garden behaviour. Run `python -m pytest tools/public_realm_assets/test_court_only_specs.py tools/public_realm_assets/test_court_specs.py -q`.

## Task 2 — local catalogue integration

Test discovery, fixed dimensions, native placement binding and existing parks.
Register the reviewed four packages in synchronized native park registries and
a separate court-only catalogue. Expose only local pilots and preserve all old
IDs/revisions. Append after the legacy full-park decoration step. Use existing
fixed-native capability rules to suppress resize handles.

Expected: searching court only finds four local choices. Native recipes stay
hash-bound and reject undersized parcels. Run narrow Vitest and native-park
backend contract tests; run `npm run type-check`.

## Task 3 — student review and delivery

Use the local app as a student to assemble a mixed athletic park, repeat and
rotate courts, check handles, undo, save and reload. Inspect 3D and ground views.
Record evidence and limitations. Obtain a fresh branch code review, fix material
findings and rerun relevant checks. Upload source renders and UI screenshots to
a dated Drive subfolder, verify metadata and record file IDs in a local manifest.
Review diff/check/status and commit one coherent verified initiative.

## Review focus

Check that local pilots cannot appear in production discovery unintentionally;
saved exact bindings still resolve; no generic fallback replaces court geometry;
the registrar cannot overwrite existing layouts or partially mutate a batch on
validation failure; correct native dimensions survive rotation/save/reload;
equipment lies inside reserved bounds; no resize controls are offered.
