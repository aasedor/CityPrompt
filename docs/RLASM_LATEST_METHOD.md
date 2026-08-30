# RLASM v6.1 — integrated proven methodology

**Method name:** Reference-Locked Atomic Sticker-and-Massing (RLASM)
**Revision:** v6.1, 2026-08-29
**Purpose:** build source-specific, physically credible, reviewable 3D building
families without hiding generic construction behind a good hero image.

This is the single canonical current method. Earlier package-local
`RLASM_*_V5.md` files are immutable historical records, not competing current
instructions. The executable companion is
`tools/archetype_compiler/rlasm_method.json`.

Active-tree storage and retirement rules are defined by
`docs/RLASM_REPOSITORY_POLICY.md`. Failed candidate evidence remains immutable
but belongs in content-addressed artifact storage rather than the active Git
tree. Only reviewed keeper packages are promoted into Git.

## Authority and review boundaries

When records disagree, use this order:

1. exact locked catalogue pixels and their hashes;
2. this canonical method and its executable companion;
3. the candidate's immutable source, geometry, material, and evidence records;
4. the current holistic independent review;
5. package-local historical recipes and general building memory.

General `high_quality_ready` status is not RLASM keeper approval. A builder,
material specialist, contact specialist, or other scoped reviewer may close
only the scope they examined. Only a separate holistic source-locked reviewer
who inspects every required view may promote a candidate to `keeper_approved`.
A later image may expose a missed defect; the keeper is then demoted or
superseded, never defended by its earlier metadata.

## The central lesson

Quality is not the presence of named objects or source-labelled materials. It
is the visible correctness of their relationships.

A candidate fails when the source, massing, roof, walls, openings, materials,
identity surfaces, supports, circulation, landscape, cameras, or review state
do not form the same building in pixels. Hashes, object counts, successful
Booleans, zero-fallback counters, and contact metadata are audit evidence; they
never override the rendered comparison.

## What we learned

### 1. The exact archetype is the goalpost

- Lock one catalogue archetype, one variant, and a compatible front/oblique/top
  source set before modeling.
- Preserve source paths, byte counts, SHA-256 hashes, and role labels.
- Use the top or highest oblique view to solve plan topology and roof ridges.
- Treat the visible images as topology authority when prose conflicts with
  them; record the conflict instead of averaging it away.
- A family description may guide interpretation, but visible locked pixels
  override conflicting prose about storeys, bays, roof form, materials, or
  program.
- A plausible family member is not a match. The early station was a convincing
  greenhouse-like shed but not the locked Victorian station.

### 2. Architecture must be solved before surface polish

- Measure width, depth, height, floor datums, bay cadence, roof rise, setbacks,
  entrance position, tower/chimney offsets, and courtyard passages as ratios.
- Build the family-defining constructor first: civic setbacks and vertical
  bays, asymmetric lodge roofs and log walls, axial courtyard halls and lifted
  eaves, or a complete inhabited train shed.
- Continue the architectural grammar around both sides and the rear.
- A registered facade cannot repair a wrong plan, mirrored asymmetry, blank
  carrier, unfinished gable, or generic secondary elevation.

### 3. Complete envelopes beat hero facades

- Every visible volume needs closed walls, roof or cap, openings, materials,
  and a valid program.
- Roofs are weathering graphs: ridges terminate inside roofs, valleys close,
  caps bear on walls, chimneys reach supports, and intersections do not expose
  black slots.
- Foundations, stairs, balconies, porches, galleries, canopies, and projections
  require visible load paths and grade contact.
- Courtyards and gates require traversable paths and adequate standing clearance.

### 4. Identity surfaces and geometry have different jobs

- Create a dedicated shadow-neutral orthographic identity source for each
  identity-bearing facade or bounded role.
- Use source-specific identity pixels for bay cadence, relief, joinery,
  ornament, and material zoning.
