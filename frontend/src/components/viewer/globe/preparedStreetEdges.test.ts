import { expect, it } from 'vitest';
import * as THREE from 'three';
import { createPreparedStreetEdges } from './preparedStreetEdges';

const points = [{x:0,y:0},{x:10,y:0}];
const level = (z: number) => ({centerZ:z,leftZ:z,rightZ:z,halfWidthM:8});

it('closes measured cut and fill sides and the outside end, including grade crossings', () => {
  const geometry = createPreparedStreetEdges(points,[level(2),level(-1)],[level(0),level(0)],-7,7)!;
  geometry.computeBoundingBox();
  expect(geometry.boundingBox!.min.toArray()).toEqual([0,-7,expect.closeTo(-1.08,5)]);
  expect(geometry.boundingBox!.max.toArray()).toEqual([10,7,2]);
  const material=new THREE.MeshBasicMaterial({side:THREE.DoubleSide}),mesh=new THREE.Mesh(geometry,material);
  const hit=(x:number,y:number,z:number,dx:number,dy:number)=>new THREE.Raycaster(new THREE.Vector3(x,y,z),
    new THREE.Vector3(dx,dy,0),0,2).intersectObject(mesh).length;
  expect(hit(1,-8,1,0,1)).toBeGreaterThan(0); // Fill face.
  expect(hit(9,8,-.5,0,-1)).toBeGreaterThan(0); // Cut face.
  expect(hit(11,0,-.5,-1,0)).toBeGreaterThan(0); // End cap.
  expect(hit(1,-8,3,0,1)).toBe(0); // No invented wall above either surface.
  geometry.dispose();material.dispose();
});

it('does not invent walls for matching surfaces or incomplete measurements', () => {
  expect(createPreparedStreetEdges(points,[level(0),level(0)],[level(0),level(0)],-8,8)).toBeNull();
  expect(createPreparedStreetEdges(points,[level(2),level(2)],[level(0)],-8,8)).toBeNull();
  expect(createPreparedStreetEdges(points,[level(2),level(2)],[level(0),level(NaN)],-8,8)).toBeNull();
});
