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
    const classroomHeroes = Object.entries(PICKER_HERO_IMAGES).filter(([id]) => !id.startsWith('trial_neighborhood20_'));
    expect(classroomHeroes).toHaveLength(12);
    const placements = new Set(CANONICAL_CHOICES.flatMap(choice => choice.placements.map(asset => asset.id)));
    expect(classroomHeroes.filter(([id]) => !placements.has(id))).toEqual([]);
    for (const [id, url] of classroomHeroes) {
      expect(url).toMatch(/^\/archetypes\/(buildings|openspaces|streets)\/classroom-heroes\/[^/]+\.webp$/);
      expect(pickerHeroImage(id, 'fallback')).toBe(url);
    }
    const unchanged = CANONICAL_CHOICES.filter(choice => !PICKER_HERO_IMAGES[choice.placements[0].id]);
    expect(unchanged).toHaveLength(CANONICAL_CHOICES.length - classroomHeroes.length);
    for (const choice of unchanged) {
      const asset = choice.placements[0];
      expect(pickerHeroImage(asset.id, asset.thumbnail)).toBe(asset.thumbnail);
    }
  });

  it('uses source-front hero art for the ten local review choices without changing their GLB thumbnails', () => {
    const trial = Object.entries(PICKER_HERO_IMAGES).filter(([id]) => id.startsWith('trial_neighborhood20_'));
    expect(trial).toHaveLength(10);
    for (const [id, url] of trial) {
      expect(url).toMatch(/^\/validation-assets\/neighborhood20\/[^/]+\/hero\.png$/);
      expect(pickerHeroImage(id, '/technical-front.png')).toBe(url);
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
