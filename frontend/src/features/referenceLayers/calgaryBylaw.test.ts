import { describe, expect, it } from 'vitest';
import { CALGARY_DISTRICTS, calgaryDistrictColour, districtChoices } from './calgaryBylaw';
import { studyPreviewLayer, studySvg, studyZones, type StudyZone } from './zoningStudy';
import type { Position } from './zoningLabels';

describe('Calgary bylaw drawing catalogue', () => {
  it('provides unique bylaw codes offline and preserves full source DC designations', () => {
    expect(new Set(CALGARY_DISTRICTS.map(d=>d.designation)).size).toBe(CALGARY_DISTRICTS.length);
    for (const code of ['R-CG','H-GO','MU-2','S-SPR','I-G']) expect(CALGARY_DISTRICTS.some(d=>d.code===code)).toBe(true);
    expect(CALGARY_DISTRICTS.some(d=>['DC','ANRI','RF'].includes(d.designation))).toBe(false);
    expect(districtChoices([{designation:'DC48Z84',code:'DC'}]).some(d=>d.designation==='DC48Z84')).toBe(true);
  });
  it('matches published City class RGB values, including modifiers and similar code prefixes', () => {
    expect(calgaryDistrictColour('R-CG')).toBe('#fff7da');
    expect(calgaryDistrictColour('M-CGd72')).toBe('#ffefa9');
    expect(calgaryDistrictColour('M-H2 f4.0 h30')).toBe('#ffe672');
    expect(calgaryDistrictColour('S-SPR')).toBe('#d3e6bd');
    expect(calgaryDistrictColour('MU-2f4.0h24')).toBe('#e99aad');
    expect(calgaryDistrictColour('DC48Z84')).toBe('#ceb2cd');
    expect(calgaryDistrictColour('R-CG-invented')).toBe('#c9c9c9');
  });
  it('keeps a custom area distinct from statutory districts through preview, reload and export', () => {
    const boundary:Position[]=[[-114.1,51.05],[-114.099,51.05],[-114.099,51.051],[-114.1,51.051]];
    const custom:StudyZone={id:'custom',label:'Community garden',color:'#75b6b0',custom:true,origin:'student',rings:[[...boundary,boundary[0]]]};
    const layer=studyPreviewLayer([custom],boundary,'proposed',1);
    expect(layer.opacity).toBe(1);
    expect(studyZones(layer)).toEqual([custom]);
    const exported=studySvg(studyZones(layer),boundary,'Trial','proposed');
    expect(exported).toContain('Custom · Community garden');
    expect(exported).not.toContain('District unassigned');
    expect(exported).toContain('#75b6b0');
  });
});
