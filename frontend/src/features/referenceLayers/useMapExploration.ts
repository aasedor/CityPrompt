import { useEffect, useMemo, useState } from 'react';

type Centre = { lng: number; lat: number };
const EMPTY: number[][] = [];

/** A small neighbourhood query, never a fake authored site boundary. */
export function explorationArea(centre: Centre): number[][] {
  if (!Number.isFinite(centre.lng) || !Number.isFinite(centre.lat)
    || Math.abs(centre.lng) > 180 || Math.abs(centre.lat) > 85) return EMPTY;
  const lng = Math.round(centre.lng * 500) / 500;
  const lat = Math.round(centre.lat * 500) / 500;
  const dy = 500 / 111320, dx = dy / Math.cos(lat * Math.PI / 180);
  return [[lng-dx,lat-dy],[lng+dx,lat-dy],[lng+dx,lat+dy],[lng-dx,lat+dy]];
}

export function useMapExploration(projectId: string | undefined, readCentre: (() => Centre) | undefined,
  longitude = -114.0719, latitude = 51.0447, enabled = true) {
  const fallback = useMemo(() => explorationArea({ lng: longitude, lat: latitude }), [longitude, latitude]);
  const key = `${projectId}:${longitude}:${latitude}`;
  const [area, setArea] = useState<{ key: string; ring: number[][] } | null>(null);
  useEffect(() => {
    if (!enabled || !readCentre) return;
    let previous = '';
    // Sample after movement settles, not every frame or during each pointer event.
    const timer = window.setInterval(() => {
      const ring = explorationArea(readCentre());
      const signature = JSON.stringify(ring);
      if (signature === previous && ring.length) setArea(current =>
        current?.key === key && JSON.stringify(current.ring) === signature ? current : { key, ring });
      previous = signature;
    }, 750);
    return () => window.clearInterval(timer);
  }, [enabled, key, readCentre]);
  return area?.key === key ? area.ring : fallback;
}
