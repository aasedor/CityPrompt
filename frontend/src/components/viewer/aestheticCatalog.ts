import type { SiteZoneProperties } from '@/types';

export type AestheticCategory = {
  id: string;
  label: string;
  description: string;
};

export type TransportModeKey = 'walking' | 'bicycle' | 'transit' | 'automobile';

export type AestheticOption = {
  id: string;
  categoryId?: string;
  label: string;
  description: string;
  photoUrl: string;
  transportModes?: TransportModeKey[];
};

export const TRANSPORT_MODE_ORDER: TransportModeKey[] = ['walking', 'bicycle', 'transit', 'automobile'];

export const TRANSPORT_MODE_OPTIONS: Array<{ id: TransportModeKey; label: string; description: string }> = [
  {
    id: 'walking',
    label: 'Walking',
    description: 'Pedestrian-focused movement and public realm comfort',
  },
  {
    id: 'bicycle',
    label: 'Bicycle',
    description: 'Protected or low-stress cycling movement',
  },
  {
    id: 'transit',
    label: 'Transit',
    description: 'Frequent bus/tram/LRT movement and stops',
  },
  {
    id: 'automobile',
    label: 'Automobile',
    description: 'Vehicle access for daily circulation and servicing',
  },
];

export const BUILDING_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = [
  {
    id: 'residential',
    label: 'Residential',
    description: 'Housing-driven forms from townhomes to mid/high-rise living',
  },
  {
    id: 'commercial',
    label: 'Commercial',
    description: 'Employment, retail, and office-focused building patterns',
  },
  {
    id: 'mixed_use',
    label: 'Mixed Use',
    description: 'Combined living, retail, and workplace urban blocks',
  },
  {
    id: 'institutional',
    label: 'Institutional',
    description: 'Civic, academic, and public-service architecture',
  },
  {
    id: 'industrial',
    label: 'Industrial',
    description: 'Production, logistics, and maker-oriented building typologies',
  },
  {
    id: 'other',
    label: 'Custom / Other',
    description: 'Manual design direction from your prompt and references',
  },
];

