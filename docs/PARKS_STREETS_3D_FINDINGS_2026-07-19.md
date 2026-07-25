# Parks and Streets in Google Tiles: Findings and Recommended Architecture

**Date:** 2026-07-19  
**Scope:** City Prompt parks, plazas, sports grounds, paths and streets in Google Photorealistic 3D Tiles, including the render-to-drape trials on the downtown test parcel.

## Executive finding

The strongest workflow is not to ask one image model to invent the plan, the 3D scene and the final visualization at the same time. City Prompt should maintain one deterministic, metric **program truth**, then use it in two different visual products:

1. an interactive, correctly scaled and ground-seated Google Tiles environment; and
2. a photoreal architectural render that adds atmosphere, planting, people and fine detail without changing the program.

The photoreal render is the appearance goal, but it must not be allowed to redefine the polygon, move a court, add a path, change a water body or landscape outside the site. The deterministic plan always wins for boundary, dimensions, count, topology and connections.

### July 19 architecture decision: promote the drape into Public Realm LEGO

The trials also show that a drape alone remains visibly flat beside the new
render-locked building families. The next system should not discard the drape;
it should make it the terrain-conforming substrate of a shared LEGO family.
Asphalt, paving, lawn, water and markings continue to follow Google terrain, while
curbs, gutters, sidewalk slabs, path edges, walls, bridges, trees, lights, benches
and other shadow-casting elements become metric, reusable 3D assemblies. Street
centerlines and park polygons therefore compile through the same versioned family,
LOD, PBR and City Prompt editing contract as buildings, using network and landscape
grammars rather than the building bay grammar.

This supersedes the assumption that almost all trees and benches must remain only
in the final render. They can move into the interactive scene once a realistic,
district-coherent, instanced and LOD-controlled asset palette passes close-range
Google Tiles QA. Render-only entourage remains a fallback, not the target product.

## Recommended end-to-end pipeline

1. **Master plan:** generate a connected community plan containing building, park/plaza and street/path zones. Keep every zone as georeferenced geometry with an archetype, variant and metric metadata.
2. **Program compilation:** convert each zone into an exact program contract. Courts, fields, bridges, conservatories, ponds, boardwalks, carriageways and sidewalks receive authoritative dimensions and topology.
3. **Whole-element fit:** test complete fixed elements at multiple positions and orientations. Retain the highest-value non-overlapping combination that fits entirely within the actual polygon. Never crop or scale an element to consume leftover space.
4. **Ground generation:** create a north-up orthographic drape from the fitted program. The drape supplies turf, paving, water, planting beds, linework and other ground materials, with no perspective and no blank paper margins.
5. **Interactive 3D:** place the drape and essential fixed objects on the terrain used by Google Tiles. Add only objects needed to understand or use the program, such as sports nets, goals, fencing, bridges or a conservatory.
6. **Render:** capture the current geospatial view and create the architectural hero image. Add realistic canopy, benches, people, cars, lighting and planting detail here, while locking the polygon and compiled program.
7. **QA:** compare the render and Tiles screenshots at the same camera. Accept an archetype/variant only when scale, topology, containment, grounding, context connections and visual character pass.

## What the trials established

### 1. Metric geometry must precede imagery

Image generation is good at material richness and atmosphere but unreliable at exact count and scale. It will readily draw a half court, widen a pitch, move a pond or invent an extra path unless the topology has already been compiled.

Regulation examples now use real dimensions:

- full football/soccer pitch: **100 x 64 m**;
- doubles-tennis safety envelope: **36.58 x 18.29 m**, containing a 23.77 x 10.97 m court;
- pickleball envelope: **18.29 x 9.14 m**;
- basketball program envelope: **32 x 19 m**;
- running-track envelope: **176.91 x 92.52 m**.

These dimensions remain unchanged regardless of parcel size.

### 2. Fit is a packing problem, not a clipping operation

The earlier fitter aligned all programs to one parcel direction and greedily slid each item. It could reject an element even when a valid arrangement existed because it did not reconsider earlier placements or test alternate orientations.

The current fitter:

- evaluates sports surfaces at several angles, including orthogonal rotation;
- rotates grouped elements together around a physical-metre centroid;
- searches nearby positions in physical distance order;
- rejects every candidate that crosses the polygon or overlaps an active program;
- uses a bounded global layout search instead of locking the first valid placement;
- prioritizes primary, larger programs while maximizing the number of complete secondary elements.

On project `0d73b4ea-31ea-48bf-8590-f1862f950504`, the same sloped 144 x 76.8 m parcel improved from one field plus two courts to **one complete 100 x 64 m field plus all three complete tennis envelopes**. A separate narrow-parcel test proves that a court turns 90 degrees when its authored orientation is the only reason it would not fit.

### 3. Rotation calculations must happen in metres

Rotating normalized X/Y coordinates distorts geometry when parcel width and height differ. A visually requested 90-degree rotation is not physically 90 degrees if normalized axes have different scales. All envelope rotation and collision work now occurs in metres, then converts back to normalized coordinates for drawing.

### 4. The drape should contain ground truth, not render entourage

Trees and benches were frequently placed in paths, courts or water when generated before the ground topology had settled. Generic 3D trees also looked cartoonish beside photogrammetry.

The successful division of responsibility is:

- **Drape:** ground materials, field/court markings, paths, plazas, beds, water and exact fixed footprints.
- **Interactive fixed 3D:** nets, goals, fencing, bridges, boardwalk structure, conservatories and similarly essential program objects.
- **Final render:** most trees, benches, people, vehicles, ornamental planting and cinematic lighting.

