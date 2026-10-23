import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, renderHook, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { DetailEditControls } from './DetailEditControls';
import { useDetailPlacement } from './useDetailPlacement';
import type { ProjectDetails } from './projectBenches';
vi.mock('../people/inclusivePeopleCatalogue.json', async () => ({ default: (await import('../people/testFixtures/inclusivePeople')).inclusivePeople }));

describe('detail duplication', () => {
  it('shows the seated fixed pose and keeps its limitation visible', () => {
    const data:ProjectDetails={version:1,revision:1,can_edit:true,benches:[],props:[{id:'wheelchair',variant:'people-inclusive-manual-wheelchair',lng:-114,lat:51,angle:0}]};
    function Editor(){const placement=useDetailPlacement(data,vi.fn());return <><button onClick={()=>placement.selectItem('wheelchair')}>Select wheelchair</button><DetailEditControls placement={placement}/></>;}
    render(<Editor/>);
    fireEvent.click(screen.getByRole('button',{name:'Select wheelchair'}));
    const action=screen.getByRole('combobox',{name:'Person action'});
    expect(action).toHaveValue('sitting');
    expect(action).toBeDisabled();
    expect(action.querySelectorAll('option')).toHaveLength(1);
    expect(screen.getByText(/Fixed pose.*motion is not animated/)).toBeInTheDocument();
  });
  it('offers all fifteen saved actions for a selected person', async () => {
    const data:ProjectDetails={version:1,revision:1,can_edit:true,benches:[],props:[{id:'person',variant:'people-pilot-commuter',lng:-114,lat:51,angle:0}]};
    const save=vi.fn(async(next:ProjectDetails)=>({...next,revision:next.revision+1}));
    function Editor(){const placement=useDetailPlacement(data,save);return <><button onClick={()=>placement.selectItem('person')}>Select person</button><DetailEditControls placement={placement}/></>;}
    render(<Editor/>);fireEvent.click(screen.getByRole('button',{name:'Select person'}));
    const action=screen.getByRole('combobox',{name:'Person action'});
    expect(action.querySelectorAll('option')).toHaveLength(15);
    await act(async()=>fireEvent.change(action,{target:{value:'sitting'}}));
    expect(save.mock.calls[0][0].props![0].people_action).toBe('sitting');
    expect(screen.getByRole('combobox',{name:'Person action'})).toHaveValue('sitting');
  });
  it('rotates immediately with a button and deletes with the keyboard, but never while typing', async () => {
    const data: ProjectDetails = {version:1,revision:1,can_edit:true,benches:[{id:'bench',lng:-114,lat:51,angle:0}]};
    const save=vi.fn(async(next:ProjectDetails)=>({...next,revision:next.revision+1}));
    function Editor() { const placement=useDetailPlacement(data,save); return <><button onClick={()=>placement.selectItem('bench')}>Select bench</button><DetailEditControls placement={placement}/></>; }
    render(<Editor/>);
    fireEvent.click(screen.getByRole('button',{name:'Select bench'}));
    await act(async()=>fireEvent.click(screen.getByRole('button',{name:'Rotate right 15°'})));
    expect(save.mock.calls[0][0].benches[0].angle).toBe(15);
    fireEvent.keyDown(screen.getByRole('spinbutton',{name:'Selected detail rotation'}),{key:'Delete'});
    expect(save).toHaveBeenCalledTimes(1);
    await act(async()=>fireEvent.keyDown(window,{key:'Delete'}));
    expect(save.mock.calls[1][0].benches).toEqual([]);
  });
  it('arms a separate copy with the same variant and yaw, without changing the saved source', async () => {
    const original = { id: 'original', variant: 'calgary_tc_curb_flexpost_r1', lng: -114, lat: 51, angle: 45 };
    const data: ProjectDetails = { version: 1, revision: 1, can_edit: true, benches: [], props: [original] };
    const save = vi.fn(async (next: ProjectDetails) => ({ ...next, revision: next.revision + 1 }));
    const { result } = renderHook(() => useDetailPlacement(data, save));
    act(() => result.current.selectItem(original.id));
    render(<DetailEditControls placement={result.current} />);
    fireEvent.click(screen.getByRole('button', { name: 'Place a copy' }));
    expect(result.current.selected).toBe(original.variant);
    expect(save).not.toHaveBeenCalled();
    await act(() => result.current.place([-114.001, 51.001]));
    const props = save.mock.calls[0][0].props!;
    expect(props).toHaveLength(2);
    expect(props[0]).toEqual(original);
    expect(props[1]).toMatchObject({ variant: original.variant, angle: 45, lng: -114.001, lat: 51.001 });
    expect(props[1].id).not.toBe(original.id);
  });
});
