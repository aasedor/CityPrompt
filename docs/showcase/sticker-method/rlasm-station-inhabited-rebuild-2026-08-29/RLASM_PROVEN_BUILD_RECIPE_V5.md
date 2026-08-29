# RLASM v5 proven building recipe

This is the repeatable production sequence that produced the independently
approved Art Deco judicial courthouse v20, grand log lodge v25, and Chinese
Siheyuan v18 on 2026-08-28.

It is a build recipe, not a style prompt. Follow the gates in order. Do not
advance because a model is attractive, detailed, or reports zero generic
fallbacks. Advance only when the required relationship is visible in the
locked renders.

## 1. Select one exact catalogue building

Start with the exact archetype and variant, not a written style description.
Collect every compatible authoritative image for that same building. Assign
explicit roles: front, 60-degree oblique, true top or aerial, and side or rear
when available. Reject mixed sibling variants.

## 2. Lock the source contract before modeling

Create the candidate folder and `prework-manifest.json`. Record each source's
catalogue ids, path, view role, byte count, and SHA-256 hash. Build
`locked-source-board.png` from those exact files. Never replace a source image
without creating a new bounded candidate version.

```powershell
python scripts/prepare_catalogue_conditioned_pilots_v2.py <candidate-folder>
```

Do not start Blender until preparation reports
`PASS_SOURCE_AND_REFERENCE_LOCK_AWAITING_DRY_BUILD`.

## 3. Measure the architectural contract

Read the sources as three coordinated drawings.

- Front: total proportions, floor rows, entrance hierarchy, bay cadence,
  shoulders, setbacks, towers, gables, and crown.
- Oblique: depth, secondary masses, projections, side grammar, supports,
  balconies, porches, galleries, chimneys, and roof intersections.
- Top or aerial: footprint graph, ridge directions and extents, hips, valleys,
  cross-gables, courtyards, passages, landscape, and circulation zones.

Write the measurements into the builder as named dimensions and schedules. Do
not infer all three dimensions from the hero image.

## 4. Build family-defining geometry first

Complete identity massing before facade polish.

### Courthouse constructor

The passed courthouse uses a tall occupied shaft, occupied shoulder and upper
setbacks, five nested crown tiers from the top source, one seated flagpole, a
restrained bronze civic entrance, and narrow vertical bays with limestone piers
and metal spandrels continuing around both sides and the rear.

Its side shaft is a perforated limestone skin over an inset structural core.
Inter-bay piers and inter-floor spandrels form the wall; omitted cells are real
window cavities. Never place frames over a solid stone box.

### Lodge constructor

The passed lodge uses an asymmetric plan, one dominant and one smaller offset
front gable, a transverse rear roof joined into one closed graph, an offset
entry and connected stair, an offset foundation-to-roof chimney, a continuous
fieldstone foundation, full round-log construction, complete rear dormers, and
closed valleys. Never mirror the front or expose broad wood-textured carriers.

### Siheyuan constructor

The passed Siheyuan uses a layered axial compound, a grade-clear moon gate,
two-storey street rooms, raised central and rear halls, lower side halls,
family-specific lifted roofs, bounded ceramic ridges, closed secondary gables,
red posts between audited lattice bays, a planted gate sightline, and a clear
walk from street to court. Never substitute a four-bar ring or generic hips.

## 5. Finish the whole physical envelope

Before identity sources or material polish, inspect the unskinned building from
front, both sides, rear, rear-side, and aerial.

- Walls and gable fields close to their roof planes.
- Roofs form coherent weathering envelopes with closed valleys.
- Porches, balconies, galleries, chimneys, and stairs have visible load paths.
- Openings and architectural grammar continue around secondary elevations.
- Courtyards and passages remain physically traversable.
- No blank or generic carrier is exposed from a non-hero camera.

A convincing principal facade cannot compensate for unfinished side or rear
architecture.

## 6. Create the registered identity source

