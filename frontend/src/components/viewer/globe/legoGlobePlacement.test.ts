import { describe, expect, it } from 'vitest';
import type { Building } from '@/types';
import type { LegoAssemblyInstance, LegoAssemblyRecipe } from '@/features/legoAssembly/legoAssemblyApi';
import {
  computeLegoStackYaw,
  excludeLegoStackBuildings,
  extractLegoRecipe,
  hasLegoRecipe,
  legoFootprintRing,
  legoInstanceTransform,
  recipeIsRenderable,
  uniqueModuleUrls,
} from './legoGlobePlacement';

const CALGARY_RING = [
  [-114.0851, 51.0404],
  [-114.0849, 51.0404],
  [-114.0849, 51.0406],
  [-114.0851, 51.0406],
];

function makeInstance(overrides: Partial<LegoAssemblyInstance> = {}): LegoAssemblyInstance {
  return {
    asset_id: 'mod-podium',
    asset_name: 'Podium',
    model_url: '/api/v1/files/podium.glb',
    family: 'brick_midrise',
    role: 'podium',
    level: 0,
    position: [0, 0, 0],
    rotation_degrees: 0,
    scale: [1, 1, 1],
    native_dimensions_m: [24, 18, 4],
    ...overrides,
  };
}

function makeRecipe(overrides: Partial<LegoAssemblyRecipe> = {}): LegoAssemblyRecipe {
  return {
    schema_version: 1,
    module_family: 'brick_midrise',
    archetype_id: 'brick_midrise_apartments',
    reuse_keys: ['midrise'],
    target: { width_m: 24, depth_m: 18, floors: 2 },
    instances: [
      makeInstance(),
      makeInstance({
        asset_id: 'mod-floor',
        asset_name: 'Floor',
        model_url: '/api/v1/files/floor.glb',
        role: 'floor',
        level: 1,
        position: [0.5, -0.25, 4],
        rotation_degrees: 90,
        scale: [1.1, 0.9, 1],
        native_dimensions_m: [24, 18, 3.2],
      }),
    ],
    assembled_height_m: 7.2,
    fit: { scale_x: 1.1, scale_y: 0.9, score: 0.95 },
    ...overrides,
  };
}

function makeBuilding(overrides: Partial<Building> = {}): Building {
  return {
    id: 'bldg-1',
    project_id: 'proj-1',
    created_at: '2026-07-14T00:00:00Z',
    ...overrides,
  };
}

function buildingWithRecipe(
  recipe: unknown = makeRecipe(),
  overrides: Partial<Building> = {},
): Building {
  return makeBuilding({
    footprint_coordinates: CALGARY_RING,
    specifications: { legoAssembly: recipe },
    ...overrides,
  });
}

describe('extractLegoRecipe', () => {
  it('accepts a complete v1 recipe (snake_case version key)', () => {
    const recipe = makeRecipe();
    expect(extractLegoRecipe(buildingWithRecipe(recipe))).toEqual(recipe);
  });

  it('accepts the camelCase schemaVersion spelling', () => {
    const recipe = makeRecipe();
    const camel: Record<string, unknown> = { ...recipe, schemaVersion: 1 };
    delete camel.schema_version;
    expect(extractLegoRecipe(buildingWithRecipe(camel))).not.toBeNull();
  });

  it('rejects missing specifications, wrong versions, and non-objects', () => {
    expect(extractLegoRecipe(makeBuilding())).toBeNull();
    expect(extractLegoRecipe(buildingWithRecipe('not-an-object'))).toBeNull();
    expect(extractLegoRecipe(buildingWithRecipe(makeRecipe({ schema_version: 2 as unknown as 1 })))).toBeNull();
  });

  it('rejects empty or malformed instance lists', () => {
    expect(extractLegoRecipe(buildingWithRecipe(makeRecipe({ instances: [] })))).toBeNull();
    expect(extractLegoRecipe(buildingWithRecipe(makeRecipe({
      instances: [makeInstance({ position: [0, 0] as unknown as [number, number, number] })],
    })))).toBeNull();
    expect(extractLegoRecipe(buildingWithRecipe(makeRecipe({
      instances: [makeInstance({ model_url: '' })],
    })))).toBeNull();
    expect(extractLegoRecipe(buildingWithRecipe(makeRecipe({
      instances: [makeInstance({ scale: [1, Number.NaN, 1] })],
    })))).toBeNull();
  });

  it('rejects a recipe without positive target dimensions', () => {
    expect(extractLegoRecipe(buildingWithRecipe(makeRecipe({
      target: undefined as unknown as LegoAssemblyRecipe['target'],
    })))).toBeNull();
    expect(extractLegoRecipe(buildingWithRecipe(makeRecipe({
      target: { width_m: 0, depth_m: 18, floors: 2 },
    })))).toBeNull();
  });
});

