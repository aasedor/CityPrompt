# Reference-Locked Atomic Sticker Method (RLASM)

Version: 1.7.0
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
14. **A role name does not make a material reference-specific.** A procedurally
    drawn palette swatch, flat colour, or generic pattern remains a generic
    fallback even when it is labeled `cedar`, `fieldstone`, `brick`, or another
    correct semantic role. Every production material must bind to a hashed crop
    from the locked reference or to a separately approved reference-matched
    reconstruction. The manifest must record that provenance and a visual
    comparison; `generic_fallback_count = 0` is invalid without both.
15. **Repeatable material fields contain no unique ornament.** A broad brick,
    stone, siding, metal, or roof swatch may contain only the repeatable field
    material. Carved bands, medallions, arches, friezes, ridge pieces, finials,
    decorative panels, and other unique architecture must be separate atomic
    cards and physical roles. If unique ornament appears in a repeatable swatch,
    reject that swatch before Blender work rather than tile the mistake.
16. **World-scale materials use real spatial units.** Broad material mapping
    must use object/world coordinates or controlled UVs whose scale is measured
    in real building units. Per-object normalized `Generated` coordinates are
    forbidden for production broad surfaces because the same swatch stretches
    differently across objects with different proportions.
17. **Opening hierarchies are reference-specific.** When the locked reference
    contains multiple window or door families, prework must inventory each by
    shape, proportion, outer-frame material, inner muntin material, surround or
    hood geometry, placement zone, and occupied-depth treatment. One universal
    sash cannot stand in for main double-hung, turret-narrow, gable-arched,
    Romanesque, storefront, dormer, or other visibly distinct roles. Cards are
    visual authority only; Blender must construct the corresponding physical
    frames, muntins, sills, lintels, arches, glazing, recesses, and returns.
18. **Pitched roofs require physical end closure.** A gable roof cannot hover
    over an empty triangular opening. Every visible gable end must have a
    physical wall carrier whose material and trim follow the locked reference.
    Openings mounted to that carrier must sit fully outside it or use a real
    aperture; the carrier may never intersect glazing or brick over a sash.
19. **Do not model a texture feature twice.** If a reference-matched roof or
    siding material already contains a repeatable seam, board, or shingle
    cadence, extra geometry is added only when it represents real profile
    depth and is projected onto the carrier. Decorative seam bars floating
    above a roof are forbidden.
20. **The primary review camera shows the complete building.** Detail and
    contact views remain required, but `front_corner.png` and `front.png` must
    frame the full silhouette, foundation, entrance, and roof. A flattering
    close crop cannot substitute for whole-building identity review.
21. **Entrances are enumerated, not inferred.** Every distinct primary,
    secondary, side, rear, service, or recessed entry must appear in the role
    inventory and receive its own atomic leaf/assembly authority. A unique door
    hidden inside a broad window or facade card is still a missing role.
22. **Cards and geometry have exclusive physical responsibilities.** When a
    handle, knob, lockset, threshold, or sconce is modeled, it must not also be
    baked into the door-leaf card. Each visible physical object appears exactly
    once, touches its carrier, and uses the reference-correct latch side.
23. **Independent final-render QA is required.** Before a pilot can pass, a
    reviewer other than the builder compares the locked reference, role/card
    inventory, actual scene geometry, and entry/contact close-ups. Builder
    evidence is never self-approval.
24. **Window reflection is neutral.** Use restrained low-iron neutral reflection
    with scene-dependent light and sky response. Strong green, amber, cyan, or
    artificial blue colour casts are forbidden unless the locked archetype
    reference explicitly proves tinted glazing. Reflection must not contain a
    photographed room, facade, frame, or other baked architectural content.
25. **Every visible building material is finished before final render.** The
    final material audit must enumerate every material used by the building and
    prove a hashed locked-reference crop or approved reference-matched
    reconstruction, correct real-unit mapping, and status
    `reference_specific_finished`. Context-only lawn, road, sidewalk, and trees
    may remain simplified only when they are explicitly classified outside the
    building-material roster. A plausible colour or material-class label is
    not a finished material.
26. **Glass reflects the rendered scene, never a photograph of the scene.** A
    physical pane may respond only to the current world, lights, and real scene
    geometry. No reflection image, photographed sky, tree, facade, room, or
    prior render may feed glass Base Color, Reflection, Emission, or a backing
    layer visible as reflection. The final glass audit requires zero image
    texture nodes and zero linked Base Color inputs on the physical pane unless
    a separately approved non-reflection optical map is explicitly documented.