export const BUILDING_AESTHETIC_OPTIONS_V2: AestheticOption[] = [
  {
    id: 'new_york_brownstone',
    categoryId: 'residential',
    label: 'New York Brownstone',
    description: 'Brooklyn-style masonry rowhouses with stoops and rhythmic facades',
    photoUrl: 'https://source.unsplash.com/1200x900/?brooklyn,brownstone,rowhouse,facade',
  },
  {
    id: 'historic_traditional',
    categoryId: 'residential',
    label: 'Historic / Traditional',
    description: 'Fine-grain brick and stone residential streets with articulated entries',
    photoUrl: 'https://source.unsplash.com/1200x900/?historic,rowhouse,architecture,street',
  },
  {
    id: 'london_georgian_terrace',
    categoryId: 'residential',
    label: 'London Georgian Terrace',
    description: 'Uniform terrace fronts, sash windows, and formal stoop sequences',
    photoUrl: 'https://source.unsplash.com/1200x900/?london,georgian,terrace,houses',
  },
  {
    id: 'modern_midrise_residential',
    categoryId: 'residential',
    label: 'Modern Mid-Rise Residential',
    description: '5-10 storey apartment blocks with active podium and urban balconies',
    photoUrl: 'https://source.unsplash.com/1200x900/?midrise,apartment,building,urban',
  },
  {
    id: 'vancouver_townhome_courtyard',
    categoryId: 'residential',
    label: 'Townhome Courtyard Cluster',
    description: 'Stacked townhomes around shared green courts and walk-up entries',
    photoUrl: 'https://source.unsplash.com/1200x900/?townhouse,courtyard,residential,architecture',
  },
  {
    id: 'parisian_haussmann',
    categoryId: 'commercial',
    label: 'Parisian Haussmann',
    description: 'Limestone blocks with iron balconies and elegant boulevard frontage',
    photoUrl: 'https://source.unsplash.com/1200x900/?paris,haussmann,building,facade',
  },
  {
    id: 'main_street_retail',
    categoryId: 'commercial',
    label: 'Main Street Retail',
    description: 'Narrow-bay storefront rhythm with upper office or residential floors',
    photoUrl: 'https://source.unsplash.com/1200x900/?main,street,retail,building,facade',
  },
  {
    id: 'office_tower_glass',
    categoryId: 'commercial',
    label: 'Glass Office Tower',
    description: 'High-performance curtain wall office profile with urban plaza edge',
    photoUrl: 'https://source.unsplash.com/1200x900/?office,tower,glass,architecture',
  },
  {
    id: 'innovation_campus',
    categoryId: 'commercial',
    label: 'Innovation Campus',
    description: 'Low-to-mid rise tech blocks with shared atria and collaborative courts',
    photoUrl: 'https://source.unsplash.com/1200x900/?technology,campus,architecture,office',
  },
  {
    id: 'podium_mixed_use',
    categoryId: 'mixed_use',
    label: 'Podium Mixed-Use',
    description: 'Retail podium with residential or office towers above',
    photoUrl: 'https://source.unsplash.com/1200x900/?mixed,use,podium,tower,city',
  },
  {
    id: 'barcelona_eixample_block',
    categoryId: 'mixed_use',
    label: 'Eixample Perimeter Block',
    description: 'Perimeter block urban form with interior courtyards and active corners',
    photoUrl: 'https://source.unsplash.com/1200x900/?barcelona,eixample,block,architecture',
  },
  {
    id: 'transit_oriented_mixed_use',
    categoryId: 'mixed_use',
    label: 'Transit-Oriented Mixed Use',
    description: 'Station-adjacent density with walkable podium and fine-grain frontage',
    photoUrl: 'https://source.unsplash.com/1200x900/?transit,oriented,development,mixed,use',
  },
  {
    id: 'collegiate_campus_quads',
    categoryId: 'institutional',
    label: 'Collegiate Campus Quads',
    description: 'Academic buildings framing courtyards, lawns, and pedestrian spines',
    photoUrl: 'https://source.unsplash.com/1200x900/?university,campus,quad,architecture',
  },
  {
    id: 'civic_library_modern',
    categoryId: 'institutional',
    label: 'Contemporary Civic Library',
    description: 'Public-facing civic architecture with transparent edges and gathering stair',
    photoUrl: 'https://source.unsplash.com/1200x900/?public,library,architecture,modern',
  },
  {
    id: 'healthcare_campus',
    categoryId: 'institutional',
    label: 'Healthcare Campus',
    description: 'Human-scaled clinical blocks with healing gardens and clear wayfinding',
    photoUrl: 'https://source.unsplash.com/1200x900/?hospital,campus,architecture,healthcare',
  },
  {
    id: 'logistics_warehouse_campus',
    categoryId: 'industrial',
    label: 'Logistics Warehouse Campus',
    description: 'Large-format logistics sheds with service yards and truck circulation',
    photoUrl: 'https://source.unsplash.com/1200x900/?warehouse,distribution,center,architecture',
  },
  {
    id: 'maker_district_brick_loft',
    categoryId: 'industrial',
    label: 'Maker District Loft',
    description: 'Adaptive industrial blocks with brick facades and workshop frontage',
    photoUrl: 'https://source.unsplash.com/1200x900/?industrial,brick,loft,district',
  },
  {
    id: 'clean_tech_industrial',
    categoryId: 'industrial',
    label: 'Clean-Tech Industrial',
    description: 'Advanced manufacturing buildings with daylighted envelopes and clean yards',
    photoUrl: 'https://source.unsplash.com/1200x900/?modern,industrial,facility,architecture',
  },
  {
    id: 'modern',
    categoryId: 'mixed_use',
    label: 'Modern',
    description: 'Contemporary urban architecture with clean geometry and glass/metal skin',
    photoUrl: 'https://source.unsplash.com/1200x900/?modern,urban,building,facade',
  },
  {
    id: 'futuristic',
    categoryId: 'mixed_use',
    label: 'Futuristic',
    description: 'Expressive high-tech massing with landmark-ready architectural language',
    photoUrl: 'https://source.unsplash.com/1200x900/?futuristic,architecture,city,building',
  },
  {
    id: 'other',
    categoryId: 'other',
    label: 'Other',
    description: 'Custom building direction guided by your text prompt and references',
    photoUrl: 'https://source.unsplash.com/1200x900/?architecture,building,facade,city',
  },
];

export const ROADWAY_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = [
  {
    id: 'pedestrian_realm',
    label: 'Pedestrian Realm',
    description: 'Walking-dominant streets, promenades, and shared public spaces',
  },
  {
    id: 'cycling_network',
    label: 'Cycling Network',
    description: 'Cycle-priority corridors and protected bike infrastructure',
  },
  {
    id: 'transit_corridor',
    label: 'Transit Corridor',
    description: 'High-capacity bus/tram/LRT oriented right-of-way typologies',
  },
  {
    id: 'complete_street',
    label: 'Complete Street',
    description: 'Balanced multimodal corridors for walking, cycling, transit, and autos',
  },
  {
    id: 'boulevard_avenue',
    label: 'Boulevard / Avenue',
    description: 'Formal urban arterials with medians, canopies, and civic frontage',
  },
  {
    id: 'service_freight',
    label: 'Service / Freight',
    description: 'Industrial access corridors optimized for servicing and goods movement',
  },
  {
    id: 'other',
    label: 'Custom / Other',
    description: 'Manual transportation direction from your prompt and references',
  },
];

