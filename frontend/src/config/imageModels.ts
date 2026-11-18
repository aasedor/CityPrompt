/** Supported image engines shared by the render selectors. Keep legacy renders readable. */
// Safe fallback before account capability discovery; never silently send an
// unavailable new model or retry a paid request with another engine.
export const DEFAULT_OPENAI_IMAGE_MODEL = 'gpt-image-2';

export const FLARE_IMAGE_MODEL = 'gpt-image-2.6-flare';
export const SUNBURST_IMAGE_MODEL = 'gpt-image-2.6-sunburst';
export const LEGACY_SUNBURST_IMAGE_MODEL = 'gpt-image-2.5-sunburst';

export const OPENAI_IMAGE_MODELS = [
  { id: FLARE_IMAGE_MODEL, label: 'GPT Image 2.6 Flare', option: 'Flare 2.6 · Faster' },
  { id: SUNBURST_IMAGE_MODEL, label: 'GPT Image 2.6 Sunburst', option: 'Sunburst 2.6 · More precise' },
  { id: 'gpt-image-2', label: 'GPT Image 2', option: 'Image 2 · Previous version' },
] as const;

const LEGACY_OPENAI_IMAGE_MODELS = [
  { id: 'gpt-image-2.5-flare', label: 'GPT Image 2.5 Flare', option: 'Flare 2.5 · Faster' },
  { id: LEGACY_SUNBURST_IMAGE_MODEL, label: 'GPT Image 2.5 Sunburst', option: 'Sunburst 2.5 · More precise' },
] as const;

export type OpenAIImageModel = typeof OPENAI_IMAGE_MODELS[number]['id']
  | typeof LEGACY_OPENAI_IMAGE_MODELS[number]['id'] | 'gpt-image-2-2026-04-21';
export const GOOGLE_IMAGE_MODELS = [
  { id: 'gemini-nano-banana-2.1', label: 'Nano Banana 2.1', option: 'Nano Banana 2.1 · Google' },
] as const;
export type PaidImageModel = OpenAIImageModel | typeof GOOGLE_IMAGE_MODELS[number]['id'];
export const PAID_IMAGE_MODELS = [...OPENAI_IMAGE_MODELS, ...GOOGLE_IMAGE_MODELS];
export type ImageEngine = PaidImageModel;
export type ImageModelChoice = ImageEngine | 'compare-all-three';
export type ImageModelAvailability = {
  default_model: OpenAIImageModel;
  /** Server-effective weekly balance; absent on older servers. */
  credit_balance?: number;
  credit_exempt?: boolean;
  models: Array<{ id: ImageEngine; available: boolean | null; minimum_credit_cost?: number }>;
};

const KNOWN_IMAGE_MODELS = [...PAID_IMAGE_MODELS, ...LEGACY_OPENAI_IMAGE_MODELS];
const OPENAI_UPGRADES = [
  [FLARE_IMAGE_MODEL, LEGACY_OPENAI_IMAGE_MODELS[0].id],
  [SUNBURST_IMAGE_MODEL, LEGACY_SUNBURST_IMAGE_MODEL],
] as const;

export function isImageEngine(model: unknown): model is ImageEngine {
  return model === 'gpt-image-2-2026-04-21' || KNOWN_IMAGE_MODELS.some(entry => entry.id === model);
}

/** Resolve each named engine before displaying the choice or quoting its cost. */
export function accountImageModel(model: ImageEngine, availability: ImageModelAvailability | null): ImageEngine {
  const versions = OPENAI_UPGRADES.find(([current, legacy]) => current === model || legacy === model);
  if (!versions) return model;
  const [current, legacy] = versions;
  if (availability?.models.some(row => row.id === current && row.available === true)) return current;
  return availability?.models.some(row => row.id === legacy && row.available !== false) ? legacy : current;
}

export function imageModelOptions(availability: ImageModelAvailability | null) {
  return PAID_IMAGE_MODELS.map(option =>
    KNOWN_IMAGE_MODELS.find(entry => entry.id === accountImageModel(option.id, availability)) ?? option);
}

export function imageModelsForChoice(choice: ImageModelChoice, availability: ImageModelAvailability | null = null): ImageEngine[] {
  return choice === 'compare-all-three'
    ? [DEFAULT_OPENAI_IMAGE_MODEL, accountImageModel(FLARE_IMAGE_MODEL, availability), accountImageModel(SUNBURST_IMAGE_MODEL, availability)]
    : [choice];
}

export function imageModelLabel(model: string): string {
  // Labels only: these retired engines cannot be selected for new jobs.
  if (model === 'qwen-image') return 'Qwen Image 2.1';
  if (model === 'flux-klein') return 'FLUX.2 Klein 4B';
  return KNOWN_IMAGE_MODELS.find((entry) => entry.id === model)?.label ?? model;
}

export function imageModelUnavailable(availability: ImageModelAvailability | null, id: string): boolean {
  const entry = availability?.models.find(model => model.id === id);
  // New versions require confirmed access. Older engines retain their
  // existing behavior when the provider's model list is unavailable.
  if (id === FLARE_IMAGE_MODEL || id === SUNBURST_IMAGE_MODEL) return entry?.available !== true;
  return entry?.available === false || (id === 'gemini-nano-banana-2.1' && !entry);
}
