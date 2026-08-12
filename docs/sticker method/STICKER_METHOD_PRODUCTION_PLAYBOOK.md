# Sticker Method production playbook

This is the canonical workflow for producing high-fidelity, LEGO-compatible
3D buildings from archetype images. Every stage is mandatory. A building is
publishable only when its unrounded architect-review mean is **strictly above
95/100**, every rendered tier scores at least 95/100, every machine gate passes,
and no hard-stop defect is present.

The method combines three coordinated representations:

1. **Locked geometry** owns footprint, massing, silhouette, roof shape,
   projections, openings, recesses and shadow-bearing construction.
2. **Geometry-conditioned stickers** own image-specific surface identity,
   material colour, fine ornament and irregular façade detail.
3. **PBR and optical layers** own roughness, normal response, transmission,
   reflections, glazing depth and lighting response.

The governing principle is:

> Make every sticker for its exact final 3D carrier, then approve the projected
> building—not the attractive flat image.

## 1. Lock the evidence and identity contract

Collect at least three compatible views: street identity, oblique massing and
roof/aerial. Add side, rear and detail views whenever available. Catalogue
metadata is supporting evidence only; use fields that agree with the images
and reject contradictory dimensions, floor counts, roof forms or style labels.

Before modelling, record:

- visible floor and bay counts;
- broad and narrow bay hierarchy;
- footprint steps, chamfers, courtyards and linked wings;
- fixed entrances, towers, turrets, dormers, chimneys and roof terminations;
- ground, repeatable middle, fixed crown and roof boundaries;
- material and glass roles;
- uncertain or hidden regions requiring architectural inference.

The exact archetype images outrank generic style knowledge and conflicting
metadata.

## 2. Choose the representation before generating images

Use a fixed select-and-place landmark when identity depends on a unique plan,
roof or ornament composition. Use discrete Sticker LEGO tiers only when the
building contains a genuine repeatable structural grid.

Never authorize arbitrary non-uniform building scaling. A polygon-placement
workflow must snap to complete approved modules. If the requested footprint
cannot be assembled from whole modules while preserving the fixed identity
kit, choose the nearest approved tier or require a new reviewed variant.

## 3. Decompose the building into LEGO modules

Every scalable family has two namespaces:

- **Fixed identity:** entrance/stair wings, end/service bays, corners, crown,
  roof hips, dormers, chimneys, annexes and other singular features.
- **Repeatable capacity:** ordinary structural bays, complete middle floors and
  compatible roof strips.

Declare the bay width and floor height in metres. Add or remove only whole
modules. Fixed assemblies remain singular and keep the same physical size.
Ground and crown bands may not be repeated as middle floors.

The validated V97.3 mill example uses 5 m façade bays and 5 m floor bands in
three bounded tiers:

| Tier | Footprint | Floors | Sticker carriers |
|---|---:|---:|---:|
| Small | 35 × 30 m | 4 | 149 |
| Canonical | 50 × 40 m | 5 | 232 |
| Large | 65 × 50 m | 6 | 335 |

## 4. Build and approve the clay geometry

The geometry agent builds the complete architectural section before final
stickers are generated:

- correct footprint, height, setbacks and linked volumes;
- roof slopes, hips, ridges, valleys, dormers and accessories;
- actual entrance apertures, tunnels, jambs, soffits and recessed backs;
- projections and returns that create silhouette, parallax or shadow;
- continuous exterior walls or precisely registered modular carrier faces;
- subordinate roofs with their own construction domain.

Review neutral clay renders against street, oblique and roof references.
Wrong massing cannot be repaired with image detail. Once approved, hash and
freeze the carrier geometry. A later topology, proportion or module change
invalidates every affected sticker.

## 5. Create the complete surface-ownership schedule

Every visible polygon receives exactly one semantic owner. Required roles
include:

- ground, middle, crown and main roof;
- subordinate roofs;
- straight, side, rear, chamfered and curved walls;
- entrance foreground, jambs, tunnel, soffit, threshold and recessed door;
- roof slopes, hips, fascia, underside and caps;
- dormer fronts, cheeks, caps and returns;
- chimney faces and caps;
- balcony, canopy and cornice tops, fronts, undersides and end caps.

Blue-grey clay, generic fallback materials, uncovered undersides and duplicate
owners are release failures even when the hero façade looks correct.

## 6. Bake the carrier-space sticker package

From the locked carrier, export the exact generation guides required by each
surface:

- UV charts and padded island masks;
- object/world position, normal, curvature and depth;
- visibility from approved cameras;
- floor, elevation, construction and material IDs;
- opening, frame, glass, column, void and ornament masks;
- window centres, column axes, floor datums and paired seam anchors;
- UV stretch and texel-density diagnostics.

Use mapping appropriate to the shape: rectified elevation for straight walls,
conformal/cylindrical charts for turrets, shared charts at corners, per-slope
roof charts, radial gores for domes, and separate front/return/cap charts for
dormers, entrances and chimneys.

## 7. Generate intrinsic stickers after geometry lock

