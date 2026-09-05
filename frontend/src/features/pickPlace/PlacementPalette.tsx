import { PLACE_ASSETS, type PlaceAssetId } from './catalogue';

export function PlacementPalette({ selected, onPick, onCancel, status, message, onRetry }: {
  selected: PlaceAssetId | null; onPick: (id: PlaceAssetId) => void; onCancel: () => void;
  status: string; message: string; onRetry: () => void;
}) {
  return <section aria-label="Place 3D objects" className="space-y-2">
    <div><p className="font-bold text-slate-900">Pick, place & reshape</p>
      <p className="text-xs text-slate-600">Choose an object, then click an empty space.</p></div>
    {PLACE_ASSETS.map(asset => <button key={asset.id} data-tour={`place-${asset.id}`} aria-pressed={selected===asset.id}
      onClick={() => onPick(asset.id)} className={`flex w-full items-center gap-2 rounded-lg border-2 border-slate-900 p-2 text-left ${selected===asset.id?'bg-[#c9ff3d]':'bg-white hover:bg-lime-50'}`}>
      <img src={asset.thumbnail} alt="" className="h-16 w-16 rounded object-cover" />
      <span><span className="block text-sm font-bold text-slate-900">{asset.label}</span>
        <span className="block text-xs text-slate-600">{asset.description}</span></span>
    </button>)}
    {selected && <button onClick={onCancel} className="min-h-11 w-full rounded-lg border border-slate-500 bg-white text-sm text-slate-900">Cancel placement · Esc</button>}
    <div role="status" aria-live="polite" className={`rounded-lg px-2 py-2 text-xs ${status==='error'?'bg-amber-50 text-amber-950':'bg-emerald-50 text-emerald-950'}`}>
      <p className="font-semibold">{status==='updating'?'Updating 3D…':status==='error'?'3D update needs attention':status==='ready'?'3D saved':'3D appears automatically'}</p>
      {message && <p className="mt-1">{message}</p>}
      {status==='error' && <button onClick={onRetry} className="mt-1 min-h-11 underline">Retry 3D update</button>}
    </div>
  </section>;
}
