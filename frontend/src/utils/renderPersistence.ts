import { rendersApi } from '@/services/api';
import type { SavedRender } from '@/types';

export interface RenderImageInput {
  imageUrl: string;
  prompt?: string;
  seed?: number;
  model?: string;
  imageQuality?: 'auto' | 'low' | 'medium' | 'high';
}

export function getRenderImageKey(render: RenderImageInput): string {
  return [
    render.model ?? '',
    render.seed ?? '',
    render.imageUrl.length,
    render.imageUrl.slice(0, 96),
    render.imageUrl.slice(-96),
  ].join(':');
}

export async function imageUrlToBase64(imageUrl: string): Promise<string> {
  if (imageUrl.startsWith('data:')) {
    return imageUrl.split(',')[1] || '';
  }

  const response = await fetch(imageUrl);
  const blob = await response.blob();

  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(reader.error);
    reader.onloadend = () => resolve((reader.result as string).split(',')[1] || '');
    reader.readAsDataURL(blob);
  });
}

export async function saveRenderedImage(
  projectId: string,
  render: RenderImageInput,
  style?: string,
): Promise<SavedRender> {
  const base64 = await imageUrlToBase64(render.imageUrl);
  return rendersApi.save(projectId, {
    image_base64: base64,
    prompt: render.prompt || '',
    style,
    seed: render.seed,
    model: render.model,
    image_quality: render.imageQuality,
  });
}
