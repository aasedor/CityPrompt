import { assetForZone, CATALOGUE_UPDATE_GUIDANCE } from '@/features/pickPlace/catalogue';
import { siteHasNoResidualLandscape } from '@/features/siteLandscape/automaticSiteTrees';
import type { SiteZone } from '@/types';
import type { ProjectDetails } from '@/features/parks/projectBenches';
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
  if (siteHasNoResidualLandscape(boundary)) return true;
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
  details?: ProjectDetails,
): CityPromptWorkflowState {
  const activeBoundary = getActiveSiteBoundary(zones);
  const physicalZones = zones.filter((zone) => (
    zone.coordinates?.length >= 3 && resolveCommunity3DKind(zone) !== null
  ));
  const pendingZones = physicalZones.filter((zone) => !(
    isCommunity3DCompiled(zone) && hasCommunity3DSourceFingerprint(zone)
    && hasExecutablePublicRealmRecipe(zone)
  ));
  const compiledZoneCount = physicalZones.length - pendingZones.length;
  const residualLandscapeReady = hasCompiledResidualLandscape(activeBoundary);
  const hasDetails = [details?.benches, details?.trees, details?.props, details?.surfaces]
    .some(items => Boolean(items?.length));
  const hasSceneContent = physicalZones.length > 0 || hasDetails;
  const allPhysicalZonesCompiled = compiledZoneCount === physicalZones.length;
  const sceneReady = hasSceneContent && allPhysicalZonesCompiled
    && (!activeBoundary || residualLandscapeReady);

  const currentStep: CityPromptWorkflowStep = !hasSceneContent
    ? activeBoundary ? 2 : 1
    : !sceneReady
      ? 3
      : 4;

  const generationReason = !hasSceneContent
    ? 'Draw a building, park, or street first. A site boundary is optional.'
    : sceneReady ? '3D up to date. Your scene is ready to render.' : CATALOGUE_UPDATE_GUIDANCE;

  const pendingReason = pendingZones.slice(0, 3).map(zone => {
    const kind = resolveCommunity3DKind(zone);
    const label = zone.name || assetForZone(zone)?.label || `${kind ?? 'Object'} ${physicalZones.indexOf(zone) + 1}`;
    return isCommunity3DCompiled(zone) && hasCommunity3DSourceFingerprint(zone)
      && !hasExecutablePublicRealmRecipe(zone)
      ? `${label}: the selected ${kind} layout could not be prepared. Check its ${kind === 'street' ? 'route length, width and selected variant' : 'outline size and selected variant'}, then retry the 3D update.`
      : `${label}: its 3D representation updates automatically. Wait for the update to finish, or use Retry 3D update.`;
  }).join(' ');
  const renderReason = !hasSceneContent
    ? 'Add a building, park, street, or detail first. A site boundary is optional.'
    : !allPhysicalZonesCompiled ? pendingReason
    : activeBoundary && !residualLandscapeReady ? 'The residual landscaping updates automatically. Wait for 3D saved, or use Retry 3D update if it fails.'
    : 'Your scene is ready for rendering.';

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
