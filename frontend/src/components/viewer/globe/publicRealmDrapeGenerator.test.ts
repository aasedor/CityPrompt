import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';

const {
  generateParkGroundTextureMock,
  getParkGroundMetaMock,
  generateStreetNetworkGroundTextureMock,
  getCurrentStreetNetworkGroundMetaMock,
  listZonesMock,
} = vi.hoisted(() => ({
  generateParkGroundTextureMock: vi.fn(),
  getParkGroundMetaMock: vi.fn(),
  generateStreetNetworkGroundTextureMock: vi.fn(),
  getCurrentStreetNetworkGroundMetaMock: vi.fn(),
  listZonesMock: vi.fn(),
}));

vi.mock('./parkGroundTexture', () => ({
  generateParkGroundTexture: generateParkGroundTextureMock,
  getParkGroundMeta: getParkGroundMetaMock,
  MAX_PARK_GROUND_BATCH_CALLS: 6,
}));

vi.mock('./streetNetworkGroundTexture', () => ({
  generateStreetNetworkGroundTexture: generateStreetNetworkGroundTextureMock,
  getCurrentStreetNetworkGroundMeta: getCurrentStreetNetworkGroundMetaMock,
}));

vi.mock('@/services/api', () => ({
  siteZonesApi: { list: listZonesMock },
}));

import { generatePublicRealmDrapes, planPublicRealmDrapes } from './publicRealmDrapeGenerator';

function zone(
  id: string,
  zoneType: SiteZone['zone_type'],
  role?: string,
): SiteZone {
  return {
    id,
    project_id: '11111111-1111-4111-8111-111111111111',
    zone_type: zoneType,
    name: role,
    coordinates: [
      [-114.1, 51.0],
      [-114.09, 51.0],
      [-114.09, 51.01],
      [-114.1, 51.01],
    ],
    color: '#fff',
    properties: role ? { _plan_role: role } : {},
    sort_order: 0,
    created_at: '2026-08-04T00:00:00Z',
    updated_at: '2026-08-04T00:00:00Z',
  };
}

const PARK_ID = '22222222-2222-4222-8222-222222222222';
const STREET_ID = '33333333-3333-4333-8333-333333333333';

describe('publicRealmDrapeGenerator', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    getParkGroundMetaMock.mockReturnValue(null);
    getCurrentStreetNetworkGroundMetaMock.mockReturnValue(null);
    generateParkGroundTextureMock.mockResolvedValue({ document_id: 'park-doc' });
    generateStreetNetworkGroundTextureMock.mockResolvedValue({ document_id: 'street-doc' });
  });

  it('plans one image call per stale park and one for the complete street network', () => {
    const zones = [
      zone(PARK_ID, 'green_space', 'open_space'),
      zone(STREET_ID, 'road', 'street'),
    ];
    expect(planPublicRealmDrapes(zones)).toEqual(expect.objectContaining({
      parksNeedingDrape: [zones[0]],
      streetZones: [zones[1]],
      streetNetworkNeedsDrape: true,
      totalImageCalls: 2,
    }));
  });

  it('does not spend an image call on the archetype-owned Skate Park v0 kit', () => {
    const skate = zone(PARK_ID, 'green_space', 'open_space');
    skate.properties = {
      green_space_archetype_id: 'skate_park',
      green_space_selected_variant_id: 'skate_park_v0',
    };

    expect(planPublicRealmDrapes([skate])).toEqual(expect.objectContaining({
      parkZones: [skate],
      parksNeedingDrape: [],
      totalImageCalls: 0,
    }));
  });

  it('saves the street atlas and park drape before returning refreshed compile revisions', async () => {
    const zones = [
      zone(PARK_ID, 'green_space', 'open_space'),
      zone(STREET_ID, 'road', 'street'),
    ];
    const refreshed = zones.map((item, index) => ({
      ...item,
      updated_at: `2026-08-04T01:00:0${index + 1}Z`,
    }));
    listZonesMock.mockResolvedValue(refreshed);
    const progress: string[] = [];

    const result = await generatePublicRealmDrapes(zones[0].project_id, zones, {
      sceneContextImageBase64: 'google-tiles-frame',
      onProgress: (value) => progress.push(`${value.label}:${value.completed}/${value.total}`),
    });

    expect(generateStreetNetworkGroundTextureMock).toHaveBeenCalledWith(
      zones[0].project_id,
      zones,
      { sceneContextImageBase64: 'google-tiles-frame' },
    );
    expect(generateParkGroundTextureMock).toHaveBeenCalledWith(zones[0], {
      siteZones: zones,
      sceneContextImageBase64: 'google-tiles-frame',
    });
    expect(generateStreetNetworkGroundTextureMock.mock.invocationCallOrder[0])
      .toBeLessThan(generateParkGroundTextureMock.mock.invocationCallOrder[0]);
    expect(result).toEqual({
      zones: refreshed,
      generatedParks: 1,
      generatedStreetNetwork: true,
      remainingParks: 0,
      imageCalls: 2,
    });
    expect(progress[progress.length - 1]).toBe('open_space drape saved:2/2');
  });

  it('reuses current drapes on retry without another image call or revision fetch', async () => {
    const zones = [
      zone(PARK_ID, 'green_space', 'open_space'),
      zone(STREET_ID, 'road', 'street'),
    ];
    getParkGroundMetaMock.mockReturnValue({ document_id: 'current-park' });
    getCurrentStreetNetworkGroundMetaMock.mockReturnValue({ document_id: 'current-street' });

    const result = await generatePublicRealmDrapes(zones[0].project_id, zones);

    expect(result.imageCalls).toBe(0);
    expect(result.zones).toBe(zones);
    expect(generateParkGroundTextureMock).not.toHaveBeenCalled();
    expect(generateStreetNetworkGroundTextureMock).not.toHaveBeenCalled();
    expect(listZonesMock).not.toHaveBeenCalled();
  });
});
