import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render as rtlRender, screen, waitFor, fireEvent } from '@testing-library/react';
import type { ReactElement } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// The panel calls useQueryClient (Place invalidates the project/zone queries).
const render = (ui: ReactElement) => rtlRender(
  <QueryClientProvider client={new QueryClient()}>{ui}</QueryClientProvider>,
);
import { LegoAssemblyPreview } from './LegoAssemblyPreview';
import type { LegoAssemblyPlan, LegoAssemblyRecipe } from './legoAssemblyApi';
import type { SiteZone } from '@/types';

// ---------------------------------------------------------------------------
// Mocks
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

// jsdom has no WebGL — keep the r3f Canvas (mounted after a successful plan)
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
    coordinates: [[0, 0], [0, 1], [1, 1]],
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
    {
      asset_id: 'mod-floor',
      asset_name: 'Repeating floor',
      model_url: '/models/floor.glb',
      family: 'nordic_timber_midrise_family',
      role: 'floor',
      level: 1,
      position: [0, 0, 4],
      rotation_degrees: 0,
      scale: [1, 1, 1],
      native_dimensions_m: [32, 20, 3.2],
    },
  ],
  fit: { scale_x: 1.08, scale_y: 1, score: 0.87 },
};

const savedRecipeFixture: LegoAssemblyRecipe = {
  schema_version: 1,
  module_family: planFixture.family,
  archetype_id: 'nordic_timber_midrise',
  reuse_keys: planFixture.reuse_keys,
  target: planFixture.target,
  instances: planFixture.instances,
  assembled_height_m: planFixture.assembled_height_m,
  fit: planFixture.fit,
  assembled_preview_url: null,
};

