import { useCallback, useState } from 'react';
import { Upload } from 'lucide-react';
import { StudioDialog } from '@/features/projects/StudioControls';
import { modelLibraryApi, type UserGeneratedBuilding } from '@/services/api';

export function ImportGlbDialog({ projectId, onImported, onClose }: {
  projectId: string; onImported: (model: UserGeneratedBuilding) => void; onClose: () => void;
}) {
  const [file,setFile] = useState<File | null>(null);
  const [name,setName] = useState('');
  const [units,setUnits] = useState('metres');
  const [height,setHeight] = useState('');
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState('');
  const close = useCallback(() => { if (!busy) onClose(); }, [busy,onClose]);
  const choose = (next?: File) => {
    setFile(null); setError('');
    if (!next) return;
    if (!next.name.toLowerCase().endsWith('.glb')) { setError('Choose a .glb building model.'); return; }
    if (next.size > 50*1024*1024) { setError('Choose a GLB smaller than 50 MB.'); return; }
    setFile(next);
  };
  const submit = async () => {
    if (!file || busy) return;
    setBusy(true); setError('');
    try {
      const model = await modelLibraryApi.importGlb(projectId,file,name,units,height.trim() ? Number(height) : undefined);
      onImported(model);
    } catch (cause) {
      const detail = (cause as {response?: {data?: {detail?: unknown}}})?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'The GLB could not be imported. Your file and settings are kept; please try again.');
    } finally { setBusy(false); }
  };
  const field='mt-1 min-h-11 w-full rounded-lg border border-slate-400 bg-white p-2 text-slate-950';
  return <StudioDialog title="Import your building" layout="compact" onClose={close}>
    <form className="space-y-4 text-slate-900" onSubmit={event => { event.preventDefault(); void submit(); }}>
      <p className="text-sm">Upload your building, then click your site to place it.</p>
      <label className="block text-sm font-semibold">GLB building file
        <input className={field} type="file" accept=".glb" disabled={busy} onChange={event => choose(event.target.files?.[0])}/>
      </label>
      <p className="text-xs text-slate-600">Free · .glb files up to 50 MB</p>
      {file && <p className="break-words text-sm"><strong>{file.name}</strong> · {(file.size/1024/1024).toFixed(1)} MB</p>}
      <details className="rounded-lg border border-slate-200 bg-slate-50 p-3">
        <summary className="cursor-pointer text-sm font-semibold">Size &amp; name (optional)</summary>
        <div className="mt-3 space-y-3">
      <label className="block text-sm font-semibold">Building name (optional)
        <input className={field} value={name} maxLength={120} disabled={busy} onChange={event => setName(event.target.value)}/>
      </label>
      <label className="block text-sm font-semibold">Model units
        <select className={field} value={units} disabled={busy} onChange={event => setUnits(event.target.value)}>
          <option value="metres">Metres (standard GLB)</option><option value="centimetres">Centimetres</option>
          <option value="millimetres">Millimetres</option><option value="feet">Feet</option>
        </select>
      </label>
      <label className="block text-sm font-semibold">Building height (m, optional)
        <input className={field} type="number" min="0.25" max="500" step="any" placeholder="Use the file’s size" value={height} disabled={busy} onChange={event => setHeight(event.target.value)}/>
      </label>
      <p className="text-xs text-slate-600">The filename supplies the name and the file supplies the size. Change the units or enter the real height if the size needs adjusting. Proportions stay the same.</p>
        </div>
      </details>
      {error && <p role="alert" className="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-800">{error}</p>}
      {busy && <p role="status" aria-live="polite" className="text-sm">Importing and checking your building…</p>}
      <div className="flex gap-2">
        <button type="button" disabled={busy} onClick={onClose} className="min-h-11 rounded-lg border border-slate-500 px-4">Cancel</button>
        <button type="submit" disabled={!file || busy} className="flex min-h-12 flex-1 items-center justify-center gap-2 rounded-lg border-2 border-slate-900 bg-[#c9ff3d] px-4 font-bold disabled:opacity-50"><Upload size={20} aria-hidden="true"/>{busy?'Uploading…':'Upload'}</button>
      </div>
    </form>
  </StudioDialog>;
}
