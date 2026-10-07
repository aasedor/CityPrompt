# Building walking coverage — 2026-10-04

## Scope and behavior

The selected building's **Walk inside** action now covers `building`,
`residential`, and `development_area` zones. Review GLBs, native LEGO recipes,
imported models, and the existing planned-massing representations register a
view only after their model and verified foundation are ready.

Authored circulation takes precedence. A shared loader handles embedded
networks, exact measured revision plans, immutable content-version URLs, and
older URLs whose served bytes match an existing measured plan. Async lookups
cannot register a route after their renderer unmounts. Native metre-scale
guards remain in place for imported and LEGO models.

Models without an authored route offer **Shell inspection · No authored
interior**. The camera starts at the actual mounted model's base and stays
within its local bounding envelope, using the model's real world transform.
This is free inspection of existing geometry, not a generated floor plan or
collision-checked circulation network. It creates no rooms, floors, stairs,
door cuts, or catalogue assets. Upper floors are accessible only where the
model has authored circulation for them.

Inspection owns temporary copies of materials so inward faces can be seen.
For a massing shell, its overlapping sibling foundation finish is temporarily
hidden to prevent flickering at the existing bottom cap; its prior visibility
returns on exit. Shared GLB geometry and cached materials remain unchanged.
Moved, deleted, unmounted or unverifiable models lose inspection availability.
A stale active inspection holds the last camera view and requests re-entry.

The building stays promoted to detailed rendering while walking, independent
of editor selection. Planning overlays and selection outlines hide during the
walk and restore with the existing editor state on exit. Return-to-start,
drag-to-turn, WASD and Escape use the shared walking controls. Unloaded models
give an actionable loading/3D-model message instead of claiming no route exists.

## Verification

- Narrow Vitest: 82 tests in ten files covering walking, exact model lifecycle,
  inspection transforms/ownership, grounding, placement and detail budgeting.
- `npm run type-check` and `git diff --check` passed.
- Browser, isolated frontend 5177/API 8008: all five saved Currie buildings
  entered their authored routes; rotations included -15, 5, 165 and 180 degrees.
  Buff-brick room geometry and the brick walk-up's open entrance were visible.
  Drag turning, return to entrance and button/Escape exit were exercised.
- An older saved blue-glass library model entered its measured route.
- A new disposable planned-mass fixture in copied database
  `cityprompt_repairs_20261004` exercised shell entry, turning, keyboard smoke
  input, return to inspection start and exit. It was tested as both residential
  and development-area ownership. The latter is its retained test state.
- Browser diagnostics returned no warnings/errors in the final checked views.
  The finite browser pilot is not exhaustive inspection of every asset's rooms
  or stairs; the existing catalogue-revision tests remain authoritative for
  route-plan coverage. Existing model/reference linework remains visible.

Evidence and fixture setup are outside Git under
`C:/dev-artifacts/CityPrompt/all-building-walking-2026-10-04/`, including
`final-building-walking.png`, `residential-shell-inspection.png`,
`development-area-shell.png`, and `shell-pilot.sql`.

## Workspace and release state

Source branch: `codex/all-building-walking-2026-10-04`, based on `b48a3641c`.
No new worktree, paid generation, catalogue promotion, main-branch update or
push. The original 5176 runtime and original databases are preserved.
Missing local test dependencies were supplied through an external dependency
overlay that reuses installed packages; source package manifests are unchanged.
