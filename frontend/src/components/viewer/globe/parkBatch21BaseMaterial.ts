import { useEffect, useMemo, useState } from 'react';
import * as THREE from 'three';
import { batch21ParkSkinForSelection } from './parkBatch21Skins';
import { batch22ParkSkinForSelection } from './parkBatch22Skins';
import { batch23ParkSkinForSelection } from './parkBatch23Skins';
import { batch24ParkSkinForSelection } from './parkBatch24Skins';
import { batch25ParkSkinForSelection } from './parkBatch25Skins';

export type Batch21ParkBaseRole = 'paver' | 'lawn' | 'planting';

export interface Batch21ParkBaseMaterialSpec {
  slug: string;
  role: Batch21ParkBaseRole;
  metersPerTile: number;
}

export interface Batch21ParkBaseMaterialMaps {
  map: THREE.Texture;
  normalMap: THREE.Texture;
  roughnessMap: THREE.Texture;
}

/** The compiled polygon is the tile-flattening mask as well as the visual
 * ground plane. Give it the exact archetype skin instead of the generic
 * plaza/grass texture so an owned LEGO kit never sits on a monochrome slab. */
export function resolveBatch21ParkBaseMaterial(
  archetypeId: string,
  variantId: string,
): Batch21ParkBaseMaterialSpec | null {
  const skin = batch25ParkSkinForSelection(archetypeId, variantId)
    ?? batch24ParkSkinForSelection(archetypeId, variantId)
    ?? batch23ParkSkinForSelection(archetypeId, variantId)
    ?? batch22ParkSkinForSelection(archetypeId, variantId)
    ?? batch21ParkSkinForSelection(archetypeId, variantId);
  if (!skin) return null;
  if (archetypeId === 'athletics_precinct_sports_fields') {
    return { slug: skin.slug, role: 'lawn', metersPerTile: 5.5 };
  }
  if (archetypeId === 'linear_park_greenway' || archetypeId === 'nature_preserve') {
    return { slug: skin.slug, role: 'planting', metersPerTile: 5.0 };
  }
  if (archetypeId === 'amsterdam_vondelpark'
    || archetypeId === 'amsterdam_hofje_garden'
    || archetypeId === 'barcelona_pati_interior'
    || archetypeId === 'barcelona_superilla') {
    return { slug: skin.slug, role: 'planting', metersPerTile: 4.0 };
  }
  if (archetypeId === 'parisian_jardin' && variantId !== 'parisian_jardin_v3') {
    return { slug: skin.slug, role: 'planting', metersPerTile: 4.0 };
  }
  if (archetypeId === 'calgary_princes_island'
    || archetypeId === 'halifax_coastal_park'
    || archetypeId === 'halifax_public_gardens'
    || archetypeId === 'montreal_mount_royal'
    || archetypeId === 'newyork_community_garden') {
    return { slug: skin.slug, role: 'planting', metersPerTile: 4.0 };
  }
  if (archetypeId === 'vancouver_beach_park'
    || archetypeId === 'toronto_ravine'
    || archetypeId === 'picturesque_olmsted_park'
    || archetypeId === 'hilltop_topographic_park'
    || archetypeId === 'estate_picnic_grove') {
    return { slug: skin.slug, role: 'planting', metersPerTile: 4.5 };
  }
  if (archetypeId === 'reclaimed_industrial_park'
    || archetypeId === 'quarry_sunken_garden_park'
    || archetypeId === 'reservoir_watershed_park') {
    return { slug: skin.slug, role: variantId.endsWith('_v3') ? 'planting' : 'lawn', metersPerTile: 5.0 };
  }
  if (archetypeId === 'calgary_prairie_plaza' && variantId !== 'calgary_prairie_plaza_v3') {
    return { slug: skin.slug, role: 'planting', metersPerTile: 4.0 };
  }
  if (archetypeId === 'london_garden_square' && variantId !== 'london_garden_square_v3') {
    return { slug: skin.slug, role: 'planting', metersPerTile: 4.0 };
  }
  if (archetypeId === 'pond_lake' || archetypeId === 'stormwater_retention_pond' || archetypeId === 'riverfront_park_beach') {
    return { slug: skin.slug, role: 'lawn', metersPerTile: 5.0 };
  }
  if (archetypeId === 'rooftop_garden' && variantId !== 'rooftop_garden_v3') {
    return { slug: skin.slug, role: 'planting', metersPerTile: 4.0 };
  }
  return { slug: skin.slug, role: 'paver', metersPerTile: 3.5 };
}

export function useBatch21ParkBaseMaterial(
  archetypeId: string,
  variantId: string,
  active: boolean,
): { spec: Batch21ParkBaseMaterialSpec; maps: Batch21ParkBaseMaterialMaps } | null {
  const spec = useMemo(
    () => (active ? resolveBatch21ParkBaseMaterial(archetypeId, variantId) : null),
    [active, archetypeId, variantId],
  );
  const [maps, setMaps] = useState<Batch21ParkBaseMaterialMaps | null>(null);

  useEffect(() => {
    if (!spec) {
      setMaps(null);
      return undefined;
    }
    let cancelled = false;
    let loaded: Batch21ParkBaseMaterialMaps | null = null;
    const root = `/park-skins/${spec.slug}/adaptive-v1/${spec.role}`;
    const loader = new THREE.TextureLoader();
    void Promise.all([
      loader.loadAsync(`${root}/albedo.jpg`),
      loader.loadAsync(`${root}/normal.png`),
      loader.loadAsync(`${root}/roughness.jpg`),
    ]).then(([map, normalMap, roughnessMap]) => {
      loaded = { map, normalMap, roughnessMap };
      Object.values(loaded).forEach((texture) => {
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.repeat.set(1 / spec.metersPerTile, 1 / spec.metersPerTile);
        texture.needsUpdate = true;
      });
      map.colorSpace = THREE.SRGBColorSpace;
      if (!cancelled) setMaps(loaded);
      else Object.values(loaded).forEach((texture) => texture.dispose());
    }).catch((error) => {
      if (!cancelled) console.warn('[parkBatch21BaseMaterial] texture fetch failed', error);
    });
    return () => {
      cancelled = true;
      setMaps(null);
      if (loaded) Object.values(loaded).forEach((texture) => texture.dispose());
    };
  }, [spec]);

  return spec && maps ? { spec, maps } : null;
}