export const ROADWAY_AESTHETIC_OPTIONS_V2: AestheticOption[] = [
  {
    id: 'kyoto_philosophers_path',
    categoryId: 'pedestrian_realm',
    label: "Kyoto Philosopher's Path",
    description: 'Canal-side pedestrian corridor with blossom canopy and intimate paving',
    photoUrl: 'https://source.unsplash.com/1200x900/?kyoto,philosophers,path,canal,walkway',
    transportModes: ['walking'],
  },
  {
    id: 'copenhagen_stroget',
    categoryId: 'pedestrian_realm',
    label: 'Copenhagen Stroget',
    description: 'Car-free retail spine with active frontages and generous walking space',
    photoUrl: 'https://source.unsplash.com/1200x900/?copenhagen,stroget,pedestrian,street',
    transportModes: ['walking'],
  },
  {
    id: 'barcelona_la_rambla',
    categoryId: 'pedestrian_realm',
    label: 'Barcelona La Rambla',
    description: 'Tree-lined promenade with central pedestrian flow and edge access',
    photoUrl: 'https://source.unsplash.com/1200x900/?barcelona,la,rambla,pedestrian',
    transportModes: ['walking', 'transit'],
  },
  {
    id: 'venice_fondamenta_walk',
    categoryId: 'pedestrian_realm',
    label: 'Venice Fondamenta Walk',
    description: 'Water-edge walkways with narrow carriageways and high pedestrian priority',
    photoUrl: 'https://source.unsplash.com/1200x900/?venice,canal,walkway,street',
    transportModes: ['walking'],
  },
  {
    id: 'amsterdam_canal_street',
    categoryId: 'cycling_network',
    label: 'Amsterdam Canal Street',
    description: 'Cycling-first canal corridor with calm local vehicle access',
    photoUrl: 'https://source.unsplash.com/1200x900/?amsterdam,canal,street,bicycle',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'copenhagen_cycle_superhighway',
    categoryId: 'cycling_network',
    label: 'Copenhagen Cycle Superhighway',
    description: 'Protected long-distance bike corridor with smooth intersections',
    photoUrl: 'https://source.unsplash.com/1200x900/?copenhagen,cycle,track,street',
    transportModes: ['walking', 'bicycle'],
  },
  {
    id: 'bogota_cicloruta',
    categoryId: 'cycling_network',
    label: 'Bogota Cicloruta',
    description: 'High-coverage cycle route integrated with green median systems',
    photoUrl: 'https://source.unsplash.com/1200x900/?bogota,bicycle,lane,street',
    transportModes: ['walking', 'bicycle'],
  },
  {
    id: 'utrecht_fietsstraat',
    categoryId: 'cycling_network',
    label: 'Utrecht Fietsstraat',
    description: 'Bicycle-priority shared street where cars are guests',
    photoUrl: 'https://source.unsplash.com/1200x900/?utrecht,bicycle,street,netherlands',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'seville_protected_cycle_track',
    categoryId: 'cycling_network',
    label: 'Seville Protected Cycle Track',
    description: 'Physically protected curbside cycleway with shaded sidewalks',
    photoUrl: 'https://source.unsplash.com/1200x900/?seville,cycle,track,street',
    transportModes: ['walking', 'bicycle'],
  },
  {
    id: 'curitiba_brt_axis',
    categoryId: 'transit_corridor',
    label: 'Curitiba BRT Axis',
    description: 'Median-running bus rapid transit with linear station sequence',
    photoUrl: 'https://source.unsplash.com/1200x900/?curitiba,brt,bus,corridor',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'bogota_transmilenio_avenue',
    categoryId: 'transit_corridor',
    label: 'Bogota TransMilenio Avenue',
    description: 'Dedicated bus lanes and platform stations on a high-volume avenue',
    photoUrl: 'https://source.unsplash.com/1200x900/?transmilenio,bogota,bus,rapid,transit',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'hong_kong_tram_street',
    categoryId: 'transit_corridor',
    label: 'Hong Kong Tram Street',
    description: 'Dense mixed corridor where tram movement shapes public street life',
    photoUrl: 'https://source.unsplash.com/1200x900/?hong,kong,tram,street',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'zurich_tram_boulevard',
    categoryId: 'transit_corridor',
    label: 'Zurich Tram Boulevard',
    description: 'Transit-forward boulevard with strong pedestrian crossings and calm traffic',
    photoUrl: 'https://source.unsplash.com/1200x900/?zurich,tram,boulevard,street',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'portland_complete_street',
    categoryId: 'complete_street',
    label: 'Portland Complete Street',
    description: 'Balanced street section with transit, cycling, autos, and large sidewalks',
    photoUrl: 'https://source.unsplash.com/1200x900/?portland,complete,street,urban',
    transportModes: ['walking', 'bicycle', 'transit', 'automobile'],
  },
  {
    id: 'barcelona_superblock',
    categoryId: 'complete_street',
    label: 'Barcelona Superblock Street',
    description: 'Low-speed local grid with reclaimed pedestrian and social space',
    photoUrl: 'https://source.unsplash.com/1200x900/?barcelona,superblock,street,public,space',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'london_exhibition_road',
    categoryId: 'complete_street',
    label: 'London Exhibition Road',
    description: 'Shared-surface civic street with coordinated multimodal movement',
    photoUrl: 'https://source.unsplash.com/1200x900/?london,exhibition,road,shared,street',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'paris_champs_elysees',
    categoryId: 'boulevard_avenue',
    label: 'Paris Champs-Elysees',
    description: 'Monumental boulevard section with formal tree canopy and median structure',
    photoUrl: 'https://source.unsplash.com/1200x900/?paris,champs,elysees,boulevard',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'mexico_city_reforma',
    categoryId: 'boulevard_avenue',
    label: 'Paseo de la Reforma',
    description: 'Large mixed-mobility avenue with events, monuments, and transit presence',
    photoUrl: 'https://source.unsplash.com/1200x900/?mexico,city,paseo,reforma,avenue',
    transportModes: ['walking', 'bicycle', 'transit', 'automobile'],
  },
  {
    id: 'tokyo_local_service_lane',
    categoryId: 'boulevard_avenue',
    label: 'Tokyo Local Service Lane',
    description: 'Fine-grain neighborhood service street with compact multimodal coexistence',
    photoUrl: 'https://source.unsplash.com/1200x900/?tokyo,local,street,lane',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'industrial_freight_collector',
    categoryId: 'service_freight',
    label: 'Industrial Freight Collector',
    description: 'Durable heavy-duty industrial corridor with turning radii for goods movement',
    photoUrl: 'https://source.unsplash.com/1200x900/?industrial,freight,road,warehouse',
    transportModes: ['automobile', 'transit'],
  },
  {
    id: 'other',
    categoryId: 'other',
    label: 'Other',
    description: 'Custom transportation aesthetic and right-of-way direction',
    photoUrl: 'https://source.unsplash.com/1200x900/?street,urban,transport,corridor',
  },
];
export const GREEN_SPACE_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = [
  {
    id: 'historic_landscape',
    label: 'Historic Landscape',
    description: 'Picturesque and formal park traditions adapted to contemporary use',
  },
  {
    id: 'urban_linear',
    label: 'Urban Linear',
    description: 'Linear promenades and edge parks embedded in dense districts',
  },
  {
    id: 'ecological_restoration',
    label: 'Ecological Restoration',
    description: 'Habitat-forward parks driven by water, biodiversity, and resilience',
  },
  {
    id: 'civic_recreation',
    label: 'Civic Recreation',
    description: 'Active public lawns and social parks for daily and event use',
  },
  {
    id: 'botanic_horticultural',
    label: 'Botanic / Horticultural',
    description: 'Curated planting experiences and immersive garden routes',
  },
  {
    id: 'other',
    label: 'Custom / Other',
    description: 'Manual landscape direction from your prompt and references',
  },
];

