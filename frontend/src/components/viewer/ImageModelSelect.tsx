import { OPENAI_IMAGE_MODELS, LOCAL_IMAGE_MODELS, isLocalImageModel, type ImageModelChoice, type ImageModelAvailability } from '@/config/imageModels';

export function ImageModelSelect({ value, onChange, disabled = false, availability, allowLocal = true }: {
  value: ImageModelChoice;
  onChange: (value: ImageModelChoice) => void;
  disabled?: boolean;
  availability: ImageModelAvailability | null;
  allowLocal?: boolean;
}) {
  const unavailable = (id: string) => availability?.models.some((model) => model.id === id && model.available === false) ?? false;
  const batchUnavailable = unavailable('gpt-image-2') || unavailable('gpt-image-2.5-flare') || unavailable('gpt-image-2.5-sunburst');
  const allUnavailable = Boolean(availability?.models.length && availability.models.every((model) => model.available === false));
  const unavailableLabel = allUnavailable ? 'Unavailable in this session' : 'Awaiting access';
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
          <option value="compare-all-three" disabled={batchUnavailable}>GPT Image 2 + Flare + Sunburst · 3 images{batchUnavailable ? ` · ${unavailableLabel}` : ''}</option>
          {OPENAI_IMAGE_MODELS.map((model) => (
            <option key={model.id} value={model.id} disabled={unavailable(model.id)}>{model.option}{unavailable(model.id) ? ` · ${unavailableLabel}` : ''}</option>
          ))}
          {allowLocal && import.meta.env.DEV && LOCAL_IMAGE_MODELS.map(model => (
            <option key={model.id} value={model.id} disabled={!availability?.models.some(entry => entry.id === model.id && entry.available === true)}>
              {model.option}{!availability?.models.some(entry => entry.id === model.id && entry.available === true) ? ' · ComfyUI unavailable' : ''}
            </option>
          ))}
        </select>
      </label>
      <p className="mt-1 text-[10px] opacity-75">
        {value === 'qwen-image'
          ? 'High-quality local render · approximately 4 megapixels · 40 steps · 0 credits. Allow several minutes; compare building details with your 3D view.'
          : isLocalImageModel(value)
          ? 'Runs on your desktop GPU · 0 credits. Returns the generated image directly, without geometry repair or replacement. Compare it with your 3D view.'
          : value === 'compare-all-three'
          ? 'Three image calls, billed separately. Same source view: GPT Image 2, Flare, then Sunburst. Each result is saved.'
          : allUnavailable ? 'Image rendering is unavailable in this session. You can still edit and explore the 3D scene.'
          : batchUnavailable ? 'This account does not yet list all three engines. Choose an available engine.' : 'One image call. Your 3D scene keeps the same geometry controls.'}
      </p>
    </div>
  );
}
