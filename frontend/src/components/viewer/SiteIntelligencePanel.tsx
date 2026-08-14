/**
 * Site Intelligence — Urban DNA report + planning-agent scenarios.
 *
 * Rendered for site_boundary zones. Backend does all the work
 * (/api/v1/urban-dna); this panel shows per-section confidence, warnings and
 * missing datasets honestly, and lets the user run/apply planning scenarios.
 * Applying a scenario writes non-destructive planning directives onto the
 * boundary zone (properties._urban_dna_directives) that the layout prompts read.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Brain, ChevronDown, ChevronRight, Loader2, Play, RefreshCw, Sparkles, X } from 'lucide-react';
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
import { isPersistedZoneId } from '@/utils/zoneIdentity';
import {
  hasScenarioPlanCompleted,
  snapshotScenarioPlanStatuses,
  type ScenarioPlanStatusSnapshot,
} from './siteIntelligencePlanStatus';

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

const METHOD_LABELS: Record<string, string> = {
  euclidean_estimate: 'straight-line est.',
};

/** Humanize the common DNA object shapes instead of leaking raw JSON:
 * nearest-X = {name?, distance_m, network_estimate_m?, method}, elevation =
 * {min_m, max_m, method}. Generic objects fall back to key: value pairs. */
function humanizeObject(value: Record<string, unknown>): string {
  const method = typeof value.method === 'string'
    ? (METHOD_LABELS[value.method] ?? value.method.replace(/_/g, ' '))
    : undefined;

  if (typeof value.min_m === 'number' && typeof value.max_m === 'number') {
    return `${value.min_m.toLocaleString()}–${value.max_m.toLocaleString()} m`;
  }

  const parts: string[] = [];
  if (typeof value.name === 'string' && value.name) parts.push(value.name);
  if (typeof value.distance_m === 'number') parts.push(`${Math.round(value.distance_m).toLocaleString()} m`);
  if (parts.length) return method ? `${parts.join(' · ')} (${method})` : parts.join(' · ');

  const pairs = Object.entries(value)
    .filter(([key, v]) => v !== null && v !== undefined && key !== 'method' && typeof v !== 'object')
    .slice(0, 4)
    .map(([key, v]) => {
      const shown = typeof v === 'number'
        ? (Number.isInteger(v) ? v.toLocaleString() : (v as number).toFixed(1))
        : String(v).slice(0, 40);
      return `${key.replace(/_/g, ' ')}: ${shown}`;
    });
  const text = pairs.join(' · ');
  if (text) return method ? `${text} (${method})` : text;
  const json = JSON.stringify(value);
  return json.length > 90 ? `${json.slice(0, 90)}…` : json;
}

function shortValue(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'number') return Number.isInteger(value) ? String(value) : value.toFixed(2);
  if (typeof value === 'string') return value.length > 90 ? `${value.slice(0, 90)}…` : value;
  if (typeof value === 'boolean') return value ? 'yes' : 'no';
  if (Array.isArray(value)) return `${value.length} item${value.length === 1 ? '' : 's'}`;
  if (typeof value === 'object') {
    const text = humanizeObject(value as Record<string, unknown>);
    return text.length > 120 ? `${text.slice(0, 120)}…` : text;
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

// Official references per city + section — curated, verified URLs (2026-07-07).
const OFFICIAL_SECTION_LINKS: Record<string, Partial<Record<UrbanDnaSectionName, Array<{ label: string; url: string }>>>> = {
  calgary: {
    land_use: [
      { label: 'Land use maps', url: 'https://www.calgary.ca/maps/land-use-bylaw.html' },
      { label: 'Bylaw 1P2007', url: 'https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html' },
    ],
  },
};

function DnaSectionRow({ name, section, cityId }: {
  name: UrbanDnaSectionName; section: UrbanDnaSection; cityId?: string;
}) {
  const [open, setOpen] = useState(false);
  const fieldEntries = Object.entries(section.fields || {});
  const filled = fieldEntries.filter(([, field]) => field.value !== null && field.value !== undefined);
  const officialLinks = (cityId && OFFICIAL_SECTION_LINKS[cityId]?.[name]) || [];

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
            <div key={fieldName} className="flex min-w-0 items-start justify-between gap-2 py-0.5">
              <span className="shrink-0 text-[10px] font-bold text-[#151515]/70">{fieldName.replace(/_/g, ' ')}</span>
              <span
                className="min-w-0 max-w-[60%] break-words text-right text-[10px] font-semibold text-[#151515]"
                title={JSON.stringify(field.value)}
              >
                {shortValue(field.value)}
              </span>
            </div>
          ))}
          {officialLinks.length > 0 && (
            <p className="mt-1 text-[9px] font-bold">
              {officialLinks.map((link, i) => (
                <span key={link.url}>
                  {i > 0 && ' · '}
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#151515]/60 underline decoration-dotted hover:text-[#151515]"
                  >
                    {link.label} ↗
                  </a>
                </span>
              ))}
            </p>
          )}
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

