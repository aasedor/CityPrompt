/**
 * TileStencilPatcher.tsx — Patches incoming Google 3D Tile materials
 * to respect the stencil buffer, so buildings inside zone polygons
 * are cut away (not rendered).
 *
 * Must be placed inside <TilesRenderer> to access TilesRendererContext.
 */

import { useEffect, useContext, useRef } from 'react';
import * as THREE from 'three';
import { TilesRendererContext } from '3d-tiles-renderer/r3f';
import { patchMaterialForStencil, unpatchMaterialStencil } from './StencilMaskPlugin';
import type { SiteZone } from '@/types';

interface TileStencilPatcherProps {
  /** Only patch when there are building zones that need masking */
  zones: SiteZone[];
}

export function TileStencilPatcher({ zones }: TileStencilPatcherProps) {
  const tiles = useContext(TilesRendererContext);
  const patchedMaterials = useRef(new Set<THREE.Material>());

  const hasBuildingZones = zones.some(
    z => (z.zone_type === 'building' || z.zone_type === 'residential') && z.coordinates.length >= 3
  );

  useEffect(() => {
    if (!tiles || !hasBuildingZones) {
      // Unpatch all if no building zones
      patchedMaterials.current.forEach(m => unpatchMaterialStencil(m));
      patchedMaterials.current.clear();
      return;
    }

    const handleLoadModel = (event: any) => {
      const { scene } = event;
      if (!scene) return;

      scene.traverse((child: any) => {
        if (child.isMesh && child.material) {
          const materials = Array.isArray(child.material) ? child.material : [child.material];
          for (const mat of materials) {
            if (!patchedMaterials.current.has(mat)) {
              patchMaterialForStencil(mat);
              patchedMaterials.current.add(mat);
            }
          }
        }
      });
    };

    // Patch existing loaded tiles
    if (tiles.forEachLoadedModel) {
      tiles.forEachLoadedModel((scene: any) => {
        scene.traverse((child: any) => {
          if (child.isMesh && child.material) {
            const materials = Array.isArray(child.material) ? child.material : [child.material];
            for (const mat of materials) {
              if (!patchedMaterials.current.has(mat)) {
                patchMaterialForStencil(mat);
                patchedMaterials.current.add(mat);
              }
            }
          }
        });
      });
    }

    // Patch new tiles as they load
    tiles.addEventListener('load-model', handleLoadModel);

    return () => {
      tiles.removeEventListener('load-model', handleLoadModel);
      // Unpatch all on cleanup
      patchedMaterials.current.forEach(m => unpatchMaterialStencil(m));
      patchedMaterials.current.clear();
    };
  }, [tiles, hasBuildingZones]);

  return null;
}
