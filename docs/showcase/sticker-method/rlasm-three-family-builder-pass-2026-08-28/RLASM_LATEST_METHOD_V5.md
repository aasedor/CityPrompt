# RLASM latest production method — v5

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
- When no clean atomic crop exists, use a source-calibrated procedural material
  and record the crop only as palette/provenance evidence. Mark photographic
  projection forbidden; do not tile a perspective photograph across geometry.
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
constructor changes. They remain `NOT_A_KEEPER` until independent approval.

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
