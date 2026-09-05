import { describe, expect, it, vi } from 'vitest';
import type { Building, SiteZone } from '@/types';
import type { Direct3DInstanceDescriptor } from './globe/direct3dCapture';
import { captureCompleteVideoFrame, type VideoCaptureScene } from './videoCaptureInventory';

function fixture() {
  const compiledAt = '2026-09-04T12:00:00Z';
  const zones: SiteZone[] = ['building', 'building', 'building', 'green_space', 'road'].map((type, index) => ({
    id: `zone-${index}`, project_id: 'project', zone_type: type as SiteZone['zone_type'],
    coordinates: [[-114, 51], [-113.999, 51], [-113.999, 51.001]],
    color: '#ffffff', sort_order: index, created_at: compiledAt, updated_at: compiledAt,
    ...(type === 'building' ? { building_id: `building-${index}` } : {}),
    properties: { community_3d: { schema_version: 1, state: 'compiled',
      kind: type === 'building' ? 'building' : type === 'road' ? 'street' : 'park',
      generator: type === 'building' ? 'planned_massing' : type === 'road' ? 'street_section' : 'park_kit',
      compiled_at: compiledAt, source_hash: 'a'.repeat(64), representation_hash: 'b'.repeat(64) } },
  }));
  const buildings: Building[] = zones.slice(0, 3).map((zone) => ({
    id: zone.building_id!, project_id: 'project', footprint_coordinates: zone.coordinates, created_at: compiledAt,
    specifications: { plannedMassing: {}, community3DRepresentation: { schema_version: 1, zone_id: zone.id,
      generator: 'planned_massing', representation_hash: 'b'.repeat(64), compiled_at: compiledAt } },
  }));
  const manifest = Object.fromEntries(zones.map((zone, index) => [`#00000${index + 1}`, {
    instance_id: `instance-${index}`, zone_id: zone.id,
    semantic_class: index < 3 ? 'building' : index === 3 ? 'park' : 'street',
    ...(zone.building_id ? { building_id: zone.building_id } : {}),
  }])) as Record<string, Direct3DInstanceDescriptor>;
  return { scene: { projectId: 'project', zones, buildings } satisfies VideoCaptureScene,
    capture: { beautyImageBase64: 'complete-image', instanceIdManifest: manifest } };
}

describe('initial video scene completeness', () => {
  it('rejects hidden buildings in a currently compiled plan before releasing the Single frame image', async () => {
    const { scene, capture } = fixture();
    capture.instanceIdManifest = Object.fromEntries(Object.entries(capture.instanceIdManifest).filter(([, instance]) => instance.semantic_class !== 'building'));
    const take = vi.fn().mockResolvedValue(capture);
    await expect(captureCompleteVideoFrame(take, () => scene)).rejects.toThrow('Turn on 3D models and wait');
    expect(take).toHaveBeenCalledOnce();
  });
  it('allows fully occluded or off-camera buildings with zero visible building pixels', async () => {
    const { scene, capture } = fixture();
    const naturallyOccluded = { ...capture, classCoverage: { building: 0, park: .1, street: .1 } };
    await expect(captureCompleteVideoFrame(async () => naturallyOccluded, () => scene)).resolves.toBe('complete-image');
    expect(naturallyOccluded.classCoverage.building).toBe(0);
  });
  it('rejects a context or wrong model identity standing in for the authored building', async () => {
    const { scene, capture } = fixture();
    capture.instanceIdManifest['#000001'].building_id = 'old-model';
    await expect(captureCompleteVideoFrame(async () => capture, () => scene)).rejects.toThrow('Turn on 3D models and wait');
  });
  it('rejects an asynchronous scene change even if its next revision is compiled', async () => {
    const { scene, capture } = fixture();
    let current = scene;
    await expect(captureCompleteVideoFrame(async () => {
      current = { ...scene, zones: scene.zones.map((zone) => ({ ...zone, updated_at: '2026-09-04T12:01:00Z' })) };
      return capture;
    }, () => current)).rejects.toThrow('plan changed');
  });
  it('rejects a stale plan before any capture work', async () => {
    const { scene, capture } = fixture();
    scene.zones[0].properties = {};
    const take = vi.fn().mockResolvedValue(capture);
    await expect(captureCompleteVideoFrame(take, () => scene)).rejects.toThrow('Generate to 3D');
    expect(take).not.toHaveBeenCalled();
  });
});
