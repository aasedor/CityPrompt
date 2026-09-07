import type { ReactNode } from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { GroundReviewPanel } from './GroundReviewPanel';
import { INACTIVE_SHARED_SITE_GROUND } from './SharedSiteGroundProvider';
import { createSharedSiteGroundLayout } from './sharedSiteGround';

vi.mock('@/features/projects/StudioControls', () => ({ StudioDialog: ({children}: {children: ReactNode}) => <div>{children}</div> }));
const boundary: SiteZone = {id:'b',project_id:'p',zone_type:'site_boundary',color:'#fff',sort_order:0,created_at:'now',
  coordinates:[[-114,51],[-113.9999,51],[-113.9999,51.0001],[-114,51.0001]],properties:{terrain_elevation_m:100},updated_at:'now'};
const layout = createSharedSiteGroundLayout(boundary)!;
const heights = Array(layout.grid.rows * layout.grid.columns).fill(99);
const reviewed = {...INACTIVE_SHARED_SITE_GROUND,review:{layout,heights,previousHeights:[...heights]}};
afterEach(cleanup);
describe('slope ground review', () => {
  it('saves a reviewed park surface only on explicit application and preserves the review after failure', async () => {
    const park={...boundary,id:'park',zone_type:'green_space' as const,properties:{green_space_archetype_id:'neighborhood_park',green_space_selected_variant_id:'neighborhood_park_v0',neighborhood_park_layout:'adaptive_rustic_v1'}};
    const onFollowParks=vi.fn().mockRejectedValueOnce(new Error('offline')).mockResolvedValue(undefined),onClose=vi.fn();
    render(<GroundReviewPanel boundary={boundary} ground={reviewed} parks={[park]} onFollowParks={onFollowParks} onApply={vi.fn()} onClose={onClose}/>);
    const apply=screen.getByRole('button',{name:'Use measured park terrain'});
    expect(onFollowParks).not.toHaveBeenCalled();
    fireEvent.click(apply);await screen.findByRole('alert');expect(onClose).not.toHaveBeenCalled();
    fireEvent.click(apply);await waitFor(()=>expect(onClose).toHaveBeenCalledOnce());
    expect(onFollowParks).toHaveBeenLastCalledWith({park:expect.objectContaining({version:1,snapshot:expect.objectContaining({source:'google_3d_tiles'})})});
  });
  it('inspection and edits do not mutate the site until Apply; opt-in saves the measured edge profile', async () => {
    const onApply=vi.fn().mockResolvedValue(undefined), onClose=vi.fn();
    render(<GroundReviewPanel boundary={boundary} ground={reviewed} onApply={onApply} onClose={onClose} />);
    fireEvent.change(screen.getByRole('spinbutton'),{target:{value:'101'}});
    fireEvent.click(screen.getByRole('checkbox'));
    expect(onApply).not.toHaveBeenCalled();
    fireEvent.click(screen.getByText('Apply redevelopment level'));
    await waitFor(()=>expect(onClose).toHaveBeenCalledOnce());
    expect(onApply).toHaveBeenCalledWith(true,101,expect.objectContaining({version:1,source:'google_visible_surface'}));
  });
  it('unmeasured edges do not prevent an ordinary level surface', async () => {
    const onApply=vi.fn().mockResolvedValue(undefined);
    render(<GroundReviewPanel boundary={boundary} ground={INACTIVE_SHARED_SITE_GROUND} onApply={onApply} onClose={()=>{}} />);
    expect((screen.getByRole('checkbox') as HTMLInputElement).disabled).toBe(true);
    fireEvent.click(screen.getByText('Apply redevelopment level'));
    await waitFor(()=>expect(onApply).toHaveBeenCalledWith(true,100,null));
  });
  it('does not save an invalid level or close after a failed save', async () => {
    const onApply=vi.fn().mockRejectedValue(new Error('offline')), onClose=vi.fn();
    render(<GroundReviewPanel boundary={boundary} ground={reviewed} onApply={onApply} onClose={onClose} />);
    fireEvent.change(screen.getByRole('spinbutton'),{target:{value:''}});
    fireEvent.click(screen.getByText('Apply redevelopment level'));
    expect(onApply).not.toHaveBeenCalled();
    fireEvent.change(screen.getByRole('spinbutton'),{target:{value:'100'}});
    fireEvent.click(screen.getByText('Apply redevelopment level'));
    await screen.findByRole('alert');
    expect(onClose).not.toHaveBeenCalled();
  });
});
