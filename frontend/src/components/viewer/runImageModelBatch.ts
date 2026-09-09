import { imageModelsForChoice, type ImageModelChoice, type OpenAIImageModel } from '@/config/imageModels';

/** A finite sequential comparison, never an automatic retry or image cascade.
 * The caller closes over one immutable capture and saves each successful result.
 * Stop after an error so partial success remains visible without surprise spend.
 */
export async function runImageModelBatch<T>(
  choice: ImageModelChoice,
  render: (model: OpenAIImageModel) => Promise<T>,
  onResult: (result: T, index: number) => Promise<void> | void,
  onStart?: (model: OpenAIImageModel, index: number, total: number) => void,
): Promise<void> {
  const models = imageModelsForChoice(choice);
  for (const [index, model] of models.entries()) {
    onStart?.(model, index, models.length);
    const result = await render(model);
    await onResult(result, index);
  }
}
