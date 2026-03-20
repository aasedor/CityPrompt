/**
 * archetypeMetadataSchema.ts
 *
 * Complete metadata schema for all three archetype domains:
 * - Buildings (5-face render)
 * - Parks / Plazas (top-down + oblique render)
 * - Streets / Pathways (oblique render)
 *
 * Every field in this schema feeds directly into the AI render pipeline.
 * Accurate metadata = accurate renders.
 * Generic metadata = generic renders.
 *
 * REAL-WORLD SPECIFICATIONS
 * All dimensions and specifications in this file are based on
 * real-world standards so the AI generates correctly proportioned elements.
 */

// ─── SHARED TYPES ─────────────────────────────────────────────────────────────

export type Season = 'spring' | 'summer' | 'autumn' | 'winter';
export type TimeOfDay = 'morning' | 'midday' | 'afternoon' | 'golden-hour' | 'dusk';
export type ActivityDensity = 'quiet' | 'low' | 'medium' | 'high' | 'very-high';
export type FaceCount = 1 | 2 | 5;

export interface CaptureAngle {
  recommendedPitch: number;    // degrees
  recommendedZoom: number;     // Mapbox zoom level
  recommendedBearing?: number; // degrees, optional
}

export interface ImagePrompt {
  positive: string;  // 20+ words describing the archetype accurately
  negative: string;  // styles and elements to exclude
}

// ─── BUILDING SCHEMA ──────────────────────────────────────────────────────────

export type BuildingDevelopmentType =
  | 'residential-lowrise'
  | 'residential-highrise'
  | 'commercial'
  | 'mixed-use'
  | 'institutional'
  | 'industrial'
  | 'other';

export type RoofForm =
  | 'pitched-gabled'
  | 'pitched-hipped'
  | 'pitched-mansard'
  | 'flat-membrane'
  | 'flat-green-roof'
  | 'flat-terrace'
  | 'sawtooth'
  | 'curved'
  | 'distinctive-civic';

export interface RoofProfile {
  form: RoofForm;
  material: string;           // e.g. "clay tiles", "slate", "EPDM membrane"
  colour: string;             // e.g. "terracotta", "dark grey", "silver"
  features: string[];         // e.g. ["skylights", "solar panels", "green roof planting"]
  pitch?: number;             // degrees, for pitched roofs
  promptAddition: string;     // specific roof description for AI prompt
}

export interface FacadeProfile {
  primaryMaterial: string;
  secondaryMaterial?: string;
  colour: string;
  windowStyle: string;        // e.g. "punched openings", "curtain wall", "casement"
  windowRhythm: string;       // e.g. "regular grid", "vertical emphasis", "horizontal bands"
  groundFloor: string;        // e.g. "activated retail", "residential entry", "blank podium"
  entryChracter: string;      // e.g. "canopied entry", "recessed portal", "glazed lobby"
  balconies: boolean;
  balconyDescription?: string;
}

export interface FacePrompts {
  front: string;   // main entry, street activation, primary facade
  right: string;   // side facade character
  rear: string;    // private elevation, simplified treatment
  left: string;    // side facade character
  roof: string;    // rooftop form and material
}

export interface ScaleVariant {
  floors: string;            // e.g. "1-3"
  heightRange: string;       // e.g. "4-12m"
  ipAdapterStrength: number; // 0.3-0.9
  promptAddition: string;    // scale-specific description
  roofOverride?: string;     // override roof description at this scale
}

export interface FootprintVariant {
  widthRange: string;        // e.g. "0-20m"
  promptAddition: string;
  imageSize: { width: number; height: number };
}

export interface BuildingArchetypeMetadata {
  // ── Identity ────────────────────────────────────────────────────────────
  archetypeId: string;
  archetypeLabel: string;
  domain: 'building';
  developmentType: BuildingDevelopmentType;
  aestheticCategory: string;

  // ── AI Prompts ──────────────────────────────────────────────────────────
  imagePrompt: ImagePrompt;
  promptBooster: string;       // 20-30 words, most distinctive visual elements

  // ── Style Profile ───────────────────────────────────────────────────────
  styleProfile: {
    materials: string[];
    facadeRhythm: string;
    heightTendency: string;
    renderingMood: string;
    streetRelationship: string;
    articulation: string;
  };

