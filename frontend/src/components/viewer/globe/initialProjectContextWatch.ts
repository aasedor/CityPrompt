interface ContextVisibilityEvents {
  addEventListener(type: 'tile-visibility-change', listener: () => void): void;
  removeEventListener(type: 'tile-visibility-change', listener: () => void): void;
}
interface InitialProjectContextWatchOptions {
  source: ContextVisibilityEvents;
  isCancelled: () => boolean;
  adjust: () => boolean;
  durationMs?: number;
  checkDelayMs?: number;
  maxChecks?: number;
  maxAdjustments?: number;
}
/** Captures and walking can own either the wrapper or nested controls. */
export function initialContextCameraIsPaused(controls: { enabled?: boolean; controls?: { enabled?: boolean } } | null | undefined): boolean {
  return controls?.enabled === false || controls?.controls?.enabled === false;
}
/** Initial framing can precede detailed Google context by a minute. Observe
 * the renderer's documented visibility event, coalescing refinement bursts.
 * No idle polling or camera reset: adjust only an actually obstructed pose. */
export function watchInitialProjectContext(options: InitialProjectContextWatchOptions): () => void {
  let source: ContextVisibilityEvents | null = options.source;
  let isCancelled: (() => boolean) | null = options.isCancelled;
  let adjust: (() => boolean) | null = options.adjust;
  const delay = options.checkDelayMs ?? 2000;
  const maxChecks = options.maxChecks ?? 60, maxAdjustments = options.maxAdjustments ?? 3;
  let checks = 0, adjustments = 0, disposed = false;
  let pending: ReturnType<typeof setTimeout> | undefined;
  let deadline: ReturnType<typeof setTimeout> | undefined;
  const stop = () => {
    if (disposed) return;
    disposed = true;
    if (pending !== undefined) clearTimeout(pending);
    if (deadline !== undefined) clearTimeout(deadline);
    source?.removeEventListener('tile-visibility-change', changed);
    // Release the renderer and callbacks even when the owner retains stop().
    source = null; isCancelled = null; adjust = null;
  };
  const check = () => {
    pending = undefined;
    if (disposed || isCancelled?.()) { stop(); return; }
    checks++;
    if (adjust?.()) adjustments++;
    if (checks >= maxChecks || adjustments >= maxAdjustments) stop();
  };
  function changed() {
    if (disposed || isCancelled?.()) { stop(); return; }
    if (pending === undefined) pending = setTimeout(check, delay);
  }
  source.addEventListener('tile-visibility-change', changed);
  deadline = setTimeout(stop, options.durationMs ?? 120000);
  changed();
  return stop;
}
