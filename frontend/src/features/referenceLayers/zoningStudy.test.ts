import { describe, expect, it } from 'vitest';
import { clipStudyZones, drawnRingProblem, studyFrame, studyMapLabels, studySvg, studyZones, zonesFromCalgary, type StudyZone } from './zoningStudy';
import type { ReferenceLayer } from './api';
import type { Position } from './zoningLabels';

const boundary:Position[]=[[-114.12,51.01],[-114.119,51.01],[-114.119,51.011],[-114.12,51.011]];
const zone:StudyZone={id:'zone',label:'Housing',color:'#dfb88b',origin:'student',rings:[[...boundary,boundary[0]]]};
describe('student zoning cartography',()=>{
  it('puts thin adjacent districts in separate callouts without clipping their full codes',()=>{
    const strips=[0,1].map((i)=>({...zone,id:`strip-${i}`,district:{code:'DC',designation:`DC100Z2006SITE${i+1}`},rings:[[
      [-114.12,51.01+i*.00001],[-114.119,51.01+i*.00001],[-114.119,51.010005+i*.00001],[-114.12,51.010005+i*.00001],[-114.12,51.01+i*.00001],
    ] as Position[]]}));
    const labels=studyMapLabels(strips,boundary);
    expect(labels).toHaveLength(2);
    expect(labels.every(label=>label.leader&&label.point[1]===674)).toBe(true);
    expect(Math.abs(labels[0].point[0]-labels[1].point[0])).toBeGreaterThan(190);
    expect(labels.map(label=>label.text)).toEqual(['DC100Z2006SITE1','DC100Z2006SITE2']);
    const svg=studySvg(strips,boundary,'Test','existing');
    expect(svg.indexOf('</g>')).toBeLessThan(svg.indexOf('font-size="20"'));
  });
  it('retains full district identity through copy, caption edits, clipping, reload and export',async()=>{
    const data={bounds:[-114.12,51.01,-114.119,51.011] as [number,number,number,number],loadedAt:'2026-10-05',districts:[
      {id:'one',label:'M-C1 d75',code:'M-C1',description:'Multi-Residential - Contextual Low Profile',anchor:boundary[0],polygon:zone.rings},
      {id:'two',label:'DC48Z84',code:'DC',description:'Direct Control',anchor:boundary[0],polygon:zone.rings},
    ]};
    const copied=zonesFromCalgary(data);
    const edited=await clipStudyZones(copied.map(z=>({...z,label:'Courtyard housing',origin:'student' as const})),boundary);
    const stored={feature_collection:{features:edited.map(z=>({id:z.id,geometry:{type:'Polygon',coordinates:z.rings},properties:z}))}} as unknown as ReferenceLayer;
    expect(studyZones(stored).map(z=>z.district)).toEqual([
      {code:'M-C1',designation:'M-C1 d75',description:'Multi-Residential - Contextual Low Profile'},
      {code:'DC',designation:'DC48Z84',description:'Direct Control'},
    ]);
    const svg=studySvg(studyZones(stored),boundary,'Test map','proposed');
    for(const value of ['M-C1 d75','DC48Z84','Courtyard housing','Direct Control','data.calgary.ca','compliance have not been checked']) expect(svg).toContain(value);
    const reordered=zonesFromCalgary({...data,districts:[...data.districts].reverse()});
    expect(reordered[0].color).toBe(copied[1].color);
    expect(reordered[1].color).toBe(copied[0].color);
  });
  it('recovers a legacy source designation without turning student labels into official districts',()=>{
    const stored={feature_collection:{features:['calgary-extract','student'].map(origin=>({id:origin,geometry:{type:'Polygon',coordinates:zone.rings},properties:{label:'DC48Z84',origin}}))}} as unknown as ReferenceLayer;
    const [source,student]=studyZones(stored);
    expect(source.district).toEqual({designation:'DC48Z84'});
    expect(student.district).toBeUndefined();
    expect(studySvg([student],boundary,'Test','proposed')).toContain('District unassigned');
  });
  it('round-trips map positions with north pointing up',()=>{
    const frame=studyFrame(boundary);
    for(const point of boundary) expect(frame.unproject(frame.project(point))).toEqual(point);
    expect(frame.project(boundary[2])[1]).toBeLessThan(frame.project(boundary[1])[1]);
  });
  it('clips drawings to an irregular boundary and retains interior holes',async()=>{
    const hole:Position[]=[[-114.1198,51.0102],[-114.1196,51.0102],[-114.1196,51.0104],[-114.1198,51.0104],[-114.1198,51.0102]];
    const result=await clipStudyZones([{...zone,rings:[zone.rings[0],hole]}],boundary);
    expect(result[0].rings).toHaveLength(2);
    const triangle=[boundary[0],boundary[1],boundary[2]];
    expect((await clipStudyZones([zone],triangle))[0].rings[0]).toHaveLength(4);
  });
  it('rejects self-crossing, collapsed and unfinished student outlines',()=>{
    expect(drawnRingProblem([boundary[0],boundary[2],boundary[3],boundary[1]])).toMatch(/crosses itself/);
    expect(drawnRingProblem(boundary.slice(0,2))).toMatch(/3–128/);
    expect(drawnRingProblem([boundary[0],boundary[0],boundary[1]])).toMatch(/adjacent/);
    expect(drawnRingProblem(boundary)).toBeNull();
  });
  it('escapes labels and titles, preserves holes and distinguishes proposed concepts in export',()=>{
    const svg=studySvg([{...zone,label:'<script>& "homes"'}],boundary,'Town & <plan>','proposed');
    expect(svg).toContain('Town &amp; &lt;plan&gt;');
    expect(svg).toContain('&lt;script&gt;&amp; &quot;homes&quot;');
    expect(svg).not.toContain('<script>');
    expect(svg).toContain('fill-rule="evenodd"');
    expect(svg).toContain('Proposed land-use concept');
    expect(svg).toContain('approximate');
  });
});
