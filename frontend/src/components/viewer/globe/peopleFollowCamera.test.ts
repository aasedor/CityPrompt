import {describe,expect,it} from 'vitest';
import {PerspectiveCamera,Vector3} from 'three';
import {applyPeopleFollowPose} from './peopleFollowCamera';
describe('automatic person framing',()=>{
  it('follows the moving subject at a fixed metric distance independently of the globe camera',()=>{
    const camera=new PerspectiveCamera();camera.position.set(1000,1000,1000);
    const source=new Vector3(100,0,200),up=new Vector3(0,1,0),forward=new Vector3(0,0,1);
    applyPeopleFollowPose(camera,source,up,forward,'walking');
    const relative=camera.position.clone().sub(source);
    expect(relative.y).toBeCloseTo(1.6);expect(relative.length()).toBeLessThan(6);
    const moved=source.clone().add(new Vector3(0,0,8));
    applyPeopleFollowPose(camera,moved,up,forward,'walking');
    expect(camera.position.clone().sub(moved).distanceTo(relative)).toBeLessThan(1e-8);
    const direction=camera.getWorldDirection(new Vector3());
    expect(direction.dot(moved.clone().addScaledVector(up,1.05).sub(camera.position).normalize())).toBeCloseTo(1);
  });
  it('uses lower framing for a lying subject without modifying the actor',()=>{
    const subject=new Vector3(1,2,3),original=subject.clone(),camera=new PerspectiveCamera();
    applyPeopleFollowPose(camera,subject,new Vector3(0,1,0),new Vector3(0,0,1),'lying_down');
    expect(camera.position.y-subject.y).toBeCloseTo(.9);expect(subject).toEqual(original);
  });
});