Use the exact locked source family to create a shadow-neutral orthographic
identity elevation for each identity-bearing facade. Preserve the raw output,
exact prompt, input paths and hashes, provider record, masking operations,
registered derivative, model datum, and UV bounds.

The identity source carries source-specific cadence, relief, joinery, ornament,
and zoning. Physical geometry still owns silhouette, roofs, opening depth,
supports, and circulation.

If the named identity is visible only in an oblique catalogue image, do not
crop that perspective into the model. Use the exact locked source as the sole
identity authority and create an isolated, shadow-neutral front-elevation
derivative of the clock, crest, seal, mosaic, or sign. Then:

- remove export padding without altering the identity pixels;
- preserve the derivative's native aspect ratio when sizing the UV plane;
- exclude surrounding coursing, windows, shadows, and facade perspective;
- record the exact prompt, source paths and hashes, raw-output hash, registered
  derivative hash, crop operation, physical carrier, and UV dimensions;
- render a straight-on identity close that shows every sticker edge inside its
  physical datum.

The Second Empire fire-station v14 crest is the regression example: v12 used a
hash-valid but oblique crop; v14 uses a source-conditioned orthographic relief
sticker seated inside the same carved stone carrier.

## 7. Enforce one visual owner per feature

Mount each identity crop only on its matching physical datum.

- Physical geometry owns flagpoles, chimneys, gates, canopies, returns, rails,
  and silhouette edges.
- Registered identity owns fine facade identity not separately modeled.
- Role-specific specimens own repeating construction on roofs, returns, side
  walls, paving, and landscape.

Clear competing source pixels where geometry owns the feature. Inspect eroded
alpha edges for pale or dark halos. Never use an identity sheet to hide wrong
massing or unfinished construction.

## 8. Derive role-specific supporting materials

Create atomic, tile-safe specimens from the same locked source family.

- Courthouse: buff ashlar, pale carved stone, bronze, aluminum, copper,
  granite, and neutral civic glass.
- Lodge: round logs, subtle chinking, staggered shingles, irregular fieldstone,
  dark timber, and warm neutral glass.
- Siheyuan: cool grey brick, grey ceramic tile, red lacquer timber, dark
  lattice, carved granite, paving, foliage, and translucent paper.

Record every specimen's source and hash. Reject perspective, baked shadows,
windows, doors, and recognizable scene fragments. Map continuous masonry and
paving in shared world-scale coordinates with explicit tile sizes in metres.
No generic fallback is allowed for an identity-bearing opaque role.

## 9. Construct openings from exterior to interior

This ordering was the final blocker on all three passed buildings. Every
reviewed opening must visibly contain:

1. exterior wall, brick, or cut-log face;
2. jamb, head, and sill return;
3. narrower inner sash, frame, or lattice;
4. low-iron pane or translucent paper;
5. a separately offset occupied-room plane;
6. short room sidewalls, head, or sill proving depth.

The structural carrier ends behind the room datum. Use a perforated skin over
an inset core for masonry. Split every log course at the jamb clearance and
expose cut ends. Pull hall carriers behind paper screens; alpha cannot reveal a
room through solid brick.

Keep glass nearly non-emissive and paper diffusive. Put restrained warmth on
the occupied room, not the pane. Uniform black, grey, cream, amber, or glowing
rectangles are not optical depth.

## 10. Complete circulation, landscape, and contact

Check that entrance stairs connect to landings and doors, foundations and
supports reach grade, passages have standing clearance, paths continue through
gates and planting, and all roof and facade projections visibly seat on their
carriers. The Siheyuan passed only after the exact gate-axis view framed a
layered planted court while preserving a clear walk.

## 11. Render the locked review camera set

Use neutral QA lighting. Mandatory roles are:

- `front.png` — identity and total proportions;
- `front_corner.png` — massing and projection depth;
- `aerial.png` — footprint and roof topology;
- `left_side.png` and `right_side.png` — grade-to-highest envelope;
- `rear.png` and `rear_side.png` — secondary continuity;
- `facade_close.png` — registration and material scale;
- `architecture_close.png` — family-defining junction;
- `glass_close.png` — oblique optical wall-section proof;
- family views such as `gate_close.png` and `courtyard.png`.

