/**
 * Site Intelligence — Urban DNA report + planning-agent scenarios.
 *
 * Rendered for site_boundary zones. Backend does all the work
 * (/api/v1/urban-dna); this panel shows per-section confidence, warnings and
 * missing datasets honestly, and lets the user run/apply planning scenarios.
 * Applying a scenario writes non-destructive planning directives onto the
 * boundary zone (properties._urban_dna_directives) that the layout prompts read.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Brain, ChevronDown, ChevronRight, Loader2, Play, RefreshCw, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import type {
  SiteZone,
  UrbanDnaScenarioRow,
  UrbanDnaSection,
  UrbanDnaSectionName,
  UrbanDnaSnapshotResponse,
  UrbanDnaValidationNote,
} from '@/types';
import { URBAN_DNA_SECTION_NAMES } from '@/types';
import { getApiErrorMessage, urbanDnaApi } from '@/services/api';

const SECTION_LABELS: Record<UrbanDnaSectionName, string> = {
  site: 'Site',
  land_use: 'Land Use',
  mobility: 'Mobility',
  public_realm: 'Public Realm',
  environment: 'Environment',
  built_form: 'Built Form',
  market: 'Market',
  policy: 'Policy',
};

const POLL_MS = 5000;

function confidenceColor(confidence: number): string {
  if (confidence >= 0.75) return 'bg-[#c9ff3d]';
  if (confidence >= 0.4) return 'bg-amber-300';
  return 'bg-red-300';
}

function ConfidenceBadge({ value }: { value: number }) {
  return (
    <span
      className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-black text-[#151515] ${confidenceColor(value)}`}
      title={`Confidence ${(value * 100).toFixed(0)}%`}
    >
      {(value * 100).toFixed(0)}%
    </span>
  );
}

function shortValue(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'number') return Number.isInteger(value) ? String(value) : value.toFixed(2);
  if (typeof value === 'string') return value.length > 90 ? `${value.slice(0, 90)}…` : value;
  if (typeof value === 'boolean') return value ? 'yes' : 'no';
  if (Array.isArray(value)) return `${value.length} item${value.length === 1 ? '' : 's'}`;
  if (typeof value === 'object') {
    const json = JSON.stringify(value);
    return json.length > 90 ? `${json.slice(0, 90)}…` : json;
  }
  return String(value);
}

function WarningList({ warnings }: { warnings: UrbanDnaValidationNote[] }) {
  if (!warnings.length) return null;
  return (
    <ul className="mt-1 space-y-0.5">
      {warnings.map((warning, index) => (
        <li
          key={`${warning.code}-${index}`}
          className={`text-[10px] leading-snug ${warning.severity === 'info' ? 'text-[#151515]/50' : 'text-amber-700'}`}
        >
          ⚠ {warning.message}
        </li>
      ))}
    </ul>
  );
}

function DnaSectionRow({ name, section }: { name: UrbanDnaSectionName; section: UrbanDnaSection }) {
  const [open, setOpen] = useState(false);
  const fieldEntries = Object.entries(section.fields || {});
  const filled = fieldEntries.filter(([, field]) => field.value !== null && field.value !== undefined);

  return (
    <div className="rounded-lg border-2 border-[#151515] bg-white shadow-[2px_2px_0_0_rgba(21,21,21,0.2)]">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-2.5 py-1.5"
      >
        <span className="flex items-center gap-1.5 text-xs font-black uppercase text-[#151515]">
          {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          {SECTION_LABELS[name]}
          <span className="font-semibold normal-case text-[#151515]/50">
            {filled.length}/{fieldEntries.length || 0}
          </span>
        </span>
        <ConfidenceBadge value={section.meta?.confidence ?? 0} />
      </button>
      {open && (
        <div className="border-t-2 border-[#151515]/20 px-2.5 py-1.5">
          {fieldEntries.length === 0 && (
            <p className="text-[10px] text-[#151515]/50">No datasets registered for this section yet.</p>
          )}
          {fieldEntries.map(([fieldName, field]) => (
            <div key={fieldName} className="flex items-start justify-between gap-2 py-0.5">
              <span className="text-[10px] font-bold text-[#151515]/70">{fieldName.replace(/_/g, ' ')}</span>
              <span className="max-w-[60%] text-right text-[10px] font-semibold text-[#151515]" title={JSON.stringify(field.value)}>
                {shortValue(field.value)}
              </span>
            </div>
          ))}
          {section.meta?.missing_datasets?.length > 0 && (
            <p className="mt-1 text-[10px] text-red-700">
              Missing: {section.meta.missing_datasets.join(', ')}
            </p>
          )}
          <WarningList warnings={section.meta?.warnings || []} />
        </div>
      )}
    </div>
  );
}

function PolicyInsightBlock({ section }: { section: UrbanDnaSection }) {
  const insight = section.fields?.insight?.value as
    | {
        summaries?: string[];
        conformance_considerations?: Array<{
          topic: string; framing: string; risk: string; detail: string;
          citations?: Array<{ doc: string; page: number; verified?: boolean }>;
        }>;
        opportunities?: Array<{
          topic: string; detail: string;
          citations?: Array<{ doc: string; page: number; verified?: boolean }>;
        }>;
        disclaimer?: string;
      }
    | undefined;
  if (!insight) return null;

  const renderCitations = (citations?: Array<{ doc: string; page: number }>) =>
    citations && citations.length > 0 ? (
      <span className="ml-1 text-[9px] font-bold text-[#151515]/50">
        [{citations.map((c) => `${c.doc} p${c.page}`).join('; ')}]
      </span>
    ) : null;

  return (
    <div className="rounded-lg border-2 border-[#151515] bg-[#fff9ec] p-2.5 shadow-[2px_2px_0_0_rgba(21,21,21,0.2)]">
      <p className="text-[10px] font-black uppercase text-[#151515]/60">Policy Insight</p>
      {(insight.summaries || []).map((summary, index) => (
        <p key={index} className="mt-1 text-[11px] leading-snug text-[#151515]">{summary}</p>
      ))}
      {(insight.conformance_considerations || []).map((consideration, index) => (
        <p key={`c-${index}`} className="mt-1 text-[10px] leading-snug text-[#151515]/80">
          <span className="font-black uppercase">{consideration.risk} · {consideration.topic}:</span>{' '}
          {consideration.detail}
          {renderCitations(consideration.citations)}
        </p>
      ))}
      {(insight.opportunities || []).map((opportunity, index) => (
        <p key={`o-${index}`} className="mt-1 text-[10px] leading-snug text-emerald-800">
          <span className="font-black uppercase">Opportunity · {opportunity.topic}:</span>{' '}
          {opportunity.detail}
          {renderCitations(opportunity.citations)}
        </p>
      ))}
      {insight.disclaimer && (
        <p className="mt-1.5 text-[9px] italic text-[#151515]/50">{insight.disclaimer}</p>
      )}
    </div>
  );
}

function ScenarioCard({
  scenario,
  onApply,
  applying,
  onDrawPlan,
  drawing,
}: {
  scenario: UrbanDnaScenarioRow;
  onApply: (row: UrbanDnaScenarioRow) => void;
  applying: boolean;
  onDrawPlan: (row: UrbanDnaScenarioRow) => void;
  drawing: boolean;
}) {
  const [open, setOpen] = useState(false);
  const payload = scenario.payload;
  const parameterCount = Object.keys(payload?.plan_parameters || {}).length;
  const plan = (payload as any)?.plan as
    | { status?: string; block_count?: number; parcel_count?: number; zone_count?: number;
        intersection_density_per_km2?: number; error?: string | null }
    | undefined;
  const planBusy = plan?.status === 'queued' || plan?.status === 'drawing';

  return (
    <div className="rounded-lg border-2 border-[#151515] bg-white shadow-[2px_2px_0_0_rgba(21,21,21,0.2)]">
      <div className="flex items-center justify-between px-2.5 py-1.5">
        <button type="button" onClick={() => setOpen((v) => !v)} className="flex items-center gap-1.5">
          {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          <span className="text-xs font-black text-[#151515]">{scenario.label}</span>
        </button>
        <div className="flex items-center gap-1.5">
          {scenario.status === 'complete' ? (
            <span className="rounded bg-[#c9ff3d] px-1.5 py-0.5 text-[9px] font-black text-[#151515]">
              {parameterCount} params
            </span>
          ) : scenario.status === 'failed' ? (
            <span className="rounded bg-red-300 px-1.5 py-0.5 text-[9px] font-black text-[#151515]">failed</span>
          ) : (
            <span className="flex items-center gap-1 text-[9px] font-black text-[#151515]/60">
              <Loader2 className="h-3 w-3 animate-spin" /> {scenario.status}
            </span>
          )}
          {scenario.status === 'complete' && (
            <>
              <button
                type="button"
                disabled={drawing || planBusy}
                onClick={() => onDrawPlan(scenario)}
                title="Draw this scenario as a plan layer: streets, blocks, park and building masses"
                className="rounded border-2 border-[#151515] bg-[#b78aff] px-1.5 py-0.5 text-[9px] font-black uppercase text-[#151515] hover:bg-[#c9a2ff] disabled:opacity-50"
              >
                {planBusy ? <Loader2 className="inline h-3 w-3 animate-spin" /> : plan?.status === 'complete' ? 'Redraw' : 'Draw Plan'}
              </button>
              {plan?.status === 'complete' && (
                <button
                  type="button"
                  onClick={async () => {
                    // Open synchronously — popup blockers kill window.open after an await.
                    const sheetWindow = window.open('', '_blank');
                    try {
                      const { data } = await (await import('@/services/api')).api.get(
                        `/api/v1/urban-dna/scenarios/${scenario.id}/plan-sheet`,
                        { responseType: 'blob' },
                      );
                      const url = URL.createObjectURL(data as Blob);
                      if (sheetWindow) {
                        sheetWindow.location.href = url;
                      } else {
                        window.open(url, '_blank');
                      }
                      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
                    } catch {
                      sheetWindow?.close();
                      toast.error('Plan sheet unavailable');
                    }
                  }}
                  title="Open the printable plan sheet: drawing, derived statistics, evaluation history, citations"
                  className="rounded border-2 border-[#151515] bg-white px-1.5 py-0.5 text-[9px] font-black uppercase text-[#151515] hover:bg-[#fff9ec]"
                >
                  Sheet
                </button>
              )}
              <button
                type="button"
                disabled={applying}
                onClick={() => onApply(scenario)}
                className="rounded border-2 border-[#151515] bg-[#c9ff3d] px-1.5 py-0.5 text-[9px] font-black uppercase text-[#151515] hover:bg-[#d8ff70] disabled:opacity-50"
              >
                Apply
              </button>
            </>
          )}
        </div>
      </div>
      {open && payload && (
        <div className="border-t-2 border-[#151515]/20 px-2.5 py-1.5">
          {payload.explanation?.narrative && (
            <p className="text-[10px] leading-snug text-[#151515]">{payload.explanation.narrative}</p>
          )}
          {plan?.status === 'complete' && (
            <p className="mt-1 text-[10px] font-bold text-[#7c3aed]">
              Plan drawn: {plan.block_count} blocks · {plan.parcel_count} parcels ·{' '}
              {plan.intersection_density_per_km2}/km² intersections — toggle it in Imported Layers.
            </p>
          )}
          {plan?.status === 'failed' && (
            <p className="mt-1 text-[10px] text-red-700">Plan drawing failed: {plan.error}</p>
          )}
          {payload.metrics?.metrics && (
            <div className="mt-1.5 rounded border border-[#151515]/25 bg-[#fbfbf7] px-1.5 py-1">
              <p className="text-[9px] font-black uppercase text-[#151515]/60">
                Derived statistics
                <span className="ml-1 font-semibold normal-case text-[#151515]/45">
                  ({payload.metrics.mode === 'geometry' ? 'from drawn plan' : 'from parameters'})
                </span>
              </p>
              {['gfa_m2', 'far_achieved', 'units', 'population', 'parking_stalls', 'open_space_m2'].map((key) => {
                const metric = payload.metrics!.metrics[key];
                if (!metric || metric.value === null) return null;
                return (
                  <div key={key} className="flex items-start justify-between gap-2 py-px">
                    <span className="text-[10px] font-bold text-[#151515]/70" title={metric.derivation}>
                      {metric.label}
                      {metric.assumptions.length > 0 && (
                        <span className="ml-0.5 text-[#151515]/40" title={`Assumptions: ${metric.assumptions.join(', ')}`}>*</span>
                      )}
                    </span>
                    <span className="text-[10px] font-semibold text-[#151515]" title={metric.derivation}>
                      {metric.value.toLocaleString()} {metric.unit !== 'FAR' ? metric.unit : ''}
                    </span>
                  </div>
                );
              })}
              {payload.metrics.ceiling_reconciliation.some((r) => r.status === 'exceeds') && (
                <p className="mt-0.5 text-[9px] leading-snug text-amber-700">
                  Exceeds a district/LAP ceiling in:{' '}
                  {payload.metrics.ceiling_reconciliation
                    .filter((r) => r.status === 'exceeds')
                    .map((r) => r.district)
                    .join(', ')}{' '}
                  — would need relaxation or amendment.
                </p>
              )}
              {payload.metrics.ceiling_reconciliation.some((r) => r.status === 'unknown') && (
                <p className="mt-0.5 text-[9px] leading-snug text-[#151515]/50">
                  Ceiling not assessable from data in:{' '}
                  {payload.metrics.ceiling_reconciliation
                    .filter((r) => r.status === 'unknown')
                    .map((r) => r.district)
                    .join(', ')}
                </p>
              )}
            </div>
          )}
          <div className="mt-1 space-y-0.5">
            {Object.values(payload.plan_parameters || {}).map((parameter) => (
              <div key={parameter.parameter_path} className="flex items-start justify-between gap-2">
                <span className="text-[10px] font-bold text-[#151515]/70" title={parameter.rationale}>
                  {parameter.parameter_path}
                  {parameter.contested && <span className="ml-1 text-amber-700">◆</span>}
                </span>
                <span className="max-w-[55%] text-right text-[10px] font-semibold text-[#151515]">
                  {shortValue(parameter.value)}
                </span>
              </div>
            ))}
          </div>
          {(payload.trade_offs || []).length > 0 && (
            <div className="mt-1.5">
              <p className="text-[9px] font-black uppercase text-amber-700">Trade-offs</p>
              {(payload.trade_offs || []).map((note, index) => (
                <p key={index} className="mt-0.5 text-[9px] leading-snug text-[#151515]/70">{note.message}</p>
              ))}
            </div>
          )}
          {scenario.error && <p className="mt-1 text-[10px] text-red-700">{scenario.error}</p>}
        </div>
      )}
    </div>
  );
}

export function SiteIntelligencePanel({ zone }: { zone: SiteZone }) {
  const queryClient = useQueryClient();
  const [snapshot, setSnapshot] = useState<UrbanDnaSnapshotResponse | null>(null);
  const [scenarios, setScenarios] = useState<UrbanDnaScenarioRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [runningScenarios, setRunningScenarios] = useState(false);
  const [applyingId, setApplyingId] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);

  const refresh = useCallback(async () => {
    try {
      const latest = await urbanDnaApi.getLatest(zone.id);
      setSnapshot(latest);
    } catch (err: any) {
      // Only a real 404 means "never generated" — a transient network/5xx error
      // must not blank the panel and re-offer paid generation mid-build.
      if (err?.response?.status === 404) setSnapshot(null);
    }
    try {
      const list = await urbanDnaApi.listScenarios(zone.id);
      setScenarios(list.scenarios);
    } catch (err: any) {
      if (err?.response?.status === 404) setScenarios([]);
    }
  }, [zone.id]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    refresh().finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [refresh]);

  // Poll while anything is in flight. 'partial' is included because the build
  // checkpoints a partial snapshot before the policy phase — it usually flips
  // to 'complete' moments later (a truly-terminal partial just keeps a cheap
  // poll alive while the panel is open).
  const planStatuses = scenarios.map((s) => (s.payload as any)?.plan?.status).join(',');
  const busy =
    snapshot?.status === 'pending' ||
    snapshot?.status === 'partial' ||
    scenarios.some((s) => s.status === 'pending' || s.status === 'running') ||
    scenarios.some((s) => {
      const plan = (s.payload as any)?.plan;
      return plan?.status === 'queued' || plan?.status === 'drawing';
    });

  // When a plan drawing completes, the new zone layer must appear on the globe.
  // Fire on any per-scenario transition INTO 'complete' — a fast draw can jump
  // queued→complete between polls and 'drawing' is never observed.
  const prevPlanStatusesRef = useRef<string>('');
  useEffect(() => {
    const prev = prevPlanStatusesRef.current.split(',');
    const next = planStatuses.split(',');
    const completedNow = next.some((s, i) => s === 'complete' && prev[i] !== 'complete');
    if (prevPlanStatusesRef.current !== '' && completedNow) {
      queryClient.invalidateQueries({ queryKey: ['site-zones'] });
    }
    prevPlanStatusesRef.current = planStatuses;
  }, [planStatuses, queryClient]);
  useEffect(() => {
    if (!busy) {
      if (pollRef.current) window.clearInterval(pollRef.current);
      pollRef.current = null;
      return;
    }
    pollRef.current = window.setInterval(refresh, POLL_MS);
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
      pollRef.current = null;
    };
  }, [busy, refresh]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await urbanDnaApi.generate(zone.id);
      toast.success('Site DNA generation started');
      await refresh();
    } catch (err) {
      toast.error(getApiErrorMessage(err, 'Failed to start DNA generation'));
    } finally {
      setGenerating(false);
    }
  };

  const handleRunScenarios = async () => {
    setRunningScenarios(true);
    try {
      const response = await urbanDnaApi.createScenarios(zone.id);
      setScenarios(response.scenarios);
      toast.success(`Queued ${response.scenarios.length} planning scenarios`);
    } catch (err) {
      toast.error(getApiErrorMessage(err, 'Failed to queue scenarios'));
    } finally {
      setRunningScenarios(false);
    }
  };

  const [drawingId, setDrawingId] = useState<string | null>(null);
  const handleDrawPlan = async (row: UrbanDnaScenarioRow) => {
    setDrawingId(row.id);
    try {
      await urbanDnaApi.generatePlan(row.id);
      toast.success(`Drawing the ${row.label} plan — streets, blocks and massing`);
      await refresh();
    } catch (err) {
      toast.error(getApiErrorMessage(err, 'Failed to queue plan drawing'));
    } finally {
      setDrawingId(null);
    }
  };

  const handleApply = async (row: UrbanDnaScenarioRow) => {
    setApplyingId(row.id);
    try {
      const result = await urbanDnaApi.applyScenario(row.id);
      toast.success(
        `Applied '${row.label}' — ${Object.keys(result.applied_parameters).length} planning directives set`,
      );
      queryClient.invalidateQueries({ queryKey: ['site-zones'] });
    } catch (err) {
      toast.error(getApiErrorMessage(err, 'Failed to apply scenario'));
    } finally {
      setApplyingId(null);
    }
  };

  const dna = snapshot?.dna;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-[10px] font-black uppercase text-[#151515]/55">
          <Brain className="h-3.5 w-3.5" /> Site Intelligence
          {snapshot?.city_id && (
            <span className="font-semibold normal-case text-[#151515]/45">({snapshot.city_id})</span>
          )}
        </span>
        {snapshot?.overall_confidence != null && <ConfidenceBadge value={snapshot.overall_confidence} />}
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-xs text-[#151515]/60">
          <Loader2 className="h-3.5 w-3.5 animate-spin" /> Loading site intelligence…
        </div>
      ) : !snapshot ? (
        <button
          type="button"
          onClick={handleGenerate}
          disabled={generating}
          className="flex w-full items-center justify-center gap-1.5 rounded-lg border-2 border-[#151515] bg-[#c9ff3d] px-2.5 py-1.5 text-xs font-black uppercase text-[#151515] shadow-[2px_2px_0_0_rgba(21,21,21,0.2)] hover:bg-[#d8ff70] disabled:opacity-50"
        >
          {generating ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
          Generate Site DNA
        </button>
      ) : (
        <>
          <div className="flex items-center justify-between text-[10px] text-[#151515]/60">
            <span>
              {snapshot.status === 'pending' ? (
                <span className="flex items-center gap-1">
                  <Loader2 className="h-3 w-3 animate-spin" /> understanding this place…
                </span>
              ) : (
                <>status: <b>{snapshot.status}</b></>
              )}
            </span>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={generating}
              className="flex items-center gap-1 font-black uppercase hover:text-[#151515] disabled:opacity-40"
              title="Regenerate the DNA from fresh data (also recovers a stuck run)"
            >
              <RefreshCw className={`h-3 w-3 ${generating ? 'animate-spin' : ''}`} /> Refresh
            </button>
          </div>

          {snapshot.status === 'failed' && (
            <p className="text-[10px] text-red-700">{snapshot.error || 'Generation failed.'}</p>
          )}

          {dna && (
            <div className="space-y-1.5">
              {dna.missing_datasets.length > 0 && (
                <p className="text-[10px] text-amber-700">
                  Unavailable datasets: {dna.missing_datasets.join(', ')} — planning continues with
                  reduced confidence.
                </p>
              )}
              {URBAN_DNA_SECTION_NAMES.map((name) =>
                name === 'market' && Object.keys(dna[name]?.fields || {}).length === 0 ? null : (
                  <DnaSectionRow key={name} name={name} section={dna[name]} />
                ),
              )}
              <PolicyInsightBlock section={dna.policy} />
            </div>
          )}

          {(snapshot.status === 'complete' || snapshot.status === 'partial') && (
            <div className="space-y-1.5 pt-1">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-black uppercase text-[#151515]/55">
                  Planning Scenarios
                </span>
                <button
                  type="button"
                  onClick={handleRunScenarios}
                  disabled={runningScenarios || scenarios.some((s) => s.status === 'pending' || s.status === 'running')}
                  className="flex items-center gap-1 rounded border-2 border-[#151515] bg-white px-1.5 py-0.5 text-[9px] font-black uppercase text-[#151515] shadow-[2px_2px_0_0_rgba(21,21,21,0.2)] hover:bg-[#fff9ec] disabled:opacity-50"
                >
                  {runningScenarios ? <Loader2 className="h-3 w-3 animate-spin" /> : <Play className="h-3 w-3" />}
                  Run scenarios
                </button>
              </div>
              {scenarios.length === 0 && (
                <p className="text-[10px] text-[#151515]/50">
                  Run the expert panel to get As-of-Right, Plan-Aligned and Climate-First concepts
                  with their trade-offs.
                </p>
              )}
              {scenarios.map((scenario) => (
                <ScenarioCard
                  key={scenario.id}
                  scenario={scenario}
                  onApply={handleApply}
                  applying={applyingId === scenario.id}
                  onDrawPlan={handleDrawPlan}
                  drawing={drawingId === scenario.id}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
