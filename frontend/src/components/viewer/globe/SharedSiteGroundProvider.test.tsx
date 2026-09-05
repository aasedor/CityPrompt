import { createContext } from 'react';
import { act, cleanup, render } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { INACTIVE_SHARED_SITE_GROUND, SharedSiteGroundProvider, useSharedSiteGround, type SharedSiteGroundState } from './SharedSiteGroundProvider';

const frame = vi.hoisted(() => ({ current: (() => {}) as () => void }));
vi.mock('@react-three/fiber', () => ({ useFrame: (callback: () => void) => { frame.current = callback; } }));
vi.mock('3d-tiles-renderer/r3f', async () => {
  const react = await import('react');
  return { TilesRendererContext: react.createContext<unknown>(null) };
});
vi.mock('3d-tiles-renderer', () => ({ WGS84_ELLIPSOID: {
  getCartographicToPosition: (lat: number, lng: number, height: number, vector: THREE.Vector3) => vector.set(lng, lat, height),
  getCartographicToNormal: (_lat: number, _lng: number, vector: THREE.Vector3) => vector.set(0, 0, 1),
  getPositionElevation: (point: THREE.Vector3) => point.z,
} }));
import { TilesRendererContext } from '3d-tiles-renderer/r3f';

const site: SiteZone = { id: 'site', project_id: 'project', zone_type: 'site_boundary',
  coordinates: [[-114, 51], [-114 + 2 / metersPerDegLon(51), 51], [-114 + 2 / metersPerDegLon(51), 51 + 2 / METERS_PER_DEG_LAT], [-114, 51 + 2 / METERS_PER_DEG_LAT]],
  properties: { community_3d_mask_existing_tiles: false, terrain_elevation_m: 99 }, is_active_boundary: true,
  created_at: 'today', updated_at: 'today', sort_order: 0, color: '#fff' };
let state: SharedSiteGroundState;
let hitObject: THREE.Object3D;
function Read() { state = useSharedSiteGround(); return null; }
function tileFixture() {
  const events = new Map<string, Set<() => void>>();
  const group = new THREE.Group(), tile = {}, scene = new THREE.Group();
  scene.add(hitObject); group.add(scene);
  return { group, scene, isLoading: false, visibleTiles: new Set([tile]),
    forEachLoadedModel: (callback: (scene: THREE.Object3D, tile: object) => void) => callback(scene, tile),
    addEventListener: (event: string, fn: () => void) => { if (!events.has(event)) events.set(event, new Set()); events.get(event)!.add(fn); },
    removeEventListener: (event: string, fn: () => void) => events.get(event)?.delete(fn),
    emit: (event: string) => events.get(event)?.forEach((fn) => fn()) };
}
const tick = (ms = 1000) => act(() => { vi.advanceTimersByTime(ms); frame.current(); });

