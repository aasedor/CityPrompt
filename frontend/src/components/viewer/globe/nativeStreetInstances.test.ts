import { describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import { disposeStreetInstances, instanceStreetModule } from './nativeStreetInstances';
import type { NativeStreetPose } from './nativeStreetPilot';

describe('native street instancing',()=>{
  it('deforms each topology span without altering the verified source or another span length',()=>{
    const source=new THREE.Group(),geometry=new THREE.BoxGeometry(6,8,60),material=new THREE.MeshStandardMaterial();
    source.add(new THREE.Mesh(geometry,material));
    const pose={kind:'bridge',url:'/bridge.glb',sha256:'b'.repeat(64),x:0,y:0,z:0,yaw:0,scale:1,stationM:0,surfaceLiftM:0,
      bridgeDeformation:{mode:'longitudinal-core-v1',nativeLengthM:60,requestedLengthM:80,rigidEndM:10}} satisfies NativeStreetPose;
    const group=instanceStreetModule(source,[pose,{...pose,y:100,bridgeDeformation:{...pose.bridgeDeformation,requestedLengthM:70}}]);
    expect(group.children).toHaveLength(2);
    const first=group.children[0] as THREE.Mesh,second=group.children[1] as THREE.Mesh;
    expect(first.geometry).not.toBe(geometry);expect(second.geometry).not.toBe(first.geometry);
    first.geometry.computeBoundingBox();second.geometry.computeBoundingBox();
    expect(first.geometry.boundingBox!.getSize(new THREE.Vector3()).z).toBeCloseTo(80);
    expect(second.geometry.boundingBox!.getSize(new THREE.Vector3()).z).toBeCloseTo(70);
    expect(first.material).toBe(material);
    geometry.computeBoundingBox();expect(geometry.boundingBox!.getSize(new THREE.Vector3()).z).toBe(60);
    const dispose=vi.spyOn(geometry,'dispose');disposeStreetInstances(group);expect(dispose).not.toHaveBeenCalled();
  });
  it('adjusts a bridge middle bay along the route while retaining its width, height and source geometry', () => {
    const source = new THREE.Group(), geometry = new THREE.BoxGeometry(6, 8, 4), material = new THREE.MeshStandardMaterial();
    source.add(new THREE.Mesh(geometry, material));
    const pose = {kind:'bridge_bay',url:'/bay.glb',sha256:'a'.repeat(64),x:0,y:0,z:0,yaw:0,
      scale:1,longitudinalScale:1.25,stationM:0,surfaceLiftM:0} satisfies NativeStreetPose;
    const group = instanceStreetModule(source, [pose]);
    const size = new THREE.Box3().setFromObject(group).getSize(new THREE.Vector3());
    expect(size.x).toBeCloseTo(6); expect(size.y).toBeCloseTo(5); expect(size.z).toBeCloseTo(8);
    expect((group.children[0] as THREE.Mesh).geometry).toBe(geometry);
    expect(new THREE.Box3().setFromObject(source).getSize(new THREE.Vector3()).z).toBe(4);
  });
  it('retains the source node transform, exact material and all 1200 rigid instances',()=>{
    const source=new THREE.Group(),material=new THREE.MeshStandardMaterial();
    const part=new THREE.Mesh(new THREE.BoxGeometry(2,3,4),material);
    part.position.set(1,2,3);source.add(part);
    const poses=Array.from({length:1200},(_,i)=>({kind:'tree',url:'/tree.glb',sha256:'a'.repeat(64),x:5,y:i*12,z:2,yaw:Math.PI/2,scale:.75,stationM:i*12,surfaceLiftM:.1} satisfies NativeStreetPose));
    const group=instanceStreetModule(source,poses),mesh=group.children[0] as THREE.InstancedMesh;
    expect(mesh.count).toBe(1200);expect(group.userData.nativeStreetMountedCount).toBe(1200);
    expect(mesh.material).toBe(material);expect(mesh.geometry).toBe(part.geometry);
    const actual=new THREE.Matrix4();mesh.getMatrixAt(0,actual);
    const expected=new THREE.Vector3(1,2,3).applyAxisAngle(new THREE.Vector3(1,0,0),Math.PI/2).multiplyScalar(.75).applyAxisAngle(new THREE.Vector3(0,0,1),Math.PI/2).add(new THREE.Vector3(5,0,2.1));
    const position=new THREE.Vector3().setFromMatrixPosition(actual);
    expect(position.distanceTo(expected)).toBeLessThan(1e-5);
    expect(()=>instanceStreetModule(new THREE.Group(),poses)).toThrow('no renderable meshes');
  });
});
