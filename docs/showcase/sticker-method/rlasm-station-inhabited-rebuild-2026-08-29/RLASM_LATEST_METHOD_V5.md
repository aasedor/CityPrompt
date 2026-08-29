# RLASM latest production method — v5

The concrete start-to-finish sequence that produced the independently passed
courthouse v20, lodge v25, and Siheyuan v18 is recorded in
[`RLASM_PROVEN_BUILD_RECIPE_V5.md`](RLASM_PROVEN_BUILD_RECIPE_V5.md). Use that
recipe as the execution checklist; this file remains the cumulative learning
record and keeper gate.

This batch uses a bounded reference-locked atomic sticker-and-massing workflow.

1. Lock one coherent three-view reference before modeling.
2. Inventory every unique architectural role and every reference-specific material.
3. Create a dedicated card for each unique role; repeating bays may reuse a card only when they are truly the same role.
4. Create clean material specimens without card labels or borders and make them seam-safe before Blender use.
5. Create a dedicated orthographic facade sticker with exterior chroma removed and neutral windows without baked scenery or reflections.
6. Build a complete physical envelope: independent volumes, real roofs, local wall planes, occupied glazing depth, rear/service elevations, and physically supported projections.
7. Mount the facade sticker flush to its matching physical facade. Never use a footprint-wide carrier box as visible geometry.
8. Use neutral low-iron glass whose reflection comes only from the current CityPrompt/render context.
9. Render front, corner, aerial, side, rear-side, facade-close, and glass-close views.
10. Compare every visible side to both the authoritative catalogue archetype images and the locked reference. Reject unfinished sides, floating objects, generic materials, hidden giant boxes, archetype drift, or reference drift before scaling.

## Mandatory keeper-promotion task gate

Completing prework, producing a GLB, passing an automated contact audit, or
reporting zero generic material fallbacks does not make a candidate a keeper.
Every candidate must complete all of these tasks before `keeper` may be used:

1. **Prove source provenance.** Record the exact catalogue archetype and
   variant ids, authoritative image paths, byte counts, and SHA-256 hashes.
   A text-only invented reference or an untraceable source is a hard failure.
2. **Review reference fidelity.** Compare the locked multi-view reference to
   the authoritative archetype images for footprint, massing, floor count,
   proportions, roof topology, entrance position, opening rhythm, material
   zoning, and identity-bearing details. Correct or regenerate drifted
   references before reviewing the model.
3. **Perform a full geometry review.** Compare front, corner, aerial, side,
   rear-side, facade-close, and glass-close model renders to both source tiers.
   Inspect every exterior and courtyard volume, roof junction, opening,
   projection, support, contact, circulation void, and service elevation.
4. **Perform a full architectural review.** Verify the archetype's structural
   grammar, program, base-middle-crown hierarchy, public entrance, roofline,
   material character, glazing system, and distinctive silhouette. A detailed
   but architecturally different building fails.
5. **Fix every relevant finding.** Maintain a discrepancy ledger, repair the
   geometry, architecture, materials, glazing, and reference package as
   required, then regenerate the complete locked review set. Partial fixes and
   hero-view-only fixes do not close the task.
6. **Repeat review after the fixes.** The corrected on-disk GLB must pass the
   same three-way archetype/reference/model comparison with no unresolved
   blocker. Automated audit results are supporting evidence only.
7. **Record independent approval.** A reviewer other than the builder records
   the final decision, evidence paths, review date, and zero unresolved
   blockers. Until then the only valid states are `awaiting_visual_qa`,
   `visual_rework_required`, or `rejected`; never `keeper`.

The machine-readable batch task list is
[`keeper-review-task-list.json`](keeper-review-task-list.json).

## Roof and carrier-volume learning

