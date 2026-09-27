import { describe, expect, it, vi } from 'vitest';
import { nativePavingProbe, trimAccessAtNativePaving } from './nativeParkAccess';

import * as THREE from 'three';
import { verifiedScene } from './nativeParkAssets';
import { nativeParkLayouts } from './nativeParkRegistry';
vi.mock('./nativeParkAssets',()=>({verifiedScene:vi.fn()}));

describe('native entrance ground ownership',()=>{
  it('finds the measured timber boardwalk height without reusing a paving-only cache',()=>{
    const scene=new THREE.Group();
    for (const [name,height] of [['paving',0],['timber',.22],['grass',.5],['glass',2]] as const) {
      const material=new THREE.MeshBasicMaterial();material.name=name;
      const mesh=new THREE.Mesh(new THREE.PlaneGeometry(2,8),material);
      mesh.rotation.x=-Math.PI/2;mesh.position.y=height;scene.add(mesh);
    }
    vi.mocked(verifiedScene).mockReturnValue(scene);
    const wetland={...nativeParkLayouts.find(p=>p.id==='wetland_rain_garden_v0--native-v1')!,walkSurfaceMaterials:['timber']};
    const paving={...wetland,walkSurfaceMaterials:['paving']};
    expect(nativePavingProbe(paving)([0,0])).toBeCloseTo(0);
    expect(nativePavingProbe(wetland)([0,0])).toBeCloseTo(.22);
    expect(nativePavingProbe(paving)([0,0])).toBeCloseTo(0);
    expect(nativePavingProbe(wetland)([2,0])).toBeNull();
    expect(nativePavingProbe(wetland,true)([0,0])).toBeCloseTo(.5);
  });
  it('keeps a missing approach over the lawn and stops before existing paving',()=>{
    const result=trimAccessAtNativePaving([[0,-20],[0,-13.5]],1.8,([x,y])=>Math.abs(x)<2 && y>=-14.7?0:null);
    expect(result.path[0]).toEqual([0,-20]);
    expect(result.path[result.path.length-1][1]).toBeCloseTo(-14.7,2);
  });
  it('requires paving under the entire path width, not a narrow sliver',()=>{
    const result=trimAccessAtNativePaving([[0,-20],[0,-13.5]],1.8,([x,y])=>Math.abs(x)<.2 && y>=-14.7?0:null);
    expect(result.path[result.path.length-1]).toEqual([0,-13.5]);
  });
  it('preserves the authored paving height at a connection',()=>{
    expect(trimAccessAtNativePaving([[0,-5],[0,0]],1.8,([,y])=>y>=-2?.22:null).endHeight).toBeCloseTo(.225);
  });
});
