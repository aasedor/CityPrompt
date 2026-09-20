import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { ConnectionEditor } from './ConnectionEditor';
import { rectangleAt } from './geometry';
import { LOCAL_STREET_ASSET } from './assetRegistry';

const house:SiteZone={id:'house',project_id:'test',zone_type:'building',coordinates:rectangleAt([-114,51],12,20),properties:{native_home_plot:true,unrelated:'preserve'},color:'#aaa',sort_order:0,created_at:'now',updated_at:'now'};
const road:SiteZone={...house,id:'road',name:'Local street',zone_type:'road',properties:{road_archetype_id:'calgary_local'}};
describe('connection controls',()=>{
  it('names catalogue sidewalk targets and distinguishes repeated street types',()=>{
    const first={...road,id:'first',name:undefined,properties:{...LOCAL_STREET_ASSET.properties,pick_place_street_section:LOCAL_STREET_ASSET.model.variantId}};
    const second={...first,id:'second'};
    render(<ConnectionEditor zone={house} zones={[house,first,second]} disabled={false} onSave={vi.fn()} onClose={vi.fn()}/>);
    fireEvent.click(screen.getByRole('checkbox',{name:'Link an entrance to a sidewalk'}));
    expect(screen.getByRole('option',{name:'Calgary local street 1'})).toHaveValue('first');
    expect(screen.getByRole('option',{name:'Calgary local street 2'})).toHaveValue('second');
  });
  it('offers mapped pedestrian targets, omits motor roads and saves the ground-level review',async()=>{
    const park={...house,id:'park',zone_type:'green_space' as const,properties:{green_space_archetype_id:'urban_pocket_park'}};
    const path={id:'existing:path',kind:'path' as const,label:'Riverside path',widthM:3,points:[[-114,51],[-114.001,51]] as [number,number][]};
    const onSave=vi.fn().mockResolvedValue(undefined);
    render(<ConnectionEditor zone={park} zones={[park]} transportContext={{lines:[path,{...path,id:'motor',kind:'road',label:'Motor road'}]}} disabled={false} onSave={onSave} onClose={vi.fn()}/>);
    fireEvent.click(screen.getByRole('checkbox',{name:'Choose and lock a park entrance'}));
    expect(screen.queryByRole('option',{name:/Motor road/})).toBeNull();
    fireEvent.change(screen.getByLabelText('Sidewalk target'),{target:{value:'existing:path'}});
    fireEvent.click(screen.getByRole('checkbox',{name:/I checked that this is suitable/}));
    fireEvent.click(screen.getByRole('button',{name:'Save connections'}));
    await waitFor(()=>expect(onSave).toHaveBeenCalled());
    expect(onSave.mock.calls[0][0].pedestrian_park_entrance).toMatchObject({streetId:'existing:path',existingGroundConfirmed:true});
  });
  it('saves an explicit native-house anchor without dropping other properties',async()=>{
    const onSave=vi.fn().mockResolvedValue(undefined),onClose=vi.fn();
    render(<ConnectionEditor zone={house} zones={[house,road]} disabled={false} onSave={onSave} onClose={onClose}/>);
    fireEvent.click(screen.getByRole('checkbox',{name:'Link an entrance to a sidewalk'}));
    expect(screen.getByRole('checkbox',{name:/Scale entrance/})).not.toBeChecked();
    fireEvent.change(screen.getByLabelText('Left / right (m)'),{target:{value:'2'}});
    fireEvent.click(screen.getByRole('button',{name:'Save connections'}));
    await waitFor(()=>expect(onClose).toHaveBeenCalled());
    expect(onSave.mock.calls[0][0]).toMatchObject({unrelated:'preserve',pedestrian_building_entrance:{version:1,xM:2,yM:-8,streetId:'road',scaleWithPlot:false}});
  });
  it('does not shift an existing proportional anchor when reopening after resize',async()=>{
    const zone={...house,coordinates:rectangleAt([-114,51],24,40),properties:{pedestrian_building_entrance:{version:1,xM:2,yM:-8,referenceWidthM:12,referenceDepthM:20,scaleWithPlot:true,streetId:'road',widthM:1.8}}};
    const onSave=vi.fn().mockResolvedValue(undefined);
    render(<ConnectionEditor zone={zone} zones={[zone,road]} disabled={false} onSave={onSave} onClose={vi.fn()}/>);
    expect(screen.getByLabelText('Left / right (m)')).toHaveValue(4);
    expect(screen.getByLabelText('Front / back (m)')).toHaveValue(-16);
    fireEvent.click(screen.getByRole('button',{name:'Save connections'}));
    await waitFor(()=>expect(onSave).toHaveBeenCalled());
    expect(onSave.mock.calls[0][0].pedestrian_building_entrance).toMatchObject({xM:4,yM:-16});
    expect(onSave.mock.calls[0][0].pedestrian_building_entrance.referenceWidthM).toBeCloseTo(24,5);
    expect(onSave.mock.calls[0][0].pedestrian_building_entrance.referenceDepthM).toBeCloseTo(40,5);
  });
  it('lets a student place and adjust an entrance with the plot guide while retaining exact offsets',async()=>{
    const onSave=vi.fn().mockResolvedValue(undefined);
    render(<ConnectionEditor zone={house} zones={[house,road]} disabled={false} onSave={onSave} onClose={vi.fn()}/>);
    fireEvent.click(screen.getByRole('checkbox',{name:'Link an entrance to a sidewalk'}));
    const guide=screen.getByRole('button',{name:/Plot anchor guide/});
    vi.spyOn(guide,'getBoundingClientRect').mockReturnValue({left:10,top:20,width:120,height:200} as DOMRect);
    fireEvent.pointerDown(guide,{clientX:100,clientY:70});
    expect(screen.getByLabelText('Left / right (m)')).toHaveValue(3);
    expect(screen.getByLabelText('Front / back (m)')).toHaveValue(-5);
    fireEvent.keyDown(guide,{key:'ArrowRight'});
    expect(screen.getByLabelText('Left / right (m)')).toHaveValue(3.25);
    fireEvent.click(screen.getByRole('button',{name:'Save connections'}));
    await waitFor(()=>expect(onSave).toHaveBeenCalledOnce());
    expect(onSave.mock.calls[0][0].pedestrian_building_entrance).toMatchObject({xM:3.25,yM:-5});
  });
  it('saves the entrance height without scaling it with the plot and rejects missing heights',async()=>{
    const onSave=vi.fn().mockResolvedValue(undefined);
    render(<ConnectionEditor zone={house} zones={[house,road]} disabled={false} onSave={onSave} onClose={vi.fn()}/>);
    fireEvent.click(screen.getByRole('checkbox',{name:'Link an entrance to a sidewalk'}));
    fireEvent.change(screen.getByLabelText('Entrance height above building base (m)'),{target:{value:''}});
    expect(screen.getByRole('button',{name:'Save connections'})).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Entrance height above building base (m)'),{target:{value:'0.18'}});
    fireEvent.click(screen.getByRole('button',{name:'Save connections'}));
    await waitFor(()=>expect(onSave).toHaveBeenCalledOnce());
    expect(onSave.mock.calls[0][0].pedestrian_building_entrance.heightAboveBaseM).toBe(.18);
  });
  it('keeps unsaved changes after a failed save and supports cancel without a write',async()=>{
    const onSave=vi.fn().mockRejectedValue(new Error('offline')),onClose=vi.fn();
    render(<ConnectionEditor zone={road} zones={[road]} disabled={false} onSave={onSave} onClose={onClose}/>);
    fireEvent.click(screen.getByRole('button',{name:'Add crossing'}));
    fireEvent.click(screen.getByRole('button',{name:'Save connections'}));
    expect(await screen.findByRole('alert')).toHaveTextContent('Could not save');
    expect(screen.getByLabelText('Position along street (%)')).toHaveValue(50);
    expect(onClose).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button',{name:'Cancel'}));
    expect(onClose).toHaveBeenCalledOnce();expect(onSave).toHaveBeenCalledOnce();
  });
  it('invalid numeric input cannot be saved',()=>{
    render(<ConnectionEditor zone={road} zones={[road]} disabled={false} onSave={vi.fn()} onClose={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button',{name:'Add crossing'}));
    fireEvent.change(screen.getByLabelText('Position along street (%)'),{target:{value:'101'}});
    expect(screen.getByRole('button',{name:'Save connections'})).toBeDisabled();
  });
});
