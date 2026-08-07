export interface Batch17ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

export type ParkSkinRole = 'paver' | 'lawn' | 'asphalt' | 'planting' | 'safety' | 'timber';

export function parkGlbMaterialRole(materialName: string): ParkSkinRole | null {
  const name = materialName.toLowerCase();
  if (name.includes('planting')) return 'planting';
  if (name.includes('lawn')) return 'lawn';
  if (name.includes('asphalt')) return 'asphalt';
  if (name.includes('timber')) return 'timber';
  if (name.includes('rubber')) return 'safety';
  if (
    name.includes('aggregate')
    || name.includes('court surround')
    || name.includes('play sand')
    || name.includes('paver')
  ) return 'paver';
  return null;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch17ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

export const BATCH17_PARK_SKINS = Object.freeze([
  skin('pickleball_courts', 'pickleball_courts_v0', 'pickleball-courts-competition-grade-v0'),
  skin('pickleball_courts', 'pickleball_courts_v2', 'pickleball-courts-park-integrated-v2'),
  skin('pickleball_courts', 'pickleball_courts_v3', 'pickleball-courts-indoor-outdoor-hybrid-v3'),
  skin('soccer_pitch_caged', 'soccer_pitch_caged_v1', 'soccer-pitch-caged-community-recreation-v1'),
  skin('soccer_pitch_caged', 'soccer_pitch_caged_v2', 'soccer-pitch-caged-youth-training-complex-v2'),
  skin('soccer_pitch_caged', 'soccer_pitch_caged_v3', 'soccer-pitch-caged-rooftop-urban-v3'),
  skin('running_track_oval', 'running_track_oval_v0', 'running-track-oval-competition-standard-v0'),
  skin('running_track_oval', 'running_track_oval_v1', 'running-track-oval-community-fitness-v1'),
  skin('running_track_oval', 'running_track_oval_v3', 'running-track-oval-park-loop-trail-v3'),
  skin('outdoor_fitness_circuit', 'outdoor_fitness_circuit_v1', 'outdoor-fitness-parkour-movement-v1'),
  skin('outdoor_fitness_circuit', 'outdoor_fitness_circuit_v2', 'outdoor-fitness-nature-trail-v2'),
  skin('outdoor_fitness_circuit', 'outdoor_fitness_circuit_v3', 'outdoor-fitness-senior-wellness-v3'),
  skin('baseball_softball_diamond', 'baseball_softball_diamond_v0', 'baseball-softball-classic-park-v0'),
  skin('baseball_softball_diamond', 'baseball_softball_diamond_v2', 'baseball-softball-softball-field-v2'),
  skin('baseball_softball_diamond', 'baseball_softball_diamond_v3', 'baseball-softball-vintage-sandlot-v3'),
  skin('cricket_pitch_oval', 'cricket_pitch_oval_v1', 'cricket-pitch-municipal-oval-v1'),
  skin('cricket_pitch_oval', 'cricket_pitch_oval_v2', 'cricket-pitch-south-asian-ground-v2'),
  skin('cricket_pitch_oval', 'cricket_pitch_oval_v3', 'cricket-pitch-caribbean-beach-v3'),
  skin('nature_play_area', 'nature_play_area_v1', 'nature-play-sensory-garden-v1'),
  skin('nature_play_area', 'nature_play_area_v2', 'nature-play-mud-water-v2'),
  skin('nature_play_area', 'nature_play_area_v3', 'nature-play-toddler-garden-v3'),
  skin('inclusive_playground', 'inclusive_playground_v1', 'inclusive-playground-sensory-explorer-v1'),
  skin('inclusive_playground', 'inclusive_playground_v2', 'inclusive-playground-mega-all-abilities-v2'),
  skin('inclusive_playground', 'inclusive_playground_v3', 'inclusive-playground-nature-inclusive-v3'),
  skin('pump_track', 'pump_track_v1', 'pump-track-dirt-bmx-v1'),
  skin('pump_track', 'pump_track_v2', 'pump-track-family-all-wheels-v2'),
  skin('pump_track', 'pump_track_v3', 'pump-track-modular-pop-up-v3'),
  skin('splash_pad_area', 'splash_pad_area_v1', 'splash-pad-modern-steel-turf-v1'),
  skin('splash_pad_area', 'splash_pad_area_v2', 'splash-pad-natural-meadow-v2'),
  skin('splash_pad_area', 'splash_pad_area_v3', 'splash-pad-urban-contemporary-v3'),
]);

export const batch17ParkSkinForSelection = (archetypeId: string, variantId: string): Batch17ParkSkinDefinition | null => (
  BATCH17_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
