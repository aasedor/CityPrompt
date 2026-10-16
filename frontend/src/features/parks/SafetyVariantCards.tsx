import { useState } from 'react';
import type { DetailAsset } from './detailCatalogue';

/** Preserve one stable asset ID per variant while browsing a compact family card. */
export function SafetyVariantCards({assets,selected,disabled,onChoose,thumbnail:Thumbnail}:{
  assets: DetailAsset[]; selected: string|null; disabled:boolean; onChoose:(id:string)=>void;
  thumbnail: React.ComponentType<{asset:DetailAsset}>;
}) {
  const families = new Map<string, DetailAsset[]>();
  assets.forEach(asset=>{const key=asset.safety!.group+':'+asset.safety!.family;families.set(key,[...(families.get(key)??[]),asset]);});
  return <>{[...families].map(([key,variants])=><SafetyFamily key={key} variants={variants} selected={selected} disabled={disabled} onChoose={onChoose} thumbnail={Thumbnail}/>)}</>;
}
function SafetyFamily({variants,selected,disabled,onChoose,thumbnail:Thumbnail}:{variants:DetailAsset[];selected:string|null;disabled:boolean;onChoose:(id:string)=>void;thumbnail:React.ComponentType<{asset:DetailAsset}>}) {
  const [choice,setChoice]=useState(variants[0].id);
  const asset=variants.find(a=>a.id===choice)??variants[0];
  const unavailable=asset.safety!.placement==='sidewalk-attachment';
  return <article className="overflow-hidden rounded-xl border border-slate-300 bg-white">
    <Thumbnail asset={asset}/>
    <div className="space-y-2 p-3">
      <h3 className="text-sm font-bold">{asset.safety!.familyLabel}</h3>
      <label className="block text-xs">Variant
        <select aria-label={`${asset.safety!.familyLabel} variant`} value={asset.id} disabled={disabled} onChange={e=>{setChoice(e.target.value);if(variants.some(a=>a.id===selected))onChoose(e.target.value);}} className="min-h-11 w-full rounded border bg-white px-1">
          {variants.map(a=><option key={a.id} value={a.id}>{a.safety!.variantLabel}</option>)}
        </select>
      </label>
      <p className="text-xs">{asset.dimensions.map(n=>n.toFixed(n>0&&n<.1?3:2)).join(' × ')} m · fixed size</p>
      <p className="text-xs text-slate-600">{asset.safety!.limitation}</p>
      {unavailable&&<p className="text-xs text-amber-900">Placement unavailable: matching sidewalk attachment and curb replacement are still being validated.</p>}
      <button type="button" aria-label={`Choose ${asset.label}`} aria-pressed={selected===asset.id} disabled={disabled||unavailable} onClick={()=>onChoose(asset.id)} className={`min-h-11 w-full rounded border px-2 text-sm font-bold disabled:opacity-50 ${selected===asset.id?'bg-lime-300':'bg-lime-100'}`}>{unavailable?'Awaiting sidewalk integration':'Choose & place'}</button>
    </div>
  </article>;
}
