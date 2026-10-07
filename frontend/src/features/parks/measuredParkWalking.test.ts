import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { nativeParkLayouts, type NativeParkLayout } from './nativeParkRegistry';
import { measuredParkWalking } from './measuredParkWalking';
import { advanceParkWalk, parkWalkHeight } from './parkWalking';

describe('verified dry park surfaces', () => {
  it('keeps people on visible paths and excludes the ground beneath a pond', () => {
    const layout = nativeParkLayouts.find(p => p.variantId === 'botanical_garden_v3')!;
    const scene = new THREE.Group();
    const add = (name: string, width: number, depth: number, y: number) => {
      const material = new THREE.MeshStandardMaterial(); material.name = name;
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, .05, depth), material); mesh.position.y = y; scene.add(mesh);
    };
    add('grass', 12, 12, -.025); add('water', 2, 2, -.6);
    const n = measuredParkWalking(layout, scene)!;
    expect(parkWalkHeight(n, 3, 0)).toBeCloseTo(0);
    expect(parkWalkHeight(n, 0, 0)).toBeNull();
    const stop = advanceParkWalk(n, [0, -1.3, 0], [0, -.5]);
    expect(stop[1]).toBeLessThanOrEqual(-1);
    expect(advanceParkWalk(n, stop, [0, -1.5])[1]).toBeLessThan(stop[1]);
    expect(parkWalkHeight(n, 8, 0)).toBeNull();
  });
  it('permits a real boardwalk above water while keeping the adjacent pond blocked', () => {
    const layout = { ...nativeParkLayouts.find(p => p.variantId === 'botanical_garden_v3')!, walkSurfaceMaterials: ['grass', 'timber'] } as NativeParkLayout;
    const scene = new THREE.Group();
    const add = (name: string, width: number, depth: number, top: number) => {
      const material = new THREE.MeshStandardMaterial(); material.name = name;
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, .05, depth), material);
      mesh.position.y = top - .025; scene.add(mesh);
    };
    add('grass', 12, 12, 0); add('water', 4, 4, .03); add('timber', 1.2, 4, .12);
    const n = measuredParkWalking(layout, scene)!;
    expect(parkWalkHeight(n, 0, 0)).toBeCloseTo(.12);
    expect(parkWalkHeight(n, 1.5, 0)).toBeNull();
    expect(advanceParkWalk(n, [0, -1.8, .12], [0, -1])[1]).toBeCloseTo(-1);
  });
});
