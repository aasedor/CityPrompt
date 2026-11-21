import '@testing-library/jest-dom/vitest';
import { render, screen, cleanup, fireEvent } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { CanonicalCatalogueCard } from './CanonicalCatalogueCard';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { SAVED_OPENSPACE_AESTHETIC_OPTIONS } from '@/components/viewer/aestheticCatalog';
import { pickerHeroImage } from './pickerHeroImages';
import { cataloguePresentationFor } from './cataloguePresentation';

vi.mock('@/data/catalogueBuildingQuantities.json', async importOriginal => {
  const { default: quantities } = await importOriginal<{ default: typeof import('@/data/catalogueBuildingQuantities.json') }>();
  return { default: { ...quantities, records: [...quantities.records,
    { variant_id: 'garden_mews_six_homes', revision: 'concept-test',
      estimated_gross_floor_area_m2: 540, estimated_dwellings_range: [5, 7] },
    { variant_id: 'garden_mews_six_homes', revision: 'authored-test',
      gross_floor_area_m2: 504, dwellings: 6, estimated_gross_floor_area_m2: 540, estimated_dwellings_range: [5, 7] },
    { variant_id: 'brick_timber_two_storey_office', revision: 'open-structure-test',
      estimated_gross_floor_area_m2: 0, estimated_dwellings_range: [0, 0] },
  ] } };
});

function expandBuilding(assetId: string, label: string, revision?: string) {
  const choice = CANONICAL_CHOICES.find(item => item.placements[0]?.id === assetId)!;
  const [asset] = choice.placements;
  const placements = revision ? [{ ...asset, model: { ...asset.model, revision } }] : choice.placements;
  render(<CanonicalCatalogueCard choice={{ ...choice, placements }} selected={null} onPlacement={vi.fn()} onDraw={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: `Expand details for ${label}` }));
}

afterEach(cleanup);
it('shows gross floor area and estimates FAR using the reference lot of a compact building', () => {
  expandBuilding('clay_brick_timber_two_storey_office', 'Brick-and-Timber Courtyard Office');
  expect(screen.getByText('Estimated FAR on reference lot')).toBeVisible();
  expect(screen.getByText(/0\.78.*288 m²/)).toBeVisible();
  expect(screen.getByText(/224 m².*2,411 ft²/)).toBeVisible();
});

it('shows planning estimates with both area units, reference-lot FAR, and a dwelling range', () => {
  expandBuilding('clay_garden_mews_six_homes', 'Garden Mews Courtyard Housing', 'concept-test');
  expect(screen.getByText('Estimated gross floor area').nextElementSibling).toHaveTextContent('540 m² · 5,813 ft²');
  expect(screen.getByText('Estimated FAR on reference lot').nextElementSibling).toHaveTextContent('0.80 on 676 m²');
  expect(screen.getByText('Estimated dwellings').nextElementSibling).toHaveTextContent('5–7');
});

it('prefers authored quantities from the same model revision', () => {
  expandBuilding('clay_garden_mews_six_homes', 'Garden Mews Courtyard Housing', 'authored-test');
  expect(screen.getByText('Gross floor area').nextElementSibling).toHaveTextContent('504 m² · 5,425 ft²');
  expect(screen.getByText('Modelled dwellings').nextElementSibling).toHaveTextContent(/^6$/);
});

it('displays explicit zero estimates for an open nonresidential structure', () => {
  expandBuilding('clay_brick_timber_two_storey_office', 'Brick-and-Timber Courtyard Office', 'open-structure-test');
  expect(screen.getByText('Estimated gross floor area').nextElementSibling).toHaveTextContent('0 m² · 0 ft²');
  expect(screen.getByText('Estimated FAR on reference lot').nextElementSibling).toHaveTextContent('0.00 on 288 m²');
  expect(screen.getByText('Estimated dwellings').nextElementSibling).toHaveTextContent(/^0$/);
});

it('shows pending quantities for a variant without matching revision data', () => {
  expandBuilding('clay_brick_timber_two_storey_office', 'Brick-and-Timber Courtyard Office', 'unlisted-test');
  expect(screen.getByText('Gross floor area').nextElementSibling).toHaveTextContent('Pending');
  expect(screen.getByText('Dwellings').nextElementSibling).toHaveTextContent('Pending');
  expect(screen.getByText('Estimated FAR on reference lot').nextElementSibling).toHaveTextContent('Floor area pending');
});

