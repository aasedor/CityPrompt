import { act, fireEvent, render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { Matrix4 } from 'three';
import { GlobeStreetDrawingPreview } from './GlobeStreetDrawingPreview';
import { STREET_ASSETS } from './assetRegistry';
import type { SiteZone } from '@/types';

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

describe('street drawing preview lifecycle', () => {
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
