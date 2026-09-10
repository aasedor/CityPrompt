import { OPENAI_IMAGE_MODELS, type ImageModelChoice, type ImageModelAvailability } from '@/config/imageModels';

export function ImageModelSelect({ value, onChange, disabled = false, availability }: {
  value: ImageModelChoice;
  onChange: (value: ImageModelChoice) => void;
  disabled?: boolean;
  availability: ImageModelAvailability | null;
}) {
  const unavailable = (id: string) => availability?.models.some((model) => model.id === id && model.available === false) ?? false;
  const batchUnavailable = unavailable('gpt-image-2') || unavailable('gpt-image-2.5-flare') || unavailable('gpt-image-2.5-sunburst');
  return (
    <div>
      <label className="flex flex-wrap items-center gap-2 text-xs font-semibold">
        Image engine
        <select
          value={value}
          onChange={(event) => onChange(event.target.value as ImageModelChoice)}
          disabled={disabled}
          className="min-h-9 max-w-full rounded-lg border border-slate-400 bg-white py-1 pl-2 pr-8 text-slate-900 disabled:opacity-60"
        >
          <option value="compare-all-three" disabled={batchUnavailable}>GPT Image 2 + Flare + Sunburst · 3 images{batchUnavailable ? ' · Awaiting access' : ''}</option>
          {OPENAI_IMAGE_MODELS.map((model) => (
            <option key={model.id} value={model.id} disabled={unavailable(model.id)}>{model.option}{unavailable(model.id) ? ' · Awaiting access' : ''}</option>
          ))}
        </select>
      </label>
      <p className="mt-1 text-[10px] opacity-75">
        {value === 'compare-all-three'
          ? 'Three image calls, billed separately. Same source view: GPT Image 2, Flare, then Sunburst. Each result is saved.'
          : batchUnavailable ? 'This account does not yet list all three engines. Choose an available engine.' : 'One image call. Your 3D scene keeps the same geometry controls.'}
      </p>
    </div>
  );
}
