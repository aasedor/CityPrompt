// =============================================================================
// Core Types for the 3D Development Platform
// =============================================================================

export interface Location {
  latitude: number;
  longitude: number;
  address?: string | null;
}

export interface ConstructionPhase {
  phase_number: number;
  name: string;
  start_date?: string;
  end_date?: string;
  color?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  location?: Location;
  status: 'draft' | 'processing' | 'ready' | 'archived';
  construction_phases?: ConstructionPhase[];
  created_at: string;
  updated_at: string;
  owner_id: string;
  owner_email?: string;
  buildings?: Building[];
  documents?: Document[];
}

export interface Building {
  id: string;
  project_id: string;
  name?: string;
  height_meters?: number;
  floor_count?: number;
  floor_height_meters?: number;
  roof_type?: string;
  construction_phase?: number;
  model_url?: string;
  lod_urls?: Record<string, string>;
  specifications?: BuildingSpecifications;
  generation_status?: string;
  generation_prompt?: string;
  meshy_task_id?: string;
  footprint_coordinates?: number[][];
  rotation_degrees?: number;
  architectural_style?: string;
  preview_url?: string;
  preview_status?: string;
  generation_engine?: string;
  created_at: string;
}

export interface BuildingSpecifications {
  total_area_sqm?: number;
  residential_units?: number;
  commercial_area_sqm?: number;
  ai_confidence?: number;
  [key: string]: unknown;
}

export interface SavedRender {
  id: string;
  image_url: string;
  prompt: string;
  style?: string;
  seed?: number;
  model?: string;
  image_quality?: 'auto' | 'low' | 'medium' | 'high';
  created_at: string;
}

export interface Document {
  id: string;
  project_id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  uploaded_at: string;
  processed_at?: string;
}

export interface ProcessingStatus {
  job_id: string;
  status: string;
  progress?: number;
  message?: string;
  result?: Record<string, unknown>;
}

export interface CustomStyleUsedDocument {
  id: string;
  filename: string;
  status: string;
  chars_used: number;
}

export interface CustomStyleExpandResponse {
  expanded_prompt: string;
  model: string;
  used_documents: CustomStyleUsedDocument[];
  truncated: boolean;
}

// =============================================================================
// Site Zone Types
// =============================================================================

export type SiteZoneType = 'site_boundary' | 'building' | 'residential' | 'road' | 'green_space' | 'parking' | 'water' | 'development_area';

export interface LayoutRoadData {
  centerline: number[][];  // [[x_offset_deg, y_offset_deg], ...]
  width_m: number;
  road_type: string;
  name?: string;
  description?: string;
}

export interface LayoutGreenSpaceData {
  polygon: number[][];  // [[x_offset_deg, y_offset_deg], ...]
  space_type: string;
  name?: string;
  description?: string;
}

export type CustomStyleDomain = 'building' | 'open_space' | 'street';

export interface CustomStyleAttachment {
  document_id: string;
  filename: string;
  file_type: string;
  kind: 'photo' | 'pdf';
  url: string;
}

export interface SiteZoneProperties {
  height?: number;
  floors?: number;
  floor_height?: number;
  tree_density?: number;
  width?: number;
  unit_count?: number;
  custom_style_enabled?: boolean;
  custom_style_domain?: CustomStyleDomain;
  custom_style_prompt?: string;
  custom_style_expanded_prompt?: string;
  custom_style_expanded_at?: string;
  custom_style_expansion_hash?: string;
  custom_style_expanded_edited?: boolean;
  custom_style_attachments?: CustomStyleAttachment[];
  _layout_strategy?: string;
  _layout_reasoning?: string;
  _layout_roads?: LayoutRoadData[];
  _layout_green_spaces?: LayoutGreenSpaceData[];
  _layout_density?: number;
  _osm_context?: OSMContext;
  [key: string]: unknown;
}

// =============================================================================
// Layout Preview Types
// =============================================================================

export interface LayoutBuildingData {
  center_x: number;
  center_y: number;
  width_m: number;
  depth_m: number;
  rotation_deg: number;
  height_m?: number;
  floors?: number;
  building_type: string;
  building_typology?: string;
  block_id?: number;
  setback_front_m: number;
  setback_side_m: number;
  name?: string;
  description?: string;
  style?: string;
}

