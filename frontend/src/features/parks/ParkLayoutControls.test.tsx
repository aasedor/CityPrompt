import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe,it,expect,vi } from 'vitest';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { ParkLayoutControls } from './ParkLayoutControls';
import { nativeParkLayouts,nativeParkProperties } from './nativeParkRegistry';

const original=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--native-v1')!;
const zone=()=>{
  const coordinates=rectangleAt([-114.05,51.04],52,39);
  return {id:'park',updated_at:'1',zone_type:'green_space',coordinates,properties:nativeParkProperties({},original,coordinates)} as SiteZone;
};
const chooseLong=()=>{fireEvent.change(screen.getByRole('combobox',{name:'Park layout'}),{target:{value:'basketball_court_v1--long-v1'}});fireEvent.click(screen.getByText('Preview layout'));};
describe('park layout editing',()=>{
  it('previews and cancels without making a write',()=>{
    const save=vi.fn(),p=zone();render(<ParkLayoutControls zone={p} zones={[p]} disabled={false} onSave={save}/>);
    chooseLong();expect(screen.getByRole('img')).toHaveAttribute('aria-label','Two courts · Long layout preview');
    fireEvent.click(screen.getByText('Cancel'));expect(save).not.toHaveBeenCalled();
    expect(screen.getByRole('combobox',{name:'Park layout'})).toHaveValue(original.id);
  });
  it('saves layout and enlarged parcel in exactly one operation',async()=>{
    const save=vi.fn().mockResolvedValue({}),p=zone();render(<ParkLayoutControls zone={p} zones={[p]} disabled={false} onSave={save}/>);
    chooseLong();fireEvent.click(screen.getByText('Apply layout'));
    await waitFor(()=>expect(save).toHaveBeenCalledTimes(1));
    expect(save.mock.calls[0][0]).toMatchObject({properties:{green_space_native_layout:{layout_id:'basketball_court_v1--long-v1'}}});
    expect(save.mock.calls[0][0].coordinates).not.toEqual(p.coordinates);
  });
  it('retains the previous park and preview after a failed save',async()=>{
    const save=vi.fn().mockRejectedValue(new Error('offline')),p=zone(),before=JSON.stringify(p);
    render(<ParkLayoutControls zone={p} zones={[p]} disabled={false} onSave={save}/>);
    chooseLong();fireEvent.click(screen.getByText('Apply layout'));
    expect(await screen.findByRole('alert')).toHaveTextContent('previous park is unchanged');
    expect(JSON.stringify(p)).toBe(before);expect(screen.getByText('Apply layout')).toBeEnabled();
  });
  it('offers explicit upgrade without replacing a saved legacy instance',()=>{
    const p=zone();delete p.properties!.green_space_native_layout;
    const save=vi.fn();render(<ParkLayoutControls zone={p} zones={[p]} disabled={false} onSave={save}/>);
    expect(screen.getByText('Upgrade to the complete park')).toBeInTheDocument();
    expect(save).not.toHaveBeenCalled();
  });
  it('follows Undo when the saved layout changes inside the same larger parcel',()=>{
    const p=zone();p.coordinates=rectangleAt([-114.05,51.04],120,70);
    const long=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--long-v1')!;
    const after={...p,properties:nativeParkProperties(p.properties!,long,p.coordinates)};
    const save=vi.fn();
    const {rerender}=render(<ParkLayoutControls zone={after} zones={[after]} disabled={false} onSave={save}/>);
    expect(screen.getByRole('combobox',{name:'Park layout'})).toHaveValue(long.id);
    rerender(<ParkLayoutControls zone={p} zones={[p]} disabled={false} onSave={save}/>);
    expect(screen.getByRole('combobox',{name:'Park layout'})).toHaveValue(original.id);
    expect(save).not.toHaveBeenCalled();
  });
});
