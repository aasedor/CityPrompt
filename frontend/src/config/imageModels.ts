/** Supported image engines shared by the render selectors. Keep legacy renders readable. */
// Safe fallback before account capability discovery; never silently send an
// unavailable new model or retry a paid request with another engine.
export const DEFAULT_OPENAI_IMAGE_MODEL = 'gpt-image-2';

export const OPENAI_IMAGE_MODELS = [
  { id: 'gpt-image-2.5-flare', label: 'GPT Image 2.5 Flare', option: 'Flare · Faster' },
  { id: 'gpt-image-2.5-sunburst', label: 'GPT Image 2.5 Sunburst', option: 'Sunburst · More precise' },
  { id: 'gpt-image-2', label: 'GPT Image 2', option: 'Image 2 · Previous version' },
] as const;

export type OpenAIImageModel = typeof OPENAI_IMAGE_MODELS[number]['id'] | 'gpt-image-2-2026-04-21';
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

export function imageModelsForChoice(choice: ImageModelChoice): ImageEngine[] {
  return choice === 'compare-all-three'
    ? ['gpt-image-2', 'gpt-image-2.5-flare', 'gpt-image-2.5-sunburst']
    : [choice];
}

export function imageModelLabel(model: string): string {
  // Labels only: these retired engines cannot be selected for new jobs.
  if (model === 'qwen-image') return 'Qwen Image 2.1';
  if (model === 'flux-klein') return 'FLUX.2 Klein 4B';
  return PAID_IMAGE_MODELS.find((entry) => entry.id === model)?.label ?? model;
}

export function imageModelUnavailable(availability: ImageModelAvailability | null, id: string): boolean {
  const entry = availability?.models.find(model => model.id === id);
  // Older servers cannot route Google. Existing OpenAI listing failures keep
  // their previous unknown-availability behavior without switching engines.
  return id === 'gemini-nano-banana-2.1' ? !entry || entry.available === false : entry?.available === false;
}
