import { direct3DInstanceUserData, direct3DProposalUserData, direct3DZoneInstanceDescriptor } from './direct3dCapture';

/** A walkway is public-realm street geometry even when its owner is a building.
 * Set both tags locally so an enclosing layer cannot relabel it as park/ground. */
export function pedestrianCaptureUserData(ownerId: string) {
  return { ...direct3DProposalUserData('street'), ...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(ownerId, 'street')) };
}
