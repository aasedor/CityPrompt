# Student UI simplification implementation plan

> Agentic workers: use the debugging, focused-test and verification workflows. Execute the user's approved list in this chat; no further design approval is needed.

**Goal:** Reduce classroom UI clutter, repair the reported import/detail/people defects, and add the requested ground-finish and quantitative-report controls.

**Architecture:** Preserve existing saved data and renderers. Remove redundant entry points, expose only supported model controls, and reuse polygon drawing and prepared ground for surface finishes. Keep exact source identity and normal depth occlusion. Distinguish missing quantitative data from zero.

**Stack:** React/TypeScript/Three.js, FastAPI/PostGIS, current local runtime.

**Spec:** The user's item-by-item approved requests immediately preceding “Please implement and test.” Perpendicular street labels means 90 degrees to the road bearing as explicitly requested. About 25 surfaces means 25 named finishes. Unsupported malformed files still need a readable error; valid complex GLBs must not be rejected merely by a standard-building complexity threshold.

## Constraints and ownership

- Existing linked worktree, branch codex/student-ui-simplification-20261029, clean base 9075331cc.
- Local changes and disposable projects only; no push, deployment, paid generation or catalogue publication.
- Parallel independent workers: GLB ingestion/imported editor; map zoning/policy/labels; people poses and quantitative report. Root owns shared ProjectViewPage, toolbar, ReshapePanel, StreetRoutePanel, details and ground surfaces. Workers must not edit root-owned files.
- Preserve saved entrance/connection data for compatibility while removing its authoring UI. Do not make old connections block normal rendering.
- Original source screenshots and notes go to the existing private Drive review parent, in a dated child folder; verify metadata and retain receipts.

## Tasks

- [x] GLB: reproduce 45 MB complex-file rejection, remove arbitrary geometry complexity gate while retaining structural validation and bounded parsing; meaningful backend tests. Simplify imported model menu to Name / View Model / Delete zone, repair close behavior, and preserve import metadata and complete model transforms.
- [x] Maps: make zoning available on and around saved sites; add unchecked-by-default “Only show zones within site boundary” filtering, retain click interaction. Research authoritative Beltline plan sources and integrate supported policy geometry, honest metadata/legend/matching. Orient street names perpendicular to street bearing where renderer supports it. Focused tests.
- [x] People/report: diagnose action retargeting and arm/chest intersections; verify representative actions on actual supported rigs. Replace report question/response UI with counts, floor area (m²/ft²), residential/retail units, public-realm totals, sources and explicit missing/estimated data. Test real calculation edge cases.
- [x] Menus: remove Finish your site/AI landscaping; remove requested redundant More tools entries and all Connections/Review entrances UI. Keep main Walk/render/catalogue controls. Hide unsupported GLB plot/outline resizing while retaining working tower storeys. Check simple removals in browser without mirrored tests.
- [x] Ground/details: diagnose below-ground placement; correct prepared-site seating and marking visibility without disabling depth tests. Add editable flat ground polygon with 25 finishes, overlaps permitted against archetype plots, correct save/Undo/Redo/reopen and persistence. Add regressions for geometry/material/placement logic.
- [x] Integrate and review all touched components, focused Vitest/pytest/type-check, diff checks. Browser test each request with a truthful pass/fail matrix and screenshots. Upload verified evidence and commit coherent tested units; final response must disclose any remaining gaps.

## Review focus

Complex GLB with many nodes/accessors must load without removing malformed-data checks; imported close must clear both model and zone selection. Ground finishes must not paint walls or disappear under shallow caps. Empty/unknown floor area and unit counts must not become fabricated zeroes. Existing projects and hidden legacy controls must remain usable. Beltline policies must use authoritative boundaries, not fabricated coverage.

## Acceptance checkpoint

Implementation and local checks complete. See docs/STUDENT_UI_SIMPLIFICATION_2026-10-29.md for the per-request browser matrix and explicit blocked new-file upload trial. That upload is not claimed passed; existing imported model controls and preview are browser-verified. Generated evidence stays outside tracked source.
