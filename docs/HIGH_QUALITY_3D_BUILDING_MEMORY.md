# High-Quality 3D Building Production Memory

This is the persistent production memory for turning City Prompt archetypes and variants into high-quality modular GLB families. It captures the construction rules established through the Kinnaird, Chicago, Gothic, glass, Nordic, industrial and Parisian pilots.

The memory has two forms:

- this document explains the decisions to people;
- [`high_quality_building_memory.json`](../tools/archetype_compiler/high_quality_building_memory.json) gives the batch pipeline versioned, executable gates.

The assessor is [`quality_memory.py`](../tools/archetype_compiler/quality_memory.py). `generate_worldclass_library.py` records its result for every generated family, so a batch can continue while only questionable outputs enter a review queue.

Current executable memory: `2026-08-09-contour-registered-void-v89`.

The current calibration set and catalogue rollout rationale are documented in
[`BUILDING_GOLD_SET_PIPELINE_SYNTHESIS_2026-08-07.md`](BUILDING_GOLD_SET_PIPELINE_SYNTHESIS_2026-08-07.md).

## The quality target

The target is Kinnaird-class architectural identity in a modular real-time asset, not a literal photogrammetric reconstruction. A successful family must read correctly at three distances:

1. **Block scale:** massing, setbacks, roofline, corner condition and base-middle-crown hierarchy match the archetype.
2. **Building scale:** entrances, balconies, bays, dormers, cornices, towers and other signature projections create the correct silhouette and shadows.
3. **Facade scale:** materials, glazing, joints, returns, interiors and restrained variation withstand close inspection.

A texture can supply surface richness. It cannot repair incorrect massing, missing corners, unsupported projections or a generic roof.

## v66 fidelity refinement

The second three-pilot pass adds three rules to the production pipeline:

- **Curved identity must be curve-native.** Rounded pavilions can use faceted
  surface cards, but their balcony slabs, rails, supports and skyline must
  continue around the curve as authored geometry. Straight balcony runs that
  stop at the tangent points break the archetype silhouette.
- **Every family gets the complete camera suite.** `archetype_match`, street,
  front-corner, rear-corner, aerial, facade-close and context renders are now
  generated in the bounded pilot rather than inferred from one hero image.
- **Reference materials are intrinsic-first.** Before producing PBR channels,
  separate material appearance from source illumination and record confidence
  for uncertain regions. Luminance-derived normal, roughness or depth maps are
  fallback-only because they preserve baked shadows and highlights.

The Paris pilot applies the first rule with continuous curved balcony datums
and a bulbous zinc dome. The Art Deco pilot adds a physically framed ceremonial
portal and eight authored lantern faces. The machiya removes an unrelated pale
larch texture from its fixed dark-timber structure.

## Four-family gold-set contract

Victorian Second Empire, Classic Haussmann, Classic Eixample and the corrected
Perpendicular Gothic Chapel are the current visual calibration set. They prove
two valid production identity modes:

- `semantic_stack` for an archetype whose authentic form is a regular
  streetwall, provided the base, entrance, ends, datums, crown and roof are
  fixed and only ordinary middle bays repeat;
- `massing_graph` where plan, silhouette or section carries identity, such as
  the Eixample chamfer or the chapel lantern and terminal towers.

Every production family must declare one of these modes. The catalogue exporter
must resolve a specific variant and record street, oblique and roof/aerial
reference roles. `production_preflight.json` must pass before facade-image or
Blender generation. After generation, structural validation is insufficient:
`visual_approval.json` must explicitly approve block, building, facade and
orbit/context comparisons before `high_quality_ready` can become true.

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

### V69 vernacular opening audit

The Swiss Alpine chalet pilot exposed a particularly costly false-positive
case. Automatic segmentation classified weathered timber grain, painted
Luftlmalerei motifs, flower-box shadows and fieldstone joints as glazing. The
first generated module exceeded 230,000 triangles and wrapped large false
frames around decorative facade regions.

For irregular vernacular elevations, the opening schedule is therefore a
pre-render requirement rather than a later refinement. The chalet's fourteen
actual sash-glass rectangles reduced the repeatable module to roughly 29,000
triangles while preserving the timber, murals and stone as albedo. Decorative
pixels never authorize physical panes, jambs or mullions. An automatic mask may
remain texture evidence, but only audited openings become construction.

This pilot also confirms why silhouette measurement remains independent of
material quality. Its stone/timber facade and fixed chalet details read well,
yet the first OpenCV pass rejected the overall aspect ratio because the
archetype photo describes a broader composition than the compact 14 by 12 metre
default. Rebuilding at the catalogue's declared 18 metre maximum frontage moved
the silhouette IoU from 0.574 to 0.713 and passed the unchanged aspect and
roofline gates. The conflict was resolved as an explicit native size-tier
decision rather than hidden by loosening thresholds.

