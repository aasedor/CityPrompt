import { STYLES, STYLE_GROUPS } from './imageStyles';
import { resolveDirect3DPresentationMode } from './useDirect3DRender';

/** All established styles remain primary creative choices. */
export function ImagePresentationControls({ style, onStyle, addPeople, addVehicles, onPeople, onVehicles, isStyleDisabled, styleHint }: {
  style: string; onStyle: (style: string) => void;
  addPeople: boolean; addVehicles: boolean;
  onPeople: (value: boolean) => void; onVehicles: (value: boolean) => void;
  isStyleDisabled?: (style: string) => boolean;
  styleHint?: (style: string) => string | undefined;
}) {
  return <section aria-label="Image presentation" className="space-y-3 bg-slate-900/90 px-4 py-3 text-white">
    <h4 className="text-sm font-bold">Choose a style</h4>
    <div className="space-y-3">
      {STYLE_GROUPS.map(group => <fieldset key={group.label}>
        <legend className="mb-1 text-xs font-bold text-slate-200">{group.label}</legend>
        <div className="flex flex-wrap gap-2">
          {group.ids.map(id => {
            const option = STYLES.find(item => item.id === id)!;
            return <button key={id} type="button" aria-pressed={style === id}
              disabled={isStyleDisabled?.(id)} title={styleHint?.(id)} onClick={() => onStyle(id)}
              className={`min-h-11 rounded-lg border px-3 text-sm font-bold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-lime-300 disabled:cursor-not-allowed disabled:opacity-40 ${style === id ? 'border-lime-300 bg-lime-300 text-slate-950' : 'border-slate-400 bg-slate-800 hover:bg-slate-700'}`}>
              {option.label}
            </button>;
          })}
        </div>
      </fieldset>)}
    </div>
    <div className="flex flex-wrap gap-x-6">
      <label className="flex min-h-11 cursor-pointer items-center gap-2 text-sm"><input className="h-5 w-5 accent-lime-300" type="checkbox" checked={addPeople} onChange={event => onPeople(event.target.checked)} />Add People</label>
      <label className="flex min-h-11 cursor-pointer items-center gap-2 text-sm"><input className="h-5 w-5 accent-lime-300" type="checkbox" checked={addVehicles} onChange={event => onVehicles(event.target.checked)} />Add Vehicles</label>
    </div>
    <p className="text-xs text-slate-200">{resolveDirect3DPresentationMode(style) === 'reproject'
      ? 'This style creates a different projection of your design. Compare its layout with your original before presenting it.'
      : 'Your current view and design guide the image. Review the result against the original before presenting it.'}</p>
  </section>;
}
