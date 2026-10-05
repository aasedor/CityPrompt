import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { ReferenceLayer } from './api';
import type { Position } from './zoningLabels';
import { api } from '@/services/api';
import { referenceLayersApi } from './api';
import ZoningStudyEditor from './ZoningStudyEditor';
import type { StudyMapDrawing } from './useStudyMapDrawing';

vi.mock('@/services/api',()=>({api:{put:vi.fn()},getApiErrorMessage:(error:Error)=>error.message}));
vi.mock('./api',()=>({referenceLayerQueryKey:(id:string)=>['reference-layers',id],referenceLayersApi:{list:vi.fn()}}));
vi.mock('./calgaryDistricts',async(importOriginal)=>({
  ...await importOriginal<typeof import('./calgaryDistricts')>(),
  fetchCalgaryDistricts:vi.fn().mockResolvedValue([{code:'S-SPR',designation:'S-SPR',description:'Special Purpose - School, Park and Community Reserve'}]),
}));
const boundary:Position[]=[[-114.12,51.01],[-114.119,51.01],[-114.119,51.011],[-114.12,51.011]];
const layer={id:'saved',name:'Existing zoning study',content_hash:'a'.repeat(64),feature_collection:{type:'FeatureCollection',
  _citypromptStudy:{schema:1,condition:'existing',boundaryCoordinates:boundary},features:[{type:'Feature',id:'one',geometry:{type:'Polygon',coordinates:[[...boundary,boundary[0]]]},properties:{label:'Housing',color:'#dfb88b',origin:'student'}}]}} as unknown as ReferenceLayer;
