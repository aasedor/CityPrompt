import { render, screen, cleanup, fireEvent } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { CanonicalCatalogueCard } from './CanonicalCatalogueCard';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { SAVED_OPENSPACE_AESTHETIC_OPTIONS } from '@/components/viewer/aestheticCatalog';

afterEach(cleanup);
it('uses the park reference photograph while placing the same exact native model', () => {
  const choice=CANONICAL_CHOICES.find(c=>c.placements[0]?.model.variantId==='botanical_garden_v3')!;
  const source=SAVED_OPENSPACE_AESTHETIC_OPTIONS.find(o=>o.id===choice.option.id)!;
  const reference=source.variants?.find(v=>v.id==='botanical_garden_v3')?.thumbnailUrl || source.catalogCardImageUrl || source.photoUrl;
  expect(choice.option.photoUrl).toBe(reference);
  const onPlacement=vi.fn();
  const {container}=render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={onPlacement} onDraw={vi.fn()}/>);
  expect(container.querySelector('img')?.getAttribute('src')).toBe(reference);
  fireEvent.click(screen.getByRole('button',{name:/Choose & place/}));
  expect(onPlacement).toHaveBeenCalledWith(choice.placements[0]);
});
