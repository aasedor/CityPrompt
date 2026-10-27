import { afterEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import { initialContextCameraIsPaused, watchInitialProjectContext } from './initialProjectContextWatch';
import { findUnobstructedProjectFrame } from './projectFrameObstruction';

const visibilityEvents = () => new THREE.EventDispatcher<{ 'tile-visibility-change': {} }>();
afterEach(() => { vi.useRealTimers(); });

describe('bounded initial project context watch', () => {
  it('clears a detailed blocker arriving after 60 seconds without resetting the existing frame', async () => {
    vi.useFakeTimers();
    const events = visibilityEvents(), scene = new THREE.Scene(), target = new THREE.Vector3(0,0,10), up = new THREE.Vector3(0,0,1);
    const camera = new THREE.PerspectiveCamera(75,2,1,10000);
    camera.position.set(30,-120,80); camera.up.copy(up); camera.lookAt(target); camera.updateMatrixWorld(true);
    const original = camera.position.clone(); let checks = 0;
    const stop = watchInitialProjectContext({ source: events, isCancelled: () => false, adjust: () => {
      checks++;
      const position = findUnobstructedProjectFrame(camera,scene,target,up,[target]);
      if (!position) return false;
      camera.position.copy(position); camera.lookAt(target); camera.updateMatrixWorld(true); return true;
    } });
    await vi.advanceTimersByTimeAsync(2000);
    expect(checks).toBe(1); expect(camera.position).toEqual(original);
    await vi.advanceTimersByTimeAsync(58000);
    expect(checks).toBe(1);
    const context = new THREE.Mesh(new THREE.BoxGeometry(40,30,40), new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
    context.position.set(30,-115,80); context.userData.sceneRole='existing'; scene.add(context); scene.updateMatrixWorld(true);
    for(let index=0;index<100;index++) events.dispatchEvent({type:'tile-visibility-change'});
    await vi.advanceTimersByTimeAsync(1999); expect(checks).toBe(1);
    await vi.advanceTimersByTimeAsync(1); expect(checks).toBe(2);
    expect(camera.position.z).toBeGreaterThan(original.z);
    expect(camera.position.distanceTo(target)).toBeCloseTo(original.distanceTo(target),6);
    const ray = new THREE.Raycaster(camera.position.clone(),target.clone().sub(camera.position).normalize(),0,camera.position.distanceTo(target)-1);
    expect(ray.intersectObject(context)).toHaveLength(0); expect(context.visible).toBe(true);
    stop(); expect(vi.getTimerCount()).toBe(0);
  });
  it('cancels pending work and removes listeners immediately when the user takes the camera', async () => {
    vi.useFakeTimers(); const events = visibilityEvents(); let checks=0;
    const stop=watchInitialProjectContext({source:events,isCancelled:()=>false,adjust:()=>{checks++;return false;}});
    events.dispatchEvent({type:'tile-visibility-change'});
    stop();
    expect(vi.getTimerCount()).toBe(0);
    events.dispatchEvent({type:'tile-visibility-change'}); await vi.advanceTimersByTimeAsync(130000);
    expect(checks).toBe(0);
  });
  it('checks cancellation again before a queued visibility check can move the camera', async () => {
    vi.useFakeTimers(); const events=visibilityEvents(); let cancelled=false,checks=0;
    watchInitialProjectContext({source:events,isCancelled:()=>cancelled,adjust:()=>{checks++;return true;}});
    cancelled=true;
    await vi.advanceTimersByTimeAsync(2000);
    expect(checks).toBe(0); expect(vi.getTimerCount()).toBe(0);
  });
  it.each(['wrapper','nested'] as const)('releases the initial camera when a capture pauses the %s controls',async(owner)=>{
    vi.useFakeTimers(); const events=visibilityEvents(); let checks=0;
    const controls={enabled:true,controls:{enabled:true}};
    watchInitialProjectContext({source:events,isCancelled:()=>initialContextCameraIsPaused(controls),
      adjust:()=>{checks++;return true;}});
    if(owner==='wrapper')controls.enabled=false;else controls.controls.enabled=false;
    events.dispatchEvent({type:'tile-visibility-change'});
    expect(vi.getTimerCount()).toBe(0);
    controls.enabled=true;controls.controls.enabled=true;
    events.dispatchEvent({type:'tile-visibility-change'});await vi.advanceTimersByTimeAsync(2000);
    expect(checks).toBe(0);
  });
  it.each([
    {label:'check budget',options:{maxChecks:2},changed:false},
    {label:'correction budget',options:{maxAdjustments:2},changed:true},
  ])('releases its source and timers at the $label',async({options,changed})=>{
    vi.useFakeTimers(); const events=visibilityEvents(); let checks=0;
    watchInitialProjectContext({source:events,isCancelled:()=>false,adjust:()=>{checks++;return changed;},...options});
    await vi.advanceTimersByTimeAsync(2000);
    events.dispatchEvent({type:'tile-visibility-change'}); await vi.advanceTimersByTimeAsync(2000);
    expect(checks).toBe(2); expect(vi.getTimerCount()).toBe(0);
    events.dispatchEvent({type:'tile-visibility-change'}); await vi.advanceTimersByTimeAsync(2000);
    expect(checks).toBe(2);
  });
  it('stops at its lifetime limit even if no further tiles arrive',async()=>{
    vi.useFakeTimers(); const events=visibilityEvents(); let checks=0;
    watchInitialProjectContext({source:events,isCancelled:()=>false,adjust:()=>{checks++;return false;}});
    await vi.advanceTimersByTimeAsync(120000);
    expect(checks).toBe(1); expect(vi.getTimerCount()).toBe(0);
    events.dispatchEvent({type:'tile-visibility-change'}); await vi.advanceTimersByTimeAsync(2000);
    expect(checks).toBe(1);
  });
});