  // ── Facade Character ────────────────────────────────────────────────────
  facadeProfile: FacadeProfile;

  // ── Roof ────────────────────────────────────────────────────────────────
  roofProfile: {
    byDevelopmentType: Record<BuildingDevelopmentType, RoofProfile>;
  };

  // ── 5-Face Render ───────────────────────────────────────────────────────
  faceCount: 5;
  facePrompts: FacePrompts;
  facadeConsistency: {
    primaryFacade: 'front';
    wrapsCorner: boolean;
    rearTreatment: string;     // how rear differs from front
    sideTreatment: string;     // side facade character
  };

  // ── Scale Variants ──────────────────────────────────────────────────────
  scaleVariants: {
    lowrise: ScaleVariant;     // 1-3 floors, up to 12m
    midrise: ScaleVariant;     // 4-8 floors, 12-28m
    highrise: ScaleVariant;    // 9-20 floors, 28-65m
    tower: ScaleVariant;       // 20+ floors, 65m+
  };

  // ── Footprint Variants ──────────────────────────────────────────────────
  footprintVariants: {
    narrow: FootprintVariant;  // 0-20m width
    standard: FootprintVariant;// 20-60m width
    wide: FootprintVariant;    // 60m+ width
  };

  // ── Capture ─────────────────────────────────────────────────────────────
  captureAngle: CaptureAngle;
  ipAdapterStrength: number;
  depthStrength: number;
}

// ─── PARK / PLAZA SCHEMA ──────────────────────────────────────────────────────

// Real-world sports court dimensions (metres)
export const SPORTS_COURT_DIMENSIONS = {
  tennis: {
    length: 23.77,
    width: 10.97,
    serviceBox: { length: 6.4, width: 4.115 },
    colour: 'hard court blue/green or clay red',
    surface: 'acrylic hard court / clay / grass',
    net: { height: 0.914, posts: 'white metal' },
    surround: '3-4m run-off each end, 2m sides',
    fence: '3.5m galvanised chain link',
    markings: 'white lines, doubles and singles',
    lighting: '6-8m column lights at corners',
    notes: 'Standard ITF dimensions. Allow 36.6m x 18.3m total including run-off.',
  },
  basketball: {
    length: 28,
    width: 15,
    threePointLine: { radius: 6.75 },
    keyArea: { length: 5.8, width: 4.9 },
    colour: 'maple wood / asphalt grey / coloured acrylic',
    surface: 'hardwood / asphalt / sport acrylic',
    hoops: { height: 3.05, backboardWidth: 1.83 },
    surround: '2m run-off each end, 1m sides',
    markings: 'white or yellow lines',
    notes: 'FIBA standard. Half-court = 14m x 15m.',
  },
  netball: {
    length: 30.5,
    width: 15.25,
    goalCircle: { radius: 4.9 },
    surface: 'asphalt / sport acrylic',
    posts: { height: 3.05 },
    markings: 'white lines',
    notes: 'INF standard dimensions.',
  },
  volleyball: {
    length: 18,
    width: 9,
    freeZone: '3m each end, 3m sides',
    net: { height: 2.43, width: 1 },
    surface: 'sand / sport acrylic / grass',
    markings: 'white lines',
    notes: 'FIVB standard. Total area 24m x 15m with free zone.',
  },
  futsal: {
    length: 40,
    width: 20,
    goalArea: { length: 6, width: 3.16 },
    penaltyArc: { radius: 6 },
    surface: 'sport acrylic / resin',
    goals: { width: 3, height: 2 },
    markings: 'white lines',
    notes: 'FIFA futsal standard.',
  },
  multiUseCourt: {
    typical: { length: 28, width: 15 },
    surface: 'sport acrylic, multiple colours',
    markings: 'basketball, netball, volleyball combined',
    notes: 'Combined court serves multiple sports.',
  },
  skatepark: {
    halfPipe: { width: 3.6, height: 1.2, length: 8 },
    quarterpipe: { width: 2.4, height: 1.2 },
    grindRail: { length: 3, height: 0.4 },
    surface: 'smooth concrete / skatelite',
    colour: 'bare concrete grey',
    notes: 'Dimensions vary by facility type.',
  },
  bowlingGreen: {
    rink: { length: 36.5, width: 5.5 },
    green: { typical: '36.5m x 36.5m — 6 rinks' },
    surface: 'close-cut grass / synthetic turf',
    colour: 'vivid green',
    surround: 'ditch 200mm wide, bank behind',
    notes: 'World Bowls standard green.',
  },
  cricketPitch: {
    pitch: { length: 20.12, width: 3.05 },
    outfield: { radius: 65 },
    surface: 'turf / synthetic',
    colour: 'light brown pitch, green outfield',
    notes: 'MCC standard. Outfield radius varies.',
  },
} as const;

