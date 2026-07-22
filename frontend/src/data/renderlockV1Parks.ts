export type ParkReferenceAngle = 'street' | 'angle_60' | 'angle_90';

export interface RenderlockV1Park {
  sequence: number;
  archetypeId: string;
  variantId: string;
  variantLabel: string;
  profileId: string;
  profileVersion: number;
  widthM: number;
  depthM: number;
  referenceViews: Readonly<Record<ParkReferenceAngle, string>>;
  programTruth: string;
  reviewState: 'keeper';
}

function referenceViews(slug: string, variant: number): RenderlockV1Park['referenceViews'] {
  const base = `/archetypes/openspaces/${slug}/variant_${variant}`;
  return Object.freeze({
    street: `${base}.png`,
    angle_60: `${base}_angle_60.jpg`,
    angle_90: `${base}_angle_90.jpg`,
  });
}

/**
 * Finite July 2026 park render-lock cohort.
 *
 * The three catalog views lock planting/material character. The exact park
 * profile remains authoritative for boundary, metric dimensions, topology,
 * safety envelopes and fixed-program count when an image invents an
 * incompatible prop (for example the dock in the stormwater reference).
 */
export const RENDERLOCK_V1_PARKS: readonly RenderlockV1Park[] = Object.freeze([
  {
    sequence: 1,
    archetypeId: 'neighborhood_park',
    variantId: 'neighborhood_park_v0',
    variantLabel: 'Rustic Timber & Gravel',
    profileId: 'neighborhood-park-v4',
    profileVersion: 4,
    widthM: 100,
    depthM: 80,
    referenceViews: referenceViews('neighborhood-park', 0),
    programTruth: 'Connected walking circuit, four gateways, clear social lawn, meadow/rain-garden rooms, playground and pavilion pads.',
    reviewState: 'keeper',
  },
  {
    sequence: 2,
    archetypeId: 'urban_pocket_park',
    variantId: 'urban_pocket_park_v0',
    variantLabel: 'Rustic Timber & Gravel',
    profileId: 'urban-pocket-park-v1',
    profileVersion: 1,
    widthM: 30,
    depthM: 30,
    referenceViews: referenceViews('urban-pocket-park', 0),
    programTruth: 'One clear lawn room with a direct gateway-connected path and layered perimeter planting.',
    reviewState: 'keeper',
  },
  {
    sequence: 3,
    archetypeId: 'linear_park_greenway',
    variantId: 'linear_park_greenway_v0',
    variantLabel: 'Rail Trail',
    profileId: 'linear-park-greenway-v1',
    profileVersion: 1,
    widthM: 400,
    depthM: 30,
    referenceViews: referenceViews('linear-park-greenway', 0),
    programTruth: 'One continuous 3.5 metre end-to-end multi-use trail with connected gateways and native corridor planting.',
    reviewState: 'keeper',
  },
  {
    sequence: 4,
    archetypeId: 'stormwater_retention_pond',
    variantId: 'stormwater_retention_pond_v0',
    variantLabel: 'Naturalistic Pond & Water Garden',
    profileId: 'stormwater-retention-pond-v1',
    profileVersion: 1,
    widthM: 90,
    depthM: 60,
    referenceViews: referenceViews('stormwater-retention-pond', 0),
    programTruth: 'One functional basin with wet shelf, inlet, outlet/weir and dry maintenance access; omit the reference dock.',
    reviewState: 'keeper',
  },
  {
    sequence: 5,
    archetypeId: 'japanese_garden',
    variantId: 'japanese_garden_v1',
    variantLabel: 'Woodland Naturalistic',
    profileId: 'japanese-garden-v4',
    profileVersion: 4,
    widthM: 70,
    depthM: 70,
    referenceViews: referenceViews('japanese-garden', 1),
    programTruth: 'Complete stroll loop, koi pond, raked-gravel court, stepping stones and one exact bridge alignment.',
    reviewState: 'keeper',
  },
  {
    sequence: 6,
    archetypeId: 'sports_field_complex',
    variantId: 'sports_field_complex_v0',
    variantLabel: 'Professional Grade',
    profileId: 'sports-field-complex-v4',
    profileVersion: 4,
    widthM: 144,
    depthM: 76.8,
    referenceViews: referenceViews('sports-field-complex', 0),
    programTruth: 'One complete 100 x 64 metre pitch plus the maximum compatible count of complete regulation tennis envelopes.',
    reviewState: 'keeper',
  },
  {
    sequence: 7,
    archetypeId: 'urban_forest',
    variantId: 'urban_forest_v2',
    variantLabel: 'Rewilded Urban',
    profileId: 'urban-forest-v2',
    profileVersion: 2,
    widthM: 144,
    depthM: 90,
    referenceViews: referenceViews('urban-forest', 2),
    programTruth: 'Near-closed native canopy, one continuous low-impact trail and exactly two daylight clearings.',
    reviewState: 'keeper',
  },
  {
    sequence: 8,
    archetypeId: 'botanical_garden',
    variantId: 'botanical_garden_v1',
    variantLabel: 'Woodland Naturalistic',
    profileId: 'botanical-garden-v5',
    profileVersion: 5,
    widthM: 144,
    depthM: 76.8,
    referenceViews: referenceViews('botanical-garden', 1),
    programTruth: 'Connected interpretive loop, compact conservatory pad and three separate collection-bed rooms.',
    reviewState: 'keeper',
  },
  {
    sequence: 9,
    archetypeId: 'nature_play_area',
    variantId: 'nature_play_area_v0',
    variantLabel: 'Forest Adventure',
    profileId: 'nature-play-area-v3',
    profileVersion: 3,
    widthM: 60,
    depthM: 45,
    referenceViews: referenceViews('nature-play-area', 0),
    programTruth: 'Two complete linked safety clearings, accessible loop and one contained shallow water-play rill pad.',
    reviewState: 'keeper',
  },
  {
    sequence: 10,
    archetypeId: 'reservoir_watershed_park',
    variantId: 'reservoir_watershed_park_v0',
    variantLabel: 'Concrete-Edge Utility Reservoir',
    profileId: 'reservoir-watershed-park-v3',
    profileVersion: 3,
    widthM: 140,
    depthM: 100,
    referenceViews: referenceViews('reservoir-watershed-park', 0),
    programTruth: 'Exact rectangular impoundment, continuous perimeter trail and clear short-edge dam/spillway.',
    reviewState: 'keeper',
  },
]);
