export interface RlasmPresentationBuilding {
  generation_engine?: string | null;
  model_url?: string | null;
  lod_urls?: Record<string, string> | null;
}

export interface ArchitecturalLightingProfile {
  ambientIntensity: number;
  hemisphereIntensity: number;
  directionalIntensity: number;
  environmentIntensity: number;
}

export const DEFAULT_GLOBE_LIGHTING: ArchitecturalLightingProfile = {
  ambientIntensity: 1.35,
  hemisphereIntensity: 1.5,
  directionalIntensity: 1.8,
  environmentIntensity: 1,
};

export const RLASM_ARCHITECTURAL_LIGHTING: ArchitecturalLightingProfile = {
  ambientIntensity: 0.55,
  hemisphereIntensity: 0.75,
  directionalIntensity: 1.25,
  environmentIntensity: 0.7,
};

function hasRenderableModel(building: RlasmPresentationBuilding): boolean {
  return Boolean(building.model_url || Object.values(building.lod_urls ?? {}).some(Boolean));
}

export function hasPlacedRlasmModel(
  buildings: readonly RlasmPresentationBuilding[] | null | undefined,
): boolean {
  return Boolean(buildings?.some((building) => (
    building.generation_engine?.trim().toLowerCase() === 'rlasm'
    && hasRenderableModel(building)
  )));
}

export function getArchitecturalLightingProfile(
  buildings: readonly RlasmPresentationBuilding[] | null | undefined,
): ArchitecturalLightingProfile {
  return hasPlacedRlasmModel(buildings)
    ? RLASM_ARCHITECTURAL_LIGHTING
    : DEFAULT_GLOBE_LIGHTING;
}