// Real-world playground equipment dimensions
export const PLAYGROUND_EQUIPMENT = {
  toddler: {
    ageRange: '2-5 years',
    items: [
      'low slide (max 1.2m height)',
      'spring riders',
      'sandpit (0.6m depth)',
      'sensory panels',
      'low climbing frame',
    ],
    safetyZone: '1.8m from equipment edge',
    surfacing: 'rubber softfall / sand / wood chips',
    colour: 'primary colours — red, blue, yellow',
  },
  junior: {
    ageRange: '5-12 years',
    items: [
      'climbing structure (2-3m height)',
      'slide (medium)',
      'swings (standard seat)',
      'monkey bars',
      'balance beams',
      'flying fox if space allows',
    ],
    safetyZone: '2.4m from equipment edge',
    surfacing: 'rubber softfall / engineered wood chips',
    colour: 'natural tones with colour accents',
  },
  youth: {
    ageRange: '12-18 years',
    items: [
      'high climbing wall (3-4m)',
      'parkour elements',
      'outdoor fitness equipment',
      'large slide',
      'aerial runway',
    ],
    safetyZone: '2.4m from equipment edge',
    surfacing: 'rubber softfall under equipment',
    colour: 'neutral tones, industrial aesthetic',
  },
  allAges: {
    ageRange: 'all ages',
    items: [
      'accessible equipment (wheelchair compatible)',
      'sensory garden elements',
      'musical instruments',
      'nature play elements (logs, rocks, water)',
    ],
    safetyZone: '2.4m from equipment edge',
    surfacing: 'rubber matting for accessibility',
    colour: 'natural materials — timber, stone',
  },
} as const;

// Real-world park furniture dimensions
export const PARK_FURNITURE = {
  bench: {
    typical: { length: 1.8, depth: 0.6, seatHeight: 0.45 },
    materials: ['hardwood slats on steel frame', 'concrete', 'recycled plastic'],
    spacing: '30-50m on main paths, 15-20m in high-use areas',
  },
  picnicTable: {
    typical: { length: 1.8, width: 1.5, height: 0.75 },
    materials: ['treated pine', 'hardwood', 'recycled plastic'],
    clearance: '1m each side for access',
  },
  bin: {
    typical: { diameter: 0.5, height: 0.9 },
    spacing: '50m on paths, near seating and entries',
    types: ['single stream', 'recycling', 'dog waste'],
  },
  drinkingFountain: {
    typical: { height: 0.9, pedestal: 0.2 },
    spacing: 'every 400m on main paths',
    notes: 'Include dog bowl at base in modern installations',
  },
  lightingColumn: {
    typical: { height: '4-8m depending on use' },
    pathLighting: '4m height, 15-20m spacing',
    parkLighting: '6-8m height, 25-30m spacing',
    types: ['traditional column', 'contemporary bollard', 'catenary'],
  },
  bikePark: {
    stand: { capacity: '2 bikes per stand', height: 0.75 },
    spacing: 'clusters of 4-8 stands at park entries',
  },
  waterFeature: {
    splashPad: { typical: '6-15m diameter', surfacing: 'non-slip concrete' },
    pond: { depth: '0.6m shallow / 1.5m deep zone' },
    fountain: { basin: '2-8m diameter typical' },
  },
} as const;

export interface SoftLandscape {
  treeSpecies: string[];
  treeForm: string;
  treeSpacing: string;
  canopyCoverage: string;     // e.g. "30-50%"
  shrubs: string | false;
  lawn: string | false;
  gardenBeds: string | false;
  groundCover: string | false;
  hedging: string | false;
  nativePlanting: boolean;
  seasonalBedding: boolean;
}

