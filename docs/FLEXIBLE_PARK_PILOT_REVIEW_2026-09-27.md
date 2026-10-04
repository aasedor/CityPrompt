# Flexible parks pilot — local review

These two shape-first choices supplement the eight fixed native parks. They use existing measured public-realm recipes and are deliberately simpler than the protected Botanical v013 assembly. They do not approve or expose the larger historical park catalogue.

| Choice | Exact variant | Supported outline | Status |
| --- | --- | --- | --- |
| Flexible pocket park | `urban_pocket_park_v0` | Simple polygon; 8–100 m oriented axes, 64–3,600 m² | Pilot, visual review provisional |
| Flexible linear greenway | `linear_park_greenway_v0` | Connected corridor; 60–1,000 m long, 12–60 m short axis, at least 3:1 aspect, 750–60,000 m² | Pilot, visual review provisional |

The shared recipe is `backend/app/services/public_realm_lego.py` (SHA-256 `b658f2edc55f144407637e2270c8b7a8ddf7a4f3053e314b683114ab7ad64a3b`). The finite selection registry is `frontend/src/data/flexibleParks.json` (SHA-256 `9884a7a0f83ba33ba3728bf3fb44cf271b4469f5cb5c3d918b9069957bfd697f`). Integration started from commit `7c86b4e337ea2bc3bd546498acb277ad7daf2320` on `codex/flexible-parks`. These are procedural kits; no new GLB is staged.

An agent used ordinary student controls in a disposable prepared-site project at `http://127.0.0.1:5182/projects/999efbaf-68cf-4767-9ccd-43ad7315f7df`. Screenshots are outside the repository at `C:/dev-artifacts/CityPrompt/archetype-field-2026-09-27/`. The worktree frontend used the shared API at port 8006 from the approved-validation installation. The new server-side gate has Python test coverage but was not exercised by that browser session.

| Check | Pocket | Greenway | Evidence / limit |
| --- | --- | --- | --- |
| Draw-first controls, exact identity | PASS | PASS | Both cards show “Choose & draw park”. |
| Irregular shape placement | PASS | PASS | Six-corner L shape and tapered corridor saved; `flexible-two-parks-overhead.png`. |
| 3D programme visible | PASS | PASS | Ground, planting and furniture shown overhead and at walking height; `flexible-park-walk.png`. The large test site makes these small parks appear distant. |
| Save/reopen | PASS | PASS | Both retained exact identities; `flexible-reopen.png`. |
| Resize and save/reopen | PASS | NOT TESTED | Pocket changed from 39.2 × 36.6 m to 45 × 42 m and persisted. |
| Unsupported-size recovery | PASS | NOT TESTED | Pocket Apply disabled for 4 × 4 m; prior saved shape retained. |
| Automatic 3D update | PASS | PASS | UI returned to “3D saved” after both placements and pocket resize. |
| Page errors | PASS | PASS | Agent-browser error log empty after reload and edit. |
| Undo/redo, entrances, exact capture, paid renders | NOT TESTED | NOT TESTED | No paid requests were used. |

Focused Vitest park suites (193 tests), a catalogue-card test, four Python validation tests, and frontend type-check passed. The production smoke build stopped while copying the very large shared public directory because C: filled. Runtime-asset checking also found 66 missing references in that local public directory, unrelated to these two thumbnails. A production artifact and fresh installation are unverified. The attempted build output is outside source at `C:/dev-artifacts/CityPrompt/flexible-parks-2026-09-27/production-smoke`. Six exact copied GLBs were removed to recover working space, but the remaining generated folder still needs cleanup. Automatic approval review rejected recursive removal of this folder.

The two programmes are simple, flexible alternatives to detailed native parks. Future visual review should use a smaller prepared site and compare nearby aerial and walking-height views with adjacent native parks.
