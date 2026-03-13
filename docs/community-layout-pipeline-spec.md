# Community Layout Pipeline Spec

This document defines a repo-aware implementation plan for evolving the current site layout and block editor stack into a rule-based community generator that produces:

1. procedurally valid 2D master plans
2. archetype-informed 3D generation inputs
3. premium 2D presentation renders
4. reusable generated scene assets over time

It is grounded in the current repository structure, especially:

- `backend/app/services/layout_planner.py`
- `backend/app/api/v1/site_zones.py`
- `backend/app/services/master_plan_2d.py`
- `frontend/src/features/block-editor/EmbeddedBlockEditor.tsx`
- `frontend/src/features/block-editor/BlockPropertiesPanel.tsx`
- `frontend/src/store/blockEditorStore.ts`
- `frontend/src/types/index.ts`
- `frontend/src/components/viewer/ZonePropertiesPanel.tsx`
- `frontend/src/components/viewer/aestheticCatalog.ts`

## Product Goal

The platform should treat community generation as a structured, staged system rather than a single prompt.

The user defines:

- `Site Boundary`
- `Buildings`
- `Streets and Paths`
- `Parks / Plazas`

The system then:

1. interprets those inputs as geometry plus design intent
2. runs rule-based spatial generation and validation
3. applies archetype metadata to massing, frontage, materials, and public realm defaults
4. generates:
   - editable master-plan geometry
   - presentation-grade 2D imagery
   - 3D model generation inputs
   - reusable model-library assets where possible

## Current Repo Assessment

### What already exists

- `layout_planner.py` already generates `buildings`, `roads`, and `green_spaces`.
- `site_zones.py` already persists `_saved_layout`, `_layout_roads`, `_layout_green_spaces`, and syncs building records from edited layouts.
- `master_plan_2d.py` already supports 2D master plan generation and selection.
- `ZonePropertiesPanel.tsx` and `aestheticCatalog.ts` already support archetype libraries and style metadata for zones.
- `EmbeddedBlockEditor.tsx` and `blockEditorStore.ts` already support editing buildings, roads, and green spaces.

### What is missing

- A staged procedural generation pipeline with explicit phases.
- Shared schema types rich enough to carry archetype metadata across buildings, streets, and open spaces.
- Rule modules for street graph generation, parceling, setbacks, and collision validation.
- A distinction between:
  - hard geometric and planning constraints
  - soft aesthetic and rendering guidance
- Diagnostics explaining why a layout was changed by the system.
- A consistent master-plan rendering pipeline that separates geometry control from image stylization.

## Architectural Principle

The system should split generation into three layers:

### 1. Hard spatial rules

These are non-negotiable geometric and planning constraints enforced in code:

- planar street graph validity
- right-of-way widths
- intersection alignment and corner radii
- setback envelopes
- lot coverage
- frontage alignment
- walkability coverage
- non-overlap and collision rules
- site-boundary containment

### 2. Archetype and style rules

These are structured defaults that influence the layout but do not override geometry safety:

- building style family
- street/pathway typology
- park/plaza typology
- material palette
- facade rhythm
- massing tendency
- planting character
- paving language
- public-realm mood

### 3. Rendering and model-generation guidance

These are downstream interpretation inputs:

- 2D presentation prompt guidance
- 3D building prompt guidance
- scene dressing hints
- asset reuse keys
- material and facade selection hints

## Phase-Based System Design

## Phase 1: Shared Data Model Upgrade

### Goal

Expand the current layout types so buildings, streets, and open spaces can all carry:

- user-selected archetype metadata
- procedural rule inputs
- validation outputs
- downstream generation style inputs

### Frontend files to modify

- `frontend/src/types/index.ts`
- `frontend/src/store/blockEditorStore.ts`
- `frontend/src/features/block-editor/BlockPropertiesPanel.tsx`
- `frontend/src/features/block-editor/EmbeddedBlockEditor.tsx`

