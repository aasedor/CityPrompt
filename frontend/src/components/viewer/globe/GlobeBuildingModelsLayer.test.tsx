import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { Building, SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const state = vi.hoisted(() => ({ status: 'sampling', height: 100 }));
vi.mock('./SharedSiteGroundProvider', () => ({ useSharedSiteGround: () => ({
  status: state.status, snapshot: null, revision: `${state.status}:${state.height}`,
  contains: () => true, heightAt: () => state.status === 'ready' ? state.height : null,
}) }));
vi.mock('@react-three/fiber', async () => {
  const three = await import('three');
  const renderer = { camera: { position: new three.Vector3() } };
  return { useFrame: () => {}, useThree: (select: (value: unknown) => unknown) => select(renderer) };
});
vi.mock('@react-three/drei', () => ({ useGLTF: () => ({ scene: new THREE.Group() }) }));
vi.mock('3d-tiles-renderer/r3f', async () => {
  const react = await import('react');
  return { TilesRendererContext: react.createContext(null),
    EastNorthUpFrame: ({ height }: { height: number }) => <div data-testid="model-frame" data-height={height} /> };
});
vi.mock('./GlobeZoneLayer', () => ({ raycastTerrainHeightAtLatLng: vi.fn() }));
vi.mock('./modelAssetAvailability', () => ({ modelAssetAvailable: async () => false }));
vi.mock('@/services/api', () => ({ resolveApiFileUrl: (url: string) => url }));

import { GlobeBuildingModelsLayer } from './GlobeBuildingModelsLayer';

const lng = -114, lat = 51;
const coordinates = [[lng, lat], [lng + 10 / metersPerDegLon(lat), lat],
  [lng + 10 / metersPerDegLon(lat), lat + 12 / METERS_PER_DEG_LAT], [lng, lat + 12 / METERS_PER_DEG_LAT]];
const building = { id: 'imported', project_id: 'project', name: 'Imported building', model_url: '/model.glb',
  height_meters: 8, footprint_coordinates: coordinates, created_at: 'today' } as Building;
const zones: SiteZone[] = [];

describe('imported model grounding lifecycle', () => {
  afterEach(() => cleanup());
  it('does not certify a loading mass until shared ground is ready and withdraws it on refinement', async () => {
    state.status = 'sampling'; state.height = 100;
    const loaded = vi.fn(), issues = vi.fn();
    const tree = () => <GlobeBuildingModelsLayer buildings={[building]} zones={zones} terrainHeight={-200}
      onLoadedIdsChange={loaded} onGroundingIssuesChange={issues} />;
    const view = render(tree());
    await waitFor(() => expect(issues).toHaveBeenLastCalledWith([{ buildingId: 'imported', reason: 'ground_not_ready' }]));
    expect(screen.queryByTestId('model-frame')).toBeNull();
    expect(loaded).toHaveBeenLastCalledWith(new Set());

    state.status = 'ready'; view.rerender(tree());
    await waitFor(() => expect(loaded).toHaveBeenLastCalledWith(new Set(['imported'])));
    expect(Number(screen.getByTestId('model-frame').dataset.height)).toBeCloseTo(100.04);
    expect(issues).toHaveBeenLastCalledWith([]);

    state.status = 'unavailable'; view.rerender(tree());
    await waitFor(() => expect(loaded).toHaveBeenLastCalledWith(new Set()));
    expect(screen.queryByTestId('model-frame')).toBeNull();
    expect(issues).toHaveBeenLastCalledWith([{ buildingId: 'imported', reason: 'ground_not_ready' }]);

    state.status = 'ready'; state.height = 101; view.rerender(tree());
    await waitFor(() => expect(loaded).toHaveBeenLastCalledWith(new Set(['imported'])));
    expect(Number(screen.getByTestId('model-frame').dataset.height)).toBeCloseTo(101.04);
  });
});
