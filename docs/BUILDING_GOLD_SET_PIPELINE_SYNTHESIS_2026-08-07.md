# Building Gold Set and Catalogue Pipeline Synthesis

Date: 2026-08-07
Gold set: Victorian Second Empire, Classic Haussmann, Classic Eixample and Perpendicular Gothic Chapel

## Decision

These four families are the calibration set for the next building-generation pipeline. They are not identical construction recipes. Together they establish two legitimate ways to make a faithful modular building:

1. **Authored semantic stack** — appropriate when the archetype is genuinely a regular streetwall or perimeter block. Base, entrance, corners, balcony datums, crown and roof remain fixed; only ordinary middle bays repeat. Victorian Second Empire and Classic Haussmann use this mode.
2. **Archetype-specific massing graph** — required when plan, silhouette or section carries identity. Eixample uses a true Cerdà chamfer with oriented diagonal assemblies. The Perpendicular chapel uses a fixed hall, central tower, octagonal lantern, terminal towers and roof graph.

The rejected option is an unclassified generic repeated box with an archetype image wrapped over it.

## What the four successful families share

### The exact variant is the design authority

Each successful result resolved a specific visual target. The selected variant controls the image paths, generation identifier, signature profile, material language and dimensions. Parent-level labels are not sufficient for production.

Classic Haussmann and Classic Eixample were historically generated through their parent entries even though they visually corresponded to variant 0. The updated registry names those variants explicitly so future rebuilds cannot drift to a sibling.

### Three views establish one coherent building

Production intake requires:

- a street or identity view;
- an oblique massing view;
- a roof or high-aerial view.

The exporter now records these paths in `referenceViews`. Missing or contradictory roles stop the pipeline before paid generation.

### Fixed identity is separated from repeatable capacity

Across the gold set, these elements remain fixed:

- public entrance and base hierarchy;
- corners, chamfers or terminal towers;
- balcony and cornice datums;
- crown, mansard, lantern and roof silhouette;
- singular portals, porticos, dormer groups and skyline objects.

Only ordinary wall bays or floors may repeat. The repeat period must remain aligned across facade albedo, semantic openings, physical glazing and interiors.

### Surface generation follows geometry

The facade image is a shadow-neutral material and registration source, not a substitute for construction. Projection, recess, return, opening shape, balcony support and roof section are built as geometry when they affect silhouettes, shadows or oblique views.

### Approval is visual and multiscale

Geometry validation proves that files are structurally usable. It does not prove likeness. Catalogue release now requires a separate `visual_approval.json` confirming review at:

- block scale;
- building scale;
- facade scale;
- orbit and live-context scale.

Until that record exists, `high_quality_ready` remains false.

## Family-specific synthesis

### Victorian Heritage — Second Empire

Success came from render-locking the Second Empire variant, keeping the crown shallow, and treating the mansard, dormers, cresting, rusticated corners and portico as fixed semantic assemblies. Its footprint can remain regular because regularity is authentic to the type; the quality comes from hierarchy and roof identity rather than arbitrary plan complexity.

### Classic Haussmann

The v19e corrections repaired the architectural section: integrated zinc dormers, recessed shopfronts, removed the false suspended slab and softened the corner. The successful decomposition is shopfront base, ordered limestone middle, two continuous balcony datums, deep cornice and occupied mansard. The neutral limestone bays can repeat, but entrances, corners and the mansard ends cannot stretch.

### Classic Eixample

The decisive improvement was the `cerda_chamfer_v21` massing graph. The diagonal corner is a real face with its own skin, glazing, entrance and balcony continuation. Cardinal textures cannot fill a diagonal wedge. This is the gold-set representative for chamfered perimeter blocks and oriented facade assemblies.

### Perpendicular Gothic Chapel

The first render-locked attempt was correctly rejected because a complete chapel elevation was printed onto a rectangular stack. The successful v2 family replaced that stack with `perpendicular_chapel_lantern_v52`: fixed chapel hall, projecting central tower, octagonal lantern, four terminal towers, battlements, buttresses and shallow lead roof. Every exposed polygonal plane receives registered construction and glazing. This is the landmark-quality ceiling for the pipeline.

## Updated production sequence

1. Export an explicit catalogue variant.
2. Discover and record the three authoritative reference roles.
3. Compile grammar and inject the variant or archetype signature.
4. Declare `identity_mode` as `semantic_stack` or `massing_graph`.
5. Run `production_preflight.json`; stop on any failure.
6. Generate or reuse the rectified facade and registered schedules.
7. Build fixed identity plus repeatable capacity modules.
8. Render archetype-match, street, aerial, close, rear-oblique and context views.
9. Run geometry and quality-memory assessment.
10. Review the comparison board and explicitly record visual approval.
11. Import only families with structural pass and visual approval.

## Rollout after the gold-set pilot

Do not generate the full catalogue as one list. Cluster it by identity mode, massing graph, roof family, corner condition, opening system and material language. Approve one representative per cluster, then generate a bounded group of five to ten related variants. Outliers return to grammar and signature authoring; they do not inherit a superficially similar parent profile.

The first catalogue wave should use the four gold clusters:

- regular heritage streetwalls derived from Haussmann;
- formal mansard heritage buildings derived from Second Empire;
- chamfered perimeter blocks derived from Eixample;
- landmark halls and towers derived from the Perpendicular chapel methodology.

Run the cheap calibration command before any facade calls:

```powershell
python tools/archetype_compiler/generate_worldclass_library.py `
  --registry tools/archetype_compiler/worldclass_gold_set_v64.json `
  --output artifacts/building-gold-set-v64/families `
  --grammar-only
```

After each rendered representative is reviewed, record approval explicitly:

```powershell
python tools/archetype_compiler/visual_approval.py `
  --output artifacts/building-gold-set-v64/families/<family>/visual_approval.json `
  --family <family> `
  --reviewer <name> `
  --reference-set 2026-08-07-four-family-v1 `
  --approve
```

Approval must never be generated automatically.