export interface HardLandscape {
  primaryPath: {
    material: string;
    width: string;
    pattern: string;
    colour: string;
  };
  secondaryPath?: {
    material: string;
    width: string;
  };
  plaza?: {
    material: string;
    pattern: string;
    colour: string;
    area: string;
  };
  edgeTreatment: string;
  kerbing: string;
  steps: boolean;
  retainingWalls: boolean;
}

export interface SportsFacility {
  present: boolean;
  type?: keyof typeof SPORTS_COURT_DIMENSIONS;
  quantity?: number;
  dimensions?: string;   // references SPORTS_COURT_DIMENSIONS
  surface?: string;
  lighting?: boolean;
  fencing?: string;
  spectatorSeating?: boolean;
  notes?: string;
  promptAddition: string; // exact AI prompt describing this facility
}

export interface PlayFacility {
  present: boolean;
  ageGroup?: keyof typeof PLAYGROUND_EQUIPMENT;
  equipment?: string[];  // references PLAYGROUND_EQUIPMENT
  surfacing?: string;
  safetyZone?: string;
  fencing?: boolean;
  shade?: boolean;
  promptAddition: string;
}

export interface ParkAmenities {
  seating: {
    type: string;
    material: string;
    density: string;    // e.g. "bench every 40m on main paths"
    quantity: string;
  };
  picnicFacilities: {
    present: boolean;
    type?: string;
    quantity?: string;
  };
  waterFeature: {
    present: boolean;
    type?: string;
    dimensions?: string;
    description?: string;
  };
  shelter: {
    present: boolean;
    type?: string;      // e.g. "open pergola", "rotunda", "shade sail"
    dimensions?: string;
  };
  toilets: {
    present: boolean;
    type?: string;
  };
  kiosk: {
    present: boolean;
    type?: string;
  };
  lighting: {
    type: string;
    height: string;
    spacing: string;
  };
  publicArt: {
    present: boolean;
    description?: string;
  };
  bikeFacilities: {
    racks: boolean;
    quantity?: string;
  };
  drinkingFountain: boolean;
  dogFacilities: {
    offLeashArea: boolean;
    dogBins: boolean;
    dogWater: boolean;
  };
  bbq: {
    present: boolean;
    quantity?: string;
  };
}

export interface ParkAtmosphere {
  character: string;
  primaryUse: string;
  activityDensity: ActivityDensity;
  season: Season;
  timeOfDay: TimeOfDay;
  noiseLevel: string;
  demographic: string;  // e.g. "families", "all ages", "active youth"
}

export interface ParkArchetypeMetadata {
  // ── Identity ────────────────────────────────────────────────────────────
  archetypeId: string;
  archetypeLabel: string;
  domain: 'parks-plazas';
  parkCategory: string;

  // ── AI Prompts ──────────────────────────────────────────────────────────
  imagePrompt: ImagePrompt;
  promptBooster: string;

  // ── Landscape ───────────────────────────────────────────────────────────
  softLandscape: SoftLandscape;
  hardLandscape: HardLandscape;

  // ── Facilities ──────────────────────────────────────────────────────────
  sportsFacilities: SportsFacility[];
  playFacilities: PlayFacility[];
  amenities: ParkAmenities;

  // ── Atmosphere ──────────────────────────────────────────────────────────
  atmosphere: ParkAtmosphere;

  // ── Render ──────────────────────────────────────────────────────────────
  faceCount: 1;
  topDownProfile: {
    canopyCoverage: string;
    pathPattern: string;
    dominantColour: string;
    keyElementsVisible: string[];  // what's visible from directly above
    promptAddition: string;
  };
  captureAngle: CaptureAngle;
  ipAdapterStrength: number;

  // ── Size Bands ──────────────────────────────────────────────────────────
  sizeBands: {
    small: {            // under 2500m²
      prompt: string;
      pitch: number;
      zoom: number;
    };
    medium: {           // 2500-22500m²
      prompt: string;
      pitch: number;
      zoom: number;
    };
    large: {            // 22500m²+
      prompt: string;
      pitch: number;
      zoom: number;
    };
  };
}

