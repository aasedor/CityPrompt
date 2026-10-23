import roster from '@/data/claudeBuildingRelease.json';
import { CATALOGUE_BUILDING_ASSETS } from './publishedBuildingAssets';

/** Exact reviewed cohort only. Canonical unpublished trials stay on the local
 * development server until their actual runtime trial and activation pass. */
export const CLAUDE_BUILDING_RELEASE_ASSETS = CATALOGUE_BUILDING_ASSETS.filter(asset =>
  (asset.readiness === 'ready' || (import.meta.env.DEV && import.meta.env.MODE === 'development'))
  && roster.entries.some(entry => entry.asset_id === asset.id
    && entry.archetype_id === asset.properties.development_archetype_id
    && entry.variant_id === asset.model.variantId
    && entry.candidate === asset.model.revision));
