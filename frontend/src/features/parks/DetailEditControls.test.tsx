import { act, fireEvent, render, renderHook, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { DetailEditControls } from './DetailEditControls';
import { useDetailPlacement } from './useDetailPlacement';
import type { ProjectDetails } from './projectBenches';

describe('detail duplication', () => {
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
