# Ground pathway overlap implementation plan

**Goal:** Let students draw simple ground paths and standalone sidewalks across
building and park plots, including entrance approaches, and retain them through
editing and reopening.

**Spec:** The user's request in this chat: pathways should draw on the ground
despite building/park overlap, like the existing water drawing tool. This is an
explicit behavior request; use the current stack and ordinary drawing controls.

**Architecture:** Keep surface-path identity tied to the existing eight narrow
pathway programmes. Pass the candidate's actual properties through placement,
boundary recovery, duplication and section replacement. Ground paths are a
nonexclusive layer relative to building/park plots; maintain site containment,
route validity, source locks and vehicle junction validation. Preserve physical
occlusion by walls/raised objects. Inspect ground-slab visibility in a browser
pilot before introducing a rendering correction.

**Execution:** Inline in the current chat. No delegation, paid generation,
publication, push or deployment. Disposable local QA projects only.

- [x] Reproduce the existing overlap rejection with focused tests and browser evidence.
- [x] Add narrow path/building/park overlap policy and propagate exact candidate identity through all controls.
- [x] Verify reverse placement order and road/boundary protections with regression tests.
- [x] Pilot a path across a park and into a building plot; inspect low/aerial views, move/bend, Undo/Redo and reload.
- [x] If path geometry is buried by shallow model ground, correct the shared surface integration with a measured regression; retain depth testing.
- [x] Run focused Vitest and TypeScript checks; record exact tested/untested gates and verified Drive screenshot delivery.
- [x] Review diff/status and commit one coherent local unit.