- Domes, cupolas, turrets, ventilators, and mansards must use style-specific physical silhouette profiles. A generic onion profile is forbidden.
- A dome profile must seat on a matching drum; its radius and height must be checked against the reference silhouette from front and aerial views.
- Any mass visible behind a sticker must be an authored building volume with a real roof/cap, local openings, finished materials, and a valid architectural role.
- A support volume that appears as a blank giant box in any camera is a hard failure, even when the front sticker looks good.
- Rear courts and non-rectangular footprints must remain physically open where the reference shows them open.

The first Ottoman pilot was rejected twice for an oversized radial dome profile
and an unfinished central carrier volume. Candidate v3 was previously treated
as the corrected production pilot, but it remains `visual_rework_required`
until authoritative archetype provenance, the full three-way review, relevant
fixes, repeat review, and independent approval are complete.

## Catalogue-conditioned pilot learning — highway motor hotel

The first pilot made with the enforced method used
`highway_motor_hotel / hotel_roadside_motel`. Its three authoritative catalogue
views proved that the building is a one-storey U-shaped motor court with an open
road entry, two parallel room wings, a rear cross-wing, an office at the left
front, and a freestanding pylon at the right road edge. The earlier text-only
Googie candidate had drifted to a different program and could not be repaired by
surface detail alone.

- Authoritative images must be passed into reference generation, and their
  paths, bytes, and hashes must be recorded. Prompt prose is not provenance.
- The highest or strict-top catalogue view controls plan topology and roof-ridge
  directions. A front hero cannot establish whether a court is U-shaped,
  enclosed, or merely a shallow facade.
- Identity-bearing program elements must survive together: room doors and
  paired windows facing the court, the embedded office, the open road entry,
  the striped outer wing, and the freestanding pylon.
- A source crop is not automatically a usable material. It must pass a visual
  seam/tiling check before mapping. Crops containing perspective, shadows,
  edges, or adjacent roles are rejected even when their hashes are valid.
- When no clean atomic crop exists, author or generate a clean source-derived
  specimen from the locked catalogue image, then review its palette, scale,
  joints, edge continuity, and repetition before use. A procedural shader may
  be used as a diagnostic, but it cannot pass the material gate merely because
  it has a family-specific name or records the source hash.
- Render a dedicated rear-side roof-junction view. Intersections that appear as
  voids require physical valley or gable closures, even when front and aerial
  views look correct.
- Parking geometry is architectural evidence: stall lines must run from each
  room wing into the court, wheel stops must face the rooms, and the road entry
  must remain unobstructed.
- Preserve every rejected build iteration. The motel pilot retained v1 through
  v4, allowing each failure (roof hierarchy, camera omission, non-seam-safe
  photo tiling, and valley closure) to remain auditable instead of being erased.
- A phone hero must show both the office and pylon without allowing the sign to
  hide the building. It remains presentation evidence only; side, rear, aerial,
  and close views still control promotion.

## Three-family calibration learning — courthouse, lodge, and Siheyuan

Three additional catalogue-conditioned pilots tested the method against
unrelated construction grammars. The Art Deco courthouse, Grand Log Lodge, and
Chinese Siheyuan all reached complete physical envelopes with traceable source
hashes, zero generic material fallbacks, zero facade stickers, complete review
camera sets, and preserved GLBs. The phone source/model comparison nevertheless
rejected all three for further visual rework. This is a method finding, not a
promotion failure to hide: source provenance and technical completeness do not
guarantee source-level architectural quality.

- A prepared concept without an exact catalogue archetype id, variant id, and
  compatible source images is invalid even when its prose and material cards
  are detailed. The Moroccan post office, Norwegian Dragon lodge, and Korean
  Hanok guild hall v1 folders are preserved but rejected as text-invented work.
- When a compatible three-view catalogue set already exists, an exact-pixel
  deterministic source board is the preferred lock. It avoids generative drift
  and makes silhouette, plan topology, and roof comparisons reproducible.
- Camera framing is part of the architectural contract. Generic dimension-based
  cameras repeatedly cropped crowns, flagpoles, roof junctions, or courtyard
  topology. Each family must author whole-silhouette, aerial/topology, rear-side,
  and identity-detail cameras before the first build.
