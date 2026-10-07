import type { Object3D } from 'three';
import type { SiteZone } from '@/types';
import { mountBuildingWalking, readBuildingWalking } from './buildingWalking';
import { measuredWalkPlan, prepareMeasuredBuildingWalking, resolveMeasuredWalkPlan } from './measuredBuildingWalking';

/** Shared lifecycle for exact embedded, versioned, and older byte-verified GLBs.
 * A late lookup must never mount a route after movement, replacement or deletion. */
export function mountModelBuildingWalking(id: string, zone: SiteZone, source: Object3D, url: string) {
  const embedded = readBuildingWalking(source);
  if (embedded) return mountBuildingWalking(id, zone, source, embedded);
  if (!url) return () => {};
  let cancelled = false, cleanup: (() => void) | undefined;
  const prepare = (plan: ReturnType<typeof measuredWalkPlan>) => {
    if (cancelled || !plan) return;
    const measured = prepareMeasuredBuildingWalking(source, plan);
    if (!measured) return;
    const unmount = mountBuildingWalking(id, zone, source, measured.network, measured.setOpen);
    cleanup = () => { unmount(); measured.dispose(); };
  };
  const declared = measuredWalkPlan(zone.properties?.pick_place_model_revision, url);
  if (declared) prepare(declared);
  else void resolveMeasuredWalkPlan(zone.properties?.pick_place_model_revision, url).then(prepare).catch(() => {});
  return () => { cancelled = true; cleanup?.(); };
}