### V70 pitched-roof construction detail

The Alpine chalet roof-detail iteration established that a correct gable prism
is only the massing layer. At hero and aerial range, broad unbroken roof planes
still read as procedural unless the covering, edge and retention systems have
construction scale.

The reusable `pitched_roof_surface_detail` assembly now adds overlapping
shingle or stone-slab courses as one consolidated disconnected mesh, rather
than hundreds of Blender objects. Sparse low-poly ballast stones remain
separate because their silhouettes and contact shadows are identity-bearing.
Ridge caps, valley/drainage lines, gutters and timber verges finish the roof
section. The chalet uses dark shingle fields on the main roof and warmer stone
slabs on the projecting cross-gables, matching the distinct systems visible in
the aerial references.

The detailed v70 hero remains below the 180,000-triangle ceiling at 102,252
triangles and passes the structural and camera-locked fidelity gates. Surface
detail therefore belongs in the near/hero LOD; district and map LODs retain the
base roof silhouette, material separation and major ridge lines while baking or
removing individual courses and ballast.

### V71 complete-category rollout

The first bounded category rollout completed all eight Mountain / Alpine
catalogue variants: four detached chalets and four mixed-use lodges. The batch
reused construction kits, not a universal shape. Every variant received its own
signature graph, exact three-view provenance, orthographic facade source,
audited opening schedule, two-axis band schedule and camera-locked fidelity
contract.

The category pass added five operational rules:

- Treat category completion as a finite variant registry. A parent label is not
  permission to share a sibling facade, footprint or roof.
- Crop rectangular facade skins to the wall body only. Isolation background,
  sky, roof slopes and shaped gables create white panels when they enter a
  repeatable elevation crop.
- Add physical curtain walls only when they are registered to the authored
  facade. A generic glass cage can hide a strong atlas; when exact registration
  is unavailable, keep the atlas and add only the reference-proven structural
  frame.
- Derive ridge direction, cross-gables, valleys, planted-roof drainage and PV
  layout from the oblique and 90-degree references. The catalogue roof label is
  not a construction drawing.
- Match the OpenCV contract to the closest compatible generated camera. The
  eco-passive lodge correctly failed under an oblique hero view but passed at
  the street camera after its overly broad generic envelope was narrowed to its
  native 19 by 15 metre proportion.

All eight final families pass structural validation and the silhouette gate.
The resulting set deliberately preserves distinct identities: weighted Swiss
cross-gables, compact Austrian larch and zinc, painted Bavarian balconies, a
stone-and-turf Berghaus, a glazed glulam hall, a Tyrolean shop-house, a
cross-gabled stone/log lodge and a planted butterfly roof with U-shaped PV.
The review package pairs exact catalogue images with the generated identity and
roof views so human approval can still identify ornament or secondary-plan work
that silhouette metrics cannot see.

### V72 landmark-section and paired-evidence pilot

The Calgary catalogue library pilot deliberately selected an archetype whose
local images conflict with its prose metadata. The images show a rectilinear
brick civic perimeter block with a giant timber entrance shell and occupied
roof court; the prose describes the real faceted New Central Library. For an
exact-variant asset, the declared street, oblique and roof images are the
construction goalposts. Text remains discovery context but cannot overrule
visible plan, section, material and silhouette evidence.

The first civic pass also proved that a landmark void cannot be represented as
a facade motif or a flat arch ring. The reusable `timber_arch_shell` assembly
samples independent front and back arch sections to create a true flare, then
adds nested laminated layers and a recessed glazed back plane. Projection is
kept inside the exported footprint allowance; the surrounding plaza belongs to
placement context rather than the building GLB.

V72 replaces the one-camera regression gate with
`building-reference-evidence@2`. It wraps the existing OpenCV silhouette
metrics but requires multiple named roles. A context-free `roof_audit` camera
isolates roof occupancy, courts and equipment from neighbouring review blocks.
The first roof audit rejected the library's 1.50:1 court even though its facade
looked convincing. Thickening the side wings changed the court to 1.30:1 and
the unchanged roof comparison then passed at IoU 0.813 with 0.013 aspect error.
The street role passes at IoU 0.706, but its 0.501 aspect error is explicitly
retained as a camera-calibration weakness rather than hidden in the mean score.

Operational rules from this pilot:

- When catalogue prose and exact variant images disagree, record the conflict
  and build from the images selected by the UI.
- Model identity-bearing voids as sections with depth, flare, inner surfaces
  and an inhabited back plane; a decal or flat trim is insufficient.
- Separate site/plaza geometry from the asset envelope before structural
  validation. Recreate it in placement or public-realm context.
- Require a context-free plan/roof audit in addition to the presentation
  aerial. A beautiful context render is not a segmentation-safe QA input.
- Gate each reference role independently. Never average a failed roof plan
  into a passing facade score.