- Phone comparison is a stronger gate than isolated render review. At phone
  scale the courthouse still lost carved relief and stepped shoulder hierarchy;
  the lodge retained an over-broad roof and under-articulated secondary sides;
  and the Siheyuan flattened its pavilion/eave hierarchy and garden detail.
- Physical completeness is necessary but not sufficient. A real moon-gate void,
  continuous chimney, supported porch, closed roof, and finished rear elevations
  may all pass while the building still reads as a simplified cousin of the
  source. The promotion gate must explicitly score silhouette hierarchy,
  family-specific section, joinery/ornament density, and material depth.
- Broad decorative strips can invert the source hierarchy. Segment spandrels,
  reliefs, rails, and trim by their actual bays and keep structural piers, roof
  masses, and entrance volumes dominant.
- Identity-bearing roof and chimney systems require front, aerial, rear-side,
  and close proof together. A chimney that is continuous but hidden below the
  ridge—or a cross-gable that exists but reads as a detached triangle—fails.
- Metadata can conflict with the visible source. When floor-count prose and
  authoritative images disagree, record the conflict and use the images to
  govern visible topology while preserving the discrepancy in evidence.
- The next method revision must replace generic primitive aggregation with
  family-specific high-level constructors: stepped civic shoulders and carved
  relief zones; joined log gables, timber joinery, and coursed stone; lifted
  ceramic eave sections, carved gate caps, and layered courtyard landscapes.
  Do not scale the batch until one representative from each grammar passes the
  phone source/model comparison without architectural blockers.

## Constructor-refinement learning — three builder passes

The courthouse v5, lodge v10, and Siheyuan v5 passed the builder geometry and
architectural scan after the failed phone comparisons were converted into
constructor changes. Their overall builder passes were later rescinded when an
independent phone review exposed generic shared material recipes. Their geometry
learnings remain valid, but those versions are `visual_rework_required`.

- Window bays and structural piers are separate schedules. Generate occupied
  openings first, place piers only in the spaces between them, and reject any
  elevation where a pier bisects a window.
- A setback crown is occupied architecture, not a decorative stack. Every
  visible stage needs a finished wall envelope, deliberate openings, a cap,
  and proof from front, aerial, side, and rear-side cameras.
- A solid gable-roof helper must not close the public gable end with roof
  material. Use paired descending roof planes, a separate occupied gable
  field, physical rake members, and a ridge; prove the sign convention before
  a heavy render so eaves cannot rise away from their supports.
- Intersecting roof end caps are a common source of detached triangular shards.
  Leave internal gable ends open only where another closed roof volume owns the
  intersection, and inspect the result from aerial and rear-side views.
- Chinese roof ridges must inherit the ceramic roof family, stop inside the
  roof footprint, and seat on a closed lifted-corner roof. Pale generic rods or
  ridge bars extending past the roof are hard failures.
- Gate caps, chimneys, entrance canopies, and other identity parts must be sized
  as members of the whole hierarchy. A physically connected part still fails
  when it dominates the source composition or reads as a floating slab.
- A builder pass is recorded only after the corrected GLB is rerendered in the
  full locked camera set and survives a 1080 × 1920 source/model comparison.
  Builder pass does not authorize keeper promotion.

## Material-fidelity correction — source-derived specimens and physical scale

The material objection to courthouse v5, lodge v10, and Siheyuan v5 exposed a
false positive in the audit: `generic_fallback_count: 0` meant only that a
material was labeled as family-specific. The dominant stone, timber, shingle,
brick, tile, and paving surfaces still came from shared noise, wave, or brick
node recipes. Renaming a generic recipe and attaching a source hash does not
make its visible result reference-specific.

- Material acceptance is visual and role-specific. In the same phone frame,
  stone, timber, shingles, brick, ceramic tile, lacquer, metal, and paving must
  remain distinguishable by construction pattern, scale, palette, roughness,
  and joint behavior.
