# Local AI render trials - retired 2026-10-30

The user retired FLUX.2 Klein, Qwen Image and Wan local generation because the
results were below the required quality. The ComfyUI integration is removed,
rather than hidden behind a flag.

## Scope and implementation

- Remove local engine choices, the Local model trials dialog, generation clients,
  backend routes/services, settings and staging environment references.
- Ignore remembered local engine selections and use the discovered supported
  default. Preserve the prompt, project and saved media. Opening the panel never
  submits an image or video request automatically.
- Preserve saved image/video records, source captures and provenance. Historical
  engine labels are display-only. Unretrieved ComfyUI jobs can no longer be
  recovered from the app.
- Keep GPT engines (including Sunburst), Google image rendering, Omni, Kling,
  free polygon captures/previews, imported GLBs and catalogue models.
- Retire no other image-processing utility or machine-wide Python installation.

The former installation was `C:/AI/ComfyUI_windows_portable`; it was already
absent when inspected. The user had deleted the weights. No model download or
replacement installation is part of this change. Saved generated outputs and
external QA evidence are preserved.

## Verification plan

1. Check remembered FLUX/Qwen selections fall back without losing the prompt.
2. Check selectors expose supported engines; run existing cloud render/animation
   tests. Confirm retired endpoints return 404 despite a stale enable flag.
3. Run relevant frontend/backend tests, TypeScript, scoped lint, staging contract
   and the unchanged production bundle budget.
4. Inspect local image/video controls in a browser without paid submissions.
   Review the change before updating the existing draft handoff PR.

Historical experiment details remain in Git history. This change does not
publish catalogue pilots, merge the draft PR or deploy the live site.

## Verification results

- 79 focused frontend tests passed; TypeScript and scoped ESLint passed.
- 36 backend tests passed with isolated PostgreSQL schemas. Two optional S3/Redis
  integration checks were skipped. Five staging configuration checks passed.
- Python lint/format checks and the existing production bundle limits passed.
- Local browser sign-in, image selector and Sunburst-to-Omni video controls were
  checked on port 5177. No paid image or video was submitted.
- Independent code review found no actionable issues. The runtime inventory
  removed only the three retired frontend source paths; assets were unchanged.
