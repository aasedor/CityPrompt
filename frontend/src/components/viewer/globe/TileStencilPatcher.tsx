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
import { unpatchMaterialStencil } from './StencilMaskPlugin';
import type { SiteZone } from '@/types';
import {
  createTileSpatialMaskSetConfig,
  patchMaterialForSpatialMask,
  unpatchMaterialSpatialMask,
} from './TileSpatialMaskPlugin';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { resolvePreparedSiteTerrainHeight } from './sitePreparationSurface';
import { useParkAssemblyGroundOwners } from './ParkAssemblyGround';

interface TileStencilPatcherProps {
  /** Only patch when there are zones that need tile masking. */
  zones: SiteZone[];
  terrainHeight: number;
  assemblyZones?: SiteZone[];
}

const NO_ASSEMBLY_ZONES: SiteZone[] = [];

export function TileStencilPatcher({ zones, terrainHeight, assemblyZones = NO_ASSEMBLY_ZONES }: TileStencilPatcherProps) {
  const tiles = useContext(TilesRendererContext);
  const parkGroundOwners = useParkAssemblyGroundOwners(assemblyZones);
  const patchedMaterials = useRef(new Set<THREE.Material>());
  const spatialMask = useMemo(
    () => {
      const siteBoundary = getActiveSiteBoundary(zones);
      return createTileSpatialMaskSetConfig(
        // The caller already reduces a prepared site to its boundary plus
        // supported public-road extensions. Do not discard those outside cuts.
        siteBoundary ? zones : [...zones, ...parkGroundOwners.filter(owner => !zones.some(zone => zone.id === owner.id))],
        siteBoundary ? resolvePreparedSiteTerrainHeight(siteBoundary, terrainHeight) : terrainHeight,
      );
    },
    [zones, terrainHeight, parkGroundOwners],
  );

  useEffect(() => {
    const unpatchAll = () => {
      patchedMaterials.current.forEach((material) => {
        unpatchMaterialSpatialMask(material);
        unpatchMaterialStencil(material);
      });
      patchedMaterials.current.clear();
    };

    if (!tiles || !spatialMask) {
      // Unsupported/invalid geometry retains real context. Projected stencil
      // fallback would clear pixels outside the actual site in oblique views.
      unpatchAll();
      return;
    }

    const patchMaterial = (material: THREE.Material) => {
      if (patchedMaterials.current.has(material)) return;
      patchMaterialForSpatialMask(material, spatialMask);
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
  }, [spatialMask, tiles]);

  return null;
}
