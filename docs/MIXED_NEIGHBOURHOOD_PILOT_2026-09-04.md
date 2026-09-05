# Mixed-neighbourhood integration pilot

This initiative follows the student-studio implementation in `e39046558` and
the [January 2027 delivery plan](STUDENT_STUDIO_IMPLEMENTATION_PLAN.md). It tests
whether reviewed clay buildings, authored streets and a small park form one
coherent, editable community before expanding the asset catalogue.

## Scope and invariants

- The saved plan controls dimensions, positions and identity. Renders change
  appearance; they do not move hidden objects into view or invent replacements.
- Architectural clay is an exact-variant, fixed-native-size delivery. Its actual
  mesh extents govern containment. Positioning may translate and rotate it;
  resizing or repeating it requires a separately verified family contract.
- Ground, street junctions and park access share the same source zones and site
  datum. A retained-ground boundary must not create unnecessary building aprons.
- Manual park access is derived from the whole scene, including barriers.
  Authored access points take precedence. An unresolved route remains unresolved.
- The bounded street pilot covers orthogonal three-arm T and four-arm X nodes.
  Unsupported geometry must be diagnosed, never represented as a phantom arm.

## Finite implementation sequence

1. Preserve the original pending clay and ground inputs. Work only on
   `codex/mixed-neighbourhood-pilot` in the existing isolated worktree.
2. Reconcile the current clay policy, exact catalogue selection, actual mesh
   bounds, frontend centring and server-side footprint checks.
3. Integrate retained ground, connected junctions and manual park access using
   existing metric public-realm programs. Do not generate a new asset family.
4. Build one local mixed-block fixture from reviewed source models, an
   orthogonal T, and a supported small park. Inspect aerial and ground views,
   geometry after edits, captured source evidence and a reload.
5. Run targeted frontend/backend checks, TypeScript, lint, production bundling
   and free GPU capture verification. Record limitations and checkpoint only
   the reviewed source changes.

## Acceptance evidence

- A native model fits the actual plot, including concavity; rejected sizes and
  floor counts cannot be forced into a distorted detailed model.
- Disabling the last clay asset cannot reactivate legacy fallback detail.
- Clay models remain centred and at native scale in both previews and the globe.
- T pavement and sidewalks have three real arms; segment flatwork does not
  overlap the node-owned intersection.
- A park connector reaches a real sidewalk/path, has whole-width clearance and
  updates when its road or barriers change. Existing authored gates survive.
- Render evidence identifies its saved source revisions and any derived access
  snapshot. A screenshot alone is not proof of valid geometry.
- No provider spending is required for this pilot. The earlier image test used
  approximately US$0.280668 of the user's US$10 total authorization.

## Preservation and catalogue status

Original pending inputs were copied byte-for-byte to the ignored
`artifacts/mixed-neighbourhood/original-inputs` directory, with hashes and the
original Git status beside them. The original checkout remains user work.
Only the current RLASM method, repository policy and matching machine-readable
method are reconciled here; unrelated pending building-family waves are not
imported. The ten original clay GLBs are read-only local fixtures. This pilot
does not promote a new family, approve a render, publish assets or deploy code.

## Ground alignment correction and local fixture

The user correctly rejected the initial downtown fixture: a level replacement
surface over occupied Google tiles did not demonstrate contact with real ground.
The final local project is **Open site ground alignment — local QA**, ID
`4b387084-4dbc-4df3-97cc-1cd48d015266`, at `51.04542, -114.04677`.
It uses a clear 62 x 84 m field near Fort Calgary, three native clay buildings,
two narrow residential streets forming a T, and a pocket park with two derived
connections. This is an illustrative open test site, not a claim that the land
is vacant, available for development or appropriate for this proposal.

The boundary properties now expose **Site ground**. **Follow existing terrain —
open sites** retains Google context and measures its visible surface. **Clear
site for redevelopment** preserves the earlier level replacement behavior.
Existing saved plans keep their preference; no migration silently changes them.

For retained ground, one revision-bound height field supplies the whole scene.
It uses visible Google tile meshes in WGS84 ellipsoid height, two repeatable
passes, a 2.5 m target spacing and a 1,200-sample limit. Missing, discontinuous or
unstable measurements prevent capture instead of being replaced by an elevation
API guess. A visible-tile raycast fallback fixes missed intersections at tile
bounding-volume seams. Tile refinement invalidates the field and its consumers.

Ground surfaces are clipped at the field's actual grid rows, columns and
triangle diagonals. Their interiors therefore follow the same planes as their
vertices, preserving UVs, materials and authored construction lifts. Rigid
buildings retain their native dimensions. Small footprint-specific foundations
clear every terrain extremum under the building, including interior grid peaks;
their skirts follow the same triangle-edge crossings. Detached yards are not
filled by a whole-plot pad. More than 3 m of required foundation is unresolved.

