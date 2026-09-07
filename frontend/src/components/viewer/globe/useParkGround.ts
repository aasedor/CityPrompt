import { useMemo } from 'react';
import type { SiteZone } from '@/types';
import {
  useSharedSiteGround,
  type SharedSiteGroundState,
} from './SharedSiteGroundProvider';
import { parkTerrainContains, readParkTerrain } from './parkTerrain';
import {
  createSharedSiteGroundLayout,
  sharedSiteGroundGridPoint,
  sampleSharedSiteGround,
} from './sharedSiteGround';
import { useAutomaticParkContext } from './AutomaticParkGround';
import type { ParkTerrainProfile } from './parkTerrain';

/** Saved park surface takes precedence over the site's level, in every layer. */
export function useParkGround(zone: SiteZone): SharedSiteGroundState {
  const shared = useSharedSiteGround();
  const automatic = useAutomaticParkContext();
  return useMemo(() => {
    if (!zone.properties?.park_terrain && !automatic.ids.has(zone.id))
      return shared;
    const snapshot = readParkTerrain(zone);
    if (!snapshot && automatic.ids.has(zone.id)) {
      const previous = (
        zone.properties?.park_terrain as ParkTerrainProfile | undefined
      )?.snapshot;
      const old =
        previous &&
        readParkTerrain({ ...zone, coordinates: previous.boundaryCoordinates });
      const g = old?.grid;
      const west = g?.west ?? 0,
        south = g?.south ?? 0,
        east = g ? west + (g.columns - 1) * g.stepLng : 0,
        north = g ? south + (g.rows - 1) * g.stepLat : 0;
      const support = old
        ? {
            ...old,
            boundaryCoordinates: [
              [west, south],
              [east, south],
              [east, north],
              [west, north],
            ] as Array<[number, number]>,
          }
        : null;
      // Every draft layer uses the same triangles. Independent subdivisions
      // made the lawn and paths intersect each other during a move.
      const layout = createSharedSiteGroundLayout(zone, 1.25);
      const approximate = (lng: number, lat: number) =>
        support
          ? sampleSharedSiteGround(
              support,
              Math.max(west, Math.min(east, lng)),
              Math.max(south, Math.min(north, lat)),
            )
          : automatic.fallback;
      const draft =
        layout && old
          ? {
              ...old,
              ...layout,
              heights: Array.from(
                { length: layout.grid.columns * layout.grid.rows },
                (_, i) => {
                  const [lng, lat] = sharedSiteGroundGridPoint(layout, i);
                  return approximate(lng, lat) ?? automatic.fallback;
                },
              ),
            }
          : null;
      return {
        status: 'sampling',
        preview: true,
        snapshot: null,
        draftLayout: layout ?? undefined,
        contains: (lng, lat) => parkTerrainContains(zone, lng, lat),
        heightAt: (lng, lat) =>
          draft
            ? sampleSharedSiteGround(draft, lng, lat)
            : approximate(lng, lat),
        revision: `draft:${JSON.stringify(zone.coordinates)}:${old?.signature ?? automatic.fallback}`,
      };
    }
    return {
      status: snapshot ? 'ready' : 'unavailable',
      snapshot,
      heightAt: (lng, lat) => sampleSharedSiteGround(snapshot, lng, lat),
      contains: (lng, lat) => parkTerrainContains(zone, lng, lat),
      revision: snapshot?.signature ?? 'park-terrain-needs-review',
      failureReason: snapshot
        ? null
        : 'Park moved or resized. Review its ground again.',
    };
  }, [shared, zone, automatic]);
}
