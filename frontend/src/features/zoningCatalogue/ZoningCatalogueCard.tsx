import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { Building2, ExternalLink, X } from 'lucide-react';
import { CANONICAL_CHOICES } from '@/features/pickPlace/canonicalCatalogue';
import type { PlaceAsset } from '@/features/pickPlace/assetRegistry';
import { matchCatalogue, rulesForZone, RULES_REVIEWED_AT } from './matching';
import type { BuildingMatch, ZoneInspection } from './types';

export const ZONING_CATALOGUE_BUILDINGS = [...new Map(CANONICAL_CHOICES.filter(c => c.domain === 'building')
  .flatMap(c => c.placements).filter((a): a is PlaceAsset => a.kind === 'object' && a.zoneType === 'building')
  .map(a => [a.model.variantId, a])).values()];

export function CatalogueMatches({ zone }: { zone: ZoneInspection }) {
  const matches = useMemo(() => matchCatalogue(ZONING_CATALOGUE_BUILDINGS, zone), [zone]);
  const district = rulesForZone(zone);
  if (!district) return <p className="text-sm leading-relaxed">{zone.custom
    ? 'This is a custom zone. Choose a Calgary district to compare catalogue uses and heights.'
    : 'This designation needs a specific bylaw review. Direct Control districts have their own rules.'}</p>;
  const { rule } = district;
  const limit = rule.height.mode === 'mapped' ? district.height ?? rule.height.metres : rule.height.metres;
  return <div className="space-y-4 text-sm leading-relaxed">
    <div className="rounded-xl bg-[#edf2ec] px-3 py-2 text-xs">
      <p className="font-semibold">{limit !== undefined ? `${limit} m reference height` : rule.height.mode === 'unlimited' ? 'No district-wide height maximum' : 'Height needs a site-specific check'} · {matches.length} models</p>
      <p className="mt-1">Use + height candidates at catalogue size. Site rules still apply.</p>
      <details className="mt-1"><summary className="flex min-h-11 cursor-pointer items-center font-semibold underline underline-offset-2">What this check covers</summary>
        <p>New buildings only. Setbacks, density, floor area, access and bylaw height measurement still need a site check.</p>
        <p className="mt-2">{rule.height.note}</p>
        {rule.note && <p className="mt-2">{rule.note}</p>}
      </details>
    </div>
    {(['permitted', 'discretionary'] as const).map(status => {
      const rows = matches.filter(m => m.status === status);
      return <section key={status} aria-label={`${status === 'permitted' ? 'Permitted' : 'Discretionary'} use candidates`}>
        <h3 className="font-bold">{status === 'permitted' ? 'Permitted' : 'Discretionary'} use candidates <span className="font-normal text-stone-500">({rows.length})</span></h3>
        {rows.length > 0 && <p className="mb-2 mt-1 text-xs text-stone-600">{status === 'permitted' ? 'Listed permitted use, subject to all applicable rules.' : 'Listed discretionary use; a development application requires assessment.'}</p>}
        {rows.length ? <ul className="space-y-2">{rows.map(row => <MatchRow key={row.asset.id} row={row} source={rule.source} />)}</ul>
          : <p className="mt-1 text-xs text-stone-600">No confirmed candidates in this catalogue.</p>}
      </section>;
    })}
    {(['review', 'outside'] as const).map(status => {
      const rows = matches.filter(m => m.status === status);
      return rows.length ? <details key={status} className="rounded-xl border border-stone-200 bg-white">
        <summary className="min-h-11 cursor-pointer p-3 text-xs font-semibold">{status === 'review' ? 'More information needed' : 'Outside this screening'} ({rows.length})</summary>
        <ul className="space-y-2 px-3 pb-3">{rows.map(row => <MatchRow key={row.asset.id} row={row} source={rule.source} />)}</ul>
      </details> : null;
    })}
    <p className="text-xs text-stone-600">A building can appear in several districts. Uses here follow the stated teaching program; changing its occupancy or size requires a new check.</p>
    <a href={rule.source} target="_blank" rel="noreferrer" className="flex min-h-11 items-center gap-2 text-xs font-semibold text-[#37594b] underline">Read {district.code} bylaw rules <ExternalLink size={13} aria-hidden /></a>
    <p className="text-[10px] text-stone-500">Bylaw snapshot reviewed {RULES_REVIEWED_AT} · {matches.length} current catalogue models · Use sources are linked on each result.</p>
  </div>;
}

