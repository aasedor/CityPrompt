import { useState, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { StudioDialog } from '@/features/projects/StudioControls';

export function StudyEditorShell({ globe, onClose, children }: { globe: boolean; onClose: () => void; children: ReactNode }) {
  const [minimised, setMinimised] = useState(false);
  if (!globe) return <StudioDialog title="Zoning map studio" onClose={onClose}>{children}</StudioDialog>;
  return createPortal(<section aria-label="Land-use drawing studio" className={`fixed right-3 z-[210] w-[min(360px,calc(100vw-24px))] overflow-y-auto rounded-2xl border border-stone-300 bg-[#fffdf6]/95 text-stone-900 shadow-xl ${minimised ? 'top-44' : 'bottom-24 top-auto max-h-[48dvh] sm:top-44 sm:max-h-none'}`}>
    <header className="sticky top-0 z-10 flex items-center justify-between gap-1 border-b border-stone-200 bg-[#fffdf6] px-3 py-1">
      <h2 className="text-sm font-bold">Draw land use</h2>
      <button type="button" className="min-h-11 px-2 text-xs underline" onClick={() => setMinimised(!minimised)}>{minimised ? 'Show controls' : 'Minimise'}</button>
      <button type="button" aria-label="Close zoning map studio" className="min-h-11 px-2 text-lg" onClick={onClose}>×</button>
    </header>
    <div hidden={minimised} className="p-3">{children}</div>
  </section>, document.body);
}
