# Reference-Locked Atomic Sticker Method (RLASM)

Version: 1.1.0
Status: active, user-approved production direction  
Machine contract: `reference_locked_atomic_sticker_method.json`

## Purpose

RLASM is the repeatable City Prompt procedure for creating a recognisable,
reference-specific 3D building without turning a reference photograph into a
tiled facade texture. It preserves the successful Sticker Method while making
the building physically credible, reusable, and practical to scale across a
large catalogue.

The defining rule is:

> Every visually unique architectural piece receives its own reference card.
> A card may be reused only when the architectural role is genuinely the same.

The approved visual precedents are the corrected Halifax and Calgary pilots.
Their clean materials, atomic opening cards, and physical construction replace
the rejected approach of repeating whole-object or whole-facade photographs.

## Non-negotiable invariants

1. **Reference identity is locked.** Use the exact archetype and variant. Do
   not substitute a more convenient sibling aesthetic.
2. **Prework happens before geometry.** The reference sheet, role inventory,
   material zones, massing notes, storey count, bay cadence, and roof system
   must be recorded before a build begins.
3. **Every unique role has a card.** Unique roofs, domes, monitors, chimneys,
   bridge pieces, entrance assemblies, window types, trim types, and special
   facade objects each need an isolated card. Identical repeats may share one.
4. **Broad surfaces use clean materials.** Brick, stone, metal, glass, siding,
   and roofing use seamless world-scale material swatches, never tiled facade
   photographs.
5. **Geometry owns depth and silhouette.** Recesses, returns, frames, arches,
   mullions, roof profiles, bridge systems, cornices, and parapets are physical
   3D construction. A card cannot impersonate structural depth.
6. **Openings remain openings.** Window and door cards sit behind physical
   glazing, frames, and mullions. They must never brick over or flatten an
   opening.
7. **No generic fallback.** A missing role or card is a hard stop, not a reason
   to use generic siding, generic windows, or the nearest available material.
8. **The pilot is non-overwriting.** Each attempt has a new candidate/version;
   rejected outputs and failure evidence remain frozen.
9. **One building is approved before scaling.** Produce and review one complete
   archetype before creating the rest of its family or wave.
10. **Review images are actual 3D renders.** AI image tools may create clean
    reference-matched cards and swatches, but the building review images must
    be rendered from the actual 3D model and labeled as such.
11. **Validation remains truthful.** Numeric or visual failures are recorded;
    thresholds are not silently relaxed. Cosmetic debt may be disclosed, but a
    genuine 3D failure cannot be waived as polish.
12. **Scale follows visual approval.** Material consolidation and performance
    optimisation happen only after the appearance is approved and must not
    change the approved visual result.
13. **Every attachment has a load-bearing contact.** Windows, frames, cards,
    balconies, canopies, rails, roof equipment, ornaments, signs, stairs, and
    every other attached object must be projected onto its actual carrier
    surface, aligned to the local surface tangent/normal, and overlap or mount
    into that carrier by a documented physical depth. A fixed world-axis plane
    is forbidden on curved, chamfered, sloped, or otherwise non-planar walls.
    The contact audit must report `floating_count = 0` before review.

## The procedure

### 1. Lock the reference set

- Record the archetype ID and exact variant ID.
- Collect the best primary view plus oblique/return and roof/aerial views when
  available.
- Hash or otherwise freeze the source files and record provenance.
- Write a short identity statement: what makes this building recognisable and
  which characteristics must not drift.

Required output: a frozen reference inventory.

### 2. Create the prework reference sheet

Before Blender work, make a reference sheet that records:

- overall massing, footprint, storeys, roof form, and silhouette;
- facade hierarchy, bay cadence, vertical and horizontal divisions;
- material zones and their transitions;
- all opening families and their proportions;
- every unique architectural role, including roof-only and rear/side roles;
- repeated roles that are explicitly allowed to share a card;
- uncertain or hidden areas that require conservative reconstruction.

Required output: `prework-reference-sheet.png` plus a role inventory.

### 3. Build the atomic card set

Use the following card taxonomy:

| Card type | Purpose | Required constraints |
| --- | --- | --- |
| Material swatch | Broad brick, stone, siding, metal, roof, or glass surfaces | Seamless, orthographic, even lighting, world-scale capable |
| Opening card | A single window, door, storefront, dormer, or occupied-depth view | One opening only; no adjacent facade; aligned and perspective-free |
| Object card | A unique dome, spire, monitor, chimney, canopy, bridge part, ornament, or trim assembly | Isolated object; neutral background; no people, text, cast shadow, or neighbours |
| Occupied-depth card | Interior signal behind glazing | Used behind physical glass/mullions; never on the exterior face |

