import { useEffect, useId, useMemo, useRef, useState, type PointerEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api, getApiErrorMessage } from '@/services/api';
import { StudyEditorShell } from './StudyEditorShell';
import { CalgaryDistrictSelect } from './CalgaryDistrictSelect';
import { CatalogueMatches } from '@/features/zoningCatalogue/ZoningCatalogueCard';
import { CALGARY_COLOUR_SOURCE, CALGARY_CATALOGUE_DATE, CUSTOM_ZONE, districtChoices as bylawChoices } from './calgaryBylaw';
import type { StudyMapDrawing } from './useStudyMapDrawing';
import { referenceLayerQueryKey, referenceLayersApi, type ReferenceLayer } from './api';
import { fetchZoningLabels, type Position, type ZoningOverlay } from './zoningLabels';
import { CALGARY_BYLAW, readCalgaryDistrict, type CalgaryDistrict } from './calgaryDistricts';
import { clipStudyZones, closedRing, downloadStudy, drawnRingProblem, studyFrame, studyMetadata, studySvg,
  studyTitle, studyZones, studyDistrictColor, studyMapLabels, studyZoneName, studyZoneCaption, studyPreviewLayer, zonesFromCalgary, type StudyCondition, type StudyZone } from './zoningStudy';

interface Props {
  projectId: string; accountId: string; boundaryId: string; boundary: Position[]; projectName: string;
  layers: ReferenceLayer[]; canEdit: boolean; zoningData?: ZoningOverlay; onClose: () => void;
  mapDrawing?: StudyMapDrawing;
}
interface Slot { zones: StudyZone[]; past: StudyZone[][]; future: StudyZone[][]; baseHash: string|null; baseline: string; opacity: number; baselineOpacity: number }
const findLayer = (layers: ReferenceLayer[], condition: StudyCondition) => layers.find(layer => studyMetadata(layer)?.condition === condition);
const loadedSlot = (layer?: ReferenceLayer): Slot => { const zones=studyZones(layer); const opacity=layer?.opacity??0.4; return { zones, past:[], future:[], baseHash:layer?.content_hash??null, baseline:JSON.stringify(zones), opacity, baselineOpacity:opacity }; };
const button = 'min-h-11 rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-semibold text-stone-900 hover:bg-lime-50 disabled:opacity-40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900';

function persistDrafts(prefix:string, slots:Record<StudyCondition,Slot>) {
  for(const condition of ['existing','proposed'] as const) {
    const value=slots[condition];
    if(JSON.stringify(value.zones)===value.baseline && value.opacity===value.baselineOpacity) localStorage.removeItem(prefix+condition);
    else localStorage.setItem(prefix+condition,JSON.stringify({schema:1,zones:value.zones,baseHash:value.baseHash,opacity:value.opacity}));
  }
}

function readDraft(key: string, saved: Slot): Slot {
  try {
    const raw=localStorage.getItem(key)??'null';
    if(raw.length>2*1024*1024) return saved;
    const value=JSON.parse(raw);
    if (value?.schema!==1 || !Array.isArray(value.zones) || value.zones.length>256) return saved;
    if (value.baseHash!==null && !/^[a-f0-9]{64}$/.test(value.baseHash)) return saved;
    const invalidPoint=(p:Position)=>!Array.isArray(p) || p.length!==2 || !p.every(Number.isFinite) || Math.abs(p[0])>180 || Math.abs(p[1])>85;
    const invalidRing=(ring:Position[])=>!Array.isArray(ring) || ring.length<4 || ring.length>4096 || ring.some(invalidPoint) || ring[0][0]!==ring[ring.length-1][0] || ring[0][1]!==ring[ring.length-1][1];
    const invalidZone=(zone:StudyZone)=>!zone || typeof zone.id!=='string' || !/^[a-zA-Z0-9_-]{1,80}$/.test(zone.id)
      || typeof zone.label!=='string' || zone.label.length>120 || !/^#[\da-f]{6}$/i.test(zone.color)
      || zone.district !== undefined && !readCalgaryDistrict(zone.district)
      || zone.custom !== undefined && typeof zone.custom !== 'boolean' || Boolean(zone.custom && zone.district)
      || !['student','calgary-extract'].includes(zone.origin) || !Array.isArray(zone.rings) || !zone.rings.length || zone.rings.length>32 || zone.rings.some(invalidRing);
    if (value.zones.some(invalidZone) || new Set(value.zones.map((zone:StudyZone)=>zone.id)).size!==value.zones.length) return saved;
    if(value.zones.reduce((sum:number,zone:StudyZone)=>sum+zone.rings.reduce((n,ring)=>n+ring.length,0),0)>50_000) return saved;
    return { ...saved, zones:value.zones.map((zone:StudyZone)=>({...zone,
      district:readCalgaryDistrict(zone.district)??(zone.origin==='calgary-extract'?readCalgaryDistrict({designation:zone.label}):undefined),
    })), baseHash:value.baseHash??null, opacity:typeof value.opacity==='number'&&Number.isFinite(value.opacity)&&value.opacity>=0&&value.opacity<=1?value.opacity:saved.opacity };
  } catch { return saved; }
}

