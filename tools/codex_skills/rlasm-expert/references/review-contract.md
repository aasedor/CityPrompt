# RLASM review contract

## Separate roles

The RLASM production expert locks sources, builds, corrects, renders, and may
record `builder_pass_only`. The independent verifier compares the exact source
board with the complete evidence set. The expert never approves its own work.

## Scope

- A scoped review names one or more categories and may close only those
  categories. Its result is `category_closure_only`.
- A keeper review is holistic and adversarial. Inspect identity, ratios,
  topology, every elevation, program, materials, openings, optics, contacts,
  load paths, circulation, landscape, visibility, cameras, and regressions.
- Metadata, hashes, object counts, and prior decisions are not visual proof.

## Keeper evidence

Require exact source board, complete full-resolution baseline renders,
family-specific contact/program views, 1080×1920 phone comparison, builder
evidence, and the previous finite blocker list. Open the pixels directly.

Approve only with zero unresolved P0 and P1 blockers. Write candidate, reviewer,
date, exact scope, inspected files, pixel findings, blocker list, decision, and
whether the review was holistic or scoped.

- **P0:** source identity, topology, envelope, opening, contact, program,
  camera, provenance, or lifecycle defect that invalidates the candidate or
  its proof.
- **P1:** clearly visible fidelity, material, optical, finish, landscape, or
  coherence defect that prevents production-quality keeper approval.
- **P2:** non-blocking polish only when it does not weaken source identity,
  construction, visibility, or evidence.

## Lifecycle

`prework` → `building` → `build_valid` → `visual_review_ready` →
`independent_review_pending` → `keeper_approved`.

At any review stage use `visual_rework_required` or `rejected`. Use
`superseded` when a newer candidate replaces a former pass or keeper. Use
`archived` only after external copy and hash verification.

Later user evidence can reopen any approval. Preserve the earlier record,
explain the supersession, and review the new bounded candidate holistically.
