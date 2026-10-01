import { expect, it, vi } from 'vitest';

vi.mock('@/data/validationCatalogue.json', async importOriginal => {
  const actual = await importOriginal<{ default: typeof import('@/data/validationCatalogue.json') }>();
  return { default: { ...actual.default, assets: actual.default.assets.filter(
    asset => asset.model.variantId !== 'student_main_street_v1',
  ) } };
});

it('loads inspector catalogues when a roster entry has no placement metadata', async () => {
  const catalogue = await import('./aestheticCatalog');
  expect(catalogue.BUILDING_AESTHETIC_OPTIONS_V2.length).toBeGreaterThan(0);
  expect(catalogue.OPENSPACE_AESTHETIC_OPTIONS_V2.length).toBeGreaterThan(0);
  expect(catalogue.ROADWAY_AESTHETIC_OPTIONS_V2.some(option => option.variants?.some(
    variant => variant.id === 'student_main_street_v1',
  ))).toBe(false);
  expect(catalogue.ROADWAY_AESTHETIC_OPTIONS_V2.some(option => option.variants?.some(
    variant => variant.id === 'student_market_street_v1',
  ))).toBe(true);
});
