import { describe, expect, it } from 'vitest';
import { AnimationClip, Bone, BoxGeometry, Group, Mesh, MeshBasicMaterial, NumberKeyframeTrack } from 'three';
import { createPeopleActor } from './peopleAnimation';
import { createPeopleActionPose } from './peoplePose';
import { PEOPLE_ACTIONS } from './peopleActions';

function makeActor() {
  const root = new Group(), hip = new Bone(); hip.name = 'pelvis'; hip.position.y = 1;
  root.add(hip); const mesh = new Mesh(new BoxGeometry(.4,1.8,.25),new MeshBasicMaterial()); mesh.position.y=.9;root.add(mesh);
  const clips = ['Idle','Walk'].map(name=>new AnimationClip(name,1,[new NumberKeyframeTrack('pelvis.position[y]',[0,1],[1,1])]));
  return createPeopleActor(root,clips,{walkClip:'Walk',idleClip:'Idle',walkStrideMeters:1.2});
}
describe('saved action poses',()=>{
  it('keeps stationary actions at their saved position and moves only walk/run captures',()=>{
    const actor=makeActor(), pose=createPeopleActionPose(actor);
    for(const action of PEOPLE_ACTIONS){
      pose.sample(action.id,2,true);
      expect(pose.root.position.toArray().every(Number.isFinite)).toBe(true);
      expect(pose.root.position.z).toBe(action.id==='walking'?2.4:action.id==='running'?5.6:0);
    }
    pose.sample('walking',2,false); expect(pose.root.position.z).toBe(0);
    actor.dispose();
  });
  it('is deterministic across action changes and restores without mutating another actor',()=>{
    const a=makeActor(),b=makeActor(),pose=createPeopleActionPose(a),other=createPeopleActionPose(b);
    pose.sample('lying_down',0,false);const first=a.root.quaternion.toArray();
    pose.sample('walking',2,true);pose.sample('lying_down',0,false);
    expect(a.root.quaternion.toArray()).toEqual(first);
    expect(b.root.quaternion.toArray()).toEqual([0,0,0,1]);
    pose.sample('standing',0,false); expect(a.root.quaternion.toArray()).toEqual([0,0,0,1]);
    expect(other.root.position.z).toBe(0); a.dispose();b.dispose();
  });
});
