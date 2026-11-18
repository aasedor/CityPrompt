import { useCallback, useEffect, useMemo, useState } from 'react';
import { rendersApi } from '@/services/api';
import { DEFAULT_OPENAI_IMAGE_MODEL, accountImageModel, imageModelsForChoice, isImageEngine, type ImageModelAvailability, type ImageModelChoice } from '@/config/imageModels';
import { readStoredRenderDraft } from './renderDraftStorage';

export function useImageModelChoice({ compareByDefault = true, projectId, accountRevision }: { compareByDefault?: boolean; projectId?: string; accountRevision?: string } = {}) {
  const [discovery, setDiscovery] = useState<{ accountRevision?: string; value: ImageModelAvailability } | null>(null);
  // Never expose a previous account/balance quote while the replacement loads.
  const availability = discovery?.accountRevision === accountRevision ? discovery?.value ?? null : null;
  const key = projectId ? `cityprompt:render-draft:${projectId}` : '';
  const initial = useMemo(() => {
    try {
      const saved = readStoredRenderDraft(key).imageModel;
      return saved === 'compare-all-three' || isImageEngine(saved) ? saved : null;
    } catch { return null; }
  }, [key]);
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
    const unavailable = (): ImageModelAvailability => ({ default_model: DEFAULT_OPENAI_IMAGE_MODEL, models: [] });
    void rendersApi.imageModels().then(result => {
      // Discovery is read-only. A malformed proxy/older-server response must
      // not crash the project or invent account balances and model access.
      return result && Array.isArray(result.models)
        && result.models.every(model => model && typeof model.id === 'string'
          && (model.available === null || typeof model.available === 'boolean'))
        && isImageEngine(result.default_model)
        ? result : unavailable();
    }).catch(unavailable).then(result => {
      if (active) setDiscovery({ accountRevision, value: result });
    });
    return () => { active = false; };
  }, [accountRevision]);
  const allAvailable = imageModelsForChoice('compare-all-three', availability).every(
    (id) => availability?.models.some((model) => model.id === id && model.available === true),
  );
  const fallback = compareByDefault && allAvailable ? 'compare-all-three' : availability?.default_model ?? DEFAULT_OPENAI_IMAGE_MODEL;
  const imageModel = selected ?? fallback;
  return {
    imageModel: imageModel === 'compare-all-three' ? imageModel : accountImageModel(imageModel, availability),
    setImageModel: setSelected,
    availability,
  };
}
