// =============================================================================
// Core Types for the 3D Development Platform
// =============================================================================

export interface Location {
  latitude: number;
  longitude: number;
  address?: string;
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

// =============================================================================
// Site Zone Types
// =============================================================================

export type SiteZoneType = 'site_boundary' | 'building' | 'residential' | 'road' | 'green_space' | 'parking' | 'water' | 'development_area';

export interface LayoutRoadData {
  centerline: number[][];  // [[x_offset_deg, y_offset_deg], ...]
  width_m: number;
  road_type: string;
}

export interface LayoutGreenSpaceData {
  polygon: number[][];  // [[x_offset_deg, y_offset_deg], ...]
  space_type: string;
}

export interface SiteZoneProperties {
  height?: number;
  floors?: number;
  floor_height?: number;
  tree_density?: number;
  width?: number;
  unit_count?: number;
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
}

export interface LayoutPreviewResponse {
  options: LayoutOption[];
  zone_id: string;
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

export interface ZoneTypeConfig {
  label: string;
  color: string;
  icon: string;
  defaultProperties: SiteZoneProperties;
}

export const ZONE_TYPE_CONFIG: Record<SiteZoneType, ZoneTypeConfig> = {
  site_boundary: {
    label: 'Site Boundary',
    color: '#f59e0b',
    icon: 'S',
    defaultProperties: {},
  },
  building: {
    label: 'Building',
    color: '#9b59b6',
    icon: 'B',
    defaultProperties: { height: 30, floors: 10, floor_height: 3 },
  },
  residential: {
    label: 'Residential',
    color: '#e91e8a',
    icon: 'R',
    defaultProperties: { height: 12, floors: 4, floor_height: 3 },
  },
  road: {
    label: 'Road',
    color: '#444444',
    icon: 'D',
    defaultProperties: { width: 10 },
  },
  green_space: {
    label: 'Green Space',
    color: '#27ae60',
    icon: 'G',
    defaultProperties: { tree_density: 0.3 },
  },
  parking: {
    label: 'Parking/Plaza',
    color: '#95a5a6',
    icon: 'P',
    defaultProperties: {},
  },
  water: {
    label: 'Water',
    color: '#3498db',
    icon: 'W',
    defaultProperties: {},
  },
  development_area: {
    label: 'Development Area',
    color: '#d4a574',
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
  description?: string;
  location?: Location;
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