export interface LayoutOption {
  option_index: number;
  option_label: string;
  buildings: LayoutBuildingData[];
  roads: LayoutRoadData[];
  green_spaces: LayoutGreenSpaceData[];
  layout_strategy: string;
  reasoning: string;
  density_achieved?: number;
  orientation_deg?: number;
  orientation_mode?: string;
}

export interface LayoutPreviewResponse {
  options: LayoutOption[];
  zone_id: string;
}

// =============================================================================
// Site Massing Types (whole-site, multi-zone)
// =============================================================================

export interface SiteMassingZone {
  zone_id: string;
  zone_type: string;
  zone_label: string;
  buildings: LayoutBuildingData[];
  roads: LayoutRoadData[];
  green_spaces: LayoutGreenSpaceData[];
}

export interface SiteMassingOption {
  option_index: number;
  option_label: string;
  zones: SiteMassingZone[];
  reasoning: string;
  total_building_count: number;
  total_floor_area_m2?: number;
  density_achieved?: number;
}

export interface SiteMassingResponse {
  project_id: string;
  options: SiteMassingOption[];
}

export type MasterPlan2DStylePreset = 'auto' | 'rendered_sales_plan' | 'hybrid_annotated_master_plan' | 'illustrative_landscape_plan';
export type MasterPlan2DQualityLevel = 'draft' | 'presentation' | 'board_ready';
export type MasterPlan2DStylePassProvider = 'auto' | 'gemini' | 'stability';
export type MasterPlan2DRenderMode = 'orthographic_aerial_site_insert' | 'legacy_prompt_first';
export type MasterPlanRenderStylePreset =
  | 'photorealistic_aerial'
  | 'photoreal_orthographic_aerial'
  | 'digital_watercolor_map'
  | 'watercolor_wash'
  | 'ink_line_drawing'
  | 'marker_render'
  | 'cinematic_dusk'
  | 'collage_mixed_media'
  | 'lush_landscape'
  | 'white_massing_model'
  | 'flat_diagrammatic';
export type MasterPlanLightingAtmospherePreset = 'crisp_summer_day' | 'golden_hour' | 'overcast_soft' | 'winter_snow';
export type MasterPlanImageProvider = 'vertex' | 'stability' | 'gemini';

