import { beforeEach, describe, expect, it, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import type { SiteZone } from '@/types';
import { api, siteZonesApi } from '@/services/api';
import { SiteLandscapePanel } from './SiteLandscapePanel';

vi.mock('@/services/api',()=>({api:{get:vi.fn(),post:vi.fn()},authApi:{me:vi.fn()},
  siteZonesApi:{list:vi.fn(),update:vi.fn()},getApiErrorMessage:(e:Error)=>e.message}));
vi.mock('@/store/undoActions',()=>({createZoneUpdateAction:vi.fn(()=>({}))}));
vi.mock('@/store/undoRedo',()=>({useUndoRedoStore:{getState:()=>({pushAction:vi.fn()})}}));
let current:SiteZone;
function mount(zone=current) {
  const client=new QueryClient({defaultOptions:{queries:{retry:false}}});
  function Harness(){const [value,setValue]=useState(zone);return <SiteLandscapePanel zone={value} onSaved={properties=>setValue({...value,properties})}/>;}
  return render(<QueryClientProvider client={client}><Harness/></QueryClientProvider>);
}
beforeEach(()=>{
  vi.clearAllMocks();
  current={id:'site',project_id:'p',zone_type:'site_boundary',coordinates:[[0,0],[1,0],[1,1]],
    properties:{site_name:'Keep my site',community_3d_mask_existing_tiles:true},updated_at:'r1',
    color:'#77aa55',sort_order:0,created_at:'r1'};
  vi.mocked(api.get).mockResolvedValue({data:{tokens:0,custom_enabled:false}});
  vi.mocked(siteZonesApi.list).mockImplementation(async()=>[current]);
  vi.mocked(siteZonesApi.update).mockImplementation(async(_id,changes)=>{current={...current,...changes,updated_at:'r2'} as SiteZone;return current;});
});
describe('automatic site trees',()=>{
  it('defaults off and saves reversible opt-in using the latest site revision without paid generation',async()=>{
    const view=mount();
    const toggle=screen.getByRole('checkbox',{name:'Automatic site trees'});
    expect(toggle).not.toBeChecked();
    current={...current,updated_at:'concurrent',properties:{...current.properties,other_setting:42}};
    fireEvent.click(toggle);
    await waitFor(()=>expect(toggle).toBeChecked());
    expect(siteZonesApi.update).toHaveBeenCalledWith('site',expect.objectContaining({expected_updated_at:'concurrent',properties:expect.objectContaining({community_3d_automatic_trees:true,other_setting:42})}));
    expect(api.post).not.toHaveBeenCalled();
    view.unmount();mount(current);
    expect(screen.getByRole('checkbox',{name:'Automatic site trees'})).toBeChecked();
    fireEvent.click(screen.getByRole('checkbox',{name:'Automatic site trees'}));
    await waitFor(()=>expect(screen.getByRole('checkbox',{name:'Automatic site trees'})).not.toBeChecked());
    expect(current.properties).toMatchObject({community_3d_automatic_trees:false,community_3d_landscape_mode:'placed_objects_only',community_3d_landscape:null,other_setting:42});
  });
  it('keeps existing automatic landscaping until the owner switches it off',()=>{
    mount({...current,properties:{community_3d_landscape:{state:'compiled'}}});
    expect(screen.getByRole('checkbox',{name:'Automatic site trees'})).toBeChecked();
  });
  it('does not replace an explicitly applied landscape with automatic trees',()=>{
    mount({...current,properties:{community_3d_landscape_mode:'generated',community_3d_landscape:{state:'compiled'}}});
    expect(screen.getByRole('checkbox',{name:'Automatic site trees'})).toBeDisabled();
  });
  it('keeps the saved choice and shows an error if saving fails',async()=>{
    vi.mocked(siteZonesApi.update).mockRejectedValue(new Error('Could not save'));
    mount();fireEvent.click(screen.getByRole('checkbox',{name:'Automatic site trees'}));
    expect(await screen.findByRole('alert')).toHaveTextContent('Could not save');
    expect(screen.getByRole('checkbox',{name:'Automatic site trees'})).not.toBeChecked();
  });
});
