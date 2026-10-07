import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { cutGeometry, type Cutout } from './terraceGeometry';

describe('prepared ground openings', () => {
  it.each([false, true])('opens both arms of a bent canal, retaining the land in its notch (reversed=%s)', reversed => {
    const source = new THREE.PlaneGeometry(30, 30, 10, 10);
    const positions = source.getAttribute('position');
    for (let i=0;i<positions.count;i++) positions.setZ(i,positions.getX(i)*.1);
    const outline: Cutout = [[-10,-10],[10,-10],[10,10],[6,10],[6,-6],[-10,-6]];
    const geometry = cutGeometry(source, [reversed ? outline.reverse() : outline]);
    const material = new THREE.MeshBasicMaterial({side:THREE.DoubleSide});
    const mesh = new THREE.Mesh(geometry,material);
    const hit = (x:number,y:number) => new THREE.Raycaster(new THREE.Vector3(x,y,20),new THREE.Vector3(0,0,-1)).intersectObject(mesh)[0];
    expect(hit(-7,-8)).toBeUndefined();
    expect(hit(8,7)).toBeUndefined();
    expect(hit(8,-8)).toBeUndefined();
    expect(hit(0,0)?.point.z).toBeCloseTo(0);
    expect(hit(4,3)?.point.z).toBeCloseTo(.4);
    expect(hit(12,12)?.point.z).toBeCloseTo(1.2);
    geometry.dispose(); source.dispose(); material.dispose();
  });
});