- Use physical geometry for silhouette, depth, openings, supports, returns,
  circulation, roof topology, and contact.
- Give each feature one visual owner. Remove duplicate source pixels when
  geometry owns a flagpole, gate aperture, chimney, canopy, frame, or reveal.
- Never mount a perspective crop. Rectify an oblique crest, clock, emblem, or
  sign into an isolated front-elevation derivative, preserve native aspect,
  prompt, inputs, hashes, and crop operations, then prove all four edges on its
  physical carrier.
- Register to the carrier's exterior face, including its actual thickness,
  rather than to an abstract centre datum. A correctly rectified identity can
  disappear inside a thick carrier when this offset is omitted.
- Inspect the generated file's real alpha channel. A checkerboard preview is
  not proof of transparency. If a generator returns checker pixels, a
  deterministic, recorded alpha extraction may repair the derivative without
  changing its identity content.
- A role card is an authority record, not automatically a surface to mount.
  Mount it only where it supplies bounded identity pixels that geometry and a
  repeating specimen do not own.

### 5. Source-specific materials are more than colour

- Condition every dominant opaque role from the exact locked source family.
- A reviewed specimen must preserve bond or course morphology, joint scale,
  grain direction, mineral variation, finish, oxidation, roughness, and aging.
- Reject perspective, baked light, windows, borders, or recognizable facade
  fragments in repeating material sheets.
- Map in metres from shared architectural datums. Use explicit X-Z, Y-Z, and
  slope-local axes while maintaining scale and phase across adjacent objects.
- A family-specific name or source hash on a generic noise/brick shader is
  still a generic material.

### 6. One physical substance needs one building-level material authority

- When walls, returns, quoins, arches, cornices, dormers, columns, and an
  identity carrier are all limestone, assign them one material-family ID.
- Preserve semantic finish differences—coursed, dressed, or carved—through
  joints, relief, roughness, and restrained value, not a second hue family.
- Keep truly different materials distinct: slate, timber, copper, iron, glass,
  lacquer, paper, and paving do not inherit the stone family.
- Review the authority across front, both sides, rear, aerial, facade close,
  and glass close. The fire station passed only after cool-white trim was
  replaced by crest-authorized warm aged limestone throughout the envelope.

### 7. An opening is a wall section, not a frame

Every reviewed opening must visibly read from exterior to interior:

1. cut wall, masonry, brick, paper-screen wall, or terminated log courses;
2. jamb, head, and sill return;
3. narrower recessed sash, frame, muntin, or lattice;
4. optical glass or mildly translucent paper;
5. a separately offset occupied-room plane;
6. enough room side/head/sill depth to prove the separation.

Cut every opaque owner. A finish skin cut over a solid wall or dormer produces
a ghost panel even when glass objects exist. Keep light on the occupied room,
not on a flat glowing pane.

### 8. Roof-mounted openings require a contact section

- Solve the dormer or lantern position from the constructed sloped roof plane.
- Make its lower cheeks cross that plane; do not hang a finished frame in air.
- Size the cutter against the complete thickened body, not an earlier wall.
- Close the gable, seat and bound the roof cap, and assign flashing/apron
  ownership at the weather joint.
- Prove wall-to-roof penetration and opening depth together in an oblique
  contact close, both whole-side views, and an aerial.
- Preserve partial attempts. Fire-station v19 integrated the body but exposed
  a new cutter-depth failure; v20 passed only after the full wall cut.

### 9. Transparent architecture must reveal its program

- A correct glass shell is incomplete when it exposes an empty floor.
- Build source-defining tracks, platforms, canopies, furniture, concourse
  openings, galleries, guardrails, supports, and connected stairs.
- Connect the transparent hall to its opaque frontage.
- Add program-specific interior views, such as platform oblique and track axis;
  an exterior aerial cannot prove occupation or circulation.
- The program must be unmistakable at review scale. Source-specific presses,
  tracks, platforms, market stalls, machinery, or other complete workflows
  cannot be substituted by ambiguous generic benches and furniture.
