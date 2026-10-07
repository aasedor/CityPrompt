import { useState } from 'react';
import { StudioDialog } from '@/features/projects/StudioControls';
import { resolveDirect3DPresentationMode } from './globe/useDirect3DRender';
import { RENDER_STYLE_EXAMPLES, renderStyleDirection, type RenderStyleGuideProps } from './renderStyleGuideData';

function ExampleImage({src, label}: {src: string; label: string}) {
  const [failed, setFailed] = useState(false);
  return failed ? <p role="status" className="flex aspect-[1.6] items-center justify-center bg-slate-100 p-4 text-sm text-slate-700">This saved example could not load. You can still choose the style.</p>
    : <img src={src} alt={label} width={1616} height={1008} loading="lazy" decoding="async" onError={() => setFailed(true)} className="aspect-[1.6] w-full rounded-lg bg-slate-100 object-contain" />;
}

function SavedExample({id}: {id: string}) {
  const [showSource, setShowSource] = useState(false);
  const example = RENDER_STYLE_EXAMPLES.find(item => item.id === id);
  if (!example) return <p className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-700">No saved image example for this style yet. Explore Photomontage, Watercolour or Charcoal to see examples from City Prompt.</p>;
  return <div className="space-y-3">
    <p className="text-xs font-semibold text-slate-600">Saved City Prompt example · {example.view}</p>
    <div className={`grid gap-3 ${showSource ? 'sm:grid-cols-2' : ''}`}>
      {showSource && <figure><ExampleImage key={example.source} src={example.source} label={`${example.label} example: original 3D source`} /><figcaption className="mt-2 text-xs font-semibold">Original 3D view</figcaption></figure>}
      <figure><ExampleImage key={example.image} src={example.image} label={`${example.label} saved image example`} /><figcaption className="mt-2 text-xs font-semibold">{example.label} image</figcaption></figure>
    </div>
    <button type="button" aria-pressed={showSource} onClick={() => setShowSource(value => !value)} className="min-h-11 text-sm font-semibold underline underline-offset-4">{showSource ? 'Hide' : 'Show'} original 3D view</button>
  </div>;
}

function StreetComparison() {
  return <div className="grid gap-4 sm:grid-cols-2">
    {RENDER_STYLE_EXAMPLES.filter(example => example.view === 'Street view').map(example => <figure key={example.id}>
      <ExampleImage src={example.image} label={`${example.label} street comparison example`} />
      <figcaption className="mt-2 text-sm font-semibold">{example.label}</figcaption>
    </figure>)}
  </div>;
}

export function RenderStyleGuide({styles, selectedStyle, onStyle, isStyleDisabled, styleHint, onClose}: RenderStyleGuideProps & {onClose: () => void}) {
  const [previewStyle, setPreviewStyle] = useState(() => RENDER_STYLE_EXAMPLES.some(example => example.id === selectedStyle)
    ? selectedStyle : styles.some(style => style.id === 'photomontage') ? 'photomontage' : selectedStyle);
  const [compareStreet, setCompareStreet] = useState(false);
  const option = styles.find(item => item.id === previewStyle) ?? styles[0];
  if (!option) return null;
  const direction = renderStyleDirection(option.id);
  const projectionChanges = resolveDirect3DPresentationMode(option.id === 'clay-model' ? 'clay-maquette' : option.id) === 'reproject';
  const disabled = isStyleDisabled?.(option.id);
  const select = () => { if (!disabled) { onStyle(option.id); onClose(); } };
  return <StudioDialog title="Render style guide" onClose={onClose}>
    <div className="space-y-5 text-slate-900">
      <p className="max-w-3xl text-sm leading-6 text-slate-600">Choose the medium and mood for your presentation. Browsing these examples uses no image credits; it changes your render style only when you choose Use this style.</p>
      <p className="text-xs font-semibold text-slate-600">Current render style: {styles.find(item => item.id === selectedStyle)?.label ?? selectedStyle}</p>
      <div className="flex flex-wrap items-end gap-4">
        <label className="min-w-0 flex-1 text-sm font-semibold">Explore a style
          <select value={option.id} onChange={event => { setPreviewStyle(event.target.value); setCompareStreet(false); }} className="mt-1 min-h-11 w-full rounded-lg border border-slate-400 bg-white px-3 text-sm text-slate-900">
            {styles.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
          </select>
        </label>
        <button type="button" aria-pressed={compareStreet} onClick={() => setCompareStreet(value => !value)} className="min-h-11 rounded-lg border border-slate-400 px-3 text-sm font-semibold">{compareStreet ? 'Return to selected style' : 'Compare street examples'}</button>
      </div>
      {compareStreet ? <>
        <StreetComparison />
        <p className="text-xs leading-5 text-slate-600">Two independent images of the same community and street direction. The source captures differ slightly. Charcoal uses a closer building view and is shown separately.</p>
      </> : <>
        <div className="border-l-4 border-lime-400 pl-4">
          <h2 className="text-xl font-semibold">{option.label}</h2>
          <p className="mt-2 text-sm leading-6">{direction?.summary ?? 'An artistic image treatment of your captured design.'}</p>
          {direction && <p className="mt-2 text-sm leading-6 text-slate-600"><strong>Useful for:</strong> {direction.goodFor}</p>}
          {projectionChanges && <p className="mt-2 text-sm font-semibold text-amber-900">Changes the camera projection. Compare the resulting layout with your original design.</p>}
        </div>
        <SavedExample key={option.id} id={option.id} />
      </>}
      <div className="flex flex-wrap gap-2" aria-label="Saved style examples">
        {RENDER_STYLE_EXAMPLES.filter(example => styles.some(item => item.id === example.id)).map(example => <button key={example.id} type="button" aria-pressed={!compareStreet && option.id === example.id}
          onClick={() => { setPreviewStyle(example.id); setCompareStreet(false); }} className="min-h-11 rounded-lg border border-slate-300 px-3 text-sm font-semibold hover:bg-lime-50">View {example.label}</button>)}
      </div>
      <div className="flex flex-wrap items-center justify-between gap-4 border-t border-slate-200 pt-4">
        <p className="max-w-lg text-xs leading-5 text-slate-600">These are example image studies, not a preview of your current project. Check your rendered buildings, paths and materials against the 3D source before presenting.</p>
        <button type="button" disabled={disabled} title={styleHint?.(option.id)} onClick={select} className="min-h-11 rounded-lg border-2 border-slate-900 bg-lime-300 px-4 text-sm font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-40">Use this style · {option.label}</button>
      </div>
      {disabled && <p role="status" className="text-sm text-amber-900">{styleHint?.(option.id) ?? 'This style is unavailable for the current scene.'}</p>}
    </div>
  </StudioDialog>;
}
