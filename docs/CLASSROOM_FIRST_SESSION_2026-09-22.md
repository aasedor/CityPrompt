# First-session guide and classroom trial pack — 22 September 2026

The next practical checkpoint is an independent novice trial. This change makes
that trial concrete; it does not claim that students have already completed it.
Worktree: `C:/dev/CityPrompt-grounding-edit-race`; branch:
`codex/classroom-first-session`.

## What changed

The placement Guide now covers eight steps: irregular site, street, buildings,
park, edits and Undo, free landscape, saving/reopening, and exact PNG download.
It replaces the inaccurate instruction to drag a building's body with its Move
handle, names the supported catalogue cards, distinguishes fixed buildings from
repeated infill, and explains landscape regeneration after layout edits. Existing
drawing-mode guidance stays intact. The guide ends with “Start designing”.

- [Student exercise](CLASSROOM_STUDENT_EXERCISE.md): approximately 35 minutes,
  four to six buildings, one street, one park, contextual placement, edits,
  Undo/Redo, reload and a downloaded exact image. No paid generation required.
- [Instructor observation sheet](CLASSROOM_TRIAL_OBSERVATION.md): setup, clear
  independent/helped outcomes, observed frustrations, debrief and catalogue needs.

## Verification

The live check used the existing disposable Currie project
`3a52b4df-8508-408e-ac20-2f674d7c23b9` on isolated services `5175/8001`.
All eight guide steps fit at 1440 × 1000 and 1280 × 720; the smaller-screen run
also confirmed focus remains inside the guide. Next/final dismissal and reopening
worked. Recommended Infill homes, Beltline brick mixed-use mid-rise, Calgary local
street and Teaching demonstration garden cards were discoverable by name. The
teaching garden thumbnail loaded successfully after waiting for the image.
The browser reported no uncaught errors. Project zones were unchanged and the
visible balance stayed at 4,057 tokens. No paid provider was called.

Focused guide/workflow tests: 2 files, 9 tests. Type-check and focused component
lint passed. The new test verifies the placement instructions and that traversing
the guide does not activate underlying project or generation controls. Existing
tests retain keyboard focus, Escape, legacy guidance and missing-target coverage.

Evidence is outside source control at
`C:/dev-artifacts/CityPrompt/classroom-first-session-2026-09-22/`:
`guide-steps.json`, `guide-laptop.json`, `guide-step-*.png`, `guide-laptop.png`,
`catalogue-search.json`, and `catalogue-teaching-loaded.json/png`.

This turn checks guidance and discoverability, not another complete authoring or
export run. Actual road edits, Undo/Redo, reload and native PNG download remain
recorded in [the preceding ground/export check](CLASSROOM_GROUND_EXPORT_2026-09-22.md).

## Next checkpoint

Run the exercise with one or two new students on their own projects. Record help
honestly, fix blockers they encounter, then choose a small catalogue batch from
their actual requests. Follow the shared runtime integration contract for each
exact variant. There is no new archetype approval, Wave 2 activation or hosting
rollout in this change. Small tile seams and natural-ground coverage limitations
remain as previously documented. No push.
