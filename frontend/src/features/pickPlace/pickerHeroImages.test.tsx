import '@testing-library/jest-dom/vitest';
import { render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { CanonicalCatalogueCard } from './CanonicalCatalogueCard';
import { PICKER_HERO_IMAGES, pickerHeroImage } from './pickerHeroImages';

describe('classroom picker hero views', () => {
  it('replaces the twelve technical thumbnails with real, staged photographic images', () => {
    expect(Object.keys(PICKER_HERO_IMAGES)).toHaveLength(12);
    const placements = new Set(CANONICAL_CHOICES.flatMap(choice => choice.placements.map(asset => asset.id)));
    expect(Object.keys(PICKER_HERO_IMAGES).filter(id => !placements.has(id))).toEqual([]);
    for (const [id, url] of Object.entries(PICKER_HERO_IMAGES)) {
      expect(url).toMatch(/^\/archetypes\/(buildings|openspaces|streets)\/classroom-heroes\/[^/]+\.webp$/);
      expect(pickerHeroImage(id, 'fallback')).toBe(url);
    }
    const unchanged = CANONICAL_CHOICES.filter(choice => !PICKER_HERO_IMAGES[choice.placements[0].id]);
    expect(unchanged).toHaveLength(33);
    for (const choice of unchanged) {
      const asset = choice.placements[0];
      expect(pickerHeroImage(asset.id, asset.thumbnail)).toBe(asset.thumbnail);
    }
  });

  it.each(['validation_machiya_cafe_gallery',
    'native-park:student_reading_garden_v2--native-v1',
    'student_quiet_residential_street_v1'])('shows the hero on the actual picker card for %s', id => {
    const choice = CANONICAL_CHOICES.find(item => item.placements[0]?.id === id)!;
    const { container } = render(<CanonicalCatalogueCard choice={choice} selected={null}
      onPlacement={vi.fn()} onDraw={vi.fn()} />);
    expect(container.querySelector('img')).toHaveAttribute('src', PICKER_HERO_IMAGES[id]);
  });
});
