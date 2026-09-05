import '@testing-library/jest-dom/vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import type { ComponentProps, ReactElement } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const { compileBoundaryCommunity3DMock, listLegoModulesMock } = vi.hoisted(() => ({
  compileBoundaryCommunity3DMock: vi.fn(),
  listLegoModulesMock: vi.fn(),
}));

vi.mock('@/features/legoAssembly/communityCompiler', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/features/legoAssembly/communityCompiler')>();
  return {
    ...actual,
    compileBoundaryCommunity3D: compileBoundaryCommunity3DMock,
  };
});

vi.mock('@/features/legoAssembly/legoAssemblyApi', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/features/legoAssembly/legoAssemblyApi')>();
  return {
    ...actual,
    legoAssemblyApi: {
      ...actual.legoAssemblyApi,
      listModules: listLegoModulesMock,
    },
  };
});

vi.mock('./aestheticCatalog', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./aestheticCatalog')>();
  const industrialBrick = {
    id: 'industrial_brick_mixed_use',
    categoryId: 'industrial_brick',
    label: 'Industrial Brick Mixed Use',
    description: 'Adapted industrial building with brick piers and large windows.',
    photoUrl: '/industrial/hero.png',
    suggestedWidth_m: 30,
    suggestedDepth_m: 20,
    minFloors: 4,
    maxFloors: 8,
    archetypeImages: [
      {
        id: 'industrial_brick_mixed_use_variant_0',
        label: 'Industrial Brick Mixed Use — Front Day',
        imageUrl: '/industrial/front-day.png',
        imagePath: '/industrial/front-day.png',
        prompt: 'Industrial brick mixed use',
      },
      {
        id: 'industrial_brick_brewery_reference',
        label: 'Brewery reference',
        imageUrl: '/industrial/brewery-reference.png',
        imagePath: '/industrial/brewery-reference.png',
        prompt: 'Industrial brick brewery',
      },
      {
        id: 'industrial_brick_brewery_variant_0_reference',
        label: 'Brewery night reference',
        imageUrl: '/industrial/brewery-night-reference.png',
        imagePath: '/industrial/brewery-night-reference.png',
        prompt: 'Industrial brick brewery at night',
      },
      {
        id: 'industrial_brick_brewery_variant_1_reference',
        label: 'Brewery courtyard reference',
        imageUrl: '/industrial/brewery-courtyard-reference.png',
        imagePath: '/industrial/brewery-courtyard-reference.png',
        prompt: 'Industrial brick brewery courtyard',
      },
    ],
    generationStyleInput: {
      developmentType: 'mixed_use',
      buildingSubcategory: 'industrial_brick_mixed_use',
    },
    variants: [
      {
        id: 'industrial_brick_original_mill',
        label: 'Original Mill',
        thumbnailUrl: '/industrial/original-mill.png',
        minFloors: 4,
        maxFloors: 8,
      },
      {
        id: 'industrial_brick_brewery',
        label: 'Brewery',
        thumbnailUrl: '/industrial/brewery.png',
        minFloors: 2,
        maxFloors: 5,
        suggestedWidth_m: 40,
        suggestedDepth_m: 26,
        shadeId: 'industrial_brick_brewery',
        facadeDetail: { primaryMaterial: 'Red brick' },
        roofDetail: { form: 'Sawtooth roof' },
        palette: { primary: '#8f3c2f' },
      },
      {
        id: 'industrial_brick_brewery_variant_0',
        label: 'Brewery Night',
        thumbnailUrl: '/industrial/brewery-night.png',
        minFloors: 2,
        maxFloors: 5,
      },
      {
        id: 'industrial_brick_brewery_variant_1',
        label: 'Brewery Courtyard',
        thumbnailUrl: '/industrial/brewery-courtyard.png',
        minFloors: 2,
        maxFloors: 5,
      },
    ],
  };
  const streetOption = (id: string, label: string, width: number, volume: 'low' | 'medium') => ({
    id,
    categoryId: 'auto_oriented',
    label,
    description: `${label} catalog description.`,
    photoUrl: `/streets/${id}/hero.png`,
    transportModes: ['walking', 'automobile'],
    propertyPresets: {
      width,
      lane_count: 2,
      volume,
      road_surface: 'asphalt',
      sidewalks: 'both',
      has_sidewalks: true,
      priority_pedestrian: id === 'calgary_local' ? 2 : 1,
      priority_auto: id === 'calgary_local' ? 1 : 2,
    },
    archetypeImages: [
      {
        id: `${id}_variant_0`,
        label: `${label} — Front Day`,
        imageUrl: `/streets/${id}/front-day.png`,
        imagePath: `/streets/${id}/front-day.png`,
        prompt: `${label} front-day reference`,
      },
      {
        id: `${id}_variant_1`,
        label: `${label} — Corner Day`,
        imageUrl: `/streets/${id}/corner-day.png`,
        imagePath: `/streets/${id}/corner-day.png`,
        prompt: `${label} corner-day reference`,
      },
    ],
    generationStyleInput: {
      domain: 'street_pathway',
      subtype: id,
    },
  });
  const streetOptions = [
    streetOption('main_street_complete', 'Main Street Complete', 18, 'medium'),
    streetOption('narrow_residential_street', 'Narrow Residential Street', 10, 'low'),
    streetOption('calgary_local', 'Calgary Local', 16, 'low'),
  ];
  const urbanPocketPark = {
    id: 'urban_pocket_park',
    categoryId: 'neighborhood_public_realm',
    label: 'Urban Pocket Park',
    description: 'Compact landscaped public room.',
    photoUrl: '/parks/urban_pocket_park/hero.png',
    archetypeImages: [{
      id: 'urban_pocket_park_variant_0',
      label: 'Urban Pocket Park — Front Day',
      imageUrl: '/parks/urban_pocket_park/front-day.png',
      imagePath: '/parks/urban_pocket_park/front-day.png',
      prompt: 'Urban pocket park front-day reference',
    }],
    generationStyleInput: {
      domain: 'park_plaza',
      subtype: 'park',
    },
  };
  const neighborhoodPark = {
    id: 'neighborhood_park',
    categoryId: 'neighborhood_public_realm',
    label: 'Neighborhood Park',
    description: 'Everyday community park with recreation and planting.',
    photoUrl: '/archetypes/openspaces/neighborhood-park/variant_0.png',
    suggestedWidth_m: 100,
    suggestedDepth_m: 80,
    variants: [
      {
        id: 'neighborhood_park_v0',
        label: 'Rustic Timber & Gravel',
        thumbnailUrl: '/archetypes/openspaces/neighborhood-park/variant_0.png',
      },
      {
        id: 'neighborhood_park_v1',
        label: 'Modern Steel & Turf',
        thumbnailUrl: '/archetypes/openspaces/neighborhood-park/variant_1.png',
      },
    ],
    archetypeImages: [],
    generationStyleInput: {
      domain: 'park_plaza',
      subtype: 'park',
    },
  };
  const japaneseMachiya = actual.BUILDING_AESTHETIC_OPTIONS_V2.find(
    (option) => option.id === 'japanese_machiya_mixed_use',
  )!;
  const daylightFactory = actual.BUILDING_AESTHETIC_OPTIONS_V2.find(
    (option) => option.id === 'daylight_factory',
  )!;
  const foodHall = actual.BUILDING_AESTHETIC_OPTIONS_V2.find(
    (option) => option.id === 'food_hall_market_hall',
  )!;
  const contemporaryMidrise = actual.BUILDING_AESTHETIC_OPTIONS_V2.find(
    (option) => option.id === 'contemporary_midrise_residential',
  )!;
  return {
    ...actual,
    BUILDING_AESTHETIC_CATEGORIES_V2: [{
      id: 'industrial_brick',
      label: 'Industrial Brick',
      description: 'Industrial masonry buildings',
    }],
    BUILDING_AESTHETIC_OPTIONS_V2: [
      industrialBrick,
      japaneseMachiya,
      daylightFactory,
      foodHall,
      contemporaryMidrise,
    ],
    ROADWAY_AESTHETIC_CATEGORIES_V2: [{
      id: 'auto_oriented',
      label: 'Auto Oriented',
      description: 'Vehicle streets with complete public-realm sections.',
    }],
    ROADWAY_AESTHETIC_OPTIONS_V2: streetOptions,
    ROADWAY_AESTHETIC_PRESETS_V2: Object.fromEntries(
      streetOptions.map((option) => [option.id, option.propertyPresets]),
    ),
    GREEN_SPACE_AESTHETIC_CATEGORIES_V2: [{
      id: 'neighborhood_public_realm',
      label: 'Neighborhood Public Realm',
      description: 'Small parks and civic spaces.',
    }],
    GREEN_SPACE_AESTHETIC_OPTIONS_V2: [neighborhoodPark, urbanPocketPark],
    GREEN_SPACE_AESTHETIC_PRESETS_V2: {},
    PLAZA_AESTHETIC_CATEGORIES_V2: [],
    PLAZA_AESTHETIC_OPTIONS_V2: [],
    PLAZA_AESTHETIC_PRESETS_V2: {},
    OPENSPACE_AESTHETIC_CATEGORIES_V2: [{
      id: 'neighborhood_public_realm',
      label: 'Neighborhood Public Realm',
      description: 'Small parks and civic spaces.',
    }],
    OPENSPACE_AESTHETIC_OPTIONS_V2: [neighborhoodPark, urbanPocketPark],
    filterOptionsByDevelopmentType: (options: unknown[]) => options,
  };
});

