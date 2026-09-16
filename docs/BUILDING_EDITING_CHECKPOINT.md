# Building placement and editing checkpoint

Phase 4 of the student design transformation. This is a verified interaction
slice, not acceptance of grounding or the complete student journey.

## Implemented behavior

Every eligible canonical building can use click placement with a footprint
preview. Canonical placement descriptors retain the exact type/variant; they
do not publish new reviewed models or bypass compiler review gates. Existing
native previews remain available. The compiler chooses reviewed geometry or
explicitly labelled design massing.

Placement can face the nearest usable proposed/existing street within 100 m.
Preview and save share the same deterministic orientation. Motorways and
footpaths are excluded. Manual rotation disables automatic facing. Orientation
is saved in the footprint and is not recalculated on context refresh.

The selected-object panel exposes type, variant, storeys, height, dimensions
and rotation, alongside direct move/corner/rotation handles. Type changes retain
the footprint. Existing irregular canonical outlines survive numeric resizing.
Edits use the existing revision, undo and automatic-compilation paths.

Explicit height edits are checked both during planning and under the backend
commit lock. A reviewed model cannot silently retain a different height or be
scaled vertically. Unsupported heights produce design massing. Five centimetres
of tolerance accommodate rounded input; older projects without an explicit
height override retain their existing representation behavior.

## Verification

Local project `c5f73929-f949-41d2-ac7d-0340e09339e7` was edited through the browser;
the frozen Gold Standard geometry was not changed.

- Click-placed a canonical brownstone and a reviewed native infill home.
- Changed the infill to 12 m: saved planned massing with the exact same footprint.
  Undo restored the native LEGO/RLASM assembly with no height override.
- Changed type/variant to limestone brownstone: retained the exact footprint,
  saved the selected identity and 6.4 m height.
- Dragged the visible move handle, then resized to 18 × 24 m and rotated to 30°.
  API measurement: 18.00004 × 24.00002 m, 29.99993°.
- Reload retained coordinates exactly and preserved identity and height.
- Inspected native, fallback, moved/reshaped, oblique and reload screenshots.
  Browser error count remained unchanged after runtime asset recovery. No new
  failed resource responses were observed during the height/undo loop.
- 75 focused frontend tests pass; TypeScript and targeted production ESLint pass.
  187 focused backend height/assembly tests pass. Existing dependency warnings
  remain unrelated to this slice.

Evidence is under the external mission artifact root: `PHASE4-*` screenshots
and `phase4-before-height.json`, `phase4-after-height.json`,
`phase4-undo-height.json`, `phase4-after-type.json`, `phase4-after-move.json`,
`phase4-after-reshape.json`, `phase4-reload.json`.

## Open acceptance work

The test scene still reports a building ground-contact issue and shows incorrect
green skate-bowl surfaces. These are retained failures for phases 6/7, not a
grounding pass. Comprehensive native frontage/entrance inspection, all-category
identity, older-project compatibility, complete undo/redo recovery and final
fresh-session acceptance remain open. HMR disrupted live canvas listeners during
development; full reload restored interaction. Browser acceptance used full
reloads, not an HMR-only state. No paid image/video generation was used.
