# High-Quality 3D Building Production Memory

This is the persistent production memory for turning City Prompt archetypes and variants into high-quality modular GLB families. It captures the construction rules established through the Kinnaird, Chicago, Gothic, glass, Nordic, industrial and Parisian pilots.

The memory has two forms:

- this document explains the decisions to people;
- [`high_quality_building_memory.json`](../tools/archetype_compiler/high_quality_building_memory.json) gives the batch pipeline versioned, executable gates.

The assessor is [`quality_memory.py`](../tools/archetype_compiler/quality_memory.py). `generate_worldclass_library.py` records its result for every generated family, so a batch can continue while only questionable outputs enter a review queue.

Current executable memory: `2026-08-08-material-void-contract-v77`.

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
- Catalogue metadata can directly select construction: number of storeys,
  ridge axis, hip height, roof texture family, passage depth and material slots.
  The image remains authoritative when prose and visible colour/topology differ.
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

## Updating this memory

When a pilot reveals a reusable lesson:

1. fix the generator or kit;
2. add the symptom, cause and correction to the JSON memory;
3. add or tighten an automated gate where the lesson is machine-testable;
4. add a regression test;
5. increment `memory_version`;
6. regenerate one approved representative before scaling the change.

Do not encode one building's ornament as a universal rule. Store universal construction principles in this memory, family identity in `architectural_signature_profiles.json`, and variant-specific dimensions/reference roles in the catalogue or massing graph.
