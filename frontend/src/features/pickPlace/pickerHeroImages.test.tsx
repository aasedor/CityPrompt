import '@testing-library/jest-dom/vitest';
import { fireEvent, render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { CanonicalCatalogueCard } from './CanonicalCatalogueCard';
import { PICKER_HERO_IMAGES, pickerHeroImage } from './pickerHeroImages';
import curatedHeroes from '@/data/catalogueHeroImages.json';
import { CATALOGUE_ASSETS, COURT_ONLY_SPORT_ASSETS, MODULAR_BRIDGE_ASSETS, hasDrawnBridgeReplacement } from './assetRegistry';
import { PUBLIC_REALM_RELEASE_ASSETS } from './publicRealmRelease';
import buildingRelease from '@/data/claudeBuildingRelease.json';
import publicRealmRelease from '@/data/publicRealmRelease20261023.json';
import localClaudeTrial from '@/data/claudeAssetLocalTrial.json';

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
  it('covers active curated placements and retained historical images while preserving route fallbacks', () => {
    const classroomHeroes = Object.entries(PICKER_HERO_IMAGES).filter(([, url]) => url.includes('/classroom-heroes/'));
    const placements = new Set(CANONICAL_CHOICES.flatMap(choice => choice.placements.map(asset => asset.id)));
    const nativePreviewIds = new Set(COURT_ONLY_SPORT_ASSETS.map(asset => asset.id));
    const drawnBridgeIds = new Set(MODULAR_BRIDGE_ASSETS.map(asset => asset.id));
    const retainedBridges = PUBLIC_REALM_RELEASE_ASSETS.filter(hasDrawnBridgeReplacement);
    const withLocalTrials = new Set([...placements].filter(id => !drawnBridgeIds.has(id)).concat([
      ...retainedBridges.map(asset => asset.id), 'clay_twisting_glass_sky_garden_tower',
      ...buildingRelease.entries.map(row => row.asset_id),
      ...publicRealmRelease.models.filter(row => row.status === 'runtime_trial').map(row => row.asset.id),
      ...localClaudeTrial.models.filter(row => !row.retired
        && !publicRealmRelease.models.some(release => ['ready', 'runtime_trial'].includes(release.status)
          && release.asset.zoneType === row.asset.zoneType
          && release.asset.model.variantId === row.asset.model.variantId)).map(row => row.asset.id),
    ]));
    // A production test run hides local trials; their explicit hero metadata
    // must remain available on the development server without activating them.
    expect(Object.keys(curatedHeroes).sort()).toEqual([...withLocalTrials].filter(id => !nativePreviewIds.has(id)).sort());
    expect(classroomHeroes.filter(([id]) => !withLocalTrials.has(id))).toEqual([]);
    for (const asset of retainedBridges) {
      expect(placements.has(asset.id), asset.id).toBe(false);
      expect(CATALOGUE_ASSETS.find(item => item.id === asset.id), asset.id).toStrictEqual(asset);
      const hero = curatedHeroes[asset.id as keyof typeof curatedHeroes];
      expect(hero, asset.id).toBeTruthy();
      expect(pickerHeroImage(asset.id, 'fallback'), asset.id).toBe(hero);
    }
    for (const asset of COURT_ONLY_SPORT_ASSETS) {
      expect(placements.has(asset.id)).toBe(true);
      expect(asset.thumbnail).toMatch(/^\/archetypes\/openspaces\/court-only-[^/]+\/preview\.png$/);
      expect(pickerHeroImage(asset.id, asset.thumbnail)).toBe(asset.thumbnail);
    }
    for (const [id, url] of classroomHeroes) {
      expect(url).toMatch(/^\/archetypes\/(buildings|openspaces|streets)\/classroom-heroes\/[^/]+\.webp$/);
      expect(pickerHeroImage(id, 'fallback')).toBe(url);
    }
    expect(pickerHeroImage('future-archetype', '/its-reference.png')).toBe('/its-reference.png');
    expect(pickerHeroImage(undefined, '/its-reference.png')).toBe('/its-reference.png');
  });

  it.each(MODULAR_BRIDGE_ASSETS.map(asset => asset.id))('shows the exact native preview and draws the released route for %s', id => {
    const asset = MODULAR_BRIDGE_ASSETS.find(item => item.id === id)!;
    const choice = CANONICAL_CHOICES.find(item => item.placements[0]?.id === id)!;
    expect(choice).toBeDefined();
    expect(pickerHeroImage(id, asset.thumbnail)).toBe(asset.thumbnail);
    const onPlacement = vi.fn();
    const { container, getByRole } = render(<CanonicalCatalogueCard choice={choice} selected={null}
      onPlacement={onPlacement} onDraw={vi.fn()} />);
    expect(container.querySelector('img')).toHaveAttribute('src', asset.thumbnail);
    fireEvent.click(getByRole('button', { name: `${asset.label} · Choose & draw route` }));
    expect(onPlacement).toHaveBeenCalledWith(asset);
  });

  it('uses photographic park views without changing locked model thumbnails', () => {
    const sourceFronts = Object.entries(PICKER_HERO_IMAGES).filter(([id]) => id.startsWith('native-park:student_'));
    expect(sourceFronts.length).toBeGreaterThan(8);
    for (const [id, url] of sourceFronts) {
      const choice = CANONICAL_CHOICES.find(item => item.placements[0]?.id === id)!;
      expect(choice).toBeDefined();
      expect(choice.placements[0]).toBe(CATALOGUE_ASSETS.find(asset => asset.id === id));
      expect(pickerHeroImage(id, choice.placements[0].thumbnail)).toBe(url);
    }
  });

  it('uses curated ground-level heroes for the main and market streets', () => {
    for (const id of ['validation_student_main_street_v1', 'validation_student_market_street_v1']) {
      const choice = CANONICAL_CHOICES.find(item => item.placements[0]?.id === id)!;
      expect(choice).toBeDefined();
      expect(pickerHeroImage(id, choice.placements[0].thumbnail)).toBe(curatedHeroes[id as keyof typeof curatedHeroes]);
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
    'native-park:student_urban_splash_plaza_v1--native-v1',
    'student_quiet_residential_street_v1'])('shows the hero on the actual picker card for %s', id => {
    const choice = CANONICAL_CHOICES.find(item => item.placements[0]?.id === id)!;
    const { container } = render(<CanonicalCatalogueCard choice={choice} selected={null}
      onPlacement={vi.fn()} onDraw={vi.fn()} />);
    expect(container.querySelector('img')).toHaveAttribute('src', PICKER_HERO_IMAGES[id]);
  });
});
