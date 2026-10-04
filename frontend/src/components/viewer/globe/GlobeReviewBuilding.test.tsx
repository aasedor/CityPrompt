import { act, cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import { GlobeReviewBuilding, reviewBuildingPointerHit } from './GlobeReviewBuilding';
import { BuildingEntranceApproaches } from './BuildingEntranceApproaches';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

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
  it('reports real mesh hits in the foundation frame without undoing the building rotation', () => {
    const frame = new THREE.Group();
    frame.position.set(1000,2000,3000);
    frame.rotation.set(.2,.1,.4);
    const rotatedBuilding = new THREE.Group();
    rotatedBuilding.rotation.z = 5*Math.PI/180;
    frame.add(rotatedBuilding); frame.updateMatrixWorld(true);
    const step = new THREE.Vector3(1,-10,.12);
    const foundationPoint = step.clone().applyMatrix4(rotatedBuilding.matrix);
    const worldPoint = rotatedBuilding.localToWorld(step.clone());
    const origin = worldPoint.clone().add(new THREE.Vector3(0,0,20));
    const direction = worldPoint.clone().sub(origin).normalize();
    const contact = {status:'ready' as const, anchorHeight:1000.04,reliefM:0,positions:[],indices:[]};
    const footprints: [number,number][][] = [[[-12,-11],[12,-11],[12,11],[-12,11]]];
    const hit = reviewBuildingPointerHit(frame, {point:worldPoint,ray:new THREE.Ray(origin,direction),distance:20},
      {footprints,lng:-114,lat:51,contact});
    hit.point.forEach((value,index) => expect(value).toBeCloseTo(foundationPoint.toArray()[index],8));
    expect(hit.ray).toEqual({origin:origin.toArray(),direction:direction.toArray(),distance:20});
    expect(hit.footprints).toBe(footprints);
    expect(worldPoint.distanceTo(rotatedBuilding.localToWorld(step.clone()))).toBeLessThan(1e-8);
  });
  it('uses verified shared contact for seating/walking and removes its report on unmount', () => {
    const {props,report,unmountWalking} = setup();
    const view = render(<GlobeReviewBuilding {...props} onGroundingIssue={report}/>);
    expect(Number(screen.getByTestId('frame').dataset.height)).toBeCloseTo(1000.04,8);
    expect(screen.getByTestId('foundation')).toBeTruthy();
    expect(report).toHaveBeenLastCalledWith('building','review:zone',null,null);
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
    expect(report).toHaveBeenLastCalledWith('building','review:zone','ground_not_ready',null);
    expect(unmountWalking).toHaveBeenCalledTimes(1);
    expect(mocks.mountWalking).toHaveBeenCalledTimes(1);
    mocks.verified.mockReturnValue(ground());
    view.rerender(<GlobeReviewBuilding {...props} onGroundingIssue={report}/>);
    expect(report).toHaveBeenLastCalledWith('building','review:zone',null,null);
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
      mode === 'partial' ? 'incomplete_footprint_ground' : 'ground_not_ready',null);
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
    expect(report).toHaveBeenLastCalledWith('building','review:zone','ground_not_ready',null);
    expect(mocks.mountWalking).toHaveBeenCalledTimes(1);
  });
  it('renders and publishes the shared measured approach, then retires it when its street disappears', () => {
    const {props,report} = setup();
    const geo = (x:number,y:number):[number,number] => [-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
    const boundary = {...zone,id:'boundary',building_id:undefined,zone_type:'site_boundary' as const,
      coordinates:[geo(-100,-100),geo(100,-100),geo(100,100),geo(-100,100)],
      properties:{community_3d_mask_existing_tiles:true,terrain_elevation_m:1000}};
    const owner = {...zone,coordinates:[geo(-19,-15),geo(19,-15),geo(19,15),geo(-19,15)],
      properties:{...zone.properties,pedestrian_building_entrance:{version:1,xM:0,yM:-15,
        referenceWidthM:38,referenceDepthM:30,scaleWithPlot:false,streetId:'street',widthM:1.8}}};
    const street = {...zone,id:'street',building_id:undefined,zone_type:'road' as const,properties:{}};
    const connection = {ownerId:'zone',kind:'building' as const,id:'route',status:'connected' as const,reason:'',
      strips:[{id:'route',ownerId:'zone',start:geo(0,-25),end:geo(0,-15),widthM:1.8,startLiftM:.025,endLiftM:.025,color:'#aaa'}]};
    mocks.display.mockReturnValue(ground('inactive')); mocks.verified.mockReturnValue(ground('inactive'));
    const draw = (zones:SiteZone[]) => <BuildingEntranceApproaches zones={zones} results={[connection]}>
      <GlobeReviewBuilding {...props} zone={owner} zones={zones} onGroundingIssue={report}/>
    </BuildingEntranceApproaches>;
    const view = render(draw([boundary,owner,street]));
    expect(view.container.querySelector('mesh[name="building-entrance-approach"]')).toBeTruthy();
    expect(report).toHaveBeenLastCalledWith('building','review:zone',null,expect.objectContaining({
      buildingId:'building',generatedSteps:0,clearWidthM:1.8,riseM:expect.any(Number),groundRevision:expect.any(String)}));
    view.rerender(draw([boundary,owner]));
    expect(view.container.querySelector('mesh[name="building-entrance-approach"]')).toBeNull();
    expect(report).toHaveBeenLastCalledWith('building','review:zone','entrance_approach_obstructed',null);
    view.unmount(); expect(report).toHaveBeenLastCalledWith('building','review:zone',null);
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
    expect(report).toHaveBeenLastCalledWith('building','review:zone',null,null);
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