export const GREEN_SPACE_AESTHETIC_OPTIONS_V2: AestheticOption[] = [
  {
    id: 'central_park_english_landscape',
    categoryId: 'historic_landscape',
    label: 'English Landscape Garden (Central Park)',
    description: 'Large picturesque park with meadows, winding paths, and layered tree canopy',
    photoUrl: 'https://source.unsplash.com/1200x900/?central,park,new,york,landscape',
  },
  {
    id: 'versailles_formal_garden',
    categoryId: 'historic_landscape',
    label: 'French Formal Garden (Versailles)',
    description: 'Axis-driven formal gardens, parterres, and ceremonial tree alignments',
    photoUrl: 'https://source.unsplash.com/1200x900/?versailles,garden,formal,landscape',
  },
  {
    id: 'high_line_linear_park',
    categoryId: 'urban_linear',
    label: 'Linear Elevated Park (High Line)',
    description: 'Elevated promenade with layered planting, overlooks, and seating pockets',
    photoUrl: 'https://source.unsplash.com/1200x900/?high,line,new,york,park',
  },
  {
    id: 'philosophers_path_garden',
    categoryId: 'urban_linear',
    label: 'Canal Garden Walk',
    description: 'Canal-edge strolling park with seasonal tree canopy and intimate paving',
    photoUrl: 'https://source.unsplash.com/1200x900/?kyoto,canal,garden,path',
  },
  {
    id: 'superkilen_cultural_park',
    categoryId: 'civic_recreation',
    label: 'Cultural Activity Park (Superkilen)',
    description: 'Program-rich social landscape with bold surfaces and active edges',
    photoUrl: 'https://source.unsplash.com/1200x900/?superkilen,copenhagen,park',
  },
  {
    id: 'civic_lawn_commons',
    categoryId: 'civic_recreation',
    label: 'Civic Lawn Commons',
    description: 'Flexible event lawn framed by shade trees, play, and social seating',
    photoUrl: 'https://source.unsplash.com/1200x900/?urban,lawn,park,city',
  },
  {
    id: 'houtan_ecological_park',
    categoryId: 'ecological_restoration',
    label: 'Ecological Wetland Park (Houtan)',
    description: 'Productive wetland terraces and boardwalks for stormwater polishing',
    photoUrl: 'https://source.unsplash.com/1200x900/?wetland,boardwalk,urban,park',
  },
  {
    id: 'bishan_river_park',
    categoryId: 'ecological_restoration',
    label: 'River Restoration Park (Bishan)',
    description: 'Naturalized river corridor with floodable lawns and habitat mosaics',
    photoUrl: 'https://source.unsplash.com/1200x900/?river,restoration,park,landscape',
  },
  {
    id: 'wetland_boardwalk_park',
    categoryId: 'ecological_restoration',
    label: 'Wetland Boardwalk Park',
    description: 'Sponge-park edge conditions with elevated pathways and riparian planting',
    photoUrl: 'https://source.unsplash.com/1200x900/?wetland,park,boardwalk,water',
  },
  {
    id: 'botanical_garden',
    categoryId: 'botanic_horticultural',
    label: 'Botanical Garden',
    description: 'Curated planting collections with educational routes and seasonal color',
    photoUrl: 'https://source.unsplash.com/1200x900/?botanical,garden,landscape,park',
  },
  {
    id: 'other',
    categoryId: 'other',
    label: 'Other',
    description: 'Custom park concept guided by your prompt and reference imagery',
    photoUrl: 'https://source.unsplash.com/1200x900/?landscape,architecture,park',
  },
];

