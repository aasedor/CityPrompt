import { useEffect, useRef } from 'react';

export const COMMUNITY_3D_PRESENTATION_READY_EVENT =
  'cityprompt:community-3d-presentation-ready';

export interface Community3DPresentationReadyDetail {
  zoneIds: string[];
}

/**
 * Announce a successful atomic Community 3D compile. Keeping this separate
 * from query invalidation lets the globe switch to a clean 3D presentation
 * immediately, while the newly compiled models and public realm reload.
 */
export function announceCommunity3DPresentationReady(zoneIds: string[]): void {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent<Community3DPresentationReadyDetail>(
    COMMUNITY_3D_PRESENTATION_READY_EVENT,
    { detail: { zoneIds: [...zoneIds] } },
  ));
}

/**
 * A completed compile should present the generated scene, not the coloured
 * authoring polygons. This is deliberately event-driven and one-shot: after
 * the automatic clean view, the user remains free to turn Plan Overlay back
 * on without an effect immediately hiding it again.
 */
export function useCleanPresentationAfterCommunity3DCompile(
  setZoneOverlaysVisible: (visible: boolean) => void,
  hasCompiledCommunity = false,
): void {
  const presentedExistingCommunityRef = useRef(false);

  useEffect(() => {
    if (!hasCompiledCommunity || presentedExistingCommunityRef.current) return;
    presentedExistingCommunityRef.current = true;
    setZoneOverlaysVisible(false);
  }, [hasCompiledCommunity, setZoneOverlaysVisible]);

  useEffect(() => {
    const showCompiledScene = () => setZoneOverlaysVisible(false);
    window.addEventListener(COMMUNITY_3D_PRESENTATION_READY_EVENT, showCompiledScene);
    return () => {
      window.removeEventListener(COMMUNITY_3D_PRESENTATION_READY_EVENT, showCompiledScene);
    };
  }, [setZoneOverlaysVisible]);
}
