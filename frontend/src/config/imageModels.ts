/** IDs shared by the Images edit API and Direct 3D. Keep legacy renders readable. */
// Safe fallback before account capability discovery; never silently send an
// unavailable new model or retry a paid request with another engine.
export const DEFAULT_OPENAI_IMAGE_MODEL = 'gpt-image-2';

export const OPENAI_IMAGE_MODELS = [
  { id: 'gpt-image-2.5-flare', label: 'GPT Image 2.5 Flare', option: 'Flare · Faster' },
  { id: 'gpt-image-2.5-sunburst', label: 'GPT Image 2.5 Sunburst', option: 'Sunburst · More precise' },
  { id: 'gpt-image-2', label: 'GPT Image 2', option: 'Image 2 · Previous version' },
] as const;

export type OpenAIImageModel = typeof OPENAI_IMAGE_MODELS[number]['id'] | 'gpt-image-2-2026-04-21';
export type ImageModelChoice = OpenAIImageModel | 'compare-all-three';
export type ImageModelAvailability = {
  default_model: OpenAIImageModel;
  models: Array<{ id: OpenAIImageModel; available: boolean | null }>;
};

export function imageModelsForChoice(choice: ImageModelChoice): OpenAIImageModel[] {
  return choice === 'compare-all-three'
    ? ['gpt-image-2', 'gpt-image-2.5-flare', 'gpt-image-2.5-sunburst']
    : [choice];
}

export function imageModelLabel(model: string): string {
  return OPENAI_IMAGE_MODELS.find((entry) => entry.id === model)?.label ?? model;
}