- Multi-wing glass roofs, monitors, and lanterns are one weathering envelope:
  derive one union outline, close every vertical face, assign one continuous
  curb/flashing owner, and trim all ribs and ridges to bounded junction nodes.
  Overlapping transparent roof primitives are not an acceptable shortcut.
- Use one source-conditioned optical/material authority across every sloped,
  vertical, end, and valley facet of a joined transparent roof. Bounded pane
  variation is acceptable; unexplained switches between perforated, opaque,
  white, and black facet families are not.
- Treat perimeter ironwork, brackets, finials, and crest shoulders as
  source-bearing architecture. Match their section, cadence, contact profile,
  silhouette, and elevation-specific variation instead of repeating a generic
  railing or ornament template around the roof edge.

### 10. Camera design is part of construction

- Author cameras from actual highest and widest geometry, not nominal dimensions.
- Whole-side/rear views include grade, complete footprint, all occupied stages,
  roof/crown, and highest termination with neutral margin.
- "Not cropped" is insufficient: retain visible neutral safety margin beyond
  the nearest grade/base corner, full footprint, and highest termination.
- Match source/model roles: front, 60-degree/front-corner, true top/aerial,
  both sides, rear, rear-side, facade close, glass close, and a family-specific
  signature or contact close.
- Use neutral broad QA lighting. Cropped or underexposed evidence is invalid
  even when the filename exists.
- Revalidate every camera target and occlusion after geometry changes. A proof
  camera that was valid before a lantern, tower, tree, or interior machine was
  added may become blocked or cease to prove its named relationship.
- Build 1080×1920 phone comparisons. Phone scale exposes silhouette,
  hierarchy, material, and carrier problems that isolated renders conceal.

### 11. Review state must be honest and non-destructive

- The builder may declare only a builder pass.
- Keeper promotion requires a separate source-locked reviewer and zero P0
  blockers across fidelity, geometry, architecture, materials, optics,
  contacts, visibility, and cameras.
- Never edit failed metadata into a pass. Advance a new bounded version,
  rerender the complete camera set, and repeat review.
- Preserve rejected sources, GLBs, renders, evidence, and reviews. They are the
  causal record that prevents the same failure from returning.
- Valid lifecycle states are `prework`, `building`, `build_valid`,
  `visual_review_ready`, `independent_review_pending`, `keeper_approved`,
  `visual_rework_required`, `superseded`, `rejected`, and `archived`.
- A scoped pass never changes the lifecycle to `keeper_approved`.

### 12. Pilot before scale

- Dry-run source locking and manifest creation.
- Build one representative archetype.
- Run the local pixel gate and phone comparison.
- Obtain independent zero-P0 approval.
- Update this method, human memory, machine memory, and tests.
- Only then start the next finite batch. Never run an open-ended correction or
  generation loop.

## Authoritative workflow

### Phase A — preserve and lock

1. Run `git status --short --branch`; inventory overlapping user work.
2. Create a named initiative branch/worktree when tracked source must change.
3. Never overwrite an existing candidate directory.
4. Lock exact archetype/variant ids and immutable front, oblique, and top views,
   plus every compatible side/rear/detail view that exists.
5. Build a source board and manifest with paths, roles, bytes, and hashes.

**Gate A:** source identities and hashes resolve; at minimum front, oblique,
and top depict one coherent variant; all available compatible views are
enrolled; no text-invented reference substitutes for catalogue proof.

### Phase B — measure and specify

1. Extract dominant ratios and datums.
2. Write the plan/roof graph, bay schedule, program, and asymmetry contract.
3. List identity-bearing geometry, identity surfaces, repeating material roles,
   transparent program, circulation, landscape, and contact requirements.
4. Author the full camera roster before building.

**Gate B:** a reviewer can explain what makes this exact building different
from a generic family member without referring to materials alone.