export const PLAZA_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = [
  {
    id: 'civic_formal',
    label: 'Civic Formal',
    description: 'Ceremonial public squares with strong spatial order',
  },
  {
    id: 'market_social',
    label: 'Market & Social',
    description: 'Everyday social hardscapes supporting commerce and gatherings',
  },
  {
    id: 'event_cultural',
    label: 'Event & Cultural',
    description: 'Plazas designed for performances, festivals, and cultural programming',
  },
  {
    id: 'green_cooling',
    label: 'Green Cooling',
    description: 'Tree-forward plazas for comfort, dwell time, and microclimate',
  },
  {
    id: 'waterfront',
    label: 'Waterfront',
    description: 'Edge plazas with promenades, boardwalks, and water interfaces',
  },
  {
    id: 'other',
    label: 'Custom / Other',
    description: 'Manual plaza direction from your prompt and references',
  },
];

export const PLAZA_AESTHETIC_OPTIONS_V2: AestheticOption[] = [
  {
    id: 'civic_fountain_square',
    categoryId: 'civic_formal',
    label: 'Civic Fountain Square',
    description: 'Formal plaza armature anchored by an iconic fountain and civic frontages',
    photoUrl: 'https://source.unsplash.com/1200x900/?civic,square,fountain,plaza',
  },
  {
    id: 'piazza_del_campo',
    categoryId: 'civic_formal',
    label: 'Piazza del Campo',
    description: 'Shell-shaped civic plaza with radial paving and active perimeter edges',
    photoUrl: 'https://source.unsplash.com/1200x900/?piazza,del,campo,siena',
  },
  {
    id: 'trafalgar_square',
    categoryId: 'civic_formal',
    label: 'Trafalgar Square',
    description: 'Monumental public square with stairs, fountains, and civic intensity',
    photoUrl: 'https://source.unsplash.com/1200x900/?trafalgar,square,london',
  },
  {
    id: 'market_plaza',
    categoryId: 'market_social',
    label: 'Market Plaza',
    description: 'Flexible market hardscape for kiosks, pop-ups, and daily retail activity',
    photoUrl: 'https://source.unsplash.com/1200x900/?market,plaza,urban,public,space',
  },
  {
    id: 'times_square_pedestrian',
    categoryId: 'market_social',
    label: 'Times Square Pedestrian Plaza',
    description: 'High-intensity pedestrianized plaza with media facades and seating bands',
    photoUrl: 'https://source.unsplash.com/1200x900/?times,square,pedestrian,plaza',
  },
  {
    id: 'festival_plaza',
    categoryId: 'event_cultural',
    label: 'Festival Plaza',
    description: 'Large event forecourt designed for cultural programming and gatherings',
    photoUrl: 'https://source.unsplash.com/1200x900/?festival,plaza,public,square',
  },
  {
    id: 'federation_square',
    categoryId: 'event_cultural',
    label: 'Federation Square',
    description: 'Angular cultural plaza with event staging and layered social terraces',
    photoUrl: 'https://source.unsplash.com/1200x900/?federation,square,melbourne',
  },
  {
    id: 'garden_plaza',
    categoryId: 'green_cooling',
    label: 'Garden Plaza',
    description: 'Shaded plaza with integrated planting, seating bands, and cooling comfort',
    photoUrl: 'https://source.unsplash.com/1200x900/?garden,plaza,trees,urban',
  },
  {
    id: 'waterfront_boardwalk_plaza',
    categoryId: 'waterfront',
    label: 'Waterfront Boardwalk Plaza',
    description: 'Promenade plaza with boardwalk terraces and edge activation',
    photoUrl: 'https://source.unsplash.com/1200x900/?waterfront,boardwalk,plaza',
  },
  {
    id: 'harbour_edge_plaza',
    categoryId: 'waterfront',
    label: 'Harbour Edge Plaza',
    description: 'Public waterfront forecourt blending seating steps and shoreline access',
    photoUrl: 'https://source.unsplash.com/1200x900/?harbour,waterfront,public,plaza',
  },
  {
    id: 'other',
    categoryId: 'other',
    label: 'Other',
    description: 'Custom plaza identity guided by your prompt and reference imagery',
    photoUrl: 'https://source.unsplash.com/1200x900/?urban,plaza,public,space',
  },
];

