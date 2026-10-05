import { useEffect, useId, useRef } from 'react';
import { ExternalLink, X } from 'lucide-react';
import { RILEY_SOURCE } from './rileyPolicy';
import type { RileyPolicyState } from './useRileyPolicy';

export function PolicyDetailsCard({ selected, onClose }: { selected: RileyPolicyState['selected']; onClose: () => void }) {
  const headingId = useId();
  const card = useRef<HTMLElement>(null);
  const selectionKey = selected ? `${selected.designation.name}:${selected.featureId ?? 'legend'}` : null;
  useEffect(() => { if (selectionKey) card.current?.focus({ preventScroll: true }); }, [selectionKey]);
  if (!selected) return null;
  const { designation, featureId } = selected;
  return <section ref={card} role="region" aria-labelledby={headingId} tabIndex={-1}
    onKeyDown={event => { if (event.key === 'Escape') { event.stopPropagation(); onClose(); } }}
    className="absolute bottom-16 right-3 z-40 max-h-[65vh] w-[min(24rem,calc(100vw-1.5rem))] overflow-y-auto rounded-2xl border border-[#151515]/25 bg-[#fffdf6] text-[#151515] shadow-2xl focus:outline-none sm:bottom-20 sm:right-4">
    <header className="sticky top-0 z-10 flex items-start gap-3 border-b border-[#151515]/10 bg-[#fffdf6] p-4">
      <span aria-hidden className="mt-1 h-5 w-5 shrink-0 rounded border border-black/25" style={{ backgroundColor: designation.color }} />
      <div className="min-w-0 flex-1"><p className="text-[10px] font-semibold uppercase tracking-widest text-[#5c554d]">{featureId ? 'Selected policy area' : 'Urban form designation'}</p><h2 id={headingId} className="mt-1 text-base font-bold leading-snug">{designation.name}</h2></div>
      <button type="button" aria-label="Close policy details" onClick={onClose} className="-mr-2 -mt-2 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl hover:bg-stone-100 focus-visible:outline focus-visible:outline-2"><X size={18} aria-hidden /></button>
    </header>
    <div className="space-y-4 p-4 text-sm leading-relaxed">
      <p>{designation.summary}</p>
      <div><h3 className="mb-2 text-xs font-bold uppercase tracking-wide">Planning considerations</h3><ul className="list-disc space-y-2 pl-4">{designation.considerations.map(text => <li key={text}>{text}</li>)}</ul></div>
      <div className="space-y-2 border-t border-[#151515]/10 pt-3 text-xs text-[#5c554d]">
        <p>Student summary of the approved Riley plan. Read alongside Building Scale, area-specific policies and the current Land Use Bylaw when proposing a change.</p>
        {designation.relatedSections && <p>{designation.relatedSections}</p>}
        <a className="flex min-h-11 items-center gap-2 font-semibold text-[#37594b] underline underline-offset-2" href={`${RILEY_SOURCE.split('#')[0]}#page=${designation.pdfPage}`} target="_blank" rel="noreferrer"><span>Read section {designation.section} · page {designation.page}</span><ExternalLink size={14} aria-hidden /></a>
        <p className="text-[10px]">Riley Communities Local Area Plan · 25P2025 / 38P2025</p>
      </div>
    </div>
  </section>;
}
