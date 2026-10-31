import { describe, expect, it } from 'vitest';
import { AnimationClip, Bone, BoxGeometry, Group, Mesh, MeshBasicMaterial, NumberKeyframeTrack, Quaternion, QuaternionKeyframeTrack, Vector3 } from 'three';
import { createPeopleActor } from './peopleAnimation';
import { createPeopleActionPose } from './peoplePose';
import { PEOPLE_ACTIONS } from './peopleActions';

function makeActor() {
  const root = new Group(), hip = new Bone(); hip.name = 'pelvis'; hip.position.y = 1;
  root.add(hip); const mesh = new Mesh(new BoxGeometry(.4,1.8,.25),new MeshBasicMaterial()); mesh.position.y=.9;root.add(mesh);
  const clips = ['Idle','Walk'].map(name=>new AnimationClip(name,1,[new NumberKeyframeTrack('pelvis.position[y]',[0,1],[1,1])]));
  return createPeopleActor(root,clips,{walkClip:'Walk',idleClip:'Idle',walkStrideMeters:1.2});
}

function wideStandingActor() {
  const source = new Group(), rig = new Group(), pelvis = new Bone();
  pelvis.name = 'pelvis'; pelvis.position.y = .1 + .9 * Math.cos(.2); rig.add(pelvis); source.add(rig);
  const tracks: QuaternionKeyframeTrack[] = [];
  for (const side of ['l', 'r']) {
    const hip = new Bone(), knee = new Bone(), foot = new Bone();
    hip.name = `thigh_${side}`; knee.name = `calf_${side}`; foot.name = `foot_${side}`;
    const sign = side === 'l' ? 1 : -1;
    hip.position.x = sign * .1; knee.position.y = -.45; foot.position.y = -.45;
    pelvis.add(hip); hip.add(knee); knee.add(foot);
    const shoe = new Mesh(new BoxGeometry(.12, .1, .25), new MeshBasicMaterial());
    shoe.name = `Low_top_sneaker_${side}`; shoe.position.y = -.05; foot.add(shoe);
    for (const [bone, angle] of [[hip, sign * .2], [foot, -sign * .2]] as const) {
      const q = new Quaternion().setFromAxisAngle(new Vector3(0, 0, 1), angle);
      tracks.push(new QuaternionKeyframeTrack(`${bone.name}.quaternion`, [0, 1], [...q.toArray(), ...q.toArray()]));
    }
  }
  const body = new Mesh(new BoxGeometry(.4, 1.75, .25), new MeshBasicMaterial()); body.position.y = .875; source.add(body);
  const clips = ['Idle', 'Walk'].map(name => new AnimationClip(name, 1, tracks));
  return createPeopleActor(source, clips, { walkClip: 'Walk', idleClip: 'Idle', walkStrideMeters: 1.2 });
}

const legPoint = (actor: ReturnType<typeof wideStandingActor>, name: string) => actor.root.getObjectByName(name)!.getWorldPosition(new Vector3());
describe('saved action poses',()=>{
  it.each([1, -1])('retargets each rig side without crossing arms and retains a moving wave (left sign %s)', sign => {
    const source = new Group(), rig = new Group(); source.add(rig); rig.scale.set(1.1, .98, 1);
    const body = new Mesh(new BoxGeometry(.4, 1.75, .25), new MeshBasicMaterial()); body.position.y = .875; source.add(body);
    for (const side of ['l', 'r']) {
      const upper = new Bone(), lower = new Bone(), hand = new Bone();
      upper.name = `upperarm_${side}`; lower.name = `lowerarm_${side}`; hand.name = `hand_${side}`;
      upper.position.set((side === 'l' ? sign : -sign) * .2, 1.4, 0);
      lower.position.y = -.25; hand.position.y = -.25;
      rig.add(upper); upper.add(lower); lower.add(hand);
    }
    const actor = createPeopleActor(source, ['Idle', 'Walk'].map(name => new AnimationClip(name, 1, [])), { idleClip: 'Idle', walkClip: 'Walk', walkStrideMeters: 1.2 });
    const pose = createPeopleActionPose(actor);
    const point = (name: string) => actor.root.worldToLocal(actor.root.getObjectByName(name)!.getWorldPosition(new Vector3()));
    for (const action of ['sitting', 'waving', 'reading', 'using_phone', 'talking', 'pointing', 'stretching', 'dancing', 'cheering', 'waiting'] as const) {
      pose.sample(action, 0, true);
      for (const side of ['l', 'r']) {
        const outward = side === 'l' ? sign : -sign;
        expect(point(`lowerarm_${side}`).x * outward, `${action} elbow`).toBeGreaterThan(.15);
        expect(actor.root.getObjectByName(`lowerarm_${side}`)!.position.length()).toBeCloseTo(.25);
        expect(actor.root.getObjectByName(`hand_${side}`)!.position.length()).toBeCloseTo(.25);
      }
    }
    pose.sample('waving', 0, true); const first = point('hand_r');
    expect(first.y).toBeGreaterThan(1.65);
    pose.sample('waving', .5, true); expect(point('hand_r').distanceTo(first)).toBeGreaterThan(.005);
    pose.sample('reading'); expect(point('hand_l').z).toBeGreaterThan(.1); expect(point('hand_r').z).toBeGreaterThan(.1);
    actor.dispose();
  });
  it('relaxes a wide idle stance to hip width without stretching legs or tilting shoes', () => {
    const actor = wideStandingActor(), pose = createPeopleActionPose(actor);
    actor.pose(0, 'idle');
    const before = legPoint(actor, 'foot_l').x - legPoint(actor, 'foot_r').x;
    const rotation = actor.root.getObjectByName('foot_l')!.getWorldQuaternion(new Quaternion());
    pose.sample('standing');
    const width = legPoint(actor, 'foot_l').x - legPoint(actor, 'foot_r').x;
    expect(before).toBeGreaterThan(.5);
    expect(width).toBeGreaterThan(.2);
    expect(width).toBeLessThan(.3);
    expect(legPoint(actor, 'thigh_l').distanceTo(legPoint(actor, 'calf_l'))).toBeCloseTo(.45, 7);
    expect(legPoint(actor, 'calf_l').distanceTo(legPoint(actor, 'foot_l'))).toBeCloseTo(.45, 7);
    expect(actor.root.getObjectByName('foot_l')!.getWorldQuaternion(new Quaternion()).angleTo(rotation)).toBeLessThan(1e-7);
    expect(legPoint(actor, 'foot_l').y).toBeCloseTo(.1, 7);
    actor.dispose();
  });
  it('preserves the walking stance and returns deterministically to relaxed standing', () => {
    const actor = wideStandingActor(), pose = createPeopleActionPose(actor);
    actor.pose(.2, 'walk', 1.2);
    const originalWidth = legPoint(actor, 'foot_l').x - legPoint(actor, 'foot_r').x;
    pose.sample('standing'); const relaxed = legPoint(actor, 'foot_l');
    pose.sample('walking', .2, true);
    expect(legPoint(actor, 'foot_l').x - legPoint(actor, 'foot_r').x).toBeCloseTo(originalWidth, 7);
    pose.sample('standing'); expect(legPoint(actor, 'foot_l').distanceTo(relaxed)).toBeLessThan(1e-7);
    actor.dispose();
  });
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
