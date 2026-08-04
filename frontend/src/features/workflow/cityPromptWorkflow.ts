import type { SiteZone } from '@/types';
import {
  hasCommunity3DSourceFingerprint,
  hasExecutablePublicRealmRecipe,
  isCommunity3DCompiled,
  resolveCommunity3DKind,
} from '@/features/community3d/community3d';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';

export type CityPromptWorkflowStep = 1 | 2 | 3 | 4;

export interface CityPromptWorkflowState {
  activeBoundary: SiteZone | null;
  physicalZones: SiteZone[];
  compiledZoneCount: number;
  residualLandscapeReady: boolean;
  sceneReady: boolean;
  hasOutput: boolean;
  currentStep: CityPromptWorkflowStep;
  canPlan: boolean;
  canGenerate3D: boolean;
  canRender: boolean;
  generationReason: string;
  renderReason: string;
}

function hasCompiledResidualLandscape(boundary: SiteZone | null): boolean {
  const raw = (boundary?.properties as Record<string, unknown> | undefined)
    ?.community_3d_landscape;
  if (!raw || typeof raw !== 'object') return false;
  const recipe = raw as Record<string, unknown>;
  return recipe.schema_version === 1
    && recipe.state === 'compiled'
    && recipe.boundary_id === boundary?.id
    && typeof recipe.source_hash === 'string'
    && /^[a-f0-9]{64}$/i.test(recipe.source_hash);
}

/**
 * Derive the one user-facing City Prompt workflow from persisted scene state.
 * The result deliberately fails closed: stale Community 3D metadata and a
 * missing residual-landscape recipe send the project back to Generate to 3D
 * instead of allowing a render that looks complete but is not current.
 */
export function deriveCityPromptWorkflow(
  zones: SiteZone[],
  hasOutput = false,
): CityPromptWorkflowState {
  const activeBoundary = getActiveSiteBoundary(zones);
  const physicalZones = zones.filter((zone) => (
    zone.coordinates?.length >= 3 && resolveCommunity3DKind(zone) !== null
  ));
  const compiledZoneCount = physicalZones.filter((zone) => (
    isCommunity3DCompiled(zone)
    && hasCommunity3DSourceFingerprint(zone)
    && hasExecutablePublicRealmRecipe(zone)
  )).length;
  const residualLandscapeReady = hasCompiledResidualLandscape(activeBoundary);
  const allPhysicalZonesCompiled = physicalZones.length > 0
    && compiledZoneCount === physicalZones.length;
  const sceneReady = Boolean(
    activeBoundary && allPhysicalZonesCompiled && residualLandscapeReady,
  );

  const currentStep: CityPromptWorkflowStep = !activeBoundary
    ? 1
    : physicalZones.length === 0
      ? 2
      : !sceneReady
        ? 3
        : 4;

  const generationReason = !activeBoundary
    ? 'Draw and save the site boundary first.'
    : physicalZones.length === 0
      ? 'Draw buildings, parks, or streets, or create a Master Planner scenario first.'
      : sceneReady
        ? 'The current scene is ready. Run Generate to 3D again whenever you want to rebuild it.'
        : compiledZoneCount > 0
          ? 'Complete or rebuild the current buildings, public realm, and residual landscaping.'
          : 'Transform the authored plan into buildings, public realm, props, and residual landscaping.';

  const renderReason = !activeBoundary
    ? 'Draw the site boundary first.'
    : physicalZones.length === 0
      ? 'Add a plan inside the site boundary first.'
      : !allPhysicalZonesCompiled
        ? 'Run Generate to 3D so every building, park, and street has a current 3D representation.'
        : !residualLandscapeReady
          ? 'Run Generate to 3D to build the residual landscaping layer.'
          : 'The compiled scene is ready for image and video rendering.';

  return {
    activeBoundary,
    physicalZones,
    compiledZoneCount,
    residualLandscapeReady,
    sceneReady,
    hasOutput,
    currentStep,
    canPlan: Boolean(activeBoundary),
    canGenerate3D: Boolean(activeBoundary && physicalZones.length > 0),
    canRender: sceneReady,
    generationReason,
    renderReason,
  };
}
