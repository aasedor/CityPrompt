import '@testing-library/jest-dom/vitest';
import { render, screen, cleanup, fireEvent } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { CanonicalCatalogueCard } from './CanonicalCatalogueCard';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { SAVED_OPENSPACE_AESTHETIC_OPTIONS } from '@/components/viewer/aestheticCatalog';
import { pickerHeroImage } from './pickerHeroImages';
import { cataloguePresentationFor } from './cataloguePresentation';

afterEach(cleanup);
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