## Measured evidence

- The final live surface contains **910 measured points**, with two identical
  passes, no unresolved building placement and approximately 0.81 m site relief.
- An independent direct raycast at **88 inter-grid locations** found no missing
  terrain. Height-field minus visible Google mesh ranged from **-2.16 cm to
  +4.57 cm**; the 95th-percentile absolute difference was **2.03 cm**. The earlier
  4 m grid had a 5.28 cm 95th-percentile difference at these locations.
- At **178 actual rendered foundation skirt vertices**, bottom minus visible
  tile height ranged from **-6.44 cm to +1.29 cm**. Negative values indicate a
  slightly embedded skirt. This checks rendered world transforms against the
  tile mesh, rather than merely comparing two consumers of the same field.
- Replay of the actual saved zone meshes exposed an additional interpolation
  error of up to 5.37 cm for the park and 3.54 cm for the street. Exact grid
  triangulation reduced this separate error to floating-point tolerance.
- Moving the east street 2 m changed its saved revision and the park access
  source signature. Both park connections resolved again; Generate to 3D
  recompiled the edited plan successfully. Reload restored the measured scene.
- The real fixture exposed a street-furniture runtime error: numeric station
  metadata was treated as a placement array. Typed placement mapping preserves
  metadata; regression coverage now uses the real fixture builder output.

Raw diagnostics, local DB fixtures, screenshots, captures and test reports are
ignored output under `artifacts/mixed-neighbourhood/`. They are not source
catalogue assets. The original fourteen pending inputs were rehashed unchanged.

## Verification checkpoint

- Final frontend run: **580 passing tests in 32 files**, including real street
  fixture metadata, exact terrain-plane interiors, interior foundation peaks,
  imported-model lifecycle, native clay placement, capture stability, and the
  saved Site ground choice.
- A subsequent five-test video adapter suite verifies that initial Single frame
  capture requires the mounted authored instance inventory. A hidden or missing
  model blocks capture; ordinary occlusion and off-camera geometry remain valid
  because this manifest describes mounted scene objects, not visible pixels.
  The live browser check also passed: capture was blocked with 3D models
  hidden and succeeded after restoring them, without a provider request.
- Save/reload testing found that saving an unchanged LEGO recipe unconditionally
  marked its zone stale and removed its proposal identity from capture. The
  endpoint now preserves the exact compiled proof for semantic no-op saves,
  after current source/catalogue checks. Real geometry/asset changes still
  invalidate it; already-stale records require a real recompile. All 238 tests
  in the combined recipe/clay/LEGO run pass, including 20 new save regressions.
- Full TypeScript check, scoped ESLint on 39 changed production files,
  `git diff --check`, and production bundling pass. Existing large-bundle
  warnings remain; the build does not copy the public asset catalogue.
- Targeted backend clay/native-bounds, catalogue, recipe, Direct 3D,
  park-access and shared-ground provenance suites pass, as do the relevant
  compiler registry checks. Detailed commands/results are retained in the
  ignored verification reports.
- Free GPU capture includes beauty, proposal mask, class/instance IDs, depth,
  normals and materials. Offline backend validation passes schema, server
  scene/claims, control preparation and saved source-revision binding, with
  all three buildings, a three-arm T, both park connections and 910 samples.
  The retained scene correctly has eight instances: it has no extra prepared
  whole-site ground instance. Mask recall/IoU are 1.0 for the source controls;
  these are not scores for an AI-generated image.
- The boundary control was exercised through More Tools > Site Boundary and
  saved with its retained preference. Save all recipes reported all three
  saved successfully. The final three HTTP 200 responses each reported
  `changed:false`, with unchanged zone revisions and representation hashes.
  A subsequent reload and closer GPU capture verified all eight instances in
  the persisted scene, with approximately 14.9% proposal coverage.
- No paid image or video generation was used for this pilot. Google Maps tile
  usage was not independently costed. Nothing was deployed or pushed.

## Practical limits

This aligns a proposal to visible photogrammetry, not surveyed bare earth.
Google can represent cars, vegetation or roofs as surface; a smooth roof can
pass the terrain checks. Students should choose a visibly clear site for this
mode. The separate parking-lot diagnostic correctly rejected large local
discontinuities instead of forcing a flat placement.

The measured centimetre differences remain real. Exact scene triangulation
eliminates added geometry interpolation error; it cannot make a sampled height
field identical to all Google triangles. Large, steep or incomplete sites can
remain unavailable, and tile refinement can temporarily hide proposals while
the surface is measured again. Native imported models with irregular footprints
still use conservative rectangular support envelopes; this is visualization
seating, not foundation engineering.

T/X support remains bounded to the documented orthogonal junction contracts.
Native clay remains limited to exact available variants. This pilot does not
complete catalogue expansion, arbitrary road engineering, generated-image
identity guarantees or an interactive generative walkthrough.
