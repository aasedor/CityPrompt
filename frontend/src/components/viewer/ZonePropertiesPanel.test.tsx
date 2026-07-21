import '@testing-library/jest-dom/vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { ReactElement } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

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
import type { SiteZone } from '@/types';

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

describe('ZonePropertiesPanel LEGO selection handoff', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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
});
