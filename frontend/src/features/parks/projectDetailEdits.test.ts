import { describe,expect,it,vi } from 'vitest';
import { validateDetailEdits } from './projectDetailEdits';
describe('preserve untouched supported details',()=>{
 const original={id:'p',lng:-114.12345678901,lat:51.12345678901,angle:300,variant:'calgary_delineator_illustrative_r1',support_zone_id:'road'};
 it('preserves exact originals through property ordering and editor rounding without requiring the old road to be loaded',()=>{
  const validate=vi.fn(()=>({ok:false as const,message:'not loaded'}));
  const reordered={id:'p',support_zone_id:'road',lng:-114.123456789,lat:51.123456789,angle:-60,variant:original.variant};
  const result=validateDetailEdits([reordered],[original],validate);
  expect(result[0]).toBe(original);expect(validate).not.toHaveBeenCalled();
 });
 it('validates changed positions and retains the authoritative support reference',()=>{
  const validate=vi.fn(()=>({ok:true as const,hostId:'new-road'}));
  const result=validateDetailEdits([{...original,lng:original.lng+.001}],[original],validate);
  expect(validate).toHaveBeenCalledOnce();expect(result[0].support_zone_id).toBe('new-road');
 });
 it('rejects an unsupported change and permits deletion without needing its old host',()=>{
  const validate=vi.fn(()=>({ok:false as const,message:'gap'}));
  expect(()=>validateDetailEdits([{...original,angle:45}],[original],validate)).toThrow('gap');
  expect(validateDetailEdits([], [original],validate)).toEqual([]);
 });
});
