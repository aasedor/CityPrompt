import { useEffect, useState } from 'react';
import * as THREE from 'three';
import { LANDSCAPE_TREE_PROFILES, LANDSCAPE_TREE_VARIANTS } from './landscapeKitProfiles';

// Shared, bounded texture cache, like useTexture's cache. A missing decorative
// image must not throw out of the globe and destroy the student's editing UI.
const textures = new Map<string, Promise<THREE.Texture>>();
let fallback: THREE.DataTexture | undefined;
export function landscapeFoliageFallback(): THREE.DataTexture {
  if (fallback) return fallback;
  const size = 32, data = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const dx = (x - 15.5) / 15.5, dy = (y - 15.5) / 15.5;
    const i = (y * size + x) * 4;
    data[i] = 82; data[i + 1] = 119; data[i + 2] = 56;
    data[i + 3] = dx * dx + dy * dy < 0.87 + 0.09 * Math.sin(x * 3 + y * 7) ? 255 : 0;
  }
  fallback = new THREE.DataTexture(data, size, size);
  fallback.colorSpace = THREE.SRGBColorSpace;
  fallback.needsUpdate = true;
  return fallback;
}

function load(url: string): Promise<THREE.Texture> {
  if (!textures.has(url)) {
    textures.set(url, new THREE.TextureLoader().loadAsync(url).catch(() => {
      console.warn(`Landscape texture unavailable; using simple foliage: ${url}`);
      return landscapeFoliageFallback();
    }));
  }
  return textures.get(url)!;
}

export function useLandscapeTreeTextures(): THREE.Texture[] {
  const [loaded, setLoaded] = useState<THREE.Texture[]>(() =>
    LANDSCAPE_TREE_VARIANTS.map(() => landscapeFoliageFallback()));
  useEffect(() => {
    let active = true;
    void Promise.all(LANDSCAPE_TREE_VARIANTS.map(variant => load(LANDSCAPE_TREE_PROFILES[variant].textureUrl)))
      .then(result => { if (active) setLoaded(result); });
    return () => { active = false; };
  }, []);
  return loaded;
}