### Backend files to modify

- `backend/app/schemas/schemas.py`
- `backend/app/api/v1/site_zones.py`

### New shared type targets

```ts
export type CommunitySystemType = 'building' | 'streets_paths' | 'parks' | 'plazas';

export interface StyleProfile {
  materials?: string[];
  facadeRhythm?: string;
  roofForm?: string;
  frontageType?: string;
  windowStyle?: string;
  massing?: string;
  heightTendency?: string;
  streetRelationship?: string;
  corridorCharacter?: string;
  movementHierarchy?: string;
  surfaceType?: string;
  plantingCharacter?: string;
  edgeConditions?: string;
  landscapeCharacter?: string;
  pavingType?: string;
  plantingType?: string;
  seatingRealm?: string;
  waterFeatures?: string;
  opennessEnclosure?: string;
  renderingMood?: string;
}

export interface GenerationStyleInput {
  domain: CommunitySystemType;
  subtype?: string;
  developmentType?: string;
  aestheticCategoryId?: string;
  aestheticCategoryLabel?: string;
  archetypeId: string;
  archetypeLabel: string;
  archetypeImageUrl?: string;
  archetypeImagePath?: string;
  generationTags?: string[];
  styleProfile?: StyleProfile;
  imagePrompt?: {
    positive?: string;
    negative?: string;
  };
  conversionHints?: Record<string, unknown>;
  reuseSignature?: string;
}

export interface ValidationNote {
  code: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
  sourcePhase:
    | 'street_graph'
    | 'row_geometry'
    | 'parceling'
    | 'civic_distribution'
    | 'zoning'
    | 'building_placement'
    | 'collision_validation';
}
```

### Layout model targets

`LayoutBuildingData` should be extended with:

- `development_type`
- `development_aesthetic`
- `development_aesthetic_category`
- `development_subcategory`
- `development_archetype_id`
- `development_archetype_label`
- `development_archetype_image`
- `generation_tags`
- `style_profile`
- `generation_style_input`
- `facade_material`
- `roof_style`
- `frontage_edge_index`
- `lot_coverage_ratio`
- `validation_notes`

`LayoutRoadData` should be extended with:

- `road_aesthetic`
- `road_aesthetic_category`
- `road_archetype_id`
- `road_archetype_label`
- `road_archetype_image`
- `transport_modes`
- `mobility_profile`
- `volume`
- `road_surface`
- `lane_count`
- `sidewalks`
- `has_sidewalks`
- `priority_pedestrian`
- `priority_cycling`
- `priority_transit`
- `priority_auto`
- `right_of_way_m`
- `pedestrian_zone_m`
- `roadway_zone_m`
- `frontage_zone_m`
- `intersection_type`
- `validation_notes`
- `generation_style_input`

`LayoutGreenSpaceData` should be extended with:

- `green_space_aesthetic`
- `green_space_aesthetic_category`
- `plaza_aesthetic`
- `plaza_aesthetic_category`
- `archetype_id`
- `archetype_label`
- `archetype_image`
- `tree_density`
- `tree_density_level`
- `has_paths`
- `has_benches`
- `shade_strategy`
- `water_feature`
- `paving_material`
- `plaza_program`
- `frontage_length_m`
- `access_points`
- `walkshed_served_units`
- `validation_notes`
- `generation_style_input`

### Save payload target

`SiteLayoutResponse` should become the canonical scene payload passed between:

- zone property editing
- block editor
- save-layout
- 2D master plan generation
- 3D generation
- reusable asset matching

## Phase 2: Procedural Rules Layer

### Goal

Move critical layout logic out of prompt-only generation and into backend rule modules.

### New backend modules

- `backend/app/services/community_rules.py`
- `backend/app/services/street_graph.py`
- `backend/app/services/parceling.py`
- `backend/app/services/layout_validation.py`
- `backend/app/services/community_prompt.py`

### Module responsibilities

#### `community_rules.py`

