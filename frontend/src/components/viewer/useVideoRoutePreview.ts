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
  const pending = useRef<{ signature: string; promise: Promise<Preview>; controller:AbortController } | null>(null);
  const [isCancelling,setIsCancelling]=useState(false);
  useEffect(() => { mounted.current = true; return () => { mounted.current = false; pending.current?.controller.abort(); }; }, []);

  const cancel=useCallback(async()=>{
    const active=pending.current;
    setRouteControls(null);
    if(!active)return;
    setIsCancelling(true);
    active.controller.abort();
    // Capture's finally restores camera, scene visibility and renderer size.
    // Do not permit another capture until that cleanup has completed.
    await active.promise.catch(()=>{});
  },[]);

  const prepare = useCallback((capture: (signal:AbortSignal) => Promise<VideoRouteCaptureResult>, minimumKeyframes = 1): Promise<Preview> => {
    if (routeControls?.signature === signature && routeControls.keyframesBase64.length >= minimumKeyframes) return Promise.resolve(routeControls);
    if (pending.current) {
      if (pending.current.signature === signature) return pending.current.promise;
      return Promise.reject(new Error('The previous preview is finishing. Try again in a moment.'));
    }
    setIsPreparingControls(true);
    const controller=new AbortController();
    const promise = Promise.resolve().then(()=>{
      controller.signal.throwIfAborted();
      return capture(controller.signal);
    }).then(result => {
      controller.signal.throwIfAborted();
      if (!mounted.current || currentSignature.current !== signature) {
        throw new Error('Your design or route changed while preparing the preview. Prepare it again for the current design.');
      }
      const preview = { ...result, signature };
      setRouteControls(preview);
      return preview;
    }).finally(() => {
      pending.current = null;
      if (mounted.current) {setIsPreparingControls(false);setIsCancelling(false);}
    });
    pending.current = { signature, promise, controller };
    return promise;
  }, [routeControls, signature]);

  return { routeControls, setRouteControls, isPreparingControls, isCancelling, prepare, cancel };
}
