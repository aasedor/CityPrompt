import { useId, useState } from 'react';
import { CALGARY_GROUPS, CALGARY_GUIDE_REVIEWED, CALGARY_SOURCES, calgaryGroup, filterCalgaryCatalogue, type CalgaryBrowsable, type CalgaryClassification, type CatalogueDomain } from './guide';

const PAGE_SIZE = 12;
const FIELD_CLASS = 'min-h-11 w-full rounded border border-primary-950/20 bg-white px-2 text-xs text-primary-950';

/** Browsing is local UI state: changing a filter must never edit a student's model. */
export function useCatalogueBrowser<T extends CalgaryBrowsable & { categoryId?: string }>(options: T[]) {
  const [groupId, setGroup] = useState('');
  const [query, setQuery] = useState('');
  const [styleId, setStyle] = useState('');
  const [limit, setLimit] = useState(PAGE_SIZE);
  const filtered = filterCalgaryCatalogue(options, groupId, query).filter(option => !styleId || option.categoryId === styleId);
  return {
    options: filtered, limit,
    props: { options, groupId, query, styleId, count: filtered.length,
      onGroup: (value: string) => { setGroup(value); setLimit(PAGE_SIZE); },
      onQuery: (value: string) => { setQuery(value); setLimit(PAGE_SIZE); },
      onStyle: (value: string) => { setStyle(value); setLimit(PAGE_SIZE); },
      onReset: () => { setGroup(''); setQuery(''); setStyle(''); setLimit(PAGE_SIZE); },
    },
    more: filtered.length > limit ? <button type="button" onClick={() => setLimit(value => value + PAGE_SIZE)}
      className={`${FIELD_CLASS} font-semibold`}>Show more choices ({filtered.length - limit} remaining)</button> : null,
  };
}

export function CalgaryGuideDetails({ classification }: { classification?: CalgaryClassification }) {
  const definition = calgaryGroup(classification);
  if (!definition) return null;
  return <details className="rounded bg-slate-50 p-2 text-xs text-slate-700">
    <summary className="cursor-pointer font-semibold">Calgary guide · {definition.label}</summary>
    <p className="mt-2">{definition.note}</p>
    {definition.districts.length > 0 && <p className="mt-1">Districts to explore: {definition.districts.join(' · ')}.</p>}
    {classification?.basis === 'draft_manual' && <p className="mt-1 font-semibold text-amber-900">This catalogue section is based on a draft Street Manual; it is not an approved construction section.</p>}
    <p className="mt-1">A catalogue reference does not establish permission on your parcel. Check the current district, local plan and site conditions.</p>
    <ul className="mt-2 space-y-1">
      {definition.sources.map(id => <li key={id}><a className="underline" href={CALGARY_SOURCES[id].url} target="_blank" rel="noreferrer">{CALGARY_SOURCES[id].label}</a><span className="block text-[10px]">{CALGARY_SOURCES[id].status}</span></li>)}
      <li><a className="underline" href={CALGARY_SOURCES.localPlans.url} target="_blank" rel="noreferrer">Check local area guidance</a></li>
    </ul>
    <p className="mt-2 text-[10px]">Sources reviewed {CALGARY_GUIDE_REVIEWED}. Design freely; explain the steps needed to make it possible.</p>
  </details>;
}

export function CatalogueBrowserControls({ domain, categories, options, groupId, query, styleId, count, onGroup, onQuery, onStyle, onReset }: {
  domain: CatalogueDomain; categories: { id: string; label: string }[]; options: CalgaryBrowsable[];
  groupId: string; query: string; styleId: string; count: number;
  onGroup: (value: string) => void; onQuery: (value: string) => void; onStyle: (value: string) => void; onReset: () => void;
}) {
  const id = useId();
  const groups = CALGARY_GROUPS.filter(group => group.domain === domain && options.some(option => option.calgaryGuide?.groupId === group.id));
  return <section aria-label="Calgary catalogue browser" className="space-y-2 rounded-lg border border-slate-200 bg-white p-2">
    <label htmlFor={`${id}-group`} className="block text-xs font-bold text-slate-900">Browse by purpose · Calgary guide</label>
    <select id={`${id}-group`} className={FIELD_CLASS} value={groupId} onChange={event => onGroup(event.target.value)}>
      <option value="">All types</option>
      {groups.map(group => <option key={group.id} value={group.id}>{group.label}{group.districts.length ? ` · e.g. ${group.districts[0]}` : ''}</option>)}
    </select>
    <label htmlFor={`${id}-search`} className="sr-only">Search catalogue or district code</label>
    <input id={`${id}-search`} className={FIELD_CLASS} type="search" placeholder={domain === 'building' ? 'Search homes, R-C1, townhomes…' : 'Search park or street types…'} value={query} onChange={event => onQuery(event.target.value)} />
    <details>
      <summary className="cursor-pointer text-xs text-slate-700">Filter appearance / existing category{styleId ? ' · active' : ''}</summary>
      <label htmlFor={`${id}-style`} className="sr-only">Appearance category</label>
      <select id={`${id}-style`} className={`${FIELD_CLASS} mt-1`} value={styleId} onChange={event => onStyle(event.target.value)}>
        <option value="">All appearances</option>
        {categories.map(category => <option key={category.id} value={category.id}>{category.label}</option>)}
      </select>
    </details>
    {groupId && <CalgaryGuideDetails classification={{ groupId, basis: domain === 'building' ? 'form_reference' : 'design_reference' }} />}
    {domain === 'street_pathway' && <p className="text-[11px] text-slate-600">Street Manual assets use draft guidance. <a href={CALGARY_SOURCES.streetManual.url} target="_blank" rel="noreferrer" className="underline">Check publication status</a>.</p>}
    <div className="flex items-center justify-between gap-2 text-xs text-slate-700"><span role="status">{count} {count === 1 ? 'choice' : 'choices'}{count === 0 ? ' · try another type or search' : ''}</span>
      {(groupId || query || styleId) && <button type="button" onClick={onReset} className="min-h-11 underline">Reset filters</button>}
    </div>
    <p className="text-[10px] text-slate-600">References for exploring ideas; parcel permissions need a separate review.</p>
  </section>;
}
