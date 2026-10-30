# Drawn bridge routes

## Accepted intent

On 30 October the user requested bridges placed like streets: draw a start and
end point, with the main span adapting to that distance. They explicitly chose
an adjustable main span over a fixed span with variable approaches. Bridge
deliveries should contain the bridge and compact end treatments, without a
surrounding neighbourhood, road network, river rectangle or broad landscape.

## Design

Use the existing hash-locked native street route, compiler, renderer, readiness
and save mechanisms. Preserve old fixed objects and their saved IDs. A new
route-capable revision has its own ID, source/module locks and declared bounds.
Do not relabel a fixed GLB as an executable street or bypass its existing gate.

First complete one timber covered bridge pilot before converting other styles.
Extract immutable bridge-only structural modules from the exact v004 source:
two end structures, two compact stair approaches and a typical middle bay.
Repeat middle bays to fill a straight two-point route; distribute the small
remaining longitudinal adjustment over those bays. Preserve width, height,
end structures, stairs and material identity. Keep the original source GLB
unchanged. No surrounding water, banks, unrelated paving or landscape remains.

Use measured module bounds and explicit extraction regions, not a global
material-name heuristic that could remove the bridge itself. A finite module
recipe owns bridge dimensions, approach length, deck datum and supported span.
The first pilot is a prepared-level-site conceptual pedestrian bridge, with
stairs, not an accessibility or engineering-compliance claim. Its ordinary UI,
walking, exact capture and reload acceptance must precede batch expansion.

## Approaches considered

* Retain each fixed structural span and vary only approaches: existing Landmark
  bridge uses this, but the user explicitly chose an adjustable main span.
* Scale complete source scenes: easy, but distorts width/height, retains broad
  context and changes rigid equipment. Rejected.
* Bridge-only native modules with an adjustable route: selected for the timber
  pilot; preserves detailed end geometry and repeatable structural bays.

## Boundaries

No catalogue JSON parse/rewrite, original GLB mutation, dependency installation,
paid generation, pilot approval invention, deployment or publication exceptions.
Natural terrain, automatic bridge intersections and curved bridge alignments
are unsupported by this first straight two-point pilot. Existing fixed scenes
remain readable. Special ring/flyover topologies need their own reviewed route
adapters rather than an arbitrary whole-scene stretch.

## Acceptance

Ordinary picker -> two endpoints -> detailed bridge; a longer route has more
bays, no extra landscape rectangle, and unchanged width/height. Move/rotate,
endpoint edit, Undo/Redo, save/reopen and exact source capture retain identity.
Walking follows the actual stairs and deck. Invalid short/oversized/bent drafts
retain editing and explain supported dimensions. Failed hashes, stale loads,
unknown IDs and wrong widths remain rejected on frontend and backend.

Photographic catalogue cards remain available, but cannot certify model or
runtime fidelity. Evidence clearly distinguishes screenshots, source captures,
API checks, offline geometry checks and paid originals.
