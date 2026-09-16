import { StrictMode, Suspense } from 'react';
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { ParkAssemblyGroundProvider, useOwnParkAssemblyGround, useParkAssemblyGroundOwners } from './ParkAssemblyGround';

const zone = { id: 'park', updated_at: 'r1', coordinates: [[0, 0], [1, 0], [1, 1]] } as SiteZone;
function Loaded({ pending = false }: { pending?: boolean }) {
  useOwnParkAssemblyGround(zone);
  if (pending) throw new Promise(() => {});
  return null;
}
function Ground({ current = zone }: { current?: SiteZone }) {
  const owners = useParkAssemblyGroundOwners([current]);
  return <output>{owners.length ? 'assembly' : 'fallback'}</output>;
}
function Scene({ loaded = true, pending = false, current = zone }) {
  return <StrictMode><ParkAssemblyGroundProvider><Ground current={current} />
    <Suspense fallback={null}>{loaded && <Loaded pending={pending} />}</Suspense>
  </ParkAssemblyGroundProvider></StrictMode>;
}
it('restores generic ground when a loaded assembly unmounts', () => {
  const view = render(<Scene />);
  expect(screen.getByText('assembly')).toBeTruthy();
  view.rerender(<Scene loaded={false} />);
  expect(screen.getByText('fallback')).toBeTruthy();
});
it('does not cut terrain while assets are suspended', () => {
  render(<Scene pending />); expect(screen.getByText('fallback')).toBeTruthy();
});
it('does not use an old registration for moved or revised geometry', () => {
  const view = render(<Scene />);
  view.rerender(<Scene current={{ ...zone, updated_at: 'r2' }} />);
  expect(screen.getByText('fallback')).toBeTruthy();
  view.rerender(<Scene current={{ ...zone, coordinates: [[2, 2], [3, 2], [3, 3]] }} />);
  expect(screen.getByText('fallback')).toBeTruthy();
});