// ─── STREET / PATHWAY SCHEMA ──────────────────────────────────────────────────

export type StreetType =
  | 'laneway'           // under 8m, pedestrian/service
  | 'local-street'      // 8-15m, low traffic
  | 'collector-street'  // 15-25m, medium traffic
  | 'arterial'          // 25-40m, high traffic
  | 'boulevard'         // 30m+, formal tree-lined
  | 'pedestrian-mall'   // car-free, activated
  | 'shared-zone'       // 20km/h, mixed pedestrian/vehicle
  | 'cycle-path'        // dedicated cycling
  | 'park-path'         // informal path through green space
  | 'waterfront-promenade'; // along water edge

// Real-world street component dimensions
export const STREET_DIMENSIONS = {
  laneway: {
    carriageway: '3-5m',
    footpath: '1.5-2m each side or none',
    total: '6-8m',
    trees: 'none or wall-trained',
    parking: 'none',
  },
  localStreet: {
    carriageway: '6-7m (two lanes)',
    footpath: '1.8-3m each side',
    natureStrip: '1.5-3m each side',
    total: '14-18m',
    trees: '6-8m spacing, nature strip',
    parking: 'on-street both sides',
  },
  collectorStreet: {
    carriageway: '9-11m (two lanes + turn)',
    footpath: '2.5-3m each side',
    natureStrip: '2-3m each side',
    total: '18-24m',
    trees: '7-10m spacing, nature strip or footpath',
    parking: 'on-street one or both sides',
    cycleLane: '1.5m each direction optional',
  },
  urbanBoulevard: {
    carriageway: '14-18m (4 lanes)',
    medianStrip: '4-6m planted',
    footpath: '4-6m each side',
    total: '28-40m',
    trees: 'double row each side + median, 6-8m spacing',
    parking: 'angle or parallel',
    cycleLane: '2m separated each direction',
  },
  pedestrianMall: {
    carriageway: 'none',
    paving: '10-20m width',
    trees: 'formal rows or clusters',
    furniture: 'dense — seating, kiosks, art, planting',
    total: '12-25m',
  },
} as const;

export interface CarriagewayProfile {
  width: string;
  lanes: number;
  surface: string;        // e.g. "asphalt", "concrete", "cobblestone"
  colour: string;
  laneMarkings: string;
  speedLimit?: number;
  cycleLane?: {
    present: boolean;
    width?: string;
    surface?: string;
    colour?: string;      // e.g. "green acrylic"
    separation?: string;  // e.g. "painted line", "wand posts", "kerb"
  };
  tramTracks?: boolean;
  medianStrip?: {
    present: boolean;
    width?: string;
    treatment?: string;   // e.g. "planted", "paved", "raised kerb"
  };
}

export interface FootpathProfile {
  width: string;
  surface: string;
  colour: string;
  pattern: string;
  kerb: string;
  natureStrip?: {
    present: boolean;
    width?: string;
    treatment?: string;  // e.g. "lawn", "groundcover", "paving"
  };
}

export interface StreetTreeProfile {
  present: boolean;
  species?: string[];
  form?: string;          // e.g. "columnar", "broad spreading", "weeping"
  height?: string;
  spacing?: string;       // e.g. "6m centres", "8m centres"
  grate?: string;         // e.g. "cast iron tree grate", "rubber surround"
  guard?: string;         // e.g. "steel tree guard", "none"
  canopyCoverage?: string;
  rootBarrier?: boolean;
  irrigation?: boolean;
}

export interface StreetFurniture {
  lightingColumns: {
    type: string;         // e.g. "traditional acorn", "contemporary", "catenary"
    height: string;
    spacing: string;
    colour: string;
  };
  seating: {
    present: boolean;
    type?: string;
    spacing?: string;
    material?: string;
  };
  bins: {
    present: boolean;
    type?: string;
    spacing?: string;
  };
  bollards: {
    present: boolean;
    type?: string;
    spacing?: string;
    colour?: string;
  };
  bikeParkng: {
    present: boolean;
    type?: string;
    quantity?: string;
  };
  wayfinding: {
    present: boolean;
    type?: string;
  };
  newspaper?: boolean;
  kiosk?: boolean;
  publicArt?: boolean;
  busStop?: {
    present: boolean;
    shelter?: boolean;
    seating?: boolean;
  };
}