export interface MasterPlanMapBounds {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface MasterPlan2DReferenceMetadata {
  reference_id?: string;
  zone_id: string;
  zone_name?: string;
  zone_type: string;
  domain?: string;
  category?: string;
  subcategory?: string;
  archetype_name?: string;
  asset_id?: string;
  image_url: string;
  image_path?: string;
  source: 'zone_prompt' | 'archetype' | 'reference_image';
  source_label: string;
  prompt_text?: string;
  caption?: string;
  tags?: string[];
  selection_order?: number;
  style_profile?: Record<string, unknown>;
  generation_style?: Record<string, unknown>;
}

export interface MasterPlan2DGenerateRequest {
  render_mode?: MasterPlan2DRenderMode;
  prompt?: string;
  render_style_preset?: MasterPlanRenderStylePreset;
  lighting_atmosphere_preset?: MasterPlanLightingAtmospherePreset;
  specific_overrides?: string;
  option_count?: number;
  style_preset?: MasterPlan2DStylePreset;
  quality_level?: MasterPlan2DQualityLevel;
  show_legend?: boolean;
  show_north_arrow?: boolean;
  show_scale_bar?: boolean;
  show_callout_markers?: boolean;
  show_surrounding_context?: boolean;
  export_width?: number;
  map_screenshot_satellite?: string;
  map_screenshot_bounds?: MasterPlanMapBounds;
  reference_images?: string[];
  reference_metadata?: MasterPlan2DReferenceMetadata[];
  selected_image_urls?: string[];
  ai_style_pass_enabled?: boolean;
  ai_style_pass_provider?: MasterPlan2DStylePassProvider;
  compose_board?: boolean;
  board_template?: 'master_plan_board_v1';
  include_photo_strip?: boolean;
  debug?: boolean;
}

export interface MasterPlan2DOption {
  id: string;
  project_id: string;
  label: string;
  style_preset: Exclude<MasterPlan2DStylePreset, 'auto'>;
  style_name: string;
  variant_index: number;
  preview_url: string;
  preview_png_url: string;
  full_png_url?: string;
  svg_url?: string;
  plan_preview_png_url?: string;
  plan_full_png_url?: string;
  plan_svg_url?: string;
  debug_png_url?: string;
  is_selected: boolean;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface MasterPlan2DGenerateResponse {
  project_id: string;
  options: MasterPlan2DOption[];
}

export interface MasterPlan2DSelectResponse {
  status: string;
  project_id: string;
  selected_option_id: string;
}

export interface MasterPlan2DExportResponse {
  option_id: string;
  project_id: string;
  label: string;
  style_preset: Exclude<MasterPlan2DStylePreset, 'auto'>;
  style_name: string;
  width: number;
  height: number;
  svg: string;
  preview_png_url?: string;
  full_png_url?: string;
  svg_url?: string;
  plan_preview_png_url?: string;
  plan_full_png_url?: string;
  plan_svg_url?: string;
  debug_png_url?: string;
}

export type MasterPlan3DScenePerspective = 'aerial_oblique' | 'street_level_eye_height' | 'corner_perspective' | 'promenade_view';
export type MasterPlan3DLightingVariant = 'golden_hour' | 'clear_daylight' | 'overcast_soft_light' | 'blue_hour_dusk';
export type MasterPlan3DScope = 'full_site' | 'selected_zones' | 'focused_frontage';

export interface MasterPlan3DZoneSnapshot {
  zone_id: string;
  zone_label?: string;
  zone_type: SiteZoneType;
  color?: string;
  polygon: number[][];
  height_m?: number;
  floor_count?: number;
  archetype_title?: string;
  archetype_metadata?: Record<string, unknown>;
  user_notes?: string;
}
export interface MasterPlan3DGenerateRequest {
  render_style_preset?: MasterPlanRenderStylePreset;
  lighting_atmosphere_preset?: MasterPlanLightingAtmospherePreset;
  specific_overrides?: string;
  selected_perspective?: MasterPlan3DScenePerspective;
  lighting_variant?: MasterPlan3DLightingVariant;
  scope?: MasterPlan3DScope;
  selected_zone_ids?: string[];
  zones?: MasterPlan3DZoneSnapshot[];
  global_style_notes?: string;
}

export interface MasterPlan3DFootprintReference {
  source_zone_label: string;
  geometry_type: string;
}

export interface MasterPlan3DFootprintGeometry {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface MasterPlan3DRendererNotes {
  keep_footprint_alignment: boolean;
  recommended_condition_strength: number;
  geometry_priority: 'high';
  style_override_applied: boolean;
  avoid: string[];
}

export interface MasterPlan3DConditioningAssets {
  structure_image_url?: string;
  depth_map_url?: string;
  segmentation_map_url?: string;
  massing_image_url?: string;
  perspective_structure_image_url?: string;
  perspective_depth_map_url?: string;
  perspective_segmentation_map_url?: string;
  perspective_massing_image_url?: string;
  camera_perspective?: string;
  control_mode?: string;
  control_strength?: number;
}

export interface MasterPlan3DRenderPackage {
  scene_id: string;
  zone_id: string;
  zone_label: string;
  zone_type: SiteZoneType;
  archetype_title: string;
  height_m: number;
  floor_count: number;
  footprint_reference: MasterPlan3DFootprintReference;
  footprint_geometry: MasterPlan3DFootprintGeometry;
  archetype_metadata: Record<string, unknown>;
  user_notes?: string;
  render_prompt: string;
  renderer_notes: MasterPlan3DRendererNotes;
  source_concept_image_url?: string;
  source_concept_asset_id?: string;
  conditioning_assets?: MasterPlan3DConditioningAssets;
  provider: MasterPlanImageProvider;
  model: string;
  prompt_type: string;
  job_type: '3d';
  render_image_url?: string;
}

export interface MasterPlan3DPackageWarning {
  zone_id?: string;
  zone_label?: string;
  reason: string;
}

export interface MasterPlan3DRendererAdapter {
  status: string;
  provider: string;
  integration_status: string;
  notes: string;
}

export interface MasterPlanProviderRouting {
  two_d_image_provider: MasterPlanImageProvider;
  three_d_image_provider: MasterPlanImageProvider;
}

export interface MasterPlan3DGenerateResponse {
  site_id: string;
  option_id: string;
  source_option_label: string;
  selected_perspective: MasterPlan3DScenePerspective;
  lighting_variant: MasterPlan3DLightingVariant;
  scope: MasterPlan3DScope;
  selected_zone_ids: string[];
  global_style_notes?: string;
  render_style_preset: MasterPlanRenderStylePreset;
  lighting_atmosphere_preset: MasterPlanLightingAtmospherePreset;
  specific_overrides?: string;
  global_style_payload?: string;
  source_concept_image_url?: string;
  provider_routing: MasterPlanProviderRouting;
  render_packages: MasterPlan3DRenderPackage[];
  skipped_zones: MasterPlan3DPackageWarning[];
  renderer_adapter: MasterPlan3DRendererAdapter;
  created_at: string;
}

// =============================================================================
// OSM Context Types
// =============================================================================

export interface OSMContextBuilding {
  osm_id: number;
  coordinates: number[][];
  height_m?: number;
  building_type: string;
  name?: string;
  levels?: string;
}

export interface OSMContextRoad {
  osm_id: number;
  coordinates: number[][];
  width_m: number;
  road_type: string;
  name?: string;
  surface?: string;
  lanes?: string;
}

export interface OSMContextFeature {
  osm_id: number;
  coordinates: number[][];
  feature_type: string;
  name?: string;
}

export interface OSMContext {
  buildings: OSMContextBuilding[];
  roads: OSMContextRoad[];
  water: OSMContextFeature[];
  parks: OSMContextFeature[];
  fetched_at: string;
  buffer_m: number;
}

export interface PreviewHistoryEntry {
  image_url: string;
  label: string;
  strategy: string;
  created_at: string;
  preview_type: 'layout' | 'site';
  option_index: number;
  layout_data?: LayoutOption | { zone_layouts: Record<string, LayoutOption> };
}

export interface LockedLayers {
  roads: number[];
  buildings: number[];
  green_spaces: number[];
}

export interface SiteZone {
  id: string;
  project_id: string;
  name?: string;
  zone_type: SiteZoneType;
  coordinates: number[][]; // [[lng, lat], ...]
  color: string;
  properties?: SiteZoneProperties;
  sort_order: number;
  building_id?: string;
  building_ids?: string[];
  created_at: string;
  updated_at: string;
}

export interface ZoneHistoryEntry {
  id: string;
  zone_id: string;
  project_id: string;
  action: 'create' | 'update' | 'delete';
  snapshot: SiteZone & Record<string, unknown>;
  previous_snapshot?: (SiteZone & Record<string, unknown>) | null;
  user_id?: string;
  user_email?: string;
  description?: string;
  created_at: string;
}

export interface ZoneHistoryListResponse {
  items: ZoneHistoryEntry[];
  total: number;
  has_more: boolean;
}

export interface ZoneSnapshotRestoreResponse {
  zone_id: string;
  deleted: boolean;
  zone?: SiteZone | null;
}

export interface ZoneTypeConfig {
  label: string;
  color: string;
  icon: string;
  defaultProperties: SiteZoneProperties;
}

/**
 * GIS Standard Land Use Colors — based on APA/LBCS color conventions
 * (American Planning Association, "Traditional Color Coding for Land Uses", 1997)
 *
 * Residential:   Yellows (#F5D63D)
 * Commercial:    Reds    (#E03C31)
 * Open Space:    Greens  (#4CAF50)
 * Transportation: Grays  (#616161)
 * Institutional: Blues   (#4A90D9)
 * Mixed Use:     Purple  (#9C27B0)
 */
export const ZONE_TYPE_CONFIG: Record<SiteZoneType, ZoneTypeConfig> = {
  site_boundary: {
    label: 'Site Boundary',
    color: '#F59E0B',
    icon: 'S',
    defaultProperties: {},
  },
  building: {
    label: 'Building',
    color: '#E03C31',       // APA Commercial Red — general/mixed-use buildings
    icon: 'B',
    defaultProperties: { height: 30, floors: 10, floor_height: 3 },
  },
  residential: {
    label: 'Residential',
    color: '#F5D63D',       // APA Residential Yellow
    icon: 'R',
    defaultProperties: { height: 12, floors: 4, floor_height: 3 },
  },
  road: {
    label: 'Streets and Paths',
    color: '#616161',       // APA Transportation Gray
    icon: 'D',
    defaultProperties: { width: 10 },
  },
  green_space: {
    label: 'Parks / Plazas',
    color: '#4CAF50',       // APA Open Space Green
    icon: 'G',
    defaultProperties: { tree_density: 0.3 },
  },
  parking: {
    label: 'Parking/Plaza',
    color: '#9E9E9E',       // APA Light Gray — utilities/parking
    icon: 'P',
    defaultProperties: {},
  },
  water: {
    label: 'Water',
    color: '#4A90D9',       // APA Institutional Blue (water)
    icon: 'W',
    defaultProperties: {},
  },
  development_area: {
    label: 'Development Area',
    color: '#C8A02A',       // APA Duplex/Medium-density Yellow-Brown
    icon: 'A',
    defaultProperties: { ground_texture: 'grass' },
  },
};

// =============================================================================
// Road Sub-Type Presets
// =============================================================================

export interface RoadPresetConfig {
  label: string;
  description: string;
  properties: SiteZoneProperties;
}

export const ROAD_PRESETS: RoadPresetConfig[] = [
  {
    label: 'Bike Lane',
    description: 'Cycling path',
    properties: {
      width: 3,
      lane_count: 1,
      road_aesthetic: 'pedestrian_focused',
      road_surface: 'asphalt',
      volume: 'low',
      has_sidewalks: false,
      pedestrian_priority: 2,
      cycling_priority: 1,
    },
  },
  {
    label: 'Local Street',
    description: 'Neighborhood road',
    properties: {
      width: 8,
      lane_count: 2,
      road_aesthetic: 'curvilinear_residential',
      road_surface: 'asphalt',
      volume: 'low',
      has_sidewalks: true,
      pedestrian_priority: 1,
      cycling_priority: 2,
      active_transport_priority: 3,
    },
  },
  {
    label: 'Collector',
    description: '2 lanes + parking',
    properties: {
      width: 14,
      lane_count: 2,
      road_aesthetic: 'neighborhood_high_street',
      road_surface: 'asphalt',
      volume: 'medium',
      has_sidewalks: true,
      pedestrian_priority: 2,
      cycling_priority: 3,
      active_transport_priority: 1,
    },
  },
  {
    label: 'Arterial',
    description: '4 lanes + median',
    properties: {
      width: 22,
      lane_count: 4,
      road_aesthetic: 'grand_boulevard',
      road_surface: 'asphalt',
      volume: 'high',
      has_sidewalks: true,
      pedestrian_priority: 3,
      transit_priority: 2,
      active_transport_priority: 1,
    },
  },
  {
    label: 'Boulevard',
    description: '6 lanes + median + sidewalks',
    properties: {
      width: 34,
      lane_count: 6,
      road_aesthetic: 'grand_boulevard',
      road_surface: 'asphalt',
      volume: 'high',
      has_sidewalks: true,
      pedestrian_priority: 2,
      cycling_priority: 3,
      transit_priority: 1,
      active_transport_priority: 4,
    },
  },
];

// =============================================================================
// Building Sub-Type Presets
// =============================================================================

export interface BuildingPresetConfig {
  label: string;
  description: string;
  properties: SiteZoneProperties;
}

export const BUILDING_PRESETS: BuildingPresetConfig[] = [
  {
    label: 'Brownstone Row',
    description: 'Traditional rowhouse',
    properties: {
      development_type: 'residential',
      development_aesthetic: 'historic_traditional',
      floors: 4,
      height: 14,
      floor_height: 3.5,
      facade_material: 'brick',
      roof_type: 'flat',
    },
  },
  {
    label: 'Modern Apartment',
    description: 'Mid-rise residential',
    properties: {
      development_type: 'residential',
      development_aesthetic: 'modern',
      floors: 8,
      height: 28,
      floor_height: 3.5,
      facade_material: 'glass',
      roof_type: 'flat',
    },
  },
  {
    label: 'Office Tower',
    description: 'High-rise commercial',
    properties: {
      development_type: 'commercial',
      development_aesthetic: 'modern',
      floors: 20,
      height: 70,
      floor_height: 3.5,
      facade_material: 'glass',
      roof_type: 'flat',
    },
  },
  {
    label: 'Mixed-Use Retail',
    description: 'Retail + residential',
    properties: {
      development_type: 'mixed_use',
      development_aesthetic: 'modern',
      floors: 6,
      height: 22,
      floor_height: 3.67,
      facade_material: 'concrete',
      roof_type: 'flat',
    },
  },
  {
    label: 'Park / Plaza',
    description: 'Open public space',
    properties: {
      development_type: 'park_plaza',
    },
  },
  {
    label: 'Institutional',
    description: 'School, library, civic',
    properties: {
      development_type: 'institutional',
      development_aesthetic: 'historic_traditional',
      floors: 3,
      height: 14,
      floor_height: 4.67,
      facade_material: 'stone',
      roof_type: 'gabled',
    },
  },
];

// =============================================================================
// API Request Types
// =============================================================================

export interface CreateProjectRequest {
  name: string;
  description?: string;
  location?: Location;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string | null;
  location?: Location | null;
  status?: string;
}

export interface CreateBuildingRequest {
  name?: string;
  height_meters?: number;
  floor_count?: number;
  floor_height_meters?: number;
  roof_type?: string;
  construction_phase?: number;
  footprint_coordinates?: number[][];
  specifications?: Record<string, unknown>;
}

// =============================================================================
// 3D Viewer Types
// =============================================================================

export type MeasurementMode = 'distance' | 'area' | 'height' | 'angle';
export type MeasurementUnit = 'metric' | 'imperial';

export type CameraMode = 'orbit' | 'firstPerson' | 'flyThrough';

export type CameraPreset = 'aerial' | 'street' | 'corner' | 'front';

export interface CameraPresetConfig {
  position: [number, number, number];
  target: [number, number, number];
  label: string;
}

export interface ViewerSettings {
  cameraMode: CameraMode;
  showShadows: boolean;
  showGrid: boolean;
  showExistingBuildings: boolean;
  showLandscaping: boolean;
  showRoads: boolean;
  showMeasurements: boolean;
  sunTime: number; // 0-24
  sunDate: Date;
  mapLayer: 'none' | 'satellite' | 'streets' | 'terrain';
  quality: 'low' | 'medium' | 'high';
  showPerformance: boolean;
  showShadowStudy: boolean;
  activePhase: number | null; // null = show all phases
  moveSpeed: number; // multiplier: 0.25 (slow) to 3 (fast), default 1
  headBobEnabled: boolean;   // subtle head bob during walk movement
  showCrosshair: boolean;    // crosshair dot in walk/fly modes
  enablePostProcessing: boolean;
  enableFog: boolean;
  show3DTiles: boolean;
  mapMode: 'mapbox' | 'globe';
}

export interface SceneObject {
  id: string;
  type: 'building' | 'terrain' | 'road' | 'vegetation' | 'context';
  name: string;
  modelUrl?: string;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: [number, number, number];
  visible: boolean;
  metadata?: Record<string, unknown>;
}

// =============================================================================
// AI Generation Types
// =============================================================================

export interface GenerationStatus {
  status: string;
  progress?: number;
  step?: string;
  model_url?: string;
  preview_model_url?: string;
  error?: string;
  meshy_task_id?: string;
}

export interface AITemplate {
  id: string;
  name: string;
  category: string;
  prompt: string;
  thumbnail_url?: string;
}

// =============================================================================
// Architectural Style Types
// =============================================================================

export interface ArchitecturalStyle {
  id: string;
  name: string;
  description: string;
  facade_material: string;
  secondary_material: string;
  roof_material: string;
  preferred_roof_types: string[];
  prompt_prefix: string;
  meshy_art_style: string;
  thumbnail_url?: string;
  tags: string[];
}

// =============================================================================
// Render Preview Types
// =============================================================================

export interface RenderPreview {
  id: string;
  building_id: string;
  image_url: string;
  prompt?: string;
  style?: string;
  source_type: string;
  source_image_url?: string;
  created_at: string;
}

// =============================================================================
// Generation Engine Types
// =============================================================================

export interface GenerationEngine {
  id: string;
  name: string;
  description: string;
  available: boolean;
  features: string[];
}

// =============================================================================
// Model Library Types
// =============================================================================

export interface ModelLibraryEntry {
  id: string;
  owner_id: string;
  source_building_id?: string;
  source_project_id?: string;
  name: string;
  description?: string;
  category: string;
  tags?: string[];
  model_url: string;
  lod_urls?: Record<string, string>;
  thumbnail_url?: string;
  generation_prompt?: string;
  generation_engine?: string;
  architectural_style?: string;
  is_public: boolean;
  use_count: number;
  created_at: string;
}

// =============================================================================
// Boundary Analysis Types
// =============================================================================

export interface BoundaryContainedZone {
  id: string;
  name?: string;
  zone_type: SiteZoneType;
  color: string;
  properties: SiteZoneProperties;
  area_m2: number;
}

export interface BoundaryAnalysisResponse {
  boundary_zone_id: string;
  contained_zones: BoundaryContainedZone[];
  zone_summary: Record<string, number>;
  total_contained: number;
  osm_context: {
    buildings?: {
      count?: number;
      avg_height?: number;
      by_type?: Record<string, number>;
    };
    roads?: {
      count?: number;
      named_roads?: string[];
      by_type?: Record<string, number>;
    };
  };
}




















// =============================================================================
// Urban Intelligence DNA (backend/app/services/urban_dna)
// =============================================================================

/** Mirrors the backend ValidationNote — source_phase extends the layout-pipeline union. */
export interface UrbanDnaValidationNote {
  code: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
  source_phase:
    | 'street_graph' | 'row_geometry' | 'parceling' | 'civic_distribution'
    | 'zoning' | 'building_placement' | 'collision_validation'
    | 'city_connector' | 'spatial_engine' | 'policy_intelligence'
    | 'agent_deliberation' | 'coordinator';
}

export interface UrbanDnaField {
  value: unknown;
  unit?: string | null;
  confidence: number;
  source_datasets: string[];
  notes: string[];
}

export interface UrbanDnaSectionMeta {
  confidence: number;
  missing_datasets: string[];
  warnings: UrbanDnaValidationNote[];
}

export interface UrbanDnaSection {
  meta: UrbanDnaSectionMeta;
  fields: Record<string, UrbanDnaField>;
}

export const URBAN_DNA_SECTION_NAMES = [
  'site', 'land_use', 'mobility', 'public_realm',
  'environment', 'built_form', 'market', 'policy',
] as const;
export type UrbanDnaSectionName = (typeof URBAN_DNA_SECTION_NAMES)[number];

export interface UrbanDnaDocument {
  dna_schema_version: string;
  city_id: string;
  project_id: string;
  zone_id: string;
  generated_at: string;
  site: UrbanDnaSection;
  land_use: UrbanDnaSection;
  mobility: UrbanDnaSection;
  public_realm: UrbanDnaSection;
  environment: UrbanDnaSection;
  built_form: UrbanDnaSection;
  market: UrbanDnaSection;
  policy: UrbanDnaSection;
  overall_confidence: number;
  missing_datasets: string[];
  warnings: UrbanDnaValidationNote[];
}

export interface UrbanDnaSnapshotResponse {
  snapshot_id: string;
  zone_id: string;
  project_id: string;
  city_id: string;
  status: 'pending' | 'partial' | 'complete' | 'failed';
  dna_schema_version: string;
  dna?: UrbanDnaDocument | null;
  overall_confidence?: number | null;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface UrbanDnaGenerateResponse {
  snapshot_id: string;
  zone_id: string;
  status: string;
  city_id: string;
}

export interface UrbanDnaScenarioRow {
  id: string;
  snapshot_id: string;
  scenario_id: string;
  label: string;
  status: 'pending' | 'running' | 'complete' | 'failed';
  payload?: {
    plan_parameters?: Record<string, {
      parameter_path: string;
      value: unknown;
      rationale: string;
      contributors: string[];
      contested: boolean;
    }>;
    trade_offs?: UrbanDnaValidationNote[];
    expert_summaries?: Record<string, string>;
    explanation?: {
      baseline: string;
      changed_parameters: Array<{
        parameter_path: string;
        baseline_value: unknown;
        value: unknown;
        driven_by: string;
      }>;
      narrative: string;
    };
    usage?: { input_tokens?: number; output_tokens?: number; estimated_cost_usd?: number };
    warnings?: UrbanDnaValidationNote[];
    metrics?: {
      mode: 'parameter' | 'geometry';
      metrics: Record<string, {
        key: string;
        label: string;
        value: number | null;
        unit: string;
        derivation: string;
        assumptions: string[];
        confidence: number;
      }>;
      ceiling_reconciliation: Array<{
        district: string;
        area_pct_of_site?: number | null;
        ceiling_floors?: number | null;
        proposed_floors?: number | null;
        status: 'within' | 'exceeds' | 'unknown';
        source: string;
      }>;
      warnings: string[];
      assumptions_used: Record<string, { value: unknown; unit: string; note: string }>;
    } | null;
  } | null;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface UrbanDnaScenarioListResponse {
  snapshot_id?: string | null;
  scenarios: UrbanDnaScenarioRow[];
  available_presets: Array<{ scenario_id: string; label: string; description: string }>;
}

export interface UrbanDnaApplyScenarioResponse {
  zone_id: string;
  scenario_id: string;
  applied_parameters: Record<string, unknown>;
}
