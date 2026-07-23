import { rendersApi, resolveApiFileUrl } from '@/services/api';
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

  const token = localStorage.getItem('access_token');
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
  const sourceUrl = resolveApiFileUrl(imageUrl);
  let response: Response | null = null;
  let fetchError: unknown = null;
  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      response = await fetch(sourceUrl, { headers, credentials: 'same-origin' });
      if (response.ok) break;
    } catch (error) {
      fetchError = error;
    }
    if (attempt === 0) await new Promise((resolve) => setTimeout(resolve, 250));
  }

  if (!response?.ok) {
    if (fetchError instanceof Error) throw new Error(`Failed to load render image: ${fetchError.message}`);
    throw new Error(response ? `Failed to load render image (${response.status})` : 'Failed to load render image');
  }

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
