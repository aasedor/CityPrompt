import { useEffect, useState, useSyncExternalStore } from 'react';
import { Building2 } from 'lucide-react';
import { getAssetTicketRevision, modelLibraryApi, resolveApiFileUrl, subscribeAssetTicketChanges, type UserGeneratedBuilding } from '@/services/api';
import { useAuthStore } from '@/store';

export function UserGeneratedBuildings({ query, onPick }: { query: string; onPick: (model: UserGeneratedBuilding) => void }) {
  const userId = useAuthStore(state => state.user?.id);
  const [models, setModels] = useState<UserGeneratedBuilding[]>([]);
  const [status, setStatus] = useState<'loading' | 'ready' | 'failed'>('loading');
  const [attempt, setAttempt] = useState(0);
  useSyncExternalStore(subscribeAssetTicketChanges, getAssetTicketRevision, getAssetTicketRevision);
  useEffect(() => {
    let cancelled = false;
    setModels([]); setStatus('loading');
    modelLibraryApi.userGenerated().then(items => {
      if (!cancelled) { setModels(items); setStatus('ready'); }
    }).catch(() => { if (!cancelled) setStatus('failed'); });
    return () => { cancelled = true; };
  }, [userId, attempt]);
  if (status === 'loading') return <p role="status" className="p-4 text-sm">Loading your generated buildings…</p>;
  if (status === 'failed') return <div role="alert" className="p-4 text-sm">Your models could not be loaded.
    <button className="ml-2 min-h-11 underline" onClick={() => setAttempt(value => value + 1)}>Try again</button></div>;
  const matches = models.filter(model => model.name.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()));
  return <div>
    <p className="mb-3 text-sm text-slate-600">Completed AI models from your projects. Reusing a model costs no generation credits.</p>
    {!models.length ? <p className="p-4 text-sm">No user generated buildings yet. Draw a building footprint, then use Generate 3D and upload your photos. Completed models appear here.</p>
      : !matches.length ? <p className="p-4 text-sm">No generated buildings match your search.</p>
      : <div className="grid items-start gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {matches.map(model => <article key={model.id} className="overflow-hidden rounded-xl border border-slate-300 bg-white">
          <button onClick={() => onPick(model)} className="w-full text-left hover:bg-lime-50">
            <GeneratedPreview source={model.preview_url ? resolveApiFileUrl(model.preview_url) : null} />
            <div className="space-y-2 p-3">
              <h3 className="font-bold">{model.name}</h3>
              <p className="text-xs text-slate-600">User generated · AI concept model{model.floor_count ? ` · ${model.floor_count} storeys` : ''}</p>
              <p className="min-h-11 rounded-lg bg-[#c9ff3d] px-3 py-3 text-center text-sm font-bold">Choose & draw footprint</p>
            </div>
          </button>
          <a className="block px-3 pb-3 text-xs underline" href={`/projects/${model.project_id}`}>Open original project</a>
        </article>)}
      </div>}
  </div>;
}

function GeneratedPreview({ source }: { source: string | null }) {
  const [failed, setFailed] = useState<string | null>(null);
  return <div className="relative flex aspect-video items-center justify-center bg-slate-100 text-slate-500">
    {source && failed !== source ? <img className="h-full w-full object-cover" src={source} alt="Building reference" loading="lazy" onError={() => setFailed(source)} />
      : <Building2 size={40} aria-label="Generated building" />}
    {source && failed !== source && <span className="absolute bottom-1 left-1 rounded bg-white/90 px-1 text-[10px]">Reference image</span>}
  </div>;
}