const props={projectId:'project',accountId:'student',boundaryId:'site',boundary,projectName:'Trial',layers:[layer],canEdit:true,onClose:vi.fn()};
const setup=(changes:Partial<typeof props>&{mapDrawing?:StudyMapDrawing}={})=>render(<QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}><ZoningStudyEditor {...props} {...changes}/></QueryClientProvider>);
beforeEach(()=>{vi.clearAllMocks();localStorage.clear();});
describe('zoning study editing and recovery',()=>{
  it('draws a custom area on the globe and saves its identity and opacity',async()=>{
    const mapDrawing={begin:vi.fn(),cancel:vi.fn(),preview:vi.fn()};
    vi.mocked(api.put).mockResolvedValue({data:layer});
    const view=setup({mapDrawing});
    fireEvent.click(screen.getByRole('tab',{name:'Proposed land use'}));
    fireEvent.change(screen.getByLabelText('New zone type'),{target:{value:'__custom__'}});
    expect(screen.getByRole('button',{name:'Draw zone'})).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Custom zone name'),{target:{value:'Community garden'}});
    fireEvent.change(screen.getByLabelText('Custom colour'),{target:{value:'#75b6b0'}});
    fireEvent.click(screen.getByRole('button',{name:'Draw zone'}));
    await act(async()=>{expect(mapDrawing.begin.mock.calls[0][0](boundary)).toBe(true);});
    expect(await screen.findByRole('button',{name:'Custom · Community garden'})).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Study fill opacity'),{target:{value:'100'}});
    fireEvent.click(screen.getByRole('button',{name:'Save map layer'}));
    await waitFor(()=>expect(api.put).toHaveBeenCalledOnce());
    expect(vi.mocked(api.put).mock.calls[0][0]).toContain('/proposed');
    expect(vi.mocked(api.put).mock.calls[0][1]).toMatchObject({opacity:1,zones:[{custom:true,label:'Community garden',color:'#75b6b0'}]});
    view.unmount();expect(mapDrawing.cancel).toHaveBeenCalled();expect(mapDrawing.preview).toHaveBeenLastCalledWith(null);
  });
  it('applies City colours and rejects a globe polygon outside the site',async()=>{
    const mapDrawing={begin:vi.fn(),cancel:vi.fn(),preview:vi.fn()};
    setup({mapDrawing});
    fireEvent.change(screen.getByLabelText('New zone type'),{target:{value:'S-SPR'}});
    fireEvent.click(screen.getByRole('button',{name:'Draw zone'}));
    await act(async()=>{mapDrawing.begin.mock.calls[0][0](boundary);});
    expect(await screen.findByLabelText('Zone colour')).toHaveValue('#d3e6bd');
    expect(screen.getByLabelText('Zone colour')).toBeDisabled();
    fireEvent.click(screen.getByRole('button',{name:'Draw zone'}));
    await act(async()=>{mapDrawing.begin.mock.calls[1][0](boundary.map(([x,y])=>[x+1,y]));});
    expect(await screen.findByRole('alert')).toHaveTextContent('Draw inside the site boundary');
    expect(within(screen.getByLabelText('Study zones')).getAllByRole('button')).toHaveLength(2);
  });
  it('keeps the full City designation when editing a caption, undoing, switching conditions and saving',async()=>{
    const district={code:'DC',designation:'DC48Z84',description:'Direct Control'};
    const cityLayer={...layer,feature_collection:{...layer.feature_collection,features:layer.feature_collection.features.map(feature=>({...feature,
      properties:{...feature.properties,label:'DC48Z84',origin:'calgary-extract',district},
    }))}};
    vi.mocked(api.put).mockResolvedValue({data:cityLayer});
    setup({layers:[cityLayer]});
    fireEvent.click(screen.getByRole('button',{name:'DC48Z84'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Courtyard housing'}});
    expect(screen.getByLabelText('Calgary district')).toHaveValue('DC48Z84');
    fireEvent.click(screen.getByRole('tab',{name:'Proposed land use'}));
    fireEvent.click(screen.getByRole('button',{name:'Copy existing study'}));
    fireEvent.click(screen.getByRole('button',{name:'DC48Z84 Courtyard housing'}));
    expect(screen.getByLabelText('Calgary district')).toHaveValue('DC48Z84');
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Courtyard proposal'}});
    fireEvent.click(screen.getByRole('button',{name:'Undo'}));
    fireEvent.click(screen.getByRole('button',{name:'Save map layer'}));
    await waitFor(()=>expect(api.put).toHaveBeenCalledOnce());
    expect(vi.mocked(api.put).mock.calls[0][1]).toMatchObject({zones:[{label:'Courtyard housing',district}]});
  });
  it('keeps legacy concept areas unassigned until the student chooses a published district',async()=>{
    setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    expect(screen.getByLabelText('Calgary district')).toHaveValue('');
    await within(screen.getByLabelText('Calgary district')).findByRole('option',{name:/S-SPR — Special Purpose/});
    fireEvent.change(screen.getByLabelText('Calgary district'),{target:{value:'S-SPR'}});
    expect(screen.getByLabelText('Map caption')).toHaveValue('Housing');
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Community garden'}});
    expect(screen.getByLabelText('Calgary district')).toHaveValue('S-SPR');
    fireEvent.click(screen.getByRole('button',{name:'Undo'}));
    fireEvent.click(screen.getByRole('button',{name:'Undo'}));
    fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    expect(screen.getByLabelText('Calgary district')).toHaveValue('');
  });
  it('edits only the selected condition and preserves undo across condition switches',()=>{
    setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Homes'}});
    fireEvent.click(screen.getByRole('tab',{name:'Proposed land use'}));
    expect(screen.queryByRole('button',{name:'Homes'})).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('tab',{name:'Existing conditions'}));
    expect(screen.getByRole('button',{name:'Homes'})).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Undo'}));
    expect(screen.getByRole('button',{name:'Housing'})).toBeInTheDocument();
  });
  it('saves the proposed slot with a boundary and revision without altering existing source',async()=>{
    vi.mocked(api.put).mockResolvedValue({data:{...layer,content_hash:'b'.repeat(64)}});
    setup();fireEvent.click(screen.getByRole('tab',{name:'Proposed land use'}));
    fireEvent.click(screen.getByRole('button',{name:'Copy existing study'}));
    fireEvent.click(screen.getByRole('button',{name:'Save map layer'}));
    await waitFor(()=>expect(api.put).toHaveBeenCalledOnce());
    const [url,body]=vi.mocked(api.put).mock.calls[0];
    expect(url).toContain('/proposed');
    expect(body).toMatchObject({boundary_id:'site',boundary_coordinates:boundary,expected_hash:null});
    expect(await screen.findByText('Proposed land-use study saved as its own map layer.')).toBeInTheDocument();
    expect(layer.feature_collection.features[0].properties.label).toBe('Housing');
  });
  it('keeps a failed/conflicting save as a recoverable draft when closed and reopened',async()=>{
    vi.mocked(api.put).mockRejectedValue(new Error('The shared study changed.'));
    const view=setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Kept draft'}});
    fireEvent.click(screen.getByRole('button',{name:'Save map layer'}));
    expect(await screen.findByRole('alert')).toHaveTextContent('shared study changed');
    view.unmount();setup();
    expect(screen.getByRole('button',{name:'Kept draft'})).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Save map layer'})).toBeEnabled();
  });
  it('flushes the latest edit before an immediate reload or page suspension',()=>{
    const view=setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Immediate draft'}});
    fireEvent(window,new Event('beforeunload'));
    const key=`cityprompt:zoning-study-v1:student:project:${JSON.stringify(['site',boundary])}:existing`;
    expect(JSON.parse(localStorage.getItem(key)!)).toMatchObject({zones:[{label:'Immediate draft'}]});
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Suspended draft'}});
    fireEvent(window,new Event('pagehide'));
    expect(JSON.parse(localStorage.getItem(key)!)).toMatchObject({zones:[{label:'Suspended draft'}]});
    view.unmount();
  });
  it('ignores damaged device drafts and retains the shared layer',()=>{
    const key=`cityprompt:zoning-study-v1:student:project:${JSON.stringify(['site',boundary])}:existing`;
    localStorage.setItem(key,JSON.stringify({schema:1,baseHash:'a'.repeat(64),zones:[{
      id:'broken',label:'Bad coordinates',color:'#ffffff',origin:'student',rings:[[[1],[2],[3],[1]]],
    }]}));
    setup();expect(screen.getByRole('button',{name:'Housing'})).toBeInTheDocument();
    expect(screen.queryByRole('button',{name:'Bad coordinates'})).not.toBeInTheDocument();
  });
  it('uses the server-normalized labels as the saved baseline',async()=>{
    const canonical={...layer,content_hash:'b'.repeat(64),feature_collection:{...layer.feature_collection,
      features:layer.feature_collection.features.map(feature=>({...feature,properties:{...feature.properties,label:'Canonical label'}}))}};
    vi.mocked(api.put).mockResolvedValue({data:canonical});
    setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'  Canonical label  '}});
    fireEvent.click(screen.getByRole('button',{name:'Save map layer'}));
    expect(await screen.findByText('Existing zoning study saved as its own map layer.')).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Canonical label'})).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Save map layer'})).toBeDisabled();
  });
  it('reloads a shared revision explicitly and allows undoing that draft replacement',async()=>{
    vi.mocked(referenceLayersApi.list).mockResolvedValue({layers:[layer],can_edit:true});
    setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Local edit'}});
    fireEvent.click(screen.getByRole('button',{name:'Reload shared version'}));
    expect(await screen.findByText(/Shared version loaded/)).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Housing'})).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Undo'}));
    expect(screen.getByRole('button',{name:'Local edit'})).toBeInTheDocument();
  });
  it('lets viewers export but prevents drawing, styling or saving',()=>{
    setup({canEdit:false});
    expect(screen.getByRole('button',{name:'Draw zone'})).toBeDisabled();
    fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    expect(screen.getByLabelText('Map caption')).toBeDisabled();
    expect(screen.getByRole('button',{name:'Save map layer'})).toBeDisabled();
    expect(screen.getByRole('button',{name:'Export SVG'})).toBeEnabled();
  });
});
