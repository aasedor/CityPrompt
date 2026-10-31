import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { Download, FileText, RefreshCw } from 'lucide-react';
import type { ParkAccessSnapshot } from '@/components/viewer/globe/parkAccessConnections';
import { useAuthStore } from '@/store';
import {
  reportError, safeSourceUrl, studentReportsApi,
  type ReportSummary, type StudentReport,
} from './studentReportsApi';

interface Props {
  projectId: string;
  zoneIds?: string[];
  planChangeToken?: unknown;
  canEdit?: boolean;
  onSelectZone?: (zoneId: string) => void;
  getParkAccessSnapshot?: () => ParkAccessSnapshot | undefined;
  getPolicyMapEvidence?: () => Promise<import('./policyMapEvidence').PolicyMapEvidence>;
}

const primaryMetrics = ['building_count', 'gfa_m2', 'gfa_ft2', 'residential_units', 'retail_units', 'site_area_m2',
  'park_count', 'park_area_m2', 'street_count', 'street_area_m2', 'ground_surface_count', 'ground_surface_area_m2',
  'detail_benches', 'detail_trees', 'detail_props', 'detail_surfaces'];
const legacyUnitBreakdown = new Set(['recorded_units', 'catalogue_dwellings', 'compiled_detached_dwellings']);
const quantityStatus = (metric: StudentReport['analysis']['metrics'][number]) => metric.value == null
  ? 'Unknown' : metric.key === 'retail_units' ? 'Recorded' : metric.confidence < 1 ? 'Estimate' : 'Calculated';

export function StudentPlanningReport(props: Props) {
  // A project switch must immediately discard the previous project's visible
  // report and busy flags, even before a new request completes.
  const account = useAuthStore(state => state.user?.id ?? 'anonymous');
  return <ProjectPlanningReport key={`${account}:${props.projectId}`} {...props} />;
}

