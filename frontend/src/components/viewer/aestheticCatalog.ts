import type { SiteZoneProperties } from '@/types';

export type AestheticCategory = {
  id: string;
  label: string;
  description: string;
};

export type TransportModeKey = 'walking' | 'bicycle' | 'transit' | 'automobile';

export type StyleProfile = {
  materials: string[];
  massing: string;
  facadeRhythm: string;
  roofForm: string;
  frontageType: string;
  articulation: string;
  publicRealm: string;
};

export type ArchetypeImage = {
  id: string;
  label: string;
  description: string;
  camera: 'street' | 'corner' | 'promenade' | 'courtyard';
  imageUrl: string;
};

export type GenerationStyleInput = {
  developmentType?: string;
  buildingSubcategory?: string;
  aestheticCategoryId?: string;
  aestheticCategoryLabel?: string;
  archetypeId: string;
  archetypeLabel: string;
  archetypeImageUrl: string;
  archetypeImageIds?: string[];
  styleProfile: StyleProfile;
};

export type AestheticOption = {
  id: string;
  categoryId?: string;
  label: string;
  description: string;
  photoUrl: string;
  photoUrls?: string[];
  transportModes?: TransportModeKey[];
  archetypeImages?: ArchetypeImage[];
  styleProfile?: StyleProfile;
  generationStyleInput?: Partial<GenerationStyleInput>;
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
const UNSPLASH_TRANSPORT_POOL = [
  'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1486325212027-8081e485255e?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1431576901776-e539bd916ba2?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1479839672679-a46483c0e7c8?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1513828583688-c52646db42da?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1528360983277-13d401cdc186?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1479510318569-1e327f2b55e3?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=1200&h=900&q=80',
];

const UNSPLASH_GREEN_SPACE_POOL = [
  'https://images.unsplash.com/photo-1501854140801-50d01698950b?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1528360983277-13d401cdc186?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1464146072230-91cabc968266?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1449844908441-8829872d2607?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1533929736458-ca588d08c8be?auto=format&fit=crop&w=1200&h=900&q=80',
];

const UNSPLASH_PLAZA_POOL = [
  'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1479839672679-a46483c0e7c8?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1529260830199-42c24126f198?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1533929736458-ca588d08c8be?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1431576901776-e539bd916ba2?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1486325212027-8081e485255e?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&h=900&q=80',
  'https://images.unsplash.com/photo-1464146072230-91cabc968266?auto=format&fit=crop&w=1200&h=900&q=80',
];

function assignPhotoExamples(options: AestheticOption[], pool: string[]): void {
  if (pool.length === 0) return;

  options.forEach((option, index) => {
    const first = pool[index % pool.length];
    const photoUrls = Array.from({ length: 4 }, (_, offset) => pool[(index + offset) % pool.length]);
    option.photoUrl = first;
    option.photoUrls = photoUrls;
  });
}
export const BUILDING_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = [
  {
    id: 'historical',
    label: 'Historical',
    description: 'Heritage urban forms with masonry texture, ornament, and streetwall continuity',
  },
  {
    id: 'contemporary_urban',
    label: 'Contemporary Urban',
    description: 'Current mixed-use and residential urban forms with active podiums',
  },
  {
    id: 'modernist',
    label: 'Modernist',
    description: 'Clear geometric composition with restrained detailing',
  },
  {
    id: 'classical',
    label: 'Classical',
    description: 'Formal symmetry, proportion, and civic facade order',
  },
  {
    id: 'industrial_brick',
    label: 'Industrial Brick',
    description: 'Loft and warehouse language with masonry and steel expression',
  },
  {
    id: 'scandinavian_nordic',
    label: 'Scandinavian / Nordic',
    description: 'Warm minimal palettes and human-scaled contemporary blocks',
  },
  {
    id: 'mediterranean',
    label: 'Mediterranean',
    description: 'Arcades, stucco and stone palettes, and shaded public edges',
  },
  {
    id: 'futuristic',
    label: 'Futuristic',
    description: 'Expressive forward-looking forms and advanced envelope language',
  },
  {
    id: 'art_deco',
    label: 'Art Deco',
    description: 'Stepped vertical composition with ornamental crown detailing',
  },
  {
    id: 'traditional_vernacular',
    label: 'Traditional / Vernacular',
    description: 'Regionally rooted forms and local material expression',
  },
  {
    id: 'minimalist',
    label: 'Minimalist',
    description: 'Reduced form language with disciplined proportion',
  },
  {
    id: 'parisian',
    label: 'Parisian',
    description: 'Boulevard-scaled stone facades with balcony continuity',
  },
  {
    id: 'brownstone_rowhouse',
    label: 'Brownstone / Rowhouse',
    description: 'Stoop-fronted rowhouse rhythm and fine-grain streetwall',
  },
  {
    id: 'mountain_alpine',
    label: 'Mountain / Alpine',
    description: 'Climate-adapted mountain forms with sloped roofs and heavy bases',
  },
  {
    id: 'transit_oriented_contemporary',
    label: 'Transit-Oriented Contemporary',
    description: 'Station-area density with active, walkable frontage systems',
  },
  {
    id: 'glass_tower_modern',
    label: 'Glass Tower Modern',
    description: 'High-rise curtain-wall towers integrated with podium streetwalls',
  },
  {
    id: 'civic_monumental',
    label: 'Civic Monumental',
    description: 'Symbolic institutional forms with durable civic presence',
  },
  {
    id: 'japanese_contemporary',
    label: 'Japanese Contemporary',
    description: 'Precise massing, layered thresholds, and refined material transitions',
  },
  {
    id: 'eco_urban_green_architecture',
    label: 'Eco-Urban / Green Architecture',
    description: 'Biophilic envelopes and climate-responsive building systems',
  },
  {
    id: 'coastal_resort_contemporary',
    label: 'Coastal / Resort Contemporary',
    description: 'Light-toned forms with terraces, breezeways, and waterfront identity',
  },
  {
    id: 'other',
    label: 'Custom / Other',
    description: 'Custom style direction from prompt with structured metadata support',
  },
];

type BuildingArchetypeVariant = {
  id: string;
  label: string;
  description: string;
  camera: ArchetypeImage['camera'];
};

type BuildingStyleSeed = {
  id: string;
  categoryId: string;
  label: string;
  description: string;
  palette: {
    skyTop: string;
    skyBottom: string;
    facadePrimary: string;
    facadeSecondary: string;
    accent: string;
    window: string;
    ground: string;
    street: string;
    landscape: string;
  };
  styleProfile: StyleProfile;
};

const BUILDING_ARCHETYPE_VARIANTS: BuildingArchetypeVariant[] = [
  { id: 'street_front', label: 'Street Front Archetype', description: 'Primary facade view for street presence and frontage language', camera: 'street' },
  { id: 'corner_view', label: 'Corner Massing Archetype', description: 'Corner perspective for massing transitions and edge behavior', camera: 'corner' },
  { id: 'promenade_view', label: 'Promenade Archetype', description: 'Pedestrian perspective for public realm and ground-floor condition', camera: 'promenade' },
  { id: 'courtyard_view', label: 'Courtyard Archetype', description: 'Inner-block perspective for depth and facade rhythm continuity', camera: 'courtyard' },
];

const BUILDING_STYLE_SEEDS: BuildingStyleSeed[] = [
  {
    id: 'heritage_brick_main_street',
    categoryId: 'historical',
    label: 'Heritage Brick Main Street',
    description: 'Canonical heritage mid-rise streetwall with traditional masonry articulation',
    palette: { skyTop: '#95a9bf', skyBottom: '#e7edf5', facadePrimary: '#97523f', facadeSecondary: '#b66a4f', accent: '#5e372b', window: '#dbf1ff', ground: '#d6c5b2', street: '#55504b', landscape: '#7f9f72' },
    styleProfile: { materials: ['red brick', 'stone trim', 'ornamental metal'], massing: '3-6 storey continuous streetwall', facadeRhythm: 'fine vertical bays', roofForm: 'flat roof with decorative cornice', frontageType: 'active main-street edge', articulation: 'recessed entries and lintel hierarchy', publicRealm: 'generous sidewalks with street trees' },
  },
  {
    id: 'urban_podium_midrise',
    categoryId: 'contemporary_urban',
    label: 'Urban Podium Mid-Rise',
    description: 'Contemporary mixed-use podium and mid-rise block archetype',
    palette: { skyTop: '#8ea6bf', skyBottom: '#ecf3fb', facadePrimary: '#8f9da9', facadeSecondary: '#c2cdd9', accent: '#425469', window: '#d8efff', ground: '#d4d8de', street: '#4d5866', landscape: '#7ca085' },
    styleProfile: { materials: ['fiber cement', 'metal panel', 'clear glazing'], massing: '5-12 storey podium-based form', facadeRhythm: 'regular balcony and mullion cadence', roofForm: 'flat roof with screened mechanical zone', frontageType: 'mixed-use podium frontage', articulation: 'setback upper floors and expressed podium', publicRealm: 'active retail sidewalk interface' },
  },
  {
    id: 'bauhaus_modernist_block',
    categoryId: 'modernist',
    label: 'Bauhaus Modernist Block',
    description: 'Modernist archetype with planar surfaces and rational window ordering',
    palette: { skyTop: '#95abc1', skyBottom: '#edf3f9', facadePrimary: '#c7ccd2', facadeSecondary: '#aeb7c2', accent: '#303845', window: '#ddf0ff', ground: '#d9dde2', street: '#525d6a', landscape: '#7f9785' },
    styleProfile: { materials: ['smooth stucco', 'steel', 'ribbon glazing'], massing: 'rectilinear slab and bar composition', facadeRhythm: 'horizontal emphasis with modular bays', roofForm: 'flat roof', frontageType: 'civic lobby setback', articulation: 'clean reveals and cantilevered slab edges', publicRealm: 'minimal hardscape and curated planting bands' },
  },
  {
    id: 'neoclassical_civic_block',
    categoryId: 'classical',
    label: 'Neoclassical Civic Block',
    description: 'Classical archetype with formal proportion, base-middle-top hierarchy, and ceremonial entry',
    palette: { skyTop: '#9ba9b9', skyBottom: '#eef1f5', facadePrimary: '#d8ceb9', facadeSecondary: '#c7b99f', accent: '#6f6758', window: '#d9ecff', ground: '#d4cab8', street: '#5a5651', landscape: '#81986f' },
    styleProfile: { materials: ['limestone', 'cast stone', 'ornamental metal'], massing: '3-8 storey formal civic frontage', facadeRhythm: 'symmetrical pilaster-led bays', roofForm: 'cornice-capped flat roof', frontageType: 'ceremonial public frontage', articulation: 'colonnades and hierarchical entry framing', publicRealm: 'formal forecourt and allee tree rows' },
  },
  {
    id: 'warehouse_loft_block',
    categoryId: 'industrial_brick',
    label: 'Warehouse Loft Block',
    description: 'Industrial brick loft archetype with large openings and heavy masonry character',
    palette: { skyTop: '#8b9dad', skyBottom: '#e4eaf0', facadePrimary: '#804c3d', facadeSecondary: '#a8644d', accent: '#3d2d28', window: '#dcefff', ground: '#ccb9a7', street: '#4f4b47', landscape: '#729366' },
    styleProfile: { materials: ['reclaimed brick', 'blackened steel', 'concrete bands'], massing: '4-8 storey robust block', facadeRhythm: 'large repetitive industrial bays', roofForm: 'flat roof with utility penthouse', frontageType: 'maker and production frontage', articulation: 'deep reveals and expressed structural frame', publicRealm: 'service-ready curb and adaptable frontage' },
  },
  {
    id: 'nordic_timber_midrise',
    categoryId: 'scandinavian_nordic',
    label: 'Nordic Timber Mid-Rise',
    description: 'Scandinavian archetype with warm timber expression and calm contemporary rhythm',
    palette: { skyTop: '#95aec6', skyBottom: '#f0f6fb', facadePrimary: '#c6b39f', facadeSecondary: '#e0d1c2', accent: '#5d6f75', window: '#e4f4ff', ground: '#d8dace', street: '#5a6166', landscape: '#80a287' },
    styleProfile: { materials: ['thermally treated timber', 'light render', 'powder-coated metal'], massing: '5-9 storey courtyard/perimeter form', facadeRhythm: 'calm modular timber-grid bays', roofForm: 'flat roof with soft parapet', frontageType: 'residential stoop and shared lobby edge', articulation: 'recessed balconies and timber frame depth', publicRealm: 'rain-garden edges and walkable courtyards' },
  },
  {
    id: 'mediterranean_arcade_block',
    categoryId: 'mediterranean',
    label: 'Mediterranean Arcade Block',
    description: 'Mediterranean archetype with shaded arcades and warm textured facades',
    palette: { skyTop: '#85adc8', skyBottom: '#ebf7ff', facadePrimary: '#d8af8b', facadeSecondary: '#efd3b3', accent: '#8c5c42', window: '#ddf3ff', ground: '#d0bf9c', street: '#5d5953', landscape: '#8ca76f' },
    styleProfile: { materials: ['lime plaster', 'terracotta', 'natural stone'], massing: '3-6 storey arcade-lined block', facadeRhythm: 'arched bay cadence', roofForm: 'tile and flat parapet hybrid', frontageType: 'arcaded mixed-use frontage', articulation: 'loggias and balcony overhangs', publicRealm: 'shaded plazas and drought-resilient planting' },
  },
  {
    id: 'parametric_future_hub',
    categoryId: 'futuristic',
    label: 'Parametric Future Hub',
    description: 'Futuristic archetype with sculpted envelope transitions and high-tech frontage',
    palette: { skyTop: '#7394b9', skyBottom: '#e2eeff', facadePrimary: '#8190a7', facadeSecondary: '#b5c7dd', accent: '#3ec4ff', window: '#dcf4ff', ground: '#c9d5e0', street: '#434c5b', landscape: '#719889' },
    styleProfile: { materials: ['advanced composites', 'high-performance glass', 'anodized metal'], massing: 'sculpted mid/high-rise hybrid', facadeRhythm: 'adaptive panel rhythm', roofForm: 'integrated roofscape system', frontageType: 'innovation district frontage', articulation: 'parametric folds and tapered corners', publicRealm: 'interactive plazas and integrated lighting' },
  },
  {
    id: 'art_deco_setback_tower',
    categoryId: 'art_deco',
    label: 'Art Deco Setback Tower',
    description: 'Art Deco archetype with stepped profile and strong vertical emphasis',
    palette: { skyTop: '#8d9fb6', skyBottom: '#e8eef6', facadePrimary: '#b09063', facadeSecondary: '#d2b585', accent: '#5b4432', window: '#daeeff', ground: '#cdbca6', street: '#57514b', landscape: '#80966e' },
    styleProfile: { materials: ['buff stone', 'decorative metal', 'spandrel glazing'], massing: 'setback tower on urban base', facadeRhythm: 'vertical pilaster rhythm', roofForm: 'stepped crown profile', frontageType: 'grand lobby and corner retail frontage', articulation: 'ornamental relief and sculpted crown line', publicRealm: 'formal sidewalks and ceremonial lighting' },
  },
  {
    id: 'vernacular_market_lane',
    categoryId: 'traditional_vernacular',
    label: 'Vernacular Market Lane',
    description: 'Traditional archetype with local materials and narrow incremental frontage',
    palette: { skyTop: '#9eb0b8', skyBottom: '#eff4f6', facadePrimary: '#9f7554', facadeSecondary: '#c5976d', accent: '#654a36', window: '#dbeef9', ground: '#cfc0ac', street: '#5b554f', landscape: '#80946f' },
    styleProfile: { materials: ['local brick', 'timber lintels', 'lime render'], massing: '2-5 storey incremental street edge', facadeRhythm: 'narrow shopfront cadence', roofForm: 'mixed gable and parapet roofs', frontageType: 'market lane active frontage', articulation: 'porches and painted trim layers', publicRealm: 'small plazas and market spillout' },
  },
  {
    id: 'minimalist_courtyard_block',
    categoryId: 'minimalist',
    label: 'Minimalist Courtyard Block',
    description: 'Minimalist archetype with precise openings and reduced material palette',
    palette: { skyTop: '#a7b3c1', skyBottom: '#f4f7fb', facadePrimary: '#c5c9cf', facadeSecondary: '#e2e6eb', accent: '#4c5663', window: '#e3f2ff', ground: '#d9dde2', street: '#59626f', landscape: '#88a28d' },
    styleProfile: { materials: ['light concrete', 'clear glazing', 'powder-coated metal'], massing: 'orthogonal courtyard perimeter block', facadeRhythm: 'strict modular opening grid', roofForm: 'flat roof', frontageType: 'quiet residential frontage', articulation: 'shadow joints and subtle recesses', publicRealm: 'minimal hardscape with controlled planting' },
  },
  {
    id: 'haussmann_boulevard_block',
    categoryId: 'parisian',
    label: 'Parisian Boulevard Block',
    description: 'Parisian archetype with elegant stone facade continuity and balcony belts',
    palette: { skyTop: '#94a8bd', skyBottom: '#edf3fa', facadePrimary: '#d6c9b1', facadeSecondary: '#e7dbc4', accent: '#6f5d4b', window: '#deedff', ground: '#d5cab5', street: '#58544f', landscape: '#809a72' },
    styleProfile: { materials: ['cut limestone', 'wrought iron', 'painted timber'], massing: '5-7 storey boulevard-aligned block', facadeRhythm: 'regular bay rhythm with balcony bands', roofForm: 'mansard-inspired crown over flat slab', frontageType: 'retail base with formal residential entries', articulation: 'cornices and wrought iron balcony detailing', publicRealm: 'formal boulevards with aligned tree canopy' },
  },
  {
    id: 'brownstone_rowhouse_stoop',
    categoryId: 'brownstone_rowhouse',
    label: 'Brownstone Stoop Rowhouse',
    description: 'Brownstone archetype with stoops, tight bays, and attached townhouse character',
    palette: { skyTop: '#8ca3bc', skyBottom: '#e8f0f9', facadePrimary: '#7f4c3b', facadeSecondary: '#a8664f', accent: '#4d2f26', window: '#ddefff', ground: '#ccb7a4', street: '#524c46', landscape: '#749767' },
    styleProfile: { materials: ['brownstone', 'ornamental railings', 'painted wood doors'], massing: '3-5 storey attached rowhouses', facadeRhythm: 'tight vertical townhouse bays', roofForm: 'flat roof with cornice', frontageType: 'stoop-front residential edge', articulation: 'stoops, lintels, and layered door surrounds', publicRealm: 'tree-lined sidewalks with shallow setbacks' },
  },
  {
    id: 'alpine_village_edge',
    categoryId: 'mountain_alpine',
    label: 'Alpine Village Edge',
    description: 'Mountain archetype with weather-ready envelope and pitched roof silhouette',
    palette: { skyTop: '#87a3c0', skyBottom: '#e5effa', facadePrimary: '#a18468', facadeSecondary: '#c3a486', accent: '#5b4536', window: '#e0f3ff', ground: '#c9b8a0', street: '#55504a', landscape: '#709064' },
    styleProfile: { materials: ['stone plinth', 'timber cladding', 'metal roof'], massing: '2-5 storey alpine streetfront cluster', facadeRhythm: 'mixed bay widths and balconies', roofForm: 'steep gable and shed roofs', frontageType: 'village high-street frontage', articulation: 'balcony projection and roof overhangs', publicRealm: 'compact streets with conifer planting' },
  },
  {
    id: 'tod_station_streetwall',
    categoryId: 'transit_oriented_contemporary',
    label: 'TOD Station Streetwall',
    description: 'Transit-oriented archetype with dense podium form and multimodal frontage',
    palette: { skyTop: '#8ea8c2', skyBottom: '#ebf4ff', facadePrimary: '#8999a9', facadeSecondary: '#b9c5d3', accent: '#2f6ca5', window: '#dbefff', ground: '#d4d9df', street: '#4f5a67', landscape: '#7ea086' },
    styleProfile: { materials: ['brick veneer', 'glass storefront systems', 'metal canopies'], massing: '6-14 storey station-area block', facadeRhythm: 'active podium with modular bays', roofForm: 'flat roof with terrace setbacks', frontageType: 'transit plaza and retail frontage', articulation: 'podium-tower transitions and corner entries', publicRealm: 'frequent doors, bike parking, transit-ready sidewalks' },
  },
  {
    id: 'glass_tower_podium',
    categoryId: 'glass_tower_modern',
    label: 'Glass Tower Podium',
    description: 'Glass tower archetype with streetwall podium and high-rise verticality',
    palette: { skyTop: '#7c9bc2', skyBottom: '#e4f1ff', facadePrimary: '#6f859b', facadeSecondary: '#9eb6cd', accent: '#31506f', window: '#d9f2ff', ground: '#ccd7e2', street: '#495664', landscape: '#799c8a' },
    styleProfile: { materials: ['curtain wall glazing', 'aluminum mullions', 'stone podium base'], massing: 'point tower on 3-6 storey podium', facadeRhythm: 'vertical mullion rhythm and slab lines', roofForm: 'flat roof with screened crown', frontageType: 'retail and lobby podium frontage', articulation: 'chamfered corners and podium terraces', publicRealm: 'expanded corners and urban plaza edges' },
  },
  {
    id: 'civic_monumental_institution',
    categoryId: 'civic_monumental',
    label: 'Civic Monumental Institution',
    description: 'Monumental civic archetype with clear hierarchy and durable public identity',
    palette: { skyTop: '#95a8ba', skyBottom: '#ecf1f6', facadePrimary: '#c8c1b4', facadeSecondary: '#ddd7ca', accent: '#5a5b60', window: '#d8ecff', ground: '#d6d0c5', street: '#5b5b59', landscape: '#829371' },
    styleProfile: { materials: ['stone cladding', 'bronze details', 'high-durability glazing'], massing: 'institutional campus blocks and pavilions', facadeRhythm: 'ordered civic bay spacing', roofForm: 'flat roof with expressed parapet', frontageType: 'civic forecourt frontage', articulation: 'monumental base and ceremonial entry axis', publicRealm: 'formal squares and shaded gathering steps' },
  },
  {
    id: 'japanese_contemporary_lanehouse',
    categoryId: 'japanese_contemporary',
    label: 'Japanese Contemporary Lanehouse',
    description: 'Japanese contemporary archetype with layered screens and refined thresholds',
    palette: { skyTop: '#95aec4', skyBottom: '#edf5fc', facadePrimary: '#b8b3a7', facadeSecondary: '#d4cec2', accent: '#4d5058', window: '#e2f3ff', ground: '#d6d4cc', street: '#555a63', landscape: '#819d87' },
    styleProfile: { materials: ['textured plaster', 'charred timber accents', 'fine metal screens'], massing: 'compact mid-rise lanehouse blocks', facadeRhythm: 'screen-layered opening cadence', roofForm: 'flat and shallow-pitch hybrid roofs', frontageType: 'recessed lane frontage', articulation: 'voids, screens, and precision shadow lines', publicRealm: 'small courts and narrow pedestrian pathways' },
  },
  {
    id: 'eco_urban_bioclimatic_block',
    categoryId: 'eco_urban_green_architecture',
    label: 'Eco-Urban Bioclimatic Block',
    description: 'Eco-urban archetype with planted facades, passive systems, and climate-smart form',
    palette: { skyTop: '#83a8ba', skyBottom: '#e6f8ff', facadePrimary: '#7f9e90', facadeSecondary: '#aac5b8', accent: '#3d6f60', window: '#daf3ff', ground: '#c9dacd', street: '#4b5e58', landscape: '#6ea680' },
    styleProfile: { materials: ['engineered timber', 'green facade systems', 'high-performance glazing'], massing: 'terraced mid-rise with vegetated setbacks', facadeRhythm: 'modular bays with integrated planting', roofForm: 'green roofs and solar canopy zones', frontageType: 'biophilic mixed-use frontage', articulation: 'terracing, fins, and planted balconies', publicRealm: 'bioswales, rain gardens, and shaded loops' },
  },
  {
    id: 'coastal_resort_contemporary_block',
    categoryId: 'coastal_resort_contemporary',
    label: 'Coastal Resort Contemporary Block',
    description: 'Coastal archetype with terraces, breezeways, and light waterfront material palette',
    palette: { skyTop: '#84adc8', skyBottom: '#e7f8ff', facadePrimary: '#d6ddd9', facadeSecondary: '#edf2ef', accent: '#4c809e', window: '#def6ff', ground: '#d7d9d2', street: '#5a6770', landscape: '#79a593' },
    styleProfile: { materials: ['light stucco', 'salt-resistant metal', 'glass guardrails'], massing: 'stepped terrace blocks with view corridors', facadeRhythm: 'wide bays with horizontal balcony layers', roofForm: 'flat roof with pergola terraces', frontageType: 'promenade and hospitality frontage', articulation: 'deep balconies and breezeway cuts', publicRealm: 'coastal planting and shaded promenade seating' },
  },
  {
    id: 'custom_style_archetype',
    categoryId: 'other',
    label: 'Custom Style Archetype',
    description: 'Structured custom archetype for user-directed style prompts',
    palette: { skyTop: '#8ea2c2', skyBottom: '#e9effa', facadePrimary: '#9094a0', facadeSecondary: '#bac0cb', accent: '#434957', window: '#e0f1ff', ground: '#d2d6df', street: '#505765', landscape: '#7e9484' },
    styleProfile: { materials: ['user-defined primary material', 'supporting cladding', 'context detailing'], massing: 'user-defined massing envelope', facadeRhythm: 'user-defined facade rhythm', roofForm: 'user-defined roof strategy', frontageType: 'user-defined frontage behavior', articulation: 'user-defined articulation language', publicRealm: 'user-defined public realm integration' },
  },
];

function hashSeed(value: string): number {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = ((hash << 5) - hash + value.charCodeAt(index)) | 0;
  }
  return Math.abs(hash);
}

