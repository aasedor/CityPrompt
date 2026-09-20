import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { Building, SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const state = vi.hoisted(() => ({ status: 'sampling', height: 100, slope: 0 }));
vi.mock('./SharedSiteGroundProvider', () => ({ useSharedSiteGround: () => ({
  status: state.status, snapshot: null, revision: `${state.status}:${state.height}`,
  contains: () => true, heightAt: (lng: number) => state.status === 'ready'
    ? state.height + (lng + 114) * 111320 * Math.cos(51 * Math.PI / 180) * state.slope : null,
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
import { BuildingEntranceApproaches } from './BuildingEntranceApproaches';

const lng = -114, lat = 51;
const coordinates = [[lng, lat], [lng + 10 / metersPerDegLon(lat), lat],
  [lng + 10 / metersPerDegLon(lat), lat + 12 / METERS_PER_DEG_LAT], [lng, lat + 12 / METERS_PER_DEG_LAT]];
const building = { id: 'imported', project_id: 'project', name: 'Imported building', model_url: '/model.glb',
  height_meters: 8, footprint_coordinates: coordinates, created_at: 'today' } as Building;
const zones: SiteZone[] = [];

describe('imported model grounding lifecycle', () => {
  afterEach(() => { cleanup(); state.slope = 0; });
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
  it('reports a raised entrance through the capture issue callback while keeping its model visible', async () => {
    state.status = 'ready'; state.height = 100; state.slope = .2;
    const loaded = vi.fn(), issues = vi.fn();
    const owner = { id: 'house', zone_type: 'building', building_id: building.id, coordinates,
      properties: {} } as SiteZone;
    render(<BuildingEntranceApproaches zones={[owner]} results={[]}>
      <GlobeBuildingModelsLayer buildings={[building]} zones={[owner]} terrainHeight={-200}
        onLoadedIdsChange={loaded} onGroundingIssuesChange={issues} />
    </BuildingEntranceApproaches>);
    await waitFor(() => expect(issues).toHaveBeenLastCalledWith([
      { buildingId: 'imported', reason: 'entrance_connection_required' },
    ]));
    expect(loaded).toHaveBeenLastCalledWith(new Set(['imported']));
    expect(Number(screen.getByTestId('model-frame').dataset.height)).toBeCloseTo(102.04);
  });
});