Image generation may assist with cleaning or reconstructing these cards, but
each result must remain recognisably tied to the locked source reference.

Required output: a complete card manifest in which every unique role maps to
exactly one approved card or clean material binding.

### 4. Model the physical construction

- Build massing and roof silhouette first.
- Model apertures, recesses, returns, frames, mullions, cornices, parapets, and
  role-specific geometry.
- Treat special systems such as Plus-15 bridges, domes, roof monitors, and
  glazed entrances as their own construction systems.
- Keep repeated geometry modular, but never stretch or duplicate fixed identity
  pieces merely to make dimensions fit.
- Derive each attached object's anchor and orientation from the carrier surface
  rather than from a convenient global X/Y/Z plane. Record carrier ID, contact
  point, tangent/normal, intentional mount depth, and support relationship.
- Inspect contact from a dedicated grazing or side camera; a beauty angle is
  not proof that an attachment is physically connected.

Required output: a physically coherent model with all unique roles present,
plus an attached-object contact audit proving zero unsupported/floating parts.

### 5. Bind cards and materials by semantic role

- Keep the role card as the visual authority for that role.
- Apply clean material swatches to compound shells and broad surfaces.
- Place opening/occupied-depth cards behind physical glazing and frames.
- Reuse a card only across instances of the same semantic role.
- Never repeat a whole-facade or whole-object photograph across child faces.

Required output: a binding audit showing no missing role and no generic
fallback.

### 6. Produce one non-overwriting pilot

- Create one new candidate/version; never overwrite a rejected candidate.
- Render the approved review cameras from the actual model.
- Preserve source, card, scene, and render hashes.
- Stop after the single pilot. Do not start an open-ended generation loop.

Required outputs:

- `preview.png`
- `prework-reference-sheet.png`
- `reference-rejected-corrected.png`

### 7. Review the pilot against the reference

The comparison sheet must show the exact reference, any rejected prior attempt,
and the corrected actual 3D render. Review:

- identity and silhouette;
- roof and unique-object completeness;
- opening proportions and real depth;
- material specificity rather than generic appearance;
- side/rear continuity and oblique parallax;
- absence of tiled photo fragments, bricked windows, ghosting, leakage,
  z-fighting, stretching, or broken glass.

User visual approval is required before scaling to another archetype.

### 8. Validate and freeze evidence

Record reference/card/material hashes, role bindings, model/render hashes, and
validator results. A genuine hard failure freezes the candidate. Cosmetic-only
findings may be disclosed for downstream GPT image/video refinement, but the
strict result remains visible.

### 9. Optimise without visual drift

After approval, consolidate materials by identical binding tuple and reuse
verified modules. Do not create one material per surface, and do not alter the
approved appearance. The resulting method must remain practical for a
500-building catalogue.

### 10. Commit the review handoff

Promote only reviewed deliverables. Store large images through Git LFS and
commit the preview, prework sheet, and comparison sheet together. Push only
when explicitly authorised.

## Hard stops

Stop and create a fresh, non-overwriting candidate when any of these occur:

- wrong archetype or sibling identity;
- missing unique role or missing card;
- generic fallback material/card;
- whole-facade photo used as a building material;
- whole-object card repeated on component faces;
- bricked, printed, or flat openings;
- missing physical window/door depth;
- unsupported or floating attachment, including a frame or card that is
  visually near a wall but does not physically contact its carrier surface;
- incomplete roof, dome, bridge, or other identity-defining system;
- leak, ghost, z-fight, stretch, duplicate stack, broken glass, or lost
  parallax/state;
- review image is not an actual render of the model;
- scaling begins before the one-building pilot is approved.

## Bounded correction policy

Use one pilot followed by at most two focused correction loops. Fix the largest
identity or structural failure first. Do not spend days on an open-ended polish
loop. After the bounded loops:

- quarantine a genuine 3D failure;
- disclose cosmetic-only debt and hand it to downstream image/video refinement;
- scale only an approved method and binding contract.

## Approved and rejected precedents

- **Approved direction — Halifax v6:** clean facade materials plus projected,
  role-specific openings; commit `9fc1bcdf4`.
- **Approved direction — Calgary v6:** clean precast construction plus atomic
  opening cards; commit `454657070`.
- **Rejected — Halifax v3:** photo fragments tiled across the building.
- **Rejected — Calgary v3:** compound photo cards repeated over component
  faces, producing a noisy and structurally implausible result.

These precedents define the method, not a universal architectural style. Each
new archetype still requires its own complete reference sheet, unique-role
inventory, card set, and pilot approval.
