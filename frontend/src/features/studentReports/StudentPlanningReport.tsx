import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { Download, FileText, RefreshCw } from 'lucide-react';

import {
  reportError, safeSourceUrl, studentReportsApi,
  type ReportSummary, type StudentChoice, type StudentDecision, type StudentFinding, type StudentReport,
} from './studentReportsApi';

interface Props {
  projectId: string;
  zoneIds?: string[];
  planChangeToken?: unknown;
  canEdit?: boolean;
  onSelectZone?: (zoneId: string) => void;
}

const kindLabels = {
  design_suggestion: 'Design suggestion', unresolved_question: 'Question to resolve', source_context: 'Source to consider',
};

function FindingCard({ finding, decision, canEdit, busy, onSave, onSelectZone }: {
  finding: StudentFinding;
  decision?: StudentDecision;
  canEdit: boolean;
  busy: boolean;
  onSave: (choice: StudentChoice, rationale: string, followThrough: string) => Promise<void>;
  onSelectZone?: (zoneId: string) => void;
}) {
  const [choice, setChoice] = useState<StudentChoice | ''>(decision?.choice ?? '');
  const [rationale, setRationale] = useState(decision?.rationale ?? '');
  const [followThrough, setFollowThrough] = useState(decision?.follow_through ?? '');
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const lifecycle = useRef(0);
  useLayoutEffect(() => {
    lifecycle.current += 1;
    return () => { lifecycle.current += 1; };
  }, []);
  const inputId = `report-${finding.id}`;
  const save = async () => {
    if (!choice || !rationale.trim()) {
      setError('Choose a response and explain your reasoning in your own words.');
      return;
    }
    setError(null);
    setSaved(false);
    const lifetime = lifecycle.current;
    try {
      await onSave(choice, rationale, followThrough);
      if (lifetime === lifecycle.current) setSaved(true);
    } catch (err) { if (lifetime === lifecycle.current) setError(reportError(err)); }
  };
  return <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <p className="text-xs font-medium uppercase tracking-wide text-teal-700">{kindLabels[finding.kind]}</p>
    <h3 className="mt-1 text-lg font-semibold text-slate-900">{finding.title}</h3>
    <p className="mt-1 text-xs text-slate-500">
      {onSelectZone && finding.location.zone_ids.length > 0
        ? <button className="underline hover:text-teal-700" onClick={() => onSelectZone(finding.location.zone_ids[0])}>{finding.location.label}</button>
        : finding.location.label}
    </p>
    <p className="mt-3 text-sm text-slate-700">{finding.observation}</p>
    <p className="mt-2 text-sm text-slate-800"><strong>Suggested next step:</strong> {finding.recommendation}</p>
    <details className="mt-3 text-sm text-slate-600">
      <summary className="cursor-pointer font-medium">Evidence and uncertainty</summary>
      <p className="mt-2">{finding.basis}</p>
      {finding.uncertainty && <p className="mt-2">{finding.uncertainty}</p>}
      {finding.sources.map((source, index) => <div className="mt-3 border-l-2 border-teal-200 pl-3" key={`${source.title}-${index}`}>
        {safeSourceUrl(source.url)
          ? <a className="font-medium text-teal-800 underline" href={safeSourceUrl(source.url)} target="_blank" rel="noopener noreferrer">{source.title}</a>
          : <strong>{source.title}</strong>}
        {source.page != null && <span> · p. {source.page}</span>}
        {source.excerpt && <blockquote className="mt-1 whitespace-pre-wrap text-xs">{source.excerpt}</blockquote>}
        {source.context_created_at && <p className="mt-1 text-xs">Site context captured {new Date(source.context_created_at).toLocaleDateString()}; verify current applicability.</p>}
      </div>)}
    </details>
    {decision && <p className="mt-3 text-xs text-slate-500">Saved response: {decision.choice} · {decision.author_name} · {new Date(decision.updated_at).toLocaleString()}</p>}
    {canEdit ? <div className="mt-4 border-t border-slate-100 pt-4">
      <label className="block text-sm font-medium text-slate-800" htmlFor={`${inputId}-choice`}>Your response</label>
      <select id={`${inputId}-choice`} className="mt-1 min-h-11 w-full rounded-lg border border-slate-300 bg-white p-2 text-sm"
        value={choice} onChange={(event) => { setChoice(event.target.value as StudentChoice | ''); setSaved(false); }}>
        <option value="">Choose how to respond</option>
        <option value="implement">Implement the suggestion</option>
        <option value="adapt">Adapt it to our vision</option>
        <option value="decline">Decline and explain why</option>
      </select>
      <label className="mt-3 block text-sm font-medium text-slate-800" htmlFor={`${inputId}-rationale`}>Your reasoning</label>
      <textarea id={`${inputId}-rationale`} className="mt-1 min-h-24 w-full rounded-lg border border-slate-300 p-2 text-sm"
        maxLength={6000} value={rationale} placeholder="Explain the evidence, priorities, or tradeoffs behind your choice."
        onChange={(event) => { setRationale(event.target.value); setSaved(false); }} />
      <label className="mt-3 block text-sm font-medium text-slate-800" htmlFor={`${inputId}-follow`}>Follow-through <span className="font-normal text-slate-500">(optional)</span></label>
      <textarea id={`${inputId}-follow`} className="mt-1 min-h-16 w-full rounded-lg border border-slate-300 p-2 text-sm"
        maxLength={6000} value={followThrough} placeholder="What changed in the design, or what still needs investigation?"
        onChange={(event) => { setFollowThrough(event.target.value); setSaved(false); }} />
      <div className="mt-3 flex items-center gap-3">
        <button disabled={busy} onClick={() => void save()} className="min-h-11 rounded-lg bg-teal-800 px-4 py-2 text-sm font-medium text-white hover:bg-teal-900 disabled:opacity-50">Save response</button>
        {saved && <span role="status" className="text-sm text-teal-700">Response saved</span>}
      </div>
      {error && <p role="alert" className="mt-2 text-sm text-red-700">{error}</p>}
    </div> : decision && <div className="mt-3 text-sm text-slate-700">
      <p className="whitespace-pre-wrap">{decision.rationale}</p>
      {decision.follow_through && <p className="mt-2 whitespace-pre-wrap">Follow-through: {decision.follow_through}</p>}
    </div>}
  </article>;
}

