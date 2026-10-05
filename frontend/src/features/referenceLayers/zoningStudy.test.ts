import { describe, expect, it } from 'vitest';
import { clipStudyZones, drawnRingProblem, studyFrame, studySvg, type StudyZone } from './zoningStudy';
import type { Position } from './zoningLabels';

const boundary:Position[]=[[-114.12,51.01],[-114.119,51.01],[-114.119,51.011],[-114.12,51.011]];
const zone:StudyZone={id:'zone',label:'Housing',color:'#dfb88b',origin:'student',rings:[[...boundary,boundary[0]]]};
describe('student zoning cartography',()=>{
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
