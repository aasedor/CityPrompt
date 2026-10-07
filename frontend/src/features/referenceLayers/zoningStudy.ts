import type { ReferenceLayer } from './api';
import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { readCalgaryDistrict, type CalgaryDistrict } from './calgaryDistricts';
import { calgaryDistrictColour } from './calgaryBylaw';
import { ZONING_SOURCE, zoningAnchor, zoningBounds, type Position, type ZoningOverlay } from './zoningLabels';

export type StudyCondition = 'existing' | 'proposed';
export interface StudyZone { id: string; label: string; color: string; origin: 'student' | 'calgary-extract'; rings: Position[][]; district?: CalgaryDistrict; custom?: boolean }
export interface StudyDocument { zones: StudyZone[]; baseHash: string | null }
export const STUDY_PALETTE = ['#dfb88b', '#d99782', '#9eaf91', '#90adbb', '#c5b1cc', '#e4d19c', '#b5b5aa'];
export const studyTitle = (condition: StudyCondition) => condition === 'existing' ? 'Existing zoning study' : 'Proposed land-use study';

export function studyMetadata(layer: ReferenceLayer) {
  const metadata = (layer.feature_collection as unknown as { _citypromptStudy?: { schema: number; condition: StudyCondition; boundaryCoordinates: Position[] } })._citypromptStudy;
  return metadata?.schema === 1 && ['existing', 'proposed'].includes(metadata.condition) ? metadata : undefined;
}
export function studyZones(layer?: ReferenceLayer): StudyZone[] {
  return layer?.feature_collection.features.flatMap(feature => feature.geometry.type === 'Polygon' ? [{
    id: String(feature.id), label: String(feature.properties.label || 'Zone'),
    color: /^#[\da-f]{6}$/i.test(String(feature.properties.color)) ? String(feature.properties.color) : '#9eaf91',
    origin: feature.properties.origin === 'calgary-extract' ? 'calgary-extract' as const : 'student' as const,
    ...(feature.properties.custom === true ? { custom: true } : {}),
    // Older City copies saved only the full designation as their label. Keep it;
    // never infer a district from an arbitrary student caption.
    district: readCalgaryDistrict(feature.properties.district) ?? (feature.properties.origin === 'calgary-extract'
      ? readCalgaryDistrict({ designation: feature.properties.label }) : undefined),
    rings: feature.geometry.coordinates.map(ring => ring.map(([x, y]) => [x, y] as Position)),
  }] : []) ?? [];
}
/** City's published Land Use Class renderer; custom colours remain student-authored. */
export const studyDistrictColor = calgaryDistrictColour;
export const studyZoneName = (zone: StudyZone) => zone.custom ? `Custom · ${zone.label}` : zone.district?.designation ?? zone.label;
export const studyZoneCaption = (zone: StudyZone) => zone.district && zone.label !== zone.district.designation ? zone.label : '';
export const zonesFromCalgary = (data: ZoningOverlay): StudyZone[] => data.districts.map(zone => ({
  id: crypto.randomUUID(), label: zone.label, origin: 'calgary-extract',
  district: { designation: zone.label, ...(zone.code ? { code: zone.code } : {}), ...(zone.description ? { description: zone.description } : {}) },
  color: studyDistrictColor(zone.label), rings: zone.polygon,
}));

export function studyPreviewLayer(zones: StudyZone[], boundary: Position[], condition: StudyCondition, opacity: number): ReferenceLayer {
  const collection = { type: 'FeatureCollection' as const, _citypromptStudy: { schema: 1, condition, boundaryCoordinates: boundary },
    features: zones.map(zone => ({ type: 'Feature' as const, id: zone.id, geometry: { type: 'Polygon' as const, coordinates: zone.rings },
      properties: { label: zone.label, color: zone.color, origin: zone.origin, district: zone.district, custom: zone.custom } })) };
  return { id: 'study-live-preview', project_id: '', name: studyTitle(condition), source_filename: '', source_crs: 'EPSG:4326', source_url: null,
    description: null, kind: 'zoning', feature_collection: collection, feature_count: zones.length, bounds: zoningBounds(boundary)!,
    warnings: [], color: '#34362f', opacity, created_at: '' };
}

export function closedRing(points: Position[]): Position[] {
  const first = points[0], last = points[points.length-1];
  return !first || first[0] === last?.[0] && first[1] === last?.[1] ? points : [...points, [...first] as Position];
}

