import type { SiteZone } from '@/types';
import { getCommunity3DMeta } from '@/features/community3d/community3d';
import { isParkTrio } from '@/components/viewer/globe/parkTrioLayout';
import { isNeighborhoodParkPilot } from '@/components/viewer/globe/neighborhoodParkLayout';
import { nativeBuildingUrl } from './nativeBuildingContract';
import { isResizeTrialShapeFreely } from './buildingResizeTrial';

/** Read saved representations, including after reload; job success does not imply detail. */
export function representationNotice(zones: SiteZone[]): string {
  // Building resize pilot: Shape freely is a choice, not a missing model.
  const shaped = zones.filter(zone => getCommunity3DMeta(zone)?.generator === 'planned_massing'
    && isResizeTrialShapeFreely(zone.properties)).length;
  const masses = zones.filter(zone => getCommunity3DMeta(zone)?.generator === 'planned_massing'
    && !(zone.zone_type === 'building' && nativeBuildingUrl(zone))).length - shaped;
  // These exact, explicitly selected layouts own their browser geometry even
  // when the server has no external asset family. Keep genuine fallbacks visible.
  const fallbackZones = zones.filter(zone => Boolean(zone.properties?.public_realm_fallback));
  const adaptive = fallbackZones.filter(zone => isParkTrio(zone) || isNeighborhoodParkPilot(zone)).length;
  const publicRealm = fallbackZones.length - adaptive;
  return [
    shaped ? `${shaped} ${shaped === 1 ? 'building is' : 'buildings are'} set to Shape freely and shown as shaped massing.` : '',
    masses ? `${masses} ${masses === 1 ? 'building is' : 'buildings are'} shown as design massing; detailed models are unavailable for this design or size.` : '',
    publicRealm ? `${publicRealm} ${publicRealm === 1 ? 'park or street has' : 'parks or streets have'} a simplified layout; the selected detailed design is unavailable for this design or size.` : '',
    adaptive ? `${adaptive} ${adaptive === 1 ? 'park uses' : 'parks use'} an adaptive 3D layout; available features depend on its outline.` : '',
  ].filter(Boolean).join(' ');
}