- Every dominant opaque envelope role needs a reviewed specimen or an equally
  explicit source-derived construction asset. The review records the specimen
  filename and SHA-256 hash; a material name alone is not evidence.
- Generated or extracted specimens must be orthographic, flat-lit, free of
  windows and other facade roles, low in baked shadow, and seam-safe. They are
  mapped to physical geometry; they are never facade-photo projections.
- Object-local generated coordinates can make one specimen change scale on
  every block. This failed on lodge v12, where chimney stones became smeared on
  the main shaft and miniature on corner blocks. Repeating masonry and paving
  use a shared world-scale mapping with an explicit tile size in metres.
- Generated-coordinate procedural Brick Texture is not a universal masonry
  solution. Courthouse v6 lost readable ashlar joints, and Siheyuan v6 produced
  vertical wall striping, printed roof grids, and oversized paving. Both are
  preserved as rejected diagnostics.
- Material-scale review must include a close view and a whole-building phone
  view. Close views expose smearing and projection seams; the phone view proves
  that construction roles remain legible without excessive contrast or noise.
- Flat source-calibrated PBR remains appropriate for genuinely smooth roles
  such as glass, dark occupied depth, and small metal trims. It is not an
  acceptable substitute for identity-bearing masonry, timber, shingles, roof
  tile, or paving.
- Courthouse v8, lodge v13, and Siheyuan v8 passed the builder material scan,
  but an independent source/model review rejected all three. Their atomic
  specimens were valid supporting materials; none carried the source-specific
  bay hierarchy, joinery, relief zoning, roof composition, or opening cadence
  required of a registered identity skin.

## Registered-identity correction — exact sources bound to physical construction

The independent review established that role-atomic specimens and a complete
physical envelope still do not reproduce a particular building. The production
method now requires both layers: a registered source-specific identity surface
and physical, family-specific construction. Neither layer may substitute for
the other.

- Generate one shadow-neutral orthographic identity source from the exact
  locked catalogue views, retain its raw output, exact prompt, source hashes,
  provider/output record, masking operations, and registered derivative.
- Register the identity source only to the audited facade datum or semantic
  surface it describes. It may carry bay cadence, relief, joinery, and material
  zoning; it may not conceal wrong massing, hide an unfinished return, or act
  as a footprint-wide carrier.
- Give every identity feature one visual owner. If the physical model owns a
  flagpole, chimney, circular gate aperture, window reveal, canopy, or other
  silhouette/depth feature, remove or clear the competing pixels from the
  identity source before mounting it. Duplicate ownership is a hard failure.
- Decontaminate alpha edges after exterior removal. Pale backgrounds and dark
  mask fringes around roofs, chimneys, gates, and gables become visible halos
  in neutral review lighting even when the alpha channel is technically valid.
- Derive tile-safe stone, timber, shingle, brick, ceramic, lacquer, foliage,
  and paving specimens from the same locked source family. They support the
  registered identity on physical side walls, roofs, returns, soffits, and
  landscape; they do not replace it.
- Rebuild the family-defining geometry before polishing material metadata:
  courthouse stage footprints and pier/spandrel grammar, lodge asymmetrical
  gable/chimney topology, and Siheyuan axial hierarchy, gate passage, lifted
  roofs, inward galleries, and planted court.
- Continue the architectural grammar around all visible secondary elevations.
  A convincing registered front paired with punched generic side windows,
  blank rear walls, open roof intersections, or a black carrier void fails.
- Glazing and paper screens are wall sections. Provide a recess, perimeter
  frame, pane or paper layer, and occupied depth; prove them in a dedicated
  `glass_close` view. Flat cards and glowing grids are insufficient.
- Use matched review roles: source/model front, front-corner or 60-degree
  oblique, true aerial/topology, rear-side, facade close, glass close, and one
  family-specific signature junction. Keep the lighting neutral enough to
  inspect support, contact, material scale, and occupied depth.
