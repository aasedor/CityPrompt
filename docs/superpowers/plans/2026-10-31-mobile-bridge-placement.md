# Mobile bridge placement implementation plan

> **For agentic workers:** Use superpowers:executing-plans. Preserve all pre-existing hydrated binary changes.

**Goal:** Students can draw the ten published bridge routes with approximate endpoints on mobile, without measuring a narrow accepted span by hand.

**Architecture:** Fit only the proposed second endpoint to the existing exact bridge programme's supported metric span, preserving the first endpoint and bearing. Share this operation between draft and final geometry. Mobile previews raycast the centre crosshair from the first point and on camera movement without requiring a hover event. Existing source bytes, geometry programmes, recipe locks, boundary/collision/ground checks and historical placements remain unchanged.

**Tech stack:** Existing React/TypeScript, Three.js and Vitest. No new dependencies.

**Spec:** The goal and architecture above implement the user's mobile bridge drawing report and prior request for adaptable two-point bridge routes. This is drawing assistance, not unrestricted structural resizing. Outside-range endpoints move to the nearest supported length; usable in-range endpoints remain exact. Degenerate/invalid points remain invalid. Site containment remains authoritative.

## Constraints and review focus

- Work from origin/deployment-version, not the historical main default.
- Never modify source GLBs, supported span limits, native compilation or release guards.
- No silent endpoint snap to unrelated roads, added bends, or shifted first anchor.
- Preserve the same preview and saved result, including Alt (junction snap bypass).
- Mobile crosshair must work without pointer events, track camera changes, and clear on undo/cancel.
- Show supported spans and touch Finish instructions. Record actual mobile-emulation coverage separately from physical-device testing.

## Tasks

- [ ] Add failing span cases for all ten production bridge variants: too short/long, valid, bearing, immutability, repeated fit and containment. Add a failing mobile no-hover/camera-move preview test and copy assertion.
- [ ] Implement the shared bridge drawing fit, mobile preview tracking and truthful drawing instructions; retain ordinary streets and route validation.
- [ ] Run narrow bridge/street preview/placement tests, TypeScript check and scoped lint. Inspect/review the complete diff.
- [ ] Trial one narrow-span bridge first on a disposable mobile viewport; then a bounded second style and desktop regression. Capture evidence and complete the shared runtime review with unrun cases explicit.
- [ ] Commit only intended source/evidence. Continue checked deployment-version PR/release under existing authorization when gates pass; preserve original services and user projects.

## Ledger

- Diagnosis: streetDrawingGeometry passes raw endpoint distances into strict native bridge span validation. Mobile preview additionally has a null pointer until pointermove, although mobile drawing uses a centre crosshair. Mobile Finish already exists with a 44 px target; retain it.
- Scope ruling: automatic fit applies to newly drawn bridge routes; existing saved geometry is not migrated or silently resized. Endpoint-edit behavior is unchanged and must not be described as newly supported auto-fit.

- Browser-derived scope extension: the V bridge's 48.986 m minimum was incorrectly blocked by generic52 m street spacing, then its correct authored axis was dropped by backend longest-axis normalization. Delegate bridge spacing and full footprint to the exact native bridge contract. Ordinary street recovery remains unchanged; invalid bridge metadata fails closed.
- All80 source bridge min/max × four-heading compiler cases exposed4 cycle-ring failures caused by comparing a local-frame corridor to UTM. Both exact span and full footprint now use the existing source frame and unchanged10 cm envelope tolerance; no tolerance or source-program change.
- Independent review caught mobile pointer-leave hiding the crosshair preview and boundary snapping moving the first anchor. Added RED regressions and fixed shared paths. Invalid parcels remain invalid.
- Verified source checkpoint:247 focused frontend tests,246 affected backend tests, independent105frontend/90backend cases, scoped Ruff/Black/diff pass. Type-check rerun after fixing test-only unknown-property cast. Browser full save/reload still pending owned API restart; no physical-device or live-release pass claimed yet.
