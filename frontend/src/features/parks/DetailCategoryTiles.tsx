import type { ReactNode } from 'react';
import { ArrowUpRight } from 'lucide-react';
import { DETAIL_CATEGORIES, searchDetails } from './detailCatalogue';

const cream = '#fff9ec', lime = '#c9ff3d', teal = '#75c8c4', coral = '#f49c7f', blue = '#bce9ed';

function DetailIllustration({ category }: { category: string }) {
  const scenes: Record<string, () => ReactNode> = {
    'Access & levels': () => <><path d="m16 104 44 8 83-32-44-9z" fill={lime}/><path d="M25 99V85h23V70h23V55h23V40h27v45l-49 18z" fill={cream}/><path d="m48 85 25 6m-2-21 25 6m-2-21 25 6"/><path d="m75 105 66-29V61L75 90z" fill={teal}/><path d="M31 79V54l78-31v24m-54 9v28m29-40v23" fill="none" strokeWidth="4"/><path d="m75 90 66-29" stroke={coral} strokeWidth="5"/></>,
    Seating: () => <><path d="m28 72 86 8 26-16-86-8z" fill={coral}/><path d="M36 62V35l80 7v28z" fill={cream}/><path d="m39 44 70 7m-70 4 70 7M36 76v24m75-18v22m24-34v21"/><path d="M27 71V58m-5 0h20m79 15V58m-6 0h20" strokeWidth="4"/><path d="M19 106h126" stroke={teal} strokeWidth="4"/></>,
    Trees: () => <><path d="m24 101 61 13 59-20-61-10z" fill={lime}/><path d="M66 97V50m0 26L46 56m20 9 23-23" strokeWidth="5"/><path d="M65 65C27 70 21 45 40 33 37 4 82 3 86 26c34-3 38 42-21 39z" fill={lime}/><path d="M120 98V45"/><path d="m119 31-19 35h10l-19 20h57l-20-20h10z" fill={teal}/><path d="M66 65V37m0 16 13-12m-13 4-10-10" fill="none"/></>,
    'Street furniture': () => <><path d="M23 101V55a12 12 0 0 1 24 0v46m0 0V55a12 12 0 0 1 24 0v46" fill="none" stroke={teal} strokeWidth="6"/><path d="M99 100V49h36v51z" fill={cream}/><path d="M95 44h44v9H95z" fill={coral}/><path d="M107 64v25m10-25v25m10-25v25"/><path d="M18 105h129"/><circle cx="44" cy="84" r="21" fill="none" strokeWidth="2"/><path d="m44 84 9-16 14 16H44m8-16h13" fill="none"/></>,
    Landscape: () => <><path d="m15 106 94 8 42-22-93-10z" fill={lime}/><path d="m27 96 9-26 28-8 24 24-15 16z" fill={cream}/><path d="m80 97 8-22 25-2 23 24-22 7z" fill={teal}/><path d="m36 70 22 15 15 17m-15-17 6-23m25 14 15 14 10 14" fill="none"/><path d="M110 69V24m-17 5 17-11 19 7-18 11z" fill={coral}/><path d="M108 53q-22-4-25-20 27 0 25 20" fill={lime}/></>,
    Lighting: () => <><path d="M42 106V27q0-12 13-12h20m-14 0v9h26v-9z" fill={cream}/><path d="m65 29-22 49h57L83 29" fill={lime} stroke="none"/><path d="M42 106V27q0-12 13-12h20" fill="none" strokeWidth="4"/><path d="M107 105V57h17v48z" fill={teal}/><path d="M105 53h21v14h-21z" fill={cream}/><path d="M110 59h11" stroke={coral} strokeWidth="4"/><path d="M22 109h118"/><path d="M120 18v12m-6-6h12"/></>,
    'Edges & gates': () => <><path d="M24 106V38h12v68m89 0V38h12v68" fill={coral}/><path d="M36 99V48q43-34 89 0v51z" fill={cream}/><path d="M80 32v68M46 46v51m12-58v58m44-58v58m12-50v50M36 68h89"/><path d="M18 38h23v9H18zm102 0h23v9h-23z" fill={teal}/><circle cx="88" cy="75" r="3" fill={lime}/></>,
    'Garden & growing': () => <><path d="m23 73 75 12 40-25-74-10z" fill={lime}/><path d="M23 73v22l75 13V85zm75 12 40-25v22l-40 26z" fill={coral}/><path d="M50 71V42m27 34V33m26 41V47"/><path d="m50 59-13-13 13 4 12-16-12 25m27-5-13-13 13 4 12-16-12 25m26 9-13-13 13 4 12-16-12 25" fill={teal}/><path d="m18 108 125 8"/></>,
    Planting: () => <><path d="M57 85V43m27 42V21m23 64V51" strokeWidth="3"/><path d="M57 70q-30 0-27-26 28 3 27 26m27-13q28 0 28-24-27-2-28 24m23 19q28 0 27-20-25 0-27 20" fill={lime}/><path d="M39 81h86l-14 29H54z" fill={coral}/><path d="M36 79h91v9H36z" fill={cream}/><circle cx="84" cy="20" r="11" fill={coral}/><circle cx="84" cy="20" r="4" fill={lime}/></>,
    Play: () => <><path d="M29 104V51h41v53m-41-26h41m-41 14h41" fill="none" strokeWidth="4"/><path d="m22 51 29-25 26 25z" fill={coral}/><path d="M67 58q16 0 22 20t47 20v11q-50 0-58-23T67 72z" fill={teal}/><path d="M40 73V57m15 16V57"/><path d="M17 113h126" stroke={lime} strokeWidth="7"/><circle cx="120" cy="34" r="14" fill={lime}/><path d="m117 27 8 7-8 7" fill="none"/></>,
    'Sport & exercise': () => <><path d="M32 103V39h62v16" fill="none" strokeWidth="5"/><path d="M75 23h60v33H75z" fill={cream}/><path d="M95 36h19v20H95z" fill={teal}/><ellipse cx="107" cy="59" rx="17" ry="5" fill={coral}/><path d="m93 62 7 17h15l7-17m-22 17-1-15m16 15 1-15" fill="none"/><circle cx="69" cy="96" r="21" fill={coral}/><path d="M49 96h40M69 75v42m-14-36q27 15 0 29m28-29q-27 15 0 29" fill="none" strokeWidth="1.5"/></>,
    'Shelters & markets': () => <><path d="M29 106V48h103v58" fill="none" strokeWidth="4"/><path d="m21 48 60-32 60 32z" fill={coral}/><path d="m21 48 10 16 17-16 17 16 16-16 17 16 17-16 16 16 10-16" fill={cream}/><path d="M37 86h87v23H37z" fill={teal}/><path d="M35 80h91v9H35z" fill={cream}/><circle cx="52" cy="75" r="6" fill={lime}/><circle cx="65" cy="75" r="6" fill={lime}/><path d="M94 78V64h18v14z" fill={coral}/></>,
    'Water & landmarks': () => <><ellipse cx="81" cy="104" rx="57" ry="12" fill={teal}/><path d="M76 103V75h11v28" fill={cream}/><ellipse cx="81" cy="75" rx="33" ry="9" fill={blue}/><path d="M81 72V24m0 25Q53 6 37 44m44 5q28-43 44-5" fill="none" strokeWidth="3"/><path d="M37 49v9m88-9v9M57 93l-16 9m63-9 16 9" stroke={teal}/><circle cx="81" cy="22" r="5" fill={coral}/></>,
    'Traffic & safety': () => <><path d="M43 110V23h72" fill="none" strokeWidth="5"/><rect x="95" y="24" width="28" height="59" rx="8" fill={cream}/><circle cx="109" cy="36" r="6" fill={coral}/><circle cx="109" cy="53" r="6" fill="#ffc44c"/><circle cx="109" cy="70" r="6" fill={lime}/><path d="M65 111V80"/><path d="m65 51 17 17-17 17-17-17z" fill={coral}/><path d="m59 69 6-7 6 7m-6-7v14" fill="none"/><path d="M17 115q9-17 21 0h104" fill={teal}/></>,
  };
  return <svg viewBox="0 0 160 125" aria-hidden="true" focusable="false" className="h-28 w-full">
    <g stroke="#232323" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round">{(scenes[category] ?? scenes.Landscape)()}</g>
  </svg>;
}