- Builder evidence may report source hashes, one or more registered identity
  surfaces, zero generic fallbacks, zero declared floating contacts, and a
  complete camera set, but keeper promotion still requires a separate reviewer
  to pass the visible source/model comparison with zero P0 blockers.

The rejected v8/v13/v8 trio and every subsequent bounded correction remain
preserved. Only the latest rerendered candidates may return to independent
review; metadata from an earlier pass is never edited into approval.

## Repeat-review learning — opening topology, proof cameras, and axial landscape

The v13/v18/v11, v16/v21/v14, and v17/v22/v15 repeat reviews exposed a second
class of false positive: a correctly named pane, depth plate, log wall, gable
roof, or planted court can exist in the scene while the required relationship
is visibly absent. The review camera—not object metadata—decides whether the
relationship has been proved.

- Never clear source-window pixels before an exact replacement bay schedule is
  registered and test-rendered. If the principal identity source owns the fine
  front-window cadence, preserve those pixels and prove the physical glazing
  wall section on a fully constructed secondary bay.
- A window is not a grille placed over construction. Masonry or log courses
  terminate at audited jamb, sill, and head clearances; the return bridges from
  the wall face to a set-back pane or paper screen; a separate occupied layer
  sits behind it. Course-splitting is part of the constructor.
- A carrier still blocks the room layer even when decorative courses are cut.
  Cut the carrier, or place a deliberate dark opening owner ahead of it and
  keep the pane and occupied layer on distinct, visibly separated datums.
- Transmission, alpha, emission, and layer names are not optical evidence. The
  locked `glass_close` must visibly show a grazing jamb return, the pane/screen
  offset, and a neutral or warm occupied layer. If those depths collapse at
  review resolution, the wall section fails.
- Whole-side proof cameras include grade, all occupied stages, roof/crown, and
  the complete highest termination with margin. Cropped side close-ups may be
  additional evidence but cannot replace the whole-envelope left/right views.
- A gable roof is incomplete when its rectangular wall stops at the eave and
  leaves a triangular void. Every exposed end receives a matching gable field
  or a different source-consistent closed roof constructor.
- A traversable moon gate can still fail identity review if it frames an
  unfinished plaza. The exact axial camera must frame layered planting and a
  coherent path network comparable to the source; primitive rocks, loose slabs,
  or a bare platform are not a garden composition.
- Preserve every failed bounded revision. Promote only the newly rendered
  candidate whose complete camera set independently closes every prior P0.

## Optical wall-section correction — exterior-to-interior order

The v18/v23/v16 independent review and the subsequent v19/v24/v17 pixel gate
showed that an opening can contain four named layers and still read as a flat
or outward-projecting prop. The constructor must be audited as a section, in
camera space and in geometry space, before a candidate is sent for review.

- Measure every opening from the exterior inward: physical wall or cut log
  face, visible jamb/head/sill return, inner sash or lattice, pane or paper,
  then a separately offset occupied-room plane and short room sidewalls. Never
  place the deepest decorative frame closest to the exterior camera.
- A deep bronze or timber box outside the wall is not a recess. The exterior
  material owns the mouth of the opening; the sash is narrower and farther
  inside. Use a slightly oblique `glass_close` so at least one wall return and
  the pane-to-room separation are visible simultaneously.
- The structural carrier terminates behind the room datum. For a masonry
  facade, compose a perforated skin from inter-bay piers and inter-floor
  spandrels over an inset core. For a log wall, split every round-log course at
  the jamb clearance and pull the inner carrier behind the pane. For a paper
  screen, pull the side-hall carrier behind the translucent screen and room
  layer instead of revealing solid brick through alpha.
- Transparency is judged in the final renderer, not by shader inputs. Tune
  low-iron glass and paper only far enough to reveal restrained occupied depth;
  preserve material identity, reflections, paper diffusion, and dark room
  contrast. A uniformly dark, grey, cream, or glowing rectangle fails even if
  transmission and alpha are non-zero.