type InsightCitation = { doc: string; page: number; verified?: boolean; url?: string | null; title?: string };

function PolicyInsightBlock({ section }: { section: UrbanDnaSection }) {
  const insight = section.fields?.insight?.value as
    | {
        summaries?: string[];
        conformance_considerations?: Array<{
          topic: string; framing: string; risk: string; detail: string;
          citations?: InsightCitation[];
        }>;
        opportunities?: Array<{
          topic: string; detail: string;
          citations?: InsightCitation[];
        }>;
        disclaimer?: string;
      }
    | undefined;
  if (!insight) return null;

  // Citations link straight to the official document (URL comes from the
  // seeded corpus, never from the model). #page=N deep-links into PDFs.
  const renderCitations = (citations?: InsightCitation[]) =>
    citations && citations.length > 0 ? (
      <span className="ml-1 text-[9px] font-bold text-[#151515]/50">
        [{citations.map((c, i) => (
          <span key={`${c.doc}-${c.page}-${i}`}>
            {i > 0 && '; '}
            {c.url ? (
              <a
                href={`${c.url}${c.url.toLowerCase().endsWith('.pdf') ? `#page=${c.page}` : ''}`}
                target="_blank"
                rel="noopener noreferrer"
                title={c.title || c.doc}
                className="underline decoration-dotted hover:text-[#151515]"
              >
                {c.doc} p{c.page}
              </a>
            ) : (
              `${c.doc} p${c.page}`
            )}
          </span>
        ))}]
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

const COMPARE_METRIC_KEYS = ['units', 'gfa_m2', 'far_achieved', 'population', 'open_space_m2'] as const;

// Comparison deltas are measured against the conservative market case; older
// projects may still carry the retired 'as_of_right' baseline.
const BASELINE_SCENARIO_IDS = ['economic', 'as_of_right'];

/** Side-by-side scenario numbers with deltas vs the Economic baseline. */
function ScenarioCompareTable({ scenarios }: { scenarios: UrbanDnaScenarioRow[] }) {
  const withMetrics = scenarios.filter((s) => s.payload?.metrics?.metrics);
  if (withMetrics.length < 2) return null;
  const baseline = withMetrics.find((s) => BASELINE_SCENARIO_IDS.includes(s.scenario_id));

  const value = (row: UrbanDnaScenarioRow, key: string): number | null => {
    const metric = row.payload?.metrics?.metrics?.[key];
    return metric && metric.value !== null ? Number(metric.value) : null;
  };
  const label = (key: string): string => {
    for (const row of withMetrics) {
      const metric = row.payload?.metrics?.metrics?.[key];
      if (metric?.label) return metric.label;
    }
    return key;
  };

  return (
    <div className="rounded-lg border-2 border-[#151515] bg-white p-2 shadow-[2px_2px_0_0_rgba(21,21,21,0.2)]">
      <p className="mb-1 text-[9px] font-black uppercase text-[#151515]/60">Scenario comparison</p>
      <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="whitespace-nowrap pb-0.5 text-left text-[9px] font-black uppercase text-[#151515]/50">Measure</th>
            {withMetrics.map((s) => (
              <th key={s.id} className="whitespace-nowrap pb-0.5 text-right text-[9px] font-black text-[#151515]">
                {s.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {COMPARE_METRIC_KEYS.map((key) => {
            if (!withMetrics.some((s) => value(s, key) !== null)) return null;
            const base = baseline ? value(baseline, key) : null;
            return (
              <tr key={key} className="border-t border-[#151515]/10">
                <td className="py-0.5 pr-1 text-[10px] font-bold text-[#151515]/70">{label(key)}</td>
                {withMetrics.map((s) => {
                  const v = value(s, key);
                  const delta = v !== null && base !== null
                    && !BASELINE_SCENARIO_IDS.includes(s.scenario_id) && base !== 0
                    ? (v - base) / base : null;
                  return (
                    <td key={s.id} className="py-0.5 text-right text-[10px] font-semibold text-[#151515]">
                      {v === null ? '—' : v.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                      {delta !== null && Math.abs(delta) >= 0.005 && (
                        <span className={delta > 0 ? 'ml-0.5 text-[9px] text-emerald-700' : 'ml-0.5 text-[9px] text-red-700'}>
                          {delta > 0 ? '+' : ''}{Math.round(delta * 100)}%
                        </span>
                      )}
                    </td>
                  );
                })}
              </tr>
            );
          })}
          <tr className="border-t border-[#151515]/10">
            <td className="py-0.5 pr-1 text-[10px] font-bold text-[#151515]/70">Plan score</td>
            {withMetrics.map((s) => {
              const score = (s.payload as any)?.plan?.final_score;
              return (
                <td key={s.id} className="py-0.5 text-right text-[10px] font-semibold text-[#151515]">
                  {typeof score === 'number' ? score.toFixed(3) : '—'}
                </td>
              );
            })}
          </tr>
        </tbody>
      </table>
      </div>
    </div>
  );
}

function ScenarioCard({
  scenario,
  onApply,
  applying,
  onDrawPlan,
  drawing,
  soloed,
  onSolo,
  onDelete,
  deleting,
}: {
  scenario: UrbanDnaScenarioRow;
  onApply: (row: UrbanDnaScenarioRow) => void;
  applying: boolean;
  onDrawPlan: (row: UrbanDnaScenarioRow) => void;
  drawing: boolean;
  soloed: boolean;
  onSolo: (row: UrbanDnaScenarioRow | null) => void;
  onDelete: (row: UrbanDnaScenarioRow) => void;
  deleting: boolean;
}) {
  const [open, setOpen] = useState(false);
  const payload = scenario.payload;
  const parameterCount = Object.keys(payload?.plan_parameters || {}).length;
  const plan = (payload as any)?.plan as
    | { status?: string; block_count?: number; parcel_count?: number; zone_count?: number;
        intersection_density_per_km2?: number; error?: string | null }
    | undefined;
  const planBusy = plan?.status === 'queued' || plan?.status === 'drawing';

  const openExport = async (path: 'plan-sheet' | 'hearing-pack', autoPrint: boolean) => {
    // Open synchronously — popup blockers kill window.open after an await.
    const sheetWindow = window.open('', '_blank');
    try {
      const { data } = await (await import('@/services/api')).api.get(
        `/api/v1/urban-dna/scenarios/${scenario.id}/${path}`,
        { responseType: 'text', transformResponse: [(value: string) => value] },
      );
      let html = data as string;
      if (autoPrint) {
        // Inject an auto-print trigger so "PDF" = browser print-to-PDF dialog.
        html = html.replace(
          '</body>',
          '<script>window.addEventListener("load",()=>setTimeout(()=>window.print(),400));</script></body>',
        );
      }
      const url = URL.createObjectURL(new Blob([html], { type: 'text/html' }));
      if (sheetWindow) {
        sheetWindow.location.href = url;
      } else {
        window.open(url, '_blank');
      }
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch {
      sheetWindow?.close();
      toast.error(path === 'hearing-pack' ? 'Hearing pack unavailable' : 'Plan sheet unavailable');
    }
  };

  return (
    <div className="rounded-lg border-2 border-[#151515] bg-white shadow-[2px_2px_0_0_rgba(21,21,21,0.2)]">
      <div className="flex flex-wrap items-center justify-between gap-y-1 px-2.5 py-1.5">
        <button type="button" onClick={() => setOpen((v) => !v)} className="flex min-w-0 items-center gap-1.5">
          {open ? <ChevronDown className="h-3 w-3 shrink-0" /> : <ChevronRight className="h-3 w-3 shrink-0" />}
          <span className="truncate text-xs font-black text-[#151515]">{scenario.label}</span>
        </button>
        <div className="flex flex-wrap items-center justify-end gap-1.5">
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
                <>
                  <button
                    type="button"
                    onClick={() => onSolo(soloed ? null : scenario)}
                    title={soloed
                      ? 'Show all plan layers again'
                      : "Show only this scenario's plan on the globe (hides other plans and framework layers)"}
                    className={`rounded border-2 border-[#151515] px-1.5 py-0.5 text-[9px] font-black uppercase text-[#151515] ${soloed ? 'bg-[#151515] text-white hover:bg-[#333]' : 'bg-white hover:bg-[#fff9ec]'}`}
                  >
                    {soloed ? 'All' : 'Solo'}
                  </button>
                  <button
                    type="button"
                    onClick={() => openExport('plan-sheet', false)}
                    title="Open the printable plan sheet: drawing, derived statistics, evaluation history, citations"
                    className="rounded border-2 border-[#151515] bg-white px-1.5 py-0.5 text-[9px] font-black uppercase text-[#151515] hover:bg-[#fff9ec]"
                  >
                    Sheet
                  </button>
                  <button
                    type="button"
                    onClick={() => openExport('plan-sheet', true)}
                    title="Open the plan sheet with the print dialog — choose 'Save as PDF'"
                    className="rounded border-2 border-[#151515] bg-white px-1.5 py-0.5 text-[9px] font-black uppercase text-[#151515] hover:bg-[#fff9ec]"
                  >
                    PDF
                  </button>
                  <button
                    type="button"
                    onClick={() => openExport('hearing-pack', false)}
                    title="Assemble the hearing pack: banner + provenance, plan drawing paired with its conditioning diagram, watermarked renders, scenario comparison, trade-offs, cited policy notes"
                    className="rounded border-2 border-[#151515] bg-[#ffd66e] px-1.5 py-0.5 text-[9px] font-black uppercase text-[#151515] hover:bg-[#ffe092]"
                  >
                    Pack
                  </button>
                </>
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
          {scenario.scenario_id.startsWith('custom_') && (
            <button
              type="button"
              // Disabled mid-run/mid-draw: deleting under an in-flight task
              // wastes the paid run and can orphan freshly drawn plan zones.
              disabled={deleting || scenario.status === 'pending' || scenario.status === 'running' || planBusy}
              onClick={() => onDelete(scenario)}
              title={scenario.status === 'pending' || scenario.status === 'running' || planBusy
                ? 'Wait for the run to finish before deleting'
                : 'Delete this custom scenario and its drawn plan layer (the brief stays prefilled for a re-run)'}
              className="rounded border-2 border-[#151515] bg-white p-0.5 text-[#151515] hover:bg-red-100 disabled:opacity-50"
            >
              {deleting ? <Loader2 className="h-3 w-3 animate-spin" /> : <X className="h-3 w-3" />}
            </button>
          )}
        </div>
      </div>
      {/* complete/failed only: a pending CUSTOM row carries its creation
          payload (brief/definition) and would render an empty strip. */}
      {open && payload && (scenario.status === 'complete' || scenario.status === 'failed') && (
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
  const [soloId, setSoloId] = useState<string | null>(null);
  const [scenariosStale, setScenariosStale] = useState(false);
  const [customOpen, setCustomOpen] = useState(false);
  const [customBrief, setCustomBrief] = useState('');
  const [runningCustom, setRunningCustom] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);
  const zonePersisted = isPersistedZoneId(zone.id);

  // Solo a scenario's plan on the globe. Layer visibility lives in
  // ProjectViewPage (hiddenLayers) two components up — a window event keeps
  // this demo control out of the ZonePropertiesPanel prop chain.
  const handleSolo = useCallback((row: UrbanDnaScenarioRow | null) => {
    setSoloId(row ? row.id : null);
    window.dispatchEvent(new CustomEvent('cityprompt:solo-plan-layer', {
      detail: { label: row ? row.label : null },
    }));
  }, []);

  const refresh = useCallback(async () => {
    // An unsaved zone has a temp- id; every urban-dna endpoint 422s on it.
    if (!isPersistedZoneId(zone.id)) {
      setSnapshot(null);
      setScenarios([]);
      return;
    }
    try {
      const latest = await urbanDnaApi.getLatest(zone.id);
      setSnapshot(latest);
    } catch (err: any) {
      // Only a real 404 means "never generated" — a transient network/5xx error
      // must not blank the panel and re-offer paid generation mid-build.
      // NOTE: the 404 itself is a NORMAL "no snapshot yet" response for any
      // boundary that never ran Site DNA — the red line devtools prints for it
      // is browser noise, not an application error.
      if (err?.response?.status === 404) setSnapshot(null);
    }
    try {
      const list = await urbanDnaApi.listScenarios(zone.id);
      setScenarios(list.scenarios);
      setScenariosStale(Boolean(list.stale));
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

  // V1 limit: a DNA refresh orphans custom cards (the list prefers the latest
  // snapshot) while their plan layers stay. Prefill the textarea from the
  // newest visible custom row's stored brief so it's re-runnable in one click.
  // NEVER fight the user: once they've typed in the textarea (touched), or
  // once the loaded list has been considered, no further prefill fires —
  // clearing the field must not snap the old brief back.
  const briefPrefilledRef = useRef(false);
  const briefTouchedRef = useRef(false);
  useEffect(() => {
    briefPrefilledRef.current = false;
    briefTouchedRef.current = false;
  }, [zone.id]);
  useEffect(() => {
    if (briefPrefilledRef.current || briefTouchedRef.current || customBrief) return;
    if (!scenarios.length) return; // wait for the first loaded list
    const customRows = scenarios.filter((s) => s.scenario_id.startsWith('custom_'));
    const newest = customRows[customRows.length - 1];
    const storedBrief = (newest?.payload as Record<string, unknown> | undefined)?.brief;
    if (typeof storedBrief === 'string' && storedBrief.trim()) {
      setCustomBrief(storedBrief);
    }
    briefPrefilledRef.current = true; // one shot per zone, prefilled or not
  }, [scenarios, customBrief]);

  // Only one plan should be visible on the globe at a time. When a zone loads
  // already carrying multiple drawn plans (stacked from earlier draws), solo
  // the most-recently-drawn one so they don't overlay. Fires once per zone and
  // only when nothing is explicitly soloed yet — a later manual Solo/All wins.
  const autoSoloedRef = useRef(false);
  useEffect(() => {
    autoSoloedRef.current = false;
  }, [zone.id]);
  useEffect(() => {
    if (autoSoloedRef.current || soloId) return;
    const drawn = scenarios.filter((s) => (s.payload as any)?.plan?.status === 'complete');
    if (drawn.length < 2) return; // 0 or 1 plan can't stack — leave it shown
    const newest = drawn.reduce((a, b) => {
      const ta = String((a.payload as any)?.plan?.generated_at ?? '');
      const tb = String((b.payload as any)?.plan?.generated_at ?? '');
      return tb > ta ? b : a;
    });
    autoSoloedRef.current = true;
    handleSolo(newest);
  }, [scenarios, soloId, handleSolo]);

  // Poll while anything is in flight. 'partial' is included because the build
  // checkpoints a partial snapshot before the policy phase — it usually flips
  // to 'complete' moments later (a truly-terminal partial just keeps a cheap
  // poll alive while the panel is open).
  const planStatuses = useMemo(
    () => snapshotScenarioPlanStatuses(scenarios),
    [scenarios],
  );
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
  const prevPlanStatusesRef = useRef<ScenarioPlanStatusSnapshot | null>(null);
  useEffect(() => {
    prevPlanStatusesRef.current = null;
  }, [zone.id]);
  useEffect(() => {
    if (hasScenarioPlanCompleted(prevPlanStatusesRef.current, planStatuses)) {
      void queryClient.invalidateQueries({ queryKey: ['site-zones'] });
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
      // refresh(), NOT setScenarios(response.scenarios) — the response only
      // holds the rows just created and would clobber the displayed cards
      // (existing custom runs and their drawn plans would vanish).
      await refresh();
      toast.success(`Queued ${response.scenarios.length} planning scenarios`);
    } catch (err) {
      toast.error(getApiErrorMessage(err, 'Failed to queue scenarios'));
    } finally {
      setRunningScenarios(false);
    }
  };

  const handleRunCustom = async () => {
    const brief = customBrief.trim();
    if (!brief) return;
    setRunningCustom(true);
    try {
      await urbanDnaApi.createScenarios(zone.id, [], brief);
      await refresh();
      toast.success('Custom scenario queued — the expert panel is running your brief');
    } catch (err) {
      toast.error(getApiErrorMessage(err, 'Failed to queue the custom scenario'));
    } finally {
      setRunningCustom(false);
    }
  };

  const handleDeleteScenario = async (row: UrbanDnaScenarioRow) => {
    setDeletingId(row.id);
    try {
      await urbanDnaApi.deleteScenario(row.id);
      if (soloId === row.id) handleSolo(null);
      // Its plan zones were deleted server-side — drop them from the globe.
      queryClient.invalidateQueries({ queryKey: ['site-zones'] });
      await refresh();
      toast.success(`Deleted '${row.label}'`);
    } catch (err) {
      toast.error(getApiErrorMessage(err, 'Failed to delete the scenario'));
    } finally {
      setDeletingId(null);
    }
  };

  const [drawingId, setDrawingId] = useState<string | null>(null);
  const handleDrawPlan = async (row: UrbanDnaScenarioRow) => {
    setDrawingId(row.id);
    try {
      await urbanDnaApi.generatePlan(row.id);
      // One plan on the globe at a time: soloing the scenario we just queued
      // hides every other drawn plan, and this plan's zones appear as they're
      // drawn — so a new plan REPLACES the previous one instead of stacking on
      // top of it. Fired only after a successful queue so a failed draw never
      // blanks the user's current view. Use "All" on a card to compare plans.
      handleSolo(row);
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
      ) : !zonePersisted ? (
        <p className="rounded-lg border-2 border-dashed border-[#151515]/40 px-2.5 py-1.5 text-[11px] text-[#151515]/70">
          Save the boundary first (<b>Save Changes</b> above) — then generate Site DNA.
        </p>
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
                  <DnaSectionRow key={name} name={name} section={dna[name]} cityId={snapshot.city_id} />
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
                  Run the expert panel to get Economic, City Policy, City Beautiful and
                  Environmental concepts with their trade-offs — or write your own brief below.
                </p>
              )}
              {scenariosStale && scenarios.length > 0 && (
                <p className="rounded border border-amber-500/50 bg-amber-50 px-1.5 py-1 text-[9px] font-bold text-amber-800">
                  These scenarios pre-date the latest DNA refresh — re-run scenarios to base them on
                  the current data.
                </p>
              )}
              <div className="rounded-lg border-2 border-dashed border-[#151515]/40 px-2 py-1.5">
                <button
                  type="button"
                  onClick={() => setCustomOpen((v) => !v)}
                  className="flex w-full items-center gap-1.5 text-[10px] font-black uppercase text-[#151515]/70"
                >
                  {customOpen ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                  Custom scenario
                </button>
                {customOpen && (
                  <div className="mt-1.5 space-y-1.5">
                    <textarea
                      value={customBrief}
                      onChange={(e) => {
                        briefTouchedRef.current = true;
                        setCustomBrief(e.target.value);
                      }}
                      maxLength={2000}
                      rows={3}
                      placeholder='Describe the concept — e.g. "a European style development with a large central park"'
                      className="w-full rounded border-2 border-[#151515] bg-white px-2 py-1.5 text-[11px] font-semibold text-[#151515] focus:bg-[#fff9ec] focus:outline-none"
                    />
                    <button
                      type="button"
                      onClick={handleRunCustom}
                      disabled={runningCustom || !customBrief.trim()}
                      className="flex w-full items-center justify-center gap-1 rounded border-2 border-[#151515] bg-[#b78aff] px-2 py-1 text-[10px] font-black uppercase text-[#151515] hover:bg-[#c9a2ff] disabled:opacity-50"
                    >
                      {runningCustom ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
                      Run custom scenario
                    </button>
                    <p className="text-[9px] leading-snug text-[#151515]/50">
                      Runs the full expert panel on your brief and adds a fourth card. A DNA refresh
                      hides older custom cards — the brief stays prefilled here to re-run in one click.
                    </p>
                  </div>
                )}
              </div>
              {scenarios.map((scenario) => (
                <ScenarioCard
                  key={scenario.id}
                  scenario={scenario}
                  onApply={handleApply}
                  applying={applyingId === scenario.id}
                  onDrawPlan={handleDrawPlan}
                  drawing={drawingId === scenario.id}
                  soloed={soloId === scenario.id}
                  onSolo={handleSolo}
                  onDelete={handleDeleteScenario}
                  deleting={deletingId === scenario.id}
                />
              ))}
              <ScenarioCompareTable scenarios={scenarios} />
            </div>
          )}
        </>
      )}
    </div>
  );
}
