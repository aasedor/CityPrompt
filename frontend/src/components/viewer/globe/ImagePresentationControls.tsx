/** Curated names reuse the existing same-camera finishing styles. */
export const IMAGE_PRESENTATION_PRESETS = [
  { id: 'photorealistic', label: 'Realistic' },
  { id: 'atmospheric', label: 'Golden hour' },
  { id: 'documentary', label: 'Overcast' },
  { id: 'winter', label: 'Winter' },
  { id: 'watercolour', label: 'Illustration' },
] as const;

export function ImagePresentationControls({ style, onStyle, addPeople, addVehicles, onPeople, onVehicles }: {
  style: string; onStyle: (style: string) => void;
  addPeople: boolean; addVehicles: boolean;
  onPeople: (value: boolean) => void; onVehicles: (value: boolean) => void;
}) {
  return <section aria-label="Image presentation" className="space-y-3 bg-slate-900/90 px-4 py-3 text-white">
    <fieldset>
      <legend className="mb-2 text-sm font-bold">Choose a look</legend>
      <div className="flex flex-wrap gap-2">
        {IMAGE_PRESENTATION_PRESETS.map(preset => <button key={preset.id} type="button" aria-pressed={style === preset.id}
          onClick={() => onStyle(preset.id)}
          className={`min-h-11 rounded-lg border px-3 text-sm font-bold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-lime-300 ${style === preset.id ? 'border-lime-300 bg-lime-300 text-slate-950' : 'border-slate-400 bg-slate-800 hover:bg-slate-700'}`}>
          {preset.label}
        </button>)}
      </div>
      {!IMAGE_PRESENTATION_PRESETS.some(preset => preset.id === style) && <p className="mt-2 text-sm">An advanced style is selected. Choose a look above to return to a current-view preset.</p>}
    </fieldset>
    <div className="flex flex-wrap gap-x-6">
      <label className="flex min-h-11 cursor-pointer items-center gap-2 text-sm"><input className="h-5 w-5 accent-lime-300" type="checkbox" checked={addPeople} onChange={event => onPeople(event.target.checked)} />Add People</label>
      <label className="flex min-h-11 cursor-pointer items-center gap-2 text-sm"><input className="h-5 w-5 accent-lime-300" type="checkbox" checked={addVehicles} onChange={event => onVehicles(event.target.checked)} />Add Vehicles</label>
    </div>
    <p className="text-xs text-slate-200">Your current view and design guide the image. Review the result against the original before presenting it.</p>
  </section>;
}
