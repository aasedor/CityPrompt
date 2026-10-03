import * as THREE from 'three';
import type { NativeStreetPose } from './nativeStreetPilot';

/** Preserve every original mesh, material and node transform while batching
 * identical modules. No decimation, changed scale or skipped cycles. */
export function instanceStreetModule(scene: THREE.Group, poses: NativeStreetPose[]): THREE.Group {
  const result=new THREE.Group();
  scene.updateMatrixWorld(true);
  const convert=new THREE.Matrix4().makeRotationX(Math.PI/2);
  scene.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return;
    const mesh=new THREE.InstancedMesh(object.geometry,object.material,poses.length);
    poses.forEach((pose,index)=>{
      const matrix=new THREE.Matrix4().compose(
        new THREE.Vector3(pose.x,pose.y,pose.z+pose.surfaceLiftM),
        new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,0,1),pose.yaw),
        new THREE.Vector3(pose.scale,pose.scale,pose.scale),
      );
      mesh.setMatrixAt(index,matrix.multiply(convert).multiply(object.matrixWorld));
    });
    mesh.instanceMatrix.needsUpdate=true;
    mesh.castShadow=true;
    mesh.receiveShadow=true;
    mesh.computeBoundingBox();
    mesh.computeBoundingSphere();
    result.add(mesh);
  });
  if (!result.children.length && poses.length) throw new Error('The verified street component contains no renderable meshes.');
  result.userData.nativeStreetMountedCount=poses.length;
  return result;
}
export function disposeStreetInstances(group: THREE.Group) {
  group.traverse(object=>{if(object instanceof THREE.InstancedMesh)object.dispose();});
  // Geometry, materials and textures belong to the immutable verified cache.
}
