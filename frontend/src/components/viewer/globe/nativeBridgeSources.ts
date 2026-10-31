import pilots from '@/data/nativeBridgePilots.json';
import release from '@/data/nativeBridgeRelease.json';
import type { NativeStreetPose } from './nativeStreetPilot';
import type { SourceSpanBridge } from './sourceSpanBridgeProgram';
import type { PlaceAsset } from '@/features/pickPlace/assetRegistry';

export type NativeBridgeSource = typeof pilots[number];
type ReleaseEntry = typeof release.entries[number];
const sha = (value: unknown) => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const canonical = (value: unknown) => JSON.stringify(value, (_key, item: unknown) =>
  item && typeof item === 'object' && !Array.isArray(item)
    ? Object.fromEntries(Object.entries(item).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0)) : item);

/** A release attests the complete immutable profile, not just its friendly ID.
 * Backend/preflight also verify the canonical SHA, source row and evidence bytes. */
export function releasedNativeBridgeProfiles(entries: ReleaseEntry[] = release.entries): NativeBridgeSource[] {
  if (release.schema !== 'cityprompt.native-bridge-release@1' || release.authorization.approvedBy !== 'human_user') return [];
  return entries.filter(entry => {
    const profile = entry.profile;
    return entry.status === 'ready_for_production_pilot' && profile.status === 'candidate'
      && sha(entry.profileSha256) && canonical(profile) === entry.profileCanonical
      && entry.runtimeReview.status === 'prepared_level_scoped_pass'
      && entry.runtimeReview.profileSha256 === entry.profileSha256 && sha(entry.runtimeReview.sha256)
      && entry.sourceVisualReview.status === 'architectural_clay_pass'
      && entry.sourceVisualReview.sourceAssemblySha256 === profile.sourceAssemblySha256
      && sha(entry.sourceVisualReview.sha256) && sha(entry.provenance.sha256)
      && [profile.sourceAssemblySha256, profile.sourceRecipeSha256, profile.programSha256, profile.referenceSha256].every(sha)
      && Object.entries(profile.modules).every(([kind, module]) => sha(module.sha256)
        && module.bytes > 0 && module.url === `/street-kits/pilots/${profile.id}/${kind}.glb`);
  }).map(entry => entry.profile as NativeBridgeSource);
}

/** Development can rehearse held profiles; production mounts only exact receipts. */
export const nativeBridgeSources: NativeBridgeSource[] = import.meta.env.DEV && import.meta.env.MODE === 'development'
  ? pilots : releasedNativeBridgeProfiles();
export const nativeBridgeSource = (variant: unknown) => nativeBridgeSources.find(row => row.id === variant);
export const nativeBridgeSourceForAssembly = (sourceSha: unknown) => nativeBridgeSources.find(row => row.sourceAssemblySha256 === sourceSha);
export const isNativeBridgeRoute = (variant: unknown) => Boolean(nativeBridgeSource(variant));

/** Discovery only. Historical fixed identities keep their existing saved resolver.
 * A family name or shared source hash cannot retire an unrelated bridge design. */
export function nativeBridgeReplacesDiscovery(asset: Pick<PlaceAsset,'id'|'model'|'properties'>): boolean {
  if (import.meta.env.DEV && import.meta.env.MODE === 'development')
    return nativeBridgeSources.some(source => source.sourceAssemblySha256 === asset.model.revision);
  return release.entries.some(entry => isNativeBridgeRoute(entry.profile.id)
    && entry.replacesDiscovery.some(fixed => fixed.placementId === asset.id
      && fixed.archetypeId === asset.properties.road_archetype_id
      && fixed.variantId === asset.model.variantId && fixed.revision === asset.model.revision));
}

/** Deformation may execute only for a released source part and exact module.
 * Never silently draw a held topology at its undeformed source length. */
export function nativeBridgeDeformationAllowed(pose: NativeStreetPose): boolean {
  if (import.meta.env.DEV) return true;
  const source = nativeBridgeSource(pose.bridgeVariantId);
  const part = (source?.program.bridge as Partial<SourceSpanBridge> | undefined)?.parts?.find(item => item.kind === pose.kind);
  const module = source?.modules[pose.kind as keyof typeof source.modules];
  if (!part?.deformation || !module || !pose.bridgeDeformation) return false;
  const { requestedLengthM, ...contract } = pose.bridgeDeformation;
  return Number.isFinite(requestedLengthM) && requestedLengthM > 0
    && module.url === pose.url && module.sha256 === pose.sha256
    && canonical(contract) === canonical(part.deformation);
}
