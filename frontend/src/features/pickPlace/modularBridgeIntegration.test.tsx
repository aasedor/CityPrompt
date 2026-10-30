import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { afterAll, expect, it, vi } from 'vitest';

vi.stubEnv('DEV', true); vi.stubEnv('MODE', 'development');
const { PlacementPalette } = await import('./PlacementPalette');
const { CLASSROOM_CHOICES } = await import('./canonicalCatalogue');
const { CATALOGUE_ASSETS } = await import('./assetRegistry');
const { nativeStreetPilot, nativeStreetLocalRouteProblem, placeNativeStreetModules } = await import('@/components/viewer/globe/nativeStreetPilot');
const { buildNativeStreetProgram } = await import('@/components/viewer/globe/nativeStreetProgram');
const { nativeStreetMaxLength } = await import('@/components/viewer/globe/streetRoutePolicy');
const { isSpecialistStreet } = await import('@/components/viewer/globe/specialistStreetProgram');
const { authoredCameraGround } = await import('@/components/viewer/globe/authoredCameraGround');
const { rectangleAt } = await import('./geometry');
const { bufferLineToPolygon } = await import('@/utils/roadGeometry');
const { detectConnectedStreetIntersections } = await import('@/components/viewer/globe/streetGraphIntersections');
import type { SiteZone } from '@/types';
afterAll(() => vi.unstubAllEnvs());
const id = 'timber_covered_bridge_route_v1';

it('replaces the fixed timber discovery card with an actual route while keeping saved fixed assets', () => {
  const pick = vi.fn(), draw = vi.fn();
  const choice = CLASSROOM_CHOICES.find(c => c.placements.some(a => a.id === id));
  expect(choice).toBeDefined();
  const asset = choice!.placements[0];
  expect(asset.kind).toBe('street'); expect(asset.properties.lane_count).toBe(0);
  expect(CLASSROOM_CHOICES.some(c => c.placements.some(a => a.id.startsWith('claude_public_realm:timber-covered-footbridge:')))).toBe(false);
  expect(CATALOGUE_ASSETS.find(a => a.id.startsWith('claude_public_realm:timber-covered-footbridge:'))?.kind).toBe('object');
  render(<PlacementPalette selected={null} onPick={pick} onPickStreet={draw} onPickCanonical={vi.fn()}
    onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Streets' }));
  fireEvent.click(screen.getByRole('button', { name: 'Browse Bridges & viaducts' }));
  fireEvent.click(screen.getByRole('button', { name: `Expand details for ${asset.label}` }));
  const card = screen.getByLabelText(`Variant for ${asset.label}`).closest('article')!;
  fireEvent.click(within(card).getByRole('button', { name: 'Choose & draw route' }));
  expect(draw).toHaveBeenCalledExactlyOnceWith(asset); expect(pick).not.toHaveBeenCalled();
});

it('routes, bounds, renders and classifies the new pilot as an elevated bridge, with no grass rectangle', () => {
  const pilot = nativeStreetPilot(id);
  expect(pilot).toBeDefined();
  const route = [{ x: 0, y: 0 }, { x: 0, y: 80 }];
  expect(nativeStreetLocalRouteProblem(pilot!, route)).toBeNull();
  expect(nativeStreetMaxLength(id)).toBe(240);
  expect(nativeStreetLocalRouteProblem(pilot!, [{x:0,y:0},{x:0,y:241}])).toBeTruthy();
  expect(nativeStreetLocalRouteProblem(pilot!, [{x:0,y:0},{x:10,y:40},{x:0,y:80}])).toBeTruthy();
  const poses = placeNativeStreetModules(pilot!, route);
  expect(poses.length).toBeGreaterThan(10);
  expect(poses[0].kind).toBe('bridge_left_stair');
  expect(poses[poses.length - 1].kind).toBe('bridge_right_stair');
  expect(buildNativeStreetProgram(pilot!.program!, 6, pilot!.fixtureLengthM, route)).toEqual([]);
  expect(isSpecialistStreet(id)).toBe(true);
});

it('walks the actual bridge stairs and deck, keeps the ground under it and creates no at-grade crossing', () => {
  const boundary = { id:'site', project_id:'test', zone_type:'site_boundary', is_active_boundary:true,
    coordinates:rectangleAt([-114,51],300,300), properties:{terrain_elevation_m:1103,community_3d_mask_existing_tiles:true},
    color:'#aaa',sort_order:0,created_at:'now',updated_at:'now' } as SiteZone;
  const line = [[-114,51-40/111320],[-114,51+40/111320]];
  const bridge = { ...boundary, id:'bridge',zone_type:'road',is_active_boundary:false,
    coordinates:bufferLineToPolygon(line,6), properties:{width:6,lane_count:0,
      road_archetype_id:'urban_pedestrian_footbridge',road_selected_variant_id:id,plan_centerline:line,
      pick_place_street_section:id,junction_preview_candidate:true} } as SiteZone;
  expect(authoredCameraGround([boundary,bridge],-114,51,1103)).toBe(1103);
  expect(authoredCameraGround([boundary,bridge],-114,51,1103,1103)).toBeCloseTo(1106.45);
  expect(authoredCameraGround([boundary,bridge],-114,51-39.99/111320,1103,1103)).toBeCloseTo(1103+3.45/18);
  const roadLine = [[-114-20/(111320*Math.cos(51*Math.PI/180)),51],[-114+20/(111320*Math.cos(51*Math.PI/180)),51]];
  const road = { ...bridge,id:'road',coordinates:bufferLineToPolygon(roadLine,16),
    properties:{width:16,road_archetype_id:'calgary_local',road_selected_variant_id:'calgary_local_v0',
      pick_place_street_section:'calgary_local_v0',plan_centerline:roadLine,junction_preview_candidate:true} } as SiteZone;
  expect(detectConnectedStreetIntersections([bridge,road],true)).toEqual([]);
});
