import { useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchZoningLabels, type Position, type ZoningOverlay } from './zoningLabels';
import { clipStudyZones, studyPreviewLayer, zonesFromCalgary } from './zoningStudy';
import type { StudyMapDrawing } from './useStudyMapDrawing';

/** Official source data is a reference, never a student-authored study slot. */
export function ExistingLandUse({ projectId, boundary, data, mapDrawing }: {
  projectId: string; boundary: Position[]; data?: ZoningOverlay; mapDrawing?: StudyMapDrawing;
}) {
  const query = useQuery({
    queryKey: ['existing-land-use-site', projectId, boundary, data?.loadedAt],
    queryFn: async ({signal}) => clipStudyZones(zonesFromCalgary(data ?? await fetchZoningLabels(boundary,
      AbortSignal.any([signal, AbortSignal.timeout(30_000)]))), boundary),
    staleTime: 15 * 60_000, retry: 1,
  });
  const preview = useMemo(() => query.data ? studyPreviewLayer(query.data, boundary, 'existing', 1) : null, [query.data, boundary]);
  useEffect(() => { mapDrawing?.cancel(); mapDrawing?.preview(preview); return () => mapDrawing?.preview(null); }, [mapDrawing, preview]);
  return <section aria-label="Existing land use" className="space-y-3 rounded-xl border border-stone-200 bg-white p-3 text-sm">
    <p>Existing land use · City of Calgary · read-only</p>
    <p className="text-xs text-stone-600">Current published land-use districts within your site. Choose Proposed land use to design a change.</p>
    {query.isFetching && <p role="status">Loading existing land use…</p>}
    {query.isError && <p role="status">Existing land use could not load. <button className="min-h-11 underline" onClick={() => void query.refetch()}>Try again</button></p>}
    {query.data && <ul aria-label="Existing site districts">{query.data.map(zone => <li className="py-2" key={zone.id}>
      <span aria-hidden className="mr-2 inline-block h-3 w-3 border" style={{backgroundColor: zone.color}}/>
      <strong>{zone.district?.designation ?? zone.label}</strong>{zone.district?.description && ` · ${zone.district.description}`}
    </li>)}</ul>}
    {query.data?.length === 0 && <p>No published districts were found inside this site.</p>}
    <a className="inline-block min-h-11 underline" href="https://maps.calgary.ca/myProperty/" target="_blank" rel="noreferrer">Check the City land-use map</a>
  </section>;
}
