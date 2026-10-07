import { useCallback, useEffect, useMemo, useState } from 'react';
import { rendersApi } from '@/services/api';
import { DEFAULT_OPENAI_IMAGE_MODEL, OPENAI_IMAGE_MODELS, isLocalImageModel, type ImageModelAvailability, type ImageModelChoice } from '@/config/imageModels';
import { comfyTrialsApi } from '@/services/comfyTrials';
import { readStoredRenderDraft } from './renderDraftStorage';

export function useImageModelChoice({ compareByDefault = true, projectId, allowLocal = true }: { compareByDefault?: boolean; projectId?: string; allowLocal?: boolean } = {}) {
  const [availability, setAvailability] = useState<ImageModelAvailability | null>(null);
  const key = projectId ? `cityprompt:render-draft:${projectId}` : '';
  const initial = useMemo(() => {
    try {
      const saved = readStoredRenderDraft(key).imageModel;
      return saved === 'compare-all-three' || OPENAI_IMAGE_MODELS.some(model => model.id === saved)
        || (allowLocal && import.meta.env.DEV && typeof saved === 'string' && isLocalImageModel(saved))
        || saved === 'gpt-image-2-2026-04-21' ? saved as ImageModelChoice : null;
    } catch { return null; }
  }, [key, allowLocal]);
  const [choices, setChoices] = useState<Record<string, ImageModelChoice>>({});
  const selected = choices[key] ?? initial;
  const setSelected = useCallback((model: ImageModelChoice) => {
    setChoices(previous => ({ ...previous, [key]: model }));
    if (!key) return;
    try {
      sessionStorage.setItem(key, JSON.stringify({ ...readStoredRenderDraft(key), imageModel: model }));
    } catch { /* The selected engine still works when storage is unavailable. */ }
  }, [key]);
  useEffect(() => {
    let active = true;
    const local = allowLocal && import.meta.env.DEV
      ? comfyTrialsApi.presets().then(result => result.presets.filter(p => p.kind === 'image' && isLocalImageModel(p.id)).map(p => ({ id: p.id as 'flux-klein' | 'qwen-image', available: p.available }))).catch(() => [])
      : Promise.resolve([]);
    void Promise.all([rendersApi.imageModels().catch(() => ({ default_model: DEFAULT_OPENAI_IMAGE_MODEL, models: [] } as ImageModelAvailability)), local]).then(([result, models]) => {
      if (active) setAvailability({ ...result, models: [...result.models, ...models] });
    });
    return () => { active = false; };
  }, [allowLocal]);
  const allAvailable = ['gpt-image-2', 'gpt-image-2.5-flare', 'gpt-image-2.5-sunburst'].every(
    (id) => availability?.models.some((model) => model.id === id && model.available === true),
  );
  return {
    imageModel: selected ?? (compareByDefault && allAvailable ? 'compare-all-three' : availability?.default_model ?? DEFAULT_OPENAI_IMAGE_MODEL),
    setImageModel: setSelected,
    availability,
  };
}
