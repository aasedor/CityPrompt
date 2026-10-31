import * as THREE from 'three';
import type { NativeStreetPose } from './nativeStreetPilot';
import { deformSourceBridgePoint } from './sourceSpanBridgeProgram';
import { nativeBridgeDeformationAllowed } from './nativeBridgeSources';

/** Preserve every original mesh, material and node transform while batching
 * identical modules. No decimation, changed scale or skipped cycles. */
export function instanceStreetModule(scene: THREE.Group, poses: NativeStreetPose[]): THREE.Group {
  const result=new THREE.Group();
  scene.updateMatrixWorld(true);
  const convert=new THREE.Matrix4().makeRotationX(Math.PI/2);
  scene.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return;
    const groups=new Map<string,NativeStreetPose[]>();
    for(const pose of poses){
      const key=JSON.stringify(pose.bridgeDeformation??null),items=groups.get(key)??[];
      items.push(pose);groups.set(key,items);
    }
    for(const items of groups.values()){
    const deformation=items[0].bridgeDeformation;
    if (deformation && !items.every(nativeBridgeDeformationAllowed)) throw new Error('This module has no released bridge deformation contract.');
    const geometry=deformation?object.geometry.clone().applyMatrix4(object.matrixWorld):object.geometry;
    if(deformation){
      const positions=geometry.getAttribute('position');
      const role=String(object.userData.deformationRole??(object.name.startsWith('pylon')?'pylon':object.name.startsWith('cables')?'cables':'ring'));
      for(let i=0;i<positions.count;i++){
        const p=deformSourceBridgePoint([positions.getX(i),positions.getY(i),positions.getZ(i)],deformation,role);
        positions.setXYZ(i,...p);
      }
      positions.needsUpdate=true;geometry.computeVertexNormals();geometry.computeBoundingBox();geometry.computeBoundingSphere();
    }
    const mesh=new THREE.InstancedMesh(geometry,object.material,items.length);
    mesh.userData.ownsBridgeGeometry=Boolean(deformation);
    items.forEach((pose,index)=>{
      const matrix=new THREE.Matrix4().compose(
        new THREE.Vector3(pose.x,pose.y,pose.z+pose.surfaceLiftM),
        new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,0,1),pose.yaw),
        new THREE.Vector3(pose.scale,pose.scale * (pose.longitudinalScale ?? 1),pose.scale),
      );
      mesh.setMatrixAt(index,deformation?matrix.multiply(convert):matrix.multiply(convert).multiply(object.matrixWorld));
    });
    mesh.instanceMatrix.needsUpdate=true;
    mesh.castShadow=true;
    mesh.receiveShadow=true;
    mesh.computeBoundingBox();
    mesh.computeBoundingSphere();
    result.add(mesh);
    }
  });
  if (!result.children.length && poses.length) throw new Error('The verified street component contains no renderable meshes.');
  result.userData.nativeStreetMountedCount=poses.length;
  return result;
}
export function disposeStreetInstances(group: THREE.Group) {
  group.traverse(object=>{if(object instanceof THREE.InstancedMesh){
    object.dispose();if(object.userData.ownsBridgeGeometry)object.geometry.dispose();
  }});
  // Geometry, materials and textures belong to the immutable verified cache.
}
