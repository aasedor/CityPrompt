import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render as rtlRender, screen, waitFor, fireEvent } from '@testing-library/react';
import type { ReactElement } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// The panel calls useQueryClient (Place invalidates the project/zone queries).
const render = (ui: ReactElement) => rtlRender(
  <QueryClientProvider client={new QueryClient()}>{ui}</QueryClientProvider>,
);
import { LegoBuilderPanel } from './LegoBuilderPanel';
import type { LegoAssemblyPlan } from './legoAssemblyApi';
import type { SiteZone } from '@/types';

// ---------------------------------------------------------------------------
// Mocks (same patterns as LegoAssemblyPreview.test.tsx)
// ---------------------------------------------------------------------------

const { apiGet, apiPost, apiPut, apiDelete } = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}));

vi.mock('@/services/api', () => ({
  api: { get: apiGet, post: apiPost, put: apiPut, delete: apiDelete },
  resolveApiFileUrl: (url: string) => url,
  getApiErrorMessage: (error: unknown, fallback = 'Something went wrong') => {
    const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
    return typeof detail === 'string' ? detail : fallback;
  },
}));

// Deterministic catalogue entry so default width/depth/floors are known.
vi.mock('@/components/viewer/aestheticCatalog', () => ({
  BUILDING_AESTHETIC_OPTIONS_V2: [
    {
      id: 'nordic_timber_midrise',
      label: 'Nordic Timber Midrise',
      description: 'Mass-timber midrise for tests',
      photoUrl: '/archetypes/buildings/nordic_timber_midrise/variant_0.png',
      suggestedWidth_m: 32,
      suggestedDepth_m: 20,
      minFloors: 4,
      maxFloors: 8,
      variants: [],
    },
  ],
}));

// jsdom has no WebGL — keep the r3f Canvas (mounted after successful plans)
// completely inert. The stubs never render their children.
vi.mock('@react-three/fiber', () => ({
  Canvas: () => null,
}));
vi.mock('@react-three/drei', () => ({
  Bounds: () => null,
  Grid: () => null,
  Html: () => null,
  OrbitControls: () => null,
  useGLTF: Object.assign(() => ({ scene: {} }), { preload: () => {} }),
  useProgress: () => ({ progress: 0 }),
}));

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function makeZone(overrides: Partial<SiteZone> = {}): SiteZone {
  return {
    id: 'zone-1',
    project_id: 'proj-1',
    zone_type: 'building',
    coordinates: [
      [-114.062, 51.045],
      [-114.061, 51.045],
      [-114.061, 51.046],
      [-114.062, 51.046],
    ],
    color: '#ff0000',
    properties: { development_archetype_id: 'nordic_timber_midrise' },
    sort_order: 0,
    created_at: '2026-07-13T00:00:00Z',
    updated_at: '2026-07-13T00:00:00Z',
    ...overrides,
  };
}

const planFixture: LegoAssemblyPlan = {
  version: 1,
  family: 'nordic_timber_midrise_family',
  archetype_id: 'nordic_timber_midrise',
  reuse_keys: ['nordic_timber_midrise'],
  target: { width_m: 32, depth_m: 20, floors: 6 },
  assembled_height_m: 21.4,
  instances: [
    {
      asset_id: 'mod-podium',
      asset_name: 'Podium',
      model_url: '/models/podium.glb',
      family: 'nordic_timber_midrise_family',
      role: 'podium',
      level: 0,
      position: [0, 0, 0],
      rotation_degrees: 0,
      scale: [1, 1, 1],
      native_dimensions_m: [32, 20, 4],
    },
  ],
  fit: { scale_x: 1, scale_y: 1, score: 0.87 },
};

