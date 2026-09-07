import '@testing-library/jest-dom/vitest';
import {fireEvent,render,screen,waitFor} from '@testing-library/react';
import {describe,it,expect,vi} from 'vitest';
import type {SiteZone} from '@/types';
import {rectangleAt} from './geometry';
import {TerraceEditor} from './TerraceEditor';
const house:SiteZone={id:'house',project_id:'test',zone_type:'building',coordinates:rectangleAt([-114,51],12,20),properties:{unrelated:'preserved'},color:'#aaa',sort_order:0,created_at:'',updated_at:''};
const site:SiteZone={...house,id:'site',zone_type:'site_boundary',coordinates:rectangleAt([-114,51],100,100),is_active_boundary:true,properties:{terrain_elevation_m:1000}};
describe('terrace editing',()=>{
 it('saves a relative level through the ordinary properties update',async()=>{
  const save=vi.fn().mockResolvedValue(undefined),close=vi.fn();render(<TerraceEditor zone={house} zones={[house,site]} disabled={false} onSave={save} onClose={close}/>);
  fireEvent.click(screen.getByLabelText('Use a level terrace'));
  fireEvent.change(screen.getByLabelText('Terrace height offset'),{target:{value:'-1'}});
  fireEvent.click(screen.getByRole('button',{name:'Save terrace and path'}));
  await waitFor(()=>expect(close).toHaveBeenCalledOnce());
  expect(save).toHaveBeenCalledWith({unrelated:'preserved',proposed_terrace:{version:1,offsetM:-1},terrace_connection:null});
 });
 it('keeps the draft when saving fails and rejects an empty height',async()=>{
  render(<TerraceEditor zone={house} zones={[house,site]} disabled={false} onSave={vi.fn().mockRejectedValue(new Error('offline'))} onClose={vi.fn()}/>);
  fireEvent.click(screen.getByLabelText('Use a level terrace'));
  fireEvent.change(screen.getByLabelText('Terrace height offset'),{target:{value:''}});
  expect(screen.getByRole('button',{name:'Save terrace and path'})).toBeDisabled();
  fireEvent.change(screen.getByLabelText('Terrace height offset'),{target:{value:'2'}});
  fireEvent.click(screen.getByRole('button',{name:'Save terrace and path'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('Could not save');
  expect(screen.getByLabelText('Terrace height offset')).toHaveValue(2);
 });
});
