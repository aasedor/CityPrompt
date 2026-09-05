import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createPortal } from 'react-dom';
import { Loader2, Upload, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { useQueryClient } from '@tanstack/react-query';
import { getApiErrorMessage } from '@/services/api';
import { referenceLayerQueryKey, referenceLayersApi } from './api';

interface ReferenceImportButtonProps {
  projectId: string;
  onImported?: (centroid: [number, number]) => void;
  className?: string;
  iconSize?: number;
}

export function ReferenceImportButton({ projectId, onImported, className, iconSize = 16 }: ReferenceImportButtonProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const busyRef = useRef(false);
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');
  const [kind, setKind] = useState<'reference' | 'zoning'>('reference');
  const [sourceUrl, setSourceUrl] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!file) return;
    dialogRef.current?.querySelector<HTMLInputElement>('input')?.focus();
    const opener = buttonRef.current;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.stopPropagation();
        if (!busyRef.current) setFile(null);
      }
      if (event.key !== 'Tab') return;
      const elements = [...(dialogRef.current?.querySelectorAll<HTMLElement>('button:not(:disabled), input:not(:disabled), select:not(:disabled)') ?? [])];
      const first = elements[0];
      const last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    window.addEventListener('keydown', onKey, true);
    return () => { window.removeEventListener('keydown', onKey, true); opener?.focus(); };
  }, [file]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file || busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setError('');
    try {
      const layer = await referenceLayersApi.import(projectId, file, { name: name.trim(), kind, source_url: sourceUrl.trim() || undefined });
      await queryClient.invalidateQueries({ queryKey: referenceLayerQueryKey(projectId) });
      onImported?.([(layer.bounds[0] + layer.bounds[2]) / 2, (layer.bounds[1] + layer.bounds[3]) / 2]);
      toast.success(`${layer.name}: ${layer.feature_count.toLocaleString()} reference features ready`);
      setFile(null);
    } catch (cause) {
      setError(getApiErrorMessage(cause, 'Reference import failed. Your file is still selected; you can retry.'));
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  };

  return <>
    <input ref={inputRef} type="file" accept=".zip,.geojson,.json" className="hidden" aria-label="Choose reference dataset" onChange={(event) => {
      const selected = event.target.files?.[0];
      if (selected) {
        if (selected.size > 25 * 1024 * 1024) toast.error('Reference files must be 25 MB or smaller.');
        else { setFile(selected); setName(selected.name.replace(/\.(zip|geojson|json)$/i, '').slice(0, 160)); setSourceUrl(''); setKind('reference'); setError(''); }
      }
      event.target.value = '';
    }} />
    <button ref={buttonRef} type="button" disabled={busy} onClick={() => inputRef.current?.click()}
      title="Import zoning or other context as an optional reference layer"
      className={className ?? 'flex w-full items-center justify-center gap-2 rounded-full border-2 border-[#151515] bg-white px-3 py-2.5 text-sm font-bold hover:bg-slate-50'}>
      {busy ? <Loader2 size={iconSize} className="animate-spin" /> : <Upload size={iconSize} />} {busy ? 'Importing…' : 'Import reference'}
    </button>
    {file && createPortal(<div className="fixed inset-0 z-[10000] flex items-center justify-center bg-black/50 p-4">
      <div ref={dialogRef} role="dialog" aria-modal="true" aria-labelledby="reference-import-title" className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-xl bg-white p-5 text-slate-900 shadow-xl">
        <div className="flex items-center justify-between"><h2 id="reference-import-title" className="text-xl font-bold">Import a reference layer</h2><button type="button" aria-label="Close reference import" disabled={busy} onClick={() => setFile(null)} className="rounded p-2"><X size={20} /></button></div>
        <p className="mt-2 text-sm text-slate-600">Zoning and other datasets stay separate from your design. Show or hide them and inspect their attributes. They never become buildings or prevent a design choice.</p>
        <form onSubmit={(event) => void submit(event)} className="mt-4 space-y-3">
          <p className="break-words text-xs text-slate-500">{file.name} · {(file.size / 1024).toFixed(0)} KB</p>
          <label className="block text-sm font-semibold">Layer name<input required disabled={busy} maxLength={160} value={name} onChange={(event) => setName(event.target.value)} className="mt-1 w-full rounded border border-slate-300 p-2 font-normal" /></label>
          <label className="block text-sm font-semibold">Reference type<select disabled={busy} value={kind} onChange={(event) => setKind(event.target.value as 'reference' | 'zoning')} className="mt-1 w-full rounded border border-slate-300 p-2 font-normal"><option value="reference">General reference</option><option value="zoning">Zoning reference</option></select></label>
          <label className="block text-sm font-semibold">Source link (optional)<input type="url" disabled={busy} maxLength={2048} value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} placeholder="https://city.example/data" className="mt-1 w-full rounded border border-slate-300 p-2 font-normal" /></label>
          <p className="text-xs text-slate-500">GeoJSON uses longitude/latitude. For shapefiles, include .shp, .shx, .dbf and .prj in one ZIP. Up to 2,000 features per layer.</p>
          {error && <p role="alert" className="rounded bg-red-50 p-2 text-sm text-red-800">{error}</p>}
          <div className="flex justify-end gap-2"><button type="button" disabled={busy} onClick={() => setFile(null)} className="rounded border border-slate-300 px-3 py-2">Cancel</button><button type="submit" disabled={busy || !name.trim()} className="rounded bg-slate-900 px-4 py-2 font-semibold text-white disabled:opacity-50">{busy ? 'Importing…' : 'Import reference'}</button></div>
        </form>
      </div>
    </div>, document.body)}
  </>;
}