vi.mock('@/services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/services/api')>();
  return {
    ...actual,
    modelLibraryApi: {
      ...actual.modelLibraryApi,
      archetypePreviews: vi.fn().mockResolvedValue({}),
    },
  };
});

import { ZonePropertiesPanel, useZonePropertiesReload } from './ZonePropertiesPanel';
import type { SiteZone } from '@/types';
import { modelLibraryApi, siteZonesApi, urbanDnaApi } from '@/services/api';
import { useViewerStore } from '@/store';

function renderPanel(ui: ReactElement) {
  return render(
    <QueryClientProvider client={new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })}>
      {ui}
    </QueryClientProvider>,
  );
}

function industrialZone(): SiteZone {
  return {
    id: '11111111-1111-4111-8111-111111111111',
    project_id: '22222222-2222-4222-8222-222222222222',
    name: 'Industrial Block',
    zone_type: 'building',
    coordinates: [
      [-113.5, 53.5],
      [-113.49955, 53.5],
      [-113.49955, 53.50018],
      [-113.5, 53.50018],
    ],
    color: '#8f3c2f',
    properties: {
      development_type: 'mixed_use',
      development_aesthetic: 'industrial_brick_mixed_use',
      development_aesthetic_category: 'industrial_brick',
      development_subcategory: 'industrial_brick_mixed_use',
      development_archetype_id: 'industrial_brick_mixed_use_variant_0',
      development_archetype_label: 'Industrial Brick Mixed Use — Front Day',
      development_selected_variant_id: 'industrial_brick_brewery',
      development_variant_shade_id: 'industrial_brick_brewery',
      development_facade_detail: { primaryMaterial: 'Red brick' },
      development_roof_detail: { form: 'Sawtooth roof' },
      development_palette: { primary: '#8f3c2f' },
      generation_style_input: {
        archetypeId: 'industrial_brick_mixed_use_variant_0',
        buildingSubcategory: 'industrial_brick_mixed_use',
      },
      floors: 6,
      floor_height: 3.5,
      height: 21,
    },
    sort_order: 0,
    created_at: '2026-07-20T00:00:00Z',
    updated_at: '2026-07-20T00:00:00Z',
  };
}

