---
name: rlasm-expert
description: Build, rebuild, diagnose, document, or review exact-archetype 3D buildings with the Reference-Locked Atomic Sticker-and-Massing (RLASM) method. Use for source locking, architectural and roof inference, source-specific materials, orthographic identity stickers, physical openings and contacts, transparent building programs, review cameras and phone boards, keeper decisions, finite batch work, or RLASM method maintenance. Trigger whenever a user asks for RLASM, archetype fidelity, non-generic building materials, floating-window/dormer correction, or keeper approval.
---

# RLASM Expert

Produce source-specific buildings under the canonical RLASM v6 contract. Treat
rendered relationships as proof and metadata as supporting evidence.

## Start safely

1. Run `git status --short --branch` before writing.
2. Read repository instructions and recovery notes.
3. Read the complete canonical method at `docs/RLASM_LATEST_METHOD.md` and its
   executable companion at `tools/archetype_compiler/rlasm_method.json`.
4. Preserve existing candidates and unrelated work. Create a new bounded
   version; never overwrite or relabel a failed candidate.
5. Read [references/field-guide.md](references/field-guide.md) for builds,
   [references/failure-catalog.md](references/failure-catalog.md) for diagnosis,
   and [references/review-contract.md](references/review-contract.md) for any
   visual decision or keeper claim.

If repository paths differ, locate the canonical files with `rg --files`.
Package-local `RLASM_*_V5.md` files are historical snapshots, not current
authority.

## Route the task

- **New build or rebuild:** source-lock, measure, construct the unskinned
  envelope, register identity/material authority, build openings/contacts,
  render the complete evidence set, then request independent review.
- **Diagnosis:** inspect source and all rendered views directly. Report the
  visible symptom, physical cause, and finite correction; do not change files
  unless the user asked for implementation.
- **Review:** use the exact locked source board and complete full-resolution
  render set. A scoped review closes only its category.
- **Batch:** prove one representative pilot before a finite next wave. Never
  start an unattended iterate-until-pass loop.
- **Archive:** create a keeper manifest, copy rejected versions externally,
  verify SHA-256, then remove only confirmed duplicates from the active folder.
- **Method update:** synchronize the canonical human method, executable RLASM
  contract, high-quality human/machine memory, tests, and this skill.

## Build sequence

1. Lock the exact archetype and variant. Enroll at least front, oblique, and
   top, plus every compatible available view, with path, bytes, role, and hash.
2. Measure plan, height, floors, bay schedule, asymmetry, roof graph, entrances,
   transparent program, circulation, landscape, and required contacts.
3. Author the whole camera roster before geometry.
4. Build a complete family-specific unskinned envelope. Continue its grammar
   around sides, rear, courtyards, roof, gables, foundations, and supports.
5. Give geometry ownership of silhouette, depth, openings, load paths,
   weathering joints, circulation, and transparent-building program.
6. Use bounded orthographic identity derivatives for source-specific cadence,
   relief, joinery, ornament, or zoning. Rectify oblique emblems; never paste
   perspective crops. Give every feature one visual owner.
7. Condition dominant materials from the exact source family. Preserve
   morphology, physical scale, axes, phase, roughness, aging, and one
   building-level authority for each physical substance.
8. Build every opening as cut carrier → returns → recessed frame/lattice →
   optical pane/screen → offset occupied layer → enclosed room depth.
9. Derive roof-mounted objects from the actual carrier surface. Prove body
   penetration, full-depth cut, seated cap, and bounded flashing in pixels.
10. Render all baseline and family-specific views under neutral QA lighting,
    inspect full resolution, and build 1080×1920 phone comparisons.
11. Run `python scripts/validate_candidate.py <candidate>` for deterministic
    preflight. Treat its result as incomplete without visual review.
12. Record only a builder pass and hand the exact source/evidence package to a
    separate independent verifier.

## Approval boundary

Never self-approve a building you produced. Never promote from a materials-only,
contact-only, glazing-only, or identity-only review. Keeper approval requires a
separate holistic source-locked adversarial regression of every mandatory view
and phone board with zero unresolved P0 and P1 blockers.

If later evidence exposes a missed defect, preserve the old decision and mark
the candidate `visual_rework_required` or `superseded`. Advance a new version,
rerender the complete camera set, and repeat holistic independent review.

## Deliverables

For each candidate preserve:

- exact source manifest and locked board;
- measured architecture, program, material, identity, and contact contracts;
- provenance and hashes for every derivative and dominant material;
- GLB, complete renders, phone boards, builder evidence, and review records;
- a truthful lifecycle state and supersession link when applicable.

Conclude with source changes, generated artifacts, checks run, current review
state, remaining blockers, and whether anything was committed or pushed.