- A warm occupied plane must be visibly distinct from the pane or paper but
  subordinate to the building. Give it real offset and short interior returns;
  do not fake occupation by tinting the glazing itself or increasing emission
  until the window becomes a lamp.
- Run the local pixel gate before independent review. If the wall face, screen,
  and occupied layer cannot be pointed to separately in the rendered close-up,
  preserve that bounded revision as rejected and correct the constructor first.
- When replacing a generic or depth-colored carrier, prove the change in both
  rear-side and aerial views. The replacement must use the family's locked
  material grammar and structural framing, not merely a less conspicuous flat
  color.

## New-family proof learning — mapping axes, deterministic facades, and crop gates

The Victorian station, Rationalist hospital, and Second Empire fire station
showed that a valid source hash and a zero-fallback audit can still produce a
visually generic or physically contradictory building. The following rules are
now part of RLASM v5:

- Resolve exact current catalogue IDs and lock front, 60-degree, and top views
  before naming the candidate. Do not build from an untraceable legacy label.
- Open every registered derivative as an image before the dry build. Reject
  crops containing unrelated facade perspective, shadows, or adjacent roles.
- Treat front/rear and side masonry as separate semantic material roles. A
  coursed shader registered in X-Z cannot be reused on a Y-Z carrier. Record
  the mapping axis and measured course size.
- When repeated booleans produce hidden windows, ghost outlines, or invalid
  modifier order, stop extending the carrier. Compose the facade from physical
  piers and spandrels around the audited bay schedule, with the core terminating
  behind the room layer.
- Re-audit all camera targets after geometry changes. Blank `glass_close`
  output and cropped crowns are failed evidence even when every mandatory
  filename exists.
- Build and inspect the phone board before declaring a builder pass. It must
  pair locked source/model front, oblique, and top roles plus glazing and
  signature-construction closes. Builder pass is still not keeper approval.

## Exact-source material authority and carrier perforation

The material-corrected station v12, hospital v16, and fire-station v12 add the
following rules to RLASM v5:

- Dominant visible materials come from reviewed, shadow-neutral sheets
  conditioned on the exact locked archetype images. Record bytes, SHA-256,
  architectural role, physical tile span, mapping axis, and source authority.
  An invented procedural material is not source-specific merely because its
  metadata says `generic_fallback_count: 0`.
- Separate palette from material morphology. Match bond or joint layout,
  course dimensions, grain direction, mineral variation, oxidation, finish,
  roughness, and bump amplitude before tuning colour under neutral QA light.
- Use a shared world-space mapping datum so fragmented walls and roofs retain
  physical scale and texture phase. Per-object normalization produces visible
  restarts and makes the same material look unrelated across the envelope.
- Keep carved surrounds and cornices inside the source stone family unless the
  reference proves a material change. Dressing and relief may change; generic
  white trim may not replace source masonry.
- Perforate every opaque layer in the wall section. Hospital ghost windows
  came from a cut cladding skin over an uncut overlap carrier; fire-station
  dormer panels came from a cut ashlar skin over an uncut dormer box. A valid
  opening requires one aligned cut through every opaque owner, followed by the
  return, sash, pane, and occupied layer.
- If coincident carriers make a secondary bay unprovable, remove that bay and
  regularize the remaining schedule. Do not keep an embossed outline for the
  sake of window count.
- Judge the corrected material on the complete neutral render set and the
  matched phone board. Preserve all earlier candidates, and keep keeper status
  false until a separate reviewer records zero P0 blockers.

## Orthographic identity rectification for oblique source emblems

Fire-station v12 proved that a tightly bounded source crop can still be an
invalid sticker. Its crest crop was hash-valid and role-specific, but the
source camera angle remained baked into the stone joints, arch, relief, and
outer rectangle. Fire-station v14 establishes the correction:

- Treat the exact locked archetype image as identity authority, not as pixels
  that must be projected unchanged when the source view is oblique.
