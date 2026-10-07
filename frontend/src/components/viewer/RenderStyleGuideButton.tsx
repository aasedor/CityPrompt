import { lazy, Suspense, useCallback, useState } from 'react';
import type { RenderStyleGuideProps } from './renderStyleGuideData';

const RenderStyleGuide = lazy(() => import('./RenderStyleGuide').then(module => ({ default: module.RenderStyleGuide })));

/** Nothing in the gallery is downloaded until the student opens it. */
export function RenderStyleGuideButton({disabled, className = '', ...props}: RenderStyleGuideProps & {disabled?: boolean; className?: string}) {
  const [open, setOpen] = useState(false);
  const close = useCallback(() => setOpen(false), []);
  return <>
    <button type="button" disabled={disabled} aria-haspopup="dialog" aria-expanded={open}
      onClick={() => setOpen(true)} className={`min-h-11 text-left text-sm font-semibold underline underline-offset-4 disabled:opacity-40 ${className}`}>
      Compare styles & examples
    </button>
    {open && <Suspense fallback={<p role="status" className="text-xs">Loading style examples…</p>}>
      <RenderStyleGuide {...props} onClose={close} />
    </Suspense>}
  </>;
}
