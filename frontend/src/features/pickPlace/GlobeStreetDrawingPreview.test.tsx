import { act, cleanup, fireEvent, render } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { Matrix4 } from 'three';
import { GlobeStreetDrawingPreview } from './GlobeStreetDrawingPreview';
import { STREET_ASSETS } from './assetRegistry';
import type { SiteZone } from '@/types';
import { nativeStreetPilot } from '@/components/viewer/globe/nativeStreetPilot';

const harness = vi.hoisted(() => ({ frame: null as null | ((state: { clock: { elapsedTime: number } }) => void),
  canvas: null as HTMLCanvasElement | null, zone: null as SiteZone | null, camera: null as unknown }));
vi.mock('./PublicRoadSuggestionMarker', () => ({ PublicRoadSuggestionMarker: () => <div data-testid="public-road-suggestion" /> }));
vi.mock('@react-three/fiber', () => ({
  useThree: () => ({ gl: { domElement: harness.canvas }, camera: harness.camera, invalidate: () => {} }),
  useFrame: (callback: typeof harness.frame) => { harness.frame = callback; },
}));
vi.mock('@/components/viewer/globe/GlobeStreetDetailLayer', () => ({
  GlobeStreetDraft: ({ zone }: { zone: SiteZone }) => { harness.zone = zone; return <div data-testid="street-model" />; },
}));
const points = [[-114, 51], [-113.998, 51]];
afterEach(cleanup);

describe('street drawing preview lifecycle', () => {
  it.each(['brt_bus_rapid_transit_corridor_v0', 'amsterdam_gracht_v1', 'landmark_signature_bridge_v2',
    'student_elevated_garden_rail_v1', 'skytrain_elevated_corridor_v0', 'elevated_rail_transit_corridor_v0',
    'student_grass_tram_avenue_v1', 'student_planted_shared_lane_v1'])
  ('keeps an unfinished %s route editable and restores 3D at valid sizes', variant => {
    harness.canvas = document.createElement('canvas');
    harness.camera = { matrixWorld: new Matrix4() };
    const pilot = nativeStreetPilot(variant)!;
    const line = (length: number) => [[-114, 51], [-114, 51 + length / 111320]];
    const boundary = { id: 'site', zone_type: 'site_boundary', coordinates: [[-115, 50], [-113, 50], [-113, 52], [-115, 52]],
      properties: { terrain_strategy: 'level', community_3d_mask_existing_tiles: true } } as unknown as SiteZone;
    const onStatusChange = vi.fn();
    const props = { points: line(10), pointHeights: [1000], zones: [boundary], terrainHeight: 1000,
      raycastSurface: () => null, skipSnapping: true, onStatusChange,
      properties: { width: pilot.widthM, road_archetype_id: pilot.sourceArchetypeId, road_selected_variant_id: variant } };
    const { rerender, queryByTestId, unmount } = render(<GlobeStreetDrawingPreview {...props} />);
    expect(queryByTestId('street-model')).toBeNull();
    expect(onStatusChange.mock.lastCall?.[0]).toBeTruthy();
    rerender(<GlobeStreetDrawingPreview {...props} points={line(pilot.program!.minLengthM + 1)} />);
    expect(queryByTestId('street-model')).not.toBeNull();
    expect(onStatusChange).toHaveBeenLastCalledWith(null);
    rerender(<GlobeStreetDrawingPreview {...props} points={line(pilot.program!.maxLengthM + 10)} />);
    expect(queryByTestId('street-model')).toBeNull();
    expect(onStatusChange.mock.lastCall?.[0]).toBeTruthy();
    rerender(<GlobeStreetDrawingPreview {...props} points={line(pilot.program!.minLengthM + 1)} />);
    expect(queryByTestId('street-model')).not.toBeNull();
    unmount();
    expect(onStatusChange).toHaveBeenLastCalledWith(null);
  });

  it('shows the mapped-road suggestion and removes it when snapping is bypassed', () => {
    harness.canvas = document.createElement('canvas');
    harness.camera = { matrixWorld: new Matrix4() };
    const sx = 111320 * Math.cos(51 * Math.PI / 180);
    const ll = (x: number, y: number) => [-114 + x / sx, 51 + y / 111320];
    const boundary = { id: 'parcel', zone_type: 'site_boundary',
      coordinates: [ll(0, 0), ll(200, 0), ll(200, 200), ll(0, 200)] } as SiteZone;
    const props = { points: [ll(0, 80), ll(100, 100)], pointHeights: [1000],
      properties: { width: 20, lane_count: 2, pick_place_street_section: 'test' }, zones: [boundary], terrainHeight: 1000,
      raycastSurface: () => null, publicRoads: { source: 'OpenStreetMap', fetched_at: '2026-09-30', blockers: [],
        roads: [{ id: 'osm:way:1', label: 'Existing Avenue', widthM: 8, points: [ll(-8, 0), ll(-8, 200)] }] } };
    const { rerender, queryByTestId } = render(<GlobeStreetDrawingPreview {...props} />);
    expect(queryByTestId('public-road-suggestion')).not.toBeNull();
    expect(harness.zone?.properties?.connect_to_public_road).toBe(true);
    rerender(<GlobeStreetDrawingPreview {...props} skipSnapping />);
    expect(queryByTestId('public-road-suggestion')).toBeNull();
    expect(harness.zone?.properties?.connect_to_public_road).toBeUndefined();
    expect(harness.zone?.properties?.plan_route_controls).toEqual(props.points);
  });

  it('extends to the pointer, handles undo/cancel, and never needs a saved recipe', () => {
    harness.canvas = document.createElement('canvas');
    harness.canvas.getBoundingClientRect = () => ({ width: 1000, height: 800, left: 0, top: 0 }) as DOMRect;
    harness.camera = { matrixWorld: new Matrix4() };
    const raycastSurface = vi.fn(() => ({ lngLat: points[1] as [number, number], height: 1000 }));
    const props = { points: [], pointHeights: [1000], properties: STREET_ASSETS[0].properties,
      zones: [], terrainHeight: 1000, raycastSurface };
    const { rerender, queryByTestId } = render(<GlobeStreetDrawingPreview {...props} />);
    expect(queryByTestId('street-model')).toBeNull();
    rerender(<GlobeStreetDrawingPreview {...props} points={[points[0]]} />);
    fireEvent.pointerMove(harness.canvas, { clientX: 800, clientY: 400 });
    act(() => harness.frame!({ clock: { elapsedTime: 1 } }));
    expect(queryByTestId('street-model')).not.toBeNull();
    expect(harness.zone?.properties?.plan_route_controls).toEqual(points);
    expect(harness.zone?.properties?.public_realm_lego).toBeUndefined();
    expect(harness.zone?.properties?.community_3d).toBeUndefined();
    rerender(<GlobeStreetDrawingPreview {...props} points={points} />);
    expect(queryByTestId('street-model')).not.toBeNull();
    // Undo leaves one confirmed point and removes the previous cursor segment.
    rerender(<GlobeStreetDrawingPreview {...props} points={[points[0]]} />);
    expect(queryByTestId('street-model')).toBeNull();
    rerender(<GlobeStreetDrawingPreview {...props} points={[]} />);
    fireEvent.pointerMove(harness.canvas, { clientX: 800, clientY: 400 });
    act(() => harness.frame!({ clock: { elapsedTime: 2 } }));
    expect(queryByTestId('street-model')).toBeNull();
    expect(raycastSurface).toHaveBeenCalledTimes(1);
  });
});
