import { useId, useMemo } from 'react';
import { BUILDING_AESTHETIC_CATEGORIES_V2 } from '@/components/viewer/aestheticCatalog';
import { CALGARY_GROUPS, type CatalogueDomain } from '@/features/calgaryCatalogue/guide';
import { choiceMatchesGroup, type CanonicalChoice } from './canonicalCatalogue';
import { availableCatalogueSizes, availableCatalogueStyles, type CatalogueFacets } from './catalogueFacets';

const field = 'mt-1 min-h-11 w-full min-w-0 rounded-lg border border-slate-400 bg-white px-2 text-sm text-slate-900';

export function CatalogueFacetControls({ domain, choices, purposeId, facets, onPurpose, onFacet }: {
  domain: CatalogueDomain; choices: CanonicalChoice[]; purposeId: string; facets: CatalogueFacets;
  onPurpose: (id: string) => void; onFacet: (key: keyof CatalogueFacets, id: string) => void;
}) {
  const id = useId();
  const options = useMemo(() => choices.filter(choice => choice.domain === domain), [choices, domain]);
  const purposes = useMemo(() => CALGARY_GROUPS.filter(group => group.domain === domain && options.some(choice => choiceMatchesGroup(choice, group.id))), [options, domain]);
  const styles = useMemo(() => availableCatalogueStyles(options, BUILDING_AESTHETIC_CATEGORIES_V2), [options]);
  const sizes = useMemo(() => availableCatalogueSizes(domain, options), [domain, options]);
  const active = Boolean(purposeId || facets.styleId || facets.sizeId);
  return <details className="rounded-lg border border-slate-200 px-3">
    <summary className="min-h-11 cursor-pointer py-3 text-sm font-semibold">
      {domain === 'building' ? 'Land use, size & style' : domain === 'park_plaza' ? 'Park purpose & size' : 'Street role & width'}{active ? ' · filters active' : ''}
    </summary>
    <div className={`grid gap-2 pb-2 ${domain === 'building' ? 'sm:grid-cols-3' : 'sm:grid-cols-2'}`}>
      <label htmlFor={`${id}-purpose`} className="min-w-0 text-xs font-semibold">
        {domain === 'building' ? 'Land-use type' : domain === 'park_plaza' ? 'Park purpose' : 'Street role'}
        <select id={`${id}-purpose`} className={field} value={purposeId} onChange={event => onPurpose(event.target.value)}>
          <option value="">All purposes</option>
          {purposes.map(group => <option key={group.id} value={group.id}>{group.label}</option>)}
        </select>
      </label>
      <label htmlFor={`${id}-size`} className="min-w-0 text-xs font-semibold">
        {domain === 'street_pathway' ? 'Corridor width' : 'Default plot area'}
        <select id={`${id}-size`} className={field} value={facets.sizeId} onChange={event => onFacet('sizeId', event.target.value)}>
          <option value="">All sizes</option>
          {sizes.map(size => <option key={size.id} value={size.id}>{size.label}</option>)}
        </select>
      </label>
      {domain === 'building' && <label htmlFor={`${id}-style`} className="min-w-0 text-xs font-semibold">Architectural style
        <select id={`${id}-style`} className={field} value={facets.styleId} onChange={event => onFacet('styleId', event.target.value)}>
          <option value="">All styles</option>
          {styles.map(style => <option key={style.id} value={style.id}>{style.label}</option>)}
        </select>
      </label>}
    </div>
    <p className="pb-3 text-[11px] leading-relaxed text-slate-600">{domain === 'street_pathway'
      ? 'Width is the registered corridor width; you draw the route length.'
      : 'Size is the default reserved plot, not floor area. Drawn shapes can differ.'}
      {domain === 'building' && ' Styles use existing catalogue categories and tags; land-use types are design references.'}</p>
  </details>;
}