- Store camera distance and obliqueness in the signature profile when the
  default review rig does not match the reference's field of view.

### V65 three-pilot expansion lessons

The rounded Parisian corner, cream terra-cotta Art Deco tower and restored
machiya pilots extended the gold-set method across three very different scales:

- A curved or faceted corner needs the same floor-accurate podium, middle and
  crown bands as an orthogonal streetwall. Angled facade skins must therefore
  support full vertical band stacks; one stretched elevation on the corner
  creates a blank drum or an implausibly tall window.
- A setback tower is one family of repeatable floor bands distributed through
  several fixed shaft tiers. Repeat the audited floor band vertically inside
  each tier, keep each setback/cap/crown fixed, and preserve one common bay
  phase rather than stretching a single facade image over the full tower.
- Geometry-first massing is necessary but not sufficient. The first Art Deco
  pass had the correct ziggurat silhouette yet read as a generic glass office
  until the reference-locked terra-cotta floor rhythm was restored.
- A low-rise semantic stack can outperform a bespoke graph when its catalogue
  grammar already preserves the decisive roof, deep eaves, lattice and
  threshold. Promote it to a graph only if multi-view review shows the plan or
  section is still wrong.
- Pilot outputs remain review-only. The Parisian needs a continuous curved
  balcony, the Art Deco crown needs more authored relief, and the machiya needs
  a frontage/orientation check before any of them joins the calibration set.

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

### V67 exact-variant facade lock lessons

The three-archetype expansion caught a failure that structural validation did
not: a Scottish Baronial graph rendered with the older Chateauesque family
atlas. The object was technically complete but visibly belonged to a different
building. Treat facade imagery as variant identity, not family styling.

- Resolve the exact selected variant before making or reusing a facade sheet.
  A sibling may inherit graph structure, but never a parent or sibling photo
  atlas unless the references are demonstrably the same building target.
- Generate a clean orthographic elevation from the selected archetype and keep
  its prompt/reference provenance. Audit normalized storey and side-bay crops
  before they become modular bands.
- Repeatable wall skins contain ordinary wall and opening cadence only. Remove
  sky, isolation background, roofs, shaped gables, towers and turrets from the
  rectangular identity crop; those silhouette cues remain fixed geometry.
- A passing GLB/extent report does not promote the pilot. In this run the civic
  portico was strong, the Jacobethan quadrangle required centre-bay revision,
  and the Scottish hotel remained a visual failure because its turret/return
  construction and tower hierarchy diverged in oblique view.

### V68 camera-locked fidelity and plan reconstruction lessons

The Scottish Baronial rebuild added a no-install OpenCV measurement stage and
used the existing Blender compiler to replace the inherited solid hotel core
with a reference-derived perimeter quadrangle.

- Measure the exact presentation camera, not an arbitrary crop. Normalize the
  audited reference outline and extracted render silhouette, then record
  silhouette intersection-over-union, roofline error and aspect-ratio error in
  a versioned contract. This is a cheap regression gate before human review.
- A high silhouette score is not proof of archetype likeness. The failed v67
  model scored 0.901 because its outer boundary resembled the reference even
  though its gate tower hierarchy and plan were wrong. The reconstructed v68
  model scored 0.891 while materially improving the quadrangle, centered gate
  tower, stepped gables and turret distribution.
- Treat aerial and roof-plan references as construction evidence. The open
  quadrangle must be separate front, side and rear wings in the graph; a void
  entry beside a solid core is documentation, not geometry.
- Do not add physical window kits merely because a fixed turret or tower can
  accept them. If the tangent, recess and material registration are not
  visually proven, the result can be pale floating panels over a good atlas.
  Remove the duplicate assembly or author an audited local opening schedule.
- Keep the result review-only when the primary massing improves but secondary
  ornament remains simplified. V68 establishes the right reconstruction
  method; it does not promote the Scottish pilot into the four-family gold set.

### V73 large-span shell and isolated-audit lessons

The Parametric Wave-Shell Natatorium extends the image-locked graph method to a
building whose identity is almost entirely plan and section rather than a
rectangular facade.

- Generate a large-span shell as a closed sampled assembly with an outer skin,
  separate soffit and sealed perimeter. Modulate plan width and longitudinal
  crest height explicitly so the building remains asymmetric and wave-like in
  the street, oblique and top-down views.
- Panel grids on double-curved roofs are construction evidence, not texture.
  Build a bounded consolidated seam mesh on the sampled surface; avoid hundreds
  of detached rods and never flatten the quilt rhythm into a planar decal.
- Curved glazed end walls follow the same analytic roof section. Their glass,
  perimeter arch, mullions and transoms are physical geometry, while generated
  orthographic imagery is restricted to material and glazing character.
- Structural masts, stays and cables must connect declared 3D endpoints. Thin
  arbitrary members are reusable, but coincident endpoints and unbounded cable
  fans fail immediately.
