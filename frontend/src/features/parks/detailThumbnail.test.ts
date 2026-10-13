import { expect, it, vi } from 'vitest';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { detailThumbnail } from './detailThumbnail';
import { detailAsset } from './detailCatalogue';

it('uses a verified pre-rendered preview without loading geometry for browsing', async () => {
  const load = vi.spyOn(GLTFLoader.prototype, 'loadAsync');
  const id = 'detail-recovered-botanical-garden-formal-fluted-urn-v1';
  expect(await detailThumbnail(id)).toBe(detailAsset(id).thumbnailUrl);
  expect(load).not.toHaveBeenCalled();
});
