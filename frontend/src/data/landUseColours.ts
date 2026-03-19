// ─── APA STANDARD LAND USE COLOURS ───────────────────────────────────────────
// Source: American Planning Association, 1997
// "Traditional Color Coding for Land Uses"

export const LAND_USE_COLOURS = {

  // RESIDENTIAL
  'residential-single-family': {
    fill: '#FFFF99',      // Lemon Yellow — APA standard
    outline: '#E6E600',
    label: 'Single Family Residential',
    opacity: 0.85,
  },
  'residential-duplex': {
    fill: '#FFE066',      // Yellow Ochre
    outline: '#E6C800',
    label: 'Duplex Residential',
    opacity: 0.85,
  },
  'residential-multifamily': {
    fill: '#C8A000',      // Dark Brown/Yellow
    outline: '#A08000',
    label: 'Multi-Family Residential',
    opacity: 0.85,
  },
  'residential-highrise': {
    fill: '#8B6914',      // Dark Brown
    outline: '#6B4F10',
    label: 'High-Rise Residential',
    opacity: 0.85,
  },

  // COMMERCIAL
  'commercial-light': {
    fill: '#FFB366',      // Light Red/Orange
    outline: '#E69040',
    label: 'Light Commercial',
    opacity: 0.85,
  },
  'commercial-retail': {
    fill: '#FF4444',      // Scarlet Red
    outline: '#CC0000',
    label: 'Retail Commercial',
    opacity: 0.85,
  },
  'commercial-office': {
    fill: '#CC2200',      // Vermilion Red
    outline: '#AA1100',
    label: 'Office Commercial',
    opacity: 0.85,
  },
  'commercial-general': {
    fill: '#E8402A',      // Scarlet Lake
    outline: '#C03020',
    label: 'General Commercial',
    opacity: 0.85,
  },

  // MIXED USE
  'mixed-use': {
    fill: '#9B59B6',      // Purple
    outline: '#7D3C98',
    label: 'Mixed Use',
    opacity: 0.85,
  },
  'mixed-use-commercial-residential': {
    fill: '#8E44AD',      // Dark Purple
    outline: '#6C3483',
    label: 'Commercial/Residential Mixed',
    opacity: 0.85,
  },

  // INDUSTRIAL
  'industrial-light': {
    fill: '#B8B8B8',      // Light Gray
    outline: '#909090',
    label: 'Light Industrial',
    opacity: 0.85,
  },
  'industrial-general': {
    fill: '#888888',      // Medium Gray
    outline: '#606060',
    label: 'General Industrial',
    opacity: 0.85,
  },
  'industrial-heavy': {
    fill: '#444444',      // Dark Gray
    outline: '#222222',
    label: 'Heavy Industrial',
    opacity: 0.85,
  },
  'industrial-warehouse': {
    fill: '#A0A0A0',      // Slate Gray
    outline: '#808080',
    label: 'Warehouse/Wholesale',
    opacity: 0.85,
  },

  // INSTITUTIONAL / PUBLIC
  'institutional': {
    fill: '#4444CC',      // Blue
    outline: '#2222AA',
    label: 'Institutional',
    opacity: 0.85,
  },
  'institutional-education': {
    fill: '#3366FF',      // Medium Blue
    outline: '#1144CC',
    label: 'Education',
    opacity: 0.85,
  },
  'institutional-health': {
    fill: '#0099CC',      // Aquamarine
    outline: '#007799',
    label: 'Health Care',
    opacity: 0.85,
  },
  'institutional-civic': {
    fill: '#3B82F6',      // Civic Blue
    outline: '#1D4ED8',
    label: 'Civic/Government',
    opacity: 0.85,
  },

  // OPEN SPACE / RECREATION
  'open-space': {
    fill: '#66CC66',      // Light Green
    outline: '#449944',
    label: 'Open Space',
    opacity: 0.85,
  },
  'recreational': {
    fill: '#44AA44',      // Medium Green
    outline: '#228822',
    label: 'Recreational',
    opacity: 0.85,
  },
  'park-plaza': {
    fill: '#4ECDC4',      // Teal Green
    outline: '#2EA89F',
    label: 'Park / Plaza',
    opacity: 0.85,
  },
  'agricultural': {
    fill: '#228B22',      // Forest Green
    outline: '#156015',
    label: 'Agricultural',
    opacity: 0.85,
  },

  // TRANSPORTATION / UTILITIES
  'transportation': {
    fill: '#666666',      // Gray
    outline: '#444444',
    label: 'Transportation',
    opacity: 0.75,
  },
  'utilities': {
    fill: '#999999',      // Light Gray
    outline: '#777777',
    label: 'Utilities',
    opacity: 0.75,
  },
  'streets-paths': {
    fill: '#D4A853',      // Warm Tan
    outline: '#B08030',
    label: 'Streets & Paths',
    opacity: 0.75,
  },

  // SPECIAL
  'site-boundary': {
    fill: 'transparent',
    outline: '#FF6B35',   // Orange outline only
    label: 'Site Boundary',
    opacity: 1.0,
  },
  'water': {
    fill: '#4488CC',      // Water Blue
    outline: '#2266AA',
    label: 'Water',
    opacity: 0.8,
  },
  'environmental': {
    fill: '#2E8B57',      // Sea Green
    outline: '#1A6640',
    label: 'Environmental',
    opacity: 0.8,
  },

  // FALLBACK
  'default': {
    fill: '#CCCCCC',
    outline: '#999999',
    label: 'Unclassified',
    opacity: 0.75,
  },
} as const;

