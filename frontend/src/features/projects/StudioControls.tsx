import { useEffect, useRef, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { Check, FileText, HelpCircle, Layers, Loader2, RotateCw, Users, X } from 'lucide-react';

export function StudioControls({ layersOpen, onLayers, onReport, onTeam, onHelp }: {
  layersOpen: boolean; onLayers: () => void; onReport: () => void; onTeam: () => void; onHelp: () => void;
}) {
  const button = 'inline-flex min-h-11 items-center justify-center gap-2 rounded-lg px-3 text-sm font-semibold text-slate-900 hover:bg-lime-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900';
  return <nav aria-label="Project tools" className="flex flex-wrap gap-1 rounded-xl border border-slate-300 bg-white/95 p-1 shadow-lg backdrop-blur-sm">
    <button type="button" className={button} onClick={onLayers} aria-expanded={layersOpen}><Layers size={17} /> Layers</button>
    <button type="button" className={button} onClick={onReport}><FileText size={17} /> Report</button>
    <button type="button" className={button} onClick={onTeam}><Users size={17} /> Team</button>
    <button type="button" className={button} onClick={onHelp}><HelpCircle size={17} /> Help</button>
  </nav>;
}

export function StudioSaveStatus({ saving, draftCount, loadError, onRetry, onReload, draftsPersistOnDevice = true, discardableCount = 0, onDiscardRejected, saveError }: {
  saving: boolean; draftCount: number; loadError: boolean; onRetry: () => void; onReload: () => void; draftsPersistOnDevice?: boolean;
  discardableCount?: number; onDiscardRejected?: () => void; saveError?: string | null;
}) {
  if (loadError) return <div role="alert" className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
    Saved drawings could not load. Your project may contain more work.
    <button onClick={onReload} className="mt-2 flex min-h-11 items-center gap-2 font-semibold underline"><RotateCw size={16} /> Try loading again</button>
  </div>;
  if (saving) return <p role="status" className="flex items-center gap-2 px-1 py-2 text-sm text-slate-700"><Loader2 size={15} className="animate-spin" /> Saving your drawings…</p>;
  if (draftCount) return <div role="status" className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
    {draftCount} {draftCount === 1 ? 'drawing is' : 'drawings are'} {draftsPersistOnDevice
      ? 'kept on this device and waiting to save.' : 'kept in this tab only. Keep the tab open and save again.'}
    <button onClick={onRetry} className="mt-2 flex min-h-11 items-center gap-2 font-semibold underline"><RotateCw size={16} /> Save again</button>
    {discardableCount > 0 && <button onClick={onDiscardRejected} className="mt-1 flex min-h-11 items-center font-semibold underline">
      Discard {discardableCount === 1 ? 'rejected drawing' : `${discardableCount} rejected drawings`}
    </button>}
  </div>;
  if (saveError) return <div role="alert" className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
    {saveError}<button onClick={onReload} className="mt-2 flex min-h-11 items-center gap-2 font-semibold underline"><RotateCw size={16} /> Reload saved version</button>
  </div>;
  return <p role="status" className="flex items-center gap-2 px-1 py-2 text-sm text-slate-700"><Check size={15} /> Drawings saved</p>;
}

export function StudioDialog({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  const panel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const element = panel.current;
    element?.focus();
    const keyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); onClose(); }
      if (event.key !== 'Tab' || !element) return;
      const nodes = [...element.querySelectorAll<HTMLElement>('button:not([disabled]),a[href],input:not([disabled]),textarea:not([disabled]),select:not([disabled]),[tabindex="0"]')]
        .filter((node) => node.getClientRects().length > 0);
      const first = nodes[0]; const last = nodes[nodes.length - 1];
      if (!first) { event.preventDefault(); return; }
      if (event.shiftKey && (document.activeElement === first || document.activeElement === element)) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && (document.activeElement === last || document.activeElement === element)) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener('keydown', keyDown, true);
    return () => { document.removeEventListener('keydown', keyDown, true); previous?.focus(); };
  }, [onClose]);
  return createPortal(<div className="fixed inset-0 z-[220] flex items-center justify-center bg-slate-950/60 p-3 backdrop-blur-sm sm:p-6" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <div ref={panel} tabIndex={-1} role="dialog" aria-modal="true" aria-label={title} className="max-h-[94dvh] w-full max-w-5xl overflow-y-auto rounded-2xl bg-white shadow-2xl outline-none">
      <header className="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-3">
        <h1 className="text-lg font-semibold text-slate-900">{title}</h1>
        <button onClick={onClose} aria-label={`Close ${title.toLowerCase()}`} className="flex h-11 w-11 items-center justify-center rounded-lg text-slate-700 hover:bg-slate-100"><X size={22} /></button>
      </header>
      <div className="p-3 sm:p-6">{children}</div>
    </div>
  </div>, document.body);
}
