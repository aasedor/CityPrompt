import { useEffect, useState } from 'react';
import { rendersApi } from '@/services/api';
import { DEFAULT_OPENAI_IMAGE_MODEL, type ImageModelAvailability, type ImageModelChoice } from '@/config/imageModels';

export function useImageModelChoice() {
  const [availability, setAvailability] = useState<ImageModelAvailability | null>(null);
  const [selected, setSelected] = useState<ImageModelChoice | null>(null);
  useEffect(() => {
    let active = true;
    rendersApi.imageModels().then((result) => {
      if (active) setAvailability(result);
    }).catch(() => { /* Keep the established engine if discovery is unavailable. */ });
    return () => { active = false; };
  }, []);
  const allAvailable = ['gpt-image-2', 'gpt-image-2.5-flare', 'gpt-image-2.5-sunburst'].every(
    (id) => availability?.models.some((model) => model.id === id && model.available === true),
  );
  return {
    imageModel: selected ?? (allAvailable ? 'compare-all-three' : availability?.default_model ?? DEFAULT_OPENAI_IMAGE_MODEL),
    setImageModel: setSelected,
    availability,
  };
}
