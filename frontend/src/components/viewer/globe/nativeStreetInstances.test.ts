import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { instanceStreetModule } from './nativeStreetInstances';
import type { NativeStreetPose } from './nativeStreetPilot';

describe('native street instancing',()=>{
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
