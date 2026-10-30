import type { SiteZone } from '@/types';
import { nativeStreetPilotForZone } from '@/components/viewer/globe/nativeStreetPilot';

/** Only the exact surface-only adapters can use unrestricted path bends. */
export const isSurfacePath = (zone: Pick<SiteZone, 'zone_type' | 'properties'>) =>
  nativeStreetPilotForZone(zone, true)?.program?.adapter === 'narrow-pathway-v1';
