import {describe, expect, it, vi} from 'vitest';
import {findSavedPhotographicVideo,preparePhotographicVideo} from './videoPhotographicWorkflow';

const request = {project_id:'p',purpose:'video_appearance' as const,beauty_image_base64:'native',source_video_sha256:'source',prompt:'daylight',source_request:{route_points:[{x:.1,y:.2}],details_revision:2}};
const guide = {purpose:'video_appearance' as const,attempt_id:'g',image_base64:'photo',source_video_sha256:'source',scene_revision_sha256:'scene',output_fingerprint:'pixels',model:'gpt-image-2.5-sunburst' as const,tokens_spent:26};
describe('paid video photographic preparation',()=>{
  it('looks up matching completed guides without creating, resuming or acknowledging jobs',async()=>{
    const client={list:vi.fn().mockResolvedValue([{id:'pending',status:'running'},{id:'g',status:'completed'}]),
      recover:vi.fn().mockResolvedValue({response:guide,source_request:request.source_request}),generate:vi.fn(),resume:vi.fn(),acknowledge:vi.fn()};
    expect(await findSavedPhotographicVideo(client as never,request)).toEqual(guide);
    expect(client.generate).not.toHaveBeenCalled();expect(client.resume).not.toHaveBeenCalled();expect(client.acknowledge).not.toHaveBeenCalled();
  });
  it.each([
    {response:{...guide,source_video_sha256:'other-recording'},source_request:request.source_request},
    {response:guide,source_request:{...request.source_request,details_revision:3}},
  ])('does not reuse a changed recording or source request during a free lookup',async(saved)=>{
    const client={list:vi.fn().mockResolvedValue([{id:'old',status:'completed'}]),recover:vi.fn().mockResolvedValue(saved),generate:vi.fn()};
    expect(await findSavedPhotographicVideo(client as never,request)).toBeNull();
    expect(client.generate).not.toHaveBeenCalled();
  });
  it('recovers a matching saved guide rather than buying another',async()=>{
    const client={list:vi.fn().mockResolvedValue([{id:'g',status:'completed'}]),recover:vi.fn().mockResolvedValue({response:guide,source_request:request.source_request}),generate:vi.fn()};
    expect(await preparePhotographicVideo(client as never,request,'scene')).toEqual(guide);
    expect(client.generate).not.toHaveBeenCalled();
  });
  it('matches canonical server JSON despite object key order and omitted optional fields',async()=>{
    const client={list:vi.fn().mockResolvedValue([{id:'g',status:'completed'}]),recover:vi.fn().mockResolvedValue({response:guide,
      source_request:{details_revision:2,route_points:[{y:.2,x:.1}]}}),generate:vi.fn().mockResolvedValue({...guide,attempt_id:'duplicate'})};
    expect(await preparePhotographicVideo(client as never,{...request,source_request:{...request.source_request,optional:undefined}},'scene')).toEqual(guide);
    expect(client.generate).not.toHaveBeenCalled();
  });
  it('buys one guide only when recovered source or scene does not match',async()=>{
    const client={list:vi.fn().mockResolvedValue([{id:'old',status:'completed'}]),recover:vi.fn().mockResolvedValue({response:{...guide,scene_revision_sha256:'old'},source_request:request.source_request}),generate:vi.fn().mockResolvedValue(guide)};
    expect(await preparePhotographicVideo(client as never,request,'scene')).toEqual(guide);
    expect(client.generate).toHaveBeenCalledOnce();
    expect(client.generate).toHaveBeenCalledWith(request);
  });
  it('does not buy when saved guide lookup fails or an earlier job is unresolved',async()=>{
    const client={list:vi.fn().mockResolvedValue([{id:'pending',status:'running'}]),resume:vi.fn().mockRejectedValue(new Error('The saved guide is still running')),recover:vi.fn(),generate:vi.fn()};
    await expect(preparePhotographicVideo(client as never,request,'scene')).rejects.toThrow(/running|saved/i);
    expect(client.generate).not.toHaveBeenCalled();
    client.list.mockRejectedValue(new Error('offline'));
    await expect(preparePhotographicVideo(client as never,request,'scene')).rejects.toThrow('offline');
    expect(client.generate).not.toHaveBeenCalled();
  });
  it('resumes a queued guide for this exact recording rather than requiring a manual recovery',async()=>{
    const client={list:vi.fn().mockResolvedValue([{id:'queued',status:'queued'}]),resume:vi.fn().mockResolvedValue({response:guide,source_request:request.source_request}),recover:vi.fn(),generate:vi.fn()};
    expect(await preparePhotographicVideo(client as never,request,'scene')).toEqual(guide);
    expect(client.generate).not.toHaveBeenCalled();
    expect(client.resume).toHaveBeenCalledOnce();
  });
  it('clears a terminal saved identity on the next explicit Generate action',async()=>{
    const stopped={id:'stopped',status:'unknown'};
    const client={list:vi.fn().mockResolvedValue([stopped]),acknowledge:vi.fn(),recover:vi.fn(),generate:vi.fn().mockResolvedValue(guide)};
    expect(await preparePhotographicVideo(client as never,request,'scene')).toEqual(guide);
    expect(client.acknowledge).toHaveBeenCalledWith(stopped);
    expect(client.generate).toHaveBeenCalledOnce();
  });
});