describe('legoFootprintRing / recipeIsRenderable', () => {
  it('requires at least 3 valid coordinate pairs from footprint_coordinates only', () => {
    expect(legoFootprintRing(makeBuilding())).toBeNull();
    expect(legoFootprintRing(makeBuilding({ footprint_coordinates: CALGARY_RING.slice(0, 2) }))).toBeNull();
    expect(legoFootprintRing(makeBuilding({ footprint_coordinates: CALGARY_RING }))).toEqual(CALGARY_RING);
  });

  it('renderable = valid recipe AND footprint ring', () => {
    expect(recipeIsRenderable(buildingWithRecipe())).toBe(true);
    // Recipe but no footprint — skipped by the layer, keeps its Meshy model.
    expect(recipeIsRenderable(buildingWithRecipe(makeRecipe(), { footprint_coordinates: undefined }))).toBe(false);
    // Footprint but no recipe.
    expect(recipeIsRenderable(makeBuilding({ footprint_coordinates: CALGARY_RING }))).toBe(false);
  });
});

describe('excludeLegoStackBuildings (Meshy-layer suppression filter)', () => {
  it('removes exactly the buildings that render as LEGO stacks', () => {
    const meshyOnly = makeBuilding({ id: 'meshy', model_url: '/api/m.glb', footprint_coordinates: CALGARY_RING });
    const both = buildingWithRecipe(makeRecipe(), { id: 'both', model_url: '/api/m.glb' });
    const legoOnly = buildingWithRecipe(makeRecipe(), { id: 'lego' });
    const recipeNoFootprint = buildingWithRecipe(makeRecipe(), {
      id: 'no-ring',
      model_url: '/api/m.glb',
      footprint_coordinates: undefined,
    });

    const kept = excludeLegoStackBuildings([meshyOnly, both, legoOnly, recipeNoFootprint]);
    expect(kept.map((b) => b.id)).toEqual(['meshy', 'no-ring']);
    expect(hasLegoRecipe(recipeNoFootprint)).toBe(true); // still counted as a recipe holder
  });
});

describe('legoInstanceTransform', () => {
  it('swizzles backend Z-up into three.js Y-up like legoShared.ModuleInstance', () => {
    const t = legoInstanceTransform(makeInstance({
      position: [1, 2, 3], // backend: x=1 east-ish, y=2 depth, z=3 up
      scale: [1.1, 0.9, 1],
      rotation_degrees: 90,
    }));
    expect(t.position).toEqual([1, 3, 2]); // up (3) lands on three Y
    expect(t.scale).toEqual([1.1, 1, 0.9]); // depth scale (0.9) lands on three Z
    expect(t.rotationYRad).toBeCloseTo(-Math.PI / 2, 6);
  });

  it('stacks levels along three.js Y for a 2-instance recipe', () => {
    const recipe = makeRecipe();
    const [podium, floor] = recipe.instances.map(legoInstanceTransform);
    expect(podium.position).toEqual([0, 0, 0]);
    // Floor planned at backend z=4 (4 m up) -> three Y = 4, above the podium.
    expect(floor.position).toEqual([0.5, 4, -0.25]);
    expect(floor.position[1]).toBeGreaterThan(podium.position[1]);
    // Planner fit scales applied verbatim: [sx, sy(depth), 1] -> [sx, 1, sy].
    expect(floor.scale).toEqual([1.1, 1, 0.9]);
  });

  it('defaults missing rotation to 0', () => {
    const instance = makeInstance();
    delete (instance as Partial<LegoAssemblyInstance>).rotation_degrees;
    // toBeCloseTo: the negation yields -0 for zero input (same as
    // legoShared.ModuleInstance), which is fine at runtime but not Object.is(0).
    expect(legoInstanceTransform(instance).rotationYRad).toBeCloseTo(0, 10);
  });
});

describe('computeLegoStackYaw', () => {
  const bearing = Math.PI / 6; // 30° footprint long axis

  it('keeps the bearing when the stack is wider than deep (long axis on X)', () => {
    expect(computeLegoStackYaw(bearing, { width_m: 24, depth_m: 18 }, 0)).toBeCloseTo(bearing, 6);
  });

  it('adds +90° when the stack is deeper than wide (long axis on Z)', () => {
    expect(computeLegoStackYaw(bearing, { width_m: 18, depth_m: 24 }, 0))
      .toBeCloseTo(bearing + Math.PI / 2, 6);
  });

  it('applies building rotation_degrees as additional CCW yaw', () => {
    const base = computeLegoStackYaw(bearing, { width_m: 24, depth_m: 18 }, 0);
    expect(computeLegoStackYaw(bearing, { width_m: 24, depth_m: 18 }, 90))
      .toBeCloseTo(base + Math.PI / 2, 6);
    expect(computeLegoStackYaw(bearing, { width_m: 24, depth_m: 18 }, null)).toBeCloseTo(base, 6);
  });
});

describe('uniqueModuleUrls', () => {
  it('dedupes repeated floor modules', () => {
    const floor = makeInstance({ model_url: '/api/v1/files/floor.glb', role: 'floor' });
    const recipe = makeRecipe({
      instances: [makeInstance(), floor, { ...floor, level: 2 }, { ...floor, level: 3 }],
    });
    expect(uniqueModuleUrls(recipe)).toEqual([
      '/api/v1/files/podium.glb',
      '/api/v1/files/floor.glb',
    ]);
  });
});
