# Current local version readiness

Scope: verify the current City Prompt version for the LuxModus handoff. Keep
GitHub access, deployment, paid generation, and catalogue publication unchanged.
Starting revision: b0ab52f2d. Initiative: codex/luxmodus-readiness-20261028.

1. Run TypeScript, the full frontend/backend suites, and the production build.
   Reproduce failures narrowly before making small fixes and rerunning checks.
2. Check catalogue delivery and repository hygiene. Keep external model assets
   and unapproved local catalogue pilots distinct from releasable source.
3. Exercise the running localhost:5174 app through the browser: project load,
   existing detailed GLBs, tower storey editing/reload, site context, and the
   free video route workflow. Use QA projects and no paid render submissions.
4. Record fresh evidence, remaining failures, and unrun checks under
   C:/dev-artifacts/CityPrompt/luxmodus-readiness-20261028. Report a precise
   tested revision, rather than implying the local branch is already on main.

Initial findings: TypeScript passes. Backend collection fails because the
repository-root scripts namespace is absent when tests run from backend/.
The existing brick-podium tests reproduce the failure before correction.
Configure pytest's repository-root search path explicitly and rerun those
tests, then the full suite. Do not remove the tower tests or alter model data.

Execution record: see `docs/LOCAL_READINESS_2026-10-28.md` and the external
evidence directory. The full original frontend and corrected backend suites
passed. Compatible dependency patches cleared npm audit. Final frontend
verification follows splitting the overloaded aggregate street-selection test
without reducing its coverage or increasing its timeout. Browser preview,
deletion, tower persistence, imports and reference data were checked. Source
and generated assets stay separate; keep this initiative local for now.
