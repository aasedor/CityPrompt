# High-Quality 3D Building Production Memory

This is the persistent production memory for turning City Prompt archetypes and variants into high-quality modular GLB families. It captures the construction rules established through the Kinnaird, Chicago, Gothic, glass, Nordic, industrial and Parisian pilots.

The memory has two forms:

- this document explains the decisions to people;
- [`high_quality_building_memory.json`](../tools/archetype_compiler/high_quality_building_memory.json) gives the batch pipeline versioned, executable gates.

The assessor is [`quality_memory.py`](../tools/archetype_compiler/quality_memory.py). `generate_worldclass_library.py` records its result for every generated family, so a batch can continue while only questionable outputs enter a review queue.

Current executable memory: `2026-07-20-dark-frame-office-renderlock-v71`.

## The quality target

The target is Kinnaird-class architectural identity in a modular real-time asset, not a literal photogrammetric reconstruction. A successful family must read correctly at three distances:

1. **Block scale:** massing, setbacks, roofline, corner condition and base-middle-crown hierarchy match the archetype.
2. **Building scale:** entrances, balconies, bays, dormers, cornices, towers and other signature projections create the correct silhouette and shadows.
3. **Facade scale:** materials, glazing, joints, returns, interiors and restrained variation withstand close inspection.

A texture can supply surface richness. It cannot repair incorrect massing, missing corners, unsupported projections or a generic roof.

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

The close-range atlas is normally 4K and must be at least 2K. A compressed 1K-or-smaller LOD serves city scale. The albedo must not contain directional sunlight or cast shadows; City Prompt owns illumination.

Gemini and GPT Image are interchangeable source providers. Provider choice is recorded as provenance, while rectification, PBR derivation, assembly and validation remain identical.

### 5. Build glazing as a layered assembly

At close range, a window is not a blue plane. It contains:

1. a wall opening or visible recess;
2. stone, brick, metal or timber returns;
3. a frame with believable profile depth;
4. a recessed physical-transmission pane;
5. a warm interior backplate or shallow room card;
6. restrained reflection from the environment.

For close City Prompt views, the semantic opening bounds also register a slim
physical sash at the pane plane. Mullions and transoms must be real geometry
when they establish the archetype's construction rhythm (especially industrial
Crittall, punched heritage sash and curtain-wall caps). Do not add a second
heavy perimeter over an audited facade sheet: let the atlas supply fine colour
and weathering while narrow physical bars, returns and sills supply parallax,
contact shadow and grazing-angle depth.

At city distance, the semantic glass mask and baked facade replace most of that geometry. Visible windows default to subtly occupied warm interiors; uniform dark-blue glass is avoided.

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
- Use true world-coordinate tile clipping when there is one replacement footprint. A projected stencil volume can erase photogrammetry that merely sits behind the proposal, producing pale wedges around an otherwise realistic model.
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

## Updating this memory

When a pilot reveals a reusable lesson:

1. fix the generator or kit;
2. add the symptom, cause and correction to the JSON memory;
3. add or tighten an automated gate where the lesson is machine-testable;
4. add a regression test;
5. increment `memory_version`;
6. regenerate one approved representative before scaling the change.

Do not encode one building's ornament as a universal rule. Store universal construction principles in this memory, family identity in `architectural_signature_profiles.json`, and variant-specific dimensions/reference roles in the catalogue or massing graph.