- A roof audit is context-free only when every presentation mesh other than the
  building is hidden. Removing neighbouring blocks while leaving roads, ground,
  trees and cars still contaminates OpenCV segmentation.
- Preserve catalogue clear-height truth for natatoria, hangars and civic halls.
  One 8-18 m internal level is valid even though ordinary stacked floors remain
  much lower; the landmark graph owns the final section.
- Passing silhouette evidence does not prove material realism. V73 passes the
  street and roof gates, but its cool curtain wall and simplified occupied
  interior remain review findings for a later optical/material pass.

### V77 material-continuity and executable-void lessons

The Scottish Baronial material/void pass exposed two cases where the catalogue
metadata was already correct but the renderer did not enforce it. The selected
variant described rusticated pink-grey granite, dark grey natural slate and a
deeply recessed porte-cochere. Those phrases now compile into generation gates
instead of remaining prompt prose.

- Large fixed assemblies declare material slots. Turret drums, shaped gables
  and crenellations must inherit the facade's granite texture family, while
  turret caps and roof planes must resolve the variant's Welsh-slate family.
  Both preflight and Blender runtime fail if a required texture key is absent,
  points at a mismatched family or cannot be found in the selected library.
- Material overrides merge deliberately. A variant colour correction may tint
  a shared intrinsic texture, but it may not silently erase the texture key or
  retain an incompatible parent material such as copper after changing only
  the roof colour.
- Semantic voids are executable construction. A passage names its target mass,
  shape, direction and minimum depth; the gate node builds around that volume,
  the portal omits its back plane and every crossing facade skin declares an
  opening clearance.
- Metadata is useful when it is traceable and subordinate to the images. The
  quality report records which catalogue phrases justified each contract, but
  visible street, oblique and aerial evidence remains the authority whenever
  the prose conflicts with the selected variant.
- These gates prevent known technical regressions; they do not prove visual
  likeness. The v77 granite tint is still too uniform on some turret drums, and
  the roof topology still needs reference-accurate dormers, intersecting
  gables, ridge/valley work and the correct tower hierarchy before promotion.

### V78 bounded five-building recipe and atlas-congruence lessons

The five-building expansion applied the material/void contract to Arts and
Crafts, Neoclassical courthouse, Italian portici, Romanesque warehouse and
Scandinavian courtyard archetypes. It produced three keeper pilots and two
provisional pilots, which is the correct outcome for a bounded learning run:
technical completion did not erase visible exact-variant differences.

- Store exact-variant construction decisions as compact deterministic recipes,
  then expand them into ordinary `massing-graph@1` nodes, voids and assemblies
  before preflight. This keeps five related pilots reviewable without weakening
  the renderer-level graph contract or copying thousands of JSON lines.
- A depth-bearing opening primitive may construct one entry or a counted run of
  round/rectangular arches. The recipe owns pier spacing, heads, jambs, reveal
  depth, back wall or through mode, and one facade-skin clearance per opening.
  A single semantic void beside five flat arch decals does not pass.
- Image-confirmed catalogue metadata can select bounded construction facts:
  number of storeys, ridge axis, hip height, roof texture family, passage depth
  and material slots. The image remains authoritative when prose and visible
  colour or topology differ.
- Exact-variant atlas congruence is a human and provenance gate. The first
  courthouse attempt paired Art Deco metadata with a Neoclassical family atlas;
  it was rejected and rebuilt against the matching Neoclassical variant rather
  than published as a polished sibling mismatch.
- Luminance-aware atlas tinting is only a bounded fallback. It can reconcile a
  reusable wall's hue while preserving dark glazing, but it cannot turn brick
  joints into smooth plaster, rectangular sash into leaded casements, or add
  dormers and projecting balconies. Arts and Crafts and Scandinavian remain
  provisional until exact-variant facade sources and fixed detail kits exist.
- Publish a named visual status beside every passing report. In v78 the
  courthouse, portici and Romanesque warehouse are keeper pilots; Arts and
  Crafts and Scandinavian are provisional. None enters catalogue release until
  the normal human visual-approval gate is signed.

### V79 image authority and selective-metadata lessons

Catalogue prose is optional evidence, not a design brief. The exact selected
reference images remain the construction authority for silhouette, proportion,
roof topology, visible colour, openings and assembly hierarchy.

- Admit metadata field by field. Every selected field records its exact dotted
  source path, the bounded construction purpose it serves and an explicit
  confirmation that it agrees with the selected images.
- Ignore generic parent `styleProfile` and `renderPrompt` prose when an exact
  variant field exists or when the prose contradicts the selected image set.
  A famous-building description cannot overrule the catalogue variant.
- A useful portion of a field may be narrower than the prose. For the Arts and
  Crafts pilot, `hand-cut clay tiles` may establish covering scale and overlap,
  while the reference image still owns the visible green roof colour.
