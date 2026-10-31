import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { ReferenceLayer } from './api';
import type { Position, ZoningOverlay } from './zoningLabels';
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
  _citypromptStudy:{schema:1,condition:'proposed',boundaryCoordinates:boundary},features:[{type:'Feature',id:'one',geometry:{type:'Polygon',coordinates:[[...boundary,boundary[0]]]},properties:{label:'Housing',color:'#dfb88b',origin:'student'}}]}} as unknown as ReferenceLayer;
const props={projectId:'project',accountId:'student',boundaryId:'site',boundary,projectName:'Trial',layers:[layer,{...layer,id:'legacy',feature_collection:{...layer.feature_collection,_citypromptStudy:{schema:1,condition:'existing',boundaryCoordinates:boundary}}}],canEdit:true,onClose:vi.fn()};
const setup=(changes:Partial<typeof props>&{mapDrawing?:StudyMapDrawing;zoningData?:ZoningOverlay}={},client=new QueryClient({defaultOptions:{queries:{retry:false}}}))=>render(<QueryClientProvider client={client}><ZoningStudyEditor {...props} {...changes}/></QueryClientProvider>);
beforeEach(()=>{vi.clearAllMocks();localStorage.clear();});
describe('zoning study editing and recovery',()=>{
  it('selects a drawn zone from the globe and edits its caption',async()=>{
    const mapDrawing={begin:vi.fn(),cancel:vi.fn(),preview:vi.fn(),onSelect:vi.fn()};
    setup({mapDrawing});
    fireEvent.click(screen.getByRole('button',{name:'Draw zone'}));
    await act(async()=>{mapDrawing.begin.mock.calls[0][0](boundary);});
    const preview=mapDrawing.preview.mock.calls[mapDrawing.preview.mock.calls.length-1][0];
    const id=preview.feature_collection.features[0].id;
    act(()=>{mapDrawing.onSelect.mock.calls[mapDrawing.onSelect.mock.calls.length-1][0](null);});
    expect(screen.queryByLabelText('Map caption')).not.toBeInTheDocument();
    act(()=>{mapDrawing.onSelect.mock.calls[mapDrawing.onSelect.mock.calls.length-1][0](id);});
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Mixed-use frontage'}});
    expect(screen.getByLabelText('Map caption')).toHaveValue('Mixed-use frontage');
  });
  it('draws a custom area on the globe and saves its identity and opacity',async()=>{
    const mapDrawing={begin:vi.fn(),cancel:vi.fn(),preview:vi.fn()};
    vi.mocked(api.put).mockResolvedValue({data:layer});
    const view=setup({mapDrawing,layers:[]});
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
  it('keeps proposal edits when switching to read-only official conditions and back',()=>{
    setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Homes'}});
    fireEvent.click(screen.getByRole('tab',{name:'Existing land use'}));
    expect(screen.queryByLabelText('Map caption')).not.toBeInTheDocument();
    expect(screen.queryByRole('button',{name:'Draw zone'})).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('tab',{name:'Proposed land use'}));
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
    expect(body).toMatchObject({boundary_id:'site',boundary_coordinates:boundary,expected_hash:'a'.repeat(64)});
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
  it('clears the submitted draft when its save succeeds after the editor closes',async()=>{
    let complete!: (response:{data:ReferenceLayer})=>void;
    vi.mocked(api.put).mockImplementation(()=>new Promise(resolve=>{complete=resolve;}));
    const view=setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'  Saved homes  '}});
    fireEvent.change(screen.getByLabelText('Study fill opacity'),{target:{value:'70'}});
    fireEvent.click(screen.getByRole('button',{name:'Save map layer'}));
    view.unmount();
    const key=`cityprompt:zoning-study-v1:student:project:${JSON.stringify(['site',boundary])}:proposed`;
    expect(localStorage.getItem(key)).not.toBeNull();
    const canonical={...layer,opacity:0.7,content_hash:'b'.repeat(64),feature_collection:{...layer.feature_collection,
      features:layer.feature_collection.features.map(feature=>({...feature,properties:{...feature.properties,label:'Saved homes'}}))}};
    await act(async()=>{complete({data:canonical});});
    expect(localStorage.getItem(key)).toBeNull();
    setup({layers:[canonical]});
    expect(screen.getByRole('button',{name:'Saved homes'})).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Save map layer'})).toBeDisabled();
    expect(screen.queryByText(/shared version changed/)).not.toBeInTheDocument();
  });
  it('updates the cached shared layer before a delayed refetch and flushes the saved revision immediately',async()=>{
    const client=new QueryClient();
    const unrelated={...layer,id:'unrelated',feature_collection:{type:'FeatureCollection' as const,features:[]}};
    client.setQueryData(['reference-layers','project'],{layers:[layer,unrelated],can_edit:true});
    let finishRefetch!:()=>void;
    vi.spyOn(client,'invalidateQueries').mockImplementation(()=>new Promise(resolve=>{finishRefetch=resolve;}));
    const canonical={...layer,content_hash:'b'.repeat(64),feature_collection:{...layer.feature_collection,
      features:layer.feature_collection.features.map(feature=>({...feature,properties:{...feature.properties,label:'Saved homes'}}))}};
    vi.mocked(api.put).mockResolvedValue({data:canonical});
    const view=setup({},client);fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Saved homes'}});
    fireEvent(window,new Event('pagehide'));
    fireEvent.click(screen.getByRole('button',{name:'Save map layer'}));
    await act(async()=>{});
    expect(client.getQueryData(['reference-layers','project'])).toEqual({layers:[unrelated,canonical],can_edit:true});
    fireEvent(window,new Event('pagehide'));
    view.unmount();
    const key=`cityprompt:zoning-study-v1:student:project:${JSON.stringify(['site',boundary])}:proposed`;
    expect(localStorage.getItem(key)).toBeNull();
    await act(async()=>{finishRefetch();});
  });
  it('does not erase a newer device draft when an earlier save finishes after close',async()=>{
    let complete!: (response:{data:ReferenceLayer})=>void;
    vi.mocked(api.put).mockImplementation(()=>new Promise(resolve=>{complete=resolve;}));
    const view=setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Submitted homes'}});
    fireEvent.click(screen.getByRole('button',{name:'Save map layer'}));
    view.unmount();
    const reopened=setup();fireEvent.click(screen.getByRole('button',{name:'Submitted homes'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Newer homes'}});
    reopened.unmount();
    const key=`cityprompt:zoning-study-v1:student:project:${JSON.stringify(['site',boundary])}:proposed`;
    const newerDraft=localStorage.getItem(key);
    await act(async()=>{complete({data:{...layer,content_hash:'b'.repeat(64)}});});
    expect(localStorage.getItem(key)).toBe(newerDraft);
    expect(JSON.parse(newerDraft!)).toMatchObject({zones:[{label:'Newer homes'}]});
  });
  it('keeps a genuine shared revision conflict and its original expected hash after reopening',async()=>{
    vi.mocked(api.put).mockRejectedValue(new Error('The shared study changed.'));
    const view=setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'My revision'}});
    view.unmount();
    setup({layers:[{...layer,content_hash:'b'.repeat(64)}]});
    expect(screen.getByText(/shared version changed/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Save map layer'}));
    expect(await screen.findByRole('alert')).toHaveTextContent('shared study changed');
    expect(vi.mocked(api.put).mock.calls[0][1]).toMatchObject({expected_hash:'a'.repeat(64),zones:[{label:'My revision'}]});
  });
  it('flushes the latest edit before an immediate reload or page suspension',()=>{
    const view=setup();fireEvent.click(screen.getByRole('button',{name:'Housing'}));
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Immediate draft'}});
    fireEvent(window,new Event('beforeunload'));
    const key=`cityprompt:zoning-study-v1:student:project:${JSON.stringify(['site',boundary])}:proposed`;
    expect(JSON.parse(localStorage.getItem(key)!)).toMatchObject({zones:[{label:'Immediate draft'}]});
    fireEvent.change(screen.getByLabelText('Map caption'),{target:{value:'Suspended draft'}});
    fireEvent(window,new Event('pagehide'));
    expect(JSON.parse(localStorage.getItem(key)!)).toMatchObject({zones:[{label:'Suspended draft'}]});
    view.unmount();
  });
  it('ignores damaged device drafts and retains the shared layer',()=>{
    const key=`cityprompt:zoning-study-v1:student:project:${JSON.stringify(['site',boundary])}:proposed`;
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
    expect(await screen.findByText('Proposed land-use study saved as its own map layer.')).toBeInTheDocument();
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

it('removes future-bylaw authoring and applies the main selector to the selected map zone',async()=>{
  const mapDrawing={begin:vi.fn(),cancel:vi.fn(),preview:vi.fn(),onSelect:vi.fn()};
  setup({mapDrawing});
  expect(screen.queryByRole('tab',{name:/Draft bylaw/})).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:'Housing'}));
  fireEvent.change(screen.getByLabelText('New zone type'),{target:{value:'C-COR1'}});
  expect(screen.getByLabelText('Calgary district')).toHaveValue('C-COR1');
  await waitFor(()=>expect(mapDrawing.preview).toHaveBeenLastCalledWith(expect.objectContaining({feature_collection:expect.objectContaining({features:[expect.objectContaining({properties:expect.objectContaining({label:'C-COR1',district:expect.objectContaining({designation:'C-COR1'})})})]})})));
});

it('keeps official outlines on repeated cached Existing visits instead of a legacy study preview',async()=>{
  const mapDrawing={begin:vi.fn(),cancel:vi.fn(),preview:vi.fn(),onSelect:vi.fn()};
  const zoningData:ZoningOverlay={loadedAt:'snapshot',bounds:[-114.12,51.01,-114.119,51.011],districts:[{id:'official',label:'C-COR1',anchor:boundary[0],polygon:[[...boundary,boundary[0]]]}]};
  setup({mapDrawing,zoningData});
  for(let visit=0;visit<2;visit++){
    fireEvent.click(screen.getByRole('tab',{name:'Existing land use'}));
    await screen.findByText('C-COR1');
    await waitFor(()=>expect(mapDrawing.preview.mock.calls.slice(-1)[0]?.[0]?.feature_collection.features[0].properties.label).toBe('C-COR1'));
    fireEvent.click(screen.getByRole('tab',{name:'Proposed land use'}));
  }
});
