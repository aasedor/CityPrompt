import '@testing-library/jest-dom/vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { ReactElement } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { compileBoundaryCommunity3DMock } = vi.hoisted(() => ({
  compileBoundaryCommunity3DMock: vi.fn(),
}));

vi.mock('@/features/legoAssembly/communityCompiler', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/features/legoAssembly/communityCompiler')>();
  return {
    ...actual,
    compileBoundaryCommunity3D: compileBoundaryCommunity3DMock,
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
    archetypeImages: [{
      id: 'industrial_brick_mixed_use_variant_0',
      label: 'Industrial Brick Mixed Use — Front Day',
      imageUrl: '/industrial/front-day.png',
      imagePath: '/industrial/front-day.png',
      prompt: 'Industrial brick mixed use',
    }],
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
    ],
  };
  return {
    ...actual,
    BUILDING_AESTHETIC_CATEGORIES_V2: [{
      id: 'industrial_brick',
      label: 'Industrial Brick',
      description: 'Industrial masonry buildings',
    }],
    BUILDING_AESTHETIC_OPTIONS_V2: [industrialBrick],
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

import { ZonePropertiesPanel } from './ZonePropertiesPanel';
import type { LayoutOption, SiteZone } from '@/types';
import { siteZonesApi, urbanDnaApi } from '@/services/api';
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
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      configurable: true,
      value: vi.fn(),
    });
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

    fireEvent.click(screen.getByRole('button', { name: /^Automatic \/ best-fitting family/i }));

    await waitFor(() => {
      expect(onUpdate).toHaveBeenCalledWith(
        industrialZone().id,
        expect.objectContaining({
          properties: expect.objectContaining({
            development_aesthetic: 'industrial_brick_mixed_use',
            development_subcategory: 'industrial_brick_mixed_use',
            development_selected_variant_id: undefined,
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

  it('routes the purple Site Boundary action through LEGO Community 3D instead of legacy bulk Meshy', async () => {
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

    fireEvent.click(await screen.findByRole('button', { name: /^Generate Community$/ }));

    await waitFor(() => {
      expect(compileBoundaryCommunity3DMock).toHaveBeenCalledWith(boundary.project_id, boundary.id);
    });
    expect(legacyBulkMeshy).not.toHaveBeenCalled();
  });

  it('rejects a multi-building preview before applying any layout or compiling Community 3D', async () => {
    const boundary = siteBoundaryZone();
    const child = industrialZone();
    const invalidLayout: LayoutOption = {
      option_index: 0,
      option_label: 'Two-building preview',
      buildings: [
        {
          center_x: 0, center_y: 0, width_m: 20, depth_m: 12, rotation_deg: 0,
          building_type: 'mixed_use', setback_front_m: 0, setback_side_m: 0,
        },
        {
          center_x: 25, center_y: 0, width_m: 20, depth_m: 12, rotation_deg: 0,
          building_type: 'mixed_use', setback_front_m: 0, setback_side_m: 0,
        },
      ],
      roads: [],
      green_spaces: [],
      layout_strategy: 'test',
      reasoning: 'Regression fixture',
    };
    useViewerStore.getState().setSitePreview(boundary.id, { [child.id]: [invalidLayout] });
    const applyLayout = vi.spyOn(siteZonesApi, 'applyLayout');
    vi.spyOn(siteZonesApi, 'renderSitePreview').mockResolvedValue({
      image_url: '/site-preview.png',
      zone_id: boundary.id,
      option_index: 0,
    });
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

    fireEvent.click(await screen.findByRole('button', { name: /^Generate Community$/ }));

    await waitFor(() => {
      expect(applyLayout).not.toHaveBeenCalled();
      expect(compileBoundaryCommunity3DMock).not.toHaveBeenCalled();
    });
  });
});
