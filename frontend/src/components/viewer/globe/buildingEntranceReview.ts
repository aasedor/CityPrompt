import type { SharedSiteGroundState } from './SharedSiteGroundProvider';

/** Display geometry may survive a tile refresh. Publish only when verification
 * has measured the same surface; their revision formats intentionally differ. */
export function entranceReviewRevision(display: SharedSiteGroundState, verification: SharedSiteGroundState): string | null {
  if (display.status !== 'ready' || verification.status !== 'ready' || display.preview || verification.preview ||
      verification.isCurrent?.() === false || !display.snapshot || !verification.snapshot ||
      display.snapshot.sourceSignature !== verification.snapshot.sourceSignature ||
      display.snapshot.signature !== verification.snapshot.signature) return null;
  return verification.revision;
}

export interface BuildingEntranceReview {
  buildingId: string;
  groundRevision: string;
  generatedSteps: number;
  riseM: number;
  clearWidthM: number;
  supportHeightM: number;
}

/** A departing fallback/renderer must not clear another renderer's evidence. */
export function updateEntranceReviews(previous: ReadonlyMap<string, BuildingEntranceReview>, rendererId: string,
  review: BuildingEntranceReview | null): ReadonlyMap<string, BuildingEntranceReview> {
  const before=previous.get(rendererId);
  if(review===null?!before:JSON.stringify(before)===JSON.stringify(review))return previous;
  const next=new Map(previous);
  if(review)next.set(rendererId,review);else next.delete(rendererId);
  return next;
}

export function currentEntranceReviews(reviews: ReadonlyMap<string, BuildingEntranceReview>, buildingIds: ReadonlySet<string>) {
  return [...new Map([...reviews.values()].filter(review=>buildingIds.has(review.buildingId))
    .map(review=>[review.buildingId,review])).values()];
}
