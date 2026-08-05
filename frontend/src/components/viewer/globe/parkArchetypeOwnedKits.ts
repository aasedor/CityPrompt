export interface ArchetypeOwnedParkKitDefinition {
  familyId: string;
  archetypeId: string;
  variantId: string;
  title: string;
  appearanceKitId: string;
  plantingStructure: string;
  slug: string;
  widthM: number;
  depthM: number;
  clearanceM: number;
  surfaceKind: 'skate' | 'inclusive_playground' | 'dog_park' | 'splash_pad' | 'community_garden'
    | 'tennis_cluster' | 'nature_play' | 'pump_track' | 'outdoor_fitness' | 'memorial_garden';
  assets: Readonly<Record<string, string>>;
  people: false;
  largeBuildings: false;
}

const kit = (
  definition: Omit<ArchetypeOwnedParkKitDefinition, 'people' | 'largeBuildings'>,
): ArchetypeOwnedParkKitDefinition => Object.freeze({
  ...definition,
  assets: Object.freeze(definition.assets),
  people: false,
  largeBuildings: false,
});

/** Every entry is one render-reviewed archetype/variant identity. These are
 * not interchangeable themes: each family owns its exact skin, modules,
 * placement program and metric receiving envelope. */
export const ARCHETYPE_OWNED_PARK_KITS = Object.freeze({
  park_skate_archetype_v0: kit({
    familyId: 'park_skate_archetype_v0',
    archetypeId: 'skate_park',
    variantId: 'skate_park_v0',
    title: 'Skate Park / Professional Grade',
    appearanceKitId: 'skate_park_v0_reference_skin',
    plantingStructure: 'skate_archetype_v0',
    slug: 'skate-park',
    widthM: 40,
    depthM: 30,
    clearanceM: 0.5,
    surfaceKind: 'skate',
    assets: {
      bowl: 'skate-bowl-module.glb',
      hubba: 'stair-hubba-module.glb',
      rail: 'skate-rail.glb',
      ledge: 'skate-ledge.glb',
    },
  }),
  park_inclusive_playground_v0: kit({
    familyId: 'park_inclusive_playground_v0',
    archetypeId: 'inclusive_playground',
    variantId: 'inclusive_playground_v0',
    title: 'Inclusive Playground / Universal Access',
    appearanceKitId: 'inclusive_playground_v0_reference_skin',
    plantingStructure: 'inclusive_playground_v0',
    slug: 'inclusive-accessible-playground',
    widthM: 50,
    depthM: 40,
    clearanceM: 0.5,
    surfaceKind: 'inclusive_playground',
    assets: {
      playStructure: 'accessible-play-structure.glb',
      swingBay: 'accessible-swing-bay.glb',
      spinner: 'inclusive-spinner.glb',
      sensoryPanel: 'sensory-panel.glb',
      shadeCanopy: 'shade-canopy.glb',
    },
  }),
  park_dog_archetype_v0: kit({
    familyId: 'park_dog_archetype_v0',
    archetypeId: 'dog_park',
    variantId: 'dog_park_v0',
    title: 'Dog Park / Natural Exercise Enclosures',
    appearanceKitId: 'dog_park_v0_reference_skin',
    plantingStructure: 'dog_park_v0',
    slug: 'dog-park',
    widthM: 80,
    depthM: 50,
    clearanceM: 0.5,
    surfaceKind: 'dog_park',
    assets: {
      boulders: 'boulder-cluster.glb',
      gate: 'dog-park-gate.glb',
      shade: 'shade-shelter.glb',
      fence: 'timber-rail-fence.glb',
    },
  }),
  park_splash_pad_v0: kit({
    familyId: 'park_splash_pad_v0',
    archetypeId: 'splash_pad_area',
    variantId: 'splash_pad_area_v0',
    title: 'Splash Pad / Timber Water Play',
    appearanceKitId: 'splash_pad_area_v0_reference_skin',
    plantingStructure: 'splash_pad_area_v0',
    slug: 'splash-pad-water-play',
    widthM: 30,
    depthM: 25,
    clearanceM: 0.5,
    surfaceKind: 'splash_pad',
    assets: {
      groundJet: 'ground-jet.glb',
      fence: 'split-rail-fence.glb',
      sprayArch: 'spray-arch.glb',
      waterTower: 'timber-water-tower.glb',
    },
  }),
  park_community_garden_v0: kit({
    familyId: 'park_community_garden_v0',
    archetypeId: 'community_garden',
    variantId: 'community_garden_v0',
    title: 'Community Garden / Allotments',
    appearanceKitId: 'community_garden_v0_reference_skin',
    plantingStructure: 'community_garden_v0',
    slug: 'community-garden-allotments',
    widthM: 50,
    depthM: 50,
    clearanceM: 0.5,
    surfaceKind: 'community_garden',
    assets: {
      compost: 'compost-bins.glb',
      greenhouse: 'garden-greenhouse.glb',
      trellis: 'garden-trellis.glb',
      raisedBed: 'raised-growing-bed.glb',
      fence: 'split-rail-fence.glb',
    },
  }),
  park_tennis_cluster_v0: kit({
    familyId: 'park_tennis_cluster_v0',
    archetypeId: 'tennis_court_cluster',
    variantId: 'tennis_court_cluster_v0',
    title: 'Tennis Court Cluster / Professional Grade',
    appearanceKitId: 'tennis_court_cluster_v0_reference_skin',
    plantingStructure: 'tennis_court_cluster_v0',
    slug: 'tennis-court-professional',
    widthM: 82,
    depthM: 46,
    clearanceM: 0.5,
    surfaceKind: 'tennis_cluster',
    assets: {
      net: 'tennis-net.glb',
      fence: 'tennis-fence-6m.glb',
      floodlight: 'tennis-floodlight.glb',
      bleacher: 'spectator-bleacher.glb',
    },
  }),
  park_nature_play_v0: kit({
    familyId: 'park_nature_play_v0',
    archetypeId: 'nature_play_area',
    variantId: 'nature_play_area_v0',
    title: 'Nature Play Area / Forest Adventure',
    appearanceKitId: 'nature_play_area_v0_reference_skin',
    plantingStructure: 'nature_play_area_v0',
    slug: 'nature-play-forest-adventure',
    widthM: 40,
    depthM: 30,
    clearanceM: 0.5,
    surfaceKind: 'nature_play',
    assets: {
      rill: 'water-rill.glb',
      balanceLog: 'balance-log.glb',
      logFort: 'log-fort.glb',
      willowTunnel: 'willow-tunnel.glb',
      steppingStump: 'stepping-stump.glb',
      boulders: 'play-boulders.glb',
    },
  }),
  park_pump_track_v0: kit({
    familyId: 'park_pump_track_v0',
    archetypeId: 'pump_track',
    variantId: 'pump_track_v0',
    title: 'Pump Track / Asphalt Competition',
    appearanceKitId: 'pump_track_v0_reference_skin',
    plantingStructure: 'pump_track_v0',
    slug: 'pump-track-asphalt-competition',
    widthM: 50,
    depthM: 30,
    clearanceM: 0.5,
    surfaceKind: 'pump_track',
    assets: {
      loop: 'pump-track-loop.glb',
      startMound: 'start-mound.glb',
    },
  }),
  park_outdoor_fitness_v0: kit({
    familyId: 'park_outdoor_fitness_v0',
    archetypeId: 'outdoor_fitness_circuit',
    variantId: 'outdoor_fitness_circuit_v0',
    title: 'Outdoor Fitness Circuit / Urban Calisthenics',
    appearanceKitId: 'outdoor_fitness_circuit_v0_reference_skin',
    plantingStructure: 'outdoor_fitness_circuit_v0',
    slug: 'outdoor-fitness-calisthenics',
    widthM: 30,
    depthM: 25,
    clearanceM: 0.5,
    surfaceKind: 'outdoor_fitness',
    assets: {
      rig: 'calisthenics-rig.glb',
      parallelBars: 'parallel-bars.glb',
      situpBench: 'situp-bench.glb',
      rings: 'rings-frame.glb',
    },
  }),
  park_memorial_garden_v0: kit({
    familyId: 'park_memorial_garden_v0',
    archetypeId: 'memorial_garden',
    variantId: 'memorial_garden_v0',
    title: 'Memorial Garden / Classical Formal',
    appearanceKitId: 'memorial_garden_v0_reference_skin',
    plantingStructure: 'memorial_garden_v0',
    slug: 'memorial-garden-classical-formal',
    widthM: 50,
    depthM: 40,
    clearanceM: 0.5,
    surfaceKind: 'memorial_garden',
    assets: {
      pool: 'reflecting-pool.glb',
      fountain: 'tiered-fountain.glb',
      wall: 'memorial-wall.glb',
      urn: 'topiary-urn.glb',
    },
  }),
});

export type ArchetypeOwnedParkFamilyId = keyof typeof ARCHETYPE_OWNED_PARK_KITS;

export function archetypeOwnedParkKitForFamily(
  familyId: string,
): ArchetypeOwnedParkKitDefinition | null {
  return familyId in ARCHETYPE_OWNED_PARK_KITS
    ? ARCHETYPE_OWNED_PARK_KITS[familyId as ArchetypeOwnedParkFamilyId]
    : null;
}

export function archetypeOwnedParkKitForSelection(
  archetypeId: string,
  variantId: string,
): ArchetypeOwnedParkKitDefinition | null {
  return Object.values(ARCHETYPE_OWNED_PARK_KITS).find((candidate) => (
    candidate.archetypeId === archetypeId && candidate.variantId === variantId
  )) ?? null;
}