export const ROADWAY_AESTHETIC_PRESETS_V2: Record<string, Partial<SiteZoneProperties>> = {
  kyoto_philosophers_path: {
    mobility_profile: 'walking_only',
    transport_modes: ['walking'],
    width: 6,
    lane_count: 1,
    volume: 'low',
    road_surface: 'paver',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 1,
    priority_cycling: 3,
    priority_transit: 4,
    priority_auto: 4,
  },
  copenhagen_stroget: {
    mobility_profile: 'walking_only',
    transport_modes: ['walking'],
    width: 8,
    lane_count: 1,
    volume: 'medium',
    road_surface: 'stone',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 1,
    priority_cycling: 3,
    priority_transit: 4,
    priority_auto: 4,
  },
  barcelona_la_rambla: {
    mobility_profile: 'pedestrian_first',
    transport_modes: ['walking', 'transit'],
    width: 14,
    lane_count: 2,
    volume: 'medium',
    road_surface: 'paver',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 1,
    priority_cycling: 4,
    priority_transit: 2,
    priority_auto: 4,
  },
  venice_fondamenta_walk: {
    mobility_profile: 'walking_only',
    transport_modes: ['walking'],
    width: 5,
    lane_count: 1,
    volume: 'low',
    road_surface: 'stone',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 1,
    priority_cycling: 4,
    priority_transit: 4,
    priority_auto: 4,
  },
  amsterdam_canal_street: {
    mobility_profile: 'pedestrian_first',
    transport_modes: ['walking', 'bicycle', 'automobile'],
    width: 10,
    lane_count: 2,
    volume: 'low',
    road_surface: 'paver',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 2,
    priority_cycling: 1,
    priority_transit: 4,
    priority_auto: 3,
  },
  copenhagen_cycle_superhighway: {
    mobility_profile: 'pedestrian_first',
    transport_modes: ['walking', 'bicycle'],
    width: 8,
    lane_count: 1,
    volume: 'medium',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 2,
    priority_cycling: 1,
    priority_transit: 4,
    priority_auto: 4,
  },
  bogota_cicloruta: {
    mobility_profile: 'pedestrian_first',
    transport_modes: ['walking', 'bicycle'],
    width: 9,
    lane_count: 1,
    volume: 'medium',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 2,
    priority_cycling: 1,
    priority_transit: 4,
    priority_auto: 4,
  },
  utrecht_fietsstraat: {
    mobility_profile: 'pedestrian_first',
    transport_modes: ['walking', 'bicycle', 'automobile'],
    width: 9,
    lane_count: 1,
    volume: 'low',
    road_surface: 'paver',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 2,
    priority_cycling: 1,
    priority_transit: 4,
    priority_auto: 3,
  },
  seville_protected_cycle_track: {
    mobility_profile: 'pedestrian_first',
    transport_modes: ['walking', 'bicycle'],
    width: 9,
    lane_count: 1,
    volume: 'medium',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 2,
    priority_cycling: 1,
    priority_transit: 4,
    priority_auto: 4,
  },
  curitiba_brt_axis: {
    mobility_profile: 'balanced',
    transport_modes: ['walking', 'transit', 'automobile'],
    width: 24,
    lane_count: 4,
    volume: 'high',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 3,
    priority_cycling: 4,
    priority_transit: 1,
    priority_auto: 2,
  },
  bogota_transmilenio_avenue: {
    mobility_profile: 'balanced',
    transport_modes: ['walking', 'transit', 'automobile'],
    width: 24,
    lane_count: 4,
    volume: 'high',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 3,
    priority_cycling: 4,
    priority_transit: 1,
    priority_auto: 2,
  },
  hong_kong_tram_street: {
    mobility_profile: 'balanced',
    transport_modes: ['walking', 'transit', 'automobile'],
    width: 16,
    lane_count: 2,
    volume: 'medium',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 2,
    priority_cycling: 4,
    priority_transit: 1,
    priority_auto: 3,
  },
  zurich_tram_boulevard: {
    mobility_profile: 'balanced',
    transport_modes: ['walking', 'transit', 'automobile'],
    width: 18,
    lane_count: 2,
    volume: 'medium',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 2,
    priority_cycling: 4,
    priority_transit: 1,
    priority_auto: 3,
  },
  portland_complete_street: {
    mobility_profile: 'balanced',
    transport_modes: ['walking', 'bicycle', 'transit', 'automobile'],
    width: 20,
    lane_count: 4,
    volume: 'medium',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 2,
    priority_cycling: 2,
    priority_transit: 1,
    priority_auto: 3,
  },
  barcelona_superblock: {
    mobility_profile: 'pedestrian_first',
    transport_modes: ['walking', 'bicycle', 'automobile'],
    width: 10,
    lane_count: 1,
    volume: 'low',
    road_surface: 'paver',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 1,
    priority_cycling: 2,
    priority_transit: 4,
    priority_auto: 3,
  },
  london_exhibition_road: {
    mobility_profile: 'pedestrian_first',
    transport_modes: ['walking', 'bicycle', 'automobile'],
    width: 12,
    lane_count: 1,
    volume: 'low',
    road_surface: 'stone',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 1,
    priority_cycling: 2,
    priority_transit: 4,
    priority_auto: 3,
  },
  paris_champs_elysees: {
    mobility_profile: 'balanced',
    transport_modes: ['walking', 'transit', 'automobile'],
    width: 30,
    lane_count: 6,
    volume: 'high',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 3,
    priority_cycling: 4,
    priority_transit: 2,
    priority_auto: 1,
  },
  mexico_city_reforma: {
    mobility_profile: 'balanced',
    transport_modes: ['walking', 'bicycle', 'transit', 'automobile'],
    width: 28,
    lane_count: 6,
    volume: 'high',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 3,
    priority_cycling: 2,
    priority_transit: 1,
    priority_auto: 4,
  },
  tokyo_local_service_lane: {
    mobility_profile: 'pedestrian_first',
    transport_modes: ['walking', 'bicycle', 'automobile'],
    width: 7,
    lane_count: 1,
    volume: 'low',
    road_surface: 'asphalt',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 1,
    priority_cycling: 2,
    priority_transit: 4,
    priority_auto: 3,
  },
  industrial_freight_collector: {
    mobility_profile: 'vehicle_access',
    transport_modes: ['automobile', 'transit'],
    width: 22,
    lane_count: 4,
    volume: 'high',
    road_surface: 'concrete',
    sidewalks: 'both',
    has_sidewalks: true,
    priority_pedestrian: 4,
    priority_cycling: 4,
    priority_transit: 2,
    priority_auto: 1,
  },
};