export default function ZoningStudyEditor({ projectId, accountId, boundaryId, boundary, projectName, layers, canEdit, zoningData, onClose, mapDrawing }: Props) {
  const queryClient=useQueryClient();
  const draftPrefix=`cityprompt:zoning-study-v1:${accountId}:${projectId}:${JSON.stringify([boundaryId,boundary])}:`;
  const [slots,setSlots]=useState<Record<StudyCondition,Slot>>(()=>({
    existing:readDraft(draftPrefix+'existing',loadedSlot(findLayer(layers,'existing'))),
    proposed:readDraft(draftPrefix+'proposed',loadedSlot(findLayer(layers,'proposed'))),
  }));
  const [condition,setCondition]=useState<StudyCondition>('existing');
  const [newType,setNewType]=useState('R-CG');
  const [customName,setCustomName]=useState('');
  const [customColour,setCustomColour]=useState('#75b6b0');
  const [showPlan,setShowPlan]=useState(false);
  const [selected,setSelected]=useState<string|null>(null);
  const [corner,setCorner]=useState(0);
  const [drawing,setDrawing]=useState(false);
  const [points,setPoints]=useState<Position[]>([]);
  const [preview,setPreview]=useState<StudyZone[]|null>(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState<string|null>(null);
  const [notice,setNotice]=useState<string|null>(null);
  const [storageProblem,setStorageProblem]=useState(false);
  const [exporting,setExporting]=useState(false);
  const svg=useRef<SVGSVGElement>(null);
  const clipId=`study-boundary-${useId().replace(/[^a-zA-Z0-9_-]/g,'')}`;
  const drag=useRef<{ zoneId:string; corner:number; zones:StudyZone[] }|null>(null);
  const controller=useRef<AbortController|null>(null);
  const slot=slots[condition];
  const zones=preview??slot.zones;
  const active=zones.find(zone=>zone.id===selected);
  const districtChoices=useMemo(()=>{
    const choices=new Map<string,CalgaryDistrict>();
    for(const zone of zoningData?.districts??[]) choices.set(zone.label,{
      designation:zone.label,code:zone.code,description:zone.description,
    });
    // Keep saved modifiers and DC references selectable even when offline.
    for(const zone of [...slots.existing.zones,...slots.proposed.zones]) if(zone.district) {
      const previous=choices.get(zone.district.designation);
      choices.set(zone.district.designation,{...previous,...zone.district});
    }
    return bylawChoices([...choices.values()]);
  },[zoningData,slots.existing.zones,slots.proposed.zones]);
  const outer=active?.rings[0]?.slice(0,-1)??[];
  const dirty=useMemo(()=>JSON.stringify(slot.zones)!==slot.baseline||slot.opacity!==slot.baselineOpacity,[slot.zones,slot.baseline,slot.opacity,slot.baselineOpacity]);
  const latestSlots=useRef(slots);
  latestSlots.current=slots;
  const frame=useMemo(()=>studyFrame(boundary),[boundary]);
  const mapLabels=useMemo(()=>studyMapLabels(zones,boundary),[zones,boundary]);
  const currentSaved=findLayer(layers,condition);
  const conflict=(currentSaved?.content_hash??null)!==slot.baseHash;
  const earlierBoundary=currentSaved && JSON.stringify(studyMetadata(currentSaved)?.boundaryCoordinates)!==JSON.stringify(boundary);

  useEffect(()=>()=>controller.current?.abort(),[]);
  const globePreview=useMemo(()=>studyPreviewLayer(zones,boundary,condition,1),[zones,boundary,condition]);
  useEffect(()=>{mapDrawing?.preview({...globePreview,opacity:slot.opacity});},[mapDrawing,globePreview,slot.opacity]);
  useEffect(()=>()=>{mapDrawing?.cancel();mapDrawing?.preview(null);},[mapDrawing]);
  useEffect(()=>{
    if (!canEdit) return;
    const flush=()=>{try{persistDrafts(draftPrefix,latestSlots.current);}catch{/* Debounced persistence reports storage failures while mounted. */}};
    window.addEventListener('beforeunload',flush);
    window.addEventListener('pagehide',flush);
    return ()=>{window.removeEventListener('beforeunload',flush);window.removeEventListener('pagehide',flush);flush();};
  },[draftPrefix,canEdit]);
  useEffect(()=>{
    if (!canEdit) return;
    const timer=setTimeout(()=>{
      try{persistDrafts(draftPrefix,slots);setStorageProblem(false);}catch{setStorageProblem(true);}
    },300);
    return ()=>clearTimeout(timer);
  },[slots,draftPrefix,canEdit]);

  const change=(next:StudyZone[])=>{
    setSlots(previous=>{const value=previous[condition];return {...previous,[condition]:{...value,zones:next,past:[...value.past,value.zones].slice(-30),future:[]}};});
    setError(null);setNotice(null);
  };
  const restore=(direction:'past'|'future')=>{
    setSlots(previous=>{const value=previous[condition];const source=value[direction];if(!source.length)return previous;
      const opposite=direction==='past'?'future':'past';return {...previous,[condition]:{...value,zones:source[source.length-1],[direction]:source.slice(0,-1),[opposite]:[...value[opposite],value.zones].slice(-30)}};
    });setSelected(null);setPreview(null);setError(null);
  };
  const updateZone=(patch:Partial<StudyZone>)=>change(slot.zones.map(zone=>zone.id===selected?{...zone,...patch}:zone));
  const select=(id:string)=>{setSelected(id);setCorner(0);};
  const switchCondition=(next:StudyCondition)=>{mapDrawing?.cancel();setCondition(next);setSelected(null);setPoints([]);setDrawing(false);setPreview(null);setError(null);setNotice(null);};
  const coordinates=(event:PointerEvent<SVGSVGElement|SVGCircleElement>):Position=>{
    const matrix=svg.current!.getScreenCTM()!;
    const point=new DOMPoint(event.clientX,event.clientY).matrixTransform(matrix.inverse());
    return frame.unproject([point.x,point.y]);
  };
  const changedCorner=(list:StudyZone[],id:string,index:number,point:Position)=>list.map(zone=>zone.id!==id?zone:{...zone,origin:'student' as const,rings:[closedRing(zone.rings[0].slice(0,-1).map((p,i)=>i===index?point:p)),...zone.rings.slice(1)]});
  const commitGeometry=async(next:StudyZone[],id:string,chosenCorner=corner)=>{
    const target=next.find(zone=>zone.id===id);
    const chosenPoint=target?.rings[0][chosenCorner];
    if(target && target.rings[0].length<=129) {const problem=drawnRingProblem(target.rings[0].slice(0,-1));if(problem){setError(problem);setPreview(null);return;}}
    setBusy(true);
    try {
      const clipped=await clipStudyZones(next,boundary);
      const pieces=clipped.filter(zone=>zone.id===id || zone.id.startsWith(id+'-'));
      if(!pieces.length)throw new Error('Keep part of this zone inside the site.');
      // Clipping can rotate the ring's starting vertex or split a polygon.
      // Keep the moved physical corner selected rather than its old array index.
      if(chosenPoint) {
        let closest={id:pieces[0].id,index:0,distance:Infinity};
        for(const piece of pieces) piece.rings[0].slice(0,-1).forEach((point,index)=>{
          const distance=Math.hypot((point[0]-chosenPoint[0])*Math.cos(chosenPoint[1]*Math.PI/180),point[1]-chosenPoint[1]);
          if(distance<closest.distance)closest={id:piece.id,index,distance};
        });
        setSelected(closest.id);setCorner(closest.index);
      }
      change(clipped);
    }
    catch(cause){setError(getApiErrorMessage(cause,'The outline could not be changed.'));}
    finally{setPreview(null);setBusy(false);}
  };
  const finish=async(drawnPoints:Position[]=points)=>{
    const problem=drawnRingProblem(drawnPoints);if(problem){setError(problem);return;}
    const district=districtChoices.find(choice=>choice.designation===newType);
    const custom=newType===CUSTOM_ZONE;
    if(!custom&&!district){setError('Choose a Calgary district or a custom zone.');return;}
    const zone:StudyZone={id:crypto.randomUUID(),label:custom?customName.trim():district!.designation,color:custom?customColour:studyDistrictColor(district!.designation),district,custom,origin:'student',rings:[closedRing(drawnPoints)]};
    setBusy(true);
    try{const clipped=await clipStudyZones([zone],boundary);if(!clipped.length)throw new Error('Draw inside the site boundary.');change([...slot.zones,...clipped]);setSelected(clipped[0].id);setCorner(0);setPoints([]);setDrawing(false);}
    catch(cause){setError(getApiErrorMessage(cause,'This outline could not finish.'));}finally{setBusy(false);setDrawing(false);}
  };
  const copyCalgary=async()=>{
    setBusy(true);setError(null);controller.current?.abort();controller.current=new AbortController();
    try {const data=zoningData??await fetchZoningLabels(boundary,AbortSignal.any([controller.current.signal,AbortSignal.timeout(30_000)]));
      const clipped=await clipStudyZones(zonesFromCalgary(data),boundary);change(clipped);setSelected(null);setNotice('Calgary outlines, full district designations and descriptions copied. You can undo this replacement.');
    }catch(cause){setError(getApiErrorMessage(cause,'Calgary outlines could not load.'));}finally{setBusy(false);}
  };
  const save=async()=>{
    setBusy(true);setError(null);const savedCondition=condition;const submitted=slot.zones;
    try {
      const response=await api.put<ReferenceLayer>(`/api/v1/zoning-studies/projects/${projectId}/${condition}`,{
        boundary_id:boundaryId,boundary_coordinates:boundary,expected_hash:slot.baseHash,zones:submitted,opacity:slot.opacity,
      });
      const canonical=studyZones(response.data);
      const opacity=response.data.opacity??slot.opacity;
      setSlots(previous=>({...previous,[savedCondition]:{...previous[savedCondition],zones:canonical,baseHash:response.data.content_hash??null,baseline:JSON.stringify(canonical),opacity,baselineOpacity:opacity}}));
      await queryClient.invalidateQueries({queryKey:referenceLayerQueryKey(projectId)});
      setNotice(`${studyTitle(savedCondition)} saved as its own map layer.`);
    }catch(cause){setError(getApiErrorMessage(cause,'The study could not save. Your draft is kept.'));}finally{setBusy(false);}
  };
  const reloadShared=async()=>{
    setBusy(true);setError(null);
    try{const response=await referenceLayersApi.list(projectId);queryClient.setQueryData(referenceLayerQueryKey(projectId),response);
      const latest=loadedSlot(findLayer(response.layers,condition));
      setSlots(previous=>({...previous,[condition]:{...latest,past:[...previous[condition].past,previous[condition].zones].slice(-30)}}));
      setSelected(null);setNotice('Shared version loaded. Undo restores your previous draft.');
    }catch(cause){setError(getApiErrorMessage(cause,'The shared version could not load.'));}finally{setBusy(false);}
  };
  const exportMap=async(format:'svg'|'png')=>{
    setExporting(true);setError(null);
    try {await downloadStudy(studySvg(slot.zones,boundary,projectName,condition),`cityprompt-${condition}-zoning`,format);setNotice(`${format.toUpperCase()} map exported.`);}
    catch(cause){setError(getApiErrorMessage(cause,'This map could not export.'));}finally{setExporting(false);}
  };

  const startDrawing=()=>{
    setDrawing(true);setSelected(null);setPoints([]);setError(null);
    if(mapDrawing&&!showPlan) mapDrawing.begin(coordinates=>{
      const drawn=coordinates.map(([x,y])=>[x,y] as Position);
      const problem=drawnRingProblem(drawn);if(problem){setError(problem);return false;}
      void finish(drawn);return true;
    },()=>{setDrawing(false);setPoints([]);});
  };
  return <StudyEditorShell globe={Boolean(mapDrawing)} onClose={onClose}>
    <p className="mb-3 text-xs leading-relaxed text-stone-600">1. Use your saved site boundary. 2. Choose a zone type. 3. Draw its corners{mapDrawing?' on the Google 3D map':''}. Save existing and proposed land use as separate layers.</p>
    <div className="mb-4 flex flex-wrap gap-2" role="tablist" aria-label="Study conditions">
      {(['existing','proposed'] as const).map(value=><button key={value} role="tab" aria-selected={condition===value} disabled={busy} className={`${button} ${condition===value?'!border-stone-900 !bg-lime-200':''}`} onClick={()=>switchCondition(value)}>{value==='existing'?'Existing conditions':'Proposed land use'}</button>)}
    </div>
    <div className={`grid items-start gap-4 ${mapDrawing?'':'lg:grid-cols-[minmax(0,1fr)_260px]'}`}>
      <div className="min-w-0">
        <div className="mb-3 space-y-2 rounded-xl border border-stone-200 bg-white/80 p-3 text-sm">
          <CalgaryDistrictSelect label="New zone type" value={newType} choices={districtChoices} disabled={!canEdit||busy||drawing} onChange={setNewType}/>
          {newType===CUSTOM_ZONE?<>
            <label className="block text-xs">Custom zone name<input aria-label="Custom zone name" value={customName} maxLength={120} disabled={!canEdit||busy||drawing} onChange={event=>setCustomName(event.target.value)} className="mt-1 min-h-11 w-full rounded-lg border border-stone-300 px-2"/></label>
            <label className="flex min-h-11 items-center justify-between text-xs">Custom colour<input aria-label="Custom colour" type="color" value={customColour} disabled={!canEdit||busy||drawing} onChange={event=>setCustomColour(event.target.value)} className="h-11 w-14"/></label>
          </>:<p className="flex items-center gap-2 text-xs text-stone-600"><span className="h-4 w-4 border border-stone-300" style={{backgroundColor:studyDistrictColor(newType)}}/>Calgary land-use class colour</p>}
        </div>
        <div className="mb-2 flex flex-wrap gap-2">
          <button className={button} disabled={!canEdit||busy||drawing||(newType===CUSTOM_ZONE&&!customName.trim())} onClick={startDrawing}>Draw zone</button>
          {drawing && <>{(!mapDrawing||showPlan)&&<button className={button} disabled={busy||points.length<3} onClick={()=>void finish()}>Finish zone</button>}<button className={button} disabled={busy} onClick={()=>{mapDrawing?.cancel();setPoints([]);setDrawing(false);}}>Cancel drawing</button></>}
          <button className={button} disabled={!canEdit||busy||!slot.past.length||drawing} onClick={()=>restore('past')}>Undo</button>
          <button className={button} disabled={!canEdit||busy||!slot.future.length||drawing} onClick={()=>restore('future')}>Redo</button>
        </div>
        <p className="mb-2 text-xs text-stone-600">{drawing?mapDrawing&&!showPlan?'Click or tap corners on the map; press Enter or use the map’s Finish button. Esc cancels. Shapes are clipped to your site.':`${points.length} corners · click or tap each corner, then finish. Shapes are clipped to the site.`:'Choose an area below to edit its type, caption or corners.'}</p>
        <div className="mb-3 space-y-2 rounded-xl border border-stone-200 bg-white/80 p-3">
        <label className="block text-xs font-semibold">Map fill opacity · {Math.round(slot.opacity*100)}%<input aria-label="Study fill opacity" type="range" min={0} max={100} step={1} value={Math.round(slot.opacity*100)} disabled={!canEdit||busy} onChange={event=>{const opacity=Number(event.target.value)/100;setSlots(previous=>({...previous,[condition]:{...previous[condition],opacity}}));}} className="mt-2 min-h-11 w-full accent-stone-800"/></label>
        <button className={`${button} w-full !border-stone-900 !bg-stone-900 !text-white`} disabled={!canEdit||busy||drawing||!dirty||!slot.zones.every(zone=>zone.label.trim())} onClick={()=>void save()}>{busy?'Working…':'Save map layer'}</button>
        <p role="status" className="text-xs text-stone-600">{!canEdit?'View and export only · an editor can change this study.':dirty?storageProblem?'Draft is in this tab only. Keep it open and save.':'Unsaved study · draft kept on this device.':slot.baseHash?'Study matches the saved map layer.':'No study saved yet.'}</p>
        {notice&&<p role="status" className="rounded-lg bg-lime-50 p-2 text-xs text-stone-800">{notice}</p>}
        {error&&<p role="alert" className="rounded-lg bg-amber-50 p-2 text-xs text-amber-950">{error}</p>}
        </div>
        {mapDrawing&&<button className={`${button} mb-2 w-full`} disabled={drawing||busy} onClick={()=>setShowPlan(!showPlan)}>{showPlan?'Return to drawing on Google 3D':'Open 2D corner editor'}</button>}
        <div hidden={Boolean(mapDrawing&&!showPlan)}>
        <svg ref={svg} role="application" aria-label="Zoning drawing canvas" tabIndex={0} viewBox="0 0 1000 760" className={`w-full rounded-xl border border-stone-300 bg-[#fffdf5] ${drawing?'cursor-crosshair':''}`} style={{touchAction:'none',userSelect:'none'}}
          onKeyDown={event=>{if(event.key==='Enter'&&drawing){event.preventDefault();void finish();}}}
          onPointerDown={event=>{if(drawing&&canEdit&&!busy){event.preventDefault();const point=coordinates(event);setPoints(previous=>previous.length<128?[...previous,point]:previous);}}}
          onPointerMove={event=>{if(drag.current)setPreview(changedCorner(drag.current.zones,drag.current.zoneId,drag.current.corner,coordinates(event)));}}
          onPointerUp={event=>{const current=drag.current;if(!current)return;drag.current=null;void commitGeometry(changedCorner(current.zones,current.zoneId,current.corner,coordinates(event)),current.zoneId,current.corner);}}
          onPointerCancel={()=>{drag.current=null;setPreview(null);}}>
          <text x="60" y="50" fontSize="25" fontWeight="700" fill="#252821">{studyTitle(condition)}</text>
          <text x="60" y="78" fontSize="14" fill="#5e6659">{projectName.slice(0,65)}</text>
          <defs><clipPath id={clipId}><path d={frame.path([closedRing(boundary)])}/></clipPath></defs>
          <path d={frame.path([closedRing(boundary)])} fill="#eeede4"/>
          <g clipPath={`url(#${clipId})`}>{zones.map(zone=><g key={zone.id}>
            <path d={frame.path(zone.rings)} fill={zone.color} fillRule="evenodd" stroke={zone.id===selected?'#141b12':'#34362f'} strokeWidth={zone.id===selected?3.5:1.5} role="button" aria-label={`Select ${studyZoneName(zone)}`} tabIndex={drawing?-1:0}
              onKeyDown={event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();select(zone.id);}}}
              onPointerDown={event=>{if(!drawing){event.stopPropagation();select(zone.id);}}}/>
          </g>)}</g>
          <path d={frame.path([closedRing(boundary)])} fill="none" stroke="#252821" strokeWidth="3" pointerEvents="none"/>
          {mapLabels.map(({id,text,point,leader,unassigned})=><g key={id} pointerEvents="none">
            {leader&&<path d={`M${leader.join(',')}L${point[0]},${point[1]-8}`} fill="none" stroke="#64685d" strokeWidth="1"/>}
            <text x={point[0]} y={point[1]} textAnchor="middle" fontSize="20" fontWeight="600" fill="#252821" paintOrder="stroke" stroke="#fffdf5" strokeWidth="3" strokeLinejoin="round">{text}{unassigned&&<tspan x={point[0]} dy="20" fontSize="12" fontWeight="400">District unassigned</tspan>}</text>
          </g>)}
          {!drawing&&canEdit&&outer.length<=128&&outer.map((point,i)=>{const [x,y]=frame.project(point);return <g key={i}>
            <circle cx={x} cy={y} r="32" fill="transparent" className="cursor-move" onPointerDown={event=>{if(busy)return;event.preventDefault();event.stopPropagation();setCorner(i);drag.current={zoneId:selected!,corner:i,zones:slot.zones};svg.current!.setPointerCapture(event.pointerId);}}/>
            <circle cx={x} cy={y} r="7" fill={i===corner?'#c9ff3d':'white'} stroke="#252821" strokeWidth="2" pointerEvents="none"/>
          </g>;})}
          {drawing&&<><polyline points={points.map(point=>frame.project(point).join(',')).join(' ')} fill="none" stroke="#252821" strokeWidth="3" strokeDasharray="8 5"/>{points.map((point,i)=>{const [x,y]=frame.project(point);return <circle key={i} cx={x} cy={y} r="6" fill="#c9ff3d" stroke="#252821" strokeWidth="2"/>;})}</>}
          <path d="M930 135V95M920 110L930 95L940 110" fill="none" stroke="#252821" strokeWidth="2"/><text x="930" y="85" textAnchor="middle" fontSize="16">N</text>
          <path d={`M60 695v-7h${frame.scaleM*frame.scale}v7`} fill="none" stroke="#252821" strokeWidth="2"/><text x="60" y="716" fontSize="13">{frame.scaleM} m · approximate</text>
          <text x="60" y="746" fontSize="12" fill="#5e6659">{condition==='existing'?'Existing conditions · student interpretation':'Proposed land use · student concept'} · study colours</text>
        </svg>
        </div>
        <details open={!mapDrawing} className="mb-3 rounded-xl border border-stone-200 p-3"><summary className="min-h-8 cursor-pointer text-xs font-semibold">Map key, export and sources</summary>
        {!!slot.zones.length&&<dl className="mt-3 grid gap-x-5 gap-y-3 text-xs sm:grid-cols-2" aria-label="District key">
          {[...new Map(slot.zones.map(zone=>[JSON.stringify([studyZoneName(zone),zone.label,zone.color]),zone])).values()].map(zone=><div key={zone.id}>
            <dt className="flex items-center gap-2 font-semibold"><span aria-hidden className="h-3 w-3 shrink-0 border border-stone-400" style={{backgroundColor:zone.color}}/>{studyZoneName(zone)}{!zone.district&&!zone.custom&&' · district unassigned'}</dt>
            <dd className="mt-1 pl-5 text-stone-600">{[zone.district?.description,studyZoneCaption(zone)].filter(Boolean).join(' · ')||(!zone.district?'Concept area':'District description unavailable in this saved study.')}</dd>
          </div>)}
        </dl>}
        <div className="mt-3 flex flex-wrap gap-2"><button className={button} disabled={exporting||drawing||busy} onClick={()=>void exportMap('svg')}>Export SVG</button><button className={button} disabled={exporting||drawing||busy} onClick={()=>void exportMap('png')}>Export PNG</button></div>
        <p className="mt-3 text-xs leading-relaxed text-stone-600"><a className="underline" href={CALGARY_BYLAW} target="_blank" rel="noreferrer">Calgary bylaw districts</a> · <a className="underline" href={CALGARY_COLOUR_SOURCE} target="_blank" rel="noreferrer">City land-use class colours</a> · catalogue {CALGARY_CATALOGUE_DATE}. Student concepts; zoning compliance is not checked.</p>
        </details>
      </div>
      <aside aria-label="Zone editing" className="space-y-3 text-sm">
        <button className={`${button} w-full`} disabled={!canEdit||busy||drawing} onClick={()=>void copyCalgary()}>Copy Calgary outlines</button>
        {condition==='proposed'&&<button className={`${button} w-full`} disabled={!canEdit||busy||drawing||!slots.existing.zones.length} onClick={()=>{change(slots.existing.zones.map(zone=>({...zone,id:crypto.randomUUID()})));setSelected(null);}}>Copy existing study</button>}
        {active&&<div className="space-y-3 rounded-xl border border-stone-200 p-3">
          <CalgaryDistrictSelect label="Calgary district" disabled={!canEdit||busy||drawing} value={active.custom?CUSTOM_ZONE:active.district?.designation??''} choices={districtChoices} onChange={value=>{
            const district=districtChoices.find(choice=>choice.designation===value);
            updateZone({district,custom:value===CUSTOM_ZONE,origin:'student',
              ...(active.label===active.district?.designation?{label:district?.designation??'Custom zone'}:{}),
              ...(district?{color:studyDistrictColor(district.designation)}:{}),
            });
          }}/>
          {active.district&&<p className="text-xs leading-relaxed text-stone-600">{active.district.description||'Saved district designation. Copy Calgary outlines to retrieve current source descriptions.'}{active.district.code==='DC'&&' Direct Control: review the specific bylaw for this designation.'}</p>}
          <details className="rounded-xl border border-stone-200 bg-[#fffdf6] p-3"><summary className="min-h-11 cursor-pointer text-xs font-bold">Catalogue matches for this zone</summary><CatalogueMatches zone={{ id: active.id, label: active.label, source: studyTitle(condition), district: active.district, custom: active.custom }} /></details>
          <label className="block font-semibold">Map caption<input aria-label="Map caption" disabled={!canEdit||busy} maxLength={120} value={active.label} onChange={event=>updateZone({label:event.target.value})} className="mt-1 min-h-11 w-full rounded-lg border-stone-300 text-sm"/></label>
          <label className="flex min-h-11 items-center justify-between font-semibold">Zone colour<input aria-label="Zone colour" type="color" disabled={!canEdit||busy||Boolean(active.district)} value={active.color} onChange={event=>updateZone({color:event.target.value})} className="h-11 w-14 cursor-pointer"/></label>
          {active.district&&<p className="text-xs text-stone-600">Colour follows the City class. Choose Custom zone to use your own colour.</p>}
          {outer.length<=128&&<><label className="block">Corner<select aria-label="Selected corner" className="mt-1 min-h-11 w-full rounded-lg border-stone-300 text-sm" value={Math.min(corner,Math.max(0,outer.length-1))} onChange={event=>setCorner(Number(event.target.value))}>{outer.map((_,i)=><option key={i} value={i}>Corner {i+1}</option>)}</select></label><p className="text-xs text-stone-600">Move selected corner 1 metre</p><div className="grid grid-cols-2 gap-1">{([['north',0,-1],['east',1,0],['south',0,1],['west',-1,0]] as const).map(([name,x,y])=><button key={name} className={button} disabled={!canEdit||busy||!outer[corner]} onClick={()=>{const point=frame.project(outer[corner]);void commitGeometry(changedCorner(slot.zones,active.id,corner,frame.unproject([point[0]+x*frame.scale,point[1]+y*frame.scale])),active.id);}}>Move {name}</button>)}</div></>}
          {outer.length>128&&<p className="text-xs text-stone-600">This detailed source outline has {outer.length} corners. Draw a simpler replacement to reshape it.</p>}
          <button className={`${button} w-full`} disabled={!canEdit||busy} onClick={()=>{change(slot.zones.filter(zone=>zone.id!==active.id));setSelected(null);}}>Remove zone</button>
        </div>}
        <div className="max-h-52 overflow-y-auto rounded-xl border border-stone-200" aria-label="Study zones">{slot.zones.map(zone=><button key={zone.id} className={`flex min-h-11 w-full items-center gap-2 border-b border-stone-100 px-3 py-2 text-left ${selected===zone.id?'bg-lime-100':''}`} onClick={()=>select(zone.id)}><span aria-hidden className="h-3 w-3 shrink-0 rounded" style={{backgroundColor:zone.color}}/><span><span className={zone.district?'font-semibold':''}>{studyZoneName(zone)||'Untitled zone'}</span>{' '}{studyZoneCaption(zone)&&<span className="block text-xs text-stone-600">{studyZoneCaption(zone)}</span>}</span></button>)}{!slot.zones.length&&<p className="p-3 text-stone-600">Start with Calgary outlines or draw your own zones.</p>}</div>
        {(conflict||earlierBoundary)&&<p className="text-xs text-amber-900">{conflict?'The shared version changed. Your draft keeps its previous revision.':'This study belongs to an earlier site boundary. Review and clip its shapes before saving.'}</p>}
        {earlierBoundary&&<button className={button} disabled={!canEdit||busy} onClick={()=>{setBusy(true);void clipStudyZones(slot.zones,boundary).then(change).catch(cause=>setError(String(cause))).finally(()=>setBusy(false));}}>Clip to current boundary</button>}
        <button className={`${button} w-full`} disabled={busy||drawing} onClick={()=>void reloadShared()}>Reload shared version</button>
      </aside>
    </div>
  </StudyEditorShell>;
}
