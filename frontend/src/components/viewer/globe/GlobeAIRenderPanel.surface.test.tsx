import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { useAuthStore } from '@/store';
import { GlobeAIRenderPanel } from './GlobeAIRenderPanel';

const renderer = vi.hoisted(() => ({ render: vi.fn() }));
vi.mock('./useDirect3DRender', async importOriginal => ({
  ...await importOriginal<typeof import('./useDirect3DRender')>(),
  useDirect3DRender: () => ({ renderDirect3D: renderer.render }),
}));

vi.mock('../useImageModelChoice', () => ({ useImageModelChoice: () => ({
  imageModel: 'gpt-image-2', setImageModel: vi.fn(), availability: {
    default_model: 'gpt-image-2', credit_balance: 1000, credit_exempt: false,
    models: [{ id: 'gpt-image-2', available: true, minimum_credit_cost: 33 }],
  },
}) }));
vi.mock('./RecoverImageAttempts', () => ({ RecoverImageAttempts: () => null }));
vi.mock('@/services/api', async importOriginal => ({
  ...await importOriginal<typeof import('@/services/api')>(),
  rendersApi: { list: vi.fn().mockResolvedValue([]) },
}));

function zone(id: string, zone_type: SiteZone['zone_type'], properties: Record<string, unknown> = {}): SiteZone {
  return { id, zone_type, properties, project_id: 'surface-test',
    coordinates: [[-114.08, 51.04], [-114.079, 51.04], [-114.079, 51.041], [-114.08, 51.041]],
    color: '#abcdef', sort_order: 0, created_at: '2026-10-29', updated_at: '2026-10-29' };
}
const park = () => zone('park', 'green_space', { community_3d: {
  schema_version: 1, state: 'compiled', kind: 'park', generator: 'park_kit',
  compiled_at: '2026-10-29', source_hash: 'a'.repeat(64), representation_hash: 'b'.repeat(64),
} });
const surface = () => zone('surface', 'development_area', { ground_surface_material: 'black_pavers' });
async function show(zones: SiteZone[], captureAvailable = true) {
  const capture = vi.fn().mockResolvedValue({ beautyImageBase64: 'data:image/png;base64,free-view' });
  render(<QueryClientProvider client={new QueryClient()}><GlobeAIRenderPanel
    canvas={document.createElement('canvas')} camera={new THREE.PerspectiveCamera()}
    siteZones={zones} buildings={[]} terrainHeight={0} projectId="surface-test"
    captureDirect3D={captureAvailable ? capture : undefined}/></QueryClientProvider>);
  await act(async () => {});
  return capture;
}
const generate = () => screen.getByRole('button', { name: /Generate image/ }) as HTMLButtonElement;
const freeExport = () => screen.getByRole('button', { name: 'Export current 3D view · free' }) as HTMLButtonElement;
beforeEach(async () => {
  // Real SHA256 in jsdom without adding Node types to the browser project.
  const cryptoModule = 'node:crypto';
  const { webcrypto } = await import(cryptoModule);
  vi.stubGlobal('crypto', webcrypto);
  renderer.render.mockReset().mockRejectedValue(new Error('Provider stopped in test'));
  sessionStorage.clear();
  useAuthStore.setState({ user: { id: 'editor', email: 'editor@example.test', role: 'editor', is_active: true,
    render_credits: 1000, created_at: '2026-10-29' }, isAuthenticated: true, isLoading: false });
});
afterEach(() => vi.unstubAllGlobals());

describe('ground surfaces in Direct 3D rendering', () => {
  it('binds paid capture to the authored surface without a compiled archetype', async () => {
    await show([park(), surface()]);
    fireEvent.click(generate());
    await screen.findByText('Provider stopped in test');
    expect(renderer.render.mock.calls[0][1].authoredSurfaceClaims).toEqual([{
      zone_id: 'surface', source_hash: 'd0b0d2c05786a8fe8d4284b35862a1c888dec5fd144d8254cbaf003d66869cff',
    }]);
  });

  it('rejects surface edits during capture before starting an image request', async () => {
    const finish = surface();
    const capture = await show([park(), finish]);
    capture.mockImplementationOnce(async () => {
      finish.properties!.ground_surface_material = 'red_brick';
      return { beautyImageBase64: 'data:image/png;base64,changed-view' };
    });
    fireEvent.click(generate());
    await screen.findByText('Ground surfaces changed during capture. Capture the current scene again.');
    expect(renderer.render).not.toHaveBeenCalled();
  });

  it('allows image generation and exports the exact view with a surface crossing a compiled park', async () => {
    await show([park(), surface()]);
    expect(generate().disabled).toBe(false);
    expect(freeExport().disabled).toBe(false);
    fireEvent.click(freeExport());
    await waitFor(() => expect(screen.getByAltText('Enlarged render')).toBeTruthy());
  });

  it.each([
    ['unknown polygon', () => zone('water', 'water')],
    ['unknown surface material', () => zone('surface', 'water', { ground_surface_material: 'unknown-material' })],
    ['uncompiled building', () => zone('building', 'development_area')],
  ] as const)('keeps %s blocked alongside a recognized surface', async (_label, invalid) => {
    await show([park(), surface(), invalid()]);
    expect(generate().disabled).toBe(true);
    expect(freeExport().disabled).toBe(true);
  });

  it('keeps the stale landscape gate with a recognized surface', async () => {
    await show([park(), surface(), zone('boundary', 'site_boundary', { community_3d_landscape: { state: 'stale' } })]);
    expect(generate().disabled).toBe(true);
    expect(freeExport().disabled).toBe(true);
  });

  it('keeps the unavailable capture gate with a recognized surface', async () => {
    await show([park(), surface()], false);
    expect(generate().disabled).toBe(true);
    expect(freeExport().disabled).toBe(true);
  });
});
