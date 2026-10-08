import { useEffect, type MutableRefObject } from 'react';
import { advanceWalkPose, type WalkPose } from './walkNavigation';

/** Modal panels own input while paused; restarting begins with no held keys. */
export function useWalkKeyboard(
  mode: 'pick' | 'active' | null,
  paused: boolean,
  pose: MutableRefObject<WalkPose | null>,
  apply: (next: WalkPose) => void,
  exit: () => void,
  cancelPick: () => void,
) {
  useEffect(() => {
    if (!mode || paused) return;
    const pressed = new Set<string>();
    const movementKeys = new Set(['w', 'a', 's', 'd', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'shift']);
    let frame = 0;
    let lastTime = performance.now();
    const tick = (time: number) => {
      const current = pose.current;
      if (current && pressed.size) {
        const next = advanceWalkPose(current, pressed, (time - lastTime) / 1000);
        if (next !== current) apply(next);
      }
      lastTime = time;
      frame = requestAnimationFrame(tick);
    };
    const keyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault(); event.stopImmediatePropagation();
        if (mode === 'pick') cancelPick(); else exit();
        return;
      }
      if (mode !== 'active') return;
      const target = event.target as HTMLElement | null;
      if (target?.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target?.tagName ?? '')) return;
      const key = event.key.toLowerCase();
      if (!movementKeys.has(key)) return;
      event.preventDefault(); event.stopImmediatePropagation(); pressed.add(key);
    };
    const keyUp = (event: KeyboardEvent) => { pressed.delete(event.key.toLowerCase()); };
    const clear = () => pressed.clear();
    window.addEventListener('keydown', keyDown, true);
    window.addEventListener('keyup', keyUp, true);
    window.addEventListener('blur', clear);
    if (mode === 'active') frame = requestAnimationFrame(tick);
    return () => {
      clear();
      window.removeEventListener('keydown', keyDown, true);
      window.removeEventListener('keyup', keyUp, true);
      window.removeEventListener('blur', clear);
      cancelAnimationFrame(frame);
    };
  }, [mode, paused, pose, apply, exit, cancelPick]);
}