describe('shared ground provider lifecycle', () => {
  beforeEach(() => { vi.useFakeTimers(); vi.setSystemTime(0); state = INACTIVE_SHARED_SITE_GROUND; hitObject = new THREE.Object3D();
    vi.spyOn(THREE.Raycaster.prototype, 'intersectObject').mockImplementation(() => [{ point: new THREE.Vector3(0, 0, 1030), object: hitObject } as THREE.Intersection]); });
  afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllEnvs(); vi.useRealTimers(); });
  it('is safe outside a provider and inactive for a prepared site', () => {
    render(<Read />); expect(state).toBe(INACTIVE_SHARED_SITE_GROUND);
    cleanup();
    render(<SharedSiteGroundProvider zones={[{ ...site, properties: {} }]}><Read /></SharedSiteGroundProvider>);
    tick(); expect(state.status).toBe('inactive'); expect(state.contains(-114, 51)).toBe(false);
  });
  it('publishes only complete repeatable tile heights, never the stored elevation, then invalidates on LOD changes', () => {
    const tiles = tileFixture(), onChange = vi.fn();
    const TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    render(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[site]} onChange={onChange}><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    expect(state.contains(-114, 51)).toBe(true); expect(state.heightAt(-114, 51)).toBeNull();
    tick(0); tick(); expect(state.status).toBe('sampling');
    tick(); expect(state.status).toBe('ready'); expect(state.heightAt(-114, 51)).toBe(1030);
    expect(window.__sharedGroundDiagnostics).toMatchObject({ status: 'ready', passes: 2, missCount: 0,
      passQuality: { valid: true }, deadlineReason: null, latestCompletedRawValues: [1030, 1030, 1030, 1030] });
    const previous = state.revision, notifications = onChange.mock.calls.length;
    tick(); expect(onChange).toHaveBeenCalledTimes(notifications);
    act(() => tiles.emit('load-model')); tick(0);
    expect(state.status).toBe('sampling'); expect(state.heightAt(-114, 51)).toBeNull(); expect(state.revision).not.toBe(previous);
    tick(); tick(); expect(state.status).toBe('ready');
  });
  it('bounds retries for missing cells and keeps the owned boundary unavailable', () => {
    vi.mocked(THREE.Raycaster.prototype.intersectObject).mockReturnValue([]);
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    render(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[site]}><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    tick(0); for (let i = 0; i < 4; i += 1) tick();
    expect(state.status).toBe('unavailable'); expect(state.contains(-114, 51)).toBe(true); expect(state.heightAt(-114, 51)).toBeNull();
    expect(window.__sharedGroundDiagnostics).toMatchObject({ status: 'unavailable', passes: 4, missCount: 4,
      deadlineReason: 'missing_samples', latestCompletedRawValues: [null, null, null, null] });
    const count = vi.mocked(THREE.Raycaster.prototype.intersectObject).mock.calls.length;
    tick(10000); expect(THREE.Raycaster.prototype.intersectObject).toHaveBeenCalledTimes(count);
  });
  it('drops old heights immediately when site geometry/revision changes', () => {
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    const tree = (zone: SiteZone) => <TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[zone]}><Read /></SharedSiteGroundProvider></TestContext.Provider>;
    const view = render(tree(site)); tick(0); tick(); tick(); expect(state.status).toBe('ready');
    view.rerender(tree({ ...site, updated_at: 'tomorrow', coordinates: site.coordinates.map(([lng, lat]) => [lng + 0.01, lat]) }));
    expect(state.status).toBe('sampling'); expect(state.heightAt(-114, 51)).toBeNull(); expect(state.contains(-114, 51)).toBe(false);
  });
  it('ignores a nearer hidden ancestor and loaded but non-visible LOD', () => {
    const tiles = tileFixture(), hidden = new THREE.Group(), hiddenMesh = new THREE.Object3D(), inactive = new THREE.Object3D();
    hidden.visible = false; hidden.add(hiddenMesh); tiles.scene.add(hidden); tiles.group.add(inactive);
    vi.mocked(THREE.Raycaster.prototype.intersectObject).mockReturnValue([
      { point: new THREE.Vector3(0, 0, 1050), object: hiddenMesh } as THREE.Intersection,
      { point: new THREE.Vector3(0, 0, 1040), object: inactive } as THREE.Intersection,
      { point: new THREE.Vector3(0, 0, 1030), object: hitObject } as THREE.Intersection,
    ]);
    const TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    render(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[site]}><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    tick(0); tick(); tick(); expect(state.status).toBe('ready'); expect(state.heightAt(-114, 51)).toBe(1030);
  });
  it('recovers an optimized bounding-volume seam miss only from a real visible-scene hit', () => {
    const tiles = tileFixture(), hidden = new THREE.Group(), hiddenMesh = new THREE.Object3D();
    hidden.visible = false; hidden.add(hiddenMesh); tiles.scene.add(hidden);
    vi.mocked(THREE.Raycaster.prototype.intersectObject).mockReturnValue([]);
    const direct = vi.spyOn(THREE.Raycaster.prototype, 'intersectObjects').mockReturnValue([
      { point: new THREE.Vector3(0, 0, 1050), object: hiddenMesh } as THREE.Intersection,
      { point: new THREE.Vector3(0, 0, 1030), object: hitObject } as THREE.Intersection,
    ]);
    const TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    render(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[site]}><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    tick(0); tick(); tick();
    expect(state.status).toBe('ready'); expect(state.heightAt(-114, 51)).toBe(1030);
    expect(direct).toHaveBeenCalledWith([tiles.scene], true);
    expect(direct).toHaveBeenCalledTimes(8); // Four measured cells, two passes.
  });
  it('does not expose sampled project data in a production environment', () => {
    vi.stubEnv('DEV', false);
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    render(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[site]}><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    tick(0); tick(); tick();
    expect(state.status).toBe('ready'); expect(window.__sharedGroundDiagnostics).toBeUndefined();
  });
});
