import type { Direct3DRenderDiagnostics } from './useDirect3DRender';

export type ImageFidelityStatus = 'failed' | 'passed' | 'review';
export function imageFidelityStatus(diagnostics: Direct3DRenderDiagnostics): ImageFidelityStatus {
  if (diagnostics.returned_safety_strategy === 'authoritative_source') return 'failed';
  if (diagnostics.processing_mode === 'scene' && diagnostics.macro_design_fidelity?.passed === true
    && diagnostics.instance_source_presence?.passed === true && diagnostics.unsupported_structure?.passed === true) return 'passed';
  return 'review';
}

export function ImageFidelityReview({ status, warnings, onOriginal }: {
  status: ImageFidelityStatus; warnings: string[]; onOriginal?: () => void;
}) {
  return <section aria-label="Design fidelity" role={status === 'failed' ? 'alert' : 'status'} className="mb-3 space-y-2 rounded-lg border border-amber-300 bg-slate-900 p-3 text-white">
    <h4 className="text-sm font-bold">{status === 'failed' ? 'AI finish failed design checks' : status === 'passed' ? 'Image checks passed · review the design' : 'Compare with your original design'}</h4>
    <p className="text-sm">{status === 'failed'
      ? 'Showing your original 3D view because the AI finish changed the design or could not be verified. Your design is unchanged. A new attempt uses credits; nothing retries automatically.'
      : status === 'passed'
        ? 'The available image checks passed. Compare building identity, heights, streets and parks with the source before presenting. These checks cannot prove exact geometry.'
        : 'This image has not passed a complete design check. Compare camera, buildings, streets and parks with the source before using it.'}</p>
    {warnings.length > 0 && <details className="text-xs text-slate-200"><summary className="min-h-11 cursor-pointer py-3">Check details</summary><ul className="list-disc space-y-1 pl-4">{warnings.map(warning => <li key={warning}>{warning}</li>)}</ul></details>}
    {onOriginal && <button type="button" onClick={onOriginal} className="min-h-11 rounded-lg border border-slate-400 px-3 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-lime-300">Inspect unverified AI original</button>}
  </section>;
}
