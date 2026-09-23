import type { SiteZone } from '@/types';
import { getCommunity3DMeta } from '@/features/community3d/community3d';
import { isParkTrio } from '@/components/viewer/globe/parkTrioLayout';
import { isNeighborhoodParkPilot } from '@/components/viewer/globe/neighborhoodParkLayout';

/** Read saved representations, including after reload; job success does not imply detail. */
export function representationNotice(zones: SiteZone[]): string {
  const masses = zones.filter(zone => getCommunity3DMeta(zone)?.generator === 'planned_massing').length;
  // These exact, explicitly selected layouts own their browser geometry even
  // when the server has no external asset family. Keep genuine fallbacks visible.
  const fallbackZones = zones.filter(zone => Boolean(zone.properties?.public_realm_fallback));
  const adaptive = fallbackZones.filter(zone => isParkTrio(zone) || isNeighborhoodParkPilot(zone)).length;
  const publicRealm = fallbackZones.length - adaptive;
  return [
    masses ? `${masses} ${masses === 1 ? 'building is' : 'buildings are'} shown as design massing; detailed models are unavailable for this design or size.` : '',
    publicRealm ? `${publicRealm} ${publicRealm === 1 ? 'park or street has' : 'parks or streets have'} a simplified layout; the selected detailed design is unavailable for this design or size.` : '',
    adaptive ? `${adaptive} ${adaptive === 1 ? 'park uses' : 'parks use'} an adaptive 3D layout; available features depend on its outline.` : '',
  ].filter(Boolean).join(' ');
}
