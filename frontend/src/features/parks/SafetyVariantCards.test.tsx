import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { DETAIL_CATALOGUE } from './detailCatalogue';
import { SafetyVariantCards } from './SafetyVariantCards';
const thumbnail=()=>null;
describe('safety family browsing',()=>{
  it('keeps all twelve curb-bulb variants unavailable while allowing previews',()=>{
    const choose=vi.fn();
    const assets=DETAIL_CATALOGUE.filter(a=>a.category==='Curb bulbs');
    expect(assets).toHaveLength(12);
    render(<SafetyVariantCards assets={assets} selected={null} disabled={false} onChoose={choose} thumbnail={thumbnail}/>);
    for(const select of screen.getAllByRole('combobox')) {
      for(const option of Array.from((select as HTMLSelectElement).options)) {
        fireEvent.change(select,{target:{value:option.value}});
        expect(screen.getAllByRole('button').every(button=>(button as HTMLButtonElement).disabled)).toBe(true);
      }
    }
    expect(choose).not.toHaveBeenCalled();
  });
  it('keeps paired RRFBs separate and selects the exact static variant',()=>{
    const choose=vi.fn();
    render(<SafetyVariantCards assets={DETAIL_CATALOGUE.filter(a=>a.safety?.group==='RRFBs')} selected={null} disabled={false} onChoose={choose} thumbnail={thumbnail}/>);
    expect(screen.getAllByRole('combobox')).toHaveLength(4);
    fireEvent.change(screen.getByRole('combobox',{name:'Paired dual-face poles · 8 m centres variant'}),{target:{value:'rrfb_calgary_pair_8m_amber_r1'}});
    fireEvent.click(screen.getByRole('button',{name:'Choose Paired dual-face poles · 8 m centres · Static amber'}));
    expect(choose).toHaveBeenCalledWith('rrfb_calgary_pair_8m_amber_r1');
  });
  it('defaults to unlit and respects read-only browsing',()=>{
    render(<SafetyVariantCards assets={DETAIL_CATALOGUE.filter(a=>a.safety?.group==='Overhead pedestrian flashers')} selected={null} disabled onChoose={()=>{throw Error('Read only');}} thumbnail={thumbnail}/>);
    expect((screen.getByRole('combobox',{name:'6 m mast arm variant'}) as HTMLSelectElement).value).toBe('overhead_calgary_reach_6m_unlit_r1');
    expect((screen.getByRole('button',{name:'Choose 6 m mast arm · Unlit'}) as HTMLButtonElement).disabled).toBe(true);
  });
});
