import type { ContextView } from './contextProvider';
import type { ReactNode } from 'react';

export function ContextControls({ requested, onChange, loading, failed, children }: {
  requested: ContextView; onChange: (view: ContextView) => void; loading: boolean; failed: boolean; children?: ReactNode;
}) {
  return <div className="absolute bottom-16 right-4 z-30 max-w-xs rounded-xl border border-slate-700 bg-white p-3 text-sm text-slate-900 shadow-lg">
    <label className="flex items-center gap-2 font-semibold">Context
      <select className="min-h-11 rounded border border-slate-500 pl-2 pr-8" value={requested} onChange={event => onChange(event.target.value as ContextView)}>
        <option value="google">Google 3D</option><option value="capture">Sample capture</option><option value="terrain">Terrain</option>
      </select>
    </label>
    <p className="mt-1 text-xs">Development sample with an artificial location.</p>
    {loading && <p role="status" className="mt-2">Loading capture… Your design stays in place.</p>}
    {failed && <p role="status" className="mt-2">The capture could not load. Google context is still shown. Choose Google 3D, then Sample capture to retry.</p>}
    {children}
  </div>;
}