### Phase C — construct the unskinned building

1. Build base, occupied masses, courts, setbacks, towers, roof graph, and caps.
2. Construct openings and structural bays from one audited schedule.
3. Complete sides, rear, gables, valleys, supports, foundations, and passages.
4. Add transparent program and circulation visible through the shell.
5. Render clay/neutral topology views and correct all P0 geometry first.
6. Prove front-, side-, and rear-facing openings in their own orientation;
   a successful Boolean operation or object count is not visible proof that
   an orientation-specific cutter reached the intended carrier.

**Gate C:** the unskinned model has the correct silhouette, topology, program,
load paths, and complete envelope from every mandatory view.

### Phase D — register identity and materials

1. Create or isolate orthographic identity sources from the locked family.
2. Record prompts, inputs, hashes, masks, native aspect, physical datums, and UVs.
3. Record the carrier exterior-face datum and verify the mounted identity's
   four edges; include carrier thickness in the registration calculation.
4. Enforce one visual owner per feature, inspect actual alpha-channel pixels,
   and record any deterministic alpha post-process.
5. Derive tile-safe supporting specimens from the same family.
6. Register material family IDs and metre-scale mapping axes/phases.
7. Fail closed if a reviewed candidate is missing exact-source enrollment.

**Gate D:** no visible identity-bearing opaque surface relies on a generic
fallback, and no identity source hides wrong geometry or unfinished returns.

### Phase E — build optical and contact sections

1. Cut every opaque owner at each opening.
2. Add returns, recessed frame/lattice, optical layer, and occupied depth.
3. Verify log ends, paper translucency, room clearance, and carrier termination.
4. Seat projections, caps, ridges, chimneys, stairs, and foundations.
5. Add family-specific contact views for fragile junctions.

**Gate E:** each claimed relationship can be pointed to in rendered pixels.

### Phase F — render and compare

Required baseline files:

- `front.png`
- `front_corner.png`
- `aerial.png`
- `left_side.png`
- `right_side.png`
- `rear.png`
- `rear_side.png`
- `facade_close.png`
- `architecture_close.png`
- `glass_close.png`
- family-specific contact/program views

Open every file at full resolution. Compare locked source and model in matched
roles, then build the phone board. Check silhouette, ratios, roof topology,
material morphology/scale, opening depth, supports, contact, landscape,
circulation, camera validity, and visibility.

**Gate F:** builder review has zero unresolved local P0 blockers. Evidence
counters support the decision but do not make it.

### Phase G — independent review and bounded iteration

Give the independent reviewer the exact source board, complete render set,
phone comparison, and previous finite blocker list. Tell the reviewer to ignore
metadata as visual proof and to run a holistic regression even when the latest
change was limited to materials, glazing, or contact.

If any P0 remains:

1. retain the current version in `visual_rework_required`;
2. record exact symptom, cause, and finite fix;
3. create the next version without overwriting;
4. rerender every required camera, not only the changed close;
5. repeat independent review.

**Gate G:** zero independent P0 and P1 blockers in a holistic review. A scoped
review may close a named blocker category but cannot satisfy this gate.

### Phase H — promote, document, and scale

1. Write the independent review record and mark only that candidate approved.
2. Publish reviewed phone images, full renders, sources, hashes, and evidence.
3. Update `docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md`,
   `tools/archetype_compiler/high_quality_building_memory.json`, and the
   version assertion test together.
4. Preserve rejected history and external heavyweight artifacts.
5. Begin a finite next batch only after the representative passes.

## Hard-stop failure catalogue

