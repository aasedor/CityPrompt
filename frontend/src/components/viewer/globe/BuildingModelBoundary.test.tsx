import { act, cleanup, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { useGLTF } from '@react-three/drei';
import { BuildingModelBoundary } from './BuildingModelBoundary';
import { retryBuildingAssets } from '@/features/pickPlace/buildingAssetRecovery';
import type { SiteZone } from '@/types';

vi.mock('@react-three/drei',()=>({useGLTF:{clear:vi.fn()}}));
afterEach(()=>{cleanup();vi.useRealTimers();vi.restoreAllMocks();});
it('automatically retries an interrupted load once, then recovers through the existing Retry action',async()=>{
  vi.useFakeTimers();vi.spyOn(console,'error').mockImplementation(()=>{});
  let broken=true;
  function Model(){if(broken)throw new Error('interrupted');return <p>Detailed tower</p>;}
  const zone={id:'tower',project_id:'qa',zone_type:'building',coordinates:[],color:'#fff',sort_order:0,
    created_at:'v1',updated_at:'v1',properties:{development_archetype_label:'Tower'}} as SiteZone;
  const expectedError=(event:ErrorEvent)=>{if(event.error?.message==='interrupted')event.preventDefault();};
  window.addEventListener('error',expectedError);
  const failure=vi.fn();window.addEventListener('cityprompt:native-building-error',failure);
  render(<BuildingModelBoundary zone={zone} request={['/podium.glb','/floor.glb']} fallback={<p>Loading model</p>}><Model/></BuildingModelBoundary>);
  expect(screen.getByText('Loading model')).toBeTruthy();
  await act(async()=>{await vi.advanceTimersByTimeAsync(600)});
  expect(useGLTF.clear).toHaveBeenCalledWith(['/podium.glb','/floor.glb']);
  expect(failure).toHaveBeenCalledOnce();
  await act(async()=>{await vi.advanceTimersByTimeAsync(30000)});
  expect(useGLTF.clear).toHaveBeenCalledTimes(1);
  broken=false;
  act(()=>retryBuildingAssets());
  expect(screen.getByText('Detailed tower')).toBeTruthy();
  expect(useGLTF.clear).toHaveBeenCalledTimes(2);
  window.removeEventListener('cityprompt:native-building-error',failure);
  window.removeEventListener('error',expectedError);
});