function japaneseMachiyaZone(): SiteZone {
  const zone = industrialZone();
  return {
    ...zone,
    name: 'Machiya Block',
    properties: {
      ...zone.properties,
      development_aesthetic: 'japanese_machiya_mixed_use',
      development_subcategory: 'japanese_machiya_mixed_use',
      development_archetype_id: 'japanese_machiya_mixed_use_variant_0',
      development_selected_variant_id: 'machiya_traditional_restored',
    },
  };
}

function siteBoundaryZone(): SiteZone {
  return {
    id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
    project_id: '22222222-2222-4222-8222-222222222222',
    name: 'AI Master Plan Boundary',
    zone_type: 'site_boundary',
    coordinates: [
      [-113.501, 53.499],
      [-113.498, 53.499],
      [-113.498, 53.502],
      [-113.501, 53.502],
    ],
    color: '#8b5cf6',
    properties: {},
    sort_order: 0,
    created_at: '2026-07-21T00:00:00Z',
    updated_at: '2026-07-21T00:00:00Z',
  };
}

function publicRealmZone(zoneType: 'road' | 'green_space'): SiteZone {
  return {
    id: zoneType === 'road'
      ? '33333333-3333-4333-8333-333333333333'
      : '44444444-4444-4444-8444-444444444444',
    project_id: '22222222-2222-4222-8222-222222222222',
    name: zoneType === 'road' ? 'Test Street' : 'Test Park',
    zone_type: zoneType,
    coordinates: [
      [-113.5, 53.5],
      [-113.4997, 53.5],
      [-113.4997, 53.50012],
      [-113.5, 53.50012],
    ],
    color: '#5d9b63',
    properties: zoneType === 'road'
      ? { road_aesthetic_category: 'auto_oriented' }
      : { green_space_aesthetic_category: 'neighborhood_public_realm' },
    sort_order: 0,
    created_at: '2026-07-22T00:00:00Z',
    updated_at: '2026-07-22T00:00:00Z',
  };
}

type ReloadResponse = { data?: SiteZone[]; error?: unknown; status: string };

function deferredReload() {
  let resolve!: (response: ReloadResponse) => void;
  let reject!: (error: Error) => void;
  const promise = new Promise<ReloadResponse>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { resolve, reject, reload: vi.fn(() => promise) };
}

function customParkZone(): SiteZone {
  return {
    ...publicRealmZone('green_space'),
    properties: { custom_style_enabled: true, custom_style_domain: 'open_space', custom_style_prompt: 'Saved park description' },
  };
}

function ReloadPanel({ zone, reload, onUpdate, onClose }: {
  zone: SiteZone;
  reload: () => Promise<ReloadResponse>;
  onUpdate: ComponentProps<typeof ZonePropertiesPanel>['onUpdate'];
  onClose: ComponentProps<typeof ZonePropertiesPanel>['onClose'];
}) {
  const { savedVersionReload, reloadSavedVersion } = useZonePropertiesReload(zone.project_id, zone.id, reload);
  return <>
    <button onClick={() => { void reloadSavedVersion(); }}>Reload saved version</button>
    <ZonePropertiesPanel key={zone.id} zone={zone} savedVersionReload={savedVersionReload}
      onUpdate={onUpdate} onDelete={vi.fn()} onClose={onClose} />
  </>;
}