- Metadata may be disabled entirely. A selective or disabled policy must not
  leak unselected prose into the production contract's traceable cues.
- This gate is opt-in for legacy compatibility. Every new image-locked pilot
  and catalogue expansion should declare it before paid or heavyweight work.

### V80 image-measured feature-schedule lessons

Looking at the right images is not enough. Before Blender, the selected street,
oblique and roof views must become an explicit, executable feature schedule.

- Record the visible storey count, wall and ridge datums, opening count and
  positions, roof axes and intersections, material zones, and real spatial
  voids. Each measurement names the graph node, assembly or void it drives.
- Production preflight verifies that every required reference role is present,
  measurements are well formed, and the named graph topology exists. This
  prevents an image cue from being written into a report but omitted from the
  build.
- Keep opening schedules elevation-specific. Exact front sash rhythm must not
  be repeated blindly across side and rear walls; sparse party-wall and service
  elevations are part of the archetype identity.
- Construct a roof as a plan graph, not a text label. Ridge axes, cross aisles,
  clerestories, surface covering and edge systems are independent requirements
  checked from the aerial reference and a context-free roof-audit camera.
- A public opening needs both foreground construction and a believable depth
  termination. Pair arches, columns or reveals with a recessed occupied
  backdrop so the space reads as a tunnel, market bay or inhabited entrance
  rather than a dark or brick-painted rectangle.
- Learned depth, camera and point-cloud models such as MoGe, Depth Anything or
  VGGT remain confidence-scored advisory evidence. They can expose curvature,
  overhang and plan uncertainty, but noisy single-view mesh output does not
  replace architecturally authored topology.
- Machine gates catch omissions; side-by-side human comparison catches
  perceptual mistakes. The Amsterdam pilot passed topology checks before human
  review identified an extra storey and the wrong roof value, so visual keeper
  status remains independent of validation success.

### V81 occupied-opening detail lessons

Correct massing and real void depth can still look visually empty when the
archetype depends on activity at the public edge. Occupation is a bounded
assembly layer attached to validated openings, not a substitute for them.

- Heritage doors split into an inset timber leaf, shallow panel relief and a
  separately framed glazed fanlight. This prevents a correctly sized entrance
  from reading as one black placeholder slab.
- Open market bays retain their columns, void volume and recessed interior
  termination, then receive low-cost counters, crate groups, goods and warm
  task lights at the exact scheduled bay positions.
- Structural articulation continues through occupied frontage. Brick piers
  rise through the contrasting market header instead of stopping below it, so
  the bay rhythm reads at street and oblique scales.
- Repeated occupation is allowed only inside approved repeatable bays. Roof
  topology, corner bays, entry hierarchy and perimeter voids remain fixed.
- Detail additions must survive the same all-elevation, triangle-budget and
  delivery-envelope checks as the base model. A richer render is not an excuse
  to weaken modular validation.

### V82 multi-scale modular material and presentation lessons

The Beaux-Arts terminal pilot applied the broader Blender-video synthesis to a
single reference-rich landmark. It separated repeatable construction from
fixed identity, built a real glass-and-iron trainshed section, added medium
detail before fine ornament, and compared the exact references with both Eevee
and Cycles.

- Decompose a landmark into fixed ceremonial modules, repeatable structural
  bays and material fields before adding decoration. The headhouse end returns,
  clock tower and roof end fields remain fixed; ordinary arches and transverse
  trainshed ribs may repeat only inside their declared spans.
- Use a multi-scale detail contract. Large massing establishes the headhouse and
  barrel silhouette; medium geometry supplies pilasters, cornice blocks, iron
  ribs, purlins, balustrades and side-wall openings; fine baked or instanced
  ornament is added only after those layers survive all reference views.
- A transparent roof is a physical section, not a shader setting. Glass and
  opaque metal occupy non-overlapping roof fields, visible iron structure sits
  below and across the glazing, and the interior volume remains unobstructed.
- Glazing realism requires an environment and something to see through or
  reflect. Pair physical panes with a readable recessed interior and keep the
  presentation world, sun and fill as a separate recipe contract that never
  enters the exported GLB.
- Compare Cycles, Eevee and the runtime independently. In this pilot Cycles
  revealed warm transmitted depth that Eevee suppressed, proving that dark
  real-time windows were chiefly a parity issue; both renderers still exposed
  the same missing carved stone relief, which remains a modeling issue.
- Prefer bounded high-detail pilots before optimization. Preserve the approved
  silhouette and section, then consolidate repeated meshes, bake non-silhouette
  ornament and reduce material/texture payloads against explicit triangle,
  material and delivery-envelope warnings.
- Metadata remains selective. Limestone family, recessed arcade section and
  barrel-vault topology were admitted because all three exact images agreed;
  feature counts, proportions, roof-field fractions and landmark placement
  remained image-measured.

