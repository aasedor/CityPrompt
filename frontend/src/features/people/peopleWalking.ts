import { Box3, Matrix4, Quaternion, Vector3, type Mesh, type Object3D, type SkinnedMesh } from 'three';

/** Fixed across reloads, batching and ordering. No random state or frame clock. */
export function peopleWalkingProfile(id: string) {
  let hash = 2166136261;
  for (const character of id) hash = Math.imul(hash ^ character.charCodeAt(0), 16777619) >>> 0;
  return { speed: 1.2 * (.93 + (hash & 65535) / 65535 * .14), phase: (hash >>> 16) / 65536 * 1.3333333 };
}

/** Retain the source walk's horizontal step, stance and foot orientation while
 * lowering its unusually high swing arc. Solve in the skeleton's rigid frame,
 * before body proportions and globe placement; never distort bone lengths. */
export function createWalkingCorrection(root: Object3D, height: number) {
  return createLegCorrection(root, height, 'walking');
}

/** Narrow the source's broad idle stance without changing anatomy or foot pitch. */
export function createStandingCorrection(root: Object3D, height: number) {
  return createLegCorrection(root, height, 'standing');
}

function createLegCorrection(root: Object3D, height: number, mode: 'walking' | 'standing') {
  const legs = ['l','r'].flatMap(side => {
    const hip = root.getObjectByName(`thigh_${side}`), knee = root.getObjectByName(`calf_${side}`), foot = root.getObjectByName(`foot_${side}`);
    if (!hip?.parent || knee?.parent !== hip || foot?.parent !== knee) return [];
    let top = hip;
    while ((top.parent as Object3D & {isBone?: boolean})?.isBone) top = top.parent!;
    const shoe = root.getObjectByName(`Low_top_sneaker_${side}`) as Mesh | undefined;
    if (!top.parent || !shoe?.isMesh) return [];
    // These authored shoes are rigidly weighted to their corresponding foot.
    // Fail closed for an unknown/mixed-weight garment rather than assume contact.
    const skin = shoe as SkinnedMesh;
    if (skin.isSkinnedMesh) {
      const indices=skin.geometry.getAttribute('skinIndex'),weights=skin.geometry.getAttribute('skinWeight');
      for(let i=0;i<indices.count;i++)for(let j=0;j<4;j++) {
        if(weights.getComponent(i,j)>1e-6 && skin.skeleton.bones[indices.getComponent(i,j)]!==foot)return [];
      }
    } else if (shoe.parent!==foot) return [];
    root.updateWorldMatrix(true,true);
    const inverseFoot=new Matrix4().copy(foot.matrixWorld).invert(),bounds=new Box3(),v=new Vector3();
    for(let i=0;i<shoe.geometry.getAttribute('position').count;i++) {
      shoe.getVertexPosition(i,v);v.applyMatrix4(shoe.matrixWorld).applyMatrix4(inverseFoot);bounds.expandByPoint(v);
    }
    const corners:Vector3[]=[];
    for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z])corners.push(new Vector3(x,y,z));
    return [{ hip, knee, foot, frame: top.parent, corners }];
  });
  const modelInverse = new Matrix4(), inverse = new Matrix4(), matrix = new Matrix4();
  const hipPoint = new Vector3(), kneePoint = new Vector3(), footPoint = new Vector3(), target = new Vector3();
  const axis = new Vector3(), bend = new Vector3(), wantedKnee = new Vector3(), from = new Vector3(), to = new Vector3();
  const footRotation = new Quaternion(), parentRotation = new Quaternion(), delta = new Quaternion();
  const unusedPosition = new Vector3(), unusedScale = new Vector3();
  function aim(joint: Object3D, child: Object3D, desired: Vector3, frame: Object3D) {
    inverse.copy(joint.parent!.matrixWorld).invert();
    from.setFromMatrixPosition(child.matrixWorld).applyMatrix4(inverse).sub(joint.position).normalize();
    to.copy(desired).applyMatrix4(frame.matrixWorld).applyMatrix4(inverse).sub(joint.position).normalize();
    delta.setFromUnitVectors(from,to); joint.quaternion.premultiply(delta);
    joint.updateWorldMatrix(false,true);
  }
  return () => {
    if (!legs.length) return;
    root.updateWorldMatrix(true,true); modelInverse.copy(root.matrixWorld).invert();
    for (const {hip,knee,foot,frame,corners} of legs) {
      target.setFromMatrixPosition(foot.matrixWorld).applyMatrix4(modelInverse);
      if (mode === 'standing') {
        hipPoint.setFromMatrixPosition(hip.matrixWorld).applyMatrix4(modelInverse);
        // The hip already contains this person's body width and proportions.
        // A small clearance leaves a relaxed stance rather than touching shoes.
        const side = hip.name.endsWith('_l') ? 1 : -1;
        const desired = hipPoint.x + side * .015 * height / 1.75;
        if (Math.abs(target.x - desired) < .01 * height / 1.75) continue;
        target.x = desired;
      } else {
        const excess = target.y - .12 * height / 1.75;
        if (excess <= 0) continue; // Source stance/heel strike is unchanged.
        // Smooth onset avoids a velocity corner where swing meets stance.
        let clearance=Infinity;
        for(const corner of corners)clearance=Math.min(clearance,from.copy(corner).applyMatrix4(foot.matrixWorld).applyMatrix4(modelInverse).y);
        const drop=Math.min(.6 * excess * excess / (excess + .025 * height / 1.75),Math.max(0,clearance-.004));
        if(drop<1e-6)continue;
        target.y -= drop;
      }
      inverse.copy(frame.matrixWorld).invert();
      target.applyMatrix4(root.matrixWorld).applyMatrix4(inverse);
      hipPoint.setFromMatrixPosition(hip.matrixWorld).applyMatrix4(inverse);
      kneePoint.setFromMatrixPosition(knee.matrixWorld).applyMatrix4(inverse);
      footPoint.setFromMatrixPosition(foot.matrixWorld).applyMatrix4(inverse);
      const upper = hipPoint.distanceTo(kneePoint), lower = kneePoint.distanceTo(footPoint);
      const distance = hipPoint.distanceTo(target);
      if (upper < 1e-5 || lower < 1e-5 || distance < 1e-5 || distance >= upper + lower - 1e-6 || distance <= Math.abs(upper-lower)+1e-6) continue;
      axis.copy(target).sub(hipPoint).divideScalar(distance);
      bend.copy(kneePoint).sub(hipPoint).addScaledVector(axis,-bend.dot(axis));
      if (mode === 'standing') {
        // A straight source knee has no bend plane. Use the person's forward
        // direction so the small knee flex bends naturally toward the toes.
        bend.set(0, 0, 1).transformDirection(matrix.copy(inverse).multiply(root.matrixWorld));
        bend.addScaledVector(axis, -bend.dot(axis));
      }
      if (bend.lengthSq() < 1e-10) continue;
      bend.normalize();
      const along = (upper*upper - lower*lower + distance*distance) / (2*distance);
      wantedKnee.copy(hipPoint).addScaledVector(axis,along).addScaledVector(bend,Math.sqrt(Math.max(0,upper*upper-along*along)));
      matrix.copy(inverse).multiply(foot.matrixWorld).decompose(unusedPosition,footRotation,unusedScale);
      aim(hip,knee,wantedKnee,frame); aim(knee,foot,target,frame);
      inverse.copy(frame.matrixWorld).invert();
      matrix.copy(inverse).multiply(knee.matrixWorld).decompose(unusedPosition,parentRotation,unusedScale);
      foot.quaternion.copy(parentRotation.invert().multiply(footRotation));
      foot.updateWorldMatrix(false,true);
    }
  };
}
