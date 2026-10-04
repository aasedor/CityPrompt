import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { advanceParkWalk, parkWalkHeight } from '@/features/parks/parkWalking';
import { buildingWalkEntry, buildingWalkEntrance, buildingWalkGround, buildingWalkStartForZone, constrainBuildingWalk, mountBuildingWalking, readBuildingWalking, type BuildingWalkNetwork } from './buildingWalking';

const rect = (x0:number,x1:number,y0:number,y1:number,z:number) => [
  [[x0,y0,z],[x1,y0,z],[x1,y1,z]], [[x0,y0,z],[x1,y1,z],[x0,y1,z]],
];
const network = (): BuildingWalkNetwork => ({ version:2, footprint:[12,16], portals:[[-1,1,-8,-6]],
  entrance:[0,-7,0], maxStepM:.2, routes:[], obstacles:[], triangles:[...rect(-5,5,-8,6,0),...rect(-5,5,0,6,3)] });
const zone = { id:'station', coordinates:[[0,0],[1,0],[1,1]], properties:{}, updated_at:'first' } as unknown as SiteZone;

function placed(n:BuildingWalkNetwork,yaw=0) {
  const frame = new THREE.Group(), scene = new THREE.Group();
  const pos = new THREE.Vector3(), east=new THREE.Vector3(),north=new THREE.Vector3(),up=new THREE.Vector3();
  const lat=51*Math.PI/180,lon=-114*Math.PI/180;
  WGS84_ELLIPSOID.getCartographicToPosition(lat,lon,1100,pos);
  WGS84_ELLIPSOID.getEastNorthUpAxes(lat,lon,east,north,up);
  frame.matrixAutoUpdate=false;frame.matrix.makeBasis(east,north,up);frame.matrix.setPosition(pos);
  const rotation=new THREE.Group();rotation.rotation.z=yaw;frame.add(rotation);
  scene.rotation.x=Math.PI/2;rotation.add(scene);frame.updateMatrixWorld(true);
  const at=(x:number,y:number,z:number) => {
    const p=scene.localToWorld(new THREE.Vector3(x,z,-y));
    const g=WGS84_ELLIPSOID.getPositionToCartographic(p,{lat:0,lon:0,height:0});
    return {lng:g.lon*180/Math.PI,lat:g.lat*180/Math.PI,groundHeight:g.height,heading:25};
  };
  return {at,cleanup:mountBuildingWalking('building',zone,scene,n)};
}

describe('occupied building walking',()=>{
  it('keeps the concourse under a gallery and preserves the upper level when already upstairs',()=>{
    const n=network();
    expect(parkWalkHeight(n,0,2,0)).toBe(0);
    expect(parkWalkHeight(n,0,2,3)).toBe(3);
    expect(advanceParkWalk(n,[0,-.1,0],[0,.3])[2]).toBe(0);
    expect(advanceParkWalk(n,[0,2,3],[0,2.2])[2]).toBe(3);
  });
  it('blocks furniture only on its occupied level and lets the user back away',()=>{
    const n=network();n.obstacles=[[-1,1,1,2,3,4]];
    expect(parkWalkHeight(n,0,1.5,0)).toBe(0);
    const p=advanceParkWalk(n,[0,.5,3],[0,1.5]);
    expect(p[1]).toBeLessThan(.81);expect(p[2]).toBeCloseTo(3);
    expect(advanceParkWalk(n,p,[0,.3])[1]).toBeLessThan(p[1]);
  });
  it('walks real treads up and down while rejecting a jump into an overlapping upper floor',()=>{
    const n=network();n.triangles=[...rect(-2,2,-1,0,0),...Array.from({length:20},(_,i)=>rect(-2,2,i*.32,(i+1)*.32,(i+1)*.15)).flat(),...rect(-2,2,6.4,8,3)];
    let p:[number,number,number]=[0,-.5,0];
    for(let i=0;i<90;i++)p=advanceParkWalk(n,p,[0,p[1]+.08]);
    expect(p[2]).toBeCloseTo(3);
    for(let i=0;i<90;i++)p=advanceParkWalk(n,p,[0,p[1]-.08]);
    expect(p[2]).toBeCloseTo(0);expect(p[1]).toBeCloseTo(-.5);
  });
  it.each([0,Math.PI/2,Math.PI,Math.PI*1.5])('uses the mounted placement transform at yaw %s',yaw=>{
    const {at,cleanup}=placed(network(),yaw);
    try {
      const entry=buildingWalkEntry([zone],at(3,3,3));
      expect(entry.lng).toBeCloseTo(at(0,-7,0).lng,8);
      expect(entry.lat).toBeCloseTo(at(0,-7,0).lat,8);
      expect(buildingWalkGround([zone],at(0,2,3))).toBeCloseTo(at(0,2,3).groundHeight,4);
      const from=at(0,2,0),next=at(0,2.1,0),p=constrainBuildingWalk([zone],from,next);
      expect(p.lat).toBeCloseTo(next.lat,8);expect(p.groundHeight).toBeCloseTo(next.groundHeight,4);
      expect(buildingWalkEntrance([{...zone,updated_at:'moved'}],from)).toBeNull();
    } finally {cleanup();}
    expect(buildingWalkEntrance([zone],at(0,2,0))).toBeNull();
  });
  it.each([0,Math.PI/2,Math.PI,Math.PI*1.5])('starts a selected model at its actual entrance and faces inward at yaw %s',yaw=>{
    const {at,cleanup}=placed(network(),yaw);
    try {
      const start=buildingWalkStartForZone([zone],zone.id)!;
      expect(start.lng).toBeCloseTo(at(0,-7,0).lng,8);
      expect(start.lat).toBeCloseTo(at(0,-7,0).lat,8);
      expect(start.heading).toBeGreaterThanOrEqual(0);
      expect(start.heading).toBeLessThan(360);
      const inward=at(0,-6,0), radians=start.heading*Math.PI/180;
      const north=inward.lat-start.lat, east=(inward.lng-start.lng)*Math.cos(start.lat*Math.PI/180);
      expect(Math.cos(radians)*north+Math.sin(radians)*east).toBeGreaterThan(0);
      expect(buildingWalkStartForZone([{...zone,updated_at:'moved'}],zone.id)).toBeNull();
    } finally {cleanup();}
    expect(buildingWalkStartForZone([zone],zone.id)).toBeNull();
  });
  it('lets a visitor exit the front portal, blocks entering through the side, and preserves turning',()=>{
    const {at,cleanup}=placed(network());
    try {
      expect(constrainBuildingWalk([zone],at(0,-7.99,0),at(0,-8.03,0))).toEqual(at(0,-8.03,0));
      const from=at(6.1,2,0),next={...at(5.9,2,0),heading:90};
      expect(constrainBuildingWalk([zone],from,next)).toEqual({...from,heading:90});
    } finally {cleanup();}
  });
  it('ignores missing or malformed optional geometry metadata without a viewer exception',()=>{
    const scene=new THREE.Group(),mesh=new THREE.Group();scene.add(mesh);
    expect(readBuildingWalking(scene)).toBeNull();
    mesh.userData.cityprompt_walking_json='{';expect(readBuildingWalking(scene)).toBeNull();
    mesh.userData.cityprompt_walking_json=JSON.stringify({...network(),maxStepM:20});expect(readBuildingWalking(scene)).toBeNull();
    mesh.userData.cityprompt_walking_json=JSON.stringify(network());expect(readBuildingWalking(scene)?.version).toBe(2);
  });
});
