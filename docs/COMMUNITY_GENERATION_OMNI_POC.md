# City Prompt Community Generation + Omni Walkthrough POC

## North star

The proof of concept should show one continuous user journey:

1. A user draws or selects a site boundary.
2. Master Plan AI creates editable buildings, streets, paths, parks and plazas.
3. City Prompt assigns compatible LEGO families and variants using parcel size,
   frontage, adjacency and district-style metadata.
4. The complete community is generated in the Google Tiles scene.
5. The user can still select, replace, resize or delete every generated element.
6. The user draws a walkthrough route.
7. City Prompt turns that route into a contextual video while preserving the
   generated community's architecture and site geometry.

The product proof is not merely that City Prompt can place many good individual
models. It is that the buildings and public realm read as one believable place,
remain editable, and survive the transition from master plan to map to video.

## POC scope: one coherent district first

Do not wait for the entire archetype catalogue before proving the experience.
Create a deliberately compatible starter district of 8-12 LEGO families:

- 3-4 mixed-use or residential streetwall families
- 2 office / employment families
- 1 civic or monumental anchor
- 1 hotel or institutional family
- 1-2 small infill / corner families
- 1 park family and 1 plaza family
- a complete-road family: roadway, curb, sidewalk, boulevard and crossings
- a coordinated tree, bench, light, bollard and planting kit

Every family can still have variants. The POC should use a constrained district
palette so variety comes from building type, footprint and façade composition—not
from unrelated rendering styles.

## 1. District visual contract

All generated assets should conform to one versioned `district_visual_profile`.
This is the missing layer between an archetype catalogue and a coherent community.

The profile should define:

- real-world unit scale and floor-to-floor ranges
- façade texel density and near/mid/far texture tiers
- shared PBR calibration for albedo, normal, roughness, AO and emissive
- maximum directional light baked into albedo
- bevel radius ranges by material and viewing distance
- glazing profiles, recess depth, mullion scale and occupied-interior behavior
- shared environmental lighting, exposure, tone mapping and shadow softness
- material families rather than identical materials: related stone, brick, metal,
  wood, glazing, paving and roof ranges
- public-realm scale rules for curbs, sidewalk joints, benches, trees and lights
- LOD transition distances and KTX2 compression targets
- Google Tiles blending rules: contact shadows, terrain offset and color response

The LEGO compiler should emit the profile ID and a conformance report in each
family manifest. Master Plan AI should only combine families whose profiles are
compatible, unless the user explicitly requests a contrast.

## 2. Archetype compatibility metadata

Every archetype variant needs machine-readable placement metadata in addition to
its geometry and materials:

```json
{
  "district_visual_profile": "cityprompt-realism-v1",
  "compatible_district_styles": ["contemporary-urban", "warehouse-mixed-use"],
  "footprint": {
    "preferred_width_m": [28, 55],
    "preferred_depth_m": [24, 42],
    "supported_shapes": ["rectangle", "corner", "l-shape"],
    "min_bay_width_m": 3.2
  },
  "height": {
    "preferred_floors": [8, 18],
    "supported_floors": [5, 24]
  },
  "edges": {
    "frontage_required": true,
    "frontage_types": ["primary-street", "plaza"],
    "rear_types": ["lane", "railway", "service"],
    "party_wall_left": true,
    "party_wall_right": true
  },
  "public_realm": {
    "setback_m": [0, 4],
    "preferred_sidewalk_family": "urban-stone-v1",
    "preferred_tree_palette": "northern-deciduous-v1"
  }
}
```

Fixed corner, entrance, crown and roof assemblies must be retained. Only middle
bays should stretch or repeat. Side and rear elevations should respond to whether
an edge is exposed, a party wall, a lane, a railway or another public frontage.

## 3. Community generation contract

The canonical generation payload should carry one scene graph through every stage:

```text
validated master plan
  -> parcels + street graph + public spaces
  -> family/variant assignment
  -> LEGO recipes + public-realm recipes
  -> atomic 3D scene build
  -> editable City Prompt objects
  -> render captures + route keyframes
  -> contextual walkthrough video
```

