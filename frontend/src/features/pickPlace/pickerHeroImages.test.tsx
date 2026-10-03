import '@testing-library/jest-dom/vitest';
import { fireEvent, render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { CanonicalCatalogueCard } from './CanonicalCatalogueCard';
import { PICKER_HERO_IMAGES, pickerHeroImage } from './pickerHeroImages';

describe('classroom picker hero views', () => {
  it('recovers from a missing hero and keeps placement usable when all exact images fail', () => {
    const choice = CANONICAL_CHOICES.find(item => item.placements[0]?.id === 'student_quiet_residential_street_v1')!;
    const onPlacement = vi.fn();
    const {container,getByText} = render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={onPlacement} onDraw={vi.fn()} />);
    fireEvent.error(container.querySelector('img')!);
    expect(container.querySelector('img')).toHaveAttribute('src', choice.placements[0].thumbnail);
    const attempted = new Set<string>();
    while (container.querySelector('img')) {
      const img=container.querySelector('img')!;
      expect(attempted.has(img.src)).toBe(false);attempted.add(img.src);
      fireEvent.error(img);
    }
    fireEvent.click(getByText('Preview image unavailable'));
    expect(onPlacement).toHaveBeenCalledWith(choice.placements[0]);
  });
  it('replaces the twelve technical thumbnails with real, staged photographic images', () => {
    expect(Object.keys(PICKER_HERO_IMAGES)).toHaveLength(12);
    const placements = new Set(CANONICAL_CHOICES.flatMap(choice => choice.placements.map(asset => asset.id)));
    expect(Object.keys(PICKER_HERO_IMAGES).filter(id => !placements.has(id))).toEqual([]);
    for (const [id, url] of Object.entries(PICKER_HERO_IMAGES)) {
      expect(url).toMatch(/^\/archetypes\/(buildings|openspaces|streets)\/classroom-heroes\/[^/]+\.webp$/);
      expect(pickerHeroImage(id, 'fallback')).toBe(url);
    }
    const unchanged = CANONICAL_CHOICES.filter(choice => !PICKER_HERO_IMAGES[choice.placements[0].id]);
    expect(unchanged).toHaveLength(CANONICAL_CHOICES.length - Object.keys(PICKER_HERO_IMAGES).length);
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