export const GREEN_SPACE_AESTHETIC_PRESETS_V2: Record<string, Partial<SiteZoneProperties>> = {
  central_park_english_landscape: {
    tree_density_level: 'dense',
    tree_density: 0.65,
    has_paths: true,
    has_benches: true,
    shade_strategy: 'picturesque_canopy',
  },
  versailles_formal_garden: {
    tree_density_level: 'medium',
    tree_density: 0.5,
    has_paths: true,
    has_benches: true,
    shade_strategy: 'formal_allee',
  },
  high_line_linear_park: {
    tree_density_level: 'medium',
    tree_density: 0.45,
    has_paths: true,
    has_benches: true,
    shade_strategy: 'layered_canopy',
  },
  philosophers_path_garden: {
    tree_density_level: 'dense',
    tree_density: 0.7,
    has_paths: true,
    has_benches: true,
    water_feature: 'canal_edge',
    shade_strategy: 'continuous_canopy',
  },
  superkilen_cultural_park: {
    tree_density_level: 'sparse',
    tree_density: 0.25,
    has_paths: true,
    has_benches: true,
    shade_strategy: 'open_active',
  },
  civic_lawn_commons: {
    tree_density_level: 'medium',
    tree_density: 0.35,
    has_paths: true,
    has_benches: true,
    shade_strategy: 'event_lawn_edge_trees',
  },
  houtan_ecological_park: {
    tree_density_level: 'medium',
    tree_density: 0.5,
    has_paths: true,
    has_benches: true,
    water_feature: 'constructed_wetland',
    shade_strategy: 'ecological_mosaic',
  },
  bishan_river_park: {
    tree_density_level: 'medium',
    tree_density: 0.45,
    has_paths: true,
    has_benches: true,
    water_feature: 'naturalized_stream',
    shade_strategy: 'floodable_greenway',
  },
  wetland_boardwalk_park: {
    tree_density_level: 'medium',
    tree_density: 0.5,
    has_paths: true,
    has_benches: true,
    water_feature: 'wetland',
    shade_strategy: 'ecological_mosaic',
  },
  botanical_garden: {
    tree_density_level: 'dense',
    tree_density: 0.7,
    has_paths: true,
    has_benches: true,
    shade_strategy: 'curated_species_mix',
  },
};

export const PLAZA_AESTHETIC_PRESETS_V2: Record<string, Partial<SiteZoneProperties>> = {
  civic_fountain_square: {
    parking_layout: 'parallel',
    covered: false,
    paving_material: 'stone',
    shade_strategy: 'edge_trees',
    water_feature: 'fountain',
    plaza_program: 'civic',
  },
  piazza_del_campo: {
    parking_layout: 'none',
    covered: false,
    paving_material: 'stone',
    shade_strategy: 'perimeter_arcades',
    plaza_program: 'civic',
  },
  trafalgar_square: {
    parking_layout: 'none',
    covered: false,
    paving_material: 'stone',
    shade_strategy: 'open_civic',
    water_feature: 'fountain',
    plaza_program: 'civic',
  },
  market_plaza: {
    parking_layout: 'parallel',
    covered: false,
    paving_material: 'paver',
    shade_strategy: 'tree_grove',
    plaza_program: 'market',
  },
  times_square_pedestrian: {
    parking_layout: 'none',
    covered: false,
    paving_material: 'concrete',
    shade_strategy: 'urban_canopy',
    plaza_program: 'market',
  },
  festival_plaza: {
    parking_layout: 'perpendicular',
    covered: false,
    paving_material: 'concrete',
    shade_strategy: 'flexible_shade_structures',
    plaza_program: 'events',
  },
  federation_square: {
    parking_layout: 'none',
    covered: false,
    paving_material: 'stone',
    shade_strategy: 'fragmented_shade',
    plaza_program: 'events',
  },
  garden_plaza: {
    parking_layout: 'parallel',
    covered: false,
    paving_material: 'stone',
    shade_strategy: 'garden_canopy',
    plaza_program: 'leisure',
  },
  waterfront_boardwalk_plaza: {
    parking_layout: 'parallel',
    covered: false,
    paving_material: 'wood_deck',
    shade_strategy: 'linear_trees',
    water_feature: 'waterfront',
    plaza_program: 'promenade',
  },
  harbour_edge_plaza: {
    parking_layout: 'parallel',
    covered: false,
    paving_material: 'stone',
    shade_strategy: 'waterfront_trees',
    water_feature: 'waterfront',
    plaza_program: 'promenade',
  },
};
export function normalizeTransportModes(value: unknown): TransportModeKey[] {
  if (!Array.isArray(value)) return [];
  const allowed = new Set<TransportModeKey>(TRANSPORT_MODE_ORDER);
  const unique = new Set<TransportModeKey>();
  for (const mode of value) {
    if (typeof mode === 'string' && allowed.has(mode as TransportModeKey)) {
      unique.add(mode as TransportModeKey);
    }
  }
  return TRANSPORT_MODE_ORDER.filter((mode) => unique.has(mode));
}

