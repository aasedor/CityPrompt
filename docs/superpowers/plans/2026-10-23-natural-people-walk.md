# Natural people walk implementation plan

> Execute inline with superpowers:executing-plans; one fresh review of the complete change.

Goal: reduce marching and synchronized motion locally without changing source models or editing cost.

Architecture: corrective leg IK after absolute source clip sampling; stable placement profile controls capture phase/pace. Tech: Three.js, TypeScript, Vitest. Spec: ../specs/2026-10-23-natural-people-walk-design.md.

Global constraints: immutable GLBs, fixed-step capture, no background editing animation, no paid providers, no push.

Review focus: anisotropic parent transforms, Earth-scale coordinates, action switching, absent/partial rigs, stance feet and clip wrap.

## Task 1 — walking correction
- [x] Add failing regression tests for high swing feet, stance preservation, source isolation, deterministic seeks and stable identity profiles.
- [x] Add peopleWalking.ts: rigid leg solver in rig coordinates, preserve foot rotation; only soften lift over ankle threshold. First real-GLB failure required shoe-bound contact limits; rejected evidence retained.
- [x] Integrate after Walk sampling and use stable identity profile in PeopleModel.tsx instead of model-batch index. Require existing saved IDs in batching types.
- [x] Narrow tests, full completed type-check, lint; all-23 actual GLB sampling and browser comparison including capture restore.
- [x] Fresh branch review, fix strict type findings, record limitations and checkpoint explicit source files only.

Ruling: append a walking-only natural biomechanics direction to the existing server-owned people action text. This addresses AI interpretation without changing architecture/camera binding or paying for an unapproved trial. AI improvement remains untested.