export interface GroundFloorActivation {
  type: string;           // e.g. "retail", "cafe", "residential", "blank"
  awnings: boolean;
  awningDepth?: string;   // e.g. "2.5m", "3m"
  signage: string;
  glazingRatio: string;   // e.g. "60-80%", "30-40%"
  outdoorDining?: boolean;
  planters?: boolean;
}

export interface StreetArchetypeMetadata {
  // ── Identity ────────────────────────────────────────────────────────────
  archetypeId: string;
  archetypeLabel: string;
  domain: 'streets-pathways';
  streetType: StreetType;

  // ── AI Prompts ──────────────────────────────────────────────────────────
  imagePrompt: ImagePrompt;
  promptBooster: string;

  // ── Street Components ───────────────────────────────────────────────────
  carriageway: CarriagewayProfile;
  footpath: FootpathProfile;
  streetTrees: StreetTreeProfile;
  furniture: StreetFurniture;
  groundFloorActivation: GroundFloorActivation;

  // ── Character ───────────────────────────────────────────────────────────
  atmosphere: {
    character: string;
    activityLevel: ActivityDensity;
    pedestrianComfort: string;
    timeOfDay: TimeOfDay;
    season: Season;
    noiseLevel: string;
  };

  // ── Render ──────────────────────────────────────────────────────────────
  faceCount: 1;
  topDownProfile: {
    pathPattern: string;
    dominantColour: string;
    treeCanopyPattern: string;
    keyElementsVisible: string[];
    promptAddition: string;
  };
  captureAngle: CaptureAngle;
  ipAdapterStrength: number;

  // ── Width Bands ─────────────────────────────────────────────────────────
  widthBands: {
    narrow: {           // under 8m
      prompt: string;
      pitch: number;
      zoom: number;
      imageSize: { width: number; height: number };
    };
    standard: {         // 8-20m
      prompt: string;
      pitch: number;
      zoom: number;
      imageSize: { width: number; height: number };
    };
    wide: {             // 20m+
      prompt: string;
      pitch: number;
      zoom: number;
      imageSize: { width: number; height: number };
    };
  };
}

// ─── EXAMPLE ENTRIES ──────────────────────────────────────────────────────────
// These show Claude Code exactly how to populate the schema
// for specific archetypes

export const EXAMPLE_TENNIS_PARK: Partial<ParkArchetypeMetadata> = {
  archetypeId: 'neighbourhood_sports_park',
  archetypeLabel: 'Neighbourhood Sports Park',
  domain: 'parks-plazas',

  sportsFacilities: [
    {
      present: true,
      type: 'tennis',
      quantity: 2,
      dimensions: '23.77m x 10.97m per court, 36.6m x 18.3m including run-off',
      surface: 'acrylic hard court, blue/green colour',
      lighting: true,
      fencing: '3.5m chain link fence surrounding courts',
      spectatorSeating: false,
      notes: 'Standard ITF dimensions. Courts oriented north-south to minimise sun glare.',
      promptAddition:
        'two tennis courts with blue acrylic surface, white line markings, ' +
        'net visible at centre, 3.5m chain link fence surround, ' +
        'corner lighting columns, north-south orientation, ' +
        'ITF standard dimensions 23.77m x 10.97m each court',
    },
    {
      present: true,
      type: 'basketball',
      quantity: 1,
      dimensions: '28m x 15m court, 32m x 19m including run-off',
      surface: 'coloured acrylic, orange and grey',
      lighting: true,
      fencing: '2m chain link fence',
      spectatorSeating: false,
      promptAddition:
        'full basketball court, orange and grey acrylic surface, ' +
        'white court markings including three-point line and key area, ' +
        'two hoops at 3.05m height with backboards, ' +
        'FIBA standard 28m x 15m dimensions',
    },
  ],

  playFacilities: [
    {
      present: true,
      ageGroup: 'junior',
      equipment: [
        'climbing structure 3m height',
        'double slide',
        'standard swings x4',
        'monkey bars',
      ],
      surfacing: 'rubber softfall 300mm depth',
      safetyZone: '2.4m from equipment edge',
      fencing: true,
      shade: true,
      promptAddition:
        'children\'s playground with 3m climbing structure, double slide, ' +
        'swing set with 4 seats, monkey bars, rubber softfall surfacing, ' +
        'fenced perimeter, shade sail overhead',
    },
  ],
};

