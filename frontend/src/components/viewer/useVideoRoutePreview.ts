import { useCallback, useEffect, useRef, useState } from 'react';
import type { VideoRouteCaptureResult } from './videoRouteControls';

type Preview = VideoRouteCaptureResult & { signature: string };

/** Share local guide capture between preview and paid preflight, without allowing
 * an older scene or an overlapping capture to replace the current guide. */
export function useVideoRoutePreview(signature: string) {
  const [routeControls, setRouteControls] = useState<Preview | null>(null);
  const [isPreparingControls, setIsPreparingControls] = useState(false);
  const currentSignature = useRef(signature);
  currentSignature.current = signature;
  const mounted = useRef(true);
  const pending = useRef<{ signature: string; promise: Promise<Preview> } | null>(null);
  useEffect(() => { mounted.current = true; return () => { mounted.current = false; }; }, []);

  const prepare = useCallback((capture: () => Promise<VideoRouteCaptureResult>): Promise<Preview> => {
    if (routeControls?.signature === signature) return Promise.resolve(routeControls);
    if (pending.current) {
      if (pending.current.signature === signature) return pending.current.promise;
      return Promise.reject(new Error('The previous preview is finishing. Try again in a moment.'));
    }
    setIsPreparingControls(true);
    const promise = Promise.resolve().then(capture).then(result => {
      if (!mounted.current || currentSignature.current !== signature) {
        throw new Error('Your design or route changed while preparing the preview. Prepare it again for the current design.');
      }
      const preview = { ...result, signature };
      setRouteControls(preview);
      return preview;
    }).finally(() => {
      pending.current = null;
      if (mounted.current) setIsPreparingControls(false);
    });
    pending.current = { signature, promise };
    return promise;
  }, [routeControls, signature]);

  return { routeControls, setRouteControls, isPreparingControls, prepare };
}