// Map from SiteForge developmentType values to colour keys
export const DEVELOPMENT_TYPE_MAP: Record<string, keyof typeof LAND_USE_COLOURS> = {
  // Title-case variants (legacy / display labels)
  'Residential':                'residential-single-family',
  'Residential - Single Family':'residential-single-family',
  'Residential - Duplex':       'residential-duplex',
  'Residential - Multi-Family': 'residential-multifamily',
  'Residential - High Rise':    'residential-highrise',
  'Commercial':                 'commercial-general',
  'Commercial - Light':         'commercial-light',
  'Commercial - Retail':        'commercial-retail',
  'Commercial - Office':        'commercial-office',
  'Mixed Use':                  'mixed-use',
  'Industrial':                 'industrial-general',
  'Industrial - Light':         'industrial-light',
  'Industrial - Heavy':         'industrial-heavy',
  'Industrial - Warehouse':     'industrial-warehouse',
  'Institutional':              'institutional',
  'Institutional - Education':  'institutional-education',
  'Institutional - Health':     'institutional-health',
  'Park / Plaza':               'park-plaza',
  'Recreational':               'recreational',
  'Open Space':                 'open-space',
  'Transportation':             'transportation',
  'Utilities':                  'utilities',
  'Streets and Paths':          'streets-paths',
  'Site Boundary':              'site-boundary',
  'Other':                      'default',

  // Lowercase/underscore variants (used by zone property dropdowns)
  'residential':                'residential-single-family',
  'residential_single_family':  'residential-single-family',
  'residential_duplex':         'residential-duplex',
  'residential_multifamily':    'residential-multifamily',
  'residential_highrise':       'residential-highrise',
  'commercial':                 'commercial-general',
  'commercial_light':           'commercial-light',
  'commercial_retail':          'commercial-retail',
  'commercial_office':          'commercial-office',
  'mixed_use':                  'mixed-use',
  'industrial':                 'industrial-general',
  'industrial_light':           'industrial-light',
  'industrial_heavy':           'industrial-heavy',
  'industrial_warehouse':       'industrial-warehouse',
  'institutional':              'institutional',
  'institutional_education':    'institutional-education',
  'institutional_health':       'institutional-health',
  'park_plaza':                 'park-plaza',
  'recreational':               'recreational',
  'open_space':                 'open-space',
  'transportation':             'transportation',
  'utilities':                  'utilities',
  'streets_paths':              'streets-paths',
  'site_boundary':              'site-boundary',
  'water':                      'water',
  'other':                      'default',
};

export function getColourForDevelopmentType(developmentType: string) {
  const key = DEVELOPMENT_TYPE_MAP[developmentType] ?? 'default';
  return LAND_USE_COLOURS[key];
}
