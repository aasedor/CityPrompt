# Grounding recovery checkpoint

Phase 7 remains in progress. This checkpoint makes an existing rejected building
recoverable; it does not relax contact validation or accept the final slope gate.

The student pilot's brownstone straddles an existing retaining edge. Its measured
footprint spans 1095.007–1098.344 m, exceeding the existing 3 m foundation limit.
This is a real surface step, not evidence for a datum correction. The loaded
representation's exact footprint remains the authority. Plot-only preflight was
not retained because a reviewed building can occupy less than its plot.

**Check building ground** now opens a plain-language explanation and identifies
the affected archetype. **Select and adjust** selects its original saved zone and
opens the existing move/property controls. Neither action writes project data.
The renderer and capture gates continue rejecting unresolved contact.

## Verification

- 20 narrow tests: recovery dialog, actual building contact, retained-ground
  selection. TypeScript and changed-file ESLint pass.
- Browser: identify brownstone, select, drag off retaining edge, inspect from
  above and obliquely. It becomes visible and the failure clears.
- Undo returns every zone to exactly its earlier coordinates and restores the
  expected rejection. Reload preserves those coordinates and the warning.
- Fresh resource failures: none. Cumulative browser errors remain 444 (earlier
  missing assets and two development HMR errors; no new recovery errors).
- The browser wait command failed after Undo because Windows interpreted an
  unquoted arrow in its predicate. The local harness now quotes predicates.
  Saved coordinates and visible state independently confirmed Undo success.

Evidence outside Git at
`C:/dev-artifacts/CityPrompt/student-design-transformation/`:
`phase7-building-contact-samples.json`, `phase7-*-recovery-zones.json`, and
visually inspected `PHASE7-GROUND-RECOVERY-*`, `PHASE7-RECOVERED-*` screenshots.
The failing pilot location is deliberately restored for regression coverage.
The frozen Gold Standard geometry is unchanged.

## Remaining ground work

Complete the mixed-object slope/entrance/contact matrix, prepared-site perimeter
and park-edge seams, asynchronous refinement, context switching and older
projects. The current Google surface is photogrammetry, not classified bare-earth
survey data. No final grounding or professional visual-quality pass is claimed.
