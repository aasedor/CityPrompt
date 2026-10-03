import {afterEach,it,expect,vi} from 'vitest';
import {RoadTerrainTrialController,TerrainTilesChangedError} from './roadTerrainTrialController';

const trial=()=>({status:vi.fn(()=>({active:true,stale:false})),setVisible:vi.fn(),dispose:vi.fn()});
afterEach(()=>vi.useRealTimers());

it('remeasures after refinement, with only one queued build',async()=>{
  vi.useFakeTimers();const first=trial(),second=trial(),create=vi.fn().mockResolvedValueOnce(first).mockResolvedValue(second);
  const controller=new RoadTerrainTrialController(create,vi.fn());controller.build();await vi.advanceTimersByTimeAsync(0);
  first.status.mockReturnValue({active:false,stale:true});controller.checkFreshness();controller.checkFreshness();
  expect(first.dispose).toHaveBeenCalledOnce();expect(create).toHaveBeenCalledOnce();
  await vi.advanceTimersByTimeAsync(1500);expect(create).toHaveBeenCalledTimes(2);expect(controller.trial).toBe(second);controller.dispose();
});

it('bounds automatic attempts and does not retry geometry failures',async()=>{
  vi.useFakeTimers();const create=vi.fn().mockRejectedValue(new TerrainTilesChangedError('refining')),changed=vi.fn();
  const c=new RoadTerrainTrialController(create,changed);c.build();await vi.runAllTimersAsync();
  expect(create).toHaveBeenCalledTimes(4);expect(changed.mock.lastCall?.[0]).toBe('error');
  create.mockRejectedValue(new Error('Object intersects the wall'));c.build();await vi.runAllTimersAsync();
  expect(create).toHaveBeenCalledTimes(5);expect(changed.mock.lastCall?.[2].message).toMatch(/Object/);c.dispose();
});

it('preserves Show original during tile changes and cancels pending refreshes',async()=>{
  vi.useFakeTimers();const t=trial(),create=vi.fn().mockResolvedValue(t),changed=vi.fn();
  const c=new RoadTerrainTrialController(create,changed);c.build();await vi.advanceTimersByTimeAsync(0);
  c.show(false);t.status.mockReturnValue({active:false,stale:true});c.checkFreshness();await vi.runAllTimersAsync();
  expect(create).toHaveBeenCalledOnce();expect(changed.mock.lastCall?.[0]).toBe('original');
  c.show(true);await vi.advanceTimersByTimeAsync(0);c.checkFreshness();c.show(false);await vi.runAllTimersAsync();
  expect(create).toHaveBeenCalledTimes(2);c.dispose();
});

it('aborts superseded builds and disposes late results after hide or unmount',async()=>{
  vi.useFakeTimers();let finish:((t:ReturnType<typeof trial>)=>void)|undefined;
  const create=vi.fn((_signal:AbortSignal)=>new Promise<ReturnType<typeof trial>>(resolve=>{finish=resolve;}));
  const changed=vi.fn(),c=new RoadTerrainTrialController(create,changed);c.build();const oldFinish=finish!;
  c.build();expect(create.mock.calls[0][0].aborted).toBe(true);const old=trial();oldFinish(old);await vi.advanceTimersByTimeAsync(0);
  expect(old.dispose).toHaveBeenCalledOnce();expect(c.trial).toBeUndefined();
  c.dispose();const count=changed.mock.calls.length,late=trial();finish!(late);await vi.runAllTimersAsync();
  expect(late.dispose).toHaveBeenCalledOnce();expect(changed).toHaveBeenCalledTimes(count);
});