This module owns hard planning defaults and zoning-compatible constraints.

Core functions:

```python
def resolve_rule_profile(
    zone_type: str,
    zone_properties: dict,
    system_selections: dict[str, dict],
) -> dict:
    ...

def compute_setback_profile(
    development_type: str,
    street_hierarchy: str | None,
    adjacency: dict | None = None,
) -> dict:
    ...

def compute_lot_coverage_limit(
    development_type: str,
    subcategory: str | None = None,
) -> float:
    ...

def minimum_frontage_for_building_type(
    development_type: str,
    building_subcategory: str | None = None,
) -> float:
    ...
```

#### `street_graph.py`

This module owns street and pathway topology generation and corridor geometry.

Core functions:

```python
def generate_street_graph(
    boundary_polygon,
    properties: dict,
    street_selections: list[dict],
    existing_lines: list | None = None,
) -> dict:
    ...

def compute_connectivity_indices(nodes: list, edges: list) -> dict:
    ...

def classify_street_segments(graph: dict, properties: dict) -> list[dict]:
    ...

def build_right_of_way_geometry(
    centerlines: list[dict],
    center_lat: float,
) -> list[dict]:
    ...

def normalize_intersections(
    segments: list[dict],
    min_angle_deg: float = 75.0,
) -> list[dict]:
    ...
```

#### `parceling.py`

This module owns block extraction and parcel subdivision.

Core functions:

```python
def extract_blocks_from_corridors(boundary_polygon, corridor_polygons: list) -> list:
    ...

def subdivide_block(
    block_polygon,
    strategy: str,
    target_count: int,
    constraints: dict,
) -> list[dict]:
    ...

def obb_subdivide(block_polygon, constraints: dict) -> list[dict]:
    ...

def straight_skeleton_subdivide(block_polygon, constraints: dict) -> list[dict]:
    ...

def generate_buildable_envelope(parcel_polygon, setback_profile: dict):
    ...
```

#### `layout_validation.py`

This module owns all final checks.

Core functions:

```python
def validate_layout_scene(
    boundary_polygon,
    buildings: list[dict],
    roads: list[dict],
    green_spaces: list[dict],
    constraints: dict,
) -> list[dict]:
    ...

def validate_building_collisions(buildings: list[dict]) -> list[dict]:
    ...

def validate_street_access(parcels: list[dict], roads: list[dict]) -> list[dict]:
    ...

def validate_walkability(
    residential_units: list[dict],
    parks: list[dict],
    pedestrian_graph: dict,
    max_walk_distance_m: float = 900.0,
) -> list[dict]:
    ...
```

#### `community_prompt.py`

This module should translate a validated scene into downstream prompts.

Core functions:

```python
def build_3d_scene_prompt(
    zone,
    layout: dict,
    system_style_inputs: dict[str, dict],
    site_context: dict | None = None,
) -> str:
    ...

def build_2d_master_plan_prompt(
    boundary_zone,
    layout_bundle: dict,
    style_preset: str,
    render_mode: str,
) -> str:
    ...
```

## Phase 3: Layout Planner Refactor

### Goal

Refactor `backend/app/services/layout_planner.py` so it becomes an orchestrator over explicit generation phases.

### Current problem

`LayoutPlanner` currently mixes:

- AI prompt generation
- algorithmic fallback
- layout assembly
- image generation

into one large service.

### Target orchestration flow

```python
class LayoutPlanner:
    async def generate_layout(...):
        envelope = self._build_generation_envelope(...)
        rule_profile = resolve_rule_profile(...)
        street_result = generate_street_graph(...)
        corridor_result = build_right_of_way_geometry(...)
        block_result = extract_blocks_from_corridors(...)
        parcel_result = subdivide_blocks_for_program(...)
        civic_result = allocate_civic_spaces(...)
        building_result = place_buildings(...)
        validation_result = validate_layout_scene(...)
        return assemble_layout_response(...)
```

