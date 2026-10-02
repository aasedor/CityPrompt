import type { MultiPolygon } from 'polygon-clipping';

export const PARCEL_FABRIC_SOURCE = 'https://www.arcgis.com/home/item.html?id=d65f01030ee6494b98b7bdce021a4b25';
export const PARCEL_TILE_ROOT = 'https://tiles.arcgis.com/tiles/AVP60cs0Q9PEA8rH/arcgis/rest/services/Calgary_VectorBasemap/VectorTileServer';
type Bounds = [number, number, number, number];
const ZOOM = 16;

export function fabricTiles([w, s, e, n]: Bounds): { x: number; y: number; z: number }[] {
  const x = (lng: number) => Math.floor((lng + 180) / 360 * 2 ** ZOOM);
  const y = (lat: number) => Math.floor((1 - Math.asinh(Math.tan(lat * Math.PI / 180)) / Math.PI) / 2 * 2 ** ZOOM);
  if ((x(e) - x(w) + 1) * (y(s) - y(n) + 1) > 64) throw new Error('Choose a smaller site to load complete parcel boundaries.');
  const tiles = [];
  for (let tx = x(w); tx <= x(e); tx++) for (let ty = y(n); ty <= y(s); ty++) tiles.push({ x: tx, y: ty, z: ZOOM });
  return tiles;
}

export function polygonArea(coordinates: MultiPolygon): number {
  return coordinates.reduce((sum, polygon) => sum + polygon.reduce((net, ring, index) => {
    const [ox, oy] = ring[0];
    const area = Math.abs(ring.slice(1).reduce((total, p, j) => total + (ring[j][0] - ox) * (p[1] - oy) - (p[0] - ox) * (ring[j][1] - oy), 0)) / 2;
    return net + (index === 0 ? area : -area);
  }, 0), 0);
}

function boundsOf(geometry: MultiPolygon): Bounds {
  const bounds: Bounds = [Infinity, Infinity, -Infinity, -Infinity];
  for (const poly of geometry) for (const [x, y] of poly[0]) {
    bounds[0] = Math.min(bounds[0], x); bounds[1] = Math.min(bounds[1], y);
    bounds[2] = Math.max(bounds[2], x); bounds[3] = Math.max(bounds[3], y);
  }
  return bounds;
}

/** Rejoin buffered tile fragments by positive-area overlap; never dissolve adjoining lots. */
export async function mergeParcelFragments(fragments: MultiPolygon[], bounds: Bounds, signal?: AbortSignal): Promise<MultiPolygon[]> {
  const { default: clipping } = await import('polygon-clipping');
  const [w, s, e, n] = bounds;
  const extent: MultiPolygon = [[[[w, s], [e, s], [e, n], [w, n], [w, s]]]];
  const merged: { geometry: MultiPolygon; bounds: Bounds }[] = [];
  for (let index = 0; index < fragments.length; index++) {
    if (index % 50 === 0) { await new Promise(resolve => setTimeout(resolve, 0)); signal?.throwIfAborted(); }
    let geometry = clipping.intersection(fragments[index], extent);
    if (polygonArea(geometry) < 1e-12) continue;
    let b = boundsOf(geometry);
    for (let i = merged.length - 1; i >= 0; i--) {
      const other = merged[i], a = other.bounds;
      if (a[2] <= b[0] || a[0] >= b[2] || a[3] <= b[1] || a[1] >= b[3]) continue;
      if (polygonArea(clipping.intersection(other.geometry, geometry)) > 1e-12) {
        geometry = clipping.union(other.geometry, geometry); b = boundsOf(geometry); merged.splice(i, 1);
        i = merged.length; // The enlarged parcel may now reach a previously checked fragment.
      }
    }
    merged.push({ geometry, bounds: b });
    if (merged.length > 1500) throw new Error('This site contains too many parcels. Choose a smaller site.');
  }
  return merged.map(p => p.geometry);
}

export async function fetchParcelFabric(bounds: Bounds, signal: AbortSignal): Promise<MultiPolygon[]> {
  const [{ VectorTile }, { default: Pbf }] = await Promise.all([import('@mapbox/vector-tile'), import('pbf')]);
  const tiles = fabricTiles(bounds);
  const fragments: MultiPolygon[] = [];
  // Four simultaneous map requests; no city-wide downloads or persistent data copies.
  for (let offset = 0; offset < tiles.length; offset += 4) {
    const batch = await Promise.all(tiles.slice(offset, offset + 4).map(async ({ x, y, z }) => {
      const response = await fetch(`${PARCEL_TILE_ROOT}/tile/${z}/${y}/${x}.pbf`, { signal });
      if (!response.ok) throw new Error('Calgary parcel boundaries could not load. Try again.');
      const tile = new VectorTile(new Pbf(new Uint8Array(await response.arrayBuffer())));
      const polygons: MultiPolygon[] = [];
      // These are ownership polygons. Street centerlines and road surfaces are deliberately absent.
      for (const name of ['Ownership Parcel RP', 'Ownership Parcle NR']) {
        const layer = tile.layers[name];
        if (!layer) continue;
        for (let i = 0; i < layer.length; i++) {
          const feature = layer.feature(i);
          if (feature.type !== 3) continue;
          const geometry = feature.toGeoJSON(x, y, z).geometry;
          if (geometry.type === 'Polygon') polygons.push([geometry.coordinates] as MultiPolygon);
          else if (geometry.type === 'MultiPolygon') polygons.push(geometry.coordinates as MultiPolygon);
        }
      }
      return polygons;
    }));
    fragments.push(...batch.flat());
    if (fragments.length > 8000) throw new Error('This site contains too many parcel details. Choose a smaller site.');
  }
  return mergeParcelFragments(fragments, bounds, signal);
}
