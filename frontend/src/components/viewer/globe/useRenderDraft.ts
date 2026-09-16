import { useCallback, useEffect, useMemo, useState } from 'react';

type RenderDraft = { selectedStyle: string; customPrompt: string; addPeople: boolean; addVehicles: boolean };
const DEFAULT_DRAFT: RenderDraft = { selectedStyle: 'photorealistic', customPrompt: '', addPeople: false, addVehicles: false };

/** Closing the panel to frame a camera must not discard the student's directions. */
export function useRenderDraft(projectId: string | undefined, styleIds: readonly string[]) {
  const key = projectId ? `cityprompt:render-draft:${projectId}` : '';
  const initial = useMemo(() => {
    try {
      const saved = key ? JSON.parse(sessionStorage.getItem(key) ?? 'null') : null;
      return {
        selectedStyle: styleIds.includes(saved?.selectedStyle) ? saved.selectedStyle as string : DEFAULT_DRAFT.selectedStyle,
        customPrompt: typeof saved?.customPrompt === 'string' ? saved.customPrompt as string : '',
        addPeople: saved?.addPeople === true,
        addVehicles: saved?.addVehicles === true,
      };
    } catch { return DEFAULT_DRAFT; }
  }, [key, styleIds]);
  const [drafts, setDrafts] = useState<Record<string, RenderDraft>>({});
  const draft = drafts[key] ?? initial;
  useEffect(() => {
    if (!key) return;
    try { sessionStorage.setItem(key, JSON.stringify(draft)); } catch { /* Editing still works without storage. */ }
  }, [key, draft]);
  const update = useCallback((patch: Partial<RenderDraft>) => {
    setDrafts(previous => ({ ...previous, [key]: { ...(previous[key] ?? initial), ...patch } }));
  }, [key, initial]);
  const setSelectedStyle = useCallback((selectedStyle: string) => update({ selectedStyle }), [update]);
  const setCustomPrompt = useCallback((customPrompt: string) => update({ customPrompt }), [update]);
  const setAddPeople = useCallback((addPeople: boolean) => update({ addPeople }), [update]);
  const setAddVehicles = useCallback((addVehicles: boolean) => update({ addVehicles }), [update]);
  return { ...draft, setSelectedStyle, setCustomPrompt, setAddPeople, setAddVehicles };
}