27. **The layer behind glass contains interior signal only.** An occupied-depth
    card may not contain exterior trees, sky, wires, neighbouring buildings,
    people, or photographed window reflection. Prefer modeled interior depth.
    When a card-built facade has no true aperture and clear glass would expose
    the uncut carrier wall, use a shallow, reflection-free modeled room proxy
    immediately behind the pane or rebuild the aperture. The proxy may contain
    restrained physical partitions, furnishings, and warm luminaires, but no
    photographic exterior content. Review context must also be sufficiently
    neutral that a saturated lawn or backdrop does not make neutral glazing
    read as green, blue, or amber glass.

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
- all opening families, proportions, frame and muntin materials, surround or
  hood geometry, placement zones, and allowed repeat counts;
- an explicit entry-role inventory covering every primary, secondary, side,
  rear, service, and recessed door;
- unique entry-adjacent objects such as hardware, sconces, canopies,
  thresholds, stoops, mailboxes, and railings;
- every unique architectural role, including roof-only and rear/side roles;
- repeated roles that are explicitly allowed to share a card;
- uncertain or hidden areas that require conservative reconstruction.

Required output: `prework-reference-sheet.png` plus a role inventory.

### 3. Build the atomic card set

Use the following card taxonomy:

| Card type | Purpose | Required constraints |
| --- | --- | --- |
| Material swatch | Broad brick, stone, siding, metal, roof, or glass surfaces | Seamless, orthographic, even lighting, world-scale capable, visibly/provenancially tied to the locked reference, repeatable field only, and free of unique ornament |
| Opening card | A single window, door, storefront, dormer, or occupied-depth view | One opening only; no adjacent facade; aligned and perspective-free; labeled with exact opening-family role and placement zone |
| Object card | A unique dome, spire, monitor, chimney, canopy, bridge part, ornament, or trim assembly | Isolated object; neutral background; no people, text, cast shadow, or neighbours |
| Occupied-depth card | Interior signal behind glazing | Used behind physical glass/mullions; never on the exterior face; contains no photographed exterior sky, trees, wires, people, facade, or reflection; replace with modeled room depth when a clean interior-only card is unavailable |

Image generation may assist with cleaning or reconstructing these cards, but
each result must remain recognisably tied to the locked source reference.
For each material, record either source-image SHA plus crop coordinates or the
approved reconstruction input/output hashes. Include a reference-versus-swatch
comparison. A hand-drawn or procedural pattern chosen only by material class
and approximate colour is a generic fallback and must fail prework.
Run an atomicity preflight on every material swatch. A swatch containing a
carved band, medallion, decorative arch, finial, roof junction, or any other
non-repeatable object fails with
`unique_ornament_embedded_in_repeatable_material_swatch` and is replaced by a
plain field swatch plus separate atomic geometry/card roles.

Door-leaf cards must be hardware-free whenever handles, knobs, locksets, or
rosettes will be modeled. Hardware, thresholds, stoops, and sconces are unique
physical roles: give them their own card or exact material binding and model
them once. Do not use a broad entry photograph as a substitute for an atomic
door leaf.

Required output: a complete card manifest in which every unique role maps to
exactly one approved card or clean material binding.

### 4. Model the physical construction

- Build massing and roof silhouette first.
- Model apertures, recesses, returns, frames, mullions, cornices, parapets, and
  role-specific geometry.
- Prove entry recess direction numerically: the leaf must sit behind the
  facade plane, never in front as an applique.
- Attach each physical latch through a rosette or backplate with restrained
  projection; no floating hardware and no duplicate baked lockset.
- Extend thresholds, stoops, risers, and steps to the declared grade/contact
  surface. A shadowed air gap beneath an entrance slab is a hard failure.
- Place entry lighting at the physical fixture and bound its output so the
  locked door material remains readable without clipping or colour wash.
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
- Map those swatches with object/world coordinates or controlled real-unit UVs;
  do not use per-object normalized `Generated` coordinates on broad surfaces.
- Verify the bound swatch against its reference material zone before rendering;
  semantic role, approximate hue, and a plausible pattern are not sufficient.
- Place opening/occupied-depth cards behind physical glazing and frames.
- Keep the reflection layer neutral and separate from the occupied-depth card;
  interior warmth belongs behind the pane, not in the reflection colour.
