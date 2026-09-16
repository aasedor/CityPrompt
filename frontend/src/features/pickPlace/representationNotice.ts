import type { SiteZone } from '@/types';
import { getCommunity3DMeta } from '@/features/community3d/community3d';

/** Read saved representations, including after reload; job success does not imply detail. */
export function representationNotice(zones: SiteZone[]): string {
  const masses = zones.filter(zone => getCommunity3DMeta(zone)?.generator === 'planned_massing').length;
  const publicRealm = zones.filter(zone => Boolean(zone.properties?.public_realm_fallback)).length;
  return [
    masses ? `${masses} ${masses === 1 ? 'building is' : 'buildings are'} shown as design massing; detailed models are unavailable for this design or size.` : '',
    publicRealm ? `${publicRealm} ${publicRealm === 1 ? 'park or street has' : 'parks or streets have'} a simplified layout; the selected detailed design is unavailable for this design or size.` : '',
  ].filter(Boolean).join(' ');
}