Whole-side cameras include grade, every occupied stage, roof or crown, and the
highest termination with margin.

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' `
  -b --python scripts/build_catalogue_conditioned_pilots_v2.py -- <candidate-folder>
```

Never overwrite an earlier candidate. Create a new bounded version for every
rerendered correction.

## 12. Run builder and pixel gates

Builder evidence records source, reference, GLB, and scene hashes; object and
render counts; identity count; generic fallback count; contacts; and cameras.
Those are audit records, not keeper proof.

Open every render at full resolution. In `glass_close`, point to wall, return,
sash or lattice, optical layer, and room separately. In aerial and rear-side,
look for carriers, open gables, floating ridges, roof slots, and material
regressions. If a relationship is not visible in pixels, fail locally before
independent review.

## 13. Request independent source-locked review

Give the reviewer the exact candidate, locked source board, every mandatory
render, and all prior P0 findings. Instruct them to ignore builder metadata as
visual proof. `PASS` requires zero P0 blockers across source fidelity,
geometry, architecture, materials, optics, contacts, visibility, and cameras.

When any P0 remains:

1. keep the candidate in `visual_rework_required`;
2. preserve its source, GLB, renders, evidence, and review;
3. implement only the finite blocker list in a new version;
4. regenerate the complete camera set;
5. repeat independent review.

## 14. Promote and publish only the passed version

After a zero-P0 pass, write `review/independent-review.json`, change only that
candidate to `keeper_approved`, retain all rejected versions, and build a phone
board pairing authoritative front, oblique, and top sources with matching model
cameras plus rear-side, optical close, and signature detail. Record bytes and
SHA-256 hashes. Promote only reviewed images and documentation through Git LFS.

```powershell
python scripts/build_registered_identity_phone_reviews.py
```

## 15. Pilot before scaling

For each new family or constructor change: dry-run source locking, build one
archetype, perform the local pixel review, obtain independent zero-P0 approval,
update the human and machine-readable memory, and only then start the next
finite batch. Never begin an open-ended generation loop.

## Final keeper checklist

A keeper answers yes to all of these:

- One exact catalogue variant and immutable source set?
- Matching front, oblique, and top geometry?
- Complete sides, rear, roofs, gables, supports, and passages?
- Registered identity mounted to matching physical construction?
- One visual owner per feature?
- Source-specific, correctly scaled opaque materials?
- Real exterior-to-interior openings with occupied depth?
- Coherent circulation, planting, foundation, and load paths?
- Complete neutral camera set?
- Local pixel gate passed?
- Independent reviewer recorded zero P0 blockers?
- Phone boards, hashes, review, and rejected history preserved?

If any answer is no, the building remains a candidate, not a keeper.

## Exact-source material correction lessons

The Victorian station, Rationalist hospital, and Second Empire fire-station
material correction added these mandatory steps:

- Zero generic fallbacks is necessary but not sufficient. Every dominant
  visible role must use a reviewed material sheet conditioned from the exact
  locked archetype: brick, ashlar, carved stone, slate, timber, copper,
  Carrara, serpentine, or family-specific equivalents. Store its SHA-256 in
  the source manifest and keep the locked source pixels unchanged.
- A material sheet describes morphology as well as palette: joint geometry,
  course size, grain direction, mineral variation, oxidation, roughness, and
  finish. A roughly correct colour with the wrong bond, block scale, or
  surface character remains generic.
- Generate sheets shadow-neutral and orthographic. Source sunlight, cast
  shadows, windows, ornament, and perspective do not belong in a repeatable
  albedo. Reintroduce illumination only in the neutral QA scene.
- Map every sheet in metres from one shared world-space datum. Front/rear,
  side, and sloped-roof roles may need distinct axes, but adjacent pieces must
  retain scale and phase instead of restarting the texture per object.
- Carved trim stays in the same source stone family unless the locked source
  proves a different material. Differentiate it with dressing, relief,
  roughness, and restrained value—not generic white paint.
- A window opening passes through every opaque owner. Cutting the finish skin
  while leaving the structural wall, dormer box, or overlap wing intact creates
  a pale panel or ghost outline. Cut wall and skin together, or remove the
  unprovable bay rather than presenting a false window.
- Review materials on front, both sides, rear, aerial, facade close, optical
  close, and the phone board. Preserve every superseded material pilot as
  rejected history; only a fresh bounded version may advance.

## New-family constructor lessons from the three-building proof batch

The station, hospital, and fire-station pilots added these mandatory steps:

- Resolve the current catalogue archetype and variant IDs before building. A
  legacy descriptive label is not source provenance.
- Inspect the registered crop itself before mounting it. It must contain only
  the role being registered: clock dial, serpentine panel, crest, or another
  bounded identity datum. Preserve crop-only failures as rejected prework.
- Never share one 2D coursed shader across perpendicular carriers. Front/rear
  masonry uses an explicit X-Z mapping; side masonry uses Y-Z. Record the
  mapping axis and inspect both a close view and the whole envelope.
- Texture scale is a physical measurement. Re-render when stone blocks,
  bricks, slate, or panel joints read as toy-sized or building-sized even if
  their palette is correct.
- Long repeated facades should use deterministic piers and spandrels when a
  chained boolean wall starts hiding openings. The structural core ends behind
  the occupied-depth datum; it never continues through a pane.
- A role skin cannot repair wrong massing. Lock the roof/plan topology, tower
  position, bay schedule, arcade, and side/rear continuation first; then mount
  the registered identity to its matching physical datum.
- Camera targets are part of the build contract. If a bay is removed during
  rework, update and visually recheck `glass_close`; a valid filename pointing
  at blank wall is failed evidence.
- Scale whole-building cameras from the highest actual object, including
  cupolas, train-shed arches, and weathervanes, rather than a nominal wall
  height. Large pale buildings require broad neutral fill so rear and side
  geometry remains readable without a moving spotlight.
- Zero generic-fallback metadata is not visual proof. The matched phone board
  remains the builder gate, and keeper promotion still requires a separate
  zero-P0 review.

## Victorian train-shed reconstruction sequence

Use this sequence whenever the archetype is dominated by an iron-and-glass
train shed rather than a masonry hall:

1. From the locked front/oblique/top views, solve the shed width:depth:rise,
   end-arch profile, headhouse:shed height, tower offset and platform axis.
2. Build one closed glass vault spanning the entire measured depth. Add
   repeated transverse trusses and longitudinal purlins at construction scale.
3. Close both ends with bounded glazing and physical iron frames. The front end
   must retain the source's monumental arch and lattice hierarchy.
4. Seat the vault on repeated source-coloured side columns, eave girders and
   arches; continue tracks and platforms through the full envelope.
5. Build the low asymmetrical headhouse separately: ground arcade first, then
   differentiated pointed pavilions, one offset clock tower and seated roofs.
6. Apply exact-source brick, sandstone and slate sheets on explicit wall/roof
   axes with measured metre scales. Assert that the candidate is enrolled in
   the source-material allowlist before rendering.
7. Rectify the clock into an isolated orthographic role sticker when the source
   is oblique. Register it to physical stone clock datums at native aspect.
8. Render front, 60-degree, top, both sides, rear, rear-side, facade close,
   glass close and great-arch close. Compare all roles before a builder pass.

A recognizable barrel roof is not sufficient. The candidate fails when the
shed is open, too short, supported by a sparse cage, or paired with a generic
repetitive headhouse.

The shed also fails when its transparent shell exposes no functioning station.
Before review, add physical track beds with sleepers and paired rails, raised
platforms with edge protection, supported platform canopies, source-backed
furniture, a headhouse-facing concourse arcade and connected stairs/guarded
galleries. Render both a platform oblique and a track-axis view; the aerial
alone is not interior proof.
