import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { DetailPlacementPanel } from './DetailPlacementPanel';
import { useDetailPlacement } from './useDetailPlacement';
import type { ProjectDetails } from './projectBenches';
import { DETAIL_CATEGORIES, searchDetails } from './detailCatalogue';
// jsdom has no WebGL or intersection observer; placement, search and saving stay real.
vi.mock('./detailThumbnail', () => ({ detailThumbnail: async () => 'data:image/png;base64,preview' }));
afterEach(() => vi.unstubAllGlobals());
describe('detail catalogue workflow', () => {
  it('makes People the first prominent category',()=>{
    vi.stubGlobal('IntersectionObserver',class {observe(){} disconnect(){}});
    function Trial(){const placement=useDetailPlacement({version:1,revision:0,can_edit:true,benches:[]},async next=>next);return <DetailPlacementPanel placement={placement} canEdit onClose={()=>{}} onArrange={()=>{}}/>;}
    render(<Trial/>);
    expect(DETAIL_CATEGORIES[0]).toBe('People');
    expect(screen.getByRole('button',{name:'Browse People'})).toHaveClass('col-span-2');
    fireEvent.click(screen.getByRole('button',{name:'Browse People'}));
    expect(screen.getByRole('combobox',{name:'Item category'})).toHaveValue('People');
    expect(screen.getByRole('button',{name:'People · choose a person & action'})).toBeVisible();
    expect(screen.getByText('23 items · AI appearance previews')).toBeVisible();
    expect(screen.getByText(/Placed people use simplified 3D models/)).toBeVisible();
    expect(screen.queryByText(/actual 3D model previews/)).not.toBeInTheDocument();
    expect(screen.getByRole('button', {name:'Choose Sofia · Summer dress'})).toBeVisible();
  });
  it('collapses the narrow catalogue after choosing an item and can reopen without cancelling placement',()=>{
    vi.stubGlobal('matchMedia',()=>({matches:true,addEventListener:vi.fn(),removeEventListener:vi.fn()}));
    vi.stubGlobal('IntersectionObserver',class {observe(){} disconnect(){}});
    function Trial(){
      const placement=useDetailPlacement({version:1,revision:0,can_edit:true,benches:[]},async next=>next);
      return <DetailPlacementPanel placement={placement} canEdit onClose={()=>{}} onArrange={()=>{}}/>;
    }
    render(<Trial/>);
    fireEvent.click(screen.getByRole('button',{name:'Browse Seating'}));
    fireEvent.click(screen.getByRole('button',{name:'Choose Timber bench'}));
    expect(screen.queryByLabelText('Search individual items')).not.toBeInTheDocument();
    expect(screen.getByText('Placing: Timber bench')).toBeVisible();
    fireEvent.click(screen.getByRole('button',{name:'Expand detail catalogue'}));
    expect(screen.getByLabelText('Search individual items')).toBeVisible();
    expect(screen.getByText('Placing: Timber bench')).toBeVisible();
  });
  it('keeps selected-item movement and deletion available in the compact sheet, with precise edits on expansion',()=>{
    vi.stubGlobal('matchMedia',()=>({matches:true,addEventListener:vi.fn(),removeEventListener:vi.fn()}));
    function Trial(){
      const placement=useDetailPlacement({version:1,revision:0,can_edit:true,benches:[{id:'bench',lng:-114,lat:51,angle:15}]},async next=>next);
      return <DetailPlacementPanel placement={placement} canEdit onClose={()=>{}} onArrange={()=>{}}/>;
    }
    render(<Trial/>);
    fireEvent.click(screen.getByRole('button',{name:'Placed items (1)'}));
    fireEvent.click(screen.getByRole('button',{name:/Timber bench.*Select to edit/}));
    expect(screen.getByRole('button',{name:'Move item'})).toBeVisible();
    expect(screen.getByRole('button',{name:'Delete item'})).toBeVisible();
    expect(screen.getByRole('button',{name:'Rotate right 15°'})).toBeVisible();
    expect(screen.queryByLabelText('Selected detail rotation')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Expand detail catalogue'}));
    expect(screen.getByLabelText('Selected detail rotation')).toHaveValue(15);
    expect(screen.getByRole('button',{name:'Place a copy'})).toBeVisible();
    fireEvent.keyDown(screen.getByLabelText('Selected detail rotation'),{key:'Delete'});
    expect(screen.getByRole('button',{name:'Placed items (1)'})).toBeVisible();
  });
  it('selects hidden placed items, rotates and deletes without opening the arrangement editor', async () => {
    const saved: ProjectDetails[] = [];
    function Trial() {
      const placement = useDetailPlacement({version:1,revision:0,can_edit:true,benches:[{id:'bench',lng:-114,lat:51,angle:0}],trees:[{id:'tree',variant:'oak-2',lng:-114,lat:51,angle:0}]}, async next => {
        const result={...next,revision:next.revision+1}; saved.push(result); return result;
      });
      return <DetailPlacementPanel placement={placement} canEdit onClose={()=>{}} onArrange={()=>{}}/>;
    }
    render(<Trial/>);
    fireEvent.click(screen.getByRole('button',{name:'Placed items (2)'}));
    fireEvent.click(screen.getByRole('button',{name:/Timber bench.*Select to edit/}));
    fireEvent.click(screen.getByRole('button',{name:'Rotate right 15°'}));
    await waitFor(()=>expect(saved).toHaveLength(1));
    expect(saved[0].benches[0].angle).toBe(15);
    fireEvent.click(screen.getByRole('button',{name:'Delete item'}));
    await waitFor(()=>expect(screen.getByRole('button',{name:'Placed items (1)'})).toBeVisible());
    expect(saved[1].benches).toEqual([]);
    expect(saved[1].trees?.[0].id).toBe('tree');
  });
  it('places repeatable access pieces with rotation while the picker stays open', async () => {
    vi.stubGlobal('IntersectionObserver', class { observe() {} disconnect() {} });
    const saved: ProjectDetails[] = [];
    function Trial() {
      const placement = useDetailPlacement({ version: 1, revision: 0, can_edit: true, benches: [] }, async next => {
        const result = { ...next, revision: next.revision + 1 }; saved.push(result); return result;
      });
      return <><DetailPlacementPanel placement={placement} canEdit onClose={() => {}} onArrange={() => {}} />
        <button onClick={() => void placement.place([-114, 51])}>Access placement ground</button></>;
    }
    render(<Trial />);
    fireEvent.click(screen.getByRole('button', { name: 'Browse Access & levels' }));
    const ramp = searchDetails('', 'Access & levels').find(m => m.id === 'detail-site-accessible-ramp')!;
    fireEvent.click(screen.getByRole('button', { name: `Choose ${ramp.label}` }));
    fireEvent.change(screen.getByLabelText('Detail rotation'), { target: { value: '90' } });
    fireEvent.click(screen.getByText('Access placement ground'));
    await waitFor(() => expect(saved).toHaveLength(1));
    expect(saved[0].props?.[0]).toMatchObject({ variant: ramp.id, angle: 90 });
    fireEvent.click(screen.getByText('Access placement ground'));
    await waitFor(() => expect(saved).toHaveLength(2));
    expect(saved[1].props).toHaveLength(2);
    expect(screen.getByRole('complementary', { name: 'Detail catalogue' })).toBeVisible();
    expect(screen.getByLabelText('Item category')).toHaveValue('Access & levels');
  });
  it('opens at categories, filters every group, and searches across items from home', () => {
    vi.stubGlobal('IntersectionObserver', class { observe() {} disconnect() {} });
    function Trial() {
      const placement = useDetailPlacement({ version: 1, revision: 0, can_edit: true, benches: [] }, async next => next);
      return <DetailPlacementPanel placement={placement} canEdit onClose={() => {}} onArrange={() => {}} />;
    }
    render(<Trial />);
    expect(screen.queryAllByRole('article')).toHaveLength(0);
    for (const category of DETAIL_CATEGORIES) {
      fireEvent.click(screen.getByRole('button', { name: `Browse ${category}` }));
      const safetyFamilies: Record<string,number> = {'Traffic & safety':39,'Curb bulbs':4};
      expect(screen.getAllByRole('article')).toHaveLength(safetyFamilies[category] ?? searchDetails('', category).length);
      fireEvent.click(screen.getByRole('button', { name: 'All categories' }));
    }
    fireEvent.change(screen.getByLabelText('Search individual items'), { target: { value: 'Traffic signal' } });
    expect(screen.getByRole('button', { name: 'Choose Traffic signal' })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'All categories' }));
    expect(screen.getByLabelText('Search individual items')).toHaveValue('');
    expect(screen.queryAllByRole('article')).toHaveLength(0);
  }, 15000);
  it('places and rotates traffic items without closing the category', async () => {
    vi.stubGlobal('IntersectionObserver', class { observe() {} disconnect() {} });
    const saved: ProjectDetails[] = [];
    function Trial() {
      const placement = useDetailPlacement({ version: 1, revision: 0, can_edit: true, benches: [] }, async next => {
        const result = { ...next, revision: next.revision + 1 }; saved.push(result); return result;
      });
      return <><DetailPlacementPanel placement={placement} canEdit onClose={() => {}} onArrange={() => {}} />
        <button onClick={() => void placement.place([-114, 51])}>Traffic placement ground</button></>;
    }
    render(<Trial />);
    fireEvent.click(screen.getByRole('button', { name: 'Browse Traffic & safety' }));
    fireEvent.click(screen.getByRole('button', { name: 'Choose Traffic signal' }));
    fireEvent.change(screen.getByLabelText('Detail rotation'), { target: { value: '90' } });
    fireEvent.click(screen.getByText('Traffic placement ground'));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Traffic signal placed and saved'));
    expect(saved[0].props?.[0]).toMatchObject({ variant: 'detail-traffic-signal', angle: 90 });
    fireEvent.click(screen.getByRole('button', { name: 'Choose Speed hump' }));
    fireEvent.click(screen.getByText('Traffic placement ground'));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Speed hump placed and saved'));
    expect(saved[1].props).toHaveLength(2);
    expect(screen.getByLabelText('Item category')).toHaveValue('Traffic & safety');
  });
  it('keeps the picker and filter open after placing different items', async () => {
    vi.stubGlobal('IntersectionObserver', class { observe() {} disconnect() {} });
    const saved: ProjectDetails[] = [];
    function Trial() {
      const placement = useDetailPlacement({ version: 1, revision: 0, can_edit: true, benches: [] }, async next => {
        const result = { ...next, revision: next.revision + 1 }; saved.push(result); return result;
      });
      return <><DetailPlacementPanel placement={placement} canEdit onClose={() => {}} onArrange={() => {}} />
        <button onClick={() => void placement.place([-114, 51])}>Map ground</button></>;
    }
    render(<Trial />);
    fireEvent.click(screen.getByRole('button', { name: 'Browse Seating' }));
    fireEvent.click(screen.getByRole('button', { name: 'Choose Timber bench' }));
    fireEvent.click(screen.getByText('Map ground'));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Timber bench placed and saved'));
    expect(screen.getByRole('complementary', { name: 'Detail catalogue' })).toBeVisible();
    expect(screen.getByLabelText('Item category')).toHaveValue('Seating');
    fireEvent.click(screen.getByRole('button', { name: 'Choose Accessible picnic table' }));
    fireEvent.click(screen.getByText('Map ground'));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Accessible picnic table placed and saved'));
    expect(saved[1].benches).toHaveLength(1);
    expect(saved[1].props?.[0].variant).toBe('picnic-table-accessible');
    fireEvent.click(screen.getByRole('button', { name: 'All categories' }));
    expect(screen.getByText('Placing: Accessible picnic table')).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Browse Trees' }));
    expect(screen.getByRole('button', { name: 'Choose Oak · shape 1' })).toBeVisible();
  });
});
