import {render,screen,fireEvent} from '@testing-library/react';
import {describe,it,expect,vi} from 'vitest';
import type {SiteZone} from '@/types';
import {BuildingEntranceReviewPanel} from './BuildingEntranceReviewPanel';

const zone:SiteZone={id:'plot',project_id:'test',building_id:'model',zone_type:'building',name:'Hill house',coordinates:[],properties:{},color:'#aaa',sort_order:0,created_at:'now',updated_at:'now'};
const review={buildingId:'model',groundRevision:'current',generatedSteps:10,riseM:1.79,clearWidthM:1.64,supportHeightM:2.12};
const props={zones:[zone],reviews:[review],issues:[],groundRevision:'current',groundCurrent:true,onClose:vi.fn(),onSelect:vi.fn()};
describe('student entrance review',()=>{
  it('shows measured approach scope and keeps native-step/access checks open',()=>{
    const select=vi.fn();render(<BuildingEntranceReviewPanel {...props} onSelect={select}/>);
    expect(screen.getByText('Hill house')).toBeTruthy();
    expect(screen.getByText(/10 generated steps.*1.79 m up/)).toBeTruthy();
    expect(screen.getByText('1.64 m')).toBeTruthy();
    expect(screen.getByText('Up to 2.12 m')).toBeTruthy();
    expect(screen.getByText(/house’s own steps continue beyond it/)).toBeTruthy();
    expect(screen.getByText(/Step-free access to the door has not been assessed/)).toBeTruthy();
    fireEvent.click(screen.getByRole('button',{name:'Select and review'}));expect(select).toHaveBeenCalledWith(zone);
  });
  it('hides obsolete numbers during measurement and after a new ground revision',()=>{
    const {rerender}=render(<BuildingEntranceReviewPanel {...props} groundCurrent={false}/>);
    expect(screen.getByText(/Ground is updating or unavailable/)).toBeTruthy();
    expect(screen.queryByText('1.64 m')).toBeNull();
    rerender(<BuildingEntranceReviewPanel {...props} groundRevision="new"/>);
    expect(screen.queryByText('1.64 m')).toBeNull();
  });
  it('shows actual route failure instead of a retained ready measurement',()=>{
    render(<BuildingEntranceReviewPanel {...props} issues={[{buildingId:'model',reason:'entrance_clear_width_too_small'}]}/>);
    expect(screen.getByText(/side rails leave too little walking space/)).toBeTruthy();
    expect(screen.queryByText('1.64 m')).toBeNull();
  });
  it('does not classify a nearly level approach as step-free access to the door',()=>{
    render(<BuildingEntranceReviewPanel {...props} reviews={[{...review,generatedSteps:0,riseM:-.03}]}/>);
    expect(screen.getByText(/Nearly level approach.*0.03 m down/)).toBeTruthy();
    expect(screen.getByText(/nearly level approach can still lead to steps/)).toBeTruthy();
  });
  it('offers connection authoring for a house without an entrance and clears removed rows',()=>{
    const {rerender}=render(<BuildingEntranceReviewPanel {...props} reviews={[]}/>);
    expect(screen.getByText(/No entrance selected/)).toBeTruthy();
    rerender(<BuildingEntranceReviewPanel {...props} zones={[]}/>);
    expect(screen.queryByText('Hill house')).toBeNull();
    expect(screen.getByText(/Place a building/)).toBeTruthy();
  });
});
