import { useEffect, useRef, useState } from 'react';
import { buildingsApi, type BuildingReferenceCandidate } from '@/services/api';

interface Props {
  buildingId: string;
  selected: BuildingReferenceCandidate[];
  onChange: (value: BuildingReferenceCandidate[]) => void;
  capacity: number;
  disabled: boolean;
}

export function BuildingReferenceSearch({ buildingId, selected, onChange, capacity, disabled }: Props) {
  const [query, setQuery] = useState('');
  const [view, setView] = useState('all');
  const [results, setResults] = useState<BuildingReferenceCandidate[]>([]);
  const [busy, setBusy] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const request = useRef(0);
  useEffect(() => () => { request.current += 1; }, [buildingId]);

  const search = async () => {
    const current = ++request.current;
    setBusy(true);
    setError(null);
    try {
      const response = await buildingsApi.searchPhotoReferences(buildingId, query.trim(), view);
      if (request.current !== current) return;
      setResults(response.candidates);
      setSearched(true);
    } catch {
      if (request.current === current) setError('Image search is unavailable. Try again or upload your own photos.');
    } finally {
      if (request.current === current) setBusy(false);
    }
  };
  const displayed = [...selected, ...results.filter((item) => !selected.some((choice) => choice.id === item.id))];

  return (
    <details className="mt-4 rounded-lg border border-primary-950/15 bg-white p-3">
      <summary className="cursor-pointer text-sm font-semibold text-primary-950">Find more views online (optional)</summary>
      <p className="mt-2 text-xs text-primary-950/65">Search Wikimedia Commons by building name. Choose clear photos of this exact building from different angles. Search costs no City Prompt tokens.</p>
      <label htmlFor="building-reference-query" className="mt-2 block text-xs font-semibold">Building name</label>
      <input id="building-reference-query" value={query} maxLength={160} onChange={(event) => setQuery(event.target.value)}
        placeholder="Walt Disney Concert Hall" disabled={disabled}
        className="mt-1 w-full rounded border border-primary-950/20 p-2 text-sm" />
      <div className="mt-2 flex gap-2">
        <select aria-label="Reference viewing angle" value={view} onChange={(event) => setView(event.target.value)} disabled={disabled}
          className="min-w-0 flex-1 rounded border border-primary-950/20 p-2 text-sm">
          <option value="all">All views</option><option value="exterior">Exterior</option>
          <option value="aerial">Aerial / roof</option><option value="rear">Rear</option><option value="side">Side</option>
        </select>
        <button type="button" onClick={search} disabled={disabled || busy || query.trim().length < 3}
          className="rounded bg-primary-950 px-3 py-2 text-sm text-white disabled:opacity-50">{busy ? 'Searching…' : 'Find views'}</button>
      </div>
      {error && <p role="alert" className="mt-2 text-xs text-red-700">{error}</p>}
      {searched && results.length === 0 && <p role="status" className="mt-2 text-xs">No usable photos found. Try the building name without the city, choose All views, or upload photos.</p>}
      {displayed.length > 0 && <>
        <p className="my-2 text-xs text-primary-950/70">{selected.length} web photos selected. Up to {capacity} available with your uploads. Selecting a photo confirms it shows the same building; search matches can be wrong.</p>
        <div className="grid max-h-80 grid-cols-2 gap-3 overflow-y-auto">
          {displayed.map((item) => {
            const checked = selected.some((choice) => choice.id === item.id);
            return <div key={item.id} className="rounded border border-primary-950/15 p-2">
              <label className="block cursor-pointer text-xs">
                <img src={item.image_url} alt={item.title} loading="lazy" referrerPolicy="no-referrer" className="h-28 w-full rounded object-contain" />
                <span className="mt-1 flex items-start gap-1">
                  <input type="checkbox" checked={checked} disabled={disabled || (!checked && selected.length >= capacity)}
                    onChange={() => onChange(checked ? selected.filter((choice) => choice.id !== item.id) : [...selected, item])} />
                  Use {item.title}
                </span>
              </label>
              <p className="mt-1 line-clamp-2 text-[10px] text-primary-950/60">{item.author} · {item.license}</p>
              <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="text-xs underline">View source and licence</a>
            </div>;
          })}
        </div>
      </>}
    </details>
  );
}
