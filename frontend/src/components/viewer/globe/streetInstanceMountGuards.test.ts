import { describe, expect, it, vi } from 'vitest';

vi.mock('@react-three/drei', () => ({ useTexture: vi.fn() }));
vi.mock('@react-three/fiber', () => ({ useThree: vi.fn() }));

import { GlobeLandscapeTreeStand } from './GlobeLandscapeKit';
import { GlobeStreetTransitShelterInstances } from './GlobeStreetTransitShelterInstances';
import { GlobeStreetVehicleInstances } from './GlobeStreetVehicleInstances';

describe('empty street instance mount guards', () => {
  it('keeps resource-owning tree, vehicle and shelter subtrees unmounted', () => {
    expect(GlobeLandscapeTreeStand({ placements: [] })).toBeNull();
    expect(GlobeStreetVehicleInstances({ placements: [] })).toBeNull();
    expect(GlobeStreetTransitShelterInstances({ placements: [] })).toBeNull();
  });
});