/** Reject self-crossing hand-drawn rings before clipping; holes in imported
 * polygons are retained by polygon-clipping and validated again on the server. */
export function drawnRingProblem(points: Position[]): string | null {
  if (points.length < 3 || points.length > 128) return 'Draw 3–128 corners before finishing the zone.';
  const origin = points[0];
  const scale = 111320 * Math.cos(origin[1] * Math.PI / 180);
  const p = points.map(([x,y]) => [(x-origin[0])*scale, (y-origin[1])*111320]);
  const cross = (a: number[], b: number[], c: number[]) => (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  const on = (a: number[], b: number[], c: number[]) => Math.abs(cross(a,b,c)) < 1e-7 && c[0] >= Math.min(a[0],b[0])-1e-7 && c[0] <= Math.max(a[0],b[0])+1e-7 && c[1] >= Math.min(a[1],b[1])-1e-7 && c[1] <= Math.max(a[1],b[1])+1e-7;
  for (let i=0; i<p.length; i++) {
    const a=p[i], b=p[(i+1)%p.length];
    if (Math.hypot(a[0]-b[0], a[1]-b[1]) < .1) return 'Leave a little space between adjacent corners.';
    for (let j=i+2; j<p.length; j++) {
      if (i===0 && j===p.length-1) continue;
      const c=p[j], d=p[(j+1)%p.length];
      if (cross(a,b,c)*cross(a,b,d)<0 && cross(c,d,a)*cross(c,d,b)<0 || on(a,b,c) || on(a,b,d) || on(c,d,a) || on(c,d,b)) return 'The zone outline crosses itself. Undo or move the corner back.';
    }
  }
  const area = Math.abs(p.reduce((sum,a,i) => { const b=p[(i+1)%p.length]; return sum+a[0]*b[1]-b[0]*a[1]; },0))/2;
  return area < 1 ? 'Give this zone at least one square metre of area.' : null;
}

export async function clipStudyZones(zones: StudyZone[], boundary: Position[]): Promise<StudyZone[]> {
  const { default: clipping } = await import('polygon-clipping');
  const site = [closedRing(boundary)];
  const clipped = zones.flatMap(zone => clipping.intersection(zone.rings, site).map((rings, i, pieces) => ({
    ...zone, id: pieces.length === 1 ? zone.id : `${zone.id.slice(0,70)}-${i}`, rings,
  })));
  if (clipped.length > 256) throw new Error('Keep the study to 256 zones or fewer.');
  if (clipped.some(zone=>zone.rings.length>32 || zone.rings.some(ring=>ring.length>4096))) throw new Error('Use simpler outlines: each zone supports 32 rings and 4,096 points per ring.');
  if (clipped.reduce((sum, zone) => sum + zone.rings.reduce((n, ring) => n + ring.length, 0), 0) > 50_000) throw new Error('This study has too many corners. Use simpler outlines.');
  return clipped;
}

export function studyFrame(boundary: Position[]) {
  const bounds = zoningBounds(boundary);
  if (!bounds) throw new Error('Draw a valid boundary first.');
  const [west,south,east,north] = bounds;
  const lonM = 111320 * Math.cos((north+south)/2 * Math.PI/180);
  const widthM = (east-west)*lonM, heightM=(north-south)*111320;
  const scale = Math.min(860/widthM, 540/heightM);
  const x0 = (1000-widthM*scale)/2, y0 = 110+(540-heightM*scale)/2;
  const project = ([x,y]: Position): Position => [x0+(x-west)*lonM*scale, y0+(north-y)*111320*scale];
  const unproject = ([x,y]: Position): Position => [west+(x-x0)/lonM/scale, north-(y-y0)/111320/scale];
  const path = (rings: Position[][]) => rings.map(ring => ring.map((point,i) => `${i?'L':'M'}${project(point).map(v=>v.toFixed(3)).join(',')}`).join(' ')+'Z').join(' ');
  const labelPoint = (zone: StudyZone) => { const anchor=zoningAnchor(zone.rings); return anchor ? project(anchor) : null; };
  const scaleSteps = [1,2,5,10,20,50,100,200,500,1000].filter(value=>value*scale<=150);
  const scaleM = scaleSteps[scaleSteps.length-1] ?? .5;
  return { project, unproject, path, labelPoint, scale, scaleM };
}

const xml = (text: string) => text.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]!));
/** Keep full codes readable. Thin areas get leaders into the map margins;
 * crowded maps retain every designation in the district key. */
