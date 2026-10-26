# Student review fixes — local acceptance

User approved implementation and testing of the reported issues on 2026-10-26.
The existing LuxModus package remains a separate, frozen handoff. No push or
deployment is part of this initiative.

## Implementation units

1. **Site information and controls:** recover street-name loading; inspect public
   data features; make existing land use an official read-only view; edit proposed
   zones immediately; remove the future-bylaw tab; group Site Context and Policy;
   audit optional tools and connect animation to immediate image results.
2. **Placement and capture:** explain entrance clearance, allow buildings beside
   sidewalks, make entrance/route defects advisory for image capture, and repair
   near-valid intersections with bounded geometric snapping before validation.
3. **Catalogue and towers:** group court-only variants under their base sports;
   preserve saved identifiers; pilot authored-floor repetition for Brick Podium
   tower with native podium/roof/material identity and a supported storey range.
4. **Video:** photographic finish defaults on; free preview stays free; explicit
   generation prepares/reuses a bound Sunburst guide and sends it with the exact
   route video; quote combined cost first; repair local worker readiness; provide
   simple route drawing/editing/deletion, automatic follow-person framing and
   distinct aerial/POV/cinematic movement.

## Verification

Each unit starts with regression tests for the reported behaviour. Run narrow
Vitest/pytest/compiler tests and TypeScript checks as appropriate. Integrate
coherent commits, inspect diffs, then test the combined localhost student flow in
a disposable project. Verify persistence/reopening as well as first use. Record
provider-dependent limitations honestly; no paid call on mount, toggles, preview,
or automatic retries. Keep generated assets in ignored output or artifact storage.

## Acceptance checklist

- [ ] Street names load and recover.
- [ ] Entrance guidance is useful; placement/capture do not unnecessarily fail.
- [ ] Public-data points disclose their records.
- [ ] Selected proposed zone changes label/colour immediately.
- [ ] Existing official land use is read-only; no future-bylaw editing tab.
- [ ] Site Context and Policy groups organize the existing controls.
- [ ] Supported tower storeys retain detailed authored geometry.
- [ ] Court variants appear under their base archetypes.
- [ ] Buildings can meet sidewalks without an artificial exclusion gap.
- [ ] Image results expose Animate render.
- [ ] Local Omni readiness is operational without weakening production controls.
- [ ] Aerial, street POV and follow-person routes have the intended framing.
- [ ] Photographic finish defaults on and guide preparation is automatic on Generate.
- [ ] Routes can be drawn, moved, shortened and deleted easily.
- [ ] Optional student tools work or explain an actionable prerequisite.
- [ ] Near-valid intersections snap safely into complete junctions.
- [ ] Combined automated checks and local browser stress tests pass.