it('keeps court-only as a base-card variant and places its original geometry and thumbnail', () => {
  const choice = CANONICAL_CHOICES.find(choice => choice.option.id === 'basketball_court')!;
  const court = choice.placements.find(asset => asset.model.variantId === 'court_only_basketball_v1')!;
  const onPlacement = vi.fn();
  const { container } = render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={onPlacement} onDraw={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button', { name: 'Expand details for Basketball court' }));
  fireEvent.change(screen.getByRole('combobox'), { target: { value: court.model.variantId } });
  expect(container.querySelector('img')?.getAttribute('src')).toBe(court.thumbnail);
  expect(screen.getAllByRole('option').filter(option => option.getAttribute('value') === court.model.variantId)).toHaveLength(1);
  fireEvent.click(screen.getByRole('button', { name: 'Choose & place' }));
  expect(onPlacement).toHaveBeenCalledWith(court);
});
it('shows the locked market reference instead of its obsolete parent image', () => {
  const choice = CANONICAL_CHOICES.find(c => c.placements[0]?.id === 'showcase_market')!;
  const { container } = render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={vi.fn()} onDraw={vi.fn()}/>);
  expect(container.querySelector('img')?.getAttribute('src')).toBe(pickerHeroImage('showcase_market', ''));
});
it('uses the park reference photograph while placing the same exact native model', () => {
  const choice=CANONICAL_CHOICES.find(c=>c.placements[0]?.model.variantId==='botanical_garden_v3')!;
  const source=SAVED_OPENSPACE_AESTHETIC_OPTIONS.find(o=>o.id===choice.option.id)!;
  const reference=source.variants?.find(v=>v.id==='botanical_garden_v3')?.thumbnailUrl || source.catalogCardImageUrl || source.photoUrl;
  expect(choice.option.photoUrl).toBe(reference);
  const onPlacement=vi.fn();
  const {container}=render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={onPlacement} onDraw={vi.fn()}/>);
  expect(container.querySelector('img')?.getAttribute('src')).toBe(pickerHeroImage(choice.placements[0].id, reference!));
  fireEvent.click(screen.getByRole('button',{name:/Choose & place/}));
  expect(onPlacement).toHaveBeenCalledWith(choice.placements[0]);
});

it('shows the curated copy and variant name while placing the unchanged registry asset', () => {
  const choice = CANONICAL_CHOICES.find(c => c.placements[0]?.id === 'clay_neoclassical_brick_headquarters')!;
  const asset = choice.placements[0];
  const presentation = cataloguePresentationFor(asset.id)!;
  const onPlacement = vi.fn();
  render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={onPlacement} onDraw={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button', { name: `Expand details for ${presentation.label}` }));
  expect(screen.getByText(presentation.description)).toBeDefined();
  expect(screen.queryByText(asset.description!)).toBeNull();
  expect(screen.getByRole('option', { name: presentation.label })).toBeDefined();
  fireEvent.click(screen.getByRole('button', { name: 'Choose & place' }));
  expect(onPlacement).toHaveBeenCalledWith(asset);
});

it.each(['building', 'park_plaza', 'street_pathway'] as const)('keeps %s browsing visual and reveals information without placing', domain => {
  const choice = CANONICAL_CHOICES.find(item => item.domain === domain && item.placements.length)!;
  const asset = choice.placements[0];
  const presentation = cataloguePresentationFor(asset.id);
  const label = presentation?.label ?? asset.label;
  const description = presentation?.description ?? asset.description!;
  const onPlacement = vi.fn(), onDraw = vi.fn();
  render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={onPlacement} onDraw={onDraw}/>);
  expect(screen.queryByText(description)).toBeNull();
  const expand = screen.getByRole('button', { name: `Expand details for ${label}` });
  expect(expand).toHaveAttribute('aria-expanded', 'false');
  fireEvent.click(expand);
  expect(screen.getByText(description)).toBeVisible();
  expect(onPlacement).not.toHaveBeenCalled();
  expect(onDraw).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: `Collapse details for ${label}` }));
  expect(screen.queryByText(description)).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: name => name.startsWith(`${label} · Choose &`) }));
  expect(onPlacement).toHaveBeenCalledWith(asset);
});