Required behavior:

- generation is atomic: either the full validated scene is committed, or no
  partial community is left on the map
- every object keeps its source parcel/segment ID, family ID, recipe and profile ID
- all generated objects can be selected, deleted, rebuilt and rendered
- façades orient to classified street edges; service/rear elevations orient to
  lanes, railways or hidden boundaries
- abutting edges use party-wall logic; exposed edges receive complete façades
- road and park meshes drape to terrain without z-fighting or floating edges
- shared assets are instanced, not duplicated per parcel

## 4. Public realm as an equal system

Buildings alone will not make the community convincing. Roads, sidewalks, parks
and landscape should use the same quality gates as the building families.

### The hybrid rule

The current drape remains useful, but it becomes the terrain-following **substrate**
rather than the finished public realm. A fully extruded road slab or park plane
cannot follow Google terrain reliably, while a photograph alone has no sectional
depth. The public-realm LEGO system therefore has two coordinated layers:

1. a thin, terrain-conforming PBR surface for asphalt, paving, turf, water,
   markings and planting beds; and
2. metric 3D assemblies for every element whose profile or shadow matters:
   curbs, gutters, sidewalk slabs, curb ramps, retaining edges, path borders,
   bridges, railings, trees, lights, benches, bollards and drainage hardware.

The drape supplies continuity over geographic terrain. The LEGO assemblies supply
depth, silhouette, contact shadow and close-range realism. Both are compiled from
the same deterministic recipe, share one seed, and remain one selectable object in
City Prompt.

### One compiler, three domain grammars

The LEGO Builder should become a domain-neutral scene compiler with three recipe
types: `building`, `street` and `park`. They share versioning, provenance,
materials, LODs, validation and City Prompt editing behavior, but each keeps the
geometry grammar appropriate to its topology:

- building recipes compile polygon edges into fixed corners, entrances, crowns,
  roofs and repeatable middle bays;
- street recipes compile centerline graphs into repeatable tangent segments plus
  fixed intersection, corner, crossing, ramp, terminal and retaining-wall nodes;
- park recipes compile polygons and internal path graphs into terrain surfaces,
  fixed gateways and program objects, repeatable path/edge modules, and seeded
  planting or furnishing zones.

This is one LEGO system, not one universal mesh algorithm. The shared contract is
what makes the result coherent and editable; the domain grammar preserves correct
building, network and landscape behavior.

### Street-family composition

Every street family should own a complete metric cross-section rather than a flat
road ribbon. Its recipe contains:

- terrain-sampled asphalt or unit-paving bands with crossfall and drainage intent;
- real curb-and-gutter profiles with radiused returns at corners;
- sidewalk slabs, joints, furnishing strips and tactile curb ramps;
- protected-cycle separators, medians, parking bands and transit platforms where
  required by the selected archetype;
- fixed nodes for T-junctions, cross-junctions, crossings, cul-de-sacs, bridges
  and grade transitions;
- lane markings and crosswalks as shallow terrain-following overlays, not floating
  decals; and
- instanced street trees, lights, benches, bollards, racks and bins selected from
  the district visual profile.

Only the tangent middle segment repeats. Intersections, curb returns, crossings and
terminations remain fixed authored assemblies in the same way that building
corners, entrances and crowns remain fixed.

### Park-family composition

Every park or plaza family should own an exact program graph and a coordinated kit:

- terrain-conforming lawn, paving, water and planting substrates;
- paths with physical edge depth, joints, curb/flush-edge rules and accessible
  grade transitions;
- fixed entrances, gates, bridges, pavilions, play/sport elements and water edges;
- repeatable retaining, seat-wall, boardwalk, fence and planting-bed modules;
- species-aware tree and understory palettes with age, crown and seasonal variants;
- coordinated benches, lights, bins, bollards and wayfinding; and
- clear collision, setback, maintenance and sightline zones.

Program truth still wins: courts, fields, ponds, bridges and paths retain their
compiled size and topology. Render imagery supplies material and planting character
without moving those elements.

