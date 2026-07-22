export interface RenderlockV1Street {
  sequence: number;
  archetypeId: string;
  variantId: string;
  variantLabel: string;
  rowM: number;
  testLengthM: number;
  referenceViews: readonly string[];
  crossSectionTruth: string;
  reviewState: 'keeper';
}

function threeViews(slug: string, variant: number): readonly string[] {
  const base = `/archetypes/streets/${slug}/variant_${variant}`;
  return Object.freeze([`${base}.png`, `${base}_angle_60.jpg`, `${base}_angle_90.jpg`]);
}

/**
 * Finite July 2026 street/path render-lock cohort.
 *
 * Catalog images lock material, furnishing and planting character. Metric
 * cross-sections remain authoritative for right-of-way width, band order,
 * markings, curbs and circulation clearances.
 */
export const RENDERLOCK_V1_STREETS: readonly RenderlockV1Street[] = Object.freeze([
  {
    sequence: 1,
    archetypeId: 'yield_street',
    variantId: 'yield_street_v0',
    variantLabel: 'Dutch Woonerf',
    rowM: 6,
    testLengthM: 240,
    referenceViews: threeViews('yield-street', 0),
    crossSectionTruth: '0.3 m flush edge + 5.4 m brick shared surface + 0.3 m flush edge; no raised curbs.',
    reviewState: 'keeper',
  },
  {
    sequence: 2,
    archetypeId: 'narrow_residential_street',
    variantId: 'narrow_residential_street_v0',
    variantLabel: 'Classic Tree-Lined',
    rowM: 10,
    testLengthM: 240,
    referenceViews: threeViews('narrow-residential-street', 0),
    crossSectionTruth: 'Two 1.2 m sidewalks, two 0.6 m planting strips, two 1.4 m parking bands and one 3.6 m unmarked yield carriageway.',
    reviewState: 'keeper',
  },
  {
    sequence: 3,
    archetypeId: 'collector_road',
    variantId: 'collector_road_v0',
    variantLabel: 'Classic Tree-Lined',
    rowM: 16,
    testLengthM: 240,
    referenceViews: threeViews('collector-road', 0),
    crossSectionTruth: 'Two 1.5 m sidewalks, two 1.25 m tree boulevards, two 3.25 m travel lanes and one 4.0 m centre turn lane.',
    reviewState: 'keeper',
  },
  {
    sequence: 4,
    archetypeId: 'main_street_complete',
    variantId: 'main_street_complete_v0',
    variantLabel: 'Classic Tree-Lined',
    rowM: 18,
    testLengthM: 240,
    referenceViews: threeViews('main-street-complete', 0),
    crossSectionTruth: 'Two 2.0 m sidewalks, two 1.25 m furnishing zones, two 2.1 m parking bands and two 3.65 m travel/sharrow lanes.',
    reviewState: 'keeper',
  },
  {
    sequence: 5,
    archetypeId: 'calgary_local',
    variantId: 'calgary_local_v0',
    variantLabel: 'As Per Street Manual',
    rowM: 16,
    testLengthM: 240,
    referenceViews: Object.freeze([
      '/archetypes/streets/calgary-local/variant_0.png',
      '/archetypes/streets/calgary-local/section_stylized.png',
      '/archetypes/streets/calgary-local/section_stylized_angle_90.jpg',
    ]),
    crossSectionTruth: 'Street Manual 16.0 m section with paired 3.25 m lanes, 2.65 m boulevards, 1.8 m sidewalks and 0.3 m setbacks.',
    reviewState: 'keeper',
  },
  {
    sequence: 6,
    archetypeId: 'protected_bike_lane_bidirectional',
    variantId: 'protected_bike_lane_bidirectional_v0',
    variantLabel: 'Two-Way Cycle Track',
    rowM: 20,
    testLengthM: 240,
    referenceViews: Object.freeze(['/archetypes/streets/protected-bike-lane-bi-directional/variant_0.png']),
    crossSectionTruth: 'One 3.6 m two-way cycle track behind a 0.5 m buffer, two 3.25 m travel lanes, one 2.2 m parking band, sidewalks and boulevards.',
    reviewState: 'keeper',
  },
  {
    sequence: 7,
    archetypeId: 'calgary_arterial_4lane_50',
    variantId: 'calgary_arterial_4lane_50_v0',
    variantLabel: 'As Per Street Manual',
    rowM: 33,
    testLengthM: 240,
    referenceViews: Object.freeze([
      '/archetypes/streets/calgary-arterial-4lane-50/variant_0.png',
      '/archetypes/streets/calgary-arterial-4lane-50/section_stylized.png',
      '/archetypes/streets/calgary-arterial-4lane-50/section_stylized_angle_90.jpg',
    ]),
    crossSectionTruth: 'Street Manual 33.0 m section with four travel lanes, 6.0 m planted median, paired 3.7 m boulevards and paired 3.0 m multi-use paths.',
    reviewState: 'keeper',
  },
  {
    sequence: 8,
    archetypeId: 'multi_use_trail',
    variantId: 'multi_use_trail_v1',
    variantLabel: 'Green Corridor',
    rowM: 4,
    testLengthM: 240,
    referenceViews: threeViews('multi-use-trail', 1),
    crossSectionTruth: 'One 3.5 m paved shared path with two 0.25 m soft shoulders, dashed centre marking and no road curbs.',
    reviewState: 'keeper',
  },
  {
    sequence: 9,
    archetypeId: 'toronto_victorian_residential_street',
    variantId: 'toronto_victorian_residential_street_v0',
    variantLabel: 'Summer Canopy',
    rowM: 16,
    testLengthM: 240,
    referenceViews: threeViews('toronto-victorian-residential-street', 0),
    crossSectionTruth: 'Two 1.5 m sidewalks, two 1.0 m maple boulevards, two 1.75 m parking bands and two unmarked 3.75 m residential lanes.',
    reviewState: 'keeper',
  },
  {
    sequence: 10,
    archetypeId: 'toronto_laneway',
    variantId: 'toronto_laneway_v0',
    variantLabel: 'Traditional Service Lane',
    rowM: 5,
    testLengthM: 240,
    referenceViews: threeViews('toronto-laneway', 0),
    crossSectionTruth: 'One 4.5 m shared service lane with paired 0.25 m flush drainage edges and no raised curbs.',
    reviewState: 'keeper',
  },
]);
