import { createContext } from 'react';
import { act, cleanup, render } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { INACTIVE_SHARED_SITE_GROUND, SharedSiteGroundProvider, useSharedSiteGround, useSharedSiteGroundVerification, type SharedSiteGroundState } from './SharedSiteGroundProvider';
import { assertSharedGroundUnchanged, captureSharedGround } from './sharedGroundCapture';
import { surveySite } from '@/features/context/surveyGround.testFixtures';

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
let verification: SharedSiteGroundState;
let hitObject: THREE.Object3D;
function Read() { state = useSharedSiteGround(); verification = useSharedSiteGroundVerification(); return null; }
function tileFixture() {
  type Event = { type?: string; scene?: THREE.Object3D };
  const events = new Map<string, Set<(event?: Event) => void>>();
  const group = new THREE.Group(), tile = {}, scene = new THREE.Group();
  scene.add(hitObject); group.add(scene);
  return { group, scene, isLoading: false, visibleTiles: new Set([tile]),
    setCamera: vi.fn(), setResolution: vi.fn(), deleteCamera: vi.fn(),
    forEachLoadedModel: (callback: (scene: THREE.Object3D, tile: object) => void) => callback(scene, tile),
    addEventListener: (event: string, fn: (value?: Event) => void) => { if (!events.has(event)) events.set(event, new Set()); events.get(event)!.add(fn); },
    removeEventListener: (event: string, fn: (value?: Event) => void) => events.get(event)?.delete(fn),
    emit: (event: string, value?: Event) => events.get(event)?.forEach((fn) => fn(value)) };
}
const tick = (ms = 1000) => act(() => { vi.advanceTimersByTime(ms); frame.current(); });