- Inspect every occupied-depth source for exterior sky, trees, wires, people,
  neighbouring buildings, or prior-render reflections. Any such content is a
  hard failure even when the glass shader itself contains no texture.
- If a transparent pane exposes an uncut facade carrier, cut the aperture or
  place a shallow reflection-free modeled room proxy before that carrier. Do
  not hide the carrier with a photographed window crop.
- Before final render, enumerate every used building material and require
  `reference_specific_finished`; classify deliberately simplified site context
  separately rather than weakening the building-material gate.
- Reuse a card only across instances of the same semantic role.
- Never repeat a whole-facade or whole-object photograph across child faces.
- Never bind baked hardware to a leaf that already has modeled hardware.

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
- every declared entrance in a building-scale view plus dedicated door
  close-ups, an oblique recess view, and a low grade/contact audit;
- exactly one physical latch per door, correct latch side, attached hardware,
  grounded thresholds/steps, and no entry-light clipping;
- an independent PASS/FAIL disposition after builder evidence is complete.

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
- unprovenanced, palette-only, or procedurally generic material swatch, even
  when its filename and semantic role are correct;
- unique ornament or a unique architectural object embedded in a repeatable
  broad material swatch;
- broad material stretched by per-object normalized coordinate mapping;
- whole-facade photo used as a building material;
- whole-object card repeated on component faces;
- bricked, printed, or flat openings;
- missing physical window/door depth;
- one generic window or door family substituted for a reference-specific
  hierarchy of distinct opening proportions, frames, muntins, arches, hoods,
  surrounds, or placement roles;
- a distinct entrance omitted because it was buried inside a broad card;
- a door leaf placed in front of the facade plane instead of inside its recess;
- baked handle, lock, or light content duplicating physical modeled geometry;
- floating handle, threshold, step, canopy, fixture, window, or trim;
- a full black reveal plate occluding the referenced door leaf;
- entry lighting detached from its fixture or clipping/washing out the locked
  material appearance;
- non-neutral window reflection colour cast without locked-reference proof;
- baked room, facade, or frame content in the glass reflection layer;
- any reflection image or prior render bound to a physical pane;
- photographed sky, trees, wires, people, neighbouring facade, or exterior
  reflection in an occupied-depth or window-backing layer;
- clear glass revealing an uncut facade carrier where an aperture or
  reflection-free room proxy is required;
- a used building material that is generic, unfinished, palette-only, or lacks
  locked-reference/reconstruction provenance;
- a saturated review lawn/backdrop making neutral glazing read as tinted;
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

When the user explicitly requests an iterate-until-PASS exception, each extra
loop must still be finite, non-overwriting, and tied to a new independent
failure report. It may correct only the bounded failing roles; it cannot widen
into an unreviewed rebuild or silently relax a hard gate.

## Approved and rejected precedents

- **Approved direction — Halifax v6:** clean facade materials plus projected,
  role-specific openings; commit `9fc1bcdf4`.
- **Approved direction — Calgary v6:** clean precast construction plus atomic
  opening cards; commit `454657070`.
- **Approved benchmark — Toronto Annex Mansion RLASM v4:** full prework,
  reference-specific brick/stone/slate, five physical opening families, and
  zero floating attachments; commit `d1aa8494b`.
- **Approved pilot — Vancouver Laneway House RLASM v12:** complete two-entry
  inventory, true recesses, hardware-free leaf cards, one physical latch per
  door, grounded steps, and fixture-local entry lighting; independent final QA
  disposition `PASS_FINAL_ARCHETYPE_VISUAL_QA`.
- **Approved material/glass polish — Vancouver Laneway House RLASM v22:** all
  17 used building materials audited as reference-specific and finished;
  physical low-iron glass uses only path-traced scene/world/light response;
  photographic exterior backing is removed; ten shallow modeled room proxies
  supply restrained warm interior cues behind uncut card-built openings;
  neutral review context prevents false green/blue glass tint; final visual QA
  `PASS_FINAL_VISUAL_QA` at 97/100.
- **Rejected — Halifax v3:** photo fragments tiled across the building.
- **Rejected — Calgary v3:** compound photo cards repeated over component
  faces, producing a noisy and structurally implausible result.

These precedents define the method, not a universal architectural style. Each
new archetype still requires its own complete reference sheet, unique-role
inventory, card set, and pilot approval.