### New internal functions to add inside `layout_planner.py`

```python
def _build_generation_envelope(
    zone_polygon,
    zone_type: str,
    properties: dict,
    neighbors: list[dict] | None,
) -> dict:
    ...

def _resolve_system_style_inputs(properties: dict) -> dict:
    ...

def _allocate_civic_spaces(
    blocks: list[dict],
    pedestrian_graph: dict,
    properties: dict,
    style_inputs: dict,
) -> list[dict]:
    ...

def _place_buildings_from_parcels(
    parcels: list[dict],
    properties: dict,
    style_inputs: dict,
) -> list[LayoutBuilding]:
    ...

def _assemble_layout_response(
    buildings: list[LayoutBuilding],
    roads: list[LayoutRoad],
    green_spaces: list[LayoutGreenSpace],
    diagnostics: list[dict],
    strategy: str,
) -> SiteLayoutResponse:
    ...
```

### Important behavior change

AI should no longer be trusted to invent core geometry from scratch when the user has already given structured site intent. AI should assist with:

- choosing strategy families
- filling missing defaults
- producing descriptions and visual prompts
- image generation

But geometry must primarily be derived through rules and validated math.

## Phase 4: Block Editor Integration

### Goal

Make the Block Editor the editable view of the procedural community scene, not just a building editor with extra shapes.

### Files to modify

- `frontend/src/features/block-editor/EmbeddedBlockEditor.tsx`
- `frontend/src/features/block-editor/BlockPropertiesPanel.tsx`
- `frontend/src/features/block-editor/BlockEditorCanvas.tsx`
- `frontend/src/features/block-editor/StatsPanel.tsx`
- `frontend/src/store/blockEditorStore.ts`

### Required behavior

- Buildings, streets/paths, and parks/plazas all appear as first-class editable scene elements.
- Archetype image selection updates visible defaults immediately.
- The Block Editor stores whether a value is:
  - system-derived
  - user-overridden
- Scene validation warnings are visible but lightweight.

### Store additions

`blockEditorStore.ts` should grow:

```ts
interface BlockEditorState {
  sceneDiagnostics: ValidationNote[];
  systemSelections: {
    building?: GenerationStyleInput;
    streets_paths?: GenerationStyleInput;
    parks?: GenerationStyleInput;
    plazas?: GenerationStyleInput;
  };
  userOverrides: Record<string, string[]>;
  replaceEditedLayout: (layout: LayoutOption) => void;
  setSceneDiagnostics: (notes: ValidationNote[]) => void;
  setSystemSelection: (domain: CommunitySystemType, input: GenerationStyleInput) => void;
}
```

### UI behavior examples

If the user selects `Historic Brownstone`:

- `facade_material` defaults to `brick`
- `floors` defaults to `4`
- `roof_style` defaults to `flat`
- frontage behavior shifts toward continuous streetwall alignment
- the 3D prompt and 2D plan style metadata include the chosen archetype

If the user selects `Kyoto Philosopher's Walk`:

- `transport_modes` shifts toward `walking`
- corridor type becomes pedestrian-first
- narrow path + water edge + planted canopy + low auto priority defaults are applied

If the user selects `English Landscape Park`:

- `space_type` stays `park`
- planting density increases
- paths become curvilinear
- open-lawn and tree-cluster distribution hints are stored in style metadata

## Phase 5: Save and Generation Payload Enrichment

### Goal

Ensure archetype-informed scene data survives from Block Editor to backend persistence to generation.

### Primary backend file

- `backend/app/api/v1/site_zones.py`

### Save-layout changes

`save_layout()` should:

1. store the full `SiteLayoutResponse`
2. derive scoped `generation_style_inputs` for:
   - `building`
   - `streets_paths`
   - `parks`
   - `plazas`
3. write summary scene metadata back into zone properties
4. preserve element-level metadata for downstream 2D and 3D pipelines

### New helper functions to add

