import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import type { StreetAsset } from './assetRegistry';

/** Uses the rendered surface bands, never an AI diagram or a second width table. */
export function StreetCrossSection({ asset, expanded = false }: { asset: StreetAsset; expanded?: boolean }) {
  const profile = resolvePilotStreetSectionProfile({ properties: asset.properties });
  if (!profile) return null;
  const scale = 280 / profile.rowM;
  const format = (n: number) => Number(n.toFixed(2));
  return <details open={expanded || undefined} className="my-2 rounded-lg border border-slate-300 bg-white text-slate-900">
    <summary className="min-h-11 cursor-pointer px-2 py-3 text-xs font-semibold">Cross-section · {format(profile.rowM)} m total</summary>
    <div className="space-y-2 px-2 pb-3">
      <svg role="img" aria-label={`${asset.label}: ${format(profile.rowM)} metre cross-section`} viewBox="0 0 300 94" className="w-full">
        <title>{profile.bands.map(b => `${b.label} ${format(b.widthM)} m`).join(' · ')}</title>
        <path d="M10 12 V24 M10 18 H290 M290 12 V24" fill="none" stroke="#334155" />
        <text x="150" y="12" textAnchor="middle" fontSize="10" fill="#0f172a">{format(profile.rowM)} m total width</text>
        {profile.bands.map((band, index) => {
          const x = 10 + (band.startM + profile.rowM / 2) * scale;
          const y = ['sidewalk', 'planting'].includes(band.kind) ? 42 : 49;
          return <g key={index}>
            <rect x={x} y={y} width={band.widthM * scale} height={70 - y} fill={band.color} stroke="#334155" strokeWidth="0.5" />
            <text x={x + band.widthM * scale / 2} y="84" textAnchor="middle" fontSize="9" fill="#0f172a">{index + 1}</text>
          </g>;
        })}
      </svg>
      <ol className="space-y-1 text-xs">
        {profile.bands.map((band, index) => <li key={index} className="flex items-start justify-between gap-2">
          <span>{index + 1}. {band.label}</span><span className="shrink-0 font-semibold">{format(band.widthM)} m</span>
        </li>)}
      </ol>
      <p className="text-[11px] text-slate-600">Widths to scale; heights schematic. Section viewed toward the first route point.</p>
      <p className="text-[11px] text-slate-600">{String(asset.properties.road_standard_citation)}. {asset.calgaryGuide.basis === 'draft_manual' ? 'Draft reference, not an approved construction standard.' : 'Teaching design, not a City standard.'}</p>
    </div>
  </details>;
}