- Create one isolated, shadow-neutral, front-elevation derivative of the exact
  named emblem. Preserve the source-specific heraldry, relief hierarchy,
  stone family, and aging; reject generic replacement badges.
- Exclude the surrounding building, adjacent material roles, readable invented
  copy, cast shadows, lens distortion, and all perspective facade fragments.
- Preserve the raw generated asset and exact prompt. Record input paths and
  hashes, output bytes and SHA-256, any deterministic export-padding crop, the
  registered derivative hash, and its physical carrier/UV dimensions.
- Remove only outside export padding, then map the derivative at its native
  aspect ratio. Do not stretch it to fill a differently proportioned carrier.
- Mount the sticker inside a real bounded plaque or relief datum. The physical
  carrier owns projection, edge profile, support brackets, and facade contact.
- Add a straight-on `facade_close` or `identity_close` that contains all four
  sticker edges and enough carrier to prove centering, level registration,
  aspect, and absence of perspective or white export borders.

This identity-rectification path is distinct from the material-sheet path.
Identity derivatives may contain the exact named ornament; repeatable material
sheets must remain ornament-free, seam-safe, and governed by physical scale.

## Architectural-type reconstruction before surface matching

The Victorian station v12 failed even though it contained brick, arches, a
clock and a barrel-shaped iron cage. Those parts described the label but not
the locked archetype. Station v16 adds these mandatory rules:

- Measure the source's architectural hierarchy from the front, 60-degree and
  top views before building details. Record shed width, shed depth, arch rise,
  headhouse height, tower offset and frontage depth as ratios, not impressions.
- Identify the weathering envelope. A grand train shed is a long, continuous,
  enclosed glass vault with bounded glazed ends; sparse ribs around an open
  platform are not an equivalent architectural type.
- Build the primary load path in source order: transverse iron trusses, roof
  glazing and purlins, monumental end frame, side columns/arches, then the low
  masonry headhouse. The headhouse must not become a generic repeated strip
  that competes with the shed.
- Match the source asymmetry deliberately: one offset clock tower, differentiated
  gabled pavilions, a low arcade and the specific tower-to-shed overlap.
- Treat source-conditioned material membership as an executable gate. Every
  new revision must be present in the exact-material allowlist; a new candidate
  must fail closed if it falls back to a procedural family shader, even when
  that shader carries non-generic metadata.
- Inspect material scale in pixels. Victorian brick and slate must retain the
  fine course rhythm visible in the source; colour agreement cannot excuse
  building-sized bricks or exaggerated mortar and bump.
- When a clock exists only in an oblique source, create a source-conditioned
  orthographic clock derivative, preserve its prompt and hashes, and mount it
  only to physical front/side clock datums. Geometry owns tower, border, return,
  support and spire.
- Do not declare the revision a keeper from builder evidence. Review the whole
  neutral camera set and phone comparison, then require independent zero-P0
  approval.

## Inhabited-envelope proof for transparent halls

Station v16 corrected the outer architectural type but still failed as a
station because the transparent shed exposed an almost empty floor. Station
v18 establishes a general rule for glass halls, markets, stations, atria and
other visually permeable envelopes:

- A correct shell does not prove the building program. Anything visible
  through a transparent envelope is part of the primary architectural review.
- Build program-defining systems physically: track beds, sleepers and paired
  rails; raised platforms and bounded edges; repeated canopy columns and
  weathering roofs; benches or other source-backed furniture; and safe
  circulation between levels.
- Connect the transparent hall to the opaque headhouse. The interior-facing
  headhouse elevation needs a real concourse arcade/opening schedule, not a
  blank carrier seen through the vault.
- A bridge or gallery requires supports, guard rails and connected stair
  flights. A floating decorative beam is not circulation.
- Add dedicated interior cameras along a platform and track axis. Whole-model
  aerials cannot prove platform contact, rail/sleeper assembly, canopy support,
  concourse openings or circulation.
- Preserve the empty-shell revision as rejected evidence and advance a new
  bounded candidate. Do not edit review metadata into a pass.