export function StudentPlanningReport(props: Props) {
  // A project switch must immediately discard the previous project's visible
  // report, drafts, and busy flags, even before a new request completes.
  return <ProjectPlanningReport key={props.projectId} {...props} />;
}

function ProjectPlanningReport({ projectId, zoneIds, planChangeToken, canEdit = true, onSelectZone }: Props) {
  const [report, setReport] = useState<StudentReport | null>(null);
  const [history, setHistory] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const selectedId = useRef<string | null>(null);
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
      const next = await studentReportsApi.create(projectId, zoneIds);
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
  const save = async (findingId: string, choice: StudentChoice, rationale: string, followThrough: string) => {
    if (!report) return;
    const lifetime = lifecycle.current;
    const sequence = ++requestSequence.current;
    setSaving(true);
    try {
      const next = await studentReportsApi.respond(report.id, findingId, {
        choice, rationale, follow_through: followThrough, expected_revision: report.response_revision,
      });
      if (lifetime === lifecycle.current && sequence === requestSequence.current) setReport(next);
    } catch (err) {
      if (lifetime === lifecycle.current) throw err;
    } finally {
      if (lifetime === lifecycle.current) {
        setSaving(false);
        if (sequence === requestSequence.current) setLoading(false);
      }
    }
  };

  return <section aria-label="Planning report" className="h-full overflow-y-auto bg-slate-50 p-4 sm:p-6">
    <div className="mx-auto max-w-4xl space-y-5">
      <header className="rounded-xl border border-teal-100 bg-white p-5">
        <div className="flex items-center gap-2 text-teal-800"><FileText size={22} /><h2 className="text-xl font-semibold">Planning report</h2></div>
        <p className="mt-2 text-sm text-slate-600">Explore the strengths, questions, and next steps in your proposal. Explain which suggestions you implement, adapt, or decline.</p>
        <p className="mt-2 text-xs text-slate-500">Requested when you are ready. You can keep designing and rendering with any recommendation unresolved. This review uses saved geometry and available documents without an AI generation charge.</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {canEdit && <button onClick={() => void create()} disabled={working || saving || loading} className="min-h-11 rounded-lg bg-teal-800 px-4 py-2 text-sm font-medium text-white hover:bg-teal-900 disabled:opacity-50">{working ? 'Preparing…' : report ? 'Request a new report' : 'Request report'}</button>}
          {report && <button onClick={() => void download()} disabled={working || saving} className="flex min-h-11 items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:opacity-50"><Download size={16} />Download printable report</button>}
          <button onClick={() => void refresh(selectedId.current ?? undefined)} disabled={loading || working || saving} className="flex min-h-11 items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:opacity-50"><RefreshCw size={16} />Refresh</button>
        </div>
        {report && <p className="mt-2 text-xs text-slate-500">Open the downloaded HTML and choose Print → Save as PDF for submission. Saved responses and their authors are included.</p>}
      </header>
      {error && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</p>}
      {loading && <p role="status" className="text-sm text-slate-500">Checking saved report…</p>}
      {!report && !loading && !error && <p className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">Your first report will capture the current saved proposal. Your reasoning stays attached to that version.</p>}
      {report && <>
        {history.length > 1 && <label className="block text-sm text-slate-700">Saved reports
          <select aria-label="Saved reports" value={report.id} disabled={saving || working} onChange={(event) => void refresh(event.target.value)} className="mt-1 min-h-11 w-full rounded-lg border border-slate-300 bg-white p-2">
            {history.map((version) => <option key={version.id} value={version.id}>{new Date(version.created_at).toLocaleString()} · {version.plan_version.slice(0, 8)} · {version.requested_by_name}</option>)}
          </select>
        </label>}
        {report.is_stale && <div role="status" className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"><strong>The proposal has changed.</strong> This report and its responses describe the earlier saved plan. Request a new report to review the current design; your earlier reasoning stays in the report history.</div>}
        <div className="text-xs text-slate-500">Plan {report.plan_version.slice(0, 12)} · {report.analysis.scope_zone_count} proposal areas · {new Date(report.created_at).toLocaleString()} · requested by {report.requested_by_name}</div>
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="mb-3 font-semibold text-slate-900">Proposal quantities</h3>
          <table className="w-full text-left text-sm"><thead className="text-xs text-slate-500"><tr><th className="pb-2">Measure</th><th className="pb-2">Value</th><th className="pb-2">How it was measured</th></tr></thead>
            <tbody>{report.analysis.metrics.map((metric) => <tr key={metric.key} className="border-t border-slate-100"><th className="py-3 pr-3 font-medium">{metric.label}</th><td className="whitespace-nowrap py-3 pr-4">{metric.value == null ? 'Unknown' : metric.value.toLocaleString(undefined, { maximumFractionDigits: 2 })} {metric.unit}</td><td className="py-3 text-xs text-slate-500">{metric.derivation}</td></tr>)}</tbody>
          </table>
        </div>
        <details className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600"><summary className="cursor-pointer font-medium">Scope and limitations</summary><ul className="mt-2 list-disc space-y-2 pl-5">{report.analysis.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></details>
        <p className="text-xs text-slate-500">Recording “implement” saves your intention. It does not change geometry or verify that a design change has been made.</p>
        {report.analysis.findings.map((finding) => <FindingCard key={`${report.id}-${finding.id}`} finding={finding} decision={report.decisions[finding.id]} canEdit={canEdit} busy={saving || working || loading} onSave={(choice, rationale, followThrough) => save(finding.id, choice, rationale, followThrough)} onSelectZone={onSelectZone} />)}
      </>}
    </div>
  </section>;
}
