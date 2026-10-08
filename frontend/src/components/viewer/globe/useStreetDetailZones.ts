import { useMemo } from 'react';
import type { SiteZone } from '@/types';
import { hasNativePark } from '@/features/parks/nativeParkRegistry';
import { publicRealmTrialAsset } from './publicRealmTrial';

export function useStreetDetailZones(zones: SiteZone[]): SiteZone[] {
  // Camera/walk UI updates must not invalidate the street layer's junction
  // and ribbon geometry caches. Actual zone edits still replace this input.
  return useMemo(() => zones.filter(zone => !publicRealmTrialAsset(zone) && !hasNativePark(zone)), [zones]);
}
