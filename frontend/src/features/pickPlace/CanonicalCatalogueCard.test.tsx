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
  expect(screen.getByText(presentation.description)).toBeDefined();
  expect(screen.queryByText(asset.description!)).toBeNull();
  expect(screen.getByRole('option', { name: presentation.label })).toBeDefined();
  fireEvent.click(screen.getByRole('button', { name: /Choose & place/ }));
  expect(onPlacement).toHaveBeenCalledWith(asset);
});
