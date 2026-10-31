import '@testing-library/jest-dom/vitest';
import { afterAll, afterEach, expect, it, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import type { SiteZone } from '@/types';

vi.stubEnv('DEV', false); vi.stubEnv('MODE', 'production');
const { StreetRoutePanel } = await import('./StreetRoutePanel');
const { MODULAR_BRIDGE_ASSETS } = await import('./assetRegistry');
afterAll(() => vi.unstubAllEnvs());
afterEach(cleanup);

it.each(['brick_arch_viaduct_route_v1', 'rail_through_truss_route_v1',
  'stone_arch_road_bridge_route_v1', 'steel_truss_road_bridge_route_v1'])(
  'shows the elevated concept and unsupported access limits when reshaping %s', variant => {
    const asset = MODULAR_BRIDGE_ASSETS.find(item => item.id === variant);
    expect(asset).toBeDefined();
    const zone = {id:'bridge', project_id:'test', zone_type:'road',
      coordinates:[[-114,51],[-114,51.001]], properties:asset?.properties,
      color:'#aaa',sort_order:0,created_at:'now',updated_at:'now'} as SiteZone;
    render(<StreetRoutePanel zone={zone} disabled={false} onReshape={vi.fn()}
      onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onPublicConnection={vi.fn()} />);
    expect(screen.getByText(/elevated concept span/i).textContent).toMatch(/pedestrian walking access.*unsupported/i);
    expect(screen.getByText(/elevated concept span/i).textContent).toMatch(/road\/rail junctions.*unsupported/i);
    expect(screen.queryByRole('checkbox', {name:'Connect to a public road'})).toBeNull();
    expect(screen.getByRole('button', {name:'Add bend point'})).toBeDisabled();
  });
