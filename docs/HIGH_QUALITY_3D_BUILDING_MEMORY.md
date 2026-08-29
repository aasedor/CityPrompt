# High-Quality 3D Building Production Memory

This is the persistent production memory for turning City Prompt archetypes and variants into high-quality modular GLB families. It captures the construction rules established through the Kinnaird, Chicago, Gothic, glass, Nordic, industrial and Parisian pilots.

The memory has two forms:

- this document explains the decisions to people;
- [`high_quality_building_memory.json`](../tools/archetype_compiler/high_quality_building_memory.json) gives the batch pipeline versioned, executable gates.

The assessor is [`quality_memory.py`](../tools/archetype_compiler/quality_memory.py). `generate_worldclass_library.py` records its result for every generated family, so a batch can continue while only questionable outputs enter a review queue.

Current executable memory: `2026-08-29-rlasm-v6-integrated-method-v129`.

Canonical RLASM authority: [`RLASM_LATEST_METHOD.md`](RLASM_LATEST_METHOD.md).
Package-local RLASM recipes are historical snapshots and must not compete with
that file.

Proven execution checklist:
[`RLASM_PROVEN_BUILD_RECIPE_V5.md`](showcase/sticker-method/rlasm-three-family-independent-pass-2026-08-28/RLASM_PROVEN_BUILD_RECIPE_V5.md).

## The quality target

The target is Kinnaird-class architectural identity in a modular real-time asset, not a literal photogrammetric reconstruction. A successful family must read correctly at three distances:

1. **Block scale:** massing, setbacks, roofline, corner condition and base-middle-crown hierarchy match the archetype.
2. **Building scale:** entrances, balconies, bays, dormers, cornices, towers and other signature projections create the correct silhouette and shadows.
3. **Facade scale:** materials, glazing, joints, returns, interiors and restrained variation withstand close inspection.

A texture can supply surface richness. It cannot repair incorrect massing, missing corners, unsupported projections or a generic roof.

### Runtime visibility standard

Every placed building with a valid LEGO recipe must resolve to its authored GLB
in the normal site view. Do not cap detailed rendering by distinct-family count:
a mixed plan may contain many one-off families, and replacing the third or later
family with a generic grey massing prism destroys the reviewed archetype identity.
The ordinary total-stack guard and WebGL context recovery may remain, but every
family inside that supported plan budget is admitted. Loading placeholders must
be transient; after the assets settle, no valid placed family remains a generic
massing proxy.

An authored building also owns the visual footprint once its saved recipe is
renderable. Suppress the planning prism and its outline from that durable saved
state rather than from a transient GLB-loader callback. For several disjoint
replacement footprints, clip source tiles with one world-coordinate polygon
union; never leave projected stencil side walls mounted behind the GLBs. The
normal 3D view must show authored construction and surrounding context, not
pale blue, grey or white planning boxes.

### Haussmann minimum acceptance standard

The user-approved Classic Haussmann live model is the minimum quality goalpost
for every new or materially revised building family, regardless of style. The
archived live reference is
[`haussmann-minimum-standard.png`](assets/high-quality-3d/haussmann-minimum-standard.png).
It establishes four inseparable acceptance pillars:

1. **Archetype-shaped massing:** corners, courts, roof profile, setbacks and
   other identity-bearing volumes create a distinctive silhouette rather than
   a decorated rectangular box.
2. **Real construction depth:** railings, balcony slabs, recesses, returns,
   cornices, dormers, entrances and other shadow-casting elements project,
   recede or remain visibly open as the reference construction requires.
3. **Photoreal material and optical response:** an archetype-specific,
   render-locked PBR skin, layered glazing and occupied depth remain convincing
   in the live City Prompt lighting stack at facade-close and oblique cameras.
4. **Resilient LEGO scaling:** fixed entrances, corners, crowns and roofs retain
   authored proportions while complete middle bays absorb ordinary width,
   depth and floor variation; oversized targets use the authored fallback or
   streetwall repeat instead of stretching the identity.

A family that succeeds in only one or two pillars is not production-ready.
Every keeper manifest records `quality_standard_evidence` naming distinctive
shape features, physical depth features, fixed identity anchors, repeatable
middle roles, the locked comparison views and the human-approved comparison
sheet. The assessor routes missing or incomplete evidence to review, so a
textured box, a detailed but non-scalable sculpture, or a modular model with
generic materials cannot receive `high_quality_ready`.

## The repeatable construction recipe

### 1. Read all reference views as one building

Use the card image plus compatible oblique, side, corner, roof and aerial views. First record what remains invariant across them:

- primary and secondary masses;
- public entrance and ground-floor hierarchy;
- structural and window bay rhythm;
- corner behavior;
- roof type and skyline objects;
- material zones and weathering level;
- signature elements that distinguish the family.

Three compatible views are the normal minimum. One-view archetypes may proceed, but they receive lower confidence and mandatory visual review. Never silently combine images from different variants.

### 2. Separate fixed identity from repeatable capacity

Every family is decomposed into:

| Fixed semantic assemblies | Repeatable middle assemblies |
| --- | --- |
| podium and entrance | typical A bay/floor |
| corners and end returns | typical B bay/floor |
| crown and terminal cornice | typical C bay/floor |
| roof, dormers and skyline | additional seam-safe variants |
| landmark pavilion or tower | neutral infill bays |

When a user's polygon changes size, only the middle expands or repeats. Entrances, corners, crowns and roofs keep authored proportions. This rule is the main defense against stretched, computer-generated buildings.

### 3. Put the correct information in geometry

Model anything that changes silhouette, creates a meaningful shadow, expresses construction depth or must remain correct from an oblique view:

- massing, wings, courtyards and setbacks;
- rounded/chamfered corners, pavilions and towers;
- entrance recesses, supported canopies and arcades;
- roofs, dormers, chimneys, parapets and deep eaves;
- window recesses, sills and stone returns at close range;
- balcony slabs, railings and wrapping cornices;
- buttresses, brise-soleil, pilotis, bay windows and oriels;
- bevels and profiles on exposed edges.

Bake fine joints, subtle weathering, material grain, small ornaments and city-distance interiors. Never place columns or projections across windows unless the reference shows that construction.

### 4. Generate a material system, not a building picture

The image provider receives the archetype views as hard design references and generates an orthographic, rectified, shadow-neutral facade elevation. The production package contains:

- albedo;
- normal;
- roughness;
- AO;
- depth;
- emissive;
- semantic glass and opaque masks;
- podium, typical, alternate and crown bands.

Generic tiled materials are supporting materials only; they are never the
primary identity skin for a new archetype. Every family must retain an
archetype-specific render-locked source derived from its compatible reference
views and register that source to named elevations and semantic surfaces
(entrance, wing, drum, pediment, dome, tower, roof or equivalent). The skin
manifest records the source archetype id, registered surfaces, UV strategy,
runtime depth/displacement binding and `generic_tiling_allowed: false`.

The runtime shader must actually consume the declared normal and depth maps.
An unused depth file, a generic marble/brick/metal tile, or a style-only atlas
does not satisfy this contract. Fine reference detail belongs in the registered
skin; silhouette, openings, returns and identity-defining shadows remain
physical geometry in front of it.

The close-range atlas is normally 4K and must be at least 2K. A compressed 1K-or-smaller LOD serves city scale. The albedo must not contain directional sunlight or cast shadows; City Prompt owns illumination.

A channel list in a manifest is not proof of a skinned model. Production
assessment resolves every near/far albedo, normal, roughness, AO, depth,
emissive, glass-mask and opaque-mask path on disk, verifies the declared atlas
widths, and requires the render-locked source plus skin manifest. The exported
GLB must embed the same registered materials; an empty texture inventory is a
contract defect even when the channel names are correct.

Gemini and GPT Image are interchangeable source providers. Provider choice is recorded as provenance, while rectification, PBR derivation, assembly and validation remain identical.

### 4A. Preserve the reference-locked image-generation recipe

Image generation is a reproducible design-source stage, not an ephemeral
conversation or a one-off beauty-render step. Every family retains the exact
inputs, prompts, raw keeper outputs and intended geometry registrations that
produced its approved skin. A future generator must be able to reproduce the
same source package without relying on chat history or temporary files.

Use this finite sequence:

1. **Lock the evidence.** Save the compatible archetype views and one labelled
   goalpost composite. Record the exact catalogue and variant ids; reject
   sibling aesthetics before prompting.
2. **Generate by semantic role.** Author a rectified front elevation, a
   shadow-neutral material study and an occupied-depth plate. Add an aerial or
   roof source, courtyard or secondary elevation, and special-enclosure study
   whenever those surfaces carry identity. These are separate jobs because one
   perspective render cannot be stretched into all of them.
3. **Constrain every prompt.** State the source archetype, output role and
   camera; lock footprint, massing, floor count, roof silhouette, bay and
   opening cadence, entrance position and material zoning; request neutral
   illumination and clean registration; explicitly forbid redesign, extra
   floors, invented wings, moved openings, baked entourage and cast shadows.
4. **Keep immutable provenance.** Store raw keeper outputs under
   `textures/source/` and record provider, model, generation date, exact prompt,
   input paths, saved output path, intended role and registered surfaces in
   `textures/source/reference-generation.json` (or the same schema under an
   equivalent source directory). Never make a temporary download the only copy.
5. **Derive, do not substitute.** Convert the keepers into semantic near/far
   albedo, normal, roughness, AO, depth, emissive, glass and opaque channels.
   Derive tile-safe construction zones from the same palette for long or
   nonlinear solids; do not replace the registered identity source with a
   generic brick, glass, metal or stone tile.
6. **Bind sources to construction.** Register each elevation and occupied-depth
   plate to audited model datums and real openings. Physical walls, recesses,
   panes, frames, screens, returns and roof junctions remain geometry.
7. **Run a locked-camera keeper loop.** Compare the unchanged live model with
   the goalposts from front/street, corner, aerial/roof and interior or rear
   cameras. Rank silhouette, opening cadence, material scale, glazing,
   construction depth and roof/corner continuity; correct the largest visible
   deltas, regenerate only the affected source or geometry, and render again.
   Promote a finite reviewed keeper batch before starting another family.

The approved comparison sheet, raw source package and provenance record ship
with the family. This makes the visual methodology reviewable, repeatable and
portable across future waves.

### 4B. Keep construction skins projection-clean and runtime-practical

A perspective reference is evidence for shape, material and occupation, but it
is not automatically a repeating construction texture. Never crop a whole
wall, railing, pergola or service yard from an oblique photograph and wrap it
around a physical solid. That bakes perspective, reflections and neighboring
objects into the material and makes the model read like a photograph pasted
onto a box.

Use these rules:

1. Derive repeating brick, ribbed metal, timber, concrete and roof materials
   from an orthographic shadow-neutral construction plate made from the same
   approved reference palette.
2. Reserve perspective sources for coordinate-registered elevation panels,
   special enclosures and occupied-depth cards where their camera relationship
   is deliberate and cannot repeat.
3. Build visually open assemblies as open geometry. Railings need top and
   bottom rails, posts and balusters; pergolas need posts, beams and fins;
   furniture needs thin seats, backs and legs. An opaque textured slab cannot
   substitute for any of them.
4. Export the real optical glass profile with physical transmission. If
   Blender's proof renderer makes a thin pane appear like a thick tinted
   solid, a temporary alpha-only proof override may be applied *after* GLB
   export, then restored. The comparison image must never silently redefine
   the delivery material.