### V83 exportable surface-story and neutral-parity lessons

The second Beaux-Arts terminal pass isolated the material workflow taught in
the reviewed Blender videos. It kept the V82 massing and cameras as a
controlled baseline, baked restrained surface history into ordinary PBR image
maps, and compared the source Blender file with its re-imported catalogue GLB.

- Procedural material work is useful only when its result survives delivery.
  Bake the approved palette and macro variation into tile-safe albedo,
  roughness and tangent-space normal maps, wire those maps directly to the
  Principled material, and retain the texture key and real-world tile scale in
  exported material metadata.
- UV scale is an architectural measurement. Every required surface declares a
  plausible metres-per-tile range; a stone course, brick field and standing
  seam roof may share machinery but should not share an arbitrary scale.
- Weathering is semantic, not global noise. Use separate bounded materials for
  plausible zones such as protected cornice bands, grade patina, oxidized roof
  metal and pale mineral roof fields. Do not apply one grunge pass to every
  object.
- Add a context-free neutral source-versus-GLB render pair. The V83 pilot
  retained all required PBR channels and reached 99.23 percent whole-frame
  mean pixel similarity after glTF export and re-import. V84 later showed that
  background pixels inflated that historical score, so only the newer
  alpha-masked foreground metric may approve future exports.
- Surface realism and archetype fidelity are independent approvals. V83 is a
  keeper for the baked-surface and parity methodology, but the exact terminal
  remains provisional because the reference has a more articulated clock
  tower, sculpted stone relief, richer capitals and a different balustrade
  cadence. Those are fixed ornament/topology tasks, not shader tasks.
- The 2048 px hero bake raised the assembled GLB to 13.9 MB. Preserve the
  visually approved source, then test 1024 px or KTX2/UASTC delivery variants
  side by side; do not accept a texture-budget regression merely because the
  pilot render improved.

### V84 three-building surface-story generalization lessons

The Neoclassical Courthouse, Italian Portici and Romanesque Warehouse extended
the V83 workflow across granite/copper, stone/stucco/pantile and
brick/brownstone/membrane material systems while preserving their V78 massing,
facade sheets and cameras as controlled baselines.

- Construction role is stricter than material family. The first batch used a
  generic terracotta source that looked like wall brick on the portici roof, a
  brown copper source without the courthouse's standing-seam language and a
  recoloured sandstone approximation for warehouse brownstone. Replacing them
  with pantile, standing-seam and brownstone sources immediately improved the
  exact-reference comparisons. Every required baked material now declares a
  named construction role at preflight.
- The 1024 px baked sets retained the visible surface hierarchy while producing
  assembled GLBs of 2.69-3.91 MB, all below the 8 MB delivery target. This is
  the approved default for bounded catalogue pilots unless a side-by-side test
  proves that a particular hero surface needs more resolution.
- Whole-frame export similarity was a false comfort because the studio
  background dominated the score. V84 changed the neutral render to transparent
  film and scores only the union of alpha-masked building pixels, with a five
  percent mean-error limit and 0.98 silhouette IoU. The stricter result is
  95.76 percent for the courthouse, 97.53 percent for the portici and 93.26
  percent for the warehouse; the warehouse correctly remains blocked.
- Italian Portici is the strongest keeper candidate because material source
  roles and existing fixed geometry reinforce the same archetype. The
  courthouse is a surface-method keeper but still needs sculpted classical
  identity. The warehouse has improved surfaces but needs both export-parity
  repair and a more faithful loading-arcade section.
- Photographic facade sheets can retain fine identity, but the visible results
  confirm that they do not replace fixed eaves, capitals, pediment relief,
  occupied arcade depth or correctly paced loading bays. Preserve the approved
  surfaces and spend the next pass on those medium-scale construction cues.

### V85 three-new-archetype lessons

The Classic Brownstone Streetwall, Blue Curtain-Wall Office and Nordic
Mass-Timber Mid-Rise tested the current image-lock, facade-sheet, layered-glass
and baked-surface workflow on three catalogue archetypes with no prior pilot
artifacts.

- The actual baked albedo is the delivered colour authority. The first
  brownstone pass declared a pale roof but still rendered a dark membrane
  because the bound V84 image map contained dark pixels. A new pale membrane
  bake fixed the exact-aerial comparison and passed the surface audit; changing
  only `base_color` would not have done so.
- Give each architectural feature one owner. The first Nordic pass combined
  loggias already present in the audited facade/glazing sheets with another
  projecting balcony and picture-frame system, producing floating timber
  cages. Removing the redundant assemblies retained the recessed loggia read
  and reduced the assembled model from 43,536 to 24,464 triangles.
