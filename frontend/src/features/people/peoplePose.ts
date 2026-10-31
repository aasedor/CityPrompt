import { Box3, Group, Matrix4, Quaternion, Vector3, type Bone, type SkinnedMesh } from 'three';
import type { PeopleActor } from './peopleAnimation';
import { peopleAction, type PeopleActionId } from './peopleActions';
import { createStandingCorrection, createWalkingCorrection } from './peopleWalking';

/** Absolute, actor-owned posing. Editing samples once; capture supplies its clock. */
export function createPeopleActionPose(actor: PeopleActor, walking = {speed:1.2,phase:0}) {
  const root = new Group(); root.add(actor.root);
  const basePosition = actor.root.position.clone(), baseRotation = actor.root.quaternion.clone();
  const bones: Array<{bone:Bone;position:Vector3;rotation:Quaternion}> = [];
  actor.root.traverse(object=>{if((object as Bone).isBone)bones.push({bone:object as Bone,position:object.position.clone(),rotation:object.quaternion.clone()});});
  actor.pose(0,'idle');
  const height = Math.max(.1,new Box3().setFromObject(actor.root).getSize(new Vector3()).y), unit=height/1.75;
  const softenWalk = createWalkingCorrection(actor.root,height);
  const relaxStanding = createStandingCorrection(actor.root,height);
  const floorCorrections = new Map<PeopleActionId,number>();
  const vector=new Vector3(), target=new Vector3(), current=new Vector3();
  const delta=new Quaternion();
  const inverse=new Matrix4();
  // Targets below describe outward distance, not a rig's left/right X sign.
  // The catalogue's Blender rigs have left on +X; assuming left is -X aims
  // upper arms through the chest. Measure each shoulder in actor space once.
  const sideSigns = Object.fromEntries(['l','r'].map(side => {
    const shoulder = actor.root.getObjectByName(`upperarm_${side}`);
    const point = shoulder ? actor.root.worldToLocal(shoulder.getWorldPosition(new Vector3())) : null;
    return [side, point && Math.abs(point.x)>1e-5 ? Math.sign(point.x) : side==='l'?1:-1];
  }));
  function aim(name:string,endName:string,x:number,y:number,z:number){
    const bone=actor.root.getObjectByName(name),end=actor.root.getObjectByName(endName);
    if(!bone?.parent||!end)return;
    root.updateWorldMatrix(true,true);
    // Aim in the parent's rigid coordinates. Decomposing world quaternions
    // loses the nonuniform body-proportion scales used by the community rigs.
    inverse.copy(bone.parent.matrixWorld).invert();
    current.setFromMatrixPosition(end.matrixWorld).applyMatrix4(inverse).sub(bone.position).normalize();
    target.set(x*unit,y*unit,z*unit);actor.root.localToWorld(target);target.applyMatrix4(inverse).sub(bone.position).normalize();
    delta.setFromUnitVectors(current,target);
    bone.quaternion.premultiply(delta);
  }
  function arm(side:'l'|'r',elbow:number[],hand:number[]){
    aim(`upperarm_${side}`,`lowerarm_${side}`,Math.abs(elbow[0])*sideSigns[side],elbow[1],elbow[2]);
    aim(`lowerarm_${side}`,`hand_${side}`,Math.abs(hand[0])*sideSigns[side],hand[1],hand[2]);
  }
  function clearBounds(){actor.root.traverse(object=>{if((object as SkinnedMesh).isSkinnedMesh){const mesh=object as SkinnedMesh;mesh.computeBoundingBox();mesh.computeBoundingSphere();}});}
  /** Measured once per actor/action, in actor-parent metres rather than ECEF. */
  function floorCorrection(action:PeopleActionId){
    const known=floorCorrections.get(action);if(known!==undefined)return known;
    root.updateWorldMatrix(true,true);inverse.copy(root.matrixWorld).invert();
    let lowest=Infinity;
    actor.root.traverse(object=>{
      const mesh=object as SkinnedMesh;if(!mesh.isMesh)return;
      const positions=mesh.geometry.getAttribute('position');
      for(let i=0;i<positions.count;i++){
        mesh.getVertexPosition(i,vector);vector.applyMatrix4(mesh.matrixWorld).applyMatrix4(inverse);
        lowest=Math.min(lowest,vector.y);
      }
    });
    const correction=Number.isFinite(lowest)?-lowest:0;floorCorrections.set(action,correction);return correction;
  }
  function sample(value:PeopleActionId|undefined,seconds=0,capture=false,phase=0){
    const action=peopleAction(value).id;
    root.position.set(0,0,0);
    actor.root.position.copy(basePosition);actor.root.quaternion.copy(baseRotation);
    bones.forEach(({bone,position,rotation})=>{bone.position.copy(position);bone.quaternion.copy(rotation);});
    const locomotion=action==='walking'||action==='running',speed=action==='running'?2.8:walking.speed;
    actor.pose(locomotion ? (capture?seconds:.2) : 0,locomotion?'walk':'idle',speed,phase+(locomotion?walking.phase:0));
    if(action==='walking')softenWalk();
    if(!locomotion && !['sitting','lying_down','dancing','stretching'].includes(action))relaxStanding();
    const pulse=capture?Math.sin(seconds*3+phase):0;
    if(action==='sitting'){
      for(const side of ['l','r'] as const){
        const x=sideSigns[side]*.1;
        aim(`thigh_${side}`,`calf_${side}`,x,.98,.43);aim(`calf_${side}`,`foot_${side}`,x,.53,.43);
        arm(side,[x*2.5,.94,.15],[x*1.4,.99,.39]);
      }
    }else if(action==='lying_down')actor.root.rotateX(Math.PI/2);
    else if(action==='waving')arm('r',[.35,1.57,.02],[.34+pulse*.04,1.94,.03]);
    else if(action==='pointing')arm('r',[.36,1.35,.33],[.33,1.35,.65]);
    else if(action==='reading'){
      arm('l',[-.29,1.08,.13],[-.14,1.19,.34]);arm('r',[.29,1.08,.13],[.14,1.19,.34]);
    }else if(action==='using_phone')arm('r',[.26,1.07,.13],[.12,1.34,.3]);
    else if(action==='talking')arm('r',[.31,1.08,.18],[.34,1.22,.36+pulse*.025]);
    else if(action==='stretching'||action==='cheering'){
      arm('l',[-.32,1.64,.02],[-.28,1.98,.02]);arm('r',[.32,1.64,.02],[.28,1.98,.02]);
    }else if(action==='dancing'){
      arm('l',[-.42,1.38,.04],[-.6,1.55,.15]);arm('r',[.42,1.35,.04],[.6,1.2,.15]);actor.root.rotateY(pulse*.08);
    }else if(action==='waiting')arm('l',[-.27,1.03,.01],[-.11,.89,.16]);
    else if(action==='looking_around'){
      const head=actor.root.getObjectByName('Head');if(head)head.rotateY(.35+pulse*.12);
    }
    root.updateWorldMatrix(true,true);
    // Walk/Idle are already source-grounded at export. Static articulated poses
    // get their own measured datum, avoiding duplicated offsets or floating feet.
    if(!locomotion)actor.root.position.y+=floorCorrection(action);
    if(capture&&locomotion)root.position.z=seconds*speed;
    root.updateWorldMatrix(true,true);clearBounds();
  }
  return {root,sample};
}
