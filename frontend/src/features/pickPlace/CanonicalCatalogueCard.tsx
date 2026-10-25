import { useId, useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { CalgaryGuideDetails } from '@/features/calgaryCatalogue/CatalogueBrowser';
import { classifyCalgaryVariant } from '@/features/calgaryCatalogue/guide';
import { StreetCrossSection } from './StreetCrossSection';
import type { CatalogueAsset } from './assetRegistry';
import type { CanonicalChoice, CanonicalSelection } from './canonicalCatalogue';
import { pickerHeroImage } from './pickerHeroImages';
import { cataloguePresentationFor } from './cataloguePresentation';
import { catalogueSizeLabel, catalogueStyleIds, catalogueStyleLabel } from './catalogueFacets';
import { lessonForChoice } from '@/features/catalogueLearning/teaching';
import { CatalogueTeachingDetails } from '@/features/catalogueLearning/CatalogueTeachingDetails';

function CatalogueThumbnail({ sources, label }: { sources: string[]; label: string }) {
  const [index, setIndex] = useState(0);
  return index < sources.length
    ? <img loading="lazy" src={sources[index]} alt="" onError={() => setIndex(value => value + 1)}
      className="aspect-video w-full bg-slate-100 object-contain" />
    : <span role="img" aria-label={`${label}: preview image unavailable`}
      className="flex aspect-video w-full items-center justify-center bg-slate-100 px-4 text-center text-sm text-slate-600">Preview image unavailable</span>;
}

export function CanonicalCatalogueCard({ choice, selected, activeStreetVariant, onPlacement, onDraw, initialVariantId }: {
  choice: CanonicalChoice; selected: string | null; activeStreetVariant?: string;
  initialVariantId?: string;
  onPlacement: (asset: CatalogueAsset) => void; onDraw: (selection: CanonicalSelection) => void;
}) {
  const { option, placements } = choice;
  const [expanded, setExpanded] = useState(false);
  const detailsId = useId();
  const [variantId, setVariantId] = useState(initialVariantId ?? placements[0]?.model.variantId ?? option.variants?.[0]?.id ?? '');
  const variant = option.variants?.find(v => v.id === variantId);
  const placement = placements.find(a => a.model.variantId === variantId);
  const variantGuide = classifyCalgaryVariant(option.id, variantId);
  const thumbnail = pickerHeroImage(placement?.id,
    option.photoUrl || option.catalogCardImageUrl || variant?.thumbnailUrl || placement?.thumbnail || '');
  const presentation = cataloguePresentationFor(placement?.id);
  const lesson=lessonForChoice(choice,variantId);
  const styles=catalogueStyleIds(choice,variantId);
  const label = presentation?.label ?? placement?.label ?? option.label;
  const placementAction = placement?.kind === 'street' ? 'Choose & draw route'
    : placement?.kind === 'object' && placement.properties.pick_place_flexible_park ? 'Choose & draw park'
    : choice.domain === 'street_pathway' ? 'Place fixed review segment' : 'Choose & place';
  const imageSources = [...new Set([thumbnail, option.photoUrl, variant?.thumbnailUrl].filter((url): url is string => Boolean(url)))];
  return <article className="overflow-hidden rounded-xl border border-slate-300 bg-white">
    <button type="button" aria-label={`${label} · ${placementAction}`} title={placementAction}
      aria-pressed={placement ? (placement.kind === 'street' ? activeStreetVariant === variantId : selected === placement.id) : false}
      onClick={() => placement ? onPlacement(placement) : onDraw({ choice, variant })}
      className="group w-full text-left hover:bg-lime-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-3px]">
      <CatalogueThumbnail key={JSON.stringify(imageSources)} sources={imageSources} label={label} />
      <span className="block p-3">
        <span className="block text-sm font-bold">{label}</span>
        {choice.domain==='building' && <span className="mt-1 block text-[11px] font-medium text-slate-600">{lesson && lesson.status!=='classified' ? 'Style to be confirmed' : styles.map(id=>catalogueStyleLabel(id)).join(' · ') || 'Style not catalogued'}</span>}
      </span>
    </button>
    <button type="button" aria-expanded={expanded} aria-controls={expanded ? detailsId : undefined}
      aria-label={`${expanded ? 'Collapse' : 'Expand'} details for ${label}`} onClick={() => setExpanded(value => !value)}
      className="flex min-h-11 w-full items-center justify-between gap-2 border-t border-slate-200 px-3 text-xs font-semibold text-slate-700 hover:bg-lime-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-3px]">
      {expanded ? 'Less information' : 'Expand details'}
      {expanded ? <ChevronUp size={16} aria-hidden="true" /> : <ChevronDown size={16} aria-hidden="true" />}
    </button>
    {expanded && <div id={detailsId} className="space-y-2 border-t border-slate-200 bg-slate-50 px-3 py-3">
      <p className="text-sm text-slate-700">{presentation?.description ?? placement?.description ?? variant?.description ?? option.description}</p>
      <p className="text-xs font-medium text-slate-700">{placement?.kind === 'object' && placement.properties.pick_place_flexible_park ? 'Flexible 3D · draw your outline' : placement ? 'Detailed 3D' : choice.domain === 'building' ? 'Design massing · detailed model depends on size and availability' : 'Design reference · layout depends on available 3D support'}</p>
      <p className="text-[11px] text-slate-600">{catalogueSizeLabel(placement)}</p>
      <CatalogueTeachingDetails choice={choice} variantId={variantId} />
      {choice.domain === 'building' && !lesson && <p className="text-[11px] text-slate-600">{styles.map(id => catalogueStyleLabel(id)).join(' · ') || 'Style not catalogued'}</p>}
      {Boolean(option.variants?.length) && <label className="block text-xs font-medium">Design variant
        <select aria-label={`Variant for ${label}`} value={variantId} onChange={event => setVariantId(event.target.value)}
          className="mt-1 min-h-11 w-full rounded-lg border border-slate-400 bg-white px-2 text-sm text-slate-900">
          {placements.filter(a => !option.variants?.some(v => v.id === a.model.variantId)).map(a => <option key={a.model.variantId} value={a.model.variantId}>{cataloguePresentationFor(a.id)?.label ?? a.label}</option>)}
          {option.variants?.map(v => <option key={v.id} value={v.id}>{cataloguePresentationFor(placements.find(a => a.model.variantId === v.id)?.id)?.label ?? v.label}</option>)}
        </select>
      </label>}
      {placement?.kind === 'street' && <StreetCrossSection asset={placement} />}
      {(placement?.calgaryGuide ?? variantGuide ?? option.calgaryGuide) && <CalgaryGuideDetails classification={(placement?.calgaryGuide ?? variantGuide ?? option.calgaryGuide)!} />}
      <button type="button" onClick={() => placement ? onPlacement(placement) : onDraw({choice, variant})}
        className="min-h-11 w-full rounded-lg border-2 border-slate-900 bg-[#c9ff3d] px-3 text-sm font-bold text-slate-950 hover:bg-lime-200">
        {placementAction}
      </button>
    </div>}
  </article>;
}
