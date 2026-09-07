import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { CalgaryContextButton } from './CalgaryContextButton';
import { fetchCalgaryTransport } from './existingTransport';
import { referenceLayersApi } from './api';

vi.mock('./existingTransport',()=>({CALGARY_TRANSPORT_ROOT:'https://calgary.test',fetchCalgaryTransport:vi.fn()}));
vi.mock('./api',()=>({referenceLayerQueryKey:(id:string)=>['reference-layers',id],referenceLayersApi:{import:vi.fn()}}));
const boundary={id:'boundary',zone_type:'site_boundary',is_active_boundary:true,coordinates:[[-114,51],[-113.999,51],[-113.999,51.001],[-114,51.001]],properties:{}} as SiteZone;
function setup(zones:SiteZone[]=[boundary]){
  render(<QueryClientProvider client={new QueryClient()}><CalgaryContextButton projectId="pilot" zones={zones} layers={[]}/></QueryClientProvider>);
}
beforeEach(()=>vi.clearAllMocks());
describe('one-click context import',()=>{
  it('requires a site and avoids accidentally loading the whole city',()=>{
    setup([]);expect(screen.getByRole('button')).toBeDisabled();
  });
  it('imports a single reference snapshot after fetching the site buffer',async()=>{
    vi.mocked(fetchCalgaryTransport).mockResolvedValue([]);vi.mocked(referenceLayersApi.import).mockResolvedValue({} as never);
    setup();fireEvent.click(screen.getByRole('button'));
    await waitFor(()=>expect(referenceLayersApi.import).toHaveBeenCalledOnce());
    expect(referenceLayersApi.import).toHaveBeenCalledWith('pilot',expect.any(File),expect.objectContaining({kind:'reference'}));
    const [west,south,east,north]=vi.mocked(fetchCalgaryTransport).mock.calls[0][0];
    expect(west).toBeLessThan(-114);expect(south).toBeLessThan(51);expect(east).toBeGreaterThan(-113.999);expect(north).toBeGreaterThan(51.001);
    expect(await screen.findByRole('status')).toHaveTextContent('Nearby routes loaded');
  });
  it('leaves the project untouched when the remote query fails',async()=>{
    vi.mocked(fetchCalgaryTransport).mockRejectedValue(new Error('Network unavailable'));
    setup();fireEvent.click(screen.getByRole('button'));
    expect(await screen.findByRole('status')).toHaveTextContent('Network unavailable');
    expect(referenceLayersApi.import).not.toHaveBeenCalled();expect(screen.getByRole('button')).toBeEnabled();
  });
});
