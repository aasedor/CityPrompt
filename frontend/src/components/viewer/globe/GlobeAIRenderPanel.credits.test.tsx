import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as THREE from 'three';
import { useAuthStore } from '@/store';
import { GlobeAIRenderPanel } from './GlobeAIRenderPanel';

const state = vi.hoisted(() => ({
  choice: 'gpt-image-2',
  availability: null as null | Record<string, unknown>,
  directRender: vi.fn(),
}));
vi.mock('../useImageModelChoice', () => ({ useImageModelChoice: () => ({
  imageModel: state.choice, availability: state.availability, setImageModel: vi.fn(),
}) }));
vi.mock('./useDirect3DRender', async importOriginal => ({
  ...await importOriginal<typeof import('./useDirect3DRender')>(),
  useDirect3DRender: () => ({ renderDirect3D: state.directRender }),
}));
vi.mock('./RecoverImageAttempts', () => ({ RecoverImageAttempts: () => null }));
vi.mock('@/services/api', async importOriginal => ({
  ...await importOriginal<typeof import('@/services/api')>(),
  rendersApi: { list: vi.fn().mockResolvedValue([]) },
}));

function availability(balance: number, exempt = false) {
  return { default_model: 'gpt-image-2', credit_balance: balance, credit_exempt: exempt, models: [
    { id: 'gpt-image-2', available: true, minimum_credit_cost: 33 },
    { id: 'gpt-image-2.5-flare', available: true, minimum_credit_cost: 66 },
    { id: 'gpt-image-2.5-sunburst', available: true, minimum_credit_cost: 66 },
  ] };
}
async function show() {
  const capture = vi.fn().mockResolvedValue({ beautyImageBase64: 'data:image/png;base64,free-view' });
  render(<QueryClientProvider client={new QueryClient()}><GlobeAIRenderPanel
    canvas={document.createElement('canvas')} camera={new THREE.PerspectiveCamera()}
    siteZones={[]} buildings={[]} detailsRevision={1} terrainHeight={0} projectId="credit-test"
    captureDirect3D={capture}/></QueryClientProvider>);
  await act(async () => {});
  return capture;
}
const generate = () => screen.getByRole('button', { name: /Generate image/ }) as HTMLButtonElement;
const freeExport = () => screen.getByRole('button', { name: 'Export current 3D view · free' }) as HTMLButtonElement;

beforeEach(() => {
  state.choice = 'gpt-image-2'; state.availability = availability(0); state.directRender.mockClear();
  sessionStorage.clear();
  useAuthStore.setState({ user: { id: 'editor', email: 'editor@example.test', role: 'editor', is_active: true, render_credits: 0, created_at: '2026-10-29' }, isAuthenticated: true, isLoading: false });
});

describe('Globe image credit admission', () => {
  it('blocks a zero-credit editor with a clear reason while keeping free export working', async () => {
    const capture = await show();
    expect(generate().disabled).toBe(true);
    expect(screen.getByText(/Not enough image tokens.*at least 33.*0 available/i)).toBeTruthy();
    expect(freeExport().disabled).toBe(false);
    fireEvent.click(generate()); expect(state.directRender).not.toHaveBeenCalled();
    fireEvent.click(freeExport());
    await waitFor(() => expect(capture).toHaveBeenCalledWith({ includeGeometryPasses: false, maxLongEdge: 2048 }));
    await waitFor(() => expect(screen.getByAltText('Enlarged render')).toBeTruthy());
    expect(state.directRender).not.toHaveBeenCalled();
  });
  it('allows an editor with enough server-effective weekly tokens even when cached auth says zero', async () => {
    state.availability = availability(1000); await show(); expect(generate().disabled).toBe(false);
  });
  it('allows the server-exempt admin with zero tokens', async () => {
    useAuthStore.setState({ user: { ...useAuthStore.getState().user!, role: 'admin' } });
    state.availability = availability(0, true); await show(); expect(generate().disabled).toBe(false);
  });
  it('checks the total minimum for every engine in a multi-image bundle', async () => {
    state.choice = 'compare-all-three'; state.availability = availability(100); await show();
    expect(generate().disabled).toBe(true);
    expect(screen.getByText(/at least 165.*100 available/i)).toBeTruthy();
    expect(freeExport().disabled).toBe(false);
  });
  it('waits for auth and balance discovery without claiming an unknown balance is zero', async () => {
    state.availability = null; useAuthStore.setState({ user: null, isLoading: true }); await show();
    expect(generate().disabled).toBe(true);
    expect(screen.getByText(/Checking image credits/i)).toBeTruthy();
    expect(screen.queryByText(/Not enough image tokens/i)).toBeNull();
    expect(freeExport().disabled).toBe(false);
  });
  it('keeps a server credit-check failure distinct from a zero balance', async () => {
    state.availability = { default_model: 'gpt-image-2', models: [{ id: 'gpt-image-2', available: true }] };
    await show();
    expect(generate().disabled).toBe(true);
    expect(screen.getByText(/Image credits could not be checked/)).toBeTruthy();
    expect(screen.queryByText(/Not enough image tokens/i)).toBeNull();
    expect(freeExport().disabled).toBe(false);
  });
  it('waits for authentication even if a cached metadata result has a zero balance', async () => {
    useAuthStore.setState({ isLoading: true }); await show();
    expect(generate().disabled).toBe(true);
    expect(screen.getByText(/Checking image credits/i)).toBeTruthy();
    expect(screen.queryByText(/Not enough image tokens/i)).toBeNull();
  });
});
