import {Vector3,type Camera} from 'three';
import type {PeopleActionId} from '@/features/people/peopleActions';
/** A metric, subject-relative shot; never inherits the aerial camera offset. */
export function applyPeopleFollowPose(camera:Camera,subject:Vector3,upDirection:Vector3,forwardDirection:Vector3,action?:PeopleActionId):void {
  const up=upDirection.clone().normalize();
  const forward=forwardDirection.clone().projectOnPlane(up).normalize();
  if (forward.lengthSq()<.5 || up.lengthSq()<.5) throw new Error('The person has no usable camera orientation.');
  const side=new Vector3().crossVectors(forward,up).normalize();
  const low=action==='lying_down',seated=action==='sitting';
  const distance=action==='running'?5:low?3:4;
  camera.position.copy(subject).addScaledVector(forward,-distance).addScaledVector(side,1.5)
    .addScaledVector(up,low?.9:seated?1.3:1.6);
  camera.up.copy(up);
  camera.lookAt(subject.clone().addScaledVector(up,low?.35:seated?.8:1.05));
  camera.updateMatrixWorld(true);
}