| Symptom | Root cause | Required response |
| --- | --- | --- |
| Detailed model still looks unlike source | family label substituted for exact topology | remeasure and rebuild plan/roof/bay hierarchy |
| “Exact-source” material still looks generic | generic recipe was renamed or only palette matched | condition role-specific morphology and metre scale from locked source |
| Front works; sides/rear are boxes | identity stopped at the hero elevation | continue family grammar and openings around the envelope |
| Crest/clock/emblem is skewed | oblique pixels were cropped directly | create an isolated orthographic derivative and remount at native aspect |
| Black/flat/glowing window | no visible wall section or carrier blocks it | cut every owner and rebuild exterior-to-interior depth |
| Dormer floats or becomes blank | body does not cross roof or cutter is too shallow | solve roof contact and full-depth cut in a new version |
| Roof has shards, rods, or black slots | caps/ridges/valleys have no bounded owner | rebuild the closed weathering graph and prove aerial/rear-side |
| T or cross lantern is made from overlapping sheds | transparent wings have separate weathering owners | rebuild from one union outline with continuous curb/flashing and bounded members |
| Joined lantern still reads perforated or checkerboard | facets use conflicting optical/material families | apply one source-conditioned translucent authority across every facet with bounded pane variation |
| Roof edge looks generically decorative | railing, brackets, finials, or crests repeat a stock profile | rebuild source-scale sections, cadence, contacts, and elevation-specific silhouettes |
| Glass hall reads as greenhouse | program and circulation were omitted | construct inhabited systems and dedicated interior views |
| Workshop contains only generic benches | object presence was confused with identifiable program | build and clearly frame a complete source-specific machine or workflow |
| Correct emblem is buried or partly missing | sticker was registered to carrier centre or alpha was assumed | mount to the exterior-face datum and inspect the real alpha channel |
| Clay metadata says openings exist but a side remains solid | Boolean success was treated as visual proof | render and inspect orientation-specific front/side/rear openings |
| Metadata says pass but phone view fails | audit evidence was treated as visual proof | demote or supersede the candidate, record P0s, rerender and independently repeat review |
| Scoped review says keeper but later view exposes a defect | category closure was confused with holistic promotion | preserve the scoped result, rescind keeper status, run a complete adversarial review |
| Whole-side camera crops or touches the frame | camera used nominal dimensions or no safety margin | reframe actual grade-to-highest geometry and full footprint with visible neutral margin |

## Definition of a keeper

A keeper answers yes to every question:

- Exact variant and immutable compatible sources?
- Measured source-specific plan, silhouette, hierarchy, and roof topology?
- Complete front, sides, rear, gables, supports, passages, and program?
- Orthographic registered identities on matching physical datums?
- One visual owner per feature?
- Exact-source, physically scaled materials with correct axes and family IDs?
- Openings with visible returns, optical layer, and occupied depth?
- Coherent foundations, circulation, landscape, and weathering contacts?
- Complete valid neutral camera set and phone comparison?
- Builder pixel gate with zero P0s?
- Independent holistic source-locked pass with zero P0s and P1s?
- Rejected history, hashes, reviews, and reviewed deliverables preserved?

If any answer is no, the building is a candidate—not a keeper.

## Current forward-standard exemplars

The following raw-photo-only pilots are the current RLASM v6.1 reference
keepers. Each began with exact catalogue photographs and no prebuilt model,
then passed a separate holistic source-locked review with zero P0 and P1
blockers:

- `07-barcelona-modernist-printing-house-rlasm-v7`: transparent workshop
  program, one sealed T-monitor weathering envelope, source-scale roof-edge
  ironwork, and complete physical openings.
- `10-amsterdam-bell-gable-house-rlasm-v10`: exact floor/bay hierarchy,
  continuous bell-gable weathering construction, source-scale Dutch roof
  material, integrated shed dormer, and visible residential circulation.
- `rlasm-amsterdam-hofje-medieval-v023`: enclosed charitable-housing court,
  full-depth gate passage, clipped living garden, source-conditioned curved
  pantiles, pale rolled-lead dormers, and visibly occupied residential depth.

These exemplars define the present visual and evidentiary floor. They are not
generic templates: each new building must still solve its own locked geometry,
materials, program, contacts, and identity from source pixels.