An urban forest is the important exception: its canopy is the program, not optional entourage. It needs a realistic species/age/crown asset system before the interactive scene can match the render.

### 5. Render imagery is an appearance reference, not a tracing authority

The best render prompts explicitly distinguish immutable geometry from flexible appearance. A useful prompt contract states that the diagram wins for boundary, scale, count and topology; the render contributes only materials, planting character, lighting and atmosphere.

The final render must also be masked to the site. A visually attractive nature-play render failed QA because landscaping extended outside the polygon.

### 6. Context integration is a graph problem

Parks and streets should not terminate at the site boundary without purpose. Master-planner output should identify external connection candidates from the existing road/path network, then require:

- street centerlines to meet compatible existing streets;
- sidewalks and multi-use paths to reach existing pedestrian edges;
- park gates to align with those arrival points;
- no new connection across a building, water body, barrier or unsafe road edge;
- road hierarchy and cross-section to remain consistent through the connection.

The ground drape should consume these locked access points rather than ask the image model to guess where entrances belong.

## Trial results on the common parcel

| Archetype | Finding |
| --- | --- |
| Sports complex | Strongest deterministic result. The orientation search fits one full field and three complete courts at authoritative scale. |
| Stormwater pond | Strong render/Tiles agreement when the basin, wet shelf, inlet, outlet pad and dry maintenance access are explicit guides. |
| Neighborhood park | Accepted after exact lawn and connected-circulation guides removed disconnected paths and invented central paving. |
| Formal reflecting pond | Accepted after replacing the generic ellipse/fountain fallback with one rounded basin and a continuous promenade. |
| Botanical garden | Ground topology and scale pass; render canopy and collection richness remain intentionally richer. |
| Japanese garden | Passed after locking the pond, gravel court, loop and bridge and preventing incompatible European-garden imagery from redefining the program. |
| Wetland/rain garden | Topology passes with three explicit cells and a locked boardwalk network; ground imagery remains more diagrammatic than the render. |
| Linear greenway/daylighted creek | Not accepted on the oversized test footprint. The generic profile created multiple water bands instead of one creek. It needs a variant-specific creek guide and footprint rule. |
| Urban forest | Ground topology passes; interactive appearance remains blocked by the lack of a sufficiently realistic canopy library. |

## Acceptance gates for each archetype and variant

An item is ready for users only when all of the following pass:

- **Containment:** no generated ground or fixed object crosses the zone polygon.
- **Whole-element rule:** no court, field, play object, bridge, pond cell or similar program is cropped.
- **Scale:** authoritative metric dimensions are preserved.
- **Topology:** required path, water, circulation and access relationships are unchanged.
- **Collision:** fixed programs do not overlap and render-stage objects do not obstruct them.
- **Grounding:** drape and fixed 3D objects sit on the same terrain frame without hovering or burying.
- **Context:** required streets, paths and gates connect to compatible existing networks.
- **Appearance:** Tiles materials convey the same archetype and variant as the render reference.
- **Camera comparison:** QA images use comparable extents and view direction.
- **Regression:** focused tests, TypeScript and the production build pass.

## Current implementation

- Whole-element packing and orientation search: [`frontend/src/components/viewer/globe/parkGroundProfiles.ts`](../frontend/src/components/viewer/globe/parkGroundProfiles.ts)
- Drape construction and render-reference prompting: [`frontend/src/components/viewer/globe/parkGroundTexture.ts`](../frontend/src/components/viewer/globe/parkGroundTexture.ts)
- Essential live 3D park objects: [`frontend/src/components/viewer/globe/GlobeParkKitLayer.tsx`](../frontend/src/components/viewer/globe/GlobeParkKitLayer.tsx)
- Final mixed-scene render prompting: [`frontend/src/components/viewer/globe/useGlobeAIRender.ts`](../frontend/src/components/viewer/globe/useGlobeAIRender.ts)
- Archetype-by-archetype readiness log: [`docs/PUBLIC_REALM_ARCHETYPE_READINESS.md`](PUBLIC_REALM_ARCHETYPE_READINESS.md)
- Screenshot comparison archive: [`artifacts/park-drape-comparisons`](../artifacts/park-drape-comparisons/)

The orientation-search change uses the `pg6` source signature so older cached drapes cannot silently masquerade as current fitted geometry.

## Verification completed for the orientation-search release

- 92 focused park/profile/render-prompt tests passed.
- TypeScript validation passed.
- Production Vite build passed.
- Live Google Tiles verification passed on project `0d73b4ea-31ea-48bf-8590-f1862f950504`.
- Final QA screenshot: [`sports_complex_orientation_search_tiles.png`](../artifacts/park-drape-comparisons/2026-07-18-batch-04/sports_complex_orientation_search_tiles.png)

## Recommended next work

1. Apply the same complete-element orientation and packing rules to playground modules, pavilions, sports courts and other fixed park programs.
2. Add explicit context-connection metadata and graph validation for the first street/path archetypes.
3. Implement a creek-specific fixed profile for the daylighted-creek greenway variant.
4. Add same-camera image comparison scoring so render/Tiles drift can be measured instead of judged only by eye.
5. Build a realistic, terrain-grounded canopy library only for archetypes whose interactive identity depends on vegetation.
6. Continue visual QA in small batches; catalog coverage prevents broken fallbacks but is not evidence that all 875 current variants are visually accepted.