describe('ZonePropertiesPanel explicit saved-version reload', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', { configurable: true, value: vi.fn() });
  });
  afterEach(() => {
    cleanup();
    vi.useRealTimers();
  });

  function setup() {
    const zone = customParkZone();
    const pending = deferredReload();
    const onUpdate = vi.fn();
    const onClose = vi.fn();
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const view = render(<ReloadPanel zone={zone} reload={pending.reload} onUpdate={onUpdate} onClose={onClose} />, {
      wrapper: ({ children }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>,
    });
    return { zone, pending, onUpdate, onClose, ...view };
  }

  function editForm() {
    fireEvent.change(screen.getByDisplayValue('Test Park'), { target: { value: 'Rejected park name' } });
    fireEvent.change(screen.getByDisplayValue('Saved park description'), { target: { value: 'Rejected park description' } });
  }

  it('only resets fields after successful explicit reload and never autosaves the rejected or restored values', async () => {
    const view = setup();
    editForm();
    const saved = { ...view.zone, name: 'Server park name', properties: { ...view.zone.properties, custom_style_prompt: 'Server park description' } };
    // Query background refreshes must still preserve in-progress local edits.
    view.rerender(<ReloadPanel zone={saved} reload={view.pending.reload} onUpdate={view.onUpdate} onClose={view.onClose} />);
    expect(screen.getByDisplayValue('Rejected park description')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Reload saved version' }));
    expect(screen.getByDisplayValue('Rejected park name')).toBeInTheDocument();
    await act(async () => { view.pending.resolve({ status: 'success', data: [saved] }); });
    expect(screen.getByDisplayValue('Server park name')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Server park description')).toBeInTheDocument();
    await act(async () => { await vi.advanceTimersByTimeAsync(1000); });
    view.unmount();
    expect(view.onUpdate).not.toHaveBeenCalled();
    expect(view.onClose).not.toHaveBeenCalled();
  });

  it.each(['error result', 'rejected request'])('preserves failed edits but cancels their old debounce after a reload %s', async (failure) => {
    const view = setup();
    editForm();
    fireEvent.click(screen.getByRole('button', { name: 'Reload saved version' }));
    await act(async () => {
      if (failure === 'error result') view.pending.resolve({ status: 'error', error: new Error('offline') });
      else view.pending.reject(new Error('offline'));
    });
    expect(screen.getByDisplayValue('Rejected park name')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Rejected park description')).toBeInTheDocument();
    await act(async () => { await vi.advanceTimersByTimeAsync(1000); });
    view.unmount();
    expect(view.onUpdate).not.toHaveBeenCalled();
    expect(view.onClose).not.toHaveBeenCalled();
  });

  it('permits a fresh edit to autosave after a failed reload', async () => {
    const view = setup();
    editForm();
    fireEvent.click(screen.getByRole('button', { name: 'Reload saved version' }));
    await act(async () => { view.pending.resolve({ status: 'error', error: new Error('offline') }); });
    fireEvent.change(screen.getByDisplayValue('Rejected park description'), { target: { value: 'Revised park description' } });
    await act(async () => { await vi.advanceTimersByTimeAsync(800); });
    expect(view.onUpdate).toHaveBeenCalledExactlyOnceWith(view.zone.id, expect.objectContaining({
      name: 'Rejected park name', properties: expect.objectContaining({ custom_style_prompt: 'Revised park description' }),
    }));
  });

  it('cancels stale unmount saves even when unmounted before the reload state commits', async () => {
    const view = setup();
    editForm();
    act(() => {
      fireEvent.click(screen.getByRole('button', { name: 'Reload saved version' }));
      view.unmount();
    });
    await act(async () => { view.pending.resolve({ status: 'success', data: [view.zone] }); });
    expect(view.onUpdate).not.toHaveBeenCalled();
  });

  it('ignores a late project A reload and preserves project B edits and their own autosave', async () => {
    const view = setup();
    editForm();
    fireEvent.click(screen.getByRole('button', { name: 'Reload saved version' }));
    const other = { ...view.zone, id: '55555555-5555-4555-8555-555555555555', project_id: '66666666-6666-4666-8666-666666666666', name: 'Project B park' };
    view.rerender(<ReloadPanel zone={other} reload={view.pending.reload} onUpdate={view.onUpdate} onClose={view.onClose} />);
    fireEvent.change(screen.getByDisplayValue('Saved park description'), { target: { value: 'Project B local description' } });
    await act(async () => { view.pending.resolve({ status: 'success', data: [view.zone] }); });
    expect(screen.getByDisplayValue('Project B park')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Project B local description')).toBeInTheDocument();
    await act(async () => { await vi.advanceTimersByTimeAsync(800); });
    expect(view.onUpdate).toHaveBeenCalledExactlyOnceWith(other.id, expect.objectContaining({
      properties: expect.objectContaining({ custom_style_prompt: 'Project B local description' }),
    }));
    expect(view.onClose).not.toHaveBeenCalled();
  });

  it('still flushes ordinary pending custom-style edits when leaving without an explicit reload', () => {
    const view = setup();
    editForm();
    view.unmount();
    expect(view.onUpdate).toHaveBeenCalledExactlyOnceWith(view.zone.id, expect.objectContaining({
      name: 'Rejected park name', properties: expect.objectContaining({ custom_style_prompt: 'Rejected park description' }),
    }));
  });
});

describe('ZonePropertiesPanel site ground', () => {
  afterEach(cleanup);

  it('preserves legacy ground until the student explicitly saves a terrain choice', () => {
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', { configurable: true, value: vi.fn() });
    const zone = siteBoundaryZone();
    const onUpdate = vi.fn();
    renderPanel(<ZonePropertiesPanel zone={zone} onUpdate={onUpdate} onDelete={vi.fn()} onClose={vi.fn()} />);
    expect(screen.getByLabelText('Site ground')).toHaveValue('clear');
    fireEvent.change(screen.getByLabelText('Site ground'), { target: { value: 'retain' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save Changes' }));
    expect(onUpdate).toHaveBeenCalledWith(zone.id, expect.objectContaining({
      properties: expect.objectContaining({ community_3d_mask_existing_tiles: false }),
    }));
  });

  it('restores a saved retained terrain choice', () => {
    const zone = { ...siteBoundaryZone(), properties: { community_3d_mask_existing_tiles: false } };
    renderPanel(<ZonePropertiesPanel zone={zone} onUpdate={vi.fn()} onDelete={vi.fn()} onClose={vi.fn()} />);
    expect(screen.getByLabelText('Site ground')).toHaveValue('retain');
  });
});

describe('ZonePropertiesPanel viewport containment', () => {
  it('owns its desktop positioning and remains bounded by the viewport', () => {
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      configurable: true,
      value: vi.fn(),
    });
    const { container } = renderPanel(
      <ZonePropertiesPanel
        zone={industrialZone()}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    const panel = Array.from(container.querySelectorAll('div')).find((element) => (
      element.className.includes('sm:max-w-[calc(100vw-2rem)]')
    ));

    expect(panel).toBeDefined();
    expect(panel?.className).toContain('overflow-x-hidden');
    expect(panel?.className).toContain('sm:max-h-[calc(100dvh-5rem)]');
    expect(panel?.className).toContain('sm:z-40');
  });
});

describe('ZonePropertiesPanel LEGO selection handoff', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useViewerStore.getState().clearSitePreview();
    compileBoundaryCommunity3DMock.mockResolvedValue({
      response: {
        status: 'compiled',
        compiled_at: '2026-07-21T00:00:00Z',
        counts: { building: 1, park: 1, street: 1 },
        items: [],
      },
      detailedBuildings: 1,
      plannedMasses: 0,
      parks: 1,
      streets: 1,
    });
    listLegoModulesMock.mockResolvedValue([{
      id: 'industrial-brick-brewery-floor',
      name: 'Industrial Brick Brewery Floor',
      model_url: '/families/industrial-brick-brewery/floor.glb',
      family: 'industrial-brick-brewery',
      role: 'floor',
      width_m: 40,
      depth_m: 26,
      height_m: 3.5,
      archetype_ids: ['industrial_brick_brewery'],
      reuse_keys: [],
      repeatable_z: true,
    }]);
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      configurable: true,
      value: vi.fn(),
    });
  });

  it.each([
    ['Main Street Complete', 'main_street_complete', 18, 1, 2],
    ['Narrow Residential Street', 'narrow_residential_street', 10, 1, 2],
    ['Calgary Local', 'calgary_local', 16, 2, 1],
  ])('persists canonical LEGO identity, engineered section and separate image metadata for %s', async (
    label,
    archetypeId,
    width,
    priorityPedestrian,
    priorityAuto,
  ) => {
    const zone = publicRealmZone('road');
    const onUpdate = vi.fn();
    renderPanel(
      <ZonePropertiesPanel
        zone={zone}
        onUpdate={onUpdate}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole('button', {
      name: `Select ${label} with Automatic / best-fitting family`,
    }));

    await waitFor(() => {
      expect(onUpdate).toHaveBeenCalledWith(
        zone.id,
        expect.objectContaining({
          properties: expect.objectContaining({
            road_aesthetic: archetypeId,
            road_subcategory: archetypeId,
            road_archetype_id: archetypeId,
            road_selected_variant_id: undefined,
            width,
            priority_pedestrian: priorityPedestrian,
            priority_auto: priorityAuto,
            road_selected_reference: expect.objectContaining({
              id: `${archetypeId}_variant_0`,
              imageUrl: `/streets/${archetypeId}/front-day.png`,
            }),
            generation_style_inputs: expect.objectContaining({
              streets_paths: expect.objectContaining({
                archetypeId: `${archetypeId}_variant_0`,
              }),
            }),
          }),
        }),
      );
    });
  });

  it('restores and autosaves road image choices independently of the canonical LEGO archetype ID', async () => {
    const zone = publicRealmZone('road');
    const onUpdate = vi.fn();
    zone.properties = {
      ...zone.properties,
      road_aesthetic: 'main_street_complete',
      road_subcategory: 'main_street_complete',
      road_archetype_id: 'main_street_complete',
      road_selected_reference: {
        id: 'main_street_complete_variant_1',
        label: 'Main Street Complete — Corner Day',
        imageUrl: '/streets/main_street_complete/corner-day.png',
      },
    };

    renderPanel(
      <ZonePropertiesPanel
        zone={zone}
        onUpdate={onUpdate}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByAltText('Main Street Complete')).toHaveAttribute(
      'src',
      '/streets/main_street_complete/corner-day.png',
    );

    fireEvent.click(screen.getByTitle('Main Street Complete — Front Day (double-click to enlarge)'));

    await waitFor(() => {
      expect(onUpdate).toHaveBeenCalledWith(
        zone.id,
        expect.objectContaining({
          properties: expect.objectContaining({
            road_archetype_id: 'main_street_complete',
            road_selected_reference: expect.objectContaining({
              id: 'main_street_complete_variant_0',
              imageUrl: '/streets/main_street_complete/front-day.png',
            }),
          }),
        }),
      );
    });
  });

  it('persists Urban Pocket Park as a compilable park while retaining its selected image', async () => {
    const zone = publicRealmZone('green_space');
    const onUpdate = vi.fn();
    renderPanel(
      <ZonePropertiesPanel
        zone={zone}
        onUpdate={onUpdate}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole('button', {
      name: 'Select Urban Pocket Park with Automatic / best-fitting family',
    }));

    await waitFor(() => {
      expect(onUpdate).toHaveBeenCalledWith(
        zone.id,
        expect.objectContaining({
          properties: expect.objectContaining({
            green_space_aesthetic: 'urban_pocket_park',
            green_space_subcategory: 'urban_pocket_park',
            green_space_archetype_id: 'urban_pocket_park',
            green_space_selected_variant_id: undefined,
            green_space_selected_reference: expect.objectContaining({
              id: 'urban_pocket_park_variant_0',
              imageUrl: '/parks/urban_pocket_park/front-day.png',
            }),
            generation_style_inputs: expect.objectContaining({
              parks: expect.objectContaining({
                archetypeId: 'urban_pocket_park_variant_0',
              }),
            }),
          }),
        }),
      );
    });
  });

  it('keeps ordinary parks visible while framing only an exact reviewed Sticker kit variant', () => {
    const { container } = renderPanel(
      <ZonePropertiesPanel
        zone={publicRealmZone('green_space')}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    const neighborhoodCard = container.querySelector<HTMLElement>(
      '[data-aesthetic-option-id="neighborhood_park"]',
    );
    const ordinaryCard = container.querySelector<HTMLElement>(
      '[data-aesthetic-option-id="urban_pocket_park"]',
    );
    const reviewedVariant = container.querySelector<HTMLElement>(
      '[data-variant-id="neighborhood_park_v0"]',
    );
    const unbuiltSibling = container.querySelector<HTMLElement>(
      '[data-variant-id="neighborhood_park_v1"]',
    );

    expect(neighborhoodCard).toBeInTheDocument();
    expect(ordinaryCard).toBeInTheDocument();
    expect(within(neighborhoodCard!).getByText('Sticker Method')).toHaveClass('bg-[#c9ff3d]');
    expect(ordinaryCard).not.toHaveTextContent('Sticker Method');
    expect(reviewedVariant).toHaveAttribute('data-lego-ready', 'true');
    expect(reviewedVariant).toHaveClass('border-emerald-500');
    expect(unbuiltSibling).toHaveAttribute('data-lego-ready', 'false');
    expect(unbuiltSibling).not.toHaveClass('border-emerald-500');
    expect(screen.getByText(/exact park variant has a reviewed 3D kit/i)).toBeInTheDocument();
  });

  it('persists Brewery -> Automatic and opens LEGO from the current draft without a refetch', async () => {
    const onUpdate = vi.fn();
    const onOpenBlockEditor = vi.fn();
    const { container } = renderPanel(
      <ZonePropertiesPanel
        zone={industrialZone()}
        onUpdate={onUpdate}
        onDelete={vi.fn()}
        onClose={vi.fn()}
        onOpenBlockEditor={onOpenBlockEditor}
      />,
    );

    fireEvent.click(screen.getAllByRole('button', { name: /archetype/i })[0]);

    expect(screen.getByText('Current selection: Brewery')).toBeInTheDocument();
    const card = container.querySelector('[data-aesthetic-option-id="industrial_brick_mixed_use"]');
    expect(card).not.toBeNull();
    expect(card?.querySelector('button button')).toBeNull();

    fireEvent.click(within(card as HTMLElement).getByRole('button', {
      name: /^Automatic \/ best-fitting family/i,
    }));

    await waitFor(() => {
      expect(onUpdate).toHaveBeenCalledWith(
        industrialZone().id,
        expect.objectContaining({
          properties: expect.objectContaining({
            development_aesthetic: 'industrial_brick_mixed_use',
            development_subcategory: 'industrial_brick_mixed_use',
            development_archetype_id: 'industrial_brick_mixed_use_variant_0',
            development_selected_variant_id: undefined,
            development_selected_reference: expect.objectContaining({
              id: 'industrial_brick_mixed_use_variant_0',
              imageUrl: '/industrial/front-day.png',
            }),
          }),
        }),
      );
    });
    expect(screen.getByText('Current selection: Automatic / best-fitting family')).toBeInTheDocument();

    // ProjectView has not supplied an updated query-backed zone. The LEGO
    // callback must still receive this panel's current local selection.
    fireEvent.click(screen.getByRole('button', { name: /build with lego modules/i }));

    expect(onOpenBlockEditor).toHaveBeenCalledTimes(1);
    const draft = onOpenBlockEditor.mock.calls[0][0] as SiteZone;
    expect(draft.id).toBe(industrialZone().id);
    expect(draft.properties?.development_subcategory).toBe('industrial_brick_mixed_use');
    expect(draft.properties?.development_selected_variant_id).toBeUndefined();
    expect(draft.properties?.floors).toBe(6);
  });

  it('shows live LEGO readiness on the exact archetype variant and falls back through authored references', async () => {
    const { container } = renderPanel(
      <ZonePropertiesPanel
        zone={industrialZone()}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    fireEvent.click(screen.getAllByRole('button', { name: /archetype/i })[0]);

    const card = container.querySelector('[data-aesthetic-option-id="industrial_brick_mixed_use"]');
    const brewery = screen.getByTitle(/^Brewery — click to select/);
    const originalMill = screen.getByTitle(/^Original Mill — click to select/);

    await waitFor(() => expect(brewery).toHaveAttribute('data-lego-ready', 'true'));
    expect(card).not.toHaveAttribute('data-lego-family-available');
    expect(originalMill).toHaveAttribute('data-lego-ready', 'false');
    expect(screen.getByAltText('Industrial Brick Mixed Use').parentElement).not.toHaveAttribute('data-lego-ready');
    expect(modelLibraryApi.archetypePreviews).not.toHaveBeenCalled();

    const breweryImage = screen.getByAltText('Brewery');
    expect(breweryImage).toHaveAttribute('src', '/industrial/brewery.png');
    fireEvent.error(breweryImage);
    expect(breweryImage).toHaveAttribute(
      'src',
      '/industrial/brewery-reference.png',
    );
  });

  it('uses the explicit photoreal card render for the selected traditional Machiya zone', () => {
    const { container } = renderPanel(
      <ZonePropertiesPanel
        zone={japaneseMachiyaZone()}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    fireEvent.click(screen.getAllByRole('button', { name: /archetype/i })[0]);

    const image = screen.getByAltText('Japanese Machiya Mixed Use');
    expect(image).toHaveAttribute(
      'src',
      '/archetypes/buildings/japanese_machiya_mixed_use/variant_3.png',
    );
    expect(image).not.toHaveAttribute(
      'src',
      '/archetypes/buildings/japanese_machiya_mixed_use/variant_0.png',
    );

    fireEvent.error(image);
    const card = container.querySelector('[data-aesthetic-option-id="japanese_machiya_mixed_use"]');
    expect(card).toHaveTextContent('Photo unavailable');
    expect(screen.queryByAltText('Japanese Machiya Mixed Use')).not.toBeInTheDocument();
  });

  it('uses the approved Sticker Method archetype render on its pinned card', () => {
    const { container } = renderPanel(
      <ZonePropertiesPanel
        zone={industrialZone()}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    fireEvent.click(screen.getAllByRole('button', { name: /archetype/i })[0]);

    const card = container.querySelector('[data-aesthetic-option-id="daylight_factory"]');
    const image = screen.getByAltText('Daylight Factory');
    expect(card).toHaveTextContent('Sticker Method');
    expect(image).toHaveAttribute(
      'src',
      '/archetypes/buildings/daylight_factory/variant_0.png',
    );
    expect(image.getAttribute('src')).not.toContain('/families/');
  });

  it('keeps the complete building catalogue visible while only highlighting Sticker Method pilots', () => {
    const { container } = renderPanel(
      <ZonePropertiesPanel
        zone={industrialZone()}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    fireEvent.click(screen.getAllByRole('button', { name: /archetype/i })[0]);

    const cards = Array.from(container.querySelectorAll<HTMLElement>('[data-aesthetic-option-id]'));
    const ids = cards.map((card) => card.dataset.aestheticOptionId);
    const daylightIndex = ids.indexOf('daylight_factory');
    const foodHallIndex = ids.indexOf('food_hall_market_hall');
    const nonStickerIndex = ids.indexOf('contemporary_midrise_residential');

    expect(ids).toEqual(expect.arrayContaining([
      'industrial_brick_mixed_use',
      'japanese_machiya_mixed_use',
      'daylight_factory',
      'food_hall_market_hall',
      'contemporary_midrise_residential',
    ]));
    expect(daylightIndex).toBeGreaterThanOrEqual(0);
    expect(foodHallIndex).toBeGreaterThanOrEqual(0);
    expect(nonStickerIndex).toBeGreaterThanOrEqual(0);
    expect(daylightIndex).toBeLessThan(nonStickerIndex);
    expect(foodHallIndex).toBeLessThan(nonStickerIndex);

    const daylightCard = cards[daylightIndex];
    const foodHallCard = cards[foodHallIndex];
    const nonStickerCard = cards[nonStickerIndex];
    expect(daylightCard).toHaveTextContent('Sticker Method');
    expect(foodHallCard).toHaveTextContent('Sticker Method');
    expect(within(daylightCard).getByText('Sticker Method')).toHaveClass('bg-[#c9ff3d]');
    expect(within(foodHallCard).getByText('Sticker Method')).toHaveClass('bg-[#c9ff3d]');
    expect(foodHallCard).toHaveTextContent('2-2 floors');
    expect(foodHallCard).toHaveTextContent('Footprint 45m x 60m');
    expect(foodHallCard).not.toHaveTextContent('1-1 floors');
    expect(nonStickerCard).not.toHaveTextContent('Sticker Method');
    expect(nonStickerCard.querySelector('img')).toHaveAttribute(
      'src',
      expect.stringMatching(/^\/archetypes\/buildings\//),
    );
    expect(screen.queryByRole('button', { name: /pending reference/i })).not.toBeInTheDocument();
  });

  it('does not collapse numeric variant suffixes when marking exact LEGO readiness', async () => {
    listLegoModulesMock.mockResolvedValue([{
      id: 'industrial-brick-brewery-night-floor',
      name: 'Industrial Brick Brewery Night Floor',
      model_url: '/families/industrial-brick-brewery/night-floor.glb',
      family: 'industrial-brick-brewery-night',
      role: 'floor',
      width_m: 40,
      depth_m: 26,
      height_m: 3.5,
      archetype_ids: ['industrial_brick_brewery_variant_0'],
      reuse_keys: [],
      repeatable_z: true,
    }]);

    renderPanel(
      <ZonePropertiesPanel
        zone={industrialZone()}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    fireEvent.click(screen.getAllByRole('button', { name: /archetype/i })[0]);

    const brewery = screen.getByTitle(/^Brewery — click to select/);
    const breweryNight = screen.getByTitle(/^Brewery Night — click to select/);
    const breweryCourtyard = screen.getByTitle(/^Brewery Courtyard — click to select/);

    await waitFor(() => expect(breweryNight).toHaveAttribute('data-lego-ready', 'true'));
    expect(brewery).toHaveAttribute('data-lego-ready', 'false');
    expect(breweryCourtyard).toHaveAttribute('data-lego-ready', 'false');
  });

  it('keeps legacy bulk generation out of the canonical Site DNA boundary panel', async () => {
    const boundary = siteBoundaryZone();
    const child = industrialZone();
    const legacyBulkMeshy = vi.spyOn(siteZonesApi, 'generateForBoundary');
    vi.spyOn(siteZonesApi, 'getBoundaryAnalysis').mockResolvedValue({
      boundary_zone_id: boundary.id,
      contained_zones: [{
        id: child.id,
        name: child.name,
        zone_type: child.zone_type,
        color: child.color,
        properties: child.properties ?? {},
        area_m2: 600,
      }],
      zone_summary: { building: 1 },
      total_contained: 1,
      osm_context: {},
    });
    vi.spyOn(urbanDnaApi, 'getLatest').mockRejectedValue({ response: { status: 404 } });
    vi.spyOn(urbanDnaApi, 'listScenarios').mockResolvedValue({
      scenarios: [],
      available_presets: [],
      stale: false,
    });

    renderPanel(
      <ZonePropertiesPanel
        zone={boundary}
        allZones={[boundary, child]}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    await screen.findByRole('button', { name: /^Generate Site DNA$/ });
    expect(screen.queryByRole('button', { name: /^Generate Community$/ })).not.toBeInTheDocument();
    expect(compileBoundaryCommunity3DMock).not.toHaveBeenCalled();
    expect(legacyBulkMeshy).not.toHaveBeenCalled();
  });

});