export function DetailCategoryTiles({ onChoose, onBrowseAll }: { onChoose: (category: string) => void; onBrowseAll: () => void }) {
  return <div className="space-y-3 p-1">
    <div className="flex flex-wrap items-center justify-between gap-2"><h3 className="font-extrabold">Choose a detail category</h3>
      <button type="button" onClick={onBrowseAll} className="min-h-11 rounded-full border-2 border-[#232323] bg-white px-3 text-xs font-bold hover:bg-[#c9ff3d]">Browse all items</button></div>
    <div className="grid grid-cols-2 gap-3 pb-2">
      {DETAIL_CATEGORIES.map((category,index) => <button key={category} type="button" aria-label={`Browse ${category}`} onClick={() => onChoose(category)}
        className="group flex flex-col rounded-2xl border-2 border-[#232323] bg-[#fff9ec] px-3 pb-3 pt-2 text-left shadow-[3px_3px_0_#232323] hover:bg-[#eef9cc] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2">
        <span className="flex w-full items-center justify-between gap-1"><span className={`rounded-full border border-[#232323] px-2 py-1 text-[10px] font-bold ${index%2?'bg-[#b5e4e2]':'bg-[#c9ff3d]'}`}>{searchDetails('',category).length} items</span><ArrowUpRight size={18} aria-hidden="true"/></span>
        <span className="w-full transition-transform duration-200 motion-safe:group-hover:-translate-y-1"><DetailIllustration category={category}/></span>
        <span className="mt-1 text-sm font-extrabold leading-snug">{category}</span>
      </button>)}
    </div>
  </div>;
}
