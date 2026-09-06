import { isCatalogueOnlyScene, CATALOGUE_UPDATE_GUIDANCE } from '@/features/pickPlace/catalogue';
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
  // Direct placement deliberately leaves unassigned land in its real context.
  if (boundary?.properties?.community_3d_landscape_mode === 'placed_objects_only'
      && boundary.properties?.community_3d_landscape == null) return true;
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
 * The result deliberately fails closed for every layer that exists. A saved
 * boundary requires current residual landscaping; a boundaryless scene needs
 * only current physical-zone representations.
 */
export function deriveCityPromptWorkflow(
  zones: SiteZone[],
  hasOutput = false,
): CityPromptWorkflowState {
  const catalogueOnly = isCatalogueOnlyScene(zones);
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
  const sceneReady = allPhysicalZonesCompiled
    && (!activeBoundary || residualLandscapeReady);

  const currentStep: CityPromptWorkflowStep = physicalZones.length === 0
    ? activeBoundary ? 2 : 1
    : !sceneReady
      ? 3
      : 4;

  const generationReason = physicalZones.length === 0
    ? 'Draw a building, park, or street first. A site boundary is optional.'
    : catalogueOnly
      ? sceneReady ? '3D up to date. Your catalogue scene is ready to render.' : CATALOGUE_UPDATE_GUIDANCE
    : sceneReady
      ? 'The current scene is ready. Run Generate to 3D again whenever you want to rebuild it.'
      : compiledZoneCount > 0
        ? activeBoundary
          ? 'Complete or rebuild the current buildings, public realm, and residual landscaping.'
          : 'Complete or rebuild the current buildings and public realm.'
        : activeBoundary
          ? 'Transform the authored plan into buildings, public realm, props, and residual landscaping.'
          : 'Transform the authored zones into buildings, public realm, and props.';

  const renderReason = physicalZones.length === 0
    ? 'Add a building, park, or street first. A site boundary is optional.'
    : catalogueOnly && !sceneReady
      ? CATALOGUE_UPDATE_GUIDANCE
    : !allPhysicalZonesCompiled
      ? 'Run Generate to 3D so every building, park, and street has a current 3D representation.'
      : activeBoundary && !residualLandscapeReady
        ? 'Run Generate to 3D to build the residual landscaping layer.'
        : 'The compiled scene is ready for rendering.';

  return {
    activeBoundary,
    physicalZones,
    compiledZoneCount,
    residualLandscapeReady,
    sceneReady,
    hasOutput,
    currentStep,
    canPlan: Boolean(activeBoundary),
    canGenerate3D: physicalZones.length > 0,
    canRender: sceneReady,
    generationReason,
    renderReason,
  };
}