function make422(detail: string) {
  return Object.assign(new Error('Unprocessable'), {
    response: { status: 422, data: { detail } },
  });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('LegoBuilderPanel', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('plans one request per buildable zone on mount and shows the assembled count', async () => {
    apiPost.mockResolvedValue({ data: planFixture });

    const zones = [
      makeZone({ id: 'z-building' }),
      makeZone({
        id: 'z-res',
        zone_type: 'residential',
        properties: { development_archetype_id: 'parkside_terraces', floors: 5 },
      }),
      // Not buildable — no plan request must be issued for it.
      makeZone({ id: 'z-road', zone_type: 'road', properties: {} }),
    ];

    render(<LegoBuilderPanel zones={zones} onClose={vi.fn()} />);

    await waitFor(() => expect(apiPost).toHaveBeenCalledTimes(2));

    // Catalogue hit: suggested dims + floor midpoint of 4..8.
    expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/plan',
      expect.objectContaining({
        target_width_m: 32,
        target_depth_m: 20,
        target_floors: 6,
        allow_setback: true,
        archetype_id: 'nordic_timber_midrise',
      }),
    );
    // No catalogue hit: 24x18 fallbacks, floors from the zone properties.
    expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/plan',
      expect.objectContaining({
        target_width_m: 24,
        target_depth_m: 18,
        target_floors: 5,
        archetype_id: 'parkside_terraces',
      }),
    );

    expect(await screen.findByText(/Assembled 2/)).toBeInTheDocument();
    expect(screen.getByText(/No family 0/)).toBeInTheDocument();
    expect(screen.getByText(/Skipped 0/)).toBeInTheDocument();
  });

  it('shows no-family rows and one deduplicated command hint on mixed success/422', async () => {
    apiPost.mockImplementation((_url: string, body: { archetype_id?: string }) =>
      body.archetype_id?.startsWith('parkside_terraces')
        ? Promise.reject(make422('No module family covers archetype parkside_terraces.'))
        : Promise.resolve({ data: planFixture }),
    );

    const zones = [
      makeZone({ id: 'z-ok' }),
      makeZone({ id: 'z-missing-1', properties: { development_archetype_id: 'parkside_terraces' } }),
      // Same base archetype via a variant suffix — the hint must list it once.
      makeZone({ id: 'z-missing-2', properties: { development_archetype_id: 'parkside_terraces_variant_2' } }),
    ];

    render(<LegoBuilderPanel zones={zones} onClose={vi.fn()} />);

    expect(await screen.findByText(/Assembled 1/)).toBeInTheDocument();
    expect(screen.getByText(/No family 2/)).toBeInTheDocument();

    // Both failed rows surface the backend detail.
    expect(screen.getAllByText(/No module family covers archetype parkside_terraces\./)).toHaveLength(2);

    // One shared hint box listing the DISTINCT missing archetype ids.
    const pre = document.querySelector('pre');
    expect(pre?.textContent).toContain('generate_family.py --archetype-id parkside_terraces');
    expect(pre?.textContent).toContain('import_manifest.py build/archetypes/parkside_terraces');
    expect(pre?.textContent?.match(/--archetype-id parkside_terraces/g)).toHaveLength(1);
    expect(screen.getByRole('button', { name: /copy commands/i })).toBeInTheDocument();
  });

  it('saves recipes only for zones with building ids and reports the saved count', async () => {
    apiPost.mockImplementation((url: string) =>
      url.includes('/recipes/')
        ? Promise.resolve({ data: { status: 'saved', building_id: 'bldg-1', legoAssembly: {} } })
        : Promise.resolve({ data: planFixture }),
    );

    const zones = [
      makeZone({ id: 'z-with-building', building_id: 'bldg-1' }),
      makeZone({ id: 'z-without-building' }),
    ];

    render(<LegoBuilderPanel zones={zones} onClose={vi.fn()} />);
    expect(await screen.findByText(/Assembled 2/)).toBeInTheDocument();

    const saveButton = screen.getByRole('button', { name: /save all recipes/i });
    expect(saveButton).toBeEnabled();
    fireEvent.click(saveButton);

    await waitFor(() => expect(screen.getByText('Saved 1 of 1 recipe')).toBeInTheDocument());

    const recipeCalls = apiPost.mock.calls.filter(([url]) => String(url).includes('/recipes/'));
    expect(recipeCalls).toHaveLength(1);
    expect(recipeCalls[0][0]).toBe('/api/v1/lego-assembly/recipes/bldg-1');
    expect(recipeCalls[0][1]).toEqual(
      expect.objectContaining({
        schema_version: 1,
        module_family: 'nordic_timber_midrise_family',
        archetype_id: 'nordic_timber_midrise',
        instances: planFixture.instances,
        target: planFixture.target,
      }),
    );
  });

  it('disables Save all recipes with a tooltip when no assembled zone has a building', async () => {
    apiPost.mockResolvedValue({ data: planFixture });

    render(<LegoBuilderPanel zones={[makeZone()]} onClose={vi.fn()} />);
    expect(await screen.findByText(/Assembled 1/)).toBeInTheDocument();

    const saveButton = screen.getByRole('button', { name: /save all recipes/i });
    expect(saveButton).toBeDisabled();
    expect(saveButton.getAttribute('title')).toContain('No assembled zone has a generated building yet');
  });

  it('still lists (but does not place) buildable zones without coordinates', async () => {
    apiPost.mockResolvedValue({ data: planFixture });

    render(
      <LegoBuilderPanel
        zones={[makeZone({ id: 'z-nocoords', coordinates: [] as number[][] })]}
        onClose={vi.fn()}
      />,
    );

    expect(await screen.findByText(/Assembled 1/)).toBeInTheDocument();
    expect(screen.getByText(/Skipped 1/)).toBeInTheDocument();
    expect(screen.getByText(/not placed in the scene/i)).toBeInTheDocument();
  });

  it('Place all posts every assembled zone to the place endpoint and badges the rows', async () => {
    apiPost.mockImplementation((url: string) =>
      url.includes('/place/')
        ? Promise.resolve({ data: { status: 'placed', zone_id: 'z', building_id: 'b', building_created: true } })
        : Promise.resolve({ data: planFixture }),
    );

    const zones = [
      makeZone({ id: 'z-a' }),
      makeZone({ id: 'z-b', building_id: 'bldg-existing' }),
    ];
    render(<LegoBuilderPanel zones={zones} onClose={vi.fn()} />);
    expect(await screen.findByText(/Assembled 2/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /place all/i }));

    await waitFor(() => expect(screen.getByText('Placed 2 of 2 zones on the map')).toBeInTheDocument());
    expect(screen.getAllByText('placed')).toHaveLength(2);

    const placeCalls = apiPost.mock.calls.filter(([url]) => String(url).includes('/place/'));
    expect(placeCalls.map(([url]) => url)).toEqual(
      expect.arrayContaining([
        '/api/v1/lego-assembly/place/z-a',
        '/api/v1/lego-assembly/place/z-b',
      ]),
    );
    // Recipe payload + the created building's display name.
    expect(placeCalls[0][1]).toEqual(
      expect.objectContaining({
        schema_version: 1,
        module_family: 'nordic_timber_midrise_family',
        instances: planFixture.instances,
        building_name: expect.any(String),
      }),
    );
  });

  it('per-row Place places one zone even without a building id and marks failures retryable', async () => {
    apiPost.mockImplementation((url: string) =>
      url.includes('/place/z-fail')
        ? Promise.reject(make422('planner said no'))
        : url.includes('/place/')
          ? Promise.resolve({ data: { status: 'placed', zone_id: 'z-ok', building_id: 'b', building_created: true } })
          : Promise.resolve({ data: planFixture }),
    );

    render(
      <LegoBuilderPanel
        zones={[makeZone({ id: 'z-ok' }), makeZone({ id: 'z-fail' })]}
        onClose={vi.fn()}
      />,
    );
    expect(await screen.findByText(/Assembled 2/)).toBeInTheDocument();

    const placeButtons = screen.getAllByRole('button', { name: /^place$/i });
    expect(placeButtons).toHaveLength(2);
    fireEvent.click(placeButtons[0]);
    await waitFor(() => expect(screen.getByText('placed')).toBeInTheDocument());

    fireEvent.click(screen.getAllByRole('button', { name: /^place$/i })[0]);
    await waitFor(() => expect(screen.getByRole('button', { name: /retry place/i })).toBeInTheDocument());
    expect(screen.getByText('planner said no')).toBeInTheDocument();
  });
});