export function studyMapLabels(zones: StudyZone[], boundary: Position[]) {
  const frame=studyFrame(boundary);
  type Label={id:string; text:string; point:Position; leader?:Position; unassigned:boolean};
  const placed:Label[]=[];
  const boxes:{x:number;y:number;width:number;height:number}[]=[];
  const pending:{zone:StudyZone;text:string;anchor:Position;width:number;height:number}[]=[];
  const boxAt=(point:Position,width:number,height:number)=>({x:point[0]-width/2,y:point[1]-18,width,height});
  const free=(box:ReturnType<typeof boxAt>)=>!boxes.some(b=>box.x<b.x+b.width+8&&box.x+box.width+8>b.x&&box.y<b.y+b.height+6&&box.y+box.height+6>b.y);
  for(const zone of zones) {
    const anchor=frame.labelPoint(zone);
    if(!anchor)continue;
    const name=studyZoneName(zone), text=zone.district?name:name.length>28?name.slice(0,26)+'…':name;
    const width=Math.max(text.length*11,!zone.district?155:0)+12, height=zone.district?25:44;
    const bounds=zoningBounds(zone.rings[0])!;
    const center=frame.project([(bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2]);
    const point=[center,anchor].find(candidate=>{
      const box=boxAt(candidate,width,height);
      return free(box)&&[0,.5,1].every(x=>[0,.5,1].every(y=>booleanPointInPolygon(frame.unproject([box.x+x*width,box.y+y*height]),{type:'Polygon',coordinates:zone.rings})));
    });
    if(point){placed.push({id:zone.id,text,point,unassigned:!zone.district&&!zone.custom});boxes.push(boxAt(point,width,height));}
    else pending.push({zone,text,anchor,width,height});
  }
  for(const item of pending) {
    const {zone,text,anchor,width,height}=item;
    const xs:number[]=[];
    for(let x=60+width/2;x<=910-width/2;x+=20)xs.push(x);
    xs.sort((a,b)=>Math.abs(a-anchor[0])-Math.abs(b-anchor[0]));
    // Two-line concept captions that do not fit remain in the district key.
    // Margin callouts leave titles, north arrow and scale bar clear.
    if(height>25)continue;
    const rows=anchor[1]>380?[674,96]:[96,674];
    const point=rows.flatMap(y=>xs.map(x=>[x,y] as Position)).find(candidate=>free(boxAt(candidate,width,height)));
    if(point){placed.push({id:zone.id,text,point,leader:anchor,unassigned:!zone.district&&!zone.custom});boxes.push(boxAt(point,width,height));}
  }
  return placed;
}
/** Deterministic vector export: same geometry, labels and colours as the editor. */
export function studySvg(zones: StudyZone[], boundary: Position[], title: string, condition: StudyCondition): string {
  const frame = studyFrame(boundary);
  const legend = [...new Map(zones.map(zone => [JSON.stringify([studyZoneName(zone),zone.label,zone.color]),zone])).values()];
  const wrap = (text: string) => text.match(/.{1,58}(?:\s|$)|\S{1,58}/g)?.map(line=>line.trim()) ?? [];
  const legendLines = legend.map(zone=>wrap([studyZoneCaption(zone),zone.district?.description,
    !zone.district&&!zone.custom?'District unassigned':undefined].filter(Boolean).join(' · ')));
  const rowHeight = 30 + Math.max(1,...legendLines.map(lines=>lines.length))*16;
  const height = 805 + Math.ceil(legend.length/2)*rowHeight;
  const paths=zones.map(zone=>`<path d="${frame.path(zone.rings)}" fill="${zone.color}" fill-rule="evenodd" stroke="#34362f" stroke-width="1.5"><title>${xml([studyZoneName(zone),studyZoneCaption(zone),zone.district?.description].filter(Boolean).join(' · '))}</title></path>`).join('');
  const labels=studyMapLabels(zones,boundary).map(({text,point,leader,unassigned})=>`${leader?`<path d="M${leader.join(',')}L${point[0]},${point[1]-8}" fill="none" stroke="#64685d" stroke-width="1"/>`:''}<text x="${point[0]}" y="${point[1]}" text-anchor="middle" paint-order="stroke" stroke="#fffdf5" stroke-width="3" stroke-linejoin="round" fill="#252821" font-size="20" font-weight="600">${xml(text)}${unassigned?`<tspan x="${point[0]}" dy="20" font-size="12" font-weight="400">District unassigned</tspan>`:''}</text>`).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="${height*2}" viewBox="0 0 1000 ${height}" font-family="Arial, Helvetica, sans-serif"><title>${xml(title)}</title><defs><clipPath id="site-boundary"><path d="${frame.path([closedRing(boundary)])}"/></clipPath></defs><rect width="1000" height="${height}" fill="#fffdf5"/><text x="60" y="48" font-size="27" font-weight="700">${xml(title.length>60?title.slice(0,58)+'…':title)}</text><text x="60" y="78" font-size="14" fill="#5e6659">${studyTitle(condition)} · student graphic</text><path d="${frame.path([closedRing(boundary)])}" fill="#eeede4"/><g clip-path="url(#site-boundary)">${paths}</g><path d="${frame.path([closedRing(boundary)])}" fill="none" stroke="#252821" stroke-width="3"/>${labels}<path d="M930 135V95M920 110L930 95L940 110" fill="none" stroke="#252821" stroke-width="2"/><text x="930" y="85" text-anchor="middle" font-size="16">N</text><path d="M60 695v-7h${frame.scaleM*frame.scale}v7" fill="none" stroke="#252821" stroke-width="2"/><text x="60" y="716" font-size="13">${frame.scaleM} m · approximate</text><text x="60" y="746" font-size="12" fill="#5e6659">${condition==='existing'?'Student interpretation; consult official districts for statutory zoning.':'Proposed land-use concept; statutory zoning remains unchanged.'}</text><a href="${ZONING_SOURCE}"><text x="60" y="765" font-size="12" fill="#5e6659">District references: City of Calgary Land Use Districts · editable study colours</text></a><text x="60" y="784" font-size="12" fill="#5e6659">Uses, height, density and DC bylaw compliance have not been checked.</text>${legend.map((zone,i)=>{
    const x=60+(i%2)*460, y=809+Math.floor(i/2)*rowHeight;
    return `<rect x="${x}" y="${y}" width="16" height="16" fill="${zone.color}"/><text x="${x+24}" y="${y+13}" font-size="13" font-weight="700">${xml(studyZoneName(zone))}</text>${legendLines[i].map((line,j)=>`<text x="${x+24}" y="${y+31+j*16}" font-size="12" fill="#5e6659">${xml(line)}</text>`).join('')}`;
  }).join('')}</svg>`;
}

export async function downloadStudy(svg: string, filename: string, format: 'svg'|'png') {
  const source = new Blob([svg], { type:'image/svg+xml;charset=utf-8' });
  const sourceUrl = URL.createObjectURL(source);
  let downloadUrl = sourceUrl;
  let clicked = false;
  try {
    if (format==='png') {
      const image = new Image();
      await new Promise<void>((resolve,reject) => { image.onload=()=>resolve(); image.onerror=()=>reject(new Error('The map image could not export. Try SVG.')); image.src=sourceUrl; });
      const canvas = document.createElement('canvas');
      // Bound pixel count even when a long legend needs extra height.
      const scale = Math.min(1, 2600/image.height, Math.sqrt(6_000_000/(image.width*image.height)));
      canvas.width=Math.round(image.width*scale); canvas.height=Math.round(image.height*scale);
      canvas.getContext('2d')!.drawImage(image,0,0,canvas.width,canvas.height);
      const blob = await new Promise<Blob>((resolve,reject)=>canvas.toBlob(value=>value?resolve(value):reject(new Error('Try exporting SVG instead.')),'image/png'));
      downloadUrl=URL.createObjectURL(blob);
    }
    const link=document.createElement('a'); link.href=downloadUrl; link.download=`${filename}.${format}`; link.click();
    clicked = true;
    setTimeout(()=>URL.revokeObjectURL(downloadUrl), 1000);
  } finally {
    if(downloadUrl!==sourceUrl) URL.revokeObjectURL(sourceUrl);
    if(!clicked) URL.revokeObjectURL(downloadUrl);
  }
}
