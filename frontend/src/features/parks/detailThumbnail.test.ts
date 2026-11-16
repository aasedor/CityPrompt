import { expect, it, vi } from 'vitest';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { detailThumbnail } from './detailThumbnail';
import { detailAsset } from './detailCatalogue';
import people from '../people/peopleCatalogue.json';
import inclusivePeople from '../people/inclusivePeopleCatalogue.json';
import extras from './detailCatalogueExtras.json';

it('uses realistic People appearance previews without changing source model data or loading geometry', async () => {
  const load = vi.spyOn(GLTFLoader.prototype, 'loadAsync');
  for (const actor of [...people, ...inclusivePeople]) {
    const asset = detailAsset(actor.id);
    expect(await detailThumbnail(actor.id)).toBe(asset.appearancePreview?.url);
    expect(asset.appearancePreview?.url).toMatch(/people-appearance-v\d+\/.+\.webp$/);
    expect(asset.url).toBe(actor.url);
    expect(asset.people).toEqual('people' in actor ? actor.people : undefined);
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

it('shows the local prairie and Calgary kits from static cards without loading any model', async () => {
  const load = vi.spyOn(GLTFLoader.prototype, 'loadAsync');
  const local = extras.filter((model) => model.sourceKit === 'prairie-foliage-v1' || model.sourceKit === 'calgary-details-v1');
  expect(local).toHaveLength(108);
  for (const model of local) {
    expect(await detailThumbnail(model.id)).toBe(model.url.replace(/\.glb$/, '.webp'));
  }
  expect(load).not.toHaveBeenCalled();
});
