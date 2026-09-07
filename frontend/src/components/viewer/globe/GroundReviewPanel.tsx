import { useState } from 'react';
import type { SiteZone } from '@/types';
import { StudioDialog } from '@/features/projects/StudioControls';
import { describeGround, validPreparedLevel } from './groundReview';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import { groundReadinessMessage } from './sharedGroundCapture';

export function GroundReviewPanel({ boundary, ground, onClose, onApply }: {
  boundary: SiteZone; ground: SharedSiteGroundState; onClose: () => void;
  onApply: (clear: boolean, height?: number) => Promise<void>;
}) {
  const [level, setLevel] = useState(String(boundary.properties?.terrain_elevation_m ?? ''));
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const review = ground.review, summary = review ? describeGround(review) : null;
  const apply = async (clear: boolean) => {
    setPending(true); setError('');
    try { await onApply(clear, clear ? Number(level) : undefined); onClose(); }
    catch { setError('Saving ground settings could not be confirmed. Reload the project to check its current level before trying again.'); }
    finally { setPending(false); }
  };
  return <StudioDialog title="Review site ground" onClose={onClose}>
    <div className="max-h-[70dvh] space-y-4 overflow-auto p-1 text-sm text-slate-900">
      <p>{ground.status === 'ready' ? 'The visible surface is consistent. Check that the samples are on ground rather than roofs or trees.' : ground.status === 'inactive' ? 'This site uses a prepared level. Follow existing terrain to inspect the original surface.' : groundReadinessMessage(ground)}</p>
      {summary && review && <>
        <p>Measured heights: {summary.min?.toFixed(1) ?? 'unknown'}–{summary.max?.toFixed(1) ?? 'unknown'} m. North is up. Red marks abrupt changes; grey cells are missing or outside your boundary. Select a coloured sample to use its height as your proposed level.</p>
        <svg viewBox={`-1 -1 ${review.layout.grid.columns + 1} ${review.layout.grid.rows + 1}`} className="mx-auto h-56 w-full" role="img" aria-label="Measured site elevations, north up">
          {summary.cells.map(cell => <rect key={cell.index} x={cell.index % review.layout.grid.columns} y={review.layout.grid.rows - 1 - Math.floor(cell.index / review.layout.grid.columns)} width="0.9" height="0.9"
            role={cell.inside && cell.height !== null ? 'button' : undefined} tabIndex={cell.inside && cell.height !== null ? 0 : undefined}
            aria-label={`Sample ${cell.index}: ${cell.height?.toFixed(1) ?? 'unknown'} metres${cell.jump ? ', abrupt change' : ''}`}
            onClick={() => { if (cell.inside && cell.height !== null) setLevel(cell.height.toFixed(2)); }}
            onKeyDown={event => { if ((event.key === 'Enter' || event.key === ' ') && cell.inside && cell.height !== null) { event.preventDefault(); setLevel(cell.height.toFixed(2)); } }}
            fill={!cell.inside || cell.height === null ? '#cbd5e1' : cell.jump ? '#dc2626' : `hsl(${120 - 90 * (cell.height - summary.min!) / Math.max(1, summary.max! - summary.min!)} 55% 48%)`}>
            <title>{cell.point.map(p => p.toFixed(6)).join(', ')}: {cell.height?.toFixed(2) ?? 'missing'} m{cell.jump ? ' — abrupt change' : ''}</title>
          </rect>)}
        </svg>
      </>}
      <p className="rounded-lg bg-amber-50 p-3">Google tiles show visible surfaces, including roofs and trees. These heights are not a ground survey. A level redevelopment surface may require cut, fill or retaining edges.</p>
      <button disabled={pending} className="min-h-11 rounded-lg border p-2" onClick={() => void apply(false)}>Follow existing terrain</button>
      <fieldset className="space-y-2 rounded-lg border p-3" disabled={pending}>
        <legend className="font-semibold">Prepare a level redevelopment surface</legend>
        <label className="block">Proposed level (m, WGS84 ellipsoid)
          <input type="number" step="0.1" min="-1000" max="10000" value={level} onChange={event => setLevel(event.target.value)} className="ml-2 min-h-11 w-36 rounded border p-2" />
        </label>
        {summary?.min !== null && summary?.max !== null && summary && level !== '' && validPreparedLevel(Number(level)) &&
          <p>Compared with the visible samples, this level is {(Number(level) - summary.min).toFixed(1)} m above the lowest and {(summary.max - Number(level)).toFixed(1)} m below the highest. Roof and tree samples can exaggerate these differences.</p>}
        <p>Applying this replaces existing tiles inside the boundary. Buildings, parks and streets use this common level. Inspect the site edges afterward.</p>
        <button disabled={level.trim() === '' || !validPreparedLevel(Number(level))} className="min-h-11 rounded-lg bg-lime-200 p-2 disabled:opacity-40" onClick={() => void apply(true)}>Apply redevelopment level</button>
      </fieldset>
      {error && <p role="alert">{error}</p>}
    </div>
  </StudioDialog>;
}
