import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { prepareReviewBuildingGlass } from './reviewBuildingGlass';

describe('local exact-GLB review glass', () => {
  it('replaces only the common fully transmissive glass on an owned clone', () => {
    const glass = new THREE.MeshPhysicalMaterial({ name:'CLAY_GLASS', color:'#94b0b3',
      roughness:.06, transmission:1, side:THREE.DoubleSide });
    const brick = new THREE.MeshStandardMaterial({ name:'SOURCE_BRICK', color:'#ad5d49' });
    const source = new THREE.Group();
    source.add(new THREE.Mesh(new THREE.BoxGeometry(2,2,.02), glass));
    source.add(new THREE.Mesh(new THREE.BoxGeometry(1,1,1), brick));
    const result = prepareReviewBuildingGlass(source);
    const pane = (result.clone.children[0] as THREE.Mesh).material as THREE.MeshPhysicalMaterial;
    expect(pane).not.toBe(glass);
    expect(pane.transmission).toBe(0);
    expect(pane.opacity).toBeGreaterThan(0);
    expect(pane.opacity).toBeLessThan(1);
    expect(pane.transparent).toBe(true);
    expect(pane.depthWrite).toBe(false);
    expect(pane.forceSinglePass).toBe(true);
    expect(pane.side).toBe(THREE.DoubleSide);
    expect(pane.color.equals(glass.color)).toBe(true);
    expect((result.clone.children[0] as THREE.Mesh).geometry).toBe((source.children[0] as THREE.Mesh).geometry);
    expect((result.clone.children[1] as THREE.Mesh).material).toBe(brick);
    expect(glass.transmission).toBe(1);
    expect(glass.transparent).toBe(false);
    expect(result.ownedMaterials).toEqual([pane]);
  });
  it('shares one owned replacement across the original glass material and leaves other glass alone', () => {
    const common = new THREE.MeshPhysicalMaterial({name:'CLAY_GLASS',transmission:1});
    const other = new THREE.MeshPhysicalMaterial({name:'heritage_sash',transmission:.4});
    const source = new THREE.Group();
    source.add(new THREE.Mesh(new THREE.BoxGeometry(1,1,1), [common,other]));
    source.add(new THREE.Mesh(new THREE.BoxGeometry(1,1,1), common));
    const result = prepareReviewBuildingGlass(source);
    const materials = (result.clone.children[0] as THREE.Mesh).material as THREE.Material[];
    expect(materials[0]).toBe((result.clone.children[1] as THREE.Mesh).material);
    expect(materials[1]).toBe(other);
    expect(result.ownedMaterials).toHaveLength(1);
  });
});