describe('shared ground provider lifecycle', () => {
  beforeEach(() => { vi.useFakeTimers(); vi.setSystemTime(0); state = INACTIVE_SHARED_SITE_GROUND; hitObject = new THREE.Object3D();
    vi.spyOn(THREE.Raycaster.prototype, 'intersectObject').mockImplementation(() => [{ point: new THREE.Vector3(0, 0, 1030), object: hitObject } as THREE.Intersection]); });
  afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllEnvs(); vi.useRealTimers(); });
  it('uses saved classified ground without a renderer and without tile refinement changing it', () => {
    const view = render(<SharedSiteGroundProvider zones={[surveySite()]}><Read /></SharedSiteGroundProvider>);
    const revision = state.revision;
    tick(); tick(60000);
    expect(state.status).toBe('ready'); expect(state.revision).toBe(revision);
    expect(state.heightAt(-122.42695, 37.75905)).toBeCloseTo(-3, 6);
    expect(THREE.Raycaster.prototype.intersectObject).not.toHaveBeenCalled();
    view.rerender(<SharedSiteGroundProvider zones={[surveySite(null)]}><Read /></SharedSiteGroundProvider>);
    expect(state.status).toBe('unavailable'); expect(state.heightAt(-122.42695, 37.75905)).toBeNull();
  });
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
    const sourceFrameGround = captureSharedGround(verification);
    act(() => {
      tiles.emit('load-model');
      // Even a caller holding the previous React value must reject stale data.
      expect(() => captureSharedGround(verification)).toThrow('Ground alignment is not ready');
      expect(() => assertSharedGroundUnchanged(sourceFrameGround, verification)).toThrow('terrain changed');
    });
    // Capture can be requested between a tile event and the next animation frame.
    expect(verification.status).toBe('sampling');
    expect(() => captureSharedGround(verification)).toThrow('Ground alignment is not ready');
    expect(state.status).toBe('ready'); expect(state.revision).toBe(previous);
    tick(0);
    expect(state.status).toBe('ready'); expect(state.heightAt(-114, 51)).toBe(1030); expect(state.revision).toBe(previous);
    expect(verification.status).toBe('sampling'); expect(verification.snapshot).toBeNull();
    expect(onChange.mock.lastCall?.[0]).toBe(verification);
    expect(() => captureSharedGround(verification)).toThrow('Ground alignment is not ready');
    tick(); tick(); expect(state.status).toBe('ready');
  });
  it('keeps the same display surface through failed refreshes and swaps only after two verified passes', () => {
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    render(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[site]}><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    tick(0); tick(); tick();
    const displayed = state;
    vi.mocked(THREE.Raycaster.prototype.intersectObject).mockReturnValue([]);
    act(() => tiles.emit('tile-visibility-change')); tick(0);
    for (let i = 0; i < 4; i += 1) tick();
    expect(state).toBe(displayed); expect(state.heightAt(-114, 51)).toBe(1030);
    expect(verification.status).toBe('unavailable');
    expect(() => captureSharedGround(verification)).toThrow();
    vi.mocked(THREE.Raycaster.prototype.intersectObject).mockReturnValue([
      { point: new THREE.Vector3(0, 0, 1030.05), object: hitObject } as THREE.Intersection,
    ]);
    act(() => tiles.emit('load-model')); tick(0); tick();
    expect(state).toBe(displayed); expect(verification.status).toBe('sampling');
    tick();
    expect(state.heightAt(-114, 51)).toBe(1030.05);
    expect(captureSharedGround(verification)?.heights).toEqual([1030.05, 1030.05, 1030.05, 1030.05]);
  });
  it('invalidates capture immediately when the tile renderer is replaced at the same site', () => {
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    const tree = (value: typeof tiles) => <TestContext.Provider value={value}><SharedSiteGroundProvider zones={[site]}><Read /></SharedSiteGroundProvider></TestContext.Provider>;
    const view = render(tree(tiles)); tick(0); tick(); tick();
    const previous = state.revision;
    view.rerender(tree(tileFixture()));
    expect(state.revision).toBe(previous);
    expect(() => captureSharedGround(verification)).toThrow('Ground alignment is not ready');
    tick(0); tick(); tick();
    expect(captureSharedGround(verification)?.heights).toEqual([1030,1030,1030,1030]);
  });
  it('retains valid ground through a metadata-only save without sampling again', () => {
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    const tree = (zone: SiteZone) => <TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[zone]}><Read /></SharedSiteGroundProvider></TestContext.Provider>;
    const view = render(tree(site)); tick(0); tick(); tick();
    const before = captureSharedGround(verification);
    const rays = vi.mocked(THREE.Raycaster.prototype.intersectObject).mock.calls.length;
    view.rerender(tree({ ...site, updated_at: 'renamed', properties: { ...site.properties, name: 'Updated label' } }));
    tick();
    expect(captureSharedGround(verification)).toMatchObject({ signature: before!.signature, boundaryUpdatedAt: 'renamed' });
    expect(THREE.Raycaster.prototype.intersectObject).toHaveBeenCalledTimes(rays);
  });
  it('retires capture evidence on unmount and remeasures after reopening', () => {
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    const tree = <TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[site]}><Read /></SharedSiteGroundProvider></TestContext.Provider>;
    const view = render(tree); tick(0); tick(); tick();
    const previous = verification;
    view.unmount();
    expect(() => captureSharedGround(previous)).toThrow('Ground alignment is not ready');
    vi.mocked(THREE.Raycaster.prototype.intersectObject).mockReturnValue([
      { point: new THREE.Vector3(0, 0, 1031), object: hitObject } as THREE.Intersection,
    ]);
    render(tree);
    expect(() => captureSharedGround(verification)).toThrow();
    tick(0); tick(); tick();
    expect(captureSharedGround(verification)?.heights).toEqual([1031,1031,1031,1031]);
  });
  it('inspects prepared terrain without replacing the design ground or changing capture readiness', () => {
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    const prepared = { ...site, properties: { community_3d_mask_existing_tiles: true, terrain_elevation_m: 99 } };
    const view = render(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[prepared]} inspectPrepared><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    tick(0); tick();
    expect(state.status).toBe('inactive'); expect(state.heightAt(-114, 51)).toBeNull();
    expect(state.inspectionStatus).toBe('sampling');
    tick();
    expect(state.inspectionStatus).toBe('ready'); expect(state.snapshot).toBeNull();
    expect(state.revision).toBe('inactive');
    expect(state.review?.heights).toEqual([1030,1030,1030,1030]);
    expect(state.review?.previousHeights).toEqual([1030,1030,1030,1030]);
    view.rerender(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[prepared]}><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    expect(state).toBe(INACTIVE_SHARED_SITE_GROUND);
    expect(tiles.deleteCamera).toHaveBeenCalled();
  });
  it('keeps hillside park sites under shared-ground verification', () => {
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    const landscape = { ...site, properties: { ...site.properties, terrain_strategy: 'landscape' as const } };
    render(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[landscape]}><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    expect(verification.status).toBe('sampling');
    tick(0); tick(); tick();
    expect(verification.status).toBe('ready');
    expect(captureSharedGround(verification)?.heights).toEqual([1030, 1030, 1030, 1030]);
  });
  it('retains measured ground for off-site tile events and releases its selection camera on unmount', () => {
    const tiles = tileFixture(), TestContext = TilesRendererContext as ReturnType<typeof createContext<unknown>>;
    const view = render(<TestContext.Provider value={tiles}><SharedSiteGroundProvider zones={[site]}><Read /></SharedSiteGroundProvider></TestContext.Provider>);
    tick(0); tick(); tick();
    const revision = state.revision, snapshot = state.snapshot;
    const remote = new THREE.Mesh(new THREE.BoxGeometry(1,1,1)); remote.position.set(1e7,1e7,1e7);
    act(() => tiles.emit('tile-visibility-change', { type: 'tile-visibility-change', scene: remote })); tick();
    expect(state.status).toBe('ready'); expect(state.revision).toBe(revision); expect(state.snapshot).toBe(snapshot);
    expect(tiles.setCamera).toHaveBeenCalledTimes(1); expect(tiles.setResolution).toHaveBeenCalledTimes(1);
    view.unmount(); expect(tiles.deleteCamera).toHaveBeenCalledWith(tiles.setCamera.mock.calls[0][0]);
    remote.geometry.dispose();
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
