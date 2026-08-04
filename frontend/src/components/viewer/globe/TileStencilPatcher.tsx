/**
 * TileStencilPatcher.tsx — Patches incoming Google 3D Tile materials
 * to respect the stencil buffer, so buildings inside zone polygons
 * are cut away (not rendered).
 *
 * Must be placed inside <TilesRenderer> to access TilesRendererContext.
 */

import { useEffect, useContext, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { TilesRendererContext } from '3d-tiles-renderer/r3f';
import {
  patchMaterialForStencil,
  shouldCreateTileStencilMask,
  unpatchMaterialStencil,
} from './StencilMaskPlugin';
import type { SiteZone } from '@/types';
import {
  createTileSpatialMaskSetConfig,
  patchMaterialForSpatialMask,
  unpatchMaterialSpatialMask,
} from './TileSpatialMaskPlugin';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';

interface TileStencilPatcherProps {
  /** Only patch when there are zones that need tile masking. */
  zones: SiteZone[];
  terrainHeight: number;
}

export function TileStencilPatcher({ zones, terrainHeight }: TileStencilPatcherProps) {
  const tiles = useContext(TilesRendererContext);
  const patchedMaterials = useRef(new Set<THREE.Material>());
  const spatialMask = useMemo(
    () => {
      const siteBoundary = getActiveSiteBoundary(zones);
      return createTileSpatialMaskSetConfig(
        siteBoundary ? [siteBoundary] : zones,
        terrainHeight,
      );
    },
    [zones, terrainHeight],
  );
  const hasStencilZones = !spatialMask && zones.some(
    (zone) => shouldCreateTileStencilMask(zone.zone_type) && zone.coordinates.length >= 3,
  );

  useEffect(() => {
    const unpatchAll = () => {
      patchedMaterials.current.forEach((material) => {
        unpatchMaterialSpatialMask(material);
        unpatchMaterialStencil(material);
      });
      patchedMaterials.current.clear();
    };

    if (!tiles || (!spatialMask && !hasStencilZones)) {
      // Unpatch all if no zones need masking.
      unpatchAll();
      return;
    }

    const patchMaterial = (material: THREE.Material) => {
      if (patchedMaterials.current.has(material)) return;
      if (spatialMask) {
        patchMaterialForSpatialMask(material, spatialMask);
      } else {
        patchMaterialForStencil(material);
      }
      patchedMaterials.current.add(material);
    };

    const handleLoadModel = (event: any) => {
      const { scene } = event;
      if (!scene) return;

      scene.traverse((child: any) => {
        if (child.isMesh && child.material) {
          const materials = Array.isArray(child.material) ? child.material : [child.material];
          for (const mat of materials) {
            patchMaterial(mat);
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
              patchMaterial(mat);
            }
          }
        });
      });
    }

    // Patch new tiles as they load
    tiles.addEventListener('load-model', handleLoadModel);

    return () => {
      tiles.removeEventListener('load-model', handleLoadModel);
      unpatchAll();
    };
  }, [hasStencilZones, spatialMask, tiles]);

  return null;
}
