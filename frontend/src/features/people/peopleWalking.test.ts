import { describe, expect, it } from 'vitest';
import { AnimationClip, Bone, BoxGeometry, Group, Mesh, MeshBasicMaterial, Quaternion, QuaternionKeyframeTrack, Vector3 } from 'three';
import { createPeopleActor } from './peopleAnimation';
import { createPeopleActionPose } from './peoplePose';
import { peopleWalkingProfile } from './peopleWalking';

function fixture() {
  const source = new Group(), rig = new Group(), pelvis = new Bone();
  pelvis.name = 'pelvis'; pelvis.position.y = 1; rig.add(pelvis); source.add(rig);
  const tracks: QuaternionKeyframeTrack[] = [];
  for (const side of ['l','r']) {
    const thigh = new Bone(), calf = new Bone(), foot = new Bone();
    thigh.name = `thigh_${side}`; calf.name = `calf_${side}`; foot.name = `foot_${side}`;
    thigh.position.x = side === 'l' ? .1 : -.1; calf.position.y = -.45; foot.position.y = -.45;
    pelvis.add(thigh); thigh.add(calf); calf.add(foot);
    const shoe=new Mesh(new BoxGeometry(.12,.1,.25),new MeshBasicMaterial());shoe.name=`Low_top_sneaker_${side}`;shoe.position.y=-.05;foot.add(shoe);
    // One deliberately high swing foot and one planted leg.
    const angles = side === 'l' ? [-.6,1.2,-.6] : [0,0,0];
    [thigh,calf,foot].forEach((bone,i)=>{
      const q = new Quaternion().setFromAxisAngle(new Vector3(1,0,0),angles[i]);
      tracks.push(new QuaternionKeyframeTrack(`${bone.name}.quaternion`,[0,1],[...q.toArray(),...q.toArray()]));
    });
  }
  const mesh = new Mesh(new BoxGeometry(.4,1.75,.25),new MeshBasicMaterial()); mesh.position.y=.875;source.add(mesh);
  const animations = [new AnimationClip('Walk',1,tracks),new AnimationClip('Idle',1,[])];
  const actor = createPeopleActor(source,animations,{walkClip:'Walk',idleClip:'Idle',walkStrideMeters:1.2});
  return {source,actor,pose:createPeopleActionPose(actor)};
}
const point = (root:Group|ReturnType<typeof fixture>['actor']['root'], name:string) => root.getObjectByName(name)!.getWorldPosition(new Vector3());

describe('walking leg correction',()=>{
  it('reduces exaggerated swing lift while retaining stance contact, limb lengths and foot orientation',()=>{
    const {actor,pose}=fixture(); actor.pose(.2,'walk',1.2);
    const before=point(actor.root,'foot_l'),stance=point(actor.root,'foot_r');
    const rotation=actor.root.getObjectByName('foot_l')!.getWorldQuaternion(new Quaternion());
    pose.sample('walking',.2,true);
    const after=point(actor.root,'foot_l');
    expect(after.y).toBeLessThan(before.y-.04);
    expect(after.y).toBeGreaterThan(.12);
    expect(after.x).toBeCloseTo(before.x,7);
    expect(after.z-pose.root.position.z).toBeCloseTo(before.z,7);
    const other=point(actor.root,'foot_r'); other.z-=pose.root.position.z;
    expect(other.distanceTo(stance)).toBeLessThan(1e-7);
    expect(point(actor.root,'thigh_l').distanceTo(point(actor.root,'calf_l'))).toBeCloseTo(.45,7);
    expect(point(actor.root,'calf_l').distanceTo(after)).toBeCloseTo(.45,7);
    expect(actor.root.getObjectByName('foot_l')!.getWorldQuaternion(new Quaternion()).angleTo(rotation)).toBeLessThan(1e-7);
    actor.dispose();
  });
  it('does not soften running or retain corrected bones after a seek, and isolates the cached source',()=>{
    const {actor,pose,source}=fixture();
    actor.pose(.2,'walk',2.8); const expected=point(actor.root,'foot_l').y;
    pose.sample('running',.2,true);expect(point(actor.root,'foot_l').y).toBeCloseTo(expected,7);
    pose.sample('walking',.25,true);const first=point(actor.root,'foot_l');
    pose.sample('walking',3,true);pose.sample('standing');pose.sample('walking',.25,true);
    expect(point(actor.root,'foot_l').distanceTo(first)).toBeLessThan(1e-7);
    expect(source.getObjectByName('thigh_l')!.quaternion.toArray()).toEqual([0,0,0,1]); actor.dispose();
  });
  it('keeps motion stable across ordering/reload with independent pace and phase per placement identity',()=>{
    const ids=['actor-a','actor-b','actor-c','actor-d'];
    const profiles=new Map(ids.map(id=>[id,peopleWalkingProfile(id)]));
    for(const id of [...ids].reverse()) {
      expect(peopleWalkingProfile(id)).toEqual(profiles.get(id));
      expect(peopleWalkingProfile(id).speed).toBeGreaterThanOrEqual(1.2*.93);
      expect(peopleWalkingProfile(id).speed).toBeLessThanOrEqual(1.2*1.07);
    }
    expect(new Set([...profiles.values()].map(p=>p.phase)).size).toBe(4);
    const {actor}=fixture(),profile=peopleWalkingProfile('actor-a'),pose=createPeopleActionPose(actor,profile);
    pose.sample('walking',3,true);expect(pose.root.position.z).toBeCloseTo(profile.speed*3);
    pose.sample('walking',3,false);expect(pose.root.position.z).toBe(0);actor.dispose();
  });
  it('matches corrected local coordinates under a rotated Earth-scale placement',()=>{
    const near=fixture(),far=fixture(),earth=new Group();
    earth.position.set(6378137.123,-1234567.4,3456789.1);earth.rotation.set(.5,-.4,.3);earth.add(far.pose.root);
    near.pose.sample('walking',.3,true);far.pose.sample('walking',.3,true);
    const actual=point(far.actor.root,'foot_l');far.pose.root.worldToLocal(actual);
    const expected=point(near.actor.root,'foot_l');near.pose.root.worldToLocal(expected);
    expect(actual.distanceTo(expected)).toBeLessThan(1e-7);near.actor.dispose();far.actor.dispose();
  });
});
