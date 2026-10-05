import { useState } from 'react';

export const WORKING_VIEW_QUALITY_KEY = 'cityprompt:working-view-quality:v1';
export const WORKING_VIEW_QUALITIES = {
  economy: { label: 'Economy', dpr: [1, 1] as [number, number], description: 'Lower screen resolution for basic laptops and tablets.' },
  balanced: { label: 'Balanced', dpr: [1, 1.5] as [number, number], description: 'A lighter everyday working view with clear edges.' },
  high: { label: 'High', dpr: [1, 2] as [number, number], description: 'Sharper screen detail when your device has enough capacity.' },
};
export type WorkingViewQuality = keyof typeof WORKING_VIEW_QUALITIES;

export function readWorkingViewQuality(): WorkingViewQuality {
  try {
    const value = localStorage.getItem(WORKING_VIEW_QUALITY_KEY);
    if (value === 'economy' || value === 'balanced' || value === 'high') return value;
  } catch { /* This preference remains usable without browser storage. */ }
  return 'balanced';
}

export function useWorkingViewQuality() {
  const [quality, setQuality] = useState(readWorkingViewQuality);
  const changeQuality = (value: WorkingViewQuality) => {
    setQuality(value);
    try { localStorage.setItem(WORKING_VIEW_QUALITY_KEY, value); } catch { /* Tab-only preference. */ }
  };
  return { quality, changeQuality, dpr: WORKING_VIEW_QUALITIES[quality].dpr };
}