export const EXAMPLE_URBAN_BOULEVARD: Partial<StreetArchetypeMetadata> = {
  archetypeId: 'formal_tree_lined_boulevard',
  archetypeLabel: 'Formal Tree-Lined Boulevard',
  domain: 'streets-pathways',
  streetType: 'boulevard',

  carriageway: {
    width: '14m (4 lanes)',
    lanes: 4,
    surface: 'asphalt',
    colour: 'dark grey',
    laneMarkings: 'white dashed centre lines, solid edge lines',
    speedLimit: 50,
    cycleLane: {
      present: true,
      width: '2m each direction',
      surface: 'asphalt',
      colour: 'green acrylic',
      separation: 'wand posts at 10m spacing',
    },
    medianStrip: {
      present: true,
      width: '5m',
      treatment: 'formally planted with standard trees and low hedging',
    },
  },

  footpath: {
    width: '5m each side',
    surface: 'natural stone paving',
    colour: 'buff/cream',
    pattern: 'regular ashlar with contrasting band at kerb edge',
    kerb: 'granite kerb, 150mm height',
    natureStrip: {
      present: false,
    },
  },

  streetTrees: {
    present: true,
    species: ['Plane tree (Platanus x acerifolia)', 'London Plane'],
    form: 'broadly spreading, formal pollarded crown',
    height: '12-15m mature height',
    spacing: '7m centres, double row each side',
    grate: '1.2m x 1.2m cast iron tree grate',
    guard: 'none — established trees',
    canopyCoverage: '60-70% of footpath',
    rootBarrier: true,
    irrigation: true,
  },

  furniture: {
    lightingColumns: {
      type: 'traditional ornate column with globe fitting',
      height: '6m',
      spacing: '20m alternating sides',
      colour: 'dark green powder coat',
    },
    seating: {
      present: true,
      type: 'cast iron and timber slat bench',
      spacing: 'every 30m at tree grates',
      material: 'cast iron frame, hardwood slats',
    },
    bins: {
      present: true,
      type: 'cast iron litter bin matching bench style',
      spacing: 'paired with every second bench',
    },
    bollards: {
      present: true,
      type: 'cast iron decorative bollard',
      spacing: '1.2m at kerb crossings',
      colour: 'dark green matching lights',
    },
    bikeParkng: {
      present: true,
      type: 'Sheffield stand',
      quantity: 'clusters of 4 at 100m intervals',
    },
    wayfinding: {
      present: true,
      type: 'blade sign on lighting columns',
    },
  },

  groundFloorActivation: {
    type: 'retail and cafe',
    awnings: true,
    awningDepth: '3m',
    signage: 'blade and fascia signage, individual tenancy character',
    glazingRatio: '70-80%',
    outdoorDining: true,
    planters: true,
  },

  promptBooster:
    'formal tree-lined boulevard, double row London Plane trees, ' +
    'natural stone paving, ornate cast iron street furniture, ' +
    'green cycle lane, outdoor dining, activated retail ground floor',
};

// ─── CLAUDE CODE INSTRUCTIONS ─────────────────────────────────────────────────
/**
 * When Claude Code uses this schema to populate archetype metadata files:
 *
 * 1. Read the front_day.png image carefully before filling any fields
 * 2. Only populate fields with what is actually visible in the image
 * 3. Use SPORTS_COURT_DIMENSIONS for exact court specifications
 * 4. Use PLAYGROUND_EQUIPMENT for play area descriptions
 * 5. Use PARK_FURNITURE for furniture dimensions and spacing
 * 6. Use STREET_DIMENSIONS for street width references
 * 7. The promptBooster field is the most important for render quality —
 *    write it last, after all other fields are complete, as a summary
 *    of the most visually distinctive elements
 * 8. For sportsFacilities, always include exact court dimensions in the
 *    promptAddition so the AI renders correct proportions
 * 9. For playFacilities, always specify equipment heights and surfacing
 *    so the AI renders correct scale
 * 10. Never invent elements that are not visible in the front_day.png
 */
