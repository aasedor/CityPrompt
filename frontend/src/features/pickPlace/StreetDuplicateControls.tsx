import { useState } from 'react';

export function StreetDuplicateControls({ disabled, width, onDuplicate }: {
  disabled: boolean; width: number; onDuplicate: (eastM: number, northM: number) => Promise<void>;
}) {
  const [open, setOpen] = useState(false);
  const [east, setEast] = useState(String(width + 8));
  const [north, setNorth] = useState('0');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const busy = disabled || pending;
  if (!open) return <button disabled={busy} className="mt-3 min-h-11 w-full rounded-lg border border-slate-700 bg-white text-sm font-semibold" onClick={() => setOpen(true)}>Duplicate street</button>;
  return <section aria-label="Duplicate street" className="my-3 rounded-lg border border-slate-300 p-2 text-sm">
    <p>Copy the complete route and any stops. Choose its offset in metres. Negative values move west or south.</p>
    <label className="mt-2 block">East offset (m)<input type="number" value={east} disabled={busy} onChange={e => setEast(e.target.value)} className="min-h-11 w-full rounded border bg-white px-2" /></label>
    <label className="mt-2 block">North offset (m)<input type="number" value={north} disabled={busy} onChange={e => setNorth(e.target.value)} className="min-h-11 w-full rounded border bg-white px-2" /></label>
    {error && <p role="alert" className="my-2 text-red-800">{error}</p>}
    <div className="mt-2 flex gap-3"><button disabled={busy || !east.trim() || !north.trim()} className="min-h-11 rounded border border-slate-700 bg-white px-2" onClick={async () => {
      setPending(true); setError(null);
      try { await onDuplicate(Number(east), Number(north)); setOpen(false); }
      catch (problem) { setError(problem instanceof Error ? problem.message : 'The copy could not be saved. Check the save status before trying again.'); }
      finally { setPending(false); }
    }}>{pending ? 'Saving copy…' : 'Create copy'}</button>
      <button disabled={busy} className="min-h-11 underline" onClick={() => { setOpen(false); setError(null); }}>Cancel copy</button></div>
  </section>;
}