```python
def _collect_layout_generation_inputs(layout: SiteLayoutResponse) -> dict:
    ...

def _summarize_layout_systems(layout: SiteLayoutResponse) -> dict:
    ...

def _merge_layout_style_metadata(props: dict, layout: SiteLayoutResponse) -> dict:
    ...
```

### Prompt composition changes

`compose_zone_prompt()` should be split or slimmed so it consumes structured scene metadata instead of reconstructing too much from loose properties.

It should explicitly describe:

- street hierarchy and character
- parks/plazas and their civic role
- building frontage and material logic
- adjacency relationships
- archetype selections per system

## Phase 6: Premium 2D Master Plan Pipeline

### Goal

Implement the hybrid `map-design-render-refine` pipeline for master plans.

This should be treated as a distinct product pipeline from raw layout generation.

### Research integration summary

The provided Gemini research is directionally correct:

- the LLM should preserve geometry and prepare a structured design representation
- a vision-language pass should extract style information from reference images
- an image-generation model should render textures while respecting geometry
- vector overlays should be added after raster generation for crisp labels and markers
- shared cartographic knowledge should live in a reusable local knowledge base rather than in one-off prompt text

### Local knowledge base

Use the repo-local master-plan knowledge base at `docs/master-plan-design-knowledge-base.md` and `backend/app/services/master_plan_design_knowledge.py` as the common source for:

- 2D figure-ground hierarchy
- landscape-led block composition
- restrained context treatment
- LBCS-informed land-use color logic
- 3D and aerial scene placemaking guidance

### Repo integration points

- `backend/app/services/master_plan_2d.py`
- `backend/app/api/v1/master_plan_2d.py`
- `frontend/src/features/projects/MasterPlan2DPanel.tsx`

### Target pipeline

#### Stage A: Geometry map

Generate a clean geometry-preserving master-plan base from:

- saved layout
- site boundary
- road corridors
- buildings
- parks/plazas

Output:

- SVG or structured 2D scene JSON

#### Stage B: Style guide extraction

Build a style guide from:

- selected archetype images
- chosen style preset
- optional user-selected reference boards

Output:

```json
{
  "palette": ["#e6e6e0", "#6e8b5d", "#4b5f74"],
  "treeCanopyStyle": "soft planimetric canopy with subtle shadow",
  "waterStyle": "deep blue reflective pond with crisp embankment edge",
  "buildingStyle": "clean orthographic white massing with soft roof shadow",
  "pathStyle": "light concrete path with subtle ambient occlusion"
}
```

#### Stage C: Guided raster rendering

Feed:

- geometry map
- style guide
- system archetype metadata
- prompt preset

into Gemini image generation or later ControlNet-compatible rendering.

Gemini should be used for:

- premium aerial render variants
- texture and atmosphere generation
- master-plan scene polish

### Important product rule

Gemini should not invent geometry. It should render from a geometry-anchored scene representation produced by backend layout code.

#### Stage D: Vector overlay refinement

Apply a post-render SVG overlay for:

- callouts
- numbered markers
- labels
- north arrow
- scale bar
- legend

This should stay deterministic and vector crisp.

### Suggested additions to `master_plan_2d.py`

```python
def build_master_plan_scene(project_id: str) -> dict:
    ...

def build_master_plan_style_guide(project_id: str, selected_images: list[str]) -> dict:
    ...

def render_master_plan_variant(scene: dict, style_guide: dict, preset: str) -> dict:
    ...

def build_master_plan_overlay(scene: dict, options: dict) -> str:
    ...
```

## Phase 7: 3D Generation Pipeline

### Goal

Use structured community scene data to inform 3D generation, not just building-by-building prompts.

### Current gap

`generate-all` in `site_zones.py` still mainly queues building generation with zone prompts. It needs to include community context as first-class input.

### Target behavior

3D generation should consume:

- selected building archetype
- selected street/pathway archetypes
- selected park/plaza archetypes
- validated scene geometry
- adjacency and frontage information
- material defaults and public-realm hints

