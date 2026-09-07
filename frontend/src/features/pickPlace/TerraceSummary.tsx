import {useMemo} from 'react';
import type {SiteZone} from '@/types';
import {buildTerraceScene} from '@/components/viewer/globe/terraceScene';
import {terraceOffset} from '@/components/viewer/globe/terraceDefinition';
import {assetForZone} from './catalogue';
import {readParkTerrain} from '@/components/viewer/globe/parkTerrain';

export function TerraceSummary({zones}:{zones:SiteZone[]}) {
  const scene=useMemo(()=>buildTerraceScene(zones,0),[zones]);
  const parks=zones.filter(z=>z.properties?.park_terrain);
  if(!scene.terraces.length&&!scene.paths.length&&!parks.length)return null;
  const name=(id:string)=>{const z=zones.find(v=>v.id===id);return z?.name||(z&&assetForZone(z)?.label)||'Removed object';};
  const lines=scene.terraces.map(z=>`${name(z.id)}: ${terraceOffset(z)!.toFixed(1)} m relative to the site level.`);
  for(const park of parks) {
    const s=readParkTerrain(park);
    lines.push(`${name(park.id)}: ${s ? 'lawn and paths follow saved hillside measurements; local activity pads remain level. Review path grades and landings.' : 'ground needs review after a move or resize.'}`);
  }
  for(const p of scene.paths)lines.push(`${name(p.ownerId)} → ${name(p.targetId)}: ${p.reason}`);
  const notes='Live concept grading review. Check building entrances, drainage, retaining edges, landings and connections to existing sidewalks. This is not an accessibility or engineering assessment. No routes to existing Google sidewalks are inferred.';
  return <section aria-label="Terrace access review" className="mb-4 rounded-xl border border-amber-300 bg-amber-50 p-4 text-slate-900">
    <h2 className="font-bold">Terrace access · current plan</h2>
    <ul className="my-2 list-disc space-y-1 pl-5 text-sm">{lines.map((line,i)=><li key={i}>{line}</li>)}</ul>
    <p className="text-xs">{notes}</p>
    <button className="mt-2 min-h-11 rounded border border-slate-600 bg-white px-3 text-sm" onClick={()=>{
      const url=URL.createObjectURL(new Blob([`Terrace access review\n${new Date().toISOString()}\n\n${lines.join('\n')}\n\n${notes}\n`],{type:'text/plain;charset=utf-8'}));
      const a=document.createElement('a');a.href=url;a.download='terrace-access-review.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    }}>Download terrace notes</button>
    <p className="mt-1 text-xs">These live notes are a separate attachment to the saved planning report.</p>
  </section>;
}
