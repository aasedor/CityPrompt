import { useMemo, useState } from 'react';
import type { SiteZone } from '@/types';
import { StudioDialog } from '@/features/projects/StudioControls';
import { describeGround, validPreparedLevel } from './groundReview';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import { groundReadinessMessage } from './sharedGroundCapture';
import { measurePreparedEdges, preparedEdgeSummary, readPreparedEdges, supportsPreparedEdges, type PreparedEdgeProfile } from './preparedSiteEdges';
import { measureParkTerrain, type ParkTerrainProfile } from './parkTerrain';
import { isNeighborhoodParkPilot } from './neighborhoodParkLayout';

export function GroundReviewPanel({ boundary, ground, onClose, onApply, parks = [], onFollowParks }: {
  boundary: SiteZone; ground: SharedSiteGroundState; onClose: () => void;
  onApply: (clear: boolean, height?: number, edges?: PreparedEdgeProfile | null) => Promise<void>;
  parks?: SiteZone[]; onFollowParks?: (profiles: Record<string, ParkTerrainProfile>) => Promise<void>;
}) {
  const [level, setLevel] = useState(String(boundary.properties?.terrain_elevation_m ?? ''));
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const savedEdges = useMemo(() => readPreparedEdges(boundary), [boundary]);
  const measuredEdges = useMemo(() => measurePreparedEdges(boundary, ground.review), [boundary, ground.review]);
  const edges = measuredEdges ?? savedEdges;
  const [includeEdges, setIncludeEdges] = useState(Boolean(savedEdges));
  const edgeSummary = edges && level.trim() !== '' && validPreparedLevel(Number(level)) ? preparedEdgeSummary(edges, Number(level)) : null;
  const review = ground.review, summary = review ? describeGround(review) : null;
  const parkProfiles = useMemo(() => Object.fromEntries(parks.filter(isNeighborhoodParkPilot).flatMap(park => {
    const profile = measureParkTerrain(park, ground.review); return profile ? [[park.id, profile]] : [];
  })), [parks, ground.review]);
  const apply = async (clear: boolean) => {
    setPending(true); setError('');
    if (clear && (level.trim() === '' || !validPreparedLevel(Number(level)) || (includeEdges && !edges))) { setPending(false); return; }
    try { await onApply(clear, clear ? Number(level) : undefined, clear ? includeEdges ? edges : null : undefined); onClose(); }
    catch { setError('Saving ground settings could not be confirmed. Reload the project to check its current level before trying again.'); }
    finally { setPending(false); }
  };
  return <StudioDialog title="Review site ground" onClose={onClose}>
    <div className="max-h-[70dvh] space-y-4 overflow-auto p-1 text-sm text-slate-900">
      <p>{boundary.properties?.terrain_strategy === 'landscape' ? 'This site retains its hillside. Review the original surface here to update a park after moving or resizing it.' : ground.status === 'ready' ? 'The visible surface is consistent. Check that the samples are on ground rather than roofs or trees.' : ground.status === 'inactive' ? 'This site uses a prepared level. Reviewing its original surface does not change your design.' : groundReadinessMessage(ground)}</p>
      {ground.inspectionStatus === 'sampling' && <p role="status">Measuring the original surface… Keep the site in view.</p>}
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
      {parks.length > 0 && onFollowParks && <section className="space-y-2 rounded-lg border border-green-700 bg-green-50 p-3">
        <h2 className="font-semibold">Let parks follow the hillside</h2>
        <p>Keep the existing site terrain. Drape the neighbourhood park's lawn and paths over its own measured surface; only activity pads stay level. Existing building terraces keep their saved level.</p>
        <p>{Object.keys(parkProfiles).length} of {parks.length} parks have repeatable measurements. Review that the park is on open ground, not tree crowns or roofs. Steep landscape is allowed; path grades still need design.</p>
        <button className="min-h-11 rounded-lg bg-lime-200 p-2 disabled:opacity-40" disabled={pending || Object.keys(parkProfiles).length !== parks.length} onClick={async () => {
          setPending(true); setError('');
          try { await onFollowParks(parkProfiles); onClose(); }
          catch { setError('Could not finish saving the terrain settings. Reopen this review to check and retry.'); }
          finally { setPending(false); }
        }}>Use measured park terrain</button>
        <p className="text-xs">This pilot supports neighbourhood parks. Moving or resizing a park requires another ground review; its measured slope will never be stretched to a new location.</p>
      </section>}
      <button disabled={pending} className="min-h-11 rounded-lg border p-2" onClick={() => void apply(false)}>Follow existing terrain</button>
      <fieldset className="space-y-2 rounded-lg border p-3" disabled={pending}>
        <legend className="font-semibold">Prepare a level redevelopment surface</legend>
        <label className="block">Proposed level (m, WGS84 ellipsoid)
          <input type="number" step="0.1" min="-1000" max="10000" value={level} onChange={event => setLevel(event.target.value)} className="ml-2 min-h-11 w-36 rounded border p-2" />
        </label>
        {summary?.min !== null && summary?.max !== null && summary && level !== '' && validPreparedLevel(Number(level)) &&
          <p>Compared with the visible samples, this level is {(Number(level) - summary.min).toFixed(1)} m above the lowest and {(summary.max - Number(level)).toFixed(1)} m below the highest. Roof and tree samples can exaggerate these differences.</p>}
        <p>Applying this replaces existing tiles inside the boundary. Objects without their own saved ground use this common level; measured parks keep their slope. Inspect the site edges afterward.</p>
        <label className="flex min-h-11 items-center gap-2"><input type="checkbox" checked={includeEdges} disabled={!edges && !includeEdges} onChange={event => setIncludeEdges(event.target.checked)} />Add retaining edges · slope pilot</label>
        <p className="text-xs">Connect the level surface to measured heights around its boundary. These are concept retaining faces, not engineered walls or accessible entrances. Review trees, roofs and nearby paths before applying.</p>
        {!edges && <p role="status" className="text-xs">{supportsPreparedEdges(boundary)
          ? 'Retaining edges need two repeatable measurements around the whole boundary. Keep the site in view while it loads, or reopen this review to retry. You can still apply a level surface without edges.'
          : 'This boundary is too large or detailed for the retaining-edge pilot. Use a smaller site or apply a level surface without edges.'}</p>}
        {Boolean(boundary.properties?.terrain_edge_profile) && !savedEdges && <p className="text-xs text-amber-800">The site outline changed. Its old retaining edges have been hidden; remeasure and apply to rebuild them.</p>}
        {edgeSummary && <p className="rounded bg-slate-100 p-2">At the boundary: up to {edgeSummary.maximumFill.toFixed(1)} m of fill and {edgeSummary.maximumCut.toFixed(1)} m of cut relative to the visible surface.{!measuredEdges && savedEdges ? ' Using saved edge measurements.' : ''}</p>}
        <button disabled={level.trim() === '' || !validPreparedLevel(Number(level)) || (includeEdges && !edges)} className="min-h-11 rounded-lg bg-lime-200 p-2 disabled:opacity-40" onClick={() => void apply(true)}>Apply redevelopment level</button>
      </fieldset>
      {error && <p role="alert">{error}</p>}
    </div>
  </StudioDialog>;
}