The sticker agent creates de-lit surface material—not a perspective screenshot.
Remove source sunlight, cast shadows, sky reflections, lens distortion and
painted false depth. Generate directly in the final carrier chart whenever
possible. Post-generation non-uniform resizing, aspect correction and arbitrary
cropping are forbidden.

Use paid/API calls selectively:

1. generate only after the carrier and masks are locked;
2. generate the smallest responsible region, floor or surface role;
3. retain the successful master and regenerate only failed regions;
4. record prompts, sources, provider, call count and asset hashes;
5. never spend more calls trying to compensate for incorrect geometry.

Metadata may guide materials or dimensions only when it improves agreement
with the references.

## 8. Bind stickers floor by floor and surface by surface

Bind a fixed ground sticker, one or more complete repeatable middle stickers,
a fixed top/crown sticker and a disjoint roof system. Maintain constant metric
texel density and window aspect across every size tier.

Corners share boundary texels or use an explicit construction-joint sticker.
Roof imagery stays on roof-facing surfaces; fascias and returns have their own
directional owners. Physical glass may be added only inside a registered
sticker-derived glass mask and must sit behind the frame plane.

## 9. Run machine gates before beauty rendering

The build stops unless all of the following pass:

- 100% visible-polygon ownership;
- zero generic/default/clay faces;
- exactly one owner per locked face;
- zero floor-band gaps or overlaps;
- zero main-roof owners below the main roof datum;
- zero occupied-wall faces owned by the roof;
- zero partial bays, stretched carriers or duplicated fixed modules;
- constant window aspect and texel density across tiers;
- valid sticker-to-carrier hashes and source provenance;
- production preflight and exported GLB surface audit.

Machine success proves completeness and registration. It does not prove
architectural fidelity.

## 10. Render the mandatory review set

Render at least:

1. archetype-match;
2. street;
3. front corner;
4. rear corner;
5. façade close-up;
6. roof audit;
7. aerial/context.

For LEGO families, render every approved size tier. Use identical review roles
so window proportions, brick scale, fixed-module count and roof behavior can be
compared directly.

## 11. Correct errors in their owning layer

Compare silhouette, floor/bay anchors, openings, seams, material zones and roof
composition against the exact references. Back-project each defect to its
owner:

- silhouette, void or projection error → geometry agent;
- surface alignment, colour or seam error → sticker agent;
- floor sequence or size-tier error → floor-sticker agent;
- optical/plastic glazing error → material/glass layer;
- uncertain architectural interpretation → architect reviewer.

Never paint a geometry error into albedo or add generic geometry over a
sticker-owned feature.

## 12. Require independent architect approval

The architect/design reviewer must be independent from generation and inspect
the exact references beside all required views. Score each size tier using:

- archetype identity: 30 points;
- massing and geometry: 20;
- sticker registration: 20;
- all-surface, roof and entrance coverage: 15;
- LEGO scale consistency/no stretching: 15.

Release requires:

- unrounded mean score **greater than 95.0**;
- every tier score **at least 95**;
- zero hard-stop defects;
- an explicit signed/recorded verdict.

If the score fails, repair the owning layer and rerender the complete affected
review set. Do not average a rejected tier into an otherwise good family.

## 13. Publish a bounded evidence package

Commit only reviewed outputs:

- exact-reference comparison board;
- size-matrix board;
- roof and oblique boards;
- individual audit renders;
- machine-readable geometry/sticker contract;
- sticker provenance and hashes;
- architect approval record;
- generator, tests and reusable quality-memory update.

Track large images with Git LFS. Keep exploratory `.blend`, GLB, logs and
unreviewed renders outside the source tree. Push after the bounded pilot, not
after an open-ended generation loop.

## Agent responsibilities

| Agent | Accountable output | Cannot approve |
|---|---|---|
| Geometry agent | locked clay, voids, roof, fixed/repeat module map, carrier hash | final sticker or architect score |
| Sticker agent | intrinsic surface masters, mapping, seams, provenance | geometry deviations |
| Floor-sticker agent | floor roles, repeat schedule, size matrix, constant scale | arbitrary stretching |
| Architect/design reviewer | independent multi-view score and hard-stop verdict | its own unreviewed generation |

## Non-negotiable hard stops

- architect mean at or below 95, any tier below 95, or any hard-stop defect;
- visible blue-grey/default/clay polygon;
- unstickered wall, roof, return, underside or cap;
- roof sticker on an occupied floor;
- flat masonry where the reference requires a usable void or tunnel;
- duplicated entrance, window, column, balcony, frame or gable;
- partial bay, repeated ground/crown, stretched window or changing texel scale;
- sticker authored before the affected carrier was locked;
- post-approval crop, aspect change, topology edit or non-uniform scaling;
- missing required review view or unrecorded architect verdict.

## Proven references

- Belle Époque Grand Magasin V95: geometry-conditioned fixed landmark, 95/100.
- Functionalist Brick Mill V97.3: discrete Sticker LEGO family, 95.3 mean,
  95/96/95 by tier, zero hard stops.

V97.3 proves the method for bounded snapped sizes. It does not authorize
arbitrary resizing or unattended catalogue rollout. Every archetype still
requires its own fixed/repeat decomposition, carrier lock and independent
visual approval.
