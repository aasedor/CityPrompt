import contracts from './publicRealmOwnershipContracts.json';
import type { PublicRealmReleaseFixture } from './publicRealmRelease';

/** Exact source bytes and an explicit ownership revision are both required.
 * A same-named imported GLB must never inherit catalogue scene extraction. */
export function publicRealmOwnership(fixture: PublicRealmReleaseFixture) {
  return Object.values(contracts).find(contract => contract.sourceSha256 === fixture.sha256
    && contract.ownershipSha256 === fixture.ownershipSha256
    && fixture.id === contract.assetId
    && fixture.url === `/street-kits/claude-20261023/${contract.sourceSha256}.glb`);
}

export function publicRealmOwnershipIdentityValid(fixture: PublicRealmReleaseFixture): boolean {
  const expected = Object.values(contracts).some(contract => contract.sourceSha256 === fixture.sha256 || contract.assetId === fixture.id);
  return expected ? !!publicRealmOwnership(fixture) : !fixture.ownershipSha256;
}
