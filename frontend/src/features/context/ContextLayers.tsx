import { useContext, useEffect, useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import { TilesPlugin, TilesRenderer, TilesRendererContext } from '3d-tiles-renderer/r3f';
import { GLTFExtensionsPlugin } from '3d-tiles-renderer/plugins';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import type { Material, Object3D } from 'three';
import type { ContextProviderDefinition } from './contextProvider';
import { restoreContextMaterials, setContextMaterialVisibility } from './contextVisibility';
import type { SiteZone } from '@/types';
import { TileStencilPatcher } from '@/components/viewer/globe/TileStencilPatcher';
import { retainResourceForDeferredDisposal } from '@/components/viewer/globe/strictModeResourceDisposal';

export function GoogleContextVisibility({ visible }: { visible: boolean }) {
  const tiles = useContext(TilesRendererContext);
  const invalidate = useThree(state => state.invalidate);
  useEffect(() => {
    if (!tiles) return;
    const data = tiles.group.userData;
    const previous = { sceneRole: data.sceneRole, contextProvider: data.contextProvider };
    data.sceneRole = 'existing'; data.contextProvider = 'google';
    return () => {
      for (const key of ['sceneRole', 'contextProvider'] as const) {
        if (previous[key] === undefined) delete data[key]; else data[key] = previous[key];
      }
    };
  }, [tiles]);
  useEffect(() => {
    if (!tiles || visible) return;
    const originals = new Map<Material, boolean>();
    const apply = (scene: Object3D) => { setContextMaterialVisibility(scene, visible, originals); invalidate(); };
    tiles.forEachLoadedModel(apply);
    const loaded = ({ scene }: { scene: Object3D }) => apply(scene);
    tiles.addEventListener('load-model', loaded);
    const disposed = ({ scene }: { scene: Object3D }) => {
      const released = new Map<Material, boolean>();
      setContextMaterialVisibility(scene, false, released);
      released.forEach((_, material) => originals.delete(material));
    };
    tiles.addEventListener('dispose-model', disposed);
    return () => { tiles.removeEventListener('load-model', loaded); tiles.removeEventListener('dispose-model', disposed);
      restoreContextMaterials(originals); invalidate(); };
  }, [tiles, visible, invalidate]);
  return null;
}

export function AlternateContextLayer({ provider, onReady, onFailure, zones, terrainHeight }: {
  provider: ContextProviderDefinition; onReady: () => void; onFailure: () => void;
  zones: SiteZone[]; terrainHeight: number;
}) {
  const draco = useMemo(() => new DRACOLoader().setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/'), []);
  useEffect(() => retainResourceForDeferredDisposal(draco, loader => loader.dispose()), [draco]);
  return <TilesRenderer url={provider.tilesetPath} onLoadModel={onReady} onLoadError={onFailure} errorTarget={12}>
    <TilesPlugin plugin={GLTFExtensionsPlugin} args={[{ dracoLoader: draco }]} />
    <CaptureBudget onFailure={onFailure} />
    <TileStencilPatcher zones={zones} terrainHeight={terrainHeight} />
  </TilesRenderer>;
}

function CaptureBudget({ onFailure }: { onFailure: () => void }) {
  const tiles = useContext(TilesRendererContext);
  useEffect(() => {
    if (!tiles) return;
    // Bounded sample; these are cache targets, not a claim of a hard GPU cap.
    tiles.lruCache.maxSize = 64; tiles.lruCache.minSize = 32;
    tiles.lruCache.maxBytesSize = 256 * 1024 * 1024; tiles.lruCache.minBytesSize = 128 * 1024 * 1024;
    tiles.group.userData.sceneRole = 'existing'; tiles.group.userData.contextProvider = 'survey-capture';
    const timer = window.setTimeout(onFailure, 30000);
    const loaded = () => window.clearTimeout(timer);
    tiles.addEventListener('load-model', loaded);
    return () => { window.clearTimeout(timer); tiles.removeEventListener('load-model', loaded); };
  }, [tiles, onFailure]);
  return null;
}
