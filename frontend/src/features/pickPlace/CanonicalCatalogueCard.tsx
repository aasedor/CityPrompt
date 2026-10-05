import { useState } from 'react';
import { CalgaryGuideDetails } from '@/features/calgaryCatalogue/CatalogueBrowser';
import { classifyCalgaryVariant } from '@/features/calgaryCatalogue/guide';
import { StreetCrossSection } from './StreetCrossSection';
import type { CatalogueAsset } from './assetRegistry';
import type { CanonicalChoice, CanonicalSelection } from './canonicalCatalogue';
import { pickerHeroImage } from './pickerHeroImages';
import { catalogueSizeLabel, catalogueStyleIds, catalogueStyleLabel } from './catalogueFacets';

function CatalogueThumbnail({ sources, label }: { sources: string[]; label: string }) {
  const [index, setIndex] = useState(0);
  return index < sources.length
    ? <img loading="lazy" src={sources[index]} alt="" onError={() => setIndex(value => value + 1)}
      className="h-36 w-full bg-slate-100 object-cover" />
    : <span role="img" aria-label={`${label}: preview image unavailable`}
      className="flex h-36 items-center justify-center bg-slate-100 px-4 text-center text-sm text-slate-600">Preview image unavailable</span>;
}

export function CanonicalCatalogueCard({ choice, selected, activeStreetVariant, onPlacement, onDraw, initialVariantId }: {
  choice: CanonicalChoice; selected: string | null; activeStreetVariant?: string;
  initialVariantId?: string;
  onPlacement: (asset: CatalogueAsset) => void; onDraw: (selection: CanonicalSelection) => void;
}) {
  const { option, placements } = choice;
  const [variantId, setVariantId] = useState(initialVariantId ?? placements[0]?.model.variantId ?? option.variants?.[0]?.id ?? '');
  const variant = option.variants?.find(v => v.id === variantId);
  const placement = placements.find(a => a.model.variantId === variantId);
  const variantGuide = classifyCalgaryVariant(option.id, variantId);
  const thumbnail = pickerHeroImage(placement?.id,
    placement?.thumbnail ?? variant?.thumbnailUrl ?? option.catalogCardImageUrl ?? option.photoUrl);
  const label = placement?.label ?? option.label;
  const imageSources = [...new Set([thumbnail, placement?.thumbnail, variant?.thumbnailUrl].filter((url): url is string => Boolean(url)))];
  return <article className="overflow-hidden rounded-xl border border-slate-300 bg-white">
    <button type="button" aria-pressed={placement ? (placement.kind === 'street' ? activeStreetVariant === variantId : selected === placement.id) : false}
      onClick={() => placement ? onPlacement(placement) : onDraw({ choice, variant })}
      className="group w-full text-left hover:bg-lime-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-3px]">
      <CatalogueThumbnail key={JSON.stringify(imageSources)} sources={imageSources} label={label} />
      <span className="block space-y-1 p-3">
        <span className="block text-sm font-bold">{label}</span>
        <span className="block text-xs text-slate-600 line-clamp-3">{placement?.description ?? variant?.description ?? option.description}</span>
        <span className="block text-xs font-medium text-slate-700">{placement?.kind === 'object' && placement.properties.pick_place_flexible_park ? 'Flexible 3D · draw your outline' : placement ? 'Detailed 3D' : choice.domain === 'building' ? 'Design massing · detailed model depends on size and availability' : 'Design reference · layout depends on available 3D support'}</span>
        <span className="block pt-1 text-sm font-semibold underline">{placement?.kind === 'street' ? 'Choose & draw route'
          : placement?.kind === 'object' && placement.properties.pick_place_flexible_park ? 'Choose & draw park' : choice.domain === 'street_pathway' ? 'Place fixed review segment' : 'Choose & place'}</span>
      </span>
    </button>
    <div className="space-y-2 px-3 pb-3">
      <p className="text-[11px] text-slate-600">{catalogueSizeLabel(placement)}</p>
      {choice.domain === 'building' && <p className="text-[11px] text-slate-600">{catalogueStyleIds(choice).map(id => catalogueStyleLabel(id)).join(' · ') || 'Style not catalogued'}</p>}
      {Boolean(option.variants?.length) && <label className="block text-xs font-medium">Design variant
        <select aria-label={`Variant for ${option.label}`} value={variantId} onChange={event => setVariantId(event.target.value)}
          className="mt-1 min-h-11 w-full rounded-lg border border-slate-400 bg-white px-2 text-sm text-slate-900">
          {placements.filter(a => !option.variants?.some(v => v.id === a.model.variantId)).map(a => <option key={a.model.variantId} value={a.model.variantId}>{a.label}</option>)}
          {option.variants?.map(v => <option key={v.id} value={v.id}>{v.label}</option>)}
        </select>
      </label>}
      {placement?.kind === 'street' && <StreetCrossSection asset={placement} />}
      {(placement?.calgaryGuide ?? variantGuide ?? option.calgaryGuide) && <CalgaryGuideDetails classification={(placement?.calgaryGuide ?? variantGuide ?? option.calgaryGuide)!} />}
    </div>
  </article>;
}
