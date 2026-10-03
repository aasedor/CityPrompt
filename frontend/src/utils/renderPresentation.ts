import type { SavedRender } from '@/types';

type Presentation = Pick<SavedRender, 'outcome' | 'presentation_strategy' | 'variant'>;

export function savedRenderNeedsReview(render: Presentation): boolean {
  if (render.variant === 'provider_original') return false;
  return render.outcome?.split('·')[0].trim() === 'review_required';
}

export function savedRenderIsSource(render: Presentation): boolean {
  if (render.variant === 'provider_original') return false;
  const strategy = render.presentation_strategy || render.outcome?.split('·')[1]?.trim();
  return strategy === 'authoritative_source';
}

export function savedRenderNotice(render: Presentation): string {
  if (render.variant === 'provider_original') return '';
  if (savedRenderIsSource(render)) return '3D source returned. The AI finish could not be verified and was kept separately for review.';
  return savedRenderNeedsReview(render)
    ? 'Review building locations, shapes, and streets against your plan before presenting.' : '';
}
