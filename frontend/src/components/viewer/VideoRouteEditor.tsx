import {useState} from 'react';
import {appendRoutePoint,normalizedRoutePoint,routeSvgPoints,type VideoRoutePoint} from './videoRenderPath';

/** Explicit edit session: point selection moves; empty-space clicks add. */
export function VideoRouteEditor({points,onChange,onClose,disabled=false}:{points:VideoRoutePoint[];onChange:(points:VideoRoutePoint[])=>void;onClose:()=>void;disabled?:boolean}) {
  const [original]=useState(()=>points);
  const [draft,setDraft]=useState(points);
  const [history,setHistory]=useState<VideoRoutePoint[][]>([]);
  const [selected,setSelected]=useState<number|null>(null);
  const change=(next:VideoRoutePoint[])=>{if(disabled||next===draft)return;setHistory(previous=>[...previous,draft]);setDraft(next);onChange(next);};
  const button='min-h-9 rounded-lg border border-white/30 bg-[#15292c] px-2 text-xs font-bold text-white disabled:opacity-40';
  return <div className="absolute inset-0">
    <div aria-label="Camera route drawing area" className="absolute inset-0 cursor-crosshair touch-none" onClick={event=>{
      if(disabled)return;
      const point=normalizedRoutePoint(event.clientX,event.clientY,event.currentTarget.getBoundingClientRect());
      if(selected!==null){change(draft.map((old,index)=>index===selected?point:old));setSelected(null);}
      else if(draft.length<24)change(appendRoutePoint(draft,point,.004));
    }}>
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="pointer-events-none absolute inset-0 h-full w-full">
        <polyline points={routeSvgPoints(draft)} fill="none" stroke="white" strokeWidth="1.8" vectorEffect="non-scaling-stroke"/>
        <polyline points={routeSvgPoints(draft)} fill="none" stroke="#ff3b4f" strokeWidth="1" vectorEffect="non-scaling-stroke"/>
      </svg>
      {draft.map((point,index)=><button type="button" key={index} disabled={disabled} aria-label={`Select route point ${index+1}`} aria-pressed={selected===index}
        style={{left:`${point.x*100}%`,top:`${point.y*100}%`}} className={`absolute -translate-x-1/2 -translate-y-1/2 h-8 w-8 rounded-full border-2 border-white text-xs font-black ${selected===index?'bg-[#c9ff3d] text-black':'bg-[#c42c40] text-white'}`}
        onClick={event=>{event.stopPropagation();setSelected(index);}}>{index+1}</button>)}
    </div>
    <div className="absolute left-2 right-2 top-2 flex flex-wrap gap-1 rounded-xl bg-black/75 p-2" onClick={event=>event.stopPropagation()}>
      <button type="button" className={button} disabled={disabled} onClick={()=>{change([]);setSelected(null);}}>Draw new route</button>
      <button type="button" className={button} disabled={disabled} onClick={()=>setSelected(null)}>Add points</button>
      <button type="button" className={button} disabled={disabled||selected===null} onClick={()=>{change(draft.filter((_,index)=>index!==selected));setSelected(null);}}>Remove selected point</button>
      <button type="button" className={button} disabled={disabled||!history.length} onClick={()=>{
        const previous=history[history.length-1];setHistory(history.slice(0,-1));setDraft(previous);onChange(previous);setSelected(null);
      }}>Undo route edit</button>
      <button type="button" className={button} disabled={disabled} onClick={onClose}>Done</button>
      <button type="button" className={button} disabled={disabled} onClick={()=>{onChange(original);onClose();}}>Cancel route edits</button>
      <p className="w-full text-[11px] text-white">{selected===null?'Click to add points. Select a numbered point, then click its new position.':'Click the new position for the selected point.'} {draft.length}/24 points.</p>
    </div>
  </div>;
}
