import { describe, expect, it } from 'vitest';
import { automaticStreetRouteRange, automaticStreetRouteCandidates } from './videoRouteControls';
import { DEFAULT_STREET_VIDEO_ROUTE } from './videoRenderPath';
import { CatmullRomCurve3, PerspectiveCamera, Vector3 } from 'three';
import { applyStreetRoutePose } from './globe/streetRenderProfile';
describe('automatic pedestrian video route',()=>{
  it('keeps the default near the captured site centre rather than foreground tiles',()=>{
    expect(DEFAULT_STREET_VIDEO_ROUTE.every(point=>point.y>=.48&&point.y<=.52&&point.x>=.47&&point.x<=.53)).toBe(true);
  });
  it('bounds the measured world route to a brisk walk without stretching short routes',()=>{
    const range=automaticStreetRouteRange(400,4);
    expect((range[1]-range[0])*400).toBeCloseTo(6.4);
    expect((range[0]+range[1])/2).toBeCloseTo(.5);
    expect(automaticStreetRouteRange(3,8)).toEqual([0,1]);
    expect(()=>automaticStreetRouteRange(Infinity,4)).toThrow();
  });
  it('retains a level forward heading across the automatic midpoint',()=>{
    const camera=new PerspectiveCamera(), up=new Vector3(0,1,0);
    const curve=new CatmullRomCurve3([new Vector3(-3.2,0,0),new Vector3(3.2,0,0)]);
    for(const progress of [.25,.5,.75]){
      applyStreetRoutePose(camera,curve,progress,up);
      const heading=camera.getWorldDirection(new Vector3());
      expect(heading.x).toBeGreaterThan(.99);expect(Math.abs(heading.y)).toBeLessThan(1e-5);
    }
  });
  it('offers only a bounded set of nearby corridors without changing the manual route',()=>{
    const original=DEFAULT_STREET_VIDEO_ROUTE.map(point=>({...point}));
    const candidates=automaticStreetRouteCandidates(original);
    expect(candidates).toHaveLength(9);expect(candidates[0]).toEqual(original);
    expect(candidates[1][0].y).toBeCloseTo(.62);
    expect(original).toEqual(DEFAULT_STREET_VIDEO_ROUTE);
  });
});
