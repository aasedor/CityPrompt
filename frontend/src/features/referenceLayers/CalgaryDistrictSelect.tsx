import type { CalgaryDistrict } from './calgaryDistricts';
import { CUSTOM_ZONE } from './calgaryBylaw';

export function CalgaryDistrictSelect({ label, value, choices, disabled, onChange }: {
  label: string; value: string; choices: CalgaryDistrict[]; disabled?: boolean; onChange: (value: string) => void;
}) {
  return <label className="block font-semibold">{label}
    <select aria-label={label} value={value} disabled={disabled} onChange={event => onChange(event.target.value)}
      className="mt-1 min-h-11 w-full rounded-lg border border-stone-300 bg-white px-2 text-sm text-stone-900">
      <option value="" disabled>Select a district</option>
      <option value={CUSTOM_ZONE}>Custom zone — your name and colour</option>
      {choices.map(district => <option key={district.designation} value={district.designation}>
        {district.designation}{district.description ? ` — ${district.description}` : ''}
      </option>)}
    </select>
  </label>;
}