### New structured scene payload

```python
{
  "buildings": [...],
  "roads": [...],
  "green_spaces": [...],
  "generation_style_inputs": {
    "building": {...},
    "streets_paths": {...},
    "parks": {...},
    "plazas": {...}
  },
  "scene_relationships": {
    "frontages": [...],
    "intersections": [...],
    "park_edges": [...]
  },
  "validation_summary": [...]
}
```

### Integration target

- `backend/app/tasks/processing.py`
- `backend/app/services/reusable_model_library.py`

## Phase 8: Reusable Asset Library

### Goal

Avoid regenerating identical or near-identical 3D content.

### Separate the libraries

The system should keep three distinct libraries:

1. Archetype image library
2. Style metadata library
3. Reusable generated 3D asset library

### Matching inputs

Asset reuse should match on:

- domain
- development type
- archetype id
- subtype
- style profile
- dimensions or size bucket
- material tags
- frontage type

### Core functions

```python
def compute_asset_signature(scene_element: dict) -> str:
    ...

def find_reusable_asset(scene_element: dict, library_entries: list[dict]) -> dict | None:
    ...

def register_generated_asset(scene_element: dict, result: dict) -> dict:
    ...
```

## Hard Constraints vs Soft Guidance

### Hard constraints

These must live in procedural code and validation modules:

- planar street graph integrity
- no self-intersecting polygons
- no overlapping buildings/roads/parks
- setback enforcement
- frontage alignment
- lot coverage
- minimum frontage width
- right-of-way dimensions
- intersection angle minimums
- walkability coverage
- park/plaza street access
- site-boundary containment

### Soft guidance

These should come from archetype metadata and user selection:

- brownstone vs Nordic vs alpine
- boulevard vs woonerf vs promenade
- English landscape vs Zen court vs civic plaza
- material palette
- roof form
- facade rhythm
- paving language
- planting character
- rendering mood

## Recommended Implementation Order

### Milestone 1

Upgrade schemas and save payloads.

Files:

- `frontend/src/types/index.ts`
- `backend/app/schemas/schemas.py`
- `backend/app/api/v1/site_zones.py`

### Milestone 2

Make Block Editor fully community-aware and archetype-driven for buildings, streets, and parks/plazas.

Files:

- `frontend/src/features/block-editor/BlockPropertiesPanel.tsx`
- `frontend/src/features/block-editor/EmbeddedBlockEditor.tsx`
- `frontend/src/store/blockEditorStore.ts`

### Milestone 3

Extract procedural rules into backend services.

Files:

- `backend/app/services/community_rules.py`
- `backend/app/services/street_graph.py`
- `backend/app/services/parceling.py`
- `backend/app/services/layout_validation.py`

### Milestone 4

Refactor `layout_planner.py` into a staged orchestrator using those services.

### Milestone 5

Refactor 2D master plan generation into geometry map + style guide + raster render + vector overlay.

Files:

- `backend/app/services/master_plan_2d.py`
- `backend/app/api/v1/master_plan_2d.py`
- `frontend/src/features/projects/MasterPlan2DPanel.tsx`

### Milestone 6

Integrate reusable 3D asset matching into scene generation.

Files:

- `backend/app/services/reusable_model_library.py`
- `backend/app/tasks/processing.py`

## Immediate Next Build Step

The best next implementation step is not rendering polish. It is schema and persistence.

Specifically:

1. extend `LayoutBuilding`, `LayoutRoad`, and `LayoutGreenSpace` in `backend/app/schemas/schemas.py`
2. mirror those richer types in `frontend/src/types/index.ts`
3. update `save_layout()` in `backend/app/api/v1/site_zones.py` to preserve structured `generation_style_input` for all systems
4. make Block Editor read and write those fields cleanly

Without that foundation, the street, park, and master-plan pipelines will remain prompt-heavy and fragile.

