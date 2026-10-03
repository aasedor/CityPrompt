# Exact catalogue local validation installation

Dedicated source: `C:/dev/CityPrompt-approved-validation`, branch
`codex/approved-catalogue-validation`, based on `d565a47b0`.
App: http://127.0.0.1:5180; API: http://127.0.0.1:8006.

This local-only integration exposes 27 exact versions: 12 buildings, eight parks
and seven streets. The source inventory is `frontend/src/data/validationCatalogue.json`.
It combines the 21 adopted quality baselines with six priority upgrade candidates;
it does not confer runtime acceptance, keeper approval or production publication.
Old source reference catalogues and other worktrees are preserved.

The twelve buildings use exact Model Library bindings in a new local database
and object bucket. Main/Market use native route module manifests; basketball and
teaching garden use upgraded modules through the existing adaptive fitter.
The six baseline parks and five baseline streets are fixed native review
fixtures. Their extension, arbitrary shape/route and station-editing integration
remains a classroom blocker. They are labelled accordingly, with resize controls
guarded. Their authored ground and geometry are preserved on prepared terrain.

The separate local environment uses database `cityprompt_validation_20260924`,
bucket `cityprompt-validation-20260924`, and Redis database 6. Existing projects,
databases, catalogue installations and ports 5174/8088 are untouched. Paid
generation providers are disabled. No browser session was run by Codex.

External handoff directory:
`C:/dev-artifacts/CityPrompt/approved-validation-2026-09-24`.
It contains the credential-bearing `CLAUDE_STUDENT_VALIDATION_PROMPT.md`,
`start.ps1`, `runtime.py`, `roster.json`, exact building bindings and
`http-preflight.json`. Do not commit private environment files or credentials.
The prompt specifies ordinary student UI authoring, finite per-model checks,
known gaps, terrain/edit/reload/export acceptance and a 27-row results matrix.

Run `scripts/prepare_validation_catalogue.py` only with the pinned external
catalogue evidence available. It verifies hashes and creates the finite static
asset installation; it does not manufacture geometry or approvals. Runtime
bootstrap is intentionally external and restricted to this separate local DB.

Non-browser validation: 47 focused frontend tests and TypeScript checking passed, native building plan
and authenticated storage readback passed for all twelve, and all 27 static GLBs
and thumbnails were served successfully with exact hashes. Native street module
hashes were checked through HTTP. Browser acceptance is deferred to Claude Code.
