# Park Composition API Study — 2026-08-05

## Purpose

This bounded study uses flat API-generated park images only as composition
evidence for the deterministic City Prompt park LEGO builder. The generated
pixels are not product assets, regulation references, or a replacement for
archetype images.

- 10 site briefs
- 2 providers per brief
- 20 successful API calls total
- Gemini `gemini-3.1-flash-image` at 1K, 3:2
- OpenAI `gpt-image-2` at 1536×1024, low-quality study mode
- No retries
- No people requested
- Large buildings replaced by reserved pads and forecourts

The prompt schedule is machine-readable in
`tools/park_skin_compiler/park_composition_api_study.json`. The generated run
ledger, images, and comparison sheets remain under ignored `artifacts/` output.

## Human reference policy

People visible in the source archetype images are evidence even though people
must not be instantiated in the park LEGO output. During archetype analysis,
use them to interpret:

- approximate feature and furniture scale;
- eye level, reach, sitting height, and child-versus-adult use;
- walking, queuing, play, coaching, and spectator zones;
- the capacity and social intensity of gathering areas;
- entrances, desire lines, pause points, and circulation conflicts;
- clearances between active play, spectators, paths, fences, and planting;
- which edges require shade, seating, visibility, or supervision.

Translate those observations into dimensions, occupancy envelopes, access
paths, edge roles, and furniture placement. Do not reproduce the people as 3D
assets, bake them into skins, or preserve their exact positions. Human figures
are approximate scale and use clues, never substitutes for regulation data or
accessibility standards.

## Strong cross-provider agreements

Both providers repeatedly converged on the following spatial relationships.
These are suitable candidate rules for the LEGO compiler, subject to regulation
data and archetype-photo review.

1. **Shared court compounds.** Repeated courts work best as banks with common
   perimeter fencing, internal dividers, consolidated lights, and one social or
   player spine. They should not be repeated as fully independent fenced kits.
2. **Paired-field corridors.** Two rectangular fields naturally share a central
   technical/spectator corridor and a midpoint arrival. Outer land remains a
   buffer rather than becoming a third stretched field.
3. **Landscape absorbs irregular residual land.** A regulation rectangle can be
   rotated into the widest part of a wedge while meadow, bioswale, windbreak,
   and trail occupy the narrowing land.
4. **One dominant oval.** Running tracks and cricket grounds organize the whole
   site. Field events, practice areas, spectator edges, and building interfaces
   stay outside the continuous oval safety envelope.
5. **Pinwheel diamonds.** Four youth diamonds consistently formed a radial
   pinwheel with home plates at a shared central hub and outfields directed
   outward. This is much stronger than rectangular bin packing.
6. **Mixed complexes use sport blocks and crossing spines.** Soccer fields and
   diamonds read as separate compatible blocks connected by public and service
   axes, not as a collection of individually placed objects.
7. **Social infrastructure belongs on an edge or spine.** Seating, shade,
   gates, drinking fountains, and reserved building forecourts consistently
   organize access without intruding into play and run-off zones.

## Provider differences and errors to reject

- The first Gemini tennis image used the correct count of four courts but
  interpreted the requested 2×2 topology as a four-across bank. GPT Image
  followed the 2×2 topology. Exact adjacency must therefore be compiler-owned.
- Both providers frequently added highly regular perimeter tree rows and loop
  paths. These are useful only when supported by the selected archetype; they
  must not become generic park decoration.
- Site boundaries and proportions drifted from the stated dimensions. Generated
  pixels must never be measured to recover regulation geometry.
- Some outputs introduced surrounding roads or context despite exclusions.
  Context treatment is not reliable composition evidence.
- Apparent clearances, fence offsets, lighting positions, and field dimensions
  are illustrative. Authoritative standards and explicit compiler dimensions
  remain the source of truth.

## Scene-level guidance

| Scene | Retain for LEGO grammar | Reject or verify |
|---|---|---|
| Professional tennis | Shared enclosure, internal dividers, central social spine, consolidated lights | Gemini topology drift; all metric spacing must be explicit |
| Naturalized tennis pods | Three separate pods, branching/looping accessible path, shared gathering node, meadow between pods | Do not use meadow when the selected variant is a dense professional bank |
| Community pickleball | Two banks of four around a shaded social promenade | Verify exact run-off and gate placement; avoid decorative trees inside clear zones |
| Caged soccer pair | Two equal pitches, common cage, divider, continuous spectator edge | Do not infer cage height or pitch dimensions from the image |
| Parallel soccer fields | Common orientation, central technical corridor, midpoint arrival, reserved clubhouse edge | Do not add a third field merely because a broad buffer remains |
| Irregular single soccer | Rotate one exact field into the widest area; use the wedge for drainage and habitat | Parcel shape in the image is illustrative, not a polygon solution |
| Track oval | Oval as primary anchor, compatible infield, events outside one straightaway, one spectator/building edge | Track lane count and event geometry require standards data |
| Baseball pinwheel | Four radial diamonds, central shared hub, outward outfields, axial warm-up areas | Safety overlap and foul territory require deterministic collision checks |
| Cricket village green | Open oval dominance, central wicket axis, pavilion edge, practice nets outside oval | Gemini showed multiple central strips; exact wicket program must come from the selected variant |
| Mixed tournament complex | Two sport blocks, crossing public/service spines, support at their intersection | Do not copy ornamental symmetry when terrain or access contradicts it |

## Compiler implications

The next park-layout layer should generate and score a small finite set of
topological candidates. It should not ask an image model where to put assets.

Each selected variant needs:

- `programSignature`: exact module types and allowed counts;
- `topology`: `grid`, `parallel_bank`, `podded`, `parallel_pair`, `pinwheel`,
  `oval_anchor`, or `mixed_blocks`;
- `orientationPolicy`: shared axis, radial, parcel-dominant edge, or fixed;
- `compoundRules`: shared fencing, dividers, gates, lighting, and spectator
  spine;
- `edgeRoles`: public arrival, building interface, service, spectator, quiet,
  and natural buffer;
- `landscapeReserve`: minimum intentional non-program area and its archetype
  structure;
- `hardConstraints`: exact dimensions, run-off, collision, access, and parcel
  containment;
- `scoringWeights`: archetype match, circulation quality, usable residual land,
  edge compatibility, crowding penalty, and orphan-space penalty.

The central lesson is that API imagery is valuable for discovering plausible
relationships, but the LEGO builder must own count, scale, topology, collision,
and site adaptation. Source-image people inform human scale and use before that
geometry is authored, but remain absent from the final park model.
