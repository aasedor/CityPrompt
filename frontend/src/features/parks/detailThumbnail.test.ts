import { expect, it, vi } from 'vitest';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { detailThumbnail } from './detailThumbnail';
import { detailAsset } from './detailCatalogue';
import people from '../people/peopleCatalogue.json';

it('uses realistic People appearance previews without changing source model data or loading geometry', async () => {
  const load = vi.spyOn(GLTFLoader.prototype, 'loadAsync');
  for (const actor of people) {
    const asset = detailAsset(actor.id);
    expect(await detailThumbnail(actor.id)).toMatch(/people-appearance-v1\/.+\.webp$/);
    expect(asset.url).toBe(actor.url);
    expect(asset.people).toEqual(actor.people);
    expect(asset.thumbnailUrl).toBe(actor.thumbnailUrl);
  }
  expect(load).not.toHaveBeenCalled();
});

it('uses a verified pre-rendered preview without loading geometry for browsing', async () => {
  const load = vi.spyOn(GLTFLoader.prototype, 'loadAsync');
  const id = 'detail-recovered-botanical-garden-formal-fluted-urn-v1';
  expect(await detailThumbnail(id)).toBe(detailAsset(id).thumbnailUrl);
  expect(load).not.toHaveBeenCalled();
});