function MatchRow({ row, source }: { row: BuildingMatch; source: string }) {
  const [failedImage, setFailedImage] = useState<string | null>(null);
  return <li className="rounded-xl border border-stone-200 bg-white p-3">
    <div className="flex items-start gap-3">
      {failedImage === row.asset.thumbnail ? <span aria-label="Preview unavailable" className="flex h-16 w-16 shrink-0 items-center justify-center rounded-lg bg-stone-100 text-stone-400"><Building2 size={25} aria-hidden /></span>
        : <img src={row.asset.thumbnail} alt="" loading="lazy" onError={() => setFailedImage(row.asset.thumbnail)} className="h-16 w-16 shrink-0 rounded-lg bg-stone-100 object-cover" />}
      <div className="min-w-0"><h4 className="text-xs font-bold leading-snug">{row.asset.label}</h4>
        <p className="mt-1 text-[11px] text-stone-600">{row.height === undefined ? 'Height unverified' : `${row.height.toFixed(1)} m model height`}{row.limit !== undefined ? ` · ${row.limit} m limit` : ''}</p>
        {row.uses.map(use => <p key={`${use.use}:${use.section}`} className="mt-1 text-[11px]"><a className="underline underline-offset-2" href={`${source}#section${use.section.split('(')[0]}`} target="_blank" rel="noreferrer">{use.use} · s.{use.section}</a></p>)}
      </div>
    </div>
    {row.program && <p className="mt-2 text-[11px] text-stone-600">{row.program.assumption}</p>}
    {row.reasons.map(reason => <p key={reason} className="mt-2 text-[11px] text-amber-900">{reason}</p>)}
  </li>;
}

export function ZoningCatalogueCard({ zone, onClose }: { zone: ZoneInspection | null; onClose: () => void }) {
  const heading = useId();
  const card = useRef<HTMLElement>(null);
  const key = zone ? `${zone.layerId ?? 'city'}:${zone.id}` : null;
  useEffect(() => { if (key) card.current?.focus({ preventScroll: true }); }, [key]);
  if (!zone) return null;
  return <section ref={card} role="region" aria-labelledby={heading} tabIndex={-1}
    onKeyDown={event => { if (event.key === 'Escape') { event.stopPropagation(); onClose(); } }}
    className="absolute bottom-16 right-3 z-40 max-h-[72vh] w-[min(26rem,calc(100vw-1.5rem))] overflow-y-auto overscroll-contain rounded-2xl border border-[#151515]/25 bg-[#fffdf6] text-[#151515] shadow-2xl focus:outline-none sm:bottom-20 sm:right-4">
    <header className="sticky top-0 z-10 flex items-start gap-3 border-b border-stone-200 bg-[#fffdf6] p-4">
      <span aria-hidden className="mt-1 h-5 w-5 shrink-0 rounded border border-black/20" style={{ backgroundColor: zone.color ?? '#fff7da' }} />
      <div className="min-w-0 flex-1"><p className="text-[10px] font-semibold uppercase tracking-widest text-stone-600">{zone.source}</p><h2 id={heading} className="mt-1 text-lg font-bold">{zone.district?.designation ?? zone.label}</h2><p className="text-xs text-stone-600">{zone.district?.description ?? 'Catalogue building matches'}</p></div>
      <button type="button" aria-label="Close zoning catalogue" onClick={onClose} className="-mr-2 -mt-2 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl hover:bg-stone-100"><X size={18} aria-hidden /></button>
    </header>
    <div className="p-4"><CatalogueMatches zone={zone} /></div>
  </section>;
}
