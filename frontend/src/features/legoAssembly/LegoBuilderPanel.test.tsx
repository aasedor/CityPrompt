import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render as rtlRender, screen, waitFor, fireEvent } from '@testing-library/react';
import { StrictMode, type ReactElement } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// The panel calls useQueryClient (Place invalidates the project/zone queries).
const render = (ui: ReactElement, client = new QueryClient()) => rtlRender(
  <QueryClientProvider client={client}>{ui}</QueryClientProvider>,
);
import { LegoBuilderPanel } from './LegoBuilderPanel';
import type { LegoAssemblyPlan } from './legoAssemblyApi';
import type { SiteZone } from '@/types';
import { resetProjectCommunityCompileCoordinatorForTests } from './projectCommunityCompile';

// ---------------------------------------------------------------------------
// Mocks (same patterns as LegoAssemblyPreview.test.tsx)
// ---------------------------------------------------------------------------

const { apiGet, apiPost, apiPut, apiDelete, siteZonesList } = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
  siteZonesList: vi.fn(),
}));

vi.mock('@/services/api', () => ({
  api: { get: apiGet, post: apiPost, put: apiPut, delete: apiDelete },
  siteZonesApi: {
    list: siteZonesList,
    update: (zoneId: string, body: unknown) => apiPut(`/api/v1/site-zones/${zoneId}`, body),
  },
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
  ROADWAY_AESTHETIC_OPTIONS_V2: [],
  GREEN_SPACE_AESTHETIC_OPTIONS_V2: [],
  PLAZA_AESTHETIC_OPTIONS_V2: [],
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

function make422(detail: unknown) {
  return Object.assign(new Error('Unprocessable'), {
    response: { status: 422, data: { detail } },
  });
}

function make409(detail: string) {
  return Object.assign(new Error('Conflict'), {
    response: { status: 409, data: { detail } },
  });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('LegoBuilderPanel', () => {
  beforeEach(() => {
    resetProjectCommunityCompileCoordinatorForTests();
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

    // The drawn polygon is authoritative for dimensions; catalogue metadata
    // still supplies the floor midpoint and architectural identity.
    expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/plan',
      expect.objectContaining({
        target_width_m: 110.5,
        target_depth_m: 70,
        target_floors: 6,
        allow_setback: false,
        allow_forced_fit: false,
        archetype_id: 'nordic_timber_midrise',
      }),
    );
    // A missing catalogue entry still uses the drawn polygon dimensions.
    expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/plan',
      expect.objectContaining({
        target_width_m: 110.5,
        target_depth_m: 70,
        target_floors: 5,
        archetype_id: 'parkside_terraces',
      }),
    );

    expect(await screen.findByText(/Detailed 2/)).toBeInTheDocument();
    expect(screen.getByText(/Massing ready 0/)).toBeInTheDocument();
    expect(screen.getByText(/Needs footprint 0/)).toBeInTheDocument();
    expect(screen.getByText('2 buildings · 0 parks · 1 streets')).toBeInTheDocument();
  });

  it('runs the complete atomic compile without a second click from the top-level workflow', async () => {
    apiPost.mockImplementation((url: string) => (
      url === '/api/v1/lego-assembly/place-community'
        ? Promise.resolve({
            data: {
              status: 'compiled',
              compiled_at: '2026-08-03T01:00:00Z',
              counts: { building: 1, park: 0, street: 0 },
              residual_landscape: {
                boundary_count: 1,
                derived_boundary_count: 0,
                area_sqm: 400,
                placement_count: 2,
              },
              items: [{
                zone_id: 'auto-building',
                kind: 'building',
                building_id: 'auto-building-model',
                building_created: true,
                generator: 'lego_assembly',
              }],
            },
          })
        : Promise.resolve({ data: planFixture })
    ));

    render(
      <LegoBuilderPanel
        zones={[makeZone({ id: 'auto-building' })]}
        autoGenerate
        onClose={vi.fn()}
      />,
    );

    await waitFor(() => expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/place-community',
      {
        items: [expect.objectContaining({
          zone_id: 'auto-building',
          recipe: expect.any(Object),
        })],
      },
    ));
    expect(await screen.findByText(/landscaped 400 m² of residual site with 2 trees/i)).toBeInTheDocument();
  });

  it('starts one planning and compile pass under React StrictMode', async () => {
    apiPost.mockImplementation((url: string) => (
      url === '/api/v1/lego-assembly/place-community'
        ? Promise.resolve({
            data: {
              status: 'compiled',
              compiled_at: '2026-08-03T01:00:00Z',
              counts: { building: 1, park: 0, street: 0 },
              items: [{
                zone_id: 'strict-building',
                kind: 'building',
                building_id: 'strict-building-model',
                building_created: true,
                generator: 'lego_assembly',
              }],
            },
          })
        : Promise.resolve({ data: planFixture })
    ));

    render(
      <StrictMode>
        <LegoBuilderPanel
          zones={[makeZone({ id: 'strict-building' })]}
          autoGenerate
          onClose={vi.fn()}
        />
      </StrictMode>,
    );

    expect(await screen.findByText(/Built 1 detailed building/)).toBeInTheDocument();
    expect(apiPost.mock.calls.filter(
      ([url]) => url === '/api/v1/lego-assembly/plan',
    )).toHaveLength(1);
    expect(apiPost.mock.calls.filter(
      ([url]) => url === '/api/v1/lego-assembly/place-community',
    )).toHaveLength(1);
    expect(screen.getByText('placed')).toBeInTheDocument();
  });

  it('keeps Rebuild from starting while the atomic community compile is in flight', async () => {
    let finishCompile!: (value: unknown) => void;
    const pendingCompile = new Promise((resolve) => {
      finishCompile = resolve;
    });
    apiPost.mockImplementation((url: string) => (
      url === '/api/v1/lego-assembly/place-community'
        ? pendingCompile
        : Promise.resolve({ data: planFixture })
    ));

    render(<LegoBuilderPanel zones={[makeZone({ id: 'race-building' })]} onClose={vi.fn()} />);
    expect(await screen.findByText(/Detailed 1/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^generate to 3d$/i }));

    await waitFor(() => expect(apiPost.mock.calls.filter(
      ([url]) => url === '/api/v1/lego-assembly/place-community',
    )).toHaveLength(1));
    const rebuild = screen.getByRole('button', { name: /rebuild buildings/i });
    expect(rebuild).toBeDisabled();
    fireEvent.click(rebuild);
    expect(apiPost.mock.calls.filter(([url]) => url === '/api/v1/lego-assembly/plan')).toHaveLength(1);

    finishCompile({
      data: {
        status: 'compiled',
        compiled_at: '2026-08-14T13:00:00Z',
        counts: { building: 1, park: 0, street: 0 },
        items: [{
          zone_id: 'race-building',
          kind: 'building',
          building_id: 'race-building-model',
          building_created: true,
          generator: 'lego_assembly',
        }],
      },
    });
    expect(await screen.findByText(/Built 1 detailed building/)).toBeInTheDocument();
  });

  it('recovers an incremental build without recompiling an already-complete sibling', async () => {
    const original = makeZone({ id: 'changing-building' });
    const alreadyCompiled = makeZone({
      id: 'steady-building',
      building_id: 'steady-model',
      properties: {
        development_archetype_id: 'nordic_timber_midrise',
        community_3d: {
          schema_version: 1,
          state: 'compiled',
          kind: 'building',
          generator: 'lego_assembly',
          compiled_at: '2026-08-14T11:55:00Z',
        },
      },
    });
    const refreshed = {
      ...original,
      updated_at: '2026-08-14T12:05:00Z',
      properties: { ...original.properties, floors: 8 },
    };
    const refreshedSteady = {
      ...alreadyCompiled,
      updated_at: '2026-08-14T12:05:00Z',
    };
    siteZonesList.mockResolvedValue([refreshed, refreshedSteady]);
    let compileCalls = 0;
    apiPost.mockImplementation((url: string) => {
      if (url === '/api/v1/lego-assembly/plan') return Promise.resolve({ data: planFixture });
      if (url === '/api/v1/lego-assembly/place-community') {
        compileCalls += 1;
        if (compileCalls === 1) {
          return Promise.reject(make409(
            'A Community 3D source zone changed while its 3D recipe was being prepared; refresh and retry.',
          ));
        }
        return Promise.resolve({
          data: {
            status: 'compiled',
            compiled_at: '2026-08-14T12:06:00Z',
            counts: { building: 1, park: 0, street: 0 },
            items: [{
              zone_id: refreshed.id,
              kind: 'building',
              building_id: 'building-1',
              building_created: false,
              generator: 'lego_assembly',
            }],
          },
        });
      }
      return Promise.reject(new Error(`unexpected POST ${url}`));
    });

    render(<LegoBuilderPanel zones={[original, alreadyCompiled]} onClose={vi.fn()} />);
    expect(await screen.findByText(/Detailed 2/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^generate to 3d$/i }));

    expect(await screen.findByText(
      'Built 1 detailed building, 0 correct-size massing fallbacks, and 0 park/street layers',
    )).toBeInTheDocument();
    expect(siteZonesList).toHaveBeenCalledWith('proj-1');
    const compileRequests = apiPost.mock.calls.filter(([url]) => (
      url === '/api/v1/lego-assembly/place-community'
    ));
    expect(compileRequests).toHaveLength(2);
    expect(compileRequests[1][1]).toEqual({
      items: [expect.objectContaining({
        zone_id: refreshed.id,
        source_updated_at: refreshed.updated_at,
      })],
      scope_zone_ids: [refreshed.id, refreshedSteady.id],
    });
    expect(screen.queryByText(/changed while its 3D recipe/i)).not.toBeInTheDocument();
  });

  it('shows the refreshed massing state when a source edit changes detailed capability', async () => {
    const original = makeZone({ id: 'capability-change' });
    const refreshed = {
      ...original,
      updated_at: '2026-08-14T12:20:00Z',
      properties: { ...original.properties, floors: 14 },
    };
    siteZonesList.mockResolvedValue([refreshed]);
    let planCalls = 0;
    let compileCalls = 0;
    apiPost.mockImplementation((url: string) => {
      if (url === '/api/v1/lego-assembly/plan') {
        planCalls += 1;
        return planCalls === 1
          ? Promise.resolve({ data: planFixture })
          : Promise.reject(make422({
              code: 'family_incompatible',
              message: 'The reviewed family does not cover this refreshed footprint.',
            }));
      }
      if (url === '/api/v1/lego-assembly/place-community') {
        compileCalls += 1;
        if (compileCalls === 1) {
          return Promise.reject(make409(
            'A Community 3D source zone changed while its 3D recipe was being prepared; refresh and retry.',
          ));
        }
        return Promise.resolve({
          data: {
            status: 'compiled',
            compiled_at: '2026-08-14T12:21:00Z',
            counts: { building: 1, park: 0, street: 0 },
            items: [{
              zone_id: refreshed.id,
              kind: 'building',
              building_id: 'capability-change-model',
              building_created: true,
              generator: 'planned_massing',
            }],
          },
        });
      }
      return Promise.reject(new Error(`unexpected POST ${url}`));
    });

    render(<LegoBuilderPanel zones={[original]} onClose={vi.fn()} />);
    expect(await screen.findByText(/Detailed 1/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^generate to 3d$/i }));

    expect(await screen.findByText(
      'Built 0 detailed buildings, 1 correct-size massing fallback, and 0 park/street layers',
    )).toBeInTheDocument();
    expect(screen.getByText('3D massing')).toBeInTheDocument();
    expect(screen.queryByText('placed')).not.toBeInTheDocument();
    expect(screen.getByText(/reviewed family does not cover this refreshed footprint/i)).toBeInTheDocument();
  });

  it('uses the refetched post-compile revision for an immediate scene rebuild', async () => {
    const original = makeZone({ id: 'repeat-building' });
    const refreshed = { ...original, updated_at: '2026-08-14T12:10:00Z' };
    const client = new QueryClient();
    client.setQueryData(['site-zones', 'proj-1'], [original]);
    let compileCalls = 0;
    apiPost.mockImplementation((url: string) => {
      if (url === '/api/v1/lego-assembly/plan') return Promise.resolve({ data: planFixture });
      if (url === '/api/v1/lego-assembly/place-community') {
        compileCalls += 1;
        if (compileCalls === 1) {
          client.setQueryData(['site-zones', 'proj-1'], [refreshed]);
        }
        return Promise.resolve({
          data: {
            status: 'compiled',
            compiled_at: `2026-08-14T12:${10 + compileCalls}:00Z`,
            counts: { building: 1, park: 0, street: 0 },
            items: [{
              zone_id: original.id,
              kind: 'building',
              building_id: 'building-1',
              building_created: compileCalls === 1,
              generator: 'lego_assembly',
            }],
          },
        });
      }
      return Promise.reject(new Error(`unexpected POST ${url}`));
    });

    render(<LegoBuilderPanel zones={[original]} onClose={vi.fn()} />, client);
    expect(await screen.findByText(/Detailed 1/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^generate to 3d$/i }));
    expect(await screen.findByRole('button', { name: /rebuild current 3d scene/i })).toBeEnabled();
    fireEvent.click(screen.getByRole('button', { name: /rebuild current 3d scene/i }));

    await waitFor(() => expect(compileCalls).toBe(2));
    const compileRequests = apiPost.mock.calls.filter(([url]) => (
      url === '/api/v1/lego-assembly/place-community'
    ));
    expect(compileRequests[1][1]).toEqual({
      items: [expect.objectContaining({
        zone_id: original.id,
        source_updated_at: refreshed.updated_at,
      })],
    });
  });

  it('compiles planner parks and streets without treating framework overlays as buildings', async () => {
    apiPost.mockImplementation((url: string) => (
      url === '/api/v1/lego-assembly/place-community'
        ? Promise.resolve({
            data: {
              status: 'compiled',
              compiled_at: '2026-07-17T01:00:00Z',
              counts: { building: 1, park: 2, street: 1 },
              residual_landscape: {
                boundary_count: 1,
                derived_boundary_count: 0,
                area_sqm: 1234,
                placement_count: 3,
              },
              items: [
                {
                  zone_id: 'z-building',
                  kind: 'building',
                  building_id: 'z-building-model',
                  building_created: true,
                  generator: 'lego_assembly',
                },
                {
                  zone_id: 'z-park',
                  kind: 'park',
                  building_id: null,
                  building_created: false,
                  generator: 'park_kit',
                },
                {
                  zone_id: 'z-street',
                  kind: 'street',
                  building_id: null,
                  building_created: false,
                  generator: 'street_section',
                },
                {
                  zone_id: 'z-plaza',
                  kind: 'park',
                  building_id: null,
                  building_created: false,
                  generator: 'park_kit',
                },
              ],
            },
          })
        : Promise.resolve({ data: planFixture })
    ));

    const zones = [
      makeZone({ id: 'z-building', properties: { _plan_role: 'building', development_archetype_id: 'nordic_timber_midrise' } }),
      makeZone({
        id: 'z-park',
        zone_type: 'green_space',
        name: 'Central Park',
        properties: { _plan_role: 'open_space', _plan_scenario: 'economic' },
      }),
      makeZone({
        id: 'z-street',
        zone_type: 'road',
        name: 'Main Street',
        properties: { _plan_role: 'street', _plan_scenario: 'economic' },
      }),
      makeZone({
        id: 'z-plaza',
        zone_type: 'parking',
        name: 'Civic Plaza',
        properties: { plaza_archetype_id: 'formal_civic_plaza' },
      }),
      makeZone({
        id: 'z-framework',
        zone_type: 'development_area',
        properties: { _plan_role: 'framework_height' },
      }),
    ];

    render(<LegoBuilderPanel zones={zones} onClose={vi.fn()} />);
    await waitFor(() => expect(apiPost).toHaveBeenCalledTimes(1));
    expect(screen.getByText('1 buildings · 2 parks · 1 streets')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^generate to 3d$/i }));
    await waitFor(() => expect(screen.getByText(
      'Built 1 detailed building, 0 correct-size massing fallbacks, and 3 park/street layers; landscaped 1,234 m² of residual site with 3 trees',
    )).toBeInTheDocument());

    expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/place-community',
      {
        items: expect.arrayContaining([
          expect.objectContaining({
            zone_id: 'z-building',
            source_updated_at: '2026-07-13T00:00:00Z',
            recipe: expect.any(Object),
          }),
          { zone_id: 'z-park', source_updated_at: '2026-07-13T00:00:00Z' },
          { zone_id: 'z-street', source_updated_at: '2026-07-13T00:00:00Z' },
          { zone_id: 'z-plaza', source_updated_at: '2026-07-13T00:00:00Z' },
        ]),
      },
    );
    const compileCall = apiPost.mock.calls.find(([url]) => url === '/api/v1/lego-assembly/place-community');
    expect(compileCall?.[1]).not.toEqual(expect.objectContaining({
      items: expect.arrayContaining([expect.objectContaining({ zone_id: 'z-framework' })]),
    }));
  });

  it('compiles parks and streets directly without an image-generation stage', async () => {
    const park = makeZone({
      id: 'z-park-refresh',
      zone_type: 'green_space',
      properties: { _plan_role: 'open_space' },
    });
    const street = makeZone({
      id: 'z-street-refresh',
      zone_type: 'road',
      properties: { _plan_role: 'street' },
    });
    apiPost.mockImplementation((url: string) => (
      url === '/api/v1/lego-assembly/place-community'
        ? Promise.resolve({
            data: {
              status: 'compiled',
              compiled_at: '2026-08-04T02:01:00Z',
              counts: { building: 0, park: 1, street: 1 },
              items: [
                {
                  zone_id: 'z-park-refresh',
                  kind: 'park',
                  building_id: null,
                  building_created: false,
                  generator: 'park_kit',
                },
                {
                  zone_id: 'z-street-refresh',
                  kind: 'street',
                  building_id: null,
                  building_created: false,
                  generator: 'street_section',
                },
              ],
            },
          })
        : Promise.reject(new Error(`unexpected POST ${url}`))
    ));

    render(<LegoBuilderPanel zones={[park, street]} onClose={vi.fn()} />);
    fireEvent.click(await screen.findByRole('button', { name: /^generate to 3d$/i }));

    await waitFor(() => expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/place-community',
      {
        items: expect.arrayContaining([
          { zone_id: 'z-park-refresh', source_updated_at: '2026-07-13T00:00:00Z' },
          { zone_id: 'z-street-refresh', source_updated_at: '2026-07-13T00:00:00Z' },
        ]),
      },
    ));
    expect(screen.queryByText(/image calls?/i)).not.toBeInTheDocument();
    expect(await screen.findByText(/Built 0 detailed buildings.*2 park\/street layers/i)).toBeInTheDocument();
  });

  it('does not treat a missing legacy AI drape as work for an already compiled park', async () => {
    const park = makeZone({
      id: 'z-procedural-park',
      zone_type: 'green_space',
      properties: {
        _plan_role: 'open_space',
        community_3d: {
          schema_version: 1,
          state: 'compiled',
          kind: 'park',
          generator: 'park_kit',
          compiled_at: '2026-08-04T01:00:00Z',
        },
      },
    });
    render(<LegoBuilderPanel zones={[park]} onClose={vi.fn()} />);
    expect(await screen.findByText(/Archetype-driven procedural skin/i)).toBeInTheDocument();
    expect(screen.queryByText(/AI ground-drape image call/i)).not.toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it('shows missing families as normal upgrade-ready massing without developer commands', async () => {
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

    expect(await screen.findByText(/Detailed 1/)).toBeInTheDocument();
    expect(screen.getByText(/Massing ready 2/)).toBeInTheDocument();
    expect(screen.getAllByText(/Detailed family to add/)).toHaveLength(2);
    expect(screen.getAllByText((_content, node) => (
      node?.tagName === 'P'
      && Boolean(node.textContent?.includes('exact footprint and 4-floor height now'))
    ))).toHaveLength(2);
    expect(screen.getByText(/2 buildings use upgrade-ready massing/i)).toBeInTheDocument();
    expect(screen.getByText(/Nothing is blocked/i)).toBeInTheDocument();
    expect(screen.queryByText(/No module family covers archetype/i)).not.toBeInTheDocument();
    expect(document.querySelector('pre')).toBeNull();
    expect(screen.queryByRole('button', { name: /copy commands/i })).not.toBeInTheDocument();
  });

  it('treats an installed but incompatible family as normal correctly sized massing', async () => {
    apiPost.mockRejectedValue(make422({
      code: 'family_incompatible',
      message: 'Industrial Brick Brewery supports 40 × 26 m and 2–5 floors.',
      supported_families: [{
        family: 'industrial-brick-brewery-v1-renderlocked',
        widths_m: [40],
        depths_m: [26],
        min_floors: 2,
        max_floors: 5,
      }],
    }));

    render(<LegoBuilderPanel zones={[
      makeZone({
        id: 'z-incompatible',
        properties: {
          development_archetype_id: 'industrial_brick_brewery',
          floors: 6,
        },
      }),
    ]} onClose={vi.fn()} />);

    expect(await screen.findByText(/Industrial Brick Brewery supports 40 × 26 m and 2–5 floors/)).toBeInTheDocument();
    expect(screen.getByText(/Massing ready 1/)).toBeInTheDocument();
    expect(screen.queryByText(/Failed 1/)).not.toBeInTheDocument();
    expect(screen.getByText(/Detailed family outside its reviewed fit/)).toBeInTheDocument();
    expect(document.querySelector('pre')).toBeNull();
    expect(screen.queryByRole('button', { name: /copy commands/i })).not.toBeInTheDocument();
  });

  it('fails closed instead of compiling an unexpected planning error as massing', async () => {
    apiPost.mockImplementation((url: string, body: { archetype_id?: string }) => {
      if (url !== '/api/v1/lego-assembly/plan') {
        return Promise.reject(new Error(`unexpected POST ${url}`));
      }
      if (body.archetype_id === 'planner_outage') {
        return Promise.reject(Object.assign(new Error('Unavailable'), {
          response: { status: 500, data: { detail: 'Planner service unavailable' } },
        }));
      }
      return Promise.resolve({ data: planFixture });
    });

    render(<LegoBuilderPanel zones={[
      makeZone({ id: 'z-supported' }),
      makeZone({
        id: 'z-unexpected',
        properties: { development_archetype_id: 'planner_outage' },
      }),
    ]} autoGenerate onClose={vi.fn()} />);

    expect(await screen.findByText(/Needs review 1/)).toBeInTheDocument();
    expect(screen.getByText(/Planner service unavailable/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^generate to 3d$/i })).toBeDisabled();
    await waitFor(() => expect(apiPost.mock.calls.filter(
      ([url]) => url === '/api/v1/lego-assembly/place-community',
    )).toHaveLength(0));
    expect(screen.queryByText('3D massing')).not.toBeInTheDocument();
  });

  it('builds a grounded exact-footprint mass for a building whose detailed family is pending', async () => {
    apiPost.mockImplementation((url: string, body: { archetype_id?: string }) => {
      if (url === '/api/v1/lego-assembly/place-community') {
        return Promise.resolve({
          data: {
            status: 'compiled',
            compiled_at: '2026-07-17T01:00:00Z',
            counts: { building: 1, park: 1, street: 0 },
            items: [
              {
                zone_id: 'z-missing',
                kind: 'building',
                building_id: 'z-missing-model',
                building_created: true,
                generator: 'planned_massing',
              },
              {
                zone_id: 'z-park',
                kind: 'park',
                building_id: null,
                building_created: false,
                generator: 'park_kit',
              },
            ],
          },
        });
      }
      return body.archetype_id === 'parkside_terraces'
        ? Promise.reject(make422('No module family covers archetype parkside_terraces.'))
        : Promise.resolve({ data: planFixture });
    });

    const zones = [
      makeZone({
        id: 'z-missing',
        properties: { development_archetype_id: 'parkside_terraces', floors: 5 },
      }),
      makeZone({
        id: 'z-park',
        zone_type: 'green_space',
        properties: { _plan_role: 'open_space' },
      }),
    ];

    render(<LegoBuilderPanel zones={zones} onClose={vi.fn()} />);
    expect(await screen.findByText(/Massing ready 1/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^generate to 3d$/i }));

    await waitFor(() => expect(screen.getByText(
      'Built 0 detailed buildings, 1 correct-size massing fallback, and 1 park/street layer',
    )).toBeInTheDocument());
    expect(screen.getByText('3D massing')).toBeInTheDocument();

    const compileCall = apiPost.mock.calls.find(([url]) => url === '/api/v1/lego-assembly/place-community');
    expect(compileCall?.[1]).toEqual({
      items: expect.arrayContaining([
        { zone_id: 'z-missing', source_updated_at: '2026-07-13T00:00:00Z' },
        { zone_id: 'z-park', source_updated_at: '2026-07-13T00:00:00Z' },
      ]),
    });
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
    expect(await screen.findByText(/Detailed 2/)).toBeInTheDocument();

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
    expect(await screen.findByText(/Detailed 1/)).toBeInTheDocument();

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

    expect(await screen.findByText(/Detailed 1/)).toBeInTheDocument();
    expect(screen.getByText(/Needs footprint 1/)).toBeInTheDocument();
    expect(screen.getByText(/not placed in the scene/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^place$/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /rebuild current 3d scene/i })).toBeDisabled();
    expect(apiPost.mock.calls.some(([url]) => url === '/api/v1/lego-assembly/place-community')).toBe(false);
  });

  it('blocks the whole compile when one building in a mixed scene has no footprint', async () => {
    apiPost.mockResolvedValue({ data: planFixture });

    render(<LegoBuilderPanel zones={[
      makeZone({ id: 'z-valid' }),
      makeZone({ id: 'z-no-footprint', coordinates: [] as number[][] }),
      makeZone({ id: 'z-park', zone_type: 'green_space', properties: { _plan_role: 'open_space' } }),
    ]} autoGenerate onClose={vi.fn()} />);

    expect(await screen.findByText(/Needs footprint 1/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^generate to 3d$/i })).toBeDisabled();
    expect(apiPost.mock.calls.some(([url]) => url === '/api/v1/lego-assembly/place-community')).toBe(false);
    expect(screen.queryByText('placed')).not.toBeInTheDocument();
  });

  it('Build community posts every assembled building and badges the rows', async () => {
    apiPost.mockImplementation((url: string) =>
      url === '/api/v1/lego-assembly/place-community'
        ? Promise.resolve({
            data: {
              status: 'compiled',
              compiled_at: '2026-07-17T01:00:00Z',
              counts: { building: 2, park: 0, street: 0 },
              items: [
                {
                  zone_id: 'z-a',
                  kind: 'building',
                  building_id: 'z-a-model',
                  building_created: true,
                  generator: 'lego_assembly',
                },
                {
                  zone_id: 'z-b',
                  kind: 'building',
                  building_id: 'bldg-existing',
                  building_created: false,
                  generator: 'lego_assembly',
                },
              ],
            },
          })
        : Promise.resolve({ data: planFixture }),
    );

    const zones = [
      makeZone({ id: 'z-a' }),
      makeZone({ id: 'z-b', building_id: 'bldg-existing' }),
    ];
    render(<LegoBuilderPanel zones={zones} onClose={vi.fn()} />);
    expect(await screen.findByText(/Detailed 2/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^generate to 3d$/i }));

    await waitFor(() => expect(screen.getByText(
      'Built 2 detailed buildings, 0 correct-size massing fallbacks, and 0 park/street layers',
    )).toBeInTheDocument());
    expect(screen.getAllByText('placed')).toHaveLength(2);

    const compileCall = apiPost.mock.calls.find(([url]) => url === '/api/v1/lego-assembly/place-community');
    expect(compileCall?.[1]).toEqual(
      {
        items: expect.arrayContaining([
          expect.objectContaining({
            zone_id: 'z-a',
            recipe: expect.objectContaining({
              schema_version: 1,
              module_family: 'nordic_timber_midrise_family',
              instances: planFixture.instances,
              building_name: expect.any(String),
            }),
          }),
          expect.objectContaining({ zone_id: 'z-b', recipe: expect.any(Object) }),
        ]),
      },
    );
  });

  it('does not mark a malformed atomic response as placed', async () => {
    apiPost.mockImplementation((url: string) => (
      url === '/api/v1/lego-assembly/place-community'
        ? Promise.resolve({
            data: {
              status: 'compiled',
              compiled_at: '2026-07-17T01:00:00Z',
              counts: { building: 1, park: 0, street: 0 },
              items: [{
                zone_id: 'z-unlinked-response',
                kind: 'building',
                building_id: null,
                building_created: false,
                generator: 'lego_assembly',
              }],
            },
          })
        : Promise.resolve({ data: planFixture })
    ));

    render(<LegoBuilderPanel zones={[
      makeZone({ id: 'z-unlinked-response' }),
    ]} onClose={vi.fn()} />);
    expect(await screen.findByText(/Detailed 1/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^generate to 3d$/i }));

    expect(await screen.findByRole('button', { name: /retry place/i })).toBeInTheDocument();
    expect(screen.queryByText('placed')).not.toBeInTheDocument();
    expect(screen.getByText(/Could not build this community/)).toBeInTheDocument();
  });

  it('marks every attempted row retryable when the atomic community build fails', async () => {
    apiPost.mockImplementation((url: string) =>
      url === '/api/v1/lego-assembly/place-community'
        ? Promise.reject(make422('One zone could not be compiled; no changes were saved.'))
        : Promise.resolve({ data: planFixture }),
    );

    render(<LegoBuilderPanel zones={[
      makeZone({ id: 'z-building' }),
      makeZone({ id: 'z-park', zone_type: 'green_space', properties: { _plan_role: 'open_space' } }),
    ]} onClose={vi.fn()} />);
    expect(await screen.findByText(/Detailed 1/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^generate to 3d$/i }));

    await waitFor(() => expect(screen.getByText('One zone could not be compiled; no changes were saved.')).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /retry place/i })).toBeInTheDocument();
    expect(screen.getByText('retry build')).toBeInTheDocument();
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
    expect(await screen.findByText(/Detailed 2/)).toBeInTheDocument();

    const placeButtons = screen.getAllByRole('button', { name: /^place$/i });
    expect(placeButtons).toHaveLength(2);
    fireEvent.click(placeButtons[0]);
    await waitFor(() => expect(screen.getByText('placed')).toBeInTheDocument());

    fireEvent.click(screen.getAllByRole('button', { name: /^place$/i })[0]);
    await waitFor(() => expect(screen.getByRole('button', { name: /retry place/i })).toBeInTheDocument());
    expect(screen.getByText('planner said no')).toBeInTheDocument();
  });

  it('Rebuild buildings replaces an already placed recipe with the latest content-hashed assets', async () => {
    const oldCatalogFingerprint = 'a'.repeat(64);
    const currentCatalogFingerprint = 'b'.repeat(64);
    const refreshedPlan = {
      ...planFixture,
      catalog_fingerprint: currentCatalogFingerprint,
      instances: [{ ...planFixture.instances[0], model_url: '/models/podium.glb?v=new-hash' }],
    };
    let planCalls = 0;
    apiPost.mockImplementation((url: string) => {
      if (url === '/api/v1/lego-assembly/plan') {
        planCalls += 1;
        return Promise.resolve({ data: planCalls === 1 ? planFixture : refreshedPlan });
      }
      if (url === '/api/v1/lego-assembly/place/zone-placed') {
        return Promise.resolve({
          data: { status: 'placed', zone_id: 'zone-placed', building_id: 'building-1', building_created: false },
        });
      }
      if (url === '/api/v1/lego-assembly/place-community') {
        return Promise.resolve({
          data: {
            status: 'compiled',
            compiled_at: '2026-08-04T01:00:00Z',
            counts: { building: 1, park: 0, street: 0 },
            items: [{
              zone_id: 'zone-placed',
              kind: 'building',
              building_id: 'building-1',
              building_created: false,
              generator: 'lego_assembly',
            }],
          },
        });
      }
      return Promise.reject(new Error(`unexpected POST ${url}`));
    });

    const placedZone = makeZone({
      id: 'zone-placed',
      building_id: 'building-1',
      properties: {
        development_archetype_id: 'nordic_timber_midrise',
        _lego_catalog_fingerprint: oldCatalogFingerprint,
        community_3d: {
          schema_version: 1,
          state: 'compiled',
          kind: 'building',
          generator: 'lego_assembly',
          compiled_at: '2026-07-19T00:00:00Z',
        },
      },
    });
    const client = new QueryClient();
    client.setQueryData(['site-zones', 'proj-1'], [{
      ...placedZone,
      updated_at: '2026-08-04T00:30:00Z',
    }]);
    render(<LegoBuilderPanel zones={[placedZone]} onClose={vi.fn()} />, client);

    expect(await screen.findByText('placed')).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalledWith(
      '/api/v1/lego-assembly/place/zone-placed',
      expect.anything(),
    );

    fireEvent.click(screen.getByRole('button', { name: /rebuild buildings/i }));

    await waitFor(() => expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/place/zone-placed',
      expect.objectContaining({
        instances: [expect.objectContaining({ model_url: '/models/podium.glb?v=new-hash' })],
        catalog_fingerprint: currentCatalogFingerprint,
        source_updated_at: '2026-08-04T00:30:00Z',
      }),
    ));
    expect(await screen.findByText(/latest family assets/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /rebuild current 3d scene/i }));
    await waitFor(() => expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/place-community',
      {
        items: [expect.objectContaining({
          zone_id: 'zone-placed',
          source_updated_at: '2026-08-04T00:30:00Z',
        })],
      },
    ));
  });

  it('Rebuild buildings upgrades an exact-massing fallback after its family is imported', async () => {
    let planCalls = 0;
    apiPost.mockImplementation((url: string) => {
      if (url === '/api/v1/lego-assembly/plan') {
        planCalls += 1;
        return planCalls === 1
          ? Promise.reject(make422('No module family covers archetype parkside_terraces.'))
          : Promise.resolve({ data: planFixture });
      }
      if (url === '/api/v1/lego-assembly/place/zone-upgrade') {
        return Promise.resolve({
          data: {
            status: 'placed',
            zone_id: 'zone-upgrade',
            building_id: 'building-upgrade',
            building_created: false,
          },
        });
      }
      return Promise.reject(new Error(`unexpected POST ${url}`));
    });

    const massingZone = makeZone({
      id: 'zone-upgrade',
      building_id: 'building-upgrade',
      properties: {
        development_archetype_id: 'parkside_terraces',
        community_3d: {
          schema_version: 1,
          state: 'compiled',
          kind: 'building',
          generator: 'planned_massing',
          compiled_at: '2026-07-19T00:00:00Z',
        },
      },
    });
    const client = new QueryClient();
    client.setQueryData(['site-zones', 'proj-1'], [massingZone]);
    const invalidateQueries = vi.spyOn(client, 'invalidateQueries');
    render(<LegoBuilderPanel zones={[massingZone]} onClose={vi.fn()} />, client);

    expect(await screen.findByText('3D massing')).toBeInTheDocument();
    expect(screen.getByText(/Detailed family to add/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /rebuild buildings/i }));

    await waitFor(() => expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/place/zone-upgrade',
      expect.objectContaining({ module_family: planFixture.family }),
    ));
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['project', 'proj-1'] });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['site-zones', 'proj-1'] });
    expect(await screen.findByText('placed')).toBeInTheDocument();
    expect(screen.queryByText('3D massing')).not.toBeInTheDocument();
    expect(screen.getByText(/latest family assets/i)).toBeInTheDocument();
  });

  it('leaves Rebuild usable and reports a project refresh failure', async () => {
    let planCalls = 0;
    apiPost.mockImplementation((url: string) => {
      if (url === '/api/v1/lego-assembly/plan') {
        planCalls += 1;
        return planCalls === 1
          ? Promise.reject(make422('No module family covers archetype nordic_timber_midrise.'))
          : Promise.resolve({ data: planFixture });
      }
      if (url === '/api/v1/lego-assembly/place/zone-refresh-fails') {
        return Promise.resolve({
          data: {
            status: 'placed',
            zone_id: 'zone-refresh-fails',
            building_id: 'building-refresh-fails',
            building_created: false,
          },
        });
      }
      return Promise.reject(new Error(`unexpected POST ${url}`));
    });
    const massingZone = makeZone({
      id: 'zone-refresh-fails',
      building_id: 'building-refresh-fails',
      properties: {
        development_archetype_id: 'nordic_timber_midrise',
        community_3d: {
          schema_version: 1,
          state: 'compiled',
          kind: 'building',
          generator: 'planned_massing',
          compiled_at: '2026-07-19T00:00:00Z',
        },
      },
    });
    const client = new QueryClient();
    client.setQueryData(['site-zones', 'proj-1'], [massingZone]);
    vi.spyOn(client, 'invalidateQueries').mockRejectedValueOnce(new Error('refresh unavailable'));
    render(<LegoBuilderPanel zones={[massingZone]} onClose={vi.fn()} />, client);
    expect(await screen.findByText('3D massing')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /rebuild buildings/i }));

    expect(await screen.findByText(/Could not finish rebuilding the building plans/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /rebuild buildings/i })).toBeEnabled();
  });
});