export function inferTransportModesFromProperties(properties: SiteZoneProperties): TransportModeKey[] {
  const explicit = normalizeTransportModes(properties.transport_modes);
  if (explicit.length > 0) return explicit;

  const profile = String(properties.mobility_profile || '').toLowerCase();
  if (profile === 'walking_only') return ['walking'];
  if (profile === 'pedestrian_first') return ['walking', 'bicycle'];
  if (profile === 'vehicle_access') return ['automobile', 'transit'];
  if (profile === 'balanced') return ['walking', 'bicycle', 'transit', 'automobile'];

  return ['walking', 'automobile'];
}

export function inferMobilityProfileFromModes(modes: TransportModeKey[]): 'walking_only' | 'pedestrian_first' | 'balanced' | 'vehicle_access' {
  const hasWalk = modes.includes('walking');
  const hasBike = modes.includes('bicycle');
  const hasTransit = modes.includes('transit');
  const hasAuto = modes.includes('automobile');

  if (hasWalk && !hasBike && !hasTransit && !hasAuto) return 'walking_only';
  if (hasAuto && !hasWalk && !hasBike) return 'vehicle_access';
  if (hasWalk && !hasAuto) return 'pedestrian_first';
  if (hasAuto && (hasTransit || hasBike || hasWalk)) return 'balanced';
  return 'pedestrian_first';
}

export function applyModeDrivenRoadDefaults(
  base: SiteZoneProperties,
  inputModes: TransportModeKey[],
  volumeInput?: string,
): SiteZoneProperties {
  const modes = TRANSPORT_MODE_ORDER.filter((mode) => inputModes.includes(mode));
  const next: SiteZoneProperties = { ...base };

  next.transport_modes = modes.length > 0 ? modes : undefined;

  const activeCount = Math.max(modes.length, 1);
  const ranks = new Map<TransportModeKey, number>();
  modes.forEach((mode, idx) => ranks.set(mode, idx + 1));
  TRANSPORT_MODE_ORDER
    .filter((mode) => !modes.includes(mode))
    .forEach((mode) => ranks.set(mode, Math.min(4, activeCount + 1)));

  next.priority_pedestrian = ranks.get('walking');
  next.priority_cycling = ranks.get('bicycle');
  next.priority_transit = ranks.get('transit');
  next.priority_auto = ranks.get('automobile');

  const volume = (volumeInput || String(next.volume || 'medium')) as 'low' | 'medium' | 'high';
  const hasWalk = modes.includes('walking');
  const hasBike = modes.includes('bicycle');
  const hasTransit = modes.includes('transit');
  const hasAuto = modes.includes('automobile');

  next.mobility_profile = inferMobilityProfileFromModes(modes);
  next.has_sidewalks = hasWalk;
  next.sidewalks = hasWalk ? 'both' : 'none';

  if (hasAuto) {
    next.width = volume === 'high' ? 22 : volume === 'low' ? 12 : 16;
    next.lane_count = volume === 'high' ? 4 : 2;
    next.road_surface = hasTransit ? 'asphalt' : (next.road_surface as string) || 'asphalt';
  } else if (hasBike && hasWalk) {
    next.width = volume === 'high' ? 11 : volume === 'low' ? 7 : 9;
    next.lane_count = 1;
    next.road_surface = (next.road_surface as string) || 'asphalt';
  } else if (hasWalk) {
    next.width = volume === 'high' ? 8 : volume === 'low' ? 5 : 6;
    next.lane_count = 1;
    next.road_surface = (next.road_surface as string) || 'paver';
  }

  if (hasTransit && !hasAuto) {
    next.width = Math.max(12, Number(next.width || 12));
    next.lane_count = Math.max(2, Number(next.lane_count || 2));
  }

  return next;
}

export function mapDevelopmentTypeToCategory(value?: string): string | undefined {
  if (!value) return undefined;
  if (value === 'residential') return 'residential';
  if (value === 'commercial') return 'commercial';
  if (value === 'mixed_use') return 'mixed_use';
  if (value === 'institutional') return 'institutional';
  if (value === 'industrial') return 'industrial';
  return 'other';
}
