import { afterEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { mountModelBuildingWalking } from './mountModelBuildingWalking';
const mocks = vi.hoisted(() => ({ read:vi.fn(), mount:vi.fn(), declared:vi.fn(), resolve:vi.fn(), prepare:vi.fn() }));
vi.mock('./buildingWalking',()=>({readBuildingWalking:mocks.read,mountBuildingWalking:mocks.mount}));
vi.mock('./measuredBuildingWalking',()=>({measuredWalkPlan:mocks.declared,resolveMeasuredWalkPlan:mocks.resolve,prepareMeasuredBuildingWalking:mocks.prepare}));
const zone={id:'zone',properties:{pick_place_model_revision:'revision'}} as unknown as SiteZone;
afterEach(()=>vi.resetAllMocks());
describe('exact loaded-model walking lifecycle',()=>{
  it('uses embedded circulation without a second request',()=>{
    const network={version:2},unmount=vi.fn(),source=new THREE.Group();
    mocks.read.mockReturnValue(network);mocks.mount.mockReturnValue(unmount);
    const cleanup=mountModelBuildingWalking('model',zone,source,'/exact.glb');
    expect(mocks.mount).toHaveBeenCalledWith('model',zone,source,network);
    expect(mocks.resolve).not.toHaveBeenCalled();cleanup();expect(unmount).toHaveBeenCalledOnce();
  });
  it('mounts a declared measured plan and restores door resources on cleanup',()=>{
    const plan={},network={},setOpen=vi.fn(),dispose=vi.fn(),unmount=vi.fn(),source=new THREE.Group();
    mocks.declared.mockReturnValue(plan);mocks.prepare.mockReturnValue({network,setOpen,dispose});mocks.mount.mockReturnValue(unmount);
    const cleanup=mountModelBuildingWalking('model',zone,source,'/exact.glb');
    expect(mocks.mount).toHaveBeenCalledWith('model',zone,source,network,setOpen);
    cleanup();expect(dispose).toHaveBeenCalledOnce();expect(unmount).toHaveBeenCalledOnce();
  });
  it('uses a verified legacy lookup but rejects its late result after unmount',async()=>{
    let resolve!:(value:object)=>void;
    mocks.resolve.mockReturnValue(new Promise(done=>{resolve=done;}));
    const cleanup=mountModelBuildingWalking('model',zone,new THREE.Group(),'/legacy.glb');
    cleanup();resolve({});await Promise.resolve();
    expect(mocks.prepare).not.toHaveBeenCalled();expect(mocks.mount).not.toHaveBeenCalled();
  });
  it('mounts verified legacy circulation and cleans it up when the model is replaced',async()=>{
    const plan={},network={},dispose=vi.fn(),setOpen=vi.fn(),unmount=vi.fn(),source=new THREE.Group();
    mocks.resolve.mockResolvedValue(plan);mocks.prepare.mockReturnValue({network,setOpen,dispose});mocks.mount.mockReturnValue(unmount);
    const cleanup=mountModelBuildingWalking('model',zone,source,'/legacy.glb');await Promise.resolve();
    expect(mocks.mount).toHaveBeenCalledWith('model',zone,source,network,setOpen);
    cleanup();expect(dispose).toHaveBeenCalledOnce();expect(unmount).toHaveBeenCalledOnce();
  });
  it('does not invent a route for an unknown model',async()=>{
    mocks.resolve.mockResolvedValue(null);
    mountModelBuildingWalking('model',zone,new THREE.Group(),'/unknown.glb');await Promise.resolve();
    expect(mocks.mount).not.toHaveBeenCalled();
  });
});
