import { act, cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import { GlobeReviewBuilding } from './GlobeReviewBuilding';

const mocks = vi.hoisted(() => ({ gltf: vi.fn(), display: vi.fn(), verified: vi.fn(),
  readWalking: vi.fn(), mountWalking: vi.fn() }));
vi.mock('@react-three/drei', () => ({ useGLTF: mocks.gltf }));
vi.mock('3d-tiles-renderer/r3f', () => ({ EastNorthUpFrame: ({ children, height }: { children: React.ReactNode; height: number }) =>
  <div data-testid="frame" data-height={height}>{children}</div> }));
vi.mock('./SharedSiteGroundProvider', () => ({ useSharedSiteGround: mocks.display, useSharedSiteGroundVerification: mocks.verified }));
vi.mock('./BuildingFoundationSurface', () => ({ BuildingFoundationSurface: () => <div data-testid="foundation"/> }));
vi.mock('@/features/legoAssembly/buildingWalking', () => ({ readBuildingWalking: mocks.readWalking, mountBuildingWalking: mocks.mountWalking }));

const zone = { id:'zone', building_id:'building', zone_type:'building', project_id:'project',
  color:'#ffffff', sort_order:0, created_at:'2026-10-04T00:00:00Z', updated_at:'2026-10-04T00:00:00Z',
  coordinates:[[-114.0001,50.9999],[-113.9999,50.9999],[-113.9999,51.0001],[-114.0001,51.0001]],
  properties:{validation_native_url:'/exact.glb',terrain_elevation_m:1000} } as SiteZone;
function ground(status: SharedSiteGroundState['status'] = 'ready'): SharedSiteGroundState {
  return { status, revision:status, snapshot:null, contains:() => true,
    heightAt:() => 1000, isCurrent:() => status === 'ready' };
}
function setup() {
  const scene = new THREE.Group();
  scene.add(new THREE.Mesh(new THREE.BoxGeometry(38,7,30)));
  mocks.gltf.mockReturnValue({scene}); mocks.display.mockReturnValue(ground());
  mocks.verified.mockReturnValue(ground()); mocks.readWalking.mockReturnValue({version:2});
  const unmountWalking = vi.fn(); mocks.mountWalking.mockReturnValue(unmountWalking);
  return { unmountWalking, report:vi.fn(), props:{zone,zones:[zone],terrainHeight:999} };
}
afterEach(() => { cleanup(); vi.clearAllMocks(); });

describe('review GLB ground lifecycle', () => {
  it('uses verified shared contact for seating/walking and removes its report on unmount', () => {
    const {props,report,unmountWalking} = setup();
    const view = render(<GlobeReviewBuilding {...props} onGroundingIssue={report}/>);
    expect(Number(screen.getByTestId('frame').dataset.height)).toBeCloseTo(1000.04,8);
    expect(screen.getByTestId('foundation')).toBeTruthy();
    expect(report).toHaveBeenLastCalledWith('building','review:zone',null);
    expect(mocks.mountWalking).toHaveBeenCalledTimes(1);
    view.unmount(); expect(unmountWalking).toHaveBeenCalledTimes(1);
    expect(report).toHaveBeenLastCalledWith('building','review:zone',null);
  });
  it('retains display seating during a tile refresh while blocking walking and shared capture readiness', () => {
    const {props,report,unmountWalking} = setup();
    const view = render(<GlobeReviewBuilding {...props} onGroundingIssue={report}/>);
    mocks.verified.mockReturnValue(ground('sampling'));
    view.rerender(<GlobeReviewBuilding {...props} onGroundingIssue={report}/>);
    expect(Number(screen.getByTestId('frame').dataset.height)).toBeCloseTo(1000.04,8);
    expect(screen.getByTestId('foundation')).toBeTruthy();
    expect(report).toHaveBeenLastCalledWith('building','review:zone','ground_not_ready');
    expect(unmountWalking).toHaveBeenCalledTimes(1);
    expect(mocks.mountWalking).toHaveBeenCalledTimes(1);
    mocks.verified.mockReturnValue(ground());
    view.rerender(<GlobeReviewBuilding {...props} onGroundingIssue={report}/>);
    expect(report).toHaveBeenLastCalledWith('building','review:zone',null);
    expect(mocks.mountWalking).toHaveBeenCalledTimes(2);
  });
  it.each(['partial','stale','preview'] as const)('blocks walking and capture status for %s verification', mode => {
    const {props,report} = setup(); const verified = ground();
    if (mode === 'partial') verified.heightAt = () => null;
    if (mode === 'stale') verified.isCurrent = () => false;
    if (mode === 'preview') verified.preview = true;
    mocks.verified.mockReturnValue(verified);
    render(<GlobeReviewBuilding {...props} onGroundingIssue={report}/>);
    expect(mocks.mountWalking).not.toHaveBeenCalled();
    expect(report).toHaveBeenLastCalledWith('building','review:zone',
      mode === 'partial' ? 'incomplete_footprint_ground' : 'ground_not_ready');
  });
  it('uses an explicitly prepared level only when shared measured ground is inactive', () => {
    const {props,report} = setup();
    const boundary = { ...zone, id:'boundary', building_id:undefined, zone_type:'site_boundary',
      coordinates:[[-114.001,50.999],[-113.999,50.999],[-113.999,51.001],[-114.001,51.001]],
      properties:{community_3d_mask_existing_tiles:true,terrain_elevation_m:1102.662} } as SiteZone;
    mocks.display.mockReturnValue(ground('inactive')); mocks.verified.mockReturnValue(ground('inactive'));
    const view = render(<GlobeReviewBuilding {...props} zones={[boundary,zone]} onGroundingIssue={report}/>);
    expect(Number(screen.getByTestId('frame').dataset.height)).toBeCloseTo(1102.702,8);
    expect(mocks.mountWalking).toHaveBeenCalledTimes(1);
    mocks.display.mockReturnValue(ground('sampling')); mocks.verified.mockReturnValue(ground('sampling'));
    view.rerender(<GlobeReviewBuilding {...props} zones={[boundary,zone]} onGroundingIssue={report}/>);
    expect(report).toHaveBeenLastCalledWith('building','review:zone','ground_not_ready');
    expect(mocks.mountWalking).toHaveBeenCalledTimes(1);
  });
  it('reports a suspended GLB until it loads, then clears the loading barrier', async () => {
    const {props,report} = setup(); const loaded = mocks.gltf();
    let resolve!: () => void; const pending = new Promise<void>(done => { resolve = done; });
    mocks.gltf.mockImplementation(() => { throw pending; });
    render(<GlobeReviewBuilding {...props} onGroundingIssue={report}/>);
    expect(report).toHaveBeenLastCalledWith('building','review:zone','review_model_loading');
    expect(mocks.mountWalking).not.toHaveBeenCalled();
    mocks.gltf.mockReturnValue(loaded);
    await act(async () => { resolve(); await pending; });
    expect(report).toHaveBeenLastCalledWith('building','review:zone',null);
    expect(mocks.mountWalking).toHaveBeenCalledTimes(1);
  });
  it('reports failed GLB loading and keeps the fallback at the owned geographic frame', () => {
    const {props,report} = setup();
    const errors = vi.spyOn(console,'error').mockImplementation(() => {});
    try {
      mocks.gltf.mockImplementation(() => { throw new Error('fixture unavailable'); });
      const view = render(<GlobeReviewBuilding {...props} onGroundingIssue={report}/>);
      expect(report).toHaveBeenLastCalledWith('building','review:zone','review_model_unavailable');
      expect(Number(screen.getByTestId('frame').dataset.height)).toBe(1000);
      expect(mocks.mountWalking).not.toHaveBeenCalled();
      view.unmount(); expect(report).toHaveBeenLastCalledWith('building','review:zone',null);
    } finally { errors.mockRestore(); }
  });
});
