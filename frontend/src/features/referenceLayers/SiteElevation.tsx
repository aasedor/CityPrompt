import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

interface ElevationData {
  elevation: number;
  ellipsoidal_height: number;
  resolution: number;
  status: 'available' | 'unavailable';
  source: 'google_elevation' | 'renderer_fallback';
  approximate: boolean;
  vertical_reference: 'mean_sea_level';
  unavailable_reason?: string | null;
}

/** Mount inside the open Layers panel. A single cached point is optional context. */
export function SiteElevation({ lat, lon }: { lat?: number | null; lon?: number | null }) {
  const hasLocation = typeof lat === 'number' && Number.isFinite(lat) && Math.abs(lat) <= 90
    && typeof lon === 'number' && Number.isFinite(lon) && Math.abs(lon) <= 180;
  const query = useQuery({
    queryKey: ['site-elevation-context', lat, lon],
    queryFn: async ({ signal }) => (await api.get<ElevationData>('/api/v1/elevation', {
      params: { lat, lng: lon }, signal,
    })).data,
    enabled: hasLocation,
    staleTime: 30 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });
  const data = query.data;
  // Missing metadata from an older API is also unavailable. A numeric fallback
  // is useful to a renderer but cannot be evidence about a real site's height.
  const available = data?.status === 'available' && data.source === 'google_elevation'
    && data.vertical_reference === 'mean_sea_level' && Number.isFinite(data.elevation);
  return <section aria-label="Site elevation" onKeyDown={(event) => event.stopPropagation()} className="w-80 max-w-full rounded-xl border border-slate-300 bg-white p-3 text-slate-900">
    <h2 className="text-sm font-bold">Site elevation</h2>
    {!hasLocation ? <p className="mt-2 text-sm text-slate-600">Add a project location to see an elevation estimate.</p>
      : query.isLoading ? <p role="status" className="mt-2 text-sm text-slate-600">Checking elevation…</p>
        : available && data ? <>
          <p className="mt-2 text-base font-semibold">Approx. {data.elevation.toLocaleString(undefined, { maximumFractionDigits: 0 })} m above sea level</p>
          <p className="mt-1 text-sm text-slate-600">At the project location. Terrain may vary across your site.</p>
          <details className="mt-1 text-sm text-slate-600">
            <summary className="min-h-11 cursor-pointer rounded py-3 font-semibold text-slate-800 focus-visible:outline focus-visible:outline-2">About this estimate</summary>
            <p>Source: Google Elevation. Map data estimate, not a site survey.</p>
            <p className="mt-2">{Number.isFinite(data.resolution) && data.resolution > 0
              ? 'Data resolution: about ' + data.resolution.toLocaleString(undefined, { maximumFractionDigits: 0 }) + ' m. This describes the spacing of the source data, not survey accuracy.'
              : 'The source did not provide a data resolution.'}</p>
            <p className="mt-2">Location: {lat?.toFixed(5)}, {lon?.toFixed(5)}</p>
          </details>
        </> : <>
          <p role="status" className="mt-2 text-sm font-semibold">Elevation unavailable</p>
          <p className="mt-1 text-sm text-slate-600">A reliable elevation estimate could not be obtained for this location. You can keep designing.</p>
          <button type="button" onClick={() => void query.refetch()} disabled={query.isFetching}
            className="mt-2 min-h-11 rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 disabled:opacity-50">{query.isFetching ? 'Checking…' : 'Try again'}</button>
        </>}
  </section>;
}
