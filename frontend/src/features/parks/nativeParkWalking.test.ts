import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { nativeParkLayouts, nativeParkProperties, readNativePark } from './nativeParkRegistry';
import { verifiedScene } from './nativeParkAssets';
import { constrainNativeParkWalk, nativeParkLiftDestination, nativeParkWalkEntrance, nativeParkWalkEntry } from './nativeParkWalking';
import { STEP_FREE_PARK_LIFTS, stepFreeParkWalkingNetwork } from './stepFreeParkAccess';
import { advanceParkWalk, parkWalkHeight, type WalkPoint } from './parkWalking';
import { authoredCameraGround } from '@/components/viewer/globe/authoredCameraGround';
vi.mock('./nativeParkAssets', () => ({ verifiedScene: vi.fn() }));

const boundary = { id: 'site', zone_type: 'site_boundary', is_active_boundary: true,
  project_id: 'qa', color: '#aaa', sort_order: 0, created_at: 'now', updated_at: 'now',
  coordinates: rectangleAt([-114, 51], 200, 200),
  properties: { terrain_elevation_m: 1103, community_3d_mask_existing_tiles: true } } as SiteZone;
function fixture(angle = 0, variantId = 'student_quarry_garden_v1') {
  const layout = nativeParkLayouts.find(p => p.variantId === variantId)!;
  const coordinates = rectangleAt([-114, 51], 70, 80, angle);
  const park = { ...boundary, id: 'park', zone_type: 'green_space', is_active_boundary: false,
    coordinates, properties: nativeParkProperties({}, layout, coordinates) } as SiteZone;
  const f = readNativePark(park)!.selection.frame;
  const point = (x: number, y: number, z = 0, heading = 0) => ({
    lng: f.longitude + (x * Math.cos(f.yaw) - y * Math.sin(f.yaw)) / metersPerDegLon(f.latitude),
    lat: f.latitude + (x * Math.sin(f.yaw) + y * Math.cos(f.yaw)) / METERS_PER_DEG_LAT,
    groundHeight: 1103 + z, heading,
  });
  return { zones: [boundary, park], point, layout };
}

describe('native park walking in saved placement frames', () => {
  beforeEach(() => { vi.mocked(verifiedScene).mockReset(); });
  it.each([0, 37, 90, 180])('recovers to the real entrance after rotation %s', angle => {
    const { zones, point } = fixture(angle);
    const entrance = nativeParkWalkEntrance(zones, point(0, 0, -4.5, 67))!;
    expect(entrance.lng).toBeCloseTo(point(0, -33.5).lng, 9);
    expect(entrance.lat).toBeCloseTo(point(0, -33.5).lat, 9);
    expect(entrance.groundHeight).toBe(1103);
    expect(entrance.heading).toBe(67);
  });
  it('permits leaving through the entrance and rejects crossing a side edge', () => {
    const { zones, point } = fixture();
    const exit = point(0, -34.1);
    expect(constrainNativeParkWalk(zones, point(0, -33.95), exit)).toEqual(exit);
    const outside = point(30.1, 0);
    const blocked = constrainNativeParkWalk(zones, outside, point(29.95, 0, 0, 123));
    expect(blocked).toEqual({ ...outside, heading: 123 });
  });
  it('keeps turning and backing away available at a pool edge', () => {
    const { zones, point } = fixture();
    const from = point(3.75, 0, -4.5);
    const stopped = constrainNativeParkWalk(zones, from, point(4.5, 0, -4.5, 180));
    expect(stopped.lng).toBeLessThan(point(4.1, 0).lng);
    expect(stopped.heading).toBe(180);
    const back = constrainNativeParkWalk(zones, stopped, point(3, 0, -4.5, 180));
    expect(back.lng).toBeLessThan(stopped.lng);
    expect(back.groundHeight).toBeCloseTo(1098.5);
  });
  it('moves a click inside the pool onto a valid dry surface', () => {
    const { zones, point } = fixture();
    const clicked = point(7, 2, -4.5);
    const recovered = nativeParkWalkEntry(zones, clicked);
    expect(recovered).not.toEqual(clicked);
    expect(recovered.groundHeight).toBeCloseTo(1098.5);
  });
  it('does not enable navigation when the exact model is unavailable', () => {
    const { zones, point } = fixture();
    vi.mocked(verifiedScene).mockImplementation(() => { throw new Error('asset unavailable'); });
    expect(nativeParkWalkEntrance(zones, point(0, 0))).toBeNull();
    expect(nativeParkWalkEntry(zones, point(0, 0))).toEqual(point(0, 0));
  });
  it.each(Object.entries(STEP_FREE_PARK_LIFTS))('opens a reversible lift and walkable bridge in %s', (variant, plan) => {
    const {zones,point,layout}=fixture(37,variant);
    const network=stepFreeParkWalkingNetwork(variant,layout.walking!);
    expect(network.version).toBe(2);
    expect(parkWalkHeight(network,plan.x,(plan.bridgeStartY+plan.bridgeEndY)/2,plan.bridgeZ)).toBeCloseTo(plan.bridgeZ);
    const lower=point(plan.x,plan.y,plan.lowerZ);
    const levelWalk=constrainNativeParkWalk(zones,lower,point(plan.x,plan.y+.07,plan.lowerZ));
    expect(levelWalk.groundHeight).toBeCloseTo(lower.groundHeight);
    const upward=nativeParkLiftDestination(zones,lower);
    expect(upward?.pose.groundHeight).toBeCloseTo(1103+plan.upperZ);
    expect(nativeParkLiftDestination(zones,upward!.pose)?.pose.groundHeight).toBeCloseTo(lower.groundHeight);
    const cabinEdgeY=plan.y+Math.min(.9,(plan.cabinDepthM??2.6)/2-.15);
    expect(parkWalkHeight(network,plan.x,cabinEdgeY,plan.upperZ)).toBeCloseTo(plan.upperZ);
    expect(parkWalkHeight(network,plan.x,cabinEdgeY,plan.lowerZ)).toBeCloseTo(plan.lowerZ);
    const edge=point(plan.x,cabinEdgeY,plan.lowerZ);
    const edgeUpper=nativeParkLiftDestination(zones,edge)?.pose;
    expect(edgeUpper).toBeTruthy();
    expect(authoredCameraGround(zones,edge.lng,edge.lat,edgeUpper!.groundHeight)).toBeCloseTo(edgeUpper!.groundHeight);
    expect(nativeParkLiftDestination(zones,point(plan.x+4,plan.y,plan.lowerZ))).toBeNull();
    const next=constrainNativeParkWalk(zones,upward!.pose,point(plan.x,plan.y+.07,plan.upperZ));
    expect(next.groundHeight).toBeCloseTo(1103+plan.upperZ);
    expect(next.lat).toBeGreaterThan(upward!.pose.lat);
    let walker:WalkPoint=[plan.x,plan.bridgeStartY+.12,plan.bridgeZ];
    for(let i=0;i<Math.ceil((plan.bridgeEndY-plan.bridgeStartY-.2)/.35);i++)
      walker=advanceParkWalk(network,walker,[plan.x,Math.min(plan.bridgeEndY-.12,walker[1]+.35)]);
    expect(walker[1]).toBeGreaterThan(plan.bridgeEndY-.65);
    expect(walker[2]).toBeCloseTo(plan.bridgeZ);
    if(plan.connectX!==undefined){
      for(let i=0;i<30;i++)walker=advanceParkWalk(network,walker,[Math.min(plan.connectX,walker[0]+.3),plan.bridgeEndY]);
      expect(walker[0]).toBeGreaterThan(plan.connectX-.5);
    }
  });
});