### Shared family manifest

All three domains should emit the same lifecycle fields:

```json
{
  "domain": "street",
  "family_id": "main-street-complete-v1",
  "variant_id": "heritage-commercial",
  "district_visual_profile": "cityprompt-realism-v1",
  "source_geometry_ids": ["street-segment-42"],
  "surface_kit": "urban-asphalt-warm-v1",
  "edge_kit": "granite-curb-gutter-v1",
  "node_kits": ["four-way-crossing-v1", "accessible-ramp-v1"],
  "prop_palette": "heritage-main-street-v1",
  "terrain_mode": "drape-and-freeze",
  "lods": ["hero", "district", "map"],
  "seed": 18427
}
```

City Prompt then treats a compiled road, park or building identically for selection,
deletion, rebuilding, rendering and provenance. Master Plan AI assigns all three in
one atomic scene build, so frontage, sidewalks, park gates and crossings meet by
construction rather than by visual coincidence.

The first public-realm kit should include:

- roadway wearing course with normal/roughness response and subtle variation
- curb and gutter with real depth and corner-radius logic
- sidewalk slabs, joints, ramps and tactile crossings
- boulevard/planting strips that follow parcel and road geometry
- crosswalks and lane markings as terrain-following overlays
- tree families with seasonal variants and near/mid/far LODs
- coordinated benches, lights, bollards, bike racks and waste bins
- park paths, lawn, understory, plaza paving and optional water elements

Road and park family metadata should expose the same district compatibility and
LOD fields as building families.

### Public-realm pilot sequence

1. Promote the existing deterministic street sections and park programs into the
   shared family manifest without discarding their tested fitting logic.
2. Build one complete main-street family: surface, curb/gutter, sidewalks, crossings,
   ramps, trees, lights and furniture, including a T and four-way intersection.
3. Build one neighborhood-park family: lawn/planting substrate, edged paths, two
   entrances, trees, benches, lights and one fixed pavilion/play program.
4. Give both hero/district/map LODs and the same PBR calibration used by the best
   render-locked building families.
5. Place the street, park and 3-5 compatible buildings together in Google Tiles;
   compare close, oblique and route-level captures to a locked district render.
6. Add them to the Community 3D Builder only after selection, deletion, regeneration,
   terrain fit, connection and frame-rate gates pass.

## 5. Route-to-video architecture

Treat the route as deterministic camera data before asking a generative model to
add realism.

### Route authoring

The user draws a line and selects:

- walk, cycle, drive or aerial mode
- camera height, speed and field of view
- forward-looking, landmark-looking or route-tangent orientation
- time of day and video style

The route service should smooth the line, sample terrain/building clearance, and
emit stable keyframes with position, heading, pitch, look-at target and timestamp.

### Deterministic scene pass

City Prompt should first capture the actual generated community along the route:

- render start/end frames for each 4-8 second segment
- optionally capture a low-resolution guide clip or intermediate keyframes
- preload visible LODs to prevent texture popping
- preserve route IDs, scene version and camera metadata for reproducibility

### Generative video pass

Use a provider adapter rather than hard-coding a preview model:

```text
WalkthroughVideoProvider
  - GeminiOmniProvider
  - VertexVeoProvider
```

As of July 2026, Gemini Omni Flash is officially available in public preview for
3-10 second image/video generation and conversational editing. Veo 3.1 on Vertex AI
is the stable fallback for first/last-frame interpolation. The initial POC should:

1. send the deterministic first frame, last frame and camera-motion prompt
2. prohibit massing, façade, road and parcel changes in the prompt
3. generate short segments rather than one long unconstrained clip
4. run a geometry-consistency check against captured frames
5. retry or fall back to the deterministic viewer recording when drift is high
6. concatenate approved segments and add labels/disclosure metadata

Official implementation references:

- https://ai.google.dev/gemini-api/docs/omni
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-first-and-last-frames

## 6. Proof-of-concept storyboard

Target a 60-90 second demonstration:

1. **Site** — open the empty Google Tiles site.
2. **Intent** — draw the boundary and choose a district character.
3. **Plan** — Master Plan AI creates roads, parcels, parks and building zones.
4. **Edit** — move one street, replace one archetype variant and change one height.
5. **Generate** — build the complete community in 3D with a visible progress state.
6. **Inspect** — orbit from aerial to street level; show coherent façades, glazing,
   roads, sidewalks and landscape.
7. **Render** — create one architectural still from the generated 3D scene.
8. **Route** — draw a line through the community and select walking pace.
9. **Video** — generate and play the contextual walkthrough.
10. **Proof** — end on a split screen: editable master plan, live Google Tiles scene,
    and generated walkthrough.

## 7. Acceptance gates

### Family gate

- silhouette and signature assemblies match the archetype references
- exposed front, side and rear elevations are complete
- windows, entrances, roof and ground floor have physical depth
- near-view textures and materials survive a close City Prompt inspection
- supported parcel sizes and shapes pass without broken bays or stretched corners

### District gate

- all selected families share one district visual profile
- no floating, buried or z-fighting buildings/roads/parks
- frontage and rear/service orientation is correct for at least 95% of parcels
- one-click generation leaves no orphaned or duplicate objects
- the entire scene remains selectable, deletable, renderable and rebuildable
- target hardware holds the agreed interactive frame rate at mid-distance LOD

### Video gate

- route stays inside traversable public space
- architecture, street geometry and key landmarks do not materially change
- no obvious camera jumps at segment joins
- the final clip clearly discloses that it is an illustrative AI visualization

## 8. Live family evidence and POC scope

The local City Prompt pilot has now proven the complete single-building path
with a render-locked Modern Glass Office and a Perpendicular Revival collegiate
landmark: compiler output, validated modules, catalogue import, planner match,
placement on the geographic polygon, content-hashed rebuild and close Google
Tiles inspection all work. The Gothic pass also proved arbitrary-angle facade
assemblies for an octagonal lantern and exposed the two district-level gaps
that must be solved before filming:

1. **Orientation contract:** every building zone needs explicit `frontageEdge`,
   `serviceEdge` and party-wall flags. Rotation must come from the public street,
   not polygon winding. The live chapel initially faced the railway and passed
   only after a 180-degree frontage correction.
2. **Distance contract:** the current hero landmarks are deliberately heavy.
   A community needs a route-aware hero tier, an instanced district tier and a
   compact map tier, with KTX2 textures and deterministic preload before video
   capture.

The POC should therefore use one deliberately coherent starter cohort rather
than a random catalogue sample:

- 2-3 residential families sharing one masonry/wood palette
- 1 mixed-use or office anchor
- 1 civic/education landmark
- 1 small commercial/community building
- one road/sidewalk kit, one park kit and one tree palette

That is enough to demonstrate AI planning, one-click 3D generation, editing,
rendering and a route walkthrough without hiding quality problems inside an
oversized first district. Record the exact family versions, planner seed,
scene version, route and render/video provider with the final proof-of-concept.

## 9. Recommended implementation sequence

1. Freeze `cityprompt-realism-v1` from the best current LEGO families.
2. Complete 8-12 compatible starter families and their footprint variants.
3. Give roads, sidewalks, parks and landscape the same profile and LOD system.
4. Finish frontage/rear/party-wall classification in Master Plan payloads.
5. Add atomic community build, object provenance and whole-community rendering.
6. Produce and QA one reference district in Google Tiles from aerial and street views.
7. Build route authoring and deterministic keyframe capture.
8. Restore the existing video service behind the Omni/Veo provider adapter.
9. Generate the 60-90 second POC and record the exact scene/version metadata.
10. Expand catalogue coverage in aesthetic cohorts, not random archetype order.

## Core strategic decision

The next milestone should not be “100 individually impressive buildings.” It should
be “one complete, coherent, editable neighborhood that survives every transition.”
Once that contract is proven, the catalogue can scale in batches without losing the
architectural and public-realm consistency that makes the result believable.