- Automated preflight, geometry, PBR-channel and export-parity checks do not
  prove that a facade sheet matches the exact variant composition. The office
  passes every machine gate and its layered glazing is materially credible,
  but the inherited rectified sheet assigns too much frontage to opaque metal
  panels. It remains conditional until a variant-native sheet is approved.
- Brownstone and Nordic timber are keeper candidates after exact-image review;
  the office is a useful glass-method pilot but is not yet a catalogue keeper.

### V86 finite-catalogue rollout lessons

The Board-Formed Concrete civic pilot converted the image-lock methodology into
a finite catalogue campaign without weakening the human visual checkpoint.

- Treat catalogue completion as an authoring queue, not an unattended render
  loop. A target becomes render-ready only after it has an exact-variant
  signature profile, compatible reference roles, an audited facade sheet and a
  production contract. Machine success never promotes it to the catalogue.
- Complete one representative exact variant for each parent archetype before
  expanding sibling variants. Keep production batches at five buildings or
  fewer, render serially, preserve resumable manifests and stop after every
  batch for exact-reference review.
- Separate paid image generation from batch execution. The rollout planner may
  estimate missing facade-sheet calls, but the runner defaults to zero and
  rejects a batch that requests paid calls without a separately authorized
  asset-generation step.
- Surface naming must describe the visible construction pattern. The first
  concrete pass used a square-panel source while declaring board-formed
  concrete; horizontal shutter-board courses and sparse staggered joints were
  required before the material matched the archetype.
- The pilot is a keeper candidate after exact-image review: its floating blind
  volumes, deep ground-floor recess, pilotis, clerestory, roof slab and raised
  roof core are preserved. Glazing/environment realism remains a named human
  review item rather than a reason to overstate machine approval.

### V87 ten-variant checkpoint lessons

The first ten-variant checkpoint tested exact-image authoring across five new
parent archetypes. It confirmed that the campaign can produce convincing new
families, but also proved why ten must be reviewed before one hundred begin.

- Treat the three reference views as the geometry authority. Multimodal output
  is a draft feature schedule, not executable geometry; normalize it, bind
  every measurement to a named node and reject metadata that conflicts with
  visible evidence.
- Count storeys and opening shapes before generating the facade atlas. A
  technically polished atlas with invented arches or the wrong floor count is
  a semantic failure and must not be promoted merely because its PBR and GLB
  checks pass.
- Large modern curtain walls use lightweight registered glass masks and fixed
  structural members. Generating a complete return/frame assembly for every
  atlas opening creates floating cages, excessive triangles and a less faithful
  silhouette. Heritage entrances and arcades may still use deep returns where
  the section is identity-bearing.
- Roofs, side walls and rear walls need explicit material ownership. Every
  visible attachment resolves to a baked construction material; every exposed
  elevation receives a related skin; and roof/aerial review remains a separate
  pass from the street facade.
- Recessed public space is topology. The Moorish pilot's three souk arches are
  a real opening block with piers, lining, clearances and deeper occupied backs,
  not dark rectangles painted onto a wall.
- Add a medium-detail construction pass after massing: entry surrounds, timber
  reveals, fins, balcony edges and roof frames. Use one owner per feature so
  the atlas and geometry do not duplicate the same balcony or window system.
- Compare exact reference, archetype-match, roof-audit and rear-corner views on
  one board. Record `keeper`, `provisional` or `rejected` independently from
  validation, PBR-channel and source-versus-GLB parity status. Scale-up remains
  blocked whenever any pilot needs semantic or proportion repair.

### V88 mandatory gold-set rebuild lessons

The V88 rebuild made the full architectural workflow compulsory for every one
of the ten checkpoint variants. A successful render is now only an intermediate
artifact: release requires reference sufficiency, representation selection,
clay massing, roof and void construction, medium detail, retopology, manual UV
audit, material bake, export parity and architect review in that order.

- The exact archetype images are the design authority. Metadata is admitted
  field by field only when it confirms a visible fact and drives a named piece
  of construction; generic parent prose may never override a counted storey,
  opening, roof axis, material zone or silhouette.
- Complex modern glass and highly ornamental curved façades work best as a
  layered representation. An image-locked semantic surface carries irregular
  pattern and fine identity, while separate physical glazing, structural
  members, balcony slabs, rails, roof forms, returns and void sections provide
  depth, transmission, shadow and orbit credibility. A generic kit is excluded
  whenever it duplicates or contradicts the exact variant.
- Treat high-quality image-locked surfaces as registered architectural stickers
  over approved geometry, not as flat billboards or independently scaled floor
  strips. Split the source by semantic ownership (wall field, gallery, oriel,
  balcony face and roof), conform each thin surface to its named construction
  and preserve one canonical metres-to-UV transform. Seam bleed must expand
  geometry and UV bounds by the same physical distance. Window centres, column
  centres and floor datums are mandatory shared anchors; any drift is a
  machine-testable hard stop before visual review.