5. Keep semantic material zones in the manifest while deduplicating identical
   embedded source images. Related zones may reference the same approved
   construction plate, and secondary equipment may consume the far LOD. This
   reduces GLB weight without replacing custom skins or erasing material
   semantics.

Close-up review must explicitly inspect glass, open railings, exposed timber,
rear service walls and roof equipment for photographic projection artifacts,
incorrect metallic response, fake solidity and duplicate-image bloat.

### 5. Build glazing as a layered assembly

At close range, a window is not a blue plane. It contains:

1. a wall opening or visible recess;
2. stone, brick, metal or timber returns;
3. a frame with believable profile depth;
4. a recessed physical-transmission pane;
5. a warm interior backplate or shallow room card;
6. restrained reflection from the environment.

The layered construction is shared, but its optical material is not generic.
Match tint, roughness, coating strength, transmission, frame depth and
occupation pattern to the archetype references. Heritage sash, steel Crittall,
bronze low-e and neutral Nordic glazing are distinct material systems. Keep the
glass itself nearly non-emissive; warm light belongs on the recessed room card.
Use coherent tint across one sash or window wall and vary occupation by room or
floor so a facade does not become a blue/beige checkerboard.

Multi-lite openings use separate pane faces behind real mullions and transoms.
For shaped openings, those faces follow the architectural head: segmental
Crittall panes reach the curved arch, rather than hiding one rectangular glass
card behind a decorative brick outline.

For close City Prompt views, the semantic opening bounds also register a slim
physical sash at the pane plane. Mullions and transoms must be real geometry
when they establish the archetype's construction rhythm (especially industrial
Crittall, punched heritage sash and curtain-wall caps). Do not add a second
heavy perimeter over an audited facade sheet: let the atlas supply fine colour
and weathering while narrow physical bars, returns and sills supply parallax,
contact shadow and grazing-angle depth.

At city distance, the semantic glass mask and baked facade replace most of that geometry. Visible windows default to subtly occupied warm interiors; uniform dark-blue glass is avoided.

The delivery GLB preserves the glazing profile and construction metadata in
glTF extras and exports physical clearcoat, transmission and specular
extensions. Both the globe and standalone LEGO viewers honor that same profile;
runtime normalization must not collapse family-specific glazing back to a
shared facade tint.

Runtime LOD switching is fail-safe per joined facade mesh and semantic band.
Only a matching near/far pair may replace one another. A far sheet on an
unrelated podium, crown or elevation must never hide a near-only authored
facade elsewhere in the GLB. When one complement is absent, keep the authored
facade sheet visible at both ranges and cull only explicitly near-only physical
frames, glazing and interiors. This is preferable to exposing an untextured or
near-black structural core during an aerial orbit.

For fixed render-locked curtain walls, the floor-band crop must retain the complete audited bay rhythm. A one-bay strip is appropriate only when the LEGO assembler explicitly tiles that module. Stretching one office bay across a full canonical elevation destroys the relationship between interior columns and the physical external frame. Derive a separate side crop when the side elevation has fewer bays than the front.

Before reusing a glass-office massing graph, compare its width, depth, floor grid, structural bay count and roof termination to every variant reference. A structurally valid inherited tower profile is still wrong when the catalogue shows a compact infill mid-rise; reference proportions take precedence over prior showcase dimensions.

### 6. Wrap construction around the building

Front-only quality fails as soon as the user orbits. Side and corner elevations must continue:

- material courses and rustication;
- balcony and cornice datums;
- compatible window rhythm and recess depth;
- podium treatment;
- roof material, eaves and drainage logic;
- corner returns and seam-safe transitions.

The side need not duplicate the hero facade, but it must look like the same building. Author front,
left, right and rear elevations for every asset, including courtyard-facing walls. Side and rear
elevations should use a related but intentionally different bay rhythm, entrance/service hierarchy
and opening mix, as real secondary elevations do. Never omit an elevation because it might abut a
future neighbour: City Prompt may occlude authored detail only after the site geometry confirms a
true party-wall condition.

### 7. Break repetition without breaking structure

Use at least three interchangeable middle variants. Variation may change curtains, interior warmth, minor balcony furnishing, window opening state and slight material patina. It must not move structural bays, floor datums, entrances, corners or roof forms.

### 8. Test the declared shape matrix

Every archetype records recommended widths, depths, floor counts, bay multiples and footprint profiles. Production validation renders at least:

- the smallest recommended rectangle;
- the largest recommended rectangle;
- every preferred non-rectangular profile;
- a low and high recommended floor count;
- one street, oblique, aerial and Google Tiles context view.

Fixed assemblies must remain intact, corners must stay within the extent contract, wings must preserve usable depth, and courtyard openings must remain credible.

A fixed landmark is not an exact-dimension trap. Its manifest must declare a
conservative `fixedLandmarkScaleBand` containing `scaleMin`, `scaleMax` and
`maxAxisRatio`. A slightly imperfect user drawing inside that two-axis contract
keeps the authored whole-building GLB and receives an explicit
`fixed_landmark_tolerance` fit label. Once either axis leaves the band, or the
independent axis scales would distort the silhouette beyond `maxAxisRatio`, the
planner must choose the authored stack/streetwall fallback. Only a final forced
fit may exceed the contract, and it remains visibly labelled.

## Catalogue-scale batch strategy

Hundreds of entries should not be treated as hundreds of unrelated sculptures. The batch first clusters archetypes by:

- massing graph;
- signature geometry kits;
- roof family;
- material zones;
- glass profile;
- podium/entrance type;
- footprint compatibility.

One representative from each cluster receives full visual approval. The remainder can run automatically, with confidence outliers and failed gates routed for review.

The resume-safe sequence is:

1. inventory references and metadata;
2. cluster reusable construction families;
3. compile grammars and signatures without API calls;
4. generate or reuse facade sources and PBR sets;
5. assemble fixed and repeatable modules;
6. validate geometry, LODs and the shape matrix;
7. produce comparison boards;
8. import only approved manifests.

Failures do not stop the rest of a batch. Inputs, logs and cached facade sources remain available for a targeted retry.

## Automated assessment

The assessor produces one of three states:

- `pass`: structurally valid and all encoded production-quality gates pass;
- `review`: structurally valid, but one or more fidelity or legacy-contract checks require inspection;
- `fail`: structurally unsafe or incomplete; never import.

Important: `pass` means the machine-readable contract is complete. Cluster representatives still require visual approval because architectural likeness and taste cannot be fully reduced to numeric checks.

Assess a generated family directly:

```powershell
python tools/archetype_compiler/quality_memory.py `
  build/codex-lego-parisian-detail-correction-v19e/parisian-v19e-detail-correction_manifest.json
```

Write the assessment beside a family:

```powershell
python tools/archetype_compiler/quality_memory.py `
  build/codex-lego-parisian-detail-correction-v19e/parisian-v19e-detail-correction_manifest.json `
  --output build/codex-lego-parisian-detail-correction-v19e/quality_assessment.json
```

Run a resume-safe library batch with the shared memory:

```powershell
backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_worldclass_library.py `
  --registry tools/archetype_compiler/worldclass_v8_library.json `
  --output build/worldclass-production/families `
  --quality-memory tools/archetype_compiler/high_quality_building_memory.json `
  --presentation-view-set all
