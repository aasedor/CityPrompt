import { ArrowUpRight, Sparkles } from 'lucide-react';
import { CALGARY_GROUPS, type CatalogueDomain } from '@/features/calgaryCatalogue/guide';
import { choiceMatchesGroup, type CanonicalChoice } from './canonicalCatalogue';

import { CatalogueCategoryIllustration } from './CatalogueCategoryIllustration';

export function CatalogueCategoryTiles({ domain, choices, onChoose, onBrowseAll, onGenerated }: {
  domain: CatalogueDomain; choices: CanonicalChoice[]; onChoose: (id: string) => void;
  onBrowseAll: () => void; onGenerated?: () => void;
}) {
  const options = choices.filter(c => c.domain === domain && (domain !== 'street_pathway' || c.placements[0]?.kind === 'street'));
  const groups = CALGARY_GROUPS.filter(g => g.domain === domain).map(g => ({...g, count:options.filter(c => choiceMatchesGroup(c,g.id)).length})).filter(g => g.count > 0);
  const noun = domain === 'building' ? 'buildings' : domain === 'park_plaza' ? 'parks' : 'streets';
  return <div className="space-y-4 p-1">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <div><h3 className="text-xl font-black tracking-tight">What would you like to add?</h3><p className="mt-1 text-sm text-slate-600">Choose a category to explore its designs.</p></div>
      <button type="button" onClick={onBrowseAll} className="min-h-11 rounded-full border-2 border-[#232323] bg-[#fff9ec] px-4 text-xs font-bold hover:bg-[#c9ff3d]">Browse all {noun}</button>
    </div>
    <div className="grid grid-cols-2 gap-3 pb-2 lg:grid-cols-3">
      {groups.map((group,index) => <button key={group.id} type="button" aria-label={`Browse ${group.label}`} onClick={() => onChoose(group.id)}
        className="group relative flex min-h-44 flex-col items-start rounded-2xl border-2 border-[#232323] bg-[#fff9ec] px-4 pb-4 pt-2 text-left shadow-[3px_3px_0_#232323] transition-colors hover:bg-[#eef9cc] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[#232323]">
        <div className="flex w-full items-center justify-between"><span className={`rounded-full border border-[#232323] px-2 py-1 text-[10px] font-bold ${index%2?'bg-[#b5e4e2]':'bg-[#c9ff3d]'}`}>{group.count} {group.count===1?'design':'designs'}</span><ArrowUpRight size={19} aria-hidden="true" /></div>
        <div className="flex w-full justify-center transition-transform duration-200 motion-safe:group-hover:-translate-y-1"><CatalogueCategoryIllustration id={group.id} /></div>
        <span className="mt-1 text-sm font-extrabold leading-snug">{group.label}</span>
      </button>)}
      {onGenerated && <button type="button" onClick={onGenerated} className="flex min-h-44 flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed border-[#232323] bg-white p-4 text-sm font-bold hover:bg-lime-50"><Sparkles size={42} aria-hidden="true"/>Your generated buildings</button>}
    </div>
  </div>;
}