- Public openings are sections, not dark facade marks. Entrances, arcades and
  undercrofts require an executable opening through the envelope, reveals or
  lining, a minimum reference-derived tunnel depth and a recessed occupied back
  layer. Every skin crossing the opening must be split or cleared.
- Alpha-bearing semantic textures must remain lossless through glTF export.
  The first precast export used lossy WebP packing and failed neutral source to
  re-import parity at 94.86 percent. Preserving PNG alpha raised parity to 99.70
  percent without changing the model, proving that image encoding is a release
  concern rather than an implementation detail.
- A registered Sticker Method asset is a fixed landmark. It may be translated
  and rotated, but polygon fitting, floor-count changes and non-uniform scaling
  are forbidden because they break the shared metres-to-UV registration. Use a
  select-and-place catalogue interaction for this representation; use another
  repeatable-bay representation when arbitrary LEGO capacity is required.
- Alpha-isolated feature stickers retain their unique material node trees after
  mesh joining. Consolidating those materials into the opaque elevation atlas
  discards the mask and exposes rectangular crop edges, so material
  consolidation is now a release-stage concern as well as an optimization.
- Machine checks and architectural acceptance remain independent. Each model
  needs street/front, front-corner, rear-corner, high-oblique/roof, close-facade
  and context views compared with the exact archetype. A named architect must
  score at least 85/100 and report no hard-stop error; a batch average cannot
  conceal a rejected building.
- Final review artifacts must be rebuilt from the same versioned source and
  export path. Repair directories are diagnostic checkpoints, not substitutes
  for a clean ten-building rerun.

### V89 non-rectangular void registration lesson

The Moorish Sticker Method pilot proved that a real tunnel is necessary but
not sufficient. A generic semicircle, a hand-tuned Gothic ogive and an
over-bulged horseshoe all passed structural validation while failing exact
architect review at 64, 77 and 69/100. A smoothed seven-control approximation
still failed at 71/100 because the visible soffit became a second dominant arch.

- For a non-rectangular public opening, extract the actual inner negative-space
  contour from the registered source or an approved binary mask. Do not infer
  the contour from the surrounding decorative frame or a style label.
- The same versioned contour must cut every sticker crossing the opening and
  generate the physical jamb/soffit section. Count, centre, spring, shoulder and
  crown drift are hard stops before Blender rendering.
- Uniformly inset/extrude the contour behind the facade plane. The lining is a
  narrow reveal owned by the passage section; it must not cover the decorative
  sticker or read as a second foreground portal.
- Deep occupied backs, plaster soffits, lower tile datums and authored return
  arcades remain reusable successes. They do not compensate for a mismatched
  portal silhouette.
- Publish failed iterations and architect scores. A machine-valid contour
  experiment remains `rejected` until the named architect clears 85/100.

### V90 continuous-sticker glazing ownership lesson

The three-landmark pilot showed that a high-quality continuous facade sticker
can lose realism when a generic physical glazing schedule is placed in front of
it. Even technically valid panes become opaque-looking duplicates when their
centres, mullions or extents do not exactly match the photographed openings.

- Approve a source-traced roof/silhouette proxy and an all-elevation occupancy
  map before generating the sticker. Blank visible sides or rears, generic roof
  boxes and doubled physical/sticker gables are automatic pre-render failures.
- Keep the continuous image-locked elevation as the visible owner of windows,
  mullions and fine surrounds until an opening-accurate semantic glass mask has
  been approved in the same metres-to-UV registration frame.
- A physical optical overlay may add transmission, reflection and recess only
  inside that approved mask. It may not introduce a second window schedule or
  cover photographed frames, curtains, ornament or masonry.
- Geometry still owns sill/reveal depth, bays, balconies, roofs, void sections
  and other silhouette- or shadow-bearing construction. Removing a duplicate
  pane does not permit the elevation to collapse back into a flat billboard.
- Treat sticker-to-glass registration as a release gate: compare opening count,
  centres, floor datums and boundaries before Blender rendering. When no exact
  mask exists, retain sticker-owned glazing and record physical glass as a
  deferred enhancement rather than guessing.
- Camera-match the review renders to the exact reference views. Neutral
  source-to-GLB parity verifies export fidelity, not architectural likeness,
  and must never be presented as an archetype-similarity score.

## Updating this memory

When a pilot reveals a reusable lesson:

1. fix the generator or kit;
2. add the symptom, cause and correction to the JSON memory;
3. add or tighten an automated gate where the lesson is machine-testable;
4. add a regression test;
5. increment `memory_version`;
6. regenerate one approved representative before scaling the change.

Do not encode one building's ornament as a universal rule. Store universal construction principles in this memory, family identity in `architectural_signature_profiles.json`, and variant-specific dimensions/reference roles in the catalogue or massing graph.