```

The consolidated index records:

- the quality-memory version used;
- `high_quality_ready` per family;
- complete hard-failure and review findings;
- summary counts for pass, review, fail and pending families.

## Cheap-to-expensive rollout

For a large catalogue, use this order:

1. **Preflight:** grammar, signature, reference and footprint checks; no image API call.
2. **One cluster representative:** full facade generation, GLB, shape matrix and visual board.
3. **Small batch:** 5-10 related archetypes using cached/shared kits.
4. **Cluster batch:** resume-safe generation with automated review routing.
5. **Catalogue import:** only validated and approved families.

This prevents expensive image generation from being spent on an incorrect semantic decomposition.

## Failure memory

The machine-readable memory contains the full symptom/cause/correction ledger. The recurring lessons are:

- flat skin plus generic box produces cartoon architecture;
- details need believable attachment and must respect openings;
- generated shadows fight runtime lighting;
- dark-blue glass without interiors looks dead;
- pasted-on dormers and unsupported awnings reveal the procedural construction;
- front-only detail fails in the Google Tiles orbit workflow;
- stretching fixed ends destroys identity on new polygon sizes;
- validating one rectangle is insufficient for a parametric LEGO family.

### V20 four-family batch lessons

The Gothic, modern glass, Nordic timber and classical civic validation batch added five production rules:

- The massing graph reference dimensions are executable, not descriptive. A floor-count mismatch can silently route a hero model through the generic stack, so preflight must prove the chosen width, depth and floors activate the intended graph.
- Generated curtain-wall albedo already contains an authored bay cadence. Physical mullions must match that cadence, use the correct metal finish and remain shallow; a second universal black grid makes the facade look caged.
- Per-elevation material clones are temporary UV tools. After surface-specific UVs are baked into the joined mesh, remap those slots to canonical shared materials before GLB export.
- An attractive AI elevation is still a failure if it invents storeys, changes the podium/roof hierarchy or moves the entrance. Use provider A/B only for a failed source and accept on architectural fidelity, not beauty alone.
- Derive 4K PBR packages sequentially or with a strict worker limit. Full albedo, normal, roughness, AO/depth and emissive arrays can exhaust memory when several families are processed concurrently.

### V21 five-family expansion lessons

The London mansion, industrial loft, Eixample block, modernist civic block and Châteauesque hotel expansion added four more production rules:

- A semantic glass mask is an instruction only when its regions are opening-accurate. Coarse or deterministic fallback regions must stay in `mask_only` mode; turning them into frames creates oversized rectangles or a second facade cage.
- Chamfered perimeter blocks need oriented skins and fixed corner assemblies on every diagonal face. Cardinal front/side textures alone leave conspicuous blank wedges at street corners.
- A projecting pavilion or tower is a small building, not a decorated front plane. Its facade material, cornice datum and roof junction must wrap both returns before it can pass an orbit-view review.
- European balcony kits use thin slabs, open end rails, pickets and believable corbels. Solid black end plates and unsupported balcony boxes immediately reveal procedural construction.

The batch also confirmed a workflow constraint: the generator is resume-safe and preserves valid manifests. When a massing graph or assembly recipe changes, write to a new versioned output or deliberately invalidate only the old manifest so the corrected representative is actually rebuilt.

### V34 render-locked variant pilot lessons

The brick/bronze mid-rise, terracotta-fin office, Second Empire mansion and Perpendicular Gothic stress test added six rules for catalogue-scale variant production:

- Give every materially or geometrically distinct variant its own signature profile. Parent-level glass, massing and kit choices can be visibly wrong even when the catalogue labels are related.
- Audit the physical span of a complete elevation before PBR derivation. Registering a 30-60 metre landmark as a 9.6 metre repeat strip miniaturizes and repeats entrances or towers.
- A render-locked podium owns its photographed stone courses. Generic `stone_base` geometry must not draw a second ladder of rails over shopfront glazing.
- Geometry that supplies depth must inherit the atlas material language. Brick pilasters remain brick and terracotta fins remain fired clay; universal pale stone or black metal makes the overlay look detached.
- Crown height is a variant datum, not automatically one typical storey. A measured 1-2 metre cornice must remain a fixed shallow module.
- Orthographic elevations with negative space around towers cannot be applied to a rectangular skin. Split them into fixed tower/crown skins and background-free repeatable nave or wing bands; reject the generic stack until that semantic massing graph exists.

Use `--grammar-only` before any paid image generation or Blender work. It exposes the exact variant, dimensions and signature contract cheaply. Start glass-heavy families with the city geometry profile; promote only the opening-accurate close LOD to full physical glazing after its mask and performance budget pass.

### City Prompt render-lock parcel pilot lessons

The Junction Contemporary Addition pilot established the live render-to-model loop:

- Lock the target to the approved project render, not a generic catalogue thumbnail. The elevation atlas must carry that render's material hierarchy, glazing warmth, entrance language and crown treatment.
- Treat a recessed rooftop addition as a fixed crown assembly at the canonical floor count. Repeat only preserved middle floors; adding a generic setback storey duplicates the pavilion and changes the silhouette.
- Measure the drawn geographic polygon for every assembly request, even when an older catalogue card has no `footprintCompatibility` record. Catalogue dimensions are recommendations; the parcel is the source of truth.
- Author coexisting native dimension tiers for materially larger parcels. Scaling a 25 x 20 m family onto a roughly 45 x 36 m site loses bay proportions and lets an older, less accurate family win the fit score.
- Use `--allow-outside-bounds` only for an intentional, named dimension tier. The resulting grammar records that it exceeds catalogue recommendations and still passes the standard geometry validator.
- Use true world-coordinate tile clipping for every supported replacement footprint. Several disjoint buildings share one polygon-union shader mask; projected stencil volumes can erase photogrammetry that merely sits behind a proposal and produce pale wedges or boxes around otherwise realistic models.
- Deleting a generated Building makes the zone ready to build again. A stale historical `community_3d` marker or `building_ids` array must not disable placement or redirect recipe saves to a deleted record.
- Review three scales before approval: rectified facade, standalone street/aerial GLB, and a close orbit inside Google Tiles. A family passes only when the architectural hierarchy survives all three.
- Generate a dedicated repeatable secondary-elevation band. Never wrap a front sign, ceremonial entrance or fire escape around side and rear walls; secondary elevations share the material language but use their own opening/service rhythm.
- Carry that side band through the PBR upgrader, including its semantic mask and real-world repeat span, then register side/rear glazing geometry to it instead of to the front atlas.
- An audited atlas already owns fine sash sightlines. Do not draw a second complete perimeter frame over those pixels. Use the semantic mask to build the cavity, internal masonry returns, recessed pane, projecting sill and warm room layer; reserve extra cap geometry for a reference that visibly requires it.
- Crop isolation backgrounds from the rectified elevation and its semantic mask before slicing repeatable bands. A white or gray margin that survives the crop will wrap into the middle of a resizable facade as a blank vertical panel.
- When a fixed Corten insert, tower, sign or entrance is modeled as geometry, exclude it from the repeatable middle atlas. Let the atlas describe the ordinary bays and let the fixed assembly carry the singular volume.
- Roof identities need real section geometry: shallow elliptical brewery vaults, framed sloped greenhouse ribs, clerestories and occupied roof terraces must replace generic mechanical clutter rather than sit on top of it.
- A masonry reveal belongs wholly inside the cut opening. Centering jamb/head/sill boxes on the opening boundary leaves half of each box on the wall face and creates a false picture-frame outline.
- Close Google Tiles QA is the calibration authority. A profile that looks restrained in a standalone preview may become oversized against photogrammetry; use roughly 45-55 mm exposed metal sightlines and construction-scale recesses rather than increasing outline thickness to signal depth.

### Perpendicular lantern + community live-QA lessons

The Perpendicular Revival family and its live City Prompt placement added five
rules that apply to the wider catalogue and the Master Plan community target:

- Polygonal towers need construction assemblies on every exposed plane. The
  compiler now supports oriented facade skins and recessed pointed-window
  arrays on arbitrary angles; converting a square mass to an octagon without
  those diagonal returns simply trades one silhouette error for four blank
  wedges.
- Frontage is semantic, not just geometric. The planner must identify the
  public-street edge and the service/rear edge, then rotate the family so the
  ceremonial entrance addresses the street. Polygon winding or zero rotation
  is not a valid orientation rule.
- Pale stone must be approved in the live Google Tiles lighting stack. Bright
  exposure can compress an otherwise detailed limestone normal/AO field into a
  flat white surface. Calibrate albedo and viewer exposure before adding more
  ornament to compensate.
- A render-locked landmark may keep its lantern, terminal towers, entrance and
  roof fixed while scaling only ordinary wall bays. This fixed-signature /
  repeat-middle contract is what lets the community planner resize families
  without multiplying entrances or destroying the silhouette.
- Neighborhood proof requires separate hero, district and map LODs. Reuse the
  same identity and material language, but instance shared pieces, compress
  textures and preload route-visible assets so the walkthrough remains stable.

### Ruskinian turret + profile-glass lessons

The Ruskinian collegiate pass exposed two reusable gaps that are easy to miss
when the front facade sheet already looks convincing:

- A round or polygonal corner is a complete fixed assembly, including its
  openings. Do not attach a front-only window after the turret is built. Each
  corner must own the two outward tangent elevations, with the pane, warm room
  card, frame and return ordered just outside the opaque drum. Window levels
  should align with the masonry-course composition rather than interrupting it
  arbitrarily.
- Semantic graph windows and facade-sheet overlays must consume the same glass
  profile. The shared profile controls tint, roughness, transmission, IOR,
  clearcoat and occupied-light behavior; alpha remains opaque for glTF. A
  profile name stored only on the facade overlay does not correct generic
  `MAT_Glass` used by entrances, turrets or roof lanterns.
- A family-specific texture library is part of the reproducible build recipe.
  If the generated PBR slate or brick keys are absent from the selected texture
  root, the compiler falls back to flat colors and can turn a signature roof
  into a white or generic slab even though the graph geometry is correct.

### Render comparison + public-realm handoff lessons

The approved Ruskinian City Prompt render showed that matching the elevation
image is necessary but not sufficient. The render derives much of its realism
from sectional hierarchy: deep traceried openings, layered arches, carved belt
courses, roof cresting, steps, planting and contact shadow at grade. Use the
same-camera live comparison to decide which cues become construction geometry;
do not ask a sharper albedo to imitate every shadow.

A standalone replacement building may be the only zone in an older project.
Its spatial tile mask therefore clears the source Google mesh without a separate
site-boundary ground surface, exposing the scene background around irregular
walls and turrets. Mount a deterministic terrain-toned footprint surface beneath
the model and overlap it slightly below surviving tiles to hide shader/mesh edge
seams. The visible entrance walk, stairs, planting and retaining edges then belong
to the coordinated public-realm LEGO recipe. This is the handoff between a
render-locked building family and the street/park family, not disposable render
entourage.

### Registered facade schedules

Do not trust a generated semantic glass mask or automatic floor-band detector
when it merges masonry, sky, two storeys, or image background into one region.
Render-locked families may carry two small normalized schedules beside their
source elevation:

- `opening_schedule.json` records exact rectangular or segmental-arched glass
  openings. `create_registered_opening_mask.py` rasterizes it at any atlas
  resolution, so the same audited bays drive near glass, cavities, frames,
  sills, interiors and city LODs.
- `band_schedule.json` records the exact repeatable floor, alternate floor,
  crown, podium and side-bay crops. It may crop both X and Y, preventing sky or
  white image background from becoming building material.

Pass these schedules through `generate_facade_sheets.py` with
`--registered-opening-schedule` and `--registered-band-schedule`. The output
manifest retains their filenames and labels the semantic mask provider as
`deterministic`. A generated elevation is an identity source; only audited
architectural regions are allowed to become modular construction.

### Ruskinian repeat-span + relief registration lessons

The polychrome collegiate family added four rules for resizable hero facades:

- Never stretch a complete elevation to fill a larger wall. Record the real
  middle-bay period and repeat that period with the same phase in the facade
  skin, semantic glass, interior cards and close LOD. Entrances, corners,
  podiums, crowns and roofs remain fixed.
- A semantic mask is not automatically a construction drawing. Broad or merged
  regions may drive an inset pane and warm room card, but they may not generate
  jambs, sills, mullions or returns until an audited opening schedule proves
  registration. Otherwise the result is a pale cage over a good atlas.
- Solve wall spans from fixed corner geometry. Front and rear skins extend to
  the inside tangent of cylindrical turrets; side skins use their own tangent
  span. Add a small overlap tolerance so the service core cannot appear as a
  dark slot during an aerial orbit.
- Relief that duplicates atlas coursing must be materially and dimensionally
  subordinate. Use the same warm stone PBR family, shallow projections and
  narrow profiles; validate in Google Tiles because bright runtime exposure can
  turn a restrained offline course into detached white trim.
- Derive an integer repeat count from the measured PBR band span before Blender
  assembly. The physical segment (`wall span / repeat count`) should stay within
  ten percent of the manifest span on every elevation; otherwise the facade,
  semantic glass and occupied interiors remain phase-aligned but are still
  visibly stretched together.
- Preserving a `side` band in the facade manifest is insufficient: the Blender
  material loader must materialize that role before the massing graph can apply
  it. Inspect left, right and rear faces in both near and far review LODs.
- Treat the quality memory as the camera-set authority. The renderer's `all`
  preset must emit front-corner, rear-corner and facade-close views as well as
  preview, street, aerial and context views; a missing role is a producer bug,
  not a manifest exception.
- A gable-roof primitive cannot assign its roof finish to a visible masonry
  end wall. Add fixed, axis-aware gable-end construction with its own verge,
  horizontal bands and pointed openings on every exposed cross-gable face.
- Layered gables need an explicit outward construction order. Offset the brick
  infill to the exposed face of the deeper stone verge; co-locating both prisms
  hides the infill and turns the whole gable into a pale stone triangle.
- Multi-role near/far PBR families legitimately carry more materials than a
  flat legacy atlas. Review above 32 assembled materials while continuing to
  consolidate shader-equivalent clones and package runtime textures with KTX2.

### Narrow rowhouse camera + secondary-elevation lessons

- A required camera is invalid when contextual planting blocks the asset. Near
  trees must have a camera-safe minimum lateral offset for narrow lots; width-
  relative placement alone can put a crown directly on the view corridor.
- A decorated principal bay is not a universal side-wall module. Use a quiet
  brick secondary band for party walls, then add only the sparse recessed side
  and rear openings supported by the oblique and roof references.
- Keep the exact front-bay count evidence-led. The Red Brick & Sandstone pilot
  is five bays wide—two sash bays, one fixed centre entrance bay, and two sash
  bays—not a generic four-bay rowhouse.

### Eixample perimeter-ring + native-tier lessons

- A courtyard declaration is not a courtyard. Disable inherited solid cores
  and roof decks, then build the cardinal wings, diagonal corner wings and roof
  pieces as a real perimeter ring. The aerial acceptance view must show an
  uninterrupted open light court.
- Bind a fixed landmark graph to its accepted native width, depth and floor
  count. If the requested tier differs, the compiler intentionally falls back
  to the parametric LEGO stack; keep the profile, cohort registry and tests
  synchronized so a parcel-envelope correction cannot silently discard the
  reference-locked massing.
- Treat catalogue floor evidence as variant-level data. The Classic Eixample
  references show one ground floor plus three residential levels, so that
  variant owns a four-storey bound even when the parent archetype permits a
  broader range.

### London one-view heritage + fixed-facade lessons

- One authoritative catalogue view is lower-confidence evidence, not a reason
  to skip the unseen construction. Infer a conservative wrapped envelope and
  require rear-corner, aerial and context review; record the side/rear inference
  in the keeper's human QA.
- When an atlas already owns the complete sash, surround and masonry rhythm,
  do not stack a generic repeated-floor kit over it. Use a fixed massing graph,
  promote only audited shadow-bearing detail, and keep glazing mask-only unless
  a registered opening schedule proves a physical return is needed.
- White presentation margins in a rectified elevation become blank facade
  wings when mapped across a canonical skin. Crop the source or UV bounds to
  the architectural extents before PBR generation and verify the complete bay
  rhythm in the rendered frontage.
- A fixed graph can still reuse the canonical roof kit. A dedicated graph node
  should preserve the audited mansard, dormers and chimneys while the body,
  cornices and raised pavilions remain explicitly authored.

### Haussmann twin-court + delivery-budget lessons

- A court must remain open through every construction layer. Building the wall
  body as perimeter wings is insufficient if a full cornice slab or roof deck
  caps the void; use explicit roof-ring strips and prove every court from the
  aerial acceptance camera.
- Separate the principal entrance from a repeatable podium source before
  scaling. Stitch ordinary shopfront slices into the repeat band and retain one
  fixed entrance role so a long boulevard frontage cannot duplicate its grand
  door.
- Dense fixed graphs may disable the final joined-mesh bevel when their
  silhouette-bearing solids already own individual construction radii. Review
  facade-close and aerial views after optimization; the Classic Haussmann graph
  fell from 215,572 to 69,780 assembled triangles without losing identity.
- Native source evidence sets the useful near-atlas ceiling. Upscaling a 1141
  px rectified elevation to 4K added payload but no detail, while a 2K near / 1K
  far package retained the accepted render and reduced the assembled GLB from
  33.1 MB to 13.9 MB before KTX2.
- Reuse the selected occupied-glass cell as both pane and shallow room card in
  roof sashes. A helper that silently allocates its own legacy room palette can
  push an otherwise identical graph over the material-review threshold.

### Rounded boulevard-corner + turret-seat lessons

- A rounded facade cannot be faked by a small cylinder attached to a straight
  block. Author the masonry quarter-drum, tangent shopfront/window bays, stone
  courses and balcony arcs as one fixed landmark assembly, then let only the
  straight wing bays repeat.
- The turret centre belongs on the outward street-corner bisector, not at the
  inner tangent origin of the rounded plan. Otherwise the mansard hides the
  bulb and leaves only a small finial visible from the acceptance camera.
- Round the mansard's outer contour to the same tangent radius, omit dormers
  that would collide with the curve, and seat the zinc crown on a real masonry
  drum. Reject floating decorative rings and validate the seat from both the
  front-corner oblique and aerial cameras.
- A perimeter graph must skin short return walls as well as its long cardinal
  elevations. The aerial view is the fastest gate for blank square-corner ends
  that a front hero camera can miss.

### Civic courtyard + ceremonial-envelope lessons

- Roof-plan evidence can overturn the apparent solid-block reading of a front
  hero image. Build civic courts as four perimeter wings and construct the
  hipped roof from explicit outer, ridge and inner contours so the void remains
  open to sky; the aerial render is the acceptance proof.
- A portico and broad ceremonial stair legitimately project beyond the civic
  body. Treat them as fixed landmark assemblies, fit their depth deliberately,
  and validate the assembled footprint rather than assuming the body dimensions
  describe every architectural projection.
- Window cards on an opaque massing core must sit just outside the exposed wall
  plane. Layer occupied glazing behind shallow ashlar surrounds, and verify the
  front, side and rear arrays from oblique cameras rather than trusting graph
  coordinates alone.
- Material identity matters at roof scale. The catalogue evidence supports pale
  green patinated copper, so a raw-brown copper albedo was rejected even though
  its channel set was technically valid. Preserve the patina colour and add
  seam relief only when it improves the near LOD without closing the roof ring.

### Neoclassical courthouse + roof-plane lessons

- Selected-variant evidence outranks generic parent-archetype prose. The
  Neoclassical Temple references prove a deep solid body and cross-hip roof,
  so the parent courthouse prompt's dome and rotunda were explicitly rejected.
- A colossal order needs construction rhythm, not smooth cylinders. Use a
  fluted shaft profile, capital-style-specific geometry, one fixed column count
  and an audited door/window schedule; never scale the temple centre as a
  repeatable ordinary bay.
- Standing seams on a dominant hip are silhouette-adjacent roof construction.
  Register each seam to its actual slope, fan the outer runs toward the ridge
  endpoints, and inspect the entire pattern from the aerial acceptance view.
- Monumental stairs and cheek walls are part of the native frontage envelope.
  Validate the assembled landmark—not only its body core—and let the full-width
  ceremonial terrace establish the reference width when the images support it.

### Paired brownstone streetwall + stoop/fence lessons

- Selected-variant evidence can describe a larger joined composition than the
  parent catalogue default. The traditional brownstone images prove a 30 metre
  paired streetwall with three fixed entrances, so compiling one 18 metre
  generic rowhouse would discard the defining construction rhythm.
- An arched entrance is not finished when its bounding silhouette is correct.
  Keep the timber backing visible and add paired leaves, panel relief and a
  transom so the portal reads as a door rather than pale glazing or a blank
  dark slab in the street view.
- Garden-level ironwork must be segmented around every fixed stoop and landing.
  Terminate fence rails at stair cheek walls and use the front-corner view to
  prove all three entrance paths remain clear.
- A flat roof still carries family identity. Preserve the paired roof seam,
  stepped cornice/parapet termination, bounded skylights, chimney caps and
  terracotta pots, then use the aerial review as the acceptance gate.
- Where the references do not prove a rear addition or exposed party-wall
  ornament, prefer a conservative solid rear envelope and quiet party wall.
  Record that inference in human QA rather than inventing a second principal
  facade.

### Victorian polychrome main-street + simulated-opening lessons

- Cohort placeholders do not outrank selected-variant evidence. The Victorian
  Polychrome references prove a native two-storey shop block, so the registry's
  provisional four floors had to be corrected before keeper promotion.
- Continuous masonry courses cannot pass through layered panes and room cards
  as if those layers were boolean wall voids. Segment decorative bands around
  the audited opening schedule and place geometry only on solid pier spans.
- Painted cast iron is not generic black metal. Preserve the evidence-led
  forest-green albedo and moderate metallic response instead of allowing a
  black-metal texture key to erase the painted finish.
- Roof-plan review controls ridge direction even when the street camera hides
  most of the roof. Register seams to the corrected hip, lift skylights onto
  explicit curbs above the local plane, and prove the service roof, chimney and
  parapet together in the aerial acceptance view.
- Fixed storefront identity includes entrance count as well as display rhythm.
  Keep both recessed entries, the cast-iron pilasters, spandrel/frieze hierarchy
  and six upper arches fixed; only ordinary display or sash bays may repeat.
- A convincing public elevation does not authorize stretching its crop around
  the long sides. Author a true-aspect secondary-elevation PBR source at real
  masonry course scale, register its own opening rhythm and alpha voids, and
  reserve physical relief for returns, sills and sashes. The front-corner
  oblique is the acceptance view for brick scale and course continuity.
- A flat service zone inside a hip is roof topology, not rooftop equipment.
  Build the sloped perimeter from an explicit inner contour meeting the deck
  at one shared elevation. Terminate standing seams at that contour and at
  skylight curbs; let registered normal/depth relief carry any seam direction
  that would otherwise cross another roof face or form a wire lattice.

### Original textile mill + variant-graph inheritance lessons

- A selected variant profile normally replaces its parent profile. When one
  variant intentionally reuses a fixed parent massing graph, declare that with
  an explicit `massing_graph_from` contract; never implicitly share the graph
  with sibling brewery, power-station or modern-loft variants.
- Selected-variant dimensions control the fixed graph. The original mill is a
  30 by 20 metre, four-level building on an audited four-metre structural grid;
  provisional parent heights must not stretch it into a generic tall block.
- Automated validation cannot detect a plausible but contradictory fallback.
  Reject a valid generic stack when the photoreal and catalogue references
  prove a gable, roof monitor, chimney, four principal bays and no terraces.
- A single rectified principal elevation can provide a conservative wrapped
  envelope, but it is not independent secondary-elevation evidence. Inspect
  rear-corner and aerial views, use different crops where supported, and record
  remaining repetition in human QA.

### SoHo cast-iron warehouse + fire-escape lessons

- Storey and bay counts are hard source-image gates. The first rectified image
  resolved seven unequal bays despite a five-bay brief; it was rejected before
  any opening schedules or PBR maps were built, and one bounded correction pass
  produced the accepted five-by-four grid.
- Do not bake a silhouette assembly into the atlas and model it again. Crop the
  photographed roof guard out of the architectural elevation when a fixed 3D
  perimeter rail owns that role, then review both the cornice and roof plan.
- Fire escapes need physical load paths. Build grated landings, three-sided
  guards, alternating flights, treads and wall braces as an axis-aware graph
  assembly so the same kit works on principal and return elevations.
- Painted cast iron and exposed black steel are different finishes. Use softer
  charcoal iron for full-height pilasters and the fixed building order; reserve
  black metal for fire escapes, roof guards and small hardware.
- A geometry-only assembled pilot can prove axes and silhouettes before PBR,
  but its missing reusable-module validation is expected and it is never a
  keeper. Promotion still requires the complete seven-module package.

### Richardsonian warehouse + secondary-elevation crop lessons

- Storey and bay counts remain hard gates even when the generated source is
  stylistically convincing. The first orthographic pass produced eight bays;
  it was rejected before scheduling, and one bounded correction produced the
  accepted ten-bay, three-level elevation.
- Compare the measured physical atlas span with the provisional massing tier.
  A 42.73 metre registered elevation would have been visibly stretched across
  the original 55 metre placeholder, so the evidence-led native frontage was
  corrected to 44 metres before keeper generation.
- A short elevation is not the long elevation compressed. When the oblique
  reference proves five side bays, partition that face into five deliberate UV
  crops and apply identical crops to semantic glazing so every bay aligns with
  one physical pier interval.
- Render validation is iterative: the first textured candidate was structurally
  valid but failed visual review because it squeezed ten bays onto the return.
  Rejecting that candidate and rerendering the crop pilot was required before
  rebuilding the complete module family.
- Roof-plan evidence owns the flat service roof. Preserve the continuous
  parapet, one low access enclosure, one modest HVAC unit and one hatch; do not
  introduce a tower, gable, court or full penthouse absent from the references.

### Cream terra-cotta Art Deco tower + tier-envelope lessons

- Every setback stage owns a distinct exposed envelope. A combined shaft stack
  buried the podium atlas inside the larger granite base, so podium, shaft,
  occupied setbacks and crown had to be separated and placed on their true
  footprint faces.
- Coordinates are axis-dependent at every tier: front and rear skins use the
  stage's half-depth, while left and right skins use its half-width. A valid
  front render cannot excuse blank return walls; aerial review must prove all
  four faces through the complete setback hierarchy.
- Do not turn an unreviewed legacy automatic glass mask into hero geometry.
  Reflective mullions and relief panels produced torn silver cutouts; the clean
  correction retained the deterministic PBR elevation and fixed physical piers
  while disabling the noisy semantic overlay until a registered schedule exists.
- Landmark crowns cannot be generic roof props. Preserve the stepped plinth,
  dark octagonal lantern, eight separate gilded posts, faceted roof and finial
  as fixed construction, and compare their silhouette to both oblique and
  roof-plan references.
- A geometry-only pilot may validate the 30 by 28 metre footprint, 15 occupied
  levels and 74.5 metre landmark silhouette, but keeper promotion still needs
  the complete module package and the corrected textured eight-view review.

### Nordic mass-timber midrise + open-roof-pavilion lessons

- A roof pavilion's void is construction evidence. The first valid pilot used
  a full shadow core and curtain walls, turning the light reference canopy into
  a sealed black box; it was rejected before canonical packaging.
- Build an open pavilion from fixed timber posts, a thin canopy and only the
  compact service wall proved by the references. Do not use opaque occupation
  geometry to close the air between those elements.
- An occupied green roof needs a visible edge contract as well as a sedum
  material. Pair the planted deck with a slender perimeter guard and verify its
  relationship to the pavilion from aerial and street-oblique cameras.
- The rectified timber atlas can carry natural larch variation and fine joint
  evidence, while fixed glulam frames, deep loggia shadows and balcony rails
  carry the near-range structure. Neither layer substitutes for the other.
- Assembled-only pilots are the right bounded checkpoint for roof silhouettes
  and semantic-glass artifacts. Their expected missing-module validation is not
  a keeper failure; promotion still requires the complete seven-role package.

### Scandinavian white-plaster housing + audited-band lessons

- Exact storey counts remain a hard gate even for a clean orthographic source.
  When repeated image corrections still returned four rows for a five-wall-level
  building, the source was rejected as a full-height atlas rather than stretched.
- Valid source evidence can still be recovered modularly. Audit the ground,
  ordinary and crown bands, then sequence or cycle them into the required wall
  stack while preserving every window's native proportions.
- Keep silhouette elements out of those bands. Balcony slabs, rails, dormers,
  Juliet guards, gable roof and passage surround are fixed geometry; the atlas
  carries plaster, openings and the planted passage view.
- Portal layers need a deliberate depth order. The shadow cavity is deepest,
  the main wall skin sits ahead of it, the fixed entrance atlas sits ahead of
  the wall, and timber jambs/header remain outermost. A coplanar entrance can
  disappear even when its source texture is correct.
- Material keys must resolve to the actual texture library. Selecting the
  registered `standing_seam` key changed the roof from a smooth dark plane to
  the seam field proved by the aerial reference.
- Older catalogue entries may have no parcel-profile metadata. Add an explicit
  compatibility override before canonical generation, identify the one native
  fixed tier, and bound which complete assemblies derived L/U kits must retain.

### Italian portici palazzo + axis-aware arcade lessons

- Reference floor counts outrank provisional cohort placeholders. The selected
  Italian portici evidence proves three occupied wall levels, so the native
  keeper is a 30 by 24 metre three-level palazzo rather than a stretched
  six-level mixed-use stack.
- Bay counts are part of the construction contract. A strong legacy elevation
  with four arches and a central pediment was rejected for this six-arch,
  roof-controlled variant; a new shadow-neutral six-bay atlas aligned the
  shutters and shopfronts to the physical rhythm.
- A deep portico is not a row of punched windows. Use an axis-aware fixed
  arcade assembly with curved rings, shared piers, capitals, recessed occupied
  shopfront cards and a continuous threshold so a corner return remains
  genuinely arched in oblique views.
- Let texture and geometry divide the work deliberately: the atlas carries
  ochre plaster, shutters, fine window trim and shopfront identity, while the
  limestone arches, sparse iron balconies, bracketed eaves, hip roof and
  chimney caps remain shadow-casting assemblies.
- Roof-plan review must include the entire hierarchy. The first pilot's plain
  chimney blocks weakened an otherwise correct hip roof; small tiled hipped
  caps brought the four chimneys back into the photoreal target's silhouette
  before canonical promotion.
- A complete rear service base may remain quieter than the public portico, but
  upper materials, eaves and roof logic still wrap all four elevations. Record
  that hierarchy explicitly rather than mirroring the ceremonial arcade onto
  every face without evidence.

### Restored machiya + roof, gable and lattice lessons

- A legacy elevation with too many wall rows can still be useful as audited
  construction bands. Crop the podium, ordinary wall and crown evidence, then
  sequence only the bands required by the selected two-wall-level machiya; do
  not reproduce the source's complete four-row stack.
- Fine `koshi` lattice needs a restrained physical overlay. Let the atlas carry
  the dense wood grid while a bounded set of shadow-casting bars establishes
  depth; duplicating every photographed slat as geometry creates a black cage.
- The shop threshold is an intentional void, not a bright facade card. Preserve
  the recessed dark opening, divide the indigo `noren` into separate hanging
  panels, and leave the narrow garden entry visibly open beside it.
- Gable framing must read as a complete triangular construction. A lone king
  post and collar looked like an accidental cross; the accepted assembly adds
  the base beam and both sloped rafters around the white clay infill.
- Kawara identity requires silhouette evidence even when the material library
  has only a neutral dark roof membrane. Use physical downslope ribs, ridge and
  eave caps on both roof planes, and prove the ridge direction from aerial view.
- Lower eaves follow the same rule. Replace flat canopy boxes with shallow
  sloped roof segments that wrap the public faces before canonical promotion.

### Scottish Baronial railway hotel + open-court landmark lessons

- Selected-variant evidence outranks a contradictory parent hero. All three
  Scottish Baronial angles prove pink-grey granite, dark slate and conical
  tourelles, so the inherited green-copper facade was rejected immediately.
- Courtyard language is not construction. Build four occupied wings and four
  corresponding roof fields around a real uninterrupted void, then prove that
  void from aerial and rear-corner cameras.
- A clean elevation with the wrong row count is a band library, not a complete
  atlas. Audit the valid masonry bands and sequence them into the exact six
  occupied levels without vertically stretching their windows.
- Landmark entrance towers need a separate envelope and explicit depth order:
  core, tower skin, portal opening, then physical arch and jamb geometry. A
  principal facade stack cannot safely stand in for that hierarchy.
- Do not stretch generic frame grids over round turrets. Place bounded real sash
  assemblies on tangent planes so each outer turret and gate tourelle reads as
  occupied rather than blank or cut by tall black slots.
- Crow-stepped gables carry silhouette identity. Keep their fixed stepped
  profiles ahead of the sloped roof field and review every step against the sky.
- A full canonical rebuild remains necessary after an assembled-only graph
  pilot passes. The pilot can reuse stale generic modules; the promoted family
  must regenerate every LEGO role with the reviewed PBR source and materials.

### Wave 3 civic-family identity, alias and footprint lessons

- Native width and depth are a placement envelope, not an instruction to fill
  the parcel with one extrusion. Archetype evidence controls the occupied
  solids inside that envelope: a theater needs a shallow lobby, deep
  auditorium, stepped shoulders and raised fly tower even when the planner
  advertises one nominal rectangular footprint. Use
  `allow_inset_footprint` for deliberately narrower modules and let empty
  envelope space preserve the silhouette.
- The runtime uses one uniform horizontal contain scale for the complete
  landmark or selected vertical stack. Never divide the drawn width and depth
  by each module independently: that operation stretches every level back to
  the rectangle, erasing narrower upper floors, setbacks, courts, chamfers,
  entrance recesses and roof shoulders. A four-vertex polygon is a site
  envelope; unused space becomes an intentional setback around the preserved
  archetype form.
- Shape matrices must be architecturally honest. A single-frontage theater may
  declare only `rectangle` when L, U or courtyard assembly would duplicate its
  marquee and public entrance. Such an exception must set
  `minimumPreferredProfiles`, explain `profileRationale`, and still prove both
  an in-band plan and an oversized `streetwall_repeat` plan.
- Catalogue identity and generation identity are separate contracts. Every
  selected variant manifest must declare both its parent `archetype_id` and its
  `variant_id` in `archetype_aliases`; do not alias materially different sibling
  aesthetics merely to increase match coverage.
- A stacked theater keeps the marquee, entrance portals and blade sign in the
  fixed podium, ordinary wall rhythm in repeatable floor variants, and its fly
  tower in the fixed roof/crown assembly. Repeating any of those public identity
  elements through middle floors produces a generic or implausible venue.
- A render-locked civic atlas may exceed the ordinary material warning only
  through a bounded per-family `material_budget` with a construction rationale.
  The global waiver ceiling remains enforced; this is not permission to retain
  accidental duplicate materials.

### Fixed landmark silhouette + fallback-kit lessons

- Arena, dome and inhabited-arch families must preserve their one-off silhouette
  as an enabled `assembled` landmark with exact variant identity and native
  floors. An ellipse, dome, arch, oculus, drum, portico or cable-net opening is
  authored construction geometry; it is never approximated by a textured box.
- Fixed landmarks must tolerate ordinary drawing imprecision without silently
  becoming generic. Declare a conservative per-family near-native scale band
  and maximum independent-axis ratio. A bounded uniform contain-fit may retain
  the complete landmark on a modestly smaller or differently proportioned
  polygon because it does not deform the authored axes; route larger or
  strongly elongated parcels to the authored stack or streetwall fallback.
- The fixed landmark and its conservative stack fallback serve different
  targets. The landmark owns native-scale visual identity. Podium, three
  repeatable middle variants, crown and roof keep oversized targets plannable
  through `streetwall_repeat` without pretending that a repeated arena or dome
  is the canonical building.
- Validate the delivered GLB bounds after compression and coordinate export,
  not only inside Blender. Imported image-to-3D hierarchies must be frozen in
  world space, normalized to the declared metric envelope and exported in a
  validator-readable package before promotion.
- For a camera-locked landmark pilot, register screen-space construction
  landmarks before judging ornament: silhouette top and base, roof edge,
  oculus extents, material-band boundaries, entrance crests and media ribbons.
  Curved shells can make physically level rings drift by dozens of pixels in
  an elevated view, so the hero-facing assembly may need a deliberate
  shell-following profile while remaining continuous and plausible from the
  required oblique and aerial checks.
- Monumental entrance stairs belong to a subtractive shell assembly. Cut the
  opening through the exterior and concourse skins, place the first riser at
  the facade plane, climb inward beneath the arch, and terminate at a recessed
  occupied landing. The shell edge, portal cheek, soffit and handrails must
  frame the circulation; a bright solid wedge placed in front of glazing will
  always read as a temporary ramp or another window.
- A free-form hall is one continuous envelope in both plan and section.
  Reconstruct its front, rear, sides and roof together from the compatible
  oblique and aerial evidence; hero-facing ribbons that stop at the corners
  produce a stage set. Exposed shell tops, edge fascias and acoustic
  undersides are separate semantic surfaces with real thickness and deliberate
  materials. In particular, do not let a white exterior shader or a reversed,
  unlit face turn the entrance canopy into a black void.

### Monumental glazing + engineered hall roof lessons

- Treat a full-height concert lobby, station portal or market entrance as a
  section through the building, not as a facade decal. The opening owns deep
  jambs and a soffit, a physical pane and frame layer, a recessed dark
  backplane, and a small number of local warm ceiling bands or occupied room
  cards. One bright card across the entire glass field flattens the opening and
  reads as an orange window.
- Preserve the reference hierarchy inside monumental glass. Exterior
  reflections remain on the pane; mullions and fanlight spokes sit in front of
  the cavity; doors and landings occupy the threshold; warm illumination is
  sparse and spatially separated behind them. Confirm that hierarchy in both a
  facade close-up and a front-corner oblique.
- A multi-aisle market or station roof is one connected engineering system,
  but not one generic shell. Author every visible aisle or vault, ridge,
  valley, clerestory, rib or truss family, purlin run and end fan. The aerial
  and rear-corner views are the acceptance views for this work.
- Roof material hierarchy is construction evidence. If the aerial references
  show opaque zinc or tile weathering fields around narrow glazed lanterns,
  do not make every slope transparent: model the opaque fields, flashing or
  terracotta bands and clerestory glazing separately, then verify ridge count,
  opacity and valley continuity from high oblique and roof-plan views.
- Size fallback-kit arches against their module envelope. A semicircular head
  needs at least half its opening width above the spring line, so its width
  cannot exceed twice the usable module height. If it does, use a segmental
  arch or keep that opening in the fixed landmark; never accept a module whose
  delivered bounds extend below ground.

### Wave 4 standard-building void + balcony lessons

- Standard buildings need the same sectional discipline as landmarks. A
  rowhouse stoop, arched residential lobby or courtyard passage is a fixed void
  through the podium envelope, not another glass bay. Split or cut the wall and
  front/rear skin, keep the circulation path unobstructed, then construct the
  jambs, soffit or ceiling, threshold, landing and stairs as one assembly.
- Floor semantics come from the reference section, not from counting visible
  horizontal bands mechanically. A raised rowhouse garden level and piano
  nobile may belong to one tall fixed podium; adding both as ordinary repeatable
  floors creates an extra window row and breaks the approved proportions.
- A render-locked elevation may carry ornament and masonry identity while
  physical geometry supplies depth, but their schedules must agree. Crop out
  neutral studio gutters, register one complete bay cadence, and do not overlay
  a second window, door or balcony pattern at a different scale.
- Balcony and loggia stacks are constructed once. Use a thin slab, recessed
  dark door or occupied room card, side returns, open end rails, regularly
  spaced pickets and consistent floor-datum anchors. When the source image
  already depicts balconies, use a clean reference-palette wall PBR beneath the
  physical stack so photographed and modeled balconies cannot ghost through
  each other.
- Ordinary roofs remain identity geometry. The mill monitor must rise above the
  gable rather than disappear inside it; Scandinavian dormers and seams must
  follow the actual ridge direction; flat residential roofs need the reference
  parapet, plant court, roof lights and service hierarchy rather than a bare
  dark slab.
- Keep these identity assemblies compatible with imperfect user drawings.
  Entrances, passages, balcony stacks, crowns and roofs stay fixed semantic
  modules while complete ordinary bays and whole floors absorb clean in-band
  variation; oversized requests must remain eligible for streetwall repetition.

### Wave 6 non-residential enclosure + material-system lessons

- A reference source is not a skin merely because it exists beside the GLB or
  appears in a manifest. Inspect the exported material graph and prove that
  authored geometry actually consumes it. Coordinate-register full elevations
  to audited model datums; do not silently fall back to a generic tile after
  generating an archetype-specific sheet.
- Preserve the reference's floor, bay and occupation cadence behind physical
  glazing. Generate a clean occupied-depth plate from the render-locked
  elevation, place it immediately behind the matching pane, and keep exterior
  fins, mullions and rails as separate shadow-casting construction. A uniform
  warm room card cannot substitute for an atrium, office or civic lobby whose
  interior hierarchy is visible in the archetype.
- A monumental atrium is a complete transparent enclosure, not one front
  curtain-wall card. Construct the public facade, both faceted returns and the
  glass roof around one shared section so floor plates, braces and occupied
  room depth remain inside the weather envelope in every oblique.
- Bound occupied backplates to the glazing volume. A room card extending above
  the atrium crest or beyond a return reads as an opaque rooftop box and
  destroys the intended transparency even when the front camera looks correct.
- Different non-residential windows still need different optical systems:
  high-transmission low-iron museum atria, neutral low-e office curtain walls
  behind solar fins, and deep smoked civic slit windows cannot share one blue
  fallback material. Preserve their profile identifiers and construction depth
  through Blender export and every Three.js viewer.
- Solar screens and recessed slits are geometry. Terracotta fins need real
  projection, rails and corner returns in front of physical glass; civic slit
  windows need open concrete cavities, deep sills and soffits, panes and
  occupied backing rather than black bands painted onto solid walls.
- A fixed non-residential landmark may still accept ordinary drawing error.
  Keep the reviewed whole-building GLB inside a conservative independent-axis
  scale band, then use family-specific podium/middle/crown/roof modules for
  oversized streetwall repetition without repeating its canonical silhouette.

### Wave 7 unitized-envelope + curved-void lessons

- A crystalline, diagrid or polygonal enclosure is a panel topology, not a
  rectangular curtain wall with a pattern painted or triangulated over it.
  Reconstruct the documented panel family, scale and opaque-to-glazed ratio;
  wrap that graph continuously around the actual plan; and expose pressure-cap
  seams between opaque neighbours as well as around glass.
- Where a unitized shell meets a curved public void, clip boundary panels to
  the authored opening curve. Omitting coarse rectangular cells leaves teeth
  hanging into the entrance; adding a timber strip in front leaves the feature
  reading as an attached canopy. The reveal, soffit and surface-following
  battens must form one continuous subtractive assembly.
- Use the enclosure supplier's counts and shape families as scale evidence.
  A façade documented as hundreds of unique four-, five- and six-sided units
  should not become a few oversized triangles or thousands of generic windows.
  Validate panel density, material ratio and joint continuity from street,
  front-corner and aerial cameras.

### Wave 8 registered-source + construction-zone lessons

- Keep the complete render-locked elevation as the identity and coordinate
  authority, but do not stretch that picture over a nonlinear shell, a long
  glulam beam, a deep arch soffit or a roof dome. Photographed openings and
  baked perspective become ghost windows and giant facade fragments on those
  solids.
- Give physical construction its own tile-safe, shadow-neutral PBR zones
  derived from the exact goalpost palette: perforated composite shell, glulam,
  louvers, honey limestone and dome stone. These are supporting materials, not
  a substitute for the registered elevation.
- Preserve reference-specific occupation separately. Clip a clean
  occupied-depth source to each real organic pane, station bay or pointed-arch
  opening, place it immediately behind physical glazing, and keep mullions,
  screens, reveals and masonry returns as independent shadow-casting geometry.
- Validate the separation from three cameras. Head-on proves opening and floor
  registration, a grazing close view proves material scale and real depth, and
  an aerial view proves that the shell, canopy or domes remain complete
  architecture rather than a hero-facing card.

### Wave 9 detached-house composition lessons

- A detached house is not a reduced apartment stack. Treat the reviewed
  whole-house GLB as a fixed residential landmark whose roof silhouette,
  threshold, entrance or porch, balconies or privacy screens, chimneys or
  towers and occupied window cavities form one composition.
- Roof and threshold usually carry more identity than extra facade ornament at
  this scale. Model cross gables, deep eaves, shingles or barrel tiles,
  clerestories, stone portals, benches and door recesses as connected
  construction with real returns and attachment logic.
- Residential windows must survive a close street view. Each opening needs a
  sill, frame or sash, physically shaded pane, curtain or privacy layer and
  recessed room depth; grilles, shutters and cedar screens remain separate
  shadow-casting geometry in front of that cavity.
- Use the render-locked elevation for exact front registration and
  reference-derived tile-safe materials for long sides, roof fields and
  construction solids. Do not stretch photographed windows, flowers, brick
  patches or lighting over secondary elevations.
- Accept ordinary hand-drawn footprint error by scaling the complete fixed
  house inside a conservative independent-axis band. For oversized targets,
  repeat complete ordinary residential bays in the fallback kit while the
  entrance, ends, cross gables, tower, chimney and roof logic remain fixed.
- Review detached houses head-on for opening alignment, from a front corner for
  privacy-screen and balcony depth, and from high oblique for every roof
  junction. A convincing front with blank side walls or an unresolved roof is
  not a finished family.
- Fine privacy screens must preserve screen-space gaps in the locked corner
  view. Recess occupied glazing and varied dark room depth behind individually
  modeled battens, retain a meaningful air gap, and avoid a density or albedo
  that optically fuses the screen into a pale solid wall.
- Exposed historic masonry is loss of finish, not ornament applied on top.
  Keep brick faces nearly flush or slightly recessed, build a shadowed mortar
  bed, break the perimeter and courses irregularly, and match the surrounding
  plaster age so the repair reads as construction revealed through stucco.

### Courtyard-ring roof junction + delivery-budget lessons

- Four perpendicular gabled bars do not become one courtyard roof merely by
  overlapping them or drawing diagonal valley beams. End-cap triangles remain
  visible as fins and the intersections read as crossed sheds.
- Stop each straight roof at its corner bay, omit the internal gable end caps,
  and close the junction with a real four-plane hip whose apex shares the
  adjoining ridge elevations. Keep the concave inner valley and convex exterior
  hip as separate construction lines while preserving the open courtyard void.
- Corner roof planes need the same true-scale tile or seam coordinates as the
  straight fields. Normalized filler UVs make otherwise correct hips read as
  smooth dark pyramids.
- Thousands of narrow reveals, frames, guards and wall strips can retain a
  visible one-segment construction chamfer. Spending a second bevel segment on
  every micro-part can exceed the city triangle budget without improving the
  locked street or aerial silhouette.
- Blender may defer the evaluated matrix after assigning a quaternion to the
  last procedural cylinder in a wing. Flush the view-layer dependency graph
  before composing wing transforms, or that final roof course or truss member
  can export vertically even when the rendered scene looks correct. Validate
  final on-disk bounds and the physical radius of gutters at the module origin.
- Recheck the street corner, aerial roof proof and interior courtyard together
  after every junction change. A roof correction is not accepted if it caps
  the open void, exposes a gable fin or removes the through-passage.

### Wave 11 continuous-curve + optical-layer lessons

- A curved opening can have the correct control points and still read as a
  staircase when its frame is assembled from many short beam chords. Build the
  stucco spandrel as one continuous face and the visible arch frame as one
  continuous ribbon with enough segments for the locked close view. Separate
  chord objects catch separate highlights and are not an acceptable final
  representation of a smooth architectural head.
- Curtain-wall materiality is a layered optical system. A vision-glass source
  may contribute subtle tint, roughness, normals and reflection variation, but
  it must not bake a second mullion grid or complete occupied scene onto every
  pane. Wash the outer base colour toward the approved neutral glass tint while
  retaining its custom non-colour PBR channels; place a separately registered,
  warmer occupied-depth source behind the pane and keep caps, spandrels and
  slabs as real geometry.
- A fixed landmark's native metric height includes every identity-bearing
  crown, roof lantern, photovoltaic rack, screen and mast. Compute and record
  bounds from the complete delivered assembly, not only the occupied shaft;
  camera proofs must include those same extents without clipping them.
- Thousands of repeated curtain-wall panes, caps and slab edges do not require
  thousands of context-dependent Blender operator calls. Directly construct
  their metric mesh vertices, faces and UVs, then preserve the same physical
  geometry, materials, semantics and close-view proof. Tooling overhead is not
  visual quality, and eliminating it keeps iterative comparison practical.
- A coherent multi-angle board must lock topology before skinning. For a tower
  cluster, preserve exact tower count, relative heights, bridge locations and
  crowns in every view; for a research campus, preserve wing count, open court,
  connectors, canopy plates, photovoltaics and service screens. Do not average
  incompatible views into a generic glass box.

### Wave 12 vegetation + real-void + load-path lessons

- A convincing planted building needs two coordinated representations. Soil,
  planter walls, trunks and branching structure remain physical geometry;
  labelled photoreal foliage cutouts can supply the fine crown silhouette that
  low-poly spheres cannot. Drive their transparency through an explicit alpha
  mix shader and glTF blend mode, use crossed vertical planes without a
  horizontal card, and inspect street, corner, aerial and mobile views for
  black rectangles or edge-on foliage loss.
- A portal is not an inset colour. Split every intersecting wing, facade skin
  and floor strip around the complete circulation volume. Build only the real
  jambs, curved spandrels, ceiling ribs, returns, passage paving and doors; the
  acceptance proof is an uninterrupted view and walkable path from the public
  forecourt into the court behind.
- Long-span identity is a connected load path, not a collection of nearby
  motifs. Derive roof nodes, tree-column branch endpoints and cable-stay
  endpoints from the same surface equation. Keep trunks outside the curtain
  wall, join each branch and stay to a visible canopy node, and carry the mast
  to a credible base. Prove the network head-on, from above and in a close
  structural view.
- Shared direct meshes make dense iteration practical, but a single normalized
  UV island must not stretch one ashlar course across a full tower pier. Split
  identity-bearing masses into coursed lifts or author physical-scale
  coordinates before export. Retain shared metric mesh instances for genuinely
  repeated parts and reject any close view where material scale follows object
  dimensions.
- Fixed landmarks and LEGO fallback kits can coexist. The complete landmark
  preserves the tower-and-court, planted-frame or mast-and-canopy composition;
  its bounded independent-axis scale band absorbs ordinary sketch error. A
  larger target repeats complete semantic bays through the normal planner path
  while keeping the entrance, ends, roof, crown and structural identity fixed.

### Wave 13 diverse structural-grammar + environmental-roof lessons

- Do not begin unrelated families from one universal facade scaffold. Identify
  the construction system that carries each goalpost first: continuous
  terra-cotta piers and setback shoulders for an Art Deco tower; timber
  post-and-beam, clay infill and open koshi lattice for a machiya; a continuous
  freestanding steel grid for a transparent pavilion; a glazed concourse below
  timber-louver floors for a station; or deep insulated larch reveals for a
  passive-house block. Repeat only complete bays written in that language.
- Lock roof direction and section against a front elevation and aerial before
  investing in tile, seam or environmental detail. The ridge, eave hierarchy,
  overhang and public/rear slopes are topology, not styling. Wrong ridge
  orientation makes an otherwise detailed machiya read as another building.
- Photovoltaic, sedum, tile, canopy and rooflight fields are physical roof
  assemblies. Give them metric coverage, supports or frames, edge clearance
  and a deliberate offset above their carrier plane; coplanar finish fields can
  disappear after glTF quantisation even when the Blender scene seems correct.
- Koshi lattice, timber louvers and exterior blinds need real screen-space
  gaps, an air cavity, physical glazing and registered occupied depth behind.
  Audit them from a grazing facade-close camera; a dark texture on an opaque
  panel or a screen fused to its pane cannot reproduce their materiality.
- Environmental systems that define the archetype remain part of both the
  fixed landmark and its semantic LEGO roof or crown kit. Oversized planning
  may repeat complete middle bays, but it must not stretch a photovoltaic
  field, duplicate a central entry or discard the reviewed roof logic.
- Transparent pavilions need one coherent interior volume behind the curtain
  wall. Do not place the same opaque occupied-room image immediately behind
  every pane. Keep the low-iron glass and pressure caps physical, continue
  floor and ceiling returns through the bay depth, and use sparse modeled
  furniture, partitions and lighting so adjacent panes reveal one open plan.
- Passive-house windows are wall sections, not facade pictures. Set the pane
  behind the insulation line; build full jamb, head and sill returns; keep the
  external blind, headbox and guide cables in front of the glass; then place a
  deep room shadow, selective occupation and curtains behind it. Vary those
  depth layers so a repeated bay does not repeat one photograph.
- Photovoltaic fields are arrays of standard-scale modules. Each module owns
  one complete, countable cell topology, a perimeter frame and real gaps to
  its neighbours; the field also owns continuous mounting rails and roof-edge
  clearance. Never stretch one PV image over an entire roof plane.

### Wave 14 sibling-variant + topology-lock lessons

- A catalogue sibling is an independent architectural contract, not a palette
  preset on the parent GLB. Lock its own four-view goalpost, footprint,
  silhouette, floor grouping, entrance, roof topology, material zones and
  glazing response before sharing any implementation helper.
- Parent ids may remain useful discovery aliases, but every catalogue variant
  and aesthetic id must resolve to the independently authored family on import.
  Preserve `source_variant_id` and `generation_archetype_id` on the fixed
  landmark and prove exact variant ids through the planner.
- Similar programs can require opposite construction systems. A white
  brise-soleil pavilion uses real open cells, pilotis and a recessed roof-garden
  room; an organic pavilion uses stone hearths, timber wall planes and one
  continuous shallow hip. Recolouring one scaffold cannot produce both.
- Rotated roof slabs are not a reliable final roof method. Gables, hips and
  rounded theater corners are closed connected mesh volumes with shared ridges,
  eaves and end faces; otherwise detached shards appear in export even when an
  individual camera disguises them.
- Screens and glass-block fields are counted construction. Calibrate their
  member spacing against the reference close view, preserve a real cavity and
  physical glass or occupied depth behind, and continue the system around the
  corners shown by the goalpost.
- The comparison sheet is a production gate. Place front, oblique, aerial,
  rear and material proofs beside the matching goalpost roles and correct the
  largest silhouette or topology mismatch before adding surface microdetail.

### Wave 15 program-topology + infrastructure lessons

- Program is often the silhouette. An inhabited energy plant needs one
  continuous skiable roof from public low point to process summit; a
  natatorium needs one shared roof equation for shell, ribs, masts and stays;
  a station needs an uninterrupted nave; and a silo complex needs transfer
  galleries that visibly connect real vessels and loading points.
- Treat those systems as routes or load paths before treating them as detail.
  Build their endpoints, landings, supports, edge protection and clearances at
  metric scale. Detached ramps, floating cables, unsupported galleries and
  ornamental stairs fail even when their colours match the reference.
- Non-orthogonal landmarks still need closed construction. Rolled titanium
  shells, folded concrete wings, barrel-vault market aisles and opposing
  bronze acoustic walls are continuous weathering volumes with thickness,
  returns, seams and drainage edges rather than flat cards or rotated boxes.
- Transparent civic halls reveal their program. Pool water, market stalls,
  station platforms, greenhouse crop decks and concert foyers should occupy a
  coherent depth behind physical glazing, with slabs, mullions and structural
  members continuing across adjacent panes.
- Preserve the reviewed landmark as an `assembled` module, then provide a
  semantic six-part fallback kit whose complete middle bays can absorb normal
  sketch error. Keep the 0.62–1.40 compatibility band and let oversized sites
  repeat whole bars along the long axis rather than stretching the landmark.
- Compare the model against the same front, oblique, rear and aerial roles used
  to lock the goalpost. Correct the largest program or silhouette mismatch
  first; material microdetail cannot repair a reversed station axis, a flat
  wave crest, an ungrounded tower or a market whose side arcades disappear.

### Wave 16 catalogue-conditioned RLASM review lessons

- Written prompts do not satisfy a reference lock. Pass the actual compatible
  catalogue images to the reference-generation operation, preserve their
  hashes and roles, and reject the generated sheet if it changes the program,
  storey count, footprint topology, roof directions, entrance or identity
  elements. The top or aerial source governs plan topology when the hero is
  visually ambiguous.
- Translate the locked views into an explicit architectural contract before
  building. For the roadside-motel pilot this meant one storey, a U-shaped
  motor court, two room wings joined by a rear cross-wing, an open road entry,
  an embedded front office, direct room access, paired windows, PTAC units,
  shallow roofs and a freestanding two-post pylon. Every item must survive in
  physical geometry and in the review views.
- A source crop is not automatically a construction texture. Audit every crop
  for perspective, baked shadows, seams and recognizable object fragments. If
  it cannot tile safely, retain it as provenance and author a clean
  source-derived orthographic specimen with explicit physical scale; prohibit
  projecting the oblique photograph onto the building. A generic procedural
  recipe remains diagnostic evidence, not a material pass.
- Review topology with dedicated cameras, not only the beauty render. Require
  an aerial view for footprint and roof direction, a court view for entrance
  and room rhythm, and a rear-oblique view for ridge, valley, gable and closure
  continuity. Dark faces are acceptable only when the evidence proves they are
  closed, shaded construction rather than holes.
- Identity infrastructure belongs to the architectural contract. Parking
  stalls must orient to the room doors and motor court; a pylon must be
  physically grounded, legible and present in the hero; and the office must be
  framed without clipping either the building or sign.
- Preserve each rejected iteration with its discrepancy ledger. Fix the
  largest silhouette, topology or material failure first, render the same
  mandatory views again, and promote only the reviewed evidence—not the whole
  experiment directory—to Git.
- “Builder review passed” and “keeper” are separate states. A phone-readable
  comparison must show authoritative source roles beside matching model views,
  state unresolved discrepancies, and remain explicitly not a keeper until an
  independent reviewer approves it.

### Wave 17 three-family source/model calibration lessons

- Reject prepared concepts that cannot name an exact catalogue archetype,
  variant and immutable compatible source set. Detailed prose is not an
  architectural source contract and must not enter the build queue.
- Use deterministic exact-pixel source boards when compatible multi-angle
  catalogue images already exist. They preserve evidence without introducing a
  second generative interpretation between the catalogue and the model.
- Author cameras per construction grammar before the first build. The framing
  must prove the complete silhouette, roof topology, rear/side envelope and one
  identity junction; a generic dimension-derived camera is not a review set.
- A technically complete physical envelope can still be an architectural
  failure. The Art Deco courthouse retained generic opening/spandrel hierarchy,
  the log lodge retained an over-broad roof and schematic secondary sides, and
  the Siheyuan retained weak lifted eaves and a flattened pavilion hierarchy.
  Phone source/model comparisons exposed these gaps more reliably than isolated
  full-resolution renders.
- Treat family identity as high-level construction, not a count of primitives.
  Civic setbacks need shoulder transitions and carved relief zones; lodge roofs
  need joined gables, coursed stone and visible timber joinery; Siheyuan roofs
  need lifted ceramic eave sections, gate caps and layered courtyard landscape.
- Review identity systems in several views together. A continuous chimney that
  terminates below the ridge, an existing cross-gable that reads as a detached
  triangle, or a real circular gate embedded in a blank wall is still a source
  mismatch.
- Do not call a pilot builder-approved when its phone comparison reveals obvious
  source-level hierarchy, proportion, material-depth or ornament-density gaps.
  Record the complete physical envelope separately from the failed architectural
  review and retain every rejected iteration as evidence.

### Wave 18 family-constructor correction lessons

- Schedule openings and structural piers independently. An Art Deco pier may
  dominate a bay, but it must land between occupied openings rather than
  bisecting a window. Treat every setback stage as an occupied, finished
  envelope and prove its windows and cap on secondary elevations.
- A closed triangular roof solid is not a safe public-gable constructor: its
  end cap can cover the timber gable field and become a detached shard inside
  intersecting roofs. Construct paired descending roof planes, a separate
  occupied gable wall, rakes, ridge and king post; check the rotation sign so
  each plane falls from ridge to supported eave.
- Roof intersection proof requires both aerial and rear-side views. An oblique
  hero can hide internal end caps, open valleys, rising eaves or disconnected
  connector roofs even when the facade looks plausible.
- Courtyard roof ridges inherit the roof material, stop inside the roof
  footprint and seat on the same lifted-corner mesh. Generic pale ridge rods,
  rods extending past their carriers and oversized gate-cap slabs are hard
  architectural failures, not finishing details.
- Identity parts must be judged as hierarchy, not mere presence. A physically
  continuous chimney, gate cap, entrance canopy or setback crown still fails
  if its scale, support or intersection contradicts the source composition.
- Preserve every failed constructor iteration, including mathematically wrong
  roof-plane tests. Promote only the rerendered correction that survives the
  full camera set and a deterministic 1080 × 1920 source/model phone board.
- `PASS_BUILDER_REVIEW_AWAITING_INDEPENDENT_APPROVAL` is not a keeper state. It
  records zero builder-visible blockers while explicitly reserving keeper
  promotion for an independent reviewer.

### Wave 19 source-specific material correction lessons

- A zero generic-fallback counter is not material evidence when the audit only
  checks material names or metadata. A shared noise, wave or brick recipe stays
  generic after it is renamed for limestone, timber, shingles or ceramic tile.
- Review dominant opaque roles visually in both a construction close-up and a
  phone source/model frame. Masonry, timber, shingles, ceramic tile, lacquer,
  metal and paving must remain distinct by pattern, joint behavior, palette,
  roughness and physical scale.
- Record immutable hashes for every source-derived material specimen used by a
  reviewed candidate. Specimens must be orthographic, shadow-neutral,
  role-atomic, edge-safe and free of windows, doors or other facade fragments;
  map them to physical geometry rather than using facade-photo projection.
- Normalized object-local coordinates can change construction scale on every
  repeated block. Use a shared world-scale mapping with an explicit tile size
  in metres for continuous masonry and paving, then inspect chimney shafts,
  corner blocks, porch piers and courtyard slabs in the same frame.
- Preserve rejected material diagnostics. Dark flat courthouse coursing,
  vertically striped Siheyuan walls, printed roof grids, oversized paving and
  distorted lodge fieldstone explain why the material gate exists and prevent
  the same procedural shortcut from returning.
- A flat source-calibrated PBR material remains valid for inherently smooth
  glass, occupied depth and small metal trim. It cannot substitute for
  identity-bearing stone, logs, shingles, brick, roof tile or paving.
- Rescind a builder pass when later review exposes a material false positive.
  Geometry and constructor lessons may remain valid, but keeper candidacy must
  move back to rework until the corrected GLB is rerendered and reviewed.

### Wave 20 registered-identity binding lessons

- Role-atomic stone, timber, shingle, brick, tile, lacquer and paving specimens
  are supporting construction assets. They do not reproduce a selected
  building's bay hierarchy, relief zoning, opening cadence or joinery. Bind a
  dedicated orthographic render-locked identity source to every principal
  facade or other identity-bearing semantic surface.
- Preserve the complete source recipe: exact compatible catalogue inputs and
  hashes, raw generated output, exact prompt, provider/output record, masking
  operations, registered derivative and intended model datum. Recreating the
  approved source must not depend on chat history.
- Register identity only to matching physical construction. The elevation can
  carry surface identity, but the model still owns silhouette, openings,
  recesses, returns, roofs, supports and circulation. A large image plane that
  hides incorrect massing or unfinished secondary elevations is a hard fail.
- Give each feature one visual owner. Clear source pixels where physical
  geometry owns a flagpole, chimney, gate aperture, canopy, pane or other
  silhouette/depth feature. Duplicate ownership creates ghost geometry;
  incomplete alpha cleanup creates pale or dark edge halos.
- Continue the source grammar around side and rear elevations. A registered
  front paired with generic punched windows, blank returns, black carrier
  voids or open roof junctions remains an architectural mismatch.
- Glazing, paper screens and lattice are wall sections: perimeter frame,
  recessed pane or paper, occupied reveal and physical depth. Require a
  dedicated glass-close camera alongside matched front, 60-degree oblique,
  aerial/topology, rear-side, facade-close and family-junction views.
- The courthouse, lodge and Siheyuan correction showed the proper fix order:
  rebuild identity massing and topology first; register the exact source;
  correct feature ownership and alpha edges; finish secondary construction;
  then tune physical-scale supporting materials and neutral review lighting.
- A build may report one registered identity surface, zero generic fallbacks,
  zero declared floating contacts and a complete camera set while still
  failing visible comparison. Never convert builder metadata into keeper
  approval; preserve rejected versions and require a separate reviewer to pass
  the corrected on-disk GLB with zero P0 blockers.

### Wave 21 optical wall-section and carrier lessons

- Audit every opening from exterior to interior: physical wall or cut-log face,
  jamb/head/sill return, inner sash or lattice, pane or paper, then a separately
  offset occupied-room plane and short room sidewalls. A deep decorative box
  projecting outside the wall is not a recess.
- The structural carrier must terminate behind the room datum. Compose
  perforated masonry skins over inset cores, split round-log courses at the
  audited jamb clearance, and pull courtyard hall carriers behind translucent
  paper screens. Alpha cannot reveal a room when solid mass still fills the
  cavity.
- Match the proof camera to the relationship. A slightly oblique glass close
  must visibly separate wall return, screen, optical layer and occupied depth;
  object names, non-zero transmission and declared offsets are not evidence.
- Keep glass nearly non-emissive and paper diffusive. Put restrained warmth on
  the recessed room plane, and tune transmission only far enough to reveal the
  physical separation. Uniform dark, grey, cream, amber or glowing rectangles
  still fail the optical wall-section gate.
- Run a local pixel gate before independent review. If the wall, pane or paper,
  and occupied layer cannot be pointed to separately, preserve the bounded
  revision as rejected and correct the constructor first.
- Prove every carrier-material replacement in rear-side and aerial views.
  Family-specific grey masonry plus red timber is a valid Siheyuan envelope;
  a flat orange depth carrier is not, even when hidden from the hero view.
- Courthouse v20, lodge v25 and Siheyuan v18 independently passed only after
  these relationships were visible across their complete source-locked camera
  sets with zero P0 blockers. That independent pixel comparison, not the
  builder counters, is the keeper boundary.

### RLASM v5 new-family constructor lessons

The Victorian station, Rationalist hospital and Second Empire fire-station
proof batch established four reusable rules:

- A coursed material owns a surface role and mapping axis. Register front/rear
  masonry in X-Z, side masonry in Y-Z and sloped roofs separately. Record the
  physical course size; a correct palette with toy-scale blocks still fails.
- If a long boolean chain hides windows or leaves embossed outlines, stop
  extending the solid carrier. Assemble the facade from physical piers and
  spandrels around the audited opening schedule and terminate the core behind
  the occupied-room datum.
- Inspect the registered derivative before construction. A valid hash does not
  excuse adjacent perspective facade, shadows or unrelated roles in a clock,
  crest or material-panel crop.
- Re-audit camera targets after every bay change and build the matched phone
  board before builder approval. Phone-scale source/model agreement is a local
  gate; independent zero-P0 review is still required for keeper promotion.

### RLASM v5 station-type and inhabited-envelope lessons

The Victorian station rebuild established that matching a category label is
not matching an archetype. A barrel roof, brick strip and clock can still form
the wrong building type, and a correct transparent shell can still expose an
empty non-building.

- Solve width, depth, rise, headhouse height, tower offset and frontage depth
  from the locked front, oblique and top views.
- Construct the continuous enclosed vault, bounded glazed ends, repeated
  trusses, purlins, side arcades and the low asymmetrical headhouse in the
  source hierarchy.
- Make source-material enrollment fail closed. A new revision omitted from an
  exact-material allowlist must not silently receive a procedural shader whose
  metadata happens to report zero generic fallbacks.
- Treat program visible through glass as primary architecture. Build physical
  ballast, sleepers, paired rails, raised platforms, supported canopies,
  source-backed furniture and circulation.
- Connect the transparent hall to its opaque headhouse with an interior
  concourse opening schedule; a blank rear carrier is a hard failure.
- Galleries require supports, guard rails and connected stairs. Require both a
  platform-oblique and track-axis render in addition to the exterior set.
- Source-condition oblique clocks into bounded orthographic identities with
  preserved prompts and hashes, mounted only on matching physical datums.

### RLASM v5 building-level material-family authority

A source-specific material sheet per semantic role is not sufficient when the
roles represent one physical substance. The Second Empire fire-station
material pass established this executable gate:

- Record one bounded, user-approved material-bearing reference as the
  chromatic and finish authority when appropriate, and preserve its hash.
- Give every same-substance exterior role one machine-readable family ID:
  wall/core, façade and side/rear skins, returns, quoins, arches, strings,
  cornices, dormers, masonry attachments, columns and identity carrier.
- Preserve role-specific morphology and construction scale. Coursed, dressed
  and carved variants may change joints, relief, roughness and restrained value
  while sharing hue, aging and mineral character.
- Do not force genuinely different materials into the family. Slate, timber,
  copper, iron and glass keep their source-locked identities.
- If no existing ornament-free sheet matches the authority, generate a
  shadow-neutral seamless material-only specimen and preserve input hash,
  exact prompt, output hash and bytes.
- Verify front, both sides, rear, aerial, façade close and glass close beside
  the authority on a phone board. Whole-envelope views run grade-to-finial.
- Preserve partial revisions. V18 advanced only after independent review
  recorded zero P0 blockers.

### RLASM v5 roof-mounted opening contact section

A dormer may contain source-specific materials, a sash, glass, and occupied
depth while remaining physically detached from its roof. A second failure can
appear after integration when an inherited Boolean cutter is shallower than
the thickened dormer body and leaves an opaque exterior skin over the window.

- Derive the opening datum from the constructed sloped roof plane.
- Make the lower dormer cheeks cross that plane and close the gable/end field.
- Size the cutter against the complete opaque body depth, not an earlier wall.
- Inspect the raw cut, then build the material-matched return, recessed sash,
  optical pane, and separately offset occupied room layer.
- Seat and bound the roof cap and assign flashing/apron ownership at the joint.
- Require complete left/right elevations, aerial, and an oblique contact close
  that proves roof penetration and opening depth in the same pixels.
- Preserve floating and partial-cut candidates and advance a bounded revision.

Fire-station v20 passed this gate with zero independent P0 blockers.

### RLASM v6 integrated authority and review scope

The accumulated station, courthouse, lodge, Siheyuan, and fire-station work
showed that quality is the visible correctness of relationships: source to
topology, wall to opening, roof to dormer, material to substance, transparent
shell to program, and evidence to review claim. Object names, hashes, counts,
and passing Booleans support an audit but never override pixels.

- `docs/RLASM_LATEST_METHOD.md` and
  `tools/archetype_compiler/rlasm_method.json` are the single current human and
  executable RLASM authorities.
- A production expert may produce a builder pass. An independent verifier must
  perform the keeper review; the same role never builds and self-approves.
- A scoped material, contact, glazing, or identity review closes only its named
  category. It must not emit `keeper_approved`.
- Keeper promotion requires a holistic source-locked adversarial regression of
  every mandatory full-resolution render and phone board with zero unresolved
  P0 and P1 blockers.
- New visual evidence can demote or supersede an earlier keeper. Preserve the
  previous record and explain the supersession instead of rewriting history.
- `high_quality_ready` from the general family assessor is not RLASM keeper
  approval. Use the dedicated RLASM contract and keeper registry.
- Corrections are finite and blocker-bounded, but there is no arbitrary maximum
  number of attempts. Never overwrite a prior candidate or start an open-ended
  unattended loop.

## Updating this memory

When a pilot reveals a reusable lesson:

1. fix the generator or kit;
2. add the symptom, cause and correction to the JSON memory;
3. add or tighten an automated gate where the lesson is machine-testable;
4. add a regression test;
5. increment `memory_version`;
6. regenerate one approved representative before scaling the change.

Do not encode one building's ornament as a universal rule. Store universal construction principles in this memory, family identity in `architectural_signature_profiles.json`, and variant-specific dimensions/reference roles in the catalogue or massing graph.