function ProjectPlanningReport({ projectId, zoneIds, planChangeToken, canEdit = true, getParkAccessSnapshot, getPolicyMapEvidence }: Props) {
  const [report, setReport] = useState<StudentReport | null>(null);
  const [history, setHistory] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const selectedId = useRef<string | null>(null);
  const hasQuantitativeTotals = report?.analysis.metrics.some(metric => metric.key === 'building_count');
  const allMetrics = report?.analysis.metrics.filter(metric => !hasQuantitativeTotals || !legacyUnitBreakdown.has(metric.key)).slice().sort((a, b) => {
    const aIndex = primaryMetrics.indexOf(a.key), bIndex = primaryMetrics.indexOf(b.key);
    return (aIndex < 0 ? primaryMetrics.length : aIndex) - (bIndex < 0 ? primaryMetrics.length : bIndex);
  }) ?? [];
  const metrics = hasQuantitativeTotals ? allMetrics.filter(metric => primaryMetrics.includes(metric.key)) : allMetrics;
  const requestSequence = useRef(0);
  const lifecycle = useRef(0);
  useLayoutEffect(() => {
    lifecycle.current += 1;
    return () => {
      lifecycle.current += 1;
      requestSequence.current += 1;
    };
  }, []);
  const refresh = useCallback(async (id?: string) => {
    const lifetime = lifecycle.current;
    const sequence = ++requestSequence.current;
    const isCurrent = () => lifetime === lifecycle.current && sequence === requestSequence.current;
    setLoading(true);
    setError(null);
    try {
      const [next, versions] = await Promise.all([
        id ? studentReportsApi.get(id) : studentReportsApi.latest(projectId), studentReportsApi.history(projectId),
      ]);
      if (!isCurrent()) return;
      selectedId.current = next?.id ?? null;
      setReport(next);
      setHistory(versions);
    } catch (err) {
      if (isCurrent()) setError(reportError(err));
    } finally { if (isCurrent()) setLoading(false); }
  }, [projectId]);
  useEffect(() => {
    selectedId.current = null;
    setReport(null);
    setHistory([]);
    void refresh();
    return () => { requestSequence.current += 1; };
  }, [refresh]);
  useEffect(() => {
    if (selectedId.current) void refresh(selectedId.current);
  }, [planChangeToken, refresh]);

  const create = async () => {
    const lifetime = lifecycle.current;
    setWorking(true);
    setError(null);
    const sequence = ++requestSequence.current;
    try {
      const mapEvidence = getPolicyMapEvidence ? await getPolicyMapEvidence() : undefined;
      if (lifetime !== lifecycle.current || sequence !== requestSequence.current) return;
      const next = await (mapEvidence
        ? studentReportsApi.create(projectId, zoneIds, getParkAccessSnapshot?.(), mapEvidence)
        : studentReportsApi.create(projectId, zoneIds, getParkAccessSnapshot?.()));
      if (lifetime !== lifecycle.current || sequence !== requestSequence.current) return;
      selectedId.current = next.id;
      setReport(next);
      setHistory((previous) => [next, ...previous]);
    } catch (err) {
      if (lifetime === lifecycle.current && sequence === requestSequence.current) setError(reportError(err));
    } finally {
      if (lifetime === lifecycle.current) {
        setWorking(false);
        if (sequence === requestSequence.current) setLoading(false);
      }
    }
  };
  const download = async () => {
    if (!report) return;
    const lifetime = lifecycle.current;
    const reportId = report.id;
    setWorking(true);
    setError(null);
    try {
      const blob = await studentReportsApi.export(reportId);
      if (lifetime !== lifecycle.current || selectedId.current !== reportId) return;
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `planning-report-${reportId}.html`;
      anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) { if (lifetime === lifecycle.current) setError(reportError(err)); }
    finally { if (lifetime === lifecycle.current) setWorking(false); }
  };
  return <section aria-label="Planning report" className="h-full overflow-y-auto bg-slate-50 p-4 sm:p-6">
    <div className="mx-auto max-w-4xl space-y-5">
      <header className="rounded-xl border border-teal-100 bg-white p-5">
        <div className="flex items-center gap-2 text-teal-800"><FileText size={22} /><h2 className="text-xl font-semibold">Planning report</h2></div>
        <p className="mt-2 text-sm text-slate-600">Buildings, floor area, residential and retail units, and public-realm totals for your saved proposal.</p>
        <p className="mt-2 text-xs text-slate-500">Calculated quantities, concept estimates and unknown values are identified with their measurement source. Preparing a report uses saved data without an AI generation charge.</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {canEdit && <button onClick={() => void create()} disabled={working || loading} className="min-h-11 rounded-lg bg-teal-800 px-4 py-2 text-sm font-medium text-white hover:bg-teal-900 disabled:opacity-50">{working ? 'Preparing…' : report ? 'Request a new report' : 'Request report'}</button>}
          {report && <button onClick={() => void download()} disabled={working} className="flex min-h-11 items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:opacity-50"><Download size={16} />Download printable report</button>}
          <button onClick={() => void refresh(selectedId.current ?? undefined)} disabled={loading || working} className="flex min-h-11 items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:opacity-50"><RefreshCw size={16} />Refresh</button>
        </div>
        {report && <p className="mt-2 text-xs text-slate-500">Open the downloaded HTML and choose Print → Save as PDF. Earlier saved responses are retained in the archive.</p>}
      </header>
      {error && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</p>}
      {loading && <p role="status" className="text-sm text-slate-500">Checking saved report…</p>}
      {!report && !loading && !error && <p className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">Your first report will capture the current saved proposal and its quantities.</p>}
      {report && <>
        {history.length > 1 && <label className="block text-sm text-slate-700">Saved reports
          <select aria-label="Saved reports" value={report.id} disabled={working} onChange={(event) => void refresh(event.target.value)} className="mt-1 min-h-11 w-full rounded-lg border border-slate-300 bg-white p-2">
            {history.map((version) => <option key={version.id} value={version.id}>{new Date(version.created_at).toLocaleString()} · {version.plan_version.slice(0, 8)} · {version.requested_by_name}</option>)}
          </select>
        </label>}
        {report.is_stale && <div role="status" className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"><strong>The proposal has changed.</strong> These quantities describe the earlier saved plan. Request a new report to measure the current design; earlier reports stay in history.</div>}
        {report.analysis.method_version === 'student-review-v1' && <p role="status" className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">This saved report predates the separation of placement plots from building footprints. Its building and floor-area quantities may include yards or paving. Request a new report for corrected quantities; this version and your responses stay in history.</p>}
        {!hasQuantitativeTotals && <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">This earlier report includes the quantities available when it was saved. Request a new report for building, unit and detail totals.</p>}
        <div className="text-xs text-slate-500">Plan {report.plan_version.slice(0, 12)} · {report.analysis.scope_zone_count} proposal areas · {new Date(report.created_at).toLocaleString()} · requested by {report.requested_by_name}</div>
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="mb-3 font-semibold text-slate-900">Proposal quantities</h3>
          <table className="w-full text-left text-sm"><thead className="text-xs text-slate-500"><tr><th className="pb-2">Measure</th><th className="pb-2">Value</th><th className="pb-2">Status</th></tr></thead>
            <tbody>{metrics.map((metric) => <tr key={metric.key} className="border-t border-slate-100"><th scope="row" className="py-2 pr-3 font-medium">{metric.label}</th><td className="whitespace-nowrap py-2 pr-4">{metric.value == null ? 'Unknown' : metric.value.toLocaleString(undefined, { maximumFractionDigits: 2 })} {metric.unit}</td><td className="py-2 text-xs text-slate-500">{quantityStatus(metric)}</td></tr>)}</tbody>
          </table>
        </div>
        <details className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
          <summary className="cursor-pointer font-medium">How totals are calculated</summary>
          <dl className="mt-3 space-y-3">{allMetrics.map(metric => <div key={metric.key}><dt className="font-semibold">{metric.label}{!primaryMetrics.includes(metric.key) && ` · ${metric.value == null ? 'Unknown' : metric.value.toLocaleString(undefined, {maximumFractionDigits: 2})} ${metric.unit}`}</dt><dd className="mt-1 text-xs">{metric.derivation}</dd></div>)}</dl>
        </details>
        <details className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600"><summary className="cursor-pointer font-medium">Scope and limitations</summary><ul className="mt-2 list-disc space-y-2 pl-5">{report.analysis.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></details>
        <details className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
          <summary className="cursor-pointer font-medium">Sources</summary>
          <ul className="mt-2 space-y-2">{[...new Map(report.analysis.findings.flatMap(finding => finding.sources).map(source => [`${source.title}:${source.url ?? ''}:${source.page ?? ''}`, source])).values()].map((source, index) => <li key={index}>
            {safeSourceUrl(source.url) ? <a className="text-teal-800 underline" href={safeSourceUrl(source.url)} target="_blank" rel="noopener noreferrer">{source.title}</a> : <strong>{source.title}</strong>}
            {source.page != null && <span> · p. {source.page}</span>}
            {source.excerpt && <p className="mt-1 whitespace-pre-wrap text-xs">{source.excerpt}</p>}
          </li>)}</ul>
          {!report.analysis.findings.some(finding => finding.sources.length) && <p className="mt-2">Saved proposal geometry and recorded object properties. No external source attached.</p>}
        </details>
        {Object.keys(report.decisions).length > 0 && <details className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
          <summary className="cursor-pointer font-medium">Earlier saved responses</summary>
          {Object.entries(report.decisions).map(([id, decision]) => <article key={id} className="mt-3 border-t pt-3">
            <p className="text-xs">{decision.author_name} · {new Date(decision.updated_at).toLocaleString()} · {decision.choice}</p>
            <p className="mt-1 whitespace-pre-wrap">{decision.rationale}</p>
            {decision.follow_through && <p className="mt-1 whitespace-pre-wrap">{decision.follow_through}</p>}
          </article>)}
        </details>}
      </>}
    </div>
  </section>;
}
