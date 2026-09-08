import { direct3DInstanceUserData, direct3DProposalUserData, direct3DZoneInstanceDescriptor } from './direct3dCapture';
import type { SiteZone } from '@/types';
import { readBuildingEntrance } from '@/features/pickPlace/pedestrianConnections';

/** A walkway is public-realm street geometry even when its owner is a building.
 * Set both tags locally so an enclosing layer cannot relabel it as park/ground. */
export function pedestrianCaptureUserData(ownerId: string) {
  return { ...direct3DProposalUserData('street'), ...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(ownerId, 'street')) };
}

/** Entrance approaches belong to their destination street in the render
 * inventory. Using the house ID with a street role contradicts the persisted
 * building identity and makes the server reject an otherwise valid capture. */
export function streetConnectionCaptureUserData(owner: SiteZone, zones: readonly SiteZone[]) {
  if (owner.zone_type === 'road') return pedestrianCaptureUserData(owner.id);
  const entrance = readBuildingEntrance(owner);
  const street = entrance && zones.find(zone => zone.id === entrance.streetId && zone.zone_type === 'road');
  if (!street) return null;
  return { ...pedestrianCaptureUserData(street.id), pedestrianOwnerZoneId: owner.id };
}
