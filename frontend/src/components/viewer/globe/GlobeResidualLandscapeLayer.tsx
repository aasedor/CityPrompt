import { useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import * as THREE from 'three';

import type { SiteZone } from '@/types';
import {
  computeCentroid,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';
import { GlobeLandscapeTreeStand } from './GlobeLandscapeKit';
import { raycastObjectFilteredTerrainHeightAtLatLng } from './GlobeZoneLayer';
import { isPlausibleTerrainAnchor } from './globeTerrainUtils';
import {
  getResidualLandscapeRecipe,
  type ResidualLandscapeRecipe,
} from './residualLandscape';
import { resolveParkTreeVariant } from './publicRealmPropPalettes';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { useSharedSiteGround } from './SharedSiteGroundProvider';

const DEG_TO_RAD = Math.PI / 180;
const TERRAIN_SAMPLE_INTERVAL_FRAMES = 30;
const TERRAIN_SAMPLE_BATCH_SIZE = 16;

function storedTerrainHeight(zone: SiteZone): number | null {
  const properties = zone.properties as Record<string, unknown> | undefined;
  const value = Number(properties?.terrain_elevation_m ?? properties?.terrain_height);
  return Number.isFinite(value) ? value : null;
}

function ResidualLandscapeInstance({
  zone,
  recipe,
  fallbackTerrainHeight,
  preparedTerrain,
}: {
  zone: SiteZone;
  recipe: ResidualLandscapeRecipe;
  fallbackTerrainHeight: number;
  preparedTerrain: number | null;
}) {
  const tiles = useContext(TilesRendererContext);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameRef = useRef(0);
  const nextPlacementRef = useRef(0);
  const [zOffsets, setZOffsets] = useState<number[]>(() => (
    recipe.placements.map(() => 0)
  ));
  const centroid = useMemo(
    () => computeCentroid(zone.coordinates),
    [zone.coordinates],
  );
  const sharedGround = useSharedSiteGround();
  const sharedActive = sharedGround.status !== 'inactive'
    && recipe.placements.every((placement) => sharedGround.contains(placement.lng, placement.lat));
  const sharedFrame = sharedActive ? sharedGround.heightAt(centroid[0], centroid[1])
    ?? sharedGround.heightAt(recipe.placements[0].lng, recipe.placements[0].lat) : null;
  const frameHeight = sharedFrame ?? preparedTerrain ?? storedTerrainHeight(zone) ?? fallbackTerrainHeight;

  useEffect(() => {
    nextPlacementRef.current = 0;
    setZOffsets(recipe.placements.map(() => 0));
  }, [recipe.placements]);

  useFrame(() => {
    if (sharedActive || preparedTerrain !== null || nextPlacementRef.current >= recipe.placements.length) return;
    frameRef.current += 1;
    if (frameRef.current % TERRAIN_SAMPLE_INTERVAL_FRAMES !== 0) return;
    const tilesGroup = tiles?.group;
    if (!tilesGroup?.children.length) return;

    const start = nextPlacementRef.current;
    const end = Math.min(start + TERRAIN_SAMPLE_BATCH_SIZE, recipe.placements.length);
    setZOffsets((previous) => {
      const next = previous.slice();
      for (let index = start; index < end; index += 1) {
        const placement = recipe.placements[index];
        const sampled = raycastObjectFilteredTerrainHeightAtLatLng(
          placement.lng,
          placement.lat,
          tilesGroup,
          raycasterRef.current,
          frameHeight,
          [4.5],
        );
        next[index] = isPlausibleTerrainAnchor(sampled, frameHeight)
          ? (sampled as number) - frameHeight
          : 0;
      }
      return next;
    });
    nextPlacementRef.current = end;
  });

  const placements = useMemo(() => {
    const metresPerLongitudeDegree = metersPerDegLon(centroid[1]);
    return recipe.placements.map((placement, index) => ({
      x: (placement.lng - centroid[0]) * metresPerLongitudeDegree,
      y: (placement.lat - centroid[1]) * METERS_PER_DEG_LAT,
      z: sharedActive ? (sharedGround.heightAt(placement.lng, placement.lat) ?? frameHeight) - frameHeight : zOffsets[index] ?? 0,
      yawRad: placement.yaw_rad,
      scale: placement.scale,
      treeVariant: resolveParkTreeVariant(
        'native_meadow',
        `${zone.id}:${placement.id}:${index}`,
      ),
    }));
  }, [centroid, recipe.placements, zone.id, zOffsets, sharedActive, sharedGround, frameHeight]);

  if (!placements.length || (sharedActive && sharedGround.status !== 'ready')) return null;
  return (
    <EastNorthUpFrame
      lat={centroid[1] * DEG_TO_RAD}
      lon={centroid[0] * DEG_TO_RAD}
      height={frameHeight}
    >
      <GlobeLandscapeTreeStand placements={placements} renderOrder={143} />
    </EastNorthUpFrame>
  );
}

/** Generated canopy for the exact site-boundary remainder. It is proposal
 * content, so it remains mounted when editable planning overlays are hidden. */
export function GlobeResidualLandscapeLayer({
  zones,
  terrainHeight,
}: {
  zones: SiteZone[];
  terrainHeight: number;
}) {
  return (
    <>
      {zones.map((zone) => {
        const recipe = getResidualLandscapeRecipe(zone);
        if (!recipe || !recipe.placements.length) return null;
        return (
          <ResidualLandscapeInstance
            key={`${zone.id}-${recipe.source_hash}-${resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)}`}
            zone={zone}
            recipe={recipe}
            fallbackTerrainHeight={terrainHeight}
            preparedTerrain={resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)}
          />
        );
      })}
    </>
  );
}