function statRow(label: string): HTMLElement {
  const row = screen.getByText(label).closest('div');
  if (!row) throw new Error(`No stat row for label "${label}"`);
  return row;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('LegoAssemblyPreview', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('derives archetype label and default width/depth/floors from the catalogue', () => {
    render(<LegoAssemblyPreview zone={makeZone()} onClose={vi.fn()} />);

    expect(screen.getByText('Nordic Timber Midrise')).toBeInTheDocument();
    expect(screen.getByLabelText('Width (m)')).toHaveValue(32);
    expect(screen.getByLabelText('Depth (m)')).toHaveValue(20);
    // Floors default to the catalogue midpoint of minFloors 4 / maxFloors 8.
    expect(screen.getByText('6')).toBeInTheDocument();
    // No buildingId — the composer must not try to fetch a recipe.
    expect(apiGet).not.toHaveBeenCalled();
  });

  it('steps floors up and down and clamps at the minimum', () => {
    const { unmount } = render(<LegoAssemblyPreview zone={makeZone()} onClose={vi.fn()} />);

    fireEvent.click(screen.getByRole('button', { name: 'More floors' }));
    expect(screen.getByText('7')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Fewer floors' }));
    fireEvent.click(screen.getByRole('button', { name: 'Fewer floors' }));
    expect(screen.getByText('5')).toBeInTheDocument();

    unmount();

    // At the clamp floor (1) the decrement control is disabled.
    render(
      <LegoAssemblyPreview
        zone={makeZone({ properties: { development_archetype_id: 'nordic_timber_midrise', floors: 1 } })}
        onClose={vi.fn()}
      />,
    );
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Fewer floors' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'More floors' })).toBeEnabled();
  });

  it('shows generation guidance only for a missing-family planning failure', async () => {
    apiPost.mockRejectedValueOnce(
      Object.assign(new Error('Unprocessable'), {
        response: {
          status: 422,
          data: {
            detail: {
              code: 'family_not_found',
              message: 'No module family covers archetype nordic_timber_midrise.',
            },
          },
        },
      }),
    );

    render(<LegoAssemblyPreview zone={makeZone()} onClose={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /auto assemble/i }));

    expect(
      await screen.findByText('No module family covers archetype nordic_timber_midrise.'),
    ).toBeInTheDocument();
    expect(screen.getByText(/No module family covers this archetype yet/)).toBeInTheDocument();
    expect(
      screen.getByText(/generate_family\.py --archetype-id nordic_timber_midrise/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/import_manifest\.py build\/archetypes\/nordic_timber_midrise/),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /copy commands/i })).toBeInTheDocument();
    // No plan — the canvas placeholder stays up.
    expect(screen.getByText(/Choose Auto Assemble/)).toBeInTheDocument();
  });

  it('shows installed-family fit guidance without generation commands when the target is incompatible', async () => {
    apiPost.mockRejectedValueOnce(
      Object.assign(new Error('Unprocessable'), {
        response: {
          status: 422,
          data: {
            detail: {
              code: 'family_incompatible',
              message: 'Industrial Brick Brewery supports 40 × 26 m and 2–5 floors.',
              supported_families: [{
                family: 'industrial-brick-brewery-v1-renderlocked',
                widths_m: [40],
                depths_m: [26],
                min_floors: 2,
                max_floors: 5,
              }],
            },
          },
        },
      }),
    );

    render(<LegoAssemblyPreview zone={makeZone()} onClose={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /auto assemble/i }));

    expect(await screen.findByText(/Industrial Brick Brewery supports/)).toBeInTheDocument();
    expect(screen.getByText(/matching family is installed/i)).toBeInTheDocument();
    expect(screen.getByText(/industrial-brick-brewery-v1-renderlocked: 40 × 26 m; 2–5 floors/i)).toBeInTheDocument();
    expect(screen.queryByText(/No module family covers this archetype yet/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/generate_family\.py/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /copy commands/i })).not.toBeInTheDocument();
  });

  it('shows family, fit score, module count and a scale warning after a successful plan', async () => {
    apiPost.mockResolvedValueOnce({ data: planFixture });

    render(<LegoAssemblyPreview zone={makeZone()} onClose={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /auto assemble/i }));

    expect(await screen.findByText('nordic_timber_midrise_family')).toBeInTheDocument();
    expect(statRow('Fit score')).toHaveTextContent('0.87');
    expect(statRow('Height')).toHaveTextContent('21.4 m');
    expect(statRow('Modules')).toHaveTextContent('2');

    // scale_x = 1.08 deviates from 1 by more than 5% — warning chip appears.
    expect(screen.getByText(/stretched to fit \(108% × 100%\)/)).toBeInTheDocument();

    // The assemble button flips to "Reassemble".
    expect(screen.getByRole('button', { name: /reassemble/i })).toBeInTheDocument();

    // The plan request carried the archetype context and the setback flag.
    expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/plan',
      expect.objectContaining({
        target_width_m: 32,
        target_depth_m: 20,
        target_floors: 6,
        allow_setback: false,
        archetype_id: 'nordic_timber_midrise',
      }),
    );
  });

  it('disables Save with an explanatory tooltip when the zone has no generated building', () => {
    render(<LegoAssemblyPreview zone={makeZone()} onClose={vi.fn()} />);

    const saveButton = screen.getByRole('button', { name: /save assembly recipe/i });
    expect(saveButton).toBeDisabled();
    expect(saveButton.getAttribute('title')).toContain('no generated building yet');
  });

  it('saves a schema_version 1 recipe with the plan instances when a buildingId is provided', async () => {
    apiGet.mockResolvedValue({ data: { legoAssembly: null } });
    apiPost.mockImplementation((url: string) =>
      url.includes('/recipes/')
        ? Promise.resolve({ data: { status: 'saved', building_id: 'bldg-1', legoAssembly: savedRecipeFixture } })
        : Promise.resolve({ data: planFixture }),
    );

    render(
      <LegoAssemblyPreview
        zone={makeZone({ building_id: 'bldg-1' })}
        buildingId="bldg-1"
        onClose={vi.fn()}
      />,
    );

    // The composer checks for an existing recipe on open.
    await waitFor(() => expect(apiGet).toHaveBeenCalledWith('/api/v1/lego-assembly/recipes/bldg-1'));

    fireEvent.click(screen.getByRole('button', { name: /auto assemble/i }));
    const saveButton = screen.getByRole('button', { name: /save assembly recipe/i });
    await waitFor(() => expect(saveButton).toBeEnabled());

    fireEvent.click(saveButton);
    await waitFor(() =>
      expect(apiPost).toHaveBeenCalledWith(
        '/api/v1/lego-assembly/recipes/bldg-1',
        expect.objectContaining({
          schema_version: 1,
          module_family: 'nordic_timber_midrise_family',
          archetype_id: 'nordic_timber_midrise',
          instances: planFixture.instances,
          target: planFixture.target,
        }),
      ),
    );

    // The saved-recipe badge appears once the save resolves.
    expect(await screen.findByText('Saved recipe')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Load' })).toBeInTheDocument();
  });

  it('Place on map posts the recipe zone-addressed and enables Clear via the returned building', async () => {
    apiPost.mockImplementation((url: string) =>
      url.includes('/place/')
        ? Promise.resolve({ data: { status: 'placed', zone_id: 'zone-1', building_id: 'bldg-new', building_created: true } })
        : Promise.resolve({ data: planFixture }),
    );
    apiDelete.mockResolvedValue({ data: { status: 'removed' } });

    // No buildingId: the zone has never been through generate-all.
    render(<LegoAssemblyPreview zone={makeZone()} onClose={vi.fn()} />);

    const placeButton = screen.getByRole('button', { name: /place on map/i });
    expect(placeButton).toBeDisabled();

    fireEvent.click(screen.getByRole('button', { name: /auto assemble/i }));
    await waitFor(() => expect(placeButton).toBeEnabled());

    fireEvent.click(placeButton);
    await waitFor(() =>
      expect(apiPost).toHaveBeenCalledWith(
        '/api/v1/lego-assembly/place/zone-1',
        expect.objectContaining({
          schema_version: 1,
          module_family: 'nordic_timber_midrise_family',
          instances: planFixture.instances,
          building_name: 'Nordic Timber Midrise',
        }),
      ),
    );
    expect(await screen.findByRole('button', { name: /placed — place again/i })).toBeInTheDocument();

    // Clear targets the building the endpoint just created/linked.
    fireEvent.click(screen.getByRole('button', { name: /clear saved recipe/i }));
    await waitFor(() =>
      expect(apiDelete).toHaveBeenCalledWith('/api/v1/lego-assembly/recipes/bldg-new'),
    );
  });

  it('shows an existing saved recipe on open and Load re-plans with its targets', async () => {
    const savedTargets: LegoAssemblyRecipe = {
      ...savedRecipeFixture,
      target: { width_m: 28, depth_m: 16, floors: 9 },
    };
    apiGet.mockResolvedValue({ data: { legoAssembly: savedTargets } });
    apiPost.mockResolvedValue({ data: planFixture });

    render(
      <LegoAssemblyPreview
        zone={makeZone({ building_id: 'bldg-1' })}
        buildingId="bldg-1"
        onClose={vi.fn()}
      />,
    );

    expect(await screen.findByText('Saved recipe')).toBeInTheDocument();
    expect(screen.getByText(/9 floors/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Load' }));
    await waitFor(() =>
      expect(apiPost).toHaveBeenCalledWith(
        '/api/v1/lego-assembly/plan',
        expect.objectContaining({
          target_width_m: 28,
          target_depth_m: 16,
          target_floors: 9,
          allow_setback: false,
        }),
      ),
    );

    // The saved targets are restored into the editable inputs.
    await waitFor(() => expect(screen.getByLabelText('Width (m)')).toHaveValue(28));
    expect(screen.getByLabelText('Depth (m)')).toHaveValue(16);
  });
});
