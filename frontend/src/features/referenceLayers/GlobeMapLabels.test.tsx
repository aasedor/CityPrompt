import { renderHook } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import { isExcludedFromDirect3DCapture } from '@/components/viewer/globe/direct3dCapture';
import { GlobeMapLabels } from './GlobeZoningLabels';

vi.mock('@react-three/fiber',()=>({useFrame:vi.fn()}));
vi.mock('./GlobeZoningSurface',()=>({GlobeZoningSurface:()=>null}));
afterEach(()=>vi.restoreAllMocks());
it('keeps street sprites out of picking and every direct scene capture',()=>{
  vi.spyOn(HTMLCanvasElement.prototype,'getContext').mockReturnValue({
    measureText:(text:string)=>({width:text.length*14}),strokeText:vi.fn(),fillText:vi.fn(),
  } as unknown as ReturnType<HTMLCanvasElement['getContext']>);
  const {result}=renderHook(()=>GlobeMapLabels({entries:[{id:'10',label:'10 AV SW',anchor:[-114.07,51.04]}],terrainHeight:1040,name:'street-names'}));
  const group=result.current.props.object as THREE.Group;
  expect(group.children).toHaveLength(1);
  const sprite=group.children[0] as THREE.Sprite;
  const hits:THREE.Intersection[]=[];
  sprite.raycast(new THREE.Raycaster(),hits);
  expect(hits).toEqual([]);
  expect(isExcludedFromDirect3DCapture(sprite)).toBe(true);
  expect(sprite.material.depthWrite).toBe(false);
  expect(sprite.position.toArray().every(Number.isFinite)).toBe(true);
});
