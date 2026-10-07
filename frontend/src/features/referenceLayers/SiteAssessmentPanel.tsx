import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Calculator, ExternalLink } from 'lucide-react';
import { api, getApiErrorMessage } from '@/services/api';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { zoningBounds, zoningCoverageProblem } from './zoningLabels';

export interface SiteAssessment {
  boundary_id: string; roll_year: number | null; property_count: number;
  partial_property_count: number; missing_value_count: number; complete: boolean;
  full_property_assessed_total: number; area_weighted_estimate: number;
  assessed_coverage_pct: number; details_omitted: number;
  warnings: string[]; source_url: string; fetched_at: string;
  records: { roll_number: string; address: string; property_type: string | null;
    assessed_value: number | null; overlap_pct: number; partial: boolean }[];
}

const dollars = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD', maximumFractionDigits: 0 });

export function SiteAssessmentPanel({ zones, projectId }: { zones: SiteZone[]; projectId: string | undefined }) {
  const boundary = getActiveSiteBoundary(zones);
  const problem = zoningCoverageProblem(zoningBounds(boundary?.coordinates ?? []));
  const signature = JSON.stringify([projectId, boundary?.id, boundary?.coordinates]);
  const [requested, setRequested] = useState<string | null>(null);
  const query = useQuery({
    queryKey: ['site-assessment-v1', signature],
    queryFn: async ({ signal }) => {
      const response = await api.post<SiteAssessment>(`/api/v1/site-assessments/zones/${boundary!.id}`,
        { coordinates: boundary!.coordinates.map(([x, y]) => [x, y]) }, { signal, timeout: 60_000 });
      return response.data;
    },
    enabled: Boolean(projectId && boundary && !problem && requested === signature),
    staleTime: 15 * 60_000, gcTime: 30 * 60_000, retry: false,
  });
  // A previous site's total must disappear immediately after an edit or switch.
  const data = !problem ? query.data : undefined;
  const calculate = () => {
    setRequested(signature);
    if (data || requested === signature) void query.refetch();
  };
  return <section aria-label="Site assessment" className="max-w-sm space-y-3 rounded-2xl border border-[#151515]/20 bg-[#fffdf6]/95 p-3 text-[#151515] shadow-lg">
    <header className="flex items-center gap-2"><Calculator size={17} aria-hidden="true" /><h3 className="text-sm font-bold">Site assessment</h3></header>
    <p className="text-xs leading-relaxed text-[#5c554d]">Look up Calgary’s published property assessments within your boundary.</p>
    <button type="button" onClick={calculate} disabled={Boolean(problem) || query.isFetching}
      className="min-h-11 w-full rounded-xl bg-[#151515] px-3 py-2 text-xs font-semibold text-[#fff9ec] hover:bg-[#323b2c] disabled:opacity-50">
      {query.isFetching ? 'Calculating assessments…' : data ? 'Refresh assessments' : 'Calculate assessed value'}
    </button>
    {problem && <p className="text-xs text-[#5c554d]">{problem.replace('zoning', 'assessment data')}</p>}
    {requested === signature && query.error && <p role="alert" className="rounded-xl bg-amber-50 p-2 text-xs text-amber-950">{getApiErrorMessage(query.error, 'Calgary assessments could not load. Please retry.')}</p>}
    {data && (data.property_count === 0 ? <p role="status" className="text-xs">No assessed properties were published for this boundary.{data.warnings.map(warning => ` ${warning}`)}</p> : <>
      <div role="status">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-[#5c554d]">{data.roll_year} · {data.property_count} assessed properties</p>
        <p className="mt-1 text-2xl font-bold tabular-nums">{dollars.format(data.full_property_assessed_total)}</p>
        <p className="text-xs text-[#5c554d]">{data.complete ? 'Full assessed value of intersecting properties' : 'Known property assessments · incomplete subtotal'}</p>
      </div>
      {data.partial_property_count > 0 && <div className="rounded-xl border border-[#151515]/15 p-2 text-xs">
        <p className="font-semibold">Within-boundary area estimate: {dollars.format(data.area_weighted_estimate)}</p>
        <p className="mt-1 leading-relaxed text-[#5c554d]">Prorated by the share of each property’s mapped area inside the site. This is a concept estimate, not an official assessment of the partial site.</p>
      </div>}
      <p className="text-[11px] leading-relaxed text-[#5c554d]">Calgary’s values include improvements for land-and-improvement properties (LI). They describe existing properties and do not value your proposed design.</p>
      {data.warnings.length > 0 && <ul className="list-disc space-y-1 pl-4 text-[11px] leading-relaxed text-amber-950">{data.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul>}
      <details className="rounded-xl border border-[#151515]/15 bg-white/80 p-2 text-xs">
        <summary className="min-h-8 cursor-pointer font-semibold">Property breakdown · {data.assessed_coverage_pct}% mapped coverage</summary>
        <div className="mt-2 max-h-64 space-y-2 overflow-y-auto" tabIndex={0} aria-label="Assessed properties">
          {data.records.map(record => <div key={record.roll_number} className="border-t border-[#151515]/10 pt-2">
            <p className="font-semibold">{record.address}</p>
            <p className="text-[#5c554d]">Roll {record.roll_number} · {record.property_type || 'Type unspecified'} · {record.assessed_value === null ? 'Value unavailable' : dollars.format(record.assessed_value)}</p>
            <p className="text-[#5c554d]">{record.overlap_pct}% of mapped property inside site{record.partial ? ' · partial property' : ''}</p>
          </div>)}
          {data.details_omitted > 0 && <p>{data.details_omitted} additional properties are included in the total.</p>}
        </div>
      </details>
      <a href={data.source_url} target="_blank" rel="noreferrer" className="flex min-h-8 items-center gap-1 text-[10px] text-[#5c554d] underline underline-offset-2">Calgary assessment data · retrieved {data.fetched_at.slice(0, 10)}<ExternalLink size={11} aria-hidden="true" /></a>
    </>)}
  </section>;
}
