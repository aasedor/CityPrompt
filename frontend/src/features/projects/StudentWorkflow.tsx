import { Camera, MapPin, Pencil, Video } from 'lucide-react';
import type { SiteZone } from '@/types';
import { publicRoadConnectionFits } from '@/features/pickPlace/publicRoadConnection';

export type StudentStep = 'site' | 'design' | 'present';

const steps = [
  { id: 'site', label: 'Site', icon: MapPin },
  { id: 'design', label: 'Design', icon: Pencil },
  { id: 'present', label: 'Present', icon: Camera },
] as const;
const action = 'flex min-h-11 w-full items-center justify-center gap-2 rounded-lg border border-slate-900 px-3 py-2 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700';

/** The explicit off-site marker is a proposal, not proof of a real junction. */
export function studentStreetAccessNotice(zones: SiteZone[], boundary: SiteZone | null): string | null {
  const streets = zones.filter(zone => zone.zone_type === 'road');
  if (!streets.length || !boundary) return null;
  if (streets.some(zone => publicRoadConnectionFits(zone, zone.coordinates, boundary))) {
    return 'A public-road connection is proposed. Check that its end meets an existing road on the map before presenting.';
  }
  if (streets.some(zone => zone.properties?.connect_to_public_road === true)) {
    return 'A public-road connection is marked, but its short off-site route is not valid yet. In Design, keep one end inside and drag the other toward the road.';
  }
  return 'No public-road connection is marked for this design. If vehicles need access, select a street in Design and use Connect to a public road.';
}

export function StudentWorkflowNav({ step, onChange }: {
  step: StudentStep; onChange: (step: StudentStep) => void;
}) {
  return <nav aria-label="Community workflow" className="mb-2 grid grid-cols-3 gap-1 rounded-xl border border-slate-900 bg-white p-1 shadow-md">
    {steps.map(({ id, label, icon: Icon }, index) => <button key={id} type="button"
      data-tour={`workflow-${id}`}
      aria-current={step === id ? 'step' : undefined} onClick={() => onChange(id)}
      className={`flex min-h-12 flex-col items-center justify-center rounded-lg px-1 text-xs font-semibold text-slate-950 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700 ${step === id ? 'bg-[#c9ff3d]' : 'hover:bg-slate-100'}`}>
      <span className="flex items-center gap-1"><Icon size={14} aria-hidden />{index + 1}</span>{' '}{label}
    </button>)}
  </nav>;
}

export function StudentStepPanel({ step, hasSite, drawingSite = false, location, canRender, renderReason, streetAccessNotice, onSite, onDesign, onImage, onVideo }: {
  step: 'site' | 'present'; hasSite: boolean; location?: string | null;
  drawingSite?: boolean;
  canRender: boolean; renderReason: string; streetAccessNotice?: string | null;
  onSite: () => void; onDesign: () => void; onImage: () => void; onVideo: () => void;
}) {
  return <section aria-label={step === 'site' ? 'Choose your site' : 'Present your community'}
    className="space-y-3 rounded-xl border border-slate-900 bg-white/95 p-4 text-slate-950 shadow-md">
    {step === 'site' ? <>
      <h2 className="text-base font-bold">Choose your site</h2>
      {location && <p className="text-xs text-slate-600">{location}</p>}
      <p className="text-sm">{hasSite ? 'Your site boundary is saved. Review it, then start building your community.' : 'Draw a boundary around the place you want to design.'}</p>
      {drawingSite && <p role="status" className="rounded-lg bg-lime-50 p-2 text-sm">Click at least three corners. Press Enter or double-click to finish. Esc clears this drawing.</p>}
      <button type="button" className={`${action} bg-white`} onClick={onSite}>{hasSite ? 'Review site boundary' : 'Draw site boundary'}</button>
      <button type="button" className={`${action} bg-[#c9ff3d] disabled:opacity-50`} disabled={!hasSite} onClick={onDesign}>Confirm site & design</button>
    </> : <>
      <h2 className="text-base font-bold">Render this view</h2>
      <p className="text-sm">Move around your community to find your view, then choose an output.</p>
      {streetAccessNotice && <p role="status" className="rounded-lg border border-amber-300 bg-amber-50 p-2 text-xs text-amber-950">{streetAccessNotice}</p>}
      <button type="button" className={`${action} bg-[#c9ff3d] disabled:opacity-50`} disabled={!canRender} onClick={onImage}><Camera size={18} aria-hidden />Image</button>
      <button type="button" className={`${action} bg-white disabled:opacity-50`} disabled={!canRender} onClick={onVideo}><Video size={18} aria-hidden />Video</button>
      {!canRender && <p role="status" className="text-sm text-slate-700">{renderReason}</p>}
      <button type="button" className={`${action} border-transparent underline`} onClick={onDesign}>Back to design</button>
    </>}
  </section>;
}