function buildBuildingArchetypeDataUri(seed: BuildingStyleSeed, variant: BuildingArchetypeVariant): string {
  const hashed = hashSeed(`${seed.id}:${variant.id}`);
  const cameraOffset: Record<ArchetypeImage['camera'], number> = { street: 0, corner: -70, promenade: 52, courtyard: 22 };
  const baseX = 180 + (hashed % 72) + cameraOffset[variant.camera];
  const baseY = 210 + (hashed % 44);
  const width = 560 + (hashed % 112);
  const height = 360 + ((hashed >> 2) % 156);
  const wingWidth = 160 + ((hashed >> 4) % 68);
  const wingHeight = 290 + ((hashed >> 5) % 120);
  const windowCols = 7 + (hashed % 3);
  const windowRows = 5 + ((hashed >> 3) % 3);
  const windowGutterX = 14;
  const windowGutterY = 12;
  const windowWidth = Math.max(14, Math.floor((width - 62 - windowGutterX * (windowCols - 1)) / windowCols));
  const windowHeight = Math.max(14, Math.floor((height - 70 - windowGutterY * (windowRows - 1)) / windowRows));

  const windows: string[] = [];
  const startX = baseX + 30;
  const startY = baseY + 38;
  for (let row = 0; row < windowRows; row += 1) {
    for (let col = 0; col < windowCols; col += 1) {
      const x = startX + col * (windowWidth + windowGutterX);
      const y = startY + row * (windowHeight + windowGutterY);
      windows.push(`<rect x="${x}" y="${y}" width="${windowWidth}" height="${windowHeight}" rx="3" fill="${seed.palette.window}" fill-opacity="0.92" />`);
    }
  }

  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" role="img" aria-label="${seed.label} ${variant.label}">
  <defs>
    <linearGradient id="sky-${seed.id}-${variant.id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${seed.palette.skyTop}" />
      <stop offset="100%" stop-color="${seed.palette.skyBottom}" />
    </linearGradient>
    <linearGradient id="facade-${seed.id}-${variant.id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${seed.palette.facadeSecondary}" />
      <stop offset="100%" stop-color="${seed.palette.facadePrimary}" />
    </linearGradient>
    <linearGradient id="street-${seed.id}-${variant.id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${seed.palette.street}" />
      <stop offset="100%" stop-color="#3a3f49" />
    </linearGradient>
  </defs>
  <rect width="1200" height="900" fill="url(#sky-${seed.id}-${variant.id})" />
  <rect y="620" width="1200" height="170" fill="${seed.palette.ground}" />
  <rect y="740" width="1200" height="160" fill="url(#street-${seed.id}-${variant.id})" />
  <rect x="${baseX}" y="${baseY}" width="${width}" height="${height}" rx="10" fill="url(#facade-${seed.id}-${variant.id})" />
  <rect x="${baseX + width - wingWidth + 14}" y="${baseY + 30}" width="${wingWidth}" height="${wingHeight}" rx="8" fill="${seed.palette.facadeSecondary}" fill-opacity="0.95" />
  <rect x="${baseX + 22}" y="${baseY + height - 92}" width="${Math.max(120, Math.floor(width * 0.28))}" height="86" rx="6" fill="${seed.palette.accent}" fill-opacity="0.92" />
  ${windows.join('\n  ')}
  <rect x="${baseX - 18}" y="${baseY - 16}" width="${width + 36}" height="18" rx="6" fill="${seed.palette.accent}" fill-opacity="0.86" />
  <rect x="88" y="662" width="196" height="56" rx="28" fill="${seed.palette.landscape}" />
  <rect x="896" y="650" width="220" height="58" rx="29" fill="${seed.palette.landscape}" />
  <text x="64" y="82" fill="#f8fafc" font-family="Inter, Arial, sans-serif" font-size="28" font-weight="700">${seed.label}</text>
  <text x="64" y="114" fill="#dbeafe" font-family="Inter, Arial, sans-serif" font-size="18">${variant.label}</text>
</svg>`.trim();

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

function toArchetypeImage(seed: BuildingStyleSeed, variant: BuildingArchetypeVariant): ArchetypeImage {
  return {
    id: `${seed.id}_${variant.id}`,
    label: variant.label,
    description: variant.description,
    camera: variant.camera,
    imageUrl: buildBuildingArchetypeDataUri(seed, variant),
  };
}

function toBuildingAestheticOption(seed: BuildingStyleSeed): AestheticOption {
  const archetypeImages = BUILDING_ARCHETYPE_VARIANTS.map((variant) => toArchetypeImage(seed, variant));
  const primary = archetypeImages[0];
  const categoryLabel = BUILDING_AESTHETIC_CATEGORIES_V2.find((category) => category.id === seed.categoryId)?.label;

  return {
    id: seed.id,
    categoryId: seed.categoryId,
    label: seed.label,
    description: seed.description,
    photoUrl: primary.imageUrl,
    photoUrls: archetypeImages.map((image) => image.imageUrl),
    archetypeImages,
    styleProfile: seed.styleProfile,
    generationStyleInput: {
      buildingSubcategory: seed.id,
      aestheticCategoryId: seed.categoryId,
      aestheticCategoryLabel: categoryLabel,
      archetypeId: primary.id,
      archetypeLabel: primary.label,
      archetypeImageUrl: primary.imageUrl,
      archetypeImageIds: archetypeImages.map((image) => image.id),
      styleProfile: seed.styleProfile,
    },
  };
}

export const BUILDING_AESTHETIC_OPTIONS_V2: AestheticOption[] = BUILDING_STYLE_SEEDS.map((seed) => toBuildingAestheticOption(seed));
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
    photoUrl: 'https://loremflickr.com/1200/900/kyoto,philosophers,path,canal,walkway',
    transportModes: ['walking'],
  },
  {
    id: 'copenhagen_stroget',
    categoryId: 'pedestrian_realm',
    label: 'Copenhagen Stroget',
    description: 'Car-free retail spine with active frontages and generous walking space',
    photoUrl: 'https://loremflickr.com/1200/900/copenhagen,stroget,pedestrian,street',
    transportModes: ['walking'],
  },
  {
    id: 'barcelona_la_rambla',
    categoryId: 'pedestrian_realm',
    label: 'Barcelona La Rambla',
    description: 'Tree-lined promenade with central pedestrian flow and edge access',
    photoUrl: 'https://loremflickr.com/1200/900/barcelona,la,rambla,pedestrian',
    transportModes: ['walking', 'transit'],
  },
  {
    id: 'venice_fondamenta_walk',
    categoryId: 'pedestrian_realm',
    label: 'Venice Fondamenta Walk',
    description: 'Water-edge walkways with narrow carriageways and high pedestrian priority',
    photoUrl: 'https://loremflickr.com/1200/900/venice,canal,walkway,street',
    transportModes: ['walking'],
  },
  {
    id: 'amsterdam_canal_street',
    categoryId: 'cycling_network',
    label: 'Amsterdam Canal Street',
    description: 'Cycling-first canal corridor with calm local vehicle access',
    photoUrl: 'https://loremflickr.com/1200/900/amsterdam,canal,street,bicycle',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'copenhagen_cycle_superhighway',
    categoryId: 'cycling_network',
    label: 'Copenhagen Cycle Superhighway',
    description: 'Protected long-distance bike corridor with smooth intersections',
    photoUrl: 'https://loremflickr.com/1200/900/copenhagen,cycle,track,street',
    transportModes: ['walking', 'bicycle'],
  },
  {
    id: 'bogota_cicloruta',
    categoryId: 'cycling_network',
    label: 'Bogota Cicloruta',
    description: 'High-coverage cycle route integrated with green median systems',
    photoUrl: 'https://loremflickr.com/1200/900/bogota,bicycle,lane,street',
    transportModes: ['walking', 'bicycle'],
  },
  {
    id: 'utrecht_fietsstraat',
    categoryId: 'cycling_network',
    label: 'Utrecht Fietsstraat',
    description: 'Bicycle-priority shared street where cars are guests',
    photoUrl: 'https://loremflickr.com/1200/900/utrecht,bicycle,street,netherlands',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'seville_protected_cycle_track',
    categoryId: 'cycling_network',
    label: 'Seville Protected Cycle Track',
    description: 'Physically protected curbside cycleway with shaded sidewalks',
    photoUrl: 'https://loremflickr.com/1200/900/seville,cycle,track,street',
    transportModes: ['walking', 'bicycle'],
  },
  {
    id: 'curitiba_brt_axis',
    categoryId: 'transit_corridor',
    label: 'Curitiba BRT Axis',
    description: 'Median-running bus rapid transit with linear station sequence',
    photoUrl: 'https://loremflickr.com/1200/900/curitiba,brt,bus,corridor',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'bogota_transmilenio_avenue',
    categoryId: 'transit_corridor',
    label: 'Bogota TransMilenio Avenue',
    description: 'Dedicated bus lanes and platform stations on a high-volume avenue',
    photoUrl: 'https://loremflickr.com/1200/900/transmilenio,bogota,bus,rapid,transit',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'hong_kong_tram_street',
    categoryId: 'transit_corridor',
    label: 'Hong Kong Tram Street',
    description: 'Dense mixed corridor where tram movement shapes public street life',
    photoUrl: 'https://loremflickr.com/1200/900/hong,kong,tram,street',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'zurich_tram_boulevard',
    categoryId: 'transit_corridor',
    label: 'Zurich Tram Boulevard',
    description: 'Transit-forward boulevard with strong pedestrian crossings and calm traffic',
    photoUrl: 'https://loremflickr.com/1200/900/zurich,tram,boulevard,street',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'portland_complete_street',
    categoryId: 'complete_street',
    label: 'Portland Complete Street',
    description: 'Balanced street section with transit, cycling, autos, and large sidewalks',
    photoUrl: 'https://loremflickr.com/1200/900/portland,complete,street,urban',
    transportModes: ['walking', 'bicycle', 'transit', 'automobile'],
  },
  {
    id: 'barcelona_superblock',
    categoryId: 'complete_street',
    label: 'Barcelona Superblock Street',
    description: 'Low-speed local grid with reclaimed pedestrian and social space',
    photoUrl: 'https://loremflickr.com/1200/900/barcelona,superblock,street,public,space',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'london_exhibition_road',
    categoryId: 'complete_street',
    label: 'London Exhibition Road',
    description: 'Shared-surface civic street with coordinated multimodal movement',
    photoUrl: 'https://loremflickr.com/1200/900/london,exhibition,road,shared,street',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'paris_champs_elysees',
    categoryId: 'boulevard_avenue',
    label: 'Paris Champs-Elysees',
    description: 'Monumental boulevard section with formal tree canopy and median structure',
    photoUrl: 'https://loremflickr.com/1200/900/paris,champs,elysees,boulevard',
    transportModes: ['walking', 'transit', 'automobile'],
  },
  {
    id: 'mexico_city_reforma',
    categoryId: 'boulevard_avenue',
    label: 'Paseo de la Reforma',
    description: 'Large mixed-mobility avenue with events, monuments, and transit presence',
    photoUrl: 'https://loremflickr.com/1200/900/mexico,city,paseo,reforma,avenue',
    transportModes: ['walking', 'bicycle', 'transit', 'automobile'],
  },
  {
    id: 'tokyo_local_service_lane',
    categoryId: 'boulevard_avenue',
    label: 'Tokyo Local Service Lane',
    description: 'Fine-grain neighborhood service street with compact multimodal coexistence',
    photoUrl: 'https://loremflickr.com/1200/900/tokyo,local,street,lane',
    transportModes: ['walking', 'bicycle', 'automobile'],
  },
  {
    id: 'industrial_freight_collector',
    categoryId: 'service_freight',
    label: 'Industrial Freight Collector',
    description: 'Durable heavy-duty industrial corridor with turning radii for goods movement',
    photoUrl: 'https://loremflickr.com/1200/900/industrial,freight,road,warehouse',
    transportModes: ['automobile', 'transit'],
  },
  {
    id: 'other',
    categoryId: 'other',
    label: 'Other',
    description: 'Custom transportation aesthetic and right-of-way direction',
    photoUrl: 'https://loremflickr.com/1200/900/street,urban,transport,corridor',
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
    photoUrl: 'https://loremflickr.com/1200/900/central,park,new,york,landscape',
  },
  {
    id: 'versailles_formal_garden',
    categoryId: 'historic_landscape',
    label: 'French Formal Garden (Versailles)',
    description: 'Axis-driven formal gardens, parterres, and ceremonial tree alignments',
    photoUrl: 'https://loremflickr.com/1200/900/versailles,garden,formal,landscape',
  },
  {
    id: 'high_line_linear_park',
    categoryId: 'urban_linear',
    label: 'Linear Elevated Park (High Line)',
    description: 'Elevated promenade with layered planting, overlooks, and seating pockets',
    photoUrl: 'https://loremflickr.com/1200/900/high,line,new,york,park',
  },
  {
    id: 'philosophers_path_garden',
    categoryId: 'urban_linear',
    label: 'Canal Garden Walk',
    description: 'Canal-edge strolling park with seasonal tree canopy and intimate paving',
    photoUrl: 'https://loremflickr.com/1200/900/kyoto,canal,garden,path',
  },
  {
    id: 'superkilen_cultural_park',
    categoryId: 'civic_recreation',
    label: 'Cultural Activity Park (Superkilen)',
    description: 'Program-rich social landscape with bold surfaces and active edges',
    photoUrl: 'https://loremflickr.com/1200/900/superkilen,copenhagen,park',
  },
  {
    id: 'civic_lawn_commons',
    categoryId: 'civic_recreation',
    label: 'Civic Lawn Commons',
    description: 'Flexible event lawn framed by shade trees, play, and social seating',
    photoUrl: 'https://loremflickr.com/1200/900/urban,lawn,park,city',
  },
  {
    id: 'houtan_ecological_park',
    categoryId: 'ecological_restoration',
    label: 'Ecological Wetland Park (Houtan)',
    description: 'Productive wetland terraces and boardwalks for stormwater polishing',
    photoUrl: 'https://loremflickr.com/1200/900/wetland,boardwalk,urban,park',
  },
  {
    id: 'bishan_river_park',
    categoryId: 'ecological_restoration',
    label: 'River Restoration Park (Bishan)',
    description: 'Naturalized river corridor with floodable lawns and habitat mosaics',
    photoUrl: 'https://loremflickr.com/1200/900/river,restoration,park,landscape',
  },
  {
    id: 'wetland_boardwalk_park',
    categoryId: 'ecological_restoration',
    label: 'Wetland Boardwalk Park',
    description: 'Sponge-park edge conditions with elevated pathways and riparian planting',
    photoUrl: 'https://loremflickr.com/1200/900/wetland,park,boardwalk,water',
  },
  {
    id: 'botanical_garden',
    categoryId: 'botanic_horticultural',
    label: 'Botanical Garden',
    description: 'Curated planting collections with educational routes and seasonal color',
    photoUrl: 'https://loremflickr.com/1200/900/botanical,garden,landscape,park',
  },
  {
    id: 'other',
    categoryId: 'other',
    label: 'Other',
    description: 'Custom park concept guided by your prompt and reference imagery',
    photoUrl: 'https://loremflickr.com/1200/900/landscape,architecture,park',
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
    photoUrl: 'https://loremflickr.com/1200/900/civic,square,fountain,plaza',
  },
  {
    id: 'piazza_del_campo',
    categoryId: 'civic_formal',
    label: 'Piazza del Campo',
    description: 'Shell-shaped civic plaza with radial paving and active perimeter edges',
    photoUrl: 'https://loremflickr.com/1200/900/piazza,del,campo,siena',
  },
  {
    id: 'trafalgar_square',
    categoryId: 'civic_formal',
    label: 'Trafalgar Square',
    description: 'Monumental public square with stairs, fountains, and civic intensity',
    photoUrl: 'https://loremflickr.com/1200/900/trafalgar,square,london',
  },
  {
    id: 'market_plaza',
    categoryId: 'market_social',
    label: 'Market Plaza',
    description: 'Flexible market hardscape for kiosks, pop-ups, and daily retail activity',
    photoUrl: 'https://loremflickr.com/1200/900/market,plaza,urban,public,space',
  },
  {
    id: 'times_square_pedestrian',
    categoryId: 'market_social',
    label: 'Times Square Pedestrian Plaza',
    description: 'High-intensity pedestrianized plaza with media facades and seating bands',
    photoUrl: 'https://loremflickr.com/1200/900/times,square,pedestrian,plaza',
  },
  {
    id: 'festival_plaza',
    categoryId: 'event_cultural',
    label: 'Festival Plaza',
    description: 'Large event forecourt designed for cultural programming and gatherings',
    photoUrl: 'https://loremflickr.com/1200/900/festival,plaza,public,square',
  },
  {
    id: 'federation_square',
    categoryId: 'event_cultural',
    label: 'Federation Square',
    description: 'Angular cultural plaza with event staging and layered social terraces',
    photoUrl: 'https://loremflickr.com/1200/900/federation,square,melbourne',
  },
  {
    id: 'garden_plaza',
    categoryId: 'green_cooling',
    label: 'Garden Plaza',
    description: 'Shaded plaza with integrated planting, seating bands, and cooling comfort',
    photoUrl: 'https://loremflickr.com/1200/900/garden,plaza,trees,urban',
  },
  {
    id: 'waterfront_boardwalk_plaza',
    categoryId: 'waterfront',
    label: 'Waterfront Boardwalk Plaza',
    description: 'Promenade plaza with boardwalk terraces and edge activation',
    photoUrl: 'https://loremflickr.com/1200/900/waterfront,boardwalk,plaza',
  },
  {
    id: 'harbour_edge_plaza',
    categoryId: 'waterfront',
    label: 'Harbour Edge Plaza',
    description: 'Public waterfront forecourt blending seating steps and shoreline access',
    photoUrl: 'https://loremflickr.com/1200/900/harbour,waterfront,public,plaza',
  },
  {
    id: 'other',
    categoryId: 'other',
    label: 'Other',
    description: 'Custom plaza identity guided by your prompt and reference imagery',
    photoUrl: 'https://loremflickr.com/1200/900/urban,plaza,public,space',
  },
];
assignPhotoExamples(ROADWAY_AESTHETIC_OPTIONS_V2, UNSPLASH_TRANSPORT_POOL);
assignPhotoExamples(GREEN_SPACE_AESTHETIC_OPTIONS_V2, UNSPLASH_GREEN_SPACE_POOL);
assignPhotoExamples(PLAZA_AESTHETIC_OPTIONS_V2, UNSPLASH_PLAZA_POOL);
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

export function mapDevelopmentTypeToCategory(_value?: string): string | undefined {
  // Legacy helper kept for compatibility. Building aesthetics are style-based and
  // should never be auto-derived from use/program development types.
  return undefined;
}

