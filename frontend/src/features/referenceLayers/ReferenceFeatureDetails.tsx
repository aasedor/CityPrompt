import type {ReferenceFeature, ReferenceLayer} from './api';

export function ReferenceFeatureDetails({layer, feature, onClose}: {layer:ReferenceLayer;feature:ReferenceFeature;onClose:()=>void}) {
  const fields = Object.entries(feature.properties).filter(([,value]) => ['string','number','boolean'].includes(typeof value));
  return <section aria-label="Site context feature" className="absolute bottom-20 right-3 z-40 max-h-[55dvh] w-80 max-w-[calc(100vw-1.5rem)] overflow-y-auto rounded-xl border bg-white p-4 text-sm text-slate-900 shadow-xl">
    <div className="flex items-start justify-between gap-2"><h3 className="font-bold">{String(feature.properties.name ?? layer.name)}</h3><button aria-label="Close feature details" onClick={onClose} className="min-h-11 min-w-11">×</button></div>
    <p className="mb-3 text-xs text-slate-600">{layer.name} · existing reference</p>
    <dl className="space-y-3">{fields.filter(([key])=>key!=='name').map(([key,value])=><div key={key}><dt className="font-semibold">{key}</dt><dd className="break-words">{String(value)}</dd></div>)}</dl>
    {layer.source_url && /^https?:\/\//i.test(layer.source_url) && <a className="mt-3 inline-block min-h-11 underline" href={layer.source_url} target="_blank" rel="noreferrer">Open source data</a>}
  </section>;
}
