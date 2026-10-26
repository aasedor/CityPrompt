import { Signpost } from 'lucide-react';
import { useId } from 'react';
import type { StreetNamesState } from './useStreetNames';

export function StreetNamesControl({ state }: { state: StreetNamesState }) {
  const description=useId();
  return <div className="rounded-xl border border-slate-900/15 bg-[#fff9ed] px-3 py-2.5">
    <label className="flex min-h-11 cursor-pointer items-center gap-2.5 text-sm font-semibold">
      <Signpost size={19} aria-hidden className="shrink-0 text-slate-700" />
      <span className="flex-1">Street names</span>
      <span className="relative inline-flex h-6 w-11 shrink-0">
        <input type="checkbox" role="switch" aria-describedby={description} checked={state.enabled}
          onChange={event=>state.setEnabled(event.target.checked)}
          className="peer absolute inset-0 z-10 h-full w-full cursor-pointer opacity-0" />
        <span aria-hidden className="absolute inset-0 rounded-full border border-slate-900 bg-slate-200 transition-colors peer-checked:bg-[#c9ff3d] peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-cyan-700" />
        <span aria-hidden className="absolute left-1 top-1 h-4 w-4 rounded-full bg-slate-900 transition-transform peer-checked:translate-x-5 motion-reduce:transition-none" />
      </span>
    </label>
    <p id={description} className="mt-0.5 text-[11px] leading-relaxed text-slate-600">Find your bearings. Labels stay out of renders.</p>
    {state.enabled && <div className="mt-2 text-[11px] leading-relaxed text-slate-600">
      {state.problem ? <p role="status">{state.problem}</p> : state.loading ? <p role="status">Loading street names…</p>
        : state.error && !state.data?.length ? <p role="status">Street names could not load. <button type="button" onClick={state.retry} className="min-h-8 font-semibold underline">Try again</button></p>
        : <p role="status">{state.data?.length ? 'Street names · City of Calgary' : 'No named streets found nearby.'}</p>}
    </div>}
  </div>;
}
